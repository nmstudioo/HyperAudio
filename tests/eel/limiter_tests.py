"""Runtime acceptance for the shared limiter core, run on the real .eel text through tests/eel/eel2py.py.
Needs numpy + scipy. Results are labelled runtime=eel2py: an independent subset interpreter, not the WDL/JSFX runtime."""
import math, os, random, sys
import numpy as np
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(__file__))
from eel2py import Eel

TP_LIMIT_DB = 0.5         # v7 gate: true-peak overshoot on tones, clicks, noise (8x reference, edges trimmed)
TP_NOISE_LIMIT_DB = 0.5   # v7 gate: same as tones (v5 measured +1.9 dB)
THD_LIMIT_DB = -40.0      # residual (non-fundamental) energy of a limited 997 Hz +6 dB tone, relative to total
CLIP_LIMIT = 0.01         # regression guard: fraction of steady-state samples on the hard clamp (v5 measures 0.0068); audibility is judged by the THD limit
TAIL_LIMIT_S = 2.0        # time for output to fall below 1e-6 after a loud burst
VARIANTS = {'spk-v10': [{}, {'mode': 1}]}   # extra settings applied after @init (mode 1 = limiter only)

def signals(fs):
    n = int(1.5 * fs); t = np.arange(n) / fs; S = {}
    for f in (100, 997, 3000, 12000):
        for db in (0, 6, 12): S[f'sine{f}_{db:+d}dB'] = np.sin(2 * np.pi * f * t + 0.7) * 10 ** (db / 20)
    for db in (0, 6): S[f'fs4_45deg_{db:+d}dB'] = np.sin(2 * np.pi * (fs / 4) * t + np.pi / 4) * 10 ** (db / 20) * math.sqrt(2) / 1.0
    r = np.random.default_rng(1); g = np.clip(r.standard_normal(n) * 0.5, -1, 1)
    S['noise_0dB'] = g * 0.5; S['noise_+6dB'] = g * 2.0
    S['square1k_0dB'] = np.sign(np.sin(2 * np.pi * 1000 * t))
    c = np.zeros(n); c[:: int(0.01 * fs)] = 1.0; S['clicks_0dB'] = c
    return S

def tp_db(y, ceil, trim=96):
    u = resample_poly(y, 8, 1)[trim * 8:-trim * 8]   # trim edge ringing caused by truncating the signal (metric artifact, found in v7 work)
    return 20 * math.log10(max(np.abs(u).max(), 1e-12) / ceil)

def make(path, fs, edit=None, setv=None):
    e = Eel(open(path, encoding='utf-8').read(), fs, edit); e.init()
    if setv: e.set(**setv)
    return e

def suite(path, fs=48000, edit=None, setv=None):
    """Returns metrics dict for one build/rate/variant."""
    M = dict(tp_overshoot_db=-99.0, tp_signal='', tp_noise_db=-99.0, sample_over=0.0, clip_frac=0.0, nonfinite=False, ceil=None, per={})
    for name, x in signals(fs).items():
        e = make(path, fs, edit, setv)
        yl, yr = e.run(x, x); y = np.array(yl); skip = int(0.1 * fs); ceil = e.get('ceilLin'); M['ceil'] = ceil   # read AFTER run: first sample applies sliders
        if not np.isfinite(y).all() or not np.isfinite(np.array(yr)).all(): M['nonfinite'] = True; continue
        M['sample_over'] = max(M['sample_over'], float(np.abs(y).max() - ceil))
        M['clip_frac'] = max(M['clip_frac'], float((np.abs(y[skip:]) >= ceil * (1 - 1e-9)).mean()))
        if name.startswith('square'): continue   # hard-edged square: 8x resampling shows Gibbs ringing of the input itself, not the limiter
        d = tp_db(y[skip:], ceil); M['per'][name] = round(d, 2)
        if name.startswith('noise'): M['tp_noise_db'] = max(M['tp_noise_db'], d)
        elif d > M['tp_overshoot_db']: M['tp_overshoot_db'] = d; M['tp_signal'] = name
    return M

def thd_db(path, fs=48000, edit=None, setv=None):
    e = make(path, fs, edit, setv); t = np.arange(fs) / fs; x = 2.0 * np.sin(2 * np.pi * 997 * t)
    yl, _ = e.run(x, x); y = np.array(yl)[fs // 2:]; w = np.hanning(len(y)); X = np.abs(np.fft.rfft(y * w)) ** 2
    k = int(round(997 * len(y) / fs)); fund = X[k - 4:k + 5].sum(); return 10 * math.log10(max(X[1:].sum() - fund, 1e-30) / X[1:].sum())

def transparency_db(path, fs=48000, edit=None, setv=None):
    e = make(path, fs, edit, setv); t = np.arange(fs) / fs; x = 0.03 * np.sin(2 * np.pi * 997 * t)
    yl, _ = e.run(x, x); y = np.array(yl)[fs // 2:]; return 20 * math.log10(np.sqrt((y ** 2).mean()) / np.sqrt((x[fs // 2:] ** 2).mean()))

def tail(path, fs=48000, edit=None, setv=None):
    e = make(path, fs, edit, setv); n = int(0.3 * fs); t = np.arange(n) / fs
    x = np.concatenate([np.sin(2 * np.pi * 100 * t) * 2.0, np.zeros(int(4 * fs))])
    yl, yr = e.run(x, x); y = np.abs(np.array(yl)); idx = np.nonzero(y[n:] > 1e-6)[0]
    return float((idx[-1] + 1) / fs) if len(idx) else 0.0

def soak(path, fs=48000, edit=None, setv=None, seconds=4, seed=7):
    """Noise, bursts, injected NaN/inf/1e9/denormals, and random slider changes. Output and state must stay finite and under the ceiling."""
    rng = random.Random(seed); e = make(path, fs, edit, setv); ok = True; worst = 0.0; why = ''
    chunk = int(0.05 * fs); sl = [k for k in e.sliders if k not in ('mode',) and ('ceil' in k.lower() or 'rel' in k.lower() or 'gain' in k.lower())]
    ranges = {'ceil': (-60, -3), 'rel': (10, 300), 'gain': (-120, 60)}
    for _ in range(int(seconds / 0.05)):
        amp = rng.choice([0.0, 0.01, 0.3, 1.0, 4.0]); x = [rng.uniform(-1, 1) * amp for _ in range(chunk)]
        for _k in range(3): x[rng.randrange(chunk)] = rng.choice([float('nan'), float('inf'), -float('inf'), 1e9, -1e9, 1e-40, 1e30])
        if sl and rng.random() < 0.5:
            k = rng.choice(sl); lo, hi = next(v for kk, v in ranges.items() if kk in k.lower()); e.set(**{k: rng.randint(lo, hi)})
        yl, yr = e.run(x, x); y = np.array(yl + yr)
        if not np.isfinite(y).all(): ok = False; why = 'non-finite output'; break
        worst = max(worst, float(np.abs(y).max() - e.get('ceilLin')))
        if any(isinstance(v, float) and not math.isfinite(v) for k, v in e.ns.items() if k.startswith('v_')): ok = False; why = 'non-finite state'; break
    if ok and worst > 1e-9: ok = False; why = f'output above ceiling by {worst:.2e}'
    return ok, why, worst

def build_checks(path, pid):
    """List of acceptance-check dicts for one .eel (all rates, all variants)."""
    out = []; tag = 'runtime=eel2py (subset interpreter, not WDL)'
    def add(n, ok, d): out.append(dict(check=n, status='pass' if ok else 'fail', detail=d + ' | ' + tag))
    add('eel.compile', True, 'parsed and transpiled')
    worst = dict(tp=-99, tpn=-99, clip=0, over=0, tail=0, thd=-99); soak_bad = []
    for fs in (48000, 44100):
        for v in VARIANTS.get(pid, [{}]):
            m = suite(path, fs, setv=v)
            worst['tp'] = max(worst['tp'], m['tp_overshoot_db']); worst['tpn'] = max(worst['tpn'], m['tp_noise_db']); worst['thd'] = max(worst['thd'], thd_db(path, fs, setv=v)); worst['clip'] = max(worst['clip'], m['clip_frac']); worst['over'] = max(worst['over'], m['sample_over'])
            if m['nonfinite']: soak_bad.append(f'{fs}:nonfinite')
            worst['tail'] = max(worst['tail'], tail(path, fs, setv=v))
            ok, why, _ = soak(path, fs, setv=v)
            if not ok: soak_bad.append(f'{fs}/{v}: {why}')
    add('limiter.ceiling', worst['over'] <= 1e-9, f"max sample over ceiling {worst['over']:.1e} (hard clamp; 17 test signals, 44.1+48 kHz)")
    add('limiter.clamp_engaged', worst['clip'] <= CLIP_LIMIT, f"fraction of steady-state samples on the hard clamp {worst['clip']:.5f} (limit {CLIP_LIMIT}); THD residual of limited 997 Hz +6 dB tone {worst['thd']:.1f} dB (limit {THD_LIMIT_DB})" if worst['thd'] <= THD_LIMIT_DB else f"THD residual {worst['thd']:.1f} dB above limit {THD_LIMIT_DB}")
    add('limiter.true_peak', worst['tp'] <= TP_LIMIT_DB and worst['tpn'] <= TP_NOISE_LIMIT_DB, f"true-peak overshoot above ceiling, 8x oversampled: tones/clicks/square {worst['tp']:+.2f} dB (limit {TP_LIMIT_DB}); +6 dB noise {worst['tpn']:+.2f} dB (guard {TP_NOISE_LIMIT_DB})")
    add('tail', worst['tail'] <= TAIL_LIMIT_S, f"output below -120 dB after {worst['tail']:.2f} s (limit {TAIL_LIMIT_S} s)")
    add('nan_soak', not soak_bad, 'NaN/inf/1e9/denormal injection + slider changes, 4 s x 2 rates: ' + ('clean' if not soak_bad else '; '.join(soak_bad)))
    return out

if __name__ == '__main__':
    import json
    for p in sys.argv[1:]:
        print(p, json.dumps(build_checks(p, os.path.basename(os.path.dirname(p))), indent=1))
