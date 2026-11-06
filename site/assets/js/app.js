(function () {
"use strict";
const $ = (s, r = document) => r.querySelector(s),
$$ = (s, r = document) => [...r.querySelectorAll(s)];
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
const wb = (s) => esc(s).replace(/_/g, "_<wbr>");
const ic = (n, x = "") =>
`<svg class="ic" aria-hidden="true" ${x}><use href="#i-${n}"/></svg>`;
const kb = (n) => (n >= 1024 ? (n / 1024).toFixed(1) + " KB" : n + " B");
const fmtF = (f) => window.HAChart.fmtF(f);
const store = {
get(k) {
try {
return localStorage.getItem(k);
} catch (e) {
return null;
}
},
set(k, v) {
try {
localStorage.setItem(k, v);
} catch (e) {}
},
};
const KIND = {
eel: {
tag: "EEL",
label: "Script",
fmt: "EEL2",
ico: "code",
what: "Liveprog script",
},
irs: {
tag: "IRS",
label: "Impulse response",
fmt: "WAV · 32f",
ico: "wave",
what: "Convolver impulse response",
},
vdc: {
tag: "VDC",
label: "VDC filter",
fmt: "VDC",
ico: "eq",
what: "ViPER-DDC filter bank",
},
};
let DATA, PROF, prof, eqHost, cmpC;

/* == toast == */
function toast(msg, err) {
const box = $("#toasts"),
t = document.createElement("div");
t.className = "toast" + (err ? " err" : "");
t.textContent = msg;
box.appendChild(t);
setTimeout(() => t.remove(), 3200);
}
async function copyText(t, btn) {
let ok = false;
try {
await navigator.clipboard.writeText(t);
ok = true;
} catch (e) {
try {
const x = document.createElement("textarea");
x.value = t;
x.readOnly = true;
x.style.cssText = "position:fixed;opacity:0";
document.body.appendChild(x);
x.select();
ok = document.execCommand("copy");
x.remove();
} catch (y) {}
}
if (btn) {
btn.dataset.state = ok ? "done" : "error";
setTimeout(() => {
delete btn.dataset.state;
}, 1800);
}
ok
? toast("Copied")
: toast("Copy failed. Select the text and copy it manually.", true);
return ok;
}

/* == charts == */
function spark(c, W = 300, H = 56) {
const lo = Math.min(...c),
hi = Math.max(...c),
X = (i) => (i / (c.length - 1)) * W,
Y = (v) => 4 + ((hi - v) / (hi - lo || 1)) * (H - 8),
d = c
.map(
(v, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1),
)
.join(""),
z = Y(Math.min(Math.max(0, lo), hi));
return `<svg class="pv-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"><line x1="0" x2="${W}" y1="${z}" y2="${z}" stroke="var(--bd2)" stroke-dasharray="3 4" vector-effect="non-scaling-stroke"/><path d="${d} L${W} ${z} L0 ${z}Z" fill="var(--tx)" opacity=".07"/><path d="${d}" fill="none" stroke="var(--tx)" stroke-width="1.8" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>`;
}
function drawHero() {
const sv = $("#heroSvg"),
f = DATA.freq,
c = prof.curves.correction;
const Lg = Math.log10,
X = (v) => 40 + (460 * (Lg(v) - Lg(20))) / 3,
peak = Math.max(...c.map(Math.abs)),
mx = Math.max(9, Math.ceil(Math.min(18, peak) / 3) * 3),
k = 100 / mx,
Y = (g) => 150 - Math.max(-mx, Math.min(mx, g)) * k;
let pk = 0;
c.forEach((v, i) => {
if (f[i] >= 60 && f[i] <= 16000 && Math.abs(v) > Math.abs(c[pk])) pk = i;
if (f[pk] < 60 || f[pk] > 16000) pk = i;
});
const d = c
.map(
(v, i) =>
(i ? "L" : "M") + X(f[i]).toFixed(1) + " " + Y(v).toFixed(1),
)
.join(""),
px = X(f[pk]).toFixed(1),
py = Y(c[pk]).toFixed(1);
const lab = [
[20, "20"],
[100, "100"],
[1000, "1k"],
[10000, "10k"],
[20000, "20k"],
]
.map(
([v, t]) =>
`<text x="${X(v).toFixed(1)}" y="278" ${v === 20 ? 'text-anchor="start"' : v === 20000 ? 'text-anchor="end"' : ""}>${t}</text>`,
)
.join("");
sv.innerHTML = `<defs><linearGradient id="hvA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--acc)" stop-opacity=".30"/><stop offset="1" stop-color="var(--acc)" stop-opacity="0"/></linearGradient></defs>
 <g stroke="var(--bd)" fill="none"><path d="M40 50H500M40 100H500M40 200H500M40 250H500" stroke-dasharray="2 5"/><path d="M40 150H500" stroke="var(--bd2)"/></g>
 <path d="${d}L500 150L40 150Z" fill="url(#hvA)"/><path d="${d}" fill="none" stroke="var(--acc)" stroke-width="9" stroke-linecap="round" opacity=".12"/><path d="${d}" fill="none" stroke="var(--acc)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
 <line x1="${px}" x2="${px}" y1="40" y2="260" stroke="var(--tx)" stroke-opacity=".28"/><circle cx="${px}" cy="${py}" r="5" fill="var(--acc)" stroke="var(--bg)" stroke-width="2"/>
 <g font-family="var(--mono)" font-size="10" fill="var(--mut)" text-anchor="middle">${lab}<text x="34" y="${Y(mx) + 4}" text-anchor="end">+${mx}</text><text x="34" y="154" text-anchor="end">0</text><text x="34" y="${Y(-mx) + 4}" text-anchor="end">−${mx}</text></g>`;
const v = c[pk];
sv.setAttribute(
"aria-label",
`Correction curve for ${prof.name}: ${v > 0 ? "largest boost" : "deepest cut"} ${Math.abs(v).toFixed(1)} dB near ${fmtF(f[pk])}`,
);
$("#heroRead").innerHTML =
`<b>${fmtF(f[pk])}</b> ${v > 0 ? "+" : "−"}${Math.abs(v).toFixed(1)} dB ${v > 0 ? "lift" : "cut"}`;
$("#heroOut").textContent =
prof.device === "iem" ? "Wired 3.5 mm" : "Internal speaker";
}
function drawCompare() {
const f = DATA.freq,
cv = prof.curves,
pts = (a) => a.map((v, i) => [f[i], v]);
cmpC = {
label: "Predicted response",
ref: 2,
delta: [0, 1],
series: [
{
label: "Before (device raw)",
pts: pts(cv.raw),
color: "var(--s-raw)",
w: 1.6,
},
{
label: "After (with profile)",
pts: pts(cv.predicted),
color: "var(--acc)",
w: 2.6,
area: true,
},
{
label: "Target",
pts: pts(cv.target),
color: "var(--tx)",
w: 1.6,
dash: "5 4",
},
],
};
window.HAChart.drawChart(eqHost, cmpC);
window.HAChart.legend($("#cmpLegend"), cmpC, () =>
window.HAChart.drawChart(eqHost, cmpC),
);
$("#cmpNote span").textContent =
prof.device === "spk"
? "Computed from the raw and target files, level-matched at 1 to 6 kHz. The speaker boost is capped at +8 dB, so the curve stays below the target between 100 and 2000 Hz by design."
: "Computed from the raw and target files, level-matched at 300 Hz to 3 kHz. This is a calculation, not an acoustic measurement.";
const pe = cv.predicted.map((v, i) => v - cv.target[i]),
sel = f
.map((x, i) =>
x >= (prof.device === "iem" ? 30 : 100) && x <= 16000 ? i : -1,
)
.filter((i) => i >= 0),
r = Math.sqrt(sel.reduce((s, i) => s + pe[i] * pe[i], 0) / sel.length);
$("#cmpSum").textContent =
`${prof.name}: RMS difference from the target ${r.toFixed(1)} dB.`;
}

/* == step 1 and 2 == */
const byDev = (d) => PROF.filter((p) => p.device === d);
function renderOuts() {
const e = prof.device === "iem";
$("#outs").innerHTML = [
["iem", "KZ EDX Pro", "In-ear · wired 3.5 mm", "phones"],
["spk", "Redmi 12 Speaker", "Internal speaker", "device"],
]
.map(
([k, n, s, i]) =>
`<button type="button" class="out-c" data-out="${k}" aria-pressed="${(k === "iem") === e}">${ic(i)}<span><b>${n}</b><small>${s}</small></span><em>${byDev(k).length} profiles</em></button>`,
)
.join("");
}
function renderSnd() {
const sc = $("#snd").scrollLeft;
$("#snd").innerHTML = byDev(prof.device)
.map(
(p) =>
`<button type="button" class="snd-c" data-p="${p.id}" aria-pressed="${p.id === prof.id}"><span class="snd-h"><b>${esc(p.short)}</b>${p.id === prof.id ? '<i class="act">Active</i>' : ""}</span>${spark(p.curves.correction)}<span class="snd-d">${esc(p.desc)}</span></button>`,
)
.join("");
$("#snd").scrollLeft = sc;
}

/* == step 3 == */
function renderGet() {
const fl = prof.files
.slice()
.sort(
(a, b) =>
["vdc", "irs", "eel"].indexOf(a.kind) -
["vdc", "irs", "eel"].indexOf(b.kind),
);
$("#getTitle").textContent = "Your files · " + prof.name;
$("#fileList").innerHTML =
fl
.map(
(x) =>
`<div class="f-row"><span class="fi">${KIND[x.kind].tag}</span><div><span class="f-t">${KIND[x.kind].what}</span><b>${wb(x.name)}</b><span class="d">${KIND[x.kind].fmt} · ${kb(x.bytes)}</span></div></div>`,
)
.join("") +
`<ul class="pfacts">${prof.facts.map(([k, v]) => `<li><span>${esc(k)}</span><b>${esc(v)}</b></li>`).join("")}</ul>`;
const g = $("#getBtn");
g.href = prof.bundle.path;
g.setAttribute("download", prof.bundle.name);
$("#evBadge").innerHTML =
`<span class="evt-b ok">Offline-verified</span><span class="evt-b dev">Device: user-reported</span><small>${esc(prof.evidence.deviceNote)} Not measured acoustically.</small>`;
$("#verLine span").innerHTML =
`SHA-256: <code class="sha">${prof.bundle.sha256.slice(0, 12)}…</code><button type="button" class="cp-b" data-ct="${prof.bundle.sha256}" aria-label="Copy the full SHA-256">${ic("copy", 'style="width:15px;height:15px"')}<span class="sr">Copy</span></button>`;
}

/* == apply checklist == */
const pgKey = () => "ha-prog-" + prof.id;
function applyItems() {
const f = (k) => prof.files.find((x) => x.kind === k).name;
return [
{
t: "Turn on ViPER-DDC and load the VDC",
d: "Open ViPER-DDC, switch it on and choose this file. It runs first.",
v: [["File", f("vdc"), f("vdc")]],
},
{
t: "Turn on the Convolver and load the impulse response",
d: "Switch the Convolver on, import the file and keep the optimization on Original.",
v: [
["File", f("irs"), f("irs")],
["Optimization", "Original", null],
],
},
{
t: "Turn on Live programmable DSP and load the script",
d:
'Pick the script. The app lists it as "' +
prof.script +
'". Its sliders are: ' +
prof.sliders.join(", ") +
".",
v: [["File", f("eel"), f("eel")]],
},
{
t: "Keep every gain at zero",
d: "The VDC and impulse response already include their level. Do not add preamp, and leave the post gain alone.",
v: [
["Convolver preamp", "0.00 dB", "0.00"],
["Post gain", "0.00 dB", "0.00"],
],
},
{
t: "Leave True Peak Detect on",
d: "It is on by default and guards against inter-sample peaks. Turn it off only to diagnose crackling.",
v: [["True Peak Detect", "On", null]],
},
];
}
function renderApply() {
const it = applyItems(),
pg = JSON.parse(store.get(pgKey()) || "[]");
$("#chk").dataset.n = it.length;
$("#applyFor").textContent =
"Steps for " +
prof.name +
". The order in the app is VDC, then Convolver, then Liveprog.";
$("#chk").innerHTML = it
.map(
(x, i) =>
`<li class="${pg[i] ? "dn" : ""}"><label class="ck"><input type="checkbox" data-i="${i}" ${pg[i] ? "checked" : ""} aria-label="Done: ${esc(x.t)}"><span class="box">${ic("check")}</span></label><div class="ck-b"><h3>${esc(x.t)}</h3><p>${esc(x.d)}</p><div class="vals">${x.v.map(([k, v, c]) => `<span class="val${c ? "" : " nc"}"><span>${esc(k)}</span><code>${esc(v)}</code>${c ? `<button type="button" class="cp-b" data-ct="${esc(c)}" aria-label="Copy ${esc(c)}">${ic("copy", 'style="width:15px;height:15px"')}<span class="sr">Copy</span></button>` : ""}</span>`).join("")}</div></div></li>`,
)
.join("");
progUI(pg, it.length);
}
function progUI(pg, n) {
const nx = pg.findIndex((v) => !v);
$$("#chk li").forEach((li, i) =>
li.classList.toggle(
"nx",
nx === i || (nx < 0 && false) || (!pg.length && i === 0),
),
);
const d = pg.filter(Boolean).length;
$("#progBar").style.width = (n ? (d / n) * 100 : 0) + "%";
$("#progTxt").textContent = d + " of " + n + " done";
$("#doneBox").hidden = d < n;
$("#doneName").textContent = prof.name;
}
$("#chk").addEventListener("change", (e) => {
const i = +e.target.dataset.i;
if (Number.isNaN(i)) return;
const n = $$("#chk li").length,
pg = JSON.parse(store.get(pgKey()) || "[]");
while (pg.length < n) pg.push(false);
pg[i] = e.target.checked;
store.set(pgKey(), JSON.stringify(pg));
e.target.closest("li").classList.toggle("dn", e.target.checked);
progUI(pg, n);
});
$("#applyReset").onclick = () => {
store.set(pgKey(), "[]");
renderApply();
};

/* == files hub == */
function buildHub() {
const row = (p, x) => {
const k = KIND[x.kind];
return `<li class="dl-row" data-p="${p.id}" data-kind="${x.kind}" data-q="${esc((p.name + " " + x.name + " " + k.label + " " + p.device).toLowerCase())}"><span class="dl-ic">${ic(k.ico)}<em>${k.tag}</em></span>
  <div class="dl-main"><span class="dl-title">${esc(p.name)}</span><span class="dl-name" title="${esc(x.name)}">${wb(x.name.replace(/\.[a-z]+$/, ""))}<span class="ext">.${x.kind === "irs" ? "irs" : x.kind}</span></span><span class="dl-sub">${k.what}<span class="rec-tag">Recommended</span></span></div>
  <div class="dl-meta"><span class="chip">${k.fmt}</span><span class="dl-size">${kb(x.bytes)}</span></div>
  <div class="dl-act"><a class="btn sm${x.kind === "eel" ? " pri-soft" : ""}" href="${x.path}" download aria-label="Download ${esc(x.name)}" data-dl="${esc(x.name)}">${ic("download")}<span>Download</span></a></div>
  <details class="dl-more"><summary>${ic("chev", 'style="width:14px;height:14px"')}Details</summary><p class="dm">SHA-256 <code class="sha">${x.sha256}</code></p>${x.kind === "eel" ? `<p>Sliders: ${p.sliders.map(esc).join(", ")}.</p>` : ""}</details></li>`;
};
$("#dlGroups").innerHTML = PROF.map(
(p) =>
`<div class="dl-group" data-g="${p.id}"><div class="dl-gh"><span class="fico">${ic(p.device === "iem" ? "phones" : "device")}</span><div><span class="eyebrow">${esc(p.tag)}</span><h3>${esc(p.name)}</h3></div><span class="dl-gc">${p.files.length} files</span><a class="btn sm" href="${p.bundle.path}" download data-dl="${esc(p.bundle.name)}">${ic("download")}<span>Zip</span></a></div><ul class="dl-list">${p.files
          .slice()
          .sort(
            (a, b) =>
              ["vdc", "irs", "eel"].indexOf(a.kind) -
              ["vdc", "irs", "eel"].indexOf(b.kind),
          )
          .map((x) => row(p, x))
          .join("")}</ul></div>`,
).join("");
$("#dlCount").textContent =
PROF.length * 3 + " files · " + PROF.length + " bundles";
$("#allBtn").href = DATA.all.path;
$("#allBtn").setAttribute("download", DATA.all.name);
}
let kindF = "all";
function filterHub() {
const q = $("#dlSearch").value.trim().toLowerCase();
$$(".dl-row").forEach((r) => {
r.hidden = !(
(kindF === "all" || r.dataset.kind === kindF) &&
(!q || r.dataset.q.includes(q))
);
});
let any = false;
$$(".dl-group").forEach((g) => {
const n = $$(".dl-row:not([hidden])", g).length;
g.hidden = !n;
$(".dl-gc", g).textContent = n + " files";
if (n) any = true;
});
$("#dlEmpty").hidden = any;
}
$("#dlSeg").addEventListener("click", (e) => {
const b = e.target.closest("button");
if (!b) return;
kindF = b.dataset.k;
$$("#dlSeg button").forEach((x) => x.setAttribute("aria-pressed", x === b));
filterHub();
});
$("#dlSearch").addEventListener("input", filterHub);
function markRec() {
$$(".dl-row").forEach((r) =>
r.classList.toggle("rec", r.dataset.p === prof.id),
);
$("#dlProf").textContent = prof.name;
}

/* == evidence, status, faq == */
function buildEvidence() {
$("#evBody").innerHTML = PROF.map((p) => {
const s = p.stats;
return `<tr><td>${esc(p.name)}</td><td>${s.rms.toFixed(2)} dB${s.capped ? " <small>(capped)</small>" : ""}</td><td>${s.gain1k > 0 ? "+" : ""}${s.gain1k.toFixed(1)} dB</td><td>${s.chainMax > 0 ? "+" : ""}${s.chainMax.toFixed(1)} dB</td><td>${s.irsPeak.toFixed(2)}</td><td>${s.sections} sections</td></tr>`;
}).join("");
}
function buildStats() {
$("#stats").innerHTML = [
["device", "Device", "Xiaomi Redmi 12", "Captured", "var(--blue)"],
["set", "Operating system", "Android 15", "HyperOS 2", "var(--violet)"],
[
"term",
"Audio pipeline",
"32-bit PCM",
"AudioOut_D · MIXER",
"var(--green)",
],
[
"chart",
"Native sample rate",
"48000 Hz",
"No OS resampling",
"var(--amber)",
],
[
"script",
"Release",
"v6.0.0",
"Stable · " + DATA.released,
"var(--violet)",
],
[
"conv",
"Profiles",
PROF.length + " builds",
byDev("iem").length + " IEM · " + byDev("spk").length + " speaker",
"var(--green)",
],
]
.map(
(s) =>
`<div class="stat" style="--c:${s[4]}">${ic(s[0])}<dl><dt>${s[1]}</dt><dd class="v">${s[2]}</dd><dd class="d">${s[3]}</dd></dl></div>`,
)
.join("");
}
const FAQ = [
[
"VDC file",
"What is a VDC file?",
"A set of biquad filters that ViPER-DDC applies first. In v5 each profile has one VDC with a 48 kHz bank and a 44.1 kHz bank, fitted so both banks give the same curve.",
],
[
"Impulse response",
"What does the impulse response do?",
"It is loaded into the Convolver and carries the stereo behaviour (crossfeed on the IEM profiles) and, for Protection V6, the smooth part of the correction. Keep the optimization on Original.",
],
[
"Script",
"What does the script do?",
"A Liveprog EEL2 script. In v5 it is the safety and character layer: input guard, a limiter with a 1.5 ms lookahead and a true-peak detector, plus profile controls such as Binaural Width, Dialogue Boost or loudness makeup.",
],
[
"Pairing",
"Why must the three files be used together?",
"The VDC and impulse response were fitted together against the target, so each profile has one matched pair. Swapping one for another profile breaks the curve. The zip for each profile keeps them together.",
],
[
"Gain",
"Why is there no preamp to set?",
"The previous release baked a worst-case attenuation of 6 to 13 dB into the VDCs. v5 removes it. Each chain is normalised so its maximum gain is −0.5 dB and the limiter protects peaks, so leave every gain at zero.",
],
[
"Speaker boost",
"Why do the speaker profiles not reach the full target?",
"Total boost is capped at +8 dB and everything below 110 Hz is high-passed to protect the small driver. Against the uncapped target the speaker profiles therefore sit 3 to 5 dB low between 100 and 2000 Hz.",
],
[
"True Peak Detect",
"What is True Peak Detect?",
"It estimates inter-sample peaks with a four-times oversampled detector so the limiter can hold its ceiling between samples. It is on by default. If you ever hear crackling, turn it off to see whether it is the cause.",
],
[
"Choosing",
"Which profile should I use?",
"For the EDX Pro start with HD. Spatial V4 adds crossfeed and a width control, and Reference V10 is dual-mono with no crossfeed. For the speaker, Protection V6 is the cautious one, Cinema V8 adds dialogue and width, and Dynamic V10 adds compression and bass harmonics.",
],
];
function buildFaq() {
$("#faqList").innerHTML = FAQ.map(
(q, i) =>
`<details class="faq-i"${i === 0 ? " open" : ""}><summary><span class="faq-n">${String(i + 1).padStart(2, "0")}</span><span class="faq-q"><span class="eyebrow">${esc(q[0])}</span><b>${esc(q[1])}</b></span><span class="faq-x" aria-hidden="true"><svg class="ic"><use href="#i-plus"/></svg></span></summary><div class="faq-a"><p>${esc(q[2])}</p></div></details>`,
).join("");
$("#faqCount").textContent = FAQ.length + " topics";
}

/* == selection == */
function select(id, quiet) {
const p = PROF.find((x) => x.id === id);
if (!p) return;
prof = p;
store.set("ha-profile", id);
document.querySelectorAll(".n-chip-t").forEach((n) => {
n.textContent = p.name;
});
$("#heroN").textContent = String(PROF.length);
renderOuts();
renderSnd();
renderGet();
renderApply();
markRec();
drawHero();
drawCompare();
if (!quiet) {
const u = new URL(location.href);
u.searchParams.set("p", id);
history.replaceState(null, "", u);
}
}
document.addEventListener("click", (e) => {
const o = e.target.closest("[data-out]");
if (o) {
const d = o.dataset.out;
if (prof.device !== d) select(byDev(d)[0].id);
return;
}
const s = e.target.closest("#snd [data-p]");
if (s) {
select(s.dataset.p);
return;
}
const c = e.target.closest("[data-ct]");
if (c) {
copyText(c.dataset.ct, c);
return;
}
const d = e.target.closest("[data-dl]");
if (d) {
toast("Downloading " + d.dataset.dl);
return;
}
const g = e.target.closest("#getBtn");
if (g) {
toast("Downloading " + prof.bundle.name);
}
});
$("#shareBtn").onclick = (e) => {
const u = new URL(location.href);
u.searchParams.set("p", prof.id);
u.hash = "setup";
copyText(u.toString(), e.currentTarget);
};
document.addEventListener("keydown", (e) => {
if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
const b = e.target.closest(".seg button");
if (!b) return;
const all = $$("button", b.parentElement),
i = all.indexOf(b),
n =
e.key === "Home"
? 0
: e.key === "End"
? all.length - 1
: (i + (e.key === "ArrowRight" ? 1 : -1) + all.length) % all.length;
e.preventDefault();
all[n].focus();
all[n].click();
});

/* == boot == */
fetch("data/profiles.json")
.then((r) => {
if (!r.ok) throw new Error("HTTP " + r.status);
return r.json();
})
.then((d) => {
DATA = d;
PROF = d.profiles;
eqHost = $("#cmpChart");
window.HAChart.wire(eqHost);
buildHub();
buildEvidence();
buildStats();
buildFaq();
const q = new URL(location.href).searchParams.get("p"),
saved = store.get("ha-profile");
select(
[q, saved, PROF[0].id].find((id) => PROF.some((p) => p.id === id)),
true,
);
})
.catch((err) => {
console.error(err);
$("#loadErr").hidden = false;
});
})();
