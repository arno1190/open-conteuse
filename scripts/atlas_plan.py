"""View definitions in nominal CAD millimetres; no rendering dependencies."""
from integrated_hardware import read_data,indexed
PARTS=indexed(read_data()[0])

def views(variant):
 specs=[]
 def add(id,title,direction,mode='assembled',target=(56,105,25),span=245,cut=None,focus=None):specs.append(dict(id=id,title=title,direction=direction,mode=mode,target=target,span=span,cut=cut,focus=focus))
 add('hero-front','Assembled front isometric',(1,-1.3,-1.8));add('hero-rear','Assembled rear isometric',(-1,-1.3,1.8))
 for id,vec in [('front',(0,0,-1)),('rear',(0,0,1)),('left',(-1,0,0)),('right',(1,0,0)),('top',(0,-1,0)),('bottom',(0,1,0))]:add('orthographic-'+id,id.title()+' orthographic',vec)
 add('lid-open','Lid removed rear isometric',(1,-1.2,1.8),'open')
 add('front-layer','Front electronics viewed from rear',(0,0,-1),'front-layer')
 add('carrier','Carrier electronics and retention',(0,0,1),'carrier')
 add('exploded-front','Exploded assembly front',(1,-1.1,-1.4),'exploded',target=(56,105,42),span=280)
 add('exploded-rear','Exploded assembly rear',(-1,-1.1,1.5),'exploded',target=(56,105,42),span=280)
 for axis,value,keep,title in [(0,32,'high','A MCU and controls longitudinal'),(0,56,'high','B centre longitudinal'),(0,82,'low','C battery and audio longitudinal'),(1,20,'high','D USB and MCU transverse'),(1,95,'high','E speaker and battery transverse'),(1,168,'low','F controls and headphone transverse'),(2,15,'low','G front layer horizontal'),(2,35,'low','H carrier layer horizontal')]:
  direction=((-1,-.7,.9) if keep=='high' else (1,-.7,.9)) if axis==0 else ((.9,-1,.9) if keep=='high' else (.9,1,.9)) if axis==1 else (.8,-1,1.5)
  add('section-'+title[0].lower(),'Section '+title,direction,'section',cut=[axis,value,keep])
 for id,title,target,span,direction in [('usb','Charging USB C port',(72.9,2,35),42,(.5,-1,.4)),('headphone','Headphone jack and wall',(108,167.8,36.3),43,(1,-.3,.6)),('switch','Switch and side retention',(108,51,35),43,(1,-.8,1)),('controls','Button and switch stack',(42,160,6),68,(1,-1,-.9)),('battery','Battery cage and cover',(80,112,36),95,(1,-1,1.6)),('mcu','MCU cradle and retainers',(25,40,38),90,(1,-1,1.6)),('sd','MicroSD service access',(62,56,35),60,(1,-1,1.5)),('speaker','Speaker flange spacer and mounts',((79,87,15) if variant=='mini' else (55,97,15)),95,(1,-1,1.1))]:add('detail-'+id,title,direction,'detail',target,span,focus=id)
 for ident in (['controls','mute_latch','nfc','sd','headphone','speaker_amp','speaker','battery','charger','power_switch','mcu','regulator'] if variant=='mini' else ['controls','display']):
  direction=(1,-1,-1.7) if ident in ['display','controls'] else (1,-1,1.7)
  add('board-'+ident,PARTS[ident]['description'],direction,'board',focus=ident)
 return specs


def native_board_point(ident,point):
 """GLB metres → local mm, rigid transforms preserving physical handedness.

 Controls front faces the enclosure front (−Z). Latch front faces +Z;
 its native KiCad localY is reversed in the normalized physical GLB frame.
 """
 x,y,z=point
 if ident=='controls':return [x*1000-30,-y*1000-30,1.6-z*1000]
 if ident=='mute_latch':return [x*1000-30,y*1000+75,z*1000]
 raise ValueError(ident)
