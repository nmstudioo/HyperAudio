import numpy as np,subprocess,re,sys,os
from scipy.signal import resample_poly
H='/home/claude/w/vm/harness'
def run(path,x,pre=None,fs=48000):
    """x: (n,2) float; runs real NSEEL VM (harness). pre: dict of var overrides not supported -> edit text"""
    t=open(path).read() if isinstance(path,str) and os.path.exists(path) else path
    open('/tmp/_rt.eel','w').write(t)
    r=subprocess.run([H,'/tmp/_rt.eel','run'],input=x.astype('<f4').tobytes(),capture_output=True,timeout=300);o=r.stdout
    if b'COMPILE OK' not in o:raise RuntimeError(o[:300])
    i=o.index(b'COMPILE OK\n')+11;return np.frombuffer(o[i:],'<f4').reshape(-1,2).astype(float)
def tp(y,ce,os_=8,trim=96):
    u=resample_poly(y,os_,1);u=u[trim*os_:-trim*os_]   # trim edge ringing from truncation (metric artifact)
    return 20*np.log10(max(np.abs(u).max(),1e-12)/ce)
def signals(fs=48000):
    n=int(1.5*fs);t=np.arange(n)/fs;S={}
    for f in (100,997,3000,12000):
        for db in (0,6,12):S['sine%d_%+d'%(f,db)]=np.sin(2*np.pi*f*t+0.7)*10**(db/20)
    for db in (0,6):S['fs4_%+d'%db]=np.sin(2*np.pi*(fs/4)*t+np.pi/4)*10**(db/20)*1.4142
    r=np.random.default_rng(1);g=np.clip(r.standard_normal(n)*0.5,-1,1);S['noise_0']=g*.5;S['noise_+6']=g*2.0
    r=np.random.default_rng(7);S['noise_+12']=np.clip(r.standard_normal(n),-4,4)*2.0
    S['square1k']=np.sign(np.sin(2*np.pi*1000*t));c=np.zeros(n);c[::480]=1;S['clicks']=c
    return S
def suite(path,ceil_db=-1.5):
    ce=10**(ceil_db/20);out={}
    for k,x in signals().items():
        y=run(path,np.stack([x,x],1));a=y[4800:,0];out[k]=(tp(a,ce),np.abs(a).max()/ce)
    return out
if __name__=='__main__':
    for k,(a,b) in suite(sys.argv[1],float(sys.argv[2]) if len(sys.argv)>2 else -1.5).items():print('%-12s TP %+.2f dB  sample/ceil %.4f'%(k,a,b))
