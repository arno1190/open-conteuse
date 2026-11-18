"""Blender regression checks for real section voids and actuator alignment.
Run after prepare_atlas.py: blender -b --python scripts/check_atlas_geometry.py
"""
import json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy,render_atlas as a
from atlas_plan import native_board_point
from mathutils import Matrix
for ident in ['controls','mute_latch']:
 origin=Vector(native_board_point(ident,(0,0,0)));basis=[]
 for i in range(3):
  point=[0,0,0];point[i]=.001;basis.append(Vector(native_board_point(ident,point))-origin)
 assert abs(Matrix(basis).determinant()-1)<1e-5,'Mirrored native PCB: '+ident
 assert (native_board_point(ident,(.03,-.03,.0016))[2]<native_board_point(ident,(.03,-.03,0))[2])==(ident=='controls')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
o=a.stl('case',ROOT/'enclosure/integrated/print/mini-front.stl','case','case','front');a.bisect(o,2,15,'low')
areas=[p.area for p in o.data.polygons if o.data.materials[p.material_index].name=='cut']
assert 1500<sum(areas)<3000 and max(areas)<3000,('Section incorrectly filled a hollow interior',sum(areas),max(areas))
a.PCB=json.loads((ROOT/'work/atlas/pcb.json').read_text());pose=next(p for p in a.L['common'] if p['part']=='controls');a.custom_components('controls',pose,'explore')
centres=json.loads((ROOT/'enclosure/controls.json').read_text())['actuators_mm']
for i,xy in enumerate(centres):
 obj=next(o for o in a.objects if o.name=='SW'+str(i+1)+' actuator');actual=sum((o.matrix_world@v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
 expected=[xy[j]+pose['xyz'][j] for j in range(2)]
 assert all(abs(actual[j]-expected[j])<1e-4 for j in range(2)),(i,actual,expected)
print('ATLAS_GEOMETRY_PASS: hollow case section preserved; all8actuators align with frozen controls centres.')
