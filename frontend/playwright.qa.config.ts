import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  testMatch: "qa.spec.ts",
  workers: 1,
  fullyParallel: false,
  timeout: 600000,
  expect: { timeout: 10000 },
  reporter: [
    ["list"],
    ["json", { outputFile: "../reports/testing/browser-test-results.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5175",
    channel: "chrome",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1586, height: 1000 } } },
    {
      name: "mobile",
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
});
