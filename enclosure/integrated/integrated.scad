// Open Conteuse integrated modular prototype, mm. Original MIT geometry.
// Single geometry source; catalogue/poses generated from hardware/integration.
// Manufacturer meshes are assembly references, NEVER printable case solids.
include <generated_data.scad>
variant = "mini"; // mini, explore
part = "assembly"; // front, lid, carrier, battery_cover, mcu_retainer, regulator_retainer, switch_retainer, button, coupon, speaker_spacer, assembly
exploded = 0;
show_parts = true;
$fn = 48;
eps = 0.05;
wall = case_wall;
W = case_width; H = case_height;
F = case_front_depth; T = case_lid_thickness;
fit = case_fit_clearance;
C = case_carrier_z; CT = case_carrier_thickness;
assert(variant=="mini" || variant=="explore", "unknown variant");
function cat(id) = [for(r=catalog_rows) if(r[0]==id) r][0];
function all_poses() = concat(common_poses,variant=="mini"?mini_poses:explore_poses);
function pose(id) = [for(p=all_poses()) if(p[0]==id) p][0];
function d(id) = cat(id)[1];
function envelope(id) = cat(id)[2];
function has(id) = len([for(p=all_poses()) if(p[0]==id) p])>0;
function rotpoint(id,v) = let(a=pose(id)[2],dim=d(id))
    a==0?v:a==90?[dim[1]-v[1],v[0],v[2]]:a==180?[dim[0]-v[0],dim[1]-v[1],v[2]]:[v[1],dim[0]-v[0],v[2]];
function globalpoint(id,v) = pose(id)[1]+rotpoint(id,v);
function pcbpoint(id,xy) = globalpoint(id,cat(id)[3]+[xy[0],xy[1],0]);
function populated(i) = variant=="explore" || i==1 || i==3 || i==4 || i==6 || i==7;
module rounded(w,h,z,r=3) {hull() for(x=[r,w-r],y=[r,h-r]) translate([x,y,0]) cylinder(r=r,h=z);}
module hexvoid(af,h) {rotate([0,0,30]) cylinder(d=af/cos(30),h=h,$fn=6);}
module nut_post(x,y,z0,top,diameter=7.8) {
    assert(top>z0,"negative post");
    difference() {
        translate([x,y,z0-eps]) cylinder(d=diameter,h=top-z0+eps);
        translate([x,y,max(0.6,top-4.8)]) cylinder(d=case_screw_clearance,h=5.0);
        translate([x,y,top-case_nut_height-case_nut_height_clearance])
            hexvoid(case_nut_af+case_nut_af_clearance,case_nut_height+case_nut_height_clearance+eps);
    }
}
module fixpoints(id,base) {
    for(xy=cat(id)[5]) let(p=pcbpoint(id,xy)) nut_post(p[0],p[1],base,p[2]);
}
module at_part(id) {
    p=pose(id);dim=d(id);
    translate(p[1])
    if(p[4]=="actuator_outward_right")
        multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) children();
    else if(p[2]==0) children();
    else if(p[2]==90) translate([dim[1],0,0]) rotate([0,0,90]) children();
    else if(p[2]==180) translate([dim[0],dim[1],0]) rotate([0,0,180]) children();
    else translate([0,dim[0],0]) rotate([0,0,270]) children();
}
module screw_clearances(height) {
    for(p=case_case_fasteners) translate([p[0],p[1],-eps]) cylinder(d=case_screw_clearance,h=height+2*eps);
}
module case_wall_brace(p) {
    // Reinforce the long post into both walls; do not rely on a touching plane.
    x=p[0];y=p[1];left=x<W/2;top=y<H/2;
    translate([left?0:x,y-1.2,wall-eps]) cube([left?x:W-x,2.4,F-wall+eps]);
    translate([x-1.2,top?0:y,wall-eps]) cube([2.4,top?y:H-y,F-wall+eps]);
}
module carrier_bracket(p) {
    // Brackets begin above the tallest front PCB, so no floor post pierces it.
    x=p[0];y=p[1];left=x<W/2;
    translate([left?wall-eps:x,y-4,12]) cube([left?x-wall+eps:W-wall-x+eps,8,C-12]);
    nut_post(x,y,12,C);
}
module port_cuts() {
    usb=globalpoint("charger",[15.875,26.386,2.67]);
    translate([usb[0]-7.2,-eps,usb[2]-4.8]) cube([14.4,wall+0.5,9.6]);
    hp=globalpoint("headphone",[33.537,16.75915,3.87248]);
    translate([W-wall-eps,hp[1],hp[2]]) rotate([0,90,0]) cylinder(d=13,h=wall+2*eps);
    // Conservative full source-envelope cut; actuator/body drawing remains a fit gate.
    sw=pose("power_switch")[1];
    translate([W-wall-eps,sw[1]-.3,sw[2]-.3]) cube([wall+2*eps,12.3,4.6]);
}
module front_windows() {
    if(variant=="explore") {
        // Whole glass aperture derived from 2090's 50 x 69 mm manufacturer glass model bounds.
        at_part("display") translate([5.942,5.55,-4]) cube([50.6,69.6,8]);
    } else {
        // Portrait ID-1 card guide pocket on outer face; no opening to electronics.
        translate([11,9,-eps]) rounded(55,87,1.1,3);
    }
    // Grille follows the actual enclosed-speaker face in the selected orientation.
    at_part("speaker")
        for(x=[10:5:60],y=[10:5:20]) translate([x,y,-pose("speaker")[1][2]-eps]) cylinder(d=2,h=wall+2*eps);
    // Button locations come from the native controls PCB geometry.
    for(i=[0:7]) if(populated(i)) let(p=pose("controls")[1]+[control_centres[i][0],control_centres[i][1],0])
        translate([p[0],p[1],-eps]) cylinder(d=5.85,h=wall+2*eps);
}
module card_guides() {
    // Rails open at the top; ID-1 card is outside the case and captive laterally.
    for(x=[8,67.0]) translate([x,5,-2]) cube([2.4,93,2.45]);
    translate([8,97.8,-2]) cube([61.4,2.4,2.45]);
}
module front() {
    difference() {
        union() {
            difference() {
                rounded(W,H,F,case_radius);
                translate([wall,wall,wall]) rounded(W-2*wall,H-2*wall,F,case_radius-wall);
            }
            for(p=case_case_fasteners) {nut_post(p[0],p[1],wall,F);case_wall_brace(p);}
            for(p=case_carrier_fasteners) carrier_bracket(p);
            fixpoints("controls",wall);
            if(has("nfc")) fixpoints("nfc",wall);
            if(has("display")) fixpoints("display",wall);
            // Four flange holes of the sealed speaker, no guessed circular driver basket.
            for(xy=cat("speaker")[7]) let(p=globalpoint("speaker",[xy[0],xy[1],0]))
                nut_post(p[0],p[1],wall,p[2]+1.0);
        }
        front_windows();port_cuts();
        for(id=["controls",variant=="mini"?"nfc":"display"]) for(xy=cat(id)[5]) let(p=pcbpoint(id,xy)) {
            translate([p[0],p[1],max(.6,p[2]-4.8)]) cylinder(d=case_screw_clearance,h=5+eps);
            translate([p[0],p[1],p[2]-2.25]) hexvoid(5.3,2.25+eps);
        }
        // Subtract through the completed floor/post union: shallow speaker posts
        // would otherwise have their nut recess filled by the front floor.
        for(xy=cat("speaker")[7]) let(p=globalpoint("speaker",[xy[0],xy[1],0])) {
            translate([p[0],p[1],p[2]+1-2.25]) hexvoid(5.3,2.25+eps);
            translate([p[0],p[1],.6]) cylinder(d=case_screw_clearance,h=p[2]+1-.6+eps);
        }
    }
    // External card rails deferred: flat print face is retained.
}
module lid() {
    difference() {
        union() {
            rounded(W,H,T,case_radius);
            translate([wall+fit,wall+fit,T-eps]) difference() {
                rounded(W-2*(wall+fit),H-2*(wall+fit),2+eps,case_radius-wall-fit);
                translate([1.2,1.2,-eps]) rounded(W-2*(wall+fit+1.2),H-2*(wall+fit+1.2),2+3*eps,case_radius-wall-fit-1.2);
            }
        }
        screw_clearances(T+3);
        for(p=case_case_fasteners) translate([p[0],p[1],T-eps]) cylinder(d=8.6,h=2+2*eps);
        // Relieve lip around the carrier's wall brackets and slide-switch wires.
        for(p=case_carrier_fasteners) translate([p[0]-5,p[1]-5,T-eps]) cube([10,10,3]);
    }
}
module battery_cage() {
    // Rigid cage carries the strap tension; the cell is not cinched/compressed.
    translate([52.8,76.8,C+CT-eps]) difference() {
        rounded(54.4,66.4,11.5+eps,2);
        translate([1.4,1.4,-eps]) rounded(51.6,63.6,12,0.6);
        // Battery JST lead exit. Every cut retains the continuous base attachment.
        translate([15,-eps,1.0]) cube([18,3,7]);
        for(y=[13.2,50.2]) for(x=[-eps,52.8]) translate([x,y-2,-eps]) cube([2,4,12]);
    }
    // Broad supports, not sharp pressure points underneath the pouch.
    for(y=[82,107,132]) translate([54.2,y,C+CT-eps]) cube([51.6,6,1.0+eps]);
}
module frame_cradle(x,y,w,h,z,height) {
    // Open bottom and generous component envelope; capture with a removable bar.
    translate([x-1.4,y-1.4,z-eps]) difference() {
        rounded(w+2.8,h+2.8,height+eps,1);
        translate([1.0,1.0,-eps]) cube([w+0.8,h+0.8,height+3*eps]);
    }
}
module mcu_cradle() {
    p=pose("mcu")[1];
    // 64 mm inner length covers the official DXF/annotation difference.
    // Z is an adjustable design reservation; published assembled-height is missing.
    frame_cradle(p[0],p[1],26,64,C+CT,10);
    // Edge seats keep clear of the two header rows; pins/socket leads pass below.
    for(x=[p[0]-.9,p[0]+25]) translate([x,p[1]+4,C+CT+9.4]) cube([1.9,56,.6]);
    for(y=[p[1]-2.5,p[1]+66.5]) for(x=[p[0]+3,p[0]+23]) nut_post(x,y,C+CT,C+CT+10);
}
module regulator_cradle() {
    p=pose("regulator")[1];dim=envelope("regulator");
    frame_cradle(p[0],p[1],dim[0],dim[1],C+CT,p[2]-C-CT+dim[2]+.3);
    // Small ventilated ledges support the assembly envelope without a solid hot pad.
    for(x=[p[0]-1,p[0]+dim[0]-1]) translate([x,p[1],C+CT-eps]) cube([2,dim[1],p[2]-C-CT+eps]);
    for(y=[p[1]-3,p[1]+dim[1]+3]) nut_post(p[0]+dim[0]/2,y,C+CT,p[2]+dim[2]+.3);
}
module switch_cradle() {
    p=pose("power_switch")[1];
    // Retain metal body behind the smaller actuator opening, no free loose switch.
    translate([p[0]-1.4,p[1]-1.4,C+CT-eps]) difference() {
        cube([6.4,14.5,p[2]-C-CT+5.4+eps]);
        translate([1.05,1.05,p[2]-C-CT-.35]) cube([8.8,12.4,4.7]);
    }
    for(y=[p[1]-3.5,p[1]+15.2]) nut_post(p[0]+1.3,y,C+CT,p[2]+4.35);
}
module carrier_raw() {
    difference() {
        union() {
            translate([wall+fit,wall+fit,C]) rounded(W-2*(wall+fit),H-2*(wall+fit),CT,case_radius-wall-fit);
            for(id=["charger","sd","headphone","speaker_amp","mute_latch"]) fixpoints(id,C+CT);
            battery_cage();mcu_cradle();regulator_cradle();switch_cradle();
        }
        // Final union must not refill short standoffs' blind screw bores.
        for(id=["charger","sd","headphone","speaker_amp","mute_latch"]) for(xy=cat(id)[5]) let(p=pcbpoint(id,xy)) {
            translate([p[0],p[1],max(C+.6,p[2]-4.8)]) cylinder(d=case_screw_clearance,h=5+eps);
            translate([p[0],p[1],p[2]-2.25]) hexvoid(5.3,2.25+eps);
        }
        // Native connector pins and service harness pass through the MCU well.
        p=pose("mcu")[1];translate([p[0]-.2,p[1]+1.5,C-eps]) cube([26.4,61,CT+2*eps]);
        for(p=case_case_fasteners) translate([p[0],p[1],C-eps]) cylinder(d=8.6,h=CT+2*eps);
        for(p=case_carrier_fasteners) translate([p[0],p[1],C-eps]) cylinder(d=case_screw_clearance,h=CT+2*eps);
        // Cell ventilation + two tie passage pairs. No wire or strap contacts cell.
        for(x=[59:10:99],y=[85:14:127]) translate([x,y,C-eps]) rounded(5,8,CT+2*eps,1);
        for(y=[90,127]) for(x=[51.4,106.4]) translate([x,y-2,C-eps]) cube([2.8,4,CT+2*eps]);
        // Lightening/service slots in unoccupied regions, with >=4 mm ribs.
        for(y=[120:12:144]) translate([14,y,C-eps]) rounded(28,6,CT+2*eps,1);
    }
}
module carrier() {translate([0,0,-C]) carrier_raw();}
module battery_cover() {
    difference() {
        rounded(54.4,66.4,2,2);
        for(y=[4,24,44]) translate([4,y,-eps]) rounded(46.4,10,2+2*eps,1);
    }
}
module mcu_retainer() {
    difference() {
        union() {
            rounded(28,5,2.4,1);
            // Short edge fingers capture the PCB ends, clear of central USB ports.
            // Height remains adjustable until actual assembled board is measured.
            for(x=[2,24]) translate([x,1.5,1.65]) cube([2,5,.55]);
        }
        for(x=[4,24]) translate([x,2.5,-1]) cylinder(d=case_screw_clearance,h=5);
    }
}
module regulator_retainer() {
    dim=envelope("regulator");
    difference() {
        rounded(5,dim[1]+8,2.4,1);
        for(y=[1,dim[1]+7]) translate([2.5,y,-eps]) cylinder(d=case_screw_clearance,h=2.5);
        translate([1.3,3.2,-eps]) cube([2.4,dim[1]+1.6,1.0]);
    }
}
module switch_retainer() {
    difference() {
        rounded(5.8,22.2,2.4,1);
        for(y=[1.6,20.3]) translate([2.9,y,-eps]) cylinder(d=case_screw_clearance,h=2.5);
    }
}
module button() {
    // Print head down. Install from INSIDE before PCB: internal head retains stem.
    // Head contact face at Z4.4; switch top Z4.6 leaves .2 mm nominal travel gap.
    union() {cylinder(d=8,h=1.2);translate([0,0,1.15]) cylinder(d=5.2,h=4.45);}
}
module speaker_spacer() {
    // Rigid PETG spacer; not called a compliant gasket or an acoustic seal.
    difference() {
        rounded(70,30,4,2);
        translate([8,8,-eps]) rounded(54,14,4.2,2);
        for(p=cat("speaker")[7]) translate([p[0],p[1],-eps]) cylinder(d=8.2,h=4.2);
    }
}
module coupon() {
    difference() {
        cube([84,28,3]);
        for(i=[0:2]) translate([9+i*14,9,.7]) hexvoid(5+[.15,.30,.45][i],2.5);
        for(i=[0:2]) translate([9+i*14,20,-eps]) cylinder(d=5.5+[.25,.35,.45][i],h=3.2);
        translate([52,6,-eps]) cube([14.4,9.6,3.2]);
        translate([75,15,-eps]) cylinder(d=13,h=3.2);
    }
}
module native_part(id) {
    r=cat(id);
    at_part(id) if(r[6]!="") import(str("models/",r[6]));
    else if(id=="mcu") {
        // Explicit reservation: actual published assembled-height is unavailable.
        color([.3,.55,.65,.45]) cube(envelope(id));
    } else if(id=="regulator") {
        color([.3,.45,.3,.7]) cube(envelope(id));
    } else if(id=="controls") {
        color("seagreen") cube([70,65,1.6]);
        for(i=[0:7]) if(populated(i)) translate([control_centres[i][0]-3,control_centres[i][1]-3,-4.3]) color("gray") cube([6,6,4.3]);
    } else if(id=="mute_latch") {
        color("seagreen") cube([45,45,1.6]);
        for(x=[13,29]) translate([x-.5,6,1.6]) color("dimgray") cube([8.62,19.3,4.7]);
    }
}
module assembly() {
    color([.75,.84,.79,.35]) front();
    translate([0,0,exploded]) color("#748f84") carrier_raw();
    translate([52.8,76.8,C+CT+11.5+exploded]) color("#8b9c91") battery_cover();
    translate([11,3,39.4+exploded]) color("#8b9c91") mcu_retainer();
    translate([39,77,39.4+exploded]) rotate([0,0,180]) color("#8b9c91") mcu_retainer();
    translate([46.85,6,37+exploded]) color("#8b9c91") regulator_retainer();
    translate([102.6,39.9,pose("power_switch")[1][2]+4.35+exploded]) color("#8b9c91") switch_retainer();
    at_part("speaker") translate([0,0,-4]) color("#8b9c91") speaker_spacer();
    if(show_parts) for(p=all_poses()) translate([0,0,p[3]=="carrier"?exploded:0]) color(p[0]=="battery"?"orange":"#aab9ae") native_part(p[0]);
    for(i=[0:7]) if(populated(i)) let(p=pose("controls")[1]+[control_centres[i][0],control_centres[i][1],0])
        translate([p[0],p[1],4.4]) mirror([0,0,1]) color("tan") button();
    translate([0,0,case_depth+2*exploded]) mirror([0,0,1]) color([.68,.79,.72,.6]) lid();
}
if(part=="front") front();
else if(part=="lid") lid();
else if(part=="carrier") carrier();
else if(part=="battery_cover") battery_cover();
else if(part=="mcu_retainer") mcu_retainer();
else if(part=="regulator_retainer") regulator_retainer();
else if(part=="switch_retainer") switch_retainer();
else if(part=="button") button();
else if(part=="speaker_spacer") speaker_spacer();
else if(part=="coupon") coupon();
else if(part=="assembly") assembly();
else assert(false,"unknown part");
