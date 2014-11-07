#Makefile of the EVOLFE optimization tool
RAE=rae
DPW=dpw

all: main.cpp
	g++ -g -o ./EvolFE main.cpp
	
help:
	@echo ""
	@echo "make all	- builds EvolFE"
	@echo "make clean - remove executable ./EvolFE"
	@echo "make cleanall - remove all"
	@echo "make cleancilinder - remove files from cilinder folder"
	@echo "make cleanrae - remove files from rae folder"
	@echo "make help - this info"
	@echo ""

cleanall: clean cleancilinder cleanrae cleandpw

clean: 
	rm -f ./EvolFE

cleancilinder:
	echo "Cleaning directory cilinder...."
	rm -rf cilinder/orig cilinder/0*
	rm -f cilinder/Test* cilinder/Train* cilinder/S1 cilinder/rangos.txt 
	rm -f cilinder/salida* cilinder/propuesta.txt cilinder/geom_ini.txt cilinder/deformed_surface.grid 
	rm -f cilinder/case.inv cilinder/datos_ini.txt cilinder/Resultados.txt
	echo "Done!!"

cleancilinderle:
	echo "Cleaning directory cilinder...."
	rm -rf cilinder_le/orig cilinder_le/0*
	rm -f cilinder_le/Test* cilinder_le/Train* cilinder_le/S1 cilinder_le/rangos.txt
	rm -f cilinder_le/salida* cilinder_le/propuesta.txt cilinder_le/geom_ini.txt cilinder_le/deformed_surface.grid	
	rm -f cilinder_le/case.inv cilinder_le/datos_ini.txt cilinder_le/Resultados.txt
	echo "Done!!"

cleanrae:
	echo "Cleaning directory rae...."
	rm -rf $(RAE)/orig $(RAE)/0*
	rm -f $(RAE)/Test* $(RAE)/Train* $(RAE)/S1 $(RAE)/rangos.txt
	rm -f $(RAE)/salida* $(RAE)/propuesta.txt $(RAE)/geom_ini.txt $(RAE)/deformed_surface.grid
	rm -f $(RAE)/case.inv $(RAE)/datos_ini_dp1.txt $(RAE)/datos_ini_dp2.txt  $(RAE)/Resultados.txt
	rm -f $(RAE)/valid_geom.txt
	echo "Done!!"


cleandpw:
	echo "Cleaning directory dpw...."
	rm -rf $(DPW)/orig $(DPW)/0*
	rm -f $(DPW)/Test* $(DPW)/Train* $(DPW)/S1 $(DPW)/rangos.txt
	rm -f $(DPW)/salida* $(DPW)/propuesta.txt $(DPW)/geom_ini.txt $(DPW)/deformed_surface.grid
	rm -f $(DPW)/case.inv $(DPW)/datos_ini_dp1.txt $(DPW)/datos_ini_dp2.txt  $(DPW)/Resultados.txt
	rm -f $(DPW)/valid_geom.txt
	echo "Done!!"
