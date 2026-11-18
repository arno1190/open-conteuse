#!/usr/bin/env python3
"""Build the complete visual atlas: captions, contact sheets, PDF and provenance.

Uses source-derived Blender images; never changes enclosure/manufacturing sources.
"""
import hashlib,io,json,math,textwrap
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table,TableStyle,Paragraph
from reportlab.lib.styles import ParagraphStyle
from integrated_hardware import ROOT,read_data,indexed
from atlas_plan import views
OUT=ROOT/'docs/visual-atlas';IMAGES=OUT/'images';SHEETS=OUT/'sheets';SHEETS.mkdir(parents=True,exist_ok=True)
CAT,LAYOUT=read_data();PARTS=indexed(CAT)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
INTRO='Mini and Explore share a nominal 112 × 210 × 50 mm enclosure. Mini has an NFC card area and five buttons. Explore has an unpowered display and eight buttons; this revision omits Explore NFC. The assembly is a digital prototype with physical fit still pending. Shared module close-ups are grouped with Mini; Explore adds its display and eight-switch board.'
LEGEND='Blue: Adafruit PCBs. Green: proposed custom PCB soldermask. Black: chips, sockets and speaker enclosure. Silver: connector shells, shield and cell foil. Gold: contacts. Warm white: proposed case finish. Grey: removable carrier and retainers. Teal/amber: proposed button finishes. Orange: section faces, not the material colour.'
MODEL_SCOPE='Nine manufacturer STEP assemblies supply purchased-module geometry. Native KiCad supplies the custom PCB outlines, holes, pads, tracks and silkscreen; their component bodies are generic illustrations at native footprint positions. MCU and regulator details are visual proxies within reserved envelopes. Colours and added identification labels are illustrative, not exact manufacturer artwork. Optional tall breakout headers, screw-terminal block, wires and fasteners are omitted. No wiring or fastening is implied by an empty space. Purchased-module models may be single external solids: section caps do not reveal speaker, cell or other hidden internal construction.'
LIMITS='Pending: received MCU/header height and switch actuator measurements; printer-specific slicing/support and physical fit; integrated codec/latch firmware; electrical, charging, acoustic, thermal, runtime and drop/retention tests. Rendering is not evidence of those properties. No purchases or fabrication orders were made.'
def specs():
 return [dict(dict(variant=v,**s),title='Exterior button close-up' if s['id']=='detail-controls' else s['title']) for v in ['mini','explore'] for s in views(v)]
def caption(s):
 mode=s['mode'];ident=s['id'];variant=s['variant'];extra=''
 if mode=='assembled':extra='Full nominal assembly. '+('Display is unpowered; ' if variant=='explore' else 'Mini has no display; ')+'case and button colours are proposed finishes.'
 elif mode=='open':extra='Lid hidden; front shell and removable carrier remain assembled. Harness and screws omitted.'
 elif mode=='front-layer':extra='Case and rear carrier hidden; view faces the rear of the controls PCB. The controls detail shows the opposite actuator side.'
 elif mode=='carrier':extra='Front shell and front electronics hidden. Rear module placement, battery cover and retainers are visible; MCU/regulator are visual proxies.'
 elif mode=='exploded':extra='Display offsets only: rear layer +45 mm X/+60 mm Z; lid −80 mm X/+35 mm Y/+120 mm Z. These are not removal paths or measured clearances.'
 elif mode=='section':
  axis,value,keep=s['cut'];extra=f"Plane {'XYZ'[axis]} = {value} mm; retain {'lower' if keep=='low' else 'higher'} coordinates. Orange marks solid cut faces; voids stay open. Native copper/silk surfaces are clipped without solid caps. Generic/proxy components remain illustrative; supplied module solids do not resolve hidden internal construction."
 elif mode=='board':
  p=PARTS[s['focus']];extra=f"{p['manufacturer']} {p['part_number']}. "+('Native KiCad board with generic component bodies; green soldermask is proposed.' if s['focus'] in ['controls','mute_latch'] else 'Visual proxy; not a manufacturer-verified assembled model.' if s['focus'] in ['mcu','regulator'] else 'Manufacturer CAD geometry with illustrative finish and component material assignment.')
 elif mode=='detail':
  details={'usb':'Charge-only USB C opening. Upper housing is cut away at Z35 to reveal the socket; service USB power isolation is still required.','headphone':'Jack mouth and recess. Upper housing cut away at Z35; plug-barrel fit and insertion-mute validation pending.','switch':'Conservative switch body envelope and retainer. Upper housing cut away at Z35. Actuator dimensions still require received-part measurement.','controls':'Exterior button caps against the opaque front face; the internal switch stack is not visible here. See section A and the controls PCB view for the internal parts. The documented nominal cap-to-switch gap is 0.2 mm.','battery':'Battery cover hidden. Rigid cage carries tie tension; do not compress the pouch cell. Cell is shown by manufacturer body geometry; tie/wire routing omitted.','mcu':'Cradle, edge seats and retaining fingers. MCU geometry is illustrative; assembled/header height remains a fit gate.','speaker':'Rear layer hidden; housing removed above Z8 to expose flange supports and spacer. Local flange bearing Z 1.0–2.7 mm; post top global Z 7.4 mm; rigid spacer 4 mm. No acoustic seal validated.','sd':'Rotated microSD breakout and removal region. Card extraction is toward +X; reserve the layout corridor and keep the harness out. No removable card is inserted in this render.'}
  extra=details[s['focus']]
 return extra

def build_sheets(plan):
 rows=[];font=ImageFont.truetype(FONT,22);bold=ImageFont.truetype(BOLD,27)
 for variant in ['mini','explore']:
  categories=[('exterior',[s for s in plan if s['variant']==variant and s['mode']=='assembled']),('assembly',[s for s in plan if s['variant']==variant and s['mode'] in ['open','front-layer','carrier','exploded']]),('sections',[s for s in plan if s['variant']==variant and s['mode']=='section']),('details',[s for s in plan if s['variant']==variant and s['mode']=='detail']),('boards',[s for s in plan if s['variant']==variant and s['mode']=='board'])]
  for category,items in categories:
   for start in range(0,len(items),4):
    subset=items[start:start+4];sheet=Image.new('RGB',(2048,1730),'#f8fafb');draw=ImageDraw.Draw(sheet);draw.text((48,28),variant.title()+' · '+category.title()+' · '+str(start//4+1),font=bold,fill='#153943')
    for i,s in enumerate(subset):
     x=32+(i%2)*1024;y=88+(i//2)*810;path=IMAGES/f'{variant}-{s["id"]}.png';im=Image.open(path).convert('RGB');im.thumbnail((984,738));sheet.paste(im,(x+(984-im.width)//2,y));title=s['title']
     draw.text((x+10,y+742),s['id'],font=font,fill='#153943');draw.text((x+10,y+771),title[:64],font=font,fill='#304b52')
    name=f'{variant}-{category}-{start//4+1:02}.png';sheet.save(SHEETS/name,optimize=True);rows.append({'file':name,'variant':variant,'category':category,'views':[s['id'] for s in subset]})
 return rows

def pdf_doc(plan):
 pdfmetrics.registerFont(TTFont('Atlas',FONT));pdfmetrics.registerFont(TTFont('AtlasBold',BOLD));path=OUT/'Open-Conteuse-Visual-Atlas.pdf';c=canvas.Canvas(str(path),pagesize=(595.28,841.89),pageCompression=1);c.setTitle('Open Conteuse Mini and Explore visual design atlas');c.setAuthor('Open Conteuse project');pages=0
 def page(title,kicker='OPEN CONTEUSE / VISUAL DESIGN ATLAS'):
  nonlocal pages
  pages+=1;c.setFillColor(HexColor('#173e47'));c.setFont('AtlasBold',8);c.drawString(36,811,kicker);c.setFont('AtlasBold',19);c.drawString(36,779,title);c.setStrokeColor(HexColor('#bed0d4'));c.line(36,765,559,765);c.setFont('Atlas',7.2);c.setFillColor(HexColor('#48636b'));c.drawString(36,24,'18 November 2026 · Nominal CAD · Physical validation pending');c.drawRightString(559,24,str(pages));return 744
 def paragraph(text,y,font=9.5,width=518,leading=14):
  style=ParagraphStyle('body',fontName='Atlas',fontSize=font,leading=leading,textColor=HexColor('#203a42'));p=Paragraph(escape(text),style);_,h=p.wrap(width,700);p.drawOn(c,36,y-h);return y-h-12
 def photo(s,y,h=279):
  im=Image.open(IMAGES/f'{s["variant"]}-{s["id"]}.png').convert('RGB');im.thumbnail((1200,900));buf=io.BytesIO();im.save(buf,format='JPEG',quality=79,optimize=True);buf.seek(0)
  c.drawImage(ImageReader(buf),36,y-h,width=523,height=h,preserveAspectRatio=True,anchor='c');y-=h+6
  c.setFont('AtlasBold',10);c.setFillColor(HexColor('#173e47'));c.drawString(36,y,s['variant'].title()+' · '+s['title']);return paragraph(caption(s),y-10,font=8.1,leading=11)
 y=page('Mini and Explore visual design atlas');y=paragraph(INTRO,y,font=11,leading=16);cover=next(s for s in plan if s['variant']=='explore' and s['id']=='hero-front');y=photo(cover,y,h=390);y=paragraph('Complete exterior, assembly, sectional, service and component view set. Read the coordinate guide before interpreting a section. All72individualPNGfigures are indexed in the repository.',y,font=10,leading=15);c.showPage()
 y=page('Materials and model confidence');y=paragraph(LEGEND,y);y=paragraph(MODEL_SCOPE,y);y=paragraph(LIMITS,y)
 for name,col in [('Case','#e4e5dd'),('Carrier','#94a5a8'),('Adafruit PCB','#0754a0'),('Custom PCB','#154d37'),('Chips','#191d22'),('Metal','#bcc4ca'),('Contacts','#d1a340'),('Cut surface','#d68843')]:
  c.setFillColor(HexColor(col));c.rect(36,y-14,28,14,fill=1,stroke=0);c.setFillColor(HexColor('#203a42'));c.setFont('Atlas',9);c.drawString(76,y-11,name);y-=28
 c.showPage()
 y=page('Coordinate and section guide');y=paragraph('X runs across the 112 mm width. Y runs from the USB end 0 to the controls end 210 mm. Z runs from the front outer face 0 to the rear 50 mm. Views are orthographic; do not measure pixels. A–F are vertical sections, G/H horizontal. Section planes remove geometry for visibility; they are not part seams.',y)
 x0,y0,scale=70,365,1.45;c.setStrokeColor(HexColor('#193d47'));c.rect(x0,y0,112*scale,210*scale,stroke=1,fill=0);c.setFont('Atlas',8);c.drawString(x0,y0+210*scale+10,'Y0 USB end');c.drawString(x0,y0-17,'Y210 controls end')
 for code,x in [('A',32),('B',56),('C',82)]:c.setStrokeColor(HexColor('#c07936'));c.line(x0+x*scale,y0,x0+x*scale,y0+210*scale);c.drawString(x0+x*scale-3,y0+210*scale+24,code)
 for code,yval in [('D',20),('E',95),('F',168)]:c.setStrokeColor(HexColor('#268195'));yv=y0+(210-yval)*scale;c.line(x0,yv,x0+112*scale,yv);c.drawString(x0+112*scale+8,yv-3,code)
 text='A X32: MCU/control side\nB X56: centreline\nC X82: battery/audio side\nD Y20: charger and MCU\nE Y95: speaker/battery\nF Y168: controls/headphone\nG Z15: front layer\nH Z35: rear layer'
 for i,line in enumerate(text.splitlines()):c.setFillColor(HexColor('#203a42'));c.drawString(280,660-i*23,line)
 paragraph('All assemblies use the same coordinate system; the speaker changes orientation between variants. Orange caps are generated with exact solid intersections. Thin KiCad copper/silkscreen surfaces are clipped uncapped so their absence is not shown as solid laminate.',320);c.showPage()
 # Figures in source-plan order, two per page. Section pages pair only within mode.
 for variant in ['mini','explore']:
  groups=[]
  categories=[('Exterior views',['assembled']),('Internal and exploded assemblies',['open','front-layer','carrier','exploded']),('Section cuts',['section']),('Assembly details',['detail']),('Component views',['board'])]
  for title,modes in categories:
   items=[s for s in plan if s['variant']==variant and s['mode'] in modes]
   for start in range(0,len(items),2):groups.append((title,items[start:start+2]))
  for title,items in groups:
   y=page(variant.title()+' / '+title)
   for s in items:y=photo(s,y,h=258)
   c.showPage()
 # Full exact-ID BOM with sourcing links.
 style=ParagraphStyle('cell',fontName='Atlas',fontSize=7.2,leading=10,textColor=HexColor('#203a42'))
 for start in range(0,len(CAT['parts']),10):
  y=page('Exact component BOM / '+str(start//10+1));rows=[['Item and exact identification','Mini','Explore','Observed price','Search links']]
  for p in CAT['parts'][start:start+10]:
   q=p.get('quote',{});price=str(q['unit_price'] if q.get('unit_price') is not None else q['pack_price'] if q.get('pack_price') is not None else 'unquoted')+' '+q.get('currency','');price+=' / pack'+str(q['pack_quantity']) if 'pack_price' in q else '';price+='; OOS' if q.get('stock')=='out_of_stock' else ''
   links=' '.join(f'<link href="{escape(p["sourcing_queries"][k])}" color="#096879">{name}</link>' for k,name in [('digikey','DigiKey'),('mouser','Mouser'),('aliexpress','AliExpress')])
   rows.append([Paragraph(escape(p['id']+' · '+p['manufacturer']+' '+p['part_number']),style),str(p['quantity']['mini']),str(p['quantity']['explore']),Paragraph(escape(price),style),Paragraph(links,style)])
  table=Table(rows,colWidths=[238,29,37,100,119],repeatRows=1);table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'AtlasBold'),('FONTSIZE',(0,0),(-1,0),7.4),('BACKGROUND',(0,0),(-1,0),HexColor('#dce8eb')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,1),(-1,-1),'Atlas'),('FONTSIZE',(0,1),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,HexColor('#ccdade'))]));w,h=table.wrap(523,680);table.drawOn(c,36,y-h)
  paragraph('Supplier prices observed 17 November 2026; not refreshed for this atlas. Unknown is not zero. Shared wire/filament/fastener packs are counted by the pricing calculator, not by summing per-device pack quantities. Search links do not authorize substitutions or guarantee authentic stock.',y-h-16,font=8.3,leading=12);c.showPage()
 y=page('Assembly sequence and release gates')
 for text in ['1. Confirm received board revisions, MCU/header height, switch actuator, solder lead lengths and connector barrel dimensions. Update CAD before a full print.','2. Print the fit coupon; review support, clearances and usable printer-bed area for 112 × 210 mm parts. The STLs are prototypes, not calibrated G-code.','3. Install nuts, insert buttons from inside, then fit controls/variant PCB and speaker with its 4 mm rigid spacer. Check free travel.','4. Fit carrier modules, MCU/regulator/switch retainers, battery cage and cover. Tie tension acts on the rigid cage, never the pouch cell. Route and strain-relieve the harness; preserve SD removal access.','5. Verify screw engagement and all underside lead clearances. The drawings omit fasteners and harnesses; consult electrical/assembly sources before powering.','6. Bring up current-limited isolated logic first, then codec/mute, power/charge thermal, acoustics, runtime and mechanical retention. All physical results remain pending.']:
  y=paragraph(text,y)
 y=paragraph('Known purchase subtotal for one Mini and one Explore: USD 242.76 + GBP 37.07 + EUR 21.99, before unquoted PCBs/cards, shipping and tax. Indicative first-purchase budgets: EUR 285–355 for Mini, EUR 275–345 for Explore, EUR 430–550 combined; these reuse explicit 17 November FX/VAT/freight assumptions, not an exact landed quote. Exact MCU and PN532 supplier stock was unavailable at that observation.',y)
 y=paragraph('Source files: github.com/arno1190/open-conteuse · hardware/integration/README.md · docs/HARDWARE_COST.md · enclosure/integrated/print/assembly_BOM.csv. The repository index includes each PNG, its caption, source/hash manifest and rendering commands.',y);c.showPage();c.save();return pages

def build_markdown(plan,sheets,pages):
 lines=['# Open Conteuse Mini and Explore visual design atlas','Updated 18 November 2026. '+INTRO,'[Download the complete PDF](Open-Conteuse-Visual-Atlas.pdf)',f'The document contains {len(plan)} shaded CAD figures and {pages} PDF pages. Each section is a separate view of the actual nominal assembly geometry.','## Colours and model confidence',LEGEND,MODEL_SCOPE,LIMITS,'## Coordinate guide','X: across 112 mm width. Y: USB end 0 → controls end 210 mm. Z: front 0 → rear 50 mm. Orange indicates section faces. Cuts A/B/C: X 32/56/82 mm; D/E/F: Y 20/95/168 mm; G/H: Z 15/35 mm. Lower/higher retained side is stated in every section caption.']
 for variant in ['mini','explore']:
  lines+=['## '+variant.title()+' views']
  for sheet in [s for s in sheets if s['variant']==variant]:lines+=['### '+sheet['category'].title()+' '+sheet['file'][-6:-4],f'![{variant} {sheet["category"]}](sheets/{sheet["file"]})']
  lines+=['### Full resolution figure index'];table=['| View | Description | Interpretation |','| --- | --- | --- |']
  for s in [s for s in plan if s['variant']==variant]:table.append(f'| [{s["id"]}](images/{variant}-{s["id"]}.png) | {s["title"]} | {caption(s)} |')
  lines.append('\n'.join(table))
 lines+=['## BOM and assembly','[Every exact purchased part and supplier query](../../hardware/integration/BOM.csv) · [Printed parts and quantities](../../enclosure/integrated/print/assembly_BOM.csv) · [Electrical and mechanical assembly](../../hardware/integration/README.md) · [Budget](../HARDWARE_COST.md)','## Regenerate','```sh\npython3 scripts/prepare_atlas.py\npython3 scripts/run_atlas.py\npython3 scripts/build_atlas_doc.py\npython3 scripts/check_atlas.py\n```','CadQuery 2.7 prepares manufacturer solids; KiCad 9 exports exact board/copper/silk geometry; Blender 4.3.2/Cycles CPU renders with 24 samples and seed 31415. Camera fitting is orthographic. Section clipping does not edit any printable STL or KiCad source. Rigid KiCad frame mappings preserve board handedness, and an independent regression check verifies the hollow section and all eight actuator centres. Manufacturer Adafruit meshes retain their existingMIT attribution; native KiCad library-derived geometry retains the existing KiCad library exception notices.','The manifest binds source hashes and rendered files. Wires/fasteners, received-part dimensions and every physical validation gate remain outside the rendered proof.']
 (OUT/'README.md').write_text('\n\n'.join(lines)+'\n')

def main():
 plan=specs()
 receipt=json.loads((OUT/'render-receipt.json').read_text())
 assert set(receipt['completed_views'])=={s['variant']+'-'+s['id']+'.png' for s in plan}
 for name,digest in receipt['images_sha256'].items():assert hashlib.sha256((IMAGES/name).read_bytes()).hexdigest()==digest,name
 for s in plan:
  p=IMAGES/f'{s["variant"]}-{s["id"]}.png';assert p.is_file(),p
 sheets=build_sheets(plan);pages=pdf_doc(plan);build_markdown(plan,sheets,pages)
 sourcefiles=['hardware/integration/catalog.json','hardware/integration/layout.json','enclosure/integrated/integrated.scad','enclosure/integrated/print/manifest.json','hardware/controls/controls.kicad_pcb','hardware/integration/mute-latch/mute-latch.kicad_pcb','enclosure/controls.json','scripts/render_atlas.py','scripts/atlas_plan.py','scripts/prepare_atlas.py','scripts/atlas_pcb_geometry.py','scripts/check_atlas_geometry.py','scripts/run_atlas.py','scripts/requirements-atlas.txt','scripts/build_atlas_doc.py']
 artifacts=[p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json']
 manifest={'renderer':{'blender':'4.3.2','engine':'Cycles CPU','samples':24,'seed':31415,'camera':'orthographic; auto-fit except details','STEP_tessellation_mm':.1,'STEP_angular_tolerance_rad':.2},'date':'2026-11-18','views':[dict(s,file=f'images/{s["variant"]}-{s["id"]}.png',caption=caption(s)) for s in plan],'sheets':sheets,'pdf_pages':pages,'physical_validation':'pending','source_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sourcefiles},'artifacts_sha256':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts}}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(len(plan),'figures',len(sheets),'sheets',pages,'PDF pages', (OUT/'Open-Conteuse-Visual-Atlas.pdf').stat().st_size,'PDFbytes')
if __name__=='__main__':main()
