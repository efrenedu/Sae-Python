import mysql.connector.plugins.mysql_native_password
import mysql.connector
import subprocess
from subprocess import Popen
import os
from constantes import constantes
from General import General
import math
import random

#Manage the Data Base Information
class conexion_bd:
    conect=None
    tabla_selected=""
    db_actual=""
    root_pass=""
    cursor=None
    mysql_folder=""
    Admin_default=["admin01","Admin123%"]   
 
    #Reset a Table
    @classmethod	
    def reset_table(cls):
        query=""
        query="TRUNCATE TABLE "+cls.tabla_selected+";"
        cls.cursor.execute(query)    
    
    #Init the Connection
    @classmethod	
    def init(cls):
        data_b="Instituto"   
        try:        
          if(cls.connect(data_b)):
               cls.set_tabla(constantes.TABLA_USUARIO)
               return True
               
        except:
          return False
       
    #set foregein Check state
    @classmethod
    def set_foregein_check(cls,valor): 
        query=""
        if(valor==False):
             query="SET FOREIGN_KEY_CHECKS = 0;"
        else:
            query="SET FOREIGN_KEY_CHECKS = 1;"
        cls.cursor.execute(query)
    
    #set the Table Target for Operations    
    @classmethod
    def set_tabla(cls,tabla_name):
        cls.tabla_selected=tabla_name
    
    #get all Data of Table as List    
    @classmethod
    def get_allData(cls,campos,num_campos,conditions=None,values=None,condition_types=None):
        query="SELECT "
        if(campos==None):
            query+="* FROM "
        else:
           for i in range(0,num_campos):
               query+=campos[i]
               if(i<num_campos-1):
                  query+=" , "
           query+=" FROM "
        query+=cls.tabla_selected
        if(conditions!=None and values!=None and condition_types!=None):
           query+=" WHERE "
           for i in range(0,len(conditions)):
               if(i>=1):
                 cond=condition_types[i]
                 cond=cond.upper()
                 query+=" "+cond
                 query+=" "  
               query+=conditions[i]+"='"+values[i]+"'"   
        query+=";"  
        try:
          cls.cursor.execute(query)
          data=cls.cursor.fetchall()
          return data
        except:
          return []        
        
    #add Data to a Table    
    @classmethod
    def add_data(cls,values):    
      query="INSERT INTO "+cls.tabla_selected+" VALUES ( "
      for i in range(0,len(values)):
        query+="'"+values[i]+"'"
        if(i<len(values)-1):
           query+=" , "        
      query+=" );"        
      try:
        cls.cursor.execute(query)
        cls.conect.commit()
        return 0
      except:
         return -1

    #update a Field of table Target
    @classmethod
    def update_data(cls,campos,values,num_campos,conditions,values_conditions,conditions_types):
       query="UPDATE "+cls.tabla_selected+" SET "
       for i in range(0,num_campos):
          query+=campos[i]+"='"+values[i]+"'"
          if(i<num_campos-1):
             query+=" , "
       query+=" WHERE "
       for i in range(0,len(conditions)):
           if(i>=1):
              query+=" "+conditions_types[i].upper()+" "
           query+=conditions[i]+"='"+values_conditions[i]+"'"
       query+=";"      
       try:
          cls.cursor.execute(query) 
          cls.conect.commit()
          return 0
       except:
          return -1 

    #delete a Register of the Table target
    @classmethod
    def delete_data(cls,conditions,values_conditions,conditions_types):   
        query="DELETE FROM "+cls.tabla_selected+" WHERE "
        for i in range(0,len(conditions)):
            if(i>=1):
               query+=" "+conditions_types[i].upper()+" "
            query+=conditions[i]+"='"+values_conditions[i]+"'"
        query+=";" 
        try:
           cls.cursor.execute(query) 
           cls.conect.commit()
           return 0
        except:
           return -1
     
    #Return True if the Table is Empty     
    @classmethod
    def is_empty(cls):
       res=False       
       query="SELECT * FROM "+cls.tabla_selected+";"
       cls.cursor.execute(query)
       last=len(cls.cursor.fetchall())            
       if(str(last)=="0"):
          res=True
       return res
       
    #generate a Ket Field Id Based in number of Registers    
    @classmethod
    def generate_id(cls,hard_verific=False,id_name=""):
        
          query="SELECT * FROM "+cls.tabla_selected+";"
          cls.cursor.execute(query)
          last=len(cls.cursor.fetchall())
          if(hard_verific==False):
             return str(last)
          else:
            id_val=int(last)
            if(id_val>0):
                 index=-1
                 for i in range(0,id_val+1):
                    if(cls.id_exist(id_name,str(i))==False):
                       index=i
                       break
                 if(index!=-1):
                    return str(index)
                 else:
                   return str(id_val)
            else:
               return str(id_val)
               
    #Return True if the Id  withe Indicated Value exist in the Table     
    @classmethod
    def id_exist(cls,id_name,id_value):
       query="SELECT * FROM "+cls.tabla_selected+" WHERE "
       query+=id_name+"='"+id_value+"';"
       try:
         cls.cursor.execute(query)
         data=cls.cursor.fetchall()
         if(data==[]):
             return False
         else:
             return True
       except:
         return False
     
    #Restore Data Base from CSV File
    @classmethod
    def restore_bd(cls,path,formato,root):
          from documento import documento     
          data=[constantes.NUM_TABLAS,[],path]
          data[1].append(constantes.TABLA_CALIF_PENDIENTE)
          data[1].append(constantes.TABLA_MATERIA_PENDIENTE)
          data[1].append(constantes.TABLA_CALIFICACION)
          data[1].append(constantes.TABLA_CALIF_MOM)
          data[1].append(constantes.TABLA_CALIFICACION_FINAL)
          data[1].append(constantes.TABLA_FECHA)
          data[1].append(constantes.TABLA_MOMENTO)
          data[1].append(constantes.TABLA_CRONOGRAMA)
          data[1].append(constantes.TABLA_AREA_DOCENTE)
          data[1].append(constantes.TABLA_PROFESOR)
          data[1].append(constantes.TABLA_AREA_FORMACION)
          data[1].append(constantes.TABLA_AÑOS_INCORPORADOS)   
          data[1].append(constantes.TABLA_DISP_HORARIO)
          data[1].append(constantes.TABLA_REPORTE)
          data[1].append(constantes.TABLA_PREGUNTA_SECRETA)
          data[1].append(constantes.TABLA_USUARIO) 
          data[1].append(constantes.TABLA_INTENTOS_USUARIO)
          data[1].append(constantes.TABLA_DESCARGA_DOCUMENTO)
          data[1].append(constantes.TABLA_FORMATO)
          data[1].append(constantes.TABLA_TRABAJADOR)
          data[1].append(constantes.TABLA_ESTUDIANTE)
          data[1].append(constantes.TABLA_SECCION)
          data[1].append(constantes.TABLA_HORARIO)
          data[1].append(constantes.TABLA_ESTATUS_ESTUD)
          data[1].append(constantes.TABLA_ESTATUS_TRABAJ)
          data[1].append(constantes.TABLA_REPRESENTANTE)
          data[1].append(constantes.TABLA_NOMBRE)
          data[1].append(constantes.TABLA_CARGO)
          data[1].append(constantes.TABLA_DIRECCION)
          data[1].append(constantes.TABLA_EXPEDIENTE)
          documento.request(root,path,7,data)
        
    #Build CSV Files withe Information of Data Base
    @classmethod
    def respaldar_bd(cls,folder,filename,formato,root):
          from documento import documento
          data=[constantes.NUM_TABLAS,[],folder,[]]
          data[1].append(constantes.TABLA_AREA_DOCENTE)
          data[1].append(constantes.TABLA_AREA_FORMACION)
          data[1].append(constantes.TABLA_CALIFICACION)
          data[1].append(constantes.TABLA_CALIFICACION_FINAL)
          data[1].append(constantes.TABLA_CALIF_MOM)
          data[1].append(constantes.TABLA_CALIF_PENDIENTE)
          data[1].append(constantes.TABLA_CRONOGRAMA)
          data[1].append(constantes.TABLA_DIRECCION)
          data[1].append(constantes.TABLA_DISP_HORARIO)
          data[1].append(constantes.TABLA_ESTUDIANTE)
          data[1].append(constantes.TABLA_EXPEDIENTE)
          data[1].append(constantes.TABLA_FECHA) 
          data[1].append(constantes.TABLA_FORMATO)
          data[1].append(constantes.TABLA_HORARIO)
          data[1].append(constantes.TABLA_MOMENTO)
          data[1].append(constantes.TABLA_MATERIA_PENDIENTE)          
          data[1].append(constantes.TABLA_PREGUNTA_SECRETA)
          data[1].append(constantes.TABLA_PROFESOR)
          data[1].append(constantes.TABLA_REPORTE)
          data[1].append(constantes.TABLA_REPRESENTANTE)
          data[1].append(constantes.TABLA_SECCION)
          data[1].append(constantes.TABLA_TRABAJADOR)
          data[1].append(constantes.TABLA_USUARIO)  
          data[1].append(constantes.TABLA_CARGO)
          data[1].append(constantes.TABLA_NOMBRE)
          data[1].append(constantes.TABLA_DESCARGA_DOCUMENTO)
          data[1].append(constantes.TABLA_ESTATUS_TRABAJ)
          data[1].append(constantes.TABLA_ESTATUS_ESTUD)
          data[1].append(constantes.TABLA_INTENTOS_USUARIO)
          data[1].append(constantes.TABLA_AÑOS_INCORPORADOS)
          data[3].append(constantes.CAMPOS_AREA_DOCENTE)
          data[3].append(constantes.CAMPOS_AREA_FORMACION)
          data[3].append(constantes.CAMPOS_CALIFICACION)
          data[3].append(constantes.CAMPOS_CALIFICACION_FINAL)
          data[3].append(constantes.CAMPOS_CALIF_MOM)
          data[3].append(constantes.CAMPOS_CALIF_PENDIENTE)
          data[3].append(constantes.CAMPOS_CRONOGRAMA)
          data[3].append(constantes.CAMPOS_DIRECCION)
          data[3].append(constantes.CAMPOS_DISP_HORARIO)
          data[3].append(constantes.CAMPOS_ESTUDIANTE)
          data[3].append(constantes.CAMPOS_EXPEDIENTE)
          data[3].append(constantes.CAMPOS_FECHA)
          data[3].append(constantes.CAMPOS_FORMATO)
          data[3].append(constantes.CAMPOS_HORARIO)
          data[3].append(constantes.CAMPOS_MOMENTO)
          data[3].append(constantes.CAMPOS_MATERIA_PENDIENTE)
          data[3].append(constantes.CAMPOS_PREGUNTA_SECRETA)
          data[3].append(constantes.CAMPOS_PROFESOR)
          data[3].append(constantes.CAMPOS_REPORTE)
          data[3].append(constantes.CAMPOS_REPRESENTANTE)
          data[3].append(constantes.CAMPOS_SECCION)
          data[3].append(constantes.CAMPOS_TRABAJADOR)
          data[3].append(constantes.CAMPOS_USUARIO)
          data[3].append(constantes.CAMPOS_CARGO)
          data[3].append(constantes.CAMPOS_NOMBRE)
          data[3].append(constantes.CAMPOS_DESCARGA_DOCUMENTO)
          data[3].append(constantes.CAMPOS_ESTATUS_TRABAJ)
          data[3].append(constantes.CAMPOS_ESTATUS_ESTUD)
          data[3].append(constantes.CAMPOS_INTENTOS_USUARIO)
          data[3].append(constantes.CAMPOS_AÑOS_INCORPORADOS)
          documento.request(root,filename,6,data)
    
     #Set Default Values of Tables    
    @classmethod
    def set_defaults_values(cls):    
        from tiempo import tiempo
        ti=tiempo()
        fecha=ti.get_fecha() 
        cls.set_tabla(constantes.TABLA_HORARIO)
        if(cls.id_exist(constantes.CLAVE_HORARIO,"default")==False):
            data_hor=["default","","",fecha]   
            cls.add_data(data_hor)  
        cls.set_tabla(constantes.TABLA_SECCION)
        if(cls.id_exist(constantes.CLAVE_SECCION,"default")==False):
            data_secc=["default","","","default","0","1000","0",fecha]   
            cls.add_data(data_secc)
        cls.set_tabla(constantes.TABLA_CARGO)
        if(cls.id_exist(constantes.CLAVE_CARGO,"default")==False):
            data_carg=["default","","",fecha,""]
            cls.add_data(data_carg) 
        cls.set_tabla(constantes.TABLA_EXPEDIENTE)
        if(cls.id_exist(constantes.CLAVE_EXPEDIENTE,"default")==False):
            data_exp=["default","","","",fecha]
            cls.add_data(data_exp)            
        cls.set_tabla(constantes.TABLA_TRABAJADOR)
        if(cls.id_exist(constantes.CLAVE_TRABAJADOR,"000")==False):
            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
            data_n=[conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE),"","","","",fecha]
            conexion_bd.add_data(data_n)
            conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
            data_estatus=[conexion_bd.generate_id(True,constantes.CLAVE_ESTATUS_TRABAJ),"inactivo","","",fecha]
            conexion_bd.add_data(data_estatus)
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            data_trabaj=["000",data_n[0],"","","default","default","default",data_estatus[0],fecha]   
            cls.add_data(data_trabaj)   
        if(cls.id_exist(constantes.CLAVE_TRABAJADOR,"001")==False):
            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
            data_n=[conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE),"admin","","admin","",fecha]
            conexion_bd.add_data(data_n)
            conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
            data_estatus=[conexion_bd.generate_id(True,constantes.CLAVE_ESTATUS_TRABAJ),"activo","","",fecha]
            conexion_bd.add_data(data_estatus)
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            data_trabaj=["001",data_n[0],"","","default","default","default",data_estatus[0],fecha]   
            cls.add_data(data_trabaj)
        cls.set_tabla(constantes.TABLA_USUARIO)
        if(cls.id_exist(constantes.CLAVE_USUARIO,cls.Admin_default[0])==False):
            conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
            data_intentos=[conexion_bd.generate_id(True,constantes.CLAVE_INTENTOS_USUARIO),"0","","",fecha]
            conexion_bd.add_data(data_intentos)
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            encripted_Admin=General.encriptar(cls.Admin_default[1])
            data_admin=[cls.Admin_default[0],encripted_Admin,"001","admin",constantes.DEFAULT_USER_ICON,data_intentos[0],"False",fecha]
            cls.add_data(data_admin)  
        orden=["Lengua y Literatura","Idiomas","Matematicas","Educacion Fisica","Arte y Patrimonio","Biologia Ambiente y Tecnologia","Fisica","Quimica","Ciencias de la Tierra","GHC","FSN","OV","GCRP"]     
        cls.set_tabla(constantes.TABLA_AREA_FORMACION)
        for odn in orden:
            if(cls.id_exist(constantes.CLAVE_AREA_FORMACION,odn)==False):
                    cls.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                    inc=[cls.generate_id(True,constantes.CLAVE_AÑOS_INCORPORADOS),"True","False","False","False","False",fecha]
                    cls.add_data(inc)
                    cls.set_tabla(constantes.TABLA_AREA_FORMACION)
                    d_area=[odn,"No",inc[0],fecha]
                    cls.add_data(d_area)

    #Build the Data Base
    @classmethod
    def create_base(cls,nomb_base):

        query="CREATE DATABASE "+nomb_base+";"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_DIRECCION+" ( "
        for i in range(0,len(constantes.CAMPOS_DIRECCION)):
            query+=constantes.CAMPOS_DIRECCION[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_DIRECCION)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_DIRECCION)):
            if(constantes.FORANEOS_DIRECCION[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_DIRECCION[j]+") REFERENCES "+constantes.FORANEOS_DIRECCION[j]+"("+constantes.CAMPOS_DIRECCION[j]+")"
                  
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CARGO+" ( "
        for i in range(0,len(constantes.CAMPOS_CARGO)):
            query+=constantes.CAMPOS_CARGO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CARGO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CARGO)):
            if(constantes.FORANEOS_CARGO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CARGO[j]+") REFERENCES "+constantes.FORANEOS_CARGO[j]+"("+constantes.CAMPOS_CARGO[j]+")"       
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_ESTATUS_TRABAJ+" ("
        for i in range(0,len(constantes.CAMPOS_ESTATUS_TRABAJ)):
            query+=constantes.CAMPOS_ESTATUS_TRABAJ[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_ESTATUS_TRABAJ)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_ESTATUS_TRABAJ)):
            if(constantes.FORANEOS_ESTATUS_TRABAJ[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_ESTATUS_TRABAJ[j]+") REFERENCES "+constantes.FORANEOS_ESTATUS_TRABAJ[j]+"("+constantes.CAMPOS_ESTATUS_TRABAJ[j]+")"
                 
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_ESTATUS_ESTUD+" ("
        for i in range(0,len(constantes.CAMPOS_ESTATUS_ESTUD)):
            query+=constantes.CAMPOS_ESTATUS_ESTUD[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_ESTATUS_ESTUD)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_ESTATUS_ESTUD)):
            if(constantes.FORANEOS_ESTATUS_ESTUD[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_ESTATUS_ESTUD[j]+") REFERENCES "+constantes.FORANEOS_ESTATUS_ESTUD[j]+"("+constantes.CAMPOS_ESTATUS_ESTUD[j]+")"       
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_AÑOS_INCORPORADOS+" ("
        for i in range(0,len(constantes.CAMPOS_AÑOS_INCORPORADOS)):
            query+=constantes.CAMPOS_AÑOS_INCORPORADOS[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_AÑOS_INCORPORADOS)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_AÑOS_INCORPORADOS)):
            if(constantes.FORANEOS_AÑOS_INCORPORADOS[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_AÑOS_INCORPORADOS[j]+") REFERENCES "+constantes.FORANEOS_AÑOS_INCORPORADOS[j]+"("+constantes.CAMPOS_AÑOS_INCORPORADOS[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_INTENTOS_USUARIO+" ("
        for i in range(0,len(constantes.CAMPOS_INTENTOS_USUARIO)):
            query+=constantes.CAMPOS_INTENTOS_USUARIO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_INTENTOS_USUARIO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_INTENTOS_USUARIO)):
            if(constantes.FORANEOS_INTENTOS_USUARIO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_INTENTOS_USUARIO[j]+") REFERENCES "+constantes.FORANEOS_INTENTOS_USUARIO[j]+"("+constantes.CAMPOS_INTENTOS_USUARIO[j]+")"                 
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_NOMBRE+" ("
        for i in range(0,len(constantes.CAMPOS_NOMBRE)):
            query+=constantes.CAMPOS_NOMBRE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_NOMBRE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_NOMBRE)):
            if(constantes.FORANEOS_NOMBRE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_NOMBRE[j]+") REFERENCES "+constantes.FORANEOS_NOMBRE[j]+"("+constantes.CAMPOS_NOMBRE[j]+")"                
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_EXPEDIENTE+" ( "
        for i in range(0,len(constantes.CAMPOS_EXPEDIENTE)):
            query+=constantes.CAMPOS_EXPEDIENTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_EXPEDIENTE)-1):
                 query+=" , "    
        for j in range(0,len(constantes.FORANEOS_EXPEDIENTE)):
            if(constantes.FORANEOS_EXPEDIENTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_EXPEDIENTE[j]+") REFERENCES "+constantes.FORANEOS_EXPEDIENTE[j]+"("+constantes.CAMPOS_EXPEDIENTE[j]+")"
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_HORARIO+" ( "
        for i in range(0,len(constantes.CAMPOS_HORARIO)):
            query+=constantes.CAMPOS_HORARIO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_HORARIO)-1):
                 query+=" , "
                 
        for j in range(0,len(constantes.FORANEOS_HORARIO)):
            if(constantes.FORANEOS_HORARIO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_HORARIO[j]+") REFERENCES "+constantes.FORANEOS_HORARIO[j]+"("+constantes.CAMPOS_HORARIO[j]+")"    
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_TRABAJADOR+" ( "
        for i in range(0,len(constantes.CAMPOS_TRABAJADOR)):
            query+=constantes.CAMPOS_TRABAJADOR[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_TRABAJADOR)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_TRABAJADOR)):
            if(constantes.FORANEOS_TRABAJADOR[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_TRABAJADOR[j]+") REFERENCES "+constantes.FORANEOS_TRABAJADOR[j]+"("+constantes.CAMPOS_TRABAJADOR[j]+")"        
        query+=" );"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_USUARIO+" ( "
        for i in range(0,len(constantes.CAMPOS_USUARIO)):
            query+=constantes.CAMPOS_USUARIO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_USUARIO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_USUARIO)):
            if(constantes.FORANEOS_USUARIO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_USUARIO[j]+") REFERENCES "+constantes.FORANEOS_USUARIO[j]+"("+constantes.CAMPOS_USUARIO[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_REPRESENTANTE+" ("
        for i in range(0,len(constantes.CAMPOS_REPRESENTANTE)):
            query+=constantes.CAMPOS_REPRESENTANTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_REPRESENTANTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_REPRESENTANTE)):
            if(constantes.FORANEOS_REPRESENTANTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_REPRESENTANTE[j]+") REFERENCES "+constantes.FORANEOS_REPRESENTANTE[j]+"("+constantes.CAMPOS_REPRESENTANTE[j]+")"         
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_SECCION+" ("
        for i in range(0,len(constantes.CAMPOS_SECCION)):
            query+=constantes.CAMPOS_SECCION[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_SECCION)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_SECCION)):
            if(constantes.FORANEOS_SECCION[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_SECCION[j]+") REFERENCES "+constantes.FORANEOS_SECCION[j]+"("+constantes.CAMPOS_SECCION[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_PROFESOR+" ("
        for i in range(0,len(constantes.CAMPOS_PROFESOR)):
            query+=constantes.CAMPOS_PROFESOR[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_PROFESOR)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_PROFESOR)):
            if(constantes.FORANEOS_PROFESOR[j]!=False):
                query+=" , "
                if(constantes.FORANEOS_PROFESOR[j]==constantes.TABLA_SECCION):
                   query+="FOREIGN KEY("+constantes.CAMPOS_PROFESOR[j]+") REFERENCES "+constantes.FORANEOS_PROFESOR[j]+"("+constantes.CLAVE_SECCION+")"
                    
                else:
                    query+="FOREIGN KEY("+constantes.CAMPOS_PROFESOR[j]+") REFERENCES "+constantes.FORANEOS_PROFESOR[j]+"("+constantes.CAMPOS_PROFESOR[j]+")"
                    
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_ESTUDIANTE+" ("
        for i in range(0,len(constantes.CAMPOS_ESTUDIANTE)):
            query+=constantes.CAMPOS_ESTUDIANTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_ESTUDIANTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_ESTUDIANTE)):
            if(constantes.FORANEOS_ESTUDIANTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_ESTUDIANTE[j]+") REFERENCES "+constantes.FORANEOS_ESTUDIANTE[j]+"("+constantes.CAMPOS_ESTUDIANTE[j]+")"   
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_AREA_FORMACION+" ("
        for i in range(0,len(constantes.CAMPOS_AREA_FORMACION)):
            query+=constantes.CAMPOS_AREA_FORMACION[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_AREA_FORMACION)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_AREA_FORMACION)):
            if(constantes.FORANEOS_AREA_FORMACION[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_AREA_FORMACION[j]+") REFERENCES "+constantes.FORANEOS_AREA_FORMACION[j]+"("+constantes.CAMPOS_AREA_FORMACION[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_AREA_DOCENTE+" ("
        for i in range(0,len(constantes.CAMPOS_AREA_DOCENTE)):
            query+=constantes.CAMPOS_AREA_DOCENTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_AREA_DOCENTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_AREA_DOCENTE)):
            if(constantes.FORANEOS_AREA_DOCENTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_AREA_DOCENTE[j]+") REFERENCES "+constantes.FORANEOS_AREA_DOCENTE[j]+"("+constantes.CAMPOS_AREA_DOCENTE[j]+")"         
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_REPORTE+" ("
        for i in range(0,len(constantes.CAMPOS_REPORTE)):
            query+=constantes.CAMPOS_REPORTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_REPORTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_REPORTE)):
            if(constantes.FORANEOS_REPORTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_REPORTE[j]+") REFERENCES "+constantes.FORANEOS_REPORTE[j]+"("+constantes.CAMPOS_REPORTE[j]+")"       
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_FORMATO+" ("
        for i in range(0,len(constantes.CAMPOS_FORMATO)):
            query+=constantes.CAMPOS_FORMATO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_FORMATO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_FORMATO)):
            if(constantes.FORANEOS_FORMATO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_FORMATO[j]+") REFERENCES "+constantes.FORANEOS_FORMATO[j]+"("+constantes.CAMPOS_FORMATO[j]+")"                   
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CRONOGRAMA+" ("
        for i in range(0,len(constantes.CAMPOS_CRONOGRAMA)):
            query+=constantes.CAMPOS_CRONOGRAMA[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CRONOGRAMA)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CRONOGRAMA)):
            if(constantes.FORANEOS_CRONOGRAMA[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CRONOGRAMA[j]+") REFERENCES "+constantes.FORANEOS_CRONOGRAMA[j]+"("+constantes.CAMPOS_CRONOGRAMA[j]+")"                   
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_MOMENTO+" ("
        for i in range(0,len(constantes.CAMPOS_MOMENTO)):
            query+=constantes.CAMPOS_MOMENTO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_MOMENTO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_MOMENTO)):
            if(constantes.FORANEOS_MOMENTO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_MOMENTO[j]+") REFERENCES "+constantes.FORANEOS_MOMENTO[j]+"("+constantes.CAMPOS_MOMENTO[j]+")"
                 
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_FECHA+" ("
        for i in range(0,len(constantes.CAMPOS_FECHA)):
            query+=constantes.CAMPOS_FECHA[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_FECHA)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_FECHA)):
            if(constantes.FORANEOS_FECHA[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_FECHA[j]+") REFERENCES "+constantes.FORANEOS_FECHA[j]+"("+constantes.CAMPOS_FECHA[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_PREGUNTA_SECRETA+" ("
        for i in range(0,len(constantes.CAMPOS_PREGUNTA_SECRETA)):
            query+=constantes.CAMPOS_PREGUNTA_SECRETA[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_PREGUNTA_SECRETA)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_PREGUNTA_SECRETA)):
            if(constantes.FORANEOS_PREGUNTA_SECRETA[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_PREGUNTA_SECRETA[j]+") REFERENCES "+constantes.FORANEOS_PREGUNTA_SECRETA[j]+"("+constantes.CAMPOS_PREGUNTA_SECRETA[j]+")"          
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_DESCARGA_DOCUMENTO+" ("
        for i in range(0,len(constantes.CAMPOS_DESCARGA_DOCUMENTO)):
            query+=constantes.CAMPOS_DESCARGA_DOCUMENTO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_DESCARGA_DOCUMENTO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_DESCARGA_DOCUMENTO)):
            if(constantes.FORANEOS_DESCARGA_DOCUMENTO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_DESCARGA_DOCUMENTO[j]+") REFERENCES "+constantes.FORANEOS_DESCARGA_DOCUMENTO[j]+"("+constantes.CAMPOS_DESCARGA_DOCUMENTO[j]+")"
                 
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CALIFICACION_FINAL+" ("
        for i in range(0,len(constantes.CAMPOS_CALIFICACION_FINAL)):
            query+=constantes.CAMPOS_CALIFICACION_FINAL[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CALIFICACION_FINAL)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CALIFICACION_FINAL)):
            if(constantes.FORANEOS_CALIFICACION_FINAL[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CALIFICACION_FINAL[j]+") REFERENCES "+constantes.FORANEOS_CALIFICACION_FINAL[j]+"("+constantes.CAMPOS_CALIFICACION_FINAL[j]+")"   
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CALIF_MOM+" ("
        for i in range(0,len(constantes.CAMPOS_CALIF_MOM)):
            query+=constantes.CAMPOS_CALIF_MOM[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CALIF_MOM)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CALIF_MOM)):
            if(constantes.FORANEOS_CALIF_MOM[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CALIF_MOM[j]+") REFERENCES "+constantes.FORANEOS_CALIF_MOM[j]+"("+constantes.CAMPOS_CALIF_MOM[j]+")"
                
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CALIFICACION+" ("
        for i in range(0,len(constantes.CAMPOS_CALIFICACION)):
            query+=constantes.CAMPOS_CALIFICACION[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CALIFICACION)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CALIFICACION)):
            if(constantes.FORANEOS_CALIFICACION[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CALIFICACION[j]+") REFERENCES "+constantes.FORANEOS_CALIFICACION[j]+"("+constantes.CAMPOS_CALIFICACION[j]+")"
                         
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_DISP_HORARIO+" ("
        for i in range(0,len(constantes.CAMPOS_DISP_HORARIO)):
            query+=constantes.CAMPOS_DISP_HORARIO[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_DISP_HORARIO)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_DISP_HORARIO)):
            if(constantes.FORANEOS_DISP_HORARIO[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_DISP_HORARIO[j]+") REFERENCES "+constantes.FORANEOS_DISP_HORARIO[j]+"("+constantes.CAMPOS_DISP_HORARIO[j]+")"
                  
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_MATERIA_PENDIENTE+" ("
        for i in range(0,len(constantes.CAMPOS_MATERIA_PENDIENTE)):
            query+=constantes.CAMPOS_MATERIA_PENDIENTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_MATERIA_PENDIENTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_MATERIA_PENDIENTE)):
            if(constantes.FORANEOS_MATERIA_PENDIENTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_MATERIA_PENDIENTE[j]+") REFERENCES "+constantes.FORANEOS_MATERIA_PENDIENTE[j]+"("+constantes.CAMPOS_MATERIA_PENDIENTE[j]+")"
                         
        query+=");"
        cls.cursor.execute(query)
        query="CREATE TABLE "+nomb_base+"."+constantes.TABLA_CALIF_PENDIENTE+" ("
        for i in range(0,len(constantes.CAMPOS_CALIF_PENDIENTE)):
            query+=constantes.CAMPOS_CALIF_PENDIENTE[i]
            query+=" VARCHAR(100)"
            if(i==0):
               query+=" PRIMARY KEY"
            if(i<len(constantes.CAMPOS_CALIF_PENDIENTE)-1):
                 query+=" , "
        for j in range(0,len(constantes.FORANEOS_CALIF_PENDIENTE)):
            if(constantes.FORANEOS_CALIF_PENDIENTE[j]!=False):
                query+=" , "
                query+="FOREIGN KEY("+constantes.CAMPOS_CALIF_PENDIENTE[j]+") REFERENCES "+constantes.FORANEOS_CALIF_PENDIENTE[j]+"("+constantes.CAMPOS_CALIF_PENDIENTE[j]+")"           
        query+=");"
        cls.cursor.execute(query)

    #Connect to the Data Base
    @classmethod	         
    def connect(cls,nomb_base):
        nomb_base=nomb_base.lower()    
        cls.conect=mysql.connector.connect(host="localhost",user="root",password="")   
        cls.cursor= cls.conect.cursor() 
        if(nomb_base=="" or nomb_base==" "):
           General.show_error("error at data base name","database name error")
           return False
        query="SHOW DATABASES;"
        cls.cursor.execute(query)
        res=cls.cursor.fetchall()
        existe=False
        for x in res:
          if(x[0]==nomb_base):
             existe=True
        if (existe==False):
            msg=f"crear base de datos de nombre {nomb_base}?"
            if(General.show_confirmDialog(msg, "crear base de datos")==True):
               cls.create_base(nomb_base)
            else:
               return False            
        cls.db_actual=nomb_base
        cls.conect=mysql.connector.connect(host="localhost",user="root",password="",database=nomb_base)   
        cls.cursor= cls.conect.cursor() 
        cls.set_defaults_values()   
        if(cls.connect==None):
            return False
        else:
            return True
        