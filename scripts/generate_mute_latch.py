#!/usr/bin/python3
"""Generate the independent codec-event mute latch PCB. Original MIT design.

Run with KiCad 9's system Python. A latched IRQ blocks the speaker regardless of
main-loop progress; this is not a safety certification or a mechanical detector.
"""
from pathlib import Path
import json, math, heapq, re, uuid
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/integration/mute-latch';OUT.mkdir(parents=True,exist_ok=True)
W=H=45;origin=(30,30)
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'open-conteuse/mute-latch/v1/'+key))
def pos(x,y):return pcb.VECTOR2I(pcb.FromMM(x+30),pcb.FromMM(y+30))
def pt(v):return (round(pcb.ToMM(v.x)-30,4),round(pcb.ToMM(v.y)-30,4))
NAMES=['3V3','GND','CODEC_IRQ','BASE','PRE_N','CLEAR_N','MUTED','LATCH_ALLOW','SPK_REQUEST','SPK_ENABLE']
# ref, value, library, footprint, x, y, electrical pin map (None = NC)
parts=[
 ('J1','3V3_ONLY','Connector_PinHeader_2.54mm','PinHeader_1x07_P2.54mm_Vertical',5,10,dict(zip(map(str,range(1,8)),['3V3','GND','CODEC_IRQ','SPK_REQUEST','CLEAR_N','MUTED','SPK_ENABLE']))),
 ('U1','SN74HC74N','Package_DIP','DIP-14_W7.62mm',13,8,{'1':'CLEAR_N','2':'GND','3':'GND','4':'PRE_N','5':'MUTED','6':'LATCH_ALLOW','7':'GND','8':None,'9':None,'10':'3V3','11':'GND','12':'GND','13':'3V3','14':'3V3'}),
 ('U2','SN74HC08N','Package_DIP','DIP-14_W7.62mm',29,8,{'1':'LATCH_ALLOW','2':'SPK_REQUEST','3':'SPK_ENABLE','4':'GND','5':'GND','6':None,'7':'GND','8':None,'9':'GND','10':'GND','11':None,'12':'GND','13':'GND','14':'3V3'}),
 ('Q1','2N3904BU_EBC','Package_TO_SOT_THT','TO-92_Inline',20,28,{'1':'GND','2':'BASE','3':'PRE_N'}),
 ('C1','100nF','MuteLatch','C_Disc_D5.0mm_W2.5mm_P2.54mm',9,4,{'1':'3V3','2':'GND'}),
 ('C2','100nF','MuteLatch','C_Disc_D5.0mm_W2.5mm_P2.54mm',25,4,{'1':'3V3','2':'GND'}),
]
for ref,value,x,y,a,b in [('R1','10k',8,32,'CODEC_IRQ','BASE'),('R2','100k',24,32,'BASE','GND'),('R3','10k',8,38,'3V3','PRE_N'),('R4','10k',24,38,'3V3','CLEAR_N'),('R5','10k',28,28,'SPK_REQUEST','GND'),('R6','10k',8,28,'SPK_ENABLE','GND')]:
 parts.append((ref,value,'Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',x,y,{'1':a,'2':b}))
for i,(x,y) in enumerate([(4,4),(41,4),(4,41),(41,41)],1):parts.append(('H'+str(i),'M2.5','MountingHole','MountingHole_2.7mm_M2.5',x,y,{}))
# Match the selected KEMET C315's exact 2.54 mm lead pitch. Retain library
# attribution; shift the stock 2.50 mm artwork centre by 0.02 mm.
caplib=OUT/'MuteLatch.pretty';caplib.mkdir(exist_ok=True)
cap=pcb.FootprintLoad('/usr/share/kicad/footprints/Capacitor_THT.pretty','C_Disc_D5.0mm_W2.5mm_P2.50mm')
cap.SetFPID(pcb.LIB_ID('MuteLatch','C_Disc_D5.0mm_W2.5mm_P2.54mm'))
for pad in cap.Pads():
 if pad.GetNumber()=='2':pad.SetPosition(pcb.VECTOR2I(pcb.FromMM(2.54),0))
for item in cap.GraphicalItems():item.Move(pcb.VECTOR2I(pcb.FromMM(.02),0))
cap_plugin=pcb.PCB_IO_KICAD_SEXPR()
cap_plugin.FootprintSave(str(caplib),cap)
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "MuteLatch") (type "KiCad") (uri "${KIPRJMOD}/MuteLatch.pretty") (options "") (descr "Exact 2.54 mm capacitor pitch, derived from KiCad library")))\n')
nc_names={('U1','8'):'Q2_N',('U1','9'):'Q2',('U2','6'):'Y2',('U2','8'):'Y3',('U2','11'):'Y4'}
board=pcb.BOARD();board.SetCopperLayerCount(2);board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))
net={};fps=[]
for name in NAMES:net[name]=pcb.NETINFO_ITEM(board,'/'+name);board.Add(net[name])
for (ref,pin),label in nc_names.items():
 key='unconnected-('+ref+'-'+label+'-Pad'+pin+')';net[key]=pcb.NETINFO_ITEM(board,key);board.Add(net[key])
for ref,value,lib,foot,x,y,pins in parts:
 fp=pcb.FootprintLoad(str(caplib) if lib=='MuteLatch' else '/usr/share/kicad/footprints/'+lib+'.pretty',foot)
 fp.SetFPID(pcb.LIB_ID(lib,foot));fp.SetReference(ref);fp.SetValue(value);fp.SetPosition(pos(x,y));fp.SetPath(pcb.KIID_PATH('/'+uid('root')+'/'+uid(ref)))
 fp.Value().SetVisible(False);fp.Reference().SetVisible(False) # schematic/BOM identify parts; do not print cramped silk
 for pad in fp.Pads():
  name=pins.get(pad.GetNumber())
  if name:pad.SetNet(net[name])
  elif (ref,pad.GetNumber()) in nc_names:
   label=nc_names[(ref,pad.GetNumber())];pad.SetNet(net['unconnected-('+ref+'-'+label+'-Pad'+pad.GetNumber()+')'])
 board.Add(fp);fps.append(fp)
for a,b in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
 l=pcb.PCB_SHAPE();l.SetShape(pcb.SHAPE_T_SEGMENT);l.SetStart(pos(*a));l.SetEnd(pos(*b));l.SetLayer(pcb.Edge_Cuts);l.SetWidth(pcb.FromMM(.05));board.Add(l)
# Deterministic two-layer router shared in algorithm with the controls generator.
STEP=.25;nx=int(W/STEP);ny=int(H/STEP);obstacles={};via_positions={}
def grid(p):return (round(p[0]/STEP),round(p[1]/STEP))
def mm(p):return (p[0]*STEP,p[1]*STEP)
for fp in fps:
 for pad in fp.Pads():
  x,y=pt(pad.GetPosition());size=pad.GetSize();rx=pcb.ToMM(size.x)/2+.45;ry=pcb.ToMM(size.y)/2+.45
  for ix in range(math.floor((x-rx)/STEP),math.ceil((x+rx)/STEP)+1):
   for iy in range(math.floor((y-ry)/STEP),math.ceil((y+ry)/STEP)+1):
    for layer in (0,1):obstacles.setdefault((ix,iy,layer),set()).add(pad.GetNetname().lstrip('/') or 'NC_HOLE')
pad_centres=[(pt(p.GetPosition()),p.GetNetname().lstrip('/'),pcb.ToMM(p.GetDrillSize().x)/2) for f in fps for p in f.Pads()]
def via_kind(point,name):
 for centre,padnet,radius in pad_centres:
  dist=math.dist(point,centre)
  if dist<=.35 and padnet==name:return 'pad'
  if dist<radius+.45:return 'blocked'
 for centre,vianet in via_positions.items():
  if point==centre and vianet==name:return 'existing'
  if math.dist(point,centre)<.7:return 'blocked'
 return 'new'
def track(a,b,name,layer=pcb.F_Cu):
 if a==b:return
 t=pcb.PCB_TRACK(board);t.SetStart(pos(*a));t.SetEnd(pos(*b));t.SetWidth(pcb.FromMM(.25));t.SetLayer(layer);t.SetNet(net[name]);board.Add(t)
def mark(a,b,name,layer):
 ga,gb=grid(a),grid(b)
 for x in range(min(ga[0],gb[0])-2,max(ga[0],gb[0])+3):
  for y in range(min(ga[1],gb[1])-2,max(ga[1],gb[1])+3):obstacles.setdefault((x,y,layer),set()).add(name)
def route(a,b,name):
 start=(*grid(a),0);end=(*grid(b),0);pending=[(0,0,start)];cost={start:0};parent={}
 while pending:
  _,g,c=heapq.heappop(pending)
  if c==end:break
  if g!=cost[c]:continue
  choices=[(c[0]+dx,c[1]+dy,c[2]) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]+[(c[0],c[1],1-c[2])]
  for n in choices:
   if not (4<=n[0]<=nx-4 and 4<=n[1]<=ny-4):continue
   via=n[2]!=c[2]
   if via:
    if via_kind(mm(n[:2]),name)=='blocked':continue
    if any(obstacles.get((n[0]+dx,n[1]+dy,layer),set())-{name} for dx in range(-3,4) for dy in range(-3,4) for layer in (0,1)):continue
   elif obstacles.get(n,set())-{name}:continue
   ng=g+(12 if via else 1)
   if ng<cost.get(n,10**9):cost[n]=ng;parent[n]=c;heapq.heappush(pending,(ng+abs(n[0]-end[0])+abs(n[1]-end[1]),ng,n))
 else:raise RuntimeError('Cannot route '+name+' '+str(a)+' -> '+str(b))
 path=[end]
 while path[-1]!=start:path.append(parent[path[-1]])
 path.reverse();simple=[path[0]]
 for i in range(1,len(path)-1):
  if tuple(path[i][j]-path[i-1][j] for j in range(3))!=tuple(path[i+1][j]-path[i][j] for j in range(3)):simple.append(path[i])
 simple.append(path[-1])
 for a,b in zip(simple,simple[1:]):
  if a[2]!=b[2]:
   if via_kind(mm(a[:2]),name) in ('pad','existing'):continue
   via_positions[mm(a[:2])]=name
   v=pcb.PCB_VIA(board);v.SetPosition(pos(*mm(a[:2])));v.SetWidth(pcb.F_Cu,pcb.FromMM(.65));v.SetDrill(pcb.FromMM(.3));v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNet(net[name]);board.Add(v)
   for dx in range(-3,4):
    for dy in range(-3,4):
     for layer in (0,1):obstacles.setdefault((a[0]+dx,a[1]+dy,layer),set()).add(name)
  else:track(mm(a[:2]),mm(b[:2]),name,pcb.F_Cu if a[2]==0 else pcb.B_Cu);mark(mm(a[:2]),mm(b[:2]),name,a[2])
for name in sorted(NAMES,key=lambda n:sum(p.GetNetname()=='/'+n for f in fps for p in f.Pads())):
 points=[pt(p.GetPosition()) for f in fps for p in f.Pads() if p.GetNetname()=='/'+name]
 connected=[points.pop(0)]
 while points:
  _,a,b=min((math.dist(a,b),a,b) for a in connected for b in points)
  for p in (a,b):track(p,mm(grid(p)),name)
  route(mm(grid(a)),mm(grid(b)),name);connected.append(b);points.remove(b)
board.BuildConnectivity();pcb.SaveBoard(str(OUT/'mute-latch.kicad_pcb'),board)
# Typed embedded symbols, with every unused output explicitly NC.
font='(effects (font (size 1.27 1.27)))'
def prop(n,v,x,y,hide=False):return f'(property "{n}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
def pinmap(ref,pins):
 n=len(pins);result=[]
 types={}
 if ref=='U1':types={str(i):('power_in' if i in (7,14) else 'output' if i in (5,6,8,9) else 'input') for i in range(1,15)}
 elif ref=='U2':types={str(i):('power_in' if i in (7,14) else 'output' if i in (3,6,8,11) else 'input') for i in range(1,15)}
 elif ref=='J1':types={'1':'power_out','2':'power_out','3':'output','4':'output','5':'output','6':'input','7':'input'}
 labels={'U1':['CLR1_N','D1','CLK1','PRE1_N','Q1','Q1_N','GND','Q2_N','Q2','PRE2_N','CLK2','D2','CLR2_N','VCC'],'U2':['A1','B1','Y1','A2','B2','Y2','GND','Y3','A3','B3','Y4','A4','B4','VCC'],'Q1':['E','B','C']}
 for i,p in enumerate(pins):
  right=n==14 and i>=7
  x=7.62 if right else -7.62;y=-2.54*(13-i if right else i)
  label=labels.get(ref,list(pins.values()))[i] if ref in labels else pins[p] or 'NC'
  result.append((p,label,x,y,180 if right else 0,types.get(p,'passive')))
 return result
lib=[];symbols=[];sch=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A4") (title_block (title "Codec-event speaker mute latch") (date "2026-11-17") (rev "1") (comment 1 "3.3 V HC logic; not HCT. External SD pulldown also required at amplifier."))']
places={'J1':(40,50),'U1':(110,50),'U2':(200,50),'Q1':(110,100),'R1':(40,105),'R2':(40,125),'R3':(40,145),'R4':(200,105),'R5':(200,125),'R6':(200,145),'C1':(110,130),'C2':(110,150),'H1':(40,180),'H2':(65,180),'H3':(90,180),'H4':(115,180)}
for ref,value,flib,foot,_,_,pins in parts:
 pdefs=pinmap(ref,pins);hole=ref.startswith('H');height=max(5.08,2.54*(max(1,len(pins) if len(pins)!=14 else 7)-1)+2.54)
 body=f'(symbol "{ref}_0_1" (rectangle (start -5.08 2.54) (end 5.08 {-height}) (stroke (width .254) (type default)) (fill (type none))))'
 pintext=''.join(f'(pin {typ} line (at {x} {y} {a}) (length 2.54) (name "{label}" {font}) (number "{p}" {font}))' for p,label,x,y,a,typ in pdefs)
 lib.append(f'(symbol "Mute:{ref}" (pin_names (offset 1.016)) (in_bom {"no" if hole else "yes"}) (on_board yes) '+prop('Reference',ref,0,5.08)+prop('Value',value,0,7.62)+body+f'(symbol "{ref}_1_1" {pintext}))')
 x,y=places[ref]
 symbols.append(f'(symbol (lib_id "Mute:{ref}") (at {x} {y} 0) (unit 1) (in_bom {"no" if hole else "yes"}) (on_board yes) (dnp no) (uuid "{uid(ref)}")'+prop('Reference',ref,x,y-8)+prop('Value',value,x,y-5)+prop('Footprint',flib+':'+foot,x,y,True)+''.join(f'(pin "{p}" (uuid "{uid(ref+"pin"+p)}"))' for p in pins)+f'(instances (project "mute-latch" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 for p,label,px,py,a,typ in pdefs:
  xx,yy=x+px,y-py;name=pins[p]
  if name is None:symbols.append(f'(no_connect (at {xx} {yy}) (uuid "{uid(ref+"NC"+p)}"))');continue
  endx=xx+(10.16 if a==180 else -10.16)
  symbols.append(f'(wire (pts (xy {xx} {yy}) (xy {endx} {yy})) (stroke (width 0) (type default)) (uuid "{uid(ref+"wire"+p)}"))')
  symbols.append(f'(label "{name}" (at {endx} {yy} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(ref+"label"+p)}"))')
def snap(m):return m.group(1)+str(round(round(float(m.group(2))/1.27)*1.27,4))+' '+str(round(round(float(m.group(3))/1.27)*1.27,4))
def snapped(s):return re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,s)
source=sch[0]+'\n(lib_symbols '+''.join(lib)+')\n'+'\n'.join(symbols)+'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'
(OUT/'mute-latch.kicad_sch').write_text(snapped(source))
(OUT/'Mute.kicad_sym').write_text(snapped('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(lib).replace('"Mute:','"')+')'))
(OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Mute") (type "KiCad") (uri "${KIPRJMOD}/Mute.kicad_sym") (options "") (descr "Original codec-event mute latch")))\n')
(OUT/'mute-latch.kicad_pro').write_text(json.dumps({'meta':{'filename':'mute-latch.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.2,'min_copper_edge_clearance':.5,'min_through_hole_diameter':.3}}}},indent=2)+'\n')
(OUT/'components.json').write_text(json.dumps([{'reference':r,'value':v,'footprint':l+':'+f,'at_mm':[x,y],'pins':p} for r,v,l,f,x,y,p in parts],indent=2)+'\n')
print('Generated routed 45 x 45 mm codec-event mute latch PCB and schematic')
