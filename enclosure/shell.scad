// Open Conteuse provisional fit study; millimetres. No physical fit verified.
// Common shell, alternate front, screw-retained back. See DIMENSIONS.md.
variant = "mini"; // mini, explore
part = "front";   // front, back, coupon, assembly
$fn = 48;
width = 100;
height = 174;
depth = 38;
wall = 2.4;
corner = 8;
clearance = 0.35;
front_depth = 19;
// PCB origin (15,98). Footprint centres duplicated from controls.json,
// checked by scripts/check_cad.py. Coordinates viewed from front.
controls = [[22,12],[51,20],[22,34],[11,23],[33,23],[57,34],[45,49],[57,49]];
board_xy = [15,98];
holes = [[4,4],[66,4],[4,61],[66,61]];
case_screws = [[7,7],[93,7],[7,167],[93,167]];
assert(variant == "mini" || variant == "explore", "unknown variant");
assert(part == "front" || part == "back" || part == "coupon" || part == "assembly" || part == "plunger", "unknown part");
assert(wall >= 2 && depth >= 32 && width > 70 + 2*wall, "invalid shell dimensions");

module rounded(w,h,d,r) {
    hull() for(x=[r,w-r],y=[r,h-r]) translate([x,y,0]) cylinder(h=d,r=r);
}
module hollow(d) {
    difference() {
        rounded(width,height,d,corner);
        translate([wall,wall,wall]) rounded(width-2*wall,height-2*wall,d,corner-wall);
    }
}
module boss(x,y,z,d=6,bore=2.1,h=8) {
    translate([x,y,z]) difference() { cylinder(h=h,d=d); cylinder(h=h+0.1,d=bore); }
}
module front() {
    difference() {
        union() {
            hollow(front_depth);
            for(p=case_screws) boss(p[0],p[1],wall-0.05,d=7,bore=2.1,h=front_depth-wall+0.05);
            // PCB stand-offs: board component side faces the front wall.
            for(p=holes) boss(board_xy[0]+p[0],board_xy[1]+p[1],wall-0.05,d=5.8,bore=2.1,h=6.55);
        }
        // Mini: previous / play / next on middle row; two volume buttons.
        // Explore uses all eight switches, with labels assigned by software.
        for(i=[0:7]) if(variant=="explore" || i==1 || i==3 || i==4 || i==6 || i==7)
            translate([board_xy[0]+controls[i][0],board_xy[1]+controls[i][1],-0.1]) cylinder(h=wall+0.2,d=5.5+clearance);
        if(variant=="explore")
            translate([21,17,-0.1]) cube([58,44,wall+0.2]); // visible display only
        else {
            // NFC card is retained outside the electronics cavity in a front pocket.
            // Window is shallow; no open card slot into battery compartment.
            translate([23,18,-0.1]) rounded(54,50,1.2,3);
        }
        // Speaker grille above controls. Driver keepout is provisional.
        for(x=[35:5:65],y=[78:5:88]) translate([x,y,-0.1]) cylinder(h=wall+0.2,d=2);
    }
    if(variant=="mini") {
        // Guide rails leave antenna area free of metal. Pocket fit is unmeasured.
        translate([20,14,-2]) cube([2.4,56,2.4]);
        translate([77.6,14,-2]) cube([2.4,56,2.4]);
        translate([20,69.8,-2]) cube([60,2.4,2.45]);
    }
}
module back() {
    difference() {
        hollow(depth-front_depth);
        for(p=case_screws) translate([p[0],p[1],-0.1]) cylinder(h=wall+0.2,d=2.8);
        // Recesses for screw heads; no speculative USB/jack cutouts.
        for(p=case_screws) translate([p[0],p[1],-0.1]) cylinder(h=1.3,d=5.2);
    }
    // Battery retention rails: service only after screw removal. No press fit on cell.
    translate([27,25,wall-0.05]) cube([2,68,6.05]);
    translate([71,25,wall-0.05]) cube([2,68,6.05]);
    translate([27,25,wall-0.05]) cube([46,2,6.05]);
}
module coupon() {
    difference() {
        cube([62,24,wall]);
        for(i=[0:3]) translate([9+i*14,12,-0.1]) cylinder(h=wall+0.2,d=5.5+[0.2,0.3,0.4,0.5][i]);
    }
    // M2.5 hole and pilot fit samples.
    for(i=[0:2]) boss(9+i*14,12,wall-0.05,d=6,bore=[2.0,2.1,2.3][i],h=6.55);
}
if(part=="front") front();
if(part=="back") back();
if(part=="coupon") coupon();
if(part=="assembly") {
    color("#d6e4cb",.7) front();
    translate([0,0,depth]) mirror([0,0,1]) color("#7ba79d",.5) back();
    // Visual keepouts only, not supplied mechanical models.
    color("green") translate([board_xy[0],board_xy[1],8.9]) cube([70,65,1.6]);
    color("orange",.6) translate([31,29,20]) cube([38,60,8]);
}

// Separate captive actuator, printed on the head, nominal 0.35 mm radial fit.
// Stem contact and travel MUST be measured using the fit coupon.
module plunger() {
    cylinder(h=1.2,d=8);
    translate([0,0,1.2]) cylinder(h=4.4,d=5.2);
    translate([0,0,4.0]) cylinder(h=.8,d=7);
}
if(part=="plunger") plunger();
