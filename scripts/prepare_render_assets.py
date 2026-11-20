"""Rasterize exact print-label artwork for CAD previews; source PDF stays canonical."""
import fitz
from project import ROOT,DOCS
out=DOCS/'textures';out.mkdir(parents=True,exist_ok=True)
pdf=fitz.open(ROOT/'content/starter/cartridge-labels.pdf');mm=72/25.4
names=['milo-moon-post','nori-cloud-pocket','pipo-sock-orchestra']
for i,name in enumerate(names):
 x=26+i*59;clip=fitz.Rect(x*mm,60.4*mm,(x+33.6)*mm,99*mm)
 pdf[0].get_pixmap(matrix=fitz.Matrix(8,8),clip=clip,alpha=False).save(out/(name+'.png'))
print('Prepared exact33.6×38.6mm label textures from current print PDF')
