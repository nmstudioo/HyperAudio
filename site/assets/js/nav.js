/* HyperAudio shared chrome: sidebar (>=768), mobile header + bottom bar + More sheet (<768), footer. */
(function () {
  'use strict';
  var D = document, R = D.documentElement, B = D.body;
  var file = location.pathname.split('/').pop() || 'index.html';
  var home = file === 'index.html';
  var GH = 'https://github.com/nmstudioo/HyperAudio';
  var P = {
    profile: '<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
    download: '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
    dash: '<rect x="3.5" y="3.5" width="7" height="8.5" rx="1.75"/><rect x="13.5" y="3.5" width="7" height="5" rx="1.75"/><rect x="13.5" y="11.5" width="7" height="9" rx="1.75"/><rect x="3.5" y="15" width="7" height="5.5" rx="1.75"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2.2-2.4 3.8M12 17.2h.01"/>',
    merge: '<circle cx="9" cy="12" r="5.5"/><circle cx="15" cy="12" r="5.5"/>',
    search: '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
    box: '<path d="M4 7h16v3H4zM5.5 10v9h13v-9M10 14h4"/>',
    log: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    more: '<circle cx="5.5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18.5" cy="12" r="1.2"/>',
    eq: '<path d="M6 4v3M6 11v9M12 4v9M12 17v3M18 4v1M18 9v11"/><circle cx="6" cy="9" r="2"/><circle cx="12" cy="15" r="2"/><circle cx="18" cy="7" r="2"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    ext: '<path d="M7 17 17 7M9 7h8v8"/>',
    x: '<path d="M6 6l12 12M18 6L6 18"/>',
    side: '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><path d="M9 4.5v15"/>',
    gh: '<path d="M12 3a9 9 0 0 0-2.85 17.54c.45.08.62-.2.62-.43v-1.5c-2.5.55-3.03-1.2-3.03-1.2-.41-1.04-1-1.32-1-1.32-.82-.56.06-.55.06-.55.9.06 1.38.93 1.38.93.8 1.38 2.1.98 2.62.75.08-.58.31-.98.57-1.2-2-.22-4.1-1-4.1-4.45 0-.98.35-1.79.93-2.42-.1-.23-.4-1.14.09-2.38 0 0 .76-.24 2.48.92a8.6 8.6 0 0 1 4.52 0c1.72-1.16 2.48-.92 2.48-.92.49 1.24.18 2.15.09 2.38.58.63.93 1.44.93 2.42 0 3.46-2.1 4.22-4.11 4.44.32.28.61.83.61 1.67v2.47c0 .24.16.52.62.43A9 9 0 0 0 12 3z"/>'
  };
  function ic(n, c) { return '<svg class="ni' + (c ? ' ' + c : '') + '" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + P[n] + '</svg>'; }
  var LOGO = '<span class="n-logo" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false"><path d="M3 8c2.2 0 2.2-2.5 4.5-2.5S9.8 8 12 8s2.2-2.5 4.5-2.5S18.8 8 21 8"/><path d="M3 13c2.2 0 2.2-2.5 4.5-2.5S9.8 13 12 13s2.2-2.5 4.5-2.5S18.8 13 21 13" opacity=".7"/><path d="M3 18h18" opacity=".4"/></svg></span>';
  var G = [['setup', 'Setup', 'profile'], ['apply', 'Apply', 'check'], ['files', 'Files', 'download'], ['evidence', 'Evidence', 'dash'], ['faq', 'FAQ', 'help']];
  var T = [['compare.html', 'Compare', 'merge'], ['finder.html', 'Finder', 'search'], ['archive.html', 'Archive', 'box'], ['changelog.html', 'Changelog', 'log']];
  var gHref = function (id) { return (home ? '' : 'index.html') + '#' + id; };
  var tAttr = function (t) { return t[0] === file ? ' aria-current="page"' : ''; };
  var themeBtn = function (c) { return '<button type="button" class="' + c + '" data-n-theme aria-label="Toggle light or dark theme"><span class="n-sun">' + ic('sun') + '</span><span class="n-moon">' + ic('moon') + '</span></button>'; };
  var chip = '<a class="n-chip" href="' + gHref('setup') + '" title="Active profile" data-tip="Active profile">' + ic('eq') + '<span class="n-chip-t">Profile</span></a>';

  function gLinks(cls) {
    return G.map(function (g) {
      return '<a class="' + cls + '" href="' + gHref(g[0]) + '" data-k="' + g[0] + '" data-tip="' + g[1] + '">' + ic(g[2]) + '<span class="nt">' + g[1] + '</span></a>';
    }).join('');
  }
  function tLinks(cls) {
    return T.map(function (t) {
      return '<a class="' + cls + '" href="' + t[0] + '"' + tAttr(t) + ' data-tip="' + t[1] + '">' + ic(t[2]) + '<span class="nt">' + t[1] + '</span></a>';
    }).join('');
  }

  var main = D.querySelector('.shell') || D.querySelector('main');
  if (!main) return;
  var mainEl = D.querySelector('main');
  if (mainEl && !mainEl.id) mainEl.id = 'main';
  B.classList.add('n-on', home ? 'n-home' : 'n-pg');
  if (!D.querySelector('.skip')) { var s = D.createElement('a'); s.className = 'skip'; s.href = '#main'; s.textContent = 'Skip to content'; B.insertBefore(s, B.firstChild); }

  var wrap = D.createElement('div');
  wrap.innerHTML =
    '<header class="mh"><a class="mh-b" href="' + gHref('setup') + '" aria-label="HyperAudio home">' + LOGO + '<b>HyperAudio</b></a>' + chip + '</header>' +
    '<aside class="sb" id="sb" aria-label="Site">' +
      '<div class="sb-top"><a class="sb-brand" href="' + (home ? '#setup' : 'index.html') + '" aria-label="HyperAudio home">' + LOGO + '<span class="sb-bt"><b>HyperAudio</b><small class="n-ver"></small></span></a>' +
      '<button type="button" class="sb-tg" aria-expanded="false" aria-controls="sb" aria-label="Expand sidebar">' + ic('side') + '</button></div>' +
      '<p class="sb-badge"><i aria-hidden="true"></i><span class="nt">Stable · device-tested</span></p>' +
      '<div class="sb-scroll">' +
        '<div role="navigation" aria-labelledby="sbg"><p class="sb-h nt" id="sbg">Guide</p>' + gLinks('nl') + '</div>' +
        '<div role="navigation" aria-labelledby="sbt"><p class="sb-h nt" id="sbt">Tools</p>' + tLinks('nl') + '</div>' +
      '</div>' +
      '<div class="sb-bot">' + chip + '<div class="sb-ctl">' + themeBtn('nb') +
        '<a class="nb" href="' + GH + '" target="_blank" rel="noopener noreferrer" aria-label="GitHub repository (opens in new tab)" data-tip="GitHub">' + ic('gh') + '</a></div>' +
        '<p class="sb-cr nt">Tested by Noushad Mostafa</p></div>' +
    '</aside><div class="sb-scrim" hidden></div>';
  var frag = D.createDocumentFragment();
  while (wrap.firstChild) frag.appendChild(wrap.firstChild);
  B.insertBefore(frag, main);
  var foot = D.createElement('div');
  foot.className = 'sf'; foot.setAttribute('role', 'contentinfo');
  foot.innerHTML = '<div class="sf-in"><p class="sf-v"><b>HyperAudio</b><span class="n-ver"></span></p>' +
    '<p class="sf-e"><i aria-hidden="true"></i>Device-tested · responses calculated, not measured</p>' +
    '<p class="sf-c">Tested by Noushad Mostafa</p>' +
    '<p class="sf-l"><a href="' + GH + '" target="_blank" rel="noopener noreferrer">GitHub</a></p></div>';
  B.appendChild(foot);



  var bb = D.createElement('div');
  bb.className = 'bb'; bb.setAttribute('role', 'navigation'); bb.setAttribute('aria-label', 'Primary');
  bb.innerHTML = gLinks('bl') + '<button type="button" class="bl bb-more" aria-haspopup="dialog" aria-expanded="false" aria-controls="sheet"' + (home ? '' : ' aria-current="true"') + '>' + ic('more') + '<span class="nt">More</span></button>';
  B.appendChild(bb);

  var sheet = D.createElement('div');
  sheet.className = 'sheet'; sheet.id = 'sheet'; sheet.hidden = true;
  sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-modal', 'true'); sheet.setAttribute('aria-label', 'More');
  sheet.innerHTML = '<div class="sheet-bg" data-close></div><div class="sheet-p"><div class="sheet-h"><span class="sheet-grab" aria-hidden="true"></span><p>More</p>' +
    '<button type="button" class="nb" data-close aria-label="Close">' + ic('x') + '</button></div>' +
    '<div role="navigation" aria-label="Tools" class="sheet-l">' + tLinks('sl') +
      '<a class="sl" href="' + GH + '" target="_blank" rel="noopener noreferrer">' + ic('gh') + '<span class="nt">GitHub</span>' + ic('ext', 'sl-x') + '</a>' +
      '<button type="button" class="sl" data-n-theme>' + '<span class="n-sun">' + ic('sun') + '</span><span class="n-moon">' + ic('moon') + '</span><span class="nt n-tl">Theme</span></button>' +
    '</div></div>';
  B.appendChild(sheet);

  function themeSync() {
    var l = R.dataset.theme === 'light';
    D.querySelectorAll('[data-n-theme]').forEach(function (b) {
      b.setAttribute('aria-pressed', l);
      if (!b.classList.contains('sl')) b.setAttribute('aria-label', l ? 'Switch to dark theme' : 'Switch to light theme');
    });
    var tl = D.querySelector('.n-tl'); if (tl) tl.textContent = l ? 'Switch to dark theme' : 'Switch to light theme';
  }
  D.addEventListener('click', function (e) {
    if (!e.target.closest('[data-n-theme]')) return;
    var n = R.dataset.theme === 'light' ? 'dark' : 'light';
    R.dataset.theme = n; try { localStorage.setItem('ha-theme', n); } catch (x) {}
    themeSync();
  });
  themeSync();

  var more = bb.querySelector('.bb-more'), closeT;
  function sheetOpen() {
    clearTimeout(closeT); sheet.hidden = false; R.classList.add('nav-lock');
    more.setAttribute('aria-expanded', 'true');
    requestAnimationFrame(function () { sheet.classList.add('open'); var f = sheet.querySelector('.sl'); if (f) f.focus(); });
  }
  function sheetClose(back) {
    if (sheet.hidden) return;
    sheet.classList.remove('open'); R.classList.remove('nav-lock'); more.setAttribute('aria-expanded', 'false');
    closeT = setTimeout(function () { sheet.hidden = true; }, 220);
    if (back !== false) more.focus();
  }
  more.addEventListener('click', function () { sheet.hidden ? sheetOpen() : sheetClose(); });
  sheet.addEventListener('click', function (e) { if (e.target.closest('[data-close]')) sheetClose(); else if (e.target.closest('a.sl')) sheetClose(false); });

  var sb = D.getElementById('sb'), tg = sb.querySelector('.sb-tg'), scrim = D.querySelector('.sb-scrim');
  function rail(open) {
    sb.dataset.open = open ? 'true' : 'false'; scrim.hidden = !open;
    tg.setAttribute('aria-expanded', open); tg.setAttribute('aria-label', open ? 'Collapse sidebar' : 'Expand sidebar');
  }
  tg.addEventListener('click', function () { rail(sb.dataset.open !== 'true'); });
  scrim.addEventListener('click', function () { rail(false); tg.focus(); });
  sb.addEventListener('click', function (e) { if (e.target.closest('a.nl') && sb.dataset.open === 'true') rail(false); });

  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (!sheet.hidden) { sheetClose(); e.preventDefault(); }
      else if (sb.dataset.open === 'true') { rail(false); tg.focus(); }
      return;
    }
    if (e.key === 'Tab' && !sheet.hidden) {
      var f = sheet.querySelectorAll('a[href],button'); if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && D.activeElement === a) { z.focus(); e.preventDefault(); }
      else if (!e.shiftKey && D.activeElement === z) { a.focus(); e.preventDefault(); }
    }
  });
  var mq = matchMedia('(min-width:768px)');
  (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(function () { sheetClose(false); rail(false); });
  rail(false);

  function setCur(k) {
    D.querySelectorAll('[data-k]').forEach(function (a) {
      if (a.dataset.k === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
  }
  if (home) {
    var ORDER = [['overview', 'setup'], ['setup', 'setup'], ['apply', 'apply'], ['files', 'files'], ['evidence', 'evidence'], ['status', 'evidence'], ['hardware', 'evidence'], ['faq', 'faq']], tick = false;
    var spy = function () {
      tick = false;
      var k = 'setup', line = innerHeight * 0.3;
      ORDER.forEach(function (o) { var el = D.getElementById(o[0]); if (el && el.getBoundingClientRect().top <= line) k = o[1]; });
      if (innerHeight + scrollY >= R.scrollHeight - 4) k = 'faq';
      setCur(k);
    };
    var req = function () { if (!tick) { tick = true; requestAnimationFrame(spy); } };
    addEventListener('scroll', req, { passive: true }); addEventListener('resize', req); addEventListener('hashchange', req);
    spy(); setTimeout(spy, 500); addEventListener('load', spy);
  }

  fetch('data/profiles.json').then(function (r) { return r.ok ? r.json() : Promise.reject(); }).then(function (d) {
    D.querySelectorAll('.n-ver').forEach(function (n) { n.textContent = d.version || ''; });
    var id; try { id = localStorage.getItem('ha-profile'); } catch (x) {}
    var p = (d.profiles || []).filter(function (q) { return q.id === id; })[0] || (d.profiles || [])[0];
    D.querySelectorAll('.n-chip-t').forEach(function (n) { if (p && n.textContent === 'Profile') n.textContent = p.name; });
  }).catch(function () {});
})();
