#!/usr/bin/env python3
"""Generate brand assets (SVG with outlined text, PNG icons, ICO). Needs fontTools, Pillow, Playwright (Chromium) and Inter."""
import json,os,sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));R=ROOT+'/site'
VER=open(ROOT+'/VERSION').read().strip()
B=R+'/assets/brand';I=R+'/assets/icons'
F={w:TTFont(f'/usr/share/fonts/opentype/inter/Inter-{w}.otf') for w in('Bold','SemiBold','Medium')}
def text(s,x,y,size,w='Bold',track=0,fill='#fff',anchor='start',extra=''):
    f=F[w];gs=f.getGlyphSet();cm=f.getBestCmap();upm=f['head'].unitsPerEm;k=size/upm
    adv=[f['hmtx'][cm[ord(c)]][0]*k+track for c in s];tot=sum(adv)-track
    cx=x-(tot if anchor=='end' else tot/2 if anchor=='middle' else 0);d=''
    for c,a in zip(s,adv):
        p=SVGPathPen(gs);gs[cm[ord(c)]].draw(TransformPen(p,(k,0,0,-k,cx,y)));d+=p.getCommands();cx+=a
    return f'<path d="{d}" fill="{fill}" {extra}/>'
AMB='#f5b84b'
WAVES=['M3 8c2.2 0 2.2-2.5 4.5-2.5S9.8 8 12 8s2.2-2.5 4.5-2.5S18.8 8 21 8','M3 13c2.2 0 2.2-2.5 4.5-2.5S9.8 13 12 13s2.2-2.5 4.5-2.5S18.8 13 21 13','M3 18h18']
OP=[1,.7,.42]
def defs(i='a'):
    return f'''<linearGradient id="{i}g" gradientUnits="userSpaceOnUse" x1="3" y1="3" x2="21" y2="21"><stop offset="0" stop-color="#ffdca0"/><stop offset=".55" stop-color="{AMB}"/><stop offset="1" stop-color="#d98a14"/></linearGradient>
<linearGradient id="{i}t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1709"/><stop offset="1" stop-color="#070707"/></linearGradient>'''
def mark(x,y,s,i='a',tile=True,sw=2,pad=0):
    """mark in an s-sized box at x,y"""
    k=s/24;g=''
    if tile:g+=f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{s*.22:.1f}" fill="url(#{i}t)"/><rect x="{x+.5}" y="{y+.5}" width="{s-1}" height="{s-1}" rx="{s*.22-.5:.1f}" fill="none" stroke="#fff" stroke-opacity=".12"/>'
    q=k*(1-2*pad/24) if pad else k;o=x+(s-24*q)/2;oy=y+(s-24*q)/2
    g+=f'<g transform="translate({o:.2f} {oy:.2f}) scale({q:.4f})" fill="none" stroke="url(#{i}g)" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'+''.join(f'<path d="{p}" opacity="{o_}"/>' for p,o_ in zip(WAVES,OP))+'</g>'
    return g
def svg(w,h,body,d='',title='HyperAudio'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}"><title>{title}</title><defs>{d}</defs>{body}</svg>\n'
def w(p,s):open(p,'w').write(s)
# logos
w(B+'/logo-mark.svg',svg(512,512,mark(0,0,512),defs(),'HyperAudio mark'))
w(I+'/favicon.svg',svg(64,64,mark(0,0,64,sw=2.4),defs(),'HyperAudio'))
for n,c in(('logo','#f4f4f4'),('logo-light','#1c1b19')):
    b=mark(0,0,96)+text('HyperAudio',120,66,50,'Bold',-1.2,c)
    w(f'{B}/{n}.svg',svg(440,96,b,defs(),'HyperAudio'))
# curve from real data
D=json.load(open(R+'/data/profiles.json'));P=D['profiles'][0];fr=D['freq'];cv=P['curves']['correction']
import math
def curve(x0,x1,yc,amp,top,bot):
    X=lambda f:x0+(x1-x0)*(math.log10(f)-math.log10(20))/3;mx=max(abs(v) for v in cv);Y=lambda v:yc-v/mx*amp
    d='M'+' L'.join(f'{X(f):.1f} {Y(v):.1f}' for f,v in zip(fr,cv))
    return d,X,Y
def art(W,H):
    s=W/1280;b=f'<rect width="{W}" height="{H}" fill="#050505"/><rect width="{W}" height="{H}" fill="url(#bg1)"/><rect width="{W}" height="{H}" fill="url(#bg2)"/>'
    gx=''.join(f'<path d="M{x} 0V{H}" />' for x in range(0,W+1,80));gy=''.join(f'<path d="M0 {y}H{W}"/>' for y in range(0,H+1,80))
    b+=f'<g stroke="#fff" stroke-opacity=".035" fill="none">{gx}{gy}</g>'
    x0,x1=80*s,W-80*s;yc=H*.80;d_,X,Y=curve(x0,x1,yc,H*.135,0,0)
    b+=f'<path d="{d_} L{x1:.1f} {yc:.1f} L{x0:.1f} {yc:.1f}Z" fill="url(#ar)"/><path d="{d_}" fill="none" stroke="{AMB}" stroke-opacity=".18" stroke-width="{14*s:.1f}" stroke-linecap="round" stroke-linejoin="round"/><path d="{d_}" fill="none" stroke="url(#cg)" stroke-width="{3.4*s:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
    b+=f'<path d="M{x0:.0f} {yc:.0f}H{x1:.0f}" stroke="#fff" stroke-opacity=".12" stroke-dasharray="3 7"/>'
    for f,t in((20,'20 Hz'),(100,'100'),(1000,'1k'),(10000,'10k'),(20000,'20k')):
        b+=text(t,X(f),H-26*s,15*s,'Medium',.6*s,'#8f8f8f','start' if f==20 else 'end' if f==20000 else 'middle')
    b+=mark(80*s,64*s,84*s,'a')
    b+=text('HyperAudio',76*s,H*.40,92*s,'Bold',-2.4*s,'#f6f6f6')
    b+=text('Calibrated DSP profiles for RootlessJamesDSP',80*s,H*.40+58*s,32*s,'Medium',-.2*s,'#b9b3a6')
    cx=80*s;cy=H*.40+100*s
    for t in('VDC','IMPULSE RESPONSE','LIVEPROG'):
        tw=sum(F['SemiBold']['hmtx'][F['SemiBold'].getBestCmap()[ord(c)]][0] for c in t)*14*s/F['SemiBold']['head'].unitsPerEm+1.4*s*len(t)+36*s
        b+=f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{tw:.1f}" height="{38*s:.1f}" rx="{19*s:.1f}" fill="#fff" fill-opacity=".05" stroke="{AMB}" stroke-opacity=".45"/>'+text(t,cx+tw/2,cy+25*s,14*s,'SemiBold',1.4*s,AMB,'middle');cx+=tw+12*s
    b+=text('v'+VER,W-80*s,64*s+34*s,22*s,'SemiBold',1*s,AMB,'end')+text('KZ EDX PRO  ·  REDMI 12',W-80*s,64*s+62*s,15*s,'Medium',1.6*s,'#8f8f8f','end')
    d=f'''<radialGradient id="bg1" cx=".12" cy=".05" r=".8"><stop offset="0" stop-color="{AMB}" stop-opacity=".16"/><stop offset="1" stop-color="{AMB}" stop-opacity="0"/></radialGradient>
<radialGradient id="bg2" cx=".95" cy="1" r=".7"><stop offset="0" stop-color="#7a4cff" stop-opacity=".10"/><stop offset="1" stop-color="#7a4cff" stop-opacity="0"/></radialGradient>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMB}" stop-opacity=".30"/><stop offset="1" stop-color="{AMB}" stop-opacity="0"/></linearGradient>
<linearGradient id="cg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffdca0"/><stop offset=".6" stop-color="{AMB}"/><stop offset="1" stop-color="#e59a20"/></linearGradient>'''+defs()
    return svg(W,H,b,d,'HyperAudio: calibrated DSP profiles for RootlessJamesDSP')
w(ROOT+'/.github/github-cover.svg',art(1280,640));w(B+'/og-image.svg',art(1200,630))
# maskable: full-bleed tile, mark in safe zone
mk=f'<rect width="512" height="512" fill="url(#at)"/>'+mark(0,0,512,tile=False,pad=2.4,sw=2.2)
w(I+'/maskable.svg',svg(512,512,mk,defs(),'HyperAudio'))
# rasterise
from playwright.sync_api import sync_playwright
jobs=[(ROOT+'/.github/github-cover.svg',ROOT+'/.github/github-cover.png',1280,640),(B+'/og-image.svg',B+'/og-image.png',1200,630),(B+'/logo-mark.svg',I+'/icon-512.png',512,512),(B+'/logo-mark.svg',I+'/icon-192.png',192,192),(I+'/maskable.svg',I+'/maskable-512.png',512,512),(I+'/maskable.svg',I+'/apple-touch-icon.png',180,180),(I+'/favicon.svg',I+'/favicon-32.png',32,32),(I+'/favicon.svg',I+'/favicon-48.png',48,48)]
import tempfile;T=tempfile.mkdtemp()
with sync_playwright() as p:
    br=p.chromium.launch();pg=br.new_page()
    for s,o,ww,hh in jobs:
        pg.set_viewport_size({'width':ww,'height':hh});open(T+'/_t.html','w').write(f'<body style="margin:0"><img src="{s}" width={ww} height={hh} style="display:block">');pg.goto('file://'+T+'/_t.html');pg.wait_for_timeout(150);pg.screenshot(path=o,omit_background=True)
    br.close()
# apple-touch: opaque, no transparent corners (iOS rounds itself)
im=Image.open(I+'/apple-touch-icon.png').convert('RGB');im.save(I+'/apple-touch-icon.png')
Image.open(I+'/favicon-48.png').convert('RGBA').save(R+'/favicon.ico',sizes=[(48,48),(32,32),(16,16)])
os.remove(T+'/_t.html');print('ok')
