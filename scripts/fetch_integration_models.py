#!/usr/bin/env python3
"""Verify and cache upstream STEP files; optionally rebuild normalized reference meshes.

Requires CadQuery2.8 for --rebuild. Re-export byte hashes can vary with OCCT builds;
never silently update catalogue hashes after a mismatch.
"""
import argparse,hashlib,urllib.request
from pathlib import Path
from integrated_hardware import read_data,ROOT
parser=argparse.ArgumentParser();parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
c,_=read_data();folder=ROOT/'work/integration-sources';folder.mkdir(parents=True,exist_ok=True)
for p in c['parts']:
 if not p.get('model'):continue
 m=p['model'];path=folder/(p['id']+'.step')
 if not path.exists():
  req=urllib.request.Request(m['source_url'],headers={'User-Agent':'OpenConteuseCAD/1.0'})
  with urllib.request.urlopen(req,timeout=60) as response:data=response.read(32000000)
  path.write_bytes(data)
 data=path.read_bytes()
 assert hashlib.sha256(data).hexdigest()==m['source_sha256'],p['id']+' source SHA256 mismatch'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==m['source_git_blob_sha1'],p['id']+' Git blob mismatch'
 if args.rebuild:
  import cadquery as cq
  shape=cq.importers.importStep(str(path)).translate(tuple(m['normalization_translation_mm']))
  output=folder/(p['id']+'.stl');cq.exporters.export(shape,str(output),exportType='STL',tolerance=.06,angularTolerance=.15,opt={'ascii':False})
  print(p['id'],'rebuilt in work cache; compare geometry/hash before manually replacing versioned model:',hashlib.sha256(output.read_bytes()).hexdigest())
 else:print(p['id'],'verified source')
