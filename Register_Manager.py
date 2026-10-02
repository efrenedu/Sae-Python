from General import General
from conexion_bd import conexion_bd
from tiempo import tiempo
from constantes import constantes
from validator_manager import Register_Validator
import requests
import os

#Manage the Operations Required for the Registers of System
class Register_Manager:

    
                   
    #Register or Update the Data for Disponibilty of TimeTables for Workers
    @classmethod
    def registrar_dispHorario(cls,user,vent,update=False):
        pnl=vent.panelActual
        data_verify={}
        combos=pnl.get_comps_byTag("combo")
        lista=pnl.get_comp_byName("lista_personal")
        turno=pnl.get_comp_byTag("radio")
        time_object=tiempo()
        data_verify["Worker"]=lista.get_selected_value()
        days={"L":"lunes","M":"martes","Mi":"miercoles","J":"jueves","V":"viernes"}
        day_disp={"disp_lunes":["",""],"disp_martes":["",""],"disp_miercoles":["",""],"disp_jueves":["",""],"disp_viernes":["",""]}
        
        for comp in combos:
           id=comp.get_id()
           val=comp.get_selected_value()
           target_day=""
           if(id.startswith("desde_")):
              target_day=id.split("desde_")[1]
              target_day=days[target_day]
              day_disp[f"disp_{target_day}"][0]=val
           elif(id.startswith("hasta_")):
             target_day=id.split("hasta_")[1]
             target_day=days[target_day]
             day_disp[f"disp_{target_day}"][1]=val
             
        data_verify["Days"]=day_disp
        res_validation=Register_Validator.validate_timeTables_Disponibility(data_verify,update)
        if(res_validation[0]==False):
            return
            
        data={}
        data[constantes.CLAVE_TRABAJADOR]=res_validation[1]
        data["turno"]=turno.get_selected_value()
        data["modificado"]=time_object.get_fecha()
        for key in day_disp:
           val=day_disp[key]
           data[key]="-".join(val)

        if(General.show_confirmDialog("registrar disponibilidad de horario?","registrar")!=True):
           return
        if(update==False):
             #Update the Register
             data[constantes.CLAVE_DISP_HORARIO]=f"Disponibility-{data[constantes.CLAVE_TRABAJADOR]}"
             conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
             cond_data={"conditions_Names":[constantes.CLAVE_DISP_HORARIO],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_DISP_HORARIO]],"conditions_Verify":["="]}              
             data_hors=conexion_bd.get_allData([constantes.CLAVE_DISP_HORARIO],cond_data,None,True)
             if(len(data_hors)>0):
                      General.show_message("El Trabajador ya tiene una Disp Horario Registrada","Disp ya Existente")
                      return
                
             conexion_bd.add_data(data)
             user.add_action_historial(["registro de desiponib. horario",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","disponib. horario","",time_object.get_fecha()]
             res_add=conexion_bd.add_data(data_hist,True)
             if(res_add<0):
                return
             General.show_message("Disponibilidad de Horario Registrada Satisfactoriamente","registro exitoso")
             vent.update_pantallas(constantes.PANTALLA_WELCOME,user)               
        else:
             #Make the Register
             conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
             cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
             data_hors=conexion_bd.get_allData([constantes.CLAVE_DISP_HORARIO],cond_data,None,True)
             if(len(data_hors)<=0):
                 General.show_error("Error Obteniendo Data de la Disp Horario del Trabajador","Error")
                 return
             data[constantes.CLAVE_DISP_HORARIO]=data_hors[0][constantes.CLAVE_DISP_HORARIO]
             vals_update={"turno":data["turno"],"disp_lunes":data["disp_lunes"],"disp_martes":data["disp_martes"],"disp_miercoles":data["disp_miercoles"],"disp_jueves":data["disp_jueves"],"disp_viernes":data["disp_viernes"],"modificado":time_object.get_fecha()}
             cond_data={"conditions_Names":[constantes.CLAVE_DISP_HORARIO],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_DISP_HORARIO]],"conditions_Verify":["="]}              
             conexion_bd.update_data(vals_update,cond_data)
             user.add_action_historial(["actualizar disponib. horario",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","disponib. horario","",time_object.get_fecha()]
             res_add=conexion_bd.add_data(data_hist,True)
             if(res_add<0):
                return
             General.show_message("disponibilidad de horario actualizada satisfactoriamente","registro exitoso")
             vent.update_pantallas(constantes.PANTALLA_WELCOME,user) 
        
    #Register or Update a Format
    @classmethod
    def registrar_formato(cls,user,vent,update=False):
       from event_manager import Event_manager
       user_token=user.get_credentials()[4]
       import time
       pnl=vent.panelActual
       fields=pnl.get_comps_byTag("field")
       valido=0
       time_object=tiempo()
       data={constantes.CLAVE_FORMATO:"","src_form":"","modificado":time_object.get_fecha()}
       combo=pnl.get_comp_byTag("combo") 
       new_formatName_comp=pnl.get_comp_byName("nombre_val")
       src_comp=pnl.get_comp_byName("destino_file")
       if(src_comp==None or combo==None or new_formatName_comp==None):
          General.show_error("Error Obteniendo Datos del Formulario","Error de Interfaz")
          return
       data_verify={}
       new_format=new_formatName_comp.get_text()
       format_name=combo.get_selected_value()   
       src_value=src_comp.get_text()
       data_verify["Format"]=format_name
       data_verify["Src"]=src_value
       data_verify["New_Format"]=new_format
       
       if(Register_Validator.validate_format_data(data_verify,update)==False):
          return
          
       data[constantes.CLAVE_FORMATO]= format_name if format_name!="nuevo" else new_format
       data["src_form"]=src_value
       if(update==False): 
            if(General.show_confirmDialog("registrar formato?","registrar")!=True):
               return
            url=constantes.SERVER+"upload.php"
            with open(data["src_form"],"rb") as temp_file:
               files={'file':temp_file}
               format_type_send=data[constantes.CLAVE_FORMATO].replace("ñ","n")
               data_sendFormat={"token":user_token,"timestamp":str(int(time.time())),"format_type":format_type_send}
               response=requests.post(url,files=files,data=data_sendFormat)
               res=response.text.strip()
               data["src_form"]=res 
               if(data["src_form"].startswith("formato")==False):
                   General.show_error(res,"Error")
                   return 
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            conexion_bd.add_data(data)
            user.add_action_historial(["registrar formato",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","formato","",time_object.get_fecha()]
            res_add=conexion_bd.add_data(data_hist,True) 
            if(res_add<0):
                return
            General.show_message("formato registrado satisfactoriamente","registro exitoso" )     
            vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
             if(General.show_confirmDialog("Modificar archivos del formato?","modificar")!=True):
               return

             if(data["src_form"].startswith("formatos")==False):
                #is local file 
                url=constantes.SERVER+"upload.php"
                with open(data["src_form"],"rb") as temp_file:
                    files={'file':temp_file}
                    format_type_send=data[constantes.CLAVE_FORMATO].replace("ñ","n")
                    data_sendFormat={"token":user_token,"timestamp":str(int(time.time())),"format_type":format_type_send}
                    response=requests.post(url,files=files,data=data_sendFormat)
                    res=response.text.strip()
                    data["src_form"]=res 
                    if(data["src_form"].startswith("formato")==False):
                         General.show_error(res,"Error")
                         return                         
             id_form=data[constantes.CLAVE_FORMATO]             
             conexion_bd.set_tabla(constantes.TABLA_FORMATO)
             values={"src_form":data["src_form"],"modificado":data["modificado"]}
             cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_FORMATO]],"conditions_Verify":["="]}              
             conexion_bd.update_data(values,cond_data)
             user.add_action_historial(["actualizar formato",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","formato","",time_object.get_fecha()]
             res_add=conexion_bd.add_data(data_hist,True)
             if(res_add<0):
                 return 
             General.show_message("formato actualizado satisfactoriamente","registro exitoso" )     
             vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       
  
    #Register a Calification
    @classmethod
    def registrar_calificacion(cls,user,vent):  
       from estudiante import estudiante
       from event_manager import Event_manager
       from validator_manager import Process_Validator_Manager
       from Process_Manager import Process_Manager
       
       pnl=vent.panelActual
       valido=0  
       calif_comp=pnl.get_comp_byName("calific_val")
       calif_val=""
       if(calif_comp==None):
          General.show_error("Faltan Componentes de Entrada de Usuario","Componentes Faltantes")
          return
       calif_val=calif_comp.get_text() 
       data_estud=Process_Manager.get_data_process()["Estudiante"]
       data_estud["Calification"]=calif_val
       
       if(Process_Validator_Manager.validate_calification_Gestion(data_estud,"Register")==False):
          return
       if(General.show_confirmDialog("registrar Nueva Calificacion?","registrar")!=True):
          return   
       time_object=tiempo()
       estud=estudiante()
       res=estud.new_calific(data_estud,time_object.get_fecha())
       if(res==True):
          user.add_action_historial(["registro de calificacion",time_object.get_tiempo()])
          conexion_bd.set_tabla(constantes.TABLA_REPORTE)
          id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
          data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","nueva calificacion","Registro de Evaluacion",time_object.get_fecha()]
          conexion_bd.add_data(data_hist,True)
          tabl=pnl.get_comp_byName("table_califics")
          fields=pnl.get_comps_byTag("field")
          for fld in fields:
             fld.set_text("")
          tabl.On_load()
          General.show_message("calificacion registrada satisafactoriamente","calificacion registrada")       
          action_comp=pnl.get_comp_byName("Action_List")
          if(action_comp!=None):
             action_comp.set_selected_index(0)
             action_comp.On_select(None)
      
    
    #Replace Old Formation Area Name by the New Area Name Required by Register of Formation Area
    @classmethod
    def replace_area_name(cls,area_data,original_area_name):
        #Modify Id of Formation Area
        conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
        cond_data={"conditions_Names":[constantes.CLAVE_AREA_FORMACION],"condition_Types":["and"],"conditions_Values":[original_area_name],"conditions_Verify":["="]}              
        old_dat=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],cond_data,None,True)
        if(len(old_dat)<=0):
           General.show_message("Error Obteniendo Datos del Area de Formacion","Error")
           return False
        next_data=area_data
        next_data[constantes.CLAVE_AÑOS_INCORPORADOS]=old_dat[0][constantes.CLAVE_AÑOS_INCORPORADOS]
        res_add=conexion_bd.add_data(next_data,True)
        if(res_add<0):
           return False
        conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
        conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:next_data[constantes.CLAVE_AREA_FORMACION]},cond_data)
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:next_data[constantes.CLAVE_AREA_FORMACION]},cond_data)
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:next_data[constantes.CLAVE_AREA_FORMACION]},cond_data)
        conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
        res=conexion_bd.delete_data(cond_data,None,True)
        if(res<0):
           return False
           
    #Register or Update a Formation Area
    @classmethod
    def registar_area(cls,user,vent,update=False):
       pnl=vent.panelActual
       id_comp=pnl.get_comp_byName("area_ra")
       list_areas=pnl.get_comp_byName("areas")
       checks=pnl.get_comps_byTag("check")
       selected_area=""
       time_object=tiempo()
       incorp_radioBtn=pnl.get_comp_byName("incorporada")
       if(list_areas==None or id_comp==None or incorp_radioBtn==None or checks==None):
         General.show_error("Error Obteniendo Datos del Formulario","UI Error")
         return
       data_disp_areas={constantes.CLAVE_AÑOS_INCORPORADOS:"","1_año":"","2_año":"","3_año":"","4_año":"","5_año":"","modificado":time_object.get_fecha()}
       data={constantes.CLAVE_AREA_FORMACION:"","incorporada":"",constantes.CLAVE_AÑOS_INCORPORADOS:"","modificado":time_object.get_fecha()}
        
       incorporada="Si" if update==False else incorp_radioBtn.get_selected_value()  
       selected_area=list_areas.get_selected_value()
       new_id_Area=id_comp.get_text()
       years_disp=0
       for i in range(0,len(checks)):
           val="True" if checks[i].is_selected() else "False"
           data_disp_areas[str(i+1)+"_año"]=val
           if(val=="True"):
               years_disp+=1
       
       data_verify={"Area":selected_area,"Num_Years":years_disp,"Change_AreaName":new_id_Area}
       if(Register_Validator.validate_formation_area_data(data_verify)==False):
          return
       data[constantes.CLAVE_AREA_FORMACION]=new_id_Area
       data["incorporada"]=incorporada
              
       if(update==False):
               if(General.show_confirmDialog("registrar area de formacion?","registrar")!=True):
                   return
               conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
               data_disp_areas[constantes.CLAVE_AÑOS_INCORPORADOS]=conexion_bd.generate_id(True,constantes.CLAVE_AÑOS_INCORPORADOS)
               conexion_bd.add_data(data_disp_areas)
               data[constantes.CLAVE_AÑOS_INCORPORADOS]=data_disp_areas[constantes.CLAVE_AÑOS_INCORPORADOS]
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               conexion_bd.add_data(data)
               user.add_action_historial(["registro de area de formacion",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","area form.","",time_object.get_fecha()]
               res_add=conexion_bd.add_data(data_hist,True) 
               if(res_add<0):
                  return
               General.show_message("Area de Formacion Registrada Satisfactoriamente","registro exitoso")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
               if(General.show_confirmDialog("actualizar area de formacion?","actualizar")!=True):
                 return
                 
               if(data[constantes.CLAVE_AREA_FORMACION]!=selected_area):
                  if(cls.replace_area_name(data,selected_area)==False):
                       return
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)       
               cond_data={"conditions_Names":[constantes.CLAVE_AREA_FORMACION],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_AREA_FORMACION]],"conditions_Verify":["="]}              
               fields_values={"incorporada":data["incorporada"],"modificado":time_object.get_fecha()}
               join_data={}
               query_fields={}
               for key in data_disp_areas:
                 if(key==constantes.CLAVE_AÑOS_INCORPORADOS):
                    continue
                 query_fields[key]=data_disp_areas[key]
               join_data["años_incorporados"]={"query_field":query_fields,"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":None}

               conexion_bd.update_data(fields_values,cond_data,join_data)
               user.add_action_historial(["actualizar area de formacion",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","area form.","",time_object.get_fecha()]
               res_add=conexion_bd.add_data(data_hist,True) 
               if(res_add<0):
                  return
                  
               General.show_message("area de formacion actualizada satisfactoriamente","actualizacion exitosa")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       
    #Register or Update a timeTable for a Worker or Section
    @classmethod
    def registrar_horario(cls,user,vent,update=False):
        time_object=tiempo()
        pnl=vent.panelActual
        user_token=user.get_credentials()[4]
        import time
        data={constantes.CLAVE_HORARIO:"","src_hor":"","turno":"","modificado":time_object.get_fecha()}
        destinatario=""
        src_comp=pnl.get_comp_byName("destino_file")
        combos=pnl.get_comps_byTag("combo")
        if(src_comp==None or combos==None):
           General.show_error("Error Obteniendo Datos del Formulario","UI Error")
           return
      
        valido=0
        is_worker=False
        data_verify={}
        for_worker=False
        worker=""
        section=""
        
        for comp in combos:
           if(comp.get_state==False):
               continue
           value=comp.get_selected_value()
           id=comp.get_id()
           if(id=="tipo_rh"):
               data_verify["Type"]=value
           elif(id=="turno_rh"):
               data_verify["turno"]=value
           elif(id=="secc_rh"):
               data_verify["section_value"]=value
           elif(id=="personal_rh"):
               data_verify["worker_value"]=value
        data_verify["src"]=src_comp.get_text()
        res= Register_Validator.validate_timetable_data(data_verify)
        if(res[0]==False):
            return
        is_worker=res[1]
          
        id_name=""
        id_target=""
        tabla_dest=""
        if(is_worker):
          tabla_dest=constantes.TABLA_TRABAJADOR
          id_name=constantes.CLAVE_TRABAJADOR
          temp_val=data_verify["worker_value"].split("-")
          id_t=""
          if(len(temp_val)==3):
            id_t=temp_val[0]+"-"+temp_val[1]
          if(id_t==""):
             General.show_error("Error en Formato de Id del Trabajdor","Error")
             return
          id_target=id_t  
        else:
           tabla_dest=constantes.TABLA_SECCION
           id_name=constantes.CLAVE_SECCION
           id_target= data_verify["section_value"]   
         
           
        conexion_bd.set_tabla(constantes.TABLA_HORARIO)
        data["src_hor"]=data_verify["src"]
        data["turno"]=data_verify["turno"]
         
        if(update==False):
            #Register
            filename=data["src_hor"].split("/")
            data[constantes.CLAVE_HORARIO]=f"Horario{tabla_dest}_{id_target}"
            if(General.show_confirmDialog("registrar horario?","registrar")!=True):
                return    
            url=constantes.SERVER+"upload_horarios.php"
            data_file={"token":user_token,"timestamp":str(int(time.time())),"Identificador":"Horario-"+id_target,"formato":"pdf"}
            with open(data["src_hor"],"rb") as temp_file:                
                  files={'file':temp_file}
                  response=requests.post(url,files=files,data=data_file)
                  res=response.text.strip()
                  data["src_hor"]=res
            conexion_bd.add_data(data)
            conexion_bd.set_tabla(tabla_dest)
            cond_data={"conditions_Names":[id_name],"condition_Types":["and"],"conditions_Values":[id_target],"conditions_Verify":["="]}              
            conexion_bd.update_data({constantes.CLAVE_HORARIO:data[constantes.CLAVE_HORARIO],"modificado":time_object.get_fecha()},cond_data)
            user.add_action_historial(["registrar horario",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","horario","",time_object.get_fecha()]
            res_add=conexion_bd.add_data(data_hist,True)
            if(res_add<0):
                return            
            General.show_message("registro del horarior realizado satisfactoriamente","horario registrado")
            vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
        else:
            #Update
            conexion_bd.set_tabla(tabla_dest)
            cond_data={"conditions_Names":[id_name],"condition_Types":["and"],"conditions_Values":[id_target],"conditions_Verify":["="]}              
            dat_hor=conexion_bd.get_allData([constantes.CLAVE_HORARIO],cond_data,None,True)
            if(len(dat_hor)<=0):
               General.show_error("Error Obteniendo Datos de la Seccion","Error")
               return
            data[constantes.CLAVE_HORARIO]=dat_hor[0][constantes.CLAVE_HORARIO]  
              
            if(General.show_confirmDialog("actualizar horario?","actualizar")!=True):
                return
            
            conexion_bd.set_tabla(constantes.TABLA_HORARIO)
            if(data["src_hor"].startswith("horarios")==False):
                data_file={"token":user_token,"timestamp":str(int(time.time())),"Identificador":"Horario-"+id_target,"formato":"pdf"} 
                url=constantes.SERVER+"upload_horarios.php"
                with open(data["src_hor"],"rb") as temp_file:                
                     files={'file':temp_file}
                     response=requests.post(url,files=files,data=data_file)
                     res=response.text.strip()
                     data["src_hor"]=res
            values_fields={"src_hor":data["src_hor"],"turno":data["turno"],"modificado":time_object.get_fecha()}
            cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[data[constantes.CLAVE_HORARIO]],"conditions_Verify":["="]}              
            conexion_bd.update_data(values_fields,cond_data)
            user.add_action_historial(["actualizar horario",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","horario","",time_object.get_fecha()]
            res_add=conexion_bd.add_data(data_hist,True)
            if(res_add<0):
               return
            General.show_message("Actualizacion del horarior realizado satisfactoriamente","horario registrado")
            vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
     
     
    #Upload Expedent to Server
    @classmethod
    def upload_expedent(cls,user_token,data_worker,data_expedent):
        import time
        zip_name=""
        id_worker=data_worker[constantes.CLAVE_TRABAJADOR]        
        #Upload Expedent
        if(data_expedent["src_exp"].startswith("expedientes/")==False and data_expedent["src_exp"]!=""):
           url=constantes.SERVER+"upload_expediente.php"
           filename=data_expedent["src_exp"]
           fail_upload=False
           zip_name=os.path.basename(data_expedent["src_exp"])  
           with open(filename,"rb") as temp_file:                
                  files={'file':temp_file}
                  data_send={"token":user_token,"timestamp":str(int(time.time()))}
                  response=requests.post(url,files=files,data=data_send)
                  res=response.text.strip()
                  data_expedent["src_exp"]=res
                  if(res.startswith("expedientes/")==False):
                      data_expedent["src_exp"]="..."
                      fail_upload=True
           if(os.path.exists(filename)):
               os.remove(filename)                          
           if(fail_upload):
              return False

        #Remove Remanent Zip File   
        if(os.path.exists(constantes.FOLDER_DOCUMENTS+zip_name) and zip_name!=""):
            os.remove(constantes.FOLDER_DOCUMENTS+zip_name)                     
        
                   
        #Upload Photo
        if(data_expedent["src_foto"].startswith("fotos/")==False and data_expedent["src_foto"]!=""):
           url=constantes.SERVER+"upload_foto.php"
           format_foto=""
           file_photo=data_expedent["src_foto"]
           with open(file_photo,"rb") as temp_photo:          
                dict_foto={"file":temp_photo}
                data_foto={"token":user_token,"timestamp":str(int(time.time())),"identificador":"Worker_"+id_worker,"format":format_foto,"target":"Worker"}   
                respond=requests.post(url,files=dict_foto,data=data_foto)          
                res=respond.text.strip()
                data_expedent["src_foto"]=res
                if(res.startswith("fotos/")==False):
                    data_expedent["src_foto"]="..."
                    return False       
        return True                   
    
    #Update or Register the Profesor Data of Worker if is Neccesary
    @classmethod
    def update_profesor_data(cls,is_teacher,data_worker,areas_teacher,update):
        time_object=tiempo()
        if(update==False and is_teacher==True):
              conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
              data_prof={constantes.CLAVE_PROFESOR:conexion_bd.generate_id(True,constantes.CLAVE_PROFESOR),constantes.CLAVE_TRABAJADOR:data_worker[constantes.CLAVE_TRABAJADOR],"seccion_guia":"default","modificado":time_object.get_fecha()}
              conexion_bd.add_data(data_prof) 
              conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
              for i in range(0,len(areas_teacher)):
                  data_areas={constantes.CLAVE_AREA_DOCENTE:data_prof[constantes.CLAVE_PROFESOR]+"-"+areas_teacher[i],constantes.CLAVE_PROFESOR:data_prof[constantes.CLAVE_PROFESOR],constantes.CLAVE_AREA_FORMACION:areas_teacher[i],"modificado":time_object.get_fecha()}
                  conexion_bd.add_data(data_areas)
        else:
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           initial_teacher=False
           if(conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,data_worker[constantes.CLAVE_TRABAJADOR])==True):
              initial_teacher=True
           if(initial_teacher==False and is_teacher==True):
                conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
                data_prof={constantes.CLAVE_PROFESOR:conexion_bd.generate_id(True,constantes.CLAVE_PROFESOR),constantes.CLAVE_TRABAJADOR:data_worker[constantes.CLAVE_TRABAJADOR],"seccion_guia":"default","modificado":time_object.get_fecha()}
                conexion_bd.add_data(data_prof) 
                conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
                for i in range(0,len(areas_teacher)):
                    data_areas={constantes.CLAVE_AREA_DOCENTE:data_prof[constantes.CLAVE_PROFESOR]+"-"+areas_teacher[i],constantes.CLAVE_PROFESOR:data_prof[constantes.CLAVE_PROFESOR],constantes.CLAVE_AREA_FORMACION:areas_teacher[i],"modificado":time_object.get_fecha()}
                    conexion_bd.add_data(data_areas)       
           elif(initial_teacher==True and is_teacher==False):
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)     
               cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data_worker[constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
               data_prof=conexion_bd.get_allData([constantes.CLAVE_PROFESOR],cond_data,None,True)       
               if(len(data_prof)<=0):
                  General.show_error("Error Obteniendo Data del Profesor","Error")
                  return False
               cond_data={"conditions_Names":[constantes.CLAVE_PROFESOR],"condition_Types":["and"],"conditions_Values":[data_prof[0][constantes.CLAVE_PROFESOR]],"conditions_Verify":["="]}              
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               conexion_bd.delete_data(cond_data)
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)   
               conexion_bd.delete_data(cond_data)
           elif(initial_teacher==True and is_teacher==True):
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)     
               cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data_worker[constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
               data_prof=conexion_bd.get_allData([constantes.CLAVE_PROFESOR],cond_data,None,True)       
               if(len(data_prof)<=0):
                  General.show_error("Error Obteniendo Data del Profesor","Error")
                  return False
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               cond_data={"conditions_Names":[constantes.CLAVE_PROFESOR],"condition_Types":["and"],"conditions_Values":[data_prof[0][constantes.CLAVE_PROFESOR]],"conditions_Verify":["="]}              
               conexion_bd.delete_data(cond_data)
               for i in range(0,len(areas_teacher)):
                   data_areas={constantes.CLAVE_AREA_DOCENTE:data_prof[0][constantes.CLAVE_PROFESOR]+"-"+areas_teacher[i],constantes.CLAVE_PROFESOR:data_prof[0][constantes.CLAVE_PROFESOR],constantes.CLAVE_AREA_FORMACION:areas_teacher[i],"modificado":time_object.get_fecha()}
                   conexion_bd.add_data(data_areas)                 
        return True
                         
       
    #Get the Data of Worker Register Form  as a Dict 
    @classmethod
    def get_regiser_worker_data(cls,comps):
        res={}
        res["cargo_ministerio"]=comps["Cargo Ministerio"].get_selected_value()
        res["cargo"]=comps["Cargo"].get_selected_value()
        res["estatus"]=comps["Estatus"].get_selected_value()
        worker=comps["List_Workers"].get_selected_value()
        cedula=comps["Cedula"].get_text()
        nacionalidad=comps["Nacionalidad"].get_selected_value()
        nacionalidad="V" if nacionalidad.lower()=="venezolano" else "E"
        cedula=f"{nacionalidad}-{cedula}"
        selected_id=""
        selected_nacionalidad=""
        
        if(worker!="nuevo"):
          work_data=worker.split("-")
          selected_id=work_data[1]
          selected_nacionalidad=work_data[0]
          
        
        res["cedula"]=cedula
        res["Selected_worker"]=[selected_id,selected_nacionalidad]
        res["fecha_ingreso"]=comps["Fecha Ingreso"].get_text()
        res["Areas"]=comps["Areas"].get_all_values()
        fields_list=comps["Fields"]
        for field in fields_list:
           id=field.get_id()
           val=field.get_text()
           if(id=="cedula"):
              continue
           res[id]=val.strip()
        return res
       
       
    #Assign the Verified Values from Worker Register Form and return it as a Dictionary of Dictionaries
    @classmethod
    def assign_verified_data(cls,data_verified,update):
       time_object=tiempo()
       data_estatus={constantes.CLAVE_ESTATUS_TRABAJ:"","estatus":"","service_years":"","fecha_ingreso":"","modificado":time_object.get_fecha()}
       data_nombre={constantes.CLAVE_NOMBRE:"","nombre":"","s_nombre":"","apellido":"","s_apellido":"","modificado":time_object.get_fecha()}
       data={constantes.CLAVE_TRABAJADOR:"",constantes.CLAVE_NOMBRE:"","correo":"","telefono":"",constantes.CLAVE_EXPEDIENTE:"",constantes.CLAVE_HORARIO:"default",constantes.CLAVE_CARGO:"",constantes.CLAVE_ESTATUS_TRABAJ:"","modificado":time_object.get_fecha()}
       data_exp={constantes.CLAVE_EXPEDIENTE:"","src_exp":"...","src_foto":"...","fecha_registro":time_object.get_fecha(),"modificado":time_object.get_fecha()}
       data_cargo={constantes.CLAVE_CARGO:"","cargo":"","cargo_ministerio":"","codigo_cargo":"","modificado":time_object.get_fecha()}
       areas_selected=[]
       
       #Assign Worker Data
       data[constantes.CLAVE_TRABAJADOR]=data_verified["cedula"]
       data["correo"]=data_verified["correo"]
       data["telefono"]=data_verified["telefono"]
       
       #Assign Expedent Data
       data_exp["src_exp"]=data_verified["destino_file"]
       data_exp["src_foto"]=data_verified["destino_foto"]
       
       #Assign Name Data
       temp_name=data_verified["nombre"].split(" ")
       fields_name=["nombre","s_nombre"]
       for i in range(0,len(temp_name)):
          data_nombre[fields_name[i]]=temp_name[i]
       temp_name=data_verified["apellido"].split(" ")
       fields_name=["apellido","s_apellido"]
       for i in range(0,len(temp_name)):
          data_nombre[fields_name[i]]=temp_name[i]
       
       #Assign Cargo Data
       data_cargo["cargo"]=data_verified["cargo"]
       data_cargo["cargo_ministerio"]=data_verified["cargo_ministerio"]
       data_cargo["codigo_cargo"]=data_verified["cargo_cod"]
       
       #Assign Status Data
       data_estatus["estatus"]="activo" if update==True else data_verified["estatus"]
       data_estatus["fecha_ingreso"]=data_verified["fecha_ingreso"]
       year_ing=int(data_verified["fecha_ingreso"].split("/")[2])
       actual_year=int(time_object.get_fecha().split("/")[2])
       dif=actual_year-year_ing
       service_years=str(dif)
       data_estatus["service_years"]=service_years
       
       res={constantes.TABLA_TRABAJADOR:data,constantes.TABLA_NOMBRE:data_nombre,constantes.TABLA_EXPEDIENTE:data_exp,constantes.TABLA_ESTATUS_TRABAJ:data_estatus,constantes.TABLA_CARGO:data_cargo}
       return res
       
    
    #Modify the Nacionality of a Worker if is Neccesary
    @classmethod
    def modify_nacionality(cls,user_token,dat_worker,new_nacionality,initial_worker_id):
       if(new_nacionality.lower()!="venezolano"):
           return True
       temp_dat=initial_worker_id.split("-")
       initial_worker_id=temp_dat[1]
       initial_nacionality=temp_dat[0]
       if(initial_nacionality!="E"):
          return True
       valor_id=dat_worker[constantes.CLAVE_TRABAJADOR]
       initial_worker_id=f"{initial_nacionality}-{initial_worker_id}"
       conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
       id_exist=conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,valor_id)
       if(id_exist==True):
            General.show_message("no se puede modificar la cedula del trabajador por una ya existente","cedula ya existente")
            return False
       cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[initial_worker_id],"conditions_Verify":["="]}                             
       old_dat_work=conexion_bd.get_allData([],cond_data,None,True)
       if(len(old_dat_work)<=0):
           General.show_error("Error Obteniendo Datos del Trabajador","Error")
           return False
       next_data=old_dat_work[0]
       next_data[constantes.CLAVE_TRABAJADOR]=valor_id
       conexion_bd.add_data(next_data)       
       join_data={}
       join_data["profesor"]={"query_field":{constantes.CLAVE_TRABAJADOR:valor_id},"share_fields":{"field":constantes.CLAVE_TRABAJADOR,"table_reference":"trabajador"},"Conditions_join":None}
       join_data["disponibilidad_horario"]={"query_field":{constantes.CLAVE_TRABAJADOR:valor_id},"share_fields":{"field":constantes.CLAVE_TRABAJADOR,"table_reference":"trabajador"},"Conditions_join":None}
       join_data["descarga_documentos"]={"query_field":{constantes.CLAVE_TRABAJADOR:valor_id},"share_fields":{"field":constantes.CLAVE_TRABAJADOR,"table_reference":"trabajador"},"Conditions_join":None}          
       if(conexion_bd.update_data({},cond_data,join_data,True)<0):
          return False
       url=constantes.SERVER+"change_user_worker.php"
       import time
       import json
       data_send={"token_user":user_token,"timestamp":str(int(time.time())),"old_worker":old_dat_work[0][constantes.CLAVE_TRABAJADOR],"new_worker":next_data[constantes.CLAVE_TRABAJADOR]}   
       respond=requests.post(url,data=data_send)          
       json_content=json.loads(respond.content)
       if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return False   
       if(conexion_bd.delete_data(cond_data,None,True)<0):
           return False                       
       return True
       
    #Register or Update a worker
    @classmethod
    def registrar_trabajador(cls,user,vent,update=False):
       from event_manager import Event_manager
       user_token=user.get_credentials()[4]
       pnl=vent.panelActual
       time_object=tiempo()
       
       fields=pnl.get_comps_byTag("field")
       cedula_comp=pnl.get_comp_byName("cedula")
       list_works=pnl.get_comp_byName("empleado")
       nacionalidad_comp=pnl.get_comp_byName("nacionalidad")
       cargo_comp=pnl.get_comp_byName("cargo")
       minist_comp=pnl.get_comp_byName("cargo_minist")
       fecha_ingreso=pnl.get_comp_byName("service_years")
       estatus=pnl.get_comp_byName("estatus")
       areas_list=pnl.get_comp_byTag("list")
       
       comps_form={"Fields":fields,"Cedula":cedula_comp,"List_Workers":list_works,"Nacionalidad":nacionalidad_comp,"Cargo":cargo_comp,"Cargo Ministerio":minist_comp,"Fecha Ingreso":fecha_ingreso,"Estatus":estatus,"Areas":areas_list}
       for key in comps_form:
          if(comps_form[key]==None):
             General.show_error("Error Obteniendo Datos del Formulario","UI Error")
             return
       data_verify=cls.get_regiser_worker_data(comps_form)
       if(Register_Validator.validate_worker_data(data_verify,update)==False):
           return
       
       data_dict=cls.assign_verified_data(data_verify,update)
       dat_worker=data_dict[constantes.TABLA_TRABAJADOR]
       dat_expedent=data_dict[constantes.TABLA_EXPEDIENTE]
       dat_status=data_dict[constantes.TABLA_ESTATUS_TRABAJ]
       dat_name=data_dict[constantes.TABLA_NOMBRE]
       dat_cargo=data_dict[constantes.TABLA_CARGO]
       areas_selected=data_verify["Areas"]
       is_teacher=False
       if(dat_cargo["cargo_ministerio"].startswith("Docente")):
            is_teacher=True
       modify_id=False
       if(General.show_confirmDialog("registrar/Actualizar tarbajador?","registrar")!=True):
            return      
       if(update==False):
               #Register Worker
               if(cls.upload_expedent(user_token,dat_worker,dat_expedent)==False):
                 General.show_message("Error al Subir El Expedient al servidor","Error del Expedient")
                 return
               conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
               dat_expedent[constantes.CLAVE_EXPEDIENTE]=f"ExpedentWorker-{dat_worker[constantes.CLAVE_TRABAJADOR]}"
               conexion_bd.add_data(dat_expedent)
               dat_worker[constantes.CLAVE_EXPEDIENTE]=dat_expedent[constantes.CLAVE_EXPEDIENTE]
               
               conexion_bd.set_tabla(constantes.TABLA_CARGO)
               dat_cargo[constantes.CLAVE_CARGO]=f"CargoWorker-{dat_worker[constantes.CLAVE_TRABAJADOR]}"
               conexion_bd.add_data(dat_cargo)
               dat_worker[constantes.CLAVE_CARGO]=dat_cargo[constantes.CLAVE_CARGO]
               
               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
               dat_name[constantes.CLAVE_NOMBRE]=f"NameWorker-{dat_worker[constantes.CLAVE_TRABAJADOR]}"
               conexion_bd.add_data(dat_name)
               dat_worker[constantes.CLAVE_NOMBRE]=dat_name[constantes.CLAVE_NOMBRE]
               conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
               dat_status[constantes.CLAVE_ESTATUS_TRABAJ]=f"StatusWorker-{dat_worker[constantes.CLAVE_TRABAJADOR]}"
               dat_status["estatus"]="activo"
               conexion_bd.add_data(dat_status)
               dat_worker[constantes.CLAVE_ESTATUS_TRABAJ]=dat_status[constantes.CLAVE_ESTATUS_TRABAJ]
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               conexion_bd.add_data(dat_worker)
               if(cls.update_profesor_data(is_teacher,dat_worker,areas_selected,update)==False):
                     return  
               user.add_action_historial(["registro de personal",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","personal","",time_object.get_fecha()]
               if(conexion_bd.add_data(data_hist,True)<0):
                  return
               General.show_message("registro exitoso del personal","registro exitoso")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
                #Update Worker
                if(cls.modify_nacionality(user_token,dat_worker,nacionalidad_comp.get_selected_value(),list_works.get_selected_value())==False):
                    return
                
                if(cls.upload_expedent(user_token,dat_worker,dat_expedent)==False):
                    General.show_message("Error al Subir El Expedient al servidor","Error del Expedient")
                    return   
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[dat_worker[constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
                join_data={}
                join_data["expediente"]={"query_field":{"src_exp":dat_expedent["src_exp"],"src_foto":dat_expedent["src_foto"],"modificado":dat_expedent["modificado"]},"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"trabajador"},"Conditions_join":None}
                join_data["nombre"]={"query_field":{"nombre":dat_name["nombre"],"s_nombre":dat_name["s_nombre"],"apellido":dat_name["apellido"],"s_apellido":dat_name["s_apellido"],"modificado":dat_name["modificado"]},"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None}
                join_data["cargo"]={"query_field":{"cargo":dat_cargo["cargo"],"cargo_ministerio":dat_cargo["cargo_ministerio"],"codigo_cargo":dat_cargo["codigo_cargo"],"modificado":dat_cargo["modificado"]},"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None}
                join_data["estatus_trabaj"]={"query_field":{"estatus":dat_status["estatus"],"service_years":dat_status["service_years"],"fecha_ingreso":dat_status["fecha_ingreso"],"modificado":dat_status["modificado"]},"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":None}
                fields_modify={"correo":dat_worker["correo"],"telefono":dat_worker["telefono"],"modificado":dat_worker["modificado"]}
                conexion_bd.update_data(fields_modify,cond_data,join_data)
                
                if(cls.update_profesor_data(is_teacher,dat_worker,areas_selected,update)==False):
                    return                
                user.add_action_historial(["actualizar personal",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","personal","",time_object.get_fecha()]
                if(conexion_bd.add_data(data_hist,True)<0):
                   return
                General.show_message("actualizacion exitosa del personal","actualizacion exitosa")
                vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
      