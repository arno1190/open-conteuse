#!/usr/bin/env python3
"""Render prototype print solids and validate STL edge incidence/print-floor bounds."""
import concurrent.futures, csv,hashlib,json,struct,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARTS=['front','lid','carrier','battery_cover','mcu_retainer','regulator_retainer','switch_retainer','button','coupon','speaker_spacer']
def triangles(path):
 data=path.read_bytes()
 if len(data)>=84 and len(data)==84+50*struct.unpack_from('<I',data,80)[0]:
  for offset in range(84,len(data),50):yield [struct.unpack_from('<fff',data,offset+12+i*12) for i in range(3)]
 else:
  vs=[tuple(map(float,l.split()[1:])) for l in data.decode().splitlines() if l.strip().startswith('vertex ')]
  for i in range(0,len(vs),3):yield vs[i:i+3]
def binary_stl(path):
 tris=list(triangles(path));data=bytearray(b'Open Conteuse prototype STL'.ljust(80,b'\0'))
 data.extend(struct.pack('<I',len(tris)))
 for tri in tris:data.extend(struct.pack('<12fH',0,0,0,*tri[0],*tri[1],*tri[2],0))
 path.write_bytes(data)
def inspect(path):
 edges=Counter();lo=[float('inf')]*3;hi=[-float('inf')]*3;n=0
 for tri in triangles(path):
  n+=1;vs=[tuple(round(v,5) for v in p) for p in tri]
  for p in vs:
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
  for i in range(3):edges[tuple(sorted((vs[i],vs[(i+1)%3])))]+=1
 assert n and all(v==2 for v in edges.values()),f'non-manifold edges: {path}'
 assert lo[2]>=-0.0001,f'below print bed: {path}: {lo}'
 return {'triangles':n,'bounds_mm':[lo,hi],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def render(job):
 variant,part=job;folder=ROOT/'enclosure/integrated/print';path=folder/f'{variant}-{part}.stl'
 result=subprocess.run(['openscad','--hardwarnings','-D',f'variant="{variant}"','-D',f'part="{part}"','-o',str(path),str(ROOT/'enclosure/integrated/integrated.scad')],capture_output=True,text=True)
 (folder/f'{variant}-{part}.log').write_text(result.stdout+result.stderr)
 assert result.returncode==0,result.stderr
 assert 'Simple:        yes' in result.stderr,result.stderr
 assert 'Volumes:         2' in result.stderr,result.stderr
 binary_stl(path)
 return path.name,inspect(path)
def assembly_bom(results):
 path=ROOT/'enclosure/integrated/print/assembly_BOM.csv'
 with path.open('w',newline='') as f:
  writer=csv.writer(f,lineterminator='\n');writer.writerow(['variant','part','stl','quantity','material','sha256','bounds_mm'])
  for name,record in sorted(results.items()):
   variant,part=name[:-4].split('-',1);qty=2 if part=='mcu_retainer' else (5 if variant=='mini' else 8) if part=='button' else 1
   writer.writerow([variant,part,name,qty,'PETG',record['sha256'],json.dumps(record['bounds_mm'])])
def main():
 jobs=[(v,p) for v in ['mini','explore'] for p in PARTS]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=dict(pool.map(render,jobs))
 (ROOT/'enclosure/integrated/print/manifest.json').write_text(json.dumps({'prototype_only':True,'physical_validation':'pending','source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['enclosure/integrated/integrated.scad','enclosure/integrated/generated_data.scad']},'parts':results},indent=2)+'\n')
 assembly_bom(results)
 print(f'{len(results)} STL exports: closed two-manifold edges and nonnegative print Z.')
if __name__=='__main__':main()
