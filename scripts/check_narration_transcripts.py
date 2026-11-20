"""Optional local ASR omission screen; never a listening or approval substitute."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from project import ROOT


def sha(data): return hashlib.sha256(data).hexdigest()


def words(text):
    text=''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))
    return re.findall(r'[a-z0-9]+',text)


def distance(reference, heard):
    row=list(range(len(heard)+1))
    for i,a in enumerate(reference,1):
        current=[i]
        for j,b in enumerate(heard,1):current.append(min(current[-1]+1,row[j]+1,row[j-1]+(a!=b)))
        row=current
    return row[-1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-model',action='store_true')
    args=parser.parse_args()
    import numpy as np
    from faster_whisper import WhisperModel
    base=ROOT/'content/starter';out=base/'qa';out.mkdir(exist_ok=True)
    model_dir=ROOT/'work/current/asr-model-base'
    model=WhisperModel('base',download_root=str(model_dir),local_files_only=not args.fetch_model,
        device='cpu',compute_type='int8',cpu_threads=2)
    weights=list(model_dir.rglob('model.bin'));assert len(weights)==1
    catalog=json.loads((base/'index.json').read_text());results=[]
    for asset in catalog['audio_assets']:
        path=base/asset['path'].removeprefix('content/')
        raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-ar','16000','-ac','1','-f','f32le','pipe:1'])
        segments,_=model.transcribe(np.frombuffer(raw,dtype=np.float32),language=asset['language'],beam_size=3)
        transcript=' '.join(segment.text.strip() for segment in segments)
        name=asset['story_id']+'.'+asset['language']+'.txt'
        (out/name).write_text(transcript+'\n')
        story=next(s for s in catalog['stories'] if s['id']==asset['story_id'])
        original=story[asset['language']]['script'];ref=words(original);heard=words(transcript)
        result={'story_id':asset['story_id'],'language':asset['language'],
            'audio_sha256':asset['audio_sha256'],'script_sha256':asset['script_sha256'],
            'transcript_file':'qa/'+name,'transcript_sha256':sha((out/name).read_bytes()),
            'reference_tokens':len(ref),'recognized_tokens':len(heard),
            'word_error_rate':round(distance(ref,heard)/len(ref),4),
            'editorial_words_per_minute':round(story[asset['language']]['word_count']/asset['duration_seconds']*60,1),
            'listening_approval':'pending'}
        results.append(result);print(name,result['word_error_rate'],result['editorial_words_per_minute'],flush=True)
    report={'method':'faster-whisper base, local CPU int8, fixed language, beam3; FFmpeg mono16k float PCM',
        'purpose':'Screen for omissions and inspect approximate transcripts; ASR mistakes are not proof of voice errors.',
        'generator_sha256':sha(Path(__file__).read_bytes()),'model_id':'Systran/faster-whisper-base',
        'model_weights_sha256':sha(weights[0].read_bytes()),
        'runtime_versions':{n:importlib.metadata.version(n) for n in ('faster-whisper','ctranslate2','numpy')},
        'human_listening_approval':'pending','results':results}
    (out/'transcript-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
