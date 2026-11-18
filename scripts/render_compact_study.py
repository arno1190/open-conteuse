#!/usr/bin/env python3
"""Same-scale envelope comparison, not fitted component geometry."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'work/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from compact_assessment import load,summary,ROOT
rows=summary(load())['envelopes'];colors=['#758087','#1d617e','#467f91','#db8c35','#378f87','#7e7398']
labels=['Current\nmodular design','Miyoo Mini\nreference','Miyoo Mini Plus\nreference','Mini target\nno display','Explore target\n2.4 inch','Explore fallback\n2.8 inch']
fig,(ax,depth)=plt.subplots(2,1,figsize=(15,8),gridspec_kw={'height_ratios':[4.2,1.1]});fig.patch.set_facecolor('#f7fafb')
x=0;centres=[]
for i,(r,color) in enumerate(zip(rows,colors)):
 w,h,d=r['size'];target=r['id'].endswith('target');ax.add_patch(FancyBboxPatch((x,0),w,h,boxstyle='round,pad=0,rounding_size=4',facecolor=color+'22',edgecolor=color,linewidth=2,linestyle='--' if target else '-'))
 centres.append(x+w/2);ax.text(x+w/2,h+5,f'{w:g} × {h:g} × {d:g}',ha='center',va='bottom',fontsize=10,color=color);ax.text(x+w/2,-10,labels[i],ha='center',va='top',fontsize=10,color=color);x+=w+22
ax.set_xlim(-5,x-15);ax.set_ylim(-42,232);ax.set_aspect('equal');ax.set_ylabel('Height (mm)');ax.set_xticks([]);ax.spines[['top','right','bottom']].set_visible(False);ax.grid(axis='y',alpha=.13)
depth.bar(range(6),[r['size'][2] for r in rows],color=colors,width=.58);depth.set_ylim(0,60);depth.set_ylabel('Depth (mm)');depth.set_xticks(range(6),['Current','Mini ref.','Plus ref.','Mini target','Explore 2.4','Explore 2.8']);depth.spines[['top','right']].set_visible(False)
for i,r in enumerate(rows):depth.text(i,r['size'][2]+1.5,str(r['size'][2])+' mm',ha='center',fontsize=9)
fig.suptitle('Open Conteuse — compact architecture targets',fontsize=20,color='#173e47');fig.text(.08,.015,'All dimensions W × H × D in mm. Miyoo dimensions are approximate published references. Dashed outlines are targets only; no component fit or physical validation is implied.',fontsize=9,color='#48636b');fig.tight_layout(rect=(0,.04,1,.94));fig.savefig(ROOT/'docs/research/compact-size-comparison.png',dpi=150)
