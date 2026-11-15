import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import type { Prediction } from "../src/types";
const root = path.resolve("..");
const positive = JSON.parse(
  fs.readFileSync(
    path.join(root, "reports/testing/ROW_250_VERIFICATION.json"),
    "utf8",
  ),
).cases.supplied_rounded;
const negative = JSON.parse(
  fs.readFileSync(
    path.join(root, "reports/testing/verified_potable_evidence.json"),
    "utf8",
  ),
).examples.nonpotable[0];
test("public production pages, actual predictions, downloads and durable history", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  for (const [url, title] of [
    ["/dashboard", "Welcome to JalSathi"],
    ["/analyze", "Analyze Sample"],
    ["/models", "Model Comparison Lab"],
    ["/batch", "Batch Analysis"],
    ["/reports", "Reports & Analysis History"],
    ["/about", "About JalSathi"],
  ]) {
    await page.goto(url);
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await page.reload();
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
  await page.goto("/analyze");
  let positiveId = "";
  for (const sample of [positive, negative]) {
    for (const [key, value] of Object.entries(sample.measurements))
      await page.locator(`#${key}`).fill(String(value));
    const [response] = await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().endsWith("/api/v1/predict") &&
          r.request().method() === "POST",
      ),
      page.getByRole("button", { name: "Analyze Sample", exact: true }).click(),
    ]);
    expect(response.status()).toBe(200);
    expect(response.request().postDataJSON()).toEqual(sample.measurements);
    const result = (await response.json()) as Prediction;
    expect(result.measurements).toEqual(sample.measurements);
    expect(result.predicted_class).toBe(sample === positive ? 1 : 0);
    expect(
      result.models.find((m) => m.id === "rf")!.potable_probability,
    ).toBeCloseTo(
      sample === positive
        ? positive.direct_potable_probability
        : negative.primary_probability,
      12,
    );
    await expect(page.locator(".prediction-banner h3")).toHaveText(
      result.label,
    );
    await expect(page.locator(".probability strong")).toHaveText(
      `${(result.selected_class_probability * 100).toFixed(1)}%`,
    );
    await expect(page.locator(".agreement")).toContainText(
      `${result.agreement_count} / 5`,
    );
    for (const model of result.models)
      await expect(
        page
          .getByTitle(`${model.name}: ${model.label}`, { exact: true })
          .locator("span")
          .first(),
      ).toHaveClass(model.predicted_class ? "model-yes" : "model-no");
    await expect(page.locator(".disclaimer")).toContainText(
      "not the probability that water is safe",
    );
    if (sample === positive) {
      positiveId = result.analysis_id;
      expect(result.agreement_count).toBe(3);
      await expect(
        page.locator(".parameter-table tbody tr").first(),
      ).toContainText("Outside range");
      await page.screenshot({
        path: path.join(
          root,
          `reports/testing/production-${info.project.name}.png`,
        ),
        fullPage: true,
        style: "[data-sonner-toaster]{visibility:hidden}",
      });
      const [pdf] = await Promise.all([
        page.waitForEvent("download"),
        page
          .getByRole("button", { name: "Download Report", exact: true })
          .click(),
      ]);
      expect(pdf.suggestedFilename()).toMatch(/\.pdf$/);
      expect(await pdf.failure()).toBeNull();
    }
  }
  await page.goto("/models");
  await page.getByRole("tab", { name: "CART Tree" }).click();
  const tree = page.getByAltText(
    "Fitted CART decision tree, depth-limited to three levels",
  );
  await expect(tree).toBeVisible();
  await expect
    .poll(() => tree.evaluate((img: HTMLImageElement) => img.naturalWidth))
    .toBeGreaterThan(0);
  await page.goto("/batch");
  const [batchResponse] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/predict/batch")),
    page
      .getByLabel("CSV file", { exact: true })
      .setInputFiles(
        path.join(root, "tests/fixtures/verified_potable_samples.csv"),
      ),
  ]);
  const batch = await batchResponse.json();
  expect(batch.valid).toBe(5);
  expect(batch.potable).toBe(5);
  await expect(
    page.getByRole("heading", { name: "Analysis results" }),
  ).toBeVisible();
  const [csv] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Export CSV" }).click(),
  ]);
  expect(await csv.failure()).toBeNull();
  await page.getByLabel("CSV file", { exact: true }).setInputFiles({
    name: "malformed.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("ph\n7"),
  });
  await expect(page.getByRole("alert")).toBeVisible();
  await page.goto("/reports");
  await page.reload();
  const saved = await page.request.get(`/api/v1/analyses/${positiveId}`);
  expect(saved.status()).toBe(200);
  expect((await saved.json()).predicted_class).toBe(1);
  if (info.project.name === "mobile") {
    await page.getByRole("button", { name: "Open navigation" }).click();
    await page
      .getByRole("link", { name: "Analyze Sample", exact: true })
      .click();
    await expect(page).toHaveURL(/analyze/);
  }
  expect(errors).toEqual([]);
});
