#!/usr/bin/env python3
"""Generate searchable exact-identity BOM and transparent first-batch cost model."""
import csv,json,urllib.parse
from compact_design import ROOT,OUT,SOURCES
D=ROOT/'docs/compact-r1';D.mkdir(exist_ok=True)
# External part allowances are planning EUR, not supplier quotes. USD conversion is a scenario.
external=[
 ('BAT1','Adafruit 258','Protected1S1200mAh cell nominal34x62x5mm',1,[9.5,12],SOURCES['cell']),
 ('SP1','AS01508AO-WP-R','PUI8ohm0.7W wired micro-speaker15x11x3mm',1,[2,5],SOURCES['speaker']),
 ('SD1','SDSQUAC-032G-GN6MA','SanDisk Ultra32GB microSD, clean original-content library',1,[5,9],'https://shop.sandisk.com/products/memory-cards/microsd-cards/sandisk-ultra-uhs-i-microsd-150mbps'),
 ('TH1','103AT-2','Semitec10k NTC bonded to pouch; insulated leads',1,[.5,1.5],'https://www.semitec-global.com/product/at-thermistor/'),
 ('INS1','RX-M2x3x3.2','Ruthex M2 heat-set insert, coupon pilot trial',4,[.08,.2],'https://www.ruthex.de/products/ruthex-gewindeeinsatz-m2-100-stuck-rx-m2x3x3-2'),
 ('SCR1','ISO4762-M2x14-A2','M2x14 socket cap screw, unambiguous standard; supplier not frozen',4,[.04,.15],'https://www.accu.co.uk/socket-cap-screws/4777-SSCF-M2-14-A2'),
 ('SCR2','ISO7045-M1.6x4-A2','Two M1.6x4 pan-head keeper screws; tap PETG1.25mm pilots, qualify pullout',2,[.04,.15],'https://www.accu.co.uk/pozi-pan-head-screws'),
 ('HAR1','PHR-2 + SPH-002T-P0.5S','JST PH2 insulated speaker harness24AWG, polarity continuity checked',1,[.3,1],'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf'),
 ('HAR2','PHR-2 + SPH-002T-P0.5S','JST PH2 thermistor harness26AWG, heatshrink',1,[.3,1],'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf'),
 ('PAD1','3M5413 12mm','Polyimide insulation, cut strips; not bare-cell compression',.1,[1,3],'https://www.3m.com/3M/en_US/p/d/b40068383/'),
 ('STR1','VELCRO ONE-WRAP10mm','Soft pouch-retention band, cut120mm',.12,[2,4],'https://www.velcro.com/products/for-cable-management/'),
 ('FOM1','closed-cell silicone0.5mm','Light battery support only; drawing-defined material, supplier unqualified',1,[.1,.4],''),
 ('GSK1','OC-GSK-SPK-R1','15x11mm outer /11x7mm opening silicone foam1mm; nominal20pctcompression, qualify supplier',1,[.1,.4],'enclosure/compact-r1/speaker-gasket.svg'),
 ('CASE','OpenConteuse compact-r1 PETG','Two shells + buttons + speaker keeper, own CAD; extrusion volume priced separately',1,[0,0],'enclosure/compact-r1/compact.scad')]
results={}
for v in ['mini','explore']:
 d=json.loads((OUT/v/'components.json').read_text());rows=[]
 for p in d['parts']:
  if p['ref'].startswith(('H','TP')):continue
  rows.append(dict(reference=p['ref'],mpn=p['mpn'],description=p.get('value',p['section']),quantity=1,unit_eur_low=p['cost_eur'][0],unit_eur_high=p['cost_eur'][1],source=p['source'],footprint=p['footprint'],basis='engineering allowance, not quote',search='https://www.digikey.fr/en/products?keywords='+urllib.parse.quote(p['mpn'])))
 for ref,mpn,desc,q,price,url in external:
  rows.append(dict(reference=ref,mpn=mpn,description=desc,quantity=q,unit_eur_low=price[0],unit_eur_high=price[1],source=url,footprint='external',basis='engineering allowance / exact standard where noted; not quote',search='https://www.google.com/search?q='+urllib.parse.quote(mpn)))
 if v=='mini':extras=[('NFC1','ELECHOUSE NFC_EX_MINI','PN5321mini with included25x10 ferrite antenna; stock100mmlead',1,[33.73,40],SOURCES['nfc']),('HAR3','SHR-07V-S-B + SSH-003T-P0.2','JST SH7 custom harness to labelled module pads (module pad order not assumed)',1,[.8,2],'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf')]
 else:extras=[('LCD1','RB024D18N01B1','2.4inch SPI18pin0.5FPC, drawing uses2.55mm thickness',1,[3,12],SOURCES['lcd']),('LENS1','OC-LENS-EX-R1','Drawing-defined clear polycarbonate55x40x0.5mm lens, supplier not frozen',1,[.5,2],'enclosure/compact-r1/lens-explore.svg' )]
 for ref,mpn,desc,q,price,url in extras:rows.append(dict(reference=ref,mpn=mpn,description=desc,quantity=q,unit_eur_low=price[0],unit_eur_high=price[1],source=url,footprint='external',basis='engineering allowance; NFC low uses observedUSD35.50x0.95EUR/USD planning FX',search='https://www.google.com/search?q='+urllib.parse.quote(mpn)))
 with (OUT/(v+'-BOM.csv')).open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 parts=[round(sum(r['quantity']*r['unit_eur_'+k] for r in rows),2) for k in ['low','high']]
 # Local PETG planning allowance, model-derived material estimate recorded separately after meshes.
 case=[2.5,5];rec={str(q):[round(parts[i]+case[i]+a[i],2) for i in range(2)] for q,a in [(1,[25,50]),(5,[12,25]),(25,[5,10])]}
 batch={str(q):[round(rec[str(q)][i]*q+[100,250][i],2) for i in range(2)] for q in [1,5,25]}
 results[v]=dict(materials_excluding_print_eur=parts,print_allowance_eur=case,recurring_per_unit_eur=rec,first_batch_including_setup_rework_reserve_eur=batch,bom_rows=len(rows),component_count=sum(1 for p in d['parts'] if not p['ref'].startswith(('H','TP'))))
results['assumptions']={'date':'2026-11-18','currency':'EUR','nfc_observed_usd':35.50,'planning_EUR_per_USD':.95,'fx_is_not_live_quote':True,'vat_rate_example_france':.20,'shipping_first_batch_eur':[40,90],'setup_rework_spares_reserve_per_batch_eur':[100,250],'excludes':['engineering labour','manual enclosure/harness assembly and debug labour','tools and print hardware','certification','extra PCB spins','commercial audio','tax and shipping in recurring tables'],'quote_status':'no binding supplier or fabrication quote','physical_validation':'pending','orders_placed':False}
for v in ['mini','explore']:
 b=results[v]['first_batch_including_setup_rework_reserve_eur']['5'];results[v]['five_unit_france_planning_total_with20pctVAT_shipping_eur']=[round((b[i]+[40,90][i])*1.2,2) for i in range(2)]
(OUT/'costs.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
# A browser-local searchable BOM; no network calls or purchasing actions.
allrows=[]
for v in ['mini','explore']:
 with (OUT/(v+'-BOM.csv')).open() as f:
  for r in csv.DictReader(f):r['variant']=v;allrows.append(r)
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Compact R1 searchable BOM</title><style>body{font:15px system-ui;max-width:1500px;margin:35px auto;padding:20px;background:#f6faf8;color:#173e43}input{padding:12px;width:65%;font:inherit}table{width:100%;border-collapse:collapse;background:white}td,th{padding:9px;text-align:left;border-bottom:1px solid #dde5e1}a{color:#186b85}small{display:block}th{position:sticky;top:0;background:#dcebe4}</style><h1>Compact R1 — component query</h1><p>Exact candidate identities and nominal placement sources. Costs are engineering allowances; all physical validation remains pending. This page works locally and places no orders.</p><input id="q" aria-label="Search all BOM fields" placeholder="Search variant, reference, part number, function…"><p id="count"></p><table><thead><tr><th>Variant / ref</th><th>Part / function</th><th>Qty</th><th>EUR / each</th><th>Sources</th></tr></thead><tbody id="rows"></tbody></table><script>const data=DATA;const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function render(){const q=document.getElementById('q').value.toLowerCase(),r=data.filter(x=>Object.values(x).join(' ').toLowerCase().includes(q));document.getElementById('count').textContent=r.length+' matching BOM rows';document.getElementById('rows').innerHTML=r.map(x=>`<tr><td>${esc(x.variant)} / ${esc(x.reference)}</td><td><b>${esc(x.mpn)}</b><small>${esc(x.description)}</small></td><td>${esc(x.quantity)}</td><td>${esc(x.unit_eur_low)}–${esc(x.unit_eur_high)}</td><td><a href="${esc(x.search)}">Query supplier</a>${x.source?' · <a href="'+esc(x.source.startsWith('https://')?x.source:'../../'+x.source)+'">Reference / drawing</a>':''}</td></tr>`).join('')}document.getElementById('q').addEventListener('input',render);render();</script></html>'''.replace('DATA',json.dumps(allrows).replace('<','\\u003c'))
(D/'BOM.html').write_text(html)
