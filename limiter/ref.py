"""numpy reference of the shared limiter core (float64). Same structure as the EEL: lookahead D, sliding-min of required gain,
moving-average smoothing, detector = windowed-sinc interpolation at 3 intermediate phases (4x)."""
import numpy as np
from collections import deque
KB=None
def taps(nt,fr,win='hann'):
    k=np.arange(nt);c=nt//2-1;d=k-(c+fr)
    s=np.where(abs(d)<1e-9,1.0,np.sin(np.pi*d)/(np.pi*d+1e-30))
    if KB is not None:w=np.i0(KB*np.sqrt(np.clip(1-(d/(nt/2))**2,0,1)))/np.i0(KB)
    else:w=0.5+0.5*np.cos(np.pi*d/(nt/2))
    v=s*w;return v/v.sum()
def limit(x,ceil_db=-1.5,rel_ms=80,fs=48000,nt=8,phases=(0.25,0.5,0.75),gate=0.4,guard=1.0,fade=True,dc=True,align=False):
    """x: (n,2). returns y (n,2), plus gain trace"""
    n=len(x);ceil=10**(ceil_db/20);D=int(max(2,min(500,np.floor(0.0015*fs+0.5))));N=D+1
    rel_k=1-np.exp(-1/(max(rel_ms,10)*0.001*fs))
    CF=[taps(nt,p) for p in phases];hist=np.zeros((2,nt));hot=0
    dq=deque();eB=np.ones(D);ew=0;esum=float(D);eprev=1.0;Lg=(nt//2-1) if align else 0;NA=N+Lg;dly=np.zeros((NA,2));w=0;chk=0
    dcR=np.exp(-2*np.pi*2.0/fs);dx=np.zeros(2);dy=np.zeros(2)
    y=np.zeros((n,2));fl=max(1,int(0.05*fs));fn=0
    for t in range(n):
        l,r=x[t]
        if dc:
            yy=np.array([l,r])-dx+dcR*dy;dx=np.array([l,r]);dy=yy;l,r=yy
        hist=np.roll(hist,-1,1);hist[0,-1]=l;hist[1,-1]=r
        peak=max(abs(l),abs(r));isp=0.0
        pc=max(abs(hist[0,nt//2-1]),abs(hist[1,nt//2-1])) if align else peak
        hot=nt if peak>ceil*gate else hot-1
        if hot>0:
            for c in CF:isp=max(isp,abs(hist[0]@c),abs(hist[1]@c))
        pk=max(pc,isp*guard);req=min(max(ceil/pk if pk>ceil else 1.0,0.0),1.0)
        while dq and dq[-1][0]>=req:dq.pop()
        dq.append((req,t))
        while dq[0][1]<=t-N:dq.popleft()
        m=dq[0][0];dly[w]=(l,r)
        e=min(m,eprev+(1-eprev)*rel_k);eprev=e;esum+=e-eB[ew];eB[ew]=e;ew=(ew+1)%D
        chk+=1
        if chk>=N*8:esum=eB.sum();chk=0
        g=min(1.0,esum/D);rp=(w+1)%NA
        if fn<fl:fn+=1;fg=fn/fl
        else:fg=1.0
        y[t]=np.clip(dly[rp]*g*fg,-ceil,ceil);w=(w+1)%NA
    return y
