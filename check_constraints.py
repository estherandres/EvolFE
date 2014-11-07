# -*- coding: utf-8 -*-

#*******************************************************************************************#
#
#                  PYTHON SCRIPT FOR CHECKING GEOMETRIC CONSTRAINTS
#   propuesta.txt --> contains the dv z coordinates of the current geom
#   writes TRUE or FALSE in the file valid_geom.txt
#
#*******************************************************************************************#

DOMINOBIN_DIR = '/Users/estherandres/INTA/overview/130620_OVERVIEW/bin' #path to domino.so
TAUBIN_DIR = "/Users/estherandres/INTA/tau/taudir_release.2014.1.0/bin"

PROPUESTATXT="propuesta.txt"

import os
import sys
import math
sys.path.append(DOMINOBIN_DIR)
from domino import *


# ********************** FUNCTIONS *************************** #
def integral (x, y, interval):
    total=0;
    for i in range(0, interval-1):
        x0=x[i]
        x1=x[i+1]
        y0=y[i]
        y1=y[i+1]

        total+=abs(((x1-x0)*(y0+(y1-y0)/2)))
    return total

def num ( s ):
  try:
    return int(s)
  except ValueError:
    return float(s)

def init_cps(testcase, cps, cps_u2, length_v, length_w):
    if (testcase==0): #cilinder
        i=0
        for iv in range(0, length_v):
           for iw in range(0, length_w):
                if (iw==1): #or iw==3):
                     cps[i][0]=0
                     cps[i][1]=iv
                     cps[i][2]=iw
                     cps_u2[i][0]=1
                     cps_u2[i][1]=iv
                     cps_u2[i][2]=iw
                     i=i+1
                if (iw==2 and (iv==0 or iv == 2)):
                    cps[i][0]=0
                    cps[i][1]=iv
                    cps[i][2]=iw
                    cps_u2[i][0]=1
                    cps_u2[i][1]=iv
                    cps_u2[i][2]=iw
                    i=i+1

    elif(testcase==1): #rae2822
        # Indices de los cps a modificar del perfil:
        i=0
        for iv in range(1, 8):
            for iw in range(0, 4):
                if (iw==1 or iw==3):
                    cps[i]=[1,iv,iw]
                    cps_u2[i]=[2, iv, iw]
                    i=i+1

    else: #dpw
        i=0
        for iu in range(1, 4):
            for iv in range(2, 8):
                for iw in range (0, 4):
                    if (iw==1 or iw==3):
                        cps[i]=[iu, iv, iw]
                        i=i+1

    #print(cps)
    #print(cps_u2)
    return cps,cps_u2


def modify_nurbs ( nurbs_modif, testcase, numDV ):
  aux = [0 for x in xrange(numDV)]
  aux_u2 = [0 for x in xrange(numDV)]

  f=open(PROPUESTATXT,'r')
  newcoords=[]
  newcoords=[line.split() for line in f]
  print(newcoords)
  f.close()

  if (testcase==0): #CILINDER
     print("Modifying the cilinder nurbs")
     i=0
     for iv in range(0, nurbs.cp_length_v):
        for iw in range(0, nurbs.cp_length_w):
           if(iw==1 and iv!=0 and iv!=nurbs.cp_length_v-1):
               print i
               z=num(newcoords[0][i])
               i=i+1
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 1)
               cp.x=x
               cp.z=z

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 1)
               cp.x=x
               cp.z=z

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 3)
               cp.x=x
               cp.z=-z

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 3)
               cp.x=x
               cp.z=-z

           if(iw==1 and (iv==0 or iv==nurbs_modif.cp_length_v-1)):
               z=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 1)
               cp.z=z

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 1)
               cp.z=z

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 3)
               cp.z=-z

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 3)
               cp.z=-z


           if (iw==2 and iv==0):
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 3)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 3)
               cp.x=x

           if (iw==2 and iv==3):
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 0, iv, 3)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs_modif, 1, iv, 3)
               cp.x=x

  elif(testcase==1): #RAE2822
    print("Modifying the rae2822 nurbs")
    for i in range(0, numDV):
        aux[i] = nurbs_getControlPoint(nurbs_modif, cps[i][0],cps[i][1],cps[i][2])
        aux_u2[i] = nurbs_getControlPoint(nurbs_modif, cps_u2[i][0],cps_u2[i][1],cps_u2[i][2])

        # Deform the z coordinate according to the modification vector
        coord_cp[i][2] = num(newcoords[0][i]) #el 0 es por el numpropuestas

        aux[i].z=coord_cp[i][2]
        # En el RAE2822 hay que modificar también el otro lado porque es falso 3D
        aux_u2[i].z= coord_cp[i][2]

  else:  #DPW
     print("Modifying the dpw nurbs")
     for i in range(0, numDV):
         aux[i] = nurbs_getControlPoint(nurbs_modif, cps[i][0],cps[i][1],cps[i][2])

         # Deform the z coordinate according to the modification vector
         coord_cp[i][2] = num(newcoords[0][i]) #el 0 es por el numpropuestas

         aux[i].z=coord_cp[i][2]

  return nurbs_modif
# ********************** END FUNCTIONS *************************** #

FOLDER_CASE=sys.argv[1]
PARAM_FILE=sys.argv[2]
GRID_FILE=sys.argv[3]
NURBS_FILE=sys.argv[4]
numDV=int(sys.argv[5])
testcase = int(sys.argv[6]) #0: cilinder 1: rae2822 airfoil 2:dpw wing

print("RUNNING CONSTRAINTS CHECKING SCRIPT")
#print(FOLDER_CASE)
#print(PARAM_FILE)
#print(GRID_FILE)
#print(NURBS_FILE)
#print(numDV)
#print(testcase)

cps = [[0 for y in xrange(3)] for x in xrange(numDV)]
cps_u2 =[[0 for y in xrange(3)] for x in xrange(numDV)]
coord_cp= [[0 for y in xrange(3)] for x in xrange(numDV)]

#flags: 0 valid \  1 invalid
flag=1
flag1=0
flag2=0
flag3=0

os.chdir(FOLDER_CASE)
#print(os.getcwd())

# Reads the parameters file. We need it to know the panels
# The first argument is the working path and the second the filename
# The working path is used to search the boundary file,
# if they are not directly defined in the parameters file.
inpara = domino_read_params( ".", PARAM_FILE);

# Imports a NURBS; returns an array of NURBS.
nurbs, num_nurbs = nurbs_controlbox_import_ascii(NURBS_FILE)

# Checks if the NURBS is imported
if (nurbs == None):
  print( "Failed to load the NURBS!\n")
  exit(1)

# Read again the NURBS; to modify it.
nurbs_modif, num_nurbs2 = nurbs_controlbox_import_ascii(NURBS_FILE)

# Checks if the NURBS is imported
if (nurbs == None):
  print( "Failed to load the NURBS!\n")
  exit(1)


cps,cps_u2=init_cps(testcase, cps, cps_u2, nurbs.cp_length_v, nurbs.cp_length_w)

nurbs_modif=modify_nurbs (nurbs_modif, testcase, numDV)

if (testcase==0): #CILINDER
  print("Checking geometric constraints for the cilinder")
  # 1- Check volume constraint for the cilinder
  cilin_xcoords=[0 for x in xrange(201)]
  cilin_zcoords=[0 for x in xrange(201)]
  for i in range (0, 201):
      alpha = (i/200.0)*2*math.pi
      x=0.5*math.cos(alpha)
      z=0.5*math.sin(alpha)

      uvw, err = nurbs_controlbox_inversion_coords( nurbs, x, 0, z, 1e-8 )
      newcoord = nurbs_controlbox_get_point( nurbs_modif, uvw.x, uvw.y, uvw.z )
      cilin_xcoords[i] = newcoord.x
      cilin_zcoords[i] = newcoord.z

  volumen=integral(cilin_xcoords, cilin_zcoords, 201)
  print("Volumen: "+str(volumen))

  dif_volumen=abs(volumen-math.pi/4)/(math.pi/4)  #10% se permite variar el volumen considerando la forma válida
  if (dif_volumen<0.99): #20% de variación de volumen
      flag=0 # cumple la restriccion
  else:
      print("No cumple la restriccion del volumen")

  #comprobamos que las x no se cruzan
  for i in range (0, 100):
      if (cilin_xcoords[i] < cilin_xcoords[i+1]):
          flag=1
          print("Se cruzan las xs del cilindro")

elif(testcase==1): #RAE2822
  print("Checking geometric constraints for the rae2822")

  # 1 - Check restriction of maximum thickness ratio >=12.1% (Constraint 1)
  cp0_vector = [0 for x in xrange(7)]
  cp1_vector = [0 for x in xrange(7)]
  uvw0_vector = [0 for x in xrange(7)]
  uvw1_vector = [0 for x in xrange(7)]
  newcoord0_vector = [0 for x in xrange(7)]
  newcoord1_vector = [0 for x in xrange(7)]

  check_maxthickness = 1
  for i in range (0,7):
      cp0_vector[i]= nurbs_getControlPoint(nurbs, 1, i+1, 1)
      cp1_vector[i]= nurbs_getControlPoint(nurbs, 1, i+1, 3)

      uvw0_vector[i], err = nurbs_controlbox_inversion( nurbs, cp0_vector[i], 1e-8 )
      uvw1_vector[i], err = nurbs_controlbox_inversion( nurbs, cp1_vector[i], 1e-8 )

      newcoord0_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw0_vector[i].x, uvw0_vector[i].y, uvw0_vector[i].z )
      newcoord1_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw1_vector[i].x, uvw1_vector[i].y, uvw1_vector[i].z )

      if (abs(newcoord0_vector[i].z - newcoord1_vector[i].z) > 0.120):
          check_maxthickness=0
  if (check_maxthickness==1):
          flag1=1 #false
  print("Constraint Maximum thickness: " + str(flag1))

  # 2 - Check restriction of minimum thickness at 0.80c >= 4% (Constraint 2)
  cp0 = nurbs_getControlPoint(nurbs, 1, 6, 1)
  cp1 = nurbs_getControlPoint(nurbs, 1, 6, 3)

  uvw0, err = nurbs_controlbox_inversion( nurbs, cp0, 1e-8 )
  uvw1, err = nurbs_controlbox_inversion( nurbs, cp1, 1e-8 )

  newcoord0 = nurbs_controlbox_get_point( nurbs_modif, uvw0.x, uvw0.y, uvw0.z )
  newcoord1 = nurbs_controlbox_get_point( nurbs_modif, uvw1.x, uvw1.y, uvw1.z )

  if (newcoord0.z - newcoord1.z < 0.04):
      flag2=1 #false

  print("Constraint Minimum thickness at 0.80c: " + str(flag2))

  # 3 - Check restriction of minimum leading edge radius >=0.004
  cp0 = nurbs_getControlPoint(nurbs, 1, 1, 1)
  cp1 = nurbs_getControlPoint(nurbs, 1, 1, 2)
  cp2 = nurbs_getControlPoint(nurbs, 1, 1, 3)

  uvw0, err = nurbs_controlbox_inversion( nurbs, cp0, 1e-8 )
  uvw1, err = nurbs_controlbox_inversion( nurbs, cp1, 1e-8 )
  uvw2, err = nurbs_controlbox_inversion( nurbs, cp2, 1e-8 )

  newcoord0 = nurbs_controlbox_get_point( nurbs_modif, uvw0.x, uvw0.y, uvw0.z )
  newcoord1 = nurbs_controlbox_get_point( nurbs_modif, uvw1.x, uvw1.y, uvw1.z )
  newcoord2 = nurbs_controlbox_get_point( nurbs_modif, uvw2.x, uvw2.y, uvw2.z )

  x1 = newcoord0.x
  x2 = newcoord1.x
  x3 = newcoord2.x
  y1 = newcoord0.z
  y2 = newcoord1.z
  y3 = newcoord2.z

  #see formula to compute the circle radius from 3 given points in: http://en.wikipedia.org/wiki/Radius
  aux_up = ((x2-x1)**2 + (y2-y1)**2) * ((x2-x3)**2 + (y2-y3)**2) * ((x3-x1)**2 + (y3-y1)**2)
  aux_up =math.sqrt(aux_up)

  aux_low= x1*y2 + x2*y3 + x3*y1 - x1*y3 - x2*y1 - x3*y2
  aux_low=2*(aux_low**2)

  radius=aux_low/aux_up #ponemos la inversa porque creemos que la formula de la wikipedia está al reves
  #print("radius: " + str(radius))

  if (radius<0.004):
      flag3=1 #false

  print("Constraint minimum leading edge radius: " + str(flag3))

  # 4 - Check restriction of area >= Area initial
  #cargando coordenadas rae original desde fichero rae2822.dat (descargado de base datos illinois)
  flag4=0;
  print("Checking minimum area constraint for the RAE2822-AIAA")
  upper_dimension=0
  lower_dimension=0

  f_rae=open("rae2822.dat", "r")
  lines=f_rae.readlines()
  f_rae.close()

  upper_dimension, lower_dimension=lines[1].split()
  print(upper_dimension)
  print(lower_dimension)
  upper_dimension=int(upper_dimension)
  lower_dimension=int(lower_dimension)

  upper_coord_x = [0 for x in range(upper_dimension)]
  upper_coord_y = [0 for x in range(upper_dimension)]
  lower_coord_x = [0 for x in range(lower_dimension)]
  lower_coord_y = [0 for x in range(lower_dimension)]

  modif_upper_coords =  [0 for x in range(upper_dimension)]
  modif_lower_coords =  [0 for x in range(lower_dimension)]

  for i in range (0, upper_dimension):
    upper_coord_x[i],upper_coord_y[i] =lines[i+3].split()
    lower_coord_x[i],lower_coord_y[i] =lines[i+3+upper_dimension+1].split()

    upper_coord_x[i]= float(upper_coord_x[i])
    upper_coord_y[i]= float(upper_coord_y[i])
    lower_coord_x[i]= float(lower_coord_x[i])
    lower_coord_y[i]= float(lower_coord_y[i])

    upper_param_coord, err = nurbs_controlbox_inversion_coords( nurbs, upper_coord_x[i], 0, upper_coord_y[i], 1e-8 )
    lower_param_coord, err = nurbs_controlbox_inversion_coords( nurbs, lower_coord_x[i], 0, lower_coord_y[i], 1e-8 )

    modif_upper_coords[i] = nurbs_controlbox_get_point( nurbs_modif, upper_param_coord.x, upper_param_coord.y, upper_param_coord.z )
    modif_lower_coords[i] = nurbs_controlbox_get_point( nurbs_modif, lower_param_coord.x, lower_param_coord.y, lower_param_coord.z )

  #for i in range (0, upper_dimension):
  #  print (str(upper_coord_x[i]) + " " + str(upper_coord_y[i]))
  #  print (str(lower_coord_x[i]) + " " + str(lower_coord_y[i]))

  # Computing the area original
  area_orig_total=0
  for i in range(0, upper_dimension-1):
      x0_upper = upper_coord_x[i]
      x0_lower = lower_coord_x[i]
      y0_upper = upper_coord_y[i]
      y0_lower = lower_coord_y[i]

      x1_upper = upper_coord_x[i+1]
      x1_lower = lower_coord_x[i+1]
      y1_upper = upper_coord_y[i+1]
      y1_lower = lower_coord_y[i+1]

      area_upper = (x1_upper-x0_upper)*(y1_upper+y0_upper)*0.5
      area_lower = (x1_lower-x0_lower)*(y1_lower+y0_lower)*0.5
      area_orig_total += (area_upper-area_lower)
  print(area_orig_total)

  # Computing the area modif
  area_modif_total=0
  for i in range(0, upper_dimension-1):
      x0_upper = modif_upper_coords[i].x
      x0_lower = modif_lower_coords[i].x
      y0_upper = modif_upper_coords[i].z
      y0_lower = modif_lower_coords[i].z

      x1_upper = modif_upper_coords[i+1].x
      x1_lower = modif_lower_coords[i+1].x
      y1_upper = modif_upper_coords[i+1].z
      y1_lower = modif_lower_coords[i+1].z

      area_upper = (x1_upper-x0_upper)*(y1_upper+y0_upper)*0.5
      area_lower = (x1_lower-x0_lower)*(y1_lower+y0_lower)*0.5
      area_modif_total += (area_upper-area_lower)
  print(area_modif_total)

  if (area_modif_total<area_orig_total):
    flag4=1

  if(flag1 == 0 and flag2 == 0 and flag3== 0): # and flag4==0):
    flag=0 #valid
  else:
    flag=1 #invalid

  print(flag)

else:  #DPW #OJO CALCULAR LA DIMENSION DE LA CUERDA Y PONER LOS PORCENTAJES EN CONSECUENCIA
  print("Checking geometric constraints for the dpw")

  # 1- Airfoil's maximum thickness constraint

  # seccion 1
  cp0_vector_sec1 = [0 for x in xrange(6)]
  cp1_vector_sec1 = [0 for x in xrange(6)]
  uvw0_vector_sec1 = [0 for x in xrange(6)]
  uvw1_vector_sec1 = [0 for x in xrange(6)]
  newcoord0_vector_sec1 = [0 for x in xrange(6)]
  newcoord1_vector_sec1 = [0 for x in xrange(6)]

  #computing the chord for this section
  le_control_point = nurbs_getControlPoint( nurbs_modif, 1, 8, 2)
  te_control_point = nurbs_getControlPoint( nurbs_modif, 1, 1, 2)

  chord=abs(le_control_point.x - te_control_point.x)
  print("Cuerda seccion 1: "+str(chord))

  for i in range (0,6):
      cp0_vector_sec1[i]= nurbs_getControlPoint(nurbs, 1, i+1, 1)
      cp1_vector_sec1[i]= nurbs_getControlPoint(nurbs, 1, i+1, 3)

      uvw0_vector_sec1[i], err = nurbs_controlbox_inversion( nurbs, cp0_vector_sec1[i], 1e-8 )
      uvw1_vector_sec1[i], err = nurbs_controlbox_inversion( nurbs, cp1_vector_sec1[i], 1e-8 )

      newcoord0_vector_sec1[i] = nurbs_controlbox_get_point( nurbs_modif, uvw0_vector_sec1[i].x, uvw0_vector_sec1[i].y, uvw0_vector_sec1[i].z )
      newcoord1_vector_sec1[i] = nurbs_controlbox_get_point( nurbs_modif, uvw1_vector_sec1[i].x, uvw1_vector_sec1[i].y, uvw1_vector_sec1[i].z )

      if (abs(newcoord0_vector_sec1[i].z - newcoord1_vector_sec1[i].z)/chord > 0.135): #OJO ES UN 13.5% DE LA CUERDA
          flag1=1 #false

  # seccion 2
  cp0_vector_sec2 = [0 for x in xrange(6)]
  cp1_vector_sec2 = [0 for x in xrange(6)]
  uvw0_vector_sec2 = [0 for x in xrange(6)]
  uvw1_vector_sec2 = [0 for x in xrange(6)]
  newcoord0_vector_sec2 = [0 for x in xrange(6)]
  newcoord1_vector_sec2 = [0 for x in xrange(6)]

  #computing the chord for this section
  le_control_point = nurbs_getControlPoint( nurbs_modif, 2, 8, 2)
  te_control_point = nurbs_getControlPoint( nurbs_modif, 2, 1, 2)

  chord=abs(le_control_point.x - te_control_point.x)
  print("Cuerda seccion2: "+str(chord))

  for i in range (0,6):
      cp0_vector_sec2[i]= nurbs_getControlPoint(nurbs, 2, i+1, 1)
      cp1_vector_sec2[i]= nurbs_getControlPoint(nurbs, 2, i+1, 3)

      uvw0_vector_sec2[i], err = nurbs_controlbox_inversion( nurbs, cp0_vector_sec2[i], 1e-8 )
      uvw1_vector_sec2[i], err = nurbs_controlbox_inversion( nurbs, cp1_vector_sec2[i], 1e-8 )

      newcoord0_vector_sec2[i] = nurbs_controlbox_get_point( nurbs_modif, uvw0_vector_sec2[i].x, uvw0_vector_sec2[i].y, uvw0_vector_sec2[i].z )
      newcoord1_vector_sec2[i] = nurbs_controlbox_get_point( nurbs_modif, uvw1_vector_sec2[i].x, uvw1_vector_sec2[i].y, uvw1_vector_sec2[i].z )

      if (abs(newcoord0_vector_sec2[i].z - newcoord1_vector_sec2[i].z)/chord > 0.135):
          flag1=1 #false

  # seccion 3
  cp0_vector_sec3 = [0 for x in xrange(6)]
  cp1_vector_sec3 = [0 for x in xrange(6)]
  uvw0_vector_sec3 = [0 for x in xrange(6)]
  uvw1_vector_sec3 = [0 for x in xrange(6)]
  newcoord0_vector_sec3 = [0 for x in xrange(6)]
  newcoord1_vector_sec3 = [0 for x in xrange(6)]

  #computing the chord for this section
  le_control_point = nurbs_getControlPoint( nurbs_modif, 3, 8, 2)
  te_control_point = nurbs_getControlPoint( nurbs_modif, 3, 1, 2)

  chord=abs(le_control_point.x - te_control_point.x)
  print("Cuerda seccion3: "+str(chord))

  for i in range (0,6):
      cp0_vector_sec3[i]= nurbs_getControlPoint(nurbs, 3, i+1, 1)
      cp1_vector_sec3[i]= nurbs_getControlPoint(nurbs, 3, i+1, 3)

      uvw0_vector_sec3[i], err = nurbs_controlbox_inversion( nurbs, cp0_vector_sec3[i], 1e-8 )
      uvw1_vector_sec3[i], err = nurbs_controlbox_inversion( nurbs, cp1_vector_sec3[i], 1e-8 )

      newcoord0_vector_sec3[i] = nurbs_controlbox_get_point( nurbs_modif, uvw0_vector_sec3[i].x, uvw0_vector_sec3[i].y, uvw0_vector_sec3[i].z )
      newcoord1_vector_sec3[i] = nurbs_controlbox_get_point( nurbs_modif, uvw1_vector_sec3[i].x, uvw1_vector_sec3[i].y, uvw1_vector_sec3[i].z )

      if (abs(newcoord0_vector_sec3[i].z - newcoord1_vector_sec3[i].z)/chord > 0.135):
          flag1=1 #false

  print("Constraint Maximum airfoil's thickness: " + str(flag1))


  # 2- Beam constraints (at 0.20 and 0.75)
  cp0_vector = [0 for x in xrange(3)]
  cp1_vector = [0 for x in xrange(3)]
  cp2_vector = [0 for x in xrange(3)]
  cp3_vector = [0 for x in xrange(3)]

  uvw0_vector = [0 for x in xrange(3)]
  uvw1_vector = [0 for x in xrange(3)]
  uvw2_vector = [0 for x in xrange(3)]
  uvw3_vector = [0 for x in xrange(3)]

  newcoord0_vector = [0 for x in xrange(3)]
  newcoord1_vector = [0 for x in xrange(3)]
  newcoord2_vector = [0 for x in xrange(3)]
  newcoord3_vector = [0 for x in xrange(3)]

  chord = [0 for x in xrange(3)] #guarda la cuerda de cada seccion

  for i in range (0,3): #the dpw has 3 sections
      cp0_vector[i]= nurbs_getControlPoint(nurbs, i+1, 6, 1)
      cp1_vector[i]= nurbs_getControlPoint(nurbs, i+1, 6, 3)
      cp2_vector[i]= nurbs_getControlPoint(nurbs, i+1, 3, 1)
      cp3_vector[i]= nurbs_getControlPoint(nurbs, i+1, 3, 3)

      uvw0_vector[i], err = nurbs_controlbox_inversion( nurbs, cp0_vector[i], 1e-8 )
      uvw1_vector[i], err = nurbs_controlbox_inversion( nurbs, cp1_vector[i], 1e-8 )
      uvw2_vector[i], err = nurbs_controlbox_inversion( nurbs, cp2_vector[i], 1e-8 )
      uvw3_vector[i], err = nurbs_controlbox_inversion( nurbs, cp3_vector[i], 1e-8 )

      newcoord0_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw0_vector[i].x, uvw0_vector[i].y, uvw0_vector[i].z )
      newcoord1_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw1_vector[i].x, uvw1_vector[i].y, uvw1_vector[i].z )
      newcoord2_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw2_vector[i].x, uvw2_vector[i].y, uvw2_vector[i].z )
      newcoord3_vector[i] = nurbs_controlbox_get_point( nurbs_modif, uvw3_vector[i].x, uvw3_vector[i].y, uvw3_vector[i].z )

      #computing the chord for this section
      le_control_point = nurbs_getControlPoint( nurbs_modif, i+1, 8, 2)
      te_control_point = nurbs_getControlPoint( nurbs_modif, i+1, 1, 2)

      chord[i]=abs(le_control_point.x - te_control_point.x)
      print("Cuerda seccion "+ str(i+1) + " "+str(chord[i]))

      if (abs(newcoord0_vector[i].z - newcoord1_vector[i].z)/chord[i] < 0.12): #OJO ES EL 12 % DE LA CUERDA QUE NO ES 1, ESTO ESTA MAL
        flag2=1 #false

      if (abs(newcoord2_vector[i].z - newcoord3_vector[i].z)/chord[i] < 0.059): #OJO ES EL 5.9 % DE LA CUERDA QUE NO ES 1, ESTO ESTA MAL
        flag2=1 #false

  print("Constraint n2: " + str(flag2))

  if(flag1 == 0 and flag2 == 0):
    flag=0 #valid
  else:
    flag=1 #invalid

  print(flag)

nurbs_controlbox_dispose( nurbs )
nurbs_controlbox_dispose( nurbs_modif )

os.system("rm -f valid_geom.txt")
domino_add_line("valid_geom.txt", str(flag))

if(testcase==0):
    domino_add_line("valid_geom.txt", str(dif_volumen))

os.chdir("../")
print(os.getcwd())

print("END CONSTRAINTS CHECKING SCRIPT")
