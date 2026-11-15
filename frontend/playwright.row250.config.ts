import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  testMatch: "row250.spec.ts",
  workers: 1,
  timeout: 90000,
  reporter: [
    ["list"],
    ["json", { outputFile: "../reports/testing/row250-browser-test.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5173",
    channel: "chrome",
    viewport: { width: 1586, height: 1000 },
    trace: "retain-on-failure",
  },
});
