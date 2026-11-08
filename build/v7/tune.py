import numpy as np,sys,itertools
sys.path.insert(0,'.')
from rt import signals,tp;import ref
S=signals();ce=10**(-1.5/20)
keys=['sine997_+6','sine3000_+6','fs4_+6','noise_+6','noise_+12','square1k','clicks']
def ev(**kw):
    r={}
    for k in keys:
        x=np.stack([S[k][:19200]]*2,1);y=ref.limit(x,**kw);r[k]=tp(y[4800:,0],ce)
    return r
for kb in (None,4,6,8):
  ref.KB=kb
  for nt,ph,g in ((16,(.25,.5,.75),1.0),(16,(.25,.5,.75),1.03),(24,(.25,.5,.75),1.0)):
    r=ev(nt=nt,align=True,phases=ph,guard=g);print('kaiser',kb,'nt',nt,'g',g,' '.join('%s %+.2f'%(k[:9],v) for k,v in r.items() if k in('noise_+6','noise_+12','square1k','sine997_+6')),'| worst %+.2f'%max(r.values()),flush=True)
