import mysql.connector.plugins.mysql_native_password
import mysql.connector
import subprocess
from subprocess import Popen
import os
import math
import random
import json

#Manage the Server Requests
class conector_server:
    conect=None
    tabla_selected=""
    db_actual=""
    root_pass=""
    cursor=None
    cursor_prepared=None
    mysql_folder=""
    tables_list=[]
    tables_alias={}
    Tables_PrimaryKeys={}
    fields_tables={} 
    permited_conectors=["and","or"]
    permited_verifications=["=","!="]
    url_server="http://localhost/Instituto/"
 
    #Reset a Table
    @classmethod	
    def reset_table(cls):
        query=f"TRUNCATE TABLE {cls.tabla_selected};"
        cls.cursor.execute(query)    
    
    #Init the Connection
    @classmethod	
    def init(cls):
        
        schema_dat=cls.get_db_structure("dataBd_schema.json")
        data_config=cls.get_config()
        if(schema_dat[0]==False):
            return schema_dat[1]
        if(data_config[0]==False):
           return data_config[1]
        conexion_res=cls.connect(data_config[1],schema_dat[1])
        if(conexion_res!=True):
           return conexion_res
        cls.set_tabla_byName("usuario")
        status_db=cls.check_dataBase()
        if(status_db!=True):
           return status_db
           
        return True


    #Read Config of Data Base 
    @classmethod
    def get_config(cls):
       import urllib.request
       import hmac
       import time
       import hashlib
       import uuid
       
       end_point=f"{cls.url_server}get_config.php"
       token="MiclaveSuperSecreta12345"
       timestamp=str(int(time.time()))
       nonce=str(uuid.uuid4())
       payload=f"{timestamp}|{nonce}".encode("utf-8")
       token=token.encode("utf-8")
       firm=hmac.new(token,payload,hashlib.sha256).hexdigest()
       
       try:
          headers={
            "User-Agent":"System-AutoLoader/1.0",
            "X-Timestamp":timestamp,
            "X-Nonce":nonce,
            "X-Signature":firm
          }
          req=urllib.request.Request(end_point,headers=headers)
          with urllib.request.urlopen(req,timeout=5) as response:
             text_json=response.read().decode("utf-8")
             data=json.loads(text_json)
             return (True,data)
       except urllib.error.HTTPError as e:
           try:
             body_err=e.read()
             body_err_text=body_err.decode("utf-8")
             json_err=json.loads(body_err_text)
             return (False,json_err)
           except:
              return (False,f"Acceso Denegado {e.code},{e.reason}")
       except Exception as e:
           return (False,f"Error de Conexion {e}")
       
    #get the Scheme Data of DB
    @classmethod
    def get_db_structure(cls,filename):
       
        import requests
        import json
        from io import BytesIO
        try:
           url=f"{cls.url_server}{filename}"
           response=requests.get(url)
           if(response.status_code>400):
              return (False,"Error Leyendo Estructura de Datos de la BD")
           raw_data=response.content 
           temp_file=BytesIO(raw_data)           
           data=json.load(temp_file)
           return (True,data)
        except:
          return (False,"Imposible Conectar con el Servidor")
      
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
    def set_tabla(cls,table_index):
        if(type(table_index).__name__!="int"):
           return
        if(table_index<0 or table_index>=len(cls.tables_list)):
            return
        cls.tabla_selected=cls.tables_list[table_index]
    
    #set the Table Target by Name
    @classmethod
    def set_tabla_byName(cls,table_name):
        if(table_name in cls.tables_list):
            cls.tabla_selected=table_name
        

    #get all Data of Table as List    
    @classmethod
    def get_allData(cls,campos,cond_data,join_data):
        fragments=[]
        values_list=[]
        fragments.append("SELECT ")
        num_campos=len(campos)
        require_prepare=False
        if(num_campos<=0):
            fragments.append("* FROM ")
        else:
           for i in range(0,num_campos):
               if(campos[i] not in cls.fields_tables[cls.tabla_selected]):
                  return []
               fragments.append(campos[i])
               if(i<num_campos-1):
                  fragments.append(" , ")
           fragments.append(" FROM ")
        fragments.append(cls.tabla_selected)
        
        if(cond_data!=None):
           require_prepare=True
           conditions=cond_data["conditions_Names"]
           condition_types=cond_data["condition_Types"]
           values_conditions=cond_data["conditions_Values"]
           verify_types=cond_data["conditions_Verify"]
       
           fragments.append(" WHERE ")
           for i in range(0,len(conditions)):
               if(i>=1):
                 cond=condition_types[i]
                 if(cond not in cls.permited_conectors):
                      return []
                 cond=cond.upper()
                 fragments.append(f" {cond} ")
               if(conditions[i] not in cls.fields_tables[cls.tabla_selected]):
                    return []
               values_list.append(values_conditions[i])
               fragments.append(f"{conditions[i]}=%s")                 
        fragments.append(";")
        query="".join(fragments) 
        try:
          if(require_prepare):
             values_tuple=tuple(values_list)
             cls.cursor_prepared.execute(query,values_tuple)
             data=cls.cursor_prepared.fetchall()
             return data
          else:
             cls.cursor.execute(query)
             data=cls.cursor.fetchall()
             return data
        except:
          return []        
        
    #add Data from a List or Dictionary to a Table    
    @classmethod
    def add_data(cls,values,do_commit):
      fragments=[] 
      fragments.append(f"INSERT INTO {cls.tabla_selected}")
      values_list=[]      
      if(type(values).__name__=="list"):
        if( len(values)<len(cls.fields_tables[cls.tabla_selected])):
           return -1
        fragments.append(" VALUES (")
        for i in range(0,len(values)):
           values_list.append(values[i])
           fragments.append("%s")
           if(i<len(values)-1):
              fragments.append(" , ")
        fragments.append(" );")              
       
      elif(type(values).__name__=="dict"):
        temp_fields=[]
        temp_insert_values=[]
        for key in values:
          if(key not in cls.fields_tables[cls.tabla_selected]):
             return -2
          temp_fields.append(key)
          temp_insert_values.append("%s")
          values_list.append(values[key])
        if(len(temp_fields)<len(cls.fields_tables[cls.tabla_selected])):
           return -1
        
        fields_str=",".join(temp_fields)
        insert_str=",".join(temp_insert_values)
        fragments.append(f"({fields_str}) VALUES({insert_str});")
      query="".join(fragments)
      try:
        tuple_values=tuple(values_list)
        cls.cursor_prepared.execute(query,tuple_values)
        if(do_commit==True):
            cls.conect.commit()
        return 0
      except:
         cls.conect.rollback()
         return -1

    #update a Field of table Target
    @classmethod
    def update_data(cls,values,cond_data,join_data,do_commit):
       if(cond_data==None):
          return -1
       fragments=[]
       fragments.append(f"UPDATE {cls.tabla_selected} SET ")
       first_value=True
       values_list=[]
       for key in values:
           if(first_value==True):
                first_value=False
           else:
              fragments.append(" , ")
           if(key not in cls.fields_tables[cls.tabla_selected]):
              return -2
           values_list.append(values[key])
           fragments.append(f"{key}=%s")
       fragments.append(" WHERE ")
       conditions=cond_data["conditions_Names"]
       condition_types=cond_data["condition_Types"]
       values_conditions=cond_data["conditions_Values"]
       verify_types=cond_data["conditions_Verify"]
       
       for i in range(0,len(conditions)):
           if(i>=1):
              if(condition_types[i] not in cls.permited_conectors):
                 return -2
              cond_upper=condition_types[i].upper()
              fragments.append(f" {cond_upper} ")
           if(conditions[i] not in cls.fields_tables[cls.tabla_selected]):
              return -2
           values_list.append(values_conditions[i])
           fragments.append(f"{conditions[i]}=%s")
       fragments.append(";")
       query="".join(fragments)  
       try:
          values_tuple=tuple(values_list)
          cls.cursor_prepared.execute(query,values_tuple) 
          if(do_commit==True):
              cls.conect.commit()
          return 0
       except:
          cls.conect.rollback()
          return -1 

    #delete a Register of the Table target
    @classmethod
    def delete_data(cls,cond_data,join_data,do_commit):   
        fragments=[]
        values_list=[]
        if(cond_data==None):
           return
        fragments.append(f"DELETE FROM {cls.tabla_selected} WHERE ")
        conditions=cond_data["conditions_Names"]
        condition_types=cond_data["condition_Types"]
        values_conditions=cond_data["conditions_Values"]
        verify_types=cond_data["conditions_Verify"]
        for i in range(0,len(conditions)):
            if(i>=1):
               if(condition_types[i] not in cls.permited_conectors):
                   return -2
               cond_upper=condition_types[i].upper()
               fragments.append(f" {cond_upper} ")
            if(conditions[i] not in cls.fields_tables[cls.tabla_selected]):
                return -2
            values_list.append(values_conditions[i])
            fragments.append(f"{conditions[i]}=%s")
        fragments.append(";")  
        query="".join(fragments)       
        try:
           values_tuple=tuple(values_list)
           cls.cursor_prepared.execute(query,values_tuple)
           if(do_commit==True):           
               cls.conect.commit()
           return 0
        except:
           cls.conect.rollback()
           return -1
     
    #Return True if the Table is Empty     
    @classmethod
    def is_empty(cls):
       res=False       
       query=f"SELECT * FROM {cls.tabla_selected};"
       cls.cursor.execute(query)
       last=len(cls.cursor.fetchall())            
       if(str(last)=="0"):
          res=True
       return res
       
    #generate a Ket Field Id Based in number of Registers    
    @classmethod
    def generate_id(cls,hard_verific=False,id_name=""):
        
          query=f"SELECT * FROM {cls.tabla_selected};"
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
       if(id_name not in cls.fields_tables[cls.tabla_selected]):
          return False
       query=f"SELECT * FROM {cls.tabla_selected} WHERE {id_name}=%s;"
       try:
         value_tuple=(id_value,)
         cls.cursor_prepared.execute(query,value_tuple)
         data=cls.cursor_prepared.fetchall()
         if(data==[]):
             return False
         else:
             return True
       except:
         return False
     
    #Restore Data Base from CSV File
    @classmethod
    def restore_bd(cls):   
          data=[len(cls.tables_list),[]]
          for tabl in reversed(cls.tables_list):
              data[1].append(tabl)
          return data
          
    #Build CSV Files withe Information of Data Base
    @classmethod
    def respaldar_bd(cls):
          data=[len(cls.tables_list),[],[]]
          for i in range(0,len(cls.tables_list)):
             tabl=cls.tables_list[i]
             fields=cls.fields_tables[tabl]
             data[1].append(tabl)
             data[2].append(fields)
          return data
          
     #Set Default Values of Tables    
    @classmethod
    def set_defaults_values(cls,seed_data): 
        import time
        local_time=time.localtime()
        fecha=time.strftime("%d/%m/20%y",local_time)
        for tabl in seed_data:
           data_list=seed_data[tabl]
           for data_tabl in data_list:
              primary_key_target=cls.Tables_PrimaryKeys[tabl]
              primary_val=data_tabl[primary_key_target]
              cls.set_tabla_byName(tabl)
              is_ok=True
              if(cls.id_exist(primary_key_target,primary_val)==True):
                 continue
              for field in data_tabl:
                  value_field=data_tabl[field]
                  if(value_field=="Calculate_date"):
                      data_tabl[field]=fecha
                  elif(type(value_field).__name__=="list"):
                      tabl_temp=value_field[0]
                      primary_target_temp=cls.Tables_PrimaryKeys[tabl_temp]
                      cls.set_tabla_byName(tabl_temp)
                      temp_data=value_field[1]
                      temp_data[ primary_target_temp]=cls.generate_id(True,primary_target_temp)
                      for temp_field in temp_data:
                         val_temp=temp_data[temp_field]
                         if(val_temp=="Calculate_date"):
                             temp_data[temp_field]=fecha
                      if(cls.add_data(temp_data)==-1):
                           is_ok=False
                      else:
                          data_tabl[field]=temp_data[primary_target_temp]
                  elif(field=="password" and tabl=="usuario"):
                        data_tabl[field]=General.encriptar(value_field)
              if(is_ok==False):
                   continue              
              cls.set_tabla_byName(tabl)
              cls.add_data(data_tabl)
        

    #Check the Data Integrity of Tables , Return False if the Table Is Corrupt
    @classmethod
    def check_dataBase(cls):
       res=True
       corrupted_tables=[]
       for i in range(0,len(cls.tables_list)):
          tabl=cls.tables_list[i]
          query=f"CHECK TABLE {cls.db_actual}.{tabl};"
          try:
             cls.cursor.execute(query)
             result=cls.cursor.fetchall()
             res_tabl=False
             for row in result:
                msg_type=row[2]
                msg_text=row[3]
                if(msg_type=="status" and msg_text=="OK"):
                    res_tabl=True
             if(res_tabl==False):
                 res=False
                 corrupted_tables.append(tabl)
          except Exception as e:
             res=False
             corrupted_tables.append(tabl)
       if(res==False):
           corrupted_tables_str=",".join(corrupted_tables)
           res=f"Las tablas {corrupted_tables_str} Estan Corruptas , imposible Iniciar Sistema"
       return res
            
    #Add Index to the required fields whe the Data Base is created for optimize the Consult    
    @classmethod
    def add_indexBd(cls,nomb_base,required_indexs):

       for key in required_indexs:
            tabl=f"{nomb_base}.{key}"
            dat_index=required_indexs[key]
            field=dat_index[1]
            id_index=dat_index[0]
            try:
               query=f" ALTER TABLE {tabl} ADD INDEX {id_index}({field});"
               cls.cursor.execute(query)
            except:
               print(f"error requesting{query}")
            
    #Build the Data Base
    @classmethod
    def create_base(cls,nomb_base,raw_fieldTables):
        query=f"CREATE DATABASE {nomb_base};"
        cls.cursor.execute(query)
        
        for i in range(0,len(cls.tables_list)):
           name_tabl=cls.tables_list[i]
           query=f"CREATE TABLE {nomb_base}.{name_tabl}("
           fields_target=raw_fieldTables[name_tabl]
           foreign_values=[]
           for j in range(0,len(fields_target)):
               target=fields_target[j]
               fragments=[]
               name_field=target["name"]
               fld_type=target["field-type"]
               fragments.append(query)
               fragments.append(name_field)
               fragments.append(" VARCHAR(255) ")
               end_char=" , " if (j<len(fields_target)-1) else ""
               primary_key=""
               if(fld_type=="PRIMARY KEY"):
                  primary_key=fld_type
               elif("FOREIGN KEY" in fld_type):
                   foregein_dat=fld_type.split(":")
                   foregein_reffld=foregein_dat[1]
                   foregein_tabl=foregein_dat[0].split("-")[1]                  
                   foreign_values.append(f"FOREIGN KEY ({name_field}) REFERENCES {foregein_tabl}({foregein_reffld})")
               fragments.append(primary_key)
               fragments.append(end_char)
               query="".join(fragments)
           if(len(foreign_values)>0):
                fragments=[]
                fragments.append(query)
                for value in foreign_values:
                   fragments.append(f",{value}")
                query="".join(fragments)
           end_query=f"{query});" 
           cls.cursor.execute(end_query)           

    #Read and Get the List of Field Names of Each Table from a Dictionary Data
    @classmethod
    def read_fields_tables(cls,data):
        for i in range(0,len(cls.tables_list)):
           name_tabl=cls.tables_list[i]
           flds_target=data[name_tabl]
           list_field_tabl=[]
           for j in range(0,len(flds_target)):
               target=flds_target[j]
               name_field=target["name"]
               fld_type=target["field-type"]
               if(fld_type=="PRIMARY KEY"):
                  cls.Tables_PrimaryKeys[name_tabl]=name_field
               list_field_tabl.append(name_field)
           cls.fields_tables[name_tabl]=list_field_tabl
    
    #Connect to the Data Base
    @classmethod	         
    def connect(cls,data_config,data_schema):
       

        nomb_base=data_config["db_name"] 
        cls.tables_list=data_schema["tables_names"]
        cls.tables_alias=data_schema["Alias_Tables"]
        raw_fieldTables=data_schema["fields_tables"]
        cls.read_fields_tables(raw_fieldTables)
        seed_data=data_schema["seed_data"]
        required_indexs=data_schema["add_indexs"]   
        
        if(nomb_base=="" or nomb_base==" "):
           return "El Nombre de la Base de datos es Invalido"
        try:
           cls.conect=mysql.connector.connect(host=data_config["host"],user=data_config["user"],password=data_config["password"])   
           cls.cursor= cls.conect.cursor() 
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
                    cls.create_base(nomb_base,raw_fieldTables)
                    cls.add_indexBd(nomb_base,required_indexs)
                else:
                    return "Creacion de Base de Datos Cancelada, No se puede Iniciar el Sistema"                  
           cls.db_actual=nomb_base
           cls.conect=mysql.connector.connect(host=data_config["host"],user=data_config["user"],password=data_config["password"],database=nomb_base)   
           cls.cursor= cls.conect.cursor()
           cls.cursor_prepared=cls.conect.cursor(prepared=True)           
           cls.set_defaults_values(seed_data)  
           
           if(cls.connect==None):
                return "Error al Conectar con la Base de Datos"
           else:
                return True
        except:
            return "Error al Conectar con la Base de Datos"
            