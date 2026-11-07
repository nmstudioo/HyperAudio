const {chromium}=require('playwright');let axe=null;try{axe=require('axe-core')}catch(e){}
const base=process.argv[2]||'http://localhost:8765/';
const pages=['index.html','compare.html','finder.html','archive.html','changelog.html','docs/index.html','docs/EVIDENCE.html','docs/OPEN.html','docs/CHANGELOG.html'];
(async()=>{const b=await chromium.launch();let bad=0;
for(const th of['dark','light'])for(const w of[375,1280]){
const c=await b.newContext({viewport:{width:w,height:900}});await c.addInitScript(t=>{try{localStorage.setItem('ha-theme',t)}catch(e){}},th);
for(const pg of pages){const p=await c.newPage();await p.goto(base+pg);await p.waitForTimeout(600);
const r=await p.evaluate(()=>{const o=[],name=e=>(e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')||e.textContent||e.getAttribute('title')||(e.querySelector('img[alt]')||{}).alt||'').trim();
if(!document.documentElement.lang)o.push('html lang missing');if(!document.title.trim())o.push('title missing');
if(document.querySelectorAll('main,[role=main]').length!==1)o.push('expected exactly one main landmark');
if(document.querySelectorAll('h1').length!==1)o.push('expected exactly one h1, found '+document.querySelectorAll('h1').length);
document.querySelectorAll('img:not([alt])').forEach(e=>o.push('img without alt '+(e.getAttribute('src')||'')));
document.querySelectorAll('button,a[href],summary,[role=button]').forEach(e=>{const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||e.closest('[hidden]'))return;if(!name(e))o.push('no accessible name: '+e.outerHTML.slice(0,70))});
document.querySelectorAll('input:not([type=hidden]),select,textarea').forEach(e=>{if(!(e.labels&&e.labels.length)&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby'))o.push('unlabelled control '+e.outerHTML.slice(0,60))});
const ids={};document.querySelectorAll('[id]').forEach(e=>ids[e.id]=(ids[e.id]||0)+1);Object.keys(ids).filter(k=>ids[k]>1).forEach(k=>o.push('duplicate id '+k));
document.querySelectorAll('[aria-labelledby],[aria-describedby]').forEach(e=>(e.getAttribute('aria-labelledby')||e.getAttribute('aria-describedby')).split(/\s+/).forEach(i=>{if(!document.getElementById(i))o.push('aria ref to missing id '+i)}));
return o});
let ax=[];if(axe){await p.addScriptTag({content:axe.source});ax=await p.evaluate(async()=>(await axe.run(document,{runOnly:['wcag2a','wcag2aa']})).violations.map(v=>v.id+' ('+v.nodes.length+') on '+JSON.stringify(v.nodes.map(n=>n.target))))}
const all=[...new Set([...r,...ax.map(x=>'axe: '+x)])];if(all.length){bad++;console.log('A11Y',pg,w,th,'\n  '+all.slice(0,6).join('\n  '))}
await p.close()}
await c.close()}
await b.close();console.log(bad?bad+' page run(s) with problems':'a11y ok'+(axe?' (builtin + axe)':' (builtin only; install axe-core for the full gate)'));process.exit(bad?1:0)})()
