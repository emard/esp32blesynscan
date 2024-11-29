// box to insert pcb and fix with 2 screws

pcb_size = [31.5,100,1.6]; // size of PCB

box_inner = [33,104,21];
thick = 2;

rail_outer = [2,100,6];
rail_inner = [3,101,2.5];

pcb_bottom = 2.5; // space from bottom
usb_pos = 14; // from PCB bottom

module pcb()
{
  translate([0,0,box_inner[2]/2-rail_inner[2]/2-pcb_bottom])
  cube(pcb_size,center=true);
}

module rail()
{
  difference()
  {
    cube(rail_outer,center=true);
    cube(rail_inner,center=true);
  }
}

module rails()
{
  for(i=[-1,1])
    translate([(box_inner[0]/2-rail_outer[0]/2)*i,0,box_inner[2]/2-rail_inner[2]/2-pcb_bottom])
      rail();
}

module usb_connector_cut()
{
  translate([0,-box_inner[1]/2,+box_inner[2]/2-pcb_bottom-usb_pos])
  cube([31,10,6],center=true);
}

module rj12_connector_cut()
{
  translate([0,box_inner[1]/2,+box_inner[2]/2-pcb_bottom-10])
  cube([15,10,16],center=true);
}

module screw_holes()
{
  for(i=[-1,1])
  translate([i*2.54*4.5,box_inner[1]/2-6,box_inner[2]/2])
    cylinder(d=1.8,h=10,$fn=16,center=true);
}

module box()
{
  difference()
  {
    cube(box_inner+[2,1,2]*thick,center=true);
    translate([0,-thick,0])
    cube(box_inner,center=true);
    usb_connector_cut();
    rj12_connector_cut();
    screw_holes();
  }
  rails();
}

box();
%pcb();


