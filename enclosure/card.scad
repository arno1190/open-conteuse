// Current story cartridge. Canonical XY: left/right and handle-to-tip.
// A reinforced passive ROM-ID PCB occupies the foot; no audio storage.
$fn=48;
part=is_undef(part)?"assembly":part;
module card_outline(){union(){translate([2,2])offset(r=2)square([36,56]);translate([0,2])offset(r=2)translate([0,0])square([40,16]);}}
module card_blank(){linear_extrude(4.3)card_outline();}
module contact_ramp_cut(x){
 // Ramp joins exposed PCB pad plane0.5 at Y59 and rises to1.15 at the tip.
 // No rear plastic at Z0 can pass over the springs in their travel lanes.
 polyhedron(points=[[x,59,-.1],[x+3.6,59,-.1],[x+3.6,60.1,-.1],[x,60.1,-.1],[x,59,.5],[x+3.6,59,.5],[x+3.6,60.1,1.215],[x,60.1,1.215]],faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]);
}
module card_common(){difference(){card_blank();
 // Matched asymmetric key and side detent. Only one insertion orientation.
 translate([-.1,19.9,.65])cube([1.2,40.3,1]);
 translate([0,28,2.4])cylinder(r=1,h=1.5);
 // PCB seat and chip cavity. Outline clearance is0.15 per edge.
 translate([9.85,46.85,.5])cube([20.3,12.3,2.9]);
 for(x=[15.2,21.2]){translate([x,47,-.1])cube([3.6,12.001,.601]);contact_ramp_cut(x);}
 for(x=[8,32])translate([x,4,-.1])cylinder(d=1.8,h=4.5);
 // Artwork recess; supplied label is not a manufacturer part.
 translate([3,4,4.1])cube([34,39,.3]);
}}
module card_back(){union(){difference(){intersection(){card_common();translate([-3,-3,-1])cube([46,66,3]);}for(x=[8,32])translate([x,4,.8])cylinder(d=4.3,h=1.4);}
 // Polymer locating pegs pass through the two NPTH holes.
 for(q=[[12,49],[28,57]])translate([q[0],q[1],.45])cylinder(d=1.5,h=1.05);
}}
module card_front(){difference(){union(){
 intersection(){card_common();translate([-3,-3,2])cube([46,66,3]);}
 // Blind screw bosses are in the exposed handle, outside the player's RF region.
 for(x=[8,32])translate([x,4,1])cylinder(d=4,h=3.1);
 // PCB corner keepers contact only bare board margins.
 for(q=[[11,48],[29,58]])translate([q[0]-.5,q[1]-.5,1.3])cube([1,1,2.8]);
 }for(x=[8,32])translate([x,4,.9])cylinder(d=1.25,h=2.9);
}}
module card_board(){translate([10,47,.5])difference(){cube([20,12,.8]);for(q=[[2,2],[18,10]])translate([q[0],q[1],-.1])cylinder(d=1.8,h=1);}}
module card_assembly(){color([.07,.32,.38])card_back();color([.08,.42,.48])card_front();color([.04,.25,.15])card_board();color([.06,.06,.06])translate([18.12,51.03,1.3])cube([3.76,3.94,1.5]);
 for(x=[8,32])color([.6,.6,.6])translate([x,4,-1.3])cylinder(d=3.2,h=1.3);
}
if(part=="back")translate([0,60,0])mirror([0,1,0])card_back();
else if(part=="front")translate([0,60,0])mirror([0,1,0])card_front();
else if(part=="print_front")translate([0,0,4.3])mirror([0,0,1])card_front();
else if(part=="pcb")translate([0,60,0])mirror([0,1,0])card_board();
else card_assembly();
