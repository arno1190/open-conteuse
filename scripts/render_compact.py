"""Blender CPU workbench views from actual SCAD meshes and native KiCad data.
Component bodies are documented nominal envelopes, not fabricated supplier models.
"""
import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from export_integrated import triangles
OUT=ROOT/'docs/compact-r1/images';OUT.mkdir(exist_ok=True)
colors={'case':(.86,.86,.80,1),'front':(.93,.91,.83,1),'green':(.035,.25,.14,1),'blue':(.035,.22,.48,1),'black':(.055,.065,.075,1),'metal':(.65,.68,.7,1),'gold':(.72,.49,.15,1),'ceramic':(.5,.37,.19,1),'battery':(.95,.55,.12,1),'glass':(.025,.08,.13,1),'button':(.04,.40,.50,1),'cut':(.9,.35,.09,1),'copper':(.62,.29,.10,1),'red':(.75,.08,.04,1),'wire':(.13,.17,.19,1),'silk':(.8,.83,.8,1)}
materials={};objects=[];CASE_H=0;CASE_D=0
def mat(key):
 if key not in materials:
  m=bpy.data.materials.new(key);m.diffuse_color=colors[key];materials[key]=m
 return materials[key]
def tag(o,g):o['group']=g;objects.append(o);return o
def mesh(name,verts,faces,c,g):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat(c));return tag(o,g)
def cube(name,box,c,g):
 x,y,z,w,h,d=box;verts=[(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z),(x,y,z+d),(x+w,y,z+d),(x+w,y+h,z+d),(x,y+h,z+d)]
 return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],c,g)
def cylinder(name,xyz,r,h,c,g):
 n=24;verts=[(xyz[0]+r*math.cos(i*2*math.pi/n),xyz[1]+r*math.sin(i*2*math.pi/n),xyz[2]+dz) for dz in [0,h] for i in range(n)]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,c,g)

def stl(name,path,c,g):
 lookup={};verts=[];faces=[]
 for t in triangles(path):
  f=[]
  for a in t:
   a=tuple(a)
   if name=='Speaker keeper':a=(a[0],a[1],CASE_D-5.6-a[2])
   if name in ['Back shell','Front shell','Actual PCB outline']:a=(a[0],CASE_H-a[1],a[2])
   key=tuple(round(x,6) for x in a)
   if key not in lookup:lookup[key]=len(verts);verts.append(key)
   f.append(lookup[key])
  faces.append(list(reversed(f)) if name in ['Back shell','Front shell','Actual PCB outline','Speaker keeper'] else f)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat(c));return tag(o,g)
def wire(name,pts,c,g,r=.35):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=r;curve.bevel_resolution=2;s=curve.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);o.data.materials.append(mat(c));return tag(o,g)
def text(name,xyz,size,c,g):
 curve=bpy.data.curves.new(name,'FONT');curve.body=name;curve.size=size;curve.align_x='CENTER';o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);o.location=xyz;o.scale.y=-1;curve.materials.append(mat(c));return tag(o,g)

def board(d,v):
 stl('Actual PCB outline',ROOT/f'work/compact-r1/{v}-pcb.stl','green' if v=='mini' else 'blue','pcb')
 copper=json.loads((ROOT/f'hardware/compact-r1/{v}-copper.json').read_text())
 # Copper geometry follows final pads/tracks; no invented traces.
 verts=[];faces=[]
 for q in copper['pads']:
  x,y=q['xy'];w,h=q['size'];a=math.radians(q['angle']);start=len(verts)
  for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:verts.append((x+dx*math.cos(a)+dy*math.sin(a),y-dx*math.sin(a)+dy*math.cos(a),11.715))
  faces.append(tuple(range(start,start+4)))
 me=bpy.data.meshes.new('Native pad copper');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('Native pad copper',me);bpy.context.collection.objects.link(o);o.data.materials.append(mat('gold'));tag(o,'pcb');o['surface_only']=True
 # Muted trace colour represents copper under solder mask.
 for i,t in enumerate(copper['tracks']):wire('Track'+str(i),[(*t['a'],11.708),(*t['b'],11.708)],'green' if v=='mini' else 'blue','pcb',t['width']/2)
 for i,t in enumerate(copper['rear_tracks']):wire('Rear track'+str(i),[(*t['a'],10.492),(*t['b'],10.492)],'green' if v=='mini' else 'blue','pcb',t['width']/2)
 for i,q in enumerate(copper['vias']):
  x,y=q['xy'];cylinder('Via'+str(i),[x,y,11.716],q['diameter']/2,.025,'gold','pcb');cylinder('Drill'+str(i),[x,y,11.745],q['drill']/2,.01,'black','pcb')
  cylinder('Rear via'+str(i),[x,y,10.465],q['diameter']/2,.025,'gold','pcb');cylinder('Rear drill'+str(i),[x,y,10.45],q['drill']/2,.01,'black','pcb')
 for p in d['parts']:
  ref=p['ref'];b=p['body_box']
  if ref.startswith(('TP','H')):continue
  c='ceramic' if ref.startswith('C') else 'black'
  if ref.startswith('J'):c='metal' if ref in ['J1','J2'] else 'black' if ref=='J3' else 'silk'
  if ref=='U1':
   cube(ref+' antenna substrate',b[:5]+[.8],'green','electronics');cube('RF shield',[b[0]+.5,b[1]+6.5,b[2]+.8,b[3]-1,b[4]-7,2.3],'metal','electronics');continue
  if ref=='SW9':
   cube('Power slide housing',[3.2,40.5,11.7,3.6,9,3.5],'metal','electronics');cube('Recessed power actuator',[1.2,43,12.4,2.1,1.5,1.6],'black','electronics')
  elif ref=='J3':cube(ref+' '+p['mpn'],[p['xy'][0]-3,p['xy'][1]-17,11.7,6,16.8,5.05],c,'electronics')
  elif ref=='J2':
   cube(ref+' steel socket',[47.25,11.6,11.7,11.5,12.8,1.68],'metal','electronics');cube('Inserted microSD card',[58.7,12.5,12,4.4,11,1],'black','electronics')
  else:cube(ref+' '+p['mpn'],b,c,'electronics')
  if ref.startswith('SW') and ref!='SW9':cylinder(ref+' actuator',[p['xy'][0],p['xy'][1],b[2]+b[5]-.5],.7,.5,'metal','electronics')
  if ref=='J1':cube('USB-C receptacle opening',[47.4,b[1]+b[4]+.01,12.2,7.2,.03,2.2],'black','electronics')
  if ref=='J3':
   o=cylinder('TRRS bushing',[p['xy'][0],p['xy'][1]-.3,14.225],2.5,.6,'black','electronics');o.data.transform(Matrix.Translation(-Vector([p['xy'][0],p['xy'][1]-.3,14.225])));o.location=[p['xy'][0],p['xy'][1]-.3,14.225];o.rotation_euler[0]=math.pi/2
   o=cylinder('TRRS opening',[p['xy'][0],p['xy'][1]+.05,14.2],1.8,.2,'black','electronics');o.data.transform(Matrix.Translation(-Vector([p['xy'][0],p['xy'][1]+.05,14.2])));o.location=[p['xy'][0],p['xy'][1]+.05,14.2];o.rotation_euler[0]=math.pi/2
  if ref.startswith('U') and b[3]>3:text(ref,[p['xy'][0],p['xy'][1],b[2]+b[5]+.03],1,'silk','electronics')
def build(v):
 global objects,CASE_H,CASE_D;objects=[];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 d=json.loads((ROOT/f'hardware/compact-r1/{v}-mechanical.json').read_text());W,H,D=d['case'];CASE_H=H;CASE_D=D
 stl('Speaker keeper',ROOT/f'enclosure/compact-r1/print/{v}-bridge.stl','case','peripheral')
 for x,y in [(36,77.3),(41.5,91.5)]:cylinder('Keeper screw head',[x,y,D-7.7],1.6,1.3,'metal','peripheral')
 stl('Back shell',ROOT/f'enclosure/compact-r1/print/{v}-back.stl','case','back')
 stl('Front shell',ROOT/f'enclosure/compact-r1/print/{v}-front.stl','front','front')
 board(d,v)
 # Actual cap mesh, transformed from its face-down print orientation.
 for p in d['parts']:
  if p['section']=='controls' and p['ref'].startswith('SW'):
   o=stl(p['ref']+' captive cap',ROOT/f'enclosure/compact-r1/print/{v}-button.stl','button','caps')
   for q in o.data.vertices:q.co=Vector((q.co.x+p['xy'][0],-q.co.y+p['xy'][1],D+.6-q.co.z))
 for e in d['extras']:
  b=e['box'];g='cell' if e['id']=='cell' else 'peripheral'
  if e['id']=='nfc':
   cube(e['mpn'],b[:5]+[1],e['color'],g);cube('NFC connector',[50,32,16.5,5,4,3.4],'silk',g)
  else:cube(e['mpn'],b,e['color'],g)
  if e['id']=='lcd':
   cube('LCD metal back',[b[0],b[1],b[2],b[3],b[4],.3],'metal',g)
   cube('Active display',[9.02,10,22.01,48.96,36.72,.02],'glass',g)
  if e['id']=='cell':text('1200 mAh',[32.5,56,8.03],4,'black','cell')
  if e['id']=='nfc':cube('PN532 controller',[35,37,16.5,6,6,1.4],'black',g)
 # Planned wire paths are visible and labelled as routing assumptions in the guide.
 for off,c in [(-.5,'red'),(.5,'wire')]:wire('Cell harness',[ (15.5+off,24,5.5),(8+off,20,8.8),(5+off,8,8.8),(5+off,8,14.8),(8+off,21,14.8)],c,'wires')
 wire('Cell NTC leads',[(31,52,8.2),(10,52,8.4),(7,8,8.8),(7,8,14.8),(8,32,14.8)],'wire','wires',.3)
 wire('Speaker wire pair',[(40.5,79,15.5),(42,77,16),(42,80,17 if v=='mini' else 19)],'red','wires',.45)
 if v=='mini':
  wire('NFC SPI harness',[(16,43,15.5),(20,46,17),(27,48,18),(31,43,18)],'wire','wires',.6)
  wire('Stock antenna lead loop',[(52,34,19),(54,31,19),(53,30,19),(44,30,19),(44,23,19)],'copper','wires',.3)
 else:
  #48mm tail nominal path; transparent reserve is documented separately.
  j8=next(p for p in d['parts'] if p['ref']=='J8');jx,jy=j8['xy']
  wire('LCD FPC fold',[(63.5,27,20),(64.5,27,19),(63.5,27,17.5),(jx+4.45,jy,17.5),(jx+4.45,jy,12.8)],'copper','wires',.18)
 for x,y in d['pcb']['holes']:
  cylinder('M2 socket head',[x,y,.2],1.9,2,'metal','fasteners');cylinder('M2 screw shank',[x,y,2.2],1,14,'metal','fasteners');cylinder('M2 insert',[x,y,11.8],1.6,3,'gold','fasteners')
 return d

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


def clip(axis,value,positive):
 for o in objects:
  if o.type=="MESH":bisect(o,axis,value,"high" if positive else "low")
  elif o.type in ["CURVE","FONT"]:o.hide_render=True

def render(v,name,direction,hidden=(),explode=False,section=None,onlypcb=False):
 d=build(v);W,H,D=d['case'];scene=bpy.context.scene
 for o in objects:
  if o['group'] in hidden:o.hide_render=True
  if onlypcb and o['group'] not in ['pcb','electronics']:o.hide_render=True
  if explode:
   if o['group'] in ['pcb','electronics','peripheral','wires']:o.location.z+=20
   if o['group'] in ['front','caps']:o.location.z+=48
 bpy.context.view_layer.update()
 if section:clip(*section)
 if name=='battery-service':
  for o in objects:
   if o['group'] not in ['back','cell','wires']:o.hide_render=True
 # KiCad/case XY uses Y downward. Reflect into Blender's Y-up presentation.
 reflection=Matrix(((1,0,0,0),(0,-1,0,H),(0,0,1,0),(0,0,0,1)))
 for o in objects:
  if o.type=='MESH':
   transform=reflection@o.matrix_world;o.data.transform(transform);o.matrix_world=Matrix.Identity(4);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  else:o.matrix_world=reflection@o.matrix_world
 target=Vector((W/2,H/2,32 if explode else D/2));loc=target+Vector((direction[0],-direction[1],direction[2]))*220
 bpy.ops.object.camera_add(location=loc);camera=bpy.context.object;forward=(target-loc).normalized();up=Vector((0,1,0)) if abs(forward.y)<.97 else Vector((0,0,1));right=forward.cross(up).normalized();up=right.cross(forward).normalized();camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_quaternion().to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=180 if explode else 128;scene.camera=camera
 if explode:
  bpy.context.view_layer.update()
  points=[o.matrix_world@Vector(c) for o in objects if not o.hide_render and not(o.type=='MESH' and not len(o.data.vertices)) for c in o.bound_box]
  rr=[(q-target).dot(right) for q in points];uu=[(q-target).dot(up) for q in points]
  camera.location+=right*((min(rr)+max(rr))/2)+up*((min(uu)+max(uu))/2)
  camera.data.ortho_scale=max(max(rr)-min(rr),max(uu)-min(uu))*1.12
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='FLAT';s.studiolight_rotate_z=.5;s.color_type='MATERIAL';s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.curvature_ridge_factor=1.2;s.curvature_valley_factor=1.0;s.show_specular_highlight=True;s.background_type='WORLD';scene.world.color=(.91,.94,.93)
 scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard';scene.render.film_transparent=False;scene.render.filepath=str(OUT/f'{v}-{name}.png');bpy.ops.render.render(write_still=True)

views=[('hero-front',(.9,1.3,1.8),()),('hero-rear',(-.9,1.3,-1.8),()),('front',(0,0,1),()),('rear',(0,0,-1),()),('left',(-1,0,0),()),('right',(1,0,0),()),('top',(0,-1,0),()),('bottom',(0,1,0),()),('open-front',(.7,1,1.8),('front','caps')),('open-rear',(-.7,1,-1.8),('back',)),('exploded',(.7,1.1,1.6),()),('pcb-front',(0,0,1),()),('pcb-rear',(0,0,-1),()),('battery-service',(.6,.8,1.8),()),('cut-x-centre',(-1,.5,.6),()),('cut-x-jack',(-1,.5,.6),()),('cut-y-antenna',(.5,-1,.8),()),('cut-y-controls',(.5,-1,.8),()),('cut-z-battery',(0,0,1),()),('cut-z-front',(.3,.5,1.8),())]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for v in ['mini','explore']:
 inputs=[f'hardware/compact-r1/{v}-mechanical.json',f'hardware/compact-r1/{v}-copper.json',f'hardware/compact-r1/{v}/{v}.kicad_pcb','scripts/render_compact.py','enclosure/compact-r1/compact.scad',f'enclosure/compact-r1/{v}-data.scad',*[f'enclosure/compact-r1/print/{v}-{p}.stl' for p in ['front','back','button','bridge']],f'work/compact-r1/{v}-pcb.stl']
 frozen={fn:hashlib.sha256((ROOT/fn).read_bytes()).hexdigest() for fn in inputs}
 records={}
 for name,direction,hidden in views:
  if args and args[0] not in [v,name,v+'-'+name]:continue
  section={'cut-x-centre':(0,32.5,True),'cut-x-jack':(0,29,True),'cut-y-antenna':(1,24,True),'cut-y-controls':(1,60 if v=='mini' else 65,True),'cut-z-battery':(2,8.5,False),'cut-z-front':(2,18,False)}.get(name)
  render(v,name,direction,hidden,name=='exploded',section,name.startswith('pcb-'))

  fn=f'docs/compact-r1/images/{v}-{name}.png';records[fn]=hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()
 if records:

  assert frozen=={fn:hashlib.sha256((ROOT/fn).read_bytes()).hexdigest() for fn in inputs},"render inputs changed during batch"
  sources={fn:hashlib.sha256((ROOT/fn).read_bytes()).hexdigest() for fn in inputs if not fn.startswith('work/')}
  (OUT.parent/f'{v}-render-receipt.json').write_text(json.dumps({'nominal_envelopes':True,'physical_validation':'pending','sources':sources,'prepared_meshes':{fn:value for fn,value in frozen.items() if fn.startswith('work/')},'images':records},indent=2)+'\n')
