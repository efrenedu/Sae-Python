import subprocess
from subprocess import Popen
import os
from constantes import constantes
from General import General
import math
import random
import json
import time
import requests

#Manage the Data Base Information
class conexion_bd:

    tabla_selected=""
    tables_list=["direccion","cargo","estatus_trabaj","estatus_estud","años_incorporados",
    "intentos_usuario","nombre","expediente","horario","trabajador","usuario",
    "representante","seccion","profesor","estudiante","area_formacion",
    "area_dictada_docentes","reporte","formato","cronograma","momento","fecha",
    "pregunta_secreta","descarga_documentos","calificacion_final","calif_momento",
    "calificacion","disponibilidad_horario","materia_pendiente","calific_pendiente"]


    #Init the Connection
    @classmethod	
    def init(cls):
        
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        data_send={"request_type":"Verify_db","timestamp":timestamp,"data_request":"","token":""}
        try:
           response=requests.post(url_target,data=data_send)
           resp_json=json.loads(response.content)
           if(resp_json["status"]=="Error"):
               General.show_error(resp_json["message"],"Error al Conectar")
               return False
           cls.set_tabla_byName("usuario")
           return True
        except:
           General.show_error("Imposible Conectar con el Servidor","Erro de Conexion")
           return False 
      

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
    def get_allData(cls,campos,cond_data=None,join_data=None,as_dict=False):
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        data_request={"fields":campos,"cond_dat":cond_data,"join_dat":join_data,"target_table":cls.tabla_selected,"as_dict":as_dict}
        data_send={"request_type":"Get Data","timestamp":timestamp,"data_request":json.dumps(data_request),"token":""}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos ")
            return []
        return resp_json["message"]
        
        
    #add Data from a List or Dictionary to a Table    
    @classmethod
    def add_data(cls,values,do_commit=False):
        from event_manager import Event_manager
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        from_dict=False
        if(type(values).__name__=="dict"):
           from_dict=True
        data_request={"values_add":values,"target_table":cls.tabla_selected,"from_dict":from_dict,"commit":do_commit}
        data_send={"request_type":"Add Data","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return -1
        return 0
        
    #update a Field of table Target
    @classmethod
    def update_data(cls,values,cond_data,join_data=None,do_commit=False):
        from event_manager import Event_manager
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        from_dict=False
        if(type(values).__name__=="dict"):
           from_dict=True
        data_request={"fields_update":values,"target_table":cls.tabla_selected,"cond_dat":cond_data,"join_dat":join_data,"commit":do_commit}
        data_send={"request_type":"Update Data","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return -1
        return 0

    #delete a Register of the Table target
    @classmethod
    def delete_data(cls,cond_data,join_data=None,do_commit=False):
        from event_manager import Event_manager
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        data_request={"target_table":cls.tabla_selected,"cond_dat":cond_data,"join_dat":join_data,"commit":do_commit}
        data_send={"request_type":"Delete Data","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return -1
        return 0
     
    #Return True if the Table is Empty     
    @classmethod
    def is_empty(cls):
       url_target=constantes.SERVER_BD_URL
       timestamp=str(int(time.time()))
       data_request={"target_table":cls.tabla_selected}
       data_send={"request_type":"Is_Empty","timestamp":timestamp,"data_request":json.dumps(data_request),"token":""}
       response=requests.post(url_target,data=data_send)
       resp_json=json.loads(response.content)
       if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return -1
       if(resp_json["message"]=="True"):
           return True
       
       return False
       
       
    #generate a Ket Field Id Based in number of Registers    
    @classmethod
    def generate_id(cls,hard_verific=False,id_name=""):
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        data_request={"target_table":cls.tabla_selected,"field_required":id_name,"Id_Request":"Generate Id"}
        data_send={"request_type":"Id Manager","timestamp":timestamp,"data_request":json.dumps(data_request),"token":""}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return "-1"
        return resp_json["message"]
               
    #Return True if the Id  withe Indicated Value exist in the Table     
    @classmethod
    def id_exist(cls,id_name,id_value):
        from event_manager import Event_manager
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        data_request={"target_table":cls.tabla_selected,"field_required":id_name,"Id_Request":"Exists Id","field_Value":id_value}
        data_send={"request_type":"Id Manager","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return False
        if(resp_json["message"]=="True"):
            return True
        else:
           return False
     
    #Request the Data of a Security Copy (ZiopFile) for Restore the Data Base
    @classmethod
    def request_restoreBd(cls,filename,root):
       from documento import documento
       from event_manager import Event_manager
       Event_manager.set_comp_values("cargando","Leyendo Copia de Seguridad : 0%")
       documento.request(root,filename,constantes.REQUEST_READ_CSV,[])
       
       
    #Recive Response From Data Base to Request of Restore Securriy Copy
    @classmethod
    def verify_response_restoreBd(cls,url_target,data_send,usr):
        from event_manager import Event_manager
        with requests.post(url_target,data=data_send,stream=True) as response:
           for line in response.iter_lines():
              if(line):
                data=json.loads(line.decode("utf-8"))
                if(data.get("status")=="Procesing"):
                   Event_manager.set_comp_values("cargando",f"Procesando Restauracion de BD {data['message']}%")
                elif(data.get("status")=="Error"):
                    General.show_error(data["message"],"Error en Restauracion de Bd")
                elif(data.get("status")=="Success"):
                   General.show_message("restauracion del respaldo realizada exitosamente","Restauracion Exitosa")
      
        from tiempo import tiempo
        time_object=tiempo()    
        Event_manager.user.add_action_historial(["restaurar BD",time_object.get_tiempo()])            
        cls.set_tabla(constantes.TABLA_REPORTE)
        id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"base de datos","restaurar","",time_object.get_fecha()]
        cls.add_data(data_hist)
        Event_manager.set_comp_values("cargando","")
        return 0
        
    #Restore Data Base from a Security Copy (ZipFile)
    @classmethod
    def restore_bd(cls,data):
        if(len(data)<=0):
            General.show_error("Data Invalida Recibida","Error de Datos")
            return -1
        from event_manager import Event_manager
        Event_manager.set_comp_values("cargando","Procesando Restauracion de BD...")
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        data_request={"Action":"Restore","data_tables":data}
        data_send={"request_type":"Security Copies","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user,"file_send":""}
        import threading  
        cls.thread_object=threading.Thread(target=cls.verify_response_restoreBd,args=(url_target,data_send,usr))
        cls.thread_object.start()         
        return 0
        
    #Build The Security Copy with the Information of Data Base
    @classmethod
    def respaldar_bd(cls,filename,root):
        url_target=constantes.SERVER_BD_URL
        timestamp=str(int(time.time()))
        from event_manager import Event_manager
        Event_manager.set_comp_values("cargando","Recibiendo Datos del Servidor...")
        usr=Event_manager.user
        token_user=usr.get_credentials()[4]
        data_request={"Action":"Repald"}
        data_send={"request_type":"Security Copies","timestamp":timestamp,"data_request":json.dumps(data_request),"token":token_user,"file_send":""}
        response=requests.post(url_target,data=data_send)
        resp_json=json.loads(response.content)
        if(resp_json["status"]=="Error"):
            Event_manager.set_comp_values("cargando","")
            General.show_error(resp_json["message"],"Error Obteniendo Datos")
            return -1
        from documento import documento
        documento.request(root,filename,constantes.REQUEST_WRITE_CSV,resp_json["data"])           
        return 0
    