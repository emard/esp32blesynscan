// box to insert pcb and fix with 2 screws

pcb_size = [19,39,1.6]; // size of PCB

box_inner = [22,40,21+3];
thick = 2;

rail_top   = [2,40,2];
rail_bot   = [3,40,2];
rail_spc   = 2;

pcb_bottom = 2.5+3; // space from bottom
usb_pos = 14; // from PCB bottom

module pcb()
{
  translate([0,0,box_inner[2]/2-rail_bot[2]/2-pcb_bottom])
  cube(pcb_size,center=true);
}

module rail_old()
{
  difference()
  {
    cube(rail_outer,center=true);
    cube(rail_inner,center=true);
  }
}

module rail(i)
{
  translate([-i*rail_bot[0]/2,0,rail_bot[2]/2+rail_spc/2])
    cube(rail_bot,center=true);
  translate([-i*rail_top[0]/2,0,-rail_top[2]/2-rail_spc/2])
    cube(rail_top,center=true);
}

module rails()
{
  for(i=[-1,1])
    translate([(box_inner[0]/2)*i,0,box_inner[2]/2-rail_bot[2]/2-pcb_bottom])
      rail(i);
}

// not used
module usb_connector_cut()
{
  translate([0,-box_inner[1]/2,+box_inner[2]/2-pcb_bottom-usb_pos])
  cube([31,10,6],center=true);
}

module rj12_connector_cut_rear()
{
  translate([0,box_inner[1]/2,+box_inner[2]/2-pcb_bottom-10])
  cube([15,10,16],center=true);
}

module rj12_connector_cut_side()
{
  translate([0,box_inner[1]/2-10,+box_inner[2]/2-pcb_bottom-16])
  cube([13,16,10],center=true);
}

// not used - can't screw thru antenna
module screw_holes()
{
  for(i=[-1,1])
  translate([i*2.54*3,box_inner[1]/2-6,box_inner[2]/2])
    cylinder(d=1.8,h=10,$fn=16,center=true);
}

module box()
{
  difference()
  {
    cube(box_inner+[2,1,2]*thick,center=true);
    translate([0,-thick,0])
    cube(box_inner,center=true);
    // usb_connector_cut();
    //rj12_connector_cut_rear();
    rj12_connector_cut_side();
    // screw_holes();
  }
  rails();
}

box();
%pcb();


