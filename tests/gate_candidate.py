"""Offline gates for a candidate profile folder: python3 tests/gate_candidate.py candidates/v6/iem-ghd/EDX_GHD
All results are calculated (numpy/scipy + eel2py subset interpreter); none are device or acoustic measurements."""
import sys, os, subprocess, json
import numpy as np
from scipy.signal import freqz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))
from verify import vdc_info, irs_info, eel_lint
b = sys.argv[1]; ok = True
def rep(n, p, d):
    global ok; ok &= p; print(('PASS ' if p else 'FAIL ') + n + ': ' + d)
i = irs_info(b + '.irs'); x = np.fromfile(b + '.irs', '<f4', offset=0)
raw = open(b + '.irs', 'rb').read(); j = raw.find(b'data'); x = np.frombuffer(raw[j+8:], '<f4').reshape(-1, i['channels'])
SPK = i['channels'] == 2   # speaker profiles: 2-channel IRS, chain measured on channel 0 (as the generator does)
rep('irs.format', i['format'] == 3 and i['channels'] in (2, 4) and i['finite'], str(i))
rep('irs.peak', i['peak'] <= 0.95, f"{i['peak']:.3f} (<=0.95)")
l1 = np.abs(x).sum(0).max(); rep('irs.l1', l1 <= 1.25, f'{l1:.3f} (<=1.25)')
e = (x**2).sum(1); c = np.cumsum(e[::-1])[::-1]; t = int(np.argmax(10*np.log10(c/c[0]+1e-30) < -80)); rep('irs.tail', t < len(x), f'-80 dB at frame {t} of {len(x)}')
v = vdc_info(b + '.vdc'); N = 1 << 15; F = np.fft.rfftfreq(N, 1/48000); m = (F >= (100 if SPK else 20)) & (F <= (16000 if SPK else 20000))
H = np.fft.rfft(x[:, 0], N) + (0 if SPK else np.fft.rfft(x[:, 1], N)); R = {}
for sr, k in v.items():
    s = np.array(k).reshape(-1, 5); pr = max(np.abs(np.roots([1, -a1, -a2])).max() for _, _, _, a1, a2 in s)
    rep(f'vdc.{sr}.stable', pr <= 0.985, f'{len(s)} sections, max pole {pr:.4f}')
    G = np.geomspace(20, 16000, 300); V = np.ones(300, complex)
    for q in s: V *= freqz(q[:3], [1, -q[3], -q[4]], worN=G, fs=sr)[1]
    R[sr] = 20*np.log10(abs(V))
    if sr == 48000:
        V = np.ones(len(F), complex)
        for q in s: V *= freqz(q[:3], [1, -q[3], -q[4]], worN=F, fs=sr)[1]
        g = (20*np.log10(abs(H*V)))[m].max(); rep('chain.max', abs(g + 0.5) < 0.05, f'max (LL+LR)*VDC {g:.2f} dB (target -0.50)')
d = abs(R[44100] - R[48000]).max(); rep('vdc.sr_match', d <= 0.3, f'{d:.3f} dB (<=0.3)')
er = eel_lint(b + '.eel'); rep('eel.lint', not er, str(er))
out = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'eel', 'limiter_tests.py'), b + '.eel'], capture_output=True, text=True).stdout
try:
    for q in json.loads(out[out.index('['):]): rep('eel.' + q['check'], q['status'] == 'pass', q['detail'])
except Exception as ex: rep('eel.suite', False, 'did not run: ' + str(ex)[:80])
print('ALL PASS (calculated only)' if ok else 'FAILED'); sys.exit(0 if ok else 1)
