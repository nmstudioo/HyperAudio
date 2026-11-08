#!/usr/bin/env python3
"""Whitespace/comment formatter for CSS, JS and HTML. Every file is verified; a file that fails verification is left untouched.
python3 tools/fmt.py [--check] [--dry] [paths...]"""
import html.parser, os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 130
SEC = re.compile(r'^[=\-\u2014#*~_]{2,}\s*(\S.*?)\s*[=\-\u2014#*~_]{2,}$', re.S)
KEEP = ('!', '@license', '@preserve', 'eslint', 'istanbul', 'sourceMappingURL', '@ts-', 'prettier-ignore', '[if ', '<![endif')

def section(body):
    m = SEC.match(body.strip())
    return m[1].strip() if m and len(m[1]) <= 60 and '\n' not in m[1] else None
def keep(body): return body.lstrip().startswith('!') or any(k in body for k in KEEP[1:])
def sec_css(n): return '/* == %s == */' % n

# ---------------- JS ----------------
KW = {'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'do', 'else', 'yield', 'await'}
def skip_str(s, i):
    q, j, n = s[i], i + 1, len(s)
    while j < n:
        if s[j] == '\\': j += 2; continue
        if s[j] == q: return j + 1
        if s[j] == '\n': return j
        j += 1
    return n
def skip_tpl(s, i):
    j, n = i + 1, len(s)
    while j < n:
        c = s[j]
        if c == '\\': j += 2
        elif c == '`': return j + 1
        elif c == '$' and s[j+1:j+2] == '{': j = skip_braces(s, j + 2)
        else: j += 1
    return n
def skip_braces(s, j):
    d, n = 1, len(s)
    while j < n:
        c = s[j]
        if c in '"\'': j = skip_str(s, j); continue
        if c == '`': j = skip_tpl(s, j); continue
        if s.startswith('//', j): k = s.find('\n', j); j = n if k < 0 else k; continue
        if s.startswith('/*', j): k = s.find('*/', j + 2); j = n if k < 0 else k + 2; continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return j + 1
        j += 1
    return n
def js_fmt(s):
    s = s.replace('\r\n', '\n').replace('\r', '\n'); n, i = len(s), 0
    lines, cur, last = [], [], ''
    def has(): return any(x.strip() for x in cur)
    def nl():
        nonlocal cur
        if has(): lines.append(''.join(cur).rstrip(' \t'))
        cur = []
    def sec(name):
        if lines and lines[-1] != '': lines.append('')
        lines.append(sec_css(name))
    if s.startswith('#!'):
        k = s.find('\n'); k = n if k < 0 else k; lines.append(s[:k]); i = k
    while i < n:
        c = s[i]
        if c == '\n': nl(); i += 1; continue
        if c in ' \t':
            if has(): cur.append(c)
            i += 1; continue
        if s.startswith('//', i) or s.startswith('/*', i):
            blk = s[i+1] == '*'
            if blk: k = s.find('*/', i + 2); k = n if k < 0 else k + 2
            else: k = s.find('\n', i); k = n if k < 0 else k
            raw = s[i:k]; body = raw[2:-2] if blk else raw[2:]; i = k
            if keep(body): cur.append(raw)
            elif not has() and section(body): sec(section(body))
            elif blk and '\n' in raw and has(): nl()
            elif blk and has() and cur and not cur[-1].endswith((' ', '\t')): cur.append(' ')
            continue
        if c in '"\'': k = skip_str(s, i); cur.append(s[i:k]); i = k; last = '"'; continue
        if c == '`': k = skip_tpl(s, i); cur.append(s[i:k]); i = k; last = '"'; continue
        if c == '/' and (last == '' or last in KW or (last not in ('w', '"', ')', ']', '}') and last in tuple('(,=:[!&|?{;+-*%<>~^'))):
            k, incls = i + 1, False
            while k < n:
                ch = s[k]
                if ch == '\\': k += 2; continue
                if ch == '[': incls = True
                elif ch == ']': incls = False
                elif ch == '/' and not incls: k += 1; break
                elif ch == '\n': k = -1; break
                k += 1
            if k > 0:
                while k < n and s[k].isalpha(): k += 1
                cur.append(s[i:k]); i = k; last = '"'; continue
        m = re.compile(r'[A-Za-z_$][\w$]*|\d[\w.]*').match(s, i)
        if m: cur.append(m[0]); last = m[0] if m[0] in KW else 'w'; i = m.end(); continue
        cur.append(c); last = c; i += 1
    nl()
    return '\n'.join(lines) + '\n'

# ---------------- CSS ----------------
STR = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')')
def outside(text, fn): return ''.join(p if k % 2 else fn(p) for k, p in enumerate(STR.split(text)))
def strip_c(t): return re.sub(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|/\*.*?\*/', lambda m: m[1] or ' ', t, flags=re.S)
def ws(t): return outside(t, lambda p: re.sub(r'\s+', ' ', p))
def com(t): return outside(t, lambda p: re.sub(r'\s*,\s*', ',', p))
def css_parse(s):
    n = len(s)
    def block(i):
        items = []
        while True:
            while i < n and s[i] in ' \t\r\n;': i += 1
            if i >= n: return items, i
            if s[i] == '}': return items, i + 1
            if s.startswith('/*', i):
                k = s.find('*/', i + 2); k = n if k < 0 else k + 2; raw = s[i:k]; i = k; body = raw[2:-2]
                if keep(body): items.append(('raw', raw))
                elif section(body): items.append(('sec', section(body)))
                continue
            j, d = i, 0
            while j < n:
                ch = s[j]
                if ch in '"\'': j = skip_str(s, j); continue
                if s.startswith('/*', j): k = s.find('*/', j + 2); j = n if k < 0 else k + 2; continue
                if ch == '(': d += 1
                elif ch == ')': d -= 1
                elif d <= 0 and ch in '{};': break
                j += 1
            text = strip_c(s[i:j]); term = s[j] if j < n else ''
            if term == '{':
                kids, i = block(j + 1); items.append(('rule', com(ws(text)).strip(), kids))
            else:
                items.append(decl(text)); i = j + 1 if term == ';' else j
    return block(0)[0]
def decl(text):
    k = -1
    parts = STR.split(text); pos, d = 0, 0
    for p_i, p in enumerate(parts):
        if p_i % 2: pos += len(p); continue
        for ch in p:
            if ch == '(': d += 1
            elif ch == ')': d -= 1
            elif ch == ':' and d == 0 and k < 0: k = pos
            pos += 1
    if k < 0 or text.lstrip().startswith('@'): return ('stmt', com(ws(text)).strip())
    prop, val = text[:k].strip(), com(ws(text[k+1:])).strip()
    val = re.sub(r'\s*!\s*important$', '!important', val, flags=re.I)
    if val == '' and prop.startswith('--'): val = ' '
    return ('decl', prop + ':' + val)
def pack(ds, end):
    lines, cur = [], ''
    for x in ds:
        piece = x + ';'
        if cur and len(cur) + len(piece) > W: lines.append(cur); cur = piece
        else: cur += piece
    if cur: lines.append(cur)
    if end and lines: lines[-1] = lines[-1][:-1] + '}'
    return lines
def css_rule(it):
    _, pre, kids = it
    flat = all(k[0] in ('decl', 'stmt') for k in kids)
    if flat:
        ds = [k[1] for k in kids]; one = pre + '{' + ';'.join(ds) + '}'
        return [one] if len(one) <= W else [pre + '{'] + pack(ds, True)
    out, run = [pre + '{'], []
    for k in kids + [('end',)]:
        if k[0] in ('decl', 'stmt'): run.append(k[1]); continue
        out += pack(run, False); run = []
        if k[0] == 'rule': out += css_rule(k)
        elif k[0] == 'sec': out.append(sec_css(k[1]))
        elif k[0] == 'raw': out.append(k[1])
    return out + ['}']
def css_fmt(s):
    items, out, prev = css_parse(s), [], None
    for it in items:
        if it[0] == 'sec' or it[0] == 'raw': block = [sec_css(it[1]) if it[0] == 'sec' else it[1]]
        elif it[0] == 'rule': block = css_rule(it)
        else: block = [it[1] + ';']
        if prev is not None and prev != 'sec': out.append('')
        elif prev == 'sec' and False: pass
        out += block; prev = 'sec' if it[0] == 'sec' else it[0]
    return '\n'.join(out) + '\n' if out else ''
def css_ok(a, b):
    def sq(t): return re.sub(r';(?=\})', '', outside(strip_c(t), lambda p: re.sub(r'\s+', '', p)))
    def ast(t):
        def f(items): return [(k[0], k[1], f(k[2])) if k[0] == 'rule' else k for k in items if k[0] in ('rule', 'decl', 'stmt')]
        return f(css_parse(t))
    return sq(a) == sq(b) and ast(a) == ast(b)

# ---------------- JS verify ----------------
def js_ok(a, b):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.js', 'w', encoding='utf-8').write(a); open(d + '/b.js', 'w', encoding='utf-8').write(b)
        try: r = subprocess.run(['node', '--expose-internals', ROOT + '/tools/jsverify.js', d + '/a.js', d + '/b.js'], capture_output=True, text=True, timeout=60)
        except Exception: return False
        return r.returncode == 0

# ---------------- HTML ----------------
RAW = ('pre', 'textarea')
def tag_end(s, i):
    q, n = None, len(s); j = i + 1
    while j < n:
        c = s[j]
        if q: q = None if c == q else q
        elif c in '"\'': q = c
        elif c == '>': return j + 1
        j += 1
    return n
def tag_fmt(t):
    out, q, pend = [], None, False
    for c in t:
        if q:
            out.append(c)
            if c == q: q = None
        elif c in ' \t\r\n': pend = True
        else:
            if pend and out and out[-1] != '<':
                if c == '>' or (c == '/' and False): pass
                elif c == '/' and out and out[-1] in '"\'': pass
                else: out.append(' ')
            pend = False; out.append(c)
            if c in '"\'': q = c
    r = ''.join(out)
    return r
def html_fmt(s, stats):
    s = s.replace('\r\n', '\n'); n, i, out = len(s), 0, []
    def text(t):
        t = re.sub(r'[ \t]*\n[ \t\n]*', '\n', t); return re.sub(r'\n[ \t]+', '\n', t)
    while i < n:
        if s.startswith('<!--', i):
            k = s.find('-->', i + 4); k = n if k < 0 else k + 3; raw = s[i:k]; body = raw[4:-3]
            if keep(body): out.append(raw)
            elif section(body): out.append('\n<!-- == %s == -->\n' % section(body))
            i = k; continue
        if s[i] == '<' and re.match(r'</?[A-Za-z!]', s[i:i+3]):
            k = tag_end(s, i); raw = s[i:k]; name = re.match(r'</?([A-Za-z0-9!-]*)', raw)[1].lower()
            out.append(raw if raw.startswith('<!') else tag_fmt(raw)); i = k
            if raw[1] != '/' and name in RAW + ('script', 'style'):
                m = re.compile(r'</%s\s*>' % name, re.I).search(s, i); e = m.start() if m else n; body = s[i:e]
                if name in RAW or not body.strip(): out.append(body)
                else:
                    ty = re.search(r'type\s*=\s*["\']?([^"\'\s>]+)', raw, re.I)
                    if name == 'script' and ty and ty[1].lower() not in ('text/javascript', 'module', 'application/javascript'): out.append(body)
                    else:
                        f = (js_fmt if name == 'script' else css_fmt)(body); ok = js_ok(body, f) if name == 'script' else css_ok(body, f)
                        if ok and not (name == 'script' and ty and ty[1].lower() == 'module'): out.append('\n' + f)
                        else: out.append(body); stats.append('inline %s kept' % name)
                i = e
            continue
        k = s.find('<', i + 1); k = n if k < 0 else k; out.append(text(s[i:k])); i = k
    r = ''.join(out); r = re.sub(r'[ \t]+\n', '\n', r); return re.sub(r'\n{2,}', '\n', r).lstrip('\n')
class Canon(html.parser.HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=False); s.ev, s.pre, s.raw = [], 0, 0
    def data(s, d):
        if s.raw: return
        d = d if s.pre else re.sub(r'\s+', ' ', d)
        if s.ev and s.ev[-1][0] == 'd': s.ev[-1] = ('d', s.ev[-1][1] + d)
        else: s.ev.append(('d', d))
    handle_data = data; handle_entityref = lambda s, n: s.data('&%s;' % n); handle_charref = lambda s, n: s.data('&#%s;' % n)
    def handle_starttag(s, t, a):
        s.ev.append(('s', t, tuple(a))); s.pre += t in RAW; s.raw += t in ('script', 'style')
    def handle_startendtag(s, t, a): s.ev.append(('s', t, tuple(a))); s.ev.append(('e', t))
    def handle_endtag(s, t):
        s.ev.append(('e', t)); s.pre -= (t in RAW and s.pre > 0); s.raw -= (t in ('script', 'style') and s.raw > 0)
    def handle_decl(s, d): s.ev.append(('x', d.lower()))
def canon(t):
    c = Canon(); c.feed(t); c.close(); ev = []
    for e in c.ev:
        if e[0] == 'd' and not e[1].strip() and not (ev and ev[-1][0] == 'x'): e = ('d', ' ')
        ev.append(e)
    return ev

def process(path, check, dry):
    ext = path.rsplit('.', 1)[-1]; src = open(path, encoding='utf-8').read(); stats = []
    if ext == 'css': new = css_fmt(src); ok = css_ok(src, new)
    elif ext == 'js': new = js_fmt(src); ok = js_ok(src, new)
    else: new = html_fmt(src, stats); ok = canon(src) == canon(new)
    new = new if new.endswith('\n') else new + '\n'
    if not ok: return 'FAILED', 'verification failed, file untouched'
    if new == src.replace('\r\n', '\n'): return 'same', ''
    if not (check or dry): open(path, 'w', encoding='utf-8', newline='\n').write(new)
    return 'changed', ', '.join(stats)

def collect(args):
    if args: return [os.path.abspath(a) for a in args]
    skip = ('/site/docs/', '/site/downloads/', '/releases/', '/node_modules/', '/.git/', '/candidates/', '/src/')
    out = []
    for d, _, fs in os.walk(ROOT):
        p = d.replace(os.sep, '/') + '/'
        if any(x in p for x in skip): continue
        out += [os.path.join(d, f) for f in fs if f.endswith(('.css', '.js', '.html'))]
    return sorted(out)

if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv: print(__doc__); sys.exit(0)
    bad_flags = [x for x in sys.argv[1:] if x.startswith('-') and x not in ('--check', '--dry')]
    if bad_flags: print('fmt: unknown option %s\n%s' % (' '.join(bad_flags), __doc__)); sys.exit(2)
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; check, dry = '--check' in sys.argv, '--dry' in sys.argv
    res = {'same': 0, 'changed': 0, 'FAILED': 0}; bad = []
    for f in collect(a):
        st, note = process(f, check, dry); res[st] += 1
        rel = os.path.relpath(f, ROOT)
        if st != 'same' or note: print('%-8s %s %s' % (st, rel, note))
        if st == 'FAILED': bad.append(rel)
    print('fmt: %(changed)d changed, %(same)d unchanged, %(FAILED)d failed' % res)
    sys.exit(1 if bad or (check and res['changed']) else 0)
