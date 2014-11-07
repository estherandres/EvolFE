
# -*- coding: utf-8 -*-
#*******************************************************************************************#
#
#                  PYTHON SCRIPT FOR CFD SIMULATIONS              
#
#*******************************************************************************************#

numPropuestas=1 #numero de lineas del fichero propuestas.txt

DOMINOBIN_DIR = '/Users/estherandres/INTA/overview/130620_OVERVIEW/bin' #path to domino.so
TAUBIN_DIR = "/Users/estherandres/INTA/tau/taudir_release.2014.1.0/bin"
NEWCOORDS_FILE="propuesta.txt"

import os
import sys
import time
sys.path.append(DOMINOBIN_DIR)
from domino import *

# Takes the input parameter: id of the geometry to be calculated
if len(sys.argv)<12:
    id_geom=sys.argv[1]
    print("Numero de geometría: " + id_geom + "\n")
    FOLDER_CASE=sys.argv[2]
    PARAM_FILE_DP1=sys.argv[3]
    PARAM_FILE_DP2=sys.argv[4]
    GRID_FILE=sys.argv[5]
    NURBS_FILE=sys.argv[6]
    numDV=int(sys.argv[7])
    parallel=int(sys.argv[8]) #0: sequential 1: parallel
    testcase = int(sys.argv[9]) #0: cilinder 1: rae2822 airfoil 2:dpw wing
    multipoint = int(sys.argv[10]) #0: single point #1: multi-point optimization
else:
    print("Error: This script requires more arguments\n")
    print("#geom folder_case parameterfile_name grid_name nurbs_name\n")

# ********************** FUNCTIONS *************************** #
# Checks if the job is still executing in the PBS system
def check_job(jobid):
  dummyfile="borrame"
  cmd='qstat ' + jobid + ' > ' + dummyfile
  #print cmd
  os.system(cmd)
  f=open(dummyfile,"r")
  lineList = f.readlines()
  f.close()
  while (int(len(lineList)) > 0):
    time.sleep(1)
    os.system(cmd)
    f=open(dummyfile,"r")
    lineList = f.readlines()
    f.close()
  cmd = "rm " + dummyfile
  os.system(cmd) 

# read job id from log file
def read_jobid(file):
  f=open(file,"r")
  lineList = f.readlines()
  f.close()
  line = lineList[int(len(lineList))-1]
  a = b = 'none'
  a,b = str.split(line, '.', 1)
  return a
  
def num(s):
  try:
    return int(s)
  except ValueError:
    return float(s)

# ********************** END FUNCTIONS *************************** #

cps = [[0 for y in xrange(3)] for x in xrange(numDV)]
cps_u2 =[[0 for y in xrange(3)] for x in xrange(numDV)]
cps_lower =[[0 for y in xrange(3)] for x in xrange(numDV)]
cps_lower_u2 =[[0 for y in xrange(3)] for x in xrange(numDV)]
coord_cp= [[0 for y in xrange(3)] for x in xrange(numDV)]

#print cps
#print cps_u2

if (testcase==0): #cilinder
  i=0
  for iv in range(0, 3):
    for iw in range(0, 4):
       if (iw==1): #or iw==3):  #no se usa ya esta parte
               cps[i][0]=0
               cps[i][1]=iv
               cps[i][2]=iw
               cps_u2[i][0]=1
               cps_u2[i][1]=iv
               cps_u2[i][2]=iw

               cps_lower[i][0]=0
               cps_lower[i][1]=iv
               cps_lower[i][2]=3
               cps_lower_u2[i][0]=1
               cps_lower_u2[i][1]=iv
               cps_lower_u2[i][2]=3

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
  cps=[1, 1, 1], [1, 1, 3], [1, 2, 1], [1, 2, 3], [1, 3, 1], [1, 3, 3], [1, 4, 1], [1, 4, 3], [1, 5, 1], [1, 5, 3], [1, 6, 1], [1, 6, 3], [1, 7, 1], [1, 7, 3]

  #los puntos con u=2 también hay que modificarlos puesto que se trata de un falso 3D
  cps_u2=[2, 1, 1], [2, 1, 3], [2, 2, 1], [2, 2, 3], [2, 3, 1], [2, 3, 3], [2, 4, 1], [2, 4, 3], [2, 5, 1], [2, 5, 3], [2, 6, 1], [2, 6, 3], [2, 7, 1], [2, 7, 3]
else: #dpw
  cps=[1, 2, 1], [1, 2, 3], [1, 3, 1], [1, 3, 3], [1, 4, 1], [1, 4, 3], [1, 5, 1], [1, 5, 3], [1, 6, 1], [1, 6, 3], [1, 7, 1], [1, 7, 3], [2, 2, 1], [2, 2, 3], [2, 3, 1], [2, 3, 3], [2, 4, 1], [2, 4, 3], [2, 5, 1], [2, 5, 3], [2, 6, 1], [2, 6, 3], [2, 7, 1], [2, 7, 3], [3, 2, 1], [3, 2, 3], [3, 3, 1], [3, 3, 3], [3, 4, 1], [3, 4, 3], [3, 5, 1], [3, 5, 3], [3, 6, 1], [3, 6, 3], [3, 7, 1], [3, 7, 3]

#print(cps)
#print(cps_u2)

print ("*************************************************************")
print ("*                                                           *")
print ("*                     SIMULATION    SCRIPT                  *")
print ("*                                                           *")
print ("*************************************************************")

# Changes directory
os.chdir(str(FOLDER_CASE))
print(os.getcwd())

# Leer de propuesta.txt las nuevas coordenadas z los puntos de control y modificarlos en la nurbs
# Reading the new z coordinates from the file
# Reading the new z coordinates from the file
f=open(NEWCOORDS_FILE,'r')
newcoords=[]
newcoords=[line.split() for line in f]
print(newcoords)

f.close()

# COMPUTATION OF THE INITIAL GEOMETRY

# Reads the parameters file. We need it to know the panels
# The first argument is the working path and the second the filename
# The working path is used to search the boundary file,
# if they are not directly defined in the parameters file.
inpara = domino_read_params( ".", PARAM_FILE_DP1);

# Imports a NURBS; returns an array of NURBS.
nurbs, num_nurbs = nurbs_controlbox_import_ascii(NURBS_FILE)
# If it is defined in the parameters file inpara.cb_filename

# Checks if the NURBS is imported
if (nurbs == None):
  print( "Failed to load the NURBS!\n")
  exit(1)

# Imports the surface grid.
grid, num_grids = ow_import_surfgrid_netcdf(GRID_FILE)
# If it is defined in the parameters file inpara.grid_filename

# Checks if the grid is imported
if (grid == None):
  print( "Failed to load the grid!\n")
  exit(1)

# print ("EXECUTING GRID2UV")
# Calculates the inversion of the vertices with the NURBS
# The parameters are neccesary to get the markers and the nurbs panels
# uv_grid = domino_grid2cb_inversion(grid, 1, nurbs, inpara)

# Saves the inversion
# nurbs_parameters_save_netcdf( uv_grid, "case.inv" )
# print ("GRID2UV DONE!!")


# Loads a previously calculated inversion
uv_grid = nurbs_parameters_import_netcdf( "case.inv" )


##########################################
# Call the nurbs2grid
##########################################
print ("EXECUTING NURBS2GRID")
new_coords = domino_grid2cb_coord(uv_grid, grid, 1, nurbs)

# Saves the new coordinates in NETCDF (in the format for TAU deformation)
domino_save_surfdeform_netcdf(new_coords, "deformed_surface.grid")

# To save in ASCII
# domino_save_surfdeform_ascii( new_coords, "deformed_surface.txt" )
print ("NURBS2GRID DONE!!")

# Releases the memory
# ow_grid_free(grid, 1)
# nurbs_parameters_free(new_coords)

print ("EXTRACTING THE X,Y,Z COORDINATES OF THE SELECTED CPS")
for i in range(0, numDV):
  cp = nurbs_getControlPoint(nurbs, int(cps[i][0]),int(cps[i][1]),int(cps[i][2]))
  coord_cp[i][0]=cp.x
  coord_cp[i][1]=cp.y
  coord_cp[i][2]=cp.z
  print("CP (" + str(cps[i]) + "): " + str(coord_cp[i]))

print ("STARTING THE SIMULATION LOOP")  
ORIG_PARAM_FILE_dp1="./orig/"+PARAM_FILE_DP1
initial_solver_solution_dp1 = domino_read_parameter(ORIG_PARAM_FILE_dp1, "Restart-data prefix")
ORIG_PARAM_FILE_dp2="./orig/"+PARAM_FILE_DP2
initial_solver_solution_dp2 = domino_read_parameter(ORIG_PARAM_FILE_dp2, "Restart-data prefix")

for i in range(0, numPropuestas):
  folder_name=str(i)+"_"+str(id_geom)
  # Creates a new directory
  os.system("mkdir " + str(folder_name))
  # Copy necessary files into the new directory
  os.system("cp ./" + PARAM_FILE_DP1 + " ./" + str(folder_name))
  os.system("cp ./" + PARAM_FILE_DP2 + " ./" + str(folder_name))
  os.system("cp " + GRID_FILE + " ./" + str(folder_name))
  os.system("cp " + NURBS_FILE + " ./" + str(folder_name))
  os.system("cp ./orig/" + initial_solver_solution_dp1 + " ./" + str(folder_name))
  os.system("cp ./orig/" + initial_solver_solution_dp2 + " ./" + str(folder_name))
                           
  # Changes directory
  os.chdir(str(folder_name))
  print(os.getcwd())

  if(testcase==0): #cilinder
      i=0
      for iv in range(0, nurbs.cp_length_v):
        for iw in range(0, nurbs.cp_length_w):
           if(iw==1 and iv!=0 and iv!=nurbs.cp_length_v-1):
               print i
               z=num(newcoords[0][i])
               i=i+1
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs, 0, iv, 1)
               cp.x=x
               cp.z=z

               cp=nurbs_getControlPoint(nurbs, 1, iv, 1)
               cp.x=x
               cp.z=z

               cp=nurbs_getControlPoint(nurbs, 0, iv, 3)
               cp.x=x
               cp.z=-z

               cp=nurbs_getControlPoint(nurbs, 1, iv, 3)
               cp.x=x
               cp.z=-z

           if(iw==1 and (iv==0 or iv==nurbs.cp_length_v-1)):
               z=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs, 0, iv, 1)
               cp.z=z

               cp=nurbs_getControlPoint(nurbs, 1, iv, 1)
               cp.z=z

               cp=nurbs_getControlPoint(nurbs, 0, iv, 3)
               cp.z=-z

               cp=nurbs_getControlPoint(nurbs, 1, iv, 3)
               cp.z=-z


           if (iw==2 and iv==0):
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs, 0, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 0, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 0, iv, 3)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, 3)
               cp.x=x

           if (iw==2 and iv==3):
               x=num(newcoords[0][i])
               i=i+1

               cp=nurbs_getControlPoint(nurbs, 0, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, iw)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 0, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, 1)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 0, iv, 3)
               cp.x=x

               cp=nurbs_getControlPoint(nurbs, 1, iv, 3)
               cp.x=x


  elif(testcase==1): #rae2822
        cp1 = nurbs_getControlPoint(nurbs, cps[0][0],cps[0][1],cps[0][2])
        cp2 = nurbs_getControlPoint(nurbs, cps[1][0],cps[1][1],cps[1][2])
        cp3 = nurbs_getControlPoint(nurbs, cps[2][0],cps[2][1],cps[2][2])
        cp4 = nurbs_getControlPoint(nurbs, cps[3][0],cps[3][1],cps[3][2])
        cp5 = nurbs_getControlPoint(nurbs, cps[4][0],cps[4][1],cps[4][2])
        cp6 = nurbs_getControlPoint(nurbs, cps[5][0],cps[5][1],cps[5][2])
        cp7 = nurbs_getControlPoint(nurbs, cps[6][0],cps[6][1],cps[6][2])
        cp8 = nurbs_getControlPoint(nurbs, cps[7][0],cps[7][1],cps[7][2])
        cp9 = nurbs_getControlPoint(nurbs, cps[8][0],cps[8][1],cps[8][2])
        cp10 = nurbs_getControlPoint(nurbs, cps[9][0],cps[9][1],cps[9][2])
        cp11 = nurbs_getControlPoint(nurbs, cps[10][0],cps[10][1],cps[10][2])
        cp12 = nurbs_getControlPoint(nurbs, cps[11][0],cps[11][1],cps[11][2])
        cp13 = nurbs_getControlPoint(nurbs, cps[12][0],cps[12][1],cps[12][2])
        cp14 = nurbs_getControlPoint(nurbs, cps[13][0],cps[13][1],cps[13][2])

        cp1_u2 = nurbs_getControlPoint(nurbs, cps_u2[0][0],cps_u2[0][1],cps_u2[0][2])
        cp2_u2 = nurbs_getControlPoint(nurbs, cps_u2[1][0],cps_u2[1][1],cps_u2[1][2])
        cp3_u2 = nurbs_getControlPoint(nurbs, cps_u2[2][0],cps_u2[2][1],cps_u2[2][2])
        cp4_u2 = nurbs_getControlPoint(nurbs, cps_u2[3][0],cps_u2[3][1],cps_u2[3][2])
        cp5_u2 = nurbs_getControlPoint(nurbs, cps_u2[4][0],cps_u2[4][1],cps_u2[4][2])
        cp6_u2 = nurbs_getControlPoint(nurbs, cps_u2[5][0],cps_u2[5][1],cps_u2[5][2])
        cp7_u2 = nurbs_getControlPoint(nurbs, cps_u2[6][0],cps_u2[6][1],cps_u2[6][2])
        cp8_u2 = nurbs_getControlPoint(nurbs, cps_u2[7][0],cps_u2[7][1],cps_u2[7][2])
        cp9_u2 = nurbs_getControlPoint(nurbs, cps_u2[8][0],cps_u2[8][1],cps_u2[8][2])
        cp10_u2 = nurbs_getControlPoint(nurbs, cps_u2[9][0],cps_u2[9][1],cps_u2[9][2])
        cp11_u2 = nurbs_getControlPoint(nurbs, cps_u2[10][0],cps_u2[10][1],cps_u2[10][2])
        cp12_u2 = nurbs_getControlPoint(nurbs, cps_u2[11][0],cps_u2[11][1],cps_u2[11][2])
        cp13_u2 = nurbs_getControlPoint(nurbs, cps_u2[12][0],cps_u2[12][1],cps_u2[12][2])
        cp14_u2 = nurbs_getControlPoint(nurbs, cps_u2[13][0],cps_u2[13][1],cps_u2[13][2])

        # Deform the z coordinate according to the modification vector
        coord_cp[0][2] = num(newcoords[i][0])
        coord_cp[1][2] = num(newcoords[i][1])
        coord_cp[2][2] = num(newcoords[i][2])
        coord_cp[3][2] = num(newcoords[i][3])
        coord_cp[4][2] = num(newcoords[i][4])
        coord_cp[5][2] = num(newcoords[i][5])
        coord_cp[6][2] = num(newcoords[i][6])
        coord_cp[7][2] = num(newcoords[i][7])
        coord_cp[8][2] = num(newcoords[i][8])
        coord_cp[9][2] = num(newcoords[i][9])
        coord_cp[10][2] = num(newcoords[i][10])
        coord_cp[11][2] = num(newcoords[i][11])
        coord_cp[12][2] = num(newcoords[i][12])
        coord_cp[13][2] = num(newcoords[i][13])

        cp1.z= coord_cp[0][2]
        cp2.z= coord_cp[1][2]
        cp3.z= coord_cp[2][2]
        cp4.z= coord_cp[3][2]
        cp5.z= coord_cp[4][2]
        cp6.z= coord_cp[5][2]
        cp7.z= coord_cp[6][2]
        cp8.z= coord_cp[7][2]
        cp9.z= coord_cp[8][2]
        cp10.z= coord_cp[9][2]
        cp11.z= coord_cp[10][2]
        cp12.z= coord_cp[11][2]
        cp13.z= coord_cp[12][2]
        cp14.z= coord_cp[13][2]

        # En el RAE2822 hay que modificar también el otro lado porque es falso 3D
        cp1_u2.z= coord_cp[0][2]
        cp2_u2.z= coord_cp[1][2]
        cp3_u2.z= coord_cp[2][2]
        cp4_u2.z= coord_cp[3][2]
        cp5_u2.z= coord_cp[4][2]
        cp6_u2.z= coord_cp[5][2]
        cp7_u2.z= coord_cp[6][2]
        cp8_u2.z= coord_cp[7][2]
        cp9_u2.z= coord_cp[8][2]
        cp10_u2.z= coord_cp[9][2]
        cp11_u2.z= coord_cp[10][2]
        cp12_u2.z= coord_cp[11][2]
        cp13_u2.z= coord_cp[12][2]
        cp14_u2.z= coord_cp[13][2]

  else: #dpw
        cp1 = nurbs_getControlPoint(nurbs, cps[0][0],cps[0][1],cps[0][2])
        cp2 = nurbs_getControlPoint(nurbs, cps[1][0],cps[1][1],cps[1][2])
        cp3 = nurbs_getControlPoint(nurbs, cps[2][0],cps[2][1],cps[2][2])
        cp4 = nurbs_getControlPoint(nurbs, cps[3][0],cps[3][1],cps[3][2])
        cp5 = nurbs_getControlPoint(nurbs, cps[4][0],cps[4][1],cps[4][2])
        cp6 = nurbs_getControlPoint(nurbs, cps[5][0],cps[5][1],cps[5][2])
        cp7 = nurbs_getControlPoint(nurbs, cps[6][0],cps[6][1],cps[6][2])
        cp8 = nurbs_getControlPoint(nurbs, cps[7][0],cps[7][1],cps[7][2])
        cp9 = nurbs_getControlPoint(nurbs, cps[8][0],cps[8][1],cps[8][2])
        cp10 = nurbs_getControlPoint(nurbs, cps[9][0],cps[9][1],cps[9][2])
        cp11 = nurbs_getControlPoint(nurbs, cps[10][0],cps[10][1],cps[10][2])
        cp12 = nurbs_getControlPoint(nurbs, cps[11][0],cps[11][1],cps[11][2])
        cp13 = nurbs_getControlPoint(nurbs, cps[12][0],cps[12][1],cps[12][2])
        cp14 = nurbs_getControlPoint(nurbs, cps[13][0],cps[13][1],cps[13][2])
        cp15 = nurbs_getControlPoint(nurbs, cps[14][0],cps[14][1],cps[14][2])
        cp16 = nurbs_getControlPoint(nurbs, cps[15][0],cps[15][1],cps[15][2])
        cp17 = nurbs_getControlPoint(nurbs, cps[16][0],cps[16][1],cps[16][2])
        cp18 = nurbs_getControlPoint(nurbs, cps[17][0],cps[17][1],cps[17][2])
        cp19 = nurbs_getControlPoint(nurbs, cps[18][0],cps[18][1],cps[18][2])
        cp20 = nurbs_getControlPoint(nurbs, cps[19][0],cps[19][1],cps[19][2])
        cp21 = nurbs_getControlPoint(nurbs, cps[20][0],cps[20][1],cps[20][2])
        cp22 = nurbs_getControlPoint(nurbs, cps[21][0],cps[21][1],cps[21][2])
        cp23 = nurbs_getControlPoint(nurbs, cps[22][0],cps[22][1],cps[22][2])
        cp24 = nurbs_getControlPoint(nurbs, cps[23][0],cps[23][1],cps[23][2])
        cp25 = nurbs_getControlPoint(nurbs, cps[24][0],cps[24][1],cps[24][2])
        cp26 = nurbs_getControlPoint(nurbs, cps[25][0],cps[25][1],cps[25][2])
        cp27 = nurbs_getControlPoint(nurbs, cps[26][0],cps[26][1],cps[26][2])
        cp28 = nurbs_getControlPoint(nurbs, cps[27][0],cps[27][1],cps[27][2])
        cp29 = nurbs_getControlPoint(nurbs, cps[28][0],cps[28][1],cps[28][2])
        cp30 = nurbs_getControlPoint(nurbs, cps[29][0],cps[29][1],cps[29][2])
        cp31 = nurbs_getControlPoint(nurbs, cps[30][0],cps[30][1],cps[30][2])
        cp32 = nurbs_getControlPoint(nurbs, cps[31][0],cps[31][1],cps[31][2])
        cp33 = nurbs_getControlPoint(nurbs, cps[32][0],cps[32][1],cps[32][2])
        cp34 = nurbs_getControlPoint(nurbs, cps[33][0],cps[33][1],cps[33][2])
        cp35 = nurbs_getControlPoint(nurbs, cps[34][0],cps[34][1],cps[34][2])
        cp36 = nurbs_getControlPoint(nurbs, cps[35][0],cps[35][1],cps[35][2])


      # Deform the z coordinate according to the modification vector
        coord_cp[0][2] = num(newcoords[i][0])
        coord_cp[1][2] = num(newcoords[i][1])
        coord_cp[2][2] = num(newcoords[i][2])
        coord_cp[3][2] = num(newcoords[i][3])
        coord_cp[4][2] = num(newcoords[i][4])
        coord_cp[5][2] = num(newcoords[i][5])
        coord_cp[6][2] = num(newcoords[i][6])
        coord_cp[7][2] = num(newcoords[i][7])
        coord_cp[8][2] = num(newcoords[i][8])
        coord_cp[9][2] = num(newcoords[i][9])
        coord_cp[10][2] = num(newcoords[i][10])
        coord_cp[11][2] = num(newcoords[i][11])
        coord_cp[12][2] = num(newcoords[i][12])
        coord_cp[13][2] = num(newcoords[i][13])
        coord_cp[14][2] = num(newcoords[i][14])
        coord_cp[15][2] = num(newcoords[i][15])
        coord_cp[16][2] = num(newcoords[i][16])
        coord_cp[17][2] = num(newcoords[i][17])
        coord_cp[18][2] = num(newcoords[i][18])
        coord_cp[19][2] = num(newcoords[i][19])
        coord_cp[20][2] = num(newcoords[i][20])
        coord_cp[21][2] = num(newcoords[i][21])
        coord_cp[22][2] = num(newcoords[i][22])
        coord_cp[23][2] = num(newcoords[i][23])
        coord_cp[24][2] = num(newcoords[i][24])
        coord_cp[25][2] = num(newcoords[i][25])
        coord_cp[26][2] = num(newcoords[i][26])
        coord_cp[27][2] = num(newcoords[i][27])
        coord_cp[28][2] = num(newcoords[i][28])
        coord_cp[29][2] = num(newcoords[i][29])
        coord_cp[30][2] = num(newcoords[i][30])
        coord_cp[31][2] = num(newcoords[i][31])
        coord_cp[32][2] = num(newcoords[i][32])
        coord_cp[33][2] = num(newcoords[i][33])
        coord_cp[34][2] = num(newcoords[i][34])
        coord_cp[35][2] = num(newcoords[i][35])

        cp1.z= coord_cp[0][2]
        cp2.z= coord_cp[1][2]
        cp3.z= coord_cp[2][2]
        cp4.z= coord_cp[3][2]
        cp5.z= coord_cp[4][2]
        cp6.z= coord_cp[5][2]
        cp7.z= coord_cp[6][2]
        cp8.z= coord_cp[7][2]
        cp9.z= coord_cp[8][2]
        cp10.z= coord_cp[9][2]
        cp11.z= coord_cp[10][2]
        cp12.z= coord_cp[11][2]
        cp13.z= coord_cp[12][2]
        cp14.z= coord_cp[13][2]
        cp15.z= coord_cp[14][2]
        cp16.z= coord_cp[15][2]
        cp17.z= coord_cp[16][2]
        cp18.z= coord_cp[17][2]
        cp19.z= coord_cp[18][2]
        cp20.z= coord_cp[19][2]
        cp21.z= coord_cp[20][2]
        cp22.z= coord_cp[21][2]
        cp23.z= coord_cp[22][2]
        cp24.z= coord_cp[23][2]
        cp25.z= coord_cp[24][2]
        cp26.z= coord_cp[25][2]
        cp27.z= coord_cp[26][2]
        cp28.z= coord_cp[27][2]
        cp29.z= coord_cp[28][2]
        cp30.z= coord_cp[29][2]
        cp31.z= coord_cp[30][2]
        cp32.z= coord_cp[31][2]
        cp33.z= coord_cp[32][2]
        cp34.z= coord_cp[33][2]
        cp35.z= coord_cp[34][2]
        cp36.z= coord_cp[35][2]

  nurbs_controlbox_export_ascii("nurbs_modif.nurbs", nurbs, 1)
  
  #########################################
  # Call the nurbs2grid
  ##########################################
  print ("EXECUTING NURBS2GRID")
  new_coords = domino_grid2cb_coord(uv_grid, grid, 1, nurbs)

  # Saves the new coordinates in NETCDF (in the format for TAU deformation)
  domino_save_surfdeform_netcdf(new_coords, "deformed_surface.grid")

  # To save in ASCII
  # domino_save_surfdeform_ascii( new_coords, "deformed_surface.txt" )
  print ("NURBS2GRID DONE!!")

  # Releases the memory
  ow_grid_free(grid, 1)
  nurbs_parameters_free(new_coords)

  # Adds a new line in the parameters file with the deform filename
  # in case it is not already defined
  domino_add_line( PARAM_FILE_DP1, "Deformed coordinates filename: deformed_surface.grid")
  
  ##########################################
  # Call TAU deformation
  ##########################################
  domino_add_line(PARAM_FILE_DP1, "Primary grid filename: " + GRID_FILE)
  print ("EXECUTING TAU DEFORMATION")
  true_deformation=os.system(TAUBIN_DIR + '/deformation ' + PARAM_FILE_DP1 + ' log')
  if (true_deformation!=0):
      sys.exit(1)
  print ("TAU DEFORMATION DONE!!")
  # before calling the solver, check if deformation went OK


  # Reads the filename of the grid generated by TAU deformation
  primary_grid = domino_read_parameter(PARAM_FILE_DP1, "Primary grid filename")

  domino_add_line(PARAM_FILE_DP2, "Primary grid filename: "+primary_grid)

  # Imports the grid
  grid, num_grids = ow_import_surfgrid_netcdf(primary_grid)
  if (grid == None):
    print( "Failed to load the grid! " + primary_grid)
    exit(1)
  
  ##########################################
  # Call TAU preprocessing
  ##########################################
  print ("EXECUTING TAU PREPROCESSING")
  os.system(TAUBIN_DIR + '/ptau3d.preprocessing ' + PARAM_FILE_DP1 + ' log')
  print ("TAU PREPROCESSING DONE!!")

  # Prepare the parameters file to call the flow solver
  domino_add_line(PARAM_FILE_DP1, "Restart-data prefix: " + initial_solver_solution_dp1)
  domino_add_line(PARAM_FILE_DP2, "Restart-data prefix: " + initial_solver_solution_dp2)
  
  ##########################################
  # Call TAU solver
  ##########################################
  print ("EXECUTING TAU SOLVER")
  if(testcase==0): #cilinder euler
    os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP1 + ' log_dp1')
    print ("TAU SOLVER DONE!!")
    if(multipoint==1):
        os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP2 + ' log_dp2')
        print ("TAU SOLVER DONE!!")
  elif(testcase==1): #rae rans
    os.system(TAUBIN_DIR + '/ptau3d.turb1eq ' + PARAM_FILE_DP1 + ' log_dp1')
    print ("TAU SOLVER DONE!!")
    if(multipoint==1):
        os.system(TAUBIN_DIR + '/ptau3d.turb2eq ' + PARAM_FILE_DP2 + ' log_dp2')
        print ("TAU SOLVER DONE!!")
  else: #dpw euler
    if(parallel==1): #parallel 8 processors
      os.system(TAUBIN_DIR + '/scatter ' + PARAM_FILE_DP1)
      os.system("/home/andrespe/bin/runtau2 2 1 8 "+ PARAM_FILE_DP1 + '> logPBSsolver_dp1')
      filename='logPBSsolver_dp1'
      jobid = read_jobid(filename)
      check_job(jobid)
      print ("TAU SOLVER DONE!!")
      os.system(TAUBIN_DIR + '/gather ' + PARAM_FILE_DP1)
      if (multipoint==1):
          os.system(TAUBIN_DIR + '/scatter ' + PARAM_FILE_DP2)
          os.system("/home/andrespe/bin/runtau2 2 1 8 "+ PARAM_FILE_DP2 + '> logPBSsolver_dp2')
          filename='logPBSsolver_dp2'
          jobid = read_jobid(filename)
          check_job(jobid)
          print ("TAU SOLVER DONE!!")
          os.system(TAUBIN_DIR + '/gather ' + PARAM_FILE_DP2)
    else: #sequential 1 processor
        os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP1 + ' log_dp1')
        print ("TAU SOLVER DONE!!")
        if (multipoint==1):
            os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP2 + ' log_dp2')
            print ("TAU SOLVER DONE!!")

  # Reads the name of the solution
  solver_solution_dp1 = domino_read_parameter(PARAM_FILE_DP1, "Restart-data prefix")
  solver_solution_dp2 = domino_read_parameter(PARAM_FILE_DP2, "Restart-data prefix")

  # Get lift, drag and cmy
  clift_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_l" )
  cdrag_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_d" )
  cmy_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_my" )

  clift_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_l" )
  cdrag_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_d" )
  cmy_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_my" )

  os.chdir("../")
  print(os.getcwd())    
  
  # Write coefficient values to the database file
  os.system("rm -f salida_dp1.txt") #lo borro primero para que siempre haya sólo tantas líneas como numPropuestas
  domino_add_line("salida_dp1.txt", str(cdrag_dp1) + " " + str(clift_dp1) + " " + str(cmy_dp1))

  os.system("rm -f salida_dp2.txt") #lo borro primero para que siempre haya sólo tantas líneas como numPropuestas
  domino_add_line("salida_dp2.txt", str(cdrag_dp2) + " " + str(clift_dp2) + " " + str(cmy_dp2))
  

  sys.exit(0)