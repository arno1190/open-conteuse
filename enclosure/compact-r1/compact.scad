// Original compact enclosure R1. Millimetres, case XY, rear at Z=0.
// Production fit, thermal, acoustic, RF and battery validation remain pending.
variant=is_undef(variant)?"mini":variant;
part=is_undef(part)?"assembly":part;
$fn=48;
if(variant=="mini") mini(); else explore();
module mini(){include <mini-data.scad>; design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves);}
module explore(){include <explore-data.scad>; design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves);}
module design(dims,holes,buttons,button_names,bodies,body_refs,extras,extra_names,reserves){
 W=dims[0];H=dims[1];D=dims[2];wall=1.8;split=12.8;S=D-5.6;keeper_posts=[[36,77.3],[41.5,91.5]];
 module rounded(w,h,z,r=5){linear_extrude(z)offset(r=r)translate([r,r])square([w-2*r,h-2*r]);}
 module ring(w,h,z,inset){difference(){rounded(w,h,z);translate([inset,inset,-.1])rounded(w-2*inset,h-2*inset,z+.2,max(1,5-inset));}}
 module ports(){
  // Enlarged countersunk approach tunnels allow recessed connector noses.
  translate([45.5,H-9,10.5])cube([11,12,8]);
  translate([22,H-9,10.5])cube([14,12,8]);
  translate([W-7,10,11.3])cube([9,17,4.4]);
  translate([-1,41,11.2])cube([8,8,6.5]);
 }
 module front(){difference(){union(){
   translate([0,0,D-wall])rounded(W,H,wall);
   translate([0,0,split+.15])ring(W,H,D-wall-split-.15+.1,wall);
   for(h=holes)translate([h[0],h[1],11.7])cylinder(d=6,h=D-wall-11.7+.05);
   for(q=keeper_posts)translate([q[0],q[1],S])cylinder(d=3.0,h=D-wall-S+.05);
   // Top two internal hooks support the seam above the lower screw pattern.
   for(x=[10,W-10])translate([x-2,1.5,12.3])cube([4,1.5,4]);
   if(variant=="mini")for(x=[29.5,55.5],y=[31.5,48.9])translate([x-1,y-1,15])cube([2,2,D-wall-15+.1]);
   else {
    // Broad panel support ledges outside the active area, no compression on glass.
    translate([4,5.8,18.8])cube([58,1.7,D-wall-18.8+.05]);
    translate([4,49.2,18.8])cube([58,1.92,D-wall-18.8+.05]);
   }
  }
  ports();
  for(q=keeper_posts)translate([q[0],q[1],S-.1])cylinder(d=1.25,h=3.5);
  if(variant=="mini")translate([29.8,31.8,15.3])cube([25.4,16.8,4.8]);
  for(h=holes){translate([h[0],h[1],11.6])cylinder(d=3.0,h=3.3);translate([h[0],h[1],14.8])cylinder(d=2.3,h=2.2);}
  for(b=buttons)translate([b[0],b[1],D-3])cylinder(d=7.4,h=4);
  // Speaker grille; rows avoid keeper skirts and shell screw posts.
  for(x=[36:2.2:47],y=[81:2.2:88])translate([x,y,D-2])cylinder(d=1.2,h=3);
  if(variant=="explore"){
   translate([8.9,10,D-2])cube([48.96,36.72,3]);
   translate([3.17,6.8,19.35])cube([60.66,43.12,2.9]);
   translate([5.8,8.3,22.1])cube([55.4,40.4,1]);
  }
  if(variant=="mini")translate([32.5,24,D-.3])linear_extrude(.4)difference(){circle(d=26);circle(d=25.2);}
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
  // Strap anchors accept a soft hook-and-loop band; never clamp the pouch.
  for(x=[10.5,53.5])translate([x,49,1.7])cube([2,8,2.5]);
 }
 ports();
 for(h=holes)translate([h[0],h[1],11.6])cylinder(d=6.4,h=3);
 // Antenna overhang clearance at the top seam (plastic lip only).
 translate([22.9,2.5,11.6])cube([19.2,1.2,2.3]);
 for(h=holes){translate([h[0],h[1],-.1])cylinder(d=2.3,h=11);translate([h[0],h[1],-.1])cylinder(d=4.2,h=2.3);}
 for(x=[10,W-10])translate([x-2.3,1.3,12])cube([4.6,2,4.5]);
 for(x=[10.5,53.5])translate([x-.1,50,2.4])cube([2.2,6,1]);
 }}
 module bridge(){difference(){union(){
  intersection(){translate([0,0,S-.8])linear_extrude(.8)hull()for(q=keeper_posts)translate(q)circle(r=2);translate([0,0,0])cube([W,93.1,D]);}
  hull()for(q=[[38.6725,84.2],[40.6479,89.3]])translate([q[0],q[1],S-1.8])cylinder(r=.6,h=1.05);
 }for(q=keeper_posts)translate([q[0],q[1],S-2])cylinder(d=1.8,h=2.2);}}
 module keeper_heads(){for(q=keeper_posts)translate([q[0],q[1],S-2.1])cylinder(d=3.2,h=1.3);}
 module cap(){
  // Actual actuator top13.6, rest clearance0.1; verify travel before powered use.
  translate([0,0,13.7])cylinder(d=3,h=D-1.8-13.7-1.2);
  translate([0,0,D-3])cylinder(d1=9,d2=7,h=1);
  translate([0,0,D-2])cylinder(d=7,h=2.6);
 }
 module pcb(){difference(){color(variant=="mini"?[.05,.32,.20]:[.06,.24,.50])translate([0,0,10.5])linear_extrude(1.2)polygon([[3.5,9],[61.5,9],[62.5,10],[62.5,91],[61.5,92],[3.5,92],[2.5,91],[2.5,10]]);for(h=holes)translate([h[0],h[1],10.4])cylinder(d=2.2,h=1.5);}}
 module components(){for(i=[0:len(bodies)-1])let(b=bodies[i])
  if(body_refs[i]=="SW9"){
   // Manufacturer housing and side actuator; full Fab bounding box would
   // incorrectly fill the empty space beside the small recessed lever.
   color([.6,.6,.6])translate([3.2,40.5,11.7])cube([3.6,9,3.5]);
   color([.1,.1,.1])translate([1.2,43,12.4])cube([2.1,1.5,1.6]);
  } else color(body_refs[i][0]=="C"?[.64,.48,.28]:[.13,.15,.17])translate([b[0],b[1],b[2]])cube([b[3],b[4],b[5]]);
 }
 module peripherals(check_mount=false){for(i=[0:len(extras)-1])let(b=extras[i],n=extra_names[i])if(!(check_mount && n=="nfc_antenna"))color(n=="cell"?[.9,.6,.17]:n=="nfc"?[.05,.3,.7]:n=="nfc_antenna"?[.65,.35,.12]:[.1,.15,.2])translate([b[0],b[1],b[2]+(check_mount && n=="speaker"?.001:0)])cube([b[3],b[4],b[5]-(check_mount && n=="speaker"?.001:0)]);}
 module assembly(explode=0){bridge();color([.6,.6,.6])keeper_heads();color([.88,.88,.83])back();translate([0,0,explode]){pcb();components();peripherals();}translate([0,0,explode*2]){color([.95,.92,.83])front();color([.1,.48,.6])for(b=buttons)translate([b[0],b[1],0])cap();}}
 module dispatch(){
 if(part=="front")front();
 else if(part=="back")back();
 else if(part=="print_front")translate([0,0,D])mirror([0,0,1])front();
 else if(part=="bridge")translate([0,0,S])mirror([0,0,1])bridge();
 else if(part=="button")translate([0,0,D+.6])rotate([180,0,0])cap();
 else if(part=="buttons")for(i=[0:len(buttons)-1])translate([6+(i%4)*12,6+floor(i/4)*12,D+.6])rotate([180,0,0])cap();
 else if(part=="pcb")pcb();
 else if(part=="components")components();
 else if(part=="peripherals")peripherals();
 else if(part=="shell_interference")intersection(){front();back();}
 else if(part=="interference")intersection(){union(){front();back();bridge();keeper_heads();}union(){components();peripherals(true);}}
 else if(part=="exploded")assembly(20);
 else if(part=="section_x")intersection(){assembly();translate([W/2,-1,-1])cube([W,H+2,D+2]);}
 else if(part=="section_y")intersection(){assembly();translate([-1,H/2,-1])cube([W+2,H,D+2]);}
 else if(part=="coupon")difference(){cube([26,16,3]);translate([7,8,-.1])cylinder(d=7.4,h=3.2);translate([19,8,-.1])cylinder(d=3,h=3.2);translate([19,3,-.1])cylinder(d=1.25,h=3.2);}
 else assembly();
 }
 // Canonical PCB coordinates have Y downward. Meshes use physical right-handed
 // coordinates Yout=H-Y so the printed housing matches manufactured KiCad boards.
 if(part=="print_front" || part=="bridge" || part=="button" || part=="buttons" || part=="coupon")dispatch();
 else translate([0,H,0])mirror([0,1,0])dispatch();

}
