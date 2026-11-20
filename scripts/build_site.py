"""Assemble the public static showcase plus complete engineering downloads."""
import shutil,subprocess,sys
from project import ROOT,DOCS,RFQ
subprocess.run([sys.executable,str(ROOT/'content/starter/validate.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'site/check.py')],check=True)
out=ROOT/'work/site-public'
if out.exists():shutil.rmtree(out)
shutil.copytree(ROOT/'site',out,ignore=shutil.ignore_patterns('.openai','__pycache__','check.py'))
(out/'design').mkdir()
shutil.copy2(DOCS/'gallery.html',out/'design/gallery.html')
shutil.copy2(DOCS/'bom.html',out/'design/bom.html')
shutil.copytree(DOCS/'images',out/'design/images')
for variant in ('mini','explore'):
 source=DOCS/'images'/(variant+'-hero-front.png');target=out/'assets'/(variant+'-current-cad.png')
 shutil.copy2(source,target)
 assert target.read_bytes()==source.read_bytes(), variant
(out/'downloads').mkdir()
for name in ['engineering-dossier.pdf','costs.json','rfq-launch-playbook.pdf','rfq-launch-playbook.html','LAUNCH-PLAYBOOK.md','quote-comparison.csv']:
 shutil.copy2(RFQ/name,out/'downloads'/name)
assert (out/'index.html').is_file() and (out/'design/gallery.html').is_file()
print('Static public artifact:',out)
