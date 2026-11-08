/* HyperAudio v7 interface enhancements. No DSP files or parameters are changed. */
(function () {
  "use strict";

  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };
  var dataPromise;

  function loadData() {
    if (!dataPromise) {
      dataPromise = fetch("data/profiles.json", { credentials: "same-origin" }).then(function (r) {
        if (!r.ok) throw new Error("Profile metadata HTTP " + r.status);
        return r.json();
      });
    }
    return dataPromise;
  }

  function setText(el, value) {
    if (el && el.textContent !== value) el.textContent = value;
  }

  function syncRelease(data) {
    var version = data && data.version ? "v" + String(data.version).replace(/^v/, "") : "";
    if (!version) return;
    var tag = $("#overview .hero-copy .tag");
    if (tag) {
      var tagText = Array.prototype.slice.call(tag.childNodes).filter(function (node) { return node.nodeType === 3; })[0];
      if (tagText) tagText.nodeValue = version + " · Stable release · calculated response";
      else tag.appendChild(document.createTextNode(version + " · Stable release · calculated response"));
    }

    setText($("#filesVersion"), version);
    ["#profileSumsLink", "#allSumsLink"].forEach(function (selector) {
      var link = $(selector);
      if (link) link.href = "downloads/" + String(data.version).replace(/^v/, "") + "/SHA256SUMS.txt";
    });

    var stats = $("#stats");
    if (stats) {
      var updateStats = function () {
        $$(".stat", stats).forEach(function (card) {
          var label = $("dt", card);
          if (label && label.textContent.trim() === "Release") {
            setText($(".v", card), version);
            setText($(".d", card), "Stable · " + (data.released || "release date not recorded"));
          }
        });
      };
      updateStats();
      if (window.MutationObserver) {
        var observer = new MutationObserver(updateStats);
        observer.observe(stats, { childList: true, subtree: true, characterData: true });
      }
    }
  }

  function moveResponseChart() {
    var steps = $("#setup .steps3");
    var chart = $("#setup .cmp-hook");
    if (steps && chart && chart.previousElementSibling !== steps) steps.insertAdjacentElement("afterend", chart);
  }

  function decorateProfiles(data) {
    var host = $("#snd");
    if (!host || !data || !Array.isArray(data.profiles)) return;
    var byId = {};
    data.profiles.forEach(function (p) { byId[p.id] = p; });

    function update() {
      $$(".snd-c", host).forEach(function (card) {
        if ($(".v7-profile-metrics", card)) return;
        var id = card.getAttribute("data-p");
        var p = byId[id];
        if (!p || !p.stats) return;
        var stats = p.stats;
        var metrics = document.createElement("span");
        metrics.className = "v7-profile-metrics";
        metrics.setAttribute("role", "group");
        metrics.setAttribute("aria-label", "Calculated profile metrics");
        [
          [Number(stats.rms).toFixed(2) + " dB", "RMS target error"],
          [Number(stats.chainMax).toFixed(1) + " dB", "Chain maximum"],
          [String(stats.sections), "VDC sections"],
          [Number(stats.irsPeak).toFixed(2), "IRS sample peak"],
        ].forEach(function (pair) {
          var item = document.createElement("span");
          var value = document.createElement("b");
          var label = document.createElement("small");
          value.textContent = pair[0];
          label.textContent = pair[1];
          item.appendChild(value);
          item.appendChild(label);
          metrics.appendChild(item);
        });
        card.appendChild(metrics);
      });
    }

    update();
    if (window.MutationObserver) {
      var observer = new MutationObserver(update);
      observer.observe(host, { childList: true, subtree: true });
    }
  }

  function improveFinder(data) {
    var result = $("#res");
    if (!result || !data || !Array.isArray(data.profiles)) return;
    function update() {
      var title = $("b", result);
      if (!title || $(".v7-use-profile", result)) return;
      var p = data.profiles.filter(function (profile) { return profile.name === title.textContent.trim(); })[0];
      if (!p) return;
      var link = document.createElement("a");
      link.className = "v7-use-profile";
      link.href = "index.html?p=" + encodeURIComponent(p.id) + "#setup";
      link.textContent = "Use this profile";
      result.appendChild(link);
    }
    update();
    if (window.MutationObserver) {
      var observer = new MutationObserver(update);
      observer.observe(result, { childList: true, subtree: true });
    }
  }

  function constrainComparison(data) {
    var a = $("#a"), b = $("#b");
    if (!a || !b || !data || !Array.isArray(data.profiles)) return;
    var byId = {};
    data.profiles.forEach(function (p) { byId[p.id] = p; });

    function sync() {
      if (!a.options.length || !b.options.length) return false;
      var selectedA = byId[a.value];
      if (!selectedA) return false;
      var device = selectedA.device;
      var available = data.profiles.filter(function (p) { return p.device === device; });
      var previousB = byId[b.value];
      $$("option", b).forEach(function (option) {
        var p = byId[option.value];
        option.hidden = !p || p.device !== device;
        option.disabled = option.hidden;
      });
      if (!previousB || previousB.device !== device) {
        var next = available.filter(function (p) { return p.id !== a.value; })[0] || available[0];
        if (next) b.value = next.id;
      }
      var selectedB = byId[b.value];
      if (selectedB && selectedB.device === device && selectedB.id === selectedA.id && available.length > 1) {
        b.value = available.filter(function (p) { return p.id !== selectedA.id; })[0].id;
      }
      return true;
    }

    a.addEventListener("change", sync);
    b.addEventListener("change", sync);
    if (!sync() && window.MutationObserver) {
      var observer = new MutationObserver(function () {
        if (sync()) observer.disconnect();
      });
      observer.observe(a, { childList: true });
      observer.observe(b, { childList: true });
    }
  }

  function correctEvidenceCopy() {
    var footer = $(".sf-e");
    setText(footer, "Offline checks · no acoustic measurement recorded");

    var badge = $("#evidence .sec-h .badge");
    setText(badge, "Offline checks · device records pending");

    var hardwareBadge = $("#hardware .sec-h .badge");
    setText(hardwareBadge, "Reference hardware");

    var note = $(".ev-read .ev-notes li:nth-child(3)");
    if (note) {
      note.innerHTML = "<b>Device verification:</b> no build-specific device results are recorded for the current release. <b>Acoustic verification:</b> no microphone measurements have been recorded. Worst-case device CPU, speaker excursion and thermal limits also remain unverified.";
    }
  }

  function init() {
    moveResponseChart();
    correctEvidenceCopy();
    loadData().then(function (data) {
      syncRelease(data);
      decorateProfiles(data);
      improveFinder(data);
      constrainComparison(data);
    }).catch(function (err) {
      if (window.console && console.warn) console.warn("HyperAudio v7 UI data enhancement unavailable:", err);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
