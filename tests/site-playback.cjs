/* Exercise the actual static UI against a DOM and controllable media objects. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {parseHTML}=require('linkedom');
const html=fs.readFileSync('site/index.html','utf8');
const cad=parseHTML(html).document.querySelectorAll('.cad-section img');
assert.deepEqual(Array.from(cad,image=>image.getAttribute('src')),['assets/mini-current-cad.png','assets/explore-current-cad.png']);
for(const variant of ['mini','explore']) assert.equal(fs.existsSync('site/assets/'+variant+'-cad.png'),false);
assert.equal(parseHTML(html).document.querySelector('[data-i18n-alt=cardAlt]').getAttribute('src'),'design/images/card-exploded.png');
const js=fs.readFileSync('site/strings.js','utf8')+'\n'+fs.readFileSync('site/app.js','utf8');
const source=JSON.parse(fs.readFileSync('site/content/index.json','utf8'));
async function setup(data=source,tts=false){
  const {window}=parseHTML(html),document=window.document,instances=[],events={},utterances=[];
  let cancels=0;
  class Audio{
    constructor(){instances.push(this);this.plays=0;}
    pause(){} load(){} removeAttribute(key){delete this[key];}
    play(){this.plays++;return Promise.resolve();}
  }
  const dialog=document.getElementById('story-dialog');
  dialog.showModal=()=>dialog.open=true;
  dialog.close=()=>{dialog.open=false;dialog.dispatchEvent(new window.Event('close'));};
  const win={addEventListener:(name,fn)=>events[name]=fn};
  if(tts){
    win.speechSynthesis={cancel:()=>cancels++,getVoices:()=>[],speak:u=>utterances.push(u)};
    win.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};
  }
  const ctx={window:win,document,location:{href:'https://example.test/?lang=fr',search:'?lang=fr'},
    history:{replaceState(){}},URL,URLSearchParams,Audio,
    fetch:async()=>({ok:true,json:async()=>structuredClone(data)}),SpeechSynthesisUtterance:win.SpeechSynthesisUtterance};
  vm.runInNewContext(js,ctx);await new Promise(resolve=>setImmediate(resolve));
  return {document,dialog,a:instances[0],events,utterances,get cancels(){return cancels;}};
}
(async()=>{
  const x=await setup(source,true),d=x.document;
  assert.equal(d.querySelectorAll('.story-card').length,3);
  d.querySelector('.story-art').click();assert(x.dialog.open);
  const listen=d.getElementById('listen-button'),stop=d.getElementById('stop-button'),fallback=d.getElementById('browser-voice-button');
  assert(!listen.disabled && fallback.hidden);
  assert.equal(d.getElementById('download-audio').getAttribute('href'),source.stories[0].fr.preview_audio);
  listen.click();assert.equal(x.a.src,source.stories[0].fr.preview_audio);assert(listen.disabled && !stop.disabled);
  const staleEnded=x.a.onended;stop.click();staleEnded();assert.match(d.getElementById('voice-status').textContent,/arrêtée/);
  listen.click();d.querySelector('[data-lang=en]').click();assert.equal(d.documentElement.lang,'en');assert(!x.a.src);
  assert.equal(d.getElementById('download-audio').getAttribute('href'),source.stories[0].en.preview_audio);
  const seconds=Math.round(source.stories[0].en.preview_audio_duration_seconds);
  assert(d.getElementById('dialog-meta').textContent.includes(Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0')));
  listen.click();x.a.onended();assert.match(d.getElementById('voice-status').textContent,/finished/);
  listen.click();x.a.onerror();assert(!fallback.hidden);assert.equal(x.utterances.length,0); // no implicit network voice
  fallback.click();assert.equal(x.utterances.length,1);assert(fallback.disabled);
  const staleUtterance=x.utterances[0];x.dialog.close();staleUtterance.onend();assert.equal(x.utterances.length,1);
  d.querySelector('.story-art').click();listen.click();x.events.pagehide();assert(!x.a.src && stop.disabled);
  const invalid=structuredClone(source);invalid.stories[0].fr.preview_audio='https://bad.test/audio.mp3';
  const y=await setup(invalid);y.document.querySelector('.story-art').click();assert(y.document.getElementById('listen-button').disabled);
  assert(y.document.getElementById('download-audio').hidden && y.document.getElementById('browser-voice-button').hidden);
  const z=await setup(invalid,true);z.document.querySelector('.story-art').click();
  assert(z.document.getElementById('listen-button').disabled);assert(!z.document.getElementById('browser-voice-button').hidden);
  assert.match(z.document.getElementById('voice-status').textContent,/Aucun enregistrement/);
  z.document.getElementById('browser-voice-button').click();assert.equal(z.utterances.length,1);
  z.utterances[0].onerror({error:'synthesis-failed'});assert(z.document.getElementById('listen-button').disabled);
  console.log('PASS: real UI FR/EN assets/duration, immutable paths, stop/stale callbacks, close/pagehide, MP3 failure, explicit browser fallback and missing-media states.');
})().catch(error=>{console.error(error);process.exitCode=1;});
