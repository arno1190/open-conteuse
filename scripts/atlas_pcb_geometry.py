#!/usr/bin/python3
"""Read exact custom-PCB footprint/pad placements for illustrative component bodies."""
import json,pcbnew as p
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];data={}
for ident,file in [('controls','hardware/controls/controls.kicad_pcb'),('mute_latch','hardware/integration/mute-latch/mute-latch.kicad_pcb')]:
 b=p.LoadBoard(str(ROOT/file));rows=[]
 for fp in b.GetFootprints():
  rows.append({'ref':fp.GetReference(),'value':fp.GetValue(),'xy':[p.ToMM(fp.GetPosition().x)-30,p.ToMM(fp.GetPosition().y)-30],'angle':fp.GetOrientationDegrees(),'pads':[[p.ToMM(q.GetPosition().x)-30,p.ToMM(q.GetPosition().y)-30,q.GetNumber()] for q in fp.Pads()]})
 data[ident]=rows
(ROOT/'work/atlas/pcb.json').write_text(json.dumps(data,indent=2)+'\n')
