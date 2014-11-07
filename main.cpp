#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>

#include <fstream>

#include <cstring>
using namespace std;

#define ALEA_11 ((rand()/double(RAND_MAX))-(rand()/double(RAND_MAX)))
#define ALEA_01 (rand()/double(RAND_MAX))
#define PUNTOS_INICIALES 4
#define TPOB 50

#define JOINPATH(a,b) string(a)+"/"+string(b)
#define JOINPATH3(a,b,c) string(a)+string(b)+string(c)

#define CONCAT2(a,b) string(a)+" "+string(b)
#define CONCAT4(a,b,c,d) string(a)+" "+string(b)+" "+string(c)+" "+string(d)
#define CONCAT5(a,b,c,d,e) string(a)+" "+string(b)+" "+string(c)+" "+string(d) \
                            +" "+string(e)

#define SVMLIB_PATH "/Users/estherandres/INTA/utils/libsvm-3.16"

int Npuntos;  //Número de puntos de control DPW wing=36, RAE2822=14
vector<double> Rmax;
vector<double> Rmin;
double Cd0_dp1, Cl0_dp1, Cm0_dp1;
double Cd0_dp2, Cl0_dp2, Cm0_dp2;

char folder_name[20];
char paramfile_dp1_name[20];
char paramfile_dp2_name[20];
char grid_name[50];
char nurbs_name[50];
char numDV[20];
char parallel[20];
char testcase[20];
char objective_function[20];
char multipoint[20];

double FuncionObjetivo (double Cd, double Cl, double Cm, double Cd0, double Cl0, double Cm0)
{
   double value, cm_penalty, lift_penalty=0;
   double Cdt_penalty, Cdl_penalty=0;
   double K=0.1;
   
   switch (atoi(objective_function))
   {
       case 0: //"MinCd"
            value=(Cd/Cd0);
            //if (Cl<0)
            //{
            //    value=10000;  // Para quitar los valores negativos de la FO
            //}
            break;
       case 1: //"MinCd/Cl_constr_Cmy"
            cm_penalty = (Cm0-Cm)*0.0001/0.01;
            if (cm_penalty < 0){
            	cm_penalty = 0;
            }
            value=(  ( (Cd+cm_penalty)/Cd0 ) / (Cl/Cl0)  );
           break;
       case 2: //"MinCd/Cl_constr_Cmy_Cl"
           lift_penalty=1-(Cl/Cl0);
           if (lift_penalty<0)
           {
                lift_penalty=0;
           }
           cm_penalty = (Cm0-Cm)*0.0001/0.01;
           if (cm_penalty < 0)
           {
            	cm_penalty = 0;
           }
           value=( ( (Cd+cm_penalty)/Cd0 ) )+5*lift_penalty;
           break;
       case 3: //"MinCd/Cl_constr_Cmy_Cl EMILIANO"
          
           Cdt_penalty=0.01*(Cm0-Cm)*(Cm0-Cm>0);
           Cdl_penalty=K*(Cl0*Cl0-Cl*Cl)*(Cl0*Cl0-Cl*Cl>0);
           value=((Cd+ Cdt_penalty + Cdl_penalty)/Cl) * (Cl0/Cd0);
           
           break;
       case 4: //"MinCd_Clcte"
           //value=Cd+0.1*fabs(Cl-Cl0)+0.01*((Cm-Cm0)<0);
           value=Cd-(Cl-Cl0)*(Cl-Cl0<0)+0.01*((Cm-Cm0)<0); //Hacer más fuerte Cl
           
           break;
           
       default:
           printf("The objective function has not been specified");
           break;
   }
   
   return value;
}
        
double Simular(vector<double> P, int id_geom, double *Cd_dp1, double *Cl_dp1, \
                double* Cm_dp1, double *Cd_dp2, double *Cl_dp2, double* Cm_dp2, \
                double* S_dp1, double* S_dp2)
{
        double S; //, S_dp1, S_dp2;
        
	char cmd[1024];
        int valid, true_deform; //0: valid, 1: invalid
        double dif_volumen;

        //Enviar P
        string propuestatxt=JOINPATH(folder_name,"propuesta.txt");
        ofstream A(propuestatxt.c_str());
        for(unsigned int i=0; i<P.size(); i++)
            A<< P.at(i)*(Rmax[i]-Rmin[i])+Rmin[i]<<" ";
        A<<"\n";
        
        A.close(); 
        
        //Before calling the CFD solver, check if the constraints are fulfilled
        sprintf(cmd, "python ./check_constraints.py %s %s %s %s %i %i", \
                    folder_name, paramfile_dp1_name, grid_name, \
                    nurbs_name, atoi(numDV), atoi(testcase));
        system(cmd); 
        
        //Read the file valid_geom.txt to see if this is a valid geom or not
        string validgeom=JOINPATH(folder_name,"valid_geom.txt");
        ifstream R_geom(validgeom.c_str());
      
        R_geom>>valid;
        if (atoi(testcase)==0)
        {
            R_geom>>dif_volumen;
        }
        
        printf("Does this geometry fulfill geometrical constraints: %i\n", valid); 
	    R_geom.close();
           
        if (valid==0)
        {
            //Call the CFD computation
            sprintf(cmd, "python ./calcula_cfd.py %i %s %s %s %s %s %i %i %i %i", id_geom, \
                        folder_name, paramfile_dp1_name, paramfile_dp2_name, grid_name, \
                        nurbs_name, atoi(numDV), atoi(parallel), atoi(testcase), atoi(multipoint));
            
            true_deform=system(cmd); 
            printf("Ha fallado deformacion: %i\n", true_deform);
            if (true_deform)
                valid=1; //Para que no considere los casos en que el deformador falla
        }
        if (valid==0)
        {
            //Leer Valor DP1
            string salidatxt_dp1=JOINPATH(folder_name,"salida_dp1.txt");
            ifstream R_dp1(salidatxt_dp1.c_str());

            R_dp1>>*Cd_dp1;
            R_dp1>>*Cl_dp1;
            R_dp1>>*Cm_dp1;

            *S_dp1=FuncionObjetivo(*Cd_dp1, *Cl_dp1, *Cm_dp1, Cd0_dp1, Cl0_dp1, Cm0_dp1);

            printf("Valor función objetivo DP1: %f\n", *(S_dp1));    

            R_dp1.close();    

            //Leer Valor DP2
            string salidatxt_dp2=JOINPATH(folder_name,"salida_dp2.txt");
            ifstream R_dp2(salidatxt_dp2.c_str());

            R_dp2>>*Cd_dp2;
            R_dp2>>*Cl_dp2;
            R_dp2>>*Cm_dp2;

            *S_dp2=FuncionObjetivo(*Cd_dp2, *Cl_dp2, *Cm_dp2, Cd0_dp2, Cl0_dp2, Cm0_dp2);

            printf("Valor función objetivo DP2: %f\n", *(S_dp2));    

            R_dp2.close();    

            S=((*S_dp1)+(*S_dp2))/2;
            
            if(atoi(testcase)==0)
            {
                //float difvol;
                //sscanf(dif_volumen, "%f", &difvol);
                printf("DIFERENCIA DE VOLUMEN: %f\n",dif_volumen);

                S+=dif_volumen*1; //Si se quiere penalizar más multiplicar por 2
            }
            
            printf("Valor función objetivo: %f\n", S);   
        }
        else
        {
            S=1000;
            *S_dp1=1000;
            *S_dp2=1000;
	    *Cd_dp1=0;
	    *Cl_dp1=0;
	    *Cm_dp1=0;
	    *Cd_dp2=0;
	    *Cl_dp2=0;
	    *Cm_dp2=0;

        }
        return S;
}


void Nuevo(vector<double> *Ne, vector<double> *P1, vector<double> *P2, \
        double fit1, double fit2)
{
    int a;

    for(unsigned int i=0; i< Ne->size(); i++)
    {

    if(rand()%3==0)
    {
            a=rand()%2;
            Ne->at(i)= a*P1->at(i)+(1-a)*P2->at(i);
    }
    else
    if(rand()%2==0)
    {
        if(P2->at(i)!=P1->at(i) && fit2!=fit1)
        {
        double m = (fit2-fit1) / (P2->at(i)-P1->at(i));
        double n = fit1 - m*P1->at(i);
        double inc = fabs(fit1-fit2);

        double min;
        if(fit1 > fit2)
            min=fit2;
        else
            min=fit1;

        Ne->at(i) = ( min- inc*1.1  - n)/m;
        }
        else
        {
            a=rand()%2;
            Ne->at(i)= a*P1->at(i)+(1-a)*P2->at(i);
        }
    }
    else
    {

        if(P2->at(i)-P1->at(i)!=0)
        {
        double inc = fabs(fit1-fit2);
        double min;
        if(fit1 > fit2)
            min=fit2;
        else
            min=fit1;

        double fit3 = min - inc;

        double f1= fit1 - fit3;
        double f2= fit2 - fit3;

        Ne->at(i) = (f1 -f2 + P2->at(i)*P2->at(i) - \
                P1->at(i)*P1->at(i))/2/(P2->at(i)-P1->at(i));
        }
        else
        {
            a=rand()%2;
            Ne->at(i)= a*P1->at(i)+(1-a)*P2->at(i);
        }
    }

        if(rand()%(Ne->size())==0)
        {

        if(rand()%3==0)
            Ne->at(i)*=(1+ALEA_11);
        else
        if(rand()%2==0)
            Ne->at(i)*=(1+ALEA_11*0.1);
        else
            Ne->at(i)*=(1+ALEA_11*0.01);

        }


    if(Ne->at(i)>1)
        Ne->at(i)=ALEA_01;

    if(Ne->at(i)<0)
        Ne->at(i)=ALEA_01;

    }

}



class BaseDeDatos
{
    public:

    vector <vector <double> > in;
    vector <double> out;
    
    vector <double> out_dp1;
    vector <double> out_dp2;
    
    vector<double> Cd_dp1;
    vector<double> Cl_dp1;
    vector<double> Cm_dp1;
    
    vector<double> Cd_dp2;
    vector<double> Cl_dp2;
    vector<double> Cm_dp2;
            
    double maximoCd1;
    double maximoCl1;
    double maximoCm1;

    double maximoCd2;
    double maximoCl2;
    double maximoCm2;

    vector<double> GeneraPuntoAleatorio(int Npuntos)
    {
        vector<double> Punto;

        for(int i=0; i<Npuntos; i++)
            Punto.push_back(rand()/double(RAND_MAX));

        return Punto;
    }


    void Generar_SVM()
    {
        char str1[50];
        char str2[50];
        char cmd[1024], cmd2[1024], cmd3[1024], aux[1024]="";
        //Normalizacion:


        // Volcar base de datos [una por parámetro (Cd1, Cl1, Cm1, Cd2, Cl2, Cm2)]
//--------------------------------------------------------------------------------
/*          Res<< DB.out_dp1.at(h)<< "\t";
            Res<< DB.Cd_dp1.at(h)<< "\t";
            Res<< DB.Cl_dp1.at(h)<< "\t";
            Res<< DB.Cm_dp1.at(h)<< "\t";
            
            Res<< DB.out_dp2.at(h)<< "\t";
            Res<< DB.Cd_dp2.at(h)<< "\t";
            Res<< DB.Cl_dp2.at(h)<< "\t";
            Res<< DB.Cm_dp2.at(h)<< "\t";					*/
//--------------------------------------------------------------------------------


	maximoCd1=fabs(Cd_dp1.at(0));

        for(unsigned int i=0; i<Cd_dp1.size(); i++)
            if(maximoCd1<fabs(Cd_dp1.at(i)))
            maximoCd1=fabs(Cd_dp1.at(i));

            string train=JOINPATH(folder_name,"Train_Cd1");
            ofstream Archivo(train.c_str());
            for(unsigned int i=0; i<Cd_dp1.size(); i++)
	    if(out.at(i)!=1000)
            {
                Archivo << Cd_dp1.at(i)/maximoCd1<<" ";
                for(unsigned int j=0; j<in.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";

                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();

            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cd1 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cd1.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cd1", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cd1.model %s",folder_name);
            system(aux);

//--------------------------------------------------------------------------------

	maximoCl1=fabs(Cl_dp1.at(0));

        for(unsigned int i=0; i<Cl_dp1.size(); i++)
            if(maximoCl1<fabs(Cl_dp1.at(i)))
            maximoCl1=fabs(Cl_dp1.at(i));

            train=JOINPATH(folder_name,"Train_Cl1");

            Archivo.open(train.c_str());

            for(unsigned int i=0; i<Cl_dp1.size(); i++)
	    if(out.at(i)!=1000)
            {

                Archivo << Cl_dp1.at(i)/maximoCl1<<" ";

                for(unsigned int j=0; j<in.at(0).size()-1; j++)

                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";

                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cl1 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cl1.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cl1", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cl1.model %s",folder_name);
            system(aux);
//--------------------------------------------------------------------------------

        maximoCm1=Cm_dp1.at(0);

        for(unsigned int i=0; i<Cm_dp1.size(); i++)
            if(maximoCm1<fabs(Cm_dp1.at(i)))
            maximoCm1=fabs(Cm_dp1.at(i));


            train=JOINPATH(folder_name,"Train_Cm1");
            Archivo.open(train.c_str());
            for(unsigned int i=0; i<Cm_dp1.size(); i++)
	    if(out.at(i)!=1000)
            {
                Archivo << Cm_dp1.at(i)/maximoCm1<<" ";
                for(unsigned int j=0; j<in.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";
                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cm1 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cm1.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cm1", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cm1.model %s",folder_name);
            system(aux);
//--------------------------------------------------------------------------------
//			DP2
//--------------------------------------------------------------------------------
//--------------------------------------------------------------------------------

        maximoCd2=Cd_dp2.at(0);

        for(unsigned int i=0; i<Cd_dp2.size(); i++)
            if(maximoCd2<fabs(Cd_dp2.at(i)))
            maximoCd2=fabs(Cd_dp2.at(i));

            train=JOINPATH(folder_name,"Train_Cd2");

            Archivo.open(train.c_str());

            for(unsigned int i=0; i<Cd_dp2.size(); i++)
	    if(out.at(i)!=1000)
            {

                Archivo << Cd_dp2.at(i)/maximoCd2<<" "; //-media

                for(unsigned int j=0; j<in.at(0).size()-1; j++)

                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";



                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cd2 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cd2.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cd2", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cd2.model %s",folder_name);
            system(aux);

//--------------------------------------------------------------------------------

        maximoCl2=Cl_dp2.at(0);

        for(unsigned int i=0; i<Cl_dp2.size(); i++)
            if(maximoCl2<fabs(Cl_dp2.at(i)))
            maximoCl2=fabs(Cl_dp2.at(i));

            train=JOINPATH(folder_name,"Train_Cl2");
            Archivo.open(train.c_str());
            for(unsigned int i=0; i<Cl_dp2.size(); i++)
	    if(out.at(i)!=1000)
            {
                Archivo << Cl_dp2.at(i)/maximoCl2<<" "; //-media
                for(unsigned int j=0; j<in.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";
                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cl2 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cl2.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cl2", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cl2.model %s",folder_name);
            system(aux);

//--------------------------------------------------------------------------------

        maximoCm2=Cm_dp2.at(0);

        for(unsigned int i=0; i<Cm_dp2.size(); i++)
            if(maximoCm2<fabs(Cm_dp2.at(i)))
            maximoCm2=fabs(Cm_dp2.at(i));

            train=JOINPATH(folder_name,"Train_Cm2");
            Archivo.open(train.c_str());
            for(unsigned int i=0; i<Cm_dp2.size(); i++)
	    if(out.at(i)!=1000)
            {
                Archivo << Cm_dp2.at(i)/maximoCm2<<" "; //-media
                for(unsigned int j=0; j<in.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";
                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Cm2 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Cm2.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Cm2", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Cm2.model %s",folder_name);
            system(aux);

//--------------------------------------------------------------------------------

// Base de datos que clasifica entre modelos viables (cumple restriccion de geometria y no hay error al deformar la malla) y no viables.

//--------------------------------------------------------------------------------

            train=JOINPATH(folder_name,"Train_Clase");
            Archivo.open(train.c_str());
            for(unsigned int i=0; i<out.size(); i++)
            {
                Archivo << (out.at(i)==1000)<<" ";
                for(unsigned int j=0; j<in.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<in.at(i).at(j)<<"\t";
                Archivo<<in.at(0).size()<<":"<<in.at(i).back();

                Archivo<<"\n";
            }
            Archivo.close();


            // Re-entrenar
        
            sprintf(cmd, "%s/gridregression.py %s/Train_Clase 2>/dev/null | \
                tail -n1 > %s/S1", SVMLIB_PATH, folder_name,folder_name);          
            system(cmd); 
            
            sprintf(aux,"mv Train_Clase.out %s",folder_name);
            system(aux);
        
            sprintf(cmd2, "cat %s/S1", folder_name);         
            system(cmd2); 
            
            sprintf(cmd3, "C=`cat %s/S1 | cut -d' ' -f 1`; G=`cat %s/S1 | \
                cut -d' ' -f 2`; P=`cat %s/S1 | cut -d' ' -f 3`; \
                %s/svm-train -c $C -g $G -p $P -d 25 -s 3 -q %s/Train_Clase", \
                folder_name, folder_name, folder_name, SVMLIB_PATH, folder_name);
            system(cmd3); 
            
            sprintf(aux, "mv Train_Clase.model %s",folder_name);
            system(aux);
        
//--------------------------------------------------------------------------------


            

    }

    private:

};

void ReadEA_Params(char *filename)
{
    FILE *fe= fopen(filename,"r");
 
    char caracteres[100];
       
    if (fe == NULL)
    {
        printf("\n Cannot find EA paramfile \n");
        exit(1);
    
    }
    
    fscanf(fe,"Test case directory: %s\n", folder_name);
    printf("%s\n", folder_name);
    
    fscanf(fe,"Paramfile_dp1: %s\n", paramfile_dp1_name);
    printf("%s\n", paramfile_dp1_name);
    
    fscanf(fe,"Paramfile_dp2: %s\n", paramfile_dp2_name);
    printf("%s\n", paramfile_dp2_name);
    
    
    fscanf(fe,"Grid: %s\n", grid_name);
    printf("%s\n", grid_name);
    
    fscanf(fe,"Nurbs: %s\n", nurbs_name);
    printf("%s\n", nurbs_name);
    
    fscanf(fe,"NumDV: %s\n", numDV);
    printf("%s\n", numDV);
    
    fscanf(fe,"Parallel (0: seq, 1: paral): %s\n", parallel);
    printf("%s\n", parallel);
    
    fscanf(fe,"Case (0:cilin, 1:rae, 2:dpw): %s\n", testcase);
    printf("%s\n", testcase);
     
    fscanf(fe,"FO: %s\n", objective_function);
    printf("%s\n", objective_function);
    
    fscanf(fe,"Multipoint: %s\n", multipoint);
    printf("%s\n", multipoint);
    
    fclose(fe);
}

void Inicializacion()
{
        char cmd[2056]="";
        sprintf(cmd, "python ./init.py %s %s %s %s %s %i %i %i %i", folder_name, \
            paramfile_dp1_name, paramfile_dp2_name, grid_name, nurbs_name, \
            atoi(numDV), atoi(parallel), atoi(testcase), atoi(multipoint));          
        system(cmd); 
        //grid2uv, calcula rangos y CFD inicial
	
        string rangostxt=JOINPATH(folder_name,"rangos.txt");
        ifstream R(rangostxt.c_str());
	     
	double aux;
    	R>>aux;
	while(!R.eof())
	{
		Rmax.push_back(aux);
		R>>aux;
		Rmin.push_back(aux);		
        	R>>aux;
	}
	
	Npuntos=Rmax.size();
	
	R.close();

        string datosinitxt_dp1=JOINPATH(folder_name,"datos_ini_dp1.txt");
        R.open(datosinitxt_dp1.c_str());		
	
	R>>Cd0_dp1;
	R>>Cl0_dp1;
	R>>Cm0_dp1;
	
	R.close();
        
        string datosinitxt_dp2=JOINPATH(folder_name,"datos_ini_dp2.txt");
        R.open(datosinitxt_dp2.c_str());		
	
	R>>Cd0_dp2;
	R>>Cl0_dp2;
	R>>Cm0_dp2;
	
	R.close();
}


int main(int argc, char* argv[])
{
    char cmd[1024]="";
    char *filename;
    double fo_dp1, fo_dp2, fo=0.0;
    double S;
    
    printf("---------------------------------------------------------------\n");
    printf("\n");
    printf("WELCOME TO THE EA + SVM PROGRAM \n");
    printf("\n");
    printf("---------------------------------------------------------------\n");
    
    if(argc>1)
    {
        printf("0 is %s, 1 is %s\n",argv[0],argv[1]);
        filename=argv[1];
    }
    else
    {
        printf("Error: Incorrect usage - first argument=EA parameter file\n");
        return 0;
    }
    
    printf("Reading EA parameters from file.... \n");
    ReadEA_Params(filename);
    printf ("Folder case: %s\n",folder_name);
    printf ("Parameter file name DP1: %s\n",paramfile_dp1_name);
    printf ("Parameter file name DP2: %s\n",paramfile_dp2_name);
    printf ("Grid name: %s\n",grid_name);
    printf ("Nurbs name: %s\n", nurbs_name);
    printf ("NumDV: %i\n", atoi(numDV));
    printf ("parallel: %i\n", atoi(parallel));
    printf ("testcase: %i\n", atoi(testcase));
    printf ("Objective function: %i\n", atoi(objective_function));
    printf ("Multipoint: %i\n",atoi(multipoint));
    
    srand (time(NULL));

    Inicializacion();

    BaseDeDatos DB;

    vector<double> Punto;

    //Incorporar la solución original a la base de datos
    //1.Leo la geometría inicial y normalizamos
    vector<double> PuntoInicial;
    double aux, aux_normalized, rango, norm;
   
    string geominitxt=JOINPATH(folder_name,"geom_ini.txt");
    ifstream A(geominitxt.c_str());
    for (int i=0; i<Npuntos; i++)
    {
      A>>aux;
            
      aux_normalized=(aux-Rmin[i])/(Rmax[i]-Rmin[i]);   
      PuntoInicial.push_back(aux_normalized);
    }
    A.close();
    
    //2.Introducimos en la base de datos
    DB.in.push_back(PuntoInicial);
    
    //3.Introducimos en la base de datos los valores de Cd0, Cl0 y Cm0
    DB.Cd_dp1.push_back(Cd0_dp1);
    DB.Cl_dp1.push_back(Cl0_dp1);
    DB.Cm_dp1.push_back(Cm0_dp1); 
    
    DB.Cd_dp2.push_back(Cd0_dp2);
    DB.Cl_dp2.push_back(Cl0_dp2);
    DB.Cm_dp2.push_back(Cm0_dp2);
    
    //4.Introducimos en la base de datos la función objetivo para el caso inicial
    fo_dp1=FuncionObjetivo(Cd0_dp1, Cl0_dp1, Cm0_dp1, Cd0_dp1, Cl0_dp1, Cm0_dp1);
    DB.out_dp1.push_back(fo_dp1);
    fo_dp2=FuncionObjetivo(Cd0_dp2, Cl0_dp2, Cm0_dp2, Cd0_dp2, Cl0_dp2, Cm0_dp2);
    DB.out_dp2.push_back(fo_dp2);
    fo=(fo_dp1+fo_dp2)/2;
    DB.out.push_back(fo);

    for(int i=0; i<PUNTOS_INICIALES; i++ )
    {
        Punto=DB.GeneraPuntoAleatorio(Npuntos);
        double a,b,c,d,e,f, S_dp1, S_dp2;
        S=Simular(Punto,i+1,&a,&b,&c,&d,&e,&f,&S_dp1,&S_dp2);
        while (S==1000)
        {
            Punto=DB.GeneraPuntoAleatorio(Npuntos);
            S=Simular(Punto,i+1,&a,&b,&c,&d,&e,&f,&S_dp1,&S_dp2);
        }
        DB.in.push_back(Punto);
        DB.out.push_back(S);
        DB.out_dp1.push_back(S_dp1);
        DB.out_dp2.push_back(S_dp2);
        DB.Cd_dp1.push_back(a);
        DB.Cl_dp1.push_back(b);
        DB.Cm_dp1.push_back(c);   
        DB.Cd_dp2.push_back(d);
        DB.Cl_dp2.push_back(e);
        DB.Cm_dp2.push_back(f);
    }

    DB.Generar_SVM();

//-----------------------------------------------
// ALGORITMO EVOLUTIVO
//-----------------------------------------------

     vector <vector <double> > Elementos;
     vector<double> Fitness;


     int Sel[TPOB];
     int Elim[TPOB];

    for(int ITS=0; ITS<5*5*Npuntos-PUNTOS_INICIALES-1; ITS++)
    {

     double Media=0;
     int MinAnt=-1;
     int Min=0;
     int j, k;

        Elementos.clear();

        for(int i=0; i<TPOB; i++)
        {
            vector<double> Pt;

            for(int j=0; j<Npuntos; j++)
                Pt.push_back(ALEA_01);

            Elementos.push_back(Pt);
        }

        cout<<"-----------------------------------\n";

        for(int zz=0; zz<250; zz++)
        {

            //Guardar Elementos
            string testtxt=JOINPATH(folder_name,"Test");
            ofstream Archivo(testtxt.c_str());
            for(unsigned int i=0; i<TPOB; i++)
            {
                Archivo << 0 <<" ";
                for(unsigned int j=0; j<Elementos.at(0).size()-1; j++)
                    Archivo<<j+1<<":"<<Elementos.at(i).at(j)<<"\t";

                Archivo<<Elementos.at(0).size()<<":"<<Elementos.at(i).back();

                Archivo<<"\n";
            }

            Archivo.close();


	    //Evaluamos las 6 SVMs entrenadas (Cd1 Cl1 Cm1 Cd2 Cl2 Cm2)

	//------------------------------------------------------------------------------------------                        
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cd1.model %s/salidaCd1 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------            
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cl1.model %s/salidaCl1 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------                        
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cm1.model %s/salidaCm1 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------            
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cd2.model %s/salidaCd2 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------                        
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cl2.model %s/salidaCl2 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------            
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Cm2.model %s/salidaCm2 > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------            

		// Evaluamos el clasificador (por ahora uso regresión, pero lo ideal es usar un clasificador binario).

	//------------------------------------------------------------------------------------------            
            sprintf(cmd, "%s/svm-predict %s/Test %s/Train_Clase.model %s/salidaClase > /dev/null", \
                    SVMLIB_PATH, folder_name, folder_name, folder_name);          
            system(cmd); 
	//------------------------------------------------------------------------------------------            

            //Leer resultados
            string salida=JOINPATH(folder_name,"salida");
            ifstream Archivo2("salidaCd1");
            ifstream Archivo3("salidaCl1");
            ifstream Archivo4("salidaCm1");
            ifstream Archivo5("salidaCd2");
            ifstream Archivo6("salidaCl2");
            ifstream Archivo7("salidaCm2");

            ifstream Archivo8("salidaClase");

            Fitness.clear();
            double S;
//#####################################################################
	    double Cd1;
	    double Cl1;
	    double Cm1;
	    double Cd2;
	    double Cl2;
	    double Cm2;

	    double Clase;
//#####################################################################
            for(int i=0; i<TPOB; i++)
            {
                Archivo2>>Cd1;
                Archivo3>>Cl1;
                Archivo4>>Cm1;
                Archivo5>>Cd2;
                Archivo6>>Cl2;
                Archivo7>>Cm2;

                Archivo8>>Clase;
		Clase=(Clase>0.5); // 0 diseño viable, 1 diseño no viable

        Cd1=Cd1*DB.maximoCd1;
        Cl1=Cl1*DB.maximoCl1;
        Cm1=Cm1*DB.maximoCm1;

        Cd2=Cd2*DB.maximoCd2;
        Cl2=Cl2*DB.maximoCl2;
        Cm2=Cm2*DB.maximoCm2;

		if(Clase==0)
		S=0.5*(FuncionObjetivo (Cd1, Cl1, Cm1, Cd0_dp1, Cl0_dp1, Cm0_dp1)+FuncionObjetivo (Cd2, Cl2, Cm2, Cd0_dp2, Cl0_dp2, Cm0_dp2));
		else
		S=1000;

                Fitness.push_back(S);
            }

            Archivo2.close();
            Archivo3.close();
            Archivo4.close();
            Archivo5.close();
            Archivo6.close();
            Archivo7.close();

            Archivo8.close();

//#####################################################################

            Media=0;

            /*Valor medio*/
            for(int i=0; i<TPOB; i++)
                Media+=Fitness.at(i)/(double)TPOB;

            /*Minimizamos (error)*/
            Min=0;

            for(int i=0; i<TPOB; i++)
                if(Fitness.at(Min)>Fitness.at(i))
                    Min=i;

            if(Min!=MinAnt)
            {
               // cout<<Fitness.at(Min)<<"\t"<<Media<<"\n";

                MinAnt=Min;
            }


            j=0; k=0;
            /*SE selecionan los buenos y se eliminan los malos*/
            for(int i=0; i<TPOB; i++)
                 if(i==Min || Fitness.at(i) < Media*(1+0.01*ALEA_11))
                 {
                          Sel[j]=i;
                          j++;
                 }
                 else
                 {
                          Elim[k]=i;
                          k++;
                 }

            /* Cada elemento eliminado se reemplaza por uno nuevo*/
            for(int i=0; i<k; i++)
            {
                int P1=rand()%j;
                int P2=rand()%j;
                Nuevo(&Elementos.at(Elim[i]),&Elementos.at(Sel[P1]),\
                        &Elementos.at(Sel[P2]), Fitness.at(P1), Fitness.at(P2));
            }
        }


        Punto=Elementos.at(Min);
        double a,b,c,d,e,f, S_dp1, S_dp2;
        S=Simular(Punto,ITS+5,&a,&b,&c,&d,&e,&f,&S_dp1,&S_dp2);
        
        while (S==1000)
        {
            Fitness.at(Min)=1000;

	// Ahora nos interesa guardar los valores para la base de datos de clasificación.
	        DB.in.push_back(Punto);
	        DB.out.push_back(S);
	        DB.out_dp1.push_back(S_dp1);
	        DB.out_dp2.push_back(S_dp2);
	        DB.Cd_dp1.push_back(a);
	        DB.Cl_dp1.push_back(b);
	        DB.Cm_dp1.push_back(c);  
	        DB.Cd_dp2.push_back(d);
	        DB.Cl_dp2.push_back(e);
	        DB.Cm_dp2.push_back(f);

            /*Volvemos a calcular el minimo*/
            Min=0;
            for(int i=0; i<TPOB; i++)
                if(Fitness.at(Min)>Fitness.at(i))
                    Min=i;
            
            if (Fitness.at(Min)==1000)
                Punto=DB.GeneraPuntoAleatorio(Npuntos);
            else
                Punto=Elementos.at(Min); 
           
            S=Simular(Punto,ITS+5,&a,&b,&c,&d,&e,&f,&S_dp1,&S_dp2);
        }
        
        DB.in.push_back(Punto);
        DB.out.push_back(S);
        DB.out_dp1.push_back(S_dp1);
        DB.out_dp2.push_back(S_dp2);
        DB.Cd_dp1.push_back(a);
        DB.Cl_dp1.push_back(b);
        DB.Cm_dp1.push_back(c);  
        DB.Cd_dp2.push_back(d);
        DB.Cl_dp2.push_back(e);
        DB.Cm_dp2.push_back(f);
        DB.Generar_SVM();

        //Shows the optimization in the screen
        printf("#geom       FO         FO_dp1            Cd_dp1          Cl_dp1            Cm_dp1           FO_dp2          Cd_dp2           Cl_dp2          Cm_dp2\n\n");
        for(unsigned int h=0; h<DB.in.size(); h++)
        {
            printf("%i \t %f\t %f\t %f \t %f \t %f \t %f \t  %f \t  %f \t %f\n", h, DB.out.at(h), DB.out_dp1.at(h), \
                    DB.Cd_dp1.at(h), DB.Cl_dp1.at(h),DB.Cm_dp1.at(h), DB.out_dp2.at(h), DB.Cd_dp2.at(h), \
                    DB.Cl_dp2.at(h),DB.Cm_dp2.at(h));  
        }

        string resultadostxt=JOINPATH(folder_name,"Resultados.txt");
	ofstream Res(resultadostxt.c_str());
        
        for(unsigned int h=0; h<DB.in.size(); h++)
        {
            
            Res<< h <<"\t"<< DB.out.at(h)<< "\t";
            Res<< DB.out_dp1.at(h)<< "\t";
            Res<< DB.Cd_dp1.at(h)<< "\t";
            Res<< DB.Cl_dp1.at(h)<< "\t";
            Res<< DB.Cm_dp1.at(h)<< "\t";
            
            Res<< DB.out_dp2.at(h)<< "\t";
            Res<< DB.Cd_dp2.at(h)<< "\t";
            Res<< DB.Cl_dp2.at(h)<< "\t";
            Res<< DB.Cm_dp2.at(h)<< "\t";
                                                                                              
            for(unsigned int g=0; g< DB.in.at(0).size(); g++)
                Res<<DB.in.at(h).at(g)*(Rmax[g]-Rmin[g])+Rmin[g]<<"\t";

            Res<<"\n";
        }
                
        Res.close();                    
    }
    
    return 0;
}
