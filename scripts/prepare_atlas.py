#!/usr/bin/env python3
"""Prepare solid-resolved manufacturer CAD and native KiCad reference geometry.

This creates visual assets only; it never edits manufacturing/enclosure geometry.
Requires CadQuery2.7, KiCad9 pcbnew via /usr/bin/python3 and kicad-cli.
"""
import gzip,hashlib,json,os,subprocess,urllib.request
from pathlib import Path
from integrated_hardware import ROOT,read_data
OUT=ROOT/'work/atlas';OUT.mkdir(parents=True,exist_ok=True)
def classify(p,b):
 d=[b.xlen,b.ylen,b.zlen];pcb=p.get('pcb');ident=p['id']
 if ident=='battery':return 'foil'
 if ident=='speaker' or ident=='power_switch':return 'black'
 if pcb:
  origin=pcb['origin_in_model_mm'];dim=pcb['size_mm']
  if d[0]>dim[0]*.85 and d[1]>dim[1]*.85 and abs(b.zmin-origin[2])<.15 and abs(d[2]-dim[2])<.2:return 'pcb_blue'
 if ident=='display' and b.zmax<3.6 and d[0]*d[1]>200:return 'glass'
 if ident=='charger' and b.ymax>25.5:return 'metal'
 if ident=='sd' and d[0]*d[1]>50:return 'metal'
 if ident=='headphone' and b.xmax>31.9:return 'black'
 if min(d)<.35:return 'metal'
 if d[0]*d[1]<2.5:return 'ceramic' if d[2]<1.6 else 'black'
 return 'black'
def prepare():
 import cadquery as cq
 cat,_=read_data();results={}
 for p in cat['parts']:
  if not p.get('model'):continue
  m=p['model'];source=ROOT/'work/integration-sources'/(p['id']+'.step');old=ROOT/'work/integration-research/manufacturer'/(p['part_number']+'.step')
  if not source.exists() and old.exists():source=old
  if not source.exists():
   source.parent.mkdir(exist_ok=True,parents=True)
   with urllib.request.urlopen(m['source_url'],timeout=60) as r:source.write_bytes(r.read())
  assert hashlib.sha256(source.read_bytes()).hexdigest()==m['source_sha256'],p['id']
  assembly=cq.importers.importStep(str(source)).translate(tuple(m['normalization_translation_mm']));rows=[]
  for solid in assembly.solids().vals():
   verts,faces=solid.tessellate(.10,.20);b=solid.BoundingBox()
   rows.append({'vertices':[[v.x,v.y,v.z] for v in verts],'faces':faces,'material':classify(p,b)})
  results[p['id']]=rows;print(p['id'],len(rows),'manufacturer solids',flush=True)
 with gzip.open(OUT/'manufacturer.json.gz','wt') as f:json.dump(results,f,separators=(',',':'))
 env=os.environ.copy();env.update(XDG_CONFIG_HOME=str(ROOT/'work/config'),XDG_CACHE_HOME=str(ROOT/'work/cache'),XDG_DATA_HOME=str(ROOT/'work/data'))
 for ident,source in [('controls','hardware/controls/controls.kicad_pcb'),('mute_latch','hardware/integration/mute-latch/mute-latch.kicad_pcb')]:
  subprocess.run(['kicad-cli','pcb','export','glb','--force','--include-tracks','--include-pads','--include-silkscreen','--include-soldermask','--no-components','-o',str(OUT/(ident+'.glb')),str(ROOT/source)],check=True,env=env,capture_output=True)
 subprocess.run(['/usr/bin/python3',str(ROOT/'scripts/atlas_pcb_geometry.py')],check=True,env=env)
if __name__=='__main__':prepare()
