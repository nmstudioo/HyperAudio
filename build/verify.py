"""Offline checks shared by build and CI. Stdlib only."""
import hashlib, json, os, re, struct, math

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def vdc_info(path):
    banks = {}
    for ln in open(path, encoding='ascii').read().split('\n'):
        m = re.match(r'SR_(\d+):(.*)$', ln.strip())
        if m: banks[int(m[1])] = [float(x) for x in m[2].split(',') if x]
    return banks

def irs_info(path):
    b = open(path, 'rb').read()
    if b[:4] != b'RIFF' or b[8:12] != b'WAVE': raise ValueError('not RIFF/WAVE')
    fmt, ch, sr = struct.unpack('<HHI', b[20:28])
    i = b.find(b'data'); n = struct.unpack('<I', b[i+4:i+8])[0]
    x = struct.unpack('<%df' % (n // 4), b[i+8:i+8+n])
    return dict(format=fmt, channels=ch, sr=sr, frames=len(x)//ch,
                peak=max(abs(v) for v in x), finite=all(math.isfinite(v) for v in x))

def eel_lint(path):
    s = open(path, encoding='utf-8').read(); err = []
    if not s.startswith('desc:'): err.append('missing desc:')
    for sec in ('@init', '@sample'):
        if sec not in s: err.append('missing ' + sec)
    code = re.sub(r'//[^\n]*', '', s)
    for a, b in ('()', '[]', '{}'):
        if code.count(a) != code.count(b): err.append('unbalanced ' + a + b)
    return err

def acceptance(pdir, p, runtime=True):
    """Per-build checks computable offline. Checks needing an EEL runtime are reported not_run, never faked."""
    out = []
    def add(n, ok, d=''): out.append(dict(check=n, status='pass' if ok else 'fail', detail=d))
    for f in p['file_order']:
        path = os.path.join(pdir, f); k = f.rsplit('.', 1)[1]
        if k == 'vdc':
            v = vdc_info(path)
            add('vdc.banks', {44100, 48000} <= set(v), 'banks ' + str(sorted(v)))
            add('vdc.sections', all(len(c) % 5 == 0 and c for c in v.values()) and len({len(c) for c in v.values()}) == 1,
                'sections %s' % {r: len(c)//5 for r, c in v.items()})
            add('vdc.finite', all(math.isfinite(x) for c in v.values() for x in c))
        elif k == 'irs':
            i = irs_info(path)
            add('irs.valid', i['format'] == 3 and i['finite'], 'float WAV %d ch %d Hz %d frames' % (i['channels'], i['sr'], i['frames']))
            add('irs.peak_matches_meta', abs(i['peak'] - p['stats']['irsPeak']) < 0.006, 'file %.3f meta %.2f' % (i['peak'], p['stats']['irsPeak']))
        elif k == 'eel':
            e = eel_lint(path); add('eel.lint', not e, '; '.join(e))
    import sys; root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        import numpy; sys.path.insert(0, os.path.dirname(__file__)); import response
        meta = json.load(open(f'{root}/src/profiles.meta.json')); out += response.checks(pdir, p, numpy.array(meta['freq']))
        if runtime:
            sys.path.insert(0, f'{root}/tests/eel'); import limiter_tests
            out += limiter_tests.build_checks(os.path.join(pdir, [f for f in p['file_order'] if f.endswith('.eel')][0]), p['id'], gate='stable-v5')
        else:
            for n in ('eel.compile', 'limiter.ceiling', 'limiter.true_peak', 'tail', 'nan_soak'): out.append(dict(check=n, status='not_run', detail='skipped (--no-runtime)'))
    except ImportError as ex:
        for n in ('response.correction_match', 'eel.compile', 'limiter.ceiling', 'limiter.true_peak', 'tail', 'nan_soak'): out.append(dict(check=n, status='not_run', detail='needs numpy/scipy: ' + str(ex)))
    out.append(dict(check='cpu', status='not_run', detail='needs on-device measurement; interpreter timing is not representative'))
    return out
