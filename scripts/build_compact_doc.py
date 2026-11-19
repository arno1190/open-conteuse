#!/usr/bin/env python3
"""Assemble the complete compact dossier, searchable gallery and contact sheets."""
import json,csv,re,html,math,hashlib,posixpath
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image as RLImage,Table,TableStyle,PageBreak,KeepTogether,Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from compact_design import ROOT,OUT
D=ROOT/'docs/compact-r1';I=D/'images'

def pdf_image(path,width,height):
 path=Path(path);cache=ROOT/'work/compact-r1/pdf-images';cache.mkdir(parents=True,exist_ok=True);jpg=cache/(path.stem+'-'+hashlib.sha256(path.read_bytes()).hexdigest()[:12]+'.jpg')
 if not jpg.exists():Image.open(path).convert('RGB').save(jpg,quality=94,subsampling=0,optimize=True)
 return RLImage(str(jpg),width=width,height=height)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',FONT));pdfmetrics.registerFont(TTFont('DV-B',BOLD));pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-B',italic='DV',boldItalic='DV-B')
style=getSampleStyleSheet()
style.add(ParagraphStyle(name='Body',fontName='DV',fontSize=9,leading=13,spaceAfter=7,textColor=colors.HexColor('#214448')))
style.add(ParagraphStyle(name='SmallDV',parent=style['Body'],fontSize=7.3,leading=10))
for h,size in [('Title',25),('Heading1',18),('Heading2',13),('Heading3',10.5)]:style[h].fontName='DV-B';style[h].fontSize=size;style[h].leading=size*1.25;style[h].textColor=colors.HexColor('#174e56')
def text(s):
 s=html.escape(s);s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'<font face="DV-B">\1</font>',s);s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link color="#146b84" href="'+(m[2] if m[2].startswith('https://') else 'https://github.com/arno1190/open-conteuse/blob/main/'+posixpath.normpath('docs/compact-r1/'+m[2]))+'">'+m[1]+'</link>',s);return s
story=[]
def para(s,sty='Body'):return Paragraph(text(s),style[sty])
def table(rows,widths=None,small=False):
 data=[[para(str(x),'SmallDV' if small else 'Body') for x in row] for row in rows];t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfede7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#688a86')),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#d5e1dc')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
views=[('hero-front','Front perspective'),('hero-rear','Rear perspective'),('front','Front orthographic'),('rear','Rear orthographic'),('left','Left / power switch'),('right','Right / microSD'),('top','Top edge'),('bottom','Bottom / USB and headphones'),('open-front','Front shell omitted'),('open-rear','Back shell omitted'),('exploded','Exploded layers'),('pcb-front','Native PCB / top'),('pcb-rear','Native PCB / underside'),('battery-service','Pouch and lead service routes'),('cut-x-centre','X≥32.5mm longitudinal section'),('cut-x-jack','X≥29mm jack section'),('cut-y-antenna','Y≥24mm antenna/display section'),('cut-y-controls','Key row: Mini Y≥60 / Explore Y≥65'),('cut-z-battery','Z≤8.5mm battery layer'),('cut-z-front','Z≤18mm front layer')]
inputs=[*[D/name for name in ['README.md','DIMENSIONS.md','ELECTRICAL.md','COST.md','ASSEMBLY.md','VALIDATION.md']],*[I/f'{v}-{name}.png' for v in ['mini','explore'] for name,title in views],*[OUT/(v+'-BOM.csv') for v in ['mini','explore']],OUT/'costs.json',ROOT/'scripts/build_compact_doc.py']
frozen={str(p.relative_to(ROOT)):sha(p) for p in inputs}
# All images remain independently downloadable; sheets are an index, not replacements.
font=ImageFont.truetype(FONT,18);bold=ImageFont.truetype(BOLD,28)
for v in ['mini','explore']:
 sheet=Image.new('RGB',(1500,1430),'#f3f8f5');draw=ImageDraw.Draw(sheet);draw.text((25,18),f'{v.title()} compact R1 — all 20 views',font=bold,fill='#174e56')
 for k,(name,title) in enumerate(views):
  image=Image.open(I/f'{v}-{name}.png').convert('RGB');image.thumbnail((285,285));x=12+(k%5)*299;y=75+(k//5)*335;sheet.paste(image,(x,y));draw.text((x+4,y+287),title[:29],font=font,fill='#214448')
 sheet.save(D/f'{v}-contact-sheet.png')
# Side-by-side integration preview for conversation and quick review.
preview=Image.new('RGB',(1600,940),'#f3f8f5');dr=ImageDraw.Draw(preview)
for k,v in enumerate(['mini','explore']):
 im=Image.open(I/f'{v}-open-front.png').convert('RGB');im.thumbnail((790,790));preview.paste(im,(k*800,70));dr.text((k*800+30,20),f'{v.title()} — '+('65×95×22mm' if v=='mini' else '67×100×24mm'),font=bold,fill='#174e56')
dr.text((30,880),'Nominal digital prototype • component bodies and wire routes require physical validation',font=font,fill='#214448');preview.save(D/'integration-comparison.png')
# Local interactive gallery, no server or remote scripts required.
items=[dict(variant=v,name=name,title=title,path=f'images/{v}-{name}.png') for v in ['mini','explore'] for name,title in views]
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Compact R1 design gallery</title><style>body{font:16px system-ui;color:#173f44;background:#f3f8f5;margin:24px}header{max-width:1200px;margin:auto}button,select{font:inherit;padding:8px;margin:5px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}figure{background:white;margin:0;padding:12px;border-radius:12px}img{width:100%}figcaption{font-weight:600}small{display:block;font-weight:400}a{color:#146b84}</style><header><h1>Compact R1 — Mini / Explore</h1><p>40 source-derived views, 12 sections. Case dimensions exclude 0.6 mm key protrusion. Nominal component envelopes and illustrative wire routes; physical validation pending. No fabrication release.</p><p><a href="Compact-R1-dossier.pdf">Combined dossier PDF</a> · <a href="BOM.html">Search all BOM components</a> · <a href="README.md">Source guide</a></p><label>Variant <select id="v"><option value="">Both</option><option>mini</option><option>explore</option></select></label><label>View <select id="mode"><option value="">All</option><option value="cut-">Sections</option><option value="pcb-">PCB</option><option value="exploded">Exploded</option><option value="open-">Open housing</option></select></label></header><main id="gallery"></main><script>const data=DATA;function render(){const v=document.getElementById('v').value,m=document.getElementById('mode').value;document.getElementById('gallery').innerHTML=data.filter(x=>(!v||x.variant===v)&&(!m||x.name.includes(m))).map(x=>`<figure><a href="${x.path}"><img loading="lazy" src="${x.path}" alt="${x.variant}: ${x.title}"></a><figcaption>${x.variant} — ${x.title}<small>Native CAD / nominal envelopes; click full PNG</small></figcaption></figure>`).join('')}document.querySelectorAll('select').forEach(x=>x.addEventListener('change',render));render();</script></html>'''.replace('DATA',json.dumps(items));(D/'gallery.html').write_text(page)
story += [para('Open Conteuse','Title'),para('Compact custom hardware R1','Heading1'),para('Two integrated digital prototypes • 19 November 2026'),pdf_image(str(D/'integration-comparison.png'),width=515,height=303),para('Mini 65×95×22 mm • Explore 67×100×24 mm. Body dimensions; captive keys add 0.6 mm depth. Physical validation pending. No purchases or fabrication orders.'),para('Use the local gallery for full-resolution PNGs, the searchable BOM for every component/query, and the native KiCad/OpenSCAD files for engineering inspection. This PDF brings the design, cost assumptions and assembly procedure together.'),PageBreak()]
# Markdown prose/tables, keeping the repository guide as the canonical readable source.
def markdown(path):
 lines=path.read_text().splitlines();paragraph=[];i=0
 def flush():
  if paragraph:story.append(para(' '.join(paragraph)));paragraph.clear()
 while i<len(lines):
  line=lines[i]
  if line.startswith('```'):
   flush();i+=1;code=[]
   while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
   story.extend([Preformatted('\n'.join(code),style['Code']),Spacer(1,8)]);i+=1;continue
  if line.startswith('!['):flush();i+=1;continue
  if line.startswith('|'):
   flush();rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    row=[x.strip() for x in lines[i].strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',x.replace(' ','')) for x in row):rows.append(row)
    i+=1
   if rows:story.extend([table(rows,[515/len(rows[0])]*len(rows[0]),True),Spacer(1,10)])
   continue
  if not line.strip():flush()
  elif line.startswith('#'):
   flush();level=len(line)-len(line.lstrip('#'));story.append(para(line.lstrip('# '),'Heading1' if level==1 else 'Heading2' if level==2 else 'Heading3'))
  elif re.match(r'^(\d+\.|-) ',line):flush();story.append(para(line))
  else:paragraph.append(line)
  i+=1
 flush()
for name in ['README.md','DIMENSIONS.md','ELECTRICAL.md','COST.md','ASSEMBLY.md','VALIDATION.md']:
 markdown(D/name);story.append(PageBreak())
for v in ['mini','explore']:
 story.append(para(v.title()+' — complete view atlas','Heading1'));story.append(para('Orange faces are section cuts; captions identify the retained canonical side. Y is measured downward from the top in the native front view. Bodies use nominal dimensions; all physical fit, cable bends, sound, power and RF results remain pending.'))
 for start in range(0,len(views),4):
  cells=[]
  for name,title in views[start:start+4]:cells.append([pdf_image(str(I/f'{v}-{name}.png'),width=245,height=245),para(title,'SmallDV')])
  grid=[]
  for j in range(0,len(cells),2):grid.append([cells[j],cells[j+1] if j+1<len(cells) else ''])
  t=Table(grid,colWidths=[257,257]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),12)]));story.extend([t,PageBreak()])
for v in ['mini','explore']:
 story.append(para(v.title()+' — complete bill of materials','Heading1'));story.append(para('Per-reference engineering allowances, not quotes. All supplier queries and reference links are in the searchable HTML/CSV. Cut/standard items remain explicitly identified by their drawing or specification.','SmallDV'))
 rows=[['Ref','Exact candidate / specification','Function','Qty','EUR / unit']]
 with (OUT/(v+'-BOM.csv')).open() as f:
  for r in csv.DictReader(f):rows.append([r['reference'],'['+r['mpn']+']('+r['search']+')',r['description'],r['quantity'],r['unit_eur_low']+'–'+r['unit_eur_high']])
 story.extend([table(rows,[40,150,240,25,60],True),PageBreak()])
def footer(c,doc):
 c.setFont('DV',7);c.setFillColor(colors.HexColor('#53716f'));c.drawString(36,23,'OPEN CONTEUSE / COMPACT R1 — NOMINAL ENGINEERING PROTOTYPE / PHYSICAL VALIDATION PENDING');c.drawRightString(559,23,str(doc.page))
class Dossier(SimpleDocTemplate):
 def afterFlowable(self,flowable):
  if isinstance(flowable,Paragraph) and flowable.style.name in ['Heading1','Heading2']:
   self._outline_count=getattr(self,'_outline_count',0)+1;key='section-'+str(self._outline_count);self.canv.bookmarkPage(key);self.canv.addOutlineEntry(flowable.getPlainText(),key,level=0 if flowable.style.name=='Heading1' else 1,closed=False)
Dossier(str(D/'Compact-R1-dossier.pdf'),pagesize=(595.28,841.89),rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40,title='Open Conteuse compact R1 — complete engineering prototype dossier',author='Open Conteuse').build(story,onFirstPage=footer,onLaterPages=footer)
print('Built 40-view gallery, 2 contact sheets, comparison PNG and combined dossier PDF')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

outputs=[D/'Compact-R1-dossier.pdf',D/'gallery.html',D/'integration-comparison.png',*[D/(v+'-contact-sheet.png') for v in ['mini','explore']]]
assert frozen=={str(p.relative_to(ROOT)):sha(p) for p in inputs},'document inputs changed during build'
(D/'document-receipt.json').write_text(json.dumps({'physical_validation':'pending','sources':{str(p.relative_to(ROOT)):sha(p) for p in inputs},'outputs':{str(p.relative_to(ROOT)):sha(p) for p in outputs}},indent=2)+'\n')
