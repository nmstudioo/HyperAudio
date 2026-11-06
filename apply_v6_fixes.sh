#!/usr/bin/env bash
# Run from the repo root: bash apply_v6_fixes.sh
set -e
mkdir -p build tests tools site/docs
cat > site/404.html <<'HA_EOF'
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#000000">
<title>Page not found · HyperAudio</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f2b13a' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M3 8c2.2 0 2.2-2.5 4.5-2.5S9.8 8 12 8s2.2-2.5 4.5-2.5S18.8 8 21 8M3 13c2.2 0 2.2-2.5 4.5-2.5S9.8 13 12 13s2.2-2.5 4.5-2.5S18.8 13 21 13M3 18c2.2 0 2.2-2.5 4.5-2.5S9.8 18 12 18s2.2-2.5 4.5-2.5S18.8 18 21 18'/%3E%3C/svg%3E">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap">
<script>try{document.documentElement.dataset.theme=localStorage.getItem('ha-theme')||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark')}catch(e){}</script>
<style>
:root{--bg:#000;--card:#0b0b0b;--bd:rgba(255,255,255,.09);--tx:#f4f1ea;--tx2:#b9b4a8;--mut:#8a857a;--acc:#f2b13a;--sans:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
:root[data-theme=light]{--bg:#f7f5ef;--card:#fff;--bd:rgba(0,0,0,.1);--tx:#17140d;--tx2:#4d483c;--mut:#7a7465;--acc:#b36f00}
*{box-sizing:border-box}html,body{margin:0}
body{min-height:100vh;display:grid;place-items:center;padding:max(20px,env(safe-area-inset-top)) 16px max(20px,env(safe-area-inset-bottom));background:radial-gradient(60% 40% at 50% 0,rgba(242,177,58,.12),transparent 70%),var(--bg);color:var(--tx);font:400 16px/1.6 var(--sans)}
.card{width:100%;max-width:520px;text-align:center;background:var(--card);border:1px solid var(--bd);border-radius:28px;padding:32px 22px 24px}
.logo{display:inline-grid;place-items:center;width:56px;height:56px;border-radius:16px;border:1px solid var(--bd);background:linear-gradient(160deg,rgba(242,177,58,.14),transparent)}
.logo svg{width:28px;height:28px;fill:none;stroke:var(--acc);stroke-width:2;stroke-linecap:round}
.eyebrow{margin:18px 0 0;font:600 12px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--tx2);display:flex;gap:8px;justify-content:center;align-items:center}
.eyebrow i{width:8px;height:8px;border-radius:50%;background:var(--acc)}
.curve{display:block;width:100%;max-width:360px;height:auto;margin:14px auto 6px}
.curve .g{stroke:var(--bd);stroke-width:1;fill:none}
.curve .l{fill:none;stroke:var(--acc);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:700;stroke-dashoffset:700;animation:dr 1.3s .1s ease forwards}
.curve text{font:500 10px var(--mono);fill:var(--mut);letter-spacing:.08em}
@keyframes dr{to{stroke-dashoffset:0}}
@media(prefers-reduced-motion:reduce){.curve .l{animation:none;stroke-dashoffset:0}}
h1{margin:6px 0 8px;font:800 clamp(26px,7vw,34px)/1.15 var(--sans);letter-spacing:-.02em}
.sub{margin:0 auto;max-width:42ch;color:var(--tx2);font-size:15px}
.req{margin:18px 0 0;padding:10px 12px;border-radius:12px;background:rgba(128,128,128,.1);text-align:left;font:400 12.5px/1.5 var(--mono);overflow-wrap:anywhere}
.req span{display:block;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}
.dym{margin:14px 0 0;font-size:14px;color:var(--tx2)}.dym a{color:var(--acc);font-weight:600}
.act{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:22px 0 0}
.btn{min-height:48px;padding:0 20px;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font:600 15px var(--sans);text-decoration:none;cursor:pointer;border:1px solid var(--bd);background:none;color:var(--tx)}
.btn.pri{background:var(--acc);border-color:var(--acc);color:#111}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:18px 0 0}
.chips a{font:500 12px var(--mono);color:var(--tx2);text-decoration:none;border:1px solid var(--bd);border-radius:999px;padding:7px 13px}
.chips a:hover,.btn:hover{border-color:var(--acc)}
a:focus-visible,button:focus-visible{outline:2px solid var(--acc);outline-offset:3px}
.foot{margin:22px 0 0;font:400 11.5px var(--mono);color:var(--mut)}.foot a{color:var(--tx2)}
</style>
</head>
<body>
<main class="card">
 <a class="logo" id="logo" href="/HyperAudio/" aria-label="HyperAudio home"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8c2.2 0 2.2-2.5 4.5-2.5S9.8 8 12 8s2.2-2.5 4.5-2.5S18.8 8 21 8M3 13c2.2 0 2.2-2.5 4.5-2.5S9.8 13 12 13s2.2-2.5 4.5-2.5S18.8 13 21 13M3 18c2.2 0 2.2-2.5 4.5-2.5S9.8 18 12 18s2.2-2.5 4.5-2.5S18.8 18 21 18"/></svg></a>
 <p class="eyebrow"><i></i><span id="eb">Error 404</span></p>
 <svg class="curve" viewBox="0 0 320 90" role="img" aria-label="A frequency response curve with a deep dropout"><path class="g" d="M0 45H320M0 15H320M0 75H320"/><path class="l" d="M0 46C30 46 42 36 72 38S122 52 152 46S188 44 194 48L200 84L206 48S250 40 280 42S310 46 320 46"/><text x="212" y="82">NO SIGNAL</text></svg>
 <h1 id="t">This path has no signal.</h1>
 <p class="sub" id="d">That page isn’t part of HyperAudio. The link may be old or mistyped, or the page may have moved.</p>
 <p class="req"><span>Requested</span><code id="path"></code></p>
 <p class="dym" id="dym" hidden>Did you mean <a id="dymA" href="#"></a>?</p>
 <div class="act"><a class="btn pri" id="home" href="/HyperAudio/">Back to HyperAudio</a><button class="btn" id="back" type="button">Go back</button></div>
 <nav class="chips" id="chips" aria-label="Pages"></nav>
 <p class="foot">Broken link? <a id="rep" href="https://github.com/nmstudioo/HyperAudio/issues/new">Report it</a></p>
</main>
<script>
(function(){
var H=/\.github\.io$/.test(location.hostname)?'/HyperAudio/':'/';
var $=function(i){return document.getElementById(i)};
$('home').href=H;$('logo').href=H;$('path').textContent=location.pathname;
var R=[['Setup',''],['Compare','compare.html'],['Finder','finder.html'],['Files','#files'],['Evidence','#evidence'],['Docs','docs/'],['Archive','archive.html'],['Changelog','changelog.html']];
var nav=$('chips');R.forEach(function(r){var a=document.createElement('a');a.href=H+r[1];a.textContent=r[0];nav.appendChild(a)});
$('back').onclick=function(){history.length>1?history.back():location.assign(H)};
$('rep').href='https://github.com/nmstudioo/HyperAudio/issues/new?title='+encodeURIComponent('Broken link: '+location.pathname)+'&body='+encodeURIComponent('URL: '+location.href+'\nReferrer: '+(document.referrer||'none'));
function lev(a,b){var d=[],i,j;for(i=0;i<=a.length;i++)d[i]=[i];for(j=1;j<=b.length;j++)d[0][j]=j;for(i=1;i<=a.length;i++)for(j=1;j<=b.length;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));return d[a.length][b.length]}
var seg='';try{seg=decodeURIComponent(location.pathname.split('/').filter(Boolean).pop()||'').toLowerCase().replace(/\.[a-z0-9]+$/,'')}catch(e){}
var best=null,bd=4;if(seg&&seg!=='hyperaudio')[['Compare','compare.html','compare'],['Finder','finder.html','finder'],['Archive','archive.html','archive'],['Changelog','changelog.html','changelog'],['Docs','docs/','docs'],['Evidence','docs/EVIDENCE.html','evidence'],['Open issues','docs/OPEN.html','open'],['Known limits','docs/LIMITS.html','limits']].forEach(function(r){var d=lev(seg,r[2]);if(d<bd){bd=d;best=r}});
if(best){var a=$('dymA');a.href=H+best[1];a.textContent=best[0];$('dym').hidden=false}
})();
</script>
</body>
</html>
HA_EOF
cat > build/docs_site.py <<'HA_EOF'
#!/usr/bin/env python3
"""Render docs/*.md to site/docs/*.html so doc links exist on the published site."""
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
HA_EOF
cat > tests/links.js <<'HA_EOF'
#!/usr/bin/env node
const fs = require('fs'), path = require('path');
const SITE = path.join(__dirname, '..', 'site'), errs = [];
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? (e.name === 'downloads' ? [] : walk(path.join(d, e.name))) : [path.join(d, e.name)]);
for (const f of walk(SITE).filter(f => f.endsWith('.html'))) {
  const rel = path.relative(SITE, f), html = fs.readFileSync(f, 'utf8');
  if (rel === '404.html') continue;
  for (const m of html.matchAll(/\b(?:href|src)\s*=\s*["']([^"']+)["']/g)) {
    const u = m[1];
    if (/^(https?:|mailto:|tel:|data:|javascript:|#)/.test(u)) continue;
    if (u.startsWith('/')) { errs.push(`${rel}: root-absolute "${u}"`); continue; }
    const p = path.join(path.dirname(f), decodeURIComponent(u.split(/[?#]/)[0]));
    const rp = path.resolve(p); if (rp !== SITE && !rp.startsWith(SITE + path.sep)) { errs.push(`${rel}: "${u}" points outside site/ (not published)`); continue; }
    if (!(fs.existsSync(p) && (!fs.statSync(p).isDirectory() || fs.existsSync(path.join(p, 'index.html'))))) errs.push(`${rel}: missing target "${u}"`);
  }
}
if (!fs.existsSync(path.join(SITE, '404.html'))) errs.push('site/404.html missing');
console.log(errs.length ? errs.map(e => 'FAIL ' + e).join('\n') : 'links ok');
process.exit(errs.length ? 1 : 0);
HA_EOF
cat > tools/apply_v6_ui.py <<'HA_EOF'
#!/usr/bin/env python3
import re, subprocess, sys, os
IDX, CSS = 'site/index.html', 'site/assets/css/site.css'
BEGIN, END = '<!-- v6-evidence:start -->', '<!-- v6-evidence:end -->'
BLOCK = BEGIN + '''
            <div class="v6ev" id="v6-evidence">
              <h3>v6 backend evidence</h3>
              <p>The v6 acceptance suite and EEL2 runtime tests are included in the repository.</p>
              <ul>
                <li><a href="docs/EVIDENCE.html">Method &amp; evidence</a></li>
                <li><a href="docs/OPEN.html">Open issues</a></li>
                <li><a href="docs/LIMITS.html">Known limits</a></li>
                <li><a href="docs/REPRODUCING.html">Reproduce the build</a></li>
                <li><a href="docs/evidence/acceptance-src-v5.0.0.json">Acceptance test data (JSON)</a></li>
              </ul>
            </div>
            ''' + END
CSS_ADD = '''
/* v6-evidence */
.v6ev{margin-top:20px;padding:16px 18px;border:1px solid var(--bd);border-radius:16px}
.v6ev h3{margin:0 0 6px;font:700 17px var(--sans)}.v6ev p{margin:0 0 10px;color:var(--tx2);font-size:14px}
.v6ev ul{margin:0;padding-left:18px;display:grid;gap:6px}.v6ev a{color:var(--acc);font-weight:600}
'''
s = open(IDX, encoding='utf-8').read()
s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', s, flags=re.S)
def enclosing(s, pos):
    for m in reversed([m for m in re.finditer(r'<(section|div|article|aside)\b[^>]*>', s[:pos])]):
        tag, depth = m[1], 0
        for t in re.finditer(r'<(/?)%s\b[^>]*>' % tag, s[m.start():]):
            depth += -1 if t[1] else 1
            if depth == 0:
                end = m.start() + t.end(); break
        else: continue
        if end > pos and 'docs/' in s[m.start():end] and 'id="evidence"' not in s[m.start():end] and len(s[m.start():end]) < 6000:
            return m.start(), end
    return None
h = re.search(r'backend\s+evidence', s, re.I)
if h:
    r = enclosing(s, h.start())
    if not r: sys.exit('Found "Backend Evidence" but could not isolate its container; delete that block by hand, then rerun.')
    s = s[:r[0]] + s[r[1]:]; print('removed misplaced block (%d chars)' % (r[1] - r[0]))
m = re.search(r'<section\b[^>]*id="evidence"', s)
if not m: sys.exit('#evidence section not found in ' + IDX)
close = s.index('</section>', m.end())
s = s[:close] + '  ' + BLOCK + '\n          ' + s[close:]
open(IDX, 'w', encoding='utf-8').write(s)
c = open(CSS, encoding='utf-8').read()
if '/* v6-evidence */' not in c: open(CSS, 'a', encoding='utf-8').write(CSS_ADD)
if os.path.exists('build/docs_site.py'): subprocess.run([sys.executable, 'build/docs_site.py'], check=True)
print('ok: evidence block is inside #evidence')
HA_EOF
python3 - <<'HA_EOF'
p='tests/check.py';s=open(p).read()
add="""# 3b docs pages up to date, links resolve, 404 exists
r = subprocess.run([sys.executable, f'{ROOT}/build/docs_site.py', '--check'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
r = subprocess.run(['node', f'{ROOT}/tests/links.js'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
"""
if 'docs_site.py' not in s: open(p,'w').write(s.replace('# 4 JS syntax',add+'# 4 JS syntax'))
HA_EOF
python3 tools/apply_v6_ui.py
python3 tests/check.py
