#!/usr/bin/env python3
"""Layout gate (needs: pip install playwright && playwright install chromium).
No horizontal overflow at 320/375/768/1024/1440 in both themes, footer reaches the viewport bottom,
one aria-current per nav, Escape closes the More sheet. Skips (exit 0) if playwright is missing."""
import functools, http.server, os, sys, threading
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('overflow: playwright not installed, skipped'); sys.exit(0)
PAGES = ['index.html', 'compare.html', 'finder.html', 'archive.html', 'changelog.html']
WIDTHS = [320, 375, 768, 1024, 1440]
err = []
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=f'{ROOT}/site')
h.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{srv.server_port}/'
with sync_playwright() as p:
    b = p.chromium.launch()
    for theme in ('dark', 'light'):
        for w in WIDTHS:
            ctx = b.new_context(viewport={'width': w, 'height': 800}, color_scheme=theme)
            ctx.add_init_script(f"try{{localStorage.setItem('ha-theme','{theme}')}}catch(e){{}}")
            for pg in PAGES:
                page = ctx.new_page(); page.goto(base + pg); page.wait_for_timeout(500)
                tag = f'{pg}@{w}/{theme}'
                o = page.evaluate("""()=>{const d=document.documentElement,bad=[];
                  document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);
                    if(r.width&&r.right>innerWidth+1&&s.position!=='fixed'&&!e.closest('.tw,.ftab-w,.snd,.legend,.seg,.code,pre,.chartbox,[class*=scroll],.sheet,.sb'))bad.push(e.className||e.tagName)});
                  return {sw:d.scrollWidth,iw:innerWidth,bad:bad.slice(0,3)}}""")
                if o['sw'] > o['iw']: err.append(f'{tag}: horizontal overflow {o["sw"]}>{o["iw"]} {o["bad"]}')
                f = page.evaluate("()=>{const r=document.querySelector('.sf').getBoundingClientRect();return [r.bottom,document.documentElement.scrollHeight]}")
                if abs(f[0] + page.evaluate('scrollY') - f[1]) > 2 and f[0] < 790 and f[0] != f[1]: err.append(f'{tag}: footer not at page bottom {f}')
                if w >= 768:
                    if not page.is_visible('.sb'): err.append(f'{tag}: sidebar hidden')
                    if page.is_visible('.bb'): err.append(f'{tag}: bottom bar visible on wide screen')
                    n = page.locator('.sb [aria-current]').count()
                else:
                    if not page.is_visible('.bb'): err.append(f'{tag}: bottom bar hidden')
                    n = page.locator('.bb [aria-current]').count()
                if n != 1: err.append(f'{tag}: expected 1 aria-current, found {n}')
                if w < 768 and theme == 'dark':
                    page.click('.bb-more'); page.wait_for_timeout(300)
                    if not page.is_visible('.sheet-p'): err.append(f'{tag}: sheet did not open')
                    page.keyboard.press('Escape'); page.wait_for_timeout(350)
                    if page.is_visible('.sheet-p'): err.append(f'{tag}: Escape did not close sheet')
                    for t in page.locator('.bb a,.bb button').all():
                        bx = t.bounding_box()
                        if bx and (bx['height'] < 44 or bx['width'] < 44): err.append(f'{tag}: bottom-bar target {bx["width"]:.0f}x{bx["height"]:.0f} < 44')
                page.close()
            ctx.close()
    b.close()
print('\n'.join('FAIL ' + e for e in err) or 'overflow: all layout checks passed'); sys.exit(1 if err else 0)
