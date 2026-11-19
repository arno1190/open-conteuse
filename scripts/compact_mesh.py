"""Mesh integrity, connected components and signed material volume, no CAD claims."""
from collections import Counter
import hashlib,math
from export_integrated import triangles

def inspect(path):
 parent={};edges=Counter();volume=0;count=0;lo=[math.inf]*3;hi=[-math.inf]*3
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for tri in triangles(path):
  a,b,c=tri;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
  vs=[tuple(round(v,5) for v in p) for p in tri];count+=1
  for v in vs:
   parent.setdefault(v,v)
   for i in range(3):lo[i]=min(lo[i],v[i]);hi[i]=max(hi[i],v[i])
  for i in range(3):
   a,b=vs[i],vs[(i+1)%3];edges[tuple(sorted((a,b)))]+=1;ra,rb=find(a),find(b)
   if ra!=rb:parent[rb]=ra
 assert count>0 and all(n==2 for n in edges.values()),f'non-manifold {path}'
 assert abs(volume)>0
 return dict(triangles=count,components=len({find(a) for a in parent}),bounds_mm=[lo,hi],volume_cm3=round(abs(volume)/1000,5),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
