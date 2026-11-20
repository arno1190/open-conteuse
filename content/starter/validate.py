#!/usr/bin/env python3
"""Validate editorial/publication boundaries and exact public mirror (stdlib only)."""
import json, math, hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
public=HERE.parents[1]/'site/content'
d=json.loads((HERE/'index.json').read_text())
assert d['schema_version']==1
assert d['status']=='editorial_draft'
assert d['script_approval']==d['audio_approval']=='pending'
assert len(d['audio_assets'])==6
assert len(d['stories'])==3
ids=set()
for s in d['stories']:
 assert s['id'] not in ids;ids.add(s['id'])
 assert s['script_approval']==s['audio_approval']=='pending'
 assert s['recording']['audio_file'] is None
 for lang in ['fr','en']:
  z=s[lang];assert len(z['script'].split())==z['word_count']
  assert 250<=z['word_count']<=400
  assert z['activity'] and z['card_activity']
  md=(HERE/(s['id']+'.'+lang+'.md')).read_text()
  assert z['script'] in md and z['activity'] in md
 for suffix in ['','-back']:
  f=HERE/'cards'/(s['id']+suffix+'.svg')
  xml=ET.parse(f).getroot()
  assert xml.tag.endswith('svg')
  assert not any(x.tag.endswith('script') for x in xml.iter())
 assert s['art']=='content/cards/'+s['id']+'.svg'
for name in ['index.json','cards.pdf','collection.pdf','cartridge-labels.pdf','cartridge-labels.json','audio-generation.json']+[str(f.relative_to(HERE)) for f in (HERE/'cards').glob('*.svg')]:
 assert (HERE/name).read_bytes()==(public/name).read_bytes(),name
spec=json.loads((HERE/'cartridge-labels.json').read_text())
assert spec['label_size']==[33.6,38.6]
assert spec['recess_xy']==[3,4,37,43]
assert spec['label_xy']==[3.2,4.2,36.8,42.8]
a,b,c,e=spec['label_xy'];ra,rb,rc,re=spec['recess_xy']
assert math.isclose(c-a,spec['label_size'][0]) and math.isclose(e-b,spec['label_size'][1])
assert all(math.isclose(x,spec['nominal_edge_clearance']) for x in [a-ra,b-rb,rc-c,re-e])
assert spec['maximum_total_paper_adhesive_thickness']==.15
assert spec['physical_validation']=='pending' and spec['electronic_rom_supplied'] is False
assert set(spec['artwork_keys'])==ids
assert spec['inserted_cartridge_exposed_y']==[0,20]
assert math.isclose(spec['label_visible_height_when_inserted'],20-spec['label_xy'][1])
assert spec['recognition_header_label_top_y']==[1.2,14.0]
assert spec['recognition_header_cartridge_y']==[5.4,18.2]
assert all(math.isclose(label_y+spec['label_xy'][1],cartridge_y) for label_y,cartridge_y in zip(spec['recognition_header_label_top_y'],spec['recognition_header_cartridge_y']))
assert spec['recognition_header_cartridge_y'][1]<spec['inserted_cartridge_exposed_y'][1]
for f in (HERE/'cartridge-labels').glob('*.svg'):
 assert f.read_bytes()==(public/'cartridge-labels'/f.name).read_bytes()
 xml=ET.parse(f).getroot();assert xml.attrib['viewBox']=='0 0 336 386'
audio_seen=set()
receipt=json.loads((HERE/'audio-generation.json').read_text())
assert receipt['audio_assets']==d['audio_assets']
assert receipt['status']=='synthetic_draft_demo' and receipt['final_audio_approval']=='pending'
for asset in d['audio_assets']:
 key=(asset['story_id'],asset['language']);assert key not in audio_seen;audio_seen.add(key)
 story=next(st for st in d['stories'] if st['id']==asset['story_id']);z=story[asset['language']]
 assert z['preview_audio']==asset['path']
 assert asset['status']=='synthetic_draft_demo' and asset['approval']==asset['final_audio_approval']=='pending'
 assert hashlib.sha256(z['script'].encode()).hexdigest()==asset['script_sha256']
 assert asset['path']=='content/audio/'+asset['story_id']+'.'+asset['language']+'.mp3'
 f=HERE/'audio'/Path(asset['path']).name
 assert hashlib.sha256(f.read_bytes()).hexdigest()==asset['audio_sha256']
 assert f.stat().st_size==asset['bytes']
 assert 120<asset['duration_seconds']<480
 assert asset['channels']==1 and asset['sample_rate_hz']==22050 and asset['codec']=='mp3'
 assert f.read_bytes()==(public/'audio'/f.name).read_bytes()
assert audio_seen=={(i,l) for i in ids for l in ['fr','en']}
for f in HERE.glob('*.pdf'):assert f.read_bytes().startswith(b'%PDF-')
print('PASS: 3 original bilingual drafts; 6 scripts and SVG faces; 6 local synthetic draft MP3s with exact script/audio hashes; no approved audio; public assets byte-identical.')
