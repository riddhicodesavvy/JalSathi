import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  testMatch: "production.spec.ts",
  workers: 1,
  timeout: 180000,
  reporter: [
    ["list"],
    ["json", { outputFile: "../reports/testing/production-browser-raw.json" }],
  ],
  use: {
    baseURL:
      process.env.JALSATHI_PUBLIC_URL || "https://jalsathi-ridcyber.vercel.app",
    channel: "chrome",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1586, height: 1000 } } },
    { name: "tablet", use: { viewport: { width: 834, height: 1112 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
