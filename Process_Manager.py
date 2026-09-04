from documento import documento
from tiempo import tiempo
from conexion_bd import conexion_bd
from constantes import constantes
from General import General
import requests
import os
from estudiante import estudiante

class Process_Manager:

    INSCRIPTION_VERIFY_ID=0
    INSCRIPTION_VERIFY_DATA_STUDENT=1
    INSCRIPTION_CONFIRM_INSCRIPTION=2
    INSCRIPTION_NUEVO_INGRESO=0
    INSCRIPTION_REGULAR=1
    INSCRIPTION_UNDEFINED=-1
    RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_GESTION_CALIFICATION=0
    RENDIMIENTO_OPTION_ACCESS_SABANA_AND_CALIFICATIONS_YEAR_PANEL=1
    RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_MATERIA_PENDIENTE=3
    RENDIMIENTO_OPTION_IDENTIFIC_MATERIA_PENDIENTE=4
    RENDIMIENTO_OPTION_IDENTIFIC_GESTION_CALIFICATIONS=5
    RENDIMIENTO_OPTION_PROCESS_MATERIA_PENDIENTE=6
    RENDIMIENTO_OPTION_PROCESS_CALIFICATIONS_TOTAL_REPORT=7
    pendent_registers=[]
    pendent_updates=[]
    pendent_deletes=[]
    data_process={}
    
    #Clear the data Saved On the Active Process of User
    @classmethod
    def clear_data_process(cls):
         cls.data_process={}
       
    #Verify data of Student in Inscription process Is Correct 
    @classmethod    
    def validar_inscripcion(cls,data):
          fields=data[0]
          birthdate_stud=data[1]
          for i in range(0,len(fields)):
              id_f=fields[i].get_id()
              valor=fields[i].get_text()
              if(id_f=="cedula_estud"):
                 continue
              if(id_f=="nombre"):
                  if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                       General.show_message("Por Favor Indique el Nombre del Estudiante Correctamente","Nombre Invalido")
                       return False
                  fullname=valor.split(" ")
                  if(len(fullname)==1):
                       cls.data_process["estudiante"]["nombre"]=fullname[0].lower()
                       cls.data_process["estudiante"]["s_nombre"]=""
                  elif(len(fullname)==2):
                       cls.data_process["estudiante"]["nombre"]=fullname[0].lower()
                       cls.data_process["estudiante"]["s_nombre"]=fullname[1].lower()
                  else:
                       General.show_message("Por Favor Indique Correctamente los Nombres del Estudiante","Nombres Invalido")
                       return False
                             
              elif(id_f=="apellido"):
                  if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                       General.show_message("Por Favor Indique el Apellido del Estudiante Correctamente","Apellido Invalido")
                       return False
                  fullapell=valor.split(" ")
                  if(len(fullapell)==1):
                       cls.data_process["estudiante"]["apellido"]=fullapell[0].lower()
                       cls.data_process["estudiante"]["s_apellido"]=""
                  elif(len(fullapell)==2):
                      cls.data_process["estudiante"]["apellido"]=fullapell[0].lower()
                      cls.data_process["estudiante"]["s_apellido"]=fullapell[1].lower()
                  else:
                      General.show_message("Por Favor Indique Correctamente los Apellidos del Estudiante","Apellidos Invalidos")                 
                      return False
              elif(id_f=="destino_file"):
                    valor_exp=valor
                    if(valor!=""):
                       if(valor.endswith(".rar")==False and valor.endswith(".zip")==False):
                           General.show_message("Por Favor suba el Expediente como un Archivo comprimido ZIP o RAR","formato de expediente Invalido")
                           return False
                       valor_exp=valor
                    else:
                       valor_exp="..."
                    cls.data_process["estudiante"]["expediente_src"]=valor_exp
              elif(id_f=="destino_foto"):
                    valor_foto=valor
                    if(valor!=""):
                       if(valor.endswith(".png")==False and valor.endswith(".jpg")==False and valor.endswith(".jpeg")):
                           General.show_message("Por Favor suba la Foto como un Archivo de Imagen PNG o JPG","formato de foto Invalido")
                           return False
                       valor_foto=valor
                    else:
                       valor_foto="..."
                    cls.data_process["estudiante"]["foto_expediente"]=valor_foto
                     
              elif(id_f=="CIrepres"):
                      temp_v=valor
                      if(temp_v.startswith("v-") or temp_v.startswith("V-") or temp_v.startswith("e-") or temp_v.startswith("E-")):
                         temp_v=valor.split("-")[1]
                      if(General.is_valid(temp_v,constantes.CADENA_SOLONUMERO,False,6)==False):
                          General.show_message("Por Favor Indique una Cedula del Representante Valida","Cedula de Representante Invalida")
                          return False
                      cls.data_process["representante"]["CI_representante"]=valor
              elif(id_f=="telef"):
                      if(General.is_valid(valor,constantes.CADENA_TELEFONO,False)==False):
                         General.show_message("Por Favor Indique un telefono Valido","telefono invalido")
                         return False
                      cls.data_process["representante"]["telefono"]=valor 
              elif(id_f=="nombre_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          General.show_message("Por Favor Indique el Nombre del Representante Correctamente","Nombre de Representante Invalido")
                          return False
                      temp_nomb=valor.split(" ")
                      if(len(temp_nomb)==1):
                          cls.data_process["representante"]["nombre"]=temp_nomb[0].lower()
                          cls.data_process["representante"]["s_nombre"]=""
                      elif(len(temp_nomb)==2):
                           cls.data_process["representante"]["nombre"]=temp_nomb[0].lower()
                           cls.data_process["representante"]["s_nombre"]=temp_nomb[1].lower() 
                      else:
                          General.show_message("Por Favor Indique Los Nombres del Representante Correctamente","Nombre de Representante Invalido")
                          return False
              elif(id_f=="apellido_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          General.show_message("Por Favor Indique el Apellido del Representante Correctamente","Apellido de Representante Invalido")
                          return False
                      temp_apell=valor.split(" ")
                      if(len(temp_apell)==1):
                           cls.data_process["representante"]["apellido"]=temp_apell[0].lower()
                           cls.data_process["representante"]["s_apellido"]=""
                      elif(len(temp_apell)==2):
                          cls.data_process["representante"]["apellido"]=temp_apell[0].lower()
                          cls.data_process["representante"]["s_apellido"]=temp_apell[1].lower()
                      else:
                         General.show_message("Por Favor Indique Los Apellidos del Representante Correctamente","Apellido de Representante Invalido")
                         return False  
              elif(id_f=="direccion"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           General.show_message("Por Favor Indique la Direccion del Estudiante separada por ',' en formato xxx,xxxx,xxx","Direccion Invalida")
                           return False
                       data_d=valor.split(",")
                       cls.data_process["estudiante"]["direccion"]={"sector":data_d[0],"parroquia":data_d[1],"casa":data_d[2]}

              elif(id_f=="correo"):
                       if(General.is_valid(valor,constantes.CADENA_CORREO,False)==False):
                           General.show_message("Por Favor Indique un Correo del Representante Valido","correo Invalido")
                           return False
                       cls.data_process["representante"]["correo"]=valor
              elif(id_f=="dir_representante"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           General.show_message("Por Favor Indique la Direccion del Representante separada por ',' en formato xxx,xxxx,xxx","Direccion Invalida")
                           return False
                       data_d=valor.split(",")
                       cls.data_process["representante"]["direccion"]={"sector":data_d[0],"parroquia":data_d[1],"casa":data_d[2]}

              elif(id_f=="parentesco"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,False)==False):
                          General.show_message("Por Favor Indique un Parentesco del Representante Valido","Parentesco Invalido")
                          return False
                      cls.data_process["estudiante"]["parentesco"]=valor.lower()
              elif(id_f=="plantel"):
                      if(General.is_valid(valor,constantes.CADENA_ALFANUMERICA,True,4)==False):
                         General.show_message("Por Favor Indique el Plantel de Procedencia del Estudiante","Plantel Invalido")
                         return False
                      cls.data_process["estudiante"]["plantel"]=valor    
              elif(id_f=="oficio"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True)==False):
                            General.show_message("Por Favor Indique un Oficio del Representante Valido","Oficio Invalido")
                            return False
                      cls.data_process["representante"]["oficio"]=valor.lower()
          if(General.is_valid(birthdate_stud,constantes.CADENA_FECHA,False)==False):
             General.show_message("Por Favor Indique el Año de Nacimiento del Estudiante","Año de Nacimiento Invalido")
             return False
          cls.data_process["estudiante"]["año_nacimiento"]=birthdate_stud                            
          cls.data_process["estudiante"]["genero"]=data[3]
          cls.data_process["estudiante"]["year_estud"]=data[4]
          cls.data_process["estudiante"]["estatus"]=data[5]
          if(data[2]=="elejir" or data[2]=="elegir"):
             General.show_message("Por Favor Indique el Estado de Salud del Estudiante","Estado de Salud Invalido")
             return False
          cls.data_process["estudiante"]["salud"]=data[2]
          return True
   
    #Verify if the Data for Request Inscription is Valid     
    @classmethod
    def validar_solicit_inscrip(cls,data):
        time_object=tiempo()
        now_date=time_object.get_fecha()
        res={"CI_Estudiante":"","CI_Repres":"","Cedulado":"","Nuevo_Ingreso":""}
        cedula_estud=""
        #Verification Over Student Id
        nacionalidad=""
        if(data["Nacionalidad"].lower()=="venezolano"):
            nacionalidad="V-"
        elif(data["Nacionalidad"].lower()=="extranjero"):
            nacionalidad="E-"
        if(data["Cedulado"]=="Si"):
            #Student with Id
            valor_CI=str(data["CI_Estud"])
            if(General.is_valid(valor_CI,constantes.CADENA_SOLONUMERO,False,6)==False):
               General.show_message("Por Favor Escriba una Cedula Valida","Cedula Invalida")
               return [False,res]
            valor_CI=nacionalidad+valor_CI
            cedula_estud=valor_CI
            res["CI_Estudiante"]=valor_CI
            res["Cedulado"]="True"

        else:
           #estud Without Id
            valor_CI=str(data["CI_Repres"])
            if(valor_CI.startswith("v-") or valor_CI.startswith("V-") or valor_CI.startswith("e-") or valor_CI.startswith("E-")):
               valor_CI=valor_CI.split("-")[1]
            year=data["Año"]
            cedulado=False
            if(General.is_valid(valor_CI,constantes.CADENA_SOLONUMERO,False,6)==False):
               General.show_message("Por Favor Escriba una Cedula del Representante Valida","Cedula Invalida")
               return [False,res]
            elif(General.is_valid(year,constantes.CADENA_YEAR,False)==False):
               General.show_message("Por Favor Escriba un Año de Nacimiento Valido","Año de Nacimiento Invalido")
               return [False,res]
            cedula_estud=nacionalidad+"1"+year[2]+year[3]+valor_CI
            cedula_repres=data["CI_Repres"]
            res["CI_Estudiante"]=cedula_estud
            res["CI_Repres"]=cedula_repres
            res["Cedulado"]="False"
 
        if(data["Inscripcion_Type"]==0):
           #inscription Nuevo Ingreso
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           if(conexion_bd.id_exist(constantes.CLAVE_ESTUDIANTE,cedula_estud)==True ):
              General.show_message("El Estudiante ya esta Inscrito","Estudiante Inscrito")
              return [False,res]
           if((time_object.is_previous(now_date,data["Fecha_end_Nuevo"],False))==True and (time_object.is_previous(data["Fecha_Init_Nuevo"],now_date,False)==True)==False):
              General.show_message("Inscripciones de Nuevo Ingresos Cerrado","Inscripciones Cerradas")
              return [False,res]
           res["Nuevo_Ingreso"]="True"
        else:
           res["Nuevo_Ingreso"]="False"
           #inscription Regular Student
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           if(conexion_bd.id_exist(constantes.CLAVE_ESTUDIANTE,cedula_estud)==False):
              General.show_message("El Estudiante No Esta Registrado","Estudiante No Registrado")
              return [False,res]
           conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"valor"],"condition_Types":["and","and"],"conditions_Values":[cedula_estud,"0"],"conditions_Verify":["=",">"]}              
           data_califs=conexion_bd.get_allData(["valor","año"],cond_data,None,True)
           if(len(data_califs)<=0):
              General.show_error("El Estudiante No se le han Actualizado/Registrado Calificaciones","Estudiante sin Calificaciones")
              return [False,res]
              
           all_aprobadas=True
           have_5_califs=False
           for calific in data_califs:
               if(int(calific["valor"])<10):
                   all_aprobadas=False
               if(calific["año"].startswith("5")):
                   have_5_califs=True
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula_estud],"conditions_Verify":["="]}              
           join_data={}
           join_data["estatus_estud"]={"query_field":["estatus","fecha_inscrip","last_year"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":None}
           data_estatus=conexion_bd.get_allData([],cond_data,join_data,True)
           if(len(data_estatus)<=0):
              General.show_error("Error Obteniendo Datos del Estatus del Estudiante","Error")
              return [False,res]
              
           if(data_estatus[0]["estatus"]=="graduado"):
                General.show_message("El Estudiante ya se ha graduado","Estudiante graduado")
                return [False,res]
           if(all_aprobadas==True):
                 if(have_5_califs==True):
                     join_data["estatus_estud"]={"query_field":{"estatus":"graduado"},"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":None}
                     conexion_bd.update_data([],cond_data,join_data)
                     General.show_message("El Estudiante ya se ha graduado","Estudiante graduado")
                     return [False,res]        
           last_inscrip=data_estatus[0]["fecha_inscrip"]
           if(time_object.is_previous(last_inscrip,data["Fecha_Init_Regular"])==False):
                 General.show_message("el Estudiante ya se ha Inscrito este Año","Estudiante Inscrito")
                 return [False,res]      
           elif((time_object.is_previous(now_date,data["Fecha_End_Regular"],False))==True and (time_object.is_previous(data["Fecha_Init_Regular"],now_date,False)==True)==False):
                 General.show_message("Inscripcion de Estudiantes Regulares Cerradas","inscripciones Cerradas")                 
                 return [False,res]
                
        return [True,res]
    
         
    #Register a New Section
    @classmethod
    def register_seccion(cls,year,turno,max_studs,min_studs):
          time_object=tiempo()
                   
          conexion_bd.set_tabla(constantes.TABLA_SECCION)
          cond_data={"conditions_Names":["año",constantes.CLAVE_SECCION],"condition_Types":["and","and"],"conditions_Values":[year,"default"],"conditions_Verify":["=","!="]}      
          data_year_seccs=conexion_bd.get_allData(["letra"],cond_data,None,True)
          best_letra_code=-1
          best_letra=""
          for secc in data_year_seccs:
              letra_secc=secc["letra"]
              code_letra=ord(letra_secc)
              if(code_letra>best_letra_code):
                  best_letra_code=code_letra
                  best_letra=letra_secc
                  
          if(best_letra==""):
             best_letra="A" 
          else:
             best_letra=chr(best_letra_code+1)
          id_horario=f"HorarioSeccion_{year}-{best_letra}"
          dat_hor={"id_hor":id_horario,"turno":turno,"src_hor":"...","modificado":time_object.get_fecha()}
          id_new_secc=f"{year}-{best_letra}"               
          new_secc_dat={"id_secc":id_new_secc,"año":year,"letra":best_letra,"id_hor":id_horario,"total_estud":"1","maximo_estud":max_studs,"minimo_estud":min_studs,"modificado":time_object.get_fecha()}
          secc_dat={"Action":"Register","data":new_secc_dat,"horario":dat_hor}
          return secc_dat
    
    #Assign Section , Verify Disponibilty of Sections and Build a New Section if is Neccesary
    @classmethod
    def get_seccion(cls,year,turno):
       max_studs="30"
       Maxlimit_int=30
       min_studs="15"
       Minlimit_int=15
       time_object=tiempo()
       join_data={}
       conexion_bd.set_tabla(constantes.TABLA_SECCION)
       fields_require=[constantes.CLAVE_SECCION,"letra","total_estud","maximo_estud","minimo_estud"]
       cond_join={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":["default"],"conditions_Verify":["!="]}        
       join_data["horario"]={"query_field":["turno"],"share_fields":{"field":"id_hor","table_reference":"seccion"},"Conditions_join":cond_join}
       cond_data={"conditions_Names":["año",constantes.CLAVE_SECCION],"condition_Types":["and","and"],"conditions_Values":[year,"default"],"conditions_Verify":["=","!="]}      
       data_seccs=conexion_bd.get_allData(fields_require,cond_data,join_data,True)
       num_seccs=len(data_seccs)
       if(num_seccs<=0):
           return cls.register_seccion(year,turno,max_studs,min_studs)
          
       sections_lowStudents=[]
       sections_availables=[]       
       for secc in data_seccs:
         cant=int(secc["total_estud"])
         if(secc["turno"]==turno and cant<Maxlimit_int):
             sections_availables.append({"Id":secc[constantes.CLAVE_SECCION],"Cant":secc["total_estud"]})
             if(cant<Minlimit_int):
                sections_lowStudents.append({"Id":secc[constantes.CLAVE_SECCION],"Cant":secc["total_estud"]})
       
       if(len(sections_lowStudents)>0): 
           new_cant=int(sections_lowStudents[0]["Cant"])+1 
           id_secc=sections_lowStudents[0]["Id"]
           return {"Action":"Update","data":{"id_secc":id_secc,"new_cant":str(new_cant)},"horario":{}}
       if(len(sections_availables)>0):
           new_cant=int(sections_availables[0]["Cant"])+1 
           id_secc=sections_availables[0]["Id"]
           return {"Action":"Update","data":{"id_secc":id_secc,"new_cant":str(new_cant)},"horario":{}}
       return cls.register_seccion(year,turno,max_studs,min_studs)
       
       
    #Execute the Action Required for Inscription Process
    @classmethod
    def inscribir(cls,usr,vent,type_i,fase):
      pnl=vent.panelActual
      time_object=tiempo()      
      from event_manager import Event_manager
      if(fase==cls.INSCRIPTION_VERIFY_ID):  
        radios=pnl.get_comp_byName("cedulado")
        radios2=pnl.get_comp_byName("nacionalidad")
        data_inscripcionInicial=[]
        valido=0
        cedulado=True
        cedula_estud=""
        cedula_repres=""
        conexion_bd.set_tabla(constantes.TABLA_FORMATO)
        if(conexion_bd.id_exist(constantes.CLAVE_FORMATO,"inscripcion")==False): 
             General.show_error("no hay formato de inscripcion registrado","formato de isncripcion sin registrar")
             return   
        
        hoy=time_object.get_fecha()
        fecha_inscrip=time_object.get_fecha()
        fecha_cierre=time_object.get_fecha()
        fecha_inscrip_nuevo=time_object.get_fecha()
        fecha_cierre_nuevo=time_object.get_fecha()
        #Get Inscriptions Date
        conexion_bd.set_tabla(constantes.TABLA_FECHA)
        fields_fecha=["razon","fecha","fecha_cierre"]
        data_fechas=conexion_bd.get_allData(fields_fecha,None,None,True)
        if(data_fechas==[]):
           General.show_error("cronograma o fechas de Inscripcion no Registradas","Fechas Inscripcion Invalidas")
           return         
        for i in range(0,len(data_fechas)):
           if(data_fechas[i]["razon"]=="inscripcion nuevo ingreso"):
               fecha_inscrip_nuevo=data_fechas[i]["fecha"]
               fecha_cierre_nuevo=data_fechas[i]["fecha_cierre"]
           elif(data_fechas[i]["razon"]=="inscripcion estudiantes regulares"):
               fecha_inscrip=data_fechas[i]["fecha"]
               fecha_cierre=data_fechas[i]["fecha_cierre"]
   
        estud=estudiante()
        data_estud={
            "Inscripcion_Type":type_i,
            "Cedulado":radios.get_selected_value(),
            "CI_Estud":pnl.get_comp_byName("cedula").get_text(),
            "CI_Repres":pnl.get_comp_byName("cedula_repres").get_text(),
            "Año":pnl.get_comp_byName("año").get_text(),
            "Fecha_Init_Regular":fecha_inscrip,
            "Fecha_End_Regular":fecha_cierre,
            "Fecha_Init_Nuevo":fecha_inscrip_nuevo,
            "Fecha_end_Nuevo":fecha_cierre_nuevo,
            "Nacionalidad":radios2.get_selected_value()
        }
        valido=cls.validar_solicit_inscrip(data_estud)
        
        if(valido[0]==True):
          usr.data_expediente=[]
          data_valid=valido[1]
          cls.data_process["estudiante"]={"CI_estudiante":data_valid["CI_Estudiante"],"cedulado":data_valid["Cedulado"]}
          cls.data_process["representante"]={"CI_representante":data_valid["CI_Repres"]}
          cls.data_process["tipo_inscripcion"]=""
          if(type_i==cls.INSCRIPTION_NUEVO_INGRESO):
                cls.data_process["tipo_inscripcion"]="Nuevo Ingreso"
                vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_2,usr)
                Event_manager.set_data_estud(data_valid["CI_Estudiante"],False,data_valid["CI_Repres"])   
          else:
                cls.data_process["tipo_inscripcion"]="Regular"
                vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_3,usr)
                Event_manager.set_data_estud(data_valid["CI_Estudiante"],True,data_valid["CI_Repres"])                           
              
      else:
          if(fase==cls.INSCRIPTION_VERIFY_DATA_STUDENT):
             data_estud=[]
             data_pendiente={"Required":"False","List":[]}
             data_repitiendo={"Required":"False","List":[]}
             data_seccion=[]
             year_curso=""
             turno=pnl.get_comp_byName("turno").get_selected_value()
             if(turno=="elejir" or turno=="elegir"):
                General.show_message("por favor seleccione un turno","turno invalido")
                return
                
             estatus="activo"
             if(cls.data_process["tipo_inscripcion"]!="Regular"):
                year_curso=pnl.get_comp_byName("curso").get_selected_value().split(" ")[0] 
                if(int(year_curso)>1):
                    estatus="irregular"    
             else:
                 estud=estudiante()
                 data_curso=estud.get_data_curso(cls.data_process["estudiante"]["CI_estudiante"])
                 year_curso=data_curso[0]
                 data_pendiente=data_curso[1]
                 data_repitiendo=data_curso[2]
             
             conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION) 
             #Verify Formation Areas 
             for i in range(0,int(year_curso)):
                join_data={}
                join_conds={"conditions_Names":[str(i+1)+"_año"],"condition_Types":["and"],"conditions_Values":["True"],"conditions_Verify":["="]}    
                join_data["años_incorporados"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":join_conds}
                cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":["Si"],"conditions_Verify":["="]}    
                areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],cond_data,join_data,True)
                if(areas==[]):
                    General.show_error("error no existen areas de formacion Disponibles para el Año de Curso Solicitado","sin areas de formacion disponibles")
                    return
                    
              
             data_seccion=cls.get_seccion(year_curso,turno)              
             fields=pnl.get_comps_byTag("field")
             data_estud.append(fields)
             data_estud.append(pnl.get_comp_byName("fecha").get_text())
             data_estud.append(pnl.get_comp_byName("salud").get_selected_value())
             data_estud.append(pnl.get_comp_byName("genero").get_selected_value())
             data_estud.append(year_curso)
             data_estud.append(estatus)
             data_verificada=cls.validar_inscripcion(data_estud)
            
             if(data_verificada==False):
                 conexion_bd.cancel_requests()
                 return
             direct_inscription=False
             if(cls.data_process["tipo_inscripcion"]=="Regular"):
                conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cls.data_process["estudiante"]["CI_estudiante"]],"conditions_Verify":["="]}              
                join_data={} 
                join_data["expediente"]={"query_field":["src_foto"],"share_fields":{"field":"id_exp","table_reference":"estudiante"},"Conditions_join":None}
                join_data["estatus_estud"]={"query_field":["plantel_procedencia"],"share_fields":{"field":"id_est","table_reference":"estudiante"},"Conditions_join":None}
                data_estudReg=conexion_bd.get_allData([],cond_data,join_data,True)
                if(len(data_estudReg)>0):
                   cls.data_process["estudiante"]["foto_expediente"]=data_estudReg[0]["src_foto"]
                   cls.data_process["estudiante"]["plantel"]=data_estudReg[0]["plantel_procedencia"]
                else:
                  cls.data_process["estudiante"]["foto_expediente"]="..."
                  cls.data_process["estudiante"]["plantel"]="..."
                cls.data_process["estudiante"]["expediente_src"]="..."
             if(cls.data_process["tipo_inscripcion"]!="Regular" or (data_pendiente["Required"]=="False" and data_repitiendo["Required"]=="False")):
                  direct_inscription=True
                  if(General.show_confirmDialog("esta seguro que desea inscribir el estudiante","inscribir estudiante")!=True):
                      conexion_bd.cancel_requests()
                      return
             cls.data_process["seccion"]=data_seccion
             id_secc=data_seccion["data"]["id_secc"]
             cls.data_process["materia_pendiente"]=data_pendiente  
             cls.data_process["areas_repitiendo"]=data_repitiendo
             data_areas=[]
             year_area=year_curso+"_año"
             if(direct_inscription==False):
                    vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_4,usr)
                    pnl=vent.panelActual
                    pnl.get_comp_byName("seccion").set_text(f"Seccion Asignada:{id_secc}")
                    if(data_pendiente["Required"]!="False"):
                        temp_pendiente=[]
                        for i in range(0,len(data_pendiente["List"])):
                            temp_pendiente.append(data_pendiente["List"][i][0] +" - "+data_pendiente["List"][i][1]+" año")
                        pnl.get_comp_byName("pendientes").set_values(temp_pendiente)         
                    if(data_repitiendo["Required"]!="False"):
                        temp_repitiendo=[]
                        for rep in range(0,len(data_repitiendo["List"])):
                           temp_repitiendo.append(data_repitiendo["List"][rep])
                        pnl.get_comp_byName("areas").set_values(temp_repitiendo)
             else:  
                 usr_creds=usr.get_credentials()
                 usr_token=usr_creds[4]
                 cls.data_process["usuario"]=usr_token
                 estud=estudiante()
                 if(estud.inscribir(cls.data_process)==False):
                       return
                       
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 if(id_hist=="-1"):
                       General.show_error("Error Generando Reporte","Error de Conexion")
                       return
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","inscripcion","",time_object.get_fecha()]
                 if(conexion_bd.add_data(data_hist,True)<0):
                     return                   
                 conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                 Event_manager.generar_reporte("inscripcion",cls.data_process)
                 usr.add_action_historial(["inscripcion de estudiante",time_object.get_tiempo()])              
                 General.show_message("inscripcion realizada satisfactoriamente","inscripcion finalizada")
                 vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION,usr)
                 cls.clear_data_process()
             
          elif(fase==cls.INSCRIPTION_CONFIRM_INSCRIPTION):
            
            if(General.show_confirmDialog("esta seguro que desea inscribir el estudiante","inscribir estudiante")!=True):
               return
            usr_creds=usr.get_credentials()
            usr_token=usr_creds[4]
            cls.data_process["usuario"]=usr_token   
            estud=estudiante()
            if(estud.inscribir(cls.data_process)==False):
               return
           
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","inscripcion","",time_object.get_fecha()]
            if(conexion_bd.add_data(data_hist,True)<0):
                return                     
            usr.add_action_historial(["inscripcion de estudiante",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            Event_manager.generar_reporte("inscripcion",cls.data_process)                    
            General.show_message("inscripcion realizada satisfactoriamente","inscripcion finalizada")
            vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION,usr)
            cls.clear_data_process()   


    #Determine and execute the Action Required for 'Rendimiento' Process
    @classmethod
    def set_rendimiento(cls,usr,vent,opcion):
        pnl=vent.panelActual
        user_t=usr.get_credentials()[2]
        is_secretaria=False
        
        if(user_t!="admin" and user_t!="coordinador"):
            is_secretaria=True
        if(opcion<=cls.RENDIMIENTO_OPTION_PROCESS_CALIFICATIONS_TOTAL_REPORT):
           cls.verificar_caudicidad(usr,vent)
        
        if(opcion==cls.RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_GESTION_CALIFICATION):
            #gestion de calific 1
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA,usr)
            usr.reset_data_process(0)            
        elif(opcion==cls.RENDIMIENTO_OPTION_ACCESS_SABANA_AND_CALIFICATIONS_YEAR_PANEL):
            #sabana de notas
            if(is_secretaria==False):
                vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_SABANA_NOTAS,usr)
                usr.reset_data_process(0)
            else:
               General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
        elif(opcion==cls.RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_MATERIA_PENDIENTE):
            #materia pendiente 1
            if(is_secretaria==False):
               vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND,usr)
               usr.reset_data_process(0)
            else:
               General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
        elif(opcion==cls.RENDIMIENTO_OPTION_PROCESS_CALIFICATIONS_TOTAL_REPORT):
            #notas finales.
             if(is_secretaria==False):
                 vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF_FINALES,usr)
                 usr.reset_data_process(0)
             else:
                 General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")  
        elif(opcion==cls.RENDIMIENTO_OPTION_IDENTIFIC_MATERIA_PENDIENTE):
            #materia pendiente 2
            data_proces=[]
            ced=pnl.get_comp_byName("cedula_p3").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([],cond_data)==[]):
                General.show_message("cedula del estudiante invalida","cedula invalida")
                return
                
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([],cond_data)==[]):
                General.show_message("estudiante sin materia pendientes","sin materias pendientes")
                return
            
            data_proces.append(ced)
            data_proces.append(pnl.get_comp_byName("area_form").get_selected_value())
            data_proces.append(pnl.get_comp_byName("secciones").get_selected_value())
            data_proces.append(pnl.get_comp_byName("year").get_text())
            data_proces.append(pnl.get_comp_byName("nombre_p3").get_text())
            estud=estudiante()
            valido=estud.verificar_data_rendimiento(data_proces,1)
            if(valido==True):
              usr.recibe_data_process(data_proces)
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_MAT_PEND,usr)
              pnl=vent.panelActual
              pnl.get_comp_byName("area_p4").set_text(data_proces[1])
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data_proces[0],data_proces[1],str(int(data_proces[3])-1)],"conditions_Verify":["=","=","="]}    
              data_pend=conexion_bd.get_allData(["max_calif"],cond_data)
              nota=data_pend[0][0]
              if(len(nota)<2):
                 nota="0"+nota
              pnl.get_comp_byName("best_nota").set_text(nota+" pts")
            else:
                if(valido==-1):
                   General.show_message("estudiante no inscrito","estudiante invalido")
                elif(valido==-2):
                   General.show_message("por favor seleccione un area de formacion","estudiante invalido")
        elif(opcion==cls.RENDIMIENTO_OPTION_IDENTIFIC_GESTION_CALIFICATIONS):
            #gestion de calific 2
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
                return
            ced=pnl.get_comp_byName("cedula_p1").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([],cond_data)==[]):
                General.show_message("cedula del estudiante invalida","cedula invalida")
                return
            data_proces=[]
            data_proces.append(ced)
            data_proces.append(pnl.get_comp_byName("area_form").get_selected_value())
            data_proces.append(pnl.get_comp_byName("mom_p1").get_selected_value())
            data_proces.append(pnl.get_comp_byName("secciones_p1").get_selected_value())
            data_proces.append(pnl.get_comp_byName("year").get_text())
            data_proces.append(pnl.get_comp_byName("nombre_p1").get_text())
            estud=estudiante()
            valido=estud.verificar_data_rendimiento(data_proces,0)
            if(valido==True):
              usr.recibe_data_process(data_proces)
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF,usr)
            else:
               if(valido==-1):
                   General.show_message("estudiante no inscrito","estudiante invalido")
               elif(valido==-2):
                   General.show_message("por favor seleccione un area de formacion","estudiante invalido")
               elif(valido==-3):
                   General.show_message("por favor seleccione un momento academico","momento invalido")
        elif(opcion==cls.RENDIMIENTO_OPTION_PROCESS_MATERIA_PENDIENTE):
             #materia pendiente 3
             estud=estudiante()
             time_object=tiempo()
             data_p=usr.get_data_process()[0]
             intento_val=pnl.get_comp_byName("intento_p4").get_selected_value()
             calif=pnl.get_comp_byName("calif_p4").get_text()
             data_pendiente=[data_p[0],data_p[1],data_p[3],intento_val,calif]
             motivo=pnl.get_comp_byName("motivo").get_text()
             if(motivo=="" or motivo==" "):
                 General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
                 return
             valido=estud.mat_pendiente(data_pendiente,time_object.get_fecha())
             if(valido[0]==True):
                 if(General.show_confirmDialog("esta seguro que desea registrar el intento?","registar intento")!=True):
                     return
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","mat. pendiente",motivo,time_object.get_fecha()]
                 conexion_bd.add_data(data_hist,True)     
                 if(valido[1]==True):
                    General.show_message("materia pendiente del estudiante aprobada existosamente","estudiante aprobado")
                 else:
                    General.show_message("calificacion de materia pendiente o revision registrada satisfactoriamente","registro exitoso de materia pendiente o revision")                 
                 vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND,usr)
                 usr.reset_data_process(0)
             else:
                if(valido[0]==-1):
                   General.show_error("la calificacion del intento de materia pendiente o revision ya se ha registrado","intento de materia pendiente o revision ya registrado")   
                elif(valido[0]==-2):
                   General.show_message("la calificacion debe ser un numero","calificacion no valida")
                elif(valido[0]==-3):                
                   General.show_message("la calificacion debe ser entre 0 y 20","calificacion no valida")
                elif(valido[0]==-4):
                   General.show_error("fecha de materia pendiente no registrada en cronograma","cronograma sin fechas")   
                elif(valido[0]==-5):
                   General.show_message("no se puede registrar el intento el dia de hoy","dia invalido para registro")   
    
    #Determine the Action to exectue from Calification Gestion Panel
    @classmethod
    def interprete_Calification_Gestion_Action(cls,usr,vent):
       pnl=vent.panelActual
       action_comp=pnl.get_comp_byName("Action_List")
       action_str="elegir"
       if(action_comp!=None):
          action_str=action_comp.get_selected_value().lower()
       if(action_str=="elegir"):
          General.show_message("Por Favor Indique una Accion a Realizar","Accion Invalida")
          return
       if("calificacion" in action_str):
          if(action_str=="nueva calificacion"):
             from Register_Manager import Register_Manager
             Register_Manager.registrar_calificacion(usr,vent)             
          elif(action_str=="editar calificacion"):
             cls.update_calification(usr,vent)
          elif(action_str=="borrar calificacion"):
             cls.delete_calification(usr,vent)
       elif(action_str=="establecer estimulacion del area de formacion"):
             cls.estimular_mom(usr,vent)
    
    #Remove a Calification Associated to an Academic Moment
    @classmethod
    def delete_calification(cls,usr,vent):
        pnl=vent.panelActual
        evaluation=""
        tabl_califics=pnl.get_comp_byName("table_califics")
        if(tabl_califics!=None):
           selected_row=tabl_califics.get_row_selectedData()
           if(selected_row!=" "):
             if(len(selected_row)>0):
                 evaluation=selected_row[0]
        motivo=pnl.get_comp_byName("motivo").get_text()
        if(evaluation==""):
             General.show_message("por Indique la Calificacion a Borrar","calificacion invalida")
             return
        if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return  
        time_object=tiempo()
        estud=estudiante()
        temp_dat=usr.get_data_process()[0]
        data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],evaluation]
        if(General.show_confirmDialog("esta seguro que desea borrar esta calificacion?","borrar calificacion")!=True):
            return  
        valido=estud.delete_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           usr.add_action_historial(["borrar calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar calificacion",motivo,time_object.get_fecha()]
           conexion_bd.add_data(data_hist,True)
           
           tabl_califics.reset()
           calificaciones=valido[1]
           for i in range(0,len(calificaciones)):
              tabl_califics.add_row(calificaciones[i])
           prom_data=valido[2]
           cali=str(prom_data[1])
           defi=str(prom_data[3])
           if(len(cali)<2):
               cali="0"+cali
           if(len(defi)<2):
               defi="0"+defi
           pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
           pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+cali+"pts")
           pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
           pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+defi+"pts")
           pnl.get_comp_byName("calific_val").set_text("")
           pnl.get_comp_byName("motivo").set_text("")
           General.show_message("calificacion borrada satisfactoriamente","calificacion borrada")
        else:
          if(valido[0]==-1):
             General.show_message("por favor seleccione la calificacion a borrar","numero de evaluacion no valido")
   
    #Modify the Calification Associated to an Academic Moment  
    @classmethod
    def update_calification(cls,usr,vent):
        pnl=vent.panelActual
        evaluation=""
        tabl_califics=pnl.get_comp_byName("table_califics")
        if(tabl_califics!=None):
           selected_row=tabl_califics.get_row_selectedData()
           if(selected_row!=" "):
             if(len(selected_row)>0):
                 evaluation=selected_row[0]
        motivo=pnl.get_comp_byName("motivo").get_text()
        if(evaluation==""):
             General.show_message("por Indique la Calificacion a Modificar","calificacion invalida")
             return      
        if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return
        if(General.show_confirmDialog("esta seguro que desea modificar esta calificacion?","modificar calificacion")!=True):
            return
        calific_comp=pnl.get_comp_byName("calific_val")
        next_calific=""
        if(calific_comp!=None):
           next_calific=calific_comp.get_text()
        time_object=tiempo()
        estud=estudiante()
        temp_dat=usr.get_data_process()[0]
        data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],evaluation,next_calific]
        valido=estud.modific_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar calificacion",motivo,time_object.get_fecha()]
           conexion_bd.add_data(data_hist,True) 
           tabl_califics.reset()
           calificaciones=valido[1]
           for i in range(0,len(calificaciones)):
               tabl_califics.add_row(calificaciones[i])
           prom_data=valido[2]
           cali=str(prom_data[1])
           defi=str(prom_data[3])
           if(len(defi)<2):
             defi="0"+defi
           if(len(cali)<2):
              cali="0"+cali
           pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
           pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+cali+"pts")
           pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
           pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+defi+"pts")
           calific_comp.set_text("")
           pnl.get_comp_byName("motivo").set_text("")
           General.show_message("calificacion modificada exitosamente","calificacion modificada")
        else:
           if(valido[0]==-1):
              General.show_message("por favor seleccione la calificacion a modificar","numero de evaluacion no valido")
           elif(valido[0]==-2):
              General.show_message("por favor escriba un valor valido para la calificacion","calificacion valida")
     
           elif(valido[0]==-3):
              General.show_message("la calificacion debe ser un numero entre 0 y 20","calificacion valida")
    
    #Assign Estimulation Points Associated to an Academic Moment
    @classmethod
    def estimular_mom(cls,usr,vent):
         pnl=vent.panelActual
         motivo=pnl.get_comp_byName("motivo").get_text()
         if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return
         estimuñ_prom_field=pnl.get_comp_byName("estimul_prom")
         estimul_areas_field=pnl.get_comp_byName("estimul_areas")
         time_object=tiempo()
         estud=estudiante()
         temp_dat=usr.get_data_process()[0]
         data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],estimuñ_prom_field.get_text(),estimul_areas_field.get_text()]
         valido=estud.estimular_area(data_estud,time_object.get_fecha())
         if(valido[0]==True):
            usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","calificacion estimulada",motivo,time_object.get_fecha()]
            conexion_bd.add_data(data_hist,True)
            estimuñ_prom_field.set_text("")
            estimul_areas_field.set_text("")  
            prom_data=valido[1]
            pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
            pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+str(prom_data[1])+"pts")
            pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
            pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+str(prom_data[3])+"pts")
            pnl.get_comp_byName("motivo").set_text("")
            General.show_message("area de formacion estimulada satisfactoriamente","area de formacion estimulada")
         else:
            if(valido[0]==-1):
               General.show_message("por favor escriba una cantidad de puntos valida","puntos de estimulacion invalidos")
            elif(valido[0]==-2):
               General.show_message("error, no se ha registrado hasta el momento ninguna calificaciones en ninguna area de formacion del momento academico seleccionado","area de formacion sin calificaciones")
            elif(valido[0]==-3):
               General.show_message("hasta el momento no se ha registrado ninguna calificacion en esta area de formacion","calificacion de area de formacion no existente")
            elif(valido[0]==-4):
                General.show_message("los puntos a estimular deben ser entre 1 y 2","puntos de estimulacion invalidos")
            elif(valido[0]==-5):
               General.show_message("no quedan puntos disponibles para estimular","puntos de estimulacion excedidos")
            elif(valido[0]==-6):
              General.show_message("el puntaje del area es demasiado alto para la cantidad de puntos de estimulacion","demasiados puntos de estimulacion")
            elif(valido[0]==-7):
              General.show_message("solo se puede aplicar un punto por cada razon de estimulacion","demasiados puntos de estimulacion")
                
    
    #process definitvecalification gestion Panel : Generate report or Set the Calification of Students from Another Institutes
    @classmethod
    def process_definitve_calification_gestion(cls,usr,vent):
       pnl=vent.panelActual
       action_comp=pnl.get_comp_byName("action_list")
       if(action_comp!=None):
          action_value=action_comp.get_selected_value()
          if(action_value=="Elegir"):
             General.show_message("Por Favor Indique la Accion a Realizar","Accion Invalida")
             return
          elif(action_value=="Generar Reporte de Notas"):
              from Consult_Manager import Consult_Manager
              Consult_Manager.generar_reporte(pnl,"notas finales",usr)
              return
      
       field_ced=pnl.get_comp_byName("cedula_estudiante")
       nacionaliad_comp=pnl.get_comp_byName("nacionalidad")
       cedula_estud=""
       if(field_ced!=None and nacionaliad_comp!=None):
          nacionalidad_value=nacionaliad_comp.get_selected_value()
          if(nacionalidad_value.lower()=="venezolano"):
              cedula_estud=f"V-{field_ced.get_text()}"
          else:
             cedula_estud=f"E-{field_ced.get_text()}"
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula_estud],"conditions_Verify":["="]}        
       data_estud=conexion_bd.get_allData([],cond_data)
       area=pnl.get_comp_byName("area").get_text()
       year=pnl.get_comp_byName("year").get_text()
       tabla=pnl.get_comp_byName("table_califics")
       old_calif=tabla.get_row_selectedData()
       if(old_calif==" "):
         General.show_message("por favor seleccione una calificacion de la lista","calificacion no seleccionada")
         return
         
       new_calif=pnl.get_comp_byName("calif").get_text() 
       time_object=tiempo()
       estud=estudiante()
       valido=estud.modific_calif_final([cedula_estud,area,year,old_calif,new_calif],time_object.get_fecha())        
       if(valido>=0):
           flds=pnl.get_comps_byTag("field")
           for fl in flds:
              if(fl.get_id()=="area" or fl.get_id()=="year" or fl.get_id()=="calif"):
                  fl.set_text("")
           tabla.reset()
           conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula_estud],"conditions_Verify":["="]}      
           data_calif=conexion_bd.get_allData([],cond_data)
           for i in range(0,len(data_calif)):
              tabla.add_row([data_calif[i][3],data_calif[i][2],data_calif[i][4]])
           if(valido==1):
              General.show_message("registro de calificacion pendientes del estudiante finalizado ","registro finalizado")
           else:
              #registramos historial 
              usr.add_action_historial(["modificacion de calificacion final",time_object.get_tiempo()])
              conexion_bd.set_tabla(constantes.TABLA_REPORTE)
              id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
              data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar calificacion final","actualizar notas faltantes del estudiante provenientes de otra institucion",time_object.get_fecha()]
              conexion_bd.add_data(data_hist,True)
              General.show_message("calificacion final modificada exitosamente","calificacion final modificada")
       else:
         if(valido==-1):
           General.show_message("cedula del estudiante no registrada","cedula invalida")
         elif(valido==-2):
           General.show_error("no se puede cambiar esta calificacion","calificaciones inmodificable")
         elif(valido==-3):
            General.show_message("por favor seleccione una calificacion de la lista","calificacion invalida")
         elif(valido==-4):
           General.show_error("la calificacion no es modificable","calificacion inmodificable")
         elif(valido==-5):
             General.show_message("la nueva calificacion debe ser un numero","nueva calificacion invalida")
         elif(valido==-6):
            General.show_message("el valor de la calificacion debe ser entre 0 y 20","nueva calificacion invalida")
    
    #Generate the Document 'Sabana de Notas'
    @classmethod
    def generate_sabana_notas(cls,usr,vent,con_notas=False):
       pnl=vent.panelActual
       valido=0 
       field=pnl.get_comp_byName("letra_p5")
       combo=pnl.get_comp_byName("year_p5")
       time_object=tiempo()
       letra=field.get_text()
       year=combo.get_selected_value()
       turno=pnl.get_comp_byName("turno").get_selected_value()
       if(year=="elejir" or year=="elegir"):
           valido=-1
       if(valido==0):  
         if(turno=="elejir" or turno=="elegir"):
             valido=-3       
         elif(General.is_valid(letra,constantes.CADENA_SOLOTEXTO,False,0)==False):
             valido=-2
         elif(len(letra)>1):
             valido=-2
       if(valido==0):
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            id_secc=year[0]+"-"+letra
            cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[id_secc],"conditions_Verify":["="]}      
            data_secc=conexion_bd.get_allData([],cond_data)
            if(data_secc!=[]):
                conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                data_areas=[]
                cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":["Si"],"conditions_Verify":["="]}    
                data_areas_temp=conexion_bd.get_allData([],cond_data)
                conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                for ar in data_areas_temp:
                   id_years=ar[2]
                   field_in=year[0]+"_año"
                   cond_data={"conditions_Names":[constantes.CLAVE_AÑOS_INCORPORADOS,field_in],"condition_Types":["and","and"],"conditions_Values":[id_years,"True"],"conditions_Verify":["=","="]}    
                   data_years=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],cond_data)
                   if(data_years!=[]):
                       data_areas.append(ar[0])
                if(data_areas!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                    cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[data_secc[0][0]],"conditions_Verify":["="]}    
                    data_estuds=conexion_bd.get_allData([],cond_data)
                    orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","historia","fsn","ov","gcrp"]     
                    areas_list=[]                
                    for j in range(0,len(orden)):
                       for k in range(0,len(data_areas)):
                            if(data_areas[k].lower()==orden[j]):
                                 area=data_areas[k]
                                 areas_list.append(area)
                    if(data_estuds!=[]):
                        nombres=[]
                        for i in range(0,len(data_estuds)):
                            conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                            cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[data_estuds[i][2]],"conditions_Verify":["="]}                    
                            data_estatus=conexion_bd.get_allData(["estatus"],cond_data)
                            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                            cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[data_estuds[i][1]],"conditions_Verify":["="]}    
                            data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],cond_data)
                            if(data_estatus[0][0]!="inactivo" and data_estatus[0][0]!="graduado" ):
                                fullname=""
                                for name_index in range(0,len(data_nombre[0])):
                                    if(name_index==0):
                                        fullname=data_nombre[0][name_index]
                                    else:
                                        if(data_nombre[0][name_index]!="" and data_nombre[0][name_index]!="..."):
                                            fullname=fullname+" "+data_nombre[0][name_index]
                                
                                temp_data=[data_estuds[i][0],fullname]
                                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                                for temp_area in areas_list:
                                    cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data_estuds[i][0],temp_area,year[0]],"conditions_Verify":["=","=","="]}    
                                    calif=conexion_bd.get_allData(["valor"],cond_data) 
                                    if(calif!=[]):
                                        if(con_notas):
                                             temp_data.append(calif[0][0])
                                    else:
                                        if(con_notas):
                                             temp_data.append("01")
                                        id_next_calif=data_estuds[i][0]+"-"+temp_area+year[0]
                                        data_next_calif=[id_next_calif,data_estuds[i][0],year[0],temp_area,"05",time_object.get_fecha()]
                                        conexion_bd.add_data(data_next_calif,True)
                                        
                                nombres.append(temp_data)  
                        dat=[nombres,areas_list,year[0]+"-"+letra,year[0]]                        
                        if(dat[0]!=[]):
                          from event_manager import Event_manager
                          if(con_notas==False):
                              Event_manager.generar_reporte("sabana de notas",dat)
                          else:
                              Event_manager.generar_reporte("notas finales del año",dat)   
                        else:
                          General.show_message("la seccion no tiene estudiantes activos","seccion sin estudiantes activos")                           
 
                    else:
                        General.show_message("no hay estudiantes registrados en la seccion","seccion sin estudiantes")
                else:
                    General.show_message("no hay areas de formacion registradas para el año indicado","areas de formacion no registradas")
       
            else:
               General.show_message("la seccion indicada no esta registrada","seccion no valida")
           
       else:
            if(valido==-1):
                General.show_message("por favor seleccione un año de curso","año invalido")
            elif(valido==-2):
                General.show_message("por favor escriba una letra de seccion valida"," letra de seccion invalida")
            elif(valido==-3):
                General.show_message("por efavor elija un turno","turno invalido")
                   
    #Validate the Cronogram Values For Planification process
    @classmethod
    def verify_cronogram(cls,usr,vent,parte):
        pnl=vent.panelActual
        fields=pnl.get_comps_byTag("date")
        data_send=[] 
        razones_send=[]        
        time_object=tiempo()
        if(parte=="general"):
            pair=[]
            pair_razon=[]
            for i in range(0,len(fields)):
               id_f=fields[i].get_id()
               if(id_f!="inicio" and id_f!="cierre"):
                  pair.append(fields[i].get_text())
                  pair_razon.append(fields[i].get_id())
                  if(i>=8):
                    pair.append(pair[0])
                    pair_razon.append("cierre "+fields[i].get_id())
                  if(len(pair)==2):
                     strict=True
                     if(i>=8):
                       strict=False
                     pair.append(strict)      
                     data_send.append(pair)
                     razones_send.append(pair_razon)
                     pair_razon=[]
                     pair=[]  
        elif(parte=="mat pendiente"):
            pair=[]
            pair_razon=[]
            for i in range(0,len(fields)):
                pair.append(fields[i].get_text())
                pair.append(fields[i].get_text())
                pair.append(False)
                data_send.append(pair)
                pair_razon.append(fields[i].get_id())
                pair_razon.append("cierre "+fields[i].get_id())
                razones_send.append(pair_razon)
                pair_razon=[]
                pair=[]
        elif(parte.startswith("momento")):
            pair=[]
            pair_razon=[]
            numero=int(parte[len(parte)-1])
            limite_double=0
            if(numero==1):
               limite_double=8
            elif(numero==2):
               limite_double=6
            elif(numero==3):
               limite_double=4
            for i in range(0,len(fields)):
               pair.append(fields[i].get_text())
               pair_razon.append(fields[i].get_id())
               if(i>=limite_double):
                  valor_p=pair[0]
                  if(pair_razon[0]=="consejo de curso"):
                      valor_p=time_object.get_next_date2(valor_p,1)
                  pair.append(valor_p)
                  pair_razon.append("cierre "+fields[i].get_id())
               if(len(pair)==2):
                     strict=True
                     if(i>=limite_double):
                       strict=False
                     pair.append(strict)
                     data_send.append(pair)
                     razones_send.append(pair_razon)
                     pair_razon=[]
                     pair=[]
   
        val=usr.validar_cronograma(data_send)
        if(val==True):
             if(General.show_confirmDialog("modificar el cronograma?","modificar crongrama")!=True):
                return
             conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
             dat_cronog=conexion_bd.get_allData([])
             if(parte=="mat pendiente"):
                 conexion_bd.set_tabla(constantes.TABLA_FECHA)
                 for i in range(0,len(data_send)):                     
                     data_send[i][1]=time_object.get_next_date2(data_send[i][1],4)
                     data_fecha=[dat_cronog[0][0]+"-momento1-"+razones_send[i][0],"momento 1",dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]
                     if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                         conexion_bd.add_data(data_fecha)
                     else:
                        cond_data={"conditions_Names":[constantes.CLAVE_FECHA],"condition_Types":["and"],"conditions_Values":[data_fecha[0]],"conditions_Verify":["="]}    
                        conexion_bd.update_data({"fecha":data_fecha[4],"fecha_cierre":data_fecha[5],"modificado":time_object.get_fecha()},cond_data) 
             elif(parte=="general"):
                   conexion_bd.set_tabla(constantes.TABLA_FECHA)
                   for i in range(0,len(data_send)):
                      data_fecha=[dat_cronog[0][0]+"-momento 1-"+razones_send[i][0],"momento 1",dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]           
                      if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                         conexion_bd.add_data(data_fecha)
                      else:
                        cond_data={"conditions_Names":[constantes.CLAVE_FECHA],"condition_Types":["and"],"conditions_Values":[data_fecha[0]],"conditions_Verify":["="]}    
                        conexion_bd.update_data({"fecha":data_fecha[4],"fecha_cierre":data_fecha[5],"modificado":time_object.get_fecha()},cond_data)    
             elif(parte.startswith("momento")):
                   mom="momento 1"
                   momento_new_data=[]
                   if(parte!=mom):
                      mom=parte
                      conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                      #Build Academic Moment if not Exist 
                      if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,mom)==False):
                          abierto="false"
                          cerrado="false"
                          if(mom=="momento 2"):
                              cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 1"],"conditions_Verify":["="]}    
                              data_mom1=conexion_bd.get_allData([],cond_data)
                              if(data_mom1[0][2]=="true"):
                                 abierto="true"
                          elif(mom=="momento 3"):
                              cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 2"],"conditions_Verify":["="]}    
                              data_mom2=conexion_bd.get_allData([],cond_data)
                              if(data_mom2[0][2]=="true"):
                                 abierto="true"   
                          momento_new_data=[mom,abierto,cerrado,time_object.get_fecha(),"","",""]
                   for i in range(0,len(data_send)):
                      if(razones_send[i][0]=="inicio" ):
                         razones_send[i][0]="periodo"
                         conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                         if(momento_new_data!=[]):
                             momento_new_data[4]=data_send[i][1]
                             momento_new_data[5]="00:00:00"
                             momento_new_data[6]=data_send[i][0]
                             conexion_bd.add_data(momento_new_data)
                         else:
                             cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[mom],"conditions_Verify":["="]}    
                             conexion_bd.update_data({"fecha_limite":data_send[i][1],"hora_limite":"00:00:00","fecha_inicio":data_send[i][0],"modificado":time_object.get_fecha()},cond_data)
                      else:
                          conexion_bd.set_tabla(constantes.TABLA_FECHA)   
                          data_fecha=[dat_cronog[0][0]+"-"+mom+"-"+razones_send[i][0],mom,dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]           
                          if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                             conexion_bd.add_data(data_fecha)
                          else:
                            cond_data={"conditions_Names":[constantes.CLAVE_FECHA],"condition_Types":["and"],"conditions_Values":[data_fecha[0]],"conditions_Verify":["="]}    
                            conexion_bd.update_data({"fecha":data_fecha[4],"fecha_cierre":data_fecha[5],"modificado":data_fecha[6]},cond_data)             
             usr.add_action_historial(["editar cronograma",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","editar cronograma","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True) 
             General.show_message("cronograma actualizado exitosamente","cronograma actualizado") 
             usr.reset_data_process(0)
             vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1,usr)
             cls.show_planificar_cronogOption(usr,vent,True)
            
        else:
           if(val==-1):
              General.show_message("error de datos del cronograma","error")
           elif(val==-2 or val==-3):
               General.show_message("las fechas debene escribirse en el formato: xx/xx/xxxx ","fecha invalida")
           elif(val==-4):
              General.show_message("las fechas de cierre deben ser posteriores a las de inicio ","fechas de cierre invalidas")
           elif(val==-5):
              General.show_message("las fechas debe ser superior a la fecha de inicio del cronograma","fechas invalidas")
    
    #Interprete the the Action  in  Cronogram Planification
    @classmethod
    def set_cronogram(cls,usr,vent):
        pnl=vent.panelActual
        if((usr.get_credentials()[2]!="coordinador" and usr.get_credentials()[2]!="admin")==True):
            General.show_error("acceso invalido para el usuario","usuario sin permiso")
            vent.update_pantallas(constantes.PANTALLA_WELCOME,usr)
            usr.reset_data_process(0)
            return
        time_object=tiempo()
        accion=pnl.get_comp_byName("acciones").get_selected_value()
        if(accion=="elejir" or accion=="elegir"):
           General.show_message("por favor seleccione una accion","accion invalida")
           return
        if(accion=="crear cronograma" or accion=="editar cronograma"):
           inicio=pnl.get_comp_byName("inicio").get_text()
           cierre=pnl.get_comp_byName("cierre").get_text()
           periodo=pnl.get_comp_byName("año_escolar").get_text()
           valido=usr.is_validYear(periodo,inicio,cierre)
           if(valido==True):
             if(accion=="crear cronograma"):    
                 if(General.show_confirmDialog("registrar el cronograma indicado?","registrar cronograma")!=True):
                      return
                 data_cronog=[periodo,inicio,cierre,time_object.get_fecha()]
                 conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                 conexion_bd.add_data(data_cronog)
                 conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                 data_mom=["momento 1","true","false",time_object.get_fecha(),"","",""]
                 conexion_bd.add_data(data_mom)
                 usr.add_action_historial(["registrar cronograma",time_object.get_fecha()])
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","crear cronograma","",time_object.get_fecha()]
                 conexion_bd.add_data(data_hist,True) 
                 General.show_message("cronograma registrado satisfactoriamente","cronograma registrado")
             else:
                 #Crongram Update
                 if(General.show_confirmDialog("actualizar el cronograma indicado?","registrar cronograma")!=True):
                      return
                 cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[periodo],"conditions_Verify":["="]}    
                     
                 conexion_bd.update_data({"inicio":inicio,"cierre":cierre,"modificado":time_object.get_fecha()},cond_data)
                 usr.add_action_historial(["modificar cronograma",time_object.get_fecha()])
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar cronograma","",time_object.get_fecha()]
                 conexion_bd.add_data(data_hist,True) 
                 General.show_message("cronograma actualizado satisfactoriamente","cronograma registrado")
             cls.show_planificar_cronogOption(usr,vent,True)
           else:
              if(valido==-1):
                 General.show_message("periodo del año escolar invalido","año escolar invalido")
              elif(valido==-2):
                  General.show_message("fechas de inicio o cierre invalidas","inicio y cierre no validos")
              elif(valido==-3):
                  General.show_message("la fecha de cierre debe ser posterior a la de inicio","inicio y cierre no validos")
              elif(valido==-4):
                  General.show_message("el cronograma del año escolar empieza en septiembre","mes de inicio no valido")
           
        elif(accion=="descargar cronograma"):
              from event_manager import Event_manager
              Event_manager.generar_reporte("cronograma")   
        elif(accion=="eliminar cronograma"):
             last_moment_close=False
             conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
             mom_dat=conexion_bd.get_allData([])
             if(mom_dat!=[]):
               for i in range(0,len(mom_dat)):
                  if(mom_dat[i][0]=="momento 3"):
                      if(mom_dat[i][2]=="true"):
                             last_moment_close=True      
               if(last_moment_close==False):
                 conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                 if(conexion_bd.get_allData([])!=[]):
                    General.show_error("no se puede eliminar el cronograma","cronograma no borrable")
                    return   
             conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
             id_cronog=pnl.get_comp_byName("año_escolar").get_text()
             cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[id_cronog],"conditions_Verify":["="]}    
             data_cronog=conexion_bd.get_allData([],cond_data)
             max_date=time_object.get_next_date2(data_cronog[0][1],4)
             if(time_object.is_previous(time_object.get_fecha(),max_date)==False and last_moment_close==False):
                if(time_object.is_previous(time_object.get_fecha(),data_cronog[0][2])):
                    General.show_error("no se puede eliminar el cronograma","cronograma no borrable")
                    return
             if(General.show_confirmDialog("esta seguro que desea borrar el cronograma?","borrar cronograma")!=True):
                 return
             cls.reset_cronogram(usr,vent,id_cronog,last_moment_close)
             usr.add_action_historial(["borrar cronograma",time_object.get_fecha()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar cronograma","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True) 
             General.show_message("cronograma borrado exitosamente","cronograma borrado")
             cls.show_planificar_cronogOption(usr,vent,True)         
             pnl.get_comp_byName("acciones").set_selected_index(0)

        else:
           if(accion.startswith("editar fechas: momento")):
              mom=""
              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
              cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 1"],"conditions_Verify":["="]}    
              dat_mom=conexion_bd.get_allData([],cond_data)
              if(dat_mom!=[]):
                  if(accion=="editar fechas: momento1"):
                     mom="momento 1"
                     if(dat_mom[0][2]=="false"):
                       vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG4,usr)
                       if(dat_mom[0][6]=="" or dat_mom[0][6]==" "):
                           pnl=vent.panelActual
                           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                           d_crong=conexion_bd.get_allData([])
                           if(d_crong!=[]):
                              inicio_c=d_crong[0][1].split("/")
                              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                              pnl.get_comp_byName("inicio").set_text(str(inicio_c[0])+"/"+str(inicio_c[1])+"/"+str(inicio_c[2]))
                     else:
                        General.show_message("el momento academico ya ha culminado","cronograma de momento no modificable")
                        return  
                  elif(accion=="editar fechas: momento 2"):
                      mom="momento 2"
                      cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 2"],"conditions_Verify":["="]}    
                      dat_mom=conexion_bd.get_allData([],cond_data)
                      if(dat_mom!=[]):
                         if(dat_mom[0][2]=="false"):
                            vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG5,usr)
                         else:
                           General.show_message("el segundo momento academico ya ha culminado","cronograma de momento no modificable")
                           return
                      else:
                         vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG5,usr)    
                  elif(accion=="editar fechas: momento 3"):
                      mom="momento 3"
                      cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 2"],"conditions_Verify":["="]}    
                      dat_mom=conexion_bd.get_allData([],cond_data)
                      if(dat_mom!=[]):
                            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento 3"],"conditions_Verify":["="]}    
                            dat_mom=conexion_bd.get_allData([],cond_data)
                            if(dat_mom!=[]):
                                if(dat_mom[0][2]=="false"):
                                     vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG6,usr)
                                else:
                                    General.show_message("el tercer momento  academico ya ha culminado ","cronograma de momento no modificable")
                                    return
                            else:
                               vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG6,usr)
                      else:
                          General.show_message("el cronograma del momento 2 aun no se ha iniciado","cronograma de momento no modificable")
                          return
              else:
                General.show_error("error en el registro de momentos del cronograma","error inesperado")
                return

              pnl=vent.panelActual  
              inicio=pnl.get_comp_byName("inicio")
              cierre=pnl.get_comp_byName("cierre")
              inicio.set_state("normal")
              cierre.set_state("normal")
              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
              if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,mom)):
                  conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                  cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[mom],"conditions_Verify":["="]}    
                  data_mom=conexion_bd.get_allData(["fecha_inicio","fecha_limite","abierto","culminado"],cond_data)
                  conexion_bd.set_tabla(constantes.TABLA_FECHA)
                  razones=["evaluacion continua","entrega de planificaciones a subdireccion academica","entrega de calificacion a departamento de evaluacion","asueto de navidad","consejo de curso","consejo de docentes","reunion de representantes","cierre pedagogico","entrega de boletas a representantes","semana aniversario","misa graduandos","acto de grado","asueto de carnaval"]
                  double_fields=[True,False,False,True,False,False,False,False,False,True,False,False,True]
                  if(data_mom!=[]):
                    if(data_mom[0][0]!="" and  data_mom[0][1]!=""):
                        #If Academic is not at End or is Open  it can Modify Date of End
                        if(data_mom[0][2]=="false" and data_mom[0][3]=="false" ):
                           inicio.set_state("normal")
                        else:
                           inicio.set_state("readonly")
                        if(data_mom[0][3]=="false"):
                            cierre.set_state("normal")
                        else:
                            cierre.set_state("readonly")
                        inicio.set_text(data_mom[0][0])
                        cierre.set_text(data_mom[0][1])
                  for i in range(0,len(razones)):
                    cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO,"razon"],"condition_Types":["and","and"],"conditions_Values":[mom,razones[i]],"conditions_Verify":["=","="]}    
                    data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data)
                    if(data_t!=[]):
                       comp=pnl.get_comp_byName(razones[i])
                       comp.set_text(data_t[0][0])
                       if(double_fields[i]==True):
                         comp_s=pnl.get_comp_byName("cierre "+razones[i])
                         comp_s.set_text(data_t[0][1])
           else:
           
             if(accion=="editar fechas: materia pend."):
                vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG3,usr)
                conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                dat_cronog=conexion_bd.get_allData([])
                pnl=vent.panelActual 
                conexion_bd.set_tabla(constantes.TABLA_FECHA)
                razones=["materia pendiente 1","materia pendiente 2","materia pendiente 3","materia pendiente 4","revision"]
                for i in range(0,len(razones)):
                  cond_data={"conditions_Names":["razon"],"condition_Types":["and"],"conditions_Values":[razones[i]],"conditions_Verify":["="]}    
                  data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data)
                  if(data_t!=[]):
                      comp= pnl.get_comp_byName(razones[i])
                      comp.set_text(data_t[0][0])
             elif(accion=="editar fechas: inscripcion"):
                vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG2,usr)
                conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                dat_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"inicio","cierre"])
                pnl=vent.panelActual   
                pnl.get_comp_byName("inicio").set_text(dat_cronog[0][1])
                pnl.get_comp_byName("cierre").set_text(dat_cronog[0][2])
                conexion_bd.set_tabla(constantes.TABLA_FECHA)
                razones=["inscripcion nuevo ingreso","inscripcion estudiantes regulares"]
                doble_field=[True,True]
                for i in range(0,len(razones)):
                  cond_data={"conditions_Names":["razon"],"condition_Types":["and"],"conditions_Values":[razones[i]],"conditions_Verify":["="]}    
                  data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data)
                  if(data_t!=[]):
                      comp= pnl.get_comp_byName(razones[i])
                      comp.set_text(data_t[0][0])
                      if(doble_field[i]==True):
                         comp_s= pnl.get_comp_byName("cierre "+razones[i])
                         comp_s.set_text(data_t[0][1])
    
   
    
    #Show the Available Options for the Planification of Cronogram
    @classmethod
    def show_planificar_cronogOption(cls,usr,vent,autollamado=False):
        pnl=vent.panelActual
        pnl_index=vent.panelActual_str
        time_object=tiempo()
        if(autollamado==True):
            accion_actual=pnl.get_comp_byName("acciones").get_selected_value()
            if( pnl_index==constantes.PANTALLA_PLANIFIC_CRONOG1 and( accion_actual=="elejir" or  accion_actual=="elegir")):
                   vent.update_pantallas(constantes.PANTALLA_PROCESO_PLANIFICACION,usr)
                   return
            vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1,usr)
            pnl=vent.panelActual
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        data_cronog=conexion_bd.get_allData([])
        field=pnl.get_comp_byName("año_escolar")
        accion_list=pnl.get_comp_byName("acciones")
        from event_manager import Event_manager
        
        Event_manager.activar_element("inicio_label",False,True)
        Event_manager.activar_element("cierre_label",False,True)
        Event_manager.activar_element("inicio",False,True)
        Event_manager.activar_element("cierre",False,True)
           
        usr.reset_data_process(0)

        if(data_cronog!=[]):
           field.set_text(data_cronog[0][0])
           acciones=["elegir"]
           limit_day=data_cronog[0][2]
           if(time_object.is_previous(time_object.get_fecha(),limit_day)):
              acciones.append("editar cronograma")
           acciones.append("editar fechas: inscripcion")
           acciones.append("editar fechas: momento1")
           acciones.append("editar fechas: momento 2")
           acciones.append("editar fechas: momento 3")
           acciones.append("editar fechas: materia pend.")
           acciones.append("eliminar cronograma")
           acciones.append("descargar cronograma")           
           accion_list.set_values(acciones)
           accion_list.set_selected_index(0)
        else:
           field.set_text("")
           acciones=["elegir","crear cronograma"]
           accion_list.set_values(acciones)
           accion_list.set_selected_index(0)
        
        
    #Reset the Cronogram
    @classmethod
    def reset_cronogram(cls,usr,vent,id_cronog,last_moment_close):
        pnl=vent.panelActual
        time_object=tiempo()
        conexion_bd.set_tabla(constantes.TABLA_FECHA)
        cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[id_cronog],"conditions_Verify":["="]}           
        conexion_bd.delete_data(cond_data)
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        conexion_bd.delete_data(cond_data)
        #Reset Sections
        for i in range(0,5):
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            if(conexion_bd.id_exist("año",str(i+1))==True):
                seccs_year=conexion_bd.get_allData([constantes.CLAVE_HORARIO,constantes.CLAVE_SECCION],2,["año"],[str(i+1)],["and"])
                cond_data={"conditions_Names":["año"],"condition_Types":["and"],"conditions_Values":[str(i+1)],"conditions_Verify":["="]}    
                conexion_bd.update_data({"total_estud":"0","modificado":time_object.get_fecha()},cond_data)
                for secc in seccs_year:
                    clave_secc=secc[1]
                    clave_hor=secc[0]
                    conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                    cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[clave_hor],"conditions_Verify":["="]} 
                    conexion_bd.update_data({"src_hor":""},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)   
                    cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[clave_secc],"conditions_Verify":["="]} 
                    d_estud=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],cond_data)
                    conexion_bd.update_data({constantes.CLAVE_SECCION:"default"},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                    for estud in d_estud:
                        cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[estud[0]],"conditions_Verify":["="]} 
                        estatus_estud=conexion_bd.get_allData(["estatus"],cond_data)
                        if(estatus_estud!=[]):
                            if(estatus_estud[0][0]!="graduado"):
                                conexion_bd.update_data({"estatus":"inactivo"},cond_data)
               
                              
        #Reset Temporal Califications               
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        data_calif_moms=conexion_bd.get_allData([])
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        for calif_mom in data_calif_moms:
            cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[calif_mom[0]],"conditions_Verify":["="]} 
            conexion_bd.delete_data(cond_data)
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            conexion_bd.delete_data(cond_data)                      

        #Reset Academic Moments
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        for i in range(0,3):
            if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,"momento "+str(i+1))==True):
                cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento "+str(i+1)],"conditions_Verify":["="]} 
                conexion_bd.delete_data(cond_data)
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"Modificacion del Cronograma","Cronograma Reseteado","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True)        
               
    #Determine and Execute the Required Actions for The Planification of Formats Process
    @classmethod
    def Determine_Action_Planification_format(cls,usr,vent):
        pnl=vent.panelActual
        accion=pnl.get_comp_byName("accion_box").get_selected_value()
        time_object=tiempo()
        import time
        if(accion!="elejir" and accion!="elegir"):
          dat=usr.get_data_process()
          if(accion=="modificar contenido"):
              if(dat!=[]):
                if(dat[0][2]=="pdf" or dat[0][2]=="PDF"):
                   General.show_message("solo se puede modificar formatos xlsx","formato invalido")
                   return
                refe=pnl.get_comp_byName("referencia").get_text()
                if(refe=="" or refe==" "):
                   General.show_message("por favor escriba una columna de referncia del formato","referncia invalida")
                   return
                vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO2,usr)  
                pnl=vent.panelActual
                src=dat[0][3]
                url=constantes.SERVER+src
                response=requests.get(url)
                if(response.status_code>400):
                   General.show_error("error obteniendo data del servidor","error de data del server")
                   return
                data_doc=[constantes.PANTALLA_PLANIF_FORMATO2,"cols_list",refe]
                file_dat=response.content
                documento.request(vent.raiz,file_dat,constantes.REQUEST_READ_EXCEL,data_doc)
              else:
                General.show_message("por favor seleccione un formato","formato no valido")        
          elif(accion=="eliminar formato"):
              if(dat!=[]):
                id_f=dat[0][0]
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                if(General.show_confirmDialog("esta seguro que desea eliminar este formato?","borrar formato")!=True):
                     return
                cond_data={"conditions_Names":["src_form"],"condition_Types":["and"],"conditions_Values":[dat[0][3]],"conditions_Verify":["="]} 
                data_form=conexion_bd.get_allData(constantes.CAMPOS_FORMATO,cond_data)
                if(len(data_form)<=1):
                  user_token=usr.get_credentials()[4]
                  url_delete=constantes.SERVER+"delete_file.php"
                  path={"directorio":"./","nombre":usr.get_data_process()[0][3],"token":user_token,"timestamp":str(int(time.time()))}
                  response_del=requests.post(url_delete,params=path)
                  res_delete=response_del.text.strip()
                conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[id_f],"conditions_Verify":["="]} 
                conexion_bd.delete_data([constantes.CLAVE_FORMATO],[id_f],["and"]) 
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                conexion_bd.delete_data(cond_data) 
                lista=pnl.get_comp_byName("formatos_list")
                data_form=conexion_bd.get_allData([])
                nombres=[]
                if(data_form!=[]):
                   for i in range(0,len(data_form)):
                       nombre=data_form[i][0]
                       nombres.append(nombre)
                lista.set_values(nombres) 
                usr.add_action_historial(["eliminar formato",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar formato","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("formato borrado satisfactoriamente","formato borrado")
              else:
                General.show_message("por favor seleccione un formato","formato no valido")
          elif(accion=="descargar formato"):

             if(dat!=[]):
               src=constantes.SERVER+dat[0][3]
               ruta=constantes.FOLDER_DOCUMENTS
               tipo_f=dat[0][2]
               extension=".xlsx"
               if(tipo_f=="PDF" or tipo_f=="pdf"):
                   extension=".pdf"
               ruta+="formato-"+dat[0][0]+extension
               documento.request(vent.raiz,ruta,constantes.REQUEST_DOWNLOAD,[src],True)
             else:
               General.show_message("por favor seleccione un formato","formato no valido")
        else:
          General.show_message("por favor seleccione una accion","accion invalida")
          
       
    #Verify if Finish The Cronogram or Academic Moments When the an User Loggin
    @classmethod
    def verificar_caudicidad(cls,usr,vent):
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cronogs=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"cierre"])
        time_object=tiempo()
        user_t=usr.get_credentials()[2]
        
        #Verifications Over Cronogram
        if(cronogs!=[] and (user_t=="admin" or user_t=="coordinador")==True):
            fecha_culminado=cronogs[0][1]
            if(time_object.is_previous(time_object.get_fecha(),fecha_culminado)==False ):
               #Academic Year is Finished
               if(General.show_confirmDialog("cronograma finalizado,desea borrarlo?","borrar cronograma")==True):
                   conexion_bd.set_tabla(constantes.TABLA_FECHA)
                   cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[cronogs[0][0]],"conditions_Verify":["="]} 
                    
                   conexion_bd.delete_data(cond_data)
                   conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                   conexion_bd.delete_data(cond_data)
                   #Reset Section
                   for i in range(0,5):
                      conexion_bd.set_tabla(constantes.TABLA_SECCION)
                      if(conexion_bd.id_exist("año",str(i+1))==True):
                          cond_data={"conditions_Names":["año"],"condition_Types":["and"],"conditions_Values":[str(i+1)],"conditions_Verify":["="]} 
                          seccs_year=conexion_bd.get_allData([constantes.CLAVE_HORARIO,constantes.CLAVE_SECCION],cond_data)
                          conexion_bd.update_data({"total_estud":"0","modificado":time_object.get_fecha()},cond_data)
                          for secc in seccs_year:
                             clave_secc=secc[1]
                             clave_hor=secc[0]
                             conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                             cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[clave_hor],"conditions_Verify":["="]} 
                             conexion_bd.update_data(["src_hor"],[""],cond_data)
                             conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)   
                             cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[clave_secc],"conditions_Verify":["="]} 
                             d_estud=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],cond_data)
                             conexion_bd.update_data([constantes.CLAVE_SECCION],["default"],cond_data)
                             conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                             for estud in d_estud:
                                cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[estud[0]],"conditions_Verify":["="]} 
                                estatus_estud=conexion_bd.get_allData(["estatus"],cond_data)
                                if(estatus_estud!=[]):
                                     if(estatus_estud[0][0]!="graduado"):
                                         conexion_bd.update_data({"estatus":"inactivo"},cond_data)
                                  
                   #Reset Temporals Califications
                   conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                   data_calif_moms=conexion_bd.get_allData([])
                   conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
                   for calif_mom in data_calif_moms:
                      cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[calif_mom[0]],"conditions_Verify":["="]} 
                      conexion_bd.delete_data(cond_data)
                      conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                      conexion_bd.delete_data(cond_data)                      
           
                   conexion_bd.set_tabla(constantes.TABLA_MOMENTO) 
                   #Reset Academic Moments
                   for i in range(0,3):
                      id_mom="momento "+str(i+1)
                      if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,id_mom)==True):
                         cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento "+str(i+1)],"conditions_Verify":["="]} 
                         conexion_bd.delete_data(cond_data)
                   conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                   id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                   data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"Modificacion del Cronograma","Cronograma Borrado","Cronograma Obsoleto",time_object.get_fecha()]
                   conexion_bd.add_data(data_hist,True)       
                   General.show_message("cronograma borrado exitosamente","cronograma borrado")
            
         
        #Verifications Over Academic Moments
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        moms=conexion_bd.get_allData([])
        if(moms!=[]):
            momentos_activos=0
            for i in range(0,len(moms)):
               if(moms[i][2]=="false" and moms[i][1]=="true" and moms[i][4]!=""):
                       momentos_activos+=1
                       limite=moms[i][4]
                       if(time_object.is_previous(time_object.get_fecha(),limite)==False):
                            #Academic Moment is Finished and Activate the Next Moment
                            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moms[i][0]],"conditions_Verify":["="]} 
                            conexion_bd.update_data({"abierto":"false","culminado":"true"},cond_data)
                            if(moms[i][0]=="momento 1"):
                               cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO,"abierto","culminado"],"condition_Types":["and","and","and"],"conditions_Values":["momento2","false","false"],"conditions_Verify":["=","=","="]} 
                               next_mom=conexion_bd.get_allData([],cond_data)
                               if(next_mom!=[]):
                                  if(next_mom[0][6]!=""):
                                     next_inicio=next_mom[0][6]
                                     if(time_object.is_previous(next_inicio,time_object.get_fecha(),False)==True):
                                        cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[next_mom[0][0]],"conditions_Verify":["="]} 
                                        conexion_bd.update_data({"abierto":"true"},cond_data,None,True)
                            elif(moms[i][0]=="momento 2"):
                                  cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO,"abierto","culminado"],"condition_Types":["and","and","and"],"conditions_Values":["momento 3","false","false"],"conditions_Verify":["=","=","="]} 
                                  next_mom=conexion_bd.get_allData([],cond_data)
                                  if(next_mom!=[]):
                                     if(next_mom[0][6]!=""):
                                        next_inicio=next_mom[0][6]
                                        if(time_object.is_previous(next_inicio,time_object.get_fecha(),False)==True):
                                            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[next_mom[0][0]],"conditions_Verify":["="]} 
                                            conexion_bd.update_data({"abierto":"true"},cond_data,None,True)
               elif(moms[i][2]=="true" and moms[i][1]=="true"):
                  if(moms[i][4]!="" and moms[i][5]!=""):
                      if(time_object.is_previous(moms[i][4],time_object.get_fecha(),False)):
                         if(time_object.is_previous_time(moms[i][5],time_object.get_tiempo())):
                             cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moms[i][0]],"conditions_Verify":["="]} 
                             conexion_bd.update_data({"abierto":"false"},cond_data,None,True)
            if(momentos_activos==0):
               activado=False
               for i in range(0,len(moms)):
                 if(activado==False):
                    if(moms[i][2]=="false" and moms[i][1]=="false" and moms[i][6]!=""):
                         inicio=moms[i][6]
                         if(time_object.is_previous(inicio,time_object.get_fecha(),False)==True):
                            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moms[i][0]],"conditions_Verify":["="]} 
                            conexion_bd.update_data({"abierto":"true"},cond_data,None,True)
                            activado=True
                            break
             