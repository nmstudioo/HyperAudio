#!/usr/bin/env python3
"""python3 build/freeze.py  -> marks releases/<VERSION>/ as FROZEN, recording the hash of its SHA256SUMS.txt."""
import hashlib, os, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); v = open(f'{R}/VERSION').read().strip(); d = f'{R}/releases/{v}'
h = hashlib.sha256(open(f'{d}/SHA256SUMS.txt', 'rb').read()).hexdigest()
open(f'{d}/FROZEN', 'w').write(f'frozen {datetime.date.today()}\nsha256sums {h}\n'); print('frozen', v, h)
