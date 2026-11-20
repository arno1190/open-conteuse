"""Current CAD exports and objective mesh checks. Physical fit remains pending."""
import concurrent.futures,json,subprocess,hashlib
from pathlib import Path
from mesh import inspect
from project import ROOT,WORK,ENCLOSURE,VARIANTS,PARTS
WORK.mkdir(parents=True,exist_ok=True)
def export(job):
 source,out,defs,empty=job;out.parent.mkdir(parents=True,exist_ok=True)
 cmd=['openscad','--hardwarnings']
 for k,v in defs.items():cmd+=['-D',k+'='+json.dumps(v)]
 cmd+=['-o',str(out),str(source)]
 p=subprocess.run(cmd,capture_output=True,text=True);log=p.stdout+p.stderr
 (WORK/(out.stem+'.log')).write_text(log)
 if empty:
  assert 'Current top level object is empty' in log and not out.exists(),(out,log)
  return str(out.relative_to(ROOT)),{'empty':True}
 assert p.returncode==0 and 'WARNING' not in log and 'ERROR' not in log,(out,log)
 info=inspect(out)
 if 'wrong_card' in out.name:assert info['volume_cm3']>0
 elif out.stem.endswith('-plugs'):assert info['components']==2,(out,info)
 elif out.stem not in ('buttons','components','peripherals','assembly','exploded'):assert info['components']==1,(out,info)
 return str(out.relative_to(ROOT)),info
frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ENCLOSURE.glob("*.scad"))}
jobs=[]
for v in VARIANTS:
 data=json.loads((ROOT/f'hardware/{v}/components.json').read_text())
 count=sum(r['section']=='controls' and r['ref'].startswith('SW') for r in data['parts'])
 for i in range(count):jobs.append((ENCLOSURE/'design.scad',ENCLOSURE/'print'/v/(f'cap_{i}.stl'),dict(variant=v,part=f'cap_{i}'),False))
 for part in PARTS:jobs.append((ENCLOSURE/'design.scad',ENCLOSURE/'print'/v/(part+'.stl'),dict(variant=v,part=part),False))
 jobs.append((ENCLOSURE/'design.scad',WORK/(v+'-plugs.stl'),dict(variant=v,part='plugs'),False))
 jobs.append((ENCLOSURE/'design.scad',WORK/(v+'-pcb.stl'),dict(variant=v,part='pcb'),False))
 for part in ('shell_interference','interference','internal_interference','cap_shell_interference','cap_pair_interference','headphone_plug_clearance','usb_plug_clearance'):
  jobs.append((ENCLOSURE/'design.scad',WORK/(v+'-'+part+'.stl'),dict(variant=v,part=part),True))
jobs.append((ENCLOSURE/'design.scad',WORK/'mini-reader-pcb.stl',dict(variant='mini',part='reader_pcb'),False))
# Slow sweep is a separate explicit geometry gate.
for part in ('front','back','print_front','pcb'):
 jobs.append((ENCLOSURE/'card.scad',ENCLOSURE/'print/story-card'/(part+'.stl'),dict(part=part),False))
for part in ('wrong_card_interference','card_sweep_interference'):
 jobs.append((ENCLOSURE/'design.scad',WORK/(part+'.stl'),dict(variant='mini',part=part),part=='card_sweep_interference'))
for _,out,_,_ in jobs:
 if out.exists():out.unlink()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=dict(pool.map(export,jobs))
sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ENCLOSURE.glob('*.scad'))}
assert sources==frozen,'CAD inputs changed during export'
(ENCLOSURE/'mesh-checks.json').write_text(json.dumps(dict(physical_validation='pending',sources=sources,exports=records),indent=2)+'\n')
print('Current enclosure meshes and collision checks passed')
