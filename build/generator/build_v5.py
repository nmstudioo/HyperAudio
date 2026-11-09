import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import FS
HERE=os.path.dirname(os.path.abspath(__file__))
V=HERE+'/inputs/v4/'
O=(sys.argv[1] if len(sys.argv)>1 else HERE+'/out')+'/'
for d in ('iem_hd','iem_v4','iem_v10','spk_v10','spk_v8','spk_v6'):os.makedirs(O+d,exist_ok=True)
NF=65536;FF=np.fft.rfftfreq(NF,1/FS)
def Hfull(h):return np.fft.rfft(h,NF)
def earM(x):   # mono-path ear response (complex on f grid)
    H=[Hm(x[:,c]) for c in range(x.shape[1])]
    return H[0]+H[2] if x.shape[1]==4 else H[0]
def peakfix(x,lim=0.944):
    p=abs(x).max();return x*(lim/p) if p>lim else x
def scale_to_maxgain(x,tgt=-0.5):
    m=dB(earM(x)).max();return x*10**((tgt-m)/20)
def wt_iem():return np.where(f<30,0.3,np.where(f<=16000,1.0,0.3))
def wt_spk():return np.where(f<90,0.0,np.where(f<=16000,1.0,0.3))
def target_iem(M):
    C=Tm['iem']-Rm['iem']-dB(M);m=(f>=300)&(f<=3000);C=C-np.median(C[m]);hi=f>16000;C[hi]=C[f<=16000][-1];return C
def target_spk(M,hp):
    C=Tm['spk']-Rm['spk'];m=(f>=1000)&(f<=6000);C=C-np.median(C[m]);C=np.clip(C,-16,8);hi=f>16000;C[hi]=C[f<=16000][-1]
    Md=dB(M);Md=Md-np.median(Md[m]);return C-Md
rep={}
def score(name,dev,x,S44,S48,gdb):
    M=earM(x);V48=resp_db(S48,f,48000)+gdb;V44=resp_db(S44,f,44100)+gdb
    tot=dB(M)+V48;P=Rm[dev]+tot;e=P-Tm[dev]
    lo,hi=(300,3000) if dev=='iem' else (1000,6000);m=(f>=lo)&(f<=hi);e=e-np.median(e[m])
    sel=(f>=(30 if dev=='iem' else 100))&(f<=16000)
    bands=[(20,100),(100,500),(500,2000),(2000,6000),(6000,10000),(10000,16000)]
    br=[np.sqrt(np.mean(e[(f>=a)&(f<b)]**2)) if ((f>=a)&(f<b)).any() else float('nan') for a,b in bands]
    z=[abs(np.roots([1,-s[3],-s[4]])).max() for s in S48+S44]
    rep[name]=dict(rms=float(np.sqrt(np.mean(e[sel]**2))),mx=float(abs(e[sel]).max()),chain_max=float(tot.max()),vdc_max=float(V48.max()),vdc_min=float(V48.min()),bank=float(abs(V44-V48).max()),pole=float(max(z)),gdb=float(gdb),irs_peak=float(abs(x).max()),irs_max_gain=float(dB(M).max()),bands=br,nsec=len(S48))
# ---------- IEM HD
x,*_=rdirs(V+'iem_hd/EDX_HD.irs');x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'iem_hd/EDX_HD.irs',x);C=target_iem(earM(x));S44,S48,g=build_vdc(O+'iem_hd/EDX_HD.vdc',C,wt_iem(),Mdb=dB(earM(x)),fmin=30);score('IEM HD','iem',x,S44,S48,g)
# ---------- IEM V4 : crossfeed level fix
x,*_=rdirs(V+'iem_v4/EDX_v4_HRIRxCrossfeed.irs');x[:,1]*=0.269;x[:,2]*=0.269;x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'iem_v4/EDX_v4_HRIRxCrossfeed.irs',x);C=target_iem(earM(x));S44,S48,g=build_vdc(O+'iem_v4/EDX_v4.vdc',C,wt_iem(),Mdb=dB(earM(x)),fmin=30);score('IEM V4','iem',x,S44,S48,g)
# ---------- IEM V10
x,*_=rdirs(V+'iem_v10/EDX_v10.irs');x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'iem_v10/EDX_v10.irs',x);C=target_iem(earM(x));S44,S48,g=build_vdc(O+'iem_v10/EDX_v10.vdc',C,wt_iem(),Mdb=dB(earM(x)),fmin=30);score('IEM V10','iem',x,S44,S48,g)
# ---------- SPK V10 (vdc-heavy): HP 110 Hz pre + fit
x,*_=rdirs(V+'spk_v10/SPK_v10.irs');x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'spk_v10/SPK_v10.irs',x)
hp48=[bq('HP',110,0,0.707,48000)];hp44=[bq('HP',110,0,0.707,44100)]
C=target_spk(earM(x),0);S44,S48,g=build_vdc(O+'spk_v10/SPK_v10.vdc',C,wt_spk(),hp48,hp44,N=9,gb=(-16,16),Mdb=dB(earM(x)),fmin=100);score('SPK V10','spk',x,S44,S48,g)
# ---------- SPK V8: L=R by power-average min-phase, then vdc
x,*_=rdirs(V+'spk_v8/SPK_v8_S.irs')
mag=np.sqrt(0.5*(abs(Hfull(x[:,0]))**2+abs(Hfull(x[:,1]))**2));h=minphase(mag,2048)
x=np.stack([h,h],1);x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'spk_v8/SPK_v8_S.irs',x);C=target_spk(earM(x),0);S44,S48,g=build_vdc(O+'spk_v8/SPK_v8_OG.vdc',C,wt_spk(),hp48,hp44,N=9,gb=(-16,16),Mdb=dB(earM(x)),fmin=100);score('SPK V8','spk',x,S44,S48,g)
# ---------- SPK V6 (convolver-heavy): min-phase IRS carries smooth correction, VDC = HP + residual
Cs=target_spk(np.ones(len(f)),0)           # capped T-R, aligned
hpR=resp_db(hp48,f,48000)
Csm=np.convolve(np.pad(Cs,(20,20),mode='edge'),np.ones(41)/41,'valid')   # ~1/3 oct smooth
magdb=np.interp(np.log(FF[1:]+1e-9),np.log(f),Csm,left=Csm[0],right=Csm[-1]);magdb=np.concatenate([[magdb[0]],magdb])
mag=10**(magdb/20);h=minphase(mag,4096,tail_ms=75);tt=np.arange(4096)/48.0;h=h*np.where(tt<12,1.0,np.where(tt>40,0.0,0.5*(1+np.cos(np.pi*(tt-12)/28))));x=np.stack([h,h],1);x=scale_to_maxgain(x,-0.5);x=peakfix(x)
wirs(O+'spk_v6/SPK_v6.irs',x);C=target_spk(earM(x),0);S44,S48,g=build_vdc(O+'spk_v6/SPK_v6.vdc',C,wt_spk(),hp48,hp44,N=6,gb=(-16,16),Mdb=dB(earM(x)),fmin=100);score('SPK V6','spk',x,S44,S48,g)
json.dump(rep,open(O+'report.json','w'),indent=1)
for k,v in rep.items():print(k,{a:(round(b,2) if isinstance(b,float) else [round(t,1) for t in b] if isinstance(b,list) else b) for a,b in v.items()})
