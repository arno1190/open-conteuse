"""Dedicated source-derived cartridge views, including its replaceable picture stack."""
import bpy,bmesh,hashlib,json,sys,subprocess
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
# Share mesh/material/camera primitives without running the player render loop.
helper=ROOT/'scripts/render_design.py'
ns={'__file__':str(helper),'__name__':'card_helpers'}
exec(compile(helper.read_text().split('\nviews=')[0],str(helper),'exec'),ns)
cube,stl,cylinder,mesh,mat=[ns[x] for x in ('cube','stl','cylinder','mesh','mat')]
ns['colors']['clear']=(.55,.83,.92,.25)
inputs=['scripts/render_card.py','scripts/render_design.py','scripts/annotate_card_views.py','enclosure/card.scad','enclosure/card-window.svg','hardware/story-card/story-card.kicad_pcb','docs/design/textures/milo-moon-post.png','content/starter/cartridge-labels.pdf']+[f'enclosure/print/story-card/{p}.stl' for p in ('front','back','pcb')]
frozen={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
metadata={};records={}
for view in ('exploded','front','rear','section'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);ns['objects'].clear()
 exploded=view=='exploded';offset={'back':0,'pcb':8 if exploded else 0,'picture':16 if exploded else 0,'window':24 if exploded else 0,'front':32 if exploded else 0}
 for part,color in [('back','button'),('front','button'),('pcb','green')]:
  obj=stl('Card '+part,ROOT/f'enclosure/print/story-card/{part}.stl',color,part)
  for vertex in obj.data.vertices:vertex.co.y=60-vertex.co.y
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.location.z+=offset[part]
 z=offset['pcb'];cube('DS2401P+',[18.12,51.03,1.3+z,3.76,3.94,1.5],'black','pcb')
 # The two native bottom wear lanes, on the exposed underside of the board.
 for x,y,h in [(15.5,48,10),(21.5,48,8)]:cube('Hard gold contact',[x,y,.49+z,3,h,.01],'gold','pcb')
 cube('Paper picture',[3.2,7.2,2.8+offset['picture'],33.6,38.6,.15],'silk','picture')
 x,y,z,w,h=3.2,7.2,2.951+offset['picture'],33.6,38.6
 obj=mesh('Original printable artwork',[(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z)],[(0,1,2,3)],'silk','picture')
 uv=obj.data.uv_layers.new(name='Artwork UV')
 for loop,co in zip(uv.data,[(0,1),(1,1),(1,0),(0,0)]):loop.uv=co
 material=bpy.data.materials.new('Replaceable printed picture');material.use_nodes=True
 image=material.node_tree.nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(ROOT/'docs/design/textures/milo-moon-post.png'),check_existing=True);material.node_tree.nodes.active=image
 material.node_tree.links.new(image.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);obj.data.materials.clear();obj.data.materials.append(material)
 # In closed views only the perimeter is drawn, representing transparent sheet.
 z=2.95+offset['window']
 if exploded:cube('Clear PETG window',[3,7,z,34,39,.5],'clear','window')
 else:
  for box in ([3,7,z,34,.12,.5],[3,45.88,z,34,.12,.5],[3,7,z,.12,39,.5],[36.88,7,z,.12,39,.5]):cube('Clear window edge',box,'clear','window')
 for x in (8,32):
  z=-8 if exploded else -1.3;sy=4;sx=(48 if x==8 else 54) if exploded else x;cylinder('M1.6 screw head',[sx,sy,z],1.6,1.3,'metal','screw');cylinder('M1.6 screw shaft',[sx,sy,z+1.3],.8,3,'metal','screw')
 if view=='section':ns['clip'](0,20,False)
 bpy.context.view_layer.update()
 reflection=Matrix(((1,0,0,0),(0,-1,0,60),(0,0,1,0),(0,0,0,1)))
 for obj in ns['objects']:
  obj.data.transform(reflection@obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 scene=bpy.context.scene;target=Vector((20,30,15 if exploded else 2));direction=Vector((.8,-1.3,1.1)) if view in ('exploded','section') else Vector((0,0,1 if view=='front' else -1))
 location=target+direction*180;bpy.ops.object.camera_add(location=location);camera=bpy.context.object
 forward=(target-location).normalized();up=Vector((0,1,0));right=forward.cross(up).normalized();up=right.cross(forward).normalized();camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_quaternion().to_euler();camera.data.type='ORTHO';scene.camera=camera
 bpy.context.view_layer.update();points=[o.matrix_world@Vector(p) for o in ns['objects'] for p in o.bound_box if not o.hide_render]
 rr=[(q-target).dot(right) for q in points];uu=[(q-target).dot(up) for q in points];camera.location+=right*((min(rr)+max(rr))/2)+up*((min(uu)+max(uu))/2);camera.data.ortho_scale=max(max(rr)-min(rr),max(uu)-min(uu))*1.16
 scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.93,.95,.93)
 scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard';scene.render.film_transparent=False
 filename=f'docs/design/images/card-{view}.png';scene.render.filepath=str(ROOT/filename);bpy.ops.render.render(write_still=True)
 pins=[]
 if exploded:
  for number,point in [(1,(38,30,36.3)),(2,(36,28,27.45)),(3,(35,26,18.95)),(4,(28,53,9.3)),(5,(38,30,1)),(6,(51,4,-8))]:
   projected=world_to_camera_view(scene,camera,reflection@Vector(point));pins.append([number,round(projected.x*1200),round((1-projected.y)*1200)])
 metadata[filename]=pins
(ROOT/'work/current/card-view-pins.json').write_text(json.dumps(metadata))
subprocess.run(['python3',str(ROOT/'scripts/annotate_card_views.py')],check=True)
assert frozen=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},'card render inputs changed'
records={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in metadata}
(ROOT/'docs/design/card-render-receipt.json').write_text(json.dumps({'physical_validation':'pending','nominal_envelopes':True,'prepared_meshes':{},'sources':frozen,'images':records},indent=2)+'\n')
