#!/usr/bin/env python3
"""v7 IEM HD candidates: same IRS + fitter + gates, only the target differs.
A = Harman IE 2019, B = JM-1 (Harman filters; renormalised to 0 dB at 1 kHz), C = v5 target (control).
Usage: build_cand.py <out_dir> <measurements_dir> ; writes <out>/<name>/EDX_HD.{irs,vdc} and report.json"""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
src=open(HERE+'/build_v5.py').read();src=src[:src.index('# ---------- IEM HD')]
OUT=sys.argv[1];MEAS=sys.argv[2];sys.argv=[sys.argv[0],OUT+'/_tmp']
exec(src)
def ldc(fn):
    r=[]
    for l in open(fn):
        p=l.replace(' ','').strip().split(',')
        try:r.append([float(x) for x in p[:2]])
        except ValueError:pass
    a=np.array(r);t=np.interp(np.log(f),np.log(a[:,0]),a[:,1]);return t-np.interp(np.log(1000.0),np.log(f),t)
T={'A_harman2019':ldc(MEAS+'/Harman_in-ear_2019.csv'),'B_jm1':ldc(MEAS+'/JM-1_with_Harman_filters.csv'),'C_v5target':Tm['iem'].copy()}
x0,*_=rdirs(V+'iem_hd/EDX_HD.irs');x0=scale_to_maxgain(x0,-0.5);x0=peakfix(x0)
res={}
for name,t in T.items():
    Tm['iem']=t;d=OUT+'/'+name;os.makedirs(d,exist_ok=True)
    wirs(d+'/EDX_HD.irs',x0);C=target_iem(earM(x0));S44,S48,g=build_vdc(d+'/EDX_HD.vdc',C,wt_iem(),Mdb=dB(earM(x0)),fmin=30);score(name,'iem',x0,S44,S48,g)
    res[name]=rep[name]
json.dump(res,open(OUT+'/report.json','w'),indent=1)
for k,v in res.items():print(k,{a:(round(b,3) if isinstance(b,float) else b) for a,b in v.items() if a in('rms','mx','chain_max','pole','bank','gdb','irs_peak')})
