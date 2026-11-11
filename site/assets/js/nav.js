(function () {
"use strict";
var D = document,
R = D.documentElement,
B = D.body;
var file = location.pathname.split("/").pop() || "index.html";
var base = R.getAttribute("data-base") || "";
var home = !base && file === "index.html";
var GH = "https://github.com/nmstudioo/HyperAudio";
var P = {
profile: '<path d="M6 4v3.5M6 13.5V20M12 4v8M12 17.5V20M18 4v2M18 11.5V20"/><circle cx="6" cy="10.5" r="2.5" fill="currentColor" fill-opacity=".16"/><circle cx="12" cy="14.8" r="2.5" fill="currentColor" fill-opacity=".16"/><circle cx="18" cy="8.8" r="2.5" fill="currentColor" fill-opacity=".16"/>',
check: '<circle cx="12" cy="12" r="8.5" fill="currentColor" fill-opacity=".16"/><path d="M8.2 12.4l2.6 2.6 5-5.4"/>',
download: '<path d="M12 4v9M8.2 9.8 12 13.6l3.8-3.8"/><path d="M4.5 14.5v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-3" fill="currentColor" fill-opacity=".16"/>',
dash: '<path d="M12 3.3l7.2 2.7v5.5c0 4.3-3 7.5-7.2 9.2-4.2-1.7-7.2-4.9-7.2-9.2V6z" fill="currentColor" fill-opacity=".16"/><path d="M8.8 12l2.2 2.2 4.3-4.5"/>',
help: '<path d="M5.5 4.5h13A2 2 0 0 1 20.5 6.5v8a2 2 0 0 1-2 2H11l-4.6 3.6v-3.6H5.5a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2z" fill="currentColor" fill-opacity=".16"/><path d="M10.2 9.6a1.9 1.9 0 1 1 2.7 1.7c-.6.3-.9.7-.9 1.3M12 14.4h.01"/>',
merge: '<circle cx="9" cy="12" r="5.6" fill="currentColor" fill-opacity=".16"/><circle cx="15" cy="12" r="5.6"/>',
search: '<circle cx="12" cy="12" r="8.5"/><path d="M15.7 8.3l-2 5.4-5.4 2 2-5.4z" fill="currentColor" fill-opacity=".16"/>',
box: '<rect x="3.5" y="4.5" width="17" height="4.5" rx="1.4" fill="currentColor" fill-opacity=".16"/><path d="M5 9v8.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9M10 13h4"/>',
book: '<path d="M5 5.5a2 2 0 0 1 2-2h12v14.5H7a2 2 0 0 0-2 2z" fill="currentColor" fill-opacity=".16"/><path d="M5 20a2 2 0 0 0 2 1.5h12V18M9 8h6"/>',
log: '<circle cx="12" cy="12" r="8.5" fill="currentColor" fill-opacity=".16"/><path d="M12 7.5V12l3 2"/>',
menu: '<path d="M4 8h16M4 16h10"/>',
more: '<circle cx="5.5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18.5" cy="12" r="1.2"/>',
eq: '<path d="M4 12h1.5M8.5 8v8M12 4.5v15M15.5 8v8M18.5 12H20"/>',
sun: '<circle cx="12" cy="12" r="4" fill="currentColor" fill-opacity=".16"/><path d="M12 2.8v1.9M12 19.3v1.9M2.8 12h1.9M19.3 12h1.9M5.5 5.5l1.3 1.3M17.2 17.2l1.3 1.3M18.5 5.5l-1.3 1.3M6.8 17.2l-1.3 1.3"/>',
moon: '<path d="M19.5 14.2A7.8 7.8 0 1 1 9.8 4.5a6.2 6.2 0 0 0 9.7 9.7z" fill="currentColor" fill-opacity=".16"/>',
ext: '<path d="M7 17 17 7M9 7h8v8"/>',
x: '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
exp: '<rect x="3.5" y="4.5" width="17" height="15" rx="3.2"/><path d="M9.5 4.5v15" /><path d="M13.6 9.8l2.2 2.2-2.2 2.2"/>',
col: '<rect x="3.5" y="4.5" width="17" height="15" rx="3.2"/><path d="M9.5 4.5v15"/><path d="M16 9.8l-2.2 2.2 2.2 2.2"/>',
gh: '<path d="M12 3a9 9 0 0 0-2.85 17.54c.45.08.62-.2.62-.43v-1.5c-2.5.55-3.03-1.2-3.03-1.2-.41-1.04-1-1.32-1-1.32-.82-.56.06-.55.06-.55.9.06 1.38.93 1.38.93.8 1.38 2.1.98 2.62.75.08-.58.31-.98.57-1.2-2-.22-4.1-1-4.1-4.45 0-.98.35-1.79.93-2.42-.1-.23-.4-1.14.09-2.38 0 0 .76-.24 2.48.92a8.6 8.6 0 0 1 4.52 0c1.72-1.16 2.48-.92 2.48-.92.49 1.24.18 2.15.09 2.38.58.63.93 1.44.93 2.42 0 3.46-2.1 4.22-4.11 4.44.32.28.61.83.61 1.67v2.47c0 .24.16.52.62.43A9 9 0 0 0 12 3z"/>',
};
function ic(n, c) {
return (
'<svg class="ni' +
(c ? " " + c : "") +
'" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
P[n] +
"</svg>"
);
}
var LOGO =
'<span class="n-logo" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M3 8c2.2 0 2.2-2.5 4.5-2.5S9.8 8 12 8s2.2-2.5 4.5-2.5S18.8 8 21 8"/><path d="M3 13c2.2 0 2.2-2.5 4.5-2.5S9.8 13 12 13s2.2-2.5 4.5-2.5S18.8 13 21 13" opacity=".7"/><path d="M3 18h18" opacity=".4"/></svg></span>';
var G = [
["setup", "Setup", "profile"],
["apply", "Apply", "check"],
["files", "Files", "download"],
["evidence", "Evidence", "dash"],
["faq", "FAQ", "help"],
];
var T = [
["compare.html", "Compare", "merge"],
["finder.html", "Finder", "search"],
["docs/index.html", "Docs", "book"],
["changelog.html", "Changelog", "log"],
];
var gHref = function (id) {
return base + id + ".html";
};
var tAttr = function (t) {
return (base ? t[0] === "docs/index.html" : t[0] === file) ? ' aria-current="page"' : "";
};
var themeBtn = function (c) {
return (
'<button type="button" class="' +
c +
'" data-n-theme aria-label="Toggle light or dark theme"><span class="n-sun">' +
ic("sun") +
'</span><span class="n-moon">' +
ic("moon") +
"</span></button>"
);
};
var chip =
'<a class="n-chip" href="' +
gHref("setup") +
'" data-tip="Active profile" aria-label="Active profile">' +
'<span class="n-chip-i">' +
ic("eq") +
'</span><span class="n-chip-b"><small>Active profile</small><span class="n-chip-t">Profile</span></span></a>';
function gLinks(cls) {
return G.map(function (g) {
return (
'<a class="' +
cls +
'" href="' +
gHref(g[0]) +
'" data-k="' +
g[0] +
'" data-tip="' +
g[1] +
'">' +
ic(g[2]) +
'<span class="nt">' +
g[1] +
"</span></a>"
);
}).join("");
}
function tLinks(cls) {
return T.map(function (t) {
return (
'<a class="' +
cls +
'" href="' +
base +
t[0] +
'"' +
tAttr(t) +
' data-tip="' +
t[1] +
'">' +
ic(t[2]) +
'<span class="nt">' +
t[1] +
"</span></a>"
);
}).join("");
}
var main = D.querySelector(".shell") || D.querySelector("main");
if (!main) return;
var mainEl = D.querySelector("main");
if (mainEl && !mainEl.id) mainEl.id = "main";
B.classList.add("n-on", home ? "n-home" : "n-pg");
if (!D.querySelector(".skip")) {
var s = D.createElement("a");
s.className = "skip";
s.href = "#main";
s.textContent = "Skip to content";
B.insertBefore(s, B.firstChild);
}
var wrap = D.createElement("div");
wrap.innerHTML =
'<header class="mh"><button type="button" class="mh-m" aria-expanded="false" aria-controls="sb" aria-label="Open menu">' +
ic("menu") +
"</button>" +
'<a class="mh-b" href="' +
gHref("setup") +
'" aria-label="HyperAudio home">' +
LOGO +
'<span class="mh-t"><b>HyperAudio</b><small class="mh-sub n-prof" aria-label="Active profile"></small></span></a>' +
themeBtn("nb mh-th") +
"</header>" +
'<aside class="sb" id="sb" aria-label="Site">' +
'<div class="sb-top"><a class="sb-brand" href="' +
(home ? "#setup" : base + "index.html") +
'" aria-label="HyperAudio home">' +
LOGO +
'<span class="sb-bt"><b>HyperAudio</b><small class="n-ver"></small></span></a>' +
'<button type="button" class="sb-tg" aria-expanded="false" aria-controls="sb" aria-label="Expand sidebar">' +
ic("exp", "tg-e") +
ic("col", "tg-c") +
ic("x", "tg-x") +
"</button></div>" +
'<p class="sb-badge"><i aria-hidden="true"></i><span class="nt">Stable · device tests pending</span></p>' +
'<div class="sb-scroll">' +
'<div role="navigation" aria-labelledby="sbg"><p class="sb-h nt" id="sbg">Guide</p>' +
gLinks("nl") +
"</div>" +
'<div role="navigation" aria-labelledby="sbt"><p class="sb-h nt" id="sbt">Tools</p>' +
tLinks("nl") +
"</div>" +
"</div>" +
'<div class="sb-bot">' +
chip +
'<div class="sb-ctl">' +
themeBtn("nb") +
'<a class="nb" href="https://nmstudioo.github.io/" target="_blank" rel="noopener noreferrer" aria-label="Website (opens in new tab)" data-tip="Website"><svg class="ni" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg></a>' +
'<a class="nb" href="' +
GH +
'" target="_blank" rel="noopener noreferrer" aria-label="GitHub repository (opens in new tab)" data-tip="GitHub">' +
ic("gh") +
"</a></div>" +
'<p class="sb-cr nt">Tested by Noushad Mostafa</p></div>' +
'</aside><div class="sb-scrim" hidden></div>';
var frag = D.createDocumentFragment();
while (wrap.firstChild) frag.appendChild(wrap.firstChild);
B.insertBefore(frag, main);
var foot = D.createElement('div');
foot.className = 'sf'; foot.setAttribute('role', 'contentinfo');
var year = new Date().getFullYear();
foot.innerHTML = '<div class="sf-in">' +
'<div class="sf-brand"><span class="sf-mark" role="img" aria-label="HyperAudio">' +
'<img class="sf-logo sf-logo-dark" src="' + base + 'assets/brand/logo.svg" width="440" height="96" alt="" decoding="async">' +
'<img class="sf-logo sf-logo-light" src="' + base + 'assets/brand/logo-light.svg" width="440" height="96" alt="" decoding="async">' +
'</span></div>' +
'<p class="sf-facts"><span>Offline checks</span> <span>No acoustic measurement recorded</span> <span>Tested by Noushad Mostafa</span></p>' +
'<nav class="sf-n" aria-label="Footer"><a href="/HyperAudio/docs/">Docs</a><a href="/HyperAudio/changelog.html">Changelog</a><a href="/HyperAudio/docs/EVIDENCE.html">Evidence</a></nav>' +
'<p class="sf-cp">© ' + year + ' Noushad Mostafa<span class="n-ver"></span></p>' +
'</div>';
B.appendChild(foot);
function themeSync() {
var l = R.dataset.theme === "light";
D.querySelectorAll("[data-n-theme]").forEach(function (b) {
b.setAttribute("aria-pressed", l);
if (!b.classList.contains("sl"))
b.setAttribute(
"aria-label",
l ? "Switch to dark theme" : "Switch to light theme",
);
});
var tl = D.querySelector(".n-tl");
if (tl)
tl.textContent = l ? "Switch to dark theme" : "Switch to light theme";
}
D.addEventListener("click", function (e) {
if (!e.target.closest("[data-n-theme]")) return;
var n = R.dataset.theme === "light" ? "dark" : "light";
R.dataset.theme = n;
try {
localStorage.setItem("ha-theme", n);
} catch (x) {}
themeSync();
});
themeSync();
var sb = D.getElementById("sb"),
tg = sb.querySelector(".sb-tg"),
scrim = D.querySelector(".sb-scrim");
var mm = D.querySelector(".mh-m"),
mob = matchMedia("(max-width:767px)"),
wide = matchMedia("(min-width:1100px)"),
pref = "full";
try { pref = localStorage.getItem("ha-rail") === "1" ? "rail" : "full"; } catch (x) {}
function mode(open) {
var m = mob.matches ? "drawer" : wide.matches ? pref : open ? "full" : "rail";
sb.dataset.mode = m;
R.dataset.sb = mob.matches ? "none" : m === "full" && !wide.matches ? "rail" : m;
var full = m === "full";
tg.setAttribute("aria-label", mob.matches ? "Close menu" : full ? "Collapse sidebar" : "Expand sidebar");
tg.setAttribute("aria-expanded", mob.matches ? open : full);
}
function rail(open) {
sb.dataset.open = open ? "true" : "false";
scrim.hidden = !open || wide.matches;
mode(open);
mm.setAttribute("aria-expanded", open);
mm.setAttribute("aria-label", open ? "Close menu" : "Open menu");
R.classList.toggle("nav-lock", open && mob.matches);
if (open && mob.matches) tg.focus();
}
mm.addEventListener("click", function () {
var o = sb.dataset.open !== "true";
rail(o);
if (!o) mm.focus();
});
tg.addEventListener("click", function () {
if (wide.matches) {
pref = pref === "full" ? "rail" : "full";
try { localStorage.setItem("ha-rail", pref === "rail" ? "1" : "0"); } catch (x) {}
mode(false);
return;
}
rail(sb.dataset.open !== "true");
});
scrim.addEventListener("click", function () {
rail(false);
(mob.matches ? mm : tg).focus();
});
sb.addEventListener("click", function (e) {
if (e.target.closest("a.nl") && sb.dataset.open === "true") rail(false);
});
D.addEventListener("keydown", function (e) {
if (e.key === "Escape") {
if (sb.dataset.open === "true") {
rail(false);
(mob.matches ? mm : tg).focus();
e.preventDefault();
}
return;
}
if (e.key === "Tab" && mob.matches && sb.dataset.open === "true") {
var f = sb.querySelectorAll("a[href],button");
if (!f.length) return;
var a = f[0],
z = f[f.length - 1];
if (e.shiftKey && D.activeElement === a) {
z.focus();
e.preventDefault();
} else if (!e.shiftKey && D.activeElement === z) {
a.focus();
e.preventDefault();
}
}
});
[matchMedia("(min-width:768px)"), wide].forEach(function (q) {
(q.addEventListener ? q.addEventListener.bind(q, "change") : q.addListener.bind(q))(function () {
rail(false);
});
});
rail(false);
var mh = D.querySelector(".mh"), ly = 0, hk = false;
addEventListener("scroll", function () {
if (hk) return;
hk = true;
requestAnimationFrame(function () {
hk = false;
var y = scrollY, d = y - ly;
if (y < 80 || d < -6) mh.classList.remove("hide");
else if (d > 8 && mob.matches && sb.dataset.open !== "true") mh.classList.add("hide");
ly = y;
});
}, { passive: true });
function setCur(k) {
D.querySelectorAll("[data-k]").forEach(function (a) {
if (a.dataset.k === k) a.setAttribute("aria-current", "true");
else a.removeAttribute("aria-current");
});
}
if (home) {
var ORDER = [
["overview", "setup"],
["setup", "setup"],
["apply", "apply"],
["files", "files"],
["evidence", "evidence"],
["status", "evidence"],
["hardware", "evidence"],
["faq", "faq"],
],
tick = false;
var spy = function () {
tick = false;
var k = "setup",
line = innerHeight * 0.3;
ORDER.forEach(function (o) {
var el = D.getElementById(o[0]);
if (el && el.getBoundingClientRect().top <= line) k = o[1];
});
if (innerHeight + scrollY >= R.scrollHeight - 4) k = "faq";
setCur(k);
};
var req = function () {
if (!tick) {
tick = true;
requestAnimationFrame(spy);
}
};
addEventListener("scroll", req, { passive: true });
addEventListener("resize", req);
addEventListener("hashchange", req);
spy();
setTimeout(spy, 500);
addEventListener("load", spy);
}
fetch(base + "data/profiles.json")
.then(function (r) {
return r.ok ? r.json() : Promise.reject();
})
.then(function (d) {
D.querySelectorAll(".n-ver").forEach(function (n) {
n.textContent = 'Release v' + (d.version || "").replace(/^v/, '');
});
var id;
try {
id = localStorage.getItem("ha-profile");
} catch (x) {}
var p =
(d.profiles || []).filter(function (q) {
return q.id === id;
})[0] || (d.profiles || [])[0];
D.querySelectorAll(".n-chip-t,.n-prof").forEach(function (n) {
if (p && (n.textContent === "Profile" || n.classList.contains("n-prof"))) n.textContent = p.name;
});
if (p) D.querySelectorAll(".n-chip").forEach(function (n) {
n.setAttribute("data-tip", p.name);
n.setAttribute("aria-label", "Active profile: " + p.name);
});
})
.catch(function () {});
})();
;(function(){try{if("serviceWorker"in navigator&&location.protocol!=="file:"){var s=document.currentScript&&document.currentScript.src;if(s)navigator.serviceWorker.register(new URL("../../sw.js",s).href).catch(function(){})}}catch(e){}})();

;(function(){try{var f=(location.pathname.split("/").pop()||"").replace(/\.html$/,"");document.querySelectorAll("[data-k]").forEach(function(a){if(a.dataset.k===f)a.setAttribute("aria-current","page")})}catch(e){}})();
