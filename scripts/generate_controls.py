#!/usr/bin/python3
"""Generate the reviewable passive controls board, not the power/audio carrier.

Requires Debian python3-pcbnew (KiCad 9). Coordinates also feed shell design.
Routing is deterministic two-layer grid A*; GND is an explicit routed tree.
"""
from pathlib import Path
import heapq
import json
import math
import re
import uuid
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware/controls"
OUT.mkdir(parents=True, exist_ok=True)
uid = lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL, "open-conteuse/controls/v1/" + key))
NAMES = ["UP", "PLAY_A", "DOWN", "LEFT", "RIGHT_B", "BACK", "VOL_DOWN", "VOL_UP"]
# Switch actuator centres measured from controls PCB lower-left in CAD xy.
CENTRES = [(22, 12), (51, 20), (22, 34), (11, 23), (33, 23), (57, 34), (45, 49), (57, 49)]
W, H = 70, 65
board = pcb.BOARD()
board.SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))
origin = (30, 30)
def pos(x, y):
    return pcb.VECTOR2I(pcb.FromMM(x + origin[0]), pcb.FromMM(y + origin[1]))
def pt(value):
    return (round(pcb.ToMM(value.x) - origin[0], 4), round(pcb.ToMM(value.y) - origin[1], 4))
net = {}
for name in ["GND", *NAMES]:
    net[name] = pcb.NETINFO_ITEM(board, "/"+name)
    board.Add(net[name])

fps = []
def footprint(library, name, ref, value, x, y):
    fp = pcb.FootprintLoad("/usr/share/kicad/footprints/" + library + ".pretty", name)
    fp.SetFPID(pcb.LIB_ID(library, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pos(x,y))
    fp.SetPath(pcb.KIID_PATH("/" + uid("root") + "/" + uid(ref)))
    fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(pcb.VECTOR2I(pcb.FromMM(.8), pcb.FromMM(.8)))
    fp.Reference().SetTextThickness(pcb.FromMM(.12))
    board.Add(fp)
    if ref.startswith("H"): fp.Reference().SetVisible(False)
    fps.append(fp)
    return fp

switches=[]
for i, ((cx,cy), name) in enumerate(zip(CENTRES,NAMES),1):
    fp=footprint("Button_Switch_THT", "SW_PUSH_6mm", "SW"+str(i), "B3F-1000", cx-3.25, cy-2.25)
    for pad in fp.Pads():
        pad.SetNet(net[name if pad.GetNumber()=="1" else "GND"])
    switches.append(fp)
connector = footprint("Connector_PinHeader_2.54mm", "PinHeader_1x09_P2.54mm_Vertical", "J1", "CONTROLS_3V3_ONLY", 5, 35)
for pad in connector.Pads():
    n=int(pad.GetNumber())
    pad.SetNet(net["GND" if n==9 else NAMES[n-1]])
for i,(x,y) in enumerate([(4,4),(66,4),(4,61),(66,61)],1):
    footprint("MountingHole", "MountingHole_2.7mm_M2.5", "H"+str(i), "M2.5", x,y)

# Rectangle edge, all components at least 2 mm inside outline.
for a,b in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
    line=pcb.PCB_SHAPE(); line.SetShape(pcb.SHAPE_T_SEGMENT)
    line.SetStart(pos(*a)); line.SetEnd(pos(*b)); line.SetLayer(pcb.Edge_Cuts)
    line.SetWidth(pcb.FromMM(.05)); board.Add(line)

# Grid collision masks include pad radius and .30 mm track/clearance allowance.
STEP=.25
nx,ny=int(W/STEP),int(H/STEP)
def grid(p): return (round(p[0]/STEP),round(p[1]/STEP))
def mm(p): return (p[0]*STEP,p[1]*STEP)
obstacles={}
for fp in fps:
    for pad in fp.Pads():
        x,y=pt(pad.GetPosition()); size=pad.GetSize()
        # conservative rectangular keepout, adequate for round pads too
        rx,ry=pcb.ToMM(size.x)/2+.45,pcb.ToMM(size.y)/2+.45
        for ix in range(math.floor((x-rx)/STEP), math.ceil((x+rx)/STEP)+1):
            for iy in range(math.floor((y-ry)/STEP), math.ceil((y+ry)/STEP)+1):
                for layer in (0,1): obstacles.setdefault((ix,iy,layer),set()).add(pad.GetNetname().lstrip("/") or "HOLE")

def track(a,b,name,layer=pcb.F_Cu):
    if a==b: return
    item=pcb.PCB_TRACK(board);item.SetStart(pos(*a));item.SetEnd(pos(*b))
    item.SetWidth(pcb.FromMM(.25));item.SetLayer(layer);item.SetNet(net[name]);board.Add(item)

def mark(a,b,name,layer=0):
    # axis-aligned segments only
    ga,gb=grid(a),grid(b)
    for x in range(min(ga[0],gb[0])-2,max(ga[0],gb[0])+3):
        for y in range(min(ga[1],gb[1])-2,max(ga[1],gb[1])+3):
            obstacles.setdefault((x,y,layer),set()).add(name)

via_positions={}
pad_centres=[(pt(p.GetPosition()),p.GetNetname().lstrip('/'),pcb.ToMM(p.GetDrillSize().x)/2) for fp in fps for p in fp.Pads()]
def via_kind(point,name):
    for centre,padnet,radius in pad_centres:
        dist=math.dist(point,centre)
        if dist<=.35 and padnet==name: return 'pad'
        if dist<radius+.45: return 'blocked'
    for centre,vianet in via_positions.items():
        if point==centre and vianet==name: return 'existing'
        if math.dist(point,centre)<.7: return 'blocked'
    return 'new'

def route(start,end,name):
    start=(*grid(start),0);end=(*grid(end),0)
    pending=[(0,0,start)]; cost={start:0}; parent={}
    while pending:
        _,g,current=heapq.heappop(pending)
        if current==end: break
        if g!=cost[current]: continue
        candidates=[(current[0]+dx,current[1]+dy,current[2]) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
        candidates.append((current[0],current[1],1-current[2]))
        for nxt in candidates:
            if not (4<=nxt[0]<=nx-4 and 4<=nxt[1]<=ny-4): continue
            via=nxt[2]!=current[2]
            if via:
                if via_kind(mm(nxt[:2]),name)=="blocked": continue
                if any(obstacles.get((nxt[0]+dx,nxt[1]+dy,layer),set())-{name}
                       for dx in range(-3,4) for dy in range(-3,4) for layer in (0,1)): continue
            elif obstacles.get(nxt,set())-{name}: continue
            ng=g+(12 if via else 1)
            if ng<cost.get(nxt,10**9):
                cost[nxt]=ng;parent[nxt]=current
                heapq.heappush(pending,(ng+abs(nxt[0]-end[0])+abs(nxt[1]-end[1]),ng,nxt))
    else: raise RuntimeError("cannot route "+name)
    path=[end]
    while path[-1]!=start: path.append(parent[path[-1]])
    path.reverse()
    # Merge collinear grid steps for a compact native PCB and readable diff.
    simple=[path[0]]
    for i in range(1,len(path)-1):
        before=tuple(path[i][axis]-path[i-1][axis] for axis in range(3))
        after=tuple(path[i+1][axis]-path[i][axis] for axis in range(3))
        if before!=after: simple.append(path[i])
    simple.append(path[-1])
    for a,b in zip(simple,simple[1:]):
        if a[2]!=b[2]:
            kind=via_kind(mm(a[:2]),name)
            if kind in ("pad","existing"): continue
            via_positions[mm(a[:2])]=name
            v=pcb.PCB_VIA(board);v.SetPosition(pos(*mm(a[:2])))
            v.SetWidth(pcb.F_Cu,pcb.FromMM(.65));v.SetDrill(pcb.FromMM(.3));v.SetViaType(pcb.VIATYPE_THROUGH)
            v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNet(net[name]);board.Add(v)
            for dx in range(-3,4):
                for dy in range(-3,4):
                    for layer in (0,1): obstacles.setdefault((a[0]+dx,a[1]+dy,layer),set()).add(name)
        else:
            track(mm(a[:2]),mm(b[:2]),name,pcb.F_Cu if a[2]==0 else pcb.B_Cu)
            mark(mm(a[:2]),mm(b[:2]),name,a[2])

# Connect duplicate signal pads directly across switch body before routing.
for fp,name in zip(switches,NAMES):
    pads=sorted([pt(p.GetPosition()) for p in fp.Pads() if p.GetNumber()=="1"])
    track(pads[0],pads[1],name);mark(pads[0],pads[1],name)
# Shortest routes first keeps each control locally simple.
for i in sorted(range(8),key=lambda i: abs(CENTRES[i][0]-5)+abs(CENTRES[i][1]-(35+2.54*i))):
    start=next(pt(p.GetPosition()) for p in connector.Pads() if p.GetNumber()==str(i+1))
    # J1 y is 2.54 mm pitch; grid does not exactly represent it. Escape to
    # grid first with a <=0.12 mm segment within the pad annulus.
    snapped=mm(grid(start));track(start,snapped,NAMES[i])
    end=min([pt(p.GetPosition()) for p in switches[i].Pads() if p.GetNumber()=="1"])
    route(snapped,end,NAMES[i])
# Route ground as an explicit tree on both layers. No copper fill is required.
grounds=[pt(p.GetPosition()) for fp in fps for p in fp.Pads() if p.GetNetname()=="/GND"]
connected=[grounds.pop(0)]
while grounds:
    distance,a,b=min((abs(a[0]-b[0])+abs(a[1]-b[1]),a,b) for a in connected for b in grounds)
    for point in (a,b):
        snapped=mm(grid(point))
        track(point,snapped,"GND")
    route(mm(grid(a)),mm(grid(b)),"GND")
    connected.append(b);grounds.remove(b)
for text,x,y,size in [("OPEN CONTEUSE CONTROLS v0.1",35,3,.8),("3V3 GPIO ONLY - NO BATTERY",35,6,.8),("J1.9 GND",16,60,.8)]:
    t=pcb.PCB_TEXT(board);t.SetText(text);t.SetPosition(pos(x,y));t.SetLayer(pcb.F_SilkS)
    t.SetTextSize(pcb.VECTOR2I(pcb.FromMM(size),pcb.FromMM(size)));t.SetTextThickness(pcb.FromMM(.12));board.Add(t)
board.BuildConnectivity()
pcb.SaveBoard(str(OUT/"controls.kicad_pcb"),board)

# Embedded symbols keep the schematic portable without custom libraries.
font='(effects (font (size 1.27 1.27)))'
def prop(name,value,x,y,hidden=False):
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hidden else '')+'))'
def libsymbol(name,pins):
    # pin tuple: number, name, x, y, orientation
    body=''.join(f'(pin passive line (at {x} {y} {a}) (length 2.54) (name "{label}" {font}) (number "{num}" {font}))' for num,label,x,y,a in pins)
    return f'(symbol "Conteuse:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) '+prop('Reference','J' if name=='Controls' else 'SW',0,4)+prop('Value',name,0,-4)+f'(symbol "{name}_0_1" (rectangle (start -2.54 2.54) (end 2.54 -2.54) (stroke (width .254) (type default)) (fill (type none)))) (symbol "{name}_1_1" {body}))'
conn_pins=[(str(i+1),name,-5.08, -i*2.54,0) for i,name in enumerate([*NAMES,'GND'])]
sw_pins=[('1','1',-5.08,0,0),('2','2',5.08,0,180)]
# simple symbol rectangle for connector extends to include all pins
conn_lib=libsymbol('Controls',conn_pins).replace('(end 2.54 -2.54)', '(end 2.54 -22.86)')
sch=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A4")',
     '(title_block (title "Open Conteuse passive controls") (date "2026-11-17") (rev "0.1") (comment 1 "Bench prototype. No power/audio carrier. 3.3 V GPIO only."))',
     '(lib_symbols '+conn_lib+libsymbol('Button',sw_pins)+')']
def label(name,x,y):
    sch.append(f'(label "{name}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(name+str(x)+str(y))}"))')
def wire(x,y,xx,yy,key):
    sch.append(f'(wire (pts (xy {x} {y}) (xy {xx} {yy})) (stroke (width 0) (type default)) (uuid "{uid(key)}"))')
def instance(lib,ref,value,fp,x,y,pins):
    sch.append(f'(symbol (lib_id "Conteuse:{lib}") (at {x} {y} 0) (unit 1) (in_bom {"no" if lib=="Hole" else "yes"}) (on_board yes) (dnp no) (uuid "{uid(ref)}")'+prop('Reference',ref,x,y-6)+prop('Value',value,x,y-3.5)+prop('Footprint',fp,x,y,True)+''.join(f'(pin "{p[0]}" (uuid "{uid(ref+"pin"+p[0])}"))' for p in pins)+f'(instances (project "controls" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
instance('Controls','J1','CONTROLS_3V3_ONLY','Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical',60,60,conn_pins)
for i,name in enumerate([*NAMES,'GND']):
    y=60+i*2.54;wire(54.92,y,45,y,'J'+name);label(name,45,y)
for i,name in enumerate(NAMES):
    x,y=115+(i%2)*65,55+(i//2)*30
    instance('Button','SW'+str(i+1),'B3F-1000','Button_Switch_THT:SW_PUSH_6mm',x,y,sw_pins)
    wire(x-5.08,y,x-15,y,'S'+name);label(name,x-15,y)
    wire(x+5.08,y,x+12,y,'G'+name);label('GND',x+12,y)
# Mounting holes in both schematic and board for parity.
hole='(symbol "Conteuse:Hole" (in_bom no) (on_board yes) '+prop('Reference','H',0,3)+prop('Value','M2.5',0,-3)+'(symbol "Hole_0_1" (circle (center 0 0) (radius 1.27) (stroke (width .254) (type default)) (fill (type none)))))'
sch[2]=sch[2][:-1]+hole+')'
for i in range(4): instance('Hole','H'+str(i+1),'M2.5','MountingHole:MountingHole_2.7mm_M2.5',50+i*15,160,[])
sch.append('(sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
schematic='\n'.join(sch)
def snap(match):
    return match.group(1)+str(round(round(float(match.group(2))/1.27)*1.27,4))+' '+str(round(round(float(match.group(3))/1.27)*1.27,4))
schematic=re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,schematic)
(OUT/'controls.kicad_sch').write_text(schematic)
library=conn_lib+libsymbol('Button',sw_pins)+hole
library=library.replace('"Conteuse:','"')
library=re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,library)
(OUT/'Conteuse.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+library+')')
(OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Conteuse") (type "KiCad") (uri "${KIPRJMOD}/Conteuse.kicad_sym") (options "") (descr "Open Conteuse passive controls")))\n')
# Explicit project minima, no exclusions or ignored errors.
(OUT/'controls.kicad_pro').write_text(json.dumps({"meta":{"filename":"controls.kicad_pro","version":1},"board":{"design_settings":{"rules":{"min_clearance":0.2,"min_track_width":0.2,"min_copper_edge_clearance":0.5,"min_through_hole_diameter":0.3}}}},indent=2)+'\n')
(ROOT/'enclosure/controls.json').write_text(json.dumps({"pcb_mm":[W,H,1.6],"actuators_mm":CENTRES,"holes_mm":[[4,4],[66,4],[4,61],[66,61]]},indent=2)+'\n')
print('Generated schematic and routed controls PCB')
