"""Current exact-identity reference BOM and transparent RFQ allowances, no quotes."""
import csv,json,urllib.parse
from pathlib import Path
from project import ROOT,HARDWARE,BOARDS,RFQ
extras=json.loads((HARDWARE/'common-parts.json').read_text())
external=extras['shared']
base=extras['explore_display']
for r in external:
 if r['reference']=='SCR2':r['mpn']='ISO7045-Z-M1.6x4-A2'
 r['basis']='engineering allowance; supplier confirmation pending'
fields=['reference','mpn','description','quantity','unit_eur_low','unit_eur_high','source','footprint','basis','search']
allrows={}
def extra(ref,mpn,desc,q,low,high,source=''):
 return dict(zip(fields,[ref,mpn,desc,q,low,high,source,'external','engineering allowance; not a quote','https://www.google.com/search?q='+urllib.parse.quote(mpn)]))
for name in BOARDS:
 d=json.loads((HARDWARE/name/'components.json').read_text());rows=[]
 for r in d['parts']:
  if r['ref'].startswith('H'):continue
  rows.append(dict(zip(fields,[r['ref'],r['mpn'],r.get('section',''),1,*r['cost_eur'],r['source'] or ('hardware/'+name+'/'+name+'.kicad_pcb' if r['ref'].startswith('TP') else 'https://www.yageo.com/en/Product/Index/product_type/chip-resistors'),r['footprint'],'copper pad, not purchased' if r['ref'].startswith('TP') else 'manual solder termination, not purchased' if r['mpn']=='OC-WIRE-3' else 'selective hard-gold copper contacts, not purchased' if r['mpn']=='OC-ID-CONTACTS' else 'planning allowance; not supplier quote','https://www.digikey.fr/en/products?keywords='+urllib.parse.quote(r['mpn'])])))
 if name in ('mini','explore'):
  rows += [dict(r) for r in external]
  rows +=[extra('CASE','OC-'+name.upper()+'-CASE','Current source-defined PETG housing, caps, bridge',1,2.5,6,'enclosure/design.scad')]
  if name=='explore':
   for ref in ('LCD1','LENS1'):
    r=dict(next(r for r in base if r['reference']==ref));r['basis']='planning allowance; not a quote';rows.append(r)
  else:
   rows +=[extra('HAR3','SHR-07V-S + SSH-003T-P0.2','7way JSTSH housing; only positions1,2,6 populated, 28AWG three-wire harness',1,.6,2,'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf'),extra('SCR3','ISO7045-Z-M1.6x4-A2','Two standard M1.6x4 pan-head reader screws; head envelope3.2x1.3mm; qualify actual fit/pullout',2,.04,.15,'https://www.accu.co.uk/pozi-pan-head-screws')]
 elif name=='story-card':rows +=[extra('WINDOW','OC-ID-WINDOW-R1','Clear PETG sheet34x39x0.50mm, cut/deburred; supplier tolerance/retention pending',1,.08,.35,'enclosure/card-window.svg'),extra('CASE','OC-ID-CARD-CASE','Two printed cartridge halves and replaceable paper insert; no audio storage',1,.5,2,'enclosure/card.scad'),extra('SCR','ISO7045-Z-M1.6x3-A2','Two cartridge handle panhead screws',2,.04,.15),extra('PCB','OC-ID-CARD-PCB','20x12x0.8mm 2layer selective hardgold wear pads; MOQ/NRE excluded',1,1,4,'hardware/story-card/story-card.kicad_pcb')]
 else:rows +=[extra('PCB','OC-ID-READER-PCB','50x11x1.6mm 2layer FR4 reader; MOQ/NRE excluded',1,1,3,'hardware/card-reader/card-reader.kicad_pcb')]
 for row in rows:
  if not row['source']:row['source']='docs/design/README.md'
 with (HARDWARE/name/'BOM.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
 allrows[name]=rows
cost={}
def total(rows):return [round(sum(float(r['quantity'])*float(r[k]) for r in rows),2) for k in ('unit_eur_low','unit_eur_high')]
for v in ('mini','explore'):
 rows=allrows[v]+(allrows['card-reader']+allrows['story-card'] if v=='mini' else [])
 mat=total(rows);pcba=[25,55];small_pcba=[3,10] if v=='mini' else [0,0];rec=[round(mat[i]+pcba[i]+small_pcba[i],2) for i in (0,1)]
 cost[v]=dict(reference_materials_including_print_and_one_card_eur=mat,main_pcb_and_machine_assembly_allowance_eur=pcba,reader_and_token_assembly_allowance_eur=small_pcba,one_off_recurring_reference_eur=rec,first_unit_with_setup_reserve_eur=[round(rec[0]+100,2),round(rec[1]+250,2)],retail_target_vat_included_eur=99 if v=='mini' else 129,volume_landed_cogs_goal_eur=35 if v=='mini' else 45)
cost['both_players_reference_recurring_eur']=[round(cost['mini']['one_off_recurring_reference_eur'][i]+cost['explore']['one_off_recurring_reference_eur'][i],2) for i in (0,1)]
cost['both_players_first_batch_with_shared_setup_reserve_eur']=[round(cost['both_players_reference_recurring_eur'][i]+[100,250][i],2) for i in (0,1)]
cost['story_card_reference_materials_eur']=total(allrows['story-card'])
cost['assumptions']=dict(date='2026-11-20',currency='EUR',quote_status='No binding quote received',physical_validation='pending',orders_placed=False,setup_reserve_eur=[100,250],excludes=['engineering and integrated codec firmware','manual box assembly, finishing, debug labour','shipping, import charges, VAT','certification, tooling and extra spins','audio production'],retail_note='Retail prices are business targets at production volume, not prices supported by q1 prototypes. RFQ must quantify MOQ, assembly, yield, warranty, packaging, channel margin and engineering amortization.',reader_fastener='ISO7045-Z-M1.6x4-A2 standard panhead3.2x1.3mm at revised reader mount; qualify fit/pullout and supplier drawing.')
(RFQ/'costs.json').write_text(json.dumps(cost,indent=2)+'\n')
print(json.dumps(cost,indent=2))
