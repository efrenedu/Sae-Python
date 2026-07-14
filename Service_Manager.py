from documento import documento
from tiempo import tiempo
from conexion_bd import conexion_bd
from constantes import constantes
from General import General
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
    CHANGE_STUDENT_SECTION1_TO_SECTION2=0
    INTERAMBIATE_STUDENTS=1
    CHANGE_STUDENT_SECTION2_TO_SECTION1=2
    UPDATE_SECTIONS=3
    USER_UNLOCK=0
    USER_RESET_PASSWORD=1
    USER_REMOVE=2
    USER_CHANGE_ACCESS_LEVEL=4
    RECOVER_PASS_REQUEST=0
    RECOVER_PASS_LOAD_FIRST_PANEL=1
    RECOVER_PASS_VERIFY_SECRET_QUESTIONS=2
    RECOVER_PASS_CHANGE_PASSWORD=3
    
    
    #Manage the Operation in User Gestion Panel except Register New User
    @classmethod
    def gestion_usuario(cls,usr,vent,opcion):
       pnl=vent.panelActual
       tabl=pnl.get_comp_byTag("table")
       temp_clave=tabl.get_row_selectedData()
       fields_user=[constantes.CLAVE_USUARIO,"password",constantes.CLAVE_TRABAJADOR,"nivel_acceso",constantes.CLAVE_INTENTOS_USUARIO,"bloqueado"]
       clave=""
       time_object=tiempo()
       if(temp_clave==" "):
          General.show_message("por favor seleccione un usuario valido","usuario invalido")
          return
       else:
          clave=temp_clave[0]
       if(opcion==cls.USER_UNLOCK):
          pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
          valid_admin=False
          if(pass_admin=="" or pass_admin==None):
               return
          if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
             p_user=General.desencriptar(usr.get_credentials()[4])
             if(p_user==pass_admin):
                valid_admin=True                                  
          if(valid_admin==False):
                General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
                return           
          conexion_bd.set_tabla(constantes.TABLA_USUARIO)
          old_d=conexion_bd.get_allData(["bloqueado"],1,[constantes.CLAVE_USUARIO],[clave],["and"])
          if(old_d!=[]):
            if(old_d[0][0]=="False"):
                 General.show_error("el usuario no esta bloquead","usuario no bloquead")
                 return
          if(General.show_confirmDialog("estas seguro que desea desbloquear el usuario?","desbloquear usuario")!=True):
               return
          fields=["bloqueado"]
          fields2=["num_intentos","last_fecha","last_hora"]
          values=["False"]
          values2=["0","",""]
          if(conexion_bd.update_data(fields,values,1,[constantes.CLAVE_USUARIO],[clave],["and"])!=-1):
             data_user=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],1,[constantes.CLAVE_USUARIO],[clave],["and"])
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             conexion_bd.update_data(fields2,values2,3,[constantes.CLAVE_INTENTOS_USUARIO],[data_user[0][0]],["and"])
             conexion_bd.set_tabla(constantes.TABLA_USUARIO)
             tabl.reset()
             new_data=conexion_bd.get_allData(fields_user,len(fields_user))
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             for i in range(0,len(new_data)):
                   if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                      temp_data=[]
                      for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           data_intentos=conexion_bd.get_allData(["num_intentos"],1,[constantes.CLAVE_INTENTOS_USUARIO],[new_data[i][4]],["and"])
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
             conexion_bd.add_data(data_hist)
             General.show_message("usuario desbloqueado exitosamente","usuario desbloqueado")      
       elif(opcion==cls.USER_RESET_PASSWORD):
          #reset password
          pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
          valid_admin=False
          if(pass_admin=="" or pass_admin==None):
               return
          if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
               p_user=General.desencriptar(usr.get_credentials()[4])
               if(p_user==pass_admin):
                   valid_admin=True     
          if(valid_admin==False):
                General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
                return
          if(General.show_confirmDialog("estas seguro que desea reestablecer el password del usuario?","registrar")!=True):
               return
          conexion_bd.set_tabla(constantes.TABLA_USUARIO)
          fields=["password"]
          values=[General.encriptar(constantes.PASS_USER_DEFAULT)]
          if(conexion_bd.update_data(fields,values,1,[constantes.CLAVE_USUARIO],[clave],["and"])!=-1):
             tabl.reset()
             new_data=conexion_bd.get_allData(fields_user,len(fields_user))
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             for i in range(0,len(new_data)):
               if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                  temp_data=[]
                  for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           data_intentos=conexion_bd.get_allData(["num_intentos"],1,[constantes.CLAVE_INTENTOS_USUARIO],[new_data[i][4]],["and"])
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
             conexion_bd.add_data(data_hist)
             General.show_message("password reestablecido a "+constantes.PASS_USER_DEFAULT,"password reestablecido")
       elif(opcion==cls.USER_REMOVE):
            #borrar usuario
            pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
            valid_admin=False
            if(pass_admin=="" or pass_admin==None):
                return
            if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
                p_user=General.desencriptar(usr.get_credentials()[4])
                if(p_user==pass_admin):
                    valid_admin=True  
            if(valid_admin==False):
                General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
                return
            if(General.show_confirmDialog("estas seguro que desea borrar el usuario?","registrar")!=True):
               return
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],1,[constantes.CLAVE_USUARIO],[clave],["and"])
            conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
            if(conexion_bd.delete_data([constantes.CLAVE_USUARIO],[clave],["and"])!=-1):   
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               conexion_bd.delete_data([constantes.CLAVE_USUARIO],[clave],["and"])
               conexion_bd.set_tabla(constantes.TABLA_USUARIO)
               if(conexion_bd.delete_data([constantes.CLAVE_USUARIO],[clave],["and"])!=-1):  
                 conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                 conexion_bd.delete_data([constantes.CLAVE_INTENTOS_USUARIO],[data_intentos[0][0]],["and"])
                 tabl.reset()
                 conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                 new_data=conexion_bd.get_allData(fields_user,len(fields_user))
                 conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                 for i in range(0,len(new_data)):
                   if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                      temp_data=[]
                      for j in range(0,len(new_data[i])):
                        if(j!=4):
                           temp_data.append(new_data[i][j])
                        else:
                           data_intentos=conexion_bd.get_allData(["num_intentos"],1,[constantes.CLAVE_INTENTOS_USUARIO],[new_data[i][4]],["and"])
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
                 conexion_bd.add_data(data_hist)
                 General.show_message("usuario eliminado exitosamente","usuario borrado")
       elif(opcion==cls.USER_CHANGE_ACCESS_LEVEL):
           pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
           valid_admin=False
           if(pass_admin=="" or pass_admin==None):
                return
           if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
                p_user=General.desencriptar(usr.get_credentials()[4])
                if(p_user==pass_admin):
                    valid_admin=True 
           if(valid_admin==False):
                General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
                return
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
                  fields=["nivel_acceso"]
                  values=[new_permit]
                  if(conexion_bd.update_data(fields,values,1,[constantes.CLAVE_USUARIO],[clave],["and"])!=-1):
                    tabl.reset()
                    new_data=conexion_bd.get_allData(fields_user,len(fields_user))
                    conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                    for i in range(0,len(new_data)):
                       if(new_data[i][0]!="admin" and new_data[i][0]!="admin01"):
                            temp_data=[]
                            for j in range(0,len(new_data[i])):
                               if(j!=4):
                                  temp_data.append(new_data[i][j])
                               else:
                                   data_intentos=conexion_bd.get_allData(["num_intentos"],1,[constantes.CLAVE_INTENTOS_USUARIO],[new_data[i][4]],["and"])
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
                    conexion_bd.add_data(data_hist)
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
            old_icon=conexion_bd.get_allData(["foto"],1,[constantes.CLAVE_USUARIO],[user_r],["and"])[0][0]
            if(old_icon!="fotos/"+file_name):
                General.show_message("ya existe una imagen con ese nombre en el servidor,cambie el nombre e intentelo de nuevo","imagen ya existe en server")
                return  
        self_pass=General.show_password_message("por favor confirme su contraseña","confirmar contraseña")
        if(self_pass==None or self_pass==""):
            return
        real_pass=General.desencriptar(usr.get_credentials()[4])
        if(self_pass!=real_pass):
            General.show_error("error de acceso,el password ingresado no coincide","error de acceso")
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
            conexion_bd.update_data(["foto"],[res],1,[constantes.CLAVE_USUARIO],[user_r],["and"])
            new_icon=res
        if(modific_pass):
            valor_pass1=General.encriptar(valor_pass1)
            conexion_bd.update_data(["password"],[valor_pass1],1,[constantes.CLAVE_USUARIO],[user_r],["and"])
            usr.change_password(valor_pass1)
        conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
        for pr in range(0,num_preg):
            pregunta=preguntas[pr][0]
            num=preguntas[pr][1]
            respuest=respuestas[pr]
            exist=conexion_bd.get_allData([constantes.CLAVE_PREGUNTA_SECRETA],1,[constantes.CLAVE_USUARIO,"numero"],[user_r,num],["and","and"])
            if(exist!=[]):
                conexion_bd.update_data(["pregunta","respuesta","modificado"],[pregunta,respuest,time_object.get_fecha()],3,[constantes.CLAVE_PREGUNTA_SECRETA],[exist[0][0]],["and"])
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
            old_user_dire=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],1,[constantes.CLAVE_USUARIO],[user_r],["and"])
            old_dire=old_user_dire[0][0]
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)        
            if(ced_dire!=old_dire):
                  data_t_dire=conexion_bd.get_allData([constantes.CLAVE_CARGO],1,[constantes.CLAVE_TRABAJADOR],[ced_dire],["and"])
                  if(data_t_dire!=[]):
                       conexion_bd.set_tabla(constantes.TABLA_CARGO)
                       conexion_bd.update_data(["cargo","modificado"],["Director",time_object.get_fecha()],2,[constantes.CLAVE_CARGO],[data_t_dire[0][0]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                       old_user=conexion_bd.get_allData([constantes.CLAVE_USUARIO],1,[constantes.CLAVE_TRABAJADOR],[ced_dire],["and"])
                       if(old_user!=[]):
                           data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],1,[constantes.CLAVE_USUARIO],[old_user[0][0]],["and"])
                           conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
                           if(conexion_bd.delete_data([constantes.CLAVE_USUARIO],[old_user[0][0]],["and"])!=-1):   
                              conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                              conexion_bd.delete_data([constantes.CLAVE_USUARIO],[old_user[0][0]],["and"])
                              conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                              conexion_bd.delete_data([constantes.CLAVE_USUARIO],[old_user[0][0]],["and"])  
                              conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                              conexion_bd.delete_data([constantes.CLAVE_INTENTOS_USUARIO],[data_intentos[0][0]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                       conexion_bd.update_data([constantes.CLAVE_TRABAJADOR,"modificado"],[ced_dire,time_object.get_fecha()],2,[constantes.CLAVE_USUARIO],[user_r],["and"])
            if(old_dire!="000" and old_dire!="001" and old_dire!=ced_dire):
                  #Prevent Assign Default Admin Worker or the old Worker
                  conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                  data_t_old=conexion_bd.get_allData([constantes.CLAVE_CARGO],1,[constantes.CLAVE_TRABAJADOR],[old_dire],["and"])
                  if(data_t_old!=[]):
                       conexion_bd.set_tabla(constantes.TABLA_CARGO)
                       conexion_bd.update_data(["cargo","modificado"],["Docente",time_object.get_fecha()],2,[constantes.CLAVE_CARGO],[data_t_old[0][0]],["and"])       
        usr.add_action_historial(["Modificar datos de usuario",time_object.get_tiempo()])     
        General.show_message("actualizacion de datos del usuario realizada satisfactoriamente","usuario actualizado")
        vent.update_pantallas(constantes.PANTALLA_WELCOME)        
        if(new_icon!=""):
            pnl=vent.panelActual
            url_i=constantes.SERVER+new_icon
            icon_welcome=pnl.get_comp_byName("logo_inicio")
            icon_welcome.change_image(url_i)  
    
    #Manage the Password Recovery from a User
    @classmethod
    def recuperar_password(cls,usr,vent,fase):
        pnl=vent.panelActual
        if(fase==cls.RECOVER_PASS_REQUEST or fase==cls.RECOVER_PASS_LOAD_FIRST_PANEL):
           user_r=pnl.get_comp_byName("usuario_login").get_text()
           if(user_r=="" or user_r==" "):
                General.show_message("por favor escriba el nombre de usuario","usuario no valido")
                return
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           if(conexion_bd.id_exist(constantes.CLAVE_USUARIO,user_r)):
              d_user=conexion_bd.get_allData(["bloqueado"],1,[constantes.CLAVE_USUARIO],[user_r],["and"])
              if(d_user[0][0]=="True"):
                 General.show_message("el usuario esta bloqueado","usuario bloqueado")
                 return
              vent.update_pantallas(constantes.PANTALLA_RECUPERAR_PASSWORD)
              pnl=vent.panelActual
              pnl.get_comp_byName("user").set_text(user_r)
              question=""
              conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
              data_pregs=conexion_bd.get_allData(constantes.CAMPOS_PREGUNTA_SECRETA,len(constantes.CAMPOS_PREGUNTA_SECRETA),[constantes.CLAVE_USUARIO],[user_r],["and"])
              if(data_pregs!=[]):
                 size_p=len(data_pregs)-1
                 import random
                 index=random.randint(0,size_p) 
                 question=data_pregs[index][3]              
              pnl.get_comp_byName("pregunta").set_text(question)
              pnl.get_comp_byName("caja6",False).set_active(False)
              pnl.get_comp_byName("caja7",False).set_active(False)
           else:
              General.show_message("el usuario indicado es inexistente","usuario inexistente")        
        elif(fase==cls.RECOVER_PASS_VERIFY_SECRET_QUESTIONS):
           user_r=pnl.get_comp_byName("user").get_text()
           preg= pnl.get_comp_byName("pregunta").get_text()
           if(preg!="" and preg!=" "):
              res= pnl.get_comp_byName("respuesta").get_text()
              conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
              data_res=conexion_bd.get_allData(constantes.CAMPOS_PREGUNTA_SECRETA,len(constantes.CAMPOS_PREGUNTA_SECRETA),[constantes.CLAVE_USUARIO,"pregunta","respuesta"],[user_r,preg,res],["and","and","and"])
              if(res=="" or res==" "):
                 General.show_message("por favor escriba una respuesta","respuesta invalida")
                 return
              if(data_res!=[]):
                pnl.get_comp_byName("caja6",False).set_active(True)
                pnl.get_comp_byName("caja7",False).set_active(True)
                pnl.get_comp_byName("caja3",False).set_active(False)
                pnl.get_comp_byName("caja5",False).set_active(False)
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
            valor_p1=General.encriptar(valor_p1)
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            conexion_bd.update_data(["password","modificado"],[valor_p1,time_object.get_fecha()],2,[constantes.CLAVE_USUARIO],[user_r],["and"])
            data_intentos=conexion_bd.get_allData([constantes.CLAVE_INTENTOS_USUARIO],1,[constantes.CLAVE_USUARIO],[user_r],["and"])
            conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
            conexion_bd.update_data(["num_intentos","last_fecha","last_hora","modificado"],["0","","",time_object.get_fecha()],4,[constantes.CLAVE_INTENTOS_USUARIO],[data_intentos[0][0]],["and"])
            General.show_message("contraseña cambiada exitosamente","contraseña modificada")
            vent.update_pantallas(constantes.PANTALLA_INICIO)
           
            
             
    #Register the User in User Gestion Panel
    @classmethod
    def registrar_usuario(cls,usr,vent):
       pnl=vent.panelActual
       pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
       valid_admin=False
       if(pass_admin=="" or pass_admin==None):
             return
          
       if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
            p_user=General.desencriptar(usr.get_credentials()[4])     
            if(p_user==pass_admin):
                valid_admin=True        
       if(valid_admin==False):
            General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
            return
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
             if(General.show_confirmDialog("registrar usuario?","registrar")!=True):
               return   
             if( valido==0 ):
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                data_worker=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[data[2]],["and"])
                if(data_worker!=[]):
                  conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                  data_users=conexion_bd.get_allData(constantes.CAMPOS_USUARIO,len(constantes.CAMPOS_USUARIO),[constantes.CLAVE_TRABAJADOR],[data[2]],["and"])
                  if(data_users!=[]):
                      valido=-6 
                  else:
                      conexion_bd.set_tabla(constantes.TABLA_CARGO)
                      cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[data_worker[0][6]],["and"])[0][1].lower()
                      if( cargo.startswith("subdirector") or cargo.startswith("sub director")):
                           cargo="directivo"
                      elif(cargo.startswith("coordinador")):
                           cargo="coordinador"
                      data[3]=cargo
                  
       if(valido==0):
           
           #Register the User
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
                conexion_bd.add_data(data_hist)
                General.show_message("usuario registrado satisfactoriamente","usuario registrado")
           vent.update_pantallas(constantes.PANTALLA_SERVICIO_GESTION_USUARIO)
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
       colors=[]
       items=[]
       title=""
       tipo_data=cls.STADISTICS_NONE
       label_msg=""
       if(filtro=="elejir" or filtro=="elegir"):
            General.show_message("por favor elija un filtro para la grafica","elija un filtro")
            return
       if(opcion=="personal"):
          label_msg="          total de\n trabajadores"
          conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
          data=conexion_bd.get_allData(None,None)
          if(data!=[]):
             if(filtro=="cargo de personal"):
               items=["docente","no docente"]
               colors=["#EE6055","#60D394"]
               tipo_data=cls.STADISTICS_WORKERS_CARGO
               title=filtro
             elif(filtro=="estatus del personal"):
               items=["activo","inactivo","de reposo","posible retiro"]
               colors=["#EE6055","#60D394","#AAF683","#FFD97D"]
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
                  d_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[carg],["and"])
                  if(d_cargo!=[]):
                    if(d_cargo[0][0].lower()=="obrero" or d_cargo[0][0].lower()=="secretaria"):
                       no_docente+=1
                    else:
                       docente+=1
                  conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                  data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[data[i][7]],["and"])
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
          data=conexion_bd.get_allData(None,None)
          label_msg="         total de\n  estudiantes"
          if(data!=[]):
             if(filtro=="tipo de cedula"):
               items=["cedulado","no cedulado"]
               colors=["#EE6055","#60D394",]
               tipo_data=cls.STADISTICS_STUDENTS_ID
               title="tipo de cedula de estudiantes"
             elif(filtro=="estatus del estudiante"):
               items=["activo","inactivos","reposo","graduados","intermit."]
               colors=["#EE6055","#60D394","#AAF683","#FFD97D","#FF9B85"]
               tipo_data=cls.STADISTICS_STUDENT_STATUS
               title=filtro
             elif(filtro=="genero"):
               items=["masculino","femenino"]
               colors=["#EE6055","#60D394"]
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
               data_estatus=conexion_bd.get_allData(["estatus","cedulado"],2,[constantes.CLAVE_ESTATUS_ESTUD],[data[i][2]],["and"])
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
          label_msg="        total de\n  secciones"
          conexion_bd.set_tabla(constantes.TABLA_SECCION)
          data=conexion_bd.get_allData(None,None)
          if(data!=[]):
              if(filtro=="cantidad de secciones segun año de curso" or filtro=="cantidad de secciones"):
                items=["1 año","2 año","3 año","4 año","5 año"]
                colors=["#EE6055","#60D394","#AAF683","#FFD97D","#FF9B85"]
                tipo_data=cls.STADISTICS_SECTIONS_COUNT
                title=filtro
              elif(filtro=="turno"):
                items=["mañana","tarde"]
                colors=["#EE6055","#60D394"]
                tipo_data=cls.STADISTICS_SECTIONS_TURNO
                title="turno de las secciones segun turno"
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
                   data_hor=conexion_bd.get_allData(["turno"],1,[constantes.CLAVE_HORARIO],[data[i][3]],["and"])
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
          data=conexion_bd.get_allData(None,None)
          label_msg="         total de\n  estudiantes"
          if(data!=[]):
              if(filtro=="año"):
                items=["1 año","2 año","3 año","4 año","5 año"]
                colors=["#EE6055","#60D394","#AAF683","#FFD97D","#FF9B85"]
                tipo_data=cls.STADISTICS_MATRICULA_ACADEMIC_YEAR
                title="matricula de estudiantes segun año de curso"
              elif(filtro=="turno"):
                items=["mañana","tarde"]
                colors=["#EE6055","#60D394"]
                tipo_data=cls.STADISTICS_MATRICULA_TURNO
                title="matricula de estudiantes segun turno"
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
                   data_hor=conexion_bd.get_allData(["turno"],1,[constantes.CLAVE_HORARIO],[data[i][3]],["and"])
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
          label_msg="          total de\n  estudiantes"
          conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
          data=conexion_bd.get_allData(None,None)
          if(data!=[]):
              items=["no cursando","cursando"]
              colors=["#EE6055","#60D394"]
              title="materias pendientes en "+filtro
              pendientes=0
              no_pendientes=0
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              for i in range(0,len(data)):
                 ced=data[i][0]
                 pend=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],[ced,filtro],["and","and"])
                 if(pend!=[]):
                    pendientes+=1
                 else:
                    no_pendientes+=1
              valores=[ no_pendientes,pendientes]
       if(len(valores)<=0):
          General.show_message("no hay datos que se puedan mostrar","sin datos para el diagrama")
          return
       from ventana_sec import ventana_secundaria
       sec=ventana_secundaria(vent,[580,500],["white","white"],True,True,[580,450])
       sec.draw_text( [290,250],"Arial","bold",25,"Blue","Cargando por favor espere")
       import threading
       hilo=threading.Thread(target=sec.draw_torta,args=(valores,title,items,colors,label_msg))
       hilo.start()
       
   
                     
    #Remove the Reactivation of an Academic Momentt
    @classmethod
    def reestablecer_momento(cls,usr,vent):
       pnl=vent.panelActual
       combo=pnl.get_comp_byTag("combo")
       time_object=tiempo()
       pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
       valid_admin=False
       if(pass_admin=="" or pass_admin==None):
          return
       if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
             p_user=General.desencriptar(usr.get_credentials()[4])
             if(p_user==pass_admin):
                valid_admin=True                                     
       if(valid_admin==False):
            General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
            return
       if(General.show_confirmDialog("reestablecer momento academico?","reestablecer momento")!=True):
            return
       if(combo.get_selected_value()!="elejir" and combo.get_selected_value()!="elegir"):
          valor=combo.get_selected_value()
          conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
          mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],[valor],["and"])
          if(mom!=[]):
             if(mom[0][2].lower()!="true"):
                General.show_message("el momento academico aun no ha finalizado","momento no finalizado")
                return
             if(mom[0][1].lower()!="true"):
                General.show_message("el momento academico esta cerrado","momento cerrado")
                return
             actual_date=time_object.get_fecha()
             actual_time=time_object.get_tiempo()
             conexion_bd.update_data(["abierto","modificado","fecha_limite","hora_limite"],["false",time_object.get_fecha(),actual_date,actual_time],4,[constantes.CLAVE_MOMENTO],[valor],["and"])           
             usr.add_action_historial(["restablecer momento",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"servicio","reestablecer momento","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist)
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
       pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
       valid_admin=False
       if(pass_admin=="" or pass_admin==None):
          return
          
       if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
             p_user=General.desencriptar(usr.get_credentials()[4])
             if(p_user==pass_admin):
                valid_admin=True  
       if(valid_admin==False):
            General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
            return
       if(General.show_confirmDialog("reactivar momento academico?","reactivar momento")!=True):
            return
            
       if(combo.get_selected_value()!="elejir" and combo.get_selected_value()!="elegir"):
          valor=combo.get_selected_value()
          conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
          mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],[valor],["and"])
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
             conexion_bd.update_data(["abierto","modificado","fecha_limite","hora_limite"],["true",time_object.get_fecha(),nueva_fecha,nuevo_tiempo],4,[constantes.CLAVE_MOMENTO],[valor],["and"])
             usr.add_action_historial(["reactivar momento",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"servicio","reactivar momento","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist)
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
        pass_admin=General.show_password_message("por favor escriba su password","password de administrado")    
        valid_admin=False
        if(pass_admin=="" or pass_admin==None):
           return         
        if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
            p_user=General.desencriptar(usr.get_credentials()[4])
            if(p_user==pass_admin):
                valid_admin=True     
        if(valid_admin==False):
            General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
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
    def organizar_secciones(cls,usr,vent,opcion):
        pnl=vent.panelActual
        id_secc1=pnl.get_comp_byName("accion").get_selected_value()
        id_secc2=pnl.get_comp_byName("intercambio").get_selected_value()
        secc1=pnl.get_comp_byName("secc1")
        secc2=pnl.get_comp_byName("secc2")
        if(id_secc1=="elejir" or id_secc1=="elegir"):
           General.show_message("por favor seleccione una seccion origen valida","seccion invalida")
           return          
        if((id_secc2=="elejir" or id_secc2=="elegir") and opcion!=cls.UPDATE_SECTIONS):
           General.show_message("seleccione una seccion destino valida","seccion destino no valida")        
           return  
        if(opcion==cls.CHANGE_STUDENT_SECTION1_TO_SECTION2):
           estud=pnl.get_comp_byName("estud").get_text()
           if(estud!=""):
              elements=secc1.get_all_values()
              new_vals=[]
              for i in range(0,len(elements)):
                 if(elements[i]!=estud):
                    new_vals.append(elements[i])
              secc1.set_values(new_vals)
              secc2.insert_value(estud)
              pnl.get_comp_byName("estud").set_text("")
              pnl.get_comp_byName("estud_intercambio").set_text("") 
           else:
             General.show_message("por favor elija el estudiante de la seccion origen a mover","estudiante no valido")                       
        elif(opcion==cls.INTERAMBIATE_STUDENTS):
           estud=pnl.get_comp_byName("estud").get_text()
           intercambio=pnl.get_comp_byName("estud_intercambio").get_text()
           if(estud!="" and intercambio!=""):
              elements1=secc1.get_all_values()
              new_vals1=[]
              for i in range(0,len(elements1)):
                 if(elements1[i]!=estud):
                    new_vals1.append(elements1[i])  
              elements2=secc2.get_all_values()
              new_vals2=[]
              for i in range(0,len(elements2)):
                 if(elements2[i]!=intercambio):
                   new_vals2.append(elements2[i])  
              secc1.set_values(new_vals1)
              secc1.insert_value(intercambio)
              secc2.set_values(new_vals2)
              secc2.insert_value(estud)
              pnl.get_comp_byName("estud").set_text("")
              pnl.get_comp_byName("estud_intercambio").set_text("") 
           else:
             General.show_message("por favor elija los estudiantes a intercambiar","estudiantes no validos")        
        elif(opcion==cls.CHANGE_STUDENT_SECTION2_TO_SECTION1):
           estud_i=pnl.get_comp_byName("estud_intercambio").get_text()
           if(estud_i!=""):
              elements=secc2.get_all_values()
              new_vals=[]
              for i in range(0,len(elements)):
                 if(elements[i]!=estud_i):
                    new_vals.append(elements[i])
              secc2.set_values(new_vals)
              secc1.insert_value(estud_i)
              pnl.get_comp_byName("estud").set_text("")
              pnl.get_comp_byName("estud_intercambio").set_text("") 
           else:
             General.show_message("por favor elija el estudiante de la seccion destino a incorporar en la origen","estudiante no valido")        
        elif(opcion==cls.UPDATE_SECTIONS):
              if(General.show_confirmDialog("actualizar seccion?","actualizar seccion")!=True):
                  return
              if(secc2.get_count()<=0 and (id_secc2!="elejir" and id_secc2!="elegir")):
                   General.show_message("debe existir al menos un estudiante en cada seccion","proporcion de estudiantes no valida")              
                   return
              guia= pnl.get_comp_byName("guia").get_selected_value()
              if(guia=="elejir" or guia=="elegir"):
                  General.show_message("por favor elija un profesor guia valido","profesor guia no valido")              
                  return
              data=[id_secc1,secc1.get_all_values(),guia,id_secc2,secc2.get_all_values()]
              usr.organizar_secciones(data)
              secc1_name=id_secc1.split("(")
              if(secc1_name[1].startswith("M")):
                 secc1_name=secc1_name[0]+"(Mañana)"
              else:
                  secc1_name=secc1_name[0]+"(Tarde)"              
              motivo="modificaciones sobre seccion:"+secc1_name
              if(id_secc2!="elejir" and id_secc2!="elegir"):
                 secc2_name=id_secc2.split("(")
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
              conexion_bd.add_data(data_hist)
              General.show_message("secciones actualizadas exitosamente","secciones actualizadas")
              pnl.get_comp_byName("estud").set_text("")
              pnl.get_comp_byName("estud_intercambio").set_text("") 
              pnl.get_comp_byName("accion").set_selected_index(0)
              pnl.get_comp_byName("intercambio").set_selected_index(0)
              pnl.get_comp_byName("guia").set_selected_index(0)
              secc1.set_values([])
              secc2.set_values([])
              
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
        estatus_id=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])[0][0]
        conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
        old_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_ESTUD,len(constantes.CAMPOS_ESTATUS_ESTUD),[constantes.CLAVE_ESTATUS_ESTUD],[estatus_id],["and"])
        cedulado=old_estatus[0][3]
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
                elif(fields[i].get_id()=="fecha"):
                    data_estud[3]=valor
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
        res=estud.is__valid_modific(cedula,cedulado,data_estud,data_repres,data_exp,data_dir)
        if(res[0]==True):
           if(General.show_confirmDialog("modificar estudiante?","modificar estudiante")!=True):
              return
           time_object=tiempo()
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           old_d=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])[0]
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           old_d_r=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[old_d[5]],["and"])[0]
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
              conexion_bd.update_data(["cedulado"],["True"],1,[constantes.CLAVE_ESTATUS_ESTUD],[next_d[2]],["and"])
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              conexion_bd.update_data([constantes.CLAVE_ESTUDIANTE],[next_d[0]],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
              conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
              old_califs=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
              for ic in range(0,len(old_califs)):
                 new_calif=list(old_califs[ic])
                 old_id=new_calif[0]
                 new_calif[0]=next_d[0]+"-"+new_calif[3]+new_calif[2]
                 new_calif[1]=next_d[0]
                 conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                 conexion_bd.add_data(new_calif)
                 conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                 conexion_bd.update_data([constantes.CLAVE_CALIFICACION_FINAL],[new_calif[0]],1,[constantes.CLAVE_CALIFICACION_FINAL],[old_id],["and"])
              conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
              conexion_bd.delete_data([constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              conexion_bd.delete_data([constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
              cedula=next_d[0]
              old_d=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])[0]
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
               conexion_bd.update_data([constantes.CLAVE_REPRESENTANTE],[res[3][0]],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
               resto=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],1,[constantes.CLAVE_REPRESENTANTE],[old_d[5]],["and"])
               if(len(resto)<=0):
                 conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                 conexion_bd.delete_data([constantes.CLAVE_REPRESENTANTE],[old_d[5]],["and"])
           else:
               repres_d=conexion_bd.get_allData([constantes.CLAVE_NOMBRE,constantes.CLAVE_DIRECCION],2,[constantes.CLAVE_REPRESENTANTE],[res[3][0]],["AND"])
               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
               conexion_bd.update_data(["nombre","s_nombre","apellido","s_apellido","modificado"],[res[3][1],res[3][2],res[3][3],res[3][4],time_object.get_fecha()],5,[constantes.CLAVE_NOMBRE],[repres_d[0][0]],["and"])
               conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
               conexion_bd.update_data(["sector","parroquia","casa","modificado"],[res[6][0],res[6][1],res[6][2],time_object.get_fecha()],4,[constantes.CLAVE_DIRECCION],[repres_d[0][1]],["and"])
               conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
               conexion_bd.update_data(["telef","correo","ocupacion","modificado"],[res[3][5],res[3][6],res[3][8],time_object.get_fecha()],4,[constantes.CLAVE_REPRESENTANTE],[res[3][0]],["and"])
               #Exist Modifications Over Representant
               if(res[3][0]!=old_d[5]):
                   conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                   conexion_bd.update_data([constantes.CLAVE_REPRESENTANTE],[res[3][0]],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
                   resto=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],1,[constantes.CLAVE_REPRESENTANTE],[old_d[5]],["and"])
                   if(len(resto)<=0):
                       conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                       conexion_bd.delete_data([constantes.CLAVE_REPRESENTANTE],[old_d[5]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                       conexion_bd.delete_data([constantes.CLAVE_NOMBRE],[old_d_r[1]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                       conexion_bd.delete_data([constantes.CLAVE_DIRECCION],[old_d_r[5]],["and"])
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
           conexion_bd.update_data(["sector","parroquia","casa","modificado"],[next_dir[0],next_dir[1],next_dir[2],time_object.get_fecha()],4,[constantes.CLAVE_DIRECCION],[old_d[8]],["and"])
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
           conexion_bd.update_data(["src_exp","src_foto","modificado"],[res[4][0],res[4][1],time_object.get_fecha()],3,[constantes.CLAVE_EXPEDIENTE],[old_d[4]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           conexion_bd.update_data(["estatus","salud","modificado"],[res[1][9],res[1][10],time_object.get_fecha()],3,[constantes.CLAVE_ESTATUS_ESTUD],[old_d[2]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           conexion_bd.update_data(["nombre","s_nombre","apellido","s_apellido","modificado"],[res[1][1],res[1][2],res[1][3],res[1][4],time_object.get_fecha()],5,[constantes.CLAVE_NOMBRE],[old_d[1]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           fields=["genero","nacimiento","parentesco","modificado"]
           values=[res[1][11],res[1][12],res[3][7],time_object.get_fecha()]
           conexion_bd.update_data(fields,values,len(fields),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
           usr.add_action_historial(["actualizar estudiante",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","estudiante","",time_object.get_fecha()]
           conexion_bd.add_data(data_hist)
           General.show_message("actualizacion del estudiante realizada exitosamnte","estudiante actualizado")
           if(err_upload==True):
               General.show_error("fallo al subir expediente, por favor vuelva a intentarlo","error en expediente")
           vent.update_pantallas(constantes.PANTALLA_WELCOME)
           
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
   