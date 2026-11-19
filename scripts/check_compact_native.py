#!/usr/bin/python3
"""Independent native-board versus mechanical-data consistency and power routing checks."""
import json,math
from compact_design import ROOT,OUT
import pcbnew as p
from compact_power_check import check as check_power
reports={}
for v in ['mini','explore']:
 d=json.loads((OUT/(v+'-mechanical.json')).read_text());b=p.LoadBoard(str(OUT/v/(v+'.kicad_pcb')));fps={f.GetReference():f for f in b.GetFootprints()}
 bb=b.GetBoardEdgesBoundingBox();assert abs(p.ToMM(bb.GetWidth())-d['pcb']['outline'][2])<.06 and abs(p.ToMM(bb.GetHeight())-d['pcb']['outline'][3])<.06
 assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-d['pcb']['thickness'])<1e-6
 actual_holes=sorted((round(p.ToMM(f.GetPosition().x)-30,4),round(p.ToMM(f.GetPosition().y)-30,4)) for f in b.GetFootprints() if f.GetReference().startswith('H'))
 assert actual_holes==sorted(map(tuple,d['pcb']['holes']))
 for r in d['parts']:
  f=fps[r['ref']];xy=[p.ToMM(f.GetPosition().x)-30,p.ToMM(f.GetPosition().y)-30]
  assert math.dist(xy,r['xy'])<1e-5,(v,r['ref'],'placement stale')
  if not r['ref'].startswith('H'):assert f.GetValue()==r['mpn'],(v,r['ref'],'MPN stale')
  for pad in f.Pads():
   pin=pad.GetNumber()
   if pin not in r['pins']:continue
   expected=r['pins'][pin]
   if expected:assert pad.GetNetname()=='/'+expected,(v,r['ref'],pin,pad.GetNetname(),expected)
 assert not [t for t in b.GetTracks() if type(t)==p.PCB_TRACK and t.GetLayer()==p.In1_Cu],'signals on GND plane'
 for net in ['/SW_L1','/SW_L2']:
  tracks=[t for t in b.GetTracks() if t.GetNetname()==net];assert tracks and all(type(t)==p.PCB_TRACK and t.GetLayer()==p.F_Cu for t in tracks)
  length=sum(p.ToMM(t.GetLength()) for t in tracks);assert length<18,(v,net,'switch-node routing too long',length)
 c8=fps['C8'];u3=fps['U3'];a=next(q.GetPosition() for q in c8.Pads() if q.GetNumber()=='1');bb=next(q.GetPosition() for q in u3.Pads() if q.GetNumber()=='1');assert p.ToMM((a-bb).EuclideanNorm())<2.1
 reports[v]=check_power(b,v)
 rules=[z for z in b.Zones() if z.GetIsRuleArea()];assert len(rules)==1
 assert all(rules[0].GetLayerSet().Contains(layer) for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu])
 for ref,limit in [('C30',2.1),('C29',4.5)]:
  a=next(q.GetPosition() for q in fps[ref].Pads() if q.GetNumber()=='1');bb=next(q.GetPosition() for q in fps['U1'].Pads() if q.GetNumber()=='2');assert p.ToMM((a-bb).EuclideanNorm())<limit
 print(v,'native placement/pin parity and local regulator routing checks passed')

if __name__=='__main__':
 import sys
 if "--write-power-report" in sys.argv:(OUT/"power-distribution.json").write_text(json.dumps({"physical_validation":"pending","minimum_geometric_core_width_mm":.8,"endpoint_probe_radius_mm":1.5,"limitations":"Geometry-only corridor existence; no AC/current/thermal or tolerance proof", "variants":reports},indent=2)+"\n")
