// box to insert pcb and fix with 2 screws
// for factory made PCB (not universal pcb)

pcb_size = [17.9,34,1.6]; // size of PCB

box_inner = [18.1,37,21+2.5];
thick = 2;

rail_top   = [0.9,13,2];
rail_bot   = [0.9,30,2];
rail_spc   = 2.5;
// todo rail from rear, 45 deg cut
// rail_rear  = 4;

pcb_bottom = 2.5+3; // space from bottom
usb_pos = 14; // from PCB bottom

module pcb()
{
  translate([0,-thick/2,box_inner[2]/2-rail_bot[2]/2-pcb_bottom])
  cube(pcb_size,center=true);
}

module rounded_cube(v,r)
{
  minkowski()
  {
    h_minkowski=0.01;
    cube(v-[2*r,2*r,h_minkowski],center=true);
    cylinder(h=h_minkowski,r=r,$fn=90,center=true);
  };
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
  translate([-i*rail_bot[0]/2,(-rail_bot[1]+box_inner[1])/2-thick,rail_bot[2]/2+rail_spc/2])
    cube(rail_bot,center=true);
  translate([-i*rail_top[0]/2,(-rail_top[1]+box_inner[1])/2-thick,-rail_top[2]/2-rail_spc/2])
    cube(rail_top,center=true);
}

// make space for antenna cable
module rail_cut(i)
{
  translate([-i*rail_bot[0]/2-i*2,(-rail_bot[1]*0+box_inner[1])/2-thick,rail_bot[2]/2+rail_spc/2])
    rotate([0,0,-30*i])
    cube([5,5,40],center=true);
}

module rails()
{
  for(i=[-1,1])
    translate([(box_inner[0]/2)*i,0,box_inner[2]/2-rail_bot[2]/2-pcb_bottom])
      difference()
      {
        rail(i);
        rail_cut(i);
      }
}

// not used
module usb_connector_cut()
{
  translate([0,-box_inner[1]/2,+box_inner[2]/2-pcb_bottom-usb_pos])
  cube([31,10,6],center=true);
}

module rj12_connector_cut_rear()
{
  translate([0,box_inner[1]/2,+box_inner[2]/2-pcb_bottom-8.5])
  cube([14.5,10,13.5],center=true);
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
    cube_dim=box_inner+[2,1,2]*thick;
    rotate([90,0,0])
    rounded_cube([cube_dim[0],cube_dim[2],cube_dim[1]],r=3);
    translate([0,-thick,0])
    rotate([90,0,0])
    rounded_cube([box_inner[0],box_inner[2],box_inner[1]],r=1.8);
    // usb_connector_cut();
    rj12_connector_cut_rear();
    //rj12_connector_cut_side();
    // screw_holes();
  }
  rails();
}

box();
%pcb();

