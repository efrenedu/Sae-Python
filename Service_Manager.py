from tiempo import tiempo
from conexion_bd import conexion_bd
from constantes import constantes
from General import General
import time
import json
import requests
import os

#Manage the Service of System
class Service_Manager:

    AUDITORIA_FILTER_NOTHING=0
    AUDITORIA_KEY_FIELD=1
    AUDITORIA_FILTER_FROM_DATE_TO_DATE=2
    AUDITORIA_FILTER_BEFORE_DATE=3
    AUDITORIA_FILTER_AFTER_DATE=4
    STADISTICS_NONE=-1
    STADISTICS_WORKERS_CARGO=0
    STADISTICS_WORKER_STATUS=1
    STADISTICS_STUDENTS_ID=2
    STADISTICS_STUDENT_STATUS=3
    STADISTIC_STUDENTS_GENDER=4
    STADISTICS_SECTIONS_COUNT=5
    STADISTICS_SECTIONS_TURNO=6
    STADISTICS_MATRICULA_ACADEMIC_YEAR=7
    STADISTICS_MATRICULA_TURNO=8
    RECOVER_PASS_REQUEST=0
    RECOVER_PASS_VERIFY_SECRET_QUESTIONS=1
    RECOVER_PASS_CHANGE_PASSWORD=2
    
    #Determine Action on Auditoria Panel
    @classmethod
    def interprete_auditoria_action(cls,usr,vent):
       from Consult_Manager import Consult_Manager
       pnl=vent.panelActual
       accion=pnl.get_comp_byName("Accion_consulta")
       accion_str=""
       if(accion!=None):
          accion_str=accion.get_selected_value()
       else:
          accion_str="Buscar"
       if(accion_str=="Buscar"):
          Consult_Manager.consultar(vent,Consult_Manager.CONSULT_USERS_HISTORIAL)
          return
       if(accion_str=="Generar Reporte de Usuarios"):
          Consult_Manager.generar_reporte(pnl,"reporte de usuarios",usr)
       elif(accion_str=="Limpiar Historial de Usuarios"):
          pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
          valid_admin=False
          if(pass_admin=="" or pass_admin==" " or pass_admin==None):
             return          
          pass_user=General.desencriptar(usr.get_credentials()[4])      
          if(pass_user==pass_admin):
            valid_admin=True                                          
          if(valid_admin==False):
             General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
             return
          if(General.show_confirmDialog("esta seguro que desea limpiar los reportes del sistema?","limpiar reportes")!=True):
             return       
          conexion_bd.set_tabla(constantes.TABLA_REPORTE)
          conexion_bd.reset_table()
          pnl.get_comp_byName("table1_cp").reset()
          General.show_message("reportes del sistema limpiados satisfactoriamente","reportes limpiados")
          
       
    #Manage the Operation in User Gestion Panel except Register New User
    @classmethod
    def gestion_usuario(cls,usr,vent):
       pnl=vent.panelActual
       accion=pnl.get_comp_byName("Accion_consulta")
       accion_str=""
       if(accion!=None):
          accion_str=accion.get_selected_value()
       else:
          accion_str="Nuevo Usuario"
       if(accion_str=="Nuevo Usuario"):
         vent.update_pantallas(constantes.PANTALLA_REGISTRO_USUARIO,usr)
         return
       tabl=pnl.get_comp_byTag("table")
       temp_clave=tabl.get_row_selectedData()
       fields_user=[constantes.CLAVE_USUARIO,"password",constantes.CLAVE_TRABAJADOR,"nivel_acceso",constantes.CLAVE_INTENTOS_USUARIO,"bloqueado"]
       clave=""
       if(temp_clave==" "):
          General.show_message("por favor seleccione un usuario valido","usuario invalido")
          return
       else:
          clave=temp_clave[0]
       time_object=tiempo()
       pass_entry=General.show_password_message("por favor escriba su password","password de administrado")    
       if(pass_entry=="" or pass_entry==None or pass_entry==" "):
           return  
       import time
       timestamp=str(int(time.time()))
       data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "password_send":pass_entry,
          "user_verify":"Admin_User"
       }
       url_send=f"{constantes.SERVER}compare_passwords.php"
       response=requests.post(url_send,data=data_user)
       json_content=json.loads(response.content)
       if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return
       if(json_content["message"]!="Same Password"):
           General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
           return
         
       
       if(accion_str=="Desbloquear Usuario"):
        
          conexion_bd.set_tabla(constantes.TABLA_USUARIO)
          cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}    
          old_d=conexion_bd.get_allData(["bloqueado"],cond_data)
          if(old_d!=[]):
            if(old_d[0][0]=="False"):
                 General.show_error("el usuario no esta bloqueado","usuario no bloquead")
                 return
          if(General.show_confirmDialog("estas seguro que desea desbloquear el usuario?","desbloquear usuario")!=True):
               return
          values={"bloqueado":"False"}
          values2={"num_intentos":"0","last_fecha":"","last_hora":""}
          cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}    
                
          if(conexion_bd.update_data(values,cond_data)!=-1):
             data_user=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],cond_data)
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[data_user[0][0]],"conditions_Verify":["="]}    
             conexion_bd.update_data(values2,cond_data)
             conexion_bd.set_tabla(constantes.TABLA_USUARIO)
             tabl.reset()
             new_data=conexion_bd.get_allData(fields_user)
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             for i in range(0,len(new_data)):
                   if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                      temp_data=[]
                      for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[new_data[i][4]],"conditions_Verify":["="]}    
                           data_intentos=conexion_bd.get_allData(["num_intentos"],cond_data)
                           temp_data.append(data_intentos[0][0])
                      passw=temp_data[1]
                      new_pass=""
                      for k in range(0,len(passw)):
                          new_pass=new_pass+'*'
                      temp_data[1]=new_pass
                      tabl.add_row(temp_data)
             
             usr.add_action_historial(["desbloquear usuario",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","desbloquear usuario","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True)
             General.show_message("usuario desbloqueado exitosamente","usuario desbloqueado")      
       elif(accion_str=="Reset Password"):
          #reset password
          
          if(General.show_confirmDialog("estas seguro que desea reestablecer el password del usuario?","registrar")!=True):
               return
          conexion_bd.set_tabla(constantes.TABLA_USUARIO)
          values={"password":General.encriptar(constantes.PASS_USER_DEFAULT)}
          cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}    
                
          if(conexion_bd.update_data(values,cond_data)!=-1):
             tabl.reset()
             new_data=conexion_bd.get_allData(fields_user)
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             for i in range(0,len(new_data)):
               if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                  temp_data=[]
                  for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[new_data[i][4]],"conditions_Verify":["="]}    
                           data_intentos=conexion_bd.get_allData(["num_intentos"],cond_data)
                           temp_data.append(data_intentos[0][0])       
                  passw=temp_data[1]
                  new_pass=""
                  for k in range(0,len(passw)):
                      new_pass=new_pass+'*'
                  temp_data[1]=new_pass
                  tabl.add_row(temp_data)
             
             usr.add_action_historial(["reestablecer password de usuario",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","reset pass","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True)
             General.show_message("password reestablecido a "+constantes.PASS_USER_DEFAULT,"password reestablecido")
       elif(accion_str=="Eliminar Usuario"):
            #borrar usuario
            
            if(General.show_confirmDialog("estas seguro que desea borrar el usuario?","registrar")!=True):
               return
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}       
            data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],cond_data)
            conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
            if(conexion_bd.delete_data(cond_data)!=-1):   
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               conexion_bd.delete_data(cond_data)
               conexion_bd.set_tabla(constantes.TABLA_USUARIO)
               if(conexion_bd.delete_data(cond_data)!=-1):  
                 conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                 cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[data_intentos[0][0]],"conditions_Verify":["="]}    
                 conexion_bd.delete_data(cond_data)
                 tabl.reset()
                 conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                 new_data=conexion_bd.get_allData(fields_user)
                 conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                 for i in range(0,len(new_data)):
                   if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                      temp_data=[]
                      for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[new_data[i][4]],"conditions_Verify":["="]}    
                           data_intentos=conexion_bd.get_allData(["num_intentos"],cond_data)
                           temp_data.append(data_intentos[0][0])   
                      passw=temp_data[1]
                      new_pass=""
                      for k in range(0,len(passw)):
                          new_pass=new_pass+'*'
                      temp_data[1]=new_pass
                      tabl.add_row(temp_data)
                
                 usr.add_action_historial(["borrar usuario",time_object.get_tiempo()])
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","borrar usuario","",time_object.get_fecha()]
                 conexion_bd.add_data(data_hist,True)
                 General.show_message("usuario eliminado exitosamente","usuario borrado")
       elif(accion_str=="Cambiar Permiso"):
           
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           new_permit=General.show_input_message("por favor introdusca el nuevo nivel de acceso","nivel de acceso")
           if(new_permit==None):
              return
           if(General.is_valid(new_permit,constantes.CADENA_SOLOTEXTO,False,0)==False):
                General.show_error("por favor escriba un tipo de acceso valido","valor de acceso invalido")
           else:
              valid_acces=False
              if(new_permit=="coordinador"):
                 valid_acces=True
              elif(new_permit=="secretaria"):
                 valid_acces=True   
              elif(new_permit=="directivo"):
                   valid_acces=True
              if(valid_acces==False):
                  General.show_error(" nuevo nivel de acceso no valido","valor invalido")
              else:
                  if(General.show_confirmDialog("estas seguro que desea cambiar el permiso del usuario?","registrar")!=True):
                      return 
                  values={"nivel_acceso":new_permit}
                  cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}    
                
                  if(conexion_bd.update_data(values,cond_data)!=-1):
                    tabl.reset()
                    new_data=conexion_bd.get_allData(fields_user)
                    conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                    for i in range(0,len(new_data)):
                       if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                            temp_data=[]
                            for j in range(0,len(new_data[i])):
                               if(j!=4):
                                  temp_data.append(new_data[i][j])
                               else:
                                   cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[new_data[i][4]],"conditions_Verify":["="]}    
                                   data_intentos=conexion_bd.get_allData(["num_intentos"],cond_data)
                                   temp_data.append(data_intentos[0][0])                           
                            passw=temp_data[1]
                            new_pass=""
                            for k in range(0,len(passw)):
                                new_pass=new_pass+'*'
                            temp_data[1]=new_pass
                            tabl.add_row(temp_data)
                    usr.add_action_historial(["cambiar permiso",time_object.get_tiempo()])
                    conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                    id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                    data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","cambio permiso","",time_object.get_fecha()]
                    conexion_bd.add_data(data_hist,True)
                    General.show_message("permiso cambiado exitosamente","permiso cambiado")
     
    #The User Request Modify the Information of Self Account
    @classmethod
    def update_user(cls,usr,vent):
    
        pnl=vent.panelActual
        user_r=usr.user
        permiso_user=usr.get_credentials()[2]
        modific_pass=False
        valor_pass1=pnl.get_comp_byName("pass1").get_text()
        valor_pass2=pnl.get_comp_byName("pass2").get_text()
        icono=pnl.get_comp_byName("icono_src").get_text()
        modific_icon=False
        time_object=tiempo()
        nuevo_dire=""
        if(icono!=""):
           if(icono.startswith("fotos/")==False):
              if(icono.endswith(".png")==False and icono.endswith(".jpg")==False and icono.endswith(".jpeg")==False):
                 General.show_message("el icono debe ser una imagen PNG o JPEG","icono invalido")
                 return
              modific_icon=True
        if(valor_pass1!=""):
          if(General.is_valid(valor_pass1,constantes.CADENA_PASSWORD,False)==False):
             General.show_message("el password debe contener una letra mayuscula, 1 minusucula, numeros, un caracter especial y una longitud de 8 ","password invalido")
             return
          elif(valor_pass1!=valor_pass2):
            General.show_message("por favor repita el password correctamente","passwords no coinciden")
            return
          modific_pass=True
        pregs=pnl.get_comps_byTag("combo")
        preguntas=[]
        respuestas=[]
        num_preg=0
        correctas=[False,False,False,False]
        for i in range(0,len(pregs)):
           if(pregs[i].get_id()!="director"):
               valor=pregs[i].get_selected_value()
               id_preg=pregs[i].get_id()
               index=id_preg[len(id_preg)-1]
               if(valor!="elejir" and valor!="elegir"):
                    num_preg+=1
                    for j in range(0,len(preguntas)):
                        if(valor==preguntas[j][0]):
                             General.show_message("las preguntas no se puede repetir","preguntas repetidas")
                             return
                    preguntas.append([valor,str(index)])
                    res=pnl.get_comp_byName("respuesta"+str(index)).get_text()
                    if(id_preg.endswith("1")):
                        correctas[0]=True
                    elif(id_preg.endswith("2")):
                        correctas[1]=True     
                    elif(id_preg.endswith("3")):
                        correctas[2]=True 
                    elif(id_preg.endswith("4")):
                        correctas[3]=True   
                    if(res=="" or res==" " or len(res)<2):
                        General.show_message("por favor escriba una respuesta valida","respuesta invalida")
                        return
                    respuestas.append(res)
           else:
               valor=pregs[i].get_selected_value()
               if(valor!="sin asignar" and permiso_user=="admin"):
                    nuevo_dire=valor        
        if(num_preg<=2):
               General.show_message("por favor elija al menos tres preguntas secretas","insuficientes preguntas secretas")
               return 
        if(num_preg>2):
            for pr in range(0,num_preg):
              if(correctas[pr]==False):
                 General.show_message("por favor asigne las preguntas ordenadamente","preguntas invalidas")
                 return  
        conexion_bd.set_tabla(constantes.TABLA_USUARIO)
        new_icon=""
        split_icon=icono.split("/")
        file_name=split_icon[len(split_icon)-1]
        if("fotos/"+file_name==constantes.DEFAULT_USER_ICON):
             General.show_message("ya existe una imagen con ese nombre en el servidor,cambie el nombre e intentelo de nuevo","imagen ya existe en server")
             return   
        if(conexion_bd.id_exist("foto","fotos/"+file_name)):
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}     
            old_icon=conexion_bd.get_allData(["foto"],cond_data)[0][0]
            if(old_icon!="fotos/"+file_name):
                General.show_message("ya existe una imagen con ese nombre en el servidor,cambie el nombre e intentelo de nuevo","imagen ya existe en server")
                return 
        pass_entry=General.show_password_message("por favor escriba su password","password de Usuario")    
        if(pass_entry=="" or pass_entry==None or pass_entry==" "):
           return  
        import time
        timestamp=str(int(time.time()))
        usr_credentials=usr.get_credentials()
        data_user={
          "token":usr_credentials[4],
          "timestamp":timestamp,
          "password_send":pass_entry,
          "user_verify":usr_credentials[0]
        }
        url_send=f"{constantes.SERVER}compare_passwords.php"
        response=requests.post(url_send,data=data_user)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return
        if(json_content["message"]!="Same Password"):
           General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
           return
    
        if(General.show_confirmDialog("modificar datos del usuario?","modificar datos usuario")!=True):
           return        
        if(modific_icon):       
            url=constantes.SERVER+"upload_foto.php"          
            temp_file=open(icono,"rb")
            dict_foto={"file":temp_file}
            respond=requests.post(url,files=dict_foto)
            temp_file.close()
            res=respond.text.strip()
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}        
            conexion_bd.update_data({"foto":res},cond_data)
            new_icon=res
        if(modific_pass):
            valor_pass1=General.get_hash(valor_pass1)
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}    
            conexion_bd.update_data({"password":valor_pass1},cond_data)
        conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
        for pr in range(0,num_preg):
            pregunta=preguntas[pr][0]
            num=preguntas[pr][1]
            respuest=respuestas[pr]
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO,"numero"],"condition_Types":["and","and"],"conditions_Values":[user_r,num],"conditions_Verify":["=","="]}    
            exist=conexion_bd.get_allData([constantes.CLAVE_PREGUNTA_SECRETA],cond_data)
            if(exist!=[]):
                cond_data={"conditions_Names":[constantes.CLAVE_PREGUNTA_SECRETA],"condition_Types":["and"],"conditions_Values":[exist[0][0]],"conditions_Verify":["="]}    
                conexion_bd.update_data({"pregunta":pregunta,"respuesta":respuest,"modificado":time_object.get_fecha()},cond_data)
            else:
              new_id_pr=user_r+"-preg-"+num
              data_pr=[new_id_pr,user_r,respuest,pregunta,num,time_object.get_fecha()]
              conexion_bd.add_data(data_pr)
        if(nuevo_dire!=""):
            #If is User Admin and change the Admin Worker
            ced_dire=nuevo_dire.split("-")
            if(len(ced_dire)==3):
               ced_dire=ced_dire[0]+"-"+ced_dire[1]
            elif(len(ced_dire)==2):
               ced_dire=ced_dire[0]
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}     
            old_user_dire=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data)
            old_dire=old_user_dire[0][0]
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)        
            if(ced_dire!=old_dire):
                  cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[ced_dire],"conditions_Verify":["="]}    
                  data_t_dire=conexion_bd.get_allData([constantes.CLAVE_CARGO],cond_data)
                  if(data_t_dire!=[]):
                       conexion_bd.set_tabla(constantes.TABLA_CARGO)
                       cond_data={"conditions_Names":[constantes.CLAVE_CARGO],"condition_Types":["and"],"conditions_Values":[data_t_dire[0][0]],"conditions_Verify":["="]}    
                       conexion_bd.update_data({"cargo":"Director","modificado":time_object.get_fecha()},cond_data)
                       conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                       cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[ced_dire],"conditions_Verify":["="]}    
                       old_user=conexion_bd.get_allData([constantes.CLAVE_USUARIO],cond_data)
                       if(old_user!=[]):
                           cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[old_user[0][0]],"conditions_Verify":["="]}    
                           data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],cond_data)
                           conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
                           if(conexion_bd.delete_data(cond_data)!=-1):   
                              conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                              conexion_bd.delete_data(cond_data)
                              conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                              conexion_bd.delete_data(cond_data)  
                              conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                              cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[data_intentos[0][0]],"conditions_Verify":["="]}    
                              conexion_bd.delete_data(cond_data)
                       conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                       cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}                   
                       conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:ced_dire,"modificado":time_object.get_fecha()},cond_data)
            if(old_dire!="000" and old_dire!="001" and old_dire!=ced_dire):
                  #Prevent Assign Default Admin Worker or the old Worker
                  conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                  cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[old_dire],"conditions_Verify":["="]}    
                  data_t_old=conexion_bd.get_allData([constantes.CLAVE_CARGO],cond_data)
                  if(data_t_old!=[]):
                       conexion_bd.set_tabla(constantes.TABLA_CARGO)
                       cond_data={"conditions_Names":[constantes.CLAVE_CARGO],"condition_Types":["and"],"conditions_Values":[data_t_old[0][0]],"conditions_Verify":["="]}    
                       conexion_bd.update_data({"cargo":"Docente","modificado":time_object.get_fecha()},cond_data)       
        usr.add_action_historial(["Modificar datos de usuario",time_object.get_tiempo()])     
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"Actualizacion de Usuario","Cambio de Configuracion del Usuario","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True)
        General.show_message("actualizacion de datos del usuario realizada satisfactoriamente","usuario actualizado")
        vent.update_pantallas(constantes.PANTALLA_WELCOME,usr)        
        if(new_icon!=""):
            pnl=vent.panelActual
            url_i=constantes.SERVER+new_icon
            icon_welcome=pnl.get_comp_byName("logo_inicio")
            icon_welcome.change_image(url_i)  
    
    #Manage the Activation of Components on Recover Pass Panel
    @classmethod
    def activate_comps_recover_password(cls,pnl,fase):
        if(fase==cls.RECOVER_PASS_REQUEST):
            pnl.get_comp_byName("caja6",False).set_active(False)
            pnl.get_comp_byName("caja7",False).set_active(False)
            
        elif(fase==cls.RECOVER_PASS_VERIFY_SECRET_QUESTIONS):
            pnl.get_comp_byName("caja6",False).set_active(True)
            pnl.get_comp_byName("caja7",False).set_active(True)
            pnl.get_comp_byName("caja3",False).set_active(False)
            pnl.get_comp_byName("caja5",False).set_active(False)
    #Manage the Password Recovery from a User
    @classmethod
    def recuperar_password(cls,usr,vent,fase):
        pnl=vent.panelActual
        if(fase==cls.RECOVER_PASS_REQUEST):
           user_r=pnl.get_comp_byName("usuario_login").get_text()
           if(user_r=="" or user_r==" "):
                General.show_message("por favor escriba el nombre de usuario","usuario no valido")
                return
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           if(conexion_bd.id_exist(constantes.CLAVE_USUARIO,user_r)):
              cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}    
              d_user=conexion_bd.get_allData(["bloqueado"],cond_data)
              if(d_user[0][0]=="True"):
                 General.show_message("el usuario esta bloqueado","usuario bloqueado")
                 return
              vent.update_pantallas(constantes.PANTALLA_RECUPERAR_PASSWORD)
              pnl=vent.panelActual
              pnl.get_comp_byName("user").set_text(user_r)
              question=""
              conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
              data_pregs=conexion_bd.get_allData([],cond_data)
              if(data_pregs!=[]):
                 size_p=len(data_pregs)-1
                 import random
                 index=random.randint(0,size_p) 
                 question=data_pregs[index][3]    
              pnl.get_comp_byName("pregunta").set_text(question)
              vent.raiz.after(200,lambda:cls.activate_comps_recover_password(pnl,fase))
             
           else:
              General.show_message("el usuario indicado es inexistente","usuario inexistente")        
        elif(fase==cls.RECOVER_PASS_VERIFY_SECRET_QUESTIONS):
           user_r=pnl.get_comp_byName("user").get_text()
           preg= pnl.get_comp_byName("pregunta").get_text()
           if(preg!="" and preg!=" "):
              res= pnl.get_comp_byName("respuesta").get_text()
              conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
              cond_data={"conditions_Names":[constantes.CLAVE_USUARIO,"pregunta","respuesta"],"condition_Types":["and","and","and"],"conditions_Values":[user_r,preg,res],"conditions_Verify":["=","=","="]}    
              data_res=conexion_bd.get_allData([],cond_data)
              if(res=="" or res==" "):
                 General.show_message("por favor escriba una respuesta","respuesta invalida")
                 return
              if(data_res!=[]):
                  vent.raiz.after(200,lambda:cls.activate_comps_recover_password(pnl,fase))
              else:
                General.show_message("la respuesta es incorrecta","respuesta incorrecta")
                cls.vent.update_pantallas(constantes.PANTALLA_INICIO)
           else:
             General.show_error("usuario sin preguntas secretas","imposible recuperar contraseña")
        elif(fase==cls.RECOVER_PASS_CHANGE_PASSWORD):
            user_r=pnl.get_comp_byName("user").get_text()
            valor_p1= pnl.get_comp_byName("pass1").get_text()   
            valor_p2= pnl.get_comp_byName("pass2").get_text()
            if(General.is_valid(valor_p1,constantes.CADENA_PASSWORD,False)==False):
                General.show_message("por favor escriba un nuevo password valido","nuevo password invalido")
                return
            elif(valor_p1!=valor_p2):
                General.show_message("por favor repita el password correctamente","passwords no coinciden")
                return
            if(General.show_confirmDialog("esta seguro que desea modificar contraseña?","modificar contraseña")!=True):
                 return
            time_object=tiempo()
            valor_p1=General.get_hash(valor_p1)
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[user_r],"conditions_Verify":["="]}    
            conexion_bd.update_data({"password":valor_p1,"modificado":time_object.get_fecha()},cond_data)
            data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],cond_data)
            conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_INTENTOS_USUARIO],"condition_Types":["and"],"conditions_Values":[data_intentos[0][0]],"conditions_Verify":["="]}    
            conexion_bd.update_data({"num_intentos":"0","last_fecha":"","last_hora":"","modificado":time_object.get_fecha()},cond_data,None,True)
            General.show_message("contraseña cambiada exitosamente","contraseña modificada")
            vent.update_pantallas(constantes.PANTALLA_INICIO)
                    
    #Register the User in User Gestion Panel
    @classmethod
    def registrar_usuario(cls,usr,vent):
       pnl=vent.panelActual
       user=pnl.get_comp_byName("usuario")
       fields=pnl.get_comps_byTag("field")
       pass_fields=pnl.get_comps_byTag("pass")
       combos=pnl.get_comps_byTag("combo")
       time_object=tiempo()
       data=["","","","",constantes.DEFAULT_USER_ICON,"","False",time_object.get_fecha()]
       valido=0
       temp_pass=""

       conexion_bd.set_tabla(constantes.TABLA_USUARIO)
       if(General.is_valid(user.get_text(),constantes.CADENA_USER,False,3)==False):
           valido=-1
       else:
           data[0]=user.get_text()
           if(conexion_bd.id_exist(constantes.CLAVE_USUARIO,data[0])):
               valido=-7
           
       for i in range(0,len(pass_fields)):
            if(valido==0):
                valor=pass_fields[i].get_text()
                if(pass_fields[i].get_id()=="pass"):
                    if(General.is_valid(valor,constantes.CADENA_PASSWORD,False)==False):
                        valido=-2
                    else:
                        temp_pass=valor
                            
                else:
                    if(temp_pass!=valor):
                        valido=-3
                    else:
                        data[1]=temp_pass
                        data[1]=General.encriptar(data[1])
       
       #verificaciones Overs Secrets Questions and Woker Id
       num_preguntas=0 
       correctas=[False,False,False,False]
       preguntas=[["elegir",""],["elegir",""],["elegir",""],["elegir",""]]
       for i in range(0,len(combos)):
          if(valido==0):
            if(combos[i].get_id()=="lista_ru"):
               #get the Worker id to Asssign the User
               if(combos[i].get_count()>1):
                  valor=combos[i].get_selected_value()
                  if(valor!="elejir" and valor!="elegir"):
                     temp_comp=valor.split("-")
                     if(len(temp_comp)==3):
                        temp_comp=temp_comp[0]+"-"+temp_comp[1]
                     elif(len(temp_comp)==2):
                        temp_comp=temp_comp[0]
                     else:
                         temp_comp=""
                     data[2]=temp_comp
                     conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                     if(conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,data[2])):
                        valido=-6
                  else:
                     valido=-5               
               else:
                     valido=-4
            if(combos[i].get_id()=="pregunta1"):
               valor=combos[i].get_selected_value()
               if(valor!="elejir" and valor!="elegir"):
                     preguntas[0][0]=valor  
                     num_preguntas+=1
                     correctas[0]=True               
            elif(combos[i].get_id()=="pregunta2"): 
               valor=combos[i].get_selected_value()
               if(valor!="elejir" and valor!="elegir"):
                     preguntas[1][0]=valor
                     num_preguntas+=1 
                     correctas[1]=True
                     if(valor==preguntas[0][0]):
                           valido=-12                     
            elif(combos[i].get_id()=="pregunta3"):
               valor=combos[i].get_selected_value()
               if(valor!="elejir" and valor!="elegir"):
                     preguntas[2][0]=valor
                     num_preguntas+=1 
                     correctas[2]=True
                     if(valor==preguntas[0][0] or valor==preguntas[1][0] ):
                           valido=-12  
            elif(combos[i].get_id()=="pregunta4"):
               valor=combos[i].get_selected_value()
               if(valor!="elejir" and valor!="elegir"):
                     preguntas[3][0]=valor
                     num_preguntas+=1 
                     correctas[3]=True
                     if(valor==preguntas[0][0] or valor==preguntas[1][0] or valor==preguntas[2][0] ):
                           valido=-12                
       if(num_preguntas<=2 and valido==0):
              valido=-8 
       if(num_preguntas>2 and valido==0):
           for pr in range(0,num_preguntas):
               if(correctas[pr]==False ):
                    valido=-13
       #verificaciones Over Responses to Secrets Qestions 
       for i in range(0,len(fields)):
          if(valido==0):
            if(fields[i].get_id()=="respuesta1"):
                if(preguntas[0][0]!="elejir" and preguntas[0][0]!="elegir"):
                    preguntas[0][1]=fields[i].get_text()
                    if(General.is_valid(preguntas[0][1],constantes.CADENA_ALFANUMERICA,True,1)==False):
                        valido=-9
            elif(fields[i].get_id()=="respuesta2"):
                if(preguntas[1][0]!="elejir" and preguntas[1][0]!="elegir"):
                    preguntas[1][1]=fields[i].get_text()
                    if(General.is_valid(preguntas[1][1],constantes.CADENA_ALFANUMERICA,True,1)==False):
                        valido=-10 
                             
            elif(fields[i].get_id()=="respuesta3"):
                if(preguntas[2][0]!="elejir" and preguntas[2][0]!="elegir"):
                    preguntas[2][1]=fields[i].get_text()
                    if(General.is_valid(preguntas[2][1],constantes.CADENA_ALFANUMERICA,True,1)==False):
                        valido=-11
                              
            elif(fields[i].get_id()=="respuesta4"):
                if(preguntas[3][0]!="elejir" and preguntas[3][0]!="elegir"):
                    preguntas[3][1]=fields[i].get_text()
                    if(General.is_valid(preguntas[3][1],constantes.CADENA_ALFANUMERICA,True,1)==False):
                        valido=-11               
       if(valido==0):
             conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
             cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[2]],"conditions_Verify":["="]}    
             data_worker=conexion_bd.get_allData([],cond_data)
             if(data_worker!=[]):
                conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                data_users=conexion_bd.get_allData([],cond_data)
                if(data_users!=[]):
                    valido=-6 
                else:
                    conexion_bd.set_tabla(constantes.TABLA_CARGO)
                    cond_data={"conditions_Names":[constantes.CLAVE_CARGO],"condition_Types":["and"],"conditions_Values":[data_worker[0][6]],"conditions_Verify":["="]}    
                    cargo=conexion_bd.get_allData([],cond_data)[0][1].lower()
                    if( cargo.startswith("subdirector") or cargo.startswith("sub director")):
                        cargo="directivo"
                    elif(cargo.startswith("coordinador")):
                        cargo="coordinador"
                    data[3]=cargo
                  
       if(valido==0):
           #Register the User
           pass_entry=General.show_password_message("por favor escriba su password","password de administrado")    
           if(pass_entry=="" or pass_entry==None or pass_entry==" "):
                 return  
           import time
           timestamp=str(int(time.time()))
           data_user={
                  "token":usr.get_credentials()[4],
                  "timestamp":timestamp,
                  "password_send":pass_entry,
                  "user_verify":"Admin_User"
           }
           url_send=f"{constantes.SERVER}compare_passwords.php"
           response=requests.post(url_send,data=data_user)
           json_content=json.loads(response.content)
           if(json_content["status"]=="Error"):
                 General.show_error(json_content["message"],"Error")
                 return
           if(json_content["message"]!="Same Password"):
                  General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
                  return
           if(General.show_confirmDialog("registrar usuario?","registrar")!=True):
                 return 
                  
           if(General.show_confirmDialog("registrar usuario?","registrar")!=True):
                return        
           conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
           data_intents=[conexion_bd.generate_id(True,constantes.CLAVE_INTENTOS_USUARIO),"0","","",time_object.get_fecha()]
           data[5]=data_intents[0]
           conexion_bd.add_data(data_intents)
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           res=conexion_bd.add_data(data)
           res2=0
           conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
           for i in range(0,num_preguntas):
               if(preguntas[i][0]!="" and res2!=-1):
                   temp_data=[data[0]+"-preg-"+str(i+1),data[0],preguntas[i][1],preguntas[i][0],str(i+1),time_object.get_fecha()]
                   temp_res=conexion_bd.add_data(temp_data)
                   if(temp_res==-1):
                        res2=-1
                        break
                        
           if(res==-1 or res2==-1):
               General.show_error("error al agregar data","error de base de datos")
               return
           else:
                #Register Historial
                usr.add_action_historial(["registro de usuario",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","usuario","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("usuario registrado satisfactoriamente","usuario registrado")
           vent.update_pantallas(constantes.PANTALLA_SERVICIO_GESTION_USUARIO,usr)
       else:
         #Error Messages
         if(valido==-1):
              General.show_message("por favor escriba un nombre de usuario valido","nombre de usuario no valido")
         elif(valido==-2):
              General.show_message("el password debe contener una letra mayuscula,una ltra minusucula,numeros, un caracter especial y ser de almenos 8 caracteres","password no valido")
         elif(valido==-3):
              General.show_message("por favor repita el password correctamente","password no coincide")
         elif(valido==-4):
              General.show_message("por favor registre el personal antes de crear usuarios","no hay personal registrado")
         elif(valido==-5):
              General.show_message("por favor seleccione un miembro del personal","miembro de personal no valido")
         elif(valido==-6):
              General.show_message("el mimebro de personal ya tiene una cuenta de usuario","miembro de personal ya tiene cuenta")
         elif(valido==-7):
              General.show_message("el nombre de usuario ya existe","usuario ya existente")
         elif(valido==-8):
              General.show_message("por favor seleccione almenos tres pregunta secretas","insuficientes preguntas secretas")
         elif(valido==-9):
              General.show_message("respuesta secreta 1 no valida","respuesta secreta invalida")
         elif(valido==-10):
              General.show_message("respuesta secreta 2 no valida","respuesta secreta invalida")
         elif(valido==-11):
              General.show_message("respuesta secreta 3 no valida","respuesta secreta invalida")
         elif(valido==-12):
              General.show_message("las preguntas secretas no deben repetirse","preguntas secretas repetidas")
         elif(valido==-13):
             General.show_message("por favor asigne las preguntas secretas ordenadamente","preguntas secretas invalidas")
    
    #Stadistics Service
    @classmethod
    def stadistics(cls,usr,vent):
       pnl=vent.panelActual
       opcion=pnl.get_comp_byName("tipo_estad").get_selected_value()
       filtro=pnl.get_comp_byName("tipo_estad2").get_selected_value()
       valores=[]
       colors_figure=[]
       items=[]
       title=""
       tipo_data=cls.STADISTICS_NONE
       label_msg=""
       if(filtro=="elejir" or filtro=="elegir"):
            General.show_message("por favor elija un filtro para la grafica","elija un filtro")
            return
       if(opcion=="personal"):
          label_msg="total de\n trabajadores"
          conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
          data=conexion_bd.get_allData([])
          if(data!=[]):
             if(filtro=="cargo de personal"):
               items=["docente","no docente"]
               tipo_data=cls.STADISTICS_WORKERS_CARGO
               title=filtro
             elif(filtro=="estatus del personal"):
               items=["activo","inactivo","de reposo","posible retiro"]
               tipo_data=cls.STADISTICS_WORKER_STATUS
               title=filtro
             docente=0
             no_docente=0
             activos=0
             de_reposo=0
             inactivos=0
             posible_retiro=0
             for i in range(0,len(data)):
               if(data[i][0]!="000" and data[i][0]!="001"):
                  conexion_bd.set_tabla(constantes.TABLA_CARGO)
                  carg=data[i][6]
                  cond_data={"conditions_Names":[constantes.CLAVE_CARGO],"condition_Types":["and"],"conditions_Values":[carg],"conditions_Verify":["="]}    
                  d_cargo=conexion_bd.get_allData(["cargo"],cond_data)
                  if(d_cargo!=[]):
                    if(d_cargo[0][0].lower()=="obrero" or d_cargo[0][0].lower()=="secretaria"):
                       no_docente+=1
                    else:
                       docente+=1
                  conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                  cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_TRABAJ],"condition_Types":["and"],"conditions_Values":[data[i][7]],"conditions_Verify":["="]}    
                  data_estatus=conexion_bd.get_allData(["estatus"],cond_data)
                  if(data_estatus[0][0]=="activo"):
                     activos+=1         
                  elif(data_estatus[0][0]=="inactivo"):
                      inactivos+=1
                  elif(data_estatus[0][0]=="de reposo"):
                      de_reposo+=1
                  elif(data_estatus[0][0]=="posible retiro"):
                    posible_retiro+=1
             if(tipo_data==cls.STADISTICS_WORKERS_CARGO):
                valores=[docente,no_docente]
             elif(tipo_data==cls.STADISTICS_WORKER_STATUS):
                valores=[activos,inactivos,de_reposo,posible_retiro]
       elif(opcion=="estudiantes"):
          conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
          data=conexion_bd.get_allData([])
          label_msg="total de\n  estudiantes"
          if(data!=[]):
             if(filtro=="tipo de cedula"):
               items=["cedulado","no cedulado"]
               tipo_data=cls.STADISTICS_STUDENTS_ID
               title="tipo de cedula de estudiantes"
             elif(filtro=="estatus del estudiante"):
               items=["activo","inactivos","reposo","graduados","intermit."]
               tipo_data=cls.STADISTICS_STUDENT_STATUS
               title=filtro
             elif(filtro=="genero"):
               items=["masculino","femenino"]
               tipo_data=cls.STADISTIC_STUDENTS_GENDER
               title="genero de los estudiantes"
             cedulados=0
             no_cedulados=0
             activos=0
             irregulares=0
             graduados=0
             inactivos=0
             intermitentes=0
             masculinos=0
             femeninos=0
             reposo=0
             for i in range(0,len(data)):
               conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
               cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[data[i][2]],"conditions_Verify":["="]}    
               data_estatus=conexion_bd.get_allData(["estatus","cedulado"],cond_data)
               if(data_estatus[0][1].lower()=="true"):
                  cedulados+=1
               else:
                  no_cedulados+=1
               if(data_estatus[0][0]=="activo"):
                  activos+=1
               elif(data_estatus[0][0]=="inactivo"):
                   inactivos+=1
               elif(data_estatus[0][0]=="irregular"):
                   irregulares+=1
               elif(data_estatus[0][0]=="graduado"):
                  graduados+=1
               elif(data_estatus[0][0]=="intermitente"):
                 intermitentes+=1
               elif(data_estatus[0][0]=="de reposo"):
                 reposo+=1
               if(data[i][6]=="masculino"):
                   masculinos+=1
               else:
                  femeninos+=1
             if(tipo_data==cls.STADISTICS_STUDENTS_ID):
                valores=[cedulados,no_cedulados]
             elif(tipo_data==cls.STADISTICS_STUDENT_STATUS):
                valores=[activos,inactivos,reposo,graduados,intermitentes]
             elif(tipo_data==cls.STADISTIC_STUDENTS_GENDER):
                valores=[masculinos,femeninos]
       elif(opcion=="secciones"):
          label_msg="total de\n secciones"
          conexion_bd.set_tabla(constantes.TABLA_SECCION)
          data=conexion_bd.get_allData([])
          if(data!=[]):
              if(filtro=="cantidad de secciones"):
                items=["1 año","2 año","3 año","4 año","5 año"]
                tipo_data=cls.STADISTICS_SECTIONS_COUNT
                title=f"{filtro}\n Segun Año"
              elif(filtro=="turno"):
                items=["mañana","tarde"]
                tipo_data=cls.STADISTICS_SECTIONS_TURNO
                title="Cantidad se Secciones \n Segun Turno"
              primer_año=0
              segundo_año=0
              tercer_año=0
              cuarto_año=0
              quinto_año=0
              mañana=0
              tarde=0
              masculino=0
              femenino=0
              cedulados=0
              no_cedulados=0
              for i in range(0,len(data)):
                 if(data[i][0]!="default"):
                   if(data[i][1]=="1"):
                      primer_año+=1
                   elif(data[i][1]=="2"):
                      segundo_año+=1
                   elif(data[i][1]=="3"):
                      tercer_año+=1
                   elif(data[i][1]=="4"):
                      cuarto_año+=1
                   elif(data[i][1]=="5"):
                      quinto_año+=1
                   conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                   cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[data[i][3]],"conditions_Verify":["="]}    
                   data_hor=conexion_bd.get_allData(["turno"],cond_data)
                   if(data_hor!=[]):
                       if(data_hor[0][0]=="tarde"):
                           tarde+=1
                       elif(data_hor[0][0]=="mañana"):
                           mañana+=1
              if(tipo_data==cls.STADISTICS_SECTIONS_COUNT):
                valores=[primer_año,segundo_año,tercer_año,cuarto_año,quinto_año]
              elif(tipo_data==cls.STADISTICS_SECTIONS_TURNO):
                 valores=[mañana,tarde]
       elif(opcion=="matricula"):
          conexion_bd.set_tabla(constantes.TABLA_SECCION)
          data=conexion_bd.get_allData([])
          label_msg="total de\n estudiantes"
          if(data!=[]):
              if(filtro=="año"):
                items=["1 año","2 año","3 año","4 año","5 año"]
                tipo_data=cls.STADISTICS_MATRICULA_ACADEMIC_YEAR
                title="matricula de estudiantes\n segun año de curso"
              elif(filtro=="turno"):
                items=["mañana","tarde"]
                tipo_data=cls.STADISTICS_MATRICULA_TURNO
                title="matricula de estudiantes\n segun turno"
              primer_año=0
              segundo_año=0
              tercer_año=0
              cuarto_año=0
              quinto_año=0
              mañana=0
              tarde=0
              for i in range(0,len(data)):
                 if(data[i][0]!="default"):
                   if(data[i][1]=="1"):
                      primer_año+=int(data[i][4])
                   elif(data[i][1]=="2"):
                      segundo_año+=int(data[i][4])
                   elif(data[i][1]=="3"):
                      tercer_año+=int(data[i][4])
                   elif(data[i][1]=="4"):
                      cuarto_año+=int(data[i][4])
                   elif(data[i][1]=="5"):
                      quinto_año+=int(data[i][4]) 
                   conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                   cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[data[i][3]],"conditions_Verify":["="]}    
                   data_hor=conexion_bd.get_allData(["turno"],cond_data)
                   if(data_hor!=[]):
                       if(data_hor[0][0]=="tarde"):
                           tarde+=int(data[i][4])
                       elif(data_hor[0][0]=="mañana"):
                           mañana+=int(data[i][4])      
              if(tipo_data==cls.STADISTICS_MATRICULA_ACADEMIC_YEAR):
                valores=[primer_año,segundo_año,tercer_año,cuarto_año,quinto_año]
              elif(tipo_data==cls.STADISTICS_MATRICULA_TURNO):
                 valores=[mañana,tarde]
       elif(opcion=="estudiantes con materias pendientes"):
          label_msg="total de\n  estudiantes"
          conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
          data=conexion_bd.get_allData([])
          if(data!=[]):
              items=["no cursando","cursando"]
              title="materias pendientes\n en "+filtro
              pendientes=0
              no_pendientes=0
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              for i in range(0,len(data)):
                 ced=data[i][0]
                 cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],"condition_Types":["and","and"],"conditions_Values":[ced,filtro],"conditions_Verify":["=","="]}    
                 pend=conexion_bd.get_allData([],cond_data)
                 if(pend!=[]):
                    pendientes+=1
                 else:
                    no_pendientes+=1
              valores=[ no_pendientes,pendientes]
       if(len(valores)<=0):
          General.show_message("no hay datos que se puedan mostrar","sin datos para el diagrama")
          return
       from ventana_sec import Stadistic_Windows
       stadistic_win=Stadistic_Windows(vent,{"Width":580,"Height":500},["#97D3E7","#323757"],usr)
       stadistic_win.draw_text( {"X":290,"Y":250},{"Font_Name":"Arial","Font_Style":"bold","Font_Size":25},["#3B346A","#FFFFFF"],"Cargando por favor espere")
       import threading
       hilo=threading.Thread(target=stadistic_win.draw_torta,args=(valores,title,items,label_msg))
       hilo.start()
       
                
    #Remove the Reactivation of an Academic Momentt
    @classmethod
    def reestablecer_momento(cls,usr,vent):
       pnl=vent.panelActual
       combo=pnl.get_comp_byTag("combo")
       time_object=tiempo()
       pass_entry=General.show_password_message("por favor escriba su password","password de administrado")    
       if(pass_entry=="" or pass_entry==None or pass_entry==" "):
           return  
       import time
       timestamp=str(int(time.time()))
       data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "password_send":pass_entry,
          "user_verify":"Admin_User"
       }
       url_send=f"{constantes.SERVER}compare_passwords.php"
       response=requests.post(url_send,data=data_user)
       json_content=json.loads(response.content)
       if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return
       if(json_content["message"]!="Same Password"):
           General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
           return
         
       if(General.show_confirmDialog("reestablecer momento academico?","reestablecer momento")!=True):
            return
       if(combo.get_selected_value()!="elejir" and combo.get_selected_value()!="elegir"):
          valor=combo.get_selected_value()
          conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
          cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[valor],"conditions_Verify":["="]}    
          mom=conexion_bd.get_allData([],cond_data)
          if(mom!=[]):
             if(mom[0][2].lower()!="true"):
                General.show_message("el momento academico aun no ha finalizado","momento no finalizado")
                return
             if(mom[0][1].lower()!="true"):
                General.show_message("el momento academico esta cerrado","momento cerrado")
                return
             actual_date=time_object.get_fecha()
             actual_time=time_object.get_tiempo()
             conexion_bd.update_data({"abierto":"false","modificado":time_object.get_fecha(),"fecha_limite":actual_date,"hora_limite":actual_time},cond_data)           
             usr.add_action_historial(["restablecer momento",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"servicio","reestablecer momento","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True)
             General.show_message("se ha reestablecido el momento exitosamente","momento reestablecido exitosamente")
             from event_manager import Event_manager
             Event_manager.activar_element("reactivar",True,True)
             Event_manager.activar_element("reestablecer",False,True)
              
          else:
             General.show_message("no se ha registrado aun el momento indicado","momento no registrado")
       else:  
          General.show_message("seleccione un momento a reestablecer","momento invaldo")
       pnl.get_comp_byTag("field").set_text("")
       
       
    #Reactivate an Academic Moment for a Time Limit
    @classmethod
    def activar_momento(cls,usr,vent):
       pnl=vent.panelActual
       combo=pnl.get_comp_byTag("combo")
       pass_entry=General.show_password_message("por favor escriba su password","password de administrado")    
       if(pass_entry=="" or pass_entry==None or pass_entry==" "):
           return  
       import time
       timestamp=str(int(time.time()))
       data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "password_send":pass_entry,
          "user_verify":"Admin_User"
       }
       url_send=f"{constantes.SERVER}compare_passwords.php"
       response=requests.post(url_send,data=data_user)
       json_content=json.loads(response.content)
       if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return
       if(json_content["message"]!="Same Password"):
           General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
           return
         
       if(General.show_confirmDialog("reactivar momento academico?","reactivar momento")!=True):
            return
            
       if(combo.get_selected_value()!="elejir" and combo.get_selected_value()!="elegir"):
          valor=combo.get_selected_value()
          conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
          cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[valor],"conditions_Verify":["="]}    
          mom=conexion_bd.get_allData([],cond_data)
          if(mom!=[]):
             if(mom[0][2].lower()!="true"):
                General.show_message("el momento academico aun no ha finalizado","momento no finalizado")
                return
             if(mom[0][1].lower()=="true"):
                General.show_message("el momento academico aun sigue activo","momento abierto")
                return
             valor_t=pnl.get_comp_byTag("field").get_text()
             if(General.is_valid(valor_t,constantes.CADENA_SOLONUMERO,False,0)==False):
                General.show_message(" por favor escriba el numero de minutos a reactivar","tiempo invalido")
                return
             if(int(valor_t)>=1200):
               General.show_message("la cantidad de minutos es excesiva","demasiado tiempo de reactivacion")
               return
             time_object=tiempo()
             minutos=int(valor_t)
             temp_fecha=time_object.get_full_time(minutos)
             nueva_fecha=temp_fecha[0]
             nuevo_tiempo=temp_fecha[1]
             conexion_bd.update_data({"abierto":"true","modificado":time_object.get_fecha(),"fecha_limite":nueva_fecha,"hora_limite":nuevo_tiempo},cond_data)
             usr.add_action_historial(["reactivar momento",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"servicio","reactivar momento","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True)
             General.show_message("se ha reactivado el momento por "+valor_t+" minutos exitosamente","reactivacion exitosa")   
             from event_manager import Event_manager
             Event_manager.activar_element("reactivar",False,True)
             Event_manager.activar_element("reestablecer",True,True)
          else:
             General.show_message("no se ha registrado aun el momento indicado","momento no registrado")
       else:  
         General.show_message("seleccione un momento a reactivar","momento invaldo")
       pnl.get_comp_byTag("field").set_text("")
   
    #Manage Security Copies of Data Base
    @classmethod
    def Security_Copies_Manage(cls,usr,vent):
        pnl=vent.panelActual
        pnl.get_comp_byName("cargando").set_active(False)
        radios=pnl.get_comp_byTag("radio")
        ubicacion=pnl.get_comp_byName("ubicacion").get_text()
        formato=".csv"
        pass_entry=General.show_password_message("por favor escriba su password","password de administrado")    
        if(pass_entry=="" or pass_entry==None or pass_entry==" "):
           return  
        import time
        timestamp=str(int(time.time()))
        data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "password_send":pass_entry,
          "user_verify":"Admin_User"
        }
        url_send=f"{constantes.SERVER}compare_passwords.php"
        response=requests.post(url_send,data=data_user)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return
        if(json_content["message"]!="Same Password"):
           General.show_error("operacion invalida, el password no coincide con el del Usuario Administrador","Password Invalido")
           return
         
        if(radios.get_selected_value()=="respaldar"):
            if(General.show_confirmDialog("estas seguro que desea crear respaldo la BD?","registrar")!=True):
               return
            pnl.get_comp_byName("cargando").set_active(True)
            conexion_bd.respaldar_bd(ubicacion,"",formato,vent.raiz)
        else:   
            if(General.show_confirmDialog("estas seguro que desea restaurar la BD?","registrar")!=True):
               return
            pnl.get_comp_byName("cargando").set_active(True)
            conexion_bd.restore_bd(ubicacion,formato,vent.raiz)   
    
    #Organizate the Sections 
    @classmethod
    def organizar_secciones(cls,usr,vent):
        pnl=vent.panelActual
        accion_comp=pnl.get_comp_byName("accion_List")
        accion_str=""
        main_seccion=pnl.get_comp_byName("secc_main_list")
        seccion_main_id=""
        motivo=""
        secc1=pnl.get_comp_byName("secc1")
        secc2=pnl.get_comp_byName("secc2")
        
        if(main_seccion!=None):
            secc_value=main_seccion.get_selected_value()
            if(secc_value!="elegir"):
               seccion_main_id=secc_value
        if(accion_comp!=None):
          accion_val=accion_comp.get_selected_value()
          if(accion_val.lower()!="elegir"):
              accion_str=accion_val
        if(accion_str==""):
           General.show_message("Por Favor Indique la Accion a Realizar","Accion Invalida")
           return
        if(seccion_main_id==""):
           General.show_message("Por Favor Indique la Seccion a Modificar","Seccion Principal Invalida")
           return
        if(accion_str=="Asignar Prof Guia"):
           guia_comp=pnl.get_comp_byName("guia")
           guia_id=""
           if(guia_comp!=None):
              guia_value=guia_comp.get_selected_value()
              if(guia_value.lower()!="elegir"):
                 guia_value=guia_value.split("-")
                 if(len(guia_value)>=3):
                    guia_id=f"{guia_value[0]}-{guia_value[1]}"
           if(guia_id==""):
              General.show_message("Por Favor Indique el Prof Asignar como guia","Profesor Guia Invalido")
              return
           if(General.show_confirmDialog("Actualizar Profesor Guia","Actualizar Profesor")==False):
              return
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           cond_data={"conditions_Names":["seccion_guia"],"condition_Types":["and"],"conditions_Values":[seccion_main_id],"conditions_Verify":["="]}                   
           old_prof_dat=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data)
           if(len(old_prof_dat)>0):
              id_old_prof=old_prof_dat[0][0]
              cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[id_old_prof],"conditions_Verify":["="]}     
              conexion_bd.update_data({"seccion_guia":""},cond_data)
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[guia_id],"conditions_Verify":["="]}       
           conexion_bd.update_data({"seccion_guia":seccion_main_id},cond_data)
           motivo="Actualizar Profesor Guia"
           guia_comp.set_selected_index(0)
           guia_comp.set_active(False)
           pnl.get_comp_byName("prof_guialabel").set_active(False)
           General.show_message("Profesor Guia Actualizado Exitosamente","Accion Exitosa")        
        else:
            seccion_sec_id=""
            sec_seccion=pnl.get_comp_byName("secc_sec_list")
            if(sec_seccion!=None):
               secc_value=sec_seccion.get_selected_value()
               if(secc_value!="elegir"):
                   seccion_sec_id=secc_value
            if(seccion_sec_id==""):
                General.show_message("Por Favor Indique la Seccion Secundara","Seccion Secundaria Invalida")
                return 
          
            if(General.show_confirmDialog("actualizar Estudiantes de las Secciones?","Actualizar Estudiantes")!=True):
                 return 
            data_secc1=secc1.get_all_values()
            data_secc2=secc2.get_all_values()
            cls.reasignar_secion(data_secc1,data_secc2,seccion_main_id,seccion_sec_id)           
            General.show_message("secciones actualizadas exitosamente","secciones actualizadas")
            secc1_name=seccion_main_id.split("(")
            if(secc1_name[1].startswith("M")):
                secc1_name=secc1_name[0]+"(Mañana)"
            else:
                secc1_name=secc1_name[0]+"(Tarde)"              
            motivo="modificaciones sobre seccion:"+secc1_name
            secc2_name=seccion_sec_id.split("(")
            if(secc2_name[1].startswith("M")):
                secc2_name=secc2_name[0]+"(Mañana)"
            else:
                secc2_name=secc2_name[0]+"(Tarde)"
            motivo=motivo+" y "+secc2_name
        time_object=tiempo()
        usr.add_action_historial(["organizar secciones",time_object.get_tiempo()])
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"servicio","organizar secciones",motivo,time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True)
        pnl.get_comp_byName("secc_main_list").set_selected_index(0)
        pnl.get_comp_byName("secc_sec_list").set_selected_index(0)
        pnl.get_comp_byName("accion_List").set_selected_index(0)
        secc1.set_values([])
        secc2.set_values([])  
     
    #Reassign Students to the Required Sections
    @classmethod
    def reasignar_secion(cls,listA,listB,seccA,seccB):
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       #Organizate Section A
       for i in range(0,len(listA)):
          id_estudent=listA[i].split("-")
          if(len(id_estudent)==3):
             id_estudent=id_estudent[0]+"-"+id_estudent[1]
          elif(len(id_estudent)==2):
             id_estudent=id_estudent[0]
          else:
              id_estudent=""
          cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[id_estudent],"conditions_Verify":["="]}              
          conexion_bd.update_data({constantes.CLAVE_SECCION:seccA},cond_data)
       
       #Organizate Section B
       for j in range(0,len(listB)):
          id_estudent=listB[j].split("-")
          if(len(id_estudent)==3):
             id_estudent=id_estudent[0]+"-"+id_estudent[1]
          elif(len(id_estudent)==2):
             id_estudent=id_estudent[0]
          else:
              id_estudent=""
          cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[id_estudent],"conditions_Verify":["="]}               
          conexion_bd.update_data({constantes.CLAVE_SECCION:seccB},cond_data)
       
       conexion_bd.set_tabla(constantes.TABLA_SECCION)
       cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[seccA],"conditions_Verify":["="]}              
       conexion_bd.update_data({"total_estud":str(len(listA))},cond_data)
       cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[seccB],"conditions_Verify":["="]}              
       conexion_bd.update_data({"total_estud":str(len(listB))},cond_data)
            
    #Update a Student from Service Panel
    @classmethod
    def update_estudiante(cls,usr,vent):
        from estudiante import estudiante
        pnl=vent.panelActual
        cedula=pnl.get_comp_byName("cedula_estud").get_text()
        if(cedula==""):
           General.show_message("por favor Indique el Estudiante","Estudiante invalido")
           return
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
        estatus_id=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],cond_data)[0][0]
        conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[estatus_id],"conditions_Verify":["="]}              
        old_estatus=conexion_bd.get_allData([],cond_data)
        cedulado=old_estatus[0][3]
        fecha=pnl.get_comp_byName("fecha")
        fields=pnl.get_comps_byTag("field")
        data_estud=[cedula,"","","","","","",""]
        data_estatus=[""]
        data_repres=["","","","","","","",""]
        data_dir=""
        data_exp=["",""]
        for i in range(0,len(fields)):
            if(fields[i].get_state()==True):
                valor=fields[i].get_text()
                if(fields[i].get_id()=="nombre"):
                    data_estud[1]=valor     
                elif(fields[i].get_id()=="apellido"):
                    data_estud[2]=valor      
                elif(fields[i].get_id()=="CIrepres"):
                    data_repres[0]=fields[i].get_text()
                elif(fields[i].get_id()=="telef"):
                    data_repres[3]=fields[i].get_text()     
                elif(fields[i].get_id()=="nombre_repres"):
                     data_repres[1]=fields[i].get_text()   
                elif(fields[i].get_id()=="apellido_repres"):
                     data_repres[2]=fields[i].get_text()                       
                elif(fields[i].get_id()=="destino_file"):
                    data_exp[0]=fields[i].get_text()    
                elif(fields[i].get_id()=="destino_foto"):
                    data_exp[1]=fields[i].get_text()       
                elif(fields[i].get_id()=="direccion"):
                    data_dir=fields[i].get_text()
                elif(fields[i].get_id()=="estatus"):
                     data_estud[4]=valor
                elif(fields[i].get_id()=="cedulado"):
                    if(cedulado.lower()=="false" or cedulado.lower()=="no"):
                          data_estud[7]=valor
                elif(fields[i].get_id()=="dir_representante"):
                    data_repres[5]=fields[i].get_text()
                elif(fields[i].get_id()=="correo"):
                    data_repres[4]=fields[i].get_text() 
                elif(fields[i].get_id()=="parentesco"):
                    data_repres[6]=fields[i].get_text() 
                elif(fields[i].get_id()=="ocupacion"):
                     data_repres[7]=fields[i].get_text() 
        if(fecha!=None):
           data_estud[3]=fecha.get_text()       
        combos=pnl.get_comps_byTag("combo")
        for j in range(0,len(combos)):
            id_c=combos[j].get_id()
            if(id_c=="salud"):
                 data_estud[5]=combos[j].get_selected_value()
            elif(id_c=="estatus2"):
                data_estud[4]=data_estud[4]+"-"+combos[j].get_selected_value()            
        radio= pnl.get_comp_byName("genero") 
        data_estud[6]=radio.get_selected_value()
        estud=estudiante()
        res=estud.is_valid_modific(cedula,cedulado,data_estud,data_repres,data_exp,data_dir)
        if(res[0]==True):
           if(General.show_confirmDialog("modificar estudiante?","modificar estudiante")!=True):
              return
           time_object=tiempo()
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
           old_d=conexion_bd.get_allData([],cond_data)[0]
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[old_d[5]],"conditions_Verify":["="]}              
           old_d_r=conexion_bd.get_allData([],cond_data)[0]
           if(res[2][0]==True):
              #The Student Change from without Student Id to with Id
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              next_cedul=""
              nacionalidad= pnl.get_comp_byName("nacionalidad").get_selected_value()
              if(nacionalidad.lower().startswith("v")):
                  next_cedul="V-"+res[2][1]
              elif(nacionalidad.lower().startswith("e")):
                  next_cedul="E-"+res[2][1]
              else:
                  next_cedul="V-"+res[2][1]
              next_d=[next_cedul]
              for ie in range(1,len(old_d)):
                 next_d.append(old_d[ie])
              conexion_bd.add_data(next_d)
              conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
              cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[next_d[2]],"conditions_Verify":["="]}              
              conexion_bd.update_data({"cedulado":"True"},cond_data)
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
              conexion_bd.update_data({constantes.CLAVE_ESTUDIANTE:next_d[0]},cond_data)
              conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
              old_califs=conexion_bd.get_allData([],cond_data)
              for ic in range(0,len(old_califs)):
                 new_calif=list(old_califs[ic])
                 old_id=new_calif[0]
                 new_calif[0]=next_d[0]+"-"+new_calif[3]+new_calif[2]
                 new_calif[1]=next_d[0]
                 conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                 conexion_bd.add_data(new_calif)
                 conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                 cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[old_id],"conditions_Verify":["="]}              
                 conexion_bd.update_data({constantes.CLAVE_CALIFICACION_FINAL:new_calif[0]},cond_data)
              conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
              cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
              conexion_bd.delete_data(cond_data)
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              conexion_bd.delete_data(cond_data)
              cedula=next_d[0]
              old_d=conexion_bd.get_allData([],cond_data)[0]
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           next_dir_r=res[6]
           for dr_r in range(0,3):
              temp_dire_r=""
              #Verify No Exist Empty Character at end or Init of String
              for chr_r in range(0,len(res[6][dr_r])):
                 if(chr_r==0):
                    if(res[6][dr_r][chr_r]!=" "):
                       temp_dire_r=temp_dire_r+res[6][dr_r][chr_r]
                 elif(chr_r==len(res[6][dr_r])-1):
                    if(res[6][dr_r][chr_r]!=" "):
                       temp_dire_r=temp_dire_r+res[6][dr_r][chr_r]
                 else:
                      temp_dire_r=temp_dire_r+res[6][dr_r][chr_r]
              res[6][dr_r]=temp_dire_r.lower()
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           if(conexion_bd.id_exist(constantes.CLAVE_REPRESENTANTE,res[3][0])==False):
               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
               id_nomb_r=conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE)
               conexion_bd.add_data([id_nomb_r,res[3][1],res[3][2],res[3][3],res[3][4],time_object.get_fecha()])
               conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
               code_dir_r=conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION)
               conexion_bd.add_data([code_dir_r,res[6][0],res[6][1],res[6][2],time_object.get_fecha()])
               conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
               conexion_bd.add_data([res[3][0],id_nomb_r,res[3][5],res[3][6],res[3][8],code_dir_r,time_object.get_fecha()])
               conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
               cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
               conexion_bd.update_data({constantes.CLAVE_REPRESENTANTE:res[3][0]},cond_data)
               cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[old_d[5]],"conditions_Verify":["="]}              
               resto=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data)
               if(len(resto)<=0):
                 conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                 conexion_bd.delete_data(cond_data)
           else:
               cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[res[3][0]],"conditions_Verify":["="]}              
               repres_d=conexion_bd.get_allData([constantes.CLAVE_NOMBRE,constantes.CLAVE_DIRECCION],cond_data)
               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
               cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[repres_d[0]],"conditions_Verify":["="]}              
               conexion_bd.update_data({"nombre":res[3][1],"s_nombre":res[3][2],"apellido":res[3][3],"s_apellido":res[3][4],"modificado":time_object.get_fecha()},cond_data)
               conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
               cond_data={"conditions_Names":[constantes.CLAVE_DIRECCION],"condition_Types":["and"],"conditions_Values":[repres_d[0][1]],"conditions_Verify":["="]}              
               conexion_bd.update_data({"sector":res[6][0],"parroquia":res[6][1],"casa":res[6][2],"modificado":time_object.get_fecha()},cond_data)
               conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
               cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[res[3][0]],"conditions_Verify":["="]}              
               conexion_bd.update_data({"telef":res[3][5],"correo":res[3][6],"ocupacion":res[3][8],"modificado":time_object.get_fecha()},cond_data)
               #Exist Modifications Over Representant
               if(res[3][0]!=old_d[5]):
                   conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                   cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
                   conexion_bd.update_data({constantes.CLAVE_REPRESENTANTE:res[3][0]},cond_data)
                   cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[old_d[5]],"conditions_Verify":["="]}              
                   resto=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data)
                   if(len(resto)<=0):
                       conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                       conexion_bd.delete_data(cond_data)
                       conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                       cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[old_d_r[1]],"conditions_Verify":["="]}              
                       conexion_bd.delete_data(cond_data)
                       conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                       cond_data={"conditions_Names":[constantes.CLAVE_DIRECCION],"condition_Types":["and"],"conditions_Values":[old_d_r[5]],"conditions_Verify":["="]}              
                       conexion_bd.delete_data(cond_data)
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           next_dir=res[5]
           for dr in range(0,3):
              temp_dire=""
              #Verify No Exist Empty Character at end or Init of String
              for chr in range(0,len(next_dir[dr])):
                 if(chr==0):
                    if(next_dir[dr][chr]!=" "):
                       temp_dire=temp_dire+next_dir[dr][chr]
                 elif(chr==len(next_dir[dr])-1):
                    if(next_dir[dr][chr]!=" "):
                       temp_dire=temp_dire+next_dir[dr][chr]
                 else:
                      temp_dire=temp_dire+next_dir[dr][chr]
              next_dir[dr]=temp_dire.lower()
           cond_data={"conditions_Names":[constantes.CLAVE_DIRECCION],"condition_Types":["and"],"conditions_Values":[old_d[8]],"conditions_Verify":["="]}              
           conexion_bd.update_data({"sector":next_dir[0],"parroquia":next_dir[1],"casa":next_dir[2],"modificado":time_object.get_fecha()},cond_data)
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           err_upload=False
           if(res[4][0]!=""):
              if(res[4][0].startswith("expedientes/")==False):
                 url=constantes.SERVER+"upload_expediente.php"
                 old_path=res[4][0]
                 with open(res[4][0],"rb") as temp_file:                
                    dict_exp={"file":temp_file}
                    response=requests.post(url,files=dict_exp)                                    
                    resp=response.text.strip()
                    res[4][0]=resp
                    if(resp.startswith("expedientes/")==False):
                        res[4][0]="..."
                        err_upload=True
                    else:
                       if(os.path.exists(constantes.FOLDER_DOCUMENTS+cedula+".zip")):
                           os.remove(constantes.FOLDER_DOCUMENTS+cedula+".zip")
                 if(os.path.exists(old_path)):
                        os.remove(old_path)
           if(res[4][1]!=""):
               if(res[4][1].startswith("fotos/")==False):
                 url=constantes.SERVER+"upload_foto.php"
                 with open(res[4][1],"rb") as temp_file:
               
                    dict_exp={"file":temp_file}
                    response=requests.post(url,files=dict_exp)
                    resp=response.text.strip()
                    res[4][1]=resp
                    if(resp.startswith("fotos/")==False):
                        res[4][1]="..."
                        err_upload=True
           cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[old_d[4]],"conditions_Verify":["="]}                                   
           conexion_bd.update_data({"src_exp":res[4][0],"src_foto":res[4][1],"modificado":time_object.get_fecha()},cond_data)
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[old_d[2]],"conditions_Verify":["="]}              
           conexion_bd.update_data({"estatus":res[1][9],"salud":res[1][10],"modificado":time_object.get_fecha()},cond_data)
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[old_d[1]],"conditions_Verify":["="]}              
           conexion_bd.update_data({"nombre":res[1][1],"s_nombre":res[1][2],"apellido":res[1][3],"s_apellido":res[1][4],"modificado":time_object.get_fecha()},cond_data)
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           values={"genero":res[1][11],"nacimiento":res[1][12],"parentesco":res[3][7],"modificado":time_object.get_fecha()}
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
           conexion_bd.update_data(values,cond_data)
           usr.add_action_historial(["actualizar estudiante",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","estudiante","",time_object.get_fecha()]
           conexion_bd.add_data(data_hist,True)
           General.show_message("actualizacion del estudiante realizada exitosamnte","estudiante actualizado")
           if(err_upload==True):
               General.show_error("fallo al subir expediente, por favor vuelva a intentarlo","error en expediente")
           vent.update_pantallas(constantes.PANTALLA_WELCOME,usr)
           
        else:
           #resultado de validacion invalido
           if(res[0]==-1): 
              General.show_message("por favor escriba un nombre valido","nombre invalido")
           elif(res[0]==-2):
              General.show_message("por favor escriba un apellido valido","apellido invalido")
           elif(res[0]==-3):
              General.show_message("por favor escriba una fecha de nacimiento valida","fecha invalido")
           elif(res[0]==-4):
             General.show_message("no se puede modificar el estatus de un estudiante irregular","estatus no modificable")
           elif(res[0]==-5):
              General.show_message("por favor elija un estado de salud valido","estado de salud no  invalido")
           elif(res[0]==-6):
              General.show_message("por favor escriba una nueva cedula valida","nueva cedula invalido")
           elif(res[0]==-7):
              General.show_message("por favor escriba cedula de representante valida","cedula de representante invalida")
           elif(res[0]==-8):
              General.show_message("por favor escriba un nombre de representante valido","nombre de representante invalido")
           elif(res[0]==-9):
              General.show_message("por favor escriba un apellido de representante valido","apellido de representante invalido")
           elif(res[0]==-10):
              General.show_message("por favor escriba un telefono de representante valido","telefono de representante invalido")
           elif(res[0]==-11):
              General.show_message("error la direccion debe ser xxxxx,xxxx,xxxx","direccion invalida")
           elif(res[0]==-12):
              General.show_message("el expdiente debe ser una archivo RAR o ZIP","formato de expediente invalido")
           elif(res[0]==-13):
              General.show_message("la foto debe ser una archivo JPEG o PNG","formato de foto invalido")
           elif(res[0]==-14):
              General.show_message("el archivo del expediente ya existe en el servidor, cambie el nombre y vuelva intentarñp","archivo de expediente ya existente")
           elif(res[0]==-15):
             General.show_message("el archivo de la foto ya existe en el servidor, cambie el nombre y vuelva intentarñp","archivo de foto ya existente")
           elif(res[0]==-16):
              General.show_message("ya existe un estudiante con la cedula indicada","cedula ya existente")
           elif(res[0]==-17):
              General.show_message("por favor escriba un correo de representante valido","correo invalido")
           elif(res[0]==-18):
              General.show_message("por favor escriba una direccion de la forma xxx,xxx,xxx","direccion de representante invalido")
           elif(res[0]==-19):
              General.show_message("por favor escriba un parentesco valido","parentesco invalido")
           elif(res[0]==-20):
              General.show_message("por favor escriba una ocupacion valida del representante","ocupacion invalida")
   