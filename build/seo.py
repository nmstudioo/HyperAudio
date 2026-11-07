#!/usr/bin/env python3
"""Single source of SEO metadata. Stdlib only.
  python3 build/seo.py          rewrite site/*.html (docs pages get the same block from build/docs_site.py), sitemap.xml, robots.txt
  python3 build/seo.py --check  fail if anything is stale
Writes per page: <title>, description, canonical, robots, Open Graph, Twitter card, JSON-LD (WebSite, SoftwareSourceCode, BreadcrumbList, TechArticle),
plus a short static "About this page" for pages whose body is filled by JavaScript. Optional search-console tokens: build/seo_config.json."""
import html, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://nmstudioo.github.io/HyperAudio/'
NAME = 'HyperAudio'
IMG = BASE + 'assets/brand/og-image.png'
AUTHOR = 'Noushad Mostafa'
REPO = 'https://github.com/nmstudioo/HyperAudio'
# path (relative to site/) -> (title, description, breadcrumb name). Titles <= 60 chars, descriptions 70-160.
P = {
 'index.html': ('HyperAudio · RootlessJamesDSP profiles for KZ EDX Pro', 'Calibrated RootlessJamesDSP profiles for the KZ EDX Pro IEM and Redmi 12 speaker: VDC, impulse response and Liveprog files, with honest evidence labels.', 'Home'),
 'compare.html': ('Compare DSP profiles · HyperAudio', 'Overlay the predicted frequency response of two HyperAudio profiles. Responses are calculated from the shipped VDC and impulse response files, not measured.', 'Compare'),
 'finder.html': ('Profile finder · HyperAudio', 'Answer two questions about your output and get the matching HyperAudio RootlessJamesDSP profile for the KZ EDX Pro or the Redmi 12 speaker.', 'Finder'),
 'archive.html': ('Version archive · HyperAudio', 'HyperAudio release history from v1 to the current 6.0.0: dates, status and checksums where the repository has them, and a clear note where it has no record.', 'Archive'),
 'changelog.html': ('Changelog · HyperAudio', 'What changed in each HyperAudio release: profiles, tooling, tests and site, with dates and the current version.', 'Changelog'),
 'docs/index.html': ('Documentation · HyperAudio', 'How HyperAudio profiles are built, what the evidence shows, known limits, open items and how to reproduce the build.', 'Docs'),
 'docs/METHOD.html': ('Method: how the profiles are built · HyperAudio', 'Chain order in RootlessJamesDSP (VDC, convolver, Liveprog), how each stage is fitted and how the targets and limits are chosen.', 'Method'),
 'docs/EVIDENCE.html': ('Evidence tiers and test matrix · HyperAudio', 'Calculated, reported and measured evidence kept separate: what each HyperAudio profile has passed offline and what remains untested on a device.', 'Evidence'),
 'docs/LIMITS.html': ('Known limits · HyperAudio', 'Known limits of the HyperAudio profiles: speaker boost cap, limiter true-peak overshoot, 44.1 kHz bank deviation and what has not been measured.', 'Limits'),
 'docs/OPEN.html': ('Open items · HyperAudio', 'Open items and blockers for HyperAudio: unverified claims, missing measurements, candidate profiles and what each needs to move forward.', 'Open items'),
 'docs/REPRODUCING.html': ('Reproduce the build · HyperAudio', 'Rebuild every HyperAudio profile from source, verify hashes and run the offline acceptance checks on your own machine.', 'Reproducing'),
 'docs/RELEASING.html': ('Release process · HyperAudio', 'How a HyperAudio release is cut: version stamp, build, freeze, verification and the tag-triggered GitHub release.', 'Releasing'),
 'docs/CHANGELOG.html': ('Changelog (full notes) · HyperAudio', 'Full HyperAudio release notes with technical detail for each version of the profiles and tooling.', 'Changelog notes'),
 'docs/refit44_report.html': ('44.1 kHz VDC refit report · HyperAudio', 'Report on refitting the 44.1 kHz VDC banks so they match the 48 kHz response within 0.3 dB, with offline verification.', '44.1 kHz refit'),
}
ABOUT = {  # static copy for pages filled in by JavaScript (crawlers and no-JS readers get text)
 'compare.html': ('About this comparison', 'The chart overlays the predicted response of two profiles. Each curve is computed from the shipped VDC biquad cascade and the impulse response, so it shows what the files should do, not what a microphone measured. Pick any two of the six profiles for the KZ EDX Pro or the Redmi 12 speaker to see where they differ.'),
 'finder.html': ('About the finder', 'The finder picks a profile from your output device and the sound you prefer. It only chooses between the six shipped HyperAudio profiles. The reasoning behind each pick is shown so you can overrule it.'),
 'archive.html': ('About the archive', 'The archive lists every HyperAudio release with its date and, where the repository has them, checksums. Older versions have little or no record in the repository, and the page says so instead of inventing detail.'),
 'changelog.html': ('About the changelog', 'The changelog records what changed in each HyperAudio release, from repository structure and tests to the profiles themselves. Release 6.0.0 changed tooling, tests, documentation and the site; its profile files are identical to 5.0.0.'),
}
def cfg():
    p = f'{ROOT}/build/seo_config.json'
    return json.load(open(p)) if os.path.exists(p) else {}
def release():
    try: return json.load(open(f'{ROOT}/site/data/versions.json'))[0]
    except Exception: return {'v': '', 'date': ''}
def url(path): return BASE if path == 'index.html' else BASE + ('docs/' if path == 'docs/index.html' else path)
def esc(s): return html.escape(s, quote=True)
def jsonld(path):
    r = release(); u = url(path); t, d, crumb = P[path]; g = []
    if path == 'index.html':
        g.append({'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME, 'url': BASE, 'description': d, 'inLanguage': 'en', 'author': {'@type': 'Person', 'name': AUTHOR}})
        g.append({'@context': 'https://schema.org', '@type': 'SoftwareSourceCode', 'name': NAME + ' profiles', 'description': d, 'codeRepository': REPO, 'url': BASE, 'license': REPO + '/blob/main/LICENSE', 'version': r['v'].lstrip('v'), 'dateModified': r['date'], 'author': {'@type': 'Person', 'name': AUTHOR}})
    else:
        items = [('Home', BASE)] + ([('Docs', BASE + 'docs/')] if path.startswith('docs/') and path != 'docs/index.html' else []) + [(crumb, u)]
        g.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': h} for i, (n, h) in enumerate(items)]})
        if path.startswith('docs/') and path != 'docs/index.html':
            g.append({'@context': 'https://schema.org', '@type': 'TechArticle', 'headline': t.split(' · ')[0], 'description': d, 'url': u, 'inLanguage': 'en', 'dateModified': r['date'], 'author': {'@type': 'Person', 'name': AUTHOR}, 'publisher': {'@type': 'Person', 'name': AUTHOR}, 'image': IMG, 'mainEntityOfPage': u})
    return ''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') for x in g)
def block(path):
    t, d, _ = P[path]; u = url(path); c = cfg(); typ = 'website' if path == 'index.html' else 'article'
    m = ['<meta name="description" content="%s"/>' % esc(d), '<link rel="canonical" href="%s"/>' % u,
         '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"/>', '<meta name="author" content="%s"/>' % AUTHOR,
         '<meta property="og:type" content="%s"/>' % typ, '<meta property="og:site_name" content="%s"/>' % NAME, '<meta property="og:locale" content="en_US"/>',
         '<meta property="og:title" content="%s"/>' % esc(t), '<meta property="og:description" content="%s"/>' % esc(d), '<meta property="og:url" content="%s"/>' % u,
         '<meta property="og:image" content="%s"/>' % IMG, '<meta property="og:image:width" content="1200"/>', '<meta property="og:image:height" content="630"/>',
         '<meta property="og:image:alt" content="HyperAudio: calibrated DSP profiles for RootlessJamesDSP, with a response curve"/>',
         '<meta name="twitter:card" content="summary_large_image"/>', '<meta name="twitter:title" content="%s"/>' % esc(t), '<meta name="twitter:description" content="%s"/>' % esc(d), '<meta name="twitter:image" content="%s"/>' % IMG]
    if c.get('google_verification'): m.append('<meta name="google-site-verification" content="%s"/>' % esc(c['google_verification']))
    if c.get('bing_verification'): m.append('<meta name="msvalidate.01" content="%s"/>' % esc(c['bing_verification']))
    return '<!--seo-->' + '\n'.join(m) + '\n' + jsonld(path) + '<!--/seo-->'
STRIP = [r'<meta\s+name="description"[^>]*>', r'<link\s+rel="canonical"[^>]*>', r'<meta\s+property="og:[^"]*"[^>]*>', r'<meta\s+name="twitter:[^"]*"[^>]*>',
         r'<meta\s+name="robots"[^>]*>', r'<meta\s+name="author"[^>]*>', r'<script type="application/ld\+json">.*?</script>', r'<!--seo-->.*?<!--/seo-->']
def process(path, s):
    """Return html with the managed SEO block, title and (if listed) static About section."""
    if path not in P: return s
    s = re.sub(r'<!--seo-->.*?<!--/seo-->\n?', '', s, flags=re.S)
    for r in STRIP[:-1]: s = re.sub(r'[ \t]*' + r + r'[ \t]*\n?', '', s, flags=re.S)
    t = '<title>%s</title>' % esc(P[path][0])
    s = re.sub(r'<title>.*?</title>', t, s, count=1, flags=re.S) if '<title>' in s else s.replace('</head>', t + '</head>', 1)
    s = s.replace('</head>', block(path) + '\n</head>', 1)
    s = re.sub(r'\n?<section class="pg-about">.*?</section>', '', s, flags=re.S)
    if path in ABOUT:
        h, p = ABOUT[path]
        s = s.replace('</main>', '<section class="pg-about"><h2>%s</h2><p class="note">%s</p></section>\n</main>' % (esc(h), esc(p)), 1)
    return s
def sitemap():
    d = release()['date']
    rows = ''.join('<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (url(p), d, '1.0' if p == 'index.html' else '0.8' if p.count('/') == 0 or p == 'docs/index.html' else '0.6') for p in P)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + '</urlset>\n'
def robots(): return 'User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n' % BASE
def targets():
    out = {}
    for p in P:
        if p.startswith('docs/'): continue  # written by build/docs_site.py via process()
        f = f'{ROOT}/site/{p}'
        if os.path.exists(f): out[f] = process(p, open(f, encoding='utf-8').read())
    out[f'{ROOT}/site/sitemap.xml'] = sitemap(); out[f'{ROOT}/site/robots.txt'] = robots()
    return out
if __name__ == '__main__':
    t = targets()
    if '--check' in sys.argv:
        bad = [os.path.relpath(f, ROOT) for f, v in t.items() if not os.path.exists(f) or open(f, encoding='utf-8').read() != v]
        print('seo stale: ' + ', '.join(bad) if bad else 'seo up to date'); sys.exit(1 if bad else 0)
    for f, v in t.items(): open(f, 'w', encoding='utf-8').write(v)
    print('seo: wrote', len(t), 'files')
