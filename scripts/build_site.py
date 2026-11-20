"""Assemble the public static showcase plus complete engineering downloads."""
import shutil,subprocess,sys
from project import ROOT,DOCS,RFQ
subprocess.run([sys.executable,str(ROOT/'content/starter/validate.py')],check=True)
out=ROOT/'work/site-public'
if out.exists():shutil.rmtree(out)
shutil.copytree(ROOT/'site',out,ignore=shutil.ignore_patterns('.openai','__pycache__','check.py'))
(out/'design').mkdir()
shutil.copy2(DOCS/'gallery.html',out/'design/gallery.html')
shutil.copy2(DOCS/'bom.html',out/'design/bom.html')
shutil.copytree(DOCS/'images',out/'design/images')
for variant in ('mini','explore'):
 shutil.copy2(DOCS/'images'/(variant+'-hero-front.png'),out/'assets'/(variant+'-current-cad.png'))
(out/'downloads').mkdir()
for name in ['engineering-dossier.pdf','costs.json','rfq-launch-playbook.pdf','rfq-launch-playbook.html','LAUNCH-PLAYBOOK.md','quote-comparison.csv']:
 shutil.copy2(RFQ/name,out/'downloads'/name)
assert (out/'index.html').is_file() and (out/'design/gallery.html').is_file()
print('Static public artifact:',out)
