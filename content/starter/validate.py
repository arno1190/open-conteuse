#!/usr/bin/env python3
"""Verify current editorial/audio provenance and mirrors; --media measures files."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC = ROOT / 'site/content'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()


def run(args):
    return subprocess.run(args,check=True,capture_output=True)


def validate(measure=False):
    d=json.loads((HERE/'index.json').read_text())
    assert d['schema_version']==1 and d['status']=='editorial_draft'
    assert d['script_approval']==d['audio_approval']=='pending'
    assert len(d['stories'])==3 and len(d['audio_assets'])==6
    spec=importlib.util.spec_from_file_location('narration_generator',HERE/'generate_audio.py')
    generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
    ids=set()
    for story in d['stories']:
        assert re.fullmatch(r'[a-z0-9-]+',story['id']) and story['id'] not in ids
        ids.add(story['id'])
        assert story['script_approval']==story['audio_approval']=='pending'
        assert story['recording']['audio_file'] is None
        for lang in ('fr','en'):
            z=story[lang]
            assert len(z['script'].split())==z['word_count'] and 350<=z['word_count']<=650
            assert z['activity'] and z['card_activity']
            md=(HERE/(story['id']+'.'+lang+'.md')).read_text()
            assert z['script'] in md and z['activity'] in md
        for suffix in ('','-back'):
            xml=ET.parse(HERE/'cards'/(story['id']+suffix+'.svg')).getroot()
            assert xml.tag.endswith('svg') and not any(e.tag.endswith('script') for e in xml.iter())
        assert story['art']=='content/cards/'+story['id']+'.svg'
    receipt=json.loads((HERE/'audio-generation.json').read_text())
    assert receipt['audio_assets']==d['audio_assets']
    assert receipt['status']=='synthetic_draft_demo' and receipt['final_audio_approval']=='pending'
    batch=receipt['batch_id'];assert re.fullmatch(r'[a-f0-9]{24}',batch)
    assert d['audio_generation']=='content/audio/'+batch+'/generation.json'
    generator.verify_batch(HERE/'audio'/batch,receipt)
    generator.verify_batch(PUBLIC/'audio'/batch,receipt)
    provenance=receipt['provenance']
    assert provenance['generator_sha256']==sha((HERE/'generate_audio.py').read_bytes())
    assert provenance['requirements_sha256']==sha((HERE/'requirements-narration.txt').read_bytes())
    assert provenance['model_lock']==json.loads((HERE/'tts-engine-lock.json').read_text())
    assert receipt['credits_sha256']==provenance['credits_sha256']==sha((HERE/'TTS-NOTICES.md').read_bytes())
    assert (HERE/'audio'/batch/'CREDITS.txt').read_bytes()==(HERE/'TTS-NOTICES.md').read_bytes()
    assert d['narration_credits']=='content/TTS-NOTICES.md'
    media=[];seen=set()
    for asset in d['audio_assets']:
        key=(asset['story_id'],asset['language']);assert key not in seen;seen.add(key)
        story=next(s for s in d['stories'] if s['id']==key[0]);z=story[key[1]]
        assert z['preview_audio']==asset['path']
        assert asset['approval']==asset['final_audio_approval']=='pending'
        assert asset['script_sha256']==sha(z['script'].encode())
        assert asset['render_plan']==generator.render_plan(z['script'],key[1])
        assert asset['render_plan_sha256']==sha(canonical(asset['render_plan']))
        f=HERE/'audio'/batch/(key[0]+'.'+key[1]+'.mp3')
        assert sha(f.read_bytes())==asset['audio_sha256'] and f.stat().st_size==asset['bytes']
        assert 120<asset['duration_seconds']<480 and asset['sample_rate_hz']==22050 and asset['channels']==1 and asset['codec']=='mp3'
        if measure:
            actual=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:format_tags=comment:stream=codec_name,sample_rate,channels','-of','json',str(f)]).stdout)
            stream=actual['streams'][0];seconds=float(actual['format']['duration'])
            assert abs(seconds-asset['duration_seconds'])<.05
            assert stream['codec_name']=='mp3' and stream['channels']==1 and int(stream['sample_rate'])==22050
            credit=actual['format']['tags']['comment'];assert 'Kokoro' in credit
            if key[1]=='fr':assert 'SIWIS' in credit and 'CC BY 4.0' in credit
            decoded=run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
            assert not decoded.stderr
            loud=run(['ffmpeg','-hide_banner','-i',str(f),'-af','loudnorm=I=-23:TP=-3:LRA=7:print_format=json','-f','null','-']).stderr.decode()
            stats,_=json.JSONDecoder().raw_decode(loud[loud.rfind('{'):])
            integrated=float(stats['input_i']);peak=float(stats['input_tp'])
            assert math.isfinite(integrated) and math.isfinite(peak) and peak<0
            media.append({'path':asset['path'],'sha256':asset['audio_sha256'],'duration_seconds':round(seconds,3),
                'codec':stream['codec_name'],'channels':stream['channels'],'sample_rate_hz':int(stream['sample_rate']),
                'integrated_lufs':integrated,'true_peak_dbtp':peak,'full_decode':'passed','embedded_credits':credit})
    assert seen=={(i,lang) for i in ids for lang in ('fr','en')}
    for name in ('index.json','audio-generation.json','TTS-NOTICES.md','cards.pdf','collection.pdf','cartridge-labels.pdf','cartridge-labels.json'):
        assert (HERE/name).read_bytes()==(PUBLIC/name).read_bytes(),name
    for directory in ('cards','cartridge-labels','tts-notices'):
        assert {p.name for p in (HERE/directory).iterdir()}=={p.name for p in (PUBLIC/directory).iterdir()},directory
        for f in (HERE/directory).iterdir():
            assert f.read_bytes()==(PUBLIC/directory/f.name).read_bytes(),str(f)
    labels=json.loads((HERE/'cartridge-labels.json').read_text())
    assert labels['label_size']==[33.6,38.6] and labels['window_xy']==[3,7,37,46]
    assert labels['label_xy']==[3.2,7.2,36.8,45.8] and labels['maximum_paper_thickness']==.15
    assert labels['pocket_xy']==[2.8,6.8,37.2,46.2] and labels['label_to_pocket_clearance_per_edge']==.4
    assert labels['label_inset_from_window_edge']==.2 and labels['label_visible_height_when_inserted']==12.8
    assert labels['physical_validation']=='pending' and labels['electronic_rom_supplied'] is False
    assert set(labels['artwork_keys'])==ids
    assert labels['recognition_header_cartridge_y']==[8.4,20.0]
    assert labels['recognition_header_label_top_y']==[1.2,12.8]
    assert labels['recognition_header_cartridge_y'][1]<=labels['inserted_cartridge_exposed_y'][1]
    for f in (HERE/'cartridge-labels').glob('*.svg'):
        assert ET.parse(f).getroot().attrib['viewBox']=='0 0 336 386'
    assert {p.name for p in (HERE/'audio').iterdir()}=={batch}
    assert {p.name for p in (PUBLIC/'audio').iterdir()}=={batch}
    transcripts=json.loads((HERE/'qa/transcript-qa.json').read_text())
    assert transcripts['generator_sha256']==sha((ROOT/'scripts/check_narration_transcripts.py').read_bytes())
    assert transcripts['human_listening_approval']=='pending'
    assert len(transcripts['results'])==6
    for result,asset in zip(transcripts['results'],d['audio_assets']):
        assert result['story_id']==asset['story_id'] and result['language']==asset['language']
        assert result['audio_sha256']==asset['audio_sha256'] and result['script_sha256']==asset['script_sha256']
        assert result['transcript_file']=='qa/'+asset['story_id']+'.'+asset['language']+'.txt'
        assert sha((HERE/result['transcript_file']).read_bytes())==result['transcript_sha256']
    for f in HERE.glob('*.pdf'):assert f.read_bytes().startswith(b'%PDF-')
    sources={str((HERE/'validate.py').relative_to(ROOT)):sha((HERE/'validate.py').read_bytes())}
    sources.update({str((HERE/a['path'].removeprefix('content/')).relative_to(ROOT)):a['audio_sha256'] for a in d['audio_assets']})
    if measure:
        quality={'sources':sources,'measurements':media,'human_listening_approval':'pending','acoustic_validation':'pending'}
        (HERE/'audio-quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n')
        (PUBLIC/'audio-quality.json').write_bytes((HERE/'audio-quality.json').read_bytes())
    else:
        quality=json.loads((HERE/'audio-quality.json').read_text())
        assert quality['sources']==sources and len(quality['measurements'])==6
        assert (HERE/'audio-quality.json').read_bytes()==(PUBLIC/'audio-quality.json').read_bytes()
        for entry,asset in zip(quality['measurements'],d['audio_assets']):
            assert entry['sha256']==asset['audio_sha256'] and entry['full_decode']=='passed'
    print('PASS: revised bilingual scripts, neural model/voice/render provenance, complete batch hashes, credits, media QA and exact public mirrors; approvals pending.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--media',action='store_true')
    validate(parser.parse_args().media)
