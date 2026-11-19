"""Check actual filled supply islands and broad-copper corridors, not circuit safety.
KiCad filled polygons contain zero-width fracture seams: restore holes before
erosion, otherwise those seams become false cuts. A0.8mm erosion-path check allows only1.5mm endpoint fanout regions. It does not
model AC impedance, current crowding, stack tolerances or temperature rise.
"""
import pcbnew as p,math

def check(board,variant):
 fs={f.GetReference():f for f in board.GetFootprints()}
 def point(ref,pin):
  q=next(q for q in fs[ref].Pads() if q.GetNumber()==str(pin));return [p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)]
 specs=[('/3V2',p.In2_Cu,[point('C4',1),point('U1',2),point('C29',1),point('C30',1)]),('/SYS',p.B_Cu,[[78.4,72],point('C7',1),point('C2',1),point('C19',1),point('C20',1)]),('/BAT',p.In2_Cu,[point('J5',1),[73.7,72]]+([point('C3',1)] if variant=='mini' else [])),('/VBUS',p.B_Cu,[[78.6,114.9],[75.75,74.4],point('C1',1)])]
 if variant=='explore':
  specs[1][2].append(point('C28',1));specs.append(('/BAT',p.B_Cu,[[73.7,72],point('C3',1)]))
 report={}
 for net,layer,points in specs:
  zone=next(z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net and z.GetLayer()==layer);poly=p.SHAPE_POLY_SET(zone.GetFilledPolysList(layer));poly.Unfracture();local=p.SHAPE_POLY_SET(poly);local.Inflate(-p.FromMM(.075),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,p.FromMM(.005));core=p.SHAPE_POLY_SET(poly);core.Inflate(-p.FromMM(.4),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,p.FromMM(.005));common=None;wide=None;rows=[]
  for x,y in points:
   v=p.VECTOR2I(p.FromMM(x),p.FromMM(y));ids={i for i in range(poly.OutlineCount()) if poly.Contains(v,i)};near=set()
   for ix in range(-6,7):
    for iy in range(-6,7):
     dx,dy=ix*.25,iy*.25
     if dx*dx+dy*dy>2.25:continue
     v=p.VECTOR2I(p.FromMM(x+dx),p.FromMM(y+dy));candidates={i for i in range(core.OutlineCount()) if core.Contains(v,i)}
     if not candidates:continue
     steps=max(1,math.ceil(math.hypot(dx,dy)/.05))
     if all(local.Contains(p.VECTOR2I(p.FromMM(x+dx*j/steps),p.FromMM(y+dy*j/steps))) for j in range(steps+1)):near.update(candidates)
   assert ids,(variant,net,'endpoint does not meet supply pour',x,y)
   common=ids if common is None else common&ids;wide=near if wide is None else wide&near;rows.append({'xy_absolute_mm':[x,y],'filled_islands':sorted(ids),'local_0_15mm_neck_to_0_8mm_cores':sorted(near)})
  assert common,(variant,net,'source/load endpoints are on different filled islands',rows)
  assert wide,(variant,net,'no shared0.8mm core within1.5mm fanout of endpoints',rows)
  report[net+'@'+p.LayerName(layer)]={'layer':p.LayerName(layer),'total_filled_islands':poly.OutlineCount(),'shared_islands':sorted(common),'shared_0_8mm_core':sorted(wide),'endpoints':rows}
 return report
