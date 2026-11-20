#!/usr/bin/python3
"""Read exact final copper/pads from native KiCad for coloured technical views."""
import json,pcbnew as p
from project import ROOT,HARDWARE
OUT=HARDWARE
for v in ['mini','explore']:
 b=p.LoadBoard(str(OUT/v/(v+'.kicad_pcb')));d={k:[] for k in ['pads','tracks','rear_tracks','vias']}
 def xy(q):return [p.ToMM(q.x)-30,p.ToMM(q.y)-30]
 for f in b.GetFootprints():
  for q in f.Pads():
   if q.GetLayerSet().Contains(p.F_Cu) and q.GetAttribute()!=p.PAD_ATTRIB_NPTH:d['pads'].append(dict(xy=xy(q.GetPosition()),size=[p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)],angle=q.GetOrientationDegrees(),pin=q.GetNumber(),ref=f.GetReference()))
 for t in b.GetTracks():
  if type(t)==p.PCB_VIA:d['vias'].append(dict(xy=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(p.F_Cu)),drill=p.ToMM(t.GetDrillValue())))
  elif t.GetLayer()==p.B_Cu:d['rear_tracks'].append(dict(a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth())))
  elif t.GetLayer()==p.F_Cu:d['tracks'].append(dict(a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth())))
 (OUT/v/'copper.json').write_text(json.dumps(d,separators=(',',':'))+'\n')
