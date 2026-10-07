/* HyperAudio © 2026 Noushad M. All rights reserved. */
(function(){'use strict';
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
let key='EDX_HARMAN_REFERENCE',fs=48000;
const fmtF=f=>f>=1000?(f/1000).toFixed(2).replace(/\.?0+$/,'')+' kHz':Math.round(f)+' Hz';
const isSpk=p=>deviceOf(p)==='spk';
const rawFor=p=>isSpk(p)?STATE.spkRaw:STATE.kzRaw;
const sum=a=>a.reduce((s,p)=>s+p[1],0);
const dataSig=()=>[STATE.target.length,sum(STATE.target),STATE.kzRaw.length,sum(STATE.kzRaw),STATE.spkRaw.length,sum(STATE.spkRaw)].join('|');
const presetSig=p=>JSON.stringify(p.filters)+p.preampPolicy.appliedPreampDb;
/* ---------- memoized engine calls ---------- */
const curveC=new Map();
let lastSig='';
function audit(k,rate){try{return auditPreset(allPresets()[k],rate)}catch(e){return{error:e.message,pass:false}}}
function curves(k){const p=allPresets()[k],c=k+'|'+fs+'|'+presetSig(p)+'|'+dataSig();if(!curveC.has(c)){const raw=rawFor(p),r1=interpLog(raw,1000),f1k=filterChainDb(1000,p.filters,fs,0),t1=interpLog(STATE.target,1000),o={raw:[],tgt:[],flt:[],cor:[]};
 for(let i=0;i<260;i++){const f=20*Math.pow(1000,i/259),fl=filterChainDb(f,p.filters,fs,0)-f1k,rw=interpLog(raw,f)-r1;o.raw.push([f,rw]);o.tgt.push([f,interpLog(STATE.target,f)-t1]);o.flt.push([f,fl]);o.cor.push([f,rw+fl])}
 if(curveC.size>24)curveC.clear();curveC.set(c,o)}return curveC.get(c)}
function why(a,p){if(a.error)return a.error;const g=[];if(a.nan||a.inf)g.push('non-finite samples');if(a.peakDb>0)g.push('peak above 0 dBFS');if(a.tailRms>TAIL_RMS_LIMIT_DB)g.push('tail RMS '+a.tailRms.toFixed(1)+' dBFS');if(a.tailPeak>TAIL_PEAK_LIMIT_DB)g.push('tail peak '+a.tailPeak.toFixed(1)+' dBFS');if(a.maxDelta>IIR_FIR_TOLERANCE_DB)g.push('IIR/FIR '+a.maxDelta.toFixed(3)+' dB');if(!a.headroom)g.push('headroom margin '+a.marginDb.toFixed(3)+' dB < required '+a.safetyDb.toFixed(3)+' dB');return g.join('; ')}
/* ---------- feedback ---------- */
const timers=new WeakMap();
function flash(btn,txt){const t=btn.querySelector('.lbl')||btn;if(!timers.has(btn))btn.dataset.orig=t.textContent;else clearTimeout(timers.get(btn));t.textContent=txt;btn.dataset.state='done';timers.set(btn,setTimeout(()=>{t.textContent=btn.dataset.orig;delete btn.dataset.state;timers.delete(btn)},1600))}
function clip(txt,btn){copyText(txt).then(ok=>{if(ok){toast('Copied to clipboard');flash(btn,'Copied')}else toast('Copy blocked by the browser. Select the text under Filter exports and copy manually.')})}
/* ---------- chart ---------- */
const SER=[['raw','Raw measurement','var(--mut)','',1.4],['tgt','Target','var(--emerald)','5 4',1.5],['flt','Filter chain (norm.)','var(--blue)','',1.6],['cor','Raw + filters','var(--violet)','',2.4]];
const host=$('#wsChart');let hid={},pts,S;
function chart(){const p=allPresets()[key];if(!p||!host.clientWidth)return;pts=curves(key);const W=Math.max(280,host.clientWidth-16),H=Math.round(Math.max(240,Math.min(460,W*.46))),m={l:40,r:12,t:12,b:34};
 let lo=1e9,hi=-1e9;SER.forEach(s=>{if(!hid[s[0]])pts[s[0]].forEach(q=>{lo=Math.min(lo,q[1]);hi=Math.max(hi,q[1])})});if(lo>hi){lo=-10;hi=10}
 const st=hi-lo>40?10:5,y0=Math.floor((lo-1)/st)*st,y1=Math.ceil((hi+1)/st)*st,L=Math.log10,X=v=>m.l+(L(v)-L(20))/3*(W-m.l-m.r),Y=v=>m.t+(y1-v)/(y1-y0)*(H-m.t-m.b);S={X,W,H,m};
 let g='';for(let v=y0;v<=y1;v+=st)g+=`<line x1="${m.l}" x2="${W-m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="${v===0?'var(--bd2)':'var(--bd)'}" stroke-width="${v===0?1.5:1}"/><text x="${m.l-6}" y="${Y(v)+4}" text-anchor="end" font-size="12" fill="var(--mut)">${v}</text>`;
 [20,50,100,200,500,1e3,2e3,5e3,1e4,2e4].forEach(v=>g+=`<line y1="${m.t}" y2="${H-m.b}" x1="${X(v)}" x2="${X(v)}" stroke="var(--bd)"/><text x="${X(v)}" y="${H-18}" text-anchor="middle" font-size="12" fill="var(--mut)">${v>=1e3?v/1e3+'k':v}</text>`);
 g+=`<text x="${m.l}" y="${H-3}" font-size="12" fill="var(--mut)">Hz (log) · dB relative to 1 kHz</text>`;
 SER.forEach(s=>{if(hid[s[0]])return;g+=`<path d="${pts[s[0]].map((q,i)=>(i?'L':'M')+X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1)).join('')}" fill="none" stroke="${s[2]}" stroke-width="${s[4]}" ${s[3]?`stroke-dasharray="${s[3]}"`:''} stroke-linejoin="round" stroke-linecap="round"/>`});
 p.filters.forEach(f=>{if(f.fc>=20&&f.fc<=2e4)g+=`<path d="M${X(f.fc)} ${H-m.b} l-4 -7 h8z" fill="var(--violet)" opacity=".8"/>`});
 g+=`<line id="cur" y1="${m.t}" y2="${H-m.b}" stroke="var(--tx2)" stroke-dasharray="3 3" style="display:none"/>`;
 host.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Frequency response of ${p.name} at ${fs} Hz">${g}</svg><div class="tip" aria-hidden="true"></div>`;
 $('#wsLegend').innerHTML=SER.map(s=>`<label><input type="checkbox" data-s="${s[0]}" ${hid[s[0]]?'':'checked'}><i style="background:${s[2]}"></i>${s[1]}</label>`).join('')+'<span class="muted-xs" style="align-self:center">▲ filter centers</span>';
 const c=pts.cor;let mx=c[0],mn=c[0];c.forEach(q=>{if(q[1]>mx[1])mx=q;if(q[1]<mn[1])mn=q});$('#wsSum').textContent=`${p.name}, ${fs} Hz: raw plus filters peaks at ${mx[1].toFixed(1)} dB near ${fmtF(mx[0])} and dips to ${mn[1].toFixed(1)} dB near ${fmtF(mn[0])}.`}
function at(f){if(!S||!pts)return;const tip=$('.tip',host),cur=$('#cur',host),i=Math.min(259,Math.max(0,Math.round(Math.log10(f/20)/3*259))),x=S.X(f);
 tip.innerHTML=`<b>${fmtF(f)}</b>`+SER.filter(s=>!hid[s[0]]).map(s=>`<div><span style="color:${s[2]}">${s[1]}</span><b>${pts[s[0]][i][1].toFixed(1)} dB</b></div>`).join('');tip.style.display='block';const w=tip.offsetWidth;tip.style.left=Math.min(Math.max(4,x/S.W*host.clientWidth-w/2),host.clientWidth-w-4)+'px';cur.setAttribute('x1',x);cur.setAttribute('x2',x);cur.style.display='';host._f=f}
const hide=()=>{const t=$('.tip',host),c=$('#cur',host);if(t)t.style.display='none';if(c)c.style.display='none'};
function ptr(e){const sv=$('svg',host);if(!sv)return;const r=sv.getBoundingClientRect(),x=(e.clientX-r.left)*S.W/r.width;at(20*Math.pow(1000,Math.min(1,Math.max(0,(x-S.m.l)/(S.W-S.m.l-S.m.r)))))}
host.addEventListener('pointermove',ptr);host.addEventListener('pointerdown',ptr);host.addEventListener('pointerleave',hide);host.addEventListener('blur',hide);
host.addEventListener('keydown',e=>{if(e.key==='Escape'){hide();return}if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();at(Math.min(2e4,Math.max(20,(host._f||1e3)*Math.pow(2,e.key==='ArrowLeft'?-.15:.15))))});
$('#wsLegend').addEventListener('change',e=>{if(e.target.dataset.s){hid[e.target.dataset.s]=!e.target.checked;chart()}});
let rz=0;new ResizeObserver(()=>{cancelAnimationFrame(rz);rz=requestAnimationFrame(chart)}).observe(host);
/* ---------- workspace ---------- */
const PDESC={EDX_STUDIO_NEUTRAL:['Neutral','Flat, studio-style monitoring.'],EDX_HARMAN_REFERENCE:['Reference','Harman IE 2019 calibration baseline.'],AUTOEQ_CRINACLE_HARMAN:['Comparison','10-band AutoEQ baseline to compare against.'],EDX_WARM_BASS:['Warm','Extra low-end warmth.'],EDX_NIGHT_RELAXED:['Night','Softer treble for long sessions.'],REDMI12_SPEAKER:['Phone speaker','Protects and corrects the loudspeaker.']};
const ic=(n,c)=>'<svg class="ic'+(c?' '+c:'')+'" aria-hidden="true"><use href="#i-'+n+'"/></svg>';
const CHECKS=[['finite','Finite samples (no NaN or Inf)'],['peak','Peak at or below 0 dBFS'],['tail','Impulse tail has decayed'],['iirFir','FIR matches the intended filters'],['headroom','Headroom margin met']];
const eelFile=p=>isSpk(p)?N.eelSpk:N.eelIem;
const ddcFile=p=>isSpk(p)?N.vdcSpk:N.vdcIem;
const eelKey=eelFile;
const ceilOf=p=>CEIL[deviceOf(p)];
function setLbl(btn,label,fn){$('.lbl',btn).textContent=label;if(fn!==undefined)$('.fn',btn).textContent=fn;btn.dataset.orig=''}
const spkC=new Map();
function spark(p){const c=presetSig(p);let d=spkC.get(c);if(!d){const f1=filterChainDb(1000,p.filters,48000,0),n=48;d='';for(let i=0;i<n;i++){const f=20*Math.pow(1000,i/(n-1)),v=Math.max(-12,Math.min(12,filterChainDb(f,p.filters,48000,0)-f1));d+=(i?'L':'M')+(i*120/(n-1)).toFixed(1)+' '+(16-v*14/12).toFixed(1)}if(spkC.size>40)spkC.clear();spkC.set(c,d)}return '<svg class="spark" viewBox="0 0 120 32" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="'+d+'"/></svg>'}
function limbar(p,a){const box=$('#wsLim');if(a.error){box.innerHTML='';return}
 const ce=ceilOf(p),pk=a.respPeakDb,en=limiterEngagesAboveDbfs(p,a),v=[pk,ce,en],lo=Math.min(-3,Math.floor(Math.min(...v)-1)),hi=Math.max(1,Math.ceil(Math.max(...v)+.5)),X=x=>Math.max(0,Math.min(100,(x-lo)/(hi-lo)*100)).toFixed(1)+'%';
 const rows=[['IR peak',pk,'var(--blue)'],['Ceiling',ce,'var(--amber)'],['Limiter engages',en,'var(--violet)']];
 box.innerHTML=rows.map(r=>'<div class="lim-r"><span>'+r[0]+'</span><div class="lim-t" aria-hidden="true"><i style="width:'+X(r[1])+';--c:'+r[2]+'"></i><em style="left:'+X(0)+'"></em></div><b>'+r[1].toFixed(3)+' dBFS</b></div>').join('')+'<p class="meta">Scale '+lo+' to '+hi+' dBFS; the vertical line marks 0 dBFS.</p>'}
function qaSummary(p,a,b){const box=$('#qaSummary');if(a.error){box.innerHTML='<p class="status" data-k="err">'+ic('warn')+'<span>Quality check could not run: '+a.error+'</span></p>';return}
 const prev=$('details',box),all=a.pass&&EEL_OK,open=!all||(prev&&prev.open);
 const row=(k,t)=>{const ok=a.checks[k],det=k==='iirFir'?' ('+a.maxDelta.toFixed(3)+' dB max)':k==='headroom'?' ('+a.marginDb.toFixed(3)+' dB, needs ≥ '+a.safetyDb.toFixed(3)+')':'';return '<li class="'+(ok?'ok':'bad')+'">'+ic(ok?'check':'warn','sm')+'<span>'+t+det+'</span><span class="r">'+(ok?'Pass':'Fail')+'</span></li>'};
 const lim='<li class="'+(EEL_OK?'ok':'bad')+'">'+ic(EEL_OK?'check':'warn','sm')+'<span>Limiter engages above '+limiterEngagesAboveDbfs(p,a).toFixed(3)+' dBFS (fixed ceiling '+ceilOf(p).toFixed(1)+' dBFS)</span><span class="r">'+(EEL_OK?'Pass':'Fail')+'</span></li>';
 const other=b.error?'could not run':(b.pass?'Pass':'Fail: '+why(b,p));
 box.innerHTML='<p class="status" data-k="'+(all?'ok':'err')+'"><b>'+ic(all?'check':'warn')+' '+p.name+' · '+fs/1000+' kHz: '+(all?'PASS':'FAIL')+'</b></p><p class="meta">'+(fs===48000?'44.1':'48')+' kHz: '+other+(a.pass?'':' · '+why(a,p))+'</p><details class="plain"'+(open?' open':'')+'><summary>'+ic('qa','sm')+'Details ('+(CHECKS.length+1)+' checks)'+ic('chev','sm chev')+'</summary><ul class="checks mt">'+CHECKS.map(c=>row(c[0],c[1])).join('')+lim+'</ul></details>'}
function workspace(){const all=allPresets();if(!all[key])key='EDX_HARMAN_REFERENCE';const p=all[key],ap=p.preampPolicy.appliedPreampDb,a=audit(key,fs),b=audit(key,fs===48000?44100:48000),tag=fs===48000?'48k':'44k',fname=sanitizeName(p.filenameBase+' '+tag+'.wav');
 const box=$('#profiles'),had=box.contains(document.activeElement);
 box.innerHTML=Object.keys(all).map(k=>{const q=all[k],on=k===key,d=PDESC[k]||['Fitted','Generated from your measurement in this session.'];return '<button class="pcard" type="button" data-k="'+k+'" aria-pressed="'+on+'"><span class="pc-head">'+ic(isSpk(q)?'speaker':'headphones','sm')+'<span class="pc-tag">'+d[0]+'</span><span class="pc-sel">'+(on?ic('check','sm')+'Selected':'')+'</span></span><span class="pc-name">'+q.name+'</span><span class="pc-desc">'+d[1]+'</span>'+spark(q)+'<span class="pc-meta">'+(isSpk(q)?'Redmi 12 speaker':'KZ EDX Pro')+' · '+q.filters.length+' filters</span></button>'}).join('');
 if(had){const cur=$('.pcard[data-k="'+key+'"]',box);cur&&cur.focus({preventScroll:true})}
 $('#wsBadge').textContent=p.preampPolicy.mode==='autoeq_fitted'?'Fitted this session':'Embedded preset';
 const st=a.error?'—':ic(a.pass?'check':'warn','sm')+' '+(a.pass?'PASS':'FAIL');
 $('#wsStats').innerHTML=[['Output',isSpk(p)?'Redmi 12 loudspeaker':'KZ EDX Pro',''],['Filters',p.filters.length,''],['Applied preamp',ap.toFixed(3)+' dB','included in the impulse'],['Headroom, '+fs/1000+' kHz',a.error?'—':a.marginDb.toFixed(3)+' dB','required '+(a.error?'—':a.safetyDb.toFixed(3))+' dB'],['Limiter engages above',a.error?'—':limiterEngagesAboveDbfs(p,a).toFixed(3)+' dBFS','fixed ceiling '+ceilOf(p).toFixed(1)+' dBFS'],['Browser QA, '+fs/1000+' kHz',st,a.pass||a.error?'all checks passed':why(a,p)]].map(x=>'<div><span>'+x[0]+'</span><b>'+x[1]+'</b>'+(x[2]?'<small>'+x[2]+'</small>':'')+'</div>').join('');
 $('#wsFcount').textContent=p.filters.length;
 $('#wsFilters').innerHTML=p.filters.map((f,i)=>'<tr><td>'+(i+1)+'</td><td>'+f.type.toUpperCase()+'</td><td>'+f.fc.toFixed(f.fc%1?1:0)+'</td><td>'+(f.g===undefined?'—':(f.g>=0?'+':'')+f.g.toFixed(2))+'</td><td>'+(f.q||.70710678).toFixed(2)+'</td></tr>').join('');
 const w=$('#wsWav');w.setAttribute('aria-disabled',a.pass?'false':'true');setLbl(w,a.pass?'Download impulse response':'Download blocked',a.pass?fname+' · '+fs/1000+' kHz · Float32 stereo · 8192 taps':(a.error?a.error:why(a,p)));
 const e=$('#wsEel');setLbl(e,'Download Liveprog script',eelFile(p));
 const dd=$('#wsDdc');setLbl(dd,'Download Viper DDC',ddcFile(p));
 const al=$('#wsAll'),ab=$('#wsAllBar'),okA=a.pass;[al,ab].forEach(x=>x.setAttribute('aria-disabled',okA?'false':'true'));setLbl(al,okA?'Download all':'Download blocked',okA?'Impulse, script and DDC · '+fs/1000+' kHz':(a.error?a.error:why(a,p)));setLbl(ab,okA?'Download all':'Download blocked');
 $$('#fsSeg button,#fsSegBar button').forEach(x=>x.setAttribute('aria-pressed',+x.dataset.fs===fs));
 qaSummary(p,a,b);limbar(p,a);chart();deploy(p,tag,a)}
function deploy(p,tag,a){
 const d=[['Profile',p.name+' — '+p.classification+(a.pass?'':' <b class="rose">Downloads blocked: QA failed</b>')],['Chain order','Convolver impulse, then Liveprog script. The impulse does the EQ; the script does dynamics and safety.'],['DDC','Load the .vdc in the DDC slot.'],['Preamp',p.preampPolicy.appliedPreampDb.toFixed(3)+' dB, included in the impulse response'],['Limiter',a.error?'—':'engages above '+limiterEngagesAboveDbfs(p,a).toFixed(3)+' dBFS · fixed ceiling '+ceilOf(p).toFixed(1)+' dBFS'],['Host sample rate',(fs/1000)+' kHz, to match the impulse']];
 $('#deployBody').innerHTML='<table class="kv"><tbody>'+d.map(r=>'<tr><th scope="row">'+r[0]+'</th><td>'+r[1]+'</td></tr>').join('')+'</tbody></table>'}
/* ---------- export flow: real state transitions, no fake progress ---------- */
let busy=false;
function setStatus(k,txt){const el=$('#exportStatus');el.dataset.k=k;el.innerHTML=txt?ic(k==='ok'?'check':k==='err'?'warn':'info','sm')+'<span></span>':'';if(txt)el.lastChild.textContent=txt}
async function exportFlow(btn,what,fn,detail,local){if(busy)return;if(btn.getAttribute('aria-disabled')==='true'){setStatus('err',$('.fn',btn)?$('.fn',btn).textContent:'Download blocked.');return}
 busy=true;btn.setAttribute('aria-busy','true');const lbl=$('.lbl',btn),old=lbl.textContent;lbl.textContent='Generating…';if(!local)setStatus('busy','Generating '+what+'…');
 await new Promise(r=>requestAnimationFrame(()=>setTimeout(r,0)));
 let r;try{r=fn()}catch(e){r={ok:false,message:'Export failed: '+e.message}}
 busy=false;btn.removeAttribute('aria-busy');lbl.textContent=old;
 if(r&&r.ok){if(!local)setStatus('ok','Downloaded '+r.filename+(detail?' · '+detail:''));btn.dataset.state='done';lbl.textContent='Downloaded';setTimeout(()=>{lbl.textContent=old;delete btn.dataset.state},1600)}
 else if(!local)setStatus('err',(r&&r.message)||'Export failed.')}
$('#profiles').addEventListener('click',e=>{const b=e.target.closest('.pcard');if(b&&b.dataset.k!==key){key=b.dataset.k;setStatus('idle','');workspace()}});
$$('#fsSeg,#fsSegBar').forEach(sg=>sg.addEventListener('click',e=>{const b=e.target.closest('button');if(b&&+b.dataset.fs!==fs){fs=+b.dataset.fs;setStatus('idle','');workspace()}}));
$('#wsWav').addEventListener('click',e=>exportFlow(e.currentTarget,'impulse response',()=>exportWAV(key,fs),fs/1000+' kHz · Float32 stereo · 8192 taps'));
$('#wsEel').addEventListener('click',e=>{const p=allPresets()[key];exportFlow(e.currentTarget,'script',()=>exportEEL(eelKey(p),eelFile(p)),'EEL2 Liveprog script')});
$('#wsDdc').addEventListener('click',e=>{const p=allPresets()[key];exportFlow(e.currentTarget,'DDC file',()=>exportEEL(ddcFile(p),ddcFile(p)),'Viper DDC')});
const allFn=()=>{const p=allPresets()[key],r=exportWAV(key,fs);if(!r.ok)return r;setTimeout(()=>exportEEL(eelKey(p),eelFile(p)),400);setTimeout(()=>exportEEL(ddcFile(p),ddcFile(p)),800);return{ok:true,filename:'3 files'}};
['#wsAll','#wsAllBar'].forEach(q=>$(q).addEventListener('click',e=>exportFlow(e.currentTarget,'kit',allFn,'impulse, script and DDC')));
$('#wsPeq').addEventListener('click',e=>clip(peqText(allPresets()[key]),e.currentTarget));
$('#wsGeq').addEventListener('click',e=>clip(geqText(allPresets()[key],fs),e.currentTarget));
/* ---------- EEL / DDC metadata from file contents ---------- */
function fillMeta(){$$('.btn[data-k]').forEach(b=>{const k=b.dataset.k,t=EEL[k];
 if(t===undefined){$('.sub',b).textContent='Viper DDC · 44.1 and 48 kHz coefficient sets';return}
 const m=re=>(t.match(re)||[])[1],d=m(/^desc:\s*(.+)$/m)||'',g=m(/^\/\/tags:\s*(.+)$/m)||'',c=m(/^limCeilDb\s*=\s*(-?[\d.]+)/m),r=m(/^limRelMs\s*=\s*([\d.]+)/m);
 const facts=[c&&'ceiling '+(+c).toFixed(1)+' dBFS',r&&'release '+Math.round(+r)+' ms'].filter(Boolean).join(' · ');
 $('.sub',b).textContent=d+(facts?' — '+facts:'')+(g?' ['+g+']':'')});}
UI_HOOKS.assets=fillMeta;
$('#scripts').addEventListener('click',e=>{const b=e.target.closest('.btn[data-k]');if(b)exportFlow(b,'script',()=>exportEEL(b.dataset.k,b.dataset.file),'',true)});
/* ---------- engine hooks (render-only) ---------- */
function labelCells(){$$('#reg tr').forEach(tr=>$$('td',tr).forEach((td,i)=>td.dataset.l=['Preset','Class','Filter peak (48k)','Calc min pre','Applied pre','Margin (48/44.1)','IIR↔FIR Δ'][i]))}
UI_HOOKS.registry=labelCells;UI_HOOKS.flash=flash;
UI_HOOKS.badge=function(){const t=$('#qa_badge'),q=$('#hdrQA'),bad=t.classList.contains('b-rose');q.textContent=bad?'QA: FAIL':'QA: PASS';q.dataset.s=bad?'fail':'pass';q.setAttribute('aria-label',t.textContent+'. Go to quality checks');q.style.color=bad?'var(--rose)':'var(--emerald)';workspace()};
UI_HOOKS.data=function(){const s=dataSig();if(s!==lastSig){lastSig=s;chart()}};
/* ---------- theme + nav ---------- */
$('#themeBtn').onclick=e=>{const d=document.documentElement,l=d.dataset.theme==='dark';d.dataset.theme=l?'light':'dark';e.currentTarget.setAttribute('aria-pressed',l);e.currentTarget.setAttribute('aria-label',l?'Switch to dark theme':'Switch to light theme');chart()};
const links=$$('nav a'),navList=$('nav ul');
links.forEach(a=>a.addEventListener('click',()=>{const t=$(a.getAttribute('href'));if(t&&t.tagName==='DETAILS')t.open=true}));
const io=new IntersectionObserver(es=>es.forEach(en=>{if(!en.isIntersecting)return;links.forEach(a=>{const on=a.getAttribute('href')==='#'+en.target.id;if(on)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');
 if(on&&navList.scrollWidth>navList.clientWidth){const r=a.getBoundingClientRect(),nr=navList.getBoundingClientRect();navList.scrollLeft+=(r.left+r.width/2)-(nr.left+nr.width/2)}})}),{rootMargin:'-20% 0px -65% 0px'});
links.forEach(a=>{const t=$(a.getAttribute('href'));t&&io.observe(t)});
$('#fitter').addEventListener('toggle',e=>{if(e.currentTarget.open)drawFitCanvas()});
})();
