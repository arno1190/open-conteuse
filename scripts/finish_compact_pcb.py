#!/usr/bin/python3
"""Import a frozen matching DSN/SES pair and refill the native reference plane.
Requires independent all-severity native DRC afterwards; never places orders.
"""
import argparse,json,gc
import pcbnew as p
from compact_design import ROOT,OUT
from compact_plane import ground,power,stitches,antenna
from import_compact_routes import import_routes
gc.disable()
a=argparse.ArgumentParser();a.add_argument('variants',nargs='*',choices=['mini','explore']);a.add_argument('--work-stage',required=True,help='matching development DSN/SES suffix under work/compact-r1, e.g. clean');args=a.parse_args()
for v in args.variants or ['mini','explore']:
 path=OUT/v/(v+'.kicad_pcb');session=ROOT/f'work/compact-r1/{v}-{args.work_stage}.ses';data=json.loads((OUT/v/'components.json').read_text())
 print(v,'imported copper items',import_routes(path,session,data),flush=True);b=p.LoadBoard(str(path));assert not any(type(t)==p.PCB_TRACK and t.GetLayer()==p.In1_Cu for t in b.GetTracks());antenna(b);stitches(b,v);ground(b);power(b);p.SaveBoard(str(path),b)
