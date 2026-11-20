#!/usr/bin/env python3
"""Rebuild original vector card art and reading PDFs; no external assets required.
Requires reportlab. Does not generate or approve audio.
"""
import json, math, textwrap, shutil, copy, sys, subprocess
from pathlib import Path
from reportlab.graphics.shapes import Drawing, Rect, Circle, Ellipse, Polygon, Line, String, Group, Path as GPath
from reportlab.graphics import renderSVG, renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from xml.sax.saxutils import escape
HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'index.json').read_text())
FONT=Path('/usr/share/fonts/truetype/dejavu')
for name,path in [('DTSans','DejaVuSans.ttf'),('DTBold','DejaVuSans-Bold.ttf'),('DTSerif','DejaVuSerif.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(FONT/path)))
INK='#183E3C';CREAM='#FFF9EE'
def rect(d,x,y,w,h,c,rx=0):d.add(Rect(x,y,w,h,fillColor=HexColor(c),strokeColor=None,rx=rx,ry=rx))
def circle(d,x,y,r,c):d.add(Circle(x,y,r,fillColor=HexColor(c),strokeColor=None))
def line(d,x1,y1,x2,y2,c=INK,w=5):d.add(Line(x1,y1,x2,y2,strokeColor=HexColor(c),strokeWidth=w,strokeLineCap=1))
def text(d,x,y,t,size=24,font='DTSans',color=INK,anchor='start'):d.add(String(x,y,t,fontName=font,fontSize=size,fillColor=HexColor(color),textAnchor=anchor))
def star(d,x,y,r,c):
 pts=[]
 for i in range(10):
  a=math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*.43;pts.extend([x+math.cos(a)*rr,y+math.sin(a)*rr])
 d.add(Polygon(pts,fillColor=HexColor(c),strokeColor=None))
def wrapped(d,t,y,size=27,width=340,font='DTBold',color=INK):
 words=t.split();rows=[];row=''
 for w in words:
  nxt=(row+' '+w).strip()
  if pdfmetrics.stringWidth(nxt,font,size)>width and row:rows.append(row);row=w
  else:row=nxt
 if row:rows.append(row)
 for row in rows:text(d,30,y,row,size,font,color);y-=size*1.18
 return y

def art(s,back=False):
 d=Drawing(400,600);rect(d,0,0,400,600,CREAM,24)
 if back:
  rect(d,0,490,400,110,s['color'],24);text(d,30,540,'À TOI D’IMAGINER',21,'DTBold');text(d,30,511,'YOUR LITTLE DETOUR',19)
  y=452
  for lang in ('fr','en'):
   text(d,30,y,lang.upper(),16,'DTBold');y-=32
   y=wrapped(d,s[lang]['card_activity'],y,25,340,'DTSans');y-=34
  text(d,30,47,'PAPIER / PAPER · CC0',16,'DTBold');text(d,30,24,'Ne déclenche pas le lecteur / Artwork only',13)
  return d
 rect(d,0,250,400,350,s['color'],24)
 text(d,30,563,'LES PETITS DÉTOURS',18,'DTBold')
 if s['id']=='milo-moon-post':
  circle(d,276,439,73,CREAM);circle(d,301,462,68,s['color'])
  for x,y,r in [(64,488,11),(323,334,9),(74,350,8)]:star(d,x,y,r,INK)
  rect(d,88,305,214,127,CREAM,12);line(d,93,421,194,351);line(d,194,351,297,421);line(d,94,309,152,357);line(d,296,309,239,357)
  circle(d,170,385,5,INK);circle(d,218,385,5,INK)
 elif s['id']=='nori-cloud-pocket':
  for x,y,r in [(118,417,48),(178,443,64),(244,425,58),(281,403,38)]:circle(d,x,y,r,CREAM)
  rect(d,112,368,173,56,CREAM,16);circle(d,166,413,5,INK);circle(d,217,413,5,INK)
  p=GPath(fillColor=HexColor(INK),strokeColor=None);p.moveTo(179,389);p.curveTo(188,375,202,375,211,389);p.lineTo(205,392);p.curveTo(198,384,190,384,185,392);p.closePath();d.add(p)
  line(d,95,325,295,325);line(d,121,302,271,302)
  star(d,76,477,12,INK);star(d,306,495,9,INK)
 else:
  # Three friendly socks, hand-drawn vector shapes; no borrowed characters.
  for x,y,col,kind in [(74,355,'#F6D978',0),(174,394,CREAM,1),(270,350,'#B9D7D2',2)]:
   rect(d,x,y,52,119,col,11);rect(d,x-20,y-20,72,49,col,18);line(d,x+4,y+96,x+48,y+96)
   circle(d,x+17,y+65,3.5,INK);circle(d,x+36,y+65,3.5,INK)
   if kind==0:
    for yy in [y+13,y+29,y+45]:line(d,x+3,yy,x+48,yy,INK,3)
   elif kind==1:
    for xx,yy in [(12,18),(34,34),(15,42)]:circle(d,x+xx,y+yy,4,'#E99B82')
   else:d.add(Ellipse(x+20,y+5,8,5,fillColor=HexColor(INK),strokeColor=None))
  for x,y in [(61,490),(318,477)]:
   line(d,x,y-27,x,y+10);circle(d,x-8,y-27,9,INK);line(d,x,y+10,x+17,y+4)
 y=215
 y=wrapped(d,s['fr']['title'],y,28,340,'DTBold');y-=9
 wrapped(d,s['en']['title'],y,23,340,'DTSans')
 text(d,30,25,'4–7 · ~4 min · FR / EN',16,'DTBold')
 return d

cards=HERE/'cards';cards.mkdir(exist_ok=True)
if '--labels-only' not in sys.argv:
 for s in DATA['stories']:
  for back in (False,True):
   path=cards/(s['id']+('-back' if back else '')+'.svg')
   renderSVG.drawToFile(art(s,back),str(path))
   svg=path.read_text().replace('font-family: DTBold;', 'font-family: DejaVu Sans, Arial, sans-serif; font-weight: bold;').replace('font-family: DTSans;', 'font-family: DejaVu Sans, Arial, sans-serif;')
   svg=svg.replace('<title>...</title>', '<title>'+escape(s['fr']['title']+' / '+s['en']['title'])+'</title>').replace('<desc>...</desc>', '<desc>Original printable paper artwork. Does not activate the electronic reader.</desc>')
   path.write_text(svg)
 # Three fronts then three backs, deliberately single-sided cut-and-pair, not uncalibrated duplex.
 c=canvas.Canvas(str(HERE/'cards.pdf'),pagesize=A4);c.setTitle('Les petits détours — cartes papier / printable paper cards')
 w,h=A4
 c.setFillColor(HexColor(INK));c.setFont('DTBold',19);c.drawString(20*mm,h-22*mm,'Des histoires à tenir dans la main')
 c.setFont('DTSans',10);c.drawString(20*mm,h-30*mm,'Original paper artwork · 3 fronts + 3 activity backs · CC0-1.0')
 c.drawString(20*mm,h-37*mm,'Print at 100% / taille réelle. Each card is 40 × 60 mm.')
 for row,back in enumerate((False,True)):
  y=h-(111+row*83)*mm
  for i,s in enumerate(DATA['stories']):
   x=(27+i*58)*mm;c.saveState();c.translate(x,y);c.scale(.1*mm,.1*mm);renderPDF.draw(art(s,back),c,0,0);c.restoreState()
   c.setStrokeColor(HexColor('#758780'));c.setLineWidth(.3)
   for xx in [x,x+40*mm]:
    for yy in [y,y+60*mm]:
     c.line(xx-2*mm,yy,xx-0.5*mm,yy);c.line(xx,yy-2*mm,xx,yy-.5*mm)
   c.setFont('DTSans',8);c.drawString(x,y-5*mm,('FRONT / RECTO ' if not back else 'BACK / VERSO ')+str(i+1))
 c.setFont('DTBold',10);c.drawString(20*mm,57*mm,'For an adult to prepare / Préparation par un adulte')
 for j,t in enumerate(['Cut the six pieces and pair each front with its activity back. No duplex alignment assumed.',
 'Cartes papier uniquement : aucun identifiant électronique, aucun déclenchement du lecteur.',
 'Paper cards do not activate the contact-ID reader. These are not electronic cartridges.',
 'Check the printed ruler below: 40 mm. Stories and audio approval remain pending.']):
  c.setFont('DTSans',8);c.drawString(20*mm,(50-j*5)*mm,t)
 c.line(20*mm,22*mm,60*mm,22*mm);c.line(20*mm,20*mm,20*mm,24*mm);c.line(60*mm,20*mm,60*mm,24*mm);c.setFont('DTSans',8);c.drawString(65*mm,21*mm,'40 mm — check after printing / vérifier après impression')
 c.showPage();c.save()
 styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyDT',fontName='DTSans',fontSize=10.5,leading=14.5,spaceAfter=6,textColor=HexColor(INK)));styles.add(ParagraphStyle(name='HeadDT',fontName='DTSerif',fontSize=26,leading=30,spaceAfter=15,textColor=HexColor(INK)));styles.add(ParagraphStyle(name='SmallDT',fontName='DTSans',fontSize=9,leading=13,spaceAfter=9,textColor=HexColor(INK)))
 flow=[Paragraph('Les petits détours<br/>Little Detours',styles['HeadDT']),Paragraph('Trois histoires originales et leurs activités, en français et en anglais.<br/>Three original stories and activities, in French and English.',styles['BodyDT']),Paragraph('Collection de démonstration · Editorial draft · 20 November 2026 · CC0-1.0',styles['SmallDT']),Paragraph('Intended ages 4–7 are editorial guidance for an adult to assess, not a tested age rating. These gentle fictional stories have not been tested with children. A child can simply listen; speaking and moving are always optional.',styles['BodyDT']),Paragraph('Read aloud at an unhurried pace. Leave about two seconds between paragraphs and eight seconds after an invitation to imagine or listen. No music or effects are needed. An adult prepares the paper cards. The paper cards do not trigger the electronic player.',styles['BodyDT']),Paragraph('Script approval: pending. Final audio approval: pending. This collection contains no final audio. The website’s optional browser voice is a synthetic demonstration and varies by device. Review scripts first and review the exact final recording separately before activating it in a child’s library.',styles['BodyDT']),PageBreak()]
 for s in DATA['stories']:
  for lang in ['fr','en']:
   z=s[lang];flow.extend([Paragraph(escape(z['title']),styles['HeadDT']),Paragraph(escape(z['subtitle']),styles['BodyDT']),Paragraph(f"{lang.upper()} · {z['word_count']} words / mots · ~4 min estimate · draft / brouillon",styles['SmallDT'])])
   flow.extend(Paragraph(escape(p),styles['BodyDT']) for p in z['script'].split('\n\n'))
   flow.extend([Spacer(1,10),Paragraph('Loin de l’écran / Away from the screen',styles['BodyDT']),Paragraph(escape(z['activity']),styles['BodyDT']),PageBreak()])
 SimpleDocTemplate(str(HERE/'collection.pdf'),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm,title='Les petits détours / Little Detours — original bilingual stories',author='Open Conteuse').build(flow)

# Separate adhesive labels for the actual electronic cartridge artwork recess.
# Canonical recess x3..37, y4..43 =34x39mm. Centered label x3.2..36.8,
# y4.2..42.8 =33.6x38.6mm, leaving0.2mm nominal edge clearance.
LABEL_MM=(33.6,38.6)
short={'milo-moon-post':('MILO','Le courrier de la Lune','The Moon Post','MILO-01'),
       'nori-cloud-pocket':('NORI','Le nuage de poche','The Pocket Cloud','NORI-02'),
       'pipo-sock-orchestra':('PIPO','L’orchestre des chaussettes','The Sock Orchestra','PIPO-03')}
def cartridge_label(story):
 d=Drawing(336,386);rect(d,0,0,336,386,story['color'],13)
 # Reuse only our original illustration geometry, not the paper-card text.
 icon=Group()
 for shape in art(story).contents[3:]:
  if not isinstance(shape,String):icon.add(copy.deepcopy(shape))
 icon.scale(.56,.56);icon.translate(100,-6);d.add(icon)
 # Visible handle header: label top1.2..14.0mm => cartridgeY5.4..18.2mm.
 # Inserted cartridge exposesY0..20mm. Icon+name remain inside that band.
 rect(d,12,246,312,128,CREAM,11)
 rect(d,22,259,103,103,story['color'],12)
 badge=Group()
 for shape in art(story).contents[3:]:
  if not isinstance(shape,String):badge.add(copy.deepcopy(shape))
 badge.scale(.34,.34);badge.translate(15,494);d.add(badge)
 name,fr,en,key=short[story['id']]
 text(d,139,302,name,42,'DTBold')
 text(d,140,276,'PETITS DÉTOURS',13,'DTBold')
 rect(d,12,12,312,120,CREAM,10)
 y=wrapped(d,fr,105,21,280,'DTBold');y-=5
 y=wrapped(d,en,y,19,280,'DTSans')
 text(d,27,25,key+' · CC0',14,'DTBold')
 return d
labels=HERE/'cartridge-labels';labels.mkdir(exist_ok=True)
for st in DATA['stories']:
 f=labels/(st['id']+'.svg');renderSVG.drawToFile(cartridge_label(st),str(f))
 svg=f.read_text().replace('font-family: DTBold;','font-family: DejaVu Sans, Arial, sans-serif; font-weight: bold;').replace('font-family: DTSans;','font-family: DejaVu Sans, Arial, sans-serif;')
 svg=svg.replace('<title>...</title>','<title>'+escape(st['fr']['title']+' — electronic cartridge artwork label')+'</title>').replace('<desc>...</desc>','<desc>33.6 x 38.6 mm paper artwork label. No electronic ROM identifier is supplied.</desc>')
 f.write_text(svg)
w,h=A4
c=canvas.Canvas(str(HERE/'cartridge-labels.pdf'),pagesize=A4)
c.setTitle('Cartridge artwork labels — 33.6 x 38.6 mm — engineering draft')
c.setFillColor(HexColor(INK));c.setFont('DTBold',18);c.drawString(20*mm,h-22*mm,'Une histoire, une cartouche')
c.setFont('DTSans',11);c.drawString(20*mm,h-31*mm,'Artwork labels for contact-ID cartridges / Étiquettes illustrées')
c.setFont('DTBold',10);c.drawString(20*mm,h-43*mm,'PRINT AT 100% / IMPRIMER À 100% · each label 33.6 × 38.6 mm')
for i,st in enumerate(DATA['stories']):
 x=(26+i*59)*mm;y=h-99*mm
 c.saveState();c.translate(x,y);c.scale(.1*mm,.1*mm);renderPDF.draw(cartridge_label(st),c,0,0);c.restoreState()
 c.setStrokeColor(HexColor('#758780'));c.setLineWidth(.3)
 for xx in [x,x+33.6*mm]:
  for yy in [y,y+38.6*mm]:
   c.line(xx-2*mm,yy,xx-.5*mm,yy);c.line(xx,yy-2*mm,xx,yy-.5*mm)
 c.setFont('DTSans',8);c.drawString(x,y-6*mm,short[st['id']][3]+' · artwork key only')
notes=[
 ('Dimensions / Dimensions','Label: 33.6 × 38.6 mm. Recess: 34 × 39 mm, canonical X3–37, Y4–43 mm.'),
 ('Nominal placement / Position nominale','Centered label: X3.2–36.8, Y4.2–42.8 mm; 0.2 mm nominal clearance per edge.'),
 ('Visible handle / Poignée visible','Icon + name occupy label top 1.2–14.0 mm, inside the nominal exposed cartridge Y0–20 mm.'),
 ('Material assumption / Hypothèse matière','Paper + adhesive total thickness ≤0.15 mm. Adhesion, wear and actual fit remain unvalidated.'),
 ('Preparation / Préparation','Adult preparation. Check printed ruler, cut around each label, fit without obstructing the contact area.'),
 ('Artwork is not electronics / Illustration uniquement','No DS2401 ROM is supplied. Printing a label does not create or activate an electronic cartridge.'),
 ('Use / Utilisation','Requires an assembled DS2401 cartridge and a parent-created local assignment to approved audio.'),
 ('Editorial status / Statut éditorial','Original fiction and art: CC0. Script approval pending. Final audio approval pending.'),
]
y=h-121*mm
for heading,body in notes:
 c.setFont('DTBold',10);c.drawString(20*mm,y,heading);y-=6*mm
 c.setFont('DTSans',8.5)
 for row in textwrap.wrap(body,105):c.drawString(20*mm,y,row);y-=4.5*mm
 y-=5*mm
c.setStrokeColor(HexColor(INK));c.line(20*mm,23*mm,60*mm,23*mm)
for xx in [20,60]:c.line(xx*mm,21*mm,xx*mm,25*mm)
c.setFont('DTSans',9);c.drawString(65*mm,22*mm,'40 mm — verify printed scale / vérifier l’échelle imprimée')
c.showPage();c.save()
label_spec={'status':'engineering_draft','units':'mm','label_size':[33.6,38.6],
 'recess_xy':[3,4,37,43],'label_xy':[3.2,4.2,36.8,42.8],'nominal_edge_clearance':.2,
 'maximum_total_paper_adhesive_thickness':.15,'physical_validation':'pending',
 'inserted_cartridge_exposed_y':[0,20],
 'label_visible_height_when_inserted':15.8,
 'recognition_header_label_top_y':[1.2,14.0],
 'recognition_header_cartridge_y':[5.4,18.2],
 'recognition_header_contents':['distinct character icon','MILO / NORI / PIPO short name'],
 'recognition_header_assumption':'Label top maps to handleward canonical Y4.2; nominal inserted exposure ends at cartridge Y20. Physical placement, occlusion and readability remain pending.',
 'electronic_rom_supplied':False,'requires':'assembled DS2401 cartridge and parent-created local assignment',
 'artwork_keys':{st['id']:short[st['id']][3] for st in DATA['stories']}}
(HERE/'cartridge-labels.json').write_text(json.dumps(label_spec,ensure_ascii=False,indent=2)+'\n')

public=HERE.parents[1]/'site/content';public.mkdir(parents=True,exist_ok=True)
if '--labels-only' not in sys.argv:
 shutil.copyfile(HERE/'index.json',public/'index.json')
 for f in ['cards.pdf','collection.pdf']:shutil.copyfile(HERE/f,public/f)
 shutil.copytree(cards,public/'cards',dirs_exist_ok=True)
for f in ['cartridge-labels.pdf','cartridge-labels.json']:shutil.copyfile(HERE/f,public/f)
shutil.copytree(labels,public/'cartridge-labels',dirs_exist_ok=True)
if shutil.which('pdftoppm'):
 subprocess.run(['pdftoppm','-scale-to','1300','-png','-singlefile',str(HERE/'cartridge-labels.pdf'),str(HERE/'cartridge-labels-preview')],check=True)
 shutil.copyfile(HERE/'cartridge-labels-preview.png',public/'cartridge-labels-preview.png')
print('Generated cartridge labels and public mirror.' if '--labels-only' in sys.argv else 'Generated cards, booklet, cartridge labels and public mirror.')
