const { chromium } = require("playwright");
const base = process.argv[2] || "http://localhost:8765/";
const pages = [
"index.html",
"compare.html",
"finder.html",
"archive.html",
"changelog.html",
];
(async () => {
const b = await chromium.launch();
let bad = 0;
for (const w of [320, 375, 768, 1024, 1440])
for (const th of ["dark", "light"]) {
const c = await b.newContext({ viewport: { width: w, height: 800 } });
await c.addInitScript((t) => {
try {
localStorage.setItem("ha-theme", t);
} catch (e) {}
}, th);
for (const pg of pages) {
const p = await c.newPage();
await p.goto(base + pg, { waitUntil: "load" });
await p.waitForTimeout(400);
const r = await p.evaluate(() => {
const f = document.querySelector(".sf-in");
if (!f) return { err: "no footer" };
const sr = document.querySelector(".sf").getBoundingClientRect(),
mid = sr.left + sr.width / 2,
off = [];
const vis = (e) =>
getComputedStyle(e).display !== "none" &&
e.getBoundingClientRect().width;
f.querySelectorAll(".sf-mark,.n-ver,.sf-e,.sf-c,.sf-l").forEach(
(e) => {
if (!vis(e)) return;
const q =
e.tagName === "P"
? (() => {
const g = document.createRange();
g.selectNodeContents(e);
return g.getBoundingClientRect();
})()
: e.getBoundingClientRect();
let cx = q.left + q.width / 2;
if (e.classList.contains("sf-e")) {
const g = document.createRange();
g.selectNodeContents(e);
const rs = g.getClientRects();
if (rs.length !== 1) return;
cx = (rs[0].left - 14 + rs[0].right) / 2;
}
if (e.classList.contains("sf-l")) {
const a = e.querySelectorAll("a");
cx =
(a[0].getBoundingClientRect().left +
a[a.length - 1].getBoundingClientRect().right) /
2;
}
if (Math.abs(cx - mid) > 1)
off.push(e.className + " " + Math.round(cx - mid) + "px");
},
);
const logo = [...f.querySelectorAll(".sf-logo")].filter(vis).length;
const imgOk = [...f.querySelectorAll(".sf-logo")]
.filter(vis)
.every((i) => i.complete && i.naturalWidth > 0);
return {
off,
logo,
imgOk,
links: f.querySelectorAll(".sf-l a").length,
over: document.documentElement.scrollWidth > innerWidth,
};
});
if (
r.err ||
r.off.length ||
r.logo !== 1 ||
!r.imgOk ||
r.links !== 2 ||
r.over
) {
bad++;
console.log("FOOTER", pg, w, th, JSON.stringify(r));
}
await p.close();
}
await c.close();
}
await b.close();
console.log(
bad
? bad + " problem(s)"
: "footer: centred, one logo per theme, 2 links, no overflow at 320-1440",
);
process.exit(bad ? 1 : 0);
})();
