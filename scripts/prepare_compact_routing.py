#!/usr/bin/python3
"""Explicit routing reset: keep placement, rebuild critical copper/thermal vias.
This intentionally discards signal routing. Follow with Freerouting and native DRC.
"""
import sys,re,json,gc
gc.disable()
import pcbnew as p
from generate_compact_pcb import local_power
from compact_plane import ground,supply_vias,stitches,antenna
from compact_router import SETTINGS
for v in ['mini','explore']:
 path=f'hardware/compact-r1/{v}/{v}.kicad_pcb';s=open(path).read();s=re.sub(r'\n\t\(zone\b[\s\S]*?\n\t\)',lambda m:m[0] if '(keepout' in m[0] else '',s);s=re.sub(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)','',s);open(path,'w').write(s);b=p.LoadBoard(path);fps=list(b.GetFootprints());nets={str(name)[1:]:net for name,net in b.GetNetsByName().items()};local_power(b,fps,nets)
 fs={f.GetReference():f for f in fps}
 for ref,offs in [('U2',[(x,y) for x in [-.35,.35] for y in [-.35,.35]]),('U3',[(x,y) for x in [-.4,.4] for y in [-.8,.8]]),('U5',[(x,y) for x in [-1.1,0,1.1] for y in [-1.1,1.1]]),('U8',[(0,0)])]:
  c=fs[ref].GetPosition()
  for x,y in offs:
   t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(c.x+p.FromMM(x),c.y+p.FromMM(y)));t.SetWidth(p.F_Cu,p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(nets['GND']);t.SetLocked(True);b.Add(t)
 data=json.load(open(f'hardware/compact-r1/{v}/components.json'))
 next(r for r in data['parts'] if r['ref']=='C8')['xy']=[49.45,42.75]
 open(f'hardware/compact-r1/{v}/components.json','w').write(json.dumps(data,indent=2)+'\n')
 antenna(b);supply_vias(b);stitches(b,v);ground(b);p.SaveBoard(path,b);dsn=f'work/compact-r1/{v}-rails.dsn';p.ExportSpecctraDSN(b,dsn);s=open(dsn).read().replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)');# Reserve selected supply corridors on just their copper layer; local
 # fixed power vias already exist, other signals must change layer around them.
 corridors=[('SYS_spine','B.Cu',[(56.5,60.5),(89,60.5),(89,78),(77,78),(77,68.5),(79,68.5),(79,64.5),(60.5,64.5),(60.5,91.5),(69,91.5),(69,95),(56.5,95)]),('SYS_boost','B.Cu',[(38.5,71.5),(42.5,71.5),(42.5,76.5),(56.5,76.5),(56.5,80.5),(38.5,80.5)]),('logic_spine','In2.Cu',[(49,40),(80.5,40),(80.5,78),(76.5,78),(76.5,48),(49,48)]),('BAT_spine','In2.Cu',[(36,50.5),(74.2,50.5),(74.2,73),(72,73),(72,54),(36,54)]),('VBUS_spine','B.Cu',[(72,65.5),(78.5,65.5),(78.5,68.2),(76.2,68.2),(76.2,114.4),(86,114.4),(86,122),(72,122)])]
 s=re.sub(r'(\(boundary\s*\(path pcb 0)[^)]*(\)\s*\))',r'\1 33550 -39100 91450 -39100 92400 -40050 92400 -120950 91450 -121900 33550 -121900 32600 -120950 32600 -40050 33550 -39100\2',s,count=1)
 if v=='explore':corridors.append(('BAT_cap','B.Cu',[(73.2,67.3),(84.5,67.3),(84.5,71.9),(83.6,71.9),(83.6,69.9),(74.2,69.9),(74.2,72.4),(73.2,72.4)]))
 shapes=''.join('(keepout "'+name+'" (polygon '+layer+' 0 '+ ' '.join(str(round(c*1000)) for pt in pts+[pts[0]] for c in (pt[0],-pt[1]))+'))\n' for name,layer,pts in corridors)
 s=s.replace('    (via \"',shapes+'    (via \"',1)
 s=s.replace('    (boundary','    '+SETTINGS.replace('(postroute on)','(postroute off)')+'\n    (boundary',1).replace('(width 600)','(width 150)').replace('(width 200)','(width 150)');pat=re.search(r'    \(padstack "Via\[0-3\]_600:300_um"[\s\S]*?\(attach off\)\s*\)',s)[0];s=s.replace(pat,pat+'\n'+pat.replace('600:300','500:300').replace('Cu 600','Cu 500'));s=s.replace('(via "Via[0-3]_600:300_um" "Via[0-3]_800:400_um")','(via "Via[0-3]_500:300_um" "Via[0-3]_600:300_um" "Via[0-3]_800:400_um")').replace('(use_via "Via[0-3]_800:400_um")','(use_via "Via[0-3]_500:300_um")');open(dsn,'w').write(s)

 # Keep foreign supply/ground routing out of the logic-power layer. Existing
 # local through-vias meet the native reference/power pours after filling.
 s=dsn and open(dsn).read()
 s=s.replace('(class Power /3V2 /BAT /GND','(class Power')
 s=re.sub(r'(\(class Power[\s\S]*?\(circuit)',r'\1 (use_layer F.Cu B.Cu)',s,count=1)
 classes=''
 for name,net,layers in [('Logic','/3V2','F.Cu In2.Cu'),('Battery','/BAT','F.Cu In2.Cu'),('Reference','/GND','F.Cu In1.Cu')]:
  classes+='(class '+name+' '+net+' (circuit (use_layer '+layers+') (use_via "Via[0-3]_500:300_um")) (rule (width150) (clearance150)))\n'
 classes=classes.replace('width150','width 150').replace('clearance150','clearance 150')
 s=s.replace('(class Power',classes+'(class Power',1);open(dsn,'w').write(s)
