#!/usr/bin/env python3
"""Check atlas coverage and source/artifact integrity, never physical fit."""
import hashlib,json,re,struct
from pathlib import Path
from atlas_plan import views
from integrated_hardware import ROOT,read_data,indexed
FOLDER=ROOT/'docs/visual-atlas'
def check():
 m=json.loads((FOLDER/'manifest.json').read_text());expected={(v,s['id']) for v in ['mini','explore'] for s in views(v)};found={(s['variant'],s['id']) for s in m['views']}
 assert expected==found and len(found)==72,'Incomplete view coverage'
 assert {p.name for p in (FOLDER/'images').glob('*.png')}=={v+'-'+id+'.png' for v,id in expected},'Unexpected or stale figures in image directory'
 for v in ['mini','explore']:
  rows=[s for s in m['views'] if s['variant']==v]
  assert sum(s['mode']=='section' for s in rows)==8
  assert sum(s['id'].startswith('orthographic-') for s in rows)==6
 for name,digest in m['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Changed source: '+name
 for name,digest in m['artifacts_sha256'].items():assert hashlib.sha256((FOLDER/name).read_bytes()).hexdigest()==digest,'Changed artifact: '+name
 for s in m['views']:
  data=(FOLDER/s['file']).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
  assert struct.unpack('>II',data[16:24])==(1440,1080),'Unexpected output size'
  if s['cut']:
   axis,value,keep=s['cut'];assert 0<value<[112,210,50][axis] and keep in ['low','high']
 receipt=json.loads((FOLDER/'render-receipt.json').read_text())
 assert len(receipt['completed_views'])==72 and len(set(receipt['completed_views']))==72
 for name,digest in receipt['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Render input changed: '+name
 for name,digest in receipt['images_sha256'].items():assert hashlib.sha256((FOLDER/'images'/name).read_bytes()).hexdigest()==digest,'Figure differs from render receipt: '+name
 assert m['physical_validation']=='pending'
 pdf=FOLDER/'Open-Conteuse-Visual-Atlas.pdf';assert pdf.read_bytes().startswith(b'%PDF-')
 assert len(re.findall(rb'/Type\s*/Page\b',pdf.read_bytes()))==m['pdf_pages'],'PDF page count mismatch'
 print(f"Atlas:72PNGviews,16sections,{len(m['sheets'])}sheets,{m['pdf_pages']}PDFpages; sources and artifact hashes verified. Physical validation pending.")
if __name__=='__main__':check()
