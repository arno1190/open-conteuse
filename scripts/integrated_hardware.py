"""Single-source catalogue/layout utilities. Standard-library host checks only."""
import csv
import hashlib
import json
import math
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'hardware/integration/catalog.json';LAYOUT=ROOT/'hardware/integration/layout.json'

def read_data():
    return json.loads(CATALOG.read_text()),json.loads(LAYOUT.read_text())

def indexed(catalog):
    return {p['id']:p for p in catalog['parts']}

def size(part):
    return part.get('clearance_envelope_mm',part['dimensions_mm'])

def rotated_size(dims,angle):
    return list(dims) if angle%180==0 else [dims[1],dims[0],dims[2]]

def transform_point(part,pose,point):
    x,y,z=point
    if pose.get('orientation')=='actuator_outward_right':
        result=[z,x,y]
    else:
        d=part['dimensions_mm'];a=pose.get('rotate_z',0)%360
        result={0:[x,y,z],90:[d[1]-y,x,z],180:[d[0]-x,d[1]-y,z],270:[y,d[0]-x,z]}[a]
    return [round(result[i]+pose['xyz'][i],6) for i in range(3)]

def aabb(part,pose):
    d=size(part)
    if pose.get('orientation')=='actuator_outward_right':d=[d[2],d[0],d[1]]
    else:d=rotated_size(d,pose.get('rotate_z',0))
    low=list(pose['xyz'])
    if pose.get('component_side')=='toward_front':
        low[2]-=4.3;d[2]=4.3+1.6+1.5
    return low,[low[i]+d[i] for i in range(3)]

def separated(a,b,gap=0):
    return any(a[1][i]+gap<=b[0][i] or b[1][i]+gap<=a[0][i] for i in range(3))

def placements(layout,variant):
    return layout['common']+layout[variant]

def validate(catalog,layout):
    errors=[];parts=indexed(catalog)
    if len(parts)!=len(catalog['parts']):errors.append('duplicate part id')
    for p in catalog['parts']:
        if not p.get('manufacturer') or not p.get('part_number'):errors.append('missing exact identification: '+p['id'])
        if not p.get('sourcing_queries'):errors.append('missing sourcing queries: '+p['id'])
        quote=p.get('quote',{})
        if quote.get('unit_price') is not None and (not quote.get('url') or not quote.get('observed_on') or not quote.get('currency')):errors.append('unattributed quote: '+p['id'])
        if p.get('model'):
            path=ROOT/p['model']['path']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=p['model']['sha256']:errors.append('changed model: '+p['id'])
    case=layout['case']
    for variant in ('mini','explore'):
        scene=placements(layout,variant)
        if len({s['part'] for s in scene})!=len(scene):errors.append('duplicate placement '+variant)
        for p in catalog['parts']:
            if p['id'] in {s['part'] for s in scene} and p['quantity'][variant]!=1:errors.append('placement quantity mismatch '+p['id']+'/'+variant)
        for item in scene:
            p=parts[item['part']];lo,hi=aabb(p,item)
            # Purposeful connector/switch protrusion is exempt only on its named wall.
            for axis,maximum in [(0,case['width']),(1,case['height'])]:
                allowance=case['wall']
                if item.get('orientation')=='actuator_outward_right' and axis==0:
                    if lo[axis]<case['wall'] or hi[axis]>maximum+1:errors.append('switch wall overrun')
                elif item['part']=='headphone' and axis==0:
                    if lo[axis]<allowance or hi[axis]>maximum:errors.append('headphone connector exceeds designated recess')
                    pcb=p['pcb'];board_hi=transform_point(p,item,[pcb['origin_in_model_mm'][0]+pcb['size_mm'][0],0,0])[0]
                    if board_hi>maximum-allowance:errors.append('headphone PCB enters case wall')
                elif lo[axis]<allowance-.001 or hi[axis]>maximum-allowance+.001:errors.append(f'{variant}: {p["id"]} leaves inner XY bounds on axis {axis}')
            if lo[2]<case['wall']-.001 or hi[2]>case['front_depth']-.35:errors.append(f'{variant}: {p["id"]} exceeds depth envelope')
        for i,item in enumerate(scene):
            for other in scene[i+1:]:
                if not separated(aabb(parts[item['part']],item),aabb(parts[other['part']],other)):
                    errors.append(f'{variant}: component envelopes overlap: {item["part"]}/{other["part"]}')
        for clearance in layout.get('service_clearances',[]):
            box=(clearance['xyz'],[clearance['xyz'][i]+clearance['size_mm'][i] for i in range(3)])
            for item in scene:
                if item['part'] not in clearance.get('allowed_contact_parts',[]) and not separated(box,aabb(parts[item['part']],item)):
                    errors.append(f'{variant}: service corridor {clearance["id"]} blocked by {item["part"]}')
    return errors

def quote(catalog,mini=1,explore=1):
    totals={};missing=[];unavailable=[];lines=[]
    for p in catalog['parts']:
        needed=p['quantity']['mini']*mini+p['quantity']['explore']*explore
        if not needed:continue
        if p.get('purchase_scope')=='shared_project_pack':needed=1
        q=p.get('quote',{})
        if q.get('unit_price') is not None:
            amount=Decimal(str(q['unit_price']))*needed;ordered=needed
        elif q.get('pack_price') is not None:
            packs=max(q.get('minimum_order_packs',1),math.ceil(needed/q['pack_quantity']));amount=Decimal(str(q['pack_price']))*packs;ordered=packs*q['pack_quantity']
        else:missing.append(p['id']);continue
        currency=q['currency'];totals[currency]=totals.get(currency,Decimal(0))+amount
        if q.get('stock')!='in_stock':unavailable.append(p['id'])
        lines.append({'part':p['id'],'needed':needed,'buy_quantity':ordered,'currency':currency,'subtotal':str(amount.quantize(Decimal('.01')))})
    return {'known_subtotals':{c:str(n.quantize(Decimal('.01'))) for c,n in totals.items()},'lines':lines,'missing_quotes':missing,'unavailable_quoted_parts':unavailable,'shipping':catalog['quote_requirements']['shipping_quote_status'],'is_complete_landed_quote':False}

def gates(catalog,layout):
    issues=[]
    for p in catalog['parts']:
        if p.get('dimensional_evidence')=='manufacturer_2D_only_height_unverified':issues.append(p['id']+': assembled/header height not verified; cradle is a design reservation')
        for note in p.get('source_notes',[]):
            if 'Retail prose lists' in note:issues.append(p['id']+': manufacturer nominal model and retail dimension text disagree')
        if p.get('assembly_scope')=='consumable' and 'ordering variant' in str(p.get('source_notes','')):issues.append(p['id']+': ordering suffix not frozen')
    q=quote(catalog)
    issues.extend('supplier quote missing: '+s for s in q['missing_quotes'])
    issues.extend('quoted item unavailable at observed supplier: '+s for s in q['unavailable_quoted_parts'])
    if not catalog['quote_requirements'].get('delivery_postcode'):issues.append('delivery postcode/country not confirmed; no exact shipping/tax quote')
    issues.extend(['power_switch: undetailed source model; actuator/retention measurement pending', 'integrated TLV320/latch firmware profile not implemented; old bench mapping incompatible', 'slicer/support review and physical print fit pending', 'physical fit/electrical/acoustic/thermal/drop validation pending'])
    return issues

def generate(catalog,layout):
    folder=ROOT/'enclosure/integrated';folder.mkdir(exist_ok=True)
    rows=[]
    for p in catalog['parts']:
        if not isinstance(p.get('dimensions_mm'),list):continue
        pcb=p.get('pcb') or {};d=p['dimensions_mm'];effective=[max(d[i],size(p)[i]) for i in range(3)]
        rows.append([p['id'],d,effective,pcb.get('origin_in_model_mm',[0,0,0]),pcb.get('size_mm',[0,0,0]),pcb.get('holes_mm',[]),Path(p.get('model',{}).get('path','')).name if p.get('model') else '',p.get('mounting',{}).get('holes_mm',[])])
    source='// Generated by scripts/integrated_hardware.py from catalog.json/layout.json. Do not hand-edit.\n'
    source+='catalog_rows = '+json.dumps(rows,separators=(',',':'))+';\n'
    source+='common_poses = '+json.dumps([[p['part'],p['xyz'],p.get('rotate_z',0),p['mount'],p.get('orientation','')] for p in layout['common']],separators=(',',':'))+';\n'
    for variant in ('mini','explore'):source+=variant+'_poses = '+json.dumps([[p['part'],p['xyz'],p.get('rotate_z',0),p['mount'],''] for p in layout[variant]],separators=(',',':'))+';\n'
    for key,value in layout['case'].items():source+='case_'+key+' = '+json.dumps(value)+';\n'
    source+='control_centres = '+json.dumps(json.loads((ROOT/'enclosure/controls.json').read_text())['actuators_mm'])+';\n'
    (folder/'generated_data.scad').write_text(source)
    rowscsv=[]
    for p in catalog['parts']:
        q=p.get('quote',{});rowscsv.append([p['id'],p['manufacturer'],p['part_number'],p['quantity']['mini'],p['quantity']['explore'],q.get('supplier',''),q.get('sku',''),q.get('unit_price',''),q.get('pack_price',''),q.get('pack_quantity',''),q.get('currency',''),q.get('stock',q.get('status','unknown')),q.get('url',p['product_url']),p['sourcing_queries']['digikey'],p['sourcing_queries']['mouser'],p['sourcing_queries']['aliexpress']])
    with (ROOT/'hardware/integration/BOM.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['id','manufacturer','part_number','qty_mini','qty_explore','quoted_supplier','quoted_sku','unit_price','pack_price','pack_quantity','currency','stock_or_quote_status','primary_source','digikey_query','mouser_query','aliexpress_query']);w.writerows(rowscsv)
    result={'catalog_revision':catalog['revision'],'nominal_geometry_errors':validate(catalog,layout),'release_gates':gates(catalog,layout),'one_mini_one_explore':quote(catalog)}
    (ROOT/'hardware/integration/status.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    cat,layout=read_data();result=generate(cat,layout)
    if result['nominal_geometry_errors']:print('\n'.join(result['nominal_geometry_errors']));raise SystemExit(1)
    print('Catalogue/model hashes, component envelopes and service corridors agree.')
    print('Release gates remain explicit:',len(result['release_gates']))
