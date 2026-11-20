"""Assemble the public static showcase plus complete engineering downloads."""
import shutil
from project import ROOT,DOCS,RFQ
out=ROOT/'work/site-public'
if out.exists():shutil.rmtree(out)
shutil.copytree(ROOT/'site',out,ignore=shutil.ignore_patterns('.openai','__pycache__','check.py'))
(out/'design').mkdir()
shutil.copy2(DOCS/'gallery.html',out/'design/gallery.html')
shutil.copy2(DOCS/'bom.html',out/'design/bom.html')
shutil.copytree(DOCS/'images',out/'design/images')
(out/'downloads').mkdir()
for name in ['engineering-dossier.pdf','costs.json']:
 shutil.copy2(RFQ/name,out/'downloads'/name)
assert (out/'index.html').is_file() and (out/'design/gallery.html').is_file()
print('Static public artifact:',out)
