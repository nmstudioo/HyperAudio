(function () {
"use strict";
var D = document;
D.querySelectorAll(".cb .cp").forEach(function (b) {
b.addEventListener("click", function () {
var t = b.parentNode.querySelector("code").textContent;
var done = function (ok) {
b.toggleAttribute("data-ok", ok);
b.setAttribute("aria-label", ok ? "Copied" : "Copy failed");
setTimeout(function () { b.removeAttribute("data-ok"); b.setAttribute("aria-label", "Copy code"); }, 1600);
};
try { navigator.clipboard.writeText(t).then(function () { done(true); }, function () { done(false); }); } catch (e) { done(false); }
});
});
var links = [].slice.call(D.querySelectorAll(".dtoc a"));
if (links.length && "IntersectionObserver" in window) {
var map = {};
links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
var io = new IntersectionObserver(function (es) {
es.forEach(function (e) {
if (e.isIntersecting) {
links.forEach(function (a) { a.classList.remove("on"); });
var a = map[e.target.id];
if (a) a.classList.add("on");
}
});
}, { rootMargin: "-80px 0px -70% 0px" });
D.querySelectorAll(".prose h2[id],.prose h3[id]").forEach(function (h) { io.observe(h); });
}
var t = D.querySelector(".dtoc details");
if (t && window.matchMedia("(max-width: 999px)").matches) t.removeAttribute("open");
})();
