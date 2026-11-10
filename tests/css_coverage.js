#!/usr/bin/env node
"use strict";
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const base = process.argv[2] || "http://localhost:8765/";
const out = process.argv[3] || "css-coverage.json";
const SITE = path.join(__dirname, "..", "site");
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
e.isDirectory() ? (e.name === "downloads" ? [] : walk(path.join(d, e.name))) : [path.join(d, e.name)]);
const pages = walk(SITE).filter(f => f.endsWith(".html") && !f.endsWith("404.html")).map(f => path.relative(SITE, f)).sort();
const files = ["base.css", "nav.css", "docs.css", "tokens.css", "fonts.css"];
const rules = {};
(async () => {
const b = await chromium.launch();
for (const theme of ["dark", "light"]) for (const w of [360, 768, 1280]) {
const c = await b.newContext({ viewport: { width: w, height: 900 } });
await c.addInitScript(t => { try { localStorage.setItem("ha-theme", t); } catch (e) {} }, theme);
for (const pg of pages) {
const p = await c.newPage();
try {
await p.goto(base + pg, { waitUntil: "networkidle" });
for (const sel of ["button", "summary", "[role=tab]", ".dl-row", ".dtabs a"]) {
const els = await p.$$(sel);
for (const e of els.slice(0, 12)) { try { await e.click({ timeout: 300, trial: false }); } catch (x) {} }
}
const res = await p.evaluate(() => {
const o = [];
for (const ss of document.styleSheets) {
let rs; try { rs = ss.cssRules; } catch (e) { continue; }
const name = (ss.href || "").split("/").pop();
const walkRules = (list, media) => { for (const r of list) {
if (r.cssRules && r.selectorText === undefined) { walkRules(r.cssRules, r.conditionText || media); continue; }
if (!r.selectorText) continue;
let hit = false;
for (const s of r.selectorText.split(",")) {
const q = s.trim().replace(/::?[a-z-]+(\([^)]*\))?/gi, m => /^::?(not|is|where|has|nth-[a-z-]+)\b/i.test(m) ? m : "");
try { if (q && document.querySelector(q)) { hit = true; break; } } catch (e) { hit = true; break; }
}
o.push([name, r.selectorText, hit]);
} };
walkRules(rs, "");
}
return o;
});
for (const [f, s, hit] of res) { (rules[f] = rules[f] || {}); rules[f][s] = rules[f][s] || hit; }
} catch (e) { console.log("skip " + pg + ": " + e.message); }
await p.close();
}
await c.close();
}
await b.close();
const rep = { pages, files: {} };
for (const f of Object.keys(rules)) {
const all = Object.keys(rules[f]), never = all.filter(s => !rules[f][s]);
rep.files[f] = { rules: all.length, never_matched: never.length, selectors: never };
}
fs.writeFileSync(out, JSON.stringify(rep, null, 1));
for (const f of Object.keys(rep.files)) console.log(f, rep.files[f].rules + " rules", rep.files[f].never_matched + " never matched");
})();
