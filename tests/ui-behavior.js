#!/usr/bin/env node
"use strict";
const pw = require("playwright");
const base = process.argv[2] || "http://localhost:8765/";
let bad = 0;
const ok = (c, m) => { if (!c) { bad++; console.log("FAIL " + m); } };
async function run(name) {
let browser;
try { browser = await pw[name].launch(); }
catch (e) {
if (process.env.CI) { bad++; console.log(`FAIL ${name} is not installed (required in CI)`); }
else console.log(`skip ${name}: not installed`);
return;
}
const ctx = await browser.newContext({ viewport: { width: 375, height: 800 } });
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
await page.addInitScript(() => document.addEventListener("securitypolicyviolation", (e) => console.error("CSP violation: " + e.violatedDirective + " " + e.blockedURI)));
await page.goto(base + "index.html", { waitUntil: "networkidle" });
await page.waitForSelector("#snd .snd-c");
for (const dev of ["iem", "spk"]) {
await page.click(`[data-out="${dev}"]`);
const ids = await page.$$eval("#snd .snd-c", (c) => c.map((x) => x.dataset.p));
ok(ids.length === 3, `${name}: ${dev} should list 3 profiles, got ${ids.length}`);
ok((await page.$$eval("#snd .profile-metrics", (m) => m.length)) === ids.length, `${name}: ${dev} cards must all show metrics`);
const ranges = [];
for (const id of ids) {
await page.click(`#snd [data-p="${id}"]`);
ranges.push(await page.$eval("#cmpChart", (h) => h._s && [h._s.y0, h._s.y1].join(",")));
}
ok(ranges.every((r) => r && r === ranges[0]), `${name}: ${dev} y-range moves between profiles (${ranges.join(" | ")})`);
}
const hasBand = async () => page.$$eval("#cmpChart svg text", (t) => t.some((x) => x.textContent === "HIGH-PASS"));
await page.click('[data-out="spk"]'); ok(await hasBand(), `${name}: speaker high-pass band missing`);
await page.click('[data-out="iem"]'); ok(!(await hasBand()), `${name}: IEM must not show the high-pass band`);
const sum0 = await page.$eval("#cmpSum", (e) => e.textContent);
const before = await page.$eval("#cmpChart", (h) => h._c.series[1].pts.slice(40, 60).map((p) => p[1].toFixed(3)).join());
await page.click('#cmpSmooth [data-o="3"]');
const after = await page.$eval("#cmpChart", (h) => h._c.series[1].pts.slice(40, 60).map((p) => p[1].toFixed(3)).join());
ok(before !== after, `${name}: 1/3-oct smoothing did not change the curve`);
ok(sum0 === (await page.$eval("#cmpSum", (e) => e.textContent)), `${name}: smoothing must not change the RMS summary`);
await page.click('#cmpSmooth [data-o="0"]');
const opts = await page.$$eval("#cmpOvl option", (o) => o.map((x) => x.value));
ok(opts.length === 3 && opts[0] === "" && opts.slice(1).every((v) => v.startsWith("iem-")), `${name}: overlay options wrong: ${opts}`);
const legend0 = await page.$$eval("#cmpLegend button", (b) => b.length);
await page.selectOption("#cmpOvl", opts[1]);
ok((await page.$$eval("#cmpLegend button", (b) => b.length)) === legend0 + 1, `${name}: overlay did not add a legend entry`);
await page.focus("#cmpChart");
await page.keyboard.press("ArrowRight");
const said = await page.$eval("#cmpChart", (h) => (h._live ? h._live.textContent : ""));
ok(/decibels/.test(said), `${name}: keyboard readout not announced (${said})`);
const dockIs = (shown) => page.waitForFunction((s) => { const d = document.querySelector("#dock"); return (!d.hidden && getComputedStyle(d).display !== "none") === s; }, shown, { timeout: 4000 }).then(() => true, () => false);
await page.evaluate(() => document.querySelector("#snd").scrollIntoView({ block: "center" }));
ok(await dockIs(true), `${name}: dock should show while choosing a profile`);
await page.evaluate(() => document.querySelector("#getBtn").scrollIntoView({ block: "center" }));
ok(await dockIs(false), `${name}: dock should hide when the download button is visible`);
const chips = await page.$$eval("#evBadge .evc", (c) => c.map((x) => x.textContent));
ok(chips.some((t) => /Calculated/.test(t)) && chips.some((t) => /No device record|Device test/.test(t)) && chips.some((t) => /Not measured|Acoustic/.test(t)), `${name}: evidence chips incomplete: ${chips}`);
for (const f of ["plus-jakarta-sans-latin-400-normal", "jetbrains-mono-latin-700-normal"]) {
const r = await page.request.get(base + `assets/fonts/${f}.woff2`);
ok(r.ok(), `${name}: font ${f} not served`);
if (r.ok() && (await r.body()).length > 4000) {
ok(await page.evaluate(() => document.fonts.check('600 16px "Plus Jakarta Sans"')), `${name}: Plus Jakarta Sans did not load`);
}
}
ok(!errors.length, `${name}: page errors/CSP violations:\n  ` + errors.slice(0, 5).join("\n  "));
await page.goto(base + "compare.html", { waitUntil: "networkidle" });
await page.waitForSelector("#b option", { state: "attached" });
await page.selectOption("#a", "spk-v8");
const b = await page.$$eval("#b option", (o) => o.map((x) => [x.value, x.disabled || x.hidden]));
ok(b.length === 3 && b.every(([v, off]) => v.startsWith("spk-") && !off), `${name}: compare list B must contain only enabled speaker profiles: ${JSON.stringify(b)}`);
await ctx.close();
await browser.close();
console.log(`behaviour ${name}: done`);
}
(async () => {
await run("chromium");
await run("webkit");
console.log(bad ? `ui-behavior: ${bad} problem(s)` : "ui-behavior: all checks passed");
process.exit(bad ? 1 : 0);
})();
