/* Exercise the actual inline parent UI with out-of-order image decodes. */
const {spawnSync}=require('node:child_process'),vm=require('node:vm'),assert=require('node:assert/strict');
const {parseHTML}=require('linkedom');
const result=spawnSync('python3',['-c','from conteuse.studio import UI;import sys;sys.stdout.buffer.write(UI)'],{encoding:'utf8'});
assert.equal(result.status,0,result.stderr);
const {document}=parseHTML(result.stdout),drawn=[],closed=[],pending={};
for(const id of ['picture-preview','picture-print'])document.getElementById(id).getContext=()=>({clearRect(){},fillRect(){},drawImage(image){drawn.push(image.name);}});
const context={document,window:{print(){}},createImageBitmap:file=>new Promise((resolve,reject)=>pending[file.name]={resolve,reject}),fetch:()=>{throw new Error('Picture must not be uploaded');}};
vm.runInNewContext(document.querySelector('script').textContent,context);
const change=name=>document.getElementById('picture').onchange({target:{files:name?[{name,type:'image/png',size:10}]:[]}});
const image=name=>({name,width:100,height:100,close(){closed.push(name);}});
(async()=>{
 const a=change('A'),b=change('B');pending.B.resolve(image('B'));await b;pending.A.resolve(image('A'));await a;
 assert.deepEqual(drawn,['B','B']);assert(closed.includes('A'));assert.equal(document.getElementById('print-picture').disabled,false);
 drawn.length=0;const c=change('C');await change(null);pending.C.resolve(image('C'));await c;
 assert.deepEqual(drawn,[]);assert.equal(document.getElementById('print-picture').disabled,true);
 const d=change('D'),e=change('E');pending.E.resolve(image('E'));await e;const message=document.getElementById('result').textContent;pending.D.reject(new Error('stale'));await d;
 assert.equal(document.getElementById('result').textContent,message);
 console.log('PASS: actual parent UI keeps latest picture, ignores stale decode/error, disables invalid selection; picture never uploaded.');
})().catch(error=>{console.error(error);process.exitCode=1;});
