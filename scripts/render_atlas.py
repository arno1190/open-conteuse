"""Blender4.3 CPU CAD atlas. Run: blender -b -t6 --python scripts/render_atlas.py -- [--only mini-hero-front] [--samples 32]."""
import bpy,bmesh,gzip,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from integrated_hardware import read_data,indexed,placements,transform_point,size
from export_integrated import triangles
C,L=read_data();PARTS=indexed(C);OUT=ROOT/'docs/visual-atlas/images';OUT.mkdir(parents=True,exist_ok=True)
M={};objects=[];records=[]
PALETTE={'case':('#e4e5dd',0,.48),'carrier':('#94a5a8',0,.6),'button':('#237e99',0,.45),'accent':('#d78f2c',0,.42),'pcb_blue':('#0754a0',0,.45),'pcb_green':('#154d37',0,.6),'pcb_black':('#202a29',0,.55),'black':('#191d22',0,.48),'metal':('#bcc4ca',.78,.27),'gold':('#d1a340',.7,.3),'foil':('#aeb7be',.78,.38),'ceramic':('#ba9c69',0,.7),'white':('#eceee5',0,.55),'glass':('#091a28',.3,.2),'cut':('#d68843',0,.55)}
def mat(name):
 if name not in M:
  col,metal,rough=PALETTE[name];m=bpy.data.materials.new(name);rgb=[int(col[i:i+2],16)/255 for i in (1,3,5)];m.diffuse_color=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=m.diffuse_color;n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;M[name]=m
 return M[name]
def tag(o,group,part):o['group']=group;o['part']=part;objects.append(o);return o
def mesh(name,v,f,material,group,part):
 data=bpy.data.meshes.new(name);data.from_pydata(v,[],f);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.data.materials.append(mat(material));return tag(o,group,part)
def cube(name,xyz,d,material,group,part):
 bpy.ops.mesh.primitive_cube_add(size=1,location=[xyz[i]+d[i]/2 for i in range(3)]);o=bpy.context.object;o.name=name;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat(material));return tag(o,group,part)
def cylinder(name,xyz,r,depth,material,group,part,end=None):
 if end is not None:
  delta=Vector(end)-Vector(xyz);depth=delta.length;loc=(Vector(end)+Vector(xyz))/2
 else:loc=Vector(xyz)+Vector((0,0,depth/2))
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name
 if end is not None:o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
 o.data.materials.append(mat(material));return tag(o,group,part)
def stl(name,path,material,group,part,transform=None):
 # Deduplicate vertices so section filling operates on real connected edges.
 verts=[];faces=[];lookup={}
 for tri in triangles(path):
  face=[]
  for point in tri:
   key=tuple(round(v,6) for v in point)
   if key not in lookup:lookup[key]=len(verts);verts.append(transform(key) if transform else key)
   face.append(lookup[key])
  faces.append(face)
 return mesh(name,verts,faces,material,group,part)
def apply_local(o,part,pose,flip_y=False):
 # Primitive geometry is constructed in normalized local coordinates.
 for vert in o.data.vertices:
  point=o.matrix_world@vert.co
  if flip_y:point.y=45-point.y
  vert.co=Vector(transform_point(part,pose,point))
 if flip_y:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 o.matrix_world=Matrix.Identity(4)
def label(text,xyz,size=2.0,rotation=(0,0,0),group='label',part='annotation'):
 bpy.ops.object.text_add(location=xyz,rotation=rotation);o=bpy.context.object;o.name='Annotation '+text;o.data.body=text;o.data.size=size;o.data.extrude=0;o.data.materials.append(mat('white'));return tag(o,group,part)
def pcb_native(ident,pose):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/f'work/atlas/{ident}.glb'))
 for o in set(bpy.data.objects)-before:
  if o.type!='MESH':continue
  local=[o.matrix_world@v.co for v in o.data.vertices]
  o.data=o.data.copy()
  for v,p in zip(o.data.vertices,local):v.co=transform_point(PARTS[ident],pose,native_board_point(ident,p))
  o.parent=None;o.matrix_world=Matrix.Identity(4);o['surface_only']='_PCB' not in o.data.name;tag(o,'front' if ident=='controls' else 'rear',ident)
  # Native KiCad materials preserved for soldermask, silkscreen and pads.

def custom_components(ident,pose,variant):
 group='front' if ident=='controls' else 'rear';p=PARTS[ident];start=len(objects)
 for fp in PCB[ident]:
  ref=fp['ref'];x,y=fp['xy'];pads=fp['pads']
  if ident=='controls':
   if not ref.startswith('SW'):continue
   index=int(ref[2:])-1
   x,y=json.loads((ROOT/'enclosure/controls.json').read_text())['actuators_mm'][index]
   if variant=='mini' and index not in [1,3,4,6,7]:continue
   cube(ref,[x-3,y-3,-3.3],[6,6,3.3],'metal',group,ident);cylinder(ref+' actuator',[x,y,-4.3],1.7,1,'black',group,ident)
  elif ref.startswith('U'):
   center=[sum(v[i] for v in pads)/len(pads) for i in (0,1)]
   cube(ref,[center[0]-3.2,center[1]-9.65,2.6],[6.4,19.3,3.7],'black',group,ident)
   for px,py,_ in pads:cube(ref+' leg',[px-.35,py-.3,1.6],[.7,.6,1.2],'metal',group,ident)
   label(fp['value'],[center[0]-2.7,center[1]-7,6.31],.8,group=group,part=ident)
  elif ref.startswith('R'):
   a,b=pads[:2];mid=[(a[i]+b[i])/2 for i in (0,1)];cylinder(ref,[mid[0]-3.15,mid[1],3.05],1.25,6.3,'ceramic',group,ident,end=[mid[0]+3.15,mid[1],3.05])
   for px,py,_ in pads:cylinder(ref+' lead',[px,py,1.6],.25,1.45,'metal',group,ident)
  elif ref.startswith('C'):cylinder(ref,[x+1.27,y,2.1],2.5,4.5,'ceramic',group,ident)
  elif ref.startswith('Q'):cube(ref,[x-.5,y-1.7,3],[4.8,3.4,4.5],'black',group,ident)
  elif ref.startswith('J'):
   for px,py,_ in pads:
    cube(ref+' housing',[px-1.2,py-1.2,1.6],[2.4,2.4,2.54],'black',group,ident);cube(ref+' pin',[px-.32,py-.32,4.14],[.64,.64,5.7],'gold',group,ident)
 for o in objects[start:]:
  if o.type=='MESH':apply_local(o,p,pose,flip_y=ident=='mute_latch')
  elif o.type=='FONT':
   point=o.location.copy()
   if ident=='mute_latch':point.y=45-point.y
   o.location=transform_point(p,pose,point)

def proxies(ident,pose):
 p=PARTS[ident];start=len(objects);group='rear'
 if ident=='mcu':
  cube('MCU visual proxy PCB',[.3,.55,10],[25.4,62.865,1.6],'pcb_black',group,ident)
  cube('RF can visual proxy',[4.3,36,11.6],[17,17,2.5],'metal',group,ident)
  for x in [2.9,15.1]:cube('USB visual proxy',[x,.8,11.6],[7.6,7.5,2.6],'metal',group,ident)
  for x in [1.57,24.43]:
   for i in range(22):cylinder('header envelope',[x,8.13+i*2.54,7],.34,3,'gold',group,ident)
 else:
  cube('Regulator visual proxy PCB',[0,0,0],[12.7,15.3,1.6],'pcb_black',group,ident);cube('Inductor visual proxy',[3.5,4,1.6],[5.5,6,2.7],'black',group,ident)
 for o in objects[start:]:apply_local(o,p,pose)

def build(variant):
 global objects
 objects=[];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for data in list(bpy.data.meshes):
  if data.users==0:bpy.data.meshes.remove(data)
 folder=ROOT/'enclosure/integrated/print'
 for part,group,material in [('front','case','case'),('lid','lid','case'),('carrier','carrier','carrier')]:
  def tx(v,part=part):return [v[0],v[1],50-v[2]] if part=='lid' else [v[0],v[1],v[2]+(L['case']['carrier_z'] if part=='carrier' else 0)]
  stl(part,folder/f'{variant}-{part}.stl',material,group,part,tx)
 def accessory(part,xyz,rot=0):
  co=math.cos(math.radians(rot));si=math.sin(math.radians(rot))
  stl(part,folder/f'{variant}-{part}.stl','carrier','rear',part,lambda v:[xyz[0]+v[0]*co-v[1]*si,xyz[1]+v[0]*si+v[1]*co,xyz[2]+v[2]])
 accessory('battery_cover',[52.8,76.8,40.9])
 accessory('mcu_retainer',[11,3,39.4]);accessory('mcu_retainer',[39,77,39.4],180);accessory('regulator_retainer',[46.85,6,37]);accessory('switch_retainer',[102.6,39.9,37.35])
 poses={p['part']:p for p in placements(L,variant)}
 sp=poses['speaker'];stl('speaker spacer',folder/f'{variant}-speaker_spacer.stl','carrier','front','speaker_spacer',lambda v:transform_point(PARTS['speaker'],sp,[v[0],v[1],v[2]-4]))
 for pose in poses.values():
  ident=pose['part'];group='rear' if pose['mount'] in ['carrier','side'] else 'front'
  if ident in ['controls','mute_latch']:pcb_native(ident,pose);custom_components(ident,pose,variant)
  elif ident in ['mcu','regulator']:proxies(ident,pose)
  else:
   for i,row in enumerate(NATIVE[ident]):mesh(ident+f' solid{i}',[transform_point(PARTS[ident],pose,v) for v in row['vertices']],row['faces'],row['material'],group,ident)
  if ident in ['nfc','sd','headphone','speaker_amp','charger']:
   board=PARTS[ident]['pcb'];xy=board['origin_in_model_mm'];pt=transform_point(PARTS[ident],pose,[xy[0]+5,xy[1]+7,xy[2]+board['size_mm'][2]+.035]);label(ident.upper()+' '+PARTS[ident]['part_number'],pt,1.45,(0,0,math.radians(pose.get('rotate_z',0))),group=group,part=ident)
 controls=json.loads((ROOT/'enclosure/controls.json').read_text())['actuators_mm']
 for i,xy in enumerate(controls):
  if variant=='mini' and i not in [1,3,4,6,7]:continue
  xyz=poses['controls']['xyz'];stl('button',folder/f'{variant}-button.stl','accent' if i in [6,7] else 'button','front','button',lambda v:[v[0]+xy[0]+xyz[0],v[1]+xy[1]+xyz[1],4.4-v[2]])
 return poses

def bisect(o,axis,value,keep):
 if o.type!='MESH':return
 coords=[o.matrix_world@Vector(p) for p in o.bound_box]
 lo=min(v[axis] for v in coords);hi=max(v[axis] for v in coords)
 if (keep=='low' and hi<=value+.00001) or (keep=='high' and lo>=value-.00001):return
 if (keep=='low' and lo>=value) or (keep=='high' and hi<=value):o.hide_render=True;return
 if o.get('surface_only',False):
  o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);point=[0,0,0];point[axis]=value;normal=[0,0,0];normal[axis]=1
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=o.matrix_world.inverted()@Vector(point),plane_no=o.matrix_world.to_3x3().transposed()@Vector(normal),clear_outer=keep=='low',clear_inner=keep=='high');bm.to_mesh(o.data);bm.free();return
 # Intersect with a closed half-space box using Blender's exact solver.
 # Unlike filling each bmesh boundary separately, this preserves hollow case
 # interiors and nested PCB holes. The cutter's slot sets cut faces orange.
 origin=[-2000,-2000,-2000];dims=[4000,4000,4000]
 if keep=='low':dims[axis]=value+2000
 else:origin[axis]=value;dims[axis]=2000-value
 bpy.ops.mesh.primitive_cube_add(size=1,location=[origin[i]+dims[i]/2 for i in range(3)])
 cutter=bpy.context.object;cutter.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data=o.data.copy();cut_index=len(o.data.materials);o.data.materials.append(mat('cut'))
 for material in o.data.materials:cutter.data.materials.append(material)
 for poly in cutter.data.polygons:poly.material_index=cut_index
 # Boolean material index copies cutter material into the existing matching slot.
 modifier=o.modifiers.new('Actual section half space','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=cutter
 bpy.context.view_layer.objects.active=o
 try:bpy.ops.object.modifier_apply(modifier=modifier.name)
 except RuntimeError:
  # Silkscreen is a zero-thickness reference surface, not a closed solid.
  # Keep its clipped outline uncapped; never fabricate a solid filled section.
  if modifier.name in o.modifiers:o.modifiers.remove(modifier)
  bm=bmesh.new();bm.from_mesh(o.data);point=[0,0,0];point[axis]=value;normal=[0,0,0];normal[axis]=1
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=o.matrix_world.inverted()@Vector(point),plane_no=o.matrix_world.to_3x3().transposed()@Vector(normal),clear_outer=keep=='low',clear_inner=keep=='high');bm.to_mesh(o.data);bm.free()
 bpy.data.objects.remove(cutter,do_unlink=True)

def setup_camera(direction,target,span):
 target=Vector(target);direction=Vector(direction).normalized();bpy.ops.object.camera_add(location=target+direction*600);cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=span
 if (cam.rotation_euler.to_matrix()@Vector((0,1,0))).dot(Vector((0,-1,0)))<-.00001:cam.rotation_euler.rotate_axis('Z',math.pi)
 bpy.context.scene.camera=cam
 # Different broad sources keep front/rear sections readable without fake transparency.
 for loc,power,size_ in [((230,-200,350),800000,250),((-240,50,-260),500000,220),((90,350,180),500000,200)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size_;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()

from atlas_plan import views,native_board_point

def render(variant,spec):
 build(variant);mode=spec['mode']
 for o in objects:
  group=o['group'];part=o['part']
  if mode in ['open','front-layer','carrier','detail'] and group=='lid':o.hide_render=True
  if mode=='front-layer' and group in ['carrier','rear','case']:o.hide_render=True
  if mode=='carrier' and group in ['front','case']:o.hide_render=True
  if mode=='exploded':
   o.location+=Vector((-80,35,120)) if group=='lid' else Vector((45,0,60)) if group in ['carrier','rear'] else Vector((0,0,0))
  if mode=='section':
   if o.type=='FONT':o.hide_render=True
   else:bisect(o,*spec['cut'])
  if mode=='detail':
   if spec['focus'] in ['controls','speaker'] and group in ['carrier','rear']:o.hide_render=True
   if spec['focus'] in ['battery','mcu'] and group in ['front','case']:o.hide_render=True
   if spec['focus']=='battery' and part=='battery_cover':o.hide_render=True
   # Remove only a portion of the housing to show connector bodies, not whole modules.
   if group=='case' and spec['focus'] in ['usb','headphone','switch','controls','speaker']:bisect(o,2,35 if spec['focus'] in ['usb','headphone','switch'] else 8,'low')
 if mode=='board':
  for o in objects:o.hide_render=o['part']!=spec['focus']
 if mode=='front-layer':spec=dict(spec,direction=(0,0,1)) # rear-facing view; other views show switch actuator side.
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=SAMPLES;scene.cycles.use_denoising=False;scene.cycles.seed=31415;scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
 scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2
 scene.use_nodes=True;nodes=scene.node_tree.nodes;nodes.clear();rl=nodes.new('CompositorNodeRLayers');over=nodes.new('CompositorNodeAlphaOver');over.inputs[1].default_value=(4,4,4,1);scene.node_tree.links.new(rl.outputs['Image'],over.inputs[2]);output=nodes.new('CompositorNodeComposite');scene.node_tree.links.new(over.outputs[0],output.inputs[0])
 scene.world.color=(.7,.7,.7);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.87,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 scene.view_settings.view_transform='AgX';setup_camera(spec['direction'],spec['target'],spec['span'])
 if mode!='detail':
  cam=scene.camera;inv=cam.rotation_euler.to_matrix().transposed();origin=Vector(spec['target']);points=[inv@(o.matrix_world@Vector(v)-origin) for o in objects if o.type=='MESH' and not o.hide_render for v in o.bound_box]
  if points:
   lo=[min(v[i] for v in points) for i in range(2)];hi=[max(v[i] for v in points) for i in range(2)];aspect=scene.render.resolution_x/scene.render.resolution_y
   cam.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*aspect)*1.15;cam.location+=cam.rotation_euler.to_matrix()@Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,0))
 file=OUT/f'{variant}-{spec["id"]}.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
 print('ATLAS_RENDERED',file.name,flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];SAMPLES=int(args[args.index('--samples')+1]) if '--samples' in args else 32;only=args[args.index('--only')+1] if '--only' in args else None
 NATIVE=json.loads(gzip.open(ROOT/'work/atlas/manufacturer.json.gz','rt').read());PCB=json.loads((ROOT/'work/atlas/pcb.json').read_text())
 for variant in ['mini','explore']:
  for spec in views(variant):
   if only and variant+'-'+spec['id']!=only:continue
   render(variant,spec)
   records.append(dict(variant=variant,**spec))
 (ROOT/'work/atlas/view-plan.json').write_text(json.dumps(records,indent=2)+'\n')
