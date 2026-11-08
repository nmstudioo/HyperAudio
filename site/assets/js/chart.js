(function () {
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = (s) =>
String(s).replace(
/[&<>"']/g,
(c) =>
({
"&": "&amp;",
"<": "&lt;",
">": "&gt;",
'"': "&quot;",
"'": "&#39;",
})[c],
);
const fmtF = (f) =>
f >= 1000
? (f / 1000).toFixed(f >= 10000 ? 1 : 2).replace(/\.?0+$/, "") + " kHz"
: Math.round(f * 10) / 10 + " Hz";
const respDb = () => 0;

/* == chart == */
function interp(p, f) {
if (f < p[0][0] || f > p[p.length - 1][0]) return null;
for (let i = 1; i < p.length; i++)
if (f <= p[i][0]) {
const a = p[i - 1],
b = p[i],
t = Math.log(f / a[0]) / Math.log(b[0] / a[0]);
return a[1] + (b[1] - a[1]) * t;
}
return p[p.length - 1][1];
}
function smooth(P) {
const n = P.length;
if (n < 3) return P.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join("");
const dx = [], m = [], t = new Array(n);
for (let i = 0; i < n - 1; i++) {
dx[i] = P[i + 1][0] - P[i][0] || 1e-6;
m[i] = (P[i + 1][1] - P[i][1]) / dx[i];
}
t[0] = m[0];
t[n - 1] = m[n - 2];
for (let i = 1; i < n - 1; i++) t[i] = m[i - 1] * m[i] <= 0 ? 0 : (m[i - 1] + m[i]) / 2;
for (let i = 0; i < n - 1; i++) {
if (m[i] === 0) { t[i] = t[i + 1] = 0; continue; }
const a = t[i] / m[i], b = t[i + 1] / m[i], h = a * a + b * b;
if (h > 9) { const k = 3 / Math.sqrt(h); t[i] = k * a * m[i]; t[i + 1] = k * b * m[i]; }
}
let d = "M" + P[0][0].toFixed(1) + " " + P[0][1].toFixed(1);
for (let i = 0; i < n - 1; i++) {
const h = dx[i] / 3;
d += "C" + (P[i][0] + h).toFixed(1) + " " + (P[i][1] + t[i] * h).toFixed(1) + " " + (P[i + 1][0] - h).toFixed(1) + " " + (P[i + 1][1] - t[i + 1] * h).toFixed(1) + " " + P[i + 1][0].toFixed(1) + " " + P[i + 1][1].toFixed(1);
}
return d;
}
function unav(host, c, msg) {
host._c = c;
host._s = null;
host._pin = false;
host.innerHTML = `<div class="unav" role="img" aria-label="Chart unavailable"><svg class="ic" aria-hidden="true"><use href="#i-warn"/></svg><b>Chart unavailable</b><span>${msg}</span></div>`;
}
function drawChart(host, c) {
host._pin = false;
try {
const ok =
c &&
Array.isArray(c.series) &&
c.series.some(
(s) =>
s &&
Array.isArray(s.pts) &&
s.pts.length > 1 &&
s.pts.every((p) => Number.isFinite(p[0]) && Number.isFinite(p[1])),
);
if (!ok)
return unav(
host,
c,
"The response could not be computed for this selection.",
);
if (c.series.every((s) => s.hidden))
return unav(
host,
c,
"Every curve is hidden. Turn one on in the legend.",
);
drawChartRaw(host, c);
} catch (e) {
console.error(e);
unav(host, c, "Drawing this chart failed.");
}
}
function drawChartRaw(host, c) {
host._c = c;
const W = Math.max(260, host.clientWidth - 16),
H = Math.round(Math.max(230, Math.min(380, W * 0.5))),
m = { l: 38, r: 10, t: 22, b: 24 };
const [x0, x1] = c.xr || [20, 20000];
let lo = 1e9,
hi = -1e9;
c.series.forEach((s) =>
s.pts.forEach((p) => {
lo = Math.min(lo, p[1]);
hi = Math.max(hi, p[1]);
}),
);
const y0 = Math.floor((lo - 1) / 3) * 3,
y1 = Math.ceil((hi + 1) / 3) * 3,
L = Math.log10,
X = (v) => m.l + ((L(v) - L(x0)) / (L(x1) - L(x0))) * (W - m.l - m.r),
Y = (v) => m.t + ((y1 - v) / (y1 - y0)) * (H - m.t - m.b);
host._s = { X, Y, W, H, m, x0, x1 };
let g = `<rect x="${m.l}" y="${m.t}" width="${W - m.l - m.r}" height="${H - m.t - m.b}" rx="8" fill="url(#pb${host.id})"/>`,
df = `<linearGradient id="pb${host.id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--tx)" stop-opacity=".06"/><stop offset="1" stop-color="var(--tx)" stop-opacity=".01"/></linearGradient><filter id="gl${host.id}" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur stdDeviation="4"/></filter>`;
const ha = c.series.some((x) => x.area);
const ys = y1 - y0 > 24 ? 6 : 3;
const P = (v) => Math.round(v) + 0.5;
const pw = W - m.l - m.r, bh = H - m.t - m.b;
[[20, 250, "BASS"], [250, 4000, "MIDS"], [4000, 20000, "TREBLE"]].forEach((z, i) => {
const a0 = Math.max(z[0], x0), a1 = Math.min(z[1], x1);
if (a1 <= a0) return;
const xa = X(a0), xb = X(a1);
if (i === 1) g += `<rect x="${xa}" y="${m.t}" width="${xb - xa}" height="${bh}" fill="var(--tx)" opacity=".025"/>`;
if (xb - xa > 46) g += `<text x="${(xa + xb) / 2}" y="${m.t + 13}" text-anchor="middle" font-size="9" letter-spacing=".16em" fill="var(--mut)" opacity=".7">${z[2]}</text>`;
});
for (let v = y0; v <= y1; v += ys)
g += `<line x1="${m.l}" x2="${W - m.r}" y1="${P(Y(v))}" y2="${P(Y(v))}" stroke="${v === 0 ? "var(--tx)" : "var(--tx)"}" stroke-opacity="${v === 0 ? 0.3 : 0.07}" stroke-width="1"/><text x="${m.l - 8}" y="${Y(v) + 3.5}" text-anchor="end" font-size="10.5" fill="${v === 0 ? "var(--tx2)" : "var(--mut)"}" style="font-variant-numeric:tabular-nums">${v > 0 ? "+" : v < 0 ? "\u2212" : ""}${Math.abs(v)}</text>`;
[20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
.filter((v) => v >= x0 * 0.999 && v <= x1 * 1.001)
.forEach((v) => {
const major = v === 100 || v === 1000 || v === 10000;
g += `<line y1="${m.t}" y2="${H - m.b}" x1="${P(X(v))}" x2="${P(X(v))}" stroke="var(--tx)" stroke-opacity="${major ? 0.1 : 0.045}"/><text x="${X(v)}" y="${H - 7}" text-anchor="middle" font-size="10.5" fill="${major ? "var(--tx2)" : "var(--mut)"}">${v >= 1000 ? v / 1000 + "k" : v}</text>`;
});
g += `<text x="${m.l - 8}" y="${m.t - 13}" text-anchor="end" font-size="9" letter-spacing=".12em" fill="var(--mut)">dB</text>`;
c.series.forEach((s, si) => {
if (s.hidden) return;
if (s.area) {
df += `<linearGradient id="ag${host.id}${si}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${s.color}" stop-opacity=".30"/><stop offset=".55" stop-color="${s.color}" stop-opacity=".08"/><stop offset="1" stop-color="${s.color}" stop-opacity="0"/></linearGradient>`;
const z = Y(Math.min(Math.max(0, y0), y1)),
px = s.pts.map((p) => X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1));
g += `<path d="M${X(s.pts[0][0])} ${z}L${smooth(s.pts.map((p) => [X(p[0]), Y(p[1])])).slice(1)}L${X(s.pts[s.pts.length - 1][0])} ${z}Z" fill="url(#ag${host.id}${si})" clip-path="url(#cp${host.id})"/>`;
}
const xy = s.pts.map((p) => [X(Math.min(Math.max(p[0], x0), x1)), Y(p[1])]),
d = s.dots ? xy.map((q, i) => (i ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1)).join("") : smooth(xy);
const pri = !!s.area;
if (pri && !s.dots)
g += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${(s.w || 2) + 4}" stroke-linecap="round" opacity=".5" filter="url(#gl${host.id})" clip-path="url(#cp${host.id})"/>`;
g += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.w || 2}" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""} stroke-linejoin="round" stroke-linecap="round" ${ha && !pri && !s.dots ? 'opacity=".7"' : ""} clip-path="url(#cp${host.id})"/>`;
if (s.dots)
s.pts.forEach(
(p) =>
(g += `<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="4" fill="var(--deep)" stroke="${s.color}" stroke-width="2"/>`),
);
});
(c.marks || []).forEach((k) => {
if (k.hidden || k.fc < x0 || k.fc > x1) return;
const y = Y(
respDb(
c.filters.filter((f) => !f.hidden),
k.fc,
),
);
const r = k.hl ? 10 : 8;
g += `<line x1="${X(k.fc)}" x2="${X(k.fc)}" y1="${Y(0)}" y2="${y}" stroke="${k.col}" stroke-width="1" opacity=".45"/><circle cx="${X(k.fc)}" cy="${y}" r="${r}" fill="${k.col}" stroke="${k.hl ? "var(--tx)" : "var(--deep)"}" stroke-width="2"/><text x="${X(k.fc)}" y="${y + 3.5}" text-anchor="middle" font-size="10" font-weight="700" fill="var(--bg)">${k.n}</text>`;
});
g += `<line id="cur" y1="${m.t}" y2="${H - m.b}" stroke="var(--tx)" stroke-opacity=".35" style="display:none"/><g id="dots" pointer-events="none"></g>`;
host.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" role="img" aria-label="${c.label}"><defs>${df}<clipPath id="cp${host.id}"><rect x="${m.l}" y="${m.t}" width="${W - m.l - m.r}" height="${H - m.t - m.b}"/></clipPath></defs>${g}<rect x="${m.l}" y="${m.t}" width="${W - m.l - m.r}" height="${H - m.t - m.b}" fill="transparent" id="hit"/></svg><div class="tip" aria-hidden="true"></div>`;
}
function hover(host, fx) {
const s = host._s,
c = host._c;
if (!s) return;
const f = Math.min(
s.x1,
Math.max(
s.x0,
s.x0 * Math.pow(s.x1 / s.x0, (fx - s.m.l) / (s.W - s.m.l - s.m.r)),
),
),
tip = $(".tip", host),
cur = $("#cur", host);
let rows = "",
dots = "";
let RV =
c.ref != null && c.series[c.ref] ? interp(c.series[c.ref].pts, f) : null;
if (!Number.isFinite(RV)) RV = null;
c.series.forEach((v, vi) => {
if (v.hidden) return;
const d = interp(v.pts, f);
if (
d == null ||
!Number.isFinite(d) ||
(v.dots && !v.pts.some((p) => Math.abs(Math.log2(p[0] / f)) < 0.35))
)
return;
if (Number.isFinite(d))
dots += `<circle cx="${s.X(f).toFixed(1)}" cy="${s.Y(d).toFixed(1)}" r="9" fill="${v.color}" opacity=".18"/><circle cx="${s.X(f).toFixed(1)}" cy="${s.Y(d).toFixed(1)}" r="4.5" fill="${v.color}" stroke="var(--bg)" stroke-width="2"/>`;
rows += `<div><span><svg class="tsw" viewBox="0 0 16 8" aria-hidden="true"><line x1="0" x2="16" y1="4" y2="4" stroke="${v.color}" stroke-width="2.5" ${v.dash ? `stroke-dasharray="${v.dash}"` : ""}/></svg>${v.label}</span><b>${d > 0 ? "+" : ""}${d.toFixed(1)} dB${RV != null && vi !== c.ref ? ` <small>(${d - RV >= 0 ? "+" : ""}${(d - RV).toFixed(1)})</small>` : ""}</b></div>`;
});
let near = null,
nd = 0.3;
(c.marks || []).forEach((k) => {
const d = Math.abs(Math.log2(k.fc / f));
if (!k.hidden && d < nd) {
nd = d;
near = k;
}
});
let dlt = "";
if (c.delta) {
const A = interp(c.series[c.delta[0]].pts, f),
B = interp(c.series[c.delta[1]].pts, f);
if (A != null && B != null)
dlt = `<div class="dl"><span>Change (after − before)</span><b>${B - A >= 0 ? "+" : ""}${(B - A).toFixed(1)} dB</b></div>`;
}
tip.innerHTML = `<b>${fmtF(f)}</b>${rows}${dlt}${near ? `<div style="margin-top:4px;color:var(--tx2)"><span>Filter ${near.n} · ${near.type.toUpperCase()}</span><b>${near.q != null ? "Q " + near.q : ""}</b></div><div style="color:var(--tx2)"><span>${fmtF(near.fc)}</span><b>${near.g != null ? (near.g > 0 ? "+" : "") + near.g + " dB" : ""}</b></div>` : ""}${host._pin ? '<div class="pin">Pinned · tap outside to clear</div>' : ""}`;
tip.style.display = "block";
const x = s.X(f),
w = tip.offsetWidth;
let lx = Math.min(Math.max(4, x - w / 2), host.clientWidth - w - 4);
const hr0 = host.getBoundingClientRect(),
vl = hr0.left + lx;
if (vl < 4) lx += 4 - vl;
else if (vl + w > innerWidth - 4) lx -= vl + w - (innerWidth - 4);
tip.style.left = lx + "px";
tip.style.top =
Math.max(4, Math.min(12, host.clientHeight - tip.offsetHeight - 4)) +
"px";
cur.setAttribute("x1", x);
cur.setAttribute("x2", x);
cur.style.display = "";
const dg = $("#dots", host);
if (dg) dg.innerHTML = dots;
host._f = f;
}
function wire(host) {
const mv = (e) => {
const sv = $("svg", host),
s = host._s;
if (!sv || !s) return;
const r = sv.getBoundingClientRect();
hover(host, ((e.clientX - r.left) * s.W) / r.width);
};
const hide = () => {
host._pin = false;
const t = $(".tip", host);
if (t) t.style.display = "none";
const q = $("#cur", host);
if (q) q.style.display = "none";
const dd = $("#dots", host);
if (dd) dd.innerHTML = "";
};
host.addEventListener("pointermove", (e) => {
if (host._pin && e.pointerType !== "mouse" && !e.buttons) return;
mv(e);
});
host.addEventListener("pointerdown", (e) => {
if (e.pointerType !== "mouse") host._pin = true;
mv(e);
});
host.addEventListener("pointerleave", () => {
if (!host._pin) hide();
});
document.addEventListener("pointerdown", (e) => {
if (host._pin && !host.contains(e.target)) hide();
});
host.addEventListener("keydown", (e) => {
if (e.key === "Escape") {
hide();
return;
}
const s = host._s;
if (!s || !["ArrowLeft", "ArrowRight"].includes(e.key)) return;
e.preventDefault();
const f =
(host._f || Math.sqrt(s.x0 * s.x1)) *
Math.pow(2, (e.key === "ArrowLeft" ? -1 : 1) * 0.15);
hover(host, s.X(Math.min(s.x1, Math.max(s.x0, f))));
});
host.addEventListener("blur", () => {
if (!host._pin) {
const t = $(".tip", host);
if (t) t.style.display = "none";
}
});
let rw = host.clientWidth;
new ResizeObserver(() => {
const w = host.clientWidth;
if (!host._c || !w || w === rw) return;
rw = w;
cancelAnimationFrame(host._raf);
host._raf = requestAnimationFrame(() => {
host._raf = 0;
drawChart(host, host._c);
});
}).observe(host);
}
function legend(el, c, redraw) {
el.innerHTML = c.series
.map(
(s, i) =>
`<button type="button" aria-pressed="${!s.hidden}" data-i="${i}"><svg viewBox="0 0 22 8" aria-hidden="true"><line x1="1" x2="21" y1="4" y2="4" stroke="${s.color}" stroke-width="2.5" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""}/>${s.dots ? `<circle cx="11" cy="4" r="3" fill="var(--deep)" stroke="${s.color}" stroke-width="1.5"/>` : ""}</svg>${s.label}</button>`,
)
.join("");
el.onclick = (e) => {
const b = e.target.closest("button");
if (!b) return;
const s = c.series[b.dataset.i];
s.hidden = !s.hidden;
b.setAttribute("aria-pressed", !s.hidden);
redraw();
};
}
window.HAChart = { drawChart, wire, legend, fmtF, interp, smooth };
})();
