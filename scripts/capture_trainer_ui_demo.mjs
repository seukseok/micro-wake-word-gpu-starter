import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const assetsDir = path.join(root, "docs", "assets");
const frameDir = path.join(root, ".tools", "trainer-ui-frames");
const url = process.env.TRAINER_URL || "http://localhost:8789";
const require = createRequire(import.meta.url);

function loadPlaywright() {
  try {
    return require("playwright-core");
  } catch {
    return require(path.join(root, ".tools", "playwright", "node_modules", "playwright-core"));
  }
}

const { chromium } = loadPlaywright();

const edgeCandidates = [
  process.env.EDGE_PATH,
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
].filter(Boolean);

function findEdge() {
  for (const candidate of edgeCandidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error("Microsoft Edge was not found. Set EDGE_PATH to a Chromium-compatible browser.");
}

function resetDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}

function prepareAssetsDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
  for (const entry of fs.readdirSync(dir)) {
    if (/^trainer-ui-.*\.(png|gif|mp4)$/.test(entry)) {
      fs.rmSync(path.join(dir, entry), { force: true });
    }
  }
}

let frameIndex = 0;

async function capture(page, name, repeat = 8, saveAsset = true) {
  const png = path.join(assetsDir, `${name}.png`);
  await page.screenshot({ path: png, fullPage: false });
  for (let i = 0; i < repeat; i += 1) {
    fs.copyFileSync(png, path.join(frameDir, `frame_${String(frameIndex).padStart(4, "0")}.png`));
    frameIndex += 1;
  }
  if (!saveAsset) {
    fs.rmSync(png, { force: true });
  }
}

async function clickTab(page, name) {
  await page.getByRole("button", { name }).click();
  await page.waitForTimeout(350);
}

const browser = await chromium.launch({
  executablePath: findEdge(),
  headless: true,
});

const page = await browser.newPage({
  viewport: { width: 1280, height: 820 },
  deviceScaleFactor: 1,
});

prepareAssetsDir(assetsDir);
resetDir(frameDir);

await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
await page.waitForTimeout(500);
await capture(page, "trainer-ui-trainer", 10);

const phrase = page.getByLabel("Wake Phrase");
await phrase.fill("");
for (const char of "hey komi") {
  await phrase.type(char, { delay: 55 });
  await capture(page, "trainer-ui-typing", 2, false);
}
await capture(page, "trainer-ui-phrase", 8, false);

await clickTab(page, "Samples");
await capture(page, "trainer-ui-samples", 10);

await clickTab(page, "Captured Audio");
await capture(page, "trainer-ui-captured-audio", 10);

await clickTab(page, "Firmware");
await capture(page, "trainer-ui-firmware", 10);

await clickTab(page, "Trainer");
await capture(page, "trainer-ui-trainer-final", 8, false);

await browser.close();

console.log(`Captured ${frameIndex} frames from ${url}`);
console.log(`Assets: ${path.relative(root, assetsDir)}`);
