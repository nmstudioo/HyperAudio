"""Minimal EEL2 (JSFX) subset -> Python transpiler, enough to run the HyperAudio .eel files.
NOT the WDL runtime. Supported: @init/@sample, slider header lines, = += -= *= /=, ?: (statement and expression),
loop(n,body), while(cond)(body), mem[expr], + - * / % ! && || comparisons, max min abs floor exp pow sqrt sin cos log10, $PI.
Unsupported syntax raises EelError, so a script that leaves the subset fails loudly instead of being mis-run.
Assumptions to confirm on a real runtime: while(cond)(body) loops while cond is nonzero; truth = |x|>1e-5;
% is int modulo (fine for the non-negative indices used); / by zero raises (EEL2 would not) so it is flagged."""
import math, re

class EelError(Exception): pass

TOK = re.compile(r'\s*(?:(\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+)|(\$PI|[A-Za-z_][A-Za-z_0-9.]*)|(\|\||&&|==|!=|<=|>=|[-+*/%]=|[-+*/%<>=!?:;,()\[\]]))')
FUN = {'max': 'max', 'min': 'min', 'abs': 'abs', 'floor': '_floor', 'exp': '_exp', 'pow': '_pow', 'sqrt': '_sqrt',
       'sin': '_sin', 'cos': '_cos', 'log10': '_log10'}

def tokenize(s):
    s = re.sub(r'//[^\n]*', '', s); out = []; i = 0
    while i < len(s):
        if s[i:].strip() == '': break
        m = TOK.match(s, i)
        if not m: raise EelError('bad token near ' + repr(s[i:i+25]))
        i = m.end(); out.append(('num', float(m[1])) if m[1] else ('id', m[2]) if m[2] else ('op', m[3]))
    return out

class P:
    def __init__(s, t): s.t = t; s.i = 0
    def pk(s): return s.t[s.i] if s.i < len(s.t) else ('eof', '')
    def nx(s): x = s.pk(); s.i += 1; return x
    def eat(s, v):
        if s.pk()[1] != v or s.pk()[0] != 'op': raise EelError(f'expected {v!r} got {s.pk()}')
        s.i += 1
    def stmts(s):
        out = []
        while s.pk() not in (('op', ')'), ('eof', '')):
            if s.pk() == ('op', ';'): s.i += 1; continue
            out.append(s.expr())
            if s.pk() == ('op', ';'): s.i += 1
            elif s.pk() not in (('op', ')'), ('eof', '')): raise EelError('expected ; near ' + str(s.t[s.i:s.i+4]))
        return out
    def expr(s):
        a = s.tern()
        k, v = s.pk()
        if k == 'op' and v in ('=', '+=', '-=', '*=', '/=', '%='):
            if a[0] not in ('var', 'mem'): raise EelError('bad assignment target')
            s.i += 1; return ('asg', v, a, s.expr())
        return a
    def tern(s):
        c = s.bin(0)
        if s.pk() == ('op', '?'):
            s.i += 1; a = s.expr(); b = ('num', 0.0)
            if s.pk() == ('op', ':'): s.i += 1; b = s.expr()
            return ('tern', c, a, b)
        return c
    LV = [('||',), ('&&',), ('==', '!='), ('<', '>', '<=', '>='), ('+', '-'), ('*', '/', '%')]
    def bin(s, lv):
        if lv == len(s.LV): return s.un()
        a = s.bin(lv + 1)
        while s.pk()[0] == 'op' and s.pk()[1] in s.LV[lv]:
            op = s.nx()[1]; a = ('bin', op, a, s.bin(lv + 1))
        return a
    def un(s):
        if s.pk() in (('op', '-'), ('op', '+'), ('op', '!')):
            op = s.nx()[1]; return ('un', op, s.un())
        return s.atom()
    def atom(s):
        k, v = s.nx()
        if k == 'num': return ('num', v)
        if k == 'op' and v == '(':
            b = s.stmts(); s.eat(')'); return ('blk', b)
        if k == 'id':
            if v == '$PI': return ('num', math.pi)
            if s.pk() == ('op', '(') and v == 'loop':
                s.i += 1; n_ = s.expr(); s.eat(','); b = s.stmts(); s.eat(')'); return ('call', 'loop', [n_, ('blk', b)])
            if s.pk() == ('op', '('):
                s.i += 1; args = []
                if s.pk() != ('op', ')'):
                    while True:
                        args.append(s.expr())
                        if s.pk() == ('op', ','): s.i += 1; continue
                        break
                s.eat(')')
                if v == 'while' and len(args) == 1 and s.pk() == ('op', '('):
                    s.i += 1; b = s.stmts(); s.eat(')'); return ('while', args[0], ('blk', b))
                return ('call', v, args)
            if s.pk() == ('op', '['):
                s.i += 1; e = s.expr(); s.eat(']'); return ('mem', v, e)
            return ('var', v)
        raise EelError(f'unexpected token {k} {v!r}')

class Gen:
    def __init__(s): s.vars = set(); s.L = []
    def V(s, n): s.vars.add(n); return 'v_' + n.replace('.', '_')
    def cond(s, n):
        if n[0] == 'bin' and n[1] in ('==', '!=', '<', '>', '<=', '>='): return f'({s.val(n[2])} {n[1]} {s.val(n[3])})'
        if n[0] == 'bin' and n[1] == '&&': return f'({s.cond(n[2])} and {s.cond(n[3])})'
        if n[0] == 'bin' and n[1] == '||': return f'({s.cond(n[2])} or {s.cond(n[3])})'
        if n[0] == 'un' and n[1] == '!': return f'(not {s.cond(n[2])})'
        return f'(abs({s.val(n)}) > 1e-5)'
    def val(s, n):
        k = n[0]
        if k == 'num': return repr(n[1])
        if k == 'var': return s.V(n[1])
        if k == 'mem': return f'_M[_ix({s.V(n[1])} + {s.val(n[2])})]'
        if k == 'un': return f'(-{s.val(n[2])})' if n[1] == '-' else s.val(n[2]) if n[1] == '+' else f'(0.0 if {s.cond(n)} is False else 1.0)'
        if k == 'bin':
            if n[1] in ('&&', '||') or n[1] in ('==', '!=', '<', '>', '<=', '>='): return f'(1.0 if {s.cond(n)} else 0.0)'
            if n[1] == '%': return f'(float(int({s.val(n[2])}) % int({s.val(n[3])})))'
            return f'({s.val(n[2])} {n[1]} {s.val(n[3])})'
        if k == 'tern': return f'({s.val(n[2])} if {s.cond(n[1])} else {s.val(n[3])})'
        if k == 'call':
            if n[1] not in FUN: raise EelError('unsupported function ' + n[1])
            return f'{FUN[n[1]]}({", ".join(s.val(a) for a in n[2])})'
        if k == 'blk' and len(n[1]) == 1: return s.val(n[1][0])
        raise EelError('unsupported in expression: ' + k)
    def tgt(s, n): return s.V(n[1]) if n[0] == 'var' else f'_M[_ix({s.V(n[1])} + {s.val(n[2])})]'
    def stmt(s, n, d):
        p = '    ' * d; k = n[0]
        if k == 'asg':
            t = s.tgt(n[2]); r = s.val(n[3])
            s.L.append(f'{p}{t} = {r}' if n[1] == '=' else f'{p}{t} = {t} {n[1][0]} ({r})')
        elif k == 'tern':
            s.L.append(f'{p}if {s.cond(n[1])}:'); s.body(n[2], d + 1)
            if n[3] != ('num', 0.0): s.L.append(f'{p}else:'); s.body(n[3], d + 1)
        elif k == 'call' and n[1] == 'loop':
            if len(n[2]) != 2: raise EelError('loop(n, body)')
            s.L.append(f'{p}for _ in range(int({s.val(n[2][0])})):'); s.body(n[2][1], d + 1)
        elif k == 'while':
            s.L.append(f'{p}_g = 0'); s.L.append(f'{p}while {s.cond(n[1])}:'); s.L.append(f'{p}    _g += 1')
            s.L.append(f'{p}    if _g > 1000000: raise RuntimeError("while guard")'); s.body(n[2], d + 1)
        elif k == 'blk': s.body(n, d)
        elif k in ('num', 'var', 'bin', 'call', 'mem', 'un'): s.L.append(f'{p}{s.val(n)}')
        else: raise EelError('unsupported statement ' + k)
    def body(s, n, d):
        n0 = len(s.L)
        for x in (n[1] if n[0] == 'blk' else [n]): s.stmt(x, d)
        if len(s.L) == n0: s.L.append('    ' * d + 'pass')

def _ix(i):
    i = int(i)
    if i < 0 or i >= _MEM: raise IndexError(f'EEL mem index {i} out of range')
    return i
_MEM = 400000
def _floor(x): return float(math.floor(x))
def _exp(x): return math.exp(x)
def _pow(a, b): return math.pow(a, b)
def _sqrt(x): return math.sqrt(x) if x > 0 else 0.0
def _sin(x): return math.sin(x)
def _cos(x): return math.cos(x)
def _log10(x): return math.log10(x)

def sections(src):
    parts = re.split(r'^@(\w+)[^\n]*$', src, flags=re.M)
    return parts[0], {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}

class Eel:
    """eel = Eel(source_text, srate); eel.init(); out = eel.run(xl, xr) -> (yl, yr) lists. eel.set(name=value) after init."""
    def __init__(self, src, srate=48000.0, edit=None):
        if edit: src = edit(src)
        head, sec = sections(src)
        if 'init' not in sec: raise EelError('missing @init')
        if 'sample' not in sec: raise EelError('missing @sample')
        self.sliders = {}
        for ln in head.split('\n'):
            m = re.match(r'\s*(?:slider\d+:)?([A-Za-z_]\w*)\s*[:=]\s*(-?[\d.]+)\s*<', ln)
            if m: self.sliders[m[1]] = float(m[2])
        g = Gen(); self.code = {}
        for name in ('init', 'sample'):
            ast = P(tokenize(sec[name])).stmts(); g.L = []
            for n in ast: g.stmt(n, 1)
            self.code[name] = g.L
        for extra in sec:
            if extra not in ('init', 'sample'): raise EelError('unsupported section @' + extra)
        g.V('srate'); g.V('spl0'); g.V('spl1')
        names = sorted(g.vars)
        pv = ['v_' + n.replace('.', '_') for n in names]; gl = 'global ' + ', '.join(pv + ['_g']) if pv else ''
        py = [f'def _init():', f'    {gl}'] + self.code['init'] + ['    pass',
              'def _run(xl, xr, yl, yr):', f'    {gl}', '    for _i in range(len(xl)):', '        v_spl0 = xl[_i]; v_spl1 = xr[_i]']
        py += ['    ' + ln for ln in self.code['sample']] + ['        yl.append(v_spl0); yr.append(v_spl1)']
        self.ns = dict(math=math, _ix=_ix, _M=[0.0] * _MEM, _floor=_floor, _exp=_exp, _pow=_pow, _sqrt=_sqrt, _sin=_sin,
                       _cos=_cos, _log10=_log10, _g=0)
        for p_ in pv: self.ns[p_] = 0.0
        self.src = '\n'.join(py)
        exec(compile(self.src, '<eel>', 'exec'), self.ns)
        self.ns['v_srate'] = float(srate)
        for k, v in self.sliders.items(): self.ns['v_' + k] = v
    def init(self): self.ns['_init']()
    def set(self, **kw):
        for k, v in kw.items():
            if 'v_' + k not in self.ns: raise EelError('unknown variable ' + k)
            self.ns['v_' + k] = float(v)
    def get(self, k): return self.ns['v_' + k]
    def run(self, xl, xr):
        yl, yr = [], []; self.ns['_run'](list(map(float, xl)), list(map(float, xr)), yl, yr); return yl, yr
