const fs=require('fs'),[a,b]=process.argv.slice(2).map(f=>fs.readFileSync(f,'utf8'));
let ac=null;try{ac=require('internal/deps/acorn/acorn/dist/acorn')}catch(e){}
try{new (require('vm').Script)(b)}catch(e){console.log('syntax: '+e.message);process.exit(1)}
if(!ac){console.log('syntax-only');process.exit(0)}
const tok=s=>{const o=[];for(const t of ac.tokenizer(s,{ecmaVersion:'latest',sourceType:'script'})){const v=t.type.label==='regexp'?t.value.pattern+'/'+t.value.flags:t.value;o.push(t.type.label+'\0'+(v===undefined?'':String(v)))}return o};
const x=tok(a),y=tok(b);
if(x.length!==y.length||x.some((v,i)=>v!==y[i])){console.log('token mismatch');process.exit(1)}
console.log('tokens '+x.length+' equal');
