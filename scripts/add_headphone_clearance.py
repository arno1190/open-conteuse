#!/usr/bin/python3
"""Add the current routed headphone-neck relief; never changes component/net routing."""
import hashlib,json,math,re,uuid
from pathlib import Path
import pcbnew as p
from project import HARDWARE

def node(kind,pts,key):
 labels=['start','end'] if kind=='gr_line' else ['start','mid','end']
 coords=' '.join('('+k+' '+str(round(x+30,6))+' '+str(round(y+30,6))+')' for k,(x,y) in zip(labels,pts))
 return '('+kind+' '+coords+' (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "'+str(uuid.uuid5(uuid.NAMESPACE_URL,key))+'"))'
for name in ['mini','explore']:
 folder=HARDWARE/name;path=folder/(name+'.kicad_pcb');text=path.read_text()
 # Rebuild only board-outline drawings; all component, pad and track geometry stays in place.
 matches=list(re.finditer(r'\n\t\(gr_(?:line|arc)\b',text));remove=[]
 for match in matches:
  start=text.index('(',match.start());depth=0
  for i in range(start,len(text)):
   if text[i]=='(':depth+=1
   elif text[i]==')':
    depth-=1
    if depth==0:
     if '(layer "Edge.Cuts")' in text[start:i+1]:remove.append((start,i+1))
     break
 assert remove,'Missing native outline'
 for start,end in reversed(remove):text=text[:start]+text[end:]
 points=[[3.5,9],[61.5,9],[62.5,10],[62.5,91],[61.5,92],[30.7,92],[30.7,91.1]]
 segments=[('gr_line',[a,b]) for a,b in zip(points,points[1:])]
 segments += [('gr_arc',[(30.7,91.1),(30.553553,90.746447),(30.2,90.6)]),('gr_line',[(30.2,90.6),(27.2,90.6)]),('gr_arc',[(27.2,90.6),(26.846447,90.746447),(26.7,91.1)])]
 tail=[[26.7,91.1],[26.7,92],[3.5,92],[2.5,91],[2.5,10],[3.5,9]]
 segments += [('gr_line',[a,b]) for a,b in zip(tail,tail[1:])]
 text=text.rstrip();assert text.endswith(')');text=text[:-1]+'\n'+'\n'.join(node(k,pts,name+'headphone-relief'+str(i)) for i,(k,pts) in enumerate(segments))+'\n)\n';path.write_text(text)
 board=p.LoadBoard(str(path));board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(path),board)
 data=json.loads((folder/'components.json').read_text())
 points=[[3.5,9],[61.5,9],[62.5,10],[62.5,91],[61.5,92],[30.7,92],[30.7,91.1]]
 points += [[round(30.2+.5*math.cos(math.radians(-i*90/12)),6),round(91.1+.5*math.sin(math.radians(-i*90/12)),6)] for i in range(1,13)]
 points += [[27.2,90.6]]+[[round(27.2+.5*math.cos(math.radians(-90-i*90/12)),6),round(91.1+.5*math.sin(math.radians(-90-i*90/12)),6)] for i in range(1,13)]
 points += [[26.7,92],[3.5,92],[2.5,91],[2.5,10]]
 data['pcb']['edge_polygon']=points;data['pcb']['headphone_neck_relief']=dict(x=[26.7,30.7],y=[90.6,92],inside_corner_radius=.5,purpose='clear reference tapered headphone neck; actual plug qualification pending')
 (folder/'components.json').write_text(json.dumps(data,indent=2)+'\n')
 print(name,'rounded headphone relief added/refilled')
