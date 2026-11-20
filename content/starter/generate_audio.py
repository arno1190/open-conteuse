#!/usr/bin/env python3
"""Generate optional local synthetic draft listening files; never approves content.
Uses eSpeak NG locally and FFmpeg, with no TTS service or credentials.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=ROOT/'work/current/tts'
LIB=WORK/'root/usr/lib/x86_64-linux-gnu'

def sha(data):return hashlib.sha256(data).hexdigest()
def run(args,**kw):return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fetch-engine',action='store_true',help='Download pinned Debian packages into work/ and extract locally; no system installation.')
 args=parser.parse_args()
 lock=json.loads((HERE/'tts-engine-lock.json').read_text())
 if args.fetch_engine:
  WORK.mkdir(parents=True,exist_ok=True)
  for row in lock['packages']:
   target=WORK/row['filename']
   if not target.exists():target.write_bytes(urllib.request.urlopen(row['url'],timeout=60).read())
   if sha(target.read_bytes())!=row['sha256']:raise ValueError('TTS engine package hash mismatch: '+row['filename'])
   run(['dpkg-deb','-x',str(target),str(WORK/'root')])
 binary=Path(os.environ.get('ESPEAK_NG_BIN',str(WORK/'root/usr/bin/espeak-ng')))
 if not binary.exists():
  binary=Path(shutil.which('espeak-ng') or '')
  if not binary.is_file():raise SystemExit('eSpeak NG missing. Run with --fetch-engine on Debian amd64 or set ESPEAK_NG_BIN and ESPEAK_NG_DATA_ROOT.')
 data_root=Path(os.environ.get('ESPEAK_NG_DATA_ROOT',str(LIB)))
 env=dict(os.environ);env['LD_LIBRARY_PATH']=str(LIB)+(os.pathsep+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
 version=run([str(binary),'--path='+str(data_root),'--version'],env=env).stdout.decode().strip().splitlines()[0].split(' Data at:')[0].strip()
 if '1.52.0' not in version:raise SystemExit('Pinned generation expects eSpeak NG 1.52.0; got '+version)
 ffmpeg=run(['ffmpeg','-version']).stdout.decode().splitlines()[0]
 catalog=json.loads((HERE/'index.json').read_text());assets=[]
 audio=HERE/'audio';audio.mkdir(exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
 for story in catalog['stories']:
  for lang,voice in [('fr','fr-fr'),('en','en-gb')]:
   script=story[lang]['script'];paras=script.split('\n\n')
   ssml='<speak><break time="1000ms"/>'
   for para in paras:
    pause=8000 if para.startswith(('Si tu','Et toi','If you')) else 2000
    ssml+=escape(para)+f'<break time="{pause}ms"/>'
   ssml+='</speak>'
   stem=story['id']+'.'+lang;wav=WORK/(stem+'.wav');out=audio/(stem+'.mp3')
   run([str(binary),'--path='+str(data_root),'-v',voice,'-s','105','-p','45','-a','70','-m','--stdin','-w',str(wav)],input=ssml.encode(),env=env)
   run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-map_metadata','-1','-af','loudnorm=I=-23:TP=-3:LRA=7','-ar','22050','-ac','1','-codec:a','libmp3lame','-b:a','64k',str(out)])
   probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,sample_rate,channels','-of','json',str(out)]).stdout)
   seconds=round(float(probe['format']['duration']),3);stream=probe['streams'][0]
   if not 120<seconds<480 or stream['channels']!=1:raise ValueError('Unexpected audio shape/duration for '+stem)
   path='content/audio/'+out.name
   story[lang]['preview_audio']=path
   story[lang]['preview_audio_duration_seconds']=seconds
   assets.append({'story_id':story['id'],'language':lang,'path':path,'status':'synthetic_draft_demo','approval':'pending','script_sha256':sha(script.encode()),'ssml_sha256':sha(ssml.encode()),'audio_sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'duration_seconds':seconds,'codec':stream['codec_name'],'sample_rate_hz':int(stream['sample_rate']),'channels':stream['channels'],'engine':'eSpeak NG 1.52.0','voice':voice,'speed_words_per_minute':105,'pitch':45,'amplitude':70,'paragraph_pause_ms':2000,'invitation_pause_ms':8000,'ffmpeg_filter':'loudnorm=I=-23:TP=-3:LRA=7','final_audio_approval':'pending'})
   print(stem,seconds,'seconds',out.stat().st_size,'bytes')
 catalog['audio_assets']=assets
 catalog['preview_note']={'fr':'Enregistrements de démonstration synthétiques, générés localement avec eSpeak NG. Voix robotique, non interprétée par un comédien. Fichiers téléchargeables pour écouter sans écran ; validation de l’audio final en attente.','en':'Synthetic demonstration recordings, generated locally with eSpeak NG. Robotic voice, not a performer’s narration. Downloadable files for listening away from a screen; final audio approval pending.'}
 (HERE/'index.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
 receipt={'status':'synthetic_draft_demo','final_audio_approval':'pending','engine_version':version,'encoder_version':ffmpeg,'engine_lock':'tts-engine-lock.json','script_encoding':'UTF-8, exact JSON script string, no trailing newline','audio_assets':assets,'physical_acoustic_validation':'pending; digital normalization does not establish safe headphone or speaker output','not_device_pack':'MP3 listening previews are not activated device libraries; device export requires supported PCM conversion and explicit parent review.'}
 (HERE/'audio-generation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
 public=ROOT/'site/content';public.mkdir(parents=True,exist_ok=True)
 shutil.copytree(audio,public/'audio',dirs_exist_ok=True)
 for f in ['index.json','audio-generation.json']:shutil.copyfile(HERE/f,public/f)
if __name__=='__main__':main()
