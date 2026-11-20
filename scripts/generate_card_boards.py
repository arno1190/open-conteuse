#!/usr/bin/python3
"""Generate the current routed contact reader and passive serial-ID card PCB.
Never modifies the hand-reviewed main boards. Requires KiCad 9 pcbnew.
"""
import gc,json
from pathlib import Path
import pcbnew as p
from project import HARDWARE
from schematic import make_schematic,uid
gc.disable()

def vec(x,y):return p.VECTOR2I(p.FromMM(x+30),p.FromMM(y+30))
def custom_pad(lib,name,pads,body,bottom=False):
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Compact',name));f.SetAttributes(p.FP_SMD)
 for num,x,y,w,h in pads:
  q=p.PAD(f);q.SetNumber(str(num));q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_ROUNDRECT);q.SetRoundRectRadiusRatio(.1);q.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));q.SetSize(p.VECTOR2I(p.FromMM(w),p.FromMM(h)));layers=p.LSET()
  for layer in ([p.B_Cu,p.B_Mask] if bottom else [p.F_Cu,p.F_Mask]+([] if name=='Wire3_Top' else [p.F_Paste])):layers.AddLayer(layer)
  q.SetLayerSet(layers);f.Add(q)
 for layer,m in ([(p.B_Fab,0),(p.B_CrtYd,.25)] if bottom else [(p.F_Fab,0),(p.F_CrtYd,.25)]):
  q=p.PCB_SHAPE();q.SetShape(p.SHAPE_T_RECT);q.SetStart(p.VECTOR2I(p.FromMM(body[0]-m),p.FromMM(body[1]-m)));q.SetEnd(p.VECTOR2I(p.FromMM(body[2]+m),p.FromMM(body[3]+m)));q.SetWidth(p.FromMM(.05));q.SetLayer(layer);f.Add(q)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),f)

def build(name,w,h,parts,holes,paths,vias):
 dest=HARDWARE/name;dest.mkdir(parents=True,exist_ok=True);lib=dest/'Compact.pretty';lib.mkdir(exist_ok=True)
 if name=='card-reader':
  custom_pad(lib,'Pogo_P70_1000045',[(1,0,0,2.2,2.2)],[-1,-1,1,1])
  custom_pad(lib,'Wire3_Top',[(1,-2.5,0,1.3,1.8),(2,0,0,1.3,1.8),(3,2.5,0,1.3,1.8)],[-3.2,-1,3.2,1])
 else:
  # Long ground pad makes before the shorter data pad. No solder paste or
  # vias in the contact wipe lanes; selective hard-gold finish is RFQ scope.
  custom_pad(lib,'ContactPads_Bottom',[(1,7,6,3,10),(2,13,5,3,8)],[5.5,1,14.5,11],True)
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Compact','Mount_M1_6'))
 q=p.PAD(f);q.SetNumber('');q.SetAttribute(p.PAD_ATTRIB_NPTH);q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetSize(p.VECTOR2I(p.FromMM(1.8),p.FromMM(1.8)));q.SetDrillSize(p.VECTOR2I(p.FromMM(1.8),p.FromMM(1.8)));q.SetLayerSet(p.LSET.AllCuMask());f.Add(q)
 q=p.PCB_SHAPE();q.SetShape(p.SHAPE_T_RECT);q.SetStart(p.VECTOR2I(p.FromMM(-1.8),p.FromMM(-1.8)));q.SetEnd(p.VECTOR2I(p.FromMM(1.8),p.FromMM(1.8)));q.SetLayer(p.F_CrtYd);q.SetWidth(p.FromMM(.05));f.Add(q);p.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),f)
 board=p.BOARD();board.SetCopperLayerCount(2);board.GetDesignSettings().SetBoardThickness(p.FromMM(1.6 if name=='card-reader' else .8));nets={}
 for net in sorted({n for r in parts for n in r['pins'].values() if n}):
  nets[net]=p.NETINFO_ITEM(board,'/'+net);board.Add(nets[net])
 fps={}
 for r in parts:
  ln,fn=r['footprint'].split(':');f=p.FootprintLoad(str(lib) if ln=='Compact' else '/usr/share/kicad/footprints/'+ln+'.pretty',fn);assert f is not None,r['footprint']
  f.SetFPID(p.LIB_ID(ln,fn));f.SetReference(r['ref']);f.SetValue(r['mpn']);f.SetPosition(vec(*r['xy']));f.SetPath(p.KIID_PATH('/'+uid(name+'root')+'/'+uid(name+r['ref'])));f.Reference().SetVisible(False);f.Value().SetVisible(False)
  for pad in f.Pads():
   n=pad.GetNumber()
   if not n:continue
   r['pins'].setdefault(n,None);net=r['pins'][n]
   if net:pad.SetNet(nets[net])
   else:
    label=f'unconnected-({r["ref"]}-'+('NC-' if name=='story-card' and r['ref']=='U1' else '')+f'Pad{n})';nn=p.NETINFO_ITEM(board,label);board.Add(nn);pad.SetNet(nn)
  board.Add(f);fps[r['ref']]=f
 for i,xy in enumerate(holes,1):
  ref='H'+str(i);fp='Compact:Mount_M1_6';f=p.FootprintLoad(str(lib),fp.split(':')[1]);f.SetFPID(p.LIB_ID(*fp.split(':')));f.SetReference(ref);f.SetValue('M1.6');f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_BOM);f.SetPosition(vec(*xy));f.SetPath(p.KIID_PATH('/'+uid(name+'root')+'/'+uid(name+ref)));f.Reference().SetVisible(False);f.Value().SetVisible(False);board.Add(f)
  parts.append(dict(ref=ref,mpn='M1.6',footprint=fp,xy=xy,pins={},size=[3.6,3.6,0],section='mounts',cost_eur=[0,0],angle=0,source=''))
 outline=[(-2,1),(w,1),(w,h),(10.5,h),(10.5,3.25),(1.5,3.25),(1.5,11),(-2,11)] if name=='card-reader' else [(0,0),(w,0),(w,h),(0,h)]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  q=p.PCB_SHAPE();q.SetShape(p.SHAPE_T_SEGMENT);q.SetStart(vec(*a));q.SetEnd(vec(*b));q.SetLayer(p.Edge_Cuts);q.SetWidth(p.FromMM(.05));board.Add(q)
 for net,layer,points in paths:
  for a,b in zip(points,points[1:]):
   if a==b:continue
   t=p.PCB_TRACK(board);t.SetStart(vec(*a));t.SetEnd(vec(*b));t.SetWidth(p.FromMM(.2));t.SetLayer(p.F_Cu if layer=='F' else p.B_Cu);t.SetNet(nets[net]);board.Add(t)
 for net,x,y in vias:
  t=p.PCB_VIA(board);t.SetPosition(vec(x,y));t.SetWidth(p.F_Cu,p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(nets[net]);board.Add(t)
 if name=='card-reader':
  z=p.ZONE(board);z.SetLayer(p.B_Cu);z.SetNet(nets['GND']);z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.Outline().NewOutline()
  for a,b in [(-1.6,1.4),(w-.4,1.4),(w-.4,h-.4),(10.9,h-.4),(10.9,2.85),(1.1,2.85),(1.1,10.6),(-1.6,10.6)]:q=vec(a,b);z.Outline().Append(q.x,q.y)
  board.Add(z)
 ds=board.GetDesignSettings();ds.m_MinClearance=p.FromMM(.15);ds.m_TrackMinWidth=p.FromMM(.15);ds.m_HoleClearance=p.FromMM(.15);ds.m_CopperEdgeClearance=p.FromMM(.25)
 p.SaveBoard(str(dest/(name+'.kicad_pcb')),board)
 if name=='card-reader':
  board=p.LoadBoard(str(dest/(name+'.kicad_pcb')));board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(dest/(name+'.kicad_pcb')),board)
 data=dict(variant=name,status='engineering_reference_for_rfq',pcb=dict(outline=[min(x for x,y in outline),min(y for x,y in outline),max(x for x,y in outline)-min(x for x,y in outline),max(y for x,y in outline)-min(y for x,y in outline)],thickness=1.6 if name=='card-reader' else .8,holes=holes,edge_polygon=outline),parts=parts,physical_validation='pending',fabrication_release=False)
 (dest/'components.json').write_text(json.dumps(data,indent=2)+'\n');make_schematic(data,dest,name)
 pro={'meta':{'filename':name+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_copper_edge_clearance':.25,'min_through_hole_diameter':.3,'min_via_diameter':.5,'min_hole_clearance':.15}}}}
 (dest/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n');(dest/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Compact") (type "KiCad") (uri "${KIPRJMOD}/Compact.pretty") (options "") (descr "Current contact interface footprints")))\n')
 print(name,'native board/schematic generated')

def part(ref,mpn,fp,xy,pins,size,cost,source):return dict(ref=ref,mpn=mpn,footprint=fp,xy=xy,pins={str(k):v for k,v in pins.items()},size=size,cost_eur=cost,section='card',angle=0,source=source)
reader=[part('J1','OC-WIRE-3','Compact:Wire3_Top',[35,9],{1:'3V2',2:'GND',3:'IO8'},[6.4,2,.8],[0,0],'hardware/card-reader/Compact.pretty/Wire3_Top.kicad_mod'),part('P1','P70-1000045R','Compact:Pogo_P70_1000045',[21,6],{1:'GND'},[2,2,3.5],[.8,1.8],'https://www.harwin.com/products/P70-1000045R'),part('P2','P70-1000045R','Compact:Pogo_P70_1000045',[27,6],{1:'CARD_DQ'},[2,2,3.5],[.8,1.8],'https://www.harwin.com/products/P70-1000045R'),part('R1','RC0603FR-074K3L','Resistor_SMD:R_0603_1608Metric',[14,3],{1:'3V2',2:'IO8'},[1.6,.8,.55],[.01,.06],'https://www.yageo.com/en/Product/Index/product_type/chip-resistors'),part('R2','RC0603FR-07330RL','Resistor_SMD:R_0603_1608Metric',[21,3],{1:'IO8',2:'CARD_DQ'},[1.6,.8,.55],[.01,.06],'https://www.yageo.com/en/Product/Index/product_type/chip-resistors'),part('D1','TPD1E10B06DPYR','Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm',[30,6],{1:'CARD_DQ',2:'GND'},[.6,1,.5],[.15,.5],'https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf'),part('D2','BAT54S,215','Package_TO_SOT_SMD:SOT-23',[14,7],{1:'GND',2:'3V2',3:'IO8'},[2.9,2.4,1.1],[.05,.2],'https://assets.nexperia.com/documents/data-sheet/BAT54_SER.pdf')]
paths=[
 ('3V2','F',[(32.5,9),(32.5,10)]),
 ('3V2','B',[(32.5,10),(32.5,11),(17,11),(17,3),(12,2),(16.5,5.5)]),
 ('3V2','F',[(12,2),(13.175,3)]),
 ('3V2','F',[(16.5,5.5),(16.5,9.5),(13.0625,9.5),(13.0625,7.95)]),
 ('IO8','F',[(37.5,9),(37.5,10)]),
 ('IO8','B',[(37.5,10),(36.3,8.8),(18,8.8),(18,9)]),
 ('IO8','F',[(18,9),(18,5),(14.825,3),(20.175,3)]),
 ('IO8','F',[(14.9375,7),(15.5,6.4),(15.5,4),(14.825,3)]),
 ('CARD_DQ','F',[(21.825,3),(26,3),(27,4),(27,6),(29.65,6)]),
 ('GND','F',[(21,6),(21,7.8)]),
 ('GND','F',[(30.35,6),(30.35,7.5)]),
 ('GND','F',[(13.0625,6.05),(12,6.05)]),
 ('GND','F',[(35,9),(35,10)])]
build('card-reader',48,12,reader,[[0,9],[46,10]],paths,[('3V2',32.5,10),('3V2',12,2),('3V2',16.5,5.5),('IO8',37.5,10),('IO8',18,9),('GND',35,10),('GND',21,7.8),('GND',30.35,7.5),('GND',12,6.05)])
card=[part('U1','DS2401P+','Package_SO_J-Lead:TSOC-6_3.76x3.94mm_P1.27mm',[10,6],{1:'GND',2:'CARD_DQ',3:None,4:None,5:None,6:None},[3.76,3.94,1.5],[3.65,5],'https://www.analog.com/media/en/technical-documentation/data-sheets/ds2401.pdf'),part('J1','OC-ID-CONTACTS','Compact:ContactPads_Bottom',[0,0],{1:'GND',2:'CARD_DQ'},[0,0,0],[0,0],'hardware/story-card/Compact.pretty/ContactPads_Bottom.kicad_mod')]
paths=[('GND','F',[(8.475,4.73),(4.5,4.73)]),('GND','B',[(4.5,4.73),(7,4.73)]),('CARD_DQ','F',[(8.475,6),(6.5,6),(4.5,7)]),('CARD_DQ','B',[(4.5,7),(4.5,11.5),(15.5,11.5),(15.5,8),(13,8)])]
build('story-card',20,12,card,[[2,2],[18,10]],paths,[('GND',4.5,4.73),('CARD_DQ',4.5,7)])
