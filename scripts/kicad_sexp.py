"""Small read-only S-expression reader for installed KiCad symbol contracts."""
import re

def parse(s):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[];root=[];cur=root
 for t in tokens:
  if t=='(':
   new=[];cur.append(new);stack.append(cur);cur=new
  elif t==')':cur=stack.pop()
  else:cur.append(t[1:-1].replace('\\"','"') if t.startswith('"') else t)
 return root[0]
def children(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def child(n,k):return next(iter(children(n,k)),None)
def symbol(file,name):
 tree=parse(file.read_text());s=next(x for x in children(tree,'symbol') if x[1]==name)
 e=child(s,'extends')
 if e:s=[*symbol(file,e[1]),*s[2:]]
 return s

def pins(s):
 out={}
 for unit in children(s,'symbol'):
  for p in children(unit,'pin'):
   out[child(p,'number')[1]]=(child(p,'name')[1],p[1])
 return out
if __name__=='__main__':
 from pathlib import Path
 for lib,name in [('Audio','MAX98357A'),('Battery_Management','BQ24074RGT'),('RF_Module','ESP32-S3-WROOM-1'),('Interface_Expansion','TCA9534PW')]:
  try:print(name,pins(symbol(Path('/usr/share/kicad/symbols')/(lib+'.kicad_sym'),name)))
  except Exception as e:print(name,e)
