"""Import exact SES copper into a native KiCad file without unsafe SWIG removals.
The output is reloaded, filled and independently checked by KiCad ERC/DRC.
"""
import re,uuid,json
from kicad_sexp import parse,child,children

def import_routes(path,session,placement):
 source=path.read_text();s=parse(session.read_text());routes=child(s,'routes');assert child(routes,'resolution')[1:]==['um','10'];scale=10000
 expected={r['ref']:r for r in placement['parts']}
 for component in children(child(s,'placement'),'component'):
  for p in children(component,'place'):
   r=expected[p[1]];assert abs(float(p[2])/scale-r['xy'][0]-30)<.0001 and abs(-float(p[3])/scale-r['xy'][1]-30)<.0001,(p[1],'moved')
   assert p[4]=='front' and abs((float(p[5])-r['angle']+180)%360-180)<.01,(p[1],'rotated')
 codes={n:int(i) for i,n in re.findall(r'^\t\(net (\d+) "([^"]*)"\)',source,re.M)}
 source,n=re.subn(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)','',source)
 # SES omits unchanged protected wiring. Retain the input DSN wiring.
 baseline_path=session.with_suffix('.dsn')
 assert baseline_path.exists(),f'Matching input DSN is required: {baseline_path}'
 baseline=parse(baseline_path.read_text())
 if baseline is not None:
  network=child(routes,'network_out'); byname={n[1]:n for n in children(network,'net')}
  for item in child(baseline,'wiring')[1:]:
   if not isinstance(item,list) or item[0] not in ('wire','via'):continue
   if child(item,'type')[1] not in ('protect','fix'):continue
   name=child(item,'net')[1]
   if name not in byname:byname[name]=['net',name];network.append(byname[name])
   if item[0]=='wire':
    a=child(item,'path');converted=['wire',['path',a[1]]+[str(float(x)*10) for x in a[2:]]]
   else:converted=['via',item[1],str(float(item[2])*10),str(float(item[3])*10)]
   converted.append(['type','protect']);byname[name].insert(2,converted)
 records=[];seen=set();layers={'F.Cu','In2.Cu','B.Cu'}
 def uid(k):return str(uuid.uuid5(uuid.NAMESPACE_URL,'open-conteuse/compact-copper/'+path.stem+'/'+k))
 def num(x):return f'{float(x)/scale:.4f}'
 for net in children(child(routes,'network_out'),'net'):
  name=net[1];assert name in codes,name
  for wire in children(net,'wire'):
   a=child(wire,'path');assert a[1] in layers,a[1];width=float(a[2])/scale;assert .149<=width<=1,width
   pts=[(float(a[i])/scale,-float(a[i+1])/scale) for i in range(3,len(a),2)]
   for start,end in zip(pts,pts[1:]):
    if start==end:continue
    key=(name,a[1],round(width,4),tuple(sorted((tuple(round(x,4) for x in start),tuple(round(x,4) for x in end)))))
    if key in seen:continue
    seen.add(key)
    lock='(locked yes)' if name in ['/SW_L1','/SW_L2','/VINA'] or child(wire,'type')==['type','protect'] else ''
    records.append(f'(segment (start {start[0]:.4f} {start[1]:.4f}) (end {end[0]:.4f} {end[1]:.4f}) (width {width:.4f}) (layer "{a[1]}") (net {codes[name]}) {lock} (uuid "{uid(str(len(records)))}"))')
  for via in children(net,'via'):
   m=re.search(r'_(\d+):(\d+)_um',via[1]);assert m,via
   key=(name,'via',round(float(via[2])/scale,4),round(float(via[3])/scale,4),m[0])
   if key in seen:continue
   seen.add(key)
   lock='(locked yes)' if child(via,'type')==['type','protect'] else ''
   records.append(f'(via (at {float(via[2])/scale:.4f} {-float(via[3])/scale:.4f}) (size {int(m[1])/1000}) (drill {int(m[2])/1000}) (layers "F.Cu" "B.Cu") (net {codes[name]}) {lock} (uuid "{uid(str(len(records)))}"))')
 source=source.rstrip();assert source.endswith(')');path.write_text(source[:-1]+'\n'+'\n'.join(records)+'\n)\n');return len(records)
