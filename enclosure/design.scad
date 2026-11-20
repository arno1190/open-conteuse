// Current Mini contact-ID / Explore enclosures. Millimetres, canonical Y downward.
// Production fit, thermal, acoustic, RF and battery validation remain pending.
variant=is_undef(variant)?"mini":variant;
part=is_undef(part)?"assembly":part;
$fn=48;
if(variant=="mini") mini(); else explore();
module mini(){include <mini-data.scad>; design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves,main_polygon);}
module explore(){include <explore-data.scad>; design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves,main_polygon);}
use <card.scad>;
include <contact-data.scad>;
module design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves,main_polygon){
 W=dims[0];H=dims[1];D=dims[2];wall=1.8;split=12.8;S=D-5.6;keeper_posts=[[36,77.3],[41.5,91.5]];

 module reader_holder(sweep=false){
  for(q=[[8.5,38],[54.5,39]])translate([q[0],q[1],14.95])cylinder(d=3,h=D-wall-14.95+.05);
  difference(){
   union(){
    translate([10.7,.1,16.6])cube([1.5,40.5,D-wall-16.6+.05]);
    translate([52.8,.1,16.6])cube([1.5,40.5,D-wall-16.6+.05]);
   }
   translate([10.6,2,19.8])cube([1.7,8,1.3]);
  }
  for(x=[12.1,45.2]){
   translate([x,2,16.6])cube([7.7,37.8,.65]);
   translate([x,2,21.65])cube([7.7,37.8,D-wall-21.65+.05]);
  }
  translate([10.7,40.2,16.6])cube([43.6,1,D-wall-16.6+.05]);
  // Asymmetric rear-side key rail, clearance from the card's matching groove.
  translate([12.1,.5,18.1])cube([1.2,39,.7]);
  // Compliant side detent. Force/wear qualification requires actual material.
  translate([11.4,.5,19.9])cube([.8,8.2,1]);
  if(!sweep)translate([12.25,8,19.9])cylinder(r=.6,h=1);
 }
 module reader_pcb(){
  translate([8.5,29,13.35])difference(){linear_extrude(1.6)polygon(reader_polygon);for(q=reader_holes)translate([q[0],q[1],-.1])cylinder(d=1.8,h=1.8);}
 }
 module reader_assembly(){
  reader_pcb();
  for(i=[0:len(reader_bodies)-1])let(b=reader_bodies[i])translate([b[0],b[1],b[2]])cube([b[3],b[4],b[5]]);
  for(x=[29.5,35.5]){
   translate([x,35,14.95])cylinder(d=2,h=.4);
   translate([x,35,15.35])cylinder(d=1.5,h=2.1);
   translate([x,35,17.45])cylinder(d=.9,h=.35); // loaded tip, pad plane17.8
  }
  for(q=[[8.5,38],[54.5,39]])translate([q[0],q[1],12.05])cylinder(d=3.2,h=1.3);
 }
 module card_at(offset=0){translate([12.5,-20-offset,17.3])card_assembly();}

 module rounded(w,h,z,r=5){linear_extrude(z)offset(r=r)translate([r,r])square([w-2*r,h-2*r]);}
 module ring(w,h,z,inset){difference(){rounded(w,h,z);translate([inset,inset,-.1])rounded(w-2*inset,h-2*inset,z+.2,max(1,5-inset));}}
 module round_rect(w,h,r){offset(r=r)translate([-w/2+r,-h/2+r])square([w-2*r,h-2*r]);}
 module edge_bevel(top=true){
  z=top?D-.4:0;
  difference(){translate([-1,-1,z])cube([W+2,H+2,.401]);
   hull(){
    translate(top?[0,0,z]:[.4,.4,z])rounded(top?W:W-.8,top?H:H-.8,.001,top?5:4.6);
    translate(top?[.4,.4,z+.4]:[0,0,z+.4])rounded(top?W-.8:W,top?H-.8:H,.001,top?4.6:5);
   }
  }
 }
 module ports(){
  // Rounded plug tunnels retain access to the recessed native connectors.
  translate([51,H+3,13.3])rotate([90,0,0])linear_extrude(12)round_rect(11.4,6.4,1.7);
  translate([29,H+3,14.2])rotate([90,0,0])cylinder(d=8.8,h=12);
  translate([W-7,10,11.3])cube([9,17,4.4]);
  translate([-1,41,11.2])cube([8,8,6.5]);
  if(variant=="mini")translate([12.2,-1,17.1])cube([40.6,3,4.7]);
 }
 module headphone_reference(){
  // Drawing-defined phone-case-style plug:5mm neck tapers to8mm over4mm.
  translate([29,91.05,14.2])rotate([-90,0,0]){
   cylinder(d1=5,d2=8,h=4);
   translate([0,0,4])cylinder(d=8,h=H+12-95.05);
  }
 }
 module usb_reference(){translate([51,H+14,13.3])rotate([90,0,0])linear_extrude(H+14-93.45)round_rect(10.5,5.8,1.5);}
 module plug_references(){headphone_reference();usb_reference();}
 module front(sweep=false){difference(){union(){
   translate([0,0,D-wall])rounded(W,H,wall);
   translate([0,0,split+.15])ring(W,H,D-wall-split-.15+.1,wall);
   for(h=holes)translate([h[0],h[1],11.7])cylinder(d=6,h=D-wall-11.7+.05);
   for(q=keeper_posts)translate([q[0],q[1],S])cylinder(d=3.0,h=D-wall-S+.05);
   // Top two internal hooks support the seam above the lower screw pattern.
   for(x=[10,W-10])translate([x-2,1.5,12.3])cube([4,1.5,4]);
   if(variant=="mini")reader_holder(sweep);
   else {
    // Broad panel support ledges outside the active area, no compression on glass.
    translate([4,5.8,18.8])cube([58,1.7,D-wall-18.8+.05]);
    translate([4,49.2,18.8])cube([58,1.92,D-wall-18.8+.05]);
   }
  }
  ports();edge_bevel(true);
  for(q=keeper_posts)translate([q[0],q[1],S-.1])cylinder(d=1.25,h=3.5);
  if(variant=="mini")for(q=[[8.5,38],[54.5,39]])translate([q[0],q[1],14.8])cylinder(d=1.25,h=3.9);
  for(h=holes){translate([h[0],h[1],11.6])cylinder(d=3.0,h=3.3);translate([h[0],h[1],14.8])cylinder(d=2.3,h=2.2);}
  for(i=[0:len(buttons)-1])translate([buttons[i][0],buttons[i][1],D-3])cylinder(d=cap_d(i)+.4,h=4);
  // Speaker grille; rows avoid keeper skirts and shell screw posts.
  for(x=[36:2.2:47],y=[81:2.2:88])translate([x,y,D-2])cylinder(d=1.2,h=3);
  if(variant=="explore"){
   translate([8.9,10,D-2])cube([48.96,36.72,3]);
   translate([3.17,6.8,19.35])cube([60.66,43.12,2.9]);
   translate([5.8,8.3,22.1])cube([55.4,40.4,1]);
  }

  translate([8,H-5,D-.3])linear_extrude(.4)mirror([0,1,0])text(variant=="mini"?"MINI":"EXPLORE",size=3,font="DejaVu Sans:style=Bold");
  translate([10,11,D-2])cylinder(d=2,h=3);
 }}
 module back(){difference(){union(){
  rounded(W,H,wall);
  translate([0,0,wall-.05])ring(W,H,split-wall+.1,wall);
  translate([0,0,11.8])ring(W,H,1,3);
  translate([2,2,12.75])ring(W-4,H-4,1.05,1);
  for(h=holes)translate([h[0],h[1],1.7])cylinder(d=6,h=8.8);
  // Pouch pocket: side fences outside the explicit36x64mm service reserve.
  for(x=[13.3,50.7])translate([x,24,1.7])cube([.8,62,2.8]);
  translate([14.1,22,1.7])cube([37.4,.8,2.8]);
  translate([14.1,87.2,1.7])cube([37.4,.8,2.8]);
  // Nominal 10mm-wide, <=1.5mm-thick soft band envelope, supplier to confirm.
  // 11x2mm slots leave 0.8mm top/bottom material; never clamp the pouch.
  for(x=[10.5,53.5])translate([x,46.5,1.7])cube([2,13,3.6]);
 }
 ports();edge_bevel(false);
 for(h=holes)translate([h[0],h[1],11.6])cylinder(d=6.4,h=3);
 // Antenna overhang clearance at the top seam (plastic lip only).
 translate([22.9,2.5,11.6])cube([19.2,1.2,2.3]);
 for(h=holes){translate([h[0],h[1],-.1])cylinder(d=2.3,h=11);translate([h[0],h[1],-.1])cylinder(d=4.2,h=2.3);}
 for(x=[10,W-10])translate([x-2.3,1.3,12])cube([4.6,2,4.5]);
 for(x=[10.5,53.5])translate([x-.1,47.5,2.5])cube([2.2,11,2]);
 }}
 module bridge(){difference(){union(){
  intersection(){translate([0,0,S-.8])linear_extrude(.8)hull()for(q=keeper_posts)translate(q)circle(r=2);translate([0,0,0])cube([W,93.1,D]);}
  hull()for(q=[[38.6725,84.2],[40.6479,89.3]])translate([q[0],q[1],S-1.8])cylinder(r=.6,h=1.05);
 }for(q=keeper_posts)translate([q[0],q[1],S-2])cylinder(d=1.8,h=2.2);}}
 module keeper_heads(){for(q=keeper_posts)translate([q[0],q[1],S-2.1])cylinder(d=3.2,h=1.3);}
 // Larger primary control; tactile debossed symbols remain identifiable without colour.
 function cap_d(i)=button_names[i]=="A"?10.5:(button_names[i]=="VOL_DOWN" || button_names[i]=="VOL_UP")?6.5:button_names[i]=="B"?7.5:variant=="mini"?8.5:7;
 module triangle(){polygon([[-1.6,-1.8],[1.5,0],[-1.6,1.8]]);}
 module glyph(i){let(n=button_names[i])
  if(n=="A"){
   translate([-1.1,0])scale([.85,.85])triangle();
   for(x=[1,2.3])translate([x,-1.6])square([.8,3.2]);
  }else if(n=="VOL_DOWN" || n=="VOL_UP"){
   translate([-2,-.4])square([4,.8]);if(n=="VOL_UP")translate([-.4,-2])square([.8,4]);
  }else if(n=="B")polygon([[-2.6,0],[-.5,-1.8],[-.5,-.6],[1.3,-.6],[1.3,1.4],[.4,1.4],[.4,.3],[-.5,.3],[-.5,1.8]]);
  else rotate(n=="LEFT"?180:n=="UP"?-90:n=="DOWN"?90:0){
   triangle();if(variant=="mini")translate([2,-1.8])square([.8,3.6]);
  }
 }
 module cap(i=0){difference(){union(){
  // Nominal actuator top13.6, stem gap0.1. Received travel/force still require qualification.
  translate([0,0,13.7])cylinder(d=3,h=D-3-13.7);
  // Flat retaining collar limits upward float to0.1mm under the22.2mm roof.
  translate([0,0,D-3])cylinder(d=cap_d(i)+1.6,h=1.1);
  translate([0,0,D-1.9])cylinder(d=cap_d(i),h=2.25);
  translate([0,0,D+.35])cylinder(d1=cap_d(i),d2=cap_d(i)-.5,h=.25);
 }translate([0,0,D+.1])linear_extrude(.6)glyph(i);}}
 module caps(){for(i=[0:len(buttons)-1])color(button_names[i]=="A"?[.98,.64,.16]:(button_names[i]=="VOL_DOWN" || button_names[i]=="VOL_UP")?[.43,.61,.54]:button_names[i]=="B"?[.82,.32,.23]:[.04,.4,.5])translate([buttons[i][0],buttons[i][1],0])cap(i);}
 module pcb(){difference(){color(variant=="mini"?[.05,.32,.20]:[.06,.24,.50])translate([0,0,10.5])linear_extrude(1.2)polygon(main_polygon);for(h=holes)translate([h[0],h[1],10.4])cylinder(d=2.2,h=1.5);}}
 module components(){for(i=[0:len(bodies)-1])let(b=bodies[i])
  if(body_refs[i]=="SW9"){
   // Manufacturer housing and side actuator; full Fab bounding box would
   // incorrectly fill the empty space beside the small recessed lever.
   color([.6,.6,.6])translate([3.2,40.5,11.7])cube([3.6,9,3.5]);
   color([.1,.1,.1])translate([1.2,43,12.4])cube([2.1,1.5,1.6]);
  } else color(body_refs[i][0]=="C"?[.64,.48,.28]:[.13,.15,.17])translate([b[0],b[1],b[2]])cube([b[3],b[4],b[5]]);
 }
 module peripherals(check_mount=false){
  for(i=[0:len(extras)-1])let(b=extras[i],n=extra_names[i])color(n=="cell"?[.9,.6,.17]:[.1,.15,.2])translate([b[0],b[1],b[2]+(check_mount && n=="speaker"?.001:0)])cube([b[3],b[4],b[5]-(check_mount && n=="speaker"?.001:0)]);
  if(variant=="mini"){reader_assembly();card_at();}
 }
 module assembly(explode=0){bridge();color([.6,.6,.6])keeper_heads();color([.88,.88,.83])back();translate([0,0,explode]){pcb();components();peripherals();}translate([0,0,explode*2]){color([.95,.92,.83])front();caps();}}
 module dispatch(){
 if(part=="front")front();
 else if(part=="back")back();
 else if(part=="print_front")translate([0,0,D])mirror([0,0,1])front();
 else if(part=="bridge")translate([0,0,S])mirror([0,0,1])bridge();
 else if(part=="button")translate([0,0,D+.6])rotate([180,0,0])cap(0);
 else if(part=="buttons")for(i=[0:len(buttons)-1])translate([8+(i%4)*15,8+floor(i/4)*15,D+.6])rotate([180,0,0])cap(i);
 else if(part=="cap_shell_interference")intersection(){union(){front();back();}union()for(t=[-.35,0,.09])translate([0,0,t])caps();}
 else if(part=="cap_pair_interference")union()for(i=[0:len(buttons)-2],j=[i+1:len(buttons)-1])intersection(){translate([buttons[i][0],buttons[i][1],0])cap(i);translate([buttons[j][0],buttons[j][1],0])cap(j);}
 else if(part=="pcb")pcb();
 else if(part=="reader_pcb")reader_pcb();
 else if(part=="components")components();
 else if(part=="peripherals")peripherals();
 else if(part=="plugs")plug_references();
 else if(part=="headphone_plug_clearance")intersection(){union(){front();back();pcb();}headphone_reference();}
 else if(part=="usb_plug_clearance")intersection(){union(){front();back();pcb();}usb_reference();}
 else if(part=="internal_interference")intersection(){components();peripherals();}
 else if(part=="shell_interference")intersection(){front();back();}
 else if(part=="interference")intersection(){union(){front();back();bridge();keeper_heads();}union(){components();peripherals(true);}}
 else if(part=="exploded")assembly(20);
 else if(part=="strap_clearance")intersection(){back();union()for(x=[10.25,53.25])translate([x,48,2.75])cube([2.5,10,1.5]);}
 else if(part=="wrong_card_interference")intersection(){front();translate([12.5,-30,17.3])translate([40,0,4.3])rotate([0,180,0])card_assembly();}
 else if(part=="card_sweep_interference")intersection(){union(){front(true);back();bridge();keeper_heads();components();reader_assembly();}union()for(t=[0:1:40])card_at(t);}
 else if(part=="section_x")intersection(){assembly();translate([W/2,-1,-1])cube([W,H+2,D+2]);}
 else if(part=="section_y")intersection(){assembly();translate([-1,H/2,-1])cube([W+2,H,D+2]);}
 else if(part=="coupon")difference(){cube([48,20,3]);for(q=[[9,10,10.9],[23,10,8.9],[35,10,6.9]])translate([q[0],q[1],-.1])cylinder(d=q[2],h=3.2);translate([44,7,-.1])cylinder(d=3,h=3.2);translate([44,14,-.1])cylinder(d=1.25,h=3.2);}
 else if(part=="port_coupon")difference(){cube([42,20,3]);translate([11,10,-.1])linear_extrude(3.2)round_rect(11.4,6.4,1.7);translate([31,10,-.1])cylinder(d=8.8,h=3.2);}
 else if(len(part)==5 && part[0]=="c" && part[1]=="a" && part[2]=="p" && part[3]=="_"){for(i=[0:len(buttons)-1])if(part==str("cap_",i))translate([0,0,D+.6])rotate([180,0,0])cap(i);}
 else assembly();
 }
 // Canonical PCB coordinates have Y downward. Meshes use physical right-handed
 // coordinates Yout=H-Y so the printed housing matches manufactured KiCad boards.
 if(part=="print_front" || part=="bridge" || part=="button" || part=="buttons" || part=="coupon" || part=="port_coupon" || (len(part)==5 && part[0]=="c" && part[1]=="a" && part[2]=="p" && part[3]=="_"))dispatch();
 else translate([0,H,0])mirror([0,1,0])dispatch();

}
