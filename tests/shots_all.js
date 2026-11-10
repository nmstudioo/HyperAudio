#!/usr/bin/env node
"use strict";
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const base = process.argv[2], out = process.argv[3];
const SITE = path.join(__dirname, "..", "site");
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
e.isDirectory() ? (e.name === "downloads" ? [] : walk(path.join(d, e.name))) : [path.join(d, e.name)]);
const pages = walk(SITE).filter(f => f.endsWith(".html") && !f.endsWith("404.html")).map(f => path.relative(SITE, f)).sort();
(async () => {
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch();
for (const theme of ["dark", "light"]) for (const w of [360, 768, 1280]) {
const c = await b.newContext({ viewport: { width: w, height: 900 }, reducedMotion: "reduce" });
await c.addInitScript(t => { try { localStorage.setItem("ha-theme", t); } catch (e) {} }, theme);
for (const pg of pages) {
const p = await c.newPage();
try {
await p.goto(base + pg, { waitUntil: "networkidle" });
await p.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}" });
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(400);
const name = pg.replace(/[\/.]/g, "_") + "-" + w + "-" + theme;
await p.screenshot({ path: out + "/" + name + ".png", fullPage: true });
if (w === 360 && pg === "index.html") {
const m = await p.$("#menuBtn");
if (m) { try { await m.click({ timeout: 500 }); await p.waitForTimeout(300); await p.screenshot({ path: out + "/" + name + "-menu.png" }); } catch (e) {} }
}
} catch (e) { console.log("skip " + pg + ": " + e.message); }
await p.close();
}
await c.close();
}
await b.close();
console.log("shots: " + fs.readdirSync(out).length);
})();
