"""Derive profile stats from the shipped files on a fine grid (numpy). Used by build.py --write-stats and the stats.derived check."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def derive(pdir, p):
    import numpy as np
    from verify import irs_info, vdc_info
    from response import vdc_db, irs_db
    F = np.geomspace(20, 20000, 4096)
    v = os.path.join(pdir, [f for f in p['file_order'] if f.endswith('.vdc')][0])
    r = os.path.join(pdir, [f for f in p['file_order'] if f.endswith('.irs')][0])
    V, rad = vdc_db(v, 48000, F); cor = V + irs_db(r, F)
    return dict(irsPeak=round(irs_info(r)['peak'], 2), sections=len(vdc_info(v)[48000]) // 5, poleRadius=round(float(rad), 3),
                gain1k=round(float(np.interp(1000, F, cor)), 1), chainMax=round(float(cor.max()), 2))

TOL = dict(irsPeak=0.006, sections=0, poleRadius=0.002, gain1k=0.15, chainMax=0.15)

def check(pdir, p):
    d = derive(pdir, p); st = p['stats']
    bad = ['%s stored %s derived %s' % (k, st.get(k), d[k]) for k in TOL if abs(float(st.get(k, 1e9)) - d[k]) > TOL[k]]
    return [dict(check='stats.derived', status='warn' if bad else 'pass',
                 detail=('stored stats drift from the files (fine grid): ' + '; '.join(bad)) if bad else 'stored stats match the files on a 4096-point grid')]
