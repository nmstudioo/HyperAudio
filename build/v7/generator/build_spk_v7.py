#!/usr/bin/env python3
"""v7 Redmi 12 speaker 'Protection V6' candidate.
Design: min-phase IRS carries the smooth correction AND the 110 Hz high-pass (so the VDC needs no low-frequency pole);
IRS scaled to L1 <= L1_MAX and the level made up in the VDC gain; VDC = peaking residual only, bandwidth-limited so max pole radius <= R_MAX.
Usage: build_spk_v7.py <out_dir>"""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
src=open(HERE+'/build_v5.py').read();src=src[:src.index('# ---------- IEM HD')]
OUT=sys.argv[1];sys.argv=[sys.argv[0],OUT+'/_tmp'];exec(src)
L1_MAX=1.20;R_MAX=0.98;FMIN=200.0
qmax=lambda fc,fs:np.pi*fc/(fs*(-np.log(R_MAX)))
def fit2(Cv,wt,fs,N,warm=None):
    ty,p,lo,hi=(list(warm[0]),list(warm[1]),list(warm[2]),list(warm[3])) if warm else ([],[],[],[])
    def ref(p):
        L=np.array(lo);H=np.array(hi);p=np.clip(p,L+1e-6,H-1e-6)
        r=least_squares(lambda q:np.concatenate([(resp_db(mkS(ty,q,fs),f,fs)-Cv)*wt,0.03*np.array(q)[1::3]]),p,bounds=(L,H),max_nfev=300,x_scale='jac');return list(r.x)
    if ty:p=ref(p)
    while len(ty)<N:
        res=Cv-(resp_db(mkS(ty,p,fs),f,fs) if ty else 0);sm=np.convolve(res,np.ones(7)/7,'same')*wt
        i=int(np.argmax(abs(sm)));fc=min(max(f[i],FMIN*1.6),16000/1.6);g=float(np.clip(res[i],-8,5));qh=min(6.0,qmax(fc/1.6,fs))
        ty.append('PK');p+=[fc,g,min(2.5,qh)];lo+=[max(FMIN,fc/1.6),-12,0.5];hi+=[min(19500,fc*1.6),6,max(qh,0.6)];p=ref(p)
    return ty,p,lo,hi
def build(path,Cv,wt,N,Mdb,xc):
    r48=fit2(Cv,wt,48000,N);S48=mkS(r48[0],r48[1],48000)
    C44=resp_db(S48,f,48000);r44=fit2(C44,np.where(f>19000,0.2,1.0),44100,N,warm=r48);S44=mkS(r44[0],r44[1],44100)
    sel=(f>=100)&(f<=16000);tot=resp_db(S48,f,48000)+Mdb;gdb=-0.5-tot[sel].max()
    vdcfile(path,S44,S48,gdb);return S44,S48,gdb
os.makedirs(OUT+'/spk_v6',exist_ok=True)
# same tuning as v5: target = the v5 chain response (calculated); only the split between IRS and VDC changes
x5,*_=rdirs(HERE+'/inputs/v5/spk_v6/SPK_v6.irs');V5=vsec(HERE+'/inputs/v5/spk_v6/SPK_v6.vdc',48000)
T5=dB(Hm(x5[:,0]))+resp_db(V5.tolist(),f,48000)
Tsm=np.convolve(np.pad(T5,(20,20),mode='edge'),np.ones(41)/41,'valid')
mdb=np.interp(np.log(FF[1:]+1e-9),np.log(f),Tsm,left=Tsm[0],right=Tsm[-1]);mdb=np.concatenate([[mdb[0]],mdb]);mdb=np.maximum(mdb,mdb.max()-70)
h=minphase(10**(mdb/20),4096,tail_ms=75);tt=np.arange(4096)/48.0;h=h*np.where(tt<12,1.0,np.where(tt>40,0.0,0.5*(1+np.cos(np.pi*(tt-12)/28))))
x=np.stack([h,h],1);L1=abs(x).sum(0).max();x=x*min(1.0,L1_MAX/L1);x=peakfix(x)
wirs(OUT+'/spk_v6/SPK_v6.irs',x)
M=earM(x);C=T5-dB(M);C=C-np.median(C[(f>=1000)&(f<=6000)])
S44,S48,g=build(OUT+'/spk_v6/SPK_v6.vdc',C,wt_spk(),6,dB(M),x)
V7=dB(M)+resp_db(S48,f,48000)+g;dev=(V7-T5)[(f>=100)&(f<=16000)]
score('SPK V6 v7','spk',x,S44,S48,g)
r=rep['SPK V6 v7'];r['dev_vs_v5_rms']=float(np.sqrt((dev**2).mean()));r['dev_vs_v5_max']=float(abs(dev).max());r['irs_L1']=float(abs(x).sum(0).max());r['vdc_gain_db']=float(g)
import json;json.dump(r,open(OUT+'/spk_v6/fit_report.json','w'),indent=1)
print({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items() if k!='bands'},'bands',[round(b,1) for b in r['bands']])
