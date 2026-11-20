"""Native schematic writer for the current component contracts; no PCB routing reset."""
from pathlib import Path
import uuid,math,re
from kicad_sexp import symbol,pins as symbolpins
from pin_contracts import CONTRACTS
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'open-conteuse/compact-r1/'+key))
def prop(n,v,x,y,hide=False):
 v=str(v).replace('"','\\"')
 return f'(property "{n}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
def make_schematic(d,dest,v):
 font='(effects (font (size 1.27 1.27)))';libs=[];symbols=[]
 contracts={k:dict(v) for k,v in CONTRACTS.items()} if v in ['mini','explore'] else {}
 for ref,ln,sn in ([('U1','RF_Module','ESP32-S3-WROOM-1'),('U2','Battery_Management','BQ24074RGT'),('U8','Audio','MAX98357A')] if v in ['mini','explore'] else []):contracts[ref]=symbolpins(symbol(Path('/usr/share/kicad/symbols')/(ln+'.kicad_sym'),sn))
 if v=='story-card':contracts['U1']={'1':('GND','power_in'),'2':('DQ','bidirectional'),**{str(i):('NC','no_connect') for i in range(3,7)}}
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
 for i,net in enumerate(['GND','VBUS'] if v in ['mini','explore'] else ['GND']):
  ref='#FLG'+str(i+1);x=76.2+i*50.8;y=1778
  libs.append(f'(symbol "Compact:FLAG{i}" (power) (in_bom no) (on_board no) '+prop('Reference',ref,0,0,True)+prop('Value','PWR_FLAG',0,0,True)+f'(symbol "FLAG{i}_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" {font}) (number "1" {font}))))')
  symbols.append(f'(symbol (lib_id "Compact:FLAG{i}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(v+ref)}")'+prop('Reference',ref,x,y,True)+prop('Value','PWR_FLAG',x,y,True)+f'(pin "1" (uuid "{uid(v+ref+"pin")}")) (instances (project "{v}" (path "/{uid(v+"root")}" (reference "{ref}") (unit 1)))))')
  symbols.append(f'(label "{net}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(v+ref+"label")}"))')
 source=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid(v+"root")}") (paper "User" 1400 1900) (title_block (title "Galia {v.title()} - engineering reference") (rev "RFQ-2026-11-20") (date "2026-11-20"))\n(lib_symbols '+''.join(libs)+')\n'+'\n'.join(symbols)+'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'
 def snap(m):return m.group(1)+str(round(round(float(m.group(2))/1.27)*1.27,4))+' '+str(round(round(float(m.group(3))/1.27)*1.27,4))
 source=re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,source)
 (dest/(v+'.kicad_sch')).write_text(source)
 (dest/'Compact.kicad_sym').write_text(re.sub(r'(\((?:at|xy) )(-?[0-9.]+) (-?[0-9.]+)',snap,'(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(libs).replace('"Compact:','"')+')'))
 (dest/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Compact") (type "KiCad") (uri "${KIPRJMOD}/Compact.kicad_sym") (options "") (descr "Original symbol pin contracts")))\n')
