#!/usr/bin/env python3
"""python3 tests/visual_diff.py OLD_DIR NEW_DIR OUT_DIR [MAX_PCT]  -> exit 1 if any screenshot differs by more than MAX_PCT percent."""
import os, sys
from PIL import Image, ImageChops
old, new, out = sys.argv[1:4]; mx = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
os.makedirs(out, exist_ok=True); bad = []; lines = []
names = sorted(set(os.listdir(old)) | set(os.listdir(new)))
for n in names:
    if not n.endswith('.png'): continue
    if not (os.path.exists(f'{old}/{n}') and os.path.exists(f'{new}/{n}')): bad.append(n); lines.append(f'MISSING {n}'); continue
    a = Image.open(f'{old}/{n}').convert('RGB'); b = Image.open(f'{new}/{n}').convert('RGB')
    if a.size != b.size: bad.append(n); lines.append(f'SIZE {n} {a.size} -> {b.size}'); b.save(f'{out}/{n}'); continue
    d = ImageChops.difference(a, b)
    if not d.getbbox(): continue
    cnt = d.convert('L').point(lambda v: 255 if v else 0).histogram()[255]; pct = cnt / (a.size[0] * a.size[1]) * 100
    lines.append(f'DIFF {n} {pct:.4f}% bbox {d.getbbox()}')
    if pct > mx: bad.append(n); d.point(lambda v: 255 if v else 0).save(f'{out}/{n}')
open(f'{out}/report.txt', 'w').write('\n'.join(lines) + f'\n{len(names)} files, {len(bad)} over {mx}%\n')
print('\n'.join(lines)); print(f'{len(names)} files compared, {len(bad)} over {mx}%'); sys.exit(1 if bad else 0)
