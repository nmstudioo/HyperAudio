#!/usr/bin/env python3
"""Render docs/*.md to site/docs/*.html so doc links exist on the published site."""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from siteconfig import REPO, BRANCH
GH = f'{REPO}/blob/{BRANCH}/'
DOCS = sorted(f[:-3] for f in os.listdir(f'{ROOT}/docs') if f.endswith('.md'))
def url(u):
    m = re.match(r'^(?:\./|\.\./|/)?(.*?)(#.*)?$', u); p, h = m[1], m[2] or ''
    if re.match(r'^(https?:|mailto:|#)', u): return u
    if p.endswith('.md') and p[:-3].split('/')[-1] in DOCS and not p.startswith(('src', 'releases')): return p[:-3].split('/')[-1] + '.html' + h
    if p.startswith('docs/') and p.endswith('.md') and p[5:-3] in DOCS: return p[5:-3] + '.html' + h
    return GH + p + h
def inline(s):
    s = html.escape(s.replace('\\|', '|'), quote=False); codes = []
    s = re.sub(r'&lt;(/?)(br|kbd|sub|sup|b|i|em|strong|code)\s*/?&gt;', lambda m: '<%s%s>' % (m[1], m[2]), s)
    s = re.sub(r'`([^`]+)`', lambda m: codes.append(m[1]) or '\0%d\0' % (len(codes) - 1), s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s"%s>%s</a>' % (html.escape(url(m[2])), ' target="_blank" rel="noopener"' if url(m[2]).startswith('http') else '', m[1]), s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s); s = re.sub(r'(?<![\w*])\*([^*]+)\*(?![\w*])', r'<i>\1</i>', s)
    return re.sub(r'\0(\d+)\0', lambda m: '<code>%s</code>' % codes[int(m[1])], s)
def md(text):
    out, L, i, title = [], text.split('\n'), 0, None
    while i < len(L):
        l = L[i]
        if l.startswith('```'):
            j = i + 1
            while j < len(L) and not L[j].startswith('```'): j += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(L[i+1:j]), quote=False)); i = j + 1; continue
        if re.match(r'^\s{0,3}([-*_])(\s*\1){2,}\s*$', l): out.append('<hr>'); i += 1; continue
        if l.startswith('>'):
            q = []
            while i < len(L) and L[i].startswith('>'): q.append(re.sub(r'^>\s?', '', L[i])); i += 1
            out.append('<blockquote>%s</blockquote>' % md('\n'.join(q))[0]); continue
        m = re.match(r'^(#{1,4})\s+(.*)$', l)
        if m:
            n = len(m[1]); title = title or m[2]; out.append('<h%d>%s</h%d>' % (n, inline(m[2]), n)); i += 1; continue
        if l.startswith('|') and i + 1 < len(L) and re.match(r'^\|[\s:|-]+\|?\s*$', L[i+1]):
            cells = lambda r: [c.strip() for c in re.split(r'(?<!\\)\|', r.strip().strip('|'))]
            t = '<div class="tw" tabindex="0"><table class="evt"><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % inline(c) for c in cells(l)); i += 2
            while i < len(L) and L[i].startswith('|'): t += '<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in cells(L[i])); i += 1
            out.append(t + '</tbody></table></div>'); continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', l)
        if m:
            def lst(i, ind):
                tag = 'ol' if re.match(r'\d', L[i].lstrip()) else 'ul'; st = int(re.match(r'\s*(\d+)', L[i])[1]) if tag == 'ol' else 1; items = []
                while i < len(L) and (mm := re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', L[i])):
                    d = len(mm[1].replace('\t', '    '))
                    if d < ind: break
                    if d > ind:
                        sub, i = lst(i, d)
                        if items: items[-1] += sub
                        else: items.append(sub)
                        continue
                    items.append(inline(mm[3])); i += 1
                return '<%s%s>%s</%s>' % (tag, ' start="%d"' % st if st > 1 else '', ''.join('<li>%s</li>' % x for x in items), tag), i
            h, i = lst(i, len(m[1].replace('\t', '    '))); out.append(h); continue
        if l.strip():
            p = []
            while i < len(L) and L[i].strip() and not re.match(r'^(#{1,4}\s|```|\||>|\s*([-*]|\d+\.)\s)', L[i]): p.append(L[i].strip()); i += 1
            out.append('<p>%s</p>' % inline(' '.join(p)) if p else ''); i += 0 if p else 1; continue
        i += 1
    return '\n'.join(out), title or 'Docs'
ORDER = ['METHOD', 'EVIDENCE', 'LIMITS', 'OPEN', 'REPRODUCING', 'RELEASING', 'CHANGELOG', 'refit44_report']
LABEL = dict(METHOD='Method', EVIDENCE='Evidence', LIMITS='Limits', OPEN='Open items', REPRODUCING='Reproduce', RELEASING='Releasing', CHANGELOG='Changelog', refit44_report='44.1 kHz refit')
STATUS = ('pass', 'warn', 'fail', 'not_run', 'untested')
COPY = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" width="18" height="18"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/></svg>'
def slug(t): return re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', t).lower()).strip('-') or 'section'
def decorate(body):
    seen, toc = {}, []
    def head(m):
        n, inner = m[1], m[2]; k = slug(inner); seen[k] = seen.get(k, 0) + 1; k = k if seen[k] == 1 else f'{k}-{seen[k]}'
        toc.append((int(n), re.sub(r'<[^>]+>', '', inner), k)); return f'<h{n} id="{k}">{inner}<a class="ha" href="#{k}" aria-label="Link to this section">#</a></h{n}>'
    body = re.sub(r'<h([23])>(.*?)</h\1>', head, body)
    body = re.sub(r'<pre><code>(.*?)</code></pre>', lambda m: f'<div class="cb"><pre tabindex="0"><code>{m[1]}</code></pre><button type="button" class="cp" aria-label="Copy code">{COPY}</button></div>', body, flags=re.S)
    body = re.sub(r'<code>(%s)</code>' % '|'.join(STATUS), lambda m: f'<span class="st st-{m[1]}">{m[1].replace("_", " ")}</span>', body)
    return body, toc
def split_head(b):
    m = re.match(r'\s*<h1>(.*?)</h1>\s*(?:<p>(.*?)</p>)?', b, re.S)
    return (m[1], m[2] or '', b[m.end():]) if m else ('', '', b)
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
_G = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
_L = '<link rel="preload" href="../assets/fonts/plus-jakarta-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="../assets/css/fonts.css">'
FONTS = _L if _os.path.exists(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'site', 'assets', 'css', 'fonts.css')) else _G
PAGE = """<!doctype html>
<html lang="en" data-base="../"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'">
<title>%(t)s · HyperAudio docs</title><meta name="description" content="%(d)s">
<link rel="icon" href="../assets/icons/favicon.svg" type="image/svg+xml">
<script src="../assets/js/theme-init.js"></script>
%(fonts)s
<link rel="stylesheet" href="../assets/css/main.css"><link rel="stylesheet" href="../assets/css/site.css"><link rel="stylesheet" href="../assets/css/nav.css"><link rel="stylesheet" href="../assets/css/docs.css">
</head>
<body>
<main class="pg dpg" id="main">
<header class="dh"><span class="eyebrow">Docs</span><h1>%(h)s</h1>%(lead)s%(src)s</header>
<nav class="dtabs" aria-label="Docs sections">%(tabs)s</nav>
<div class="dgrid%(hasToc)s">
<article class="prose">
%(b)s
%(pn)s</article>
%(toc)s</div>
</main>
<script src="../assets/js/docs.js"></script>
<script src="../assets/js/nav.js"></script>
</body></html>
"""
def tabs(cur, titles):
    return ''.join('<a href="%s.html"%s>%s</a>' % (n, ' aria-current="page"' if n == cur else '', html.escape(LABEL.get(n, titles[n]))) for n in ORDER_ALL) + ('<a href="./"%s>All docs</a>' % (' aria-current="page"' if cur == 'index' else ''))
def render():
    global ORDER_ALL
    ORDER_ALL = [n for n in ORDER if n in DOCS] + [n for n in DOCS if n not in ORDER]
    raw = {n: md(open(f'{ROOT}/docs/{n}.md', encoding='utf-8').read()) for n in ORDER_ALL}; titles = {n: raw[n][1] for n in ORDER_ALL}; pages = {}; cards = []
    for i, n in enumerate(ORDER_ALL):
        body, toc = decorate(raw[n][0]); h, lead, rest = split_head(body)
        if not h: h, rest = titles[n], body
        plain = re.sub(r'<[^>]+>', '', lead)
        pn = ''
        if len(ORDER_ALL) > 1:
            pv, nx = (ORDER_ALL[i - 1] if i else None), (ORDER_ALL[i + 1] if i + 1 < len(ORDER_ALL) else None)
            pn = '<nav class="dnav" aria-label="Previous and next">' + ('<a href="%s.html"><span class="k">Previous</span><b>%s</b></a>' % (pv, html.escape(LABEL.get(pv, titles[pv]))) if pv else '') + ('<a href="%s.html"><span class="k">Next</span><b>%s</b></a>' % (nx, html.escape(LABEL.get(nx, titles[nx]))) if nx else '') + '</nav>'
        tl = ''.join('<li class="l%d"><a href="#%s">%s</a></li>' % (lv, k, html.escape(t)) for lv, t, k in toc)
        tocx = '<aside class="dtoc" aria-label="On this page"><details open><summary>On this page</summary><ol>%s</ol></details></aside>' % tl if len(toc) >= 3 else ''
        src = '<a class="src" href="%sdocs/%s.md" target="_blank" rel="noopener">docs/%s.md &middot; edit on GitHub</a>' % (GH, n, n)
        pages[f'{n}.html'] = PAGE % dict(fonts=FONTS, t=html.escape(re.sub(r'<[^>]+>', '', h)), d=html.escape(plain[:155] or 'HyperAudio documentation'), h=h, lead='<p class="lead">%s</p>' % lead if lead else '', src=src, tabs=tabs(n, titles), hasToc=' has-toc' if tocx else '', b=rest, pn=pn, toc=tocx)
        cards.append('<li><a class="dcard" href="%s.html"><span class="k">docs/%s.md</span><b>%s</b><span class="d">%s</span><span class="go">Read &rarr;</span></a></li>' % (n, n, html.escape(LABEL.get(n, titles[n])), html.escape((plain[:110] + ('…' if len(plain) > 110 else '')) or 'Open the page.')))
    pages['index.html'] = PAGE % dict(fonts=FONTS, t='Docs', d='HyperAudio documentation: method, evidence, limits, open items and how to reproduce the build.', h='Documentation', lead='<p class="lead">How the profiles are built, what the evidence shows, and what is still open.</p>', src='', tabs=tabs('index', titles), hasToc='', b='<ul class="dcards">%s</ul>' % ''.join(cards), pn='', toc='')
    import seo
    pages = {k: seo.process('docs/' + k, v) for k, v in pages.items()}
    return pages
def evidence_json():
    d = f'{ROOT}/docs/evidence'
    return {f: open(f'{d}/{f}', 'rb').read() for f in sorted(os.listdir(d)) if f.endswith('.json')} if os.path.isdir(d) else {}
if __name__ == '__main__':
    pages, d = render(), f'{ROOT}/site/docs'; os.makedirs(d + '/evidence', exist_ok=True); ev = evidence_json()
    if '--check' in sys.argv:
        bad = [k for k, v in pages.items() if not os.path.exists(f'{d}/{k}') or open(f'{d}/{k}', encoding='utf-8').read() != v] + [f for f in os.listdir(d) if f.endswith('.html') and f not in pages]
        bad += ['evidence/' + k for k, v in ev.items() if not os.path.exists(f'{d}/evidence/{k}') or open(f'{d}/evidence/{k}', 'rb').read() != v]
        print('docs pages stale: ' + ', '.join(bad) if bad else 'docs pages up to date'); sys.exit(1 if bad else 0)
    for k, v in pages.items(): open(f'{d}/{k}', 'w', encoding='utf-8').write(v)
    for k, v in ev.items(): open(f'{d}/evidence/{k}', 'wb').write(v)
    print('wrote %d pages to site/docs' % len(pages))
