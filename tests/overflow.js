const { chromium } = require("playwright");
const base = process.argv[2] || "http://localhost:8765/";
const pages = [
"index.html",
"compare.html",
"finder.html",
"archive.html","setup.html","apply.html","files.html","evidence.html","faq.html",
"changelog.html",
"docs/index.html",
"docs/EVIDENCE.html",
"docs/OPEN.html",
"docs/CHANGELOG.html",
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
try {
await p.goto(base + pg, { waitUntil: "load" });
await p.waitForTimeout(500);
} catch (e) {
console.log("LOAD FAIL", pg, w, e.message);
bad++;
await p.close();
continue;
}
const r = await p.evaluate(() => {
const W = innerWidth,
o = [];
document.querySelectorAll("body *").forEach((e) => {
if (
e.closest("svg") ||
e.closest(".tw,.dtabs,.snd,.seg,pre,[data-scroll]")
)
return;
const s = getComputedStyle(e);
if (s.position === "fixed" || s.display === "none") return;
const r = e.getBoundingClientRect();
if (r.width && r.right > W + 1)
o.push(
(e.id
? "#" + e.id
: e.tagName.toLowerCase() +
"." +
String(e.className).split(" ")[0]) +
" " +
Math.round(r.right),
);
});
return {
sw: document.documentElement.scrollWidth,
W,
o: [...new Set(o)].slice(0, 4),
};
});
if (r.sw > r.W || r.o.length) {
bad++;
console.log(
"OVERFLOW",
pg,
w,
th,
"scrollWidth",
r.sw,
r.o.join(", "),
);
}
await p.close();
}
await c.close();
}
await b.close();
console.log(
bad
? bad + " problem(s)"
: "overflow: all pages pass at 320-1440, dark+light",
);
process.exit(bad ? 1 : 0);
})();
