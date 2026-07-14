from constantes import constantes

#trigger the Events Required for UI Components
class UI_Event:

   #verify the Types of Events from Table and trigger the required Events
   @classmethod
   def interprete_Table_Event(cls,ev_type,comp_id,ev_value,comp_value):
      if(ev_type=="Load"):
         cls.interprete_Table_LoadEvent(comp_id,ev_value)
      else:
         cls.interprete_Table_SelectEvent(comp_id,ev_value,comp_value)
   
   #Trigger the Event when a Table Load
   @classmethod
   def interprete_Table_LoadEvent(cls,comp_id,ev_value):
       from conexion_bd import conexion_bd
       from event_manager import Event_manager
       comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
       panel_id=Event_manager.vent.panelActual_str
       if(comp==None):
           return   
       if(ev_value==constantes.TABLE_LOAD_DATA_GESTION_USUARIOS):
           if(panel_id!=constantes.PANTALLA_SERVICIO_GESTION_USUARIO):
              return
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           flds=[constantes.CLAVE_USUARIO,"password",constantes.CLAVE_TRABAJADOR,"nivel_acceso",constantes.CLAVE_INTENTOS_USUARIO,"bloqueado"]
           data=conexion_bd.get_allData(flds,len(flds))
           comp.reset()
           conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)        
           for i in range(0,len(data)):
              temp_data=[]
              for j in range(0,len(data[i])):
                  if(j!=4):
                     temp_data.append(data[i][j])
                  else:
                    data_intentos=conexion_bd.get_allData(["num_intentos"],1,[constantes.CLAVE_INTENTOS_USUARIO],[data[i][4]],["and"])
                    temp_data.append(data_intentos[0][0])   
              if(temp_data[3]!="admin"):
                  passw=temp_data[1]
                  new_pass=""
                  for k in range(0,len(passw)):
                      new_pass=new_pass+'*'
                  temp_data[1]=new_pass
                  comp.add_row(temp_data)
       elif(ev_value==constantes.TABLE_LOAD_DATA_CALIFICATIONS_STUDENTS):  
             dat_rend=Event_manager.user.get_data_process()[0]
             conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
             dat_calif=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],dat_rend[4]],["and","and","and"])
             if(dat_calif==[]):
                comp.reset()
                value_momento=["","","",""]
                value_momento[0]="promedio: 5.0 pts"
                value_momento[1]="calificacion: 05 pts "
                value_momento[2]="estimulacion: 0 pts"
                value_momento[3]="definitiva: 0 pts"
                posibles=["calific_m_p1_1","calific_m_p1_2","calific_m_p1_3","calific_m_p1_4"]
                for i in range(0,len(posibles)):
                    Event_manager.set_comp_values(posibles[i],value_momento[i])
                return   
             id_calif=dat_calif[0][0]
             conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
             dat_calif_mom=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_calif,dat_rend[2]],["and","and"])
             comp.reset()
             if(dat_calif_mom!=[]):
               conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
               califications=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM],[dat_calif_mom[0][0]],["and"])
               if(califications!=[]):
                   for i in range(0,len(califications)):
                       dat_row=[califications[i][3], dat_rend[1],dat_rend[2],califications[i][2]]
                       comp.add_row(dat_row) 
               conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
               data_area_actual=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_MOMENTO],[dat_rend[0],dat_rend[1],dat_rend[2]],["and","and","and"])
               value_momento=["","","",""]
               value_momento[0]="promedio:\n"+dat_calif_mom[0][3]+"pts"
               value_momento[1]="calificacion:\n"+dat_calif_mom[0][4]+"pts"
               value_momento[2]="pts estimulacion:\n"+dat_calif_mom[0][5]+"pts"
               str_definitive=str(int(dat_calif_mom[0][4] )+int(dat_calif_mom[0][5]))
               if(len(str_definitive)<2):
                   str_definitive="0"+str_definitive
               value_momento[3]="definitiva:\n"+str_definitive+"pts"  
               posibles=["calific_m_p1_1","calific_m_p1_2","calific_m_p1_3","calific_m_p1_4"]
               for i in range(0,len(posibles)):
                    Event_manager.set_comp_values(posibles[i],value_momento[i])
             else:
                 value_momento=["","","",""]
                 value_momento[0]="promedio:"
                 value_momento[1]="calificacion:"
                 value_momento[2]="pts estimulacion:"
                 value_momento[3]="definitiva:"
                 posibles=["calific_m_p1_1","calific_m_p1_2","calific_m_p1_3","calific_m_p1_4"]
                 for i in range(0,len(posibles)):
                     Event_manager.set_comp_values(posibles[i],value_momento[i])

   
   #Trigger the Event when Select a Item On the Table
   @classmethod
   def interprete_Table_SelectEvent(cls,comp_id,ev_value,comp_value):
        from conexion_bd import conexion_bd
        from event_manager import Event_manager
        if(ev_value==constantes.TABLE_LOAD_DATA_CALIFICATIONS_STUDENTS):
           data=comp_value
           if(data!=" "):
             if(len(data)>0):
                 Event_manager.set_comp_values("calific_num_p2",data[0])

        elif(ev_value==constantes.TABLE_SET_DATA_DEFINITIVE_CALIFICATION_STUDENT):
             data=comp_value
             if(data!=" "):
               if(len(data)>0):
                  Event_manager.set_comp_values("area",data[0])
                  Event_manager.set_comp_values("year",data[1])
                  Event_manager.set_comp_values("calif","")
          
            
   #verify the type of event from List Box and trigger the required event
   @classmethod
   def interprete_ListBox_Event(cls,ev_type,comp_id,ev_value,comp_value):
       if(ev_type=="Load"):
          cls.interprete_ListBox_Load_Event(comp_id,ev_value,comp_value)
       else:
          cls.interprete_ListBox_Select_Event(comp_id,ev_value,comp_value)
    
   #trigger the events required when Load a List Box
   @classmethod
   def interprete_ListBox_Load_Event(cls,comp_id,ev_value,comp_value):
         from conexion_bd import conexion_bd
         from event_manager import Event_manager
         comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
         if(comp==None):
            return   
         if(ev_value==constantes.LISTBOX_SET_WORKERS_USERS_CANDIDATOS_DATA or ev_value==constantes.LISTBOX_SET_WORKERS_DATA):
             conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
             res=conexion_bd.get_allData(None,None)
             data=[]
             for i in range(0,len(res)):
                if(ev_value==constantes.LISTBOX_SET_WORKERS_USERS_CANDIDATOS_DATA):
                   cargo=res[i][7]
                   if(cargo=="coordinador" or cargo=="secretaria" or cargo=="sub director" or cargo=="director"):
                      data.append(res[i][1])
                else:
                  data.append(res[i][1])
             if(data!=[]):
                  comp.set_values(data)
         elif(ev_value==constantes.LISTBOX_SET_LIST_USERS_DATA):
             conexion_bd.set_tabla(constantes.TABLA_USUARIO)
             res=conexion_bd.get_allData(None,None)
             data=[]
             for i in range(0,len(res)):
                 if(res[i][0]!="admin"):
                    data.append(res[i][0])
             if(data!=[]):
                  comp.set_values(data)
          
         elif(ev_value==constantes.LISTBOX_SET_DATA_FORMATO):
           conexion_bd.set_tabla(constantes.TABLA_FORMATO)
           res=conexion_bd.get_allData(None,None)
           data=[]
           if(res!=[]):
               for i in range(0,len(res)):
                     data.append(res[i][0])
           comp.set_values(data)
           
   #trigger the events required when select a item in a List Box
   @classmethod
   def interprete_ListBox_Select_Event(cls,comp_id,ev_value,comp_value):
        from conexion_bd import conexion_bd
        from event_manager import Event_manager
        comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
        panel_id=Event_manager.vent.panelActual_str
        if(comp==None):
            return 
        if(comp_value==" " and (ev_value==constantes.LISTBOX_SET_WORKERS_DATA and panel_id==constantes.PANTALLA_REGISTRO_DISP_HORARIO)==False):
           return
           
        if(ev_value==constantes.LISTBOX_SET_WORKERS_DATA):
           
            comp.last_selected=comp_value
            Event_manager.activar_element("caja2",True)
            Event_manager.activar_element("caja3",True)
            if(panel_id==constantes.PANTALLA_REGISTRO_DISP_HORARIO):
              Event_manager.set_comp_values("personal_selected",comp.last_selected)
        elif(ev_value==constantes.LISTBOX_SET_AREAS_FORMACION_DISPONIBLES_DOCENTES):
                
           comp.last_selected=comp_value
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           name=comp_value.split(" ")
           id_worker=""
           id_worker=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),["nombre","apellido"],[name[0],name[1]],["and","and"])[0][0]
           if(id_worker!=None and id_worker!=""):
              conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
              areas=conexion_bd.get_allData(constantes.CAMPOS_AREA_DOCENTE,len( constantes.CAMPOS_AREA_DOCENTE),[constantes.CLAVE_TRABAJADOR],[id_worker],["and"])             
              if(areas==[]):
                 return
              data_areas=["elegir"]
              for i in range(0,len(areas)):
                 data_areas.append(areas[i][2])
              Event_manager.set_comp_values("areas_disponibles",data_areas)
        
        elif(ev_value==constantes.LISTBOX_SET_DATA_FORMATO):
            
           comp.last_selected=comp_value
           conexion_bd.set_tabla(constantes.TABLA_FORMATO)
           id_format=comp_value
           data_format=conexion_bd.get_allData(constantes.CAMPOS_FORMATO,len(constantes.CAMPOS_FORMATO),[constantes.CLAVE_FORMATO],[id_format],["and"])
           if(data_format==[]):
              return
           file_format=""
           if(data_format[0][1].endswith(".pdf")==True):
              file_format="PDF"
           else:
              file_format="XLSX"
           Event_manager.user.reset_data_process(0)
           Event_manager.user.recibe_data_process([id_format,data_format[0][0],file_format,data_format[0][1]])
           Event_manager.set_comp_values("form_field",data_format[0][0])
           Event_manager.set_comp_values("type_field",file_format)
        elif(ev_value==constantes.LISTBOX_SET_VALUE_TO_REMOVE_COLUMN_FORMATO):
            if(comp_id.endswith("2")):
               Event_manager.set_comp_values("val_delete_col2",comp_value)
            else:            
              Event_manager.set_comp_values("val_delete_col",comp_value)
        elif(ev_value==constantes.LISTBOX_SET_STUDENT_DATA_SELECTED): 
            Event_manager.set_comp_values("estud",comp_value)
        elif(ev_value==constantes.LISTBOX_SET_STUDENT_INTERCAMBIO_DATA_SELECTED):
            Event_manager.set_comp_values("estud_intercambio",comp_value)
        elif(ev_value==constantes.LISTBOX_SET_FIELD_TO_REMOVE_FORMATO):
            Event_manager.set_comp_values("field_delete",str(comp.get_selected_index()[0])+"-"+comp_value) 
                   
   
   #trigger the events required for Text Fields
   @classmethod 
   def interprete_TextField_Events(cls,comp_id,ev_value,comp_value):
        from conexion_bd import conexion_bd
        from event_manager import Event_manager
        comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
        panel_id=Event_manager.vent.panelActual_str
        if(comp==None):
            return    
        if(ev_value==constantes.TEXFIELD_SET_FOLDER_RESPALDO_BD_TEXT):
            if(panel_id==constantes.PANTALLA_SERVICIO_RESPALDO_BD and comp_id!="destino_file"):
                 comp.set_text(constantes.FOLDER_RESPALDOS)
            comp.set_state("readonly")
            comp.field_state="readonly"
        elif(ev_value==constantes.TEXTFIELD_DISABLED):
               comp.set_state("disabled")
               comp.field_state="disabled"
        elif(ev_value==constantes.TEXTFIELD_DISABLED_AND_SET_TEXT_ZERO):
              comp.set_state("disabled")  
              comp.set_text("0")
              comp.field_state="disabled"
        elif(ev_value==constantes.TEXTFIELD_READONLY):
            comp.set_state("readonly")
            comp.field_state="readonly"
        elif(ev_value==constantes.TEXTFIELD_ACTIVATE_ON_LOAD):
            comp.set_state("normal")
            comp.field_state="normal"  
            
   #trigger the events of Labels
   @classmethod
   def interprete_label_Events(cls,comp_id,ev_value,comp_value):
        from conexion_bd import conexion_bd
        from event_manager import Event_manager
        comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
        if(comp==None):
            return
        if(ev_value==constantes.LABEL_LOAD_WORKER_SELECTED_INFO):
            if(comp_id=="personal_selected"):
                comp.set_text("Sin seleccionar")
            else:
              comp.set_text("")
        elif(ev_value==constantes.LABEL_LOAD_HISTORIAL_INFO):
            data_historial=Event_manager.user.get_historia()
            new_text="Sin Actividad Reciente"
            if(data_historial!=[]):
                new_text=""
                for i in range(0,len(data_historial)):
                    if(i<=3):
                        new_text=new_text+" "+data_historial[i][0]+","+data_historial[i][1]+"\n"
                    else:
                        break              
            comp.set_text(new_text)                            
        elif(ev_value==constantes.LABEL_LOAD_CRONOGRAM_INFO):
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           data_cronog=conexion_bd.get_allData(None,None)
           if(data_cronog!=[]):
                comp.set_text("Año Escolar: "+data_cronog[0][0])
           else:
               comp.set_text("Año Escolar: ")
        
   
   #verify the type of event from Combobox and trigger the required event
   @classmethod
   def interprete_Combobox_Event(cls,ev_type,comp_id,ev_value,comp_value,state_comp):
       if(ev_type=="Load"):
          cls.interprete_Combobox_LoadEvent(comp_id,ev_value,state_comp)
       else:
          cls.interprete_Combobox_SelectEvent(comp_id,ev_value,comp_value)
    
   #trigger the events required when select a item in a ComboBox
   @classmethod
   def interprete_Combobox_SelectEvent(cls,comp_id,ev_value,comp_value):
       from conexion_bd import conexion_bd
       from event_manager import Event_manager
       comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
       panel_id=Event_manager.vent.panelActual_str
       if(comp==None):
            return
       if(ev_value>=constantes.COMBOBOX_SHOW_AREAS_FORMACION_DOCENTES and ev_value<=constantes.COMBOBOX_LOAD_WORKERS_HORARIOS):
          if(ev_value==constantes.COMBOBOX_SHOW_AREAS_FORMACION_DOCENTES):
              if(comp_value.lower()!="obrero" and comp_value.lower()!="secretaria" and comp_value!="elejir" and comp_value!="elegir"):
                 Event_manager.activar_element("caja_areas",True)
                 Event_manager.activar_element("caja3_rp",True)
              else:
                Event_manager.activar_element("caja_areas",False)
                Event_manager.activar_element("caja3_rp",False)           
          elif(ev_value==constantes.COMBOBOX_LOAD_DATA_AUDITORIA_STADITICAS):
             if(panel_id==constantes.PANTALLA_SERVICIO_AUDITORIA):
                valor=comp_value
                if(valor=="campo clave" or valor=="antes de" or valor=="despues de"):
                     Event_manager.activar_element("fecha2",False,True)
                     Event_manager.activar_element("fecha1",True,True)
                     Event_manager.activar_element("label_dateFrom",True,True)
                     Event_manager.activar_element("label_dateTo",False,True)              
                     Event_manager.activar_element("identificador_cp",False,True)
                     Event_manager.set_comp_values("field1","")    
                     if(valor=="campo clave"):
                        Event_manager.set_comp_values("label_dateFrom","valor campo:")                     
                     else:
                        Event_manager.set_comp_values("label_dateFrom","fecha")                     
                elif(valor=="desde - hasta"):
                     Event_manager.activar_element("fecha2",True,True)
                     Event_manager.activar_element("fecha1",True,True)
                     Event_manager.activar_element("label_dateFrom",True,True)
                     Event_manager.activar_element("label_dateTo",True,True)
                     Event_manager.set_comp_values("label_dateFrom","desde")                     
                     Event_manager.set_comp_values("fecha1","")    
                     Event_manager.set_comp_values("fecha2","")  
                     Event_manager.activar_element("identificador_cp",False,True)
                elif(valor=="accion realizada" or valor=="usuario"):
                     Event_manager.activar_element("fecha2",False,True)
                     Event_manager.activar_element("fecha1",False,True)
                     Event_manager.activar_element("label_dateFrom",True,True)
                     Event_manager.activar_element("label_dateTo",False,True)
                     Event_manager.set_comp_values("label_dateFrom","valor") 
                     Event_manager.activar_element("identificador_cp",True,True)
                elif((valor=="elejir" or valor=="elegir") or valor=="no filtrar"):
                     Event_manager.activar_element("fecha2",False,True)
                     Event_manager.activar_element("fecha1",False,True)
                     Event_manager.activar_element("label_dateFrom",False,True)
                     Event_manager.activar_element("label_dateTo",False,True)
                     Event_manager.activar_element("identificador_cp",False,True)
                  
             elif(panel_id==constantes.PANTALLA_SERVICIO_ESTADISTICA):
                   valor=comp_value
                   if(valor=="personal"):
                        new_vals=["elegir","cargo de personal","estatus del personal"]
                        Event_manager.set_comp_values("tipo_estad2",new_vals)
                   elif(valor=="estudiantes"):
                        new_vals=["elegir","tipo de cedula","estatus del estudiante","genero"]
                        Event_manager.set_comp_values("tipo_estad2",new_vals)
                   elif(valor=="matricula"):
                        new_vals=["elegir","año","turno"]
                        Event_manager.set_comp_values("tipo_estad2",new_vals)
                   elif(valor=="secciones"):
                        new_vals=["elegir","cantidad de secciones","turno"]
                        Event_manager.set_comp_values("tipo_estad2",new_vals)
                   elif("estudiantes con materias pendientes"):
                       new_vals=["elegir"]
                       conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                       data_areas=conexion_bd.get_allData(None,None)
                       if(data_areas!=[]):
                          for i in range(0,len(data_areas)):
                             new_vals.append(data_areas[i][0])
                       Event_manager.set_comp_values("tipo_estad2",new_vals)  
          elif(ev_value==constantes.COMBOBOX_SHOW_INFO_MATERIA_PENDIENTE):
            if(panel_id==constantes.PANTALLA_RENDIMIENTO_MAT_PEND): 
               valor=comp_value
               if(valor!="elejir" and valor!="elegir"):
                   conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                   data=Event_manager.user.get_data_process()[0]
                   area=data[1]
                   id_student=data[0]
                   data_pen=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_ESTUDIANTE],[area,id_student],["and","and"])
                   conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                   if(valor!="revision"):
                      mat_Pendent=conexion_bd.get_allData(constantes.CAMPOS_CALIF_PENDIENTE,len(constantes.CAMPOS_CALIF_PENDIENTE),[constantes.CLAVE_MATERIA_PENDIENTE,"intento"],[data_pen[0][0],valor],["and","and"])
                      Event_manager.set_comp_values("fecha_p4","")
                      if(mat_Pendent!=[]):
                        Event_manager.set_comp_values("calif_p4",mat_Pendent[0][3])
                        Event_manager.set_comp_values("fecha_p4",mat_Pendent[0][4])
                      else:
                        Event_manager.set_comp_values("calif_p4","")
                   else:
                      mat_Pendent=conexion_bd.get_allData(constantes.CAMPOS_CALIF_PENDIENTE,len(constantes.CAMPOS_CALIF_PENDIENTE),[constantes.CLAVE_MATERIA_PENDIENTE,"revision"],[data_pen[0][0],valor],["and","and"])
                      Event_manager.set_comp_values("fecha_p4","")
                      if(mat_Pendent!=[]):
                         Event_manager.set_comp_values("calif_p4",mat_Pendent[0][3])
                         Event_manager.set_comp_values("fecha_p4",mat_Pendent[0][4])
                      else:
                         Event_manager.set_comp_values("calif_p4","")
               else:
                   Event_manager.set_comp_values("fecha_p4","")
                   Event_manager.set_comp_values("calif_p4","")
          elif(ev_value==constantes.COMBOBOX_CHANGE_TIMES_DISP_HORARIOS):
             valor=comp_value
             if(valor=="mañana"):
                Event_manager.set_comp_values("table_cell1",[" 7:30-8:05 "," 8:05-8:40 "," 8:40-9:15 "," 9:15-9:50 "," 9:50-10:25","10:25-11:00","11:00-11:35","11:35-12:10"])
                Event_manager.set_comp_values("horas_rh","0")         
             elif(valor=="tarde"):
                Event_manager.set_comp_values("table_cell1",["12:30-1:05 "," 1:05-1:40 "," 1:40-2:15 "," 2:15-2:50 "," 2:50-3:25 "," 3:25-4:00 "," 4:00-4:35 "," 4:35-5:10 "])
                Event_manager.set_comp_values("horas_rh","0")    
             else:
               Event_manager.set_comp_values("table_cell1",["no definido","no definido","no definido","no definido","no definido","no definido","no definido","no definido"])
               Event_manager.set_comp_values("horas_rh","0")
           
          elif(ev_value==constantes.COMBOBOX_GET_FULL_DATA_WORKER_REGISTRO_HORARIOS or ev_value==constantes.COMBOBOX_GET_DATA_SECCION_REGISTRO_HORARIO):
             valor=comp_value
             if(valor=="elejir" or valor=="elegir"):
                Event_manager.activar_element("secc_label",False,True)
                Event_manager.activar_element("secc_rh",False,True)
                Event_manager.activar_element("personal_label",False,True)
                Event_manager.activar_element("personal_rh",False,True)
                Event_manager.activar_element("turno_rh",False,True)
                Event_manager.activar_element("turno_seccion",False,True)
                Event_manager.activar_element("turnoSeccion_label",False,True)
                Event_manager.activar_element("turno_label",False,True)
               
             elif(valor=="seccion"): 
                            
                conexion_bd.set_tabla(constantes.TABLA_SECCION)
                dat_secc=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION))             
                data_field=["elegir"]
                if(dat_secc==[]):
                   return
                for i in range(0,len(dat_secc)):
                    if(dat_secc[i][0]!="default" and ev_value!=constantes.COMBOBOX_GET_DATA_SECCION_REGISTRO_HORARIO):
                       data_field.append(dat_secc[i][0])
                    elif(dat_secc[i][3]!="default" and ev_value== constantes.constantes.COMBOBOX_GET_DATA_SECCION_REGISTRO_HORARIO):
                       data_field.append(dat_secc[i][0])      
                Event_manager.activar_element("secc_label",True,True)
                Event_manager.activar_element("secc_rh",True,True)
                Event_manager.activar_element("personal_label",False,True)
                Event_manager.activar_element("personal_rh",False,True)
                Event_manager.set_comp_values("secc_rh",data_field)
                Event_manager.activar_element("turnoSeccion_label",True,True)
                Event_manager.activar_element("turno_label",False,True)               
                Event_manager.activar_element("turno_seccion",True,True)
                Event_manager.activar_element("turno_rh",False,True)
             else:
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                dat_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR))             
                data_field=["elegir"]
                if(dat_trabaj==[]):
                   return
                for i in range(0,len(dat_trabaj)):
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                    data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[dat_trabaj[i][7]],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                    data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[dat_trabaj[i][1]],["and"])
                    if(dat_trabaj[i][0]!="000" and dat_trabaj[i][0]!="001" and data_estatus[0][0]!="inactivo"):
                        #prevent get data from Admin Default Worker or Inactive workers
                        if(ev_value!=constantes.COMBOBOX_GET_DATA_SECCION_REGISTRO_HORARIO):
                              data_field.append(dat_trabaj[i][0]+"-"+data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize())
                        elif(dat_trabaj[i][5]!="default" and ev_value== constantes.COMBOBOX_GET_DATA_SECCION_REGISTRO_HORARIO):
                             data_field.append(data_nombre[0][0]+" "+data_nombre[0][1])        
                    
                Event_manager.activar_element("secc_label",False,True)
                Event_manager.activar_element("secc_rh",False,True)
                Event_manager.activar_element("personal_label",True,True)
                Event_manager.activar_element("personal_rh",True,True)
                Event_manager.set_comp_values("personal_rh",data_field)
                Event_manager.activar_element("turnoSeccion_label",False,True)
                Event_manager.activar_element("turno_label",True,True)
                Event_manager.activar_element("turno_seccion",False,True)
                Event_manager.activar_element("turno_rh",True,True)
   
          elif(ev_value==constantes.COMBOBOX_SHOW_MODIFICAR_FORMATO_REFERENCE_DATA):
              valor=comp_value
              if(valor=="modificar contenido"): 
                 Event_manager.activar_element("ref_label",True,True)
                 Event_manager.activar_element("referencia",True,True)
              else:
                 Event_manager.activar_element("ref_label",False,True)
                 Event_manager.activar_element("referencia",False,True)                

          elif(ev_value==constantes.COMBOBOX_LOAD_DATA_AREA_FORMACION):
               
               if(comp_value!="elejir" and comp_value!="elegir" and comp_value!="nueva"):
                  conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                  data_areas=conexion_bd.get_allData(constantes.CAMPOS_AREA_FORMACION,len(constantes.CAMPOS_AREA_FORMACION),[constantes.CLAVE_AREA_FORMACION],[comp_value],["and"])
                  if(data_areas==[]):
                     return
                  conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                  data_in=conexion_bd.get_allData(["1_año","2_año","3_año","4_año","5_año"],5,[constantes.CLAVE_AÑOS_INCORPORADOS],[data_areas[0][2]],["and"])
                  Event_manager.set_comp_values("incorporada",data_areas[0][1])
                  for i in range(0,5):
                     valor=data_in[0][i]
                     if(valor=="True" or valor=="true"):
                         valor=True
                     else:
                         valor=False 
                     Event_manager.set_comp_values("check"+str(i+1),valor)
                  Event_manager.set_comp_values("area_ra",comp_value)
                  Event_manager.activar_element("incorporada",True,True)
                  Event_manager.activar_element("actualizar_ru",True,True)
                  Event_manager.activar_element("registrar_ru",False,True)
                  Event_manager.set_comp_values("incorporada",data_areas[0][1])
                  Event_manager.activar_element("incorporada_Label",True,True)
               else:
                  Event_manager.set_comp_values("incorporada","No")
                  for i in range(0,5):
                      Event_manager.set_comp_values("check"+str(i+1),False)
                  Event_manager.set_comp_values("area_ra","")
                  Event_manager.activar_element("incorporada",False,True)
                  Event_manager.activar_element("actualizar_ru",False,True)
                  Event_manager.activar_element("registrar_ru",True,True)
                  Event_manager.activar_element("incorporada_Label",False,True)  
          elif(ev_value==constantes.COMBOBOX_LOAD_WORKERS_HORARIOS or ev_value==constantes.COMBOBOX_LOAD_WORKERS_DISP_HORARIOS):
              if(comp_value!="elejir" and comp_value!="elegir"):
                  id_temp=comp_value.split("-")
                  if(len(id_temp)==3):
                     id_temp=id_temp[0]+"-"+id_temp[1]
                  elif(len(id_temp)==2):
                      id_temp=id_temp[0]
                  else:
                      id_temp=""
                  conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
                  data_disp=conexion_bd.get_allData(constantes.CAMPOS_DISP_HORARIO,len(constantes.CAMPOS_DISP_HORARIO),[constantes.CLAVE_TRABAJADOR],[id_temp],["and"])
                  if(data_disp!=[]):
                     Event_manager.load_data_disp(id_temp)
                     Event_manager.activar_element("actualizar_rdh",True,True)
                     Event_manager.activar_element("registrar_rdh",False,True)
                  else:
                     Event_manager.load_data_disp("")
                     Event_manager.activar_element("actualizar_rdh",False,True)
                     Event_manager.activar_element("registrar_rdh",True,True)
              else:
                Event_manager.load_data_disp("")
                Event_manager.activar_element("actualizar_rdh",False,True)
                Event_manager.activar_element("registrar_rdh",True,True)
       elif(ev_value>=constantes.COMBOBOX_LOAD_WORKERS_FOR_REGISTER and ev_value<=constantes.COMBOBOX_CHANGE_RESPUESTA_SECRETAS):
          if(ev_value==constantes.COMBOBOX_LOAD_WORKERS_FOR_REGISTER):
              if(comp_value!="elejir" and comp_value!="elegir" and comp_value!="nuevo"):
                 temp_v=comp_value.split("-")
                 valor=""
                 if(len(temp_v)==3):
                     valor=temp_v[0]+"-"+temp_v[1]
                 elif(len(temp_v)==2):
                     valor=temp_v[0]
                
                 Event_manager.activar_element("estatus_label",True,True)
                 Event_manager.activar_element("estatus",True,True)
                 Event_manager.activar_element("actualizar_rp",True,True)
                 Event_manager.activar_element("registrar_rp",False,True)
                 Event_manager.load_data_trabajador(valor)
              else:
                 Event_manager.activar_element("estatus_label",False,True)
                 Event_manager.activar_element("estatus",False,True)
                 Event_manager.activar_element("actualizar_rp",False,True)
                 Event_manager.activar_element("registrar_rp",True,True)
                 Event_manager.activar_element("caja_areas",False,False)
                 Event_manager.activar_element("caja3_rp",False,False)
                 Event_manager.load_data_trabajador("")
           
          elif(ev_value==constantes.COMBOBOX_LOAD_STUDENTS):
             
              if(comp_value!="elejir" and comp_value!="elegir"):
                 valor=comp_value.split("-")
                 if(len(valor)==3):
                    valor=valor[0]+"-"+valor[1]
                 elif(len(valor)==2):
                    valor=valor[0]
                 else:
                    valor=""
                 Event_manager.load_data_estudiante(valor)
              else:
                 Event_manager.load_data_estudiante("")
           
          elif(ev_value==constantes.COMBOBOX_LOAD_SECCION):
               Event_manager.set_comp_values("secc2",[])
               Event_manager.set_comp_values("intercambio",["elegir"])
               Event_manager.set_comp_values("estud","")
               Event_manager.set_comp_values("estud_intercambio","")
               if(comp_value!="elejir" and comp_value!="elegir"):
                  conexion_bd.set_tabla(constantes.TABLA_SECCION)
                  data_secc=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION),[constantes.CLAVE_SECCION],[comp_value],["and"])
                  other_values=["elegir"]
                  if(data_secc!=[]):
                     year=data_secc[0][1]
                     letra=data_secc[0][2]
                     turno=""
                     if(data_secc[0][0].endswith("(M)")):
                         turno="mañana"
                     else:
                        turno="tarde"
                     next_data=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION),["año"],[year],["and"])
                     if(next_data!=[]):
                       for i in range(0,len(next_data)):
                          turno_next=""
                          if(next_data[i][0].endswith("(M)")):
                              turno_next="mañana"
                          else:
                              turno_next="tarde"
                          if(next_data[i][2]!=letra):
                            if(next_data[i][0]!="default"):
                                other_values.append(next_data[i][0])
                          elif( next_data[i][2]==letra and turno_next!=turno):
                             if(next_data[i][0]!="default"):
                                 other_values.append(next_data[i][0])            
                     conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                     data_estuds=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_SECCION],[comp_value],["and"])
                     data_box=[]
                     for j in range(0,len(data_estuds)):
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_estuds[j][1]],["and"])
                        nomb=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                        data_box.append(data_estuds[j][0]+"-"+nomb)
                     Event_manager.set_comp_values("secc1",data_box)
                     conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
                     data_guia=conexion_bd.get_allData(constantes.CAMPOS_PROFESOR,len(constantes.CAMPOS_PROFESOR),["seccion_guia"],[comp_value],["and"])
                     if(data_guia!=[]):
                        id_prof=data_guia[0][1]
                        nomb=""
                        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                        data_temp=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[id_prof],["and"])
                        if(data_temp!=[]):
                          conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                          data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_temp[0][1]],["and"])
                          if(data_nomb!=[]):
                              for nom in data_nomb[0]:
                                 if(nom!=""):
                                     if(nomb==""):
                                          nomb=nom.capitalize()
                                     else:
                                         nomb=nomb+" "+nom.capitalize()
                        valor_prof=id_prof+"-"+nomb
                        Event_manager.set_guia(valor_prof)
                     else:
                         Event_manager.set_guia("elegir")    
                  Event_manager.set_comp_values("intercambio",other_values)   
               else:
                  Event_manager.set_comp_values("secc1",[])
           
          elif(ev_value==constantes.COMBOBOX_SET_DATA_STUDENTES_SECCION):      
              if(comp_value!="elejir" and comp_value!="elegir"):
                  conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                  data_estuds=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_SECCION],[comp_value],["and"])
                  data_box=[]
                  for j in range(0,len(data_estuds)):
                      conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                      data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_estuds[j][1]],["and"])
                      nomb=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                      data_box.append(data_estuds[j][0]+"-"+nomb)
                  Event_manager.set_comp_values("secc2",data_box)
              else:
                  Event_manager.set_comp_values("secc2",[])
           
          elif(ev_value==constantes.COMBOBOX_LOAD_PREGUNTAS_SECRETAS or ev_value==constantes.COMBOBOX_CHANGE_RESPUESTA_SECRETAS):
              num=comp_id[len(comp_id)-1]
              if(comp_value!="elejir" and comp_value!="elegir"):
                 Event_manager.set_respuesta_secr("respuesta"+str(num),"")
              else:
                Event_manager.set_respuesta_secr("respuesta"+str(num),".")
       elif(ev_value>=constantes.COMBOBOX_SHOW_FORMATOS_DESCARGABLE_SECCION and ev_value<=constantes.COMBOBOX_REACTIVATE_MOMENTS_SHOW_OPTION):
        
          if(ev_value==constantes.COMBOBOX_SHOW_FORMATOS_DESCARGABLE_SECCION):
              if(comp_value=="evaluacion continua" or comp_value=="lista de la seccion" or comp_value=="asistencia seccion"):
                Event_manager.activar_element("seccion",True,True)
                Event_manager.activar_element("secc_label",True,True)
                conexion_bd.set_tabla(constantes.TABLA_SECCION)
                data_secc=conexion_bd.get_allData(None,None)
                new_data=["elegir"]
                for i in range(0,len(data_secc)):
                   temp_dat=data_secc[i][0]
                   if(temp_dat!="default"):
                      new_data.append(temp_dat)
                Event_manager.set_comp_values("seccion",new_data)
              else:
                Event_manager.activar_element("secc_label",False,True)
                Event_manager.activar_element("seccion",False,True)
          elif(ev_value==constantes.COMBOBOX_LOAD_LIST_FORMATOS):
               conexion_bd.set_tabla(constantes.TABLA_FORMATO)
               if(comp_value=="nuevo"):
                    Event_manager.activar_element("nombre_val",True,True)
                    Event_manager.activar_element("nombre_val_label",True,True)
                    Event_manager.set_comp_values("nombre_val","") 
               else:
                  Event_manager.set_comp_values("nombre_val","")
                  Event_manager.activar_element("nombre_val",False,True)
                  Event_manager.activar_element("nombre_val_label",False,True)
               if(conexion_bd.id_exist(constantes.CLAVE_FORMATO,comp_value)==True):
                  data_form=conexion_bd.get_allData(["src_form"],1,[constantes.CLAVE_FORMATO],[comp_value],["and"])
                  if(data_form!=[]):
                     Event_manager.set_comp_values("destino_file",data_form[0][0])
                  Event_manager.activar_element("actualizar_ru",True,True)
                  Event_manager.activar_element("registrar_ru",False,True)
               else:
                  Event_manager.activar_element("actualizar_ru",False,True)
                  Event_manager.activar_element("registrar_ru",True,True)
                  Event_manager.set_comp_values("destino_file","")
          elif(ev_value==constantes.COMBOBOX_SET_DATA_HORARIO):
              id_hor=""  
              if(comp_value=="elejir" or comp_value=="elegir"):
                 Event_manager.set_comp_values("destino_file","")
                 Event_manager.set_comp_values("turno_rh-","elegir")
                 Event_manager.activar_element("actualizar",False,True)
                 Event_manager.activar_element("registrar",True,True)
                 Event_manager.set_comp_values("turno_seccion","")
                 return        
              is_seccion=False  
              if(comp_id=="secc_rh"):
                 is_seccion=True
                 conexion_bd.set_tabla(constantes.TABLA_SECCION)
                 id_hor=conexion_bd.get_allData([constantes.CLAVE_HORARIO],1,[constantes.CLAVE_SECCION],[comp_value],["and"])[0][0]
              else:
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                id_temp=comp_value.split("-")
                if(len(id_temp)==3):
                   id_temp=id_temp[0]+"-"+id_temp[1]
                elif(len(id_temp)==2):
                   id_temp=iid_temp[0]
                else:
                   id_temp="" 
                id_hor=conexion_bd.get_allData([constantes.CLAVE_HORARIO],1,[constantes.CLAVE_TRABAJADOR],[id_temp],["and"])[0][0]
              if(id_hor!="" and id_hor!="default"):
                conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                data_hor=conexion_bd.get_allData(constantes.CAMPOS_HORARIO,len(constantes.CAMPOS_HORARIO),[constantes.CLAVE_HORARIO],[id_hor],["and"])
                if(data_hor!=[]):
                   val_hor=data_hor[0][1]
                   if(val_hor=="..."):
                      val_hor=""
                   Event_manager.set_comp_values("destino_file",val_hor)
                   if(is_seccion==False):
                       Event_manager.set_comp_values("turno_rh-",data_hor[0][2])
                   else:
                       Event_manager.set_comp_values("turno_seccion",data_hor[0][2])
                   Event_manager.activar_element("actualizar",True,True)
                   Event_manager.activar_element("registrar",False,True)
                else:
                   Event_manager.set_comp_values("destino_file","")
                   Event_manager.set_comp_values("turno_rh-","elegir")
                   Event_manager.activar_element("actualizar",False,True)
                   Event_manager.activar_element("registrar",True,True)
              else:
                   Event_manager.set_comp_values("destino_file","")
                   Event_manager.set_comp_values("turno_rh-","elegir")
                   Event_manager.activar_element("actualizar",False,True)
                   Event_manager.activar_element("registrar",True,True)
          elif(ev_value==constantes.COMBOBOX_LOAD_SECCION_RENDIMIENTO):
               
               if(comp_value!="elejir" and comp_value!="elegir"):
                   conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                   data_estuds=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_ESTUD],3,[constantes.CLAVE_SECCION],[comp_value],["and"])             
                   new_data=["elegir"]
                   for estuds in data_estuds:
                      conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                      data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estuds[2]],["and"])
                      if(data_estatus[0][0]!="inactivo" and data_estatus[0][0]!="graduado"):
                          val=estuds[0]+"-"
                          conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                          data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[estuds[1]],["and"])
                          val=val+data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                          new_data.append(val)
                   Event_manager.set_comp_values("estudiantes",new_data)
                   conexion_bd.set_tabla(constantes.TABLA_SECCION)
                   data_seccion=conexion_bd.get_allData(["año"],1,[constantes.CLAVE_SECCION],[comp_value],["and"])
                   Event_manager.set_comp_values("year",data_seccion[0][0])   
               else:
                   new_data=["elegir"]
                   Event_manager.set_comp_values("estudiantes",new_data)
                   Event_manager.set_comp_values("year","")
                   Event_manager.search_estud("","")
          elif(ev_value==constantes.COMBOBOX_SET_STUDENT_DATA_RENDIMIENTO):      
              if(comp_value!="elejir" and comp_value!="elegir"):
                  temp_val=comp_value.split("-")
                  cedula=""
                  nombre=""
                  if(len(temp_val)==3):
                     cedula=temp_val[0]+"-"+temp_val[1]
                     nombre=temp_val[2]
                  elif(len(temp_val)==2):
                     cedula=temp_val[0]
                     nombre=temp_val[1]
                  Event_manager.search_estud(cedula,nombre)
              else:
                 Event_manager.search_estud("","")
          elif(ev_value==constantes.COMBOBOX_LOAD_SECCION_RENIDMIENTO_FILTER_MATERIA_PENDIENTE):
               if(comp_value!="elejir" and comp_value!="elegir"):
                  conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                  data_estuds=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_ESTUD],3,[constantes.CLAVE_SECCION],[comp_value],["and"])             
                  new_data=["elegir"]
                  for estuds in data_estuds:
                     conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                     data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estuds[2]],["and"])
                     if(data_estatus[0][0]!="inactivo" and data_estatus[0][0]!="graduado"):
                        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                        data_pend=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[estuds[0]],["and"])
                        if(data_pend!=[]):
                           val=estuds[0]+"-"
                           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                           data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[estuds[1]],["and"])
                           val=val+data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                           new_data.append(val)
                  Event_manager.set_comp_values("estudiantes",new_data)
                  conexion_bd.set_tabla(constantes.TABLA_SECCION)
                  data_seccion=conexion_bd.get_allData(["año"],1,[constantes.CLAVE_SECCION],[comp_value],["and"])
                  Event_manager.set_comp_values("year",data_seccion[0][0])     
               else:
                   new_data=["elegir"]
                   Event_manager.set_comp_values("estudiantes",new_data)
                   Event_manager.set_comp_values("year","")
                   Event_manager.search_estud("","")
          elif(ev_value==constantes.COMBOBOX_SET_DATA_CRONOGRAMA):
               valor=comp_value
               if(comp_value=="crear cronograma" or comp_value=="editar cronograma"):
                  Event_manager.activar_element("inicio_label",True,True)
                  Event_manager.activar_element("cierre_label",True,True)
                  Event_manager.activar_element("inicio",True,True)
                  Event_manager.activar_element("cierre",True,True)
                  if(comp_value=="editar cronograma"):
                    conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                    dat_cronog=conexion_bd.get_allData(None,None)
                    if(dat_cronog!=[]):
                        Event_manager.set_comp_values("inicio",dat_cronog[0][1])
                        Event_manager.set_comp_values("cierre",dat_cronog[0][2])       
                  else:
                     from tiempo import tiempo
                     time_object=tiempo()
                     date_time=time_object.get_inicio_clases()
                     year_time=time_object.get_fecha().split("/")[2]
                     year_escol=year_time+"-"+str(int(year_time)+1)
                     Event_manager.set_comp_values("inicio",date_time)
                     Event_manager.set_comp_values("año_escolar",year_escol)
                     Event_manager.set_comp_values("cierre","xx/xx/xxxx")       
               else:
                  Event_manager.activar_element("inicio_label",False,True)
                  Event_manager.activar_element("cierre_label",False,True)
                  Event_manager.activar_element("inicio",False,True)
                  Event_manager.activar_element("cierre",False,True)
          elif(ev_value==constantes.COMBOBOX_REACTIVATE_MOMENTS_SHOW_OPTION):
            if(comp_value!="elegir" and comp_value!="elejir"):
                conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                dat=conexion_bd.get_allData([constantes.CLAVE_MOMENTO,"abierto"],2,[constantes.CLAVE_MOMENTO],[comp_value],["and"])
                if(dat!=[]):
                    mom_val=dat[0][1]
                    if(mom_val=="false"):
                        Event_manager.activar_element("reactivar",True,True)
                        Event_manager.activar_element("reestablecer",False,True)
                    else:
                        Event_manager.activar_element("reactivar",False,True)
                        Event_manager.activar_element("reestablecer",True,True)    
            else:
                Event_manager.activar_element("reactivar",True,True)
                Event_manager.activar_element("reestablecer",False,True)
                              
   #trigger the events required when load a ComboBox
   @classmethod
   def interprete_Combobox_LoadEvent(cls,comp_id,ev_value,state):
        from conexion_bd import conexion_bd
        from event_manager import Event_manager
        comp=Event_manager.vent.panelActual.get_comp_byName(comp_id)
        panel_id=Event_manager.vent.panelActual_str
        if(comp==None):
            return
            
        
        if(ev_value>=constantes.COMBOBOX_LOAD_AREA_FORMACION and ev_value<=constantes.COMBOBOX_LOAD_WORKERS_HORARIOS):
        
           if(ev_value==constantes.COMBOBOX_LOAD_AREA_FORMACION):
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               data=conexion_bd.get_allData(None,None)
               vals=["elegir"]
               for i in range(0,len(data)):
                   vals.append(data[i][0])
               comp.set_values(vals)
           elif(ev_value==constantes.COMBOBOX_LOAD_DATA_AUDITORIA_STADITICAS and panel_id==constantes.PANTALLA_SERVICIO_ESTADISTICA):
               #load the data for stadistics
               comp.On_select(None)
           elif(ev_value==constantes.COMBOBOX_LOAD_MOMENTOS_ACADEMICOS ):
              Event_manager.verificar_caudicidad()
              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
              data=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),["abierto"],["true"],["and"])
              if(data==[]):
                 return
              vals=["elegir"]
              for i in range(0,len(data)):
                 vals.append(data[i][0])
              comp.set_values(vals)
           elif(ev_value==constantes.COMBOBOX_LOAD_WORKERS_USERS or ev_value==constantes.COMBOBOX_LOAD_WORKERS_DISP_HORARIOS or ev_value==constantes.COMBOBOX_LOAD_WORKERS_HORARIOS):
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               data=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR))
               new_dat=["elegir"]
               
               if(data!=[]):
                 for i in range(0,len(data)):
                    if(ev_value==constantes.COMBOBOX_LOAD_WORKERS_USERS):
                      if(data[i][0]!="000" and data[i][0]!="001"):
                        #prevent to include the worker assign to default admin
                        conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                        if(conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,data[i][0])==False): 
                            cargo_id=data[i][6] 
                            conexion_bd.set_tabla(constantes.TABLA_CARGO)
                            data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[cargo_id],["and"])                      
                            if(data_cargo!=[]):
                              cargo=data_cargo[0][1].lower()
                              if(cargo=="secretaria" or cargo=="director" or cargo.startswith("subdirector") or cargo.startswith("sub director") or cargo=="coordinador de evaluacion"):
                                  conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                                  data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data[i][1]],["and"])
                                  new_dat.append(data[i][0]+"-"+data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize())
                    else:
                        conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                        data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_TRABAJ,len(constantes.CAMPOS_ESTATUS_TRABAJ),[constantes.CLAVE_ESTATUS_TRABAJ],[data[i][7]],["and"])
                        conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
                        if(data[i][0]!="000" and data[i][0]!="001" and data_estatus[0][1]!="inactivo"):
                           #prevent include the worker assign to default admin or inactive workers
                           if(ev_value!=constantes.COMBOBOX_LOAD_WORKERS_HORARIOS):
                              conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                              data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data[i][1]],["and"])
                              new_dat.append(data[i][0]+"-"+data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize())
                           else:
                             id_temp=data[i][0]
                             dat_disponibility=conexion_bd.get_allData(constantes.CAMPOS_DISP_HORARIO,len(constantes.CAMPOS_DISP_HORARIO),[constantes.CLAVE_TRABAJADOR],[id_temp],["and"])
                             if(dat_disponibility!=[]):
                               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                               data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data[i][1]],["and"])
                               new_dat.append(data[i][0]+"-"+data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize())
               comp.set_values(new_dat)
           elif(ev_value==constantes.COMBOBOX_REMOVE_ALL_ITEMS_ON_LOAD): 
                new_dat=["elegir"]
                comp.set_values(new_dat)  
           elif(ev_value==constantes.COMBOBOX_LOAD_DATA_AREA_FORMACION):
               #load the list of 'Areas de Formacion' in the Register in they Panel
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               data_areas=conexion_bd.get_allData(None,None)
               new_data=["nueva"]
               for i in range(0,len(data_areas)):
                  new_data.append(data_areas[i][0])
               comp.set_values(new_data)   
        elif(ev_value>=constantes.COMBOBOX_LOAD_WORKERS_FOR_REGISTER and ev_value<=constantes.COMBOBOX_REACTIVATE_MOMENTS_SHOW_OPTION):
           if(ev_value==constantes.COMBOBOX_LOAD_WORKERS_FOR_REGISTER):
               #carga lista de trabajadores en pantalla de registro de trbajadores
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR))
               new_data=["nuevo"]
               for i in range(0,len(data_trabaj)):
                   if(data_trabaj[i][0]!="000" and data_trabaj[i][0]!="001" ):
                     #prevent to include the worker assign to the default admin
                     conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                     data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_trabaj[i][1]],["and"])
                     nombre=data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize()   
                     new_data.append(data_trabaj[i][0]+"-"+nombre)
               comp.set_values(new_data)    
           elif(ev_value==constantes.COMBOBOX_LOAD_STUDENTS):
               Event_manager.load_estuds_combobox()
           elif(ev_value==constantes.COMBOBOX_LOAD_SECCION):
              conexion_bd.set_tabla(constantes.TABLA_SECCION)
              data_secc=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION))
              new_data=["elegir"]
              for i in range(0,len(data_secc)):
                 if(data_secc[i][0]!="default"):
                    new_data.append(data_secc[i][0])
              comp.set_values(new_data)
           elif(ev_value==constantes.COMBOBOX_LOAD_PROFESORES):
              conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
              data_prof=conexion_bd.get_allData(constantes.CAMPOS_PROFESOR,len(constantes.CAMPOS_PROFESOR))
              new_data=["elegir"]
              for i in range(0,len(data_prof)):
                 conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                 id_prof=data_prof[i][1]
                 nomb=""
                 data_temp=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[id_prof],["and"])
                 if(data_temp!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                    data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_temp[0][1]],["and"])
                    nomb=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                 new_data.append(id_prof+"-"+nomb)
              comp.set_values(new_data)
           elif(ev_value==constantes.COMBOBOX_LOAD_PREGUNTAS_SECRETAS):
              num=comp_id[len(comp_id)-1]
              conexion_bd.set_tabla(constantes.TABLA_PREGUNTA_SECRETA)
              dat=conexion_bd.get_allData(["pregunta","respuesta"],2,[constantes.CLAVE_USUARIO,"numero"],[Event_manager.user.user,str(num)],["and","and"])
              if(dat!=[]):
                  comp.set_value(dat[0][0])
                  Event_manager.set_respuesta_secr("respuesta"+str(num),dat[0][1])
              else:
                 comp.set_selected_index(0)
                 Event_manager.set_respuesta_secr("respuesta"+str(num),".")      
           elif(ev_value==constantes.COMBOBOX_LOAD_WORKERS_CARNETS_AND_CONSTANCIAS):
               #workers for 'constancias' or 'carnets'
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               data_t=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_TRABAJ],3)
               new_data=["elegir"]
               for i in range(0,len(data_t)):
                  clave_estatus=data_t[i][2]
                  clave_nombre=data_t[i][1]
                  id_t=data_t[i][0]
                  if(id_t!="000" and id_t!="001"):
                      conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                      data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[clave_estatus],["AND"])
                      if(data_estatus!=[]):
                          if(data_estatus[0][0]!="inactivo"):
                              conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                              data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[clave_nombre],["AND"])
                              if(data_nomb!=[]):
                                  new_val=id_t+"-"+data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize()
                                  new_data.append(new_val)
               comp.set_values(new_data)
           elif(ev_value==constantes.COMBOBOX_LOAD_SECCION_RENDIMIENTO or ev_value==constantes.COMBOBOX_LOAD_SECCION_RENIDMIENTO_FILTER_MATERIA_PENDIENTE):
              #carga secciones para las pantallas del rendimiento
              conexion_bd.set_tabla(constantes.TABLA_SECCION)
              data_secciones=conexion_bd.get_allData([constantes.CLAVE_SECCION,"total_estud"],2)
              new_data=["elegir"]
              for secc in data_secciones:
                 if(secc[0]!="default"):
                     if(int(secc[1])>0):
                        valido=True
                        if(ev_value==constantes.COMBOBOX_LOAD_SECCION_RENIDMIENTO_FILTER_MATERIA_PENDIENTE):
                           #prevent add students with 'materia pendientes' to the list
                           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                           estuds=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],1,[constantes.CLAVE_SECCION],[secc[0]],["and"])
                           conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                           num_pendientes=0
                           for estudent in estuds:
                              pendientes=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[estudent[0]],["and"])
                              if(len(pendientes)>0):
                                  num_pendientes+=1    
                           if(num_pendientes==0):
                               valido=False
                        if(valido):
                            new_data.append(secc[0])
              comp.set_values(new_data)
           elif(ev_value==constantes.COMBOBOX_SET_STUDENT_DATA_RENDIMIENTO):
              new_data=["elegir"]
              comp.set_values(new_data)
              comp.set_selected_index(0)
           elif(ev_value==constantes.COMBOBOX_LOAD_LIST_FORMATOS):
               format_types=["elegir","nuevo","asistencia seccion","asistencia del personal","carnet","constancia de estudio","constancia de prestacion de servicios","cronograma","diario de clases","disp horario","evaluacion continua","inscripcion","info estudiante","info trabajador","lista de la seccion","lista de trabajadores","notas finales","notas finales del año","notas del momento","materia pendiente","planificacion","reporte de descargas","reporte de usuarios","sabana de notas"]
               conexion_bd.set_tabla(constantes.TABLA_FORMATO)
               data_formats=conexion_bd.get_allData(None,None)
               for form in data_formats:
                  is_new=True
                  for temp_format in format_types:
                      if(form[0]==temp_format):
                         is_new=False
                  if(is_new==True):
                      format_types.append(form[0])
               comp.set_values(format_types) 
           elif(ev_value==constantes.COMBOBOX_LOAD_WORKER_POSIBLE_DIRECTOR):     
              user=Event_manager.user
              cred=user.get_credentials()
              permiso=cred[2]
              usr=cred[0]
              conexion_bd.set_tabla(constantes.TABLA_USUARIO)
              dat_usr=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],1,[constantes.CLAVE_USUARIO],[usr],["and"])
              ced=dat_usr[0][0]
              if(permiso=="admin"):
                  Event_manager.activar_element("director_label",True,True)
                  conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                  data_trabaj=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR,constantes.CLAVE_CARGO,constantes.CLAVE_NOMBRE],3)
                  new_data=["sin asignar"]
                  if(ced!="000" and ced!="001"):
                      #prevent get data from default admin worker
                      data_temp_user=conexion_bd.get_allData([constantes.CLAVE_NOMBRE],1,[constantes.CLAVE_TRABAJADOR],[ced],["and"])
                      conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                      data_name_user=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_temp_user[0][0]],["and"])
                      val=ced+"-"
                      for temp_name in data_name_user[0]:
                         if(temp_name!="" and temp_name!="..."):
                             val=val+temp_name.capitalize()+" "
                      new_data=[val]
                  for trabaj in data_trabaj:
                      if(trabaj[0]!="000" and trabaj[0]!="001" and trabaj[0]!=ced):
                          #prevent get data for default admin worker or the actual admin worker
                          conexion_bd.set_tabla(constantes.TABLA_CARGO)
                          data_cargo=conexion_bd.get_allData(["cargo","cargo_ministerio"],2,[constantes.CLAVE_CARGO],[trabaj[1]],["and"])
                          if(data_cargo!=[]):
                               if(data_cargo[0][0].lower()!="secretaria" and data_cargo[0][0].lower()!="obrero"):
                                    if(data_cargo[0][1].endswith("VI") or data_cargo[0][1].endswith("V") or data_cargo[0][1].endswith("IV")):
                                        valor_temp=trabaj[0]+"-"
                                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)                 
                                        data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[trabaj[2]],["and"])
                                        for name_temp in data_nomb[0]:
                                               if(name_temp!="" and name_temp!="..."):
                                                    valor_temp=valor_temp+name_temp.capitalize()+" "                                                
                                        new_data.append(valor_temp)
                  comp.set_values(new_data)
                  comp.set_selected_index(0) 
              else:
                  Event_manager.vent.raiz.after(200,comp.set_active,False)
                  Event_manager.activar_element("director_label",False,True)
                

                                    
   #trigger the event required when select a radio Button
   @classmethod
   def interprete_RadioButton_Event(cls,comp_id,comp_value):
            from event_manager import Event_manager
            from conexion_bd import conexion_bd  
            if(comp_value=="docente"):
                #action when indicate the worker is 'docente'
                values=["elegir","Docente","Docente de Aula",]
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                lista_trabaj=conexion_bd.get_allData([constantes.CLAVE_CARGO],1)
                posibles=["Coordinador de Evaluacion","Coordinador de Orientacion","Sub Director Academico","Sub Director Administrativo"]
                conexion_bd.set_tabla(constantes.TABLA_CARGO)
                for posibl in posibles:
                   valid_carg=True
                   for trab in lista_trabaj:
                     data_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[trab[0]],["and"])
                     if(data_cargo!=[]):
                         if(data_cargo[0][0].lower()==posibl.lower()):
                                valid_carg=False
                   if(valid_carg==True):
                       values.append(posibl)          
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR) 
                empl=Event_manager.vent.panelActual.get_comp_byName("empleado").get_selected_value()    
                
                if(empl!="nuevo"):
                   empl=empl.split("-")
                   if(len(empl)==3):
                      empl=empl[0]+"-"+empl[1]
                   elif(len(empl)==2):
                      empl=empl[0]
                   else:
                      empl=""
                   data_empl=conexion_bd.get_allData([constantes.CLAVE_CARGO],1,[constantes.CLAVE_TRABAJADOR],[empl],["and"])
                   if(data_empl!=[]):
                     conexion_bd.set_tabla(constantes.TABLA_CARGO)
                     carg_empl=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[data_empl[0][0]],["and"])        
                     if(carg_empl!=[]):
                        existe=False
                        for vl in values:
                            if(vl.lower()==carg_empl[0][0].lower()):
                                   existe=True
                        if(existe==False):
                             values.append(carg_empl[0][0])               
                Event_manager.set_comp_values("cargo",values)
                values2=["elegir","Docente I","Docente II","Docente III","Docente IV","Docente V","Docente VI"]
                Event_manager.set_comp_values("cargo_minist",values2)
                Event_manager.activar_element("caja_areas",True)
                Event_manager.activar_element("caja3_rp",True)
            elif(comp_value=="no docente"):
              #action when indicate the worker is 'no docente'
              values=["elegir","Obrero","Secretaria"]
              Event_manager.set_comp_values("cargo",values)
              values2=["elegir","Aseador I","Aseador II","Aseador III","Aseador IV","Bachiller I","Bachiller II","Bachiller III","Bachiller IV","TSU","Cocinera"]
              Event_manager.set_comp_values("cargo_minist",values2)
            elif(comp_value=="mañana" or comp_value=="tarde"):
                #for Indicate the Disponibility of a worker 
                values=[]
                if(comp_value=="mañana"):
                    values=["no disponible","7:30AM","8:15AM","9:00AM","9:45AM","10:30AM","11:15AM","12:00PM"]
                else: 
                    values=["no disponible","12:00PM","12:45PM","1:30PM","2:15PM","3:00PM","3:45PM","4:30PM","5:15PM"]
                Event_manager.set_comp_values("desde_L",values)
                Event_manager.set_comp_values("hasta_L",values)
                Event_manager.set_comp_values("desde_M",values)
                Event_manager.set_comp_values("hasta_M",values)
                Event_manager.set_comp_values("desde_Mi",values)
                Event_manager.set_comp_values("hasta_Mi",values)
                Event_manager.set_comp_values("desde_J",values)
                Event_manager.set_comp_values("hasta_J",values)
                Event_manager.set_comp_values("desde_V",values)
                Event_manager.set_comp_values("hasta_V",values)        
            elif(comp_value=="respaldar" or comp_value=="restaurar"):
                #for indicate action in database Management Panel
                if(comp_value=="respaldar"):
                   Event_manager.activar_element("files",False,True)
                   Event_manager.set_comp_values("titulo_respaldo","RESPALDAR BASE DE DATOS")
                else:
                   Event_manager.activar_element("files",True,True)
                   Event_manager.set_comp_values("titulo_respaldo","RESTAURAR BASE DE DATOS")
            elif(comp_value=="Si" or comp_value=="No"):
                #for the radio button in Inscription process to indicate if the student have 'cedula'
                if(comp_id=="cedulado"):
                   if(comp_value=="Si"):
                       Event_manager.activar_element("cedula",True,True)
                       Event_manager.activar_element("ci_label",True,True)
                       Event_manager.activar_element("año_label",False,True)
                       Event_manager.activar_element("año",False,True)
                       Event_manager.activar_element("cedula_repres",False,True)
                       Event_manager.activar_element("ci_repres_label",False,True)
                       
                   else:
                       Event_manager.activar_element("cedula",False,True)
                       Event_manager.activar_element("ci_label",False,True)
                       Event_manager.activar_element("año_label",True,True)
                       Event_manager.activar_element("año",True,True)
                       Event_manager.activar_element("cedula_repres",True,True)
                       Event_manager.activar_element("ci_repres_label",True,True)
                        
            elif(comp_value=="modificar cronograma" or comp_value== "crear cronograma"):
                if(comp_value=="modificar cronograma"):
                    Event_manager.activar_element("caja_b",True)
                    Event_manager.activar_element("caja6",False)
                else:
                    Event_manager.activar_element("caja_b",False)
                    Event_manager.activar_element("caja6",True)
       
           
   
