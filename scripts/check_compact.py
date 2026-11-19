#!/usr/bin/env python3
"""Check compact artefact integrity, cost scope and mechanical-source consistency.
Native ERC/DRC and full CGAL intersections are handled by compact-check.sh.
"""
from pathlib import Path
import csv,json,hashlib,sys,math
from compact_design import ROOT,OUT
from compact_mesh import inspect
from export_integrated import triangles

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def overlaps(a,b):return all(min(a[i]+a[i+3],b[i]+b[i+3])-max(a[i],b[i])>1e-4 for i in range(3))
def run(check_manifest=True):
 for v in ['mini','explore']:
  d=json.loads((OUT/(v+'-mechanical.json')).read_text());rows={p['ref']:p for p in d['parts']};case=d['case'];assert d['physical_validation']=='pending' and d['fabrication_release'] is False
  assert d['pcb']['holes']==[[6,56],[59,56],[6,88],[59,88]]
  with (OUT/(v+'-BOM.csv')).open() as f:bom={r['reference']:r for r in csv.DictReader(f)}
  for ref,p in rows.items():
   if ref.startswith(('H','TP')):continue
   assert bom[ref]['mpn']==p['mpn'],(v,ref,'BOM mismatch')
   for e in d['extras']:assert not overlaps(p['body_box'],e['box']),(v,ref,e['id'],'body overlap')
  assert rows['U1']['pins']['28'] is None and rows['U1']['pins']['29'] is None and rows['U1']['pins']['30'] is None
  assert rows['U3']['pins']['1']=='VINA' and rows['U3']['pins']['13']=='SYS'
  assert rows['U5']['pins']['3']=='1V8' and 'EP3.45x3.45' in rows['U5']['footprint']
  assert rows['J1']['angle']==0 and rows['J2']['angle']==90 and rows['SW9']['angle']==270
  if v=='mini':
   antenna=next(e['box'] for e in d['extras'] if e['id']=='nfc_antenna');assert abs(antenna[2]+antenna[5]-(case[2]-1.8))<.001
  for part in ['front','back','print_front','button','buttons','coupon','bridge']:
   result=inspect(ROOT/f'enclosure/compact-r1/print/{v}-{part}.stl');expected=(5 if v=='mini' else 8) if part=='buttons' else 1
   assert result['components']==expected,(v,part,result['components']);assert result['bounds_mm'][0][2]>=-.0001
  # Verify actual physical mesh handedness against native-PCB canonical Y-down.
  mesh=ROOT/f'enclosure/compact-r1/print/{v}-front.stl';vertices={tuple(round(c,3) for c in q) for tri in triangles(mesh) for q in tri}
  pm=ROOT/f'enclosure/compact-r1/print/{v}-print_front.stl';printed={tuple(round(c,3) for c in q) for tri in triangles(pm) for q in tri}
  for p in rows.values():
   if p['section']=='controls' and p['ref'].startswith('SW'):
    x,y=p['xy'];assert (round(x+3.7,3),round(case[1]-y,3),case[2]) in vertices,(v,p['ref'],'assembly handedness')
    assert (round(x+3.7,3),round(y,3),0) in printed,(v,p['ref'],'front print orientation')
  receipt=ROOT/f'docs/compact-r1/{v}-render-receipt.json'
  if check_manifest:
   r=json.loads(receipt.read_text());assert len(r['images'])==20
   for fn,h in r['sources'].items():assert sha(ROOT/fn)==h,('render source stale',fn)
   for fn,h in r['images'].items():assert sha(ROOT/fn)==h,('image stale',fn)
 if check_manifest:
  for filename,count,output_key in [('enclosure/compact-r1/mesh-receipt.json',14,'meshes'),('docs/compact-r1/document-receipt.json',5,'outputs')]:
   receipt=json.loads((ROOT/filename).read_text());assert receipt['physical_validation']=='pending' and len(receipt[output_key])==count
   for name,value in receipt['sources'].items():assert sha(ROOT/name)==value,('source receipt stale',name)
   for name,value in receipt[output_key].items():assert sha(ROOT/name)==(value['sha256'] if isinstance(value,dict) else value),('output receipt stale',name)
 c=json.loads((OUT/'costs.json').read_text());assert c['assumptions']['quote_status']=='no binding supplier or fabrication quote' and not c['assumptions']['orders_placed']
 if check_manifest:
  verification=json.loads((OUT/'verification.json').read_text());assert verification['physical_validation']=='pending' and verification['fabrication_release'] is False and verification['orders_placed'] is False
  for fn,h in verification['source_hashes'].items():assert sha(ROOT/fn)==h,('verification source stale',fn)
  m=json.loads((OUT/'manifest.json').read_text());assert m['physical_validation']=='pending' and not m['fabrication_release']
  for fn,h in m['files'].items():assert sha(ROOT/fn)==h,('artefact stale',fn)
 print('Compact R1 nominal body fit, PCB/BOM identities, mesh integrity, costs and artefact hashes agree. Physical validation pending.')
if __name__=='__main__':run('--geometry-only' not in sys.argv)
