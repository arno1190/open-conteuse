"""Cross-check current release identities, receipts and physical-release boundary."""
import csv,hashlib,json
from pathlib import Path
from project import ROOT,HARDWARE,BOARDS,ENCLOSURE,DOCS
for name in BOARDS:
 data=json.loads((HARDWARE/name/'components.json').read_text())
 bom=list(csv.DictReader((HARDWARE/name/'BOM.csv').open()));refs={r['reference']:r['mpn'] for r in bom}
 for row in data['parts']:
  if not row['ref'].startswith('H'):assert refs.get(row['ref'])==row['mpn'],(name,row['ref'])
 assert all(r['source'] and r['search'] for r in bom)
 for kind in ['erc','drc']:
  report=(HARDWARE/name/'checks'/(kind+'.rpt')).read_text()
  assert ('ERC messages: 0' in report if kind=='erc' else 'Found 0 DRC violations' in report and 'Found 0 unconnected pads' in report and 'Found 0 Footprint errors' in report)
for name in ['mini','explore']:
 receipt=json.loads((DOCS/(name+'-render-receipt.json')).read_text())
 assert receipt['physical_validation']=='pending'
 for fn,sha in receipt['prepared_meshes'].items():
  if (ROOT/fn).exists():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn
 for mapping in ['sources','images']:
  for fn,sha in receipt[mapping].items():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn
mesh=json.loads((ENCLOSURE/'mesh-checks.json').read_text())
assert mesh['physical_validation']=='pending'
for fn,sha in mesh['sources'].items():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn
for fn,entry in mesh['exports'].items():
 if not fn.startswith('work/'):assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==entry['sha256'],fn
for v in ['mini','explore']:
 assert mesh['exports'][f'work/current/{v}-internal_interference.stl']['empty']
assert mesh['exports']['work/current/card_sweep_interference.stl']['empty']
assert mesh['exports']['work/current/wrong_card_interference.stl']['volume_cm3']>0

pdf=json.loads((ROOT/'rfq/dossier-receipt.json').read_text())
for fn,sha in {**pdf['sources'],**pdf['outputs']}.items():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn

manifest=json.loads((ROOT/'rfq/manifest.json').read_text())
assert manifest['physical_validation']=='pending' and not manifest['fabrication_release']
for fn,sha in manifest['files'].items():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn

manufacturing=json.loads((ROOT/'rfq/manufacturing-receipt.json').read_text())
assert not manufacturing['fabrication_release']
for fn,sha in {**manufacturing['sources'],**manufacturing['outputs']}.items():assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==sha,fn

print('Current BOM/native checks, CAD/image/PDF/manufacturing receipts and RFQ manifest verified.')
