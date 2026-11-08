#!/usr/bin/env node
"use strict";
const { chromium } = require("playwright");
const fs = require("fs");
const base = process.argv[2] || "http://localhost:8765/";
const out = process.argv[3] || "shots";
(async () => {
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch();
for (const theme of ["dark", "light"]) for (const w of [360, 768, 1280]) {
const c = await b.newContext({ viewport: { width: w, height: 900 } });
await c.addInitScript((t) => { try { localStorage.setItem("ha-theme", t); } catch (e) {} }, theme);
for (const pg of ["index", "compare", "finder"]) {
const p = await c.newPage();
await p.goto(base + pg + ".html", { waitUntil: "networkidle" });
await p.screenshot({ path: `${out}/${pg}-${w}-${theme}.png`, fullPage: true });
await p.close();
}
await c.close();
}
await b.close();
console.log("screenshots written to " + out);
})();
