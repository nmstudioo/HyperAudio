const VERSION = '7.0.0', CACHE = 'hyperaudio-' + VERSION + '-4c065afa';

const SHELL = ['./', 'apply.html', 'archive.html', 'assets/css/base.css', 'assets/css/docs.css', 'assets/css/fonts.css', 'assets/css/nav.css', 'assets/css/tokens.css', 'assets/fonts/jetbrains-mono-latin-400-normal.woff2', 'assets/fonts/jetbrains-mono-latin-700-normal.woff2', 'assets/fonts/plus-jakarta-sans-latin-400-normal.woff2', 'assets/fonts/plus-jakarta-sans-latin-600-normal.woff2', 'assets/fonts/plus-jakarta-sans-latin-800-normal.woff2', 'assets/icons/favicon.svg', 'assets/js/app.js', 'assets/js/chart.js', 'assets/js/docs.js', 'assets/js/nav.js', 'assets/js/pages.js', 'assets/js/theme-init.js', 'changelog.html', 'compare.html', 'data/choose.json', 'data/evidence.json', 'data/profiles.json', 'data/versions.json', 'docs/index.html', 'evidence.html', 'faq.html', 'files.html', 'finder.html', 'index.html', 'manifest.webmanifest', 'setup.html'];
const MAX_RUNTIME = 60;
const cacheable = u => !/\.(zip|eel|irs|vdc)$/i.test(u.pathname) && !u.pathname.includes('/downloads/');
async function trim(c) { const k = await c.keys(); if (k.length > MAX_RUNTIME + SHELL.length) await Promise.all(k.slice(0, k.length - MAX_RUNTIME - SHELL.length).map(x => c.delete(x))); }
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n.startsWith('hyperaudio-') && n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
const r = e.request, u = new URL(r.url);
if (r.method !== 'GET') return;
if (u.origin !== location.origin) return;
e.respondWith(fetch(r).then(res => {
if (res.ok && res.type === 'basic' && !r.headers.has('range') && cacheable(u)) { const copy = res.clone(), key = new Request(u.origin + u.pathname); caches.open(CACHE).then(c => c.put(key, copy).then(() => trim(c))); }
return res;
}).catch(() => caches.match(new Request(u.origin + u.pathname)).then(m => m || caches.match(r, { ignoreSearch: true })).then(m => m || (r.mode === 'navigate' ? (u.pathname.endsWith('/') ? caches.match('index.html') : new Response('You are offline and this page is not saved yet.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } })) : Response.error()))));
});
