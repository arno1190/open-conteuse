"""Run the actual SD-export CLI and feed its record to the shared firmware decoder."""
import hashlib,json,subprocess,tempfile,sys
from pathlib import Path
from project import ROOT
sys.path.insert(0,str(ROOT))
from conteuse.studio import Studio
from conteuse.wifi import card_uid
# Valid DS2401 family/serial/CRC fixture, not a credential.
rom=bytearray([1,2,3,4,5,6,7,0]);crc=0
for byte in rom[:7]:
 for _ in range(8):
  mix=(crc^byte)&1;crc>>=1
  if mix:crc^=0x8c
  byte>>=1
rom[-1]=crc;uid=card_uid(rom.hex())
with tempfile.TemporaryDirectory() as directory:
 root=Path(directory);studio=Studio(root/'studio');source=ROOT/'examples/first-adventure'
 digest=studio.approve(source);studio.assign_card(uid,digest)
 subprocess.run([sys.executable,'-m','conteuse.tools','--root',str(root/'studio'),'export',str(source),str(root/'sd')],cwd=ROOT,check=True,capture_output=True)
 record=root/'sd/cards'/f'{uid}.0.json';value=json.loads(record.read_text());generation=str(value['generation']);expected=hashlib.sha256(f'{uid}:{digest}:{generation}'.encode()).hexdigest();assert value['sha256']==expected
 subprocess.run([str(ROOT/'work/admin-protocol-test'),str(record),uid,digest,generation,expected],check=True)
print('Actual SD export -> shared firmware mapping decoder passed.')
