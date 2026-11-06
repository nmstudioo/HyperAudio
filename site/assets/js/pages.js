(function () {
"use strict";
const $ = (s) => document.querySelector(s),
esc = (s) =>
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
const J = (u) =>
fetch(u).then((r) => {
if (!r.ok) throw 0;
return r.json();
});
const fail = () => {
const e = $("#err");
if (e) e.hidden = false;
};
window.HAP = {
compare() {
Promise.all([J("data/profiles.json"), J("data/choose.json")])
.then(([d, c]) => {
const P = d.profiles,
f = d.freq,
o = P.map(
(p) => `<option value="${p.id}">${esc(p.name)}</option>`,
).join("");
$("#a").innerHTML = o;
$("#b").innerHTML = o;
$("#b").selectedIndex = 1;
let ch;
const draw = () => {
const A = P.find((p) => p.id === $("#a").value),
B = P.find((p) => p.id === $("#b").value),
pt = (a) => a.map((v, i) => [f[i], v]);
ch = {
label: "Predicted response",
ref: 0,
series: [
{
label: A.short + " · " + A.name,
pts: pt(A.curves.predicted),
color: "var(--acc)",
w: 2.4,
},
{
label: B.short + " · " + B.name,
pts: pt(B.curves.predicted),
color: "var(--s-raw)",
w: 2.4,
dash: "5 4",
},
],
};
HAChart.drawChart($("#ch"), ch);
HAChart.legend($("#lg"), ch, () => HAChart.drawChart($("#ch"), ch));
$("#pk").innerHTML = [A, B]
.map(
(p) =>
`<div class="pick"><b>${esc(p.name)}</b><span>Choose this if… ${esc(c.choose[p.id] || "")}</span></div>`,
)
.join("");
};
HAChart.wire($("#ch"));
$("#a").onchange = $("#b").onchange = draw;
draw();
})
.catch(fail);
},
finder() {
Promise.all([J("data/profiles.json"), J("data/choose.json")])
.then(([d, c]) => {
const dev = $("#dev"),
goal = $("#goal");
const run = () => {
goal.innerHTML =
goal.innerHTML && goal.dataset.d === dev.value
? goal.innerHTML
: c.goals[dev.value]
.map((g) => `<option value="${g[0]}">${esc(g[1])}</option>`)
.join("");
goal.dataset.d = dev.value;
const id = Object.keys(c.tags).find(
(k) =>
c.tags[k].device === dev.value &&
c.tags[k].goal.includes(goal.value),
),
p = d.profiles.find((x) => x.id === id);
if (!p) return;
const gl = c.goals[dev.value].find((g) => g[0] === goal.value)[1],
ev = p.evidence || {};
$("#res").innerHTML =
`<b>${esc(p.name)}</b><span>${esc(p.desc)}</span>`;
$("#why").innerHTML = [
`You picked ${dev.value === "iem" ? "the EDX Pro" : "the Redmi 12 speaker"}, so only its ${d.profiles.filter((x) => x.device === dev.value).length} profiles were considered.`,
`Your priority is “${gl}”. ${esc(c.choose[id])}`,
`Predicted error to target: ${p.stats.rms.toFixed(2)} dB RMS${p.stats.capped ? " (boost capped, so low-mid sits below target by design)" : ""}. Calculated, not measured.`,
`Device check: ${esc(ev.deviceNote || "not recorded")}`,
]
.map((t) => `<li>${t}</li>`)
.join("");
};
dev.onchange = () => {
goal.innerHTML = "";
run();
};
goal.onchange = run;
run();
})
.catch(fail);
},
versions(id, all) {
J("data/versions.json")
.then((v) => {
$("#" + id).innerHTML = v
.filter((x) => all || x.notes.length)
.map(
(x) =>
`<li class="${x.legacy ? "legacy " : ""}${/^v[12]$/.test(x.v) ? x.v : ""}"><b>${esc(x.v)}</b> <small>${esc(x.status)}${x.date ? " · " + esc(x.date) : ""}</small>${x.notes.length ? "<ul>" + x.notes.map((n) => `<li>${esc(n)}</li>`).join("") + "</ul>" : ""}${x.dl ? `<br><a href="${x.dl}">SHA256SUMS.txt</a>` : ""}</li>`,
)
.join("");
})
.catch(() => {
$("#" + id).innerHTML = "<li>Could not load versions.</li>";
});
},
};
})();
