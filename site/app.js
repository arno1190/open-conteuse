/* Original showcase UI. No account, microphone, analytics or tracking service. */
'use strict';
(() => {
  const {strings,extraFr}=window.GaliaCopy;
  const originals = new Map();
  document.querySelectorAll('[data-i18n]').forEach(el => originals.set(el, el.innerHTML));
  const originalAttrs = new Map();
  document.querySelectorAll('[data-i18n-alt],[data-i18n-aria]').forEach(el => originalAttrs.set(el, el.getAttribute(el.hasAttribute('data-i18n-alt')?'alt':'aria-label')));
  let lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'fr';
  let stories = [], current = null, speechGeneration = 0;
  const recording = new Audio();
  const recordingPath = () => current && /^content\/audio\/[a-f0-9]{24}\/[a-z0-9.-]+\.mp3$/.test(current[lang].preview_audio || '') ? current[lang].preview_audio : '';
  const canListen = () => Boolean(recordingPath());
  const dialog = document.getElementById('story-dialog');
  const listen = document.getElementById('listen-button');
  const stop = document.getElementById('stop-button');
  const fallback = document.getElementById('browser-voice-button');
  const status = document.getElementById('voice-status');
  const t = key => lang === 'en' ? strings.en[key] : extraFr[key];
  const canSpeak = () => 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  function stopSpeech(message = '') {
    speechGeneration++;
    recording.pause(); recording.removeAttribute("src"); recording.load();
    if (canSpeak()) window.speechSynthesis.cancel();
    listen.disabled = !canListen(); stop.disabled = true; fallback.disabled=false;
    status.textContent = message;
  }
  function setLanguage(next, updateURL = true) {
    stopSpeech(); lang = next;
    document.documentElement.lang = lang;
    document.title = lang === 'fr' ? 'Galia — De grandes histoires, dans une petite poche.' : 'Galia — Big stories, little pockets.';
    document.querySelector('meta[name="description"]').content = lang === 'fr' ? 'Galia : un projet de conteuse de poche et des petites aventures originales à écouter, imaginer et prolonger sans écran. Aperçu français et anglais.' : 'Galia: a pocket audio-player project and original little adventures to hear, imagine and carry on away from screens. French and English preview.';
    originals.forEach((html,el) => { el.innerHTML = lang === 'fr' ? html : (strings.en[el.dataset.i18n] ?? html); });
    originalAttrs.forEach((value,el) => {
      const attr = el.hasAttribute('data-i18n-alt') ? 'alt' : 'aria-label';
      const key = el.dataset.i18nAlt || el.dataset.i18nAria;
      el.setAttribute(attr,lang === 'fr' ? value : (strings.en[key] ?? value));
    });
    document.querySelectorAll('[data-lang]').forEach(el => el.dataset.lang === lang ? el.setAttribute('aria-current','page') : el.removeAttribute('aria-current'));
    if(updateURL){const url = new URL(location.href);url.searchParams.set('lang',lang);history.replaceState({},'',url);}
    if(stories.length) renderStories();
    if(current) populateDialog(current);
  }
  function make(tag,text,className){const el=document.createElement(tag);if(text)el.textContent=text;if(className)el.className=className;return el;}
  function recordingDuration(copy) {
    const seconds=Math.round(copy.preview_audio_duration_seconds);
    return Number.isFinite(seconds)&&seconds>0 ? Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0') : t('durationLabel');
  }
  function renderStories() {
    const grid = document.getElementById('story-grid'); grid.replaceChildren();
    stories.forEach(story => {
      const copy=story[lang], article=make('article',null,'story-card');
      const art=make('button',null,'story-art');art.type='button';art.style.setProperty('--card-color',story.color);art.setAttribute('aria-label',t('storyOpen')+' : '+copy.title);
      const image=make('img');image.src=story.art;image.alt='';image.width=250;image.height=350;image.loading='lazy';art.append(image);art.addEventListener('click',()=>openStory(story));
      const meta=make('div',null,'story-meta');meta.append(make('span',lang==='fr'?'4–7 ans':'Ages 4–7'),make('span',recordingDuration(copy)));
      const button=make('button',t('storyOpen'),'text-link');button.type='button';button.addEventListener('click',()=>openStory(story));
      article.append(art,meta,make('h3',copy.title),make('p',copy.subtitle),button);grid.append(article);
    });
  }
  function populateDialog(story){
    const copy=story[lang];
    document.getElementById('dialog-kind').textContent=t('storyKind');
    document.getElementById('dialog-title').textContent=copy.title;
    document.getElementById('dialog-subtitle').textContent=copy.subtitle;
    document.getElementById('dialog-meta').textContent=t('ageLabel')+' · '+t('durationLabel');
    const art=document.getElementById('dialog-art');art.src=story.art;art.alt='';
    document.getElementById('dialog-activity').textContent=copy.activity;
    const script=document.getElementById('dialog-script');script.replaceChildren();
    const paragraphs=Array.isArray(copy.script)?copy.script:String(copy.script).split(/\n\s*\n/);
    paragraphs.forEach(p=>script.append(make('p',p)));
    listen.disabled=!canListen();stop.disabled=true;fallback.hidden=Boolean(recordingPath())||!canSpeak();fallback.disabled=false;
    status.textContent=canListen()?'':canSpeak()?t('recordingUnavailable'):t('voiceUnavailable');
    const download=document.getElementById('download-audio'); download.hidden=!recordingPath();if(recordingPath())download.href=recordingPath();
    document.getElementById('dialog-meta').textContent=t('ageLabel')+' · '+recordingDuration(copy);
  }
  function openStory(story){stopSpeech();current=story;populateDialog(story);dialog.showModal();}
  function speak(useBrowser=false){
    if(!current || (useBrowser ? !canSpeak() : !canListen()))return;
    stopSpeech();const generation=speechGeneration;
    const copy=current[lang];
    if(!useBrowser && recordingPath()){
      recording.src=recordingPath();listen.disabled=true;stop.disabled=false;status.textContent=t('speaking');
      recording.onended=()=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;status.textContent=t('finished');};
      const failed=()=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;fallback.hidden=!canSpeak();fallback.disabled=false;status.textContent=t('voiceError');};
      recording.onerror=failed;
      recording.play().catch(failed);
      return;
    }
    fallback.disabled=true;
    const text=Array.isArray(copy.script)?copy.script.join('\n\n'):copy.script;
    // Paragraph-sized utterances avoid the long-utterance cutoff on some browsers.
    const chunks=String(text).split(/\n\s*\n/).filter(Boolean);
    const language=lang==='fr'?'fr-FR':'en-GB';
    const voices=window.speechSynthesis.getVoices();
    const voice=voices.find(v=>v.lang===language&&v.localService)||voices.find(v=>v.lang===language)||voices.find(v=>v.lang.startsWith(lang));
    listen.disabled=true;stop.disabled=false;status.textContent=t('speaking');
    function read(index){
      if(generation!==speechGeneration)return;
      if(index>=chunks.length){listen.disabled=!canListen();stop.disabled=true;fallback.disabled=false;status.textContent=t('finished');return;}
      const utterance=new SpeechSynthesisUtterance(chunks[index]);utterance.lang=language;utterance.rate=.85;utterance.pitch=1;if(voice)utterance.voice=voice;
      utterance.onend=()=>read(index+1);
      utterance.onerror=event=>{if(generation!==speechGeneration)return;listen.disabled=!canListen();stop.disabled=true;status.textContent=event.error==='not-allowed'?t('voiceUnavailable'):t('voiceError');fallback.disabled=false;};
      window.speechSynthesis.speak(utterance);
    }
    read(0);
  }
  document.querySelectorAll('[data-lang]').forEach(el=>el.addEventListener('click',event=>{event.preventDefault();setLanguage(el.dataset.lang);}));
  document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>stopSpeech());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});
  listen.addEventListener('click',()=>speak(false));fallback.addEventListener('click',()=>speak(true));stop.addEventListener('click',()=>stopSpeech(t('stopped')));
  window.addEventListener('pagehide',()=>stopSpeech());
  window.addEventListener('popstate',()=>setLanguage(new URLSearchParams(location.search).get('lang')==='en'?'en':'fr',false));
  setLanguage(lang,false);
  fetch('content/index.json').then(response=>{if(!response.ok)throw new Error('collection unavailable');return response.json();}).then(data=>{
    if(!Array.isArray(data.stories)||!data.stories.length)throw new Error('empty collection');
    stories=data.stories.filter(story=>story.fr?.title&&story.en?.title&&story.fr?.script&&story.en?.script&&/^content\/[a-z0-9/_.-]+\.svg$/.test(story.art));
    if(!stories.length)throw new Error('invalid collection');renderStories();
  }).catch(()=>{const grid=document.getElementById('story-grid');grid.replaceChildren(make('p',t('loadError'),'error-note'));});
})();
