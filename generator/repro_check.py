#!/usr/bin/env python3
"""Rebuild v5 profiles and compare byte-for-byte with src/profiles. Usage: repro_check.py <out_dir> <repo_root>"""
import sys,hashlib,os
out,repo=sys.argv[1],sys.argv[2]
M={'iem_hd':'iem-hd','iem_v10':'iem-v10','iem_v4':'iem-v4','spk_v10':'spk-v10','spk_v8':'spk-v8','spk_v6':'spk-v6'}
bad=0
for a,b in M.items():
    for fn in sorted(os.listdir(os.path.join(out,a))):
        if not fn.endswith(('.vdc','.irs')):continue
        h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]
        r=os.path.join(repo,'src/profiles',b,fn);o=os.path.join(out,a,fn)
        ok=os.path.exists(r) and h(r)==h(o);bad+=not ok
        print('OK  ' if ok else 'DIFF',fn,h(o))
print('REPRODUCED' if not bad else 'MISMATCH %d'%bad);sys.exit(bad)
