#!/usr/bin/env python3
"""Record printable mesh quantities and source/artifact integrity, never a quote."""
import json,hashlib
from compact_design import ROOT,OUT
from compact_mesh import inspect
from export_integrated import binary_stl
E=ROOT/'enclosure/compact-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prints():
 receipt=json.loads((E/'mesh-receipt.json').read_text())
 for name,value in receipt['sources'].items():assert sha(ROOT/name)==value,('mesh input changed',name)
 result={'mesh_sources':receipt['sources'],'material_assumption':'PETG, density1.27g/cm3, EUR25/kg; dense solid mesh upper bound,10% waste; slicer time/support pending','physical_validation':'pending','parts':{}}
 for v in ['mini','explore']:
  total=0
  for part in ['front','back','print_front','button','buttons','coupon','bridge']:
   path=E/f'print/{v}-{part}.stl';binary_stl(path);r=inspect(path);r['mass_dense_g']=round(r['volume_cm3']*1.27,2);r['material_upper_eur']=round(r['mass_dense_g']*.025*1.1,2);r['quantity_in_device']=1 if part in ['print_front','back','buttons','bridge'] else 0
   if r['quantity_in_device']:total+=r['mass_dense_g']
   result['parts'][str(path.relative_to(ROOT))]=r
  result[v+'_set_dense_mass_g']=round(total,2);result[v+'_set_material_upper_eur']=round(total*.025*1.1,2)
 (E/'print-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
def manifest():
 paths=[]
 for folder in ['hardware/compact-r1','enclosure/compact-r1','docs/compact-r1']:
  paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='manifest.json' and not p.name.endswith(('.lck','~','.kicad_prl')))
 paths.extend(p for p in (ROOT/'scripts').glob('*compact*') if p.is_file());paths.extend(ROOT/p for p in ['scripts/kicad_sexp.py','firmware/src/compact_bringup.cpp','firmware/platformio.ini'])
 m={'revision':'compact-r1','physical_validation':'pending','fabrication_release':False,'orders_placed':False,'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}}
 (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':
 import sys
 if '--prints' in sys.argv:prints()
 else:manifest()
