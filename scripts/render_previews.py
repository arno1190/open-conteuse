#!/usr/bin/env python3
"""Render actual shell meshes, actual PCB routing and labelled integration envelopes.

Run from repository root after scripts/cad-check.sh and export_preview_pcb.py.
Generated meshes/data remain in work; reviewed PNGs go to docs/previews.
"""
import os,struct,json
os.environ['MPLCONFIGDIR']=os.path.abspath('work/previews/mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import FancyBboxPatch,Rectangle,Circle
from pathlib import Path
P=Path('docs/previews');P.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titleweight':'medium'})
BG='#f5f4ef';INK='#243b39';GREEN='#6f9990';ORANGE='#d4a16a'
def stl(path):
 raw=Path(path).read_bytes()
 if raw[:5].lower()==b'solid':
  import re
  v=np.array([[float(x) for x in m] for m in re.findall(rb'vertex\s+([-+.\deE]+)\s+([-+.\deE]+)\s+([-+.\deE]+)',raw)])
  return v.reshape(-1,3,3)
 n=struct.unpack_from('<I',raw,80)[0]
 dt=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);return np.frombuffer(raw,dtype=dt,count=n,offset=84)['v'].copy()
def mesh(ax,v,color,alpha=1):
 normals=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9)
 light=np.array([-.4,-.4,1]);light/=np.linalg.norm(light)
 brightness=.58+.42*np.abs(normals@light)
 from matplotlib.colors import to_rgb
 colors=np.clip(np.array(to_rgb(color))[None,:]*brightness[:,None],0,1)
 ax.add_collection3d(Poly3DCollection(v,facecolors=colors,edgecolor='none',alpha=alpha,zsort='average'))
fig=plt.figure(figsize=(13,9),facecolor=BG)
for i,(variant,title) in enumerate([('mini','Mini · NFC card pocket'),('explore','Explore · display opening')],1):
 ax=fig.add_subplot(1,2,i,projection='3d',computed_zorder=False)
 v=stl('work/cad/'+variant+'-front.stl').astype(float)
 v[:,:,1]*=-1;v[:,:,2]*=-1
 mesh(ax,v,'#91b5a8' if variant=='mini' else '#86a6bd')
 caps=stl('work/cad/'+variant+'-plunger.stl').astype(float)
 coords=json.load(open('enclosure/controls.json'))['actuators_mm']
 for j,(x,y) in enumerate(coords):
  if variant=='mini' and j not in [1,3,4,6,7]:continue
  cap=caps.copy();cap[:,:,0]+=15+x;cap[:,:,1]+=98+y;cap[:,:,2]-=1.2
  cap[:,:,1]*=-1;cap[:,:,2]*=-1;mesh(ax,cap,'#d2a477')
 ax.set(xlim=(-8,108),ylim=(-181,7),zlim=(-30,35));ax.set_box_aspect((116,188,65));ax.view_init(62,-64);ax.set_axis_off();ax.set_facecolor(BG)
 ax.set_title(title,color=INK,pad=0,fontsize=15)
fig.suptitle('Open Conteuse — current enclosure geometry',color=INK,fontsize=21,y=.95)
fig.text(.5,.12,'100 × 174 × 38 mm nominal assembled shell  •  CAD fit study, not physically validated',ha='center',color=INK)
fig.text(.5,.08,'Shells and captive plungers rendered from the actual OpenSCAD meshes. Display/card/speaker not installed.',ha='center',color='#596765',fontsize=10)
fig.subplots_adjust(left=0,right=1,top=.9,bottom=.15,wspace=-.15);fig.savefig(P/'enclosure-design.png',dpi=180,facecolor=BG);plt.close(fig)
# Actual PCB copper, pads and switch locations.
fig,ax=plt.subplots(figsize=(9,8),facecolor=BG);ax.set_facecolor(BG)
ax.add_patch(Rectangle((0,0),70,65,facecolor='#153e34',edgecolor='#31564b',lw=2))
data=json.load(open('work/previews/pcb.json'))
for layer,col,alpha in [('B.Cu','#7da7cf',.65),('F.Cu','#e5ad79',1)]:
 for t in data['tracks']:
  if t['layer']==layer:ax.plot([t['a'][0],t['b'][0]],[t['a'][1],t['b'][1]],color=col,lw=1.15,alpha=alpha,zorder=2)
for p in data['pads']:
 x,y=p['xy'];r=1.35 if p['ref'].startswith('H') else .9
 ax.add_patch(Circle((x,y),r,fc='#dabd71',ec='none',zorder=4));ax.add_patch(Circle((x,y),p['drill']/2,fc=BG,ec='none',zorder=5))
names=['Up','Play / A','Down','Prev / Left','Next / Right','Back / B','Volume −','Volume +']
for i,((x,y),name) in enumerate(zip(coords,names)):
 ax.add_patch(Rectangle((x-3,y-3),6,6,fc='#eef0e9',ec='#a1aaa0',lw=.8,zorder=6))
 ax.add_patch(Circle((x,y),1.65,fc='#566460',ec='none',zorder=7))
 ax.text(x,y-5.1,f'SW{i+1}',ha='center',va='bottom',color='#edf2e6',fontsize=9,zorder=8)
ax.text(35,3,'COMMON CONTROLS BOARD',ha='center',va='center',color='#edf2e6',fontsize=10)
ax.set(xlim=(-5,75),ylim=(70,-5));ax.set_aspect('equal');ax.set_axis_off()
fig.suptitle('KiCad controls PCB · actual routed geometry',color=INK,fontsize=18,y=.97)
fig.text(.5,.08,'70 × 65 mm · 2 layers · copper shown on both sides\nZero ERC/DRC violations and no unrouted pads; final audio/power carrier not included.',ha='center',color=INK,linespacing=1.6)
fig.subplots_adjust(top=.9,bottom=.15);fig.savefig(P/'controls-pcb.png',dpi=180,facecolor=BG);plt.close(fig)
# Integration is a truthful dimensioned keepout study, not an invented completed assembly.
fig,axes=plt.subplots(1,3,figsize=(15,10),facecolor=BG)
for ax in axes:
 ax.set_facecolor(BG);ax.set_xlim(-8,108);ax.set_ylim(184,-8);ax.set_aspect('equal');ax.axis('off')
 ax.add_patch(FancyBboxPatch((0,0),100,174,boxstyle='round,pad=0,rounding_size=8',fc='#e1e6dd',ec='#83968c',lw=1.5))
 for x,y in [(7,7),(93,7),(7,167),(93,167)]:ax.add_patch(Circle((x,y),2.2,fc=BG,ec='#83968c',lw=.7))
# Front cavities.
for ax,variant in zip(axes[:2],['mini','explore']):
 ax.add_patch(Rectangle((15,98),70,65,fc='#518b73',alpha=.7,ec='#306b55',lw=1.3))
 for x,y in [(4,4),(66,4),(4,61),(66,61)]:ax.add_patch(Circle((15+x,98+y),1.35,fc=BG,ec='#306b55',lw=.6))
 ax.text(50,154,'Controls PCB\n70 × 65',ha='center',va='center',color='white',fontsize=10)
 for i,(x,y) in enumerate(coords):
  if variant=='mini' and i not in [1,3,4,6,7]:continue
  ax.add_patch(Circle((15+x,98+y),3,fc='#edc997',ec='#9b733e',lw=.7))
 ax.add_patch(Circle((50,83),20,fc='#a9b7bf',ec='#667d87',ls='--',alpha=.75,lw=1))
 ax.text(50,80,'Speaker\nØ40 assumed',ha='center',va='center',fontsize=9,color=INK)
 if variant=='mini':
  ax.add_patch(Rectangle((28.5,20),43,40,fc='#b8a8d1',ec='#827398',ls='--',alpha=.8))
  ax.text(50,40,'PN532 reader\n43 × 40 assumed',ha='center',va='center',fontsize=9,color=INK)
  ax.add_patch(Rectangle((23,14),54,58,fill=False,ec='#8d6b44',lw=1.5))
  ax.text(50,67,'Card guides outside',ha='center',fontsize=8,color='#775a39')
 else:
  ax.add_patch(Rectangle((7,12),86,50,fc='#9cb4ca',ec='#5a7d98',ls='--',alpha=.75))
  ax.add_patch(Rectangle((21,17),58,44,fc='#405e71',ec='none',alpha=.8))
  ax.text(50,38,'Display module\n86 × 50 assumed',ha='center',va='center',fontsize=9,color='white')
 ax.text(50,178,'Front half · inner view',ha='center',va='top',fontsize=10,color=INK)
axes[0].set_title('Mini integration',fontsize=16,color=INK,pad=15);axes[1].set_title('Explore integration',fontsize=16,color=INK,pad=15)
ax=axes[2];ax.set_title('Shared back · proposals',fontsize=16,color=INK,pad=15)
ax.add_patch(Rectangle((31,29),38,60,fc='#dfb17d',ec='#a27746',ls='--',alpha=.8));ax.text(50,57,'Battery\n38 × 60 × 8\nplaceholder',ha='center',va='center',fontsize=9,color=INK)
ax.add_patch(Rectangle((70,29),26,63,fc='#95b1a1',ec='#587c6c',ls='--',alpha=.8));ax.text(83,60,'DevKit\n26 × 63\nassumed',ha='center',va='center',fontsize=8,color=INK)
ax.add_patch(Rectangle((18,106),64,39,fill=False,ec='#ac8869',ls='--',lw=1.3));ax.text(50,125,'Audio / headphones\nand charger section\nNOT designed / fitted',ha='center',va='center',fontsize=10,color=INK)
ax.text(50,178,'Location / mounts / wiring unresolved',ha='center',va='top',fontsize=9,color=INK)
fig.suptitle('Component integration — what exists and what is still assumed',fontsize=20,color=INK,y=.95)
fig.text(.5,.09,'Solid green = real controls PCB footprint. Dashed outlines = provisional component envelopes, not measured models.',ha='center',fontsize=11,color=INK)
fig.text(.5,.055,'Layout is an explanatory keepout plan, not collision clearance or electrical validation. Back shown in common front coordinates.',ha='center',fontsize=10,color='#596765')
fig.subplots_adjust(top=.86,bottom=.15,wspace=.12,left=.025,right=.98);fig.savefig(P/'integration-plan.png',dpi=170,facecolor=BG);plt.close(fig)
print('Wrote enclosure-design.png, controls-pcb.png, integration-plan.png')
