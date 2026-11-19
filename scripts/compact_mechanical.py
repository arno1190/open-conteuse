#!/usr/bin/python3
"""Generate shared mechanical data from final native PCB placements."""
import json,sys
from pathlib import Path
import pcbnew as p
from compact_design import ROOT,OUT
for v in ['mini','explore']:
 d=json.loads((OUT/v/'components.json').read_text());b=p.LoadBoard(str(OUT/v/(v+'.kicad_pcb')));index={f.GetReference():f for f in b.GetFootprints()}
 for row in d['parts']:
  f=index[row['ref']];items=[x for x in f.GraphicalItems() if x.GetLayer()==p.F_Fab and isinstance(x,p.PCB_SHAPE)]
  if items:
   boxes=[x.GetBoundingBox() for x in items];lo=[min(p.ToMM(x.GetLeft()) for x in boxes)-30,min(p.ToMM(x.GetTop()) for x in boxes)-30];hi=[max(p.ToMM(x.GetRight()) for x in boxes)-30,max(p.ToMM(x.GetBottom()) for x in boxes)-30]
  else:lo=[row['xy'][i]-row['size'][i]/2 for i in (0,1)];hi=[lo[i]+row['size'][i] for i in (0,1)]
  row['body_box']=[*[round(x,4) for x in lo],11.7,round(hi[0]-lo[0],4),round(hi[1]-lo[1],4),row['size'][2]]
  row['pads']=[dict(xy=[round(p.ToMM(q.GetPosition().x)-30,4),round(p.ToMM(q.GetPosition().y)-30,4)],size=[p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)],net=q.GetNetname(),pin=q.GetNumber()) for q in f.Pads() if q.GetLayerSet().Contains(p.F_Cu)]
 d['extras']=[dict(id='cell',mpn='Adafruit 258 protected 1200mAh',box=[15.5,24,3.0,34,62,5],color='battery',basis='supplier nominal dimensions; incoming cell revision, lead and protection envelope must be measured'),dict(id='speaker',mpn='PUI AS01508AO-WP-R',box=[34,78.9,16.4 if v=='mini' else 18.4,15,11,3],color='black',basis='nominal datasheet body; acoustic coupling and cable still require bench checks')]
 if v=='mini':d['extras'] += [dict(id='nfc',mpn='ELECHOUSE NFC_EX_MINI',box=[30,32,15.5,25,16.4,4.4],color='blue',basis='supplier nominal module outline; wire connector overhang is a separate reserve'),dict(id='nfc_antenna',mpn='included 25x10 ferrite antenna',box=[20,19,19.6,25,10,.6],color='copper',basis='25x10 specified; 0.6 assembled thickness including adhesive is a conservative assumption')]
 else:d['extras'] += [dict(id='lcd',mpn='RB024D18N01B1',box=[3.37,7,19.45,60.26,42.72,2.55],color='glass',basis='drawing thickness2.55 used instead of summary2.3; tolerance and contact side pending incoming inspection'),dict(id='lens',mpn='cut polycarbonate clear 55x40x0.5',box=[6,8.5,22.5,55,40,.5],color='glass',basis='drawing-only cut part, not an off-the-shelf supplier quote')]
 d['clearance_reserves']=[dict(id='battery_service',box=[14.5,23,2.5,36,64,7],purpose='pouch/protection/lead/swelling envelope; no hard compression'),dict(id='wifi_keepout',box=[8.5,0,0,48,9,22],purpose='all-layer copper/metal exclusion in antenna-overhang region'),dict(id='usb_plug',box=[45.5,88,10.5,11,12,8],purpose='plug approach reserve, extends outside enclosure'),dict(id='headphone_plug',box=[22,90,10.5,14,12,8],purpose='plug approach reserve, extends outside enclosure')]
 if v=='mini':d['clearance_reserves'].append(dict(id='nfc_wire',box=[8,30,15.5,21,18,3],purpose='keyed harness + stock100mm antenna lead service loops; nominal reserve, bend routing pending'))
 else:d['clearance_reserves'].append(dict(id='fpc_fold',box=[61,10,15,3.5,35,6.5],purpose='1mm nominal bend radius, 48mm FPC folded under panel; contact face and received tail must be confirmed'))
 d['physical_validation']='pending';d['fabrication_release']=False
 (OUT/(v+'-mechanical.json')).write_text(json.dumps(d,indent=2)+'\n')
