const VERSION = '6.0.0', CACHE = 'hyperaudio-' + VERSION;
const SHELL = ['./', 'index.html', 'compare.html', 'finder.html', 'archive.html', 'changelog.html', 'assets/css/main.css', 'assets/css/site.css', 'assets/css/nav.css', 'assets/css/docs.css', 'assets/js/docs.js', 'data/evidence.json', 'docs/index.html', 'assets/js/app.js', 'assets/js/chart.js', 'assets/js/nav.js', 'assets/js/theme-init.js', 'data/profiles.json', 'data/versions.json', 'data/choose.json', 'manifest.webmanifest', 'assets/icons/favicon.svg'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n.startsWith('hyperaudio-') && n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
const r = e.request, u = new URL(r.url);
if (r.method !== 'GET' || u.origin !== location.origin) return;
e.respondWith(fetch(r).then(res => {
if (res.ok && res.type === 'basic' && !r.headers.has('range')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); }
return res;
}).catch(() => caches.match(r, { ignoreSearch: true }).then(m => m || (r.mode === 'navigate' ? caches.match('index.html') : Response.error()))));
});
