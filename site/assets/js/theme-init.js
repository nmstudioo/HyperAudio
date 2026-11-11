try {
var t = localStorage.getItem("ha-theme");
if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
} catch (e) {}

;(function(){var m={"setup": "setup.html", "apply": "apply.html", "files": "files.html", "evidence": "evidence.html", "faq": "faq.html", "releases": "files.html#releases", "status": "evidence.html#status", "hardware": "setup.html#hardware"},h=location.hash.slice(1);if(h&&m[h]&&!/\/docs\//.test(location.pathname)&&/(^|\/)(index\.html)?$/.test(location.pathname))location.replace(m[h]);})();
