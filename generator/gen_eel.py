import numpy as np
# ---- unrolled gated true-peak detector (8-tap Hann-sinc, phases .25 .5 .75) ----
NT=16;KB=4.0;LG=NT//2-1;GUARD_TP=1.015
def coefs(fr):
    k=np.arange(NT);d=k-(LG+fr);w=np.i0(KB*np.sqrt(np.clip(1-(d/(NT/2))**2,0,1)))/np.i0(KB)
    v=np.where(abs(d)<1e-9,1.0,np.sin(np.pi*d)/(np.pi*d+1e-30))*w;return v/v.sum()
CF=[coefs(x) for x in (0.25,0.5,0.75)]
def dot(pref):
    out=[]
    for c in CF:out.append('('+' + '.join('%s%d * %.9f'%(pref,k,c[k]) for k in range(NT))+')')
    return out
ISP_INIT='isp_hot = 0;\n'+''.join('ia%d = 0; ib%d = 0;\n'%(k,k) for k in range(NT))
def ISP(l,r):
    s='  // true-peak (gated, unrolled, 16-tap Kaiser sinc): history shift\n'
    for k in range(NT-1):s+='  ia%d = ia%d; ib%d = ib%d;\n'%(k,k+1,k,k+1)
    s+='  ia%d = %s; ib%d = %s;\n'%(NT-1,l,NT-1,r)
    s+='  isp_pk = 0;\n  (tpDetect > 0 && max(abs(%s), abs(%s)) > ceilLin * 0.4) ? ( isp_hot = %d; ) : ( isp_hot -= 1; );\n  isp_hot > 0 ? (\n'%(l,r,NT)
    for pa,pf in (('ia','a'),('ib','b')):
        for q in dot(pa):s+='    isp_pk = max(isp_pk, abs(%s));\n'%q
    s+='  );\n'
    return s
LIM_CLEAR='''L_i = 0;
loop(L_NA, L_dlyL[L_i] = 0; L_dlyR[L_i] = 0; L_i += 1; );
L_i = 0;
loop(L_cap, L_dqV[L_i] = 1.0; L_dqI[L_i] = 0; L_i += 1; );
L_i = 0;
loop(L_D, L_eB[L_i] = 1.0; L_i += 1; );
L_w = 0; L_head = 0; L_tail = 0; L_t = 0; L_ew = 0; L_eprev = 1.0; L_esum = L_D; L_chk = 0; L_fadeN = 0;
'''+ISP_INIT
LIM_INIT='''
// shared limiter core v7: 1.5 ms lookahead + 7 samples detector alignment, O(1) sliding minimum (monotonic deque), moving-average ramp, gated true-peak (16-tap Kaiser sinc, 4x)
L_D = max(2, min(500, floor(0.0015 * fs + 0.5)));
L_N = L_D + 1; L_cap = L_N + 1; L_NA = L_N + '''+str(LG)+''';
L_dlyL = 40000; L_dlyR = L_dlyL + L_NA; L_dqV = L_dlyR + L_NA; L_dqI = L_dqV + L_cap; L_eB = L_dqI + L_cap;
L_fadeLen = max(1, floor(0.05 * fs));
'''+LIM_CLEAR
LIM_S='''
  // ---- limiter core (input l,r; output spl0,spl1; needs ceilLin, rel_k) ----
'''+ISP('l','r')+'''  pk = max(max(abs(ia'''+str(LG)+'''), abs(ib'''+str(LG)+''')), isp_pk * '''+('%.3f'%GUARD_TP)+''');
  req = pk > ceilLin ? ceilLin / pk : 1.0;
  req = min(max(req, 0.0), 1.0);
  L_t += 1;
  while (L_tail > L_head && L_dqV[(L_tail - 1) % L_cap] >= req) ( L_tail -= 1; );
  L_dqV[L_tail % L_cap] = req; L_dqI[L_tail % L_cap] = L_t; L_tail += 1;
  while (L_dqI[L_head % L_cap] <= L_t - L_N) ( L_head += 1; );
  m = L_dqV[L_head % L_cap];
  L_dlyL[L_w] = l; L_dlyR[L_w] = r;
  rec = L_eprev + (1.0 - L_eprev) * rel_k;
  e = min(m, rec); L_eprev = e;
  L_esum += e - L_eB[L_ew]; L_eB[L_ew] = e; L_ew += 1; L_ew >= L_D ? ( L_ew = 0; );
  L_chk += 1;
  L_chk >= L_N * 8 ? ( L_i = 0; L_s = 0.0; loop(L_D, L_s += L_eB[L_i]; L_i += 1; ); L_esum = L_s; L_chk = 0; );
  g = min(1.0, L_esum / L_D);
  L_rp = L_w + 1; L_rp >= L_NA ? ( L_rp = 0; );
  L_fadeN < L_fadeLen ? ( L_fadeN += 1; fg = L_fadeN / L_fadeLen; ) : ( fg = 1.0; );
  spl0 = min(max(L_dlyL[L_rp] * g * fg, -ceilLin), ceilLin);
  spl1 = min(max(L_dlyR[L_rp] * g * fg, -ceilLin), ceilLin);
  L_w += 1; L_w >= L_NA ? ( L_w = 0; );
'''
GUARD='abs(spl0) < 1e6 ? 0 : (spl0 = 0.0);\nabs(spl1) < 1e6 ? 0 : (spl1 = 0.0);\n'
DCB='yl = l - dxL + dcR * dyL; dxL = l; dyL = yl; abs(dyL) < 1e-30 ? ( dyL = 0.0; ); l = yl;\nyr = r - dxR + dcR * dyR; dxR = r; dyR = yr; abs(dyR) < 1e-30 ? ( dyR = 0.0; ); r = yr;\n'
DCI='dcR = exp(-2.0 * $PI * 2.0 / fs); dxL = 0; dyL = 0; dxR = 0; dyR = 0;\n'
def common(pre,ceil,rel,cdef):
    return ('fs = srate > 0 ? srate : 48000;\npre_k = 1.0 - exp(-1.0 / (0.01 * fs)); preLin = 1.0; preTgt = 1.0; ceilLin = %.6f; rel_k = 0.001;\nprev_pre = -99999; prev_ceil = -99999; prev_rel = -99999;\n'%cdef)
def params(pre,ceil,rel):
    return '''(%s != prev_pre || %s != prev_ceil || %s != prev_rel) ? (
  prev_pre = %s; prev_ceil = %s; prev_rel = %s;
  preTgt = pow(10.0, %s / 200.0);
  ceilLin = pow(10.0, min(%s, -3) / 200.0);
  rel_k = 1.0 - exp(-1.0 / (max(%s, 10) * 0.001 * fs));
);
preLin += (preTgt - preLin) * pre_k;
'''%(pre,ceil,rel,pre,ceil,rel,pre,ceil,rel)
def ind(s,n='  '):return ''.join(n+x if x.strip() else x for x in s.splitlines(True))
def iem(desc,ceil,width):
    sl='preGain10:0<-120,60,1>Pre Gain tenths dB\nceilDb10:%d<-600,-3,1>Limiter Ceiling tenths dBFS\nrelMs:80<10,500,1>Limiter Release ms\n'%ceil
    ini='preGain10 = 0;\nceilDb10 = %d;\nrelMs = 80;\n'%ceil
    if width:sl+='spatialWidth:100<50,150,1>Binaural Width percent\n';ini+='spatialWidth = 100;\n'
    fe='mid = 0.5 * (l + r); side = 0.5 * (l - r) * spatialWidth * 0.01; l = mid + side; r = mid - side;\n' if width else ''
    return 'desc:%s\n//tags: iem limiter true-peak\n\n%s\n@init\n%s%s%s%s\n@sample\n%s%s\nl = spl0 * preLin;\nr = spl1 * preLin;\n%s%s\n'%(desc,sl,ini,common('preGain10','ceilDb10','relMs',10**(ceil/200)),DCI,LIM_INIT,params('preGain10','ceilDb10','relMs'),GUARD,DCB,fe)+LIM_S
def spk6():
    sl='master:1<0,1,1{Bypass,Protect}>Processing\ninputGain10:0<-120,60,1>Input Gain tenths dB\nceiling10:-30<-120,-3,1>Peak Ceiling tenths dBFS\nreleaseMs:80<20,300,1>Release ms\n'
    ini='master = 1;\ninputGain10 = 0;\nceiling10 = -30;\nreleaseMs = 80;\nprevMaster = 1;\n'
    return ('desc:HyperAudio Speaker Protection v6 v7\n//tags: speaker limiter true-peak\n\n'+sl+'\n@init\n'+ini+common('','','',10**(-30/200))+LIM_INIT+'\n@sample\n'+GUARD+
      'master == 0 ? (\n  prevMaster = 0;\n) : (\n  prevMaster == 0 ? (\n'+ind(LIM_CLEAR,'    ')+'    prevMaster = 1;\n  );\n'+ind(params('inputGain10','ceiling10','releaseMs'))+'  l = spl0 * preLin; r = spl1 * preLin;\n'+LIM_S+');\n')
def spk8():
    sl='master:1<0,1,1{Bypass,Cinema Spatial Active}>Cinema Engine\ninputGain10:0<-120,60,1>Input Gain tenths dB\ndialogueBoost:0<0,60,1>Center Dialogue Boost tenths dB\nsurroundWidth:130<80,180,1>Surround Stage Width percent\nceiling10:-20<-120,-3,1>Peak Ceiling tenths dBFS\nreleaseMs:80<20,300,1>Limiter Release ms\n'
    ini='master = 1;\ninputGain10 = 0;\ndialogueBoost = 0;\nsurroundWidth = 130;\nceiling10 = -20;\nreleaseMs = 80;\nprevMaster = 1; prev_dia = -99999; diaGain = 1.0;\n'
    return ('desc:HyperAudio Speaker Cinema Limiter v8 v7\n//tags: speaker cinema limiter true-peak\n\n'+sl+'\n@init\n'+ini+common('','','',10**(-20/200))+LIM_INIT+'\n@sample\n'+GUARD+
      'master == 0 ? (\n  prevMaster = 0;\n) : (\n  prevMaster == 0 ? (\n'+ind(LIM_CLEAR,'    ')+'    prevMaster = 1;\n  );\n'+ind(params('inputGain10','ceiling10','releaseMs'))+'  dialogueBoost != prev_dia ? ( prev_dia = dialogueBoost; diaGain = pow(10.0, dialogueBoost / 200.0); );\n  l = spl0 * preLin; r = spl1 * preLin;\n  mid = 0.5 * (l + r) * diaGain; side = 0.5 * (l - r) * surroundWidth * 0.01;\n  l = mid + side; r = mid - side;\n'+LIM_S+');\n')
def spk10():
    sl='mode:2<0,2,1{Bypass,Limiter Only,Dynamic Loudness}>Processing Mode\ninputGain10:0<-120,60,1>Input Gain tenths dB\ncompThresh:-20<-50,0,1>Dynamic Threshold dBFS\ncompRatio10:25<10,100,1>Compression Ratio x10\nmakeupDb:6<0,18,1>Loudness Makeup dB\nvBassMix:30<0,100,1>Virtual Bass Harmonics percent\nceiling10:-15<-60,-3,1>Peak Ceiling tenths dBFS\nreleaseMs:80<20,300,1>Limiter Release ms\n'
    ini='mode = 2;\ninputGain10 = 0;\ncompThresh = -20;\ncompRatio10 = 25;\nmakeupDb = 6;\nvBassMix = 30;\nceiling10 = -15;\nreleaseMs = 80;\nprevMode = 2;\n'+'''atkK = 1 - exp(-1 / (fs * 0.008)); relK = 1 - exp(-1 / (fs * 0.120)); holdK = exp(-1 / (fs * 0.020));
pkEnv = 0; compEnv = 0;
vb_w0 = 2 * $PI * 110 / fs; vb_alpha = sin(vb_w0) * 0.707;
vb_b0 = (1 - cos(vb_w0)) * 0.5; vb_b1 = 1 - cos(vb_w0); vb_b2 = vb_b0;
vb_a0 = 1 + vb_alpha; vb_a1 = -2 * cos(vb_w0); vb_a2 = 1 - vb_alpha;
vb_b0 /= vb_a0; vb_b1 /= vb_a0; vb_b2 /= vb_a0; vb_a1 /= -vb_a0; vb_a2 /= -vb_a0;
vb_xL1 = 0; vb_xL2 = 0; vb_yL1 = 0; vb_yL2 = 0; vb_xR1 = 0; vb_xR2 = 0; vb_yR1 = 0; vb_yR2 = 0;
hdc = exp(-2.0 * $PI * 20.0 / fs); hxL = 0; hyL = 0; hxR = 0; hyR = 0;
'''
    body='''  l = spl0 * preLin; r = spl1 * preLin;
  mode == 2 ? (
    subL = vb_b0 * l + vb_b1 * vb_xL1 + vb_b2 * vb_xL2 + vb_a1 * vb_yL1 + vb_a2 * vb_yL2;
    vb_xL2 = vb_xL1; vb_xL1 = l; vb_yL2 = vb_yL1; vb_yL1 = subL;
    subR = vb_b0 * r + vb_b1 * vb_xR1 + vb_b2 * vb_xR2 + vb_a1 * vb_yR1 + vb_a2 * vb_yR2;
    vb_xR2 = vb_xR1; vb_xR1 = r; vb_yR2 = vb_yR1; vb_yR1 = subR;
    qL = subL * subL * 3.0; qR = subR * subR * 3.0;
    hyL = qL - hxL + hdc * hyL; hxL = qL; abs(hyL) < 1e-30 ? ( hyL = 0.0; );
    hyR = qR - hxR + hdc * hyR; hxR = qR; abs(hyR) < 1e-30 ? ( hyR = 0.0; );
    l += hyL * vBassMix * 0.01; r += hyR * vBassMix * 0.01;
    pkEnv = max(max(abs(l), abs(r)), pkEnv * holdK);
    pkEnv > compEnv ? ( compEnv += (pkEnv - compEnv) * atkK; ) : ( compEnv += (pkEnv - compEnv) * relK; );
    compGain = 1.0;
    compEnv > 0.00001 ? (
      overDb = 20 * log10(compEnv) - compThresh;
      overDb > 0 ? ( compGain = pow(10, -overDb * (1.0 - 10.0 / compRatio10) / 20); );
    );
    abs(pkEnv) < 1e-20 ? ( pkEnv = 0; ); abs(compEnv) < 1e-20 ? ( compEnv = 0; );
    abs(vb_yL1) < 1e-20 ? ( vb_yL1 = 0; ); abs(vb_yL2) < 1e-20 ? ( vb_yL2 = 0; ); abs(vb_yR1) < 1e-20 ? ( vb_yR1 = 0; ); abs(vb_yR2) < 1e-20 ? ( vb_yR2 = 0; );
    mk = pow(10, makeupDb / 20);
    l *= compGain * mk; r *= compGain * mk;
  );
'''
    return ('desc:HyperAudio Speaker Dynamic Loudness v10 v7\n//tags: speaker loudness compressor bass limiter true-peak\n\n'+sl+'\n@init\n'+common('','','',10**(-15/200))+ini+LIM_INIT+'\n@sample\n'+GUARD+
      'mode == 0 ? (\n  prevMode = 0;\n) : (\n  prevMode == 0 ? (\n'+ind(LIM_CLEAR,'    ')+'    pkEnv = 0; compEnv = 0; hxL = 0; hyL = 0; hxR = 0; hyR = 0;\n    vb_xL1 = 0; vb_xL2 = 0; vb_yL1 = 0; vb_yL2 = 0; vb_xR1 = 0; vb_xR2 = 0; vb_yR1 = 0; vb_yR2 = 0;\n    prevMode = mode;\n  );\n'+ind(params('inputGain10','ceiling10','releaseMs'))+body+LIM_S+');\n')
import re
def post(t):
    return t.replace('\n@init\n','tpDetect:1<0,1,1{Off,On}>True Peak Detect\n\n@init\ntpDetect = 1;\n',1)
def hd():
    t=iem('HyperAudio IEM Engine v5 HD',-15,False)
    return t
if __name__=='__main__':
    import sys,os
    D=(sys.argv[1] if len(sys.argv)>1 else 'out_eel')+'/'
    [os.makedirs(D+q,exist_ok=True) for q in ('iem_hd','iem_v4','iem_v10','spk_v6','spk_v8','spk_v10')]
    open(D+'iem_hd/EDX_HD.eel','w').write(post(iem('HyperAudio IEM EDX HD v7',-15,False)))
    open(D+'iem_v4/EDX_v4.eel','w').write(post(iem('HyperAudio IEM EDX Spatial v4 v7',-5,True)))
    open(D+'iem_v10/EDX_v10.eel','w').write(post(iem('HyperAudio IEM EDX Reference v10 v7',-10,False)))
    open(D+'spk_v6/SPK_v6.eel','w').write(post(spk6()));open(D+'spk_v8/SPK_v8.eel','w').write(post(spk8()));open(D+'spk_v10/SPK_v10.eel','w').write(post(spk10()))
