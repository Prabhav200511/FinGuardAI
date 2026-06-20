/* Capture verified dashboard states for documentation and demo assets. */

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const OUTPUT = path.join(ROOT, "docs", "assets");
fs.mkdirSync(OUTPUT, { recursive: true });

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  const ignoredConsole = /metrics config|metrics tracking|ERR_NETWORK_ACCESS_DENIED/;
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error" && !ignoredConsole.test(message.text())) {
      errors.push(`console: ${message.text()}`);
    }
  });

  await page.goto("http://127.0.0.1:8501", { waitUntil: "domcontentloaded", timeout: 120000 });
  await page.getByText("FinGuard AI", { exact: false }).first().waitFor({ timeout: 120000 });
  await page.waitForTimeout(15000);
  const initialText = await page.locator("body").innerText();
  if (!initialText.includes("Session Transactions")) {
    fs.writeFileSync(path.join(OUTPUT, "dashboard-debug-text.txt"), initialText, "utf8");
    await page.screenshot({ path: path.join(OUTPUT, "dashboard-debug.png"), fullPage: true });
    throw new Error("Dashboard did not finish rendering its summary metrics");
  }
  await page.screenshot({ path: path.join(OUTPUT, "dashboard-live-feed.png"), fullPage: true });

  await page.getByRole("tab", { name: /Fraud Alerts/ }).click();
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(OUTPUT, "dashboard-alerts.png"), fullPage: true });

  const explain = page.getByRole("button", { name: /Get AI Explanation/ }).first();
  if (await explain.count()) {
    await explain.click();
    await page.getByText(/This transaction looks suspicious/).first().waitFor({ timeout: 30000 });
    await page.waitForTimeout(1000);
  }
  await page.screenshot({ path: path.join(OUTPUT, "dashboard-explanation-en.png"), fullPage: true });

  await page.getByRole("tab", { name: /Analytics/ }).click();
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(OUTPUT, "dashboard-analytics.png"), fullPage: true });

  const bodyText = await page.locator("body").innerText();
  if (/Traceback|ValueError|Exception/.test(bodyText)) {
    throw new Error("Visible application error detected during dashboard capture");
  }
  fs.writeFileSync(path.join(OUTPUT, "dashboard-visible-text.txt"), bodyText, "utf8");
  fs.writeFileSync(path.join(OUTPUT, "browser-errors.txt"), errors.join("\n"), "utf8");
  await browser.close();

  console.log(`Captured dashboard assets in ${OUTPUT}`);
  console.log(`Browser errors: ${errors.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
