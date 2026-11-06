#!/usr/bin/env python3
"""Render docs/*.md to site/docs/*.html so doc links exist on the published site.
python3 build/docs_site.py          write
python3 build/docs_site.py --check  exit 1 if site/docs is stale"""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH = 'https://github.com/nmstudioo/HyperAudio/blob/main/'
DOCS = sorted(f[:-3] for f in os.listdir(f'{ROOT}/docs') if f.endswith('.md'))

def url(u):
    m = re.match(r'^(?:\./|\.\./|/)?(.*?)(#.*)?$', u); p, h = m[1], m[2] or ''
    if re.match(r'^(https?:|mailto:|#)', u): return u
    if p.endswith('.md') and p[:-3].split('/')[-1] in DOCS and not p.startswith(('src', 'releases')): return p[:-3].split('/')[-1] + '.html' + h
    if p.startswith('docs/') and p.endswith('.md') and p[5:-3] in DOCS: return p[5:-3] + '.html' + h
    return GH + p + h

def inline(s):
    s = html.escape(s, quote=False); codes = []
    s = re.sub(r'`([^`]+)`', lambda m: codes.append(m[1]) or '\0%d\0' % (len(codes) - 1), s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s"%s>%s</a>' % (html.escape(url(m[2])), ' target="_blank" rel="noopener"' if url(m[2]).startswith('http') else '', m[1]), s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s); s = re.sub(r'(?<![\w*])\*([^*]+)\*(?![\w*])', r'<i>\1</i>', s)
    return re.sub(r'\0(\d+)\0', lambda m: '<code>%s</code>' % html.escape(codes[int(m[1])], quote=False), s)

def md(text):
    out, L, i, title = [], text.split('\n'), 0, None
    while i < len(L):
        l = L[i]
        if l.startswith('```'):
            j = i + 1
            while j < len(L) and not L[j].startswith('```'): j += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(L[i+1:j]), quote=False)); i = j + 1; continue
        m = re.match(r'^(#{1,4})\s+(.*)$', l)
        if m:
            n = len(m[1]); title = title or m[2]; out.append('<h%d>%s</h%d>' % (n, inline(m[2]), n)); i += 1; continue
        if l.startswith('|') and i + 1 < len(L) and re.match(r'^\|[\s:|-]+\|?\s*$', L[i+1]):
            cells = lambda r: [c.strip() for c in r.strip().strip('|').split('|')]
            t = '<div class="tw"><table class="evt"><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % inline(c) for c in cells(l)); i += 2
            while i < len(L) and L[i].startswith('|'): t += '<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in cells(L[i])); i += 1
            out.append(t + '</tbody></table></div>'); continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', l)
        if m:
            tag = 'ol' if m[2][0].isdigit() else 'ul'; items = []
            while i < len(L) and (mm := re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', L[i])): items.append(inline(mm[3])); i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % x for x in items), tag)); continue
        if l.strip():
            p = []
            while i < len(L) and L[i].strip() and not re.match(r'^(#{1,4}\s|```|\||\s*([-*]|\d+\.)\s)', L[i]): p.append(L[i].strip()); i += 1
            out.append('<p>%s</p>' % inline(' '.join(p)) if p else ''); i += 0 if p else 1; continue
        i += 1
    return '\n'.join(out), title or 'Docs'

PAGE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>%(t)s · HyperAudio docs</title><link rel="icon" href="../assets/icons/favicon.svg" type="image/svg+xml">
<script src="../assets/js/theme-init.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/main.css"><link rel="stylesheet" href="../assets/css/site.css">
<style>.dtop{display:flex;gap:14px;align-items:center;flex-wrap:wrap;max-width:820px;margin:0 auto;padding:max(14px,env(safe-area-inset-top)) 16px 0;font:600 13px var(--mono)}.dtop a{color:var(--tx2);text-decoration:none}.dtop a:hover{color:var(--acc)}
.dc{max-width:820px;margin:0 auto;padding:12px 16px max(48px,env(safe-area-inset-bottom))}.dc h1{font:800 clamp(26px,6vw,34px)/1.15 var(--sans);margin:.6em 0 .4em}.dc h2{font:700 21px var(--sans);margin:1.6em 0 .4em}.dc h3{font:700 17px var(--sans);margin:1.3em 0 .3em}
.dc p,.dc li{color:var(--tx2);line-height:1.65}.dc a{color:var(--acc);font-weight:600}.dc code{font:500 .9em var(--mono);background:rgba(128,128,128,.14);padding:1px 6px;border-radius:6px;overflow-wrap:anywhere}.dc pre{overflow-x:auto;padding:14px;border:1px solid var(--bd);border-radius:12px}.dc pre code{background:none;padding:0}.dc .tw{overflow-x:auto}</style></head>
<body><nav class="dtop" aria-label="Docs"><a href="../">&larr; HyperAudio</a><a href="./">Docs</a><a href="../archive.html">Archive</a><a href="../changelog.html">Changelog</a></nav>
<main class="dc" id="main">
%(b)s
</main></body></html>
'''
def render():
    pages, idx = {}, []
    for n in DOCS:
        b, t = md(open(f'{ROOT}/docs/{n}.md', encoding='utf-8').read()); pages[f'{n}.html'] = PAGE % dict(t=html.escape(t), b=b); idx.append((n, t))
    li = '\n'.join('<li><a href="%s.html">%s</a> <small>docs/%s.md</small></li>' % (n, html.escape(t), n) for n, t in idx)
    pages['index.html'] = PAGE % dict(t='Docs', b='<h1>Docs</h1>\n<ul>\n%s\n</ul>' % li)
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
