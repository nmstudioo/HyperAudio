#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const fail = [];
const index = read("site/index.html");
const app = read("site/assets/js/app.js");
const pages = read("site/assets/js/pages.js");
const nav = read("site/assets/js/nav.js");
const ui = read("site/assets/js/v7-ui.js");
const css = read("site/assets/css/v7-ui.css");
const seo = read("build/seo.py");
const sw = read("site/sw.js");
const profileData = JSON.parse(read("site/data/profiles.json"));

function need(ok, message) { if (!ok) fail.push(message); }
need(index.includes("assets/css/v7-ui.css"), "homepage does not load v7-ui.css");
need(index.includes("assets/js/v7-ui.js"), "homepage does not load v7-ui.js");
need(index.includes('id="filesVersion"'), "release label hook is missing");
need(index.includes('id="profileSumsLink"'), "profile checksum link hook is missing");
need(!index.includes('tabindex="0" id="cmpChart" tabindex="0"'), "duplicate chart tabindex remains");
need(!index.includes("Offline + author device test"), "stale evidence badge remains");
need(!index.includes("Tested on the author's phone"), "unqualified device-test claim remains");
need(!app.includes('"v6.0.0"'), "hardcoded old release value remains in stats");
need(app.includes("DATA.version"), "release statistic is not data-driven");
need(pages.includes("Use this profile"), "finder recommendation action is missing");
need(ui.includes("constrainComparison"), "same-device comparison constraint is missing");
need(ui.includes("RMS target error"), "profile metrics are missing");
need(ui.includes('setAttribute("role", "group")'), "profile metrics are not exposed as an accessible group");
need(ui.includes("tagText.nodeValue"), "release badge update must preserve its decorative marker");
need(profileData.profiles.every((p) => p.stats && [p.stats.rms, p.stats.chainMax, p.stats.sections, p.stats.irsPeak].every((v) => Number.isFinite(Number(v)))), "one or more profile metric fields are missing or non-finite");
need(nav.includes("no acoustic measurement recorded"), "footer evidence copy is not qualified");
need(!seo.includes("current 6.0.0"), "archive SEO still advertises 6.0.0 as current");
need(css.includes("@media (max-width: 480px)"), "mobile styling is missing");
need(sw.includes("assets/css/v7-ui.css"), "service worker does not precache the v7 stylesheet");
need(sw.includes("assets/js/v7-ui.js"), "service worker does not precache the v7 UI script");
need(css.includes("#getSt:empty"), "empty download status must not render a stray circle");
need(css.includes("grid-template-areas"), "wide-screen chooser layout is missing");
need(css.includes("ol.why"), "finder reasoning list must reset the .why link style");
need(!index.includes("Swipe to see all"), "stale swipe instruction remains (profile cards are not a carousel)");
need(read("site/assets/js/chart.js").includes("t: 22"), "chart top margin must leave room for the dB unit label");
need(profileData.version === "6.1.0", "this overlay must not silently bump the stable DSP release");
need(profileData.profiles.length === 6, "stable profile set changed unexpectedly");
need(profileData.profiles.every((p) => p.files.length === 3), "a stable profile no longer has its matched three-file set");

if (fail.length) {
  console.error(fail.map((x) => "FAIL " + x).join("\n"));
  process.exit(1);
}
console.log("v7 UI contract: all checks passed");
