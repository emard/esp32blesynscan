from umatrix import * # https://github.com/iyassou/umatrix
from math import *

# example rotating a vector around axis
# https://en.wikipedia.org/wiki/Rotation_matrix

# astro change of basis
# https://en.wikipedia.org/wiki/Astronomical_coordinate_systems#Converting_coordinates

# vector length or magnitude
def mag(v):
  return sqrt((v*v.transpose)[0][0])

# rotation matrix given angle and unit vector
def rotm(a,u):
  return matrix([u[0]*u[0]*(1-cos(a))     +cos(a), u[0]*u[1]*(1-cos(a))-u[2]*sin(a), u[0]*u[2]*(1-cos(a))+u[1]*sin(a)],
                [u[0]*u[1]*(1-cos(a))+u[2]*sin(a), u[1]*u[1]*(1-cos(a))     +cos(a), u[1]*u[2]*(1-cos(a))-u[0]*sin(a)],
                [u[0]*u[2]*(1-cos(a))-u[1]*sin(a), u[1]*u[2]*(1-cos(a))+u[0]*sin(a), u[2]*u[2]*(1-cos(a))     +cos(a)])

# applied example rotating a vector around axis
# +angle: counter-clockwise direction, -angle: clockwise direction
def rota(vector,angle,axis):
  print("vector", vector, "rotate %.1f°" % angle, "around axis", axis)

  # calculate unit vector "u"
  axis_invabs = 1/mag(matrix(axis))
  u = matrix(axis).apply(lambda x: x*axis_invabs)[0] # convert to unit vector
  print("unit axis:", u, "len:", mag(matrix(u)))

  # convert angle to radians
  angle_rad = angle*pi/180

  RM = rotm(angle_rad,u)
  print("rotation matrix")
  print(RM)
  print("rotated vector")
  print(RM*matrix(vector).transpose)

vector = [1,0,0] # x,y,z
angle  = 90      # [°]
axis   = [0,0,1] # x,y,z
print("example rotation.rota(",vector,",",angle,",",axis,")")
rota(vector,angle,axis)
