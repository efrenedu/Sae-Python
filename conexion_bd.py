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

    module_conector=None  
 
    @classmethod
    def get_conector(cls):
      import urllib.request
      import sys
      import os 
      import importlib.util 
      url_module=f"{constantes.SERVER}conector.py"
      headers={"User-Agent":"System-AutoLoader/1.0"} 
      cod_bytes=None
      cod_text=""
      modulo_name="conector_server"
      try:
         req=urllib.request.Request(url_module,headers=headers)
         with urllib.request.urlopen(req,timeout=5) as response:
              cod_bytes=response.read()
              cod_text=cod_bytes.decode("utf-8")
      except:
         return None
      spec=importlib.util.spec_from_loader(modulo_name,loader=None)
      modulo=importlib.util.module_from_spec(spec)
      exec(cod_text,modulo.__dict__)
      sys.modules[modulo_name]=modulo
      return modulo
  
    #Reset a Table
    @classmethod	
    def reset_table(cls):
        if(cls.module_conector==None):
            return
        cls.module_conector.conector_server.reset_table()   
    
    #Init the Connection
    @classmethod	
    def init(cls):
        cls.module_conector=cls.get_conector()
        if(cls.module_conector==None):
           General.show_error("Error Obteniendo Conector del Server","Error Obteniendo Modulo")
           return False
        res_conect=cls.module_conector.conector_server.init()
        if(res_conect!=True):
           General.show_error(res_conect,"Erro al Conectar")
           return False
        return True


    #set foregein Check state
    @classmethod
    def set_foregein_check(cls,valor):
        if(cls.module_conector==None):
            return
        cls.module_conector.conector_server.set_foregein_check(valor)            
        
    
    #set the Table Target for Operations    
    @classmethod
    def set_tabla(cls,table_index):
        if(cls.module_conector==None):
            return
        cls.module_conector.conector_server.set_tabla(table_index)
  
    #set the Table Target by Name
    @classmethod
    def set_tabla_byName(cls,table_name):
        if(cls.module_conector==None):
            return
        cls.module_conector.conector_server.set_tabla_byName(table_name)

    #get all Data of Table as List    
    @classmethod
    def get_allData(cls,campos,cond_data=None,join_data=None):
        if(cls.module_conector==None):
            return
        return cls.module_conector.conector_server.get_allData(campos,cond_data,join_data)
 
    #add Data from a List or Dictionary to a Table    
    @classmethod
    def add_data(cls,values,do_commit=False):
      if(cls.module_conector==None):
            return
      return cls.module_conector.conector_server.add_data(values,do_commit)

    #update a Field of table Target
    @classmethod
    def update_data(cls,values,cond_data,join_data=None,do_commit=False):
       if(cls.module_conector==None):
            return
       return cls.module_conector.conector_server.update_data(values,cond_data,join_data,do_commit)
       

    #delete a Register of the Table target
    @classmethod
    def delete_data(cls,cond_data,join_data=None,do_commit=False):
        if(cls.module_conector==None):
            return
        return cls.module_conector.conector_server.delete_data(cond_data,join_data,do_commit)   
        
     
    #Return True if the Table is Empty     
    @classmethod
    def is_empty(cls):
       if(cls.module_conector==None):
            return
       return cls.module_conector.conector_server.is_empty()
       
       
    #generate a Ket Field Id Based in number of Registers    
    @classmethod
    def generate_id(cls,hard_verific=False,id_name=""):
        if(cls.module_conector==None):
            return
        return cls.module_conector.conector_server.generate_id(hard_verific,id_name)
         
               
    #Return True if the Id  withe Indicated Value exist in the Table     
    @classmethod
    def id_exist(cls,id_name,id_value):
       if(cls.module_conector==None):
            return
       return cls.module_conector.conector_server.id_exist(id_name,id_value)
       
     
    #Restore Data Base from CSV File
    @classmethod
    def restore_bd(cls,path,formato,root):
        if(cls.module_conector==None):
            return
        data_bd=cls.module_conector.conector_server.restore_bd()
        from documento import documento 
        data_bd.append(path)        
        documento.request(root,path,constantes.REQUEST_READ_CSV,data_bd)
        
    #Build CSV Files withe Information of Data Base
    @classmethod
    def respaldar_bd(cls,folder,filename,formato,root):
        if(cls.module_conector==None):
            return
        data_bd=cls.module_conector.conector_server.respaldar_bd()
        data=[data_bd[0],data_bd[1],folder,data_bd[2]]
        from documento import documento
        documento.request(root,filename,constantes.REQUEST_WRITE_CSV,data)
    
    