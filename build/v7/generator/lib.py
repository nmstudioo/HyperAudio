#!/usr/bin/env python3
"""HyperAudio DSP generator library (extracted from the pipeline that produced v5)."""
import sys,re,struct,os,numpy as np
from scipy.optimize import least_squares
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'inputs','data')+os.sep
def rdirs(fn):
    d=open(fn,'rb').read();pos=12;fm=None;ex=[]
    while pos+8<=len(d):
        cid=d[pos:pos+4];sz=struct.unpack('<I',d[pos+4:pos+8])[0]
        if cid==b'fmt ':fm=struct.unpack('<HHIIHH',d[pos+8:pos+24]);fmx=sz
        elif cid==b'data':ds=pos+8;dn=min(sz,len(d)-ds);dsz=sz
        else:ex.append((cid,sz))
        pos+=8+sz+(sz&1)
    tag,ch,sr,br,ba,bits=fm
    if tag==3 or (tag==0xFFFE):x=np.frombuffer(d[ds:ds+dn],'<f8' if bits==64 else '<f4')
    else:x=np.frombuffer(d[ds:ds+dn],'<i2').astype(float)/32768
    n=len(x)//ch;return x[:n*ch].reshape(n,ch).astype(float),fm,ex,len(d),dsz,dn
ld=lambda fn:np.loadtxt(fn,delimiter=',',comments='#',skiprows=1 if open(fn).readline().startswith('frequency') else 2)
f=np.geomspace(20,20000,1200)
def curve(fn):a=ld(fn);return np.interp(np.log(f),np.log(a[:,0]),a[:,1])
Rm={'iem':curve(DATA+'Raw/kz_edx_pro_raw.txt'),'spk':curve(DATA+'Raw/redmi12_speaker_raw.txt')}
Tm={'iem':curve(DATA+'target/kz_edx_pro_target.txt'),'spk':curve(DATA+'target/redmi12_speaker_target.txt')}
def vsec(fn,bank):
    t=open(fn).read();m=re.search(r'SR_%d:([^\n]*)'%bank,t);v=np.array([float(s) for s in m.group(1).split(',') if s.strip()]);return v.reshape(-1,5)
def vr(S,fs):
    z=np.exp(-1j*2*np.pi*f/fs);H=np.ones(len(f),complex)
    for b0,b1,b2,a1,a2 in S:H*=(b0+b1*z+b2*z**2)/(1-a1*z-a2*z**2)
    return H
Hm=lambda h:np.exp(-1j*2*np.pi*np.outer(f,np.arange(len(h)))/48000)@h
dB=lambda x:20*np.log10(abs(x)+1e-30)
builds=[('IEM HD','iem','iem_hd/EDX_HD.irs','iem_hd/EDX_HD.vdc'),('IEM V4','iem','iem_v4/EDX_v4_HRIRxCrossfeed.irs','iem_v4/EDX_v4.vdc'),('IEM V10','iem','iem_v10/EDX_v10.irs','iem_v10/EDX_v10.vdc'),('SPK V6','spk','spk_v6/SPK_v6.irs','spk_v6/SPK_v6.vdc'),('SPK V8','spk','spk_v8/SPK_v8_S.irs','spk_v8/SPK_v8_OG.vdc'),('SPK V10','spk','spk_v10/SPK_v10.irs','spk_v10/SPK_v10.vdc')]
FS=48000
def wirs(path,x):
    x=np.asarray(x,'<f4');n,ch=x.shape;data=x.tobytes()
    fmt=struct.pack('<HHIIHH',3,ch,FS,FS*4*ch,4*ch,32)
    body=b'WAVE'+b'fmt '+struct.pack('<I',16)+fmt+b'data'+struct.pack('<I',len(data))+data
    open(path,'wb').write(b'RIFF'+struct.pack('<I',len(body))+body)
def minphase(mag,N=2048,nfft=65536,tail_ms=8):
    # mag: |H| on rfft grid (nfft//2+1) -> min-phase FIR length N
    c=np.fft.irfft(np.log(np.maximum(mag,1e-8)),nfft);w=np.zeros(nfft);w[0]=1;w[1:nfft//2]=2;w[nfft//2]=1
    h=np.fft.irfft(np.exp(np.fft.rfft(c*w)),nfft)[:N]
    k=int(tail_ms*FS/1000);h[N-k:]*=0.5*(1+np.cos(np.pi*np.arange(k)/k));return h
def bq(t_,fc,g,q,fs):
    A=10**(g/40);w=2*np.pi*fc/fs;al=np.sin(w)/(2*q);c=np.cos(w)
    if t_=='PK':b=[1+al*A,-2*c,1-al*A];a=[1+al/A,-2*c,1-al/A]
    elif t_=='LS':s=2*np.sqrt(A)*al;b=[A*((A+1)-(A-1)*c+s),2*A*((A-1)-(A+1)*c),A*((A+1)-(A-1)*c-s)];a=[(A+1)+(A-1)*c+s,-2*((A-1)+(A+1)*c),(A+1)+(A-1)*c-s]
    elif t_=='HS':s=2*np.sqrt(A)*al;b=[A*((A+1)+(A-1)*c+s),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-s)];a=[(A+1)-(A-1)*c+s,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-s]
    else: # HP
        b=[(1+c)/2,-(1+c),(1+c)/2];a=[1+al,-2*c,1-al]
    b=np.array(b)/a[0];a=np.array(a)/a[0];return [b[0],b[1],b[2],-a[1],-a[2]]
def resp_db(S,ff,fs):
    z=np.exp(-1j*2*np.pi*ff/fs);H=np.ones(len(ff),complex)
    for b0,b1,b2,a1,a2 in S:H*=(b0+b1*z+b2*z**2)/(1-a1*z-a2*z**2)
    return 20*np.log10(abs(H))
def mkS(ty,p,fs,pre=()):
    return list(pre)+[bq(ty[i],p[3*i],p[3*i+1],p[3*i+2],fs) for i in range(len(ty))]
def fit(Cv,wt,fs,N=10,pre=(),warm=None,gb=(-12,6),first=('LS','HS')):
    PRE=resp_db(pre,f,fs) if len(pre) else 0
    tgt=Cv-PRE
    if warm is None:
        ty=list(first);p=[150,-2,0.6, 6000,-2,0.6];lo=[20,-14,0.3, 3000,-14,0.3];hi=[500,8,1.0, 16000,8,1.0]
    else: ty,p,lo,hi=warm[0][:],list(warm[1]),list(warm[2]),list(warm[3])
    def ref(p):
        L=np.array(lo);H=np.array(hi);p=np.clip(p,L+1e-6,H-1e-6)
        r=least_squares(lambda q:np.concatenate([(resp_db(mkS(ty,q,fs),f,fs)-tgt)*wt,0.03*np.array(q)[1::3]]),p,bounds=(L,H),max_nfev=300,x_scale='jac');return list(r.x)
    p=ref(p)
    while len(ty)<N:
        res=tgt-resp_db(mkS(ty,p,fs),f,fs);sm=np.convolve(res,np.ones(7)/7,'same')*wt
        i=int(np.argmax(abs(sm)));fc=f[i];g=float(np.clip(res[i],-8,5))
        ty.append('PK');p+=[fc,g,2.5];lo+=[max(20,fc/1.6),gb[0],0.5];hi+=[min(19500,fc*1.6),gb[1],6];p=ref(p)
    return ty,p,lo,hi
def vdcfile(path,S44,S48,gdb):
    g=10**(gdb/20)
    def s(S):
        S=[list(x) for x in S];S[0][0]*=g;S[0][1]*=g;S[0][2]*=g;return ','.join('%.9f'%v for r in S for v in r)
    open(path,'w').write('SR_44100:'+s(S44)+'\nSR_48000:'+s(S48)+'\n')
def build_vdc(path,Cv,wt,pre48=(),pre44=(),N=10,gb=(-12,6),Mdb=None,fmin=30):
    r48=fit(Cv,wt,48000,N,pre48,gb=gb);S48=mkS(r48[0],r48[1],48000,pre48)
    C44=resp_db(S48,f,48000);r44=fit(C44,np.where(f>19000,0.2,1.0),44100,N,pre44,warm=r48,gb=gb);S44=mkS(r44[0],r44[1],44100,pre44)
    sel=(f>=fmin)&(f<=16000);tot=resp_db(S48,f,48000)+(0 if Mdb is None else Mdb);gdb=-0.5-tot[sel].max()   # chain max gain -0.5 dB
    vdcfile(path,S44,S48,gdb);return S44,S48,gdb
