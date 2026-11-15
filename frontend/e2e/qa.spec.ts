import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import type { Prediction } from "../src/types";
const root = path.resolve("..");
const samples: {
  dataset_index: number;
  true_label: number;
  measurements: Record<string, number>;
}[] = JSON.parse(
  fs.readFileSync(
    path.join(root, "tests/fixtures/browser_samples.json"),
    "utf8",
  ),
);
const evidence = path.join(root, "reports/testing");
test("every CSV fixture is handled correctly by the batch interface", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "desktop",
    "Full fixture matrix runs once on desktop; mobile parity runs separately.",
  );
  const specs = JSON.parse(
    fs.readFileSync(
      path.join(root, "tests/fixtures/specifications.json"),
      "utf8",
    ),
  ) as Record<
    string,
    { rows: number; expected_status: number; invalid: number }
  >;
  const evidenceRows: unknown[] = [];
  await page.goto("/batch");
  await expect(
    page.getByRole("heading", { name: "Batch Analysis", exact: true }),
  ).toBeVisible();
  for (const [name, spec] of Object.entries(specs)) {
    const awaited = page.waitForResponse((r) =>
      r.url().endsWith("/predict/batch"),
    );
    await page
      .getByLabel("CSV file", { exact: true })
      .setInputFiles(path.join(root, "tests/fixtures/csv", name));
    const response = await awaited;
    expect(response.status()).toBe(spec.expected_status);
    const body = await response.json();
    if (response.ok()) {
      await expect(
        page.getByRole("heading", { name: "Analysis results", exact: true }),
      ).toBeVisible();
      expect(body.total).toBe(spec.rows);
      expect(body.invalid).toBe(spec.invalid);
      if (body.valid > 0) {
        const [download] = await Promise.all([
          page.waitForEvent("download"),
          page.getByRole("button", { name: "Export CSV" }).click(),
        ]);
        expect(download.suggestedFilename()).toMatch(/\.csv$/);
      }
    } else
      await expect(
        page.getByRole("alert").filter({ hasText: "Data unavailable" }),
      ).toBeVisible();
    evidenceRows.push({
      file: name,
      status: response.status(),
      valid: body.valid ?? 0,
      invalid: body.invalid ?? spec.rows,
      uiHandled: true,
    });
  }
  fs.writeFileSync(
    path.join(evidence, "browser-csv-results.json"),
    JSON.stringify(evidenceRows, null, 2),
  );
});
test("comparison tabs, batch controls, history pagination and project metadata", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "desktop",
    "Page interactions run once; mobile layout is covered by smoke tests.",
  );
  await page.goto("/dashboard");
  await expect(page.getByText("3,276", { exact: true })).toBeVisible();
  await page
    .getByRole("link", {
      name: /Compare models Inspect real evaluation results/,
    })
    .click();
  await expect(page).toHaveURL(/models/);
  for (const tab of [
    "Comparison",
    "Confusion Matrices",
    "ROC Curves",
    "Precision-Recall",
    "Feature Importance",
    "CART Tree",
  ]) {
    await page.getByRole("tab", { name: tab, exact: true }).click();
    await expect(page.getByRole("tabpanel")).toBeVisible();
  }
  const artifact = JSON.parse(
    fs.readFileSync(path.join(root, "ml/artifacts/registry.json"), "utf8"),
  );
  await page.getByRole("button", { name: "accuracy", exact: true }).click();
  const best = [...artifact.models].sort(
    (a, b) => b.metrics.accuracy - a.metrics.accuracy,
  )[0];
  await expect(page.locator(".table-scroll tbody tr").first()).toContainText(
    best.name,
  );
  await page
    .getByRole("button", { name: "View Details", exact: false })
    .first()
    .click();
  await expect(page.getByRole("dialog")).toContainText(
    "Actual fitted hyperparameters",
  );
  await page.getByRole("button", { name: "Close details" }).click();
  await page.goto("/reports");
  await expect(
    page.getByRole("button", { name: /Preview/ }).first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: /Preview/ })
    .first()
    .click();
  await expect(page.getByRole("dialog")).toContainText("pH");
  await expect(page.getByRole("dialog")).toContainText("Laboratory testing");
  await page.getByRole("button", { name: "Close details" }).click();
  const next = page.getByRole("button", { name: "Next", exact: true });
  await expect(next).toBeEnabled();
  await next.click();
  await expect(page.getByText(/11–20 of/)).toBeVisible();
  await page.goto("/about");
  await expect(
    page.getByText("Approximation only", { exact: false }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: /Bayesian-style averaging/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: /Adaptive basis/ }),
  ).toContainText("not implemented");
  await page.goto("/batch");
  await page
    .getByLabel("CSV file", { exact: true })
    .setInputFiles(
      path.join(root, "tests/fixtures/csv/balanced_labeled_100.csv"),
    );
  await expect(
    page.getByRole("heading", { name: "Analysis results", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("combobox", { name: "Filter predictions" })
    .selectOption("1");
  await page
    .getByRole("combobox", { name: "Sort samples" })
    .selectOption("probability");
  await page
    .getByRole("textbox", { name: "Search samples" })
    .fill("no such measurement");
  await expect(page.locator(".table-scroll tbody tr")).toHaveCount(0);
  await page
    .getByLabel("CSV file", { exact: true })
    .setInputFiles(path.join(root, "tests/fixtures/csv/single_sample.csv"));
  await expect(page.locator(".table-scroll tbody tr")).toHaveCount(1);
  await expect(
    page.getByRole("textbox", { name: "Search samples" }),
  ).toHaveValue("");
});
test("edited nine-field payload, both observed states, API/history and CSV parity", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/analyze");
  await expect(page.locator("#ph")).toBeVisible();
  const recorded: unknown[] = [];
  const observed = new Set<number>();
  for (const sample of samples.slice(
    0,
    info.project.name === "desktop" ? 50 : 3,
  )) {
    for (const [key, value] of Object.entries(sample.measurements))
      await page.locator(`#${key}`).fill(String(value));
    const [response, request] = await Promise.all([
      page.waitForResponse(
        (r) => r.url().endsWith("/predict") && r.request().method() === "POST",
      ),
      page.waitForRequest(
        (r) => r.url().endsWith("/predict") && r.method() === "POST",
      ),
      page.getByRole("button", { name: "Analyze Sample", exact: true }).click(),
    ]);
    expect(request.postDataJSON()).toEqual(sample.measurements);
    expect(response.status()).toBe(200);
    const result = (await response.json()) as Prediction;
    expect(result.measurements).toEqual(sample.measurements);
    await expect(
      page.getByRole("heading", { name: result.label, exact: true }),
    ).toBeVisible();
    await expect(page.locator(".probability strong")).toHaveText(
      `${(result.selected_class_probability * 100).toFixed(1)}%`,
    );
    await expect(page.locator(".agreement")).toContainText(
      `${result.agreement_count} / 5`,
    );
    const saved = await page.request.get(
      `http://127.0.0.1:8001/api/v1/analyses/${result.analysis_id}`,
    );
    expect(await saved.json()).toEqual(result);
    recorded.push({ ...sample, result });
    if (!observed.has(result.predicted_class)) {
      observed.add(result.predicted_class);
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({
        path: path.join(
          evidence,
          `${info.project.name}-actual-class-${result.predicted_class}.png`,
        ),
        fullPage: true,
        style: "[data-sonner-toaster]{visibility:hidden}",
      });
    }
  }
  if (info.project.name === "desktop")
    expect([...observed].sort()).toEqual([0, 1]);
  fs.writeFileSync(
    path.join(evidence, `${info.project.name}-form-evidence.json`),
    JSON.stringify(recorded, null, 2),
  );
  const selected = samples.slice(0, info.project.name === "desktop" ? 50 : 3);
  const headers = Object.keys(selected[0].measurements);
  const csv = [
    headers.join(","),
    ...selected.map((s) => headers.map((k) => s.measurements[k]).join(",")),
  ].join("\n");
  await page.goto("/batch");
  const responsePromise = page.waitForResponse((r) =>
    r.url().endsWith("/predict/batch"),
  );
  await page.getByLabel("CSV file", { exact: true }).setInputFiles({
    name: "browser-parity.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(csv),
  });
  const batch = await (await responsePromise).json();
  expect(batch.valid).toBe(selected.length);
  for (let i = 0; i < selected.length; i++) {
    const single = (recorded[i] as { result: Prediction }).result;
    const item = batch.results[i] as Prediction;
    expect(item.measurements).toEqual(single.measurements);
    expect(item.version).toBe(single.version);
    expect(item.primary_model).toBe(single.primary_model);
    for (let j = 0; j < 5; j++) {
      expect(item.models[j].id).toBe(single.models[j].id);
      expect(item.models[j].predicted_class).toBe(
        single.models[j].predicted_class,
      );
      expect(item.models[j].potable_probability).toBeCloseTo(
        single.models[j].potable_probability,
        12,
      );
    }
  }
  await expect(
    page.getByRole("heading", { name: "Analysis results", exact: true }),
  ).toBeVisible();
  fs.writeFileSync(
    path.join(evidence, `${info.project.name}-browser-parity.json`),
    JSON.stringify({
      samples: selected.length,
      modelComparisons: selected.length * 5,
      mismatches: 0,
    }),
  );
  expect(errors).toEqual([]);
});
test("a failed re-analysis must not keep a previous successful result", async ({
  page,
}) => {
  await page.goto("/analyze");
  await expect(page.locator("#ph")).toBeVisible();
  await page
    .getByRole("button", { name: "Analyze Sample", exact: true })
    .click();
  await expect(page.locator(".prediction-banner")).toBeVisible();
  await page.route("**/api/v1/predict", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { message: "Intentional isolated regression failure" },
      }),
    }),
  );
  await page.locator("#ph").fill("3.1");
  await page
    .getByRole("button", { name: "Analyze Sample", exact: true })
    .click();
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "Intentional isolated regression failure" }),
  ).toBeVisible();
  await expect(page.locator(".prediction-banner")).toHaveCount(0);
});
test("pending submissions lock edits/reset and clear reliably", async ({
  page,
}) => {
  await page.goto("/analyze");
  await expect(page.locator("#ph")).toBeVisible();
  let release!: () => void;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/v1/predict", async (route) => {
    await held;
    await route.continue();
  });
  await page
    .getByRole("button", { name: "Analyze Sample", exact: true })
    .click();
  await expect(page.getByRole("button", { name: "Analyzing…" })).toBeDisabled();
  await expect(page.locator("#ph")).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Reset", exact: true }),
  ).toBeDisabled();
  release();
  await expect(page.locator(".prediction-banner")).toBeVisible();
  await page.getByRole("button", { name: "Analyze Another" }).click();
  await expect(page.locator(".prediction-banner")).toHaveCount(0);
  await expect(page.locator("#ph")).toBeFocused();
});
