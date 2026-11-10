import re
def skip(s, i, b):
    c = s[i]
    if c == '/' and s.startswith('/*', i):
        j = s.find('*/', i + 2); return b if j < 0 else j + 2
    if c in '"\'':
        j = i + 1
        while j < b and s[j] != c: j += 2 if s[j] == '\\' else 1
        return j + 1
    return i
def scan(s, a, b):
    items = []; i = a
    while i < b:
        if s[i].isspace(): i += 1; continue
        if s.startswith('/*', i): i = skip(s, i, b); continue
        st = i
        while i < b and s[i] not in '{;':
            n = skip(s, i, b); i = n if n != i else i + 1
        if i >= b: break
        pre = s[st:i]
        if s[i] == ';': items.append((st, i + 1, pre, None)); i += 1; continue
        i += 1; bs = i; d = 1
        while i < b and d:
            n = skip(s, i, b)
            if n != i: i = n; continue
            if s[i] == '{': d += 1
            elif s[i] == '}': d -= 1
            i += 1
        items.append((st, i, pre, (bs, i - 1)))
    return items
def clean(p): return re.sub(r'/\*.*?\*/', '', p, flags=re.S).strip()
AT_NEST = re.compile(r'@(media|supports|layer|container)\b')
def split_sel(p):
    out = []; d = 0; cur = ''
    for ch in p:
        if ch in '([': d += 1
        elif ch in ')]': d -= 1
        if ch == ',' and d == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    out.append(cur.strip()); return [x for x in out if x]
def decls(s, a, b):
    out = []; i = a; st = a; d = 0
    while i < b:
        n = skip(s, i, b)
        if n != i: i = n; continue
        c = s[i]
        if c == '(': d += 1
        elif c == ')': d -= 1
        elif c == ';' and d == 0: out.append((st, i + 1)); st = i + 1
        i += 1
    if s[st:b].strip(): out.append((st, b))
    return out
def balanced(s): return s.count('{') == s.count('}')
