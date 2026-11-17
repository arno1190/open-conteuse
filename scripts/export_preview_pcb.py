#!/usr/bin/python3
"""Export actual KiCad copper and pad coordinates for the PNG renderer.

Requires KiCad 9 pcbnew; run using Debian /usr/bin/python3 from repo root.
"""
import pcbnew as p,json
b=p.LoadBoard('hardware/controls/controls.kicad_pcb')
def xy(v):return [p.ToMM(v.x)-30,p.ToMM(v.y)-30]
data={'tracks':[],'pads':[]}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 data['tracks'].append({'a':xy(t.GetStart()),'b':xy(t.GetEnd()),'layer':t.GetLayerName(),'net':t.GetNetname()})
for f in b.GetFootprints():
 for pad in f.Pads():data['pads'].append({'xy':xy(pad.GetPosition()),'drill':p.ToMM(pad.GetDrillSize().x),'ref':f.GetReference(),'pin':pad.GetNumber()})
json.dump(data,open('work/previews/pcb.json','w'))
