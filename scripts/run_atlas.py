#!/usr/bin/env python3
"""Run the full atlas render with frozen-input and completion receipts."""
import datetime,hashlib,json,re,subprocess,time
from pathlib import Path
from atlas_plan import views
from integrated_hardware import ROOT
OUT=ROOT/'docs/visual-atlas';WORK=ROOT/'work/atlas'
def source_hashes():
 paths=[ROOT/p for p in ['scripts/render_atlas.py','scripts/atlas_plan.py','scripts/integrated_hardware.py','scripts/export_integrated.py','hardware/integration/catalog.json','hardware/integration/layout.json','enclosure/controls.json','hardware/controls/controls.kicad_pcb','hardware/integration/mute-latch/mute-latch.kicad_pcb']]
 paths+=sorted((ROOT/'enclosure/integrated/print').glob('*.stl'))
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def receipt(log,inputs,started,prepared):
 names=re.findall(r'^ATLAS_RENDERED (\S+\.png)$',log.read_text(),re.M);expected={v+'-'+s['id']+'.png' for v in ['mini','explore'] for s in views(v)}
 assert len(names)==len(expected)==72 and set(names)==expected,'Render run did not complete every planned view exactly once'
 assert 'Traceback (most recent call last)' not in log.read_text(),'Renderer raised an error'
 assert source_hashes()==inputs,'Render inputs changed during run'
 images={}
 for name in names:
  p=OUT/'images'/name;assert p.stat().st_mtime>=started-1,'Old figure survived render: '+name
  images[name]=hashlib.sha256(p.read_bytes()).hexdigest()
 result={'started_utc':datetime.datetime.fromtimestamp(started,datetime.timezone.utc).isoformat(),'source_sha256':inputs,'prepared_inputs_sha256':prepared,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'completed_views':names,'images_sha256':images,'physical_validation':'pending'}
 (OUT/'render-completion.txt').write_text('\n'.join('ATLAS_RENDERED '+name for name in names)+'\n')
 (OUT/'render-receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
 WORK.mkdir(parents=True,exist_ok=True);inputs=source_hashes();prepared={name:hashlib.sha256((WORK/name).read_bytes()).hexdigest() for name in ['manufacturer.json.gz','controls.glb','mute_latch.glb','pcb.json']};started=time.time();log=WORK/'render-final.log'
 with log.open('w') as f:subprocess.run(['blender','-b','-t','8','--python',str(ROOT/'scripts/render_atlas.py'),'--','--samples','24'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
 receipt(log,inputs,started,prepared);print('72 views rendered with frozen source inputs and image-hash receipt.')
if __name__=='__main__':main()
