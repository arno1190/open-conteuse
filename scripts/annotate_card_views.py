"""Add a numbered legend to dedicated CAD views; no geometry is painted in."""
import json
from PIL import Image,ImageDraw,ImageFont
from project import ROOT
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title=ImageFont.truetype(font,34);body=ImageFont.truetype(font,23);number=ImageFont.truetype(font,22)
legend=['1  Front retaining frame · aperture 32 × 37 mm','2  Clear PETG window · 34 × 39 × 0.50 mm','3  Replaceable paper picture · 33.6 × 38.6 × ≤0.15 mm','4  ID PCB + DS2401P+ · two underside hard-gold contacts','5  Rear shell + picture support + PCB locating pegs','6  Two M1.6 × 3 screws · adult opening only']
for path,pins in json.loads((ROOT/'work/current/card-view-pins.json').read_text()).items():
 source=Image.open(ROOT/path).convert('RGB');out=Image.new('RGB',(1200,1530),'#f6f8f4');out.paste(source,(0,70));draw=ImageDraw.Draw(out)
 view=path.rsplit('-',1)[1].split('.')[0];draw.text((35,18),'Galia Mini · story card · '+view,font=title,fill='#183c35')
 for n,x,y in pins:
  y+=70;draw.ellipse((x-17,y-17,x+17,y+17),fill='#fff7e6',outline='#18483d',width=2);draw.text((x,y),str(n),anchor='mm',font=number,fill='#183c35')
 for i,line in enumerate(legend):draw.text((35,1280+i*32),line,font=body,fill='#183c35')
 draw.text((35,1480),'Nominal CAD / proposed finish · physical fit and retention pending',font=body,fill='#46655b');out.save(ROOT/path)
