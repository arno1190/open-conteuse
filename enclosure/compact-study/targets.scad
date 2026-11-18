// Generated design envelopes only. NOT a fitted enclosure or printable release.
// [width,height,depth], mm. Reference dimensions are approximate, not measured.
$fn=48;
module envelope(d) {minkowski(){cube([d[0]-6,d[1]-6,d[2]-6]);sphere(r=3);}}
// Current modular Mini / Explore: existing CAD
translate([3,3,3]) envelope([112, 210, 50]);
// Miyoo Mini reference: seller-advertised comparison envelope; not a measured mechanical drawing
translate([133,3,3]) envelope([65, 93.5, 18]);
// Miyoo Mini Plus reference: rounded seller-advertised comparison envelope; not a measured mechanical drawing
translate([216,3,3]) envelope([78, 108, 22]);
// Custom Mini target: design target only
translate([312,3,3]) envelope([65, 95, 22]);
// Custom Explore target: design target only
translate([395,3,3]) envelope([65, 100, 24]);
// Explore 2.8 inch fallback target: design target only; exact raw panel not selected
translate([478,3,3]) envelope([73, 105, 24]);
