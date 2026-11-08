#!/usr/bin/env python3
"""Promote the v7 candidates into src/profiles, refresh src/profiles.meta.json, bump VERSION, add a changelog section.
  python3 tools/promote_v7.py --hd A|B|C [--version 7.0.0] [--keep-v6-structure] [--dry-run]
--hd A = Harman IE 2019, B = JM-1, C = v5 target (control). --keep-v6-structure: Protection V6 gets only the new EEL (fallback if the
VDC-to-IRS level path is a problem on the device). Changed builds are reset to device status 'untested'. Then run the printed commands."""
import argparse, datetime, json, os, shutil, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'build'))
from verify import irs_info, vdc_info
from response import vdc_db, irs_db
ap = argparse.ArgumentParser(); ap.add_argument('--hd', required=True, choices='ABC'); ap.add_argument('--version', default='7.0.0')
ap.add_argument('--keep-v6-structure', action='store_true'); ap.add_argument('--dry-run', action='store_true'); a = ap.parse_args()
V7 = os.path.join(ROOT, 'candidates', 'v7'); SP = os.path.join(ROOT, 'src', 'profiles')
HD = {'A': 'A_harman2019', 'B': 'B_jm1', 'C': 'C_v5target'}[a.hd]
SRC = {'iem-hd': 'iem-hd/' + HD, 'iem-v4': 'iem-v4', 'iem-v10': 'iem-v10', 'spk-v6': 'spk-v6', 'spk-v8': 'spk-v8', 'spk-v10': 'spk-v10'}
same = lambda x, y: os.path.exists(y) and open(x, 'rb').read() == open(y, 'rb').read()
changed = {}; copies = []
for pid, sub in SRC.items():
    for fn in sorted(os.listdir(os.path.join(V7, sub))):
        if not fn.endswith(('.irs', '.vdc', '.eel')): continue
        if pid == 'spk-v6' and a.keep_v6_structure and not fn.endswith('.eel'): continue
        s, d = os.path.join(V7, sub, fn), os.path.join(SP, pid, fn)
        if not same(s, d): copies.append((s, d)); changed.setdefault(pid, []).append(fn)
print('HD candidate %s (%s); files to change:' % (a.hd, HD))
for pid, fs in changed.items(): print('  %-8s %s' % (pid, ', '.join(fs)))
if a.dry_run: print('dry run: nothing written'); sys.exit(0)

meta = json.load(open(os.path.join(ROOT, 'src', 'profiles.meta.json'), encoding='utf-8')); F = np.array(meta['freq'])
for s, d in copies: shutil.copyfile(s, d)

def target_from_csv(path):
    r = [l.strip().split(',') for l in open(path)][1:]; x = np.array([[float(p[0]), float(p[1])] for p in r if len(p) >= 2 and p[0].replace('.', '').isdigit()])
    t = np.interp(np.log(F), np.log(x[:, 0]), x[:, 1]); return t - np.interp(np.log(1000.0), np.log(F), t)
CSV = {'A': 'Harman_in-ear_2019.csv', 'B': 'JM-1_with_Harman_filters.csv'}
for p in meta['profiles']:
    pid = p['id']
    if pid not in changed: continue
    pdir = os.path.join(SP, pid); f = lambda e: os.path.join(pdir, [n for n in p['file_order'] if n.endswith(e)][0])
    c = p['curves']; raw = np.array(c['raw']); old = np.array(c['correction']); st = p['stats']; tg_old = np.array(c['target'])
    V, rad = vdc_db(f('.vdc'), 48000, F); cor = V + irs_db(f('.irs'), F)
    if pid == 'iem-hd' and a.hd in CSV: c['target'] = [round(float(v), 1) for v in target_from_csv(os.path.join(ROOT, 'data', 'measurements', CSV[a.hd]))]
    tg = np.array(c['target'])
    st['irsPeak'] = round(irs_info(f('.irs'))['peak'], 2); st['sections'] = len(vdc_info(f('.vdc'))[48000]) // 5; st['poleRadius'] = round(float(rad), 3)
    st['gain1k'] = round(float(np.interp(1000, F, cor)), 1); st['chainMax'] = round(float(cor.max()), 1)
    off = float(np.mean(np.array(c['predicted']) - raw - old))
    if p['device'] == 'iem':
        k = (F >= 30) & (F <= 16000); e = (raw + cor - tg)[k]; e0 = (raw + old - tg_old)[k]
        st['rms'] = round(float(np.sqrt(((e - e.mean()) ** 2).mean())), 2); st['max'] = round(float(abs(e - e.mean()).max()), 1)
        off += float(e0.mean() - e.mean())   # predicted stays level-aligned to the (possibly new) target, as in the stored curves
    c['correction'] = [round(float(v), 1) for v in cor]; c['predicted'] = [round(float(v), 1) for v in raw + cor + off]
    n = st['sections']
    for fx in p['facts']:
        if fx[0] == 'VDC': fx[1] = '%d sections' % n
    if p['script'].endswith(' v5'): p['script'] = p['script'][:-3] + ' v7'
    if pid == 'spk-v6' and not a.keep_v6_structure:
        p['desc'] = 'The IRS carries the smooth correction and the 110 Hz high-pass that protects the micro-speaker; the VDC adds five narrow corrections.'
    p['evidence'] = {'offline': True, 'device': 'untested', 'deviceNote': 'v7 build: not device-tested yet. Earlier reports apply to the v6.1.0 files only.'}
ver = a.version; meta['version'] = 'v' + ver; meta['released'] = datetime.date.today().isoformat()
open(os.path.join(ROOT, 'src', 'profiles.meta.json'), 'w', encoding='utf-8').write(json.dumps(meta, separators=(',', ':')))
open(os.path.join(ROOT, 'VERSION'), 'w').write(ver + '\n')
cl = os.path.join(ROOT, 'docs', 'CHANGELOG.md'); t = open(cl, encoding='utf-8').read()
sec = ['## v%s' % ver, '', 'Calculated and offline-checked only; no device tests for these files yet.', '',
       '- Shared limiter core v7 in all six scripts: 16-tap Kaiser true-peak detector, centre-aligned lookahead, worst 8x overshoot +0.25 dB (v5: +1.7 to +1.95 dB), +0.15 ms latency.',
       '- IEM HD target: %s.' % {'A': 'Harman IE 2019 (new fit)', 'B': 'JM-1 with Harman filters (new fit)', 'C': 'unchanged v5 target'}[a.hd],
       '- Speakers: the 110 Hz high-pass and low shelf moved from the VDC into the IRS (chain response unchanged); max pole radius 0.971 to 0.980; Protection V6 IRS L1 %s.' % ('stays 2.24 (kept v5 structure)' if a.keep_v6_structure else '2.24 to 1.20'),
       '- IEM Spatial V4 and Reference V10: new limiter only.', '']
if '## v%s' % ver not in t:
    i = t.index('## Unreleased'); open(cl, 'w', encoding='utf-8').write(t[:i] + '\n'.join(sec) + '\n' + t[i:])
print('\nNext:\n  python3 build/build.py\n  python3 build/docs_site.py && python3 tools/ship.py\n  python3 build/freeze.py\n  git add -A && git commit -m "release: v%s" && git tag v%s' % (ver, ver))
