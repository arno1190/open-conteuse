#!/usr/bin/env python3
"""Render/check all compact printable solids and nominal interference diagnostics."""
import concurrent.futures,hashlib,json,subprocess,shutil
from pathlib import Path
from compact_design import ROOT
from compact_mesh import inspect
from export_integrated import binary_stl,triangles
E=ROOT/'enclosure/compact-r1';W=ROOT/'work/compact-r1';W.mkdir(parents=True,exist_ok=True)
PARTS=['front','back','print_front','button','buttons','coupon','bridge']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[E/'compact.scad',*[E/(v+'-data.scad') for v in ['mini','explore']],*[ROOT/f'hardware/compact-r1/{v}-mechanical.json' for v in ['mini','explore']],ROOT/'scripts/export_compact_meshes.py',ROOT/'scripts/compact_mesh.py',ROOT/'scripts/export_integrated.py']
sources={str(p.relative_to(ROOT)):sha(p) for p in inputs}
def geometry(path):
 # OpenSCAD may permute triangles between processes. Compare exact float32
 # oriented triangles independently of their order/cyclic vertex origin.
 return sorted(min(tuple(t[i:]+t[:i]) for i in range(3)) for tri in triangles(path) for t in [[tuple(x) for x in tri]])

def render(job):
 v,part=job;empty=part in ['interference','shell_interference'];path=E/f'print/{v}-{part}.stl' if part in PARTS else W/f'{v}-{part}.stl';path.parent.mkdir(exist_ok=True);target=path;path=W/'reexport'/f'{v}-{part}.stl';path.parent.mkdir(exist_ok=True);path.unlink(missing_ok=True)
 result=subprocess.run(['openscad','--hardwarnings','-D',f'variant="{v}"','-D',f'part="{part}"','-o',str(path),str(E/'compact.scad')],capture_output=True,text=True);log=result.stdout+result.stderr;(W/f'{v}-{part}.log').write_text(log)
 if empty:
  assert result.returncode!=0 and 'Current top level object is empty' in log and not path.exists(),(v,part,log)
  print(v,part,'empty',flush=True);return v,part,{'empty':True}
 assert result.returncode==0 and 'Simple:        yes' in log and 'WARNING:' not in log and 'ERROR:' not in log,(v,part,log)
 binary_stl(path)
 if not target.exists() or geometry(path)!=geometry(target):shutil.copyfile(path,target)
 stats=inspect(target);expected=(5 if v=='mini' else 8) if part=='buttons' else 1;assert stats['components']==expected,(v,part,stats);assert stats['bounds_mm'][0][2]>=-.0001
 print(v,part,'manifold',flush=True);return v,part,stats
jobs=[(v,part) for v in ['mini','explore'] for part in PARTS+['pcb','interference','shell_interference']]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(render,jobs))
assert sources=={str(p.relative_to(ROOT)):sha(p) for p in inputs},'Inputs changed during mesh export'
# Temporary PCB reference meshes are regenerated on fresh runners. Their
# geometric statistics are stable; their triangle-order byte hashes are not.
# The render receipt separately records the exact prepared mesh actually used.
receipt={'physical_validation':'pending','fabrication_release':False,'sources':sources,'meshes':{str((E/f'print/{v}-{part}.stl').relative_to(ROOT)):r for v,part,r in results if part in PARTS},'intersections':{v+'/'+part:r for v,part,r in results if part.endswith('interference')},'reference_meshes':{v:{k:value for k,value in r.items() if k!='sha256'} for v,part,r in results if part=='pcb'}}
(E/'mesh-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('14 printable meshes and both nominal assemblies checked. Physical validation pending.')
