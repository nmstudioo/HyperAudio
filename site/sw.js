const VERSION = '6.1.0', CACHE = 'hyperaudio-' + VERSION;
const SHELL = ['./', 'index.html', 'compare.html', 'finder.html', 'archive.html', 'changelog.html', 'assets/css/main.css', 'assets/css/site.css', 'assets/css/v7-ui.css', 'assets/css/nav.css', 'assets/css/docs.css', 'assets/js/docs.js', 'data/evidence.json', 'docs/index.html', 'assets/js/app.js', 'assets/js/chart.js', 'assets/js/nav.js', 'assets/js/v7-ui.js', 'assets/js/theme-init.js', 'data/profiles.json', 'data/versions.json', 'data/choose.json', 'manifest.webmanifest', 'assets/icons/favicon.svg'];
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'], MAX_RUNTIME = 60;
const cacheable = u => !/\.(zip|eel|irs|vdc)$/i.test(u.pathname) && !u.pathname.includes('/downloads/');
async function trim(c) { const k = await c.keys(); if (k.length > MAX_RUNTIME + SHELL.length) await Promise.all(k.slice(0, k.length - MAX_RUNTIME - SHELL.length).map(x => c.delete(x))); }
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n.startsWith('hyperaudio-') && n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
const r = e.request, u = new URL(r.url);
if (r.method !== 'GET') return;
if (FONT_HOSTS.includes(u.hostname)) {
e.respondWith(caches.open(CACHE).then(c => c.match(r).then(m => { const f = fetch(r).then(res => { if (res.ok || res.type === 'opaque') c.put(r, res.clone()); return res; }).catch(() => m || Response.error()); return m || f; })));
return;
}
if (u.origin !== location.origin) return;
e.respondWith(fetch(r).then(res => {
if (res.ok && res.type === 'basic' && !r.headers.has('range') && cacheable(u)) { const copy = res.clone(), key = new Request(u.origin + u.pathname); caches.open(CACHE).then(c => c.put(key, copy).then(() => trim(c))); }
return res;
}).catch(() => caches.match(new Request(u.origin + u.pathname)).then(m => m || caches.match(r, { ignoreSearch: true })).then(m => m || (r.mode === 'navigate' ? (u.pathname.endsWith('/') ? caches.match('index.html') : new Response('You are offline and this page is not saved yet.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } })) : Response.error()))));
});
