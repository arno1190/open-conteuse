"""Quote-only manufacturing references, never a fabrication authorization."""
import csv,hashlib,json,os,subprocess
from pathlib import Path
from project import ROOT,HARDWARE,RFQ,BOARDS,WORK
out=RFQ/'manufacturing-reference';out.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,XDG_CONFIG_HOME=str(ROOT/'work/config'),XDG_CACHE_HOME=str(ROOT/'work/cache'),XDG_DATA_HOME=str(ROOT/'work/data'))
sources={}
def run(args):
 result=subprocess.run(['kicad-cli','pcb','export',*args],env=env,capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
for name in BOARDS:
 board=HARDWARE/name/(name+'.kicad_pcb');sources[str(board.relative_to(ROOT))]=hashlib.sha256(board.read_bytes()).hexdigest();dest=out/name;dest.mkdir(exist_ok=True)
 layers='F.Cu,'+('In1.Cu,In2.Cu,' if name in ['mini','explore'] else '')+'B.Cu,F.Paste,B.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts'
 run(['gerbers','--layers',layers,'-o',str(dest)+os.sep,str(board)])
 run(['drill','--format','excellon','--excellon-units','mm','--excellon-separate-th','--generate-map','--map-format','pdf','-o',str(dest)+os.sep,str(board)])
 temp=WORK/(name+'-positions.csv');run(['pos','--format','csv','--units','mm','--side','both','--exclude-dnp','-o',str(temp),str(board)])
 with temp.open() as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 # Copper test pads, mounting holes and drawing-defined solder/wear pads are not placed parts.
 assert fields[0]=='Ref',fields
 parts={r['ref']:r for r in json.loads((HARDWARE/name/'components.json').read_text())['parts']}
 rows=[r for r in rows if not r['Ref'].startswith(('TP','H')) and parts[r['Ref']]['mpn'] not in ['OC-WIRE-3','OC-ID-CONTACTS']]
 with (dest/'assembly-positions.csv').open('w',newline='') as f:w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
 for r in rows:assert r['Ref'] in parts
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in sources.items())
outputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
(RFQ/'manufacturing-receipt.json').write_text(json.dumps(dict(fabrication_release=False,purpose='quote_only_pending_DFM',sources=sources,outputs=outputs),indent=2)+'\n')
print('Quote-only Gerber/drill/placement references:',len(outputs),'files')
