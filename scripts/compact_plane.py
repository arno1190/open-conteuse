"""Continuous In1 GND reference zone, with native keepout/edge clearance filling."""
import pcbnew as p

def ground(board):
 z=next((z for z in board.Zones() if not z.GetIsRuleArea() and z.GetLayer()==p.In1_Cu),None)
 if z is None:
  z=p.ZONE(board);z.SetLayer(p.In1_Cu);z.SetNet(board.FindNet('/GND'));z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15));board.Add(z)
  z.Outline().NewOutline()
  for x,y in [(3.5,9),(61.5,9),(62.5,10),(62.5,91),(61.5,92),(3.5,92),(2.5,91),(2.5,10)]:z.Outline().Append(p.FromMM(x+30),p.FromMM(y+30))
 for zone in board.Zones():
  if not zone.GetIsRuleArea():zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());return z

def power(board):
 """Broad logic/system pours support power distribution around signal routing.
 In1 remains the reference plane. Exact copper connectivity is filled/DRC checked.
 """
 specs=[(p.In2_Cu,'/3V2',0,[(33.5,39),(91.5,39),(92.5,40),(92.5,121),(91.5,122),(33.5,122),(32.5,121),(32.5,40)]),(p.B_Cu,'/SYS',0,[(33.5,39),(91.5,39),(92.5,40),(92.5,121),(91.5,122),(33.5,122),(32.5,121),(32.5,40)]),(p.F_Cu,'/GND',0,[(33.5,39),(91.5,39),(92.5,40),(92.5,121),(91.5,122),(33.5,122),(32.5,121),(32.5,40)]),(p.B_Cu,'/VBUS',1,[(72,65.5),(78.5,65.5),(78.5,68.2),(76.2,68.2),(76.2,114.4),(86,114.4),(86,122),(72,122)]),(p.In2_Cu,'/BAT',1,[(36,50.5),(74.2,50.5),(74.2,73),(72,73),(72,54),(36,54)])]
 if any(f.GetReference()=='J8' for f in board.GetFootprints()):specs.append((p.B_Cu,'/BAT',2,[(73.2,67.3),(84.5,67.3),(84.5,71.9),(83.6,71.9),(83.6,69.9),(74.2,69.9),(74.2,72.4),(73.2,72.4)]))
 for layer,name,priority,points in specs:
  z=next((z for z in board.Zones() if not z.GetIsRuleArea() and z.GetLayer()==layer and z.GetNetname()==name),None)
  if z is None:
   z=p.ZONE(board);z.SetLayer(layer);z.SetNet(board.FindNet(name));z.SetAssignedPriority(priority);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.25));board.Add(z);z.Outline().NewOutline()
   for x,y in points:z.Outline().Append(p.FromMM(x),p.FromMM(y))
 for zone in board.Zones():
  if not zone.GetIsRuleArea():zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones())

def stitches(board,variant):
 """Explicit pad-to-reference stitches omitted by the external router."""
 fps={f.GetReference():f for f in board.GetFootprints()}
 def pad(ref,n):return next(q for q in fps[ref].Pads() if q.GetNumber()==str(n)).GetPosition()
 requests=[(pad('J2',6),(-1.35,0)),(pad('TP1',1),(0,0))]
 if variant=='explore':requests.extend([(pad('R3',2),(0,0)),(pad('U6',4),(-1,0)),(pad('U11',2),(0,0))])
 else:requests.extend([(pad('U10',2),(0,0)),(pad('J7',2),(0,0))])
 for start,(dx,dy) in requests:
  end=p.VECTOR2I(start.x+p.FromMM(dx),start.y+p.FromMM(dy))
  if any(type(t)==p.PCB_VIA and t.GetPosition()==end and t.GetNetname()=='/GND' for t in board.GetTracks()):continue
  if start!=end:
   t=p.PCB_TRACK(board);t.SetStart(start);t.SetEnd(end);t.SetWidth(p.FromMM(.2));t.SetLayer(p.F_Cu);t.SetNet(board.FindNet('/GND'));t.SetLocked(True);board.Add(t)
  t=p.PCB_VIA(board);t.SetPosition(end);t.SetWidth(p.F_Cu,p.FromMM(.5));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(board.FindNet('/GND'));t.SetLocked(True);board.Add(t)

def supply_vias(board):
 """Local source/load stitches, placed before routing; via-in-pad quote required."""
 def via(net,x,y):
  t=p.PCB_VIA(board);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetWidth(p.F_Cu,p.FromMM(.5));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(board.FindNet(net));t.SetLocked(True);board.Add(t)
 def track(net,a,b,width=.2):
  t=p.PCB_TRACK(board);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(b[0]),p.FromMM(b[1])));t.SetWidth(p.FromMM(width));t.SetLayer(p.F_Cu);t.SetNet(board.FindNet(net));t.SetLocked(True);board.Add(t)
 for f in board.GetFootprints():
  for pad in f.Pads():
   local=(f.GetReference().startswith('C') and pad.GetNetname() in ['/3V2','/SYS','/GND','/VBUS','/BAT']) or (f.GetReference()=='U1' and pad.GetNumber()=='2') or (f.GetReference()=='J5' and pad.GetNumber()=='1')
   local=local or (pad.GetNetname()=='/GND' and pad.GetAttribute()==p.PAD_ATTRIB_SMD and min(p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y))>=.7 and f.GetReference() not in ['U2','U3','U5','U8'])
   if local:via(pad.GetNetname(),p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y))
 for net,points in [('/BAT',[(74.5625,71.75),(73.7,71.75),(73.7,72)]),('/BAT',[(74.5625,72.25),(73.7,72.25),(73.7,72)]),('/SYS',[(77.4375,71.75),(78.4,71.75),(78.4,72)]),('/SYS',[(77.4375,72.25),(78.4,72.25),(78.4,72)]),('/VBUS',[(75.75,73.4375),(75.75,74.4)]),('/HPL',[(55.75,70.5625),(55.75,69.2)]),('/VBUS',[(78.6,116.02),(78.6,114.9)]),('/SYS',[(83.45,74),(84.1,74),(84.5,73.6)]),('/PWR_EN',[(83.45,74.5),(84.5,74.475)])]:
  for a,b in zip(points,points[1:]):track(net,a,b,.15 if net=='/PWR_EN' else .2)
 for net,x,y in [('/BAT',73.7,72),('/SYS',78.4,72),('/VBUS',75.75,74.4),('/VBUS',78.6,114.9),('/SYS',84.5,73.6),('/PWR_EN',84.5,74.475),('/HPL',55.75,69.2)]:via(net,x,y)

 # Explicit fanout of the compact connector and the previously congested GPIO.
 # These stubs/vias are placed before routing and checked against native pads.
 fs={f.GetReference():f for f in board.GetFootprints()}
 track('/IO5',(53.75,45.57),(52.45,45.57),.15);via('/IO5',52.45,45.57)
 if 'J8' in fs:
  for pad in fs['J8'].Pads():
   number=pad.GetNumber();net=pad.GetNetname()
   if not number.isdigit() or not net.startswith('/'):continue
   y=p.ToMM(pad.GetPosition().y);x=p.ToMM(pad.GetPosition().x)-(1.45 if int(number)%2 else .9)
   track(net,(p.ToMM(pad.GetPosition().x),y),(x,y),.15);via(net,x,y)

def antenna(board):
 """Restore the all-layer antenna-overhang rule area after a routing reset."""
 if any(z.GetIsRuleArea() for z in board.Zones()):return
 z=p.ZONE(board);z.SetIsRuleArea(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);layers=p.LSET()
 for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:layers.AddLayer(layer)
 z.SetLayerSet(layers);z.Outline().NewOutline()
 for x,y in [(38.5,18),(86.5,18),(86.5,39),(38.5,39)]:z.Outline().Append(p.FromMM(x),p.FromMM(y))
 board.Add(z)

