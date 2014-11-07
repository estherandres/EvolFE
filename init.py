# -*- coding: utf-8 -*-

#*******************************************************************************************#
#
#                  PYTHON SCRIPT FOR INITIALIZATION
#   Receives the following input parameters:
#   - folder case
#   - parameter file
#   - grid file
#   - nurbs file
#   - numDV
#   - parallel (0:sequential; 1: parallel)
#   - case (0: cilinder 1: rae2822 airfoil 2:dpw wing)
#
#*******************************************************************************************#

DOMINOBIN_DIR = '/Users/estherandres/INTA/overview/130620_OVERVIEW/bin' #path to domino.so
TAUBIN_DIR = "/Users/estherandres/INTA/tau/taudir_release.2014.1.0/bin"

import os
import sys
import time
sys.path.append(DOMINOBIN_DIR)
from domino import *

FOLDER_CASE=sys.argv[1]
PARAM_FILE_DP1=sys.argv[2]
PARAM_FILE_DP2=sys.argv[3]
GRID_FILE=sys.argv[4]
NURBS_FILE=sys.argv[5]
numDV=int(sys.argv[6])
parallel=int(sys.argv[7])
testcase = int(sys.argv[8]) #0: cilinder 1: rae2822 airfoil 2:dpw wing
multipoint = int(sys.argv[9])


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
# ********************** END FUNCTIONS *************************** #

print("RUNNING INIT SCRIPT")
print(FOLDER_CASE)
print(PARAM_FILE_DP1)
print(PARAM_FILE_DP2)
print(GRID_FILE)
print(NURBS_FILE)
print(numDV)
print(parallel)
print(testcase)
print(multipoint)

os.chdir(FOLDER_CASE)
print(os.getcwd())

#Inicialización de los vectores para valores iniciales, max y min a 0
coordz_initial=[]
coordz_lb=[]
coordz_ub=[]
coordx_initial=[]
coordx_lb=[]
coordx_ub=[]
for i in range (0, numDV):
  coordz_initial.append(0.0)
  coordz_lb.append(0.0)
  coordz_ub.append(0.0)
  coordx_initial.append(0.0)
  coordx_lb.append(0.0)
  coordx_ub.append(0.0)

# Reads the parameters file. We need it to know the panels
# The first argument is the working path and the second the filename
# The working path is used to search the boundary file,
# if they are not directly defined in the parameters file.
inpara = domino_read_params( ".", PARAM_FILE_DP1);

# Imports a NURBS; returns an array of NURBS.
nurbs, num_nurbs = nurbs_controlbox_import_ascii(NURBS_FILE)

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

print ("EXECUTING GRID2UV")
# Calculates the inversion of the vertices with the NURBS
# The parameters are necessary to get the markers and the nurbs panels
uv_grid = domino_grid2cb_inversion(grid, 1, nurbs, inpara)

# Saves the inversion
nurbs_parameters_save_netcdf( uv_grid, "case.inv" )
print ("GRID2UV DONE!!")

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
ow_grid_free(grid, 1)
nurbs_parameters_free(new_coords)

# Adds a new line in the parameters file with the deform filename
# in case it is not already defined
domino_add_line( PARAM_FILE_DP1, "Deformed coordinates filename: deformed_surface.grid")

print ("EXTRACTING THE X,Y,Z COORDINATES OF THE CONTROL POINTS AND COMPUTING THE DV RANGE")

if (testcase==0): #CILINDER
  i=0
  for iu in range(0, nurbs.cp_length_u):
     for iv in range(0, nurbs.cp_length_v):
         for iw in range(0, nurbs.cp_length_w):
           if (iu==1): 
             if(iw==1 and iv!=0 and iv!=nurbs.cp_length_v-1):
                cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                coordz_initial[i]=cp.z
                coordx_initial[i]=cp.x
                coordz_lb[i]=coordz_initial[i]-0.99*abs(coordz_initial[i])
                coordz_ub[i]=coordz_initial[i]+0.99*abs(coordz_initial[i])

                coordx_lb[i]=coordx_initial[i]-0.25
                coordx_ub[i]=coordx_initial[i]+0.25
                
                domino_add_line("rangos.txt", str(coordz_ub[i]) + " " + str(coordz_lb[i]))
                domino_add_line("geom_ini.txt", str(coordz_initial[i]))
                domino_add_line("rangos.txt", str(coordx_ub[i]) + " " + str(coordx_lb[i]))
                domino_add_line("geom_ini.txt", str(coordx_initial[i]))
                i+=1

             if(iw==1 and (iv==0 or iv==nurbs.cp_length_v-1)):
                cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                coordz_initial[i]=cp.z
                coordz_lb[i]=coordz_initial[i]-0.99*abs(coordz_initial[i])
                coordz_ub[i]=coordz_initial[i]+0.99*abs(coordz_initial[i])
                domino_add_line("rangos.txt", str(coordz_ub[i]) + " " + str(coordz_lb[i]))
                domino_add_line("geom_ini.txt", str(coordz_initial[i]))
                i+=1

             if (iw==2 and iv==0):  #leading edge
                cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                domino_add_line("rangos.txt", str(cp.x+0.25) + " " + str(cp.x-0.99))
                domino_add_line("geom_ini.txt", str(cp.x))
                i+=1

             if (iw==2 and iv == 3):  #trailing edge
                cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                domino_add_line("rangos.txt", str(cp.x+0.99) + " " + str(cp.x-0.25))
                domino_add_line("geom_ini.txt", str(cp.x))
                i+=1

elif(testcase==1): #RAE2822
  i=0
  for iu in range(0, nurbs.cp_length_u):
     for iv in range(0, nurbs.cp_length_v):
         for iw in range(0, nurbs.cp_length_w):
           if (iw==1 or iw==3):
              if (iv>=1 and iv<=7):
                  if (iu==1):
                     cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                     coordz_initial[i]=cp.z
                     coordz_lb[i]=coordz_initial[i]-0.20*coordz_initial[i]
                     coordz_ub[i]=coordz_initial[i]+0.20*coordz_initial[i]
                     #Comprobar si los rangos están ordenados
                     if (coordz_ub[i]<coordz_lb[i]):
                         aux=coordz_ub[i]
                         coordz_ub[i]=coordz_lb[i]
                         coordz_lb[i]=aux
                     domino_add_line("rangos.txt", str(coordz_ub[i]) + " " + str(coordz_lb[i]))
                     domino_add_line("geom_ini.txt", str(coordz_initial[i]))
                     i+=1
else:  #DPW
  i=0
  for iu in range(0, nurbs.cp_length_u):
     for iv in range(0, nurbs.cp_length_v):
         for iw in range(0, nurbs.cp_length_w):
           if (iw==1 or iw==3):
              if (iv>=2 and iv<=7):
                  if (iu>=1 and iu<=3):
                     cp = nurbs_getControlPoint(nurbs, iu, iv, iw)
                     coordz_initial[i]=cp.z
                     coordz_lb[i]=coordz_initial[i]-0.20*coordz_initial[i]
                     coordz_ub[i]=coordz_initial[i]+0.20*coordz_initial[i]
                     #Comprobar si los rangos están ordenados
                     if (coordz_ub[i]<coordz_lb[i]):
                         aux=coordz_ub[i]
                         coordz_ub[i]=coordz_lb[i]
                         coordz_lb[i]=aux
                     domino_add_line("rangos.txt", str(coordz_ub[i]) + " " + str(coordz_lb[i]))
                     domino_add_line("geom_ini.txt", str(coordz_initial[i]))
                     i+=1          
          
          
print ("PERFORMING THE INITIAL CFDs COMPUTATIONS ON THE ORIGINAL GEOMETRY")
##########################################
# Copy files to the iteration 0rig folder
##########################################
os.system("mkdir orig")
os.system("cp ./" + PARAM_FILE_DP1 + " orig/")
os.system("cp ./" + PARAM_FILE_DP2 + " orig/")
os.system("cp ./" + GRID_FILE + " orig/")
os.system("cp ./" + NURBS_FILE + " orig/")
#os.system("cp -r ./rae" + " orig/")
os.system("cp ./case.inv orig/")
os.system("mv ./deformed_surface.grid orig/")

os.chdir("./orig")
#print(os.getcwd())


##########################################
# Call TAU deformation
##########################################
print ("EXECUTING TAU DEFORMATION")
var = os.system(TAUBIN_DIR + '/deformation ' + PARAM_FILE_DP1 + ' log')
# Checks if tau deformation went ok
if (var != 0):
  print( "TAU deformation failed!\n")
  exit(1)
print ("TAU DEFORMATION DONE!!")

# Reads the filename of the grid generated by TAU deformation
primary_grid = domino_read_parameter(PARAM_FILE_DP1, "Primary grid filename");

domino_add_line(PARAM_FILE_DP2,"Primary grid filename: "+primary_grid)

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

##########################################
# Call TAU solver
##########################################
print ("EXECUTING TAU SOLVER")
if(testcase==0): #cilinder euler
    os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP1 + ' log_dp1')
    print ("TAU SOLVER DONE!!")
    if (multipoint==1):
        os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP2 + ' log_dp2')

        print ("TAU SOLVER DONE!!")
elif(testcase==1): #rae rans
    os.system(TAUBIN_DIR + '/ptau3d.turb1eq ' + PARAM_FILE_DP1 + ' log_dp1')
    print ("TAU SOLVER DONE!!")
    if (multipoint==1):
        os.system(TAUBIN_DIR + '/ptau3d.turb2eq ' + PARAM_FILE_DP2 + ' log_dp2')
        print ("TAU SOLVER DONE!!")
else: #dpw euler
    if(parallel==1): #parallel 8 processors
        os.system("/home/andrespe/bin/runtau2 2 1 8 "+ PARAM_FILE_DP1 + '> logPBSsolver_dp1')
        filename='logPBSsolver_dp1'
        jobid = read_jobid(filename)
        check_job(jobid)
        print ("TAU SOLVER DONE!!")
        os.system(TAUBIN_DIR + '/gather ' + PARAM_FILE_DP1)
        if (multipoint==1):
            os.system("/home/andrespe/bin/runtau2 2 1 8 "+ PARAM_FILE_DP2 + '> logPBSsolver_dp2')
            filename='logPBSsolver_dp2'
            jobid = read_jobid(filename)
            check_job(jobid)
            print ("TAU SOLVER DONE!!")
            os.system(TAUBIN_DIR + '/gather ' + PARAM_FILE_DP2)
    else: #sequential 1 processor
        os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP1 + ' log_dp1')
        print ("TAU SOLVER DONE!!")
        if(multipoint == 1):
            os.system(TAUBIN_DIR + '/ptau3d.el ' + PARAM_FILE_DP2 + ' log_dp2')
            print ("TAU SOLVER DONE!!")

# Reads the name of the solution
solver_solution_dp1 = domino_read_parameter(PARAM_FILE_DP1, "Restart-data prefix")
solver_solution_dp2 = domino_read_parameter(PARAM_FILE_DP2, "Restart-data prefix")

# Get the reference lift and drag for DP1
ref_clift_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_l" )
ref_cdrag_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_d" )
ref_cmy_dp1 = domino_read_netcdf_dbl(solver_solution_dp1, "c_my" )
print ("reference lift dp1: " + str(ref_clift_dp1))
print ("reference drag dp1: " + str(ref_cdrag_dp1))

# Get the reference lift and drag for DP2
ref_clift_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_l" )
ref_cdrag_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_d" )
ref_cmy_dp2 = domino_read_netcdf_dbl(solver_solution_dp2, "c_my" )
print ("reference lift dp2: " + str(ref_clift_dp2))
print ("reference drag dp2: " + str(ref_cdrag_dp2))

os.chdir("../")
#print(os.getcwd())
          
domino_add_line("datos_ini_dp1.txt", str(ref_cdrag_dp1) + " " + str(ref_clift_dp1) + " " + str(ref_cmy_dp1) + " ")

domino_add_line("datos_ini_dp2.txt", str(ref_cdrag_dp2) + " " + str(ref_clift_dp2) + " " + str(ref_cmy_dp2) + " ")

os.chdir("../")
#print(os.getcwd())

print("End init script")
