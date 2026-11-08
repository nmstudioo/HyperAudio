#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const exists = (p) => fs.existsSync(path.join(root, p));
const fail = [];
const need = (ok, message) => { if (!ok) fail.push(message); };
const index = read("site/index.html");
const app = read("site/assets/js/app.js");
const pages = read("site/assets/js/pages.js");
const nav = read("site/assets/js/nav.js");
const chart = read("site/assets/js/chart.js");
const css = read("site/assets/css/site.css");
const sw = read("site/sw.js");
const profileData = JSON.parse(read("site/data/profiles.json"));
const html = ["index", "compare", "finder", "archive", "changelog", "404"].map((n) => [n, read(`site/${n}.html`)]);
need(!exists("site/assets/js/v7-ui.js") && !exists("site/assets/css/v7-ui.css"), "overlay files must stay merged into app.js / site.css");
html.forEach(([n, s]) => {
need(!/v7-ui\.(js|css)/.test(s), `${n}.html still references the overlay`);
need(!/fonts\.g(oogleapis|static)\.com/.test(s), `${n}.html still loads Google Fonts`);
need(s.includes("Content-Security-Policy"), `${n}.html has no CSP meta`);
need(s.includes("assets/css/fonts.css"), `${n}.html does not load fonts.css`);
});
need(sw.includes("assets/css/fonts.css") && !sw.includes("v7-ui"), "service worker shell is out of date");
need(/UI_VERSION\s*=\s*'7\./.test(sw), "service worker must carry its own UI_VERSION");
["plus-jakarta-sans-latin-400-normal", "plus-jakarta-sans-latin-600-normal", "plus-jakarta-sans-latin-800-normal", "jetbrains-mono-latin-400-normal", "jetbrains-mono-latin-700-normal"].forEach((f) => {
need(exists(`site/assets/fonts/${f}.woff2`), `font file missing: ${f}.woff2 (run tools/fetch_fonts.sh)`);
need(read("site/assets/css/fonts.css").includes(f), `fonts.css does not reference ${f}`);
});
need(index.indexOf('class="steps3"') < index.indexOf('class="cmp-hook"'), "response chart must come after profile selection");
need(index.includes('id="dock"') && index.includes('id="cmpSmooth"') && index.includes('id="cmpOvl"'), "dock, smoothing or overlay hook is missing");
need(index.includes('id="filesVersion"') && index.includes('id="profileSumsLink"'), "release label hooks are missing");
need(!index.includes("Offline + author device test"), "stale evidence badge remains");
need(!index.includes("Tested on the author's phone"), "unqualified device-test claim remains");
need(!index.includes("Swipe to see all"), "stale swipe instruction remains");
need(!index.includes('tabindex="0" id="cmpChart" tabindex="0"'), "duplicate chart tabindex remains");
need(nav.includes("no acoustic measurement recorded"), "footer evidence copy is not qualified");
need(app.includes("DATA.version"), "release statistic is not data-driven");
need(app.includes("RMS target error") && app.includes("function metrics("), "profile metrics must be rendered by app.js");
need(app.includes("function evChips(") && app.includes("loadEv"), "shared evidence chip component is missing");
need(!app.includes("MutationObserver") && !/MutationObserver/.test(pages), "no DOM patching via MutationObserver");
need(pages.includes("Use this profile"), "finder recommendation action is missing");
need(pages.includes("syncDeviceOptions"), "same-device comparison constraint is missing");
need(chart.includes("c.yr") && chart.includes("c.bands") && chart.includes("_read"), "chart needs fixed range, bands and spoken readout");
need(!chart.includes("respDb"), "dead respDb code is back");
need(chart.includes("t: 22"), "chart top margin must leave room for the dB unit label");
["@media (max-width: 480px)", "#getSt:empty", "grid-template-areas", "ol.why", ".v7-dock", ".evc", "prefers-reduced-motion"].forEach((k) => need(css.includes(k), `site.css is missing ${k}`));
need(profileData.version === read("VERSION").trim(), "profiles.json version must equal VERSION");
need(profileData.profiles.length === 6, "stable profile set changed unexpectedly");
need(profileData.profiles.every((p) => p.files.length === 3), "a stable profile no longer has its matched three-file set");
need(profileData.profiles.every((p) => p.stats && [p.stats.rms, p.stats.chainMax, p.stats.sections, p.stats.irsPeak].every((v) => Number.isFinite(Number(v)))), "profile metric fields are missing or non-finite");
if (fail.length) {
console.error(fail.map((x) => "FAIL " + x).join("\n"));
process.exit(1);
}
console.log("v7 UI contract: all checks passed");
