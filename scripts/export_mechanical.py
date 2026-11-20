#!/usr/bin/python3
"""Read current routed-board body/pad positions and write enclosure inputs."""
import json
from pathlib import Path
import pcbnew as p
from project import HARDWARE,ENCLOSURE,VARIANTS

def read(name):
 path=HARDWARE/name;d=json.loads((path/'components.json').read_text());b=p.LoadBoard(str(path/(name+'.kicad_pcb')));fs={f.GetReference():f for f in b.GetFootprints()}
 for r in d['parts']:
  f=fs[r['ref']];r['xy']=[round(p.ToMM(f.GetPosition().x)-30,4),round(p.ToMM(f.GetPosition().y)-30,4)];r['angle']=f.GetOrientationDegrees()
  shapes=[q.GetBoundingBox() for q in f.GraphicalItems() if q.GetLayer()==p.F_Fab and isinstance(q,p.PCB_SHAPE)]
  lo=[min(p.ToMM(q.GetLeft()) for q in shapes)-30,min(p.ToMM(q.GetTop()) for q in shapes)-30] if shapes else [r['xy'][i]-r['size'][i]/2 for i in (0,1)]
  hi=[max(p.ToMM(q.GetRight()) for q in shapes)-30,max(p.ToMM(q.GetBottom()) for q in shapes)-30] if shapes else [lo[i]+r['size'][i] for i in (0,1)]
  r['body_box']=[*map(lambda x:round(x,4),lo),11.7,round(hi[0]-lo[0],4),round(hi[1]-lo[1],4),r['size'][2]]
  r['pads']=[dict(xy=[round(p.ToMM(q.GetPosition().x)-30,4),round(p.ToMM(q.GetPosition().y)-30,4)],size=[p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)],net=q.GetNetname(),pin=q.GetNumber()) for q in f.Pads() if q.GetLayerSet().Contains(p.F_Cu)]
 d['physical_validation']='pending';d['fabrication_release']=False;d.get('sources',{}).pop('nfc',None);d.get('sources',{}).pop('nfc_manual',None)
 return d
for v in VARIANTS:
 d=read(v)
 d['extras']=[dict(id='cell',mpn='Adafruit 258',box=[15.5,24,3,34,62,5],color='battery',basis='supplier nominal; measure actual protection/lead envelope'),dict(id='speaker',mpn='AS01508AO-WP-R',box=[34,78.9,18.4,15,11,3],color='black',basis='supplier nominal; gasket and cable qualification pending')]
 d['clearance_reserves']=[dict(id='battery_service',box=[14.5,23,2.5,36,64,7]),dict(id='wifi_keepout',box=[8.5,0,0,48,9,24]),dict(id='usb_plug',box=[45.3,d['case'][1]-7,10.1,11.4,12,6.4]),dict(id='headphone_plug',box=[24.6,d['case'][1]-5,9.8,8.8,12,8.8])]
 if v=='explore':
  d['extras'] += [dict(id='lcd',mpn='RB024D18N01B1',box=[3.37,7,19.45,60.26,42.72,2.55],color='glass',basis='drawing2.55mm; received FPC face/tail pending'),dict(id='lens',mpn='OC-LENS-EX-R1',box=[6,8.5,22.5,55,40,.5],color='glass',basis='drawing-defined cut polycarbonate')]
  d['clearance_reserves'].append(dict(id='fpc_fold',box=[61,10,15,3.5,35,6.5]))
 (HARDWARE/v/'mechanical.json').write_text(json.dumps(d,indent=2)+'\n')
 def a(x):return json.dumps(x,separators=(',',':'))
 buttons=[r for r in d['parts'] if r['section']=='controls' and r['ref'].startswith('SW')]
 rows=['// Generated from current native PCB and explicit nominal peripheral envelopes.','dims='+a(d['case'])+';','main_polygon='+a(d['pcb']['edge_polygon'])+';','holes='+a(d['pcb']['holes'])+';','buttons='+a([r['xy'] for r in buttons])+';','button_names='+a([r['pins']['1'].replace('KEY_','') for r in buttons])+';','bodies='+a([r['body_box'] for r in d['parts'] if not r['ref'].startswith(('H','TP'))])+';','body_refs='+a([r['ref'] for r in d['parts'] if not r['ref'].startswith(('H','TP'))])+';','extras='+a([r['box'] for r in d['extras']])+';','extra_names='+a([r['id'] for r in d['extras']])+';','reserves='+a([r['box'] for r in d['clearance_reserves']])+';']
 (ENCLOSURE/(v+'-data.scad')).write_text('\n'.join(rows)+'\n')
reader=read('card-reader');boxes=[]
for r in reader['parts']:
 if r['ref'].startswith(('P','H')):continue
 b=r['body_box'];b=[round(b[0]+8.5,4),round(b[1]+29,4),14.95,*b[3:]];r['case_body_box']=b;boxes.append(b)
(HARDWARE/'card-reader/mechanical.json').write_text(json.dumps(reader,indent=2)+'\n')
(HARDWARE/'story-card/mechanical.json').write_text(json.dumps(read('story-card'),indent=2)+'\n')
(ENCLOSURE/'contact-data.scad').write_text('// Reader body envelopes; springs and PCBs are separate exact nominal geometry.\nreader_bodies='+json.dumps(boxes,separators=(',',':'))+';\nreader_polygon='+json.dumps(reader['pcb']['edge_polygon'])+';\nreader_holes='+json.dumps(reader['pcb']['holes'])+';\n')
