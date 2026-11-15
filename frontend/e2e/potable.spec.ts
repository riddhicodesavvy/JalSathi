import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import type { Prediction } from "../src/types";
const root = path.resolve("..");
interface Example {
  number: number;
  dataset_index: number;
  measurements: Record<string, number>;
  primary_probability: number;
  api_result: Prediction;
}
const evidence = JSON.parse(
  fs.readFileSync(
    path.join(root, "reports/testing/verified_potable_evidence.json"),
    "utf8",
  ),
) as { examples: { potable: Example[]; nonpotable: Example[] } };
test("ten original samples agree across direct inference, live API, UI, indicators, standards and PDF", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const entries = [];
  const reports = path.join(root, "runtime/verified-example-reports");
  fs.mkdirSync(reports, { recursive: true });
  await page.goto("/analyze");
  await expect(page.locator("#ph")).toBeVisible();
  // Alternate states and leave the strongest verified positive example in the form.
  for (let i = 4; i >= 0; i--) {
    for (const group of ["nonpotable", "potable"] as const) {
      const sample = evidence.examples[group][i];
      for (const [key, value] of Object.entries(sample.measurements))
        await page.locator(`#${key}`).fill(String(value));
      const [response, request] = await Promise.all([
        page.waitForResponse(
          (r) =>
            r.url().endsWith("/api/v1/predict") &&
            r.request().method() === "POST",
        ),
        page.waitForRequest(
          (r) => r.url().endsWith("/api/v1/predict") && r.method() === "POST",
        ),
        page
          .getByRole("button", { name: "Analyze Sample", exact: true })
          .click(),
      ]);
      expect(response.status()).toBe(200);
      expect(request.postDataJSON()).toEqual(sample.measurements);
      const result = (await response.json()) as Prediction;
      expect(result.measurements).toEqual(sample.measurements);
      expect(result.primary_model).toBe("rf");
      expect(result.predicted_class).toBe(group === "potable" ? 1 : 0);
      expect(result.version).toBe(sample.api_result.version);
      const rf = result.models.find((m) => m.id === "rf")!;
      expect(rf.potable_probability).toBeCloseTo(
        sample.primary_probability,
        12,
      );
      await expect(page.locator(".prediction-banner h3")).toHaveText(
        result.label,
      );
      await expect(page.locator(".prediction-banner")).toHaveClass(
        new RegExp(group === "potable" ? "potable" : "nonpotable"),
      );
      await expect(page.locator(".probability strong")).toHaveText(
        `${(result.selected_class_probability * 100).toFixed(1)}%`,
      );
      const arc = (await page
        .locator(".ring-value")
        .getAttribute("stroke-dasharray"))!
        .split(" ")
        .map(Number);
      expect(arc[0]).toBeCloseTo(result.selected_class_probability * 308, 10);
      const agreement = result.models.filter(
        (m) => m.predicted_class === result.predicted_class,
      ).length;
      expect(result.agreement_count).toBe(agreement);
      await expect(page.locator(".agreement")).toContainText(
        `${agreement} / 5`,
      );
      for (const model of result.models) {
        const indicator = page.getByTitle(`${model.name}: ${model.label}`, {
          exact: true,
        });
        await expect(indicator).toBeVisible();
        await expect(indicator.locator("span").first()).toHaveClass(
          model.predicted_class ? "model-yes" : "model-no",
        );
      }
      // The only active reference is dimensionless pH; it remains independent of classification.
      expect(result.parameters[0].status).toBe(
        sample.measurements.ph >= 6.5 && sample.measurements.ph <= 8.5
          ? "within"
          : "outside",
      );
      expect(
        result.parameters.slice(1).every((p) => p.status === "unknown"),
      ).toBe(true);
      for (let row = 0; row < 9; row++)
        await expect(
          page.locator(".parameter-table tbody tr").nth(row).locator(".status"),
        ).toHaveClass(new RegExp(result.parameters[row].status));
      await expect(page.locator(".disclaimer")).toContainText(
        "Laboratory testing",
      );
      await expect(page.locator(".disclaimer")).toContainText(
        "not the probability that water is safe",
      );
      await expect(page.locator(".prediction-banner")).toContainText(
        "Educational estimate",
      );
      await expect(
        page.getByText(/guaranteed safe|certified safe|guaranteed potable/i),
      ).toHaveCount(0);
      const [download] = await Promise.all([
        page.waitForEvent("download"),
        page
          .getByRole("button", { name: "Download Report", exact: true })
          .click(),
      ]);
      const reportPath = path.join(reports, `${group}-${sample.number}.pdf`);
      await download.saveAs(reportPath);
      if (group === "potable") {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.mouse.move(0, 0);
        await page.screenshot({
          path: path.join(
            root,
            `reports/testing/verified-potable-${sample.number}.png`,
          ),
          fullPage: true,
          style: "[data-sonner-toaster]{visibility:hidden}",
        });
      }
      entries.push({
        group,
        number: sample.number,
        dataset_index: sample.dataset_index,
        measurements: sample.measurements,
        uiVerified: true,
        reportPath,
        result,
      });
    }
  }
  expect(errors).toEqual([]);
  fs.writeFileSync(
    path.join(root, "reports/testing/verified_potable_browser_evidence.json"),
    JSON.stringify({ entries, errors, verified: entries.length }, null, 2),
  );
});
