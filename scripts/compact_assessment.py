#!/usr/bin/env python3
"""Dimension and cost-target arithmetic; does not assert manufacturability."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():return json.loads((ROOT/'hardware/compact/assessment.json').read_text())
def budget(data,variant,quantity):
 p=data['planning_costs'];rows=p['common_items']+p['variant_items'][variant];assembly=p['pcb_assembly_per_unit'][str(quantity)]
 return [sum(r['range'][i] for r in rows)+assembly[i] for i in range(2)]
def summary(data):
 base=data['envelopes'][0]['size'];volume=lambda d:d[0]*d[1]*d[2]/1000
 return {'envelopes':[{**r,'volume_cm3':round(volume(r['size']),2),'volume_reduction_percent':round(100*(1-volume(r['size'])/volume(base)),2)} for r in data['envelopes']], 'recurring_targets_eur':{str(q):{v:budget(data,v,q) for v in ['mini','explore']} for q in [5,25]},'quote_status':data['planning_costs']['quote_status'],'physical_validation':'pending'}
def generate(data):
 result=summary(data);(ROOT/'hardware/compact/summary.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['// Generated design envelopes only. NOT a fitted enclosure or printable release.','// [width,height,depth], mm. Reference dimensions are approximate, not measured.','$fn=48;','module envelope(d) {minkowski(){cube([d[0]-6,d[1]-6,d[2]-6]);sphere(r=3);}}']
 x=0
 for r in data['envelopes']:
  lines.append(f'// {r["label"]}: {r["basis"]}')
  lines.append(f'translate([{x+3},3,3]) envelope({json.dumps(r["size"])});');x+=r['size'][0]+18
 (ROOT/'enclosure/compact-study/targets.scad').write_text('\n'.join(lines)+'\n')
 return result
if __name__=='__main__':print(json.dumps(generate(load()),indent=2))
