#!/usr/bin/env python3
import json
from pathlib import Path
from compact_design import ROOT,OUT
E=ROOT/'enclosure/compact-r1';E.mkdir(exist_ok=True)
def array(x):return json.dumps(x,separators=(',',':'))
for v in ['mini','explore']:
 d=json.loads((OUT/(v+'-mechanical.json')).read_text());lines=['// Generated from native PCB placements. Nominal engineering prototype.','dims='+array(d['case'])+';','holes='+array(d['pcb']['holes'])+';']
 buttons=[r for r in d['parts'] if r['section']=='controls' and r['ref'].startswith('SW')]
 lines+=['buttons='+array([r['xy'] for r in buttons])+';','button_names='+array([r['pins']['1'].replace('KEY_','') for r in buttons])+';','bodies='+array([r['body_box'] for r in d['parts'] if not r['ref'].startswith(('H','TP'))])+';','body_refs='+array([r['ref'] for r in d['parts'] if not r['ref'].startswith(('H','TP'))])+';','extras='+array([r['box'] for r in d['extras']])+';','extra_names='+array([r['id'] for r in d['extras']])+';','reserves='+array([r['box'] for r in d['clearance_reserves']])+';']
 (E/(v+'-data.scad')).write_text('\n'.join(lines)+'\n')
