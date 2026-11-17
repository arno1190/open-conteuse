#!/usr/bin/env python3
"""PNG views from exported SCAD geometry and supplier STL references, not illustrations."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from export_integrated import triangles
from integrated_hardware import read_data,indexed,placements,transform_point,size,ROOT
c,l=read_data();parts=indexed(c)
colors={'battery':'#e6a34a','nfc':'#3165af','display':'#243f54','speaker':'#363b3c','headphone':'#7868a8','charger':'#568d91','sd':'#9a744d','mcu':'#3f8ba3','regulator':'#56a06b','controls':'#4b987a','mute_latch':'#5f9873','speaker_amp':'#8070a4','power_switch':'#555555'}
def box(d):
 v=np.array([[x,y,z] for x in [0,d[0]] for y in [0,d[1]] for z in [0,d[2]]]);faces=[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
 return [v[f] for f in faces]
def add(ax,faces,color,alpha=1):
 mesh=Poly3DCollection(faces,facecolor=color,edgecolor='none',alpha=alpha,rasterized=True);ax.add_collection3d(mesh)
def view(variant,exploded):
 fig=plt.figure(figsize=(15,10));ax=fig.add_subplot(111,projection='3d');offset=55 if exploded else 0
 # Carrier is actual SCAD mesh; front omitted to reveal internals.
 path=ROOT/f'enclosure/integrated/print/{variant}-carrier.stl'
 fs=np.array(list(triangles(path)));fs[:,:,2]+=l['case']['carrier_z']+offset;add(ax,fs,'#c4d1c8',.24)
 for pose in placements(l,variant):
  p=parts[pose['part']];model=p.get('model');f=list(triangles(ROOT/model['path'])) if model else box(size(p));f=np.array(f)
  # Limit coplanar detail for practical PNG size; manufacturer's silhouette remains.
  # Preserve all triangles so projected supplier surfaces have no sampled holes.
  flat=[transform_point(p,pose,point) for point in f.reshape(-1,3)];f=np.array(flat).reshape(f.shape)
  if pose['mount']=='carrier':f[:,:,2]+=offset
  add(ax,f,colors[p['id']],1)
  lo=f.reshape(-1,3).min(axis=0);hi=f.reshape(-1,3).max(axis=0)
  label=p['id']+ (' (envelope)' if not model else '')
  # Legend below identifies every purchased component.
 ax.set(xlim=(0,112),ylim=(0,210),zlim=(0,110 if exploded else 52),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)');ax.set_box_aspect((112,210,110 if exploded else 70));ax.view_init(elev=53,azim=-53)
 fig.text(.02,.83,'\n'.join(p['part']+': '+parts[p['part']]['part_number']+(' [envelope]' if not parts[p['part']].get('model') else '') for p in placements(l,variant)),fontsize=9,va='top')
 fig.suptitle(f'{variant.title()} — '+('exploded integration' if exploded else 'internal integration'),fontsize=20)
 fig.text(.08,.045,'Source-derived nominal CAD • front/lid omitted for visibility • MCU/regulator/PCB envelopes labelled\nPhysical fit, switch actuator and assembled MCU height pending. No physical prototype validated.',fontsize=11)
 path=ROOT/'docs/previews/integrated'/f'{variant}-{"exploded" if exploded else "integration"}.png'
 fig.savefig(path,dpi=150);plt.close(fig)
if __name__=='__main__':
 for variant in ['mini','explore']:
  for exploded in ([] if '--front-only' in sys.argv else [False,True]):view(variant,exploded)
  fig=plt.figure(figsize=(8,10));ax=fig.add_subplot(111,projection='3d')
  fs=np.array(list(triangles(ROOT/f'enclosure/integrated/print/{variant}-front.stl')))
  add(ax,fs,'#87ac9a',1)
  ax.set(xlim=(0,112),ylim=(0,210),zlim=(0,50));ax.set_box_aspect((112,210,50));ax.view_init(elev=-65,azim=-65);ax.set_axis_off()
  fig.suptitle(f'{variant.title()} — actual SCAD front',fontsize=18)
  fig.text(.08,.05,'112 × 210 × 50 mm case • nominal prototype\nBare front shell; buttons/PCB/lid omitted. Physical fit pending.',fontsize=10)
  fig.savefig(ROOT/f'docs/previews/integrated/{variant}-front.png',dpi=150);plt.close(fig)
