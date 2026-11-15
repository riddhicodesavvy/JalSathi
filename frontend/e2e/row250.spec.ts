import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import type { Prediction } from "../src/types";
const root = path.resolve("..");
const evidence = JSON.parse(
  fs.readFileSync(
    path.join(root, "reports/testing/ROW_250_VERIFICATION.json"),
    "utf8",
  ),
);
test("row 250 exact supplied values agree with direct model, API and UI", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const expected = evidence.cases.supplied_rounded;
  await page.goto("/analyze");
  await expect(page.locator("#ph")).toBeVisible();
  for (const [key, value] of Object.entries(expected.measurements))
    await page.locator(`#${key}`).fill(String(value));
  const [request, response] = await Promise.all([
    page.waitForRequest(
      (r) => r.url().endsWith("/api/v1/predict") && r.method() === "POST",
    ),
    page.waitForResponse(
      (r) =>
        r.url().endsWith("/api/v1/predict") && r.request().method() === "POST",
    ),
    page.getByRole("button", { name: "Analyze Sample", exact: true }).click(),
  ]);
  expect(request.postDataJSON()).toEqual(expected.measurements);
  expect(response.status()).toBe(200);
  const result = (await response.json()) as Prediction;
  expect(result.measurements).toEqual(expected.measurements);
  expect(result.primary_model).toBe("rf");
  expect(result.predicted_class).toBe(expected.direct_class);
  expect(
    result.models.find((m) => m.id === "rf")!.potable_probability,
  ).toBeCloseTo(expected.direct_potable_probability, 12);
  await expect(page.locator(".prediction-banner h3")).toHaveText(result.label);
  await expect(page.locator(".probability strong")).toHaveText(
    `${(result.selected_class_probability * 100).toFixed(1)}%`,
  );
  await expect(page.locator(".agreement")).toContainText(
    `${result.agreement_count} / 5`,
  );
  for (const m of result.models)
    await expect(
      page
        .getByTitle(`${m.name}: ${m.label}`, { exact: true })
        .locator("span")
        .first(),
    ).toHaveClass(m.predicted_class ? "model-yes" : "model-no");
  expect(result.parameters[0].status).toBe("outside");
  await expect(page.locator(".parameter-table tbody tr").first()).toContainText(
    "Outside range",
  );
  await expect(page.locator(".disclaimer")).toContainText(
    "not the probability that water is safe",
  );
  expect(errors).toEqual([]);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.mouse.move(0, 0);
  await page.screenshot({
    path: path.join(root, "reports/testing/row250-frontend.png"),
    fullPage: true,
    style: "[data-sonner-toaster]{visibility:hidden}",
  });
  fs.writeFileSync(
    path.join(root, "reports/testing/ROW_250_BROWSER_VERIFICATION.json"),
    JSON.stringify(
      { passed: true, submitted: request.postDataJSON(), result, errors },
      null,
      2,
    ),
  );
});
