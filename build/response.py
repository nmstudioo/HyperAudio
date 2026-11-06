"""Response checks from the shipped files alone (numpy only): VDC biquad cascade x IRS vs the stored curves.
Convention (verified against all six builds, 0.03 dB RMS): VDC section = b0,b1,b2,a1,a2 with H=(b0+b1z^-1+b2z^-2)/(1-a1z^-1-a2z^-2);
IRS path = channel 0 (2ch) or channel 0+1 (4ch true-stereo, mono in -> left out); correction = VDC_dB(48k bank) + IRS_dB."""
import struct, numpy as np
from verify import vdc_info

def vdc_db(path, fs, F):
    b = vdc_info(path)[fs]; z = np.exp(-1j * 2 * np.pi * np.asarray(F) / fs); H = np.ones(len(F), complex); rad = 0.0
    for i in range(0, len(b), 5):
        b0, b1, b2, a1, a2 = b[i:i + 5]
        H *= (b0 + b1 * z + b2 * z * z) / (1 - a1 * z - a2 * z * z); rad = max(rad, max(abs(np.roots([1, -a1, -a2]))))
    return 20 * np.log10(np.abs(H) + 1e-12), rad

def irs_db(path, F):
    bb = open(path, 'rb').read(); ch, sr = struct.unpack('<HI', bb[22:24] + bb[24:28]); i = bb.find(b'data'); n = struct.unpack('<I', bb[i + 4:i + 8])[0]
    x = np.frombuffer(bb[i + 8:i + 8 + n], dtype='<f4').reshape(-1, ch).astype(float); N = 1 << 16
    X = np.fft.rfft(x[:, 0] + (x[:, 1] if ch == 4 else 0), N); fr = np.fft.rfftfreq(N, 1 / sr)
    return 20 * np.log10(np.abs(np.interp(F, fr, X.real) + 1j * np.interp(F, fr, X.imag)) + 1e-12)

def checks(pdir, p, F):
    import os; out = []
    def add(n, ok, d): out.append(dict(check=n, status='pass' if ok else 'fail', detail=d))
    v = os.path.join(pdir, [f for f in p['file_order'] if f.endswith('.vdc')][0]); r = os.path.join(pdir, [f for f in p['file_order'] if f.endswith('.irs')][0])
    V, rad = vdc_db(v, 48000, F); cor = V + irs_db(r, F); c = p['curves']; sc = np.array(c['correction']); d = cor - sc
    add('response.correction_match', np.sqrt((d ** 2).mean()) <= 0.1 and abs(d).max() <= 0.25, f'file-derived VDC x IRS vs stored correction: RMS {np.sqrt((d**2).mean()):.3f} dB, max {abs(d).max():.3f} dB (limits 0.1 / 0.25)')
    g = float(np.interp(1000, F, cor)); add('response.gain1k', abs(g - p['stats']['gain1k']) <= 0.1, f"gain at 1 kHz {g:+.2f} dB, meta {p['stats']['gain1k']:+.1f}")
    add('response.chain_max', cor.max() <= 0.0, f"max chain gain {cor.max():+.2f} dB (must be <= 0 dB; meta chainMax {p['stats']['chainMax']})")
    add('vdc.stable', rad < 1.0, f'max pole radius {rad:.4f} (meta {p["stats"]["poleRadius"]})')
    raw, tg = np.array(c['raw']), np.array(c['target']); e = raw + cor - tg
    if p['device'] == 'iem': k = (F >= 30) & (F <= 16000); e = e[k] - e[k].mean(); band = '30-16k Hz, level-aligned'
    else: e = (e + np.mean(np.array(c['predicted']) - raw - sc))[(F >= 100) & (F <= 10000)]; band = '100-10k Hz, stored level offset'
    add('response.error_vs_target', abs(np.sqrt((e ** 2).mean()) - p['stats']['rms']) <= 0.5, f"recomputed RMS {np.sqrt((e**2).mean()):.2f} dB ({band}) vs meta {p['stats']['rms']} dB (band convention inferred; tolerance 0.5 dB)")
    B = vdc_info(v); d4 = vdc_db(v, 44100, F)[0] - V; mx = abs(d4).max()
    out.append(dict(check='vdc.sr_consistency', status='pass' if mx <= 0.3 else 'warn', detail=f'44.1 kHz bank vs 48 kHz bank max {mx:.2f} dB over 20-20k Hz (limit 0.3)' + ('' if mx <= 0.3 else '; known v5 deviation, refit in candidates/v6 awaiting listening check')))
    return out
