/* Original showcase UI. No account, microphone, analytics or tracking service. */
'use strict';
(() => {
  const strings = {
    en: {
      controlsTitle:'Galia Mini: five buttons, five simple gestures.',controlsIntro:'On Galia Mini, one large central button for play and pause. Previous and next tracks sit on either side. Two smaller buttons below control volume: different gestures, symbols and shapes to recognise, without relying on colour alone.',exploreControlsTitle:'Galia Explore: eight buttons for finding your way.',exploreControlsText:'Four directions to browse the library, a large A button to play or confirm, a smaller B button to go back, and two separate volume buttons. This layout accompanies the small screen; it differs from Galia Mini.',exploreDpad:'Four directions',explorePrimary:'Play / confirm',exploreBack:'B / back',controlPlay:'Play / pause',controlTrack:'Previous / next',controlVolume:'Volume',controlsPending:'Proposed layout and tactile cues; comfort, accidental presses and use by children still need physical prototype testing.',workflowEyebrow:'The journey we are preparing',workflowTitle:'Start with an idea.<br>Your approval at every step.',workflowStatus:'A product goal, not a live creation service. Today: local import, review and export tools; here: three demonstration stories.',workflowOneState:'Personalisation to design',workflowOneTitle:'You choose the starting point.',workflowOne:'Something your child wonders about, a language, a memory or an authorised source. You decide what belongs in their library.',workflowTwoState:'Local review exists; creation connections planned',workflowTwoTitle:'Read it. Then listen to it.',workflowTwo:'A draft is not an approval. The intended workflow separates script review from approval of the final audio file, and asks again when the version changes.',workflowThreeState:'Local export exists; hardware playback unvalidated',workflowThreeTitle:'The card finds its story.',workflowThree:'Once approved and transferred, the card will select audio kept inside the player. The goal: listening away from screens, at their own pace.',providerTitle:'What about my subscriptions or creative tools?',providerText:'Provider connections, MCP and speech-generation tools are being assessed. No account is connected here. A subscription does not automatically include API access, voice credits or permission to copy a catalogue. Options and costs will be checked provider by provider, with your agreement before any content transfer.',
      cadEyebrow:'Behind the little project',cadTitle:'From drawing to something tangible.',cadNote:'Views of the current CAD geometry with nominal component envelopes. Colours aid reading; assembly and safety still need physical prototype validation.',cadMiniAlt:'Galia Mini current CAD geometry with contact-ID cartridge',cadExploreAlt:'Galia Explore current CAD geometry with display',caseOnly:'· case only',skip:'Skip to content', announcement:'A little project, growing up. Meet our first stories.', announcementLink:'Open the collection', nav:'Main navigation', navStories:'The stories', navRitual:'A little ritual', navPlayers:'The players', navParents:'For grown-ups',
      heroEyebrow:'Little ears. Great big elsewhere.', heroTitle:'Shall we go somewhere,<br>without going anywhere?', heroIntro:'A card, a story, and a whole world to imagine. Galia is a pocket audio-player project, with stories prepared by parents around the things their children love.', heroCta:'Discover the stories', heroSecond:'Meet the Galia Mini', heroNote:'First collection, freely available · Hardware in development', heroAlt:'An illustrated colour study of a small green audio player with a story card', roundel:'A little player.<br>A world of detours.', heroCaption:'Illustrative styling study · Final shape subject to physical prototyping.', ribbonLabel:'The Galia spirit', ribbonOne:'Listen at your own pace', ribbonTwo:'Imagine it your way', ribbonThree:'Carry on without a screen',
      storiesEyebrow:'Our very first collection', storiesTitle:'Three cards.<br>A thousand little journeys.', storiesIntro:'A gentle mystery, a walk full of sounds, a small journey into evening. Pick a story, try the preview, and let your imagination find its way.', loading:'The stories are on their way…', printCards:'Print the cards', cardsNote:'Paper cards for imagining and playing. They do not replace the prototype’s electronic cards.', reviewNote:'An original collection in the making. Texts suggested for ages 4–7, to explore with a grown-up first. Scripts and synthetic demonstration recordings still need adult review; final voice production is pending.',
      ritualEyebrow:'Every journey starts somewhere', ritualTitle:'A little ritual.<br>A lovely place to begin.', ritualIntro:'On the way home, in a cushion den, in a quiet moment before dinner… Every story finds its moment.', ritualOneTitle:'I pick my elsewhere.', ritualOne:'An illustrated card to find an old favourite, or discover a new story together.', ritualTwoTitle:'I open my ears.', ritualTwo:'Listen, pause, come back. There is no hurry here: the pictures happen in your imagination.', ritualThreeTitle:'I take a little story with me.', ritualThree:'Find a sound, invent a cloud, draw a shelter… A simple idea to carry the adventure on, away from screens.',
      playersEyebrow:'Two little companions in the making', playersTitle:'A pocket can hold<br>a whole wide world.', playersIntro:'Galia Mini keeps it simple: slide in a card and find your story. Galia Explore adds a small screen for browsing. Two open design projects, with listening at their heart.', miniPill:'A simple little gesture', miniDescription:'Slide in a card. Find a familiar story.', miniFeatureLabel:'Selection', miniFeature:'Contact ID card, identifier only', sharedAudioLabel:'Listening', sharedAudio:'Speaker and 3.5 mm headphone jack', sharedUsbLabel:'Connection', sharedUsb:'USB-C charging and data', priceTarget:'target incl. French VAT, unconfirmed', explorePill:'A little more exploring', exploreDescription:'A little window into your audio library.', exploreFeatureLabel:'Browsing', exploreFeature:'Small library-navigation screen', developmentTitle:'A tangible idea. A journey still ahead.', developmentText:'These are target retail prices, not sales offers. Supplier quotes, prototypes, safety testing and manufacturing costs remain to be validated. Dimensions are nominal; drawings on this page are styling studies. Orders and reservations are not open.', developmentLink:'Explore the open design files',
      parentsEyebrow:'For grown-ups', parentsTitle:'Their interests.<br>Your little story workshop.', parentsIntro:'Dinosaurs, distant stars, a question from today… Our ambition is to help you prepare stories and little discoveries around your child, using your ideas and sources you have permission to use. You choose, read and listen first.', parentsLink:'Get to know the project', parentOneTitle:'Already: import, review, choose', parentOne:'The local prototype can import recordings and some authorised podcasts, review an exact version and assign content to cards. Playback on the hardware still needs validation.', parentTwoTitle:'Next? More personal stories', parentTwo:'Stories about their interests, little lessons, material prepared from your own sources: that is our direction. Assisted creation and connections to your subscriptions are under assessment, not available on this showcase.', parentThreeTitle:'Always: a grown-up has the final say', parentThree:'The three stories here are original demonstrations. The script and final audio need separate approvals. A card selects a story stored in the player; it gives no rights to a subscription.',
      faqEyebrow:'Little questions', faqTitle:'Before the next detour.', faqOneTitle:'Can I buy a player yet?', faqOne:'Not yet. This showcase introduces a design project and its first stories. Manufacturing, final pricing and compliance have not been validated.', faqTwoTitle:'Do I need a screen to listen?', faqTwo:'For this preview, a browser starts a synthetic demonstration recording; you can download it for later listening. The Galia Mini project aims for screen-free listening, with files stored in the player. Galia Explore has a small navigation screen.', faqThreeTitle:'What is inside the card?', faqThree:'The planned Galia Mini card carries only an electronic identifier. It selects audio already stored in the player. The printable paper cards here are play materials and do not trigger the prototype.', faqFourTitle:'Are the stories in French and English?', faqFour:'Yes. All three original stories and their activities are available in both languages. Use FR / EN at the top of the page. Synthetic demonstration recordings are available in both languages; browser voices are a fallback when a file is unavailable.', faqFiveTitle:'Can we use the stories at home?', faqFive:'The collection’s sources and licence are available with the downloads. Read the text together first and adapt the activity to your child. A card chooses a story; no child voice recording is needed.',
      closingEyebrow:'See you somewhere new?', closingTitle:'The next adventure<br>starts with a listen.', closingCta:'Choose a story', footerDescription:'Pocket players. Original stories. Little escapes.', footerSources:'Project sources', footerBook:'The storybook to read together', footerContent:'Collection sources', footerGallery:'All CAD views',footerDossier:'Engineering dossier and RFQ',footerLabels:'Cartridge artwork labels', footerCards:'Printable cards', footerStatus:'Design preview · November 2026 · Hardware not physically validated', close:'Close', listen:'Play the preview', stop:'Stop', downloadAudio:'Download the demonstration audio', voiceNote:'Locally generated synthetic demonstration recording (eSpeak NG), not the final narration. Download it to listen away from the screen. If no recording is available, the browser voice is a fallback and may use a network service.', activityTitle:'And now, away from the screen…', transcript:'Read the story',
      storyOpen:'Discover this story', storyKind:'A little listening adventure', speaking:'Reading the story. You can stop at any time.', finished:'The reading has finished. The adventure can carry on away from the screen.', stopped:'Reading stopped.', voiceUnavailable:'Speech is not available in this browser. You can read the full story below.', voiceError:'The voice could not finish the reading. The full text is available below.', loadError:'The collection could not load. You can still download the printable cards or read the source texts.', ageLabel:'Suggested ages 4–7', durationLabel:'About 4 minutes · estimate'
    }
  };
  const extraFr = {storyOpen:'Découvrir cette histoire',storyKind:'Une petite aventure à écouter',speaking:'Lecture en cours. Vous pouvez arrêter quand vous voulez.',finished:'La lecture est terminée. L’aventure peut continuer sans écran.',stopped:'Lecture arrêtée.',voiceUnavailable:'La voix n’est pas disponible dans ce navigateur. Vous pouvez lire toute l’histoire ci-dessous.',voiceError:'La lecture vocale n’a pas pu aller au bout. Le texte complet reste disponible ci-dessous.',loadError:'La collection n’a pas pu se charger. Vous pouvez télécharger les cartes ou consulter les textes sources.',ageLabel:'4–7 ans · indication',durationLabel:'Environ 4 minutes · estimation'};
  const originals = new Map();
  document.querySelectorAll('[data-i18n]').forEach(el => originals.set(el, el.innerHTML));
  const originalAttrs = new Map();
  document.querySelectorAll('[data-i18n-alt],[data-i18n-aria]').forEach(el => originalAttrs.set(el, el.getAttribute(el.hasAttribute('data-i18n-alt')?'alt':'aria-label')));
  let lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'fr';
  let stories = [], current = null, speechGeneration = 0;
  const recording = new Audio();
  const recordingPath = () => current && /^content\/audio\/[a-z0-9.-]+\.mp3$/.test(current[lang].preview_audio || '') ? current[lang].preview_audio : '';
  const canListen = () => Boolean(recordingPath()) || canSpeak();
  const dialog = document.getElementById('story-dialog');
  const listen = document.getElementById('listen-button');
  const stop = document.getElementById('stop-button');
  const status = document.getElementById('voice-status');
  const t = key => lang === 'en' ? strings.en[key] : extraFr[key];
  const canSpeak = () => 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  function stopSpeech(message = '') {
    speechGeneration++;
    recording.pause(); recording.removeAttribute("src"); recording.load();
    if (canSpeak()) window.speechSynthesis.cancel();
    listen.disabled = !canListen(); stop.disabled = true;
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
    listen.disabled=!canListen();stop.disabled=true;
    status.textContent=canListen()?'':t('voiceUnavailable');
    const download=document.getElementById('download-audio'); download.hidden=!recordingPath();if(recordingPath())download.href=recordingPath();
    document.getElementById('dialog-meta').textContent=t('ageLabel')+' · '+recordingDuration(copy);
  }
  function openStory(story){stopSpeech();current=story;populateDialog(story);dialog.showModal();}
  function speak(){
    if(!current||!canListen())return;
    stopSpeech();const generation=speechGeneration;
    const copy=current[lang];
    if(recordingPath()){
      recording.src=recordingPath();listen.disabled=true;stop.disabled=false;status.textContent=t('speaking');
      recording.onended=()=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;status.textContent=t('finished');};
      recording.onerror=()=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;status.textContent=t('voiceError');};
      recording.play().catch(()=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;status.textContent=t('voiceError');});
      return;
    }
    const text=Array.isArray(copy.script)?copy.script.join('\n\n'):copy.script;
    // Paragraph-sized utterances avoid the long-utterance cutoff on some browsers.
    const chunks=String(text).split(/\n\s*\n/).filter(Boolean);
    const language=lang==='fr'?'fr-FR':'en-GB';
    const voices=window.speechSynthesis.getVoices();
    const voice=voices.find(v=>v.lang===language&&v.localService)||voices.find(v=>v.lang===language)||voices.find(v=>v.lang.startsWith(lang));
    listen.disabled=true;stop.disabled=false;status.textContent=t('speaking');
    function read(index){
      if(generation!==speechGeneration)return;
      if(index>=chunks.length){listen.disabled=false;stop.disabled=true;status.textContent=t('finished');return;}
      const utterance=new SpeechSynthesisUtterance(chunks[index]);utterance.lang=language;utterance.rate=.85;utterance.pitch=1;if(voice)utterance.voice=voice;
      utterance.onend=()=>read(index+1);
      utterance.onerror=event=>{if(generation!==speechGeneration)return;listen.disabled=false;stop.disabled=true;status.textContent=event.error==='not-allowed'?t('voiceUnavailable'):t('voiceError');};
      window.speechSynthesis.speak(utterance);
    }
    read(0);
  }
  document.querySelectorAll('[data-lang]').forEach(el=>el.addEventListener('click',event=>{event.preventDefault();setLanguage(el.dataset.lang);}));
  document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>stopSpeech());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});
  listen.addEventListener('click',speak);stop.addEventListener('click',()=>stopSpeech(t('stopped')));
  window.addEventListener('pagehide',()=>stopSpeech());
  window.addEventListener('popstate',()=>setLanguage(new URLSearchParams(location.search).get('lang')==='en'?'en':'fr',false));
  setLanguage(lang,false);
  fetch('content/index.json').then(response=>{if(!response.ok)throw new Error('collection unavailable');return response.json();}).then(data=>{
    if(!Array.isArray(data.stories)||!data.stories.length)throw new Error('empty collection');
    stories=data.stories.filter(story=>story.fr?.title&&story.en?.title&&story.fr?.script&&story.en?.script&&/^content\/[a-z0-9/_.-]+\.svg$/.test(story.art));
    if(!stories.length)throw new Error('invalid collection');renderStories();
  }).catch(()=>{const grid=document.getElementById('story-grid');grid.replaceChildren(make('p',t('loadError'),'error-note'));});
})();
