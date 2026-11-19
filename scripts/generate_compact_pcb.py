#!/usr/bin/python3
"""Generate real native KiCad compact schematic/placement, DSN route input.
Requires KiCad9 pcbnew; library footprints retain KiCad attribution.
"""
from pathlib import Path
import json,uuid,math,re,sys
import pcbnew as pcb
from compact_design import ROOT,OUT,write
from kicad_sexp import symbol,pins as symbolpins
from compact_pin_contracts import CONTRACTS
from compact_router import SETTINGS
from compact_plane import ground

def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'open-conteuse/compact-r1/'+key))
def pos(x,y):return pcb.VECTOR2I(pcb.FromMM(x+30),pcb.FromMM(y+30))
def prop(n,v,x,y,hide=False):
 v=str(v).replace('"','\\"')
 return f'(property "{n}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
def custom(lib,name,pads,rect,size=None):
 f=pcb.FOOTPRINT(None);f.SetFPID(pcb.LIB_ID('Compact',name));f.SetAttributes(pcb.FP_SMD)
 for num,x,y,w,h in pads:
  p=pcb.PAD(f);p.SetNumber(str(num));p.SetAttribute(pcb.PAD_ATTRIB_SMD);p.SetShape(pcb.PAD_SHAPE_ROUNDRECT);p.SetRoundRectRadiusRatio(.15);p.SetSize(pcb.VECTOR2I(pcb.FromMM(w),pcb.FromMM(h)));p.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));ls=pcb.LSET();[ls.AddLayer(a) for a in [pcb.F_Cu,pcb.F_Paste,pcb.F_Mask]];p.SetLayerSet(ls);f.Add(p)
 for layer,margin in [(pcb.F_Fab,0),(pcb.F_CrtYd,.3)]:
  s=pcb.PCB_SHAPE();s.SetShape(pcb.SHAPE_T_RECT);s.SetStart(pcb.VECTOR2I(pcb.FromMM(rect[0]-margin),pcb.FromMM(rect[1]-margin)));s.SetEnd(pcb.VECTOR2I(pcb.FromMM(rect[2]+margin),pcb.FromMM(rect[3]+margin)));s.SetLayer(layer);s.SetWidth(pcb.FromMM(.05));f.Add(s)
 pcb.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),f)

def generate(v):
 d=json.loads((OUT/(v+'.json')).read_text());dest=OUT/v;dest.mkdir(exist_ok=True);lib=dest/'Compact.pretty';lib.mkdir(exist_ok=True)
 # DSJ0014A TI recommended footprint: verify drawing against this local footprint before release.
 custom(lib,'TPS63020_DSJ',[(i,-1.45,-1.5+(i-1)*.5,.7,.28) for i in range(1,8)]+[(i,1.45,1.5-(i-8)*.5,.7,.28) for i in range(8,15)]+[(15,0,0,1.6,2.8)],[-1.5,-2,1.5,2])
 # Manufacturer SJ-4351x SMT recommended top view, front at x=0, body extends +X.
 custom(lib,'SJ43514',[(1,.6,3.5,2,3),(2,13,3.5,2,3),(3,5.3,-3.5,2,3),(4,3.5,3.5,2,3)],[0,-4.5,18,4.5])
 board=pcb.BOARD();board.SetCopperLayerCount(4);board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.2))
 contracts={k:dict(v) for k,v in CONTRACTS.items()}
 for ref,ln,sn in [('U1','RF_Module','ESP32-S3-WROOM-1'),('U2','Battery_Management','BQ24074RGT'),('U8','Audio','MAX98357A')]:contracts[ref]=symbolpins(symbol(Path('/usr/share/kicad/symbols')/(ln+'.kicad_sym'),sn))
 nets=sorted({n for p in d['parts'] for n in p['pins'].values() if n});net={}
 for n in nets:net[n]=pcb.NETINFO_ITEM(board,'/'+n);board.Add(net[n])
 fps=[]
 for p in d['parts']:
  libname,foot=p['footprint'].split(':');fp=pcb.FootprintLoad(str(lib) if libname=='Compact' else '/usr/share/kicad/footprints/'+libname+'.pretty',foot)
  if fp is None:raise ValueError('Missing footprint '+p['footprint'])
  fp.SetFPID(pcb.LIB_ID(libname,foot));fp.SetReference(p['ref']);fp.SetValue(p['mpn']);fp.SetPosition(pos(*p['xy']));fp.SetOrientationDegrees(p['angle']);fp.SetPath(pcb.KIID_PATH('/'+uid(v+'root')+'/'+uid(v+p['ref'])))
  fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
  if p['ref'].startswith('TP'):fp.SetAttributes(fp.GetAttributes()|pcb.FP_EXCLUDE_FROM_BOM)
  if p['ref']=='U1':
   for item in list(fp.GraphicalItems()):
    if item.GetLayer()==pcb.F_SilkS:fp.Remove(item)
  physical={pad.GetNumber() for pad in fp.Pads() if pad.GetNumber()}
  missing=set(p['pins'])-physical
  if missing:print(p['ref'],'declared pins not in footprint',missing);raise ValueError('pin contract')
  # Every physical NC pad remains a named unconnected net, matching schematic no-connects.
  for pin in physical:p['pins'].setdefault(pin,None)
  for pad in fp.Pads():
   pin=pad.GetNumber()
   if not pin:continue
   n=p['pins'].get(pin)
   if n:pad.SetNet(net[n])
   else:
    pn=contracts.get(p['ref'],{}).get(pin,(pin,'passive'))[0]
    key=f'unconnected-({p["ref"]}-'+(pn+'-' if pn!=pin else '')+f'Pad{pin})'
    if key not in net:net[key]=pcb.NETINFO_ITEM(board,key);board.Add(net[key])
    pad.SetNet(net[key])
  if p['ref']=='U1':
   fp.SetFPID(pcb.LIB_ID('Compact','ESP32-S3-WROOM-1-R1'));p['footprint']='Compact:ESP32-S3-WROOM-1-R1'
   for zone in list(fp.Zones()):fp.Remove(zone)
   for pad in fp.Pads():
    if pad.GetAttribute()==pcb.PAD_ATTRIB_PTH and pad.GetNumber()=='41':pad.SetDrillSize(pcb.VECTOR2I(pcb.FromMM(.3),pcb.FromMM(.3)));pad.SetSize(pcb.VECTOR2I(pcb.FromMM(.5),pcb.FromMM(.5)))
   original=fp.GetPosition();angle=fp.GetOrientationDegrees();fp.SetPosition(pcb.VECTOR2I(0,0));fp.SetOrientationDegrees(0)
   pcb.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),fp);fp.SetPosition(original);fp.SetOrientationDegrees(angle)
  board.Add(fp);fps.append(fp)
 # Mounting holes absent from electronic BOM but present schematic and parity.
 for i,(x,y) in enumerate(d['pcb']['holes'],1):
  fp=pcb.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty','MountingHole_2.2mm_M2');fp.SetFPID(pcb.LIB_ID('MountingHole','MountingHole_2.2mm_M2'));fp.SetReference('H'+str(i));fp.SetValue('M2');fp.SetPosition(pos(x,y));fp.SetPath(pcb.KIID_PATH('/'+uid(v+'root')+'/'+uid(v+'H'+str(i))));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);fp.SetAttributes(fp.GetAttributes()|pcb.FP_EXCLUDE_FROM_BOM);board.Add(fp)
  d['parts'].append(dict(ref='H'+str(i),mpn='M2',footprint='MountingHole:MountingHole_2.2mm_M2',pins={},xy=[x,y],size=[4.4,4.4,0],section='mounts',cost_eur=[0,0],angle=0,source=''))
 x,y,w,h=d['pcb']['outline']
 outline=[(x+1,y),(x+w-1,y),(x+w,y+1),(x+w,y+h-1),(x+w-1,y+h),(x+1,y+h),(x,y+h-1),(x,y+1)]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  s=pcb.PCB_SHAPE();s.SetShape(pcb.SHAPE_T_SEGMENT);s.SetStart(pos(*a));s.SetEnd(pos(*b));s.SetWidth(pcb.FromMM(.05));s.SetLayer(pcb.Edge_Cuts);board.Add(s)
 # Module antenna overhangs PCB top edge. No copper under module antenna in any layer.
 z=pcb.ZONE(board);z.SetIsRuleArea(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True)
 layers=pcb.LSET()
 for layer in [pcb.F_Cu,pcb.In1_Cu,pcb.In2_Cu,pcb.B_Cu]:layers.AddLayer(layer)
 z.SetLayerSet(layers);poly=z.Outline();poly.NewOutline()
 for a,b in [(8.5,-12),(56.5,-12),(56.5,9),(8.5,9)]:q=pos(a,b);poly.Append(q.x,q.y)
 board.Add(z)
 pack(board,d,fps)
 local_power(board,fps,net)
 pcb.SaveBoard(str(dest/(v+'.kicad_pcb')),board)
 # Set explicit limits without exclusions. Four-layer routing is still subject to SI/thermal review.
 pro={'meta':{'filename':v+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_copper_edge_clearance':.25,'min_through_hole_diameter':.3,'min_via_diameter':.5,'min_hole_clearance':.15}}},'net_settings':{'classes':[{'name':'Default','clearance':.15,'track_width':.2,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.2,'diff_pair_via_gap':.25}]}}
 (dest/(v+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
 (dest/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Compact") (type "KiCad") (uri "${KIPRJMOD}/Compact.pretty") (options "") (descr "Original compact R1 footprints; drawing review pending")))\n')
 make_schematic(d,dest,v)
 board=pcb.LoadBoard(str(dest/(v+'.kicad_pcb')))
 ds=board.GetDesignSettings();ds.m_MinClearance=pcb.FromMM(.15);ds.m_TrackMinWidth=pcb.FromMM(.15);ds.m_HoleClearance=pcb.FromMM(.15)
 ds.m_CopperEdgeClearance=pcb.FromMM(.25);ds.m_NetSettings.GetDefaultNetclass().SetClearance(pcb.FromMM(.15))
 power=pcb.NETCLASS('Power');power.SetClearance(pcb.FromMM(.15));power.SetTrackWidth(pcb.FromMM(.6));power.SetViaDiameter(pcb.FromMM(.8));power.SetViaDrill(pcb.FromMM(.4));ds.m_NetSettings.SetNetclass('Power',power)
 for name in ['SYS','BAT','VBUS','3V2','GND','SW_L1','SW_L2','SPK_P','SPK_N','LCD_5V','LCD_SW']:
  ni=board.FindNet('/'+name)
  if ni:ni.SetNetClass(power);ds.m_NetSettings.SetNetclassPatternAssignment('/'+name,'Power')
 pcb.SaveBoard(str(dest/(v+'.kicad_pcb')),board)
 ground(board);pcb.SaveBoard(str(dest/(v+'.kicad_pcb')),board)
 print('DSN',pcb.ExportSpecctraDSN(board,str(ROOT/'work/compact-r1'/(v+'.dsn'))))
 dsn=ROOT/'work/compact-r1'/(v+'.dsn');s=dsn.read_text();s=s.replace('    (boundary','    '+SETTINGS+'\n    (boundary',1);s=s.replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)');dsn.write_text(s)
 (dest/'components.json').write_text(json.dumps(d,indent=2)+'\n')

def local_power(board,fps,net):
 """Critical buck-boost switching loops and first caps are hand-routed on F.Cu.
 No vias/long auto-routed detours are permitted on SW_L1/SW_L2.
 """
 fs={f.GetReference():f for f in fps}
 def at(ref,num):
  q=next(q for q in fs[ref].Pads() if q.GetNumber()==str(num)).GetPosition();return (pcb.ToMM(q.x)-30,pcb.ToMM(q.y)-30)
 def line(name,a,b,w):
  if a==b:return
  t=pcb.PCB_TRACK(board);t.SetStart(pos(*a));t.SetEnd(pos(*b));t.SetWidth(pcb.FromMM(w));t.SetLayer(pcb.F_Cu);t.SetNet(net[name]);t.SetLocked(True);board.Add(t)
 for name,pins,escape,last in [('SW_L1',[8,9],54.4,1),('SW_L2',[6,7],49.6,2)]:
  for n in pins:
   a=at('U3',n);line(name,a,(escape,a[1]),.25);line(name,(escape,a[1]),(escape,47),.25)
  goal=at('L1',last);line(name,(escape,47),(escape,goal[1]),.6);line(name,(escape,goal[1]),goal,.6)
 for name,pins,escape,cap,pad in [('SYS',[10,11],55.2,'C7',1),('3V2',[4,5],48.8,'C4',1)]:
  target=at(cap,pad)
  for n in pins:
   a=at('U3',n);line(name,a,(escape,a[1]),.25);line(name,(escape,a[1]),(escape,target[1]),.25)
  line(name,(escape,target[1]),target,.6)
 # VINA decoupling sits directly beside VINA/GND, not across the converter.
 a=at('U3',1);goal=at('C8',1);line('VINA',a,(a[0],goal[1]),.2);line('VINA',(a[0],goal[1]),goal,.2)
 a=at('U3',2);goal=at('C8',2);line('GND',a,(goal[0],a[1]),.2);line('GND',(goal[0],a[1]),goal,.2)
 for cap,delta in [('C4',(-.8,0)),('C7',(.8,0)),('C8',(-.8,0))]:
  a=at(cap,2);q=(a[0]+delta[0],a[1]+delta[1]);line('GND',a,q,.4)
  via=pcb.PCB_VIA(board);via.SetPosition(pos(*q));via.SetWidth(pcb.F_Cu,pcb.FromMM(.6));via.SetDrill(pcb.FromMM(.3));via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNet(net['GND']);via.SetLocked(True);board.Add(via)

def pack(board,d,fps):
 """Keep functional controls/ports fixed; place ICs/passives near desired sites.
 Uses actual library courtyard envelopes; not a component/thermal validation.
 """
 def bounds(fp):
  items=[a for a in fp.GraphicalItems() if a.GetLayer()==pcb.F_CrtYd]
  if fp.GetReference()=='U1':return [22.75,9,42.25,29.3]
  if not items:items=list(fp.Pads())
  boxes=[a.GetBoundingBox() for a in items]
  return [min(pcb.ToMM(b.GetLeft()) for b in boxes)-30,min(pcb.ToMM(b.GetTop()) for b in boxes)-30,max(pcb.ToMM(b.GetRight()) for b in boxes)-30,max(pcb.ToMM(b.GetBottom()) for b in boxes)-30]
 def intersects(a,b):return a[0]<b[2]+.15 and a[2]>b[0]-.15 and a[1]<b[3]+.15 and a[3]>b[1]-.15
 fixed={'U1','U3','L1','C3','R2','C4','C7','C8','C29','C30','J1','J2','J3','J8','SW9'}|{'SW'+str(i) for i in range(1,9)}
 occupied=[[x-2.4,y-2.4,x+2.4,y+2.4] for x,y in d['pcb']['holes']]
 for f in fps:
  if f.GetReference() in fixed:
   occupied.append(bounds(f));f.SetLocked(True)
 moving=[f for f in fps if f.GetReference() not in fixed]
 moving.sort(key=lambda f:(0 if f.GetReference().startswith(('U','J','L')) else 1,-(bounds(f)[2]-bounds(f)[0])*(bounds(f)[3]-bounds(f)[1])))
 pd={p['ref']:p for p in d['parts']}
 for f in moving:
  ref=f.GetReference();ox,oy=pd[ref]['xy'];a=bounds(f);dx,dy=pcb.ToMM(f.GetPosition().x)-30,pcb.ToMM(f.GetPosition().y)-30;local=[a[0]-dx,a[1]-dy,a[2]-dx,a[3]-dy]
  choices=[]
  for xi in range(8,122):
   for yi in range(20,181):
    x,y=xi/2,yi/2;rect=[local[0]+x,local[1]+y,local[2]+x,local[3]+y]
    if rect[0]<2.8 or rect[1]<9.3 or rect[2]>62.2 or rect[3]>91.7:continue
    if any(intersects(rect,b) for b in occupied):continue
    choices.append(((x-ox)**2+(y-oy)**2,x,y,rect))
  if not choices:raise ValueError('No placement for '+ref)
  _,x,y,rect=min(choices);f.SetPosition(pos(x,y));pd[ref]['xy']=[x,y];occupied.append(rect)
 print(d['variant'],'packed',len(fps),'footprints')

def make_schematic(d,dest,v):
 font='(effects (font (size 1.27 1.27)))';libs=[];symbols=[]
 contracts={k:dict(v) for k,v in CONTRACTS.items()}
 for ref,ln,sn in [('U1','RF_Module','ESP32-S3-WROOM-1'),('U2','Battery_Management','BQ24074RGT'),('U8','Audio','MAX98357A')]:contracts[ref]=symbolpins(symbol(Path('/usr/share/kicad/symbols')/(ln+'.kicad_sym'),sn))
 # Pin contract for logic and codec, audited against manufacturers; passive inputs/outputs used only for physical connectors/passives.
 for p in d['parts']:
  ref=p['ref'];pins=p['pins'];hole=ref.startswith(('H','TP'));ps=sorted(pins,key=lambda s:(not s.isdigit(),int(s) if s.isdigit() else s));n=len(ps);half=math.ceil(n/2);height=max(2.54,(half-1)*2.54)
  pdefs=[]
  for i,pin in enumerate(ps):
   right=i>=half;xx=12.7 if right else -12.7;yy=-(i-half if right else i)*2.54
   name,typ=contracts.get(ref,{}).get(pin,(pin,'passive'))
   if typ=='unspecified':typ='passive'
   if pins[pin] is None:typ='passive' # Explicit NC per-instance, including optional output pins.
   # OPI pins are explicit NC; retain manufacturer pin names.
   pdefs.append((pin,name,xx,yy,180 if right else 0,typ))
  body=f'(symbol "{ref}_0_1" (rectangle (start -10.16 2.54) (end 10.16 {-height-2.54}) (stroke (width .254) (type default)) (fill (type none))))'
  text=''.join(f'(pin {typ} line (at {xx} {yy} {a}) (length 2.54) (name "{name}" {font}) (number "{pin}" {font}))' for pin,name,xx,yy,a,typ in pdefs)
  libs.append(f'(symbol "Compact:{ref}" (pin_names (offset .508)) (in_bom {"no" if hole else "yes"}) (on_board yes) '+prop('Reference',ref,0,6)+prop('Value',p['mpn'],0,9)+body+f'(symbol "{ref}_1_1" {text}))')
  i=len(symbols) # placement index separately from label count
  idx=d['parts'].index(p);x=76.2+(idx%7)*177.8;y=50.8+(idx//7)*101.6
  symbols.append(f'(symbol (lib_id "Compact:{ref}") (at {x} {y} 0) (unit 1) (in_bom {"no" if hole else "yes"}) (on_board yes) (dnp no) (uuid "{uid(v+ref)}")'+prop('Reference',ref,x,y-12.7)+prop('Value',p['mpn'],x,y-8.89)+prop('Footprint',p['footprint'],x,y,True)+prop('Datasheet',p['source'],x,y,True)+''.join(f'(pin "{pin}" (uuid "{uid(v+ref+pin)}"))' for pin in ps)+f'(instances (project "{v}" (path "/{uid(v+"root")}" (reference "{ref}") (unit 1)))))')
  for pin,name,px,py,a,typ in pdefs:
   xx,yy=x+px,y-py;net=pins[pin]
   if net is None:symbols.append(f'(no_connect (at {xx} {yy}) (uuid "{uid(v+ref+pin+"NC")}"))');continue
   end=xx+(12.7 if a==180 else -12.7)
   symbols.append(f'(wire (pts (xy {xx} {yy}) (xy {end} {yy})) (stroke (width 0) (type default)) (uuid "{uid(v+ref+pin+"wire")}"))')
   symbols.append(f'(label "{net}" (at {end} {yy} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(v+ref+pin+"label")}"))')
 # Explicit power sources at USB/cell and regulator outputs; no ERC exclusions.
 for i,net in enumerate(['GND','VBUS']):
  ref='#FLG'+str(i+1);x=76.2+i*50.8;y=1778
  libs.append(f'(symbol "Compact:FLAG{i}" (power) (in_bom no) (on_board no) '+prop('Reference',ref,0,0,True)+prop('Value','PWR_FLAG',0,0,True)+f'(symbol "FLAG{i}_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" {font}) (number "1" {font}))))')
  symbols.append(f'(symbol (lib_id "Compact:FLAG{i}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(v+ref)}")'+prop('Reference',ref,x,y,True)+prop('Value','PWR_FLAG',x,y,True)+f'(pin "1" (uuid "{uid(v+ref+"pin")}")) (instances (project "{v}" (path "/{uid(v+"root")}" (reference "{ref}") (unit 1)))))')
  symbols.append(f'(label "{net}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(v+ref+"label")}"))')
 source=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid(v+"root")}") (paper "User" 1400 1900) (title_block (title "Open Conteuse compact {v} R1 - engineering prototype") (rev "R1") (date "2026-11-18"))\n(lib_symbols '+''.join(libs)+')\n'+'\n'.join(symbols)+'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'
 def snap(m):return m.group(1)+str(round(round(float(m.group(2))/1.27)*1.27,4))+' '+str(round(round(float(m.group(3))/1.27)*1.27,4))
 source=re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,source)
 (dest/(v+'.kicad_sch')).write_text(source)
 (dest/'Compact.kicad_sym').write_text(re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,'(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(libs).replace('"Compact:','"')+')'))
 (dest/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Compact") (type "KiCad") (uri "${KIPRJMOD}/Compact.kicad_sym") (options "") (descr "Original symbol pin contracts")))\n')
if __name__=='__main__':
 write()
 for v in sys.argv[1:] or ['mini','explore']:generate(v)
