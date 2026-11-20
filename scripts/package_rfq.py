"""Package current engineering sources only; never workspace/private studio data."""
import hashlib,json,zipfile,subprocess
from project import ROOT,RFQ
visible=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0'))
include=['.github/workflows','hardware','enclosure','docs/design','rfq','firmware','content/starter','site','schemas','examples','conteuse','scripts','tests']
files=[ROOT/p for p in ['README.md','LICENSE','AGENTS.md','docs/REQUIREMENTS.md','docs/ARCHITECTURE.md','docs/VALIDATION.md','docs/ROADMAP.md','docs/CONTENT.md','docs/PERSONALIZATION.md']]
for prefix in include:
 for p in (ROOT/prefix).rglob('*'):
  if str(p.relative_to(ROOT)) not in visible:continue
  if not p.is_file() or any(q in p.parts for q in ['.pio','__pycache__','.openai']):continue
  if p.suffix in ['.zip','.pyc','.log','.lck'] or p.name=='manifest.json' and p.parent==RFQ:continue
  files.append(p)
files=sorted(set(files))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(RFQ/'manifest.json').write_text(json.dumps(dict(physical_validation='pending',fabrication_release=False,files=manifest),indent=2)+'\n')
out=RFQ/'open-conteuse-rfq.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[RFQ/'manifest.json']:z.write(p,str(p.relative_to(ROOT)))
print(out,len(files),'files',out.stat().st_size,'bytes')
