"""Build one engineering RFQ PDF from current docs, exact BOM and CAD views."""
import csv,json,re,hashlib,io
from html import escape as html_escape
from PIL import Image as RasterImage
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from project import ROOT,RFQ,DOCS,BOARDS,HARDWARE
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';pdfmetrics.registerFont(TTFont('D',font));pdfmetrics.registerFont(TTFont('DB',font.replace('Sans.ttf','Sans-Bold.ttf')))
styles=getSampleStyleSheet()
for k in styles.byName:styles[k].fontName='D'
styles.add(ParagraphStyle(name='Tiny',fontName='D',fontSize=6.5,leading=9))
styles['BodyText'].fontSize=9;styles['BodyText'].leading=13
inputs=[ROOT/p for p in ['scripts/build_dossier.py','docs/design/CARDS.md','rfq/LAUNCH-PLAYBOOK.md','docs/AUDIT.md','rfq/README.md','rfq/manufacturing-notes.md','docs/design/README.md','docs/design/UX.md','docs/PERSONALIZATION.md','docs/design/ELECTRICAL.md','docs/VALIDATION.md','site/PRICING.md','content/starter/cards-preview.png','content/starter/cartridge-labels-preview.png','content/starter/cartridge-labels.json']]+[HARDWARE/n/'BOM.csv' for n in BOARDS]+sorted((DOCS/'images').glob('*.png'))
frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
def board_label(name):
 return {'card':'Galia Mini story card','mini':'Galia Mini','explore':'Galia Explore','card-reader':'Contact-ID reader','story-card':'Story cartridge'}.get(name,name)
def view_label(p):
 name=p.stem.replace('explore-cut-card-springs','explore-upper-assembly-section').replace('explore-cut-card-reader','explore-connector-plane-section')
 model,view=name.split('-',1)
 return board_label(model)+' · '+view.replace('-',' ')
flow=[]
def para(x,sty='BodyText'):
 x=re.sub(r'!\[[^]]*\]\([^)]*\)','',x);x=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',x)
 flow.append(Paragraph(escape(x.replace('**','').replace('`','')),styles[sty]))
def emit_table(lines):
 rows=[]
 for line in lines:
  cells=[x.strip() for x in line.strip().strip('|').split('|')]
  if all(re.fullmatch(r'[-: ]+',x) for x in cells):continue
  rows.append([Paragraph(escape(re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',x).replace('**','')),styles['Tiny']) for x in cells])
 if rows:
  t=Table(rows,colWidths=[519/len(rows[0])]*len(rows[0]),repeatRows=1)
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),'#d7e8e0'),('LINEBELOW',(0,0),(-1,-1),.25,'#d0d0d0'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));flow.append(t);flow.append(Spacer(1,8))

for name in ['docs/design/CARDS.md','rfq/LAUNCH-PLAYBOOK.md','docs/AUDIT.md','rfq/README.md' ,'rfq/manufacturing-notes.md','docs/design/README.md','docs/design/UX.md','docs/PERSONALIZATION.md','docs/design/ELECTRICAL.md','docs/VALIDATION.md','site/PRICING.md']:
 if flow:flow.append(PageBreak())
 text=(ROOT/name).read_text();block=[];table=[]
 for line in text.splitlines()+['']:
  if line=='>' or line.startswith('> '):line=line[1:].lstrip()
  if line.startswith('|'):
   if block:para(' '.join(block));block=[]
   table.append(line);continue
  if table:emit_table(table);table=[]
  if re.match(r'^(?:[0-9]+\. |[-] )',line):
   if block:para(' '.join(block));block=[]
   para(line);continue
  if line.startswith('#') or not line.strip():
   if block:para(' '.join(block));block=[]
   if line.startswith('#'):para(line.lstrip('# '),'Heading1' if line.startswith('# ') else 'Heading2')
  elif line.startswith('!['):continue
  else:block.append(line)
 flow.append(Spacer(1,8))
for name in BOARDS:
 flow.append(PageBreak());para(board_label(name)+' · exact reference BOM','Heading1');para('All prices are engineering allowances, not supplier quotes. Drawing-defined items require supplier approval. Full machine-readable links/queries are in hardware/'+name+'/BOM.csv.')
 rows=[[Paragraph(x,styles['Tiny']) for x in ['Ref / qty','Exact MPN','Footprint / basis','EUR each']]]
 for r in csv.DictReader((HARDWARE/name/'BOM.csv').open()):
  rows.append([Paragraph(escape(x),styles['Tiny']) for x in [r['reference']+' / '+str(r['quantity']),r['mpn'],r['footprint']+'; '+r['description'],r['unit_eur_low']+'–'+r['unit_eur_high']]])
 t=Table(rows,colWidths=[45,145,215,58],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),'#d7e8e0'),('LINEBELOW',(0,0),(-1,-1),.25,'#d0d0d0'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));flow.append(t)
images=sorted((DOCS/'images').glob('*.png'))
for p in images:
 flow.append(PageBreak());para(view_label(p),'Heading1');para('Actual current CAD geometry with nominal component envelopes. Colours aid reading; orange shows section faces. Physical validation pending. Harness routes are assumptions.');flow.append(Spacer(1,10));buffer=io.BytesIO();picture=RasterImage.open(p).convert('RGB');picture.save(buffer,format='JPEG',quality=90,subsampling=0);buffer.seek(0);w,h=picture.size;scale=min(465/w,600/h);flow.append(Image(buffer,width=w*scale,height=h*scale))
flow.append(PageBreak());para('Original bilingual listening collection','Heading1');para('Three original tales, six scripts and six card faces are supplied separately in content/starter. Printable cards and the read-aloud booklet are public preview assets. These are paper artwork, not electronic cartridges. Scripts and final recordings need separate approval; six downloadable local synthetic recordings and optional browser speech are demonstrations only.')
flow.append(Image(str(ROOT/'content/starter/cards-preview.png'),width=350,height=495))
spec=json.loads((ROOT/'content/starter/cartridge-labels.json').read_text())
def dimensions(values):return '×'.join(f'{value:g}' for value in values)
window=[spec['window_xy'][i+2]-spec['window_xy'][i] for i in (0,1)]
pocket=[spec['pocket_xy'][i+2]-spec['pocket_xy'][i] for i in (0,1)]
flow.append(PageBreak());para('Electronic cartridge picture inserts','Heading1')
para(f"Replaceable paper {dimensions(spec['label_size'])}mm, maximum {spec['maximum_paper_thickness']:g}mm thick, no adhesive. It fits behind a {dimensions(window)}mm clear window inside the {dimensions(pocket)}mm pocket. Paper inset from the window is {spec['label_inset_from_window_edge']:g}mm per edge; paper-to-pocket clearance is {spec['label_to_pocket_clearance_per_edge']:g}mm per edge. These pictures contain catalogue keys, not DS2401 ROM IDs. Adult screw access, physical fit, window retention and child suitability remain unvalidated.")
flow.append(Image(str(ROOT/'content/starter/cartridge-labels-preview.png'),width=350,height=495))

def foot(c,d):c.setFont('D',7);c.drawString(40,24,'Galia · RFQ engineering reference · physical validation pending');c.drawRightString(555,24,str(d.page))
SimpleDocTemplate(str(RFQ/'engineering-dossier.pdf'),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=35,bottomMargin=40,title='Galia current engineering RFQ dossier',author='Galia').build(flow,onFirstPage=foot,onLaterPages=foot)
# Browse all views without requiring a CAD viewer.
html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Current design views</title><style>body{font:18px system-ui;margin:2rem;background:#edf4f0;color:#193e36}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}img{width:100%;background:white}figure{margin:0}figcaption{padding:.5rem}</style><h1>Current Galia Mini / Galia Explore design views</h1><p><a href="bom.html">Search the exact component BOM</a></p><p>Engineering geometry and nominal envelopes. Physical validation pending; orange faces identify sections.</p><main>'
for p in images:html+='<figure><a href="images/'+p.name+'"><img loading="lazy" src="images/'+p.name+'" alt="'+view_label(p)+'"></a><figcaption>'+view_label(p)+'</figcaption></figure>'
(DOCS/'gallery.html').write_text(html+'</main>')
parts_html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Current exact component BOM</title><style>body{font:16px system-ui;margin:2rem;color:#163f38}label{display:block}input{font:inherit;padding:.8rem;width:min(32rem,85%)}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:.7rem;border-bottom:1px solid #ccd9d3;vertical-align:top}td{overflow-wrap:anywhere}main{overflow:auto}small{display:block;font-size:14px}</style><h1>Current exact component BOM</h1><p>Engineering allowances, not quotes. Drawing-defined parts and physical qualification remain pending. Copper/manual features are explicitly identified. <a href="gallery.html">CAD gallery</a></p><label for="filter">Find a component, reference or board</label><input id="filter" type="search" placeholder="DS2401, USB, Galia Mini…"><main><table><thead><tr><th>Board / ref / qty</th><th>Exact part</th><th>Basis and package</th><th>Reference EUR</th><th>Sources</th></tr></thead><tbody>'
for name in BOARDS:
 for r in csv.DictReader((HARDWARE/name/'BOM.csv').open()):
  source=r['source'] if r['source'].startswith('https://') else 'https://github.com/arno1190/open-conteuse/blob/main/'+r['source']
  parts_html+='<tr><td>'+html_escape(board_label(name)+' / '+r['reference']+' / '+r['quantity'])+'</td><td>'+html_escape(r['mpn'])+'</td><td>'+html_escape(r['description'])+'<small>'+html_escape(r['footprint']+' · '+r['basis'])+'</small></td><td>'+html_escape(r['unit_eur_low']+'–'+r['unit_eur_high'])+'</td><td><a href="'+html_escape(source,quote=True)+'">Source/drawing</a> · <a href="'+html_escape(r['search'],quote=True)+'">Find exact part</a></td></tr>'
parts_html+='</tbody></table></main><script>document.getElementById("filter").addEventListener("input",e=>{const q=e.target.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script></html>'
(DOCS/'bom.html').write_text(parts_html)
print('PDF, searchable BOM and gallery:',len(images),'views')

assert frozen=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'Dossier inputs changed during build'
outputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [RFQ/'engineering-dossier.pdf',DOCS/'gallery.html',DOCS/'bom.html']}
(RFQ/'dossier-receipt.json').write_text(json.dumps({'physical_validation':'pending','sources':frozen,'outputs':outputs},indent=2)+'\n')
