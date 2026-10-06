from documento import documento
from tiempo import tiempo
from conexion_bd import conexion_bd
from constantes import constantes
from General import General
import requests
import os
from estudiante import estudiante
from validator_manager import Process_Validator_Manager

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
    data_process={}
    
    #Clear the data Saved On the Active Process of User
    @classmethod
    def clear_data_process(cls):
         cls.data_process={}
       
    #get the data Saved On the Active Process as Dict
    @classmethod
    def get_data_process(cls):
        return cls.data_process
        
    #Force the Value of  data Saved On the Active Process 
    @classmethod
    def set_data_process(cls,data):
       cls.data_process=data

    #Set the Request for Register a New Section or Update a Existent On Inscription Process
    @classmethod
    def register_section(cls,year,turno,max_studs,min_studs):
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
    def get_section(cls,year,turno):
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
           return cls.register_section(year,turno,max_studs,min_studs)
          
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
       return cls.register_section(year,turno,max_studs,min_studs)
       
       
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
        valido=Process_Validator_Manager.validar_solicit_inscrip(data_estud)
        
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
                    
              
             data_seccion=cls.get_section(year_curso,turno)              
             fields=pnl.get_comps_byTag("field")
             data_estud.append(fields)
             data_estud.append(pnl.get_comp_byName("fecha").get_text())
             data_estud.append(pnl.get_comp_byName("salud").get_selected_value())
             data_estud.append(pnl.get_comp_byName("genero").get_selected_value())
             data_estud.append(year_curso)
             data_estud.append(estatus)
             data_verificada=Process_Validator_Manager.validar_inscripcion(data_estud)
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
                 id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
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
            id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
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
    def rendimiento_gestion(cls,usr,vent,option):
        pnl=vent.panelActual
        user_t=usr.get_credentials()[2]
        is_secretaria=False
        
        if(user_t!="admin" and user_t!="coordinador"):
            is_secretaria=True
        if(option<=cls.RENDIMIENTO_OPTION_PROCESS_CALIFICATIONS_TOTAL_REPORT):           
           cls.verify_expired_dates(usr,vent)
        
        if(option==cls.RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_GESTION_CALIFICATION):
            #gestion de calific 1
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA,usr)
            cls.clear_data_process()              
        elif(option==cls.RENDIMIENTO_OPTION_ACCESS_SABANA_AND_CALIFICATIONS_YEAR_PANEL):
            #'sabana' of Califications
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
                return
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_SABANA_NOTAS,usr)
            cls.clear_data_process()  
             
        elif(option==cls.RENDIMIENTO_OPTION_ACCESS_IDENTIFIC_MATERIA_PENDIENTE):
            #materia pendiente 1
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND,usr)
            cls.clear_data_process() 
              
        elif(option==cls.RENDIMIENTO_OPTION_PROCESS_CALIFICATIONS_TOTAL_REPORT):
            #Definitive Califications
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")         
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF_FINALES,usr)
            cls.clear_data_process()
        elif(option==cls.RENDIMIENTO_OPTION_IDENTIFIC_MATERIA_PENDIENTE):
            #materia pendiente 2
            data_proces=[]
            ced=pnl.get_comp_byName("cedula_p3").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data)==[]):
                General.show_message("cedula del estudiante invalida","cedula invalida")
                return
                
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],cond_data)==[]):
                General.show_message("estudiante sin materia pendientes","sin materias pendientes")
                return
            area=pnl.get_comp_byName("area_form").get_selected_value()
            section=pnl.get_comp_byName("secciones").get_selected_value()
            year=pnl.get_comp_byName("year").get_text()
            name_estud=pnl.get_comp_byName("nombre_p3").get_text()
            dat_estud={"Id_Estud":ced,"Area":area,"Section":section,"Year":year,"Name":name_estud}
            valido=Process_Validator_Manager.verify_Student_Credentials(dat_estud,option)
            if(valido==True):
              cls.data_process["Estudiante"]=dat_estud
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_MAT_PEND,usr)
              pnl=vent.panelActual
              pnl.get_comp_byName("area_p4").set_text(dat_estud["Area"])
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[dat_estud["Id_Estud"],dat_estud["Area"],str(int(dat_estud["Year"])-1)],"conditions_Verify":["=","=","="]}    
              data_pend=conexion_bd.get_allData(["max_calif"],cond_data,None,True)
              target_pts="00"
              if(len(data_pend)>0):
                 nota=data_pend[0]["max_calif"]
                 if(len(nota)<2):
                     nota="0"+nota
                 target_pts=nota
              pnl.get_comp_byName("best_nota").set_text(target_pts+" pts")
            
        elif(option==cls.RENDIMIENTO_OPTION_IDENTIFIC_GESTION_CALIFICATIONS):
            #gestion de calific 2
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
                return
            ced=pnl.get_comp_byName("cedula_p1").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[ced],"conditions_Verify":["="]}      
            if(conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data)==[]):
                General.show_message("cedula del estudiante invalida","cedula invalida")
                return
            area=pnl.get_comp_byName("area_form").get_selected_value()
            section=pnl.get_comp_byName("secciones_p1").get_selected_value()
            year=pnl.get_comp_byName("year").get_text()
            name_estud=pnl.get_comp_byName("nombre_p1").get_text()
            momento=pnl.get_comp_byName("mom_p1").get_selected_value()
            dat_estud={"Id_Estud":ced,"Area":area,"Momento":momento,"Section":section,"Year":year,"Name":name_estud}    
            valido=Process_Validator_Manager.verify_Student_Credentials(dat_estud,option)
            if(valido==True):
              cls.data_process["Estudiante"]=dat_estud
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF,usr)
        elif(option==cls.RENDIMIENTO_OPTION_PROCESS_MATERIA_PENDIENTE):
             #materia pendiente 3
             cls.process_seguimiento_materia_pendiente(usr,vent)
    

    
    #Determine the Action to execute from Calification Gestion Panel
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
    
    #Process 'Seguimiento de Materia Pendiente' From Rendimiento Process
    @classmethod 
    def process_seguimiento_materia_pendiente(cls,usr,vent):
         pnl=vent.panelActual
         estud=estudiante()
         time_object=tiempo()
         data_estud=cls.data_process["Estudiante"]
         intento_val=pnl.get_comp_byName("intento_p4").get_selected_value()
         calif=pnl.get_comp_byName("calif_p4").get_text()
         motivo=pnl.get_comp_byName("motivo").get_text()
         data_pendiente={"Id_Estud":data_estud["Id_Estud"],"Area":data_estud["Area"],"Section":data_estud["Section"],"Intento_Id":intento_val,"Calificacion_Value":calif,"Motivo":motivo}
         if(Process_Validator_Manager.verify_materiaPendiente_Data(data_pendiente)==False):
            return
         if(General.show_confirmDialog("esta seguro que desea registrar el intento?","registar intento")!=True):
            return
         msg_res=estud.mat_pendiente(data_pendiente,time_object.get_fecha())
         conexion_bd.set_tabla(constantes.TABLA_REPORTE)
         id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
         data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","mat. pendiente",motivo,time_object.get_fecha()]
         res_add=conexion_bd.add_data(data_hist,True)  
         if(res_add<0):
            return 
         General.show_message(msg_res[0],msg_res[1])     
         vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND,usr)
         cls.clear_data_process()
    
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
        data_estud=cls.data_process["Estudiante"]
        data_estud["Evaluation"]=evaluation
        data_estud["Motivo"]=motivo
        if(Process_Validator_Manager.validate_calification_Gestion(data_estud,"Delete")==False):
            return
        if(General.show_confirmDialog("esta seguro que desea borrar esta calificacion?","borrar calificacion")!=True):
            return  
        valido=estud.delete_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           usr.add_action_historial(["borrar calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
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
           action_comp=pnl.get_comp_byName("Action_List")
           if(action_comp!=None):
               action_comp.set_selected_index(0)
               action_comp.On_select(None)
           General.show_message("calificacion borrada satisfactoriamente","calificacion borrada")
      
    #Modify the Calification Associated to an Academic Moment  
    @classmethod
    def update_calification(cls,usr,vent):
        pnl=vent.panelActual
        evaluation=""
        tabl_califics=pnl.get_comp_byName("table_califics")
        calific_comp=pnl.get_comp_byName("calific_val")
        if(tabl_califics==None or calific_comp==None):
           return
        selected_row=tabl_califics.get_row_selectedData()
        if(selected_row!=" "):
          if(len(selected_row)>0):
             evaluation=selected_row[0]
        motivo=pnl.get_comp_byName("motivo").get_text()
        next_calific=calific_comp.get_text()
        time_object=tiempo()
        estud=estudiante()
        data_estud=cls.data_process["Estudiante"]
        data_estud["Evaluation"]=evaluation
        data_estud["Calification"]=next_calific
        data_estud["Motivo"]=motivo
        if(Process_Validator_Manager.validate_calification_Gestion(data_estud,"Update")==False):
            return
        if(General.show_confirmDialog("esta seguro que desea modificar esta calificacion?","modificar calificacion")!=True):
            return    
        valido=estud.modific_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
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
           action_comp=pnl.get_comp_byName("Action_List")
           if(action_comp!=None):
               action_comp.set_selected_index(0)
               action_comp.On_select(None)
           General.show_message("calificacion modificada exitosamente","calificacion modificada")
       
       
    #Assign Estimulation Points Associated to an Academic Moment
    @classmethod
    def estimular_mom(cls,usr,vent):
         pnl=vent.panelActual
         motivo=pnl.get_comp_byName("motivo").get_text()
         estimul_prom_field=pnl.get_comp_byName("estimul_prom")
         estimul_areas_field=pnl.get_comp_byName("estimul_areas")
         estimul_prom_text=estimul_prom_field.get_text()
         estimul_areas_text=estimul_areas_field.get_text()
         time_object=tiempo()
         estud=estudiante()
         data_estud=cls.data_process["Estudiante"]
         data_estud["Estimulacion_Promedio"]=estimul_prom_text
         data_estud["Estimulacion_Areas"]=estimul_areas_text
         data_estud["Motivo"]=motivo
         if(Process_Validator_Manager.validate_calification_Gestion(data_estud,"Estimulation")==False):
            return
         if(General.show_confirmDialog("esta seguro que desea estimular la calificacion de esta area?","borrar calificacion")!=True):
             return
           
         valido=estud.estimular_area(data_estud,time_object.get_fecha())
         if(valido[0]==True):
            usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","calificacion estimulada",motivo,time_object.get_fecha()]
            conexion_bd.add_data(data_hist,True)
            estimul_prom_field.set_text("")
            estimul_areas_field.set_text("")  
            prom_data=valido[1]
            pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
            pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+str(prom_data[1])+"pts")
            pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
            pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+str(prom_data[3])+"pts")
            pnl.get_comp_byName("motivo").set_text("")
            action_comp=pnl.get_comp_byName("Action_List")
            if(action_comp!=None):
               action_comp.set_selected_index(0)
               action_comp.On_select(None)
            General.show_message("area de formacion estimulada satisfactoriamente","area de formacion estimulada")
         
    
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
      
       #Process Change of Calification for Students 'Nuevo Ingreso' with Califications from Another Institute (Califications With Value 0)
       field_ced=pnl.get_comp_byName("cedula_estudiante")
       nacionaliad_comp=pnl.get_comp_byName("nacionalidad")
       cedula_estud=""
       if(field_ced!=None and nacionaliad_comp!=None):
          nacionalidad_value=nacionaliad_comp.get_selected_value()
          if(nacionalidad_value.lower()=="venezolano"):
              cedula_estud=f"V-{field_ced.get_text()}"
          else:
             cedula_estud=f"E-{field_ced.get_text()}"
       area=pnl.get_comp_byName("area").get_text()
       year=pnl.get_comp_byName("year").get_text()
       tabla=pnl.get_comp_byName("table_califics")
       new_calif=pnl.get_comp_byName("calif").get_text() 
       time_object=tiempo()
       estud=estudiante()
       data_estud={"Id_Estud":cedula_estud,"Area":area,"Year":year,"Calification":new_calif}
       if(Process_Validator_Manager.validateData_DefiniteCalifications_Gestion(data_estud)==False):
            return
       if(General.show_confirmDialog("esta seguro que desea Modificar la Calificacion Indicada","Modificar Calificacion")!=True):
            return
             
       res=estud.modific_calif_final(data_estud,time_object.get_fecha())        
       usr.add_action_historial(["modificacion de calificacion final",time_object.get_tiempo()])
       conexion_bd.set_tabla(constantes.TABLA_REPORTE)
       id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
       data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar calificacion final","actualizar notas faltantes del estudiante provenientes de otra institucion",time_object.get_fecha()]
       res_add=conexion_bd.add_data(data_hist,True)
       if(res_add<0):
          return 
          
       flds=pnl.get_comps_byTag("field")
       for fl in flds:
          if(fl.get_id()=="area" or fl.get_id()=="year" or fl.get_id()=="calif"):
              fl.set_text("")
       tabla.reset()
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula_estud],"conditions_Verify":["="]}      
       data_calif=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION,"año","valor"],cond_data,None,True)
       for i in range(0,len(data_calif)):
          tabla.add_row([data_calif[i][constantes.CLAVE_AREA_FORMACION],data_calif[i]["año"],data_calif[i]["valor"]])
       
       if(res==False):
           General.show_message("Calificacion Modificada, Actualizacion de Calificacion Pendientes del Estudiante ","Actualizacion finalizada")
       else:
           General.show_message("calificacion final modificada exitosamente","calificacion final modificada")
     
      
       
            
    #Generate the Document 'Sabana de Notas'
    @classmethod
    def generate_sabana_notas(cls,usr,vent,require_califications=False):
       pnl=vent.panelActual
       valido=0 
       field=pnl.get_comp_byName("letra_p5")
       combo=pnl.get_comp_byName("year_p5")
       time_object=tiempo()
       letra=field.get_text()
       year=combo.get_selected_value()
       turno=pnl.get_comp_byName("turno").get_selected_value()
       data_verify={"Year":year,"Turno":turno,"Letra":letra}
       if(Process_Validator_Manager.validar_sectionData_NotasMomento_Sabana_generation(data_verify)==False):
           return
       
       #Get the all Data of Student of Section
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       id_secc=year[0]+"-"+letra
       cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[id_secc],"conditions_Verify":["="]}      
       join_data={}
       join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None}
       cond_join={"conditions_Names":["estatus","estatus"],"condition_Types":["and","and"],"conditions_Values":["inactivo","graduado"],"conditions_Verify":["!=","!="]}                         
       join_data["estatus_estud"]={"query_field":["estatus"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":cond_join}
       data_secc=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data,join_data,True)
       if(len(data_secc)<=0):
           General.show_message("No Existen Estudiantes en la Seccion Indicada","Seccion sin Estudiantes")
           return

       #Get the Formation Area Availables for the Year of Section in Order as a List
       conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
       data_areas=[]
       join_data={}
       cond_join={"conditions_Names":[year[0]+"_año"],"condition_Types":["and"],"conditions_Values":["True"],"conditions_Verify":["="]}                         
       join_data["años_incorporados"]={"query_field":[constantes.CLAVE_AÑOS_INCORPORADOS],"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":cond_join}
       cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":["Si"],"conditions_Verify":["="]}    
       data_areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],cond_data,join_data,True)
       if(len(data_areas)<=0):
           General.show_message("No Existen Areas de Formacion Registradas Activas para el Año de Curso","Año sin Areas de Formacion Activas")
           return 
       orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","historia","fsn","ov","gcrp"]     
       areas_list=[]
       for name in orden:
         for area in data_areas:
             area_temp=area[constantes.CLAVE_AREA_FORMACION]
             if(area_temp.lower()==name):
                 areas_list.append(area_temp)
                 break
             
      
       #Save the Data of Students as a List
       name_ids=["nombre","s_nombre","apellido","s_apellido"]
       estudents_data=[]
       for estud in data_secc:
          name_dat=[]
          for id in name_ids:
             if(estud[id]!="" and estud[id]!="..."):
                name_dat.append(estud[id])
          name_estud=" ".join(name_dat)
          cedula_estud=estud[constantes.CLAVE_ESTUDIANTE]
          temp_data=[cedula_estud,name_estud]
          #Get the Califications Of Each Formation Area Associated to the Student
          conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
          for area in areas_list:
              cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año",constantes.CLAVE_AREA_FORMACION],"condition_Types":["and","and","and"],"conditions_Values":[cedula_estud,year[0],area],"conditions_Verify":["=","=","="]}    
              dat_califs=conexion_bd.get_allData(["valor"],cond_data,None,True)
              calific_target="01"
              if(len(dat_califs)<=0):
                  #Make a DefaultRegister of Calification if It not Exist
                  data_register={constantes.CLAVE_CALIFICACION_FINAL:f"{cedula_estud}-{area}{year[0]}",constantes.CLAVE_ESTUDIANTE:cedula_estud,"año":year[0],constantes.CLAVE_AREA_FORMACION:area,"valor":"01","modificado":time_object.get_fecha()}
                  conexion_bd.add_data(data_register,True)
              else:
                  calific_target=dat_califs[0]["valor"]
              if(require_califications):
                  temp_data.append(calific_target)
             
          estudents_data.append(temp_data)

       #Request the Document         
       dat=[estudents_data,areas_list,year[0]+"-"+letra,year[0]]                        
       from event_manager import Event_manager
       if(require_califications==False):
           Event_manager.generar_reporte("sabana de notas",dat)
       else:
          Event_manager.generar_reporte("notas finales del año",dat)   
                      
     
    #Get the Value of Date From Date Fields On Edit Cronogram Panels
    @classmethod
    def get_date_fields_cronogram_values(cls,vent,parte):
        pnl=vent.panelActual
        fields=pnl.get_comps_byTag("date")
        data_send=[]         
        time_object=tiempo()
        start_mom=""
        end_mom=""
        index_single_fields=len(fields)
        if(parte=="general"):
            index_single_fields=8
        elif(parte=="mat pendiente"):
            index_single_fields=0
        elif(parte.startswith("momento")):
            moment_number=int(parte[len(parte)-1])
            if(moment_number==1):
               index_single_fields=8
            elif(moment_number==2):
               index_single_fields=6
            elif(moment_number==3):
               index_single_fields=4      
        temp_dates=[]
        temp_razon=""
        limit_dates=2
        index=0
        
        for temp_field in fields:
            value_field=temp_field.get_text()
            id_field=temp_field.get_id()
            strict_verification=True
            if((id_field=="inicio" or id_field=="cierre")==True and parte.startswith("momento")==False ):
                 continue               
            temp_dates.append(value_field)
            if(temp_razon==""):
               temp_razon=id_field
            if(index>=index_single_fields):
               next_value=value_field
               strict_verification=False
               if(id_field=="consejo de curso"):
                  next_value=time_object.get_next_date2(next_value,1)
               temp_dates.append(next_value)
            if(len(temp_dates)>=limit_dates):                 
                data_dict={"Inicio":temp_dates[0],"Cierre":temp_dates[1],"Razon":temp_razon,"Strict_Verification":strict_verification}
                data_send.append(data_dict)
                if(temp_razon=="inicio"):
                    start_mom=temp_dates[0]
                    end_mom=temp_dates[1]
                temp_dates=[]
                temp_razon=""
            index+=1                
        return [data_send,start_mom,end_mom]
    
    
    #Verify if Is Neccesary Register or Update an Academic Moment When a Cronogram Part Require Modify
    @classmethod
    def verify_moments_registers(cls,cronogram_part_modify,inicio_moment,end_moment):
          
          time_object=tiempo()
          if(cronogram_part_modify!="momento 1"): 
               conexion_bd.set_tabla(constantes.TABLA_MOMENTO)  
               moement_verify={"momento 2":"momento 1","momento 3":"momento 2"}               
               if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,cronogram_part_modify)==False):
                   #Build a New Academic Momento ('Momento 2' and 'Momento 3')
                   abierto="false"
                   cerrado="false"  
                   cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moement_verify[cronogram_part_modify]],"conditions_Verify":["="]}        
                   dat_verify=conexion_bd.get_allData(["culminado"],cond_data,None,True)
                   if(len(dat_verify)<=0):
                        General.show_message("Error Obteniendo Data del Momento Anterior ","Error ")  
                        return False
                   if(dat_verify["culminado"]=="true"):
                        abierto="true"
                   momento_new_data={constantes.CLAVE_MOMENTO:cronogram_part_modify,"abierto":abierto,"culminado":cerrado,"modificado":time_object.get_fecha(),"fecha_limite":end_moment,"hora_limite":"00:00:00","fecha_inicio":inicio_moment}
                   conexion_bd.add_data(momento_new_data)
               else:
                    #Update Dates if Start and End of Academic Moment
                    cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[cronogram_part_modify],"conditions_Verify":["="]}    
                    conexion_bd.update_data({"fecha_limite":end_moment,"hora_limite":"00:00:00","fecha_inicio":inicio_moment,"modificado":time_object.get_fecha()},cond_data)
          return True
               
    #Process the Edition of Cronogram Dates
    @classmethod
    def Process_Cronogram_Edit_Dates(cls,usr,vent,parte):
        data_dates=cls.get_date_fields_cronogram_values(vent,parte)
        pnl=vent.panelActual
        data_send=data_dates[0]
        inicio_moment=data_dates[1] 
        end_moment=data_dates[2] 
        
        time_object=tiempo()
        target_moment="momento 1"
        if(parte.startswith("momento")):
           target_moment=parte
           if(cls.verify_moments_registers(parte,inicio_moment,end_moment)==False):
               return
        if(Process_Validator_Manager.validate_cronogram_Dates(data_send)==False):
            return
        if(General.show_confirmDialog("modificar el cronograma?","modificar crongrama")!=True):
            return
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        dat_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],None,None,True)
        
            
        for i in range(0,len(data_send)):
          date_init=data_send[i]["Inicio"]
          date_end=data_send[i]["Cierre"]    
          if(parte=="mat pendiente"):          
              date_end=time_object.get_next_date2(date_end,4)
          if(parte.startswith("momento")):
             
             if(data_send[i]["Razon"]=="inicio"):
                 conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                 cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[target_moment],"conditions_Verify":["="]}    
                 conexion_bd.update_data({"fecha_limite":end_moment,"fecha_inicio":inicio_moment,"modificado":time_object.get_fecha()},cond_data) 
                 continue
          data_register={constantes.CLAVE_FECHA:dat_cronog[0][constantes.CLAVE_CRONOGRAMA]+f"-{target_moment}-"+data_send[i]["Razon"],constantes.CLAVE_MOMENTO:target_moment,constantes.CLAVE_CRONOGRAMA:dat_cronog[0][constantes.CLAVE_CRONOGRAMA],"razon":data_send[i]["Razon"],"fecha":date_init,"fecha_cierre":date_end,"modificado":time_object.get_fecha()}
          conexion_bd.set_tabla(constantes.TABLA_FECHA)
          if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_register[constantes.CLAVE_FECHA])==False):
              conexion_bd.add_data(data_register)
          else:
              cond_data={"conditions_Names":[constantes.CLAVE_FECHA],"condition_Types":["and"],"conditions_Values":[data_register[constantes.CLAVE_FECHA]],"conditions_Verify":["="]}    
              conexion_bd.update_data({"fecha":data_register["fecha"],"fecha_cierre":data_register["fecha_cierre"],"modificado":time_object.get_fecha()},cond_data) 
        
        usr.add_action_historial(["editar cronograma",time_object.get_tiempo()])
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","editar cronograma","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True) 
        General.show_message("cronograma actualizado exitosamente","cronograma actualizado") 
        cls.clear_data_process()
        vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1,usr)
        cls.show_planificar_cronogOption(usr,vent,True)
        
    #Process Cronogram Register/Update
    @classmethod
    def Process_Cronogram_Register_Update(cls,usr,vent,accion):
       pnl=vent.panelActual
       inicio=pnl.get_comp_byName("inicio").get_text()
       cierre=pnl.get_comp_byName("cierre").get_text()
       periodo=pnl.get_comp_byName("año_escolar").get_text()
       data_cronog={"Periodo":periodo,"Inicio":inicio,"Cierre":cierre}
       time_object=tiempo()
       if(Process_Validator_Manager. validate_cronogram(data_cronog)==False):
            return
       if(accion=="crear cronograma"): 
           #Register Cronogram and First Academic Moment       
           if(General.show_confirmDialog("registrar el cronograma indicado?","registrar cronograma")!=True):
              return
           data_cronog=[periodo,inicio,cierre,time_object.get_fecha()]
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           conexion_bd.add_data(data_cronog)
           conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
           
           data_mom=["momento 1","true","false",time_object.get_fecha(),cierre,"00:00:00",inicio]
           conexion_bd.add_data(data_mom)
           usr.add_action_historial(["registrar cronograma",time_object.get_fecha()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","crear cronograma","",time_object.get_fecha()]
           conexion_bd.add_data(data_hist,True) 
           General.show_message("Cronograma Registrado Satisfactoriamente","cronograma registrado")
       else:
          #Crongram Update
          if(General.show_confirmDialog("actualizar el cronograma indicado?","registrar cronograma")!=True):
              return
          cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[periodo],"conditions_Verify":["="]}    
          conexion_bd.update_data({"inicio":inicio,"cierre":cierre,"modificado":time_object.get_fecha()},cond_data)
          usr.add_action_historial(["modificar cronograma",time_object.get_fecha()])
          conexion_bd.set_tabla(constantes.TABLA_REPORTE)
          id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
          data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar cronograma","",time_object.get_fecha()]
          conexion_bd.add_data(data_hist,True) 
          General.show_message("cronograma actualizado satisfactoriamente","cronograma registrado")
       cls.show_planificar_cronogOption(usr,vent,True)
     
    #Try Remove the Cronogram if is Possible
    @classmethod
    def remove_cronogram(cls,usr,vent):
        time_object=tiempo()
        last_moment_close=False
        pnl=vent.panelActual
        id_cronog=pnl.get_comp_byName("año_escolar").get_text()
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        mom_dat=conexion_bd.get_allData([constantes.CLAVE_MOMENTO,"culminado"],None,None,True)
        if(len(mom_dat)>0):
           for i in range(0,len(mom_dat)):
               if(mom_dat[i][constantes.CLAVE_MOMENTO]!="momento 3"):
                  continue
               if(mom_dat[i]["culminado"]=="true"):
                 #Cronogram is Finished
                 last_moment_close=True 
                     
           if(last_moment_close==False):
               #Active Crongram
               conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
               if(len(conexion_bd.get_allData([constantes.CLAVE_CALIF_MOM],None,None))>0):
                   #Exist Califications for the Student Associated to Active Academic Moments
                   General.show_error("No se puede Eliminar el Cronograma","Cronograma no Borrable")
                   return  
                   
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[id_cronog],"conditions_Verify":["="]}    
        data_cronog=conexion_bd.get_allData(["inicio","cierre"],cond_data,None,True)
        max_date=time_object.get_next_date2(data_cronog[0]["inicio"],4)
        if(time_object.is_previous(time_object.get_fecha(),max_date)==False and last_moment_close==False):
           if(time_object.is_previous(time_object.get_fecha(),data_cronog[0]["cierre"])):
             # The Cronogram is Not Over and  the Date is Very Late for Remove the Cronogram
              General.show_error("no se puede eliminar el cronograma","cronograma no borrable")
              return
   
        if(General.show_confirmDialog("esta seguro que desea borrar el cronograma?","borrar cronograma")!=True):
                 return
        if(cls.reset_cronogram(usr,vent,id_cronog)<0):
            return         
        usr.add_action_historial(["borrar cronograma",time_object.get_fecha()])
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar cronograma","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True) 
        General.show_message("cronograma borrado exitosamente","cronograma borrado")
        cls.show_planificar_cronogOption(usr,vent,True)         
        pnl.get_comp_byName("acciones").set_selected_index(0)
     
     
    #Verify the Requerid Academic Moment and Try to Set the Date Value On the Requerdis texts field when Change to a Edit Cronogram Panel
    @classmethod
    def set_dateFields_Values(cls,part_date_modify,momento,razones_requerid,has_end_DateField,target_panel,usr,vent):
        data_mom=[]
        if(part_date_modify=="momentos"):
           res=Process_Validator_Manager.validate_Date_Moment_Edition(momento)
           if(res[0]==False):    
               return
           data_mom=res[1]
        vent.update_pantallas(target_panel,usr)
        pnl=vent.panelActual  
        
        if( len(data_mom)>0 and part_date_modify=="momentos"):
              inicio=pnl.get_comp_byName("inicio")
              cierre=pnl.get_comp_byName("cierre")
              inicio.set_state("normal")
              cierre.set_state("normal")
              inicio.set_text(data_mom[0]["fecha_inicio"])
              cierre.set_text(data_mom[0]["fecha_limite"])
              #If Academic is not at End or is Open  it can Modify Date of End
              if(data_mom[0]["culminado"]=="false" and data_mom[0]["abierto"]=="false" ):
                 inicio.set_state("normal")
              else:
                 inicio.set_state("readonly")
              if(data_mom[0]["culminado"]=="false"):
                 cierre.set_state("normal")
              else:
                cierre.set_state("readonly")
        elif(part_date_modify=="inscripcion"):
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            dat_cronog= conexion_bd.get_allData(["inicio","cierre"],None,None,True)
            inicio=pnl.get_comp_byName("inicio")
            cierre=pnl.get_comp_byName("cierre")
            inicio.set_state("normal")
            cierre.set_state("normal")
            inicio.set_text(dat_cronog[0]["inicio"])
            cierre.set_text(dat_cronog[0]["cierre"])
            inicio.set_state("readonly")
            cierre.set_state("readonly")
        conexion_bd.set_tabla(constantes.TABLA_FECHA)     
        for i in range(0,len(razones_requerid)):
            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO,"razon"],"condition_Types":["and","and"],"conditions_Values":[momento,razones_requerid[i]],"conditions_Verify":["=","="]}    
            data_temp=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data,None,True)
            if(len(data_temp)<=0):
                continue
            comp=pnl.get_comp_byName(razones_requerid[i])
            if(comp==None):
                 continue
            comp.set_text(data_temp[0]["fecha"])
            if(has_end_DateField[i]==True):
               comp_s=pnl.get_comp_byName("cierre "+razones_requerid[i])
               comp_s.set_text(data_temp[0]["fecha_cierre"])
        return True
    
    #Interprete the the Action  in  Cronogram Planification
    @classmethod
    def cronogram_gestion(cls,usr,vent):
        pnl=vent.panelActual
        if((usr.get_credentials()[2]!="coordinador" and usr.get_credentials()[2]!="admin")==True):
            General.show_error("acceso invalido para el usuario","usuario sin permiso")
            vent.update_pantallas(constantes.PANTALLA_WELCOME,usr)
            cls.clear_data_process()
            return
        time_object=tiempo()
        accion=pnl.get_comp_byName("acciones").get_selected_value()
        if(accion=="elejir" or accion=="elegir"):
             General.show_message("por favor seleccione una accion","accion invalida")
             return
        if(accion=="crear cronograma" or accion=="editar cronograma"):
             cls.Process_Cronogram_Register_Update(usr,vent,accion)
        elif(accion=="descargar cronograma"):
             from event_manager import Event_manager
             Event_manager.generar_reporte("cronograma")   
        elif(accion=="eliminar cronograma"):
             cls.remove_cronogram(usr,vent)
        else:
        
           if(accion.startswith("editar fechas: momento")):
              mom=""
              target_panel=-1
              razones=["evaluacion continua","entrega de planificaciones a subdireccion academica","entrega de calificacion a departamento de evaluacion","asueto de navidad","consejo de curso","consejo de docentes","reunion de representantes","cierre pedagogico","entrega de boletas a representantes","semana aniversario","misa graduandos","acto de grado","asueto de carnaval"]
              has_end_DateField=[True,False,False,True,False,False,False,False,False,True,False,False,True]
        
              if(accion.endswith("momento1")):
                 mom="momento 1"
                 target_panel=constantes.PANTALLA_PLANIFIC_CRONOG4
              if(accion.endswith("momento 2")):
                 mom="momento 2"
                 target_panel=constantes.PANTALLA_PLANIFIC_CRONOG5
              elif(accion.endswith("momento 3")):
                 mom="momento 3"
                 target_panel=constantes.PANTALLA_PLANIFIC_CRONOG6
              cls.set_dateFields_Values("momentos",mom,razones,has_end_DateField,target_panel,usr,vent)                
           else:
             mom="momento 1"
             if(accion=="editar fechas: materia pend."):
                target_panel=constantes.PANTALLA_PLANIFIC_CRONOG3
                razones=["materia pendiente 1","materia pendiente 2","materia pendiente 3","materia pendiente 4","revision"]
                has_end_DateField=[False,False,False,False,False]
                cls.set_dateFields_Values("materia pendiente",mom,razones,has_end_DateField,target_panel,usr,vent)           
             elif(accion=="editar fechas: inscripcion"):
                target_panel=constantes.PANTALLA_PLANIFIC_CRONOG2
                razones=["inscripcion nuevo ingreso","inscripcion estudiantes regulares"]
                has_end_DateField=[True,True]
                cls.set_dateFields_Values("inscripcion",mom,razones,has_end_DateField,target_panel,usr,vent)
  
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
        data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"cierre"],None,None,True)
        field=pnl.get_comp_byName("año_escolar")
        accion_list=pnl.get_comp_byName("acciones")
        from event_manager import Event_manager
        
        Event_manager.activar_element("inicio_label",False,True)
        Event_manager.activar_element("cierre_label",False,True)
        Event_manager.activar_element("inicio",False,True)
        Event_manager.activar_element("cierre",False,True)
        cls.clear_data_process()

        if(len(data_cronog)>0):
           field.set_text(data_cronog[0][constantes.CLAVE_CRONOGRAMA])
           acciones=["elegir"]
           limit_day=data_cronog[0]["cierre"]
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
    def reset_cronogram(cls,usr,vent,id_cronog):
        time_object=tiempo()
        #Remove Dates
        conexion_bd.set_tabla(constantes.TABLA_FECHA)
        cond_data={"conditions_Names":[constantes.CLAVE_CRONOGRAMA],"condition_Types":["and"],"conditions_Values":[id_cronog],"conditions_Verify":["="]}           
        conexion_bd.delete_data(cond_data)
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        conexion_bd.delete_data(cond_data)
        
        num_year=5
        #Reset Sections (Each Year)
        for i in range(0,num_year):
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            
            cond_data={"conditions_Names":["año"],"condition_Types":["and"],"conditions_Values":[str(i+1)],"conditions_Verify":["="]}           
            seccs_year=conexion_bd.get_allData([constantes.CLAVE_HORARIO,constantes.CLAVE_SECCION],cond_data,None,True)
            if(len(seccs_year)<=0):
               continue
            conexion_bd.update_data({"total_estud":"0","modificado":time_object.get_fecha()},cond_data)
            for secc in seccs_year:
               clave_secc=secc[constantes.CLAVE_SECCION]
               clave_hor=secc[constantes.CLAVE_HORARIO]
               conexion_bd.set_tabla(constantes.TABLA_HORARIO)
               cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[clave_hor],"conditions_Verify":["="]} 
               conexion_bd.update_data({"src_hor":""},cond_data)
               
               #Update Students States
               conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)   
               cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[clave_secc],"conditions_Verify":["="]} 
               join_data={}
               cond_join={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":["graduado"],"conditions_Verify":["!="]} 
               join_data["estatus_estud"]={"query_field":{"estatus":"inactivo"},"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":cond_join}
               conexion_bd.update_data({constantes.CLAVE_SECCION:"default"},cond_data,join_data)
               
                              
        #Reset Temporal Califications               
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        data_calif_moms=conexion_bd.get_allData([constantes.CLAVE_CALIF_MOM],None,None,True)
        for calif_mom in data_calif_moms:
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
            cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[calif_mom[constantes.CLAVE_CALIF_MOM]],"conditions_Verify":["="]} 
            conexion_bd.delete_data(cond_data)
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            conexion_bd.delete_data(cond_data)                      

        #Reset Academic Moments
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        for i in range(0,3):
            cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":["momento "+str(i+1)],"conditions_Verify":["="]} 
            conexion_bd.delete_data(cond_data)
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"Modificacion del Cronograma","Cronograma Reseteado","",time_object.get_fecha()]
        return conexion_bd.add_data(data_hist,True)        
               
    #Determine and Execute the Required Actions for The Planification of Formats Process
    @classmethod
    def Determine_Action_Planification_format(cls,usr,vent):
        pnl=vent.panelActual
        action=pnl.get_comp_byName("accion_box").get_selected_value()
        time_object=tiempo()
        import time
        src=pnl.get_comp_byName('form_field').get_text()
        type_form=pnl.get_comp_byName('type_field').get_text()
        reference_text=pnl.get_comp_byName('referencia').get_text()  
        data_form={"Action":action,"Formato":src,"Format_Type":type_form,"Reference_Text":reference_text}
        if(Process_Validator_Manager.verify_formatGestion_Data(data_form)==False):
            return
        conexion_bd.set_tabla(constantes.TABLA_FORMATO)
        cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[src],"conditions_Verify":["="]} 
                
        dat_form=conexion_bd.get_allData(["src_form"],cond_data,None,True)
        if(len(dat_form)<=0):
           General.show_message("Error Obteniendo Data del Formato","Error")
           return
        src_filename=dat_form[0]["src_form"]       
        if(action=="modificar contenido"):

                vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO2,usr)  
                pnl=vent.panelActual
                url=constantes.SERVER+src_filename
                response=requests.get(url)
                if(response.status_code>400):
                   General.show_error("error obteniendo data del servidor","error de data del server")
                   return
                dict_form={"Source":src_filename,"Reference_Text":reference_text,"Format_Id":src}
                cls.data_process={"Formatos":dict_form}
                data_doc=[constantes.PANTALLA_PLANIF_FORMATO2,"cols_list",reference_text]
                file_dat=response.content
                documento.request(vent.raiz,file_dat,constantes.REQUEST_READ_EXCEL,data_doc)
        elif(action=="eliminar formato"):
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                if(General.show_confirmDialog("esta seguro que desea eliminar este formato?","borrar formato")!=True):
                     return
                cond_data={"conditions_Names":["src_form"],"condition_Types":["and"],"conditions_Values":[src_filename],"conditions_Verify":["="]} 
                data_form=conexion_bd.get_allData(constantes.CAMPOS_FORMATO,cond_data)
                if(len(data_form)<=1):
                  user_token=usr.get_credentials()[4]
                  url_delete=constantes.SERVER+"delete_file.php"
                  path={"directorio":"./","nombre":src_filename,"token":user_token,"timestamp":str(int(time.time()))}
                  response_del=requests.post(url_delete,params=path)
                  res_delete=response_del.text.strip()
                conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[src],"conditions_Verify":["="]} 
                conexion_bd.delete_data(cond_data) 
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                conexion_bd.delete_data(cond_data,None,True) 
                lista=pnl.get_comp_byName("formatos_list")
                data_form=conexion_bd.get_allData([constantes.CLAVE_FORMATO],None,None,True)
                nombres=[]
                for i in range(0,len(data_form)):
                     nombre=data_form[i][constantes.CLAVE_FORMATO]
                     nombres.append(nombre)
                lista.set_values(nombres) 
                usr.add_action_historial(["eliminar formato",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
                data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar formato","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("formato borrado satisfactoriamente","formato borrado")
             
        elif(action=="descargar formato"):
               src_file=constantes.SERVER+src_filename
               ruta=constantes.FOLDER_DOCUMENTS
               extension=".xlsx"
               if(type_form.lower()=="pdf"):
                   extension=".pdf"
               ruta+="formato-"+src+extension
               documento.request(vent.raiz,ruta,constantes.REQUEST_DOWNLOAD,[src_file],True)
           
    #Manage the Columns Values for the Modify Format Option On Format Gestion
    @classmethod
    def modify_columns_format(cls,action,vent):
       pnl=vent.panelActual
       target_field=None
       fields_names={"Add":"val_col","Modify":"cols_edit","Remove":"val_delete_col"}
       fields_comps={"Add":None,"Modify":None,"Remove":None}
       for key in fields_names:
          field=fields_names[key]
          fields_comps[key]=pnl.get_comp_byName(field)
          if(fields_comps[key]==None):
             General.show_error("Faltan Text Fields en el Formulario","Faltan TextFields")
             return
             
       target_field=fields_comps[action]  
       target_field_val=target_field.get_text()
       if(target_field_val==cls.data_process["Formatos"]["Reference_Text"]):
          General.show_message("No se puede Modificar el Valor de la Celda de Referencia","Columna Invalida")
          return
       if(General.is_valid(target_field_val,constantes.CADENA_ALFANUMERICA,False,1)==False):
          General.show_message("Por Favor Indique un valor Valido a la Columna Modificar","Valor de Columna Invalido")
          return
       lista=pnl.get_comp_byName("cols_list")
       actual_data=lista.get_all_values()
       if(action=="Add"):
           actual_data.append(target_field_val)
           lista.set_values(actual_data)
       elif(action=="Modify"):
          old_field=fields_comps["Remove"]
          lista.modif_selected_item(old_field.get_text(),target_field_val)
       elif(action=="Remove"):
          new_list=[]
          for i in range(0,len(actual_data)):
             if(actual_data[i]!=target_field_val):
                new_list.append(actual_data[i])
          lista.set_values(new_list) 
       for key in fields_comps:
          field=fields_comps[key]
          fields_comps[key].set_text("")
       
    
    #Update a Format File in the Server (Upload Modified File and Update Format Source On Data Base)
    @classmethod 
    def finish_update_formato(cls,archivo,usr,vent):
        url=constantes.SERVER+"upload.php"
        user_token=usr.get_credentials()[4]
        import time
        format_name=cls.data_process["Formatos"]["Format_Id"]
        with open(archivo,"rb") as temp_file:
           dict_file={"file":temp_file}
           data_sendFormat={"token":user_token,"timestamp":str(int(time.time())),"format_type":format_name}
           response=requests.post(url,files=dict_file,data=data_sendFormat)
        if(response.status_code>400):
           General.show_error("error al actualizar datos","error inesperado")
           os.remove(archivo)
           return 
        res=response.text
        if(res.startswith("Error")):
            General.show_error(res,"Update Format Error")
            return
        conexion_bd.set_tabla(constantes.TABLA_FORMATO)
        cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[format_name],"conditions_Verify":["="]}              
        conexion_bd.update_data({"src_form":res.strip()},cond_data)
        os.remove(archivo)
        time_object=tiempo()
        usr.add_action_historial(["modificacion de formato",time_object.get_tiempo()])
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=f"report_{usr.user}_{time_object.get_full_time_str()}"
        data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar formato","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist,True)
        General.show_message("actualizacion del contenido del formato realizada exitsamente","actualizacion exitosa")
        vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO1,usr)
        cls.clear_data_process()
        
    #Request Update a Modified format file From Format Gestion of Planification Process    
    @classmethod 
    def update_formato(cls,vent):
        pnl=vent.panelActual
        filename_source=cls.data_process["Formatos"]["Source"]
        url=constantes.SERVER+filename_source
        response=requests.get(url)
        if(response.status_code>400):
            General.show_error("error obteniendo data del servidor","error de data del server")
            return
        if(General.show_confirmDialog("modificar el contenido del formato?","modificar formato")!=True):
            return 
        old_file=filename_source.split("/")[1]               
        lista=pnl.get_comp_byName("cols_list")
        valores=lista.get_all_values()
        reference=cls.data_process["Formatos"]["Reference_Text"]
        row=cls.data_process["Formatos"]["Row_Requerid"]      
        data=[valores,reference,row,vent.panelActual_str]
        file_dat=[response.content,old_file]
        documento.request(vent.raiz,file_dat,constantes.REQUEST_MODIFIC_EXCEL,data)
        
    #Verify if Finish The Cronogram or Academic Moments When an User Loggin
    @classmethod
    def verify_expired_dates(cls,usr,vent):
        time_object=tiempo()
        user_type=usr.get_credentials()[2]
        
        #Change Academic Moments Status if is Neccesary
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        moms=conexion_bd.get_allData([constantes.CLAVE_MOMENTO,"abierto","culminado","fecha_inicio","fecha_limite","hora_limite"],None,None,True)
        for moment in moms:
           target_moment=moment[constantes.CLAVE_MOMENTO]
           open_mom=moment["abierto"]
           finished=moment["culminado"]
           limite=moment["fecha_limite"]
           if(open_mom=="true" and finished=="false"):
             if(time_object.is_previous(time_object.get_fecha(),limite)==True):
                continue
             #Active Moment Finish
             conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
             cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moment[constantes.CLAVE_MOMENTO]],"conditions_Verify":["="]} 
             conexion_bd.update_data({"abierto":"false","culminado":"true"},cond_data,None,True)
                           
           elif(open_mom=="false" and finished=="false"):
               #Moment Waiting for Activation
               inicio=moment["fecha_inicio"]
               if(time_object.is_previous(inicio,time_object.get_fecha(),False)==True):
                  conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                  cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moment[constantes.CLAVE_MOMENTO]],"conditions_Verify":["="]} 
                  conexion_bd.update_data({"abierto":"true"},cond_data,None,True)
                              
           elif(open_mom=="true" and finished=="true"):
               #Inactive Moments Reactivate for a Short Lapse of Time
               inactivate_conditions=[False,False]
               if(time_object.is_previous(moment["fecha_limite"],time_object.get_fecha(),False)):
                    inactivate_conditions[0]=True
               if(time_object.is_previous_time(moment["hora_limite"],time_object.get_tiempo())):
                    inactivate_conditions[1]=True
               if(inactivate_conditions[0]==True and inactivate_conditions[1]==True):        
                    cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[moment[constantes.CLAVE_MOMENTO]],"conditions_Verify":["="]} 
                    conexion_bd.update_data({"abierto":"false"},cond_data,None,True)
         
        #Permit Remove Cronogram if it is Finished  
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cronogs=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"cierre"],None,None,True)
        if(len(cronogs)<=0 or (user_type!="admin" and user_type!="coordinador")==True):
            return
        fecha_culminado=cronogs[0]["cierre"]
        if(time_object.is_previous(time_object.get_fecha(),fecha_culminado)==True ):
           return
        if(General.show_confirmDialog("cronograma finalizado,desea borrarlo?","borrar cronograma")==False):
            return
        if(cls.reset_cronogram(usr,vent,cronogs[0][constantes.CLAVE_CRONOGRAMA])<0):    
           return
        General.show_message("Cronograma Borrado Exitosamente","Cronograma Borrado")
        
         
        
             