#!/usr/bin/env python3
"""v7 speaker V8 / V10: fold the 110 Hz protection high-pass (VDC section 0, pole radius 0.990) into the IRS.
Exact LTI re-ordering, so the chain response is unchanged (calculated); the VDC keeps its other 9 sections.
IRS is rescaled if L1 > L1_MAX and the VDC gain is adjusted so the chain is identical.
Usage: build_spk_fold.py <profiles_dir_v5> <out_dir>"""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
SRC,OUT=sys.argv[1],sys.argv[2]
from lib import *
from scipy.signal import lfilter
L1_MAX=1.20
def vdc_lines(fn):
    t=open(fn).read();return {b:np.array([float(s) for s in re.search(r'SR_%d:([^\n]*)'%b,t).group(1).split(',') if s.strip()]).reshape(-1,5) for b in (44100,48000)}
def hp_unit(fs,n=8192):
    b0,b1,b2,a1,a2=bq('HP',110,0,0.707,fs);d=np.zeros(n);d[0]=1;return lfilter([b0,b1,b2],[1,-a1,-a2],d),np.array([b0,b1,b2,a1,a2])
os.makedirs(OUT,exist_ok=True)
res={}
for name,irs,vdc in (('spk_v6','SPK_v6.irs','SPK_v6.vdc'),('spk_v8','SPK_v8_S.irs','SPK_v8_OG.vdc'),('spk_v10','SPK_v10.irs','SPK_v10.vdc')):
    d=SRC+'/'+name.replace('_','-')+'/';x,*_=rdirs(d+irs);V=vdc_lines(d+vdc);n=len(x)
    NF=2                                     # sections 0 (110 Hz protection high-pass) and 1 (low shelf) carry the 0.990 poles
    d0=np.zeros(16384);d0[0]=1;h=d0
    for q in V[48000][:NF]:h=lfilter(q[:3],[1,-q[3],-q[4]],h)
    y=np.stack([np.convolve(x[:,c],h)[:n] for c in range(x.shape[1])],1)
    tail=np.stack([np.convolve(x[:,c],h)[n:] for c in range(x.shape[1])],1);ter=float(abs(tail[:, :]).max())
    s=min(1.0,L1_MAX/abs(y).sum(0).max());y=y*s
    S48=V[48000][NF:].copy();S44=V[44100][NF:].copy()
    for S in (S48,S44):S[0][:3]/=s
    if name!='spk_v6':                      # remaining 44.1 sections were fitted jointly with the folded ones: refit to the 48 kHz response
        T=resp_db(S48.tolist(),f,48000);W=np.where(f<=16000,1.0,0.1)
        def mk(p):return p.reshape(-1,5)
        def resid(p):
            Sx=mk(p);pen=[max(0,abs(np.roots([1,-q[3],-q[4]])).max()-0.985)*1e3 for q in Sx]
            return np.concatenate([(resp_db(Sx.tolist(),f,44100)-T)*W,pen])
        r=least_squares(resid,S44.flatten(),method='lm',max_nfev=4000);S44=mk(r.x)
    os.makedirs(OUT+'/'+name,exist_ok=True)
    wirs(OUT+'/'+name+'/'+irs,y)
    fmt=lambda S:','.join('%.9f'%v for r in S for v in r)
    open(OUT+'/'+name+'/'+vdc,'w').write('SR_44100:'+fmt(S44)+'\nSR_48000:'+fmt(S48)+'\n')
    # calculated equivalence on the f grid (channel 0)
    a=dB(Hm(x[:,0]))+resp_db(V[48000].tolist(),f,48000);b=dB(Hm(y[:,0]))+resp_db(S48.tolist(),f,48000)
    z=lambda S,fs:max(abs(np.roots([1,-r[3],-r[4]])).max() for r in S)
    bank=float(abs(resp_db(S44.tolist(),f,44100)-resp_db(S48.tolist(),f,48000))[(f>=20)&(f<=16000)].max());res[name]=dict(bank44_48=bank,chain_dev_max_db=float(abs(a-b).max()),irs_L1=float(abs(y).sum(0).max()),irs_peak=float(abs(y).max()),trunc_tail_peak=ter,pole48=float(z(S48,48000)),pole44=float(z(S44,44100)),irs_scale=float(s))
    print(name,{k:round(v,5) for k,v in res[name].items()})
import json;json.dump(res,open(OUT+'/fold_report.json','w'),indent=1)
