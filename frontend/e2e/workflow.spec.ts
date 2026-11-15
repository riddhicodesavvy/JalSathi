import { expect, test } from "@playwright/test";
import path from "node:path";
test("real prediction, model details, report and all pages", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/analyze");
  await expect(
    page.getByRole("heading", { name: "Water Quality Parameters" }),
  ).toBeVisible();
  await page.getByLabel("pH", { exact: true }).fill("7.2");
  await page.getByLabel("pH slider", { exact: true }).focus();
  await page.keyboard.press("ArrowRight");
  expect(
    Number(await page.getByLabel("pH", { exact: true }).inputValue()),
  ).toBeGreaterThan(7.2);
  await page.getByLabel("pH", { exact: true }).fill("7.2");
  await page
    .getByRole("button", { name: "Analyze Sample", exact: true })
    .click();
  await expect(
    page.getByText("MODEL-BASED CLASSIFICATION", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("8 Unverified", { exact: false })).toBeVisible();
  await page
    .getByRole("button", { name: "Model Details", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toContainText("CART decision path");
  await page.getByRole("button", { name: "Close details" }).click();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Download Report", exact: true }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/\.pdf$/);
  await page.mouse.move(0, 0);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: `test-results/${info.project.name}-analyzer.png`,
    fullPage: true,
    style: '[data-sonner-toaster] { visibility: hidden; }',
  });
  for (const [url, title] of [
    ["/dashboard", "Welcome to JalSathi"],
    ["/models", "Model Comparison Lab"],
    ["/batch", "Batch Analysis"],
    ["/reports", "Reports & Analysis History"],
    ["/about", "About JalSathi"],
  ]) {
    await page.goto(url);
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
  }
  await page.goto("/models");
  await page.getByRole("tab", { name: "CART Tree" }).click();
  await expect(
    page.getByAltText(
      "Fitted CART decision tree, depth-limited to three levels",
    ),
  ).toBeVisible();
  await page.goto("/batch");
  await page
    .getByLabel("CSV file", { exact: true })
    .setInputFiles(path.resolve("../data/samples/demo.csv"));
  await expect(
    page.getByRole("heading", { name: "Analysis results" }),
  ).toBeVisible();
  const [csv] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Export CSV" }).click(),
  ]);
  expect(csv.suggestedFilename()).toMatch(/\.csv$/);
  if (info.project.name === "mobile") {
    await page.getByRole("button", { name: "Open navigation" }).click();
    await page
      .getByRole("link", { name: "Analyze Sample", exact: true })
      .click();
    await expect(page).toHaveURL(/analyze/);
    await expect(
      page.getByRole("button", { name: "Open navigation" }),
    ).toHaveAttribute("aria-expanded", "false");
  }
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});
test("invalid form and honest backend error", async ({ page }) => {
  await page.goto("/analyze");
  await page.getByLabel("pH", { exact: true }).fill("15");
  await page
    .getByRole("button", { name: "Analyze Sample", exact: true })
    .click();
  await expect(page.locator("#ph")).toHaveAttribute("aria-invalid", "true");
  await page.route("**/api/v1/features", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { message: "Backend unavailable for test" },
      }),
    }),
  );
  await page.reload();
  await expect(page.getByRole("alert")).toContainText(
    "Backend unavailable for test",
  );
});
