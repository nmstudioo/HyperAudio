"""SEO gate (offline, stdlib). python3 tests/seo_audit.py  -> exit 1 on any failure."""
import glob, json, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = f'{ROOT}/site'; sys.path.insert(0, f'{ROOT}/build'); from siteconfig import SITE as BASE
errs = []
def need(c, m):
    if not c: errs.append(m)
class H(HTMLParser):
    def __init__(s): super().__init__(); s.m = {}; s.h = []; s.imgs = []; s.a = []; s.t = ''; s._t = 0; s.ld = []; s._ld = 0; s.can = []; s.lang = None; s._h = None; s.vp = False
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == 'html': s.lang = a.get('lang')
        if tag == 'title': s._t = 1
        if tag == 'meta':
            k = a.get('name') or a.get('property')
            if k: s.m.setdefault(k, []).append(a.get('content', ''))
            if a.get('name') == 'viewport': s.vp = True
        if tag == 'link' and a.get('rel') == 'canonical': s.can.append(a.get('href'))
        if tag == 'script' and a.get('type') == 'application/ld+json': s._ld = 1; s.ld.append('')
        if tag in ('h1', 'h2', 'h3'): s._h = [tag, '']
        if tag == 'img': s.imgs.append(a)
        if tag == 'a' and a.get('href'): s.a.append(a['href'])
    def handle_endtag(s, tag):
        if tag == 'title': s._t = 0
        if tag == 'script': s._ld = 0
        if s._h and tag == s._h[0]: s.h.append(tuple(s._h)); s._h = None
    def handle_data(s, d):
        if s._t: s.t += d
        if s._ld: s.ld[-1] += d
        if s._h: s._h[1] += d
pages = sorted(f for f in glob.glob(f'{S}/**/*.html', recursive=True) if not os.path.basename(f).startswith('google')); urls = set()
sm = open(f'{S}/sitemap.xml', encoding='utf-8').read() if os.path.exists(f'{S}/sitemap.xml') else ''
need(sm, 'sitemap.xml missing'); need('Sitemap: ' + BASE + 'sitemap.xml' in open(f'{S}/robots.txt').read(), 'robots.txt lacks Sitemap line')
for f in pages:
    r = os.path.relpath(f, S); p = H(); p.feed(open(f, encoding='utf-8').read())
    if r == '404.html':
        need('noindex' in ' '.join(p.m.get('robots', [])), '404 must be noindex'); need(BASE + '404.html' not in sm, '404 in sitemap'); continue
    d = p.m.get('description', [''])[0]; t = p.t.strip(); u = BASE if r == 'index.html' else BASE + ('docs/' if r == 'docs/index.html' else r)
    need(p.lang == 'en', f'{r}: html lang'); need(p.vp, f'{r}: viewport')
    need(15 <= len(t) <= 60, f'{r}: title length {len(t)} ({t!r})'); need(70 <= len(d) <= 160, f'{r}: description length {len(d)}')
    need(len(p.m.get('description', [])) == 1, f'{r}: description count'); need(p.can == [u], f'{r}: canonical {p.can} != {u}')
    need('<loc>%s</loc>' % u in sm, f'{r}: not in sitemap')
    for k in ('og:title', 'og:description', 'og:url', 'og:image', 'og:type', 'twitter:card', 'twitter:image'): need(len(p.m.get(k, [])) == 1, f'{r}: {k} count {len(p.m.get(k, []))}')
    need(p.m.get('og:url', [''])[0] == u, f'{r}: og:url mismatch'); need('noindex' not in ' '.join(p.m.get('robots', [])), f'{r}: accidental noindex')
    h1 = [h for h in p.h if h[0] == 'h1']; need(len(h1) == 1, f'{r}: h1 count {len(h1)}')
    lv = [int(h[0][1]) for h in p.h]; need(all(b - a <= 1 for a, b in zip(lv, lv[1:])), f'{r}: heading level skip {lv}')
    for i in p.imgs: need(i.get('alt') is not None, f'{r}: img without alt {i.get("src")}')
    for j in p.ld:
        try: json.loads(j)
        except Exception as e: errs.append(f'{r}: invalid JSON-LD {e}')
    need(len(p.ld) >= 1, f'{r}: no JSON-LD')
    for a in p.a:  # internal links must resolve
        if a.startswith(('http', 'mailto:', '#', 'javascript:', 'data:')): continue
        q = os.path.normpath(os.path.join(os.path.dirname(f), a.split('#')[0].split('?')[0] or '.'))
        need(os.path.exists(q) or os.path.exists(q + '/index.html'), f'{r}: broken internal link {a}')
    for a in p.a:
        need(not re.fullmatch(r'(click here|here|read more)', a.lower()), f'{r}: non-descriptive link')
ts = [re.search(r'<title>(.*?)</title>', open(f, encoding='utf-8').read(), re.S)[1] for f in pages if not f.endswith('404.html')]
need(len(ts) == len(set(ts)), 'duplicate titles'); 
ds = []
for f in pages:
    if f.endswith('404.html'): continue
    m = re.search(r'name="description" content="([^"]*)"', open(f, encoding='utf-8').read()); ds.append(m[1] if m else '')
need(len(ds) == len(set(ds)), 'duplicate descriptions')
home = open(f'{S}/index.html', encoding='utf-8').read(); txt = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', home, flags=re.S)
for kw in ('RootlessJamesDSP', 'KZ EDX Pro', 'Redmi 12', 'VDC', 'impulse response'): need(kw in txt, f'home static text lacks "{kw}"')
print('seo audit: %d pages' % (len(pages) - 1), 'FAILED:' if errs else 'ok'); [print(' -', e) for e in errs]; sys.exit(1 if errs else 0)
