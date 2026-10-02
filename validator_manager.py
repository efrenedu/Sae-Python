from General import General
from constantes import constantes
from tiempo import tiempo

#Validate Data for Process 
class Process_Validator_Manager:
    
    #Verification Before Access the Panels Gestion of Califications or 'Seguimiento de Materia Pendiente'
    @classmethod 
    def verify_Student_Credentials(cls,data,rendimient_action):
       from Process_Manager import Process_Manager
       if(data["Id_Estud"]=="" or data["Id_Estud"]==" "):
             General.show_message("Cedula del Estudiante Invalida","Estudiante Invalido")
             return False
       if(data["Section"]=="elejir" or data["Section"]=="elegir"):
             General.show_message("Por Favor Indique el Estudiante","Estudiante Invalido")
             return False
       if(data["Year"]=="" or data["Year"]==" "):
             General.show_message("Año de Curso del Estudiante Invalido","Año Invalido")
             return False
       if(data["Name"]=="" or data["Name"]==" "):
             General.show_message("Nombre del Estudiante Invalido","Estudiante Invalido")
             return False
       if(data["Area"]=="elejir" or data["Area"]=="elegir"):
             General.show_message("Por Favor Indique el Area de la Materia Pendiente","Area de Formacion Invalida")
             return False
       if(rendimient_action==Process_Manager.RENDIMIENTO_OPTION_IDENTIFIC_GESTION_CALIFICATIONS):
           if(data["Momento"]=="elegir" or data["Momento"]=="elejir"):
                return False
       return True 
     
    #Verify the Data of Request to Register a Try of Materia Pendiente
    @classmethod 
    def verify_materiaPendiente_Data(cls,data):
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],"condition_Types":["and","and"],"conditions_Values":[data["Id_Estud"],data["Area"]],"conditions_Verify":["=","="]}              
        data_m_pen=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE,"año"],cond_data,None,True)               
        intento_val=data["Intento_Id"]
        conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
        cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE,"intento"],"condition_Types":["and","and"],"conditions_Values":[data_m_pen[0][constantes.CLAVE_MATERIA_PENDIENTE],intento_val],"conditions_Verify":["=","="]}              
        data_c_pen=conexion_bd.get_allData([constantes.CLAVE_CALIF_PENDIENTE],cond_data)               
        year_pend=data_m_pen[0]["año"]
        if(data_c_pen!=[]):
           #el intento de materia pendiente o revision ya existe
             General.show_message("El intento de Materia Pendiente ya se ha Registrado","Intento ya Registrado")
             return False
             
        if(intento_val=="elegir"):
            General.show_message("Por Favor Indique el Numero del Intento de Materia Pendiente del Estudiante","Intento Invalido")
            return False
           
        calif=data["Calificacion_Value"]
        if(General.is_valid(calif,constantes.CADENA_SOLONUMERO,False)==False):
            General.show_message("Por Favor Indique una Calificacion Valida","Calificacion Invalida")
            return False
            
        elif((int(calif)>=0 and int(calif)<=20)==False):
            General.show_message("La Calificacion debe ser entre 0 y 20 pts","Calificacion Invalida")
            return False
            
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cronog=conexion_bd.get_allData([])
         
        if(cronog==[]):
            General.show_error("no existe un cronograma activo","cronograma inexistente")
            return False        
        conexion_bd.set_tabla(constantes.TABLA_FECHA)
        razon="materia pendiente "+intento_val[len(intento_val)-1]
        if(intento_val=="revision"):
            razon=intento_val
          
        cond_data={"conditions_Names":["razon"],"condition_Types":["and"],"conditions_Values":[razon],"conditions_Verify":["="]}                            
        data_cronog=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data,None,True)
        if(data_cronog==[]):
            General.show_message("Aun no se ha Registrado la Fecha Para El Intento Indicado de la Materia Pendiente","Fecha Invalida")
            return False
        inicio=data_cronog[0]["fecha"]
        cierre=data_cronog[0]["fecha_cierre"]
        time_object=tiempo()
        if(time_object.is_previous(time_object.get_fecha(),inicio)==True or time_object.is_previous(cierre,time_object.get_fecha())==True):
           General.show_message("No se puede Registrar el Intento Indicado de Materia Pendiente en este Momento segun el Cronograma","Fecha Invalida")
           return False
        motivo=data["Motivo"]
        if(motivo=="" or motivo==" "):
            General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
            return False
        
        return True

    #Verify Data for Calification Gestion Panels
    @classmethod
    def validate_calification_Gestion(cls,data,action):
       from conexion_bd import conexion_bd
       if(action=="Update" or action=="Delete"):
          if(data["Motivo"]=="" or data["Motivo"]==" "):
             General.show_message("Por Favor Indique El Motivo de la Modificacion","Motivo Invalido")
             return False
          if(data["Evaluation"]=="" or data["Evaluation"]==" "):
             General.show_message("Por Favor Indique la Evaluacion a Modificar","Evaluacion Invalida")
             return False
          if(action=="Update"):
             calif=data["Calification"]
             if(General.is_valid(calif,constantes.CADENA_CALIFICACION,False,0)==False):
                General.show_message("Por Favor Indique una Calificacion Valida","Calificacion Invalida")
                return False
             val_cal=float(calif)
             if((val_cal>=0.0 and val_cal<=20.0)==False):
                 General.show_message("La Calificacion debe estar entre 0 y 20 pts","Calificacion Invalida")
                 return False
             
          conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
          cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data["Year"]],"conditions_Verify":["=","=","="]}                         
          join_data={}
          cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[data["Momento"]],"conditions_Verify":["="]}                         
          join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join}
          data_calific=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,join_data,True)    
          if(len(data_calific)<=0):
              General.show_message("Aun no se ha Registrado Ninguna Calificacion en esta Area de Formacion","Calificacion Invalida")
              return False
       elif(action=="Register"):
             calif=data["Calification"]
             if(General.is_valid(calif,constantes.CADENA_SOLONUMERO,False,0)==False):
                General.show_message("Por Favor Ingrese un Valor Numerico como Valificacion","Calificacion Invalida")
                return False  
             val_num=int(calif)
             if((val_num>=0 and val_num<=20)==False):
                General.show_message("La Calificacion debe ser un Numero ente 0 y 20","Calificacion Invalida")
                return False
       elif(action=="Estimulation"):
            if(data["Motivo"]=="" or data["Motivo"]==" "):
               General.show_message("Por Favor Indique El Motivo de la Modificacion","Motivo Invalido")
               return False
            estimul_prom=data["Estimulacion_Promedio"]
            estimul_area=data["Estimulacion_Areas"]
            if(General.is_valid(estimul_prom,constantes.CADENA_SOLONUMERO,False,0)==False ):
                General.show_message("Por Favor Indique Un Valor Numerioc para la Estimulacion por Promedio","Estimulacion Invalida")
                return False
            if(General.is_valid(estimul_area,constantes.CADENA_SOLONUMERO,False,0)==False ):
                General.show_message("Por Favor Indique Un Valor Numerioc para la Estimulacion por Areas de Formacion","Estimulacion Invalida")
                return False
            num_estimul_prom=int(estimul_prom)
            num_estimul_area=int(estimul_area)
            if(num_estimul_prom<0 or num_estimul_prom>1):
                General.show_message("Por Favor Indique como Eastimulacion por Promedio un Numero entre 0 y 1 ","Estimulacion Invalida")
                return False
            if(num_estimul_area<0 or num_estimul_area>1):
                General.show_message("Por Favor Indique como Eastimulacion por Areas de Formacion un Numero entre 0 y 1 ","Estimulacion Invalida")
                return False
                
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año"],"condition_Types":["and","and"],"conditions_Values":[data["Id_Estud"],data["Year"]],"conditions_Verify":["=","="]}              
            join_data={}
            cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[data["Momento"]],"conditions_Verify":["="]}                         
            join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM,"estimulacion"],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join}
            all_califics_mom=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_AREA_FORMACION],cond_data,join_data,True)    
            if(len(all_califics_mom)<=0):
               General.show_message("Aun no se han Registrado Calificaciones en el Momento Actual"," Estudiante sin Calificaciones en el Momento Academico")
               return False
            
            estimul_other_areas=0
            for calific in all_califics_mom:
                area_name=calific[constantes.CLAVE_AREA_FORMACION]
                estimul=calific["estimulacion"]
                if(area_name!=data["Area"]):
                    estimul_other_areas+=int(estimul)
            if(estimul_other_areas>=2):
                 General.show_message("El Estudiante ya se le ha Asignado el Maximo Posible de Estimulacion en las Otras Areas de Formacion","Estimulacion Completa")
                 return False
            if(estimul_other_areas+(num_estimul_prom+num_estimul_area)>2):
                 General.show_message("El Estudiante Solo puede Tener Un Maximo de 2 Pts de Estimulacion entre todas las Areas de Fornacion del Momento Academico","Estimulacion Excedida")
                 return False
       return True
         
    #Verify Data for Generation of 'Sabana de Notas' and Section Califications of Academic Moment  Documents 
    @classmethod    
    def validar_sectionData_NotasMomento_Sabana_generation(cls,data):
        if(data["Year"]=="elegir"):
           General.show_message("Por Favor Indique Un Año de Curso","Año de Curso Invalido")
           return False
        if(data["Turno"]=="elegir"):
           General.show_message("Por Favor Indique el Turno de la Seccion","Turno Invalido")
           return False
        if(General.is_valid(data["Letra"],constantes.CADENA_SOLOTEXTO,False,0)==False):
             General.show_message("Por Favor Indique La Letra de la Seccion","Letra Invalida")
             return False
        if(len(data["Letra"])>1):
             General.show_message("Por Favor Indique una Sola Letra ","Letra Invalida")
             return False
        return True
    
    #Verify Data for Definitive Calification Gestion Panels
    @classmethod
    def validateData_DefiniteCalifications_Gestion(cls,data):
         from conexion_bd import conexion_bd
         conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
         cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"]],"conditions_Verify":["=","=","="]}                         
         califics_list=conexion_bd.get_allData(["valor"],cond_data,None,True)
         if(len(califics_list)<=0):
             General.show_message("El Estudiante No Tiene Calificaciones Pendientes de Asignar","Modificacion Invalida")
             return False
         require_modifics=False
         for calific in califics_list:
            if(calific["valor"]=="0"):
                require_modifics=True              
         if(require_modifics==False):
             General.show_message("El Estudiante No Tiene Calificaciones Pendientes de Asignar","Modificacion Invalida")
             return False
         if(General.is_valid(data["Area"],constantes.CADENA_SOLOTEXTO,True,0)==False):
             General.show_message("Por Favor Indique el Area de la Calificacion a Modificar","Area Invalida")
             return False
         if(General.is_valid(data["Year"],constantes.CADENA_SOLONUMERO,False,0)==False):
             General.show_message("Por Favor Indique el Año de la Calificacion a Modificar","Año de Curso Invalido")
             return False
         val_year=int(data["Year"])
         if(val_year<=0 or val_year>5):
            General.show_message("El Año solo puede tener un valor entre 1 y 5","Año Invalido")
            return False
         if(General.is_valid(data["Calification"],constantes.CADENA_SOLONUMERO,False,0)==False ):
              General.show_message("Por Favor Indique Un Valor Numerico para la Calificacion a Modificar","Nueva Calificacion Invalida")
              return False
         next_calific_val=int(data["Calification"])
         if(next_calific_val<=0 or next_calific_val>20):
              General.show_message("La Nueva Calificacion debe tener un valor entre 1 y 20 ","Nueva Calificacion Invalida ")
              return False
         return True
         
         
    #Validate Data for Cronogram Dates Update/Register
    @classmethod
    def validate_cronogram_Dates(cls,data):
        from conexion_bd import conexion_bd
        time_object=tiempo()
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        dat_cronog=conexion_bd.get_allData(["inicio"],None,None,True)
        init_cronog=""
        if(len(dat_cronog)<=0): 
           General.show_message("Aun no se ha Registrado Ningun Cronograma","Cronograma No Registrado")
           return False
        init_cronog=dat_cronog[0]["inicio"]
        for i in range(0,len(data)):
            inicio=data[i]["Inicio"]
            razon=data[i]["Razon"]
            cierre=data[i]["Cierre"]
            strict_verification=data[i]["Strict_Verification"]
            if(General.is_valid(inicio,constantes.CADENA_FECHA,False)==False):
               General.show_message(f" Formato de Fecha de Inicio de {razon} Invalido","Fecha de Inicio Invalido")
               return False               
            elif(General.is_valid(cierre,constantes.CADENA_FECHA,False)==False):
               General.show_message(f" Formato de Fecha de Cierre de {razon} Invalido","Fecha de Cierre Invalido")
               return False 
               
            if(time_object.is_previous(inicio,init_cronog)):
               General.show_message(f"La Fecha {razon} no puede tener una fecha de inicio Anterior a la del Cronograma","Fecha de Inicio Invalida")
               return False
            if(time_object.is_previous(inicio,cierre,strict_verification)==False):
                General.show_message(f"La Fecha de Cierre de {razon} de ser Posteriro a la de Inicio","Fehca de Cierre Invalida")
                return False
                
        return True
    
    #Validate Data for Cronogram Register/Update
    @classmethod
    def validate_cronogram(cls,data):
        periodo=data["Periodo"]
        inicio=data["Inicio"]
        cierre=data["Cierre"]
        year=periodo.split("-")
        if(len(year)!=2):
           General.show_message("Mal Formato del Periodo del Año Escolar","Periodo Invalido")
           return False
           
        if(General.is_valid(year[0],constantes.CADENA_SOLONUMERO,False,3)==False):
            General.show_message("El Año de Inicio del Periodo debe ser un Numero","Inicio del Periodo Invalido")
            return False
        elif(General.is_valid(year[1],constantes.CADENA_SOLONUMERO,False,3)==False):
           General.show_message("El Año de Fin del Periodo debe ser un Numero","Fin del Periodo Invalido")
           return False
                   
        if(General.is_valid(inicio,constantes.CADENA_FECHA,False)==False):
            General.show_message("La Fecha de Inicio del Cronograma es Invalida","Fecha de Inicio Invalida")
            return False
        elif(General.is_valid(cierre,constantes.CADENA_FECHA,False)==False):
            General.show_message("La Fecha de Cierre del Cronograma es Invalida","Fecha de Cierre Invalida")
            return False
        time_object=tiempo()
        temp_inicio=inicio.split("/")
        if(temp_inicio[1]!="09" and temp_inicio[1]!="9"):
           General.show_message("El Inicio del Año Escolar debe ser en el mes de Septiembre","Fecha de Inicio Invalida")
           return False
        if(time_object.is_previous(inicio,cierre)!=True):
           General.show_message("La Fecha de Cierre del Cronograma debe ser Posterior a la de Inicio","Fecha de Cierre Invalida")
           return False
        return True
    
    #Verify if the Moment Requerid Can Change the Dates
    @classmethod
    def validate_Date_Moment_Edition(cls,momento):
        from conexion_bd import conexion_bd
        verify_preview_moment=""
        if(momento=="momento 3"):
            verify_preview_moment="momento 2"
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[momento],"conditions_Verify":["="]}    
        data_mom=conexion_bd.get_allData(["fecha_inicio","fecha_limite","abierto","culminado"],cond_data,None,True)
        cond_data={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[verify_preview_moment],"conditions_Verify":["="]}    
        dat_preview_mom=conexion_bd.get_allData(["fecha_inicio","culminado"],cond_data,None,True)
        if(len(data_mom)<=0):
              if(momento=="momento 1"):
                  General.show_error("error en el registro de momentos del cronograma","Error")
                  return [False,[]]
        else:
             if(data_mom[0]["culminado"]!="false"):
                 General.show_message("El Momento Academico Indicado ya ha culminado","Fechas del Momento Academico No Modificables")
                 return [False,[]]                   
        if(verify_preview_moment!="" and len(dat_preview_mom)<=0):
             General.show_error(f"El {verify_preview_moment} Aun no se ha Registrado","Error")
             return [False,[]]
        return [True,data_mom]
    
    #Validate the data for Formats Gestion 
    @classmethod
    def verify_formatGestion_Data(cls,data):
        action=data["Action"]
        target_form=data["Formato"]
        type_form=data["Format_Type"]
        reference_text=data["Reference_Text"]
        if(action=="elegir"):
           General.show_message("Por Favor Indique la Accion a Realizar","Accion Invalida")
           return False
        if(target_form=="" or target_form==" "):
           General.show_message("Por Favor Indique el Formato","Formato Invalido")
           return False
        if(action=="modificar contenido"):
            if(type_form.lower()=="pdf"):
               General.show_message("Solo Formatos en XLSX Se pueden Modificar","Tipo de Formato Invalido")
               return False
            if(reference_text=="" or reference_text==" "):
               General.show_message("Por Favor Indique El Texto de la Celda de Referencia","Texto de Referencia Invalido")
               return False
        return True
    #Verify data of Student in Inscription process Is Correct 
    @classmethod    
    def validar_inscripcion(cls,data):
          from Process_Manager import Process_Manager
          fields=data[0]
          birthdate_stud=data[1]
          data_process=Process_Manager.get_data_process()
          
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
                       data_process["estudiante"]["nombre"]=fullname[0].lower()
                       data_process["estudiante"]["s_nombre"]=""
                  elif(len(fullname)==2):
                       data_process["estudiante"]["nombre"]=fullname[0].lower()
                       data_process["estudiante"]["s_nombre"]=fullname[1].lower()
                  else:
                       General.show_message("Por Favor Indique Correctamente los Nombres del Estudiante","Nombres Invalido")
                       return False
                             
              elif(id_f=="apellido"):
                  if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                       General.show_message("Por Favor Indique el Apellido del Estudiante Correctamente","Apellido Invalido")
                       return False
                  fullapell=valor.split(" ")
                  if(len(fullapell)==1):
                       data_process["estudiante"]["apellido"]=fullapell[0].lower()
                       data_process["estudiante"]["s_apellido"]=""
                  elif(len(fullapell)==2):
                      data_process["estudiante"]["apellido"]=fullapell[0].lower()
                      data_process["estudiante"]["s_apellido"]=fullapell[1].lower()
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
                    data_process["estudiante"]["expediente_src"]=valor_exp
              elif(id_f=="destino_foto"):
                    valor_foto=valor
                    if(valor!=""):
                       if(valor.endswith(".png")==False and valor.endswith(".jpg")==False and valor.endswith(".jpeg")):
                           General.show_message("Por Favor suba la Foto como un Archivo de Imagen PNG o JPG","formato de foto Invalido")
                           return False
                       valor_foto=valor
                    else:
                       valor_foto="..."
                    data_process["estudiante"]["foto_expediente"]=valor_foto
                     
              elif(id_f=="CIrepres"):
                      temp_v=valor
                      if(temp_v.startswith("v-") or temp_v.startswith("V-") or temp_v.startswith("e-") or temp_v.startswith("E-")):
                         temp_v=valor.split("-")[1]
                      if(General.is_valid(temp_v,constantes.CADENA_SOLONUMERO,False,6)==False):
                          General.show_message("Por Favor Indique una Cedula del Representante Valida","Cedula de Representante Invalida")
                          return False
                      data_process["representante"]["CI_representante"]=valor
              elif(id_f=="telef"):
                      if(General.is_valid(valor,constantes.CADENA_TELEFONO,False)==False):
                         General.show_message("Por Favor Indique un telefono Valido","telefono invalido")
                         return False
                      data_process["representante"]["telefono"]=valor 
              elif(id_f=="nombre_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          General.show_message("Por Favor Indique el Nombre del Representante Correctamente","Nombre de Representante Invalido")
                          return False
                      temp_nomb=valor.split(" ")
                      if(len(temp_nomb)==1):
                          data_process["representante"]["nombre"]=temp_nomb[0].lower()
                          data_process["representante"]["s_nombre"]=""
                      elif(len(temp_nomb)==2):
                           data_process["representante"]["nombre"]=temp_nomb[0].lower()
                           data_process["representante"]["s_nombre"]=temp_nomb[1].lower() 
                      else:
                          General.show_message("Por Favor Indique Los Nombres del Representante Correctamente","Nombre de Representante Invalido")
                          return False
              elif(id_f=="apellido_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          General.show_message("Por Favor Indique el Apellido del Representante Correctamente","Apellido de Representante Invalido")
                          return False
                      temp_apell=valor.split(" ")
                      if(len(temp_apell)==1):
                           data_process["representante"]["apellido"]=temp_apell[0].lower()
                           data_process["representante"]["s_apellido"]=""
                      elif(len(temp_apell)==2):
                          data_process["representante"]["apellido"]=temp_apell[0].lower()
                          data_process["representante"]["s_apellido"]=temp_apell[1].lower()
                      else:
                         General.show_message("Por Favor Indique Los Apellidos del Representante Correctamente","Apellido de Representante Invalido")
                         return False  
              elif(id_f=="direccion"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           General.show_message("Por Favor Indique la Direccion del Estudiante separada por ',' en formato xxx,xxxx,xxx","Direccion Invalida")
                           return False
                       data_d=valor.split(",")
                       data_process["estudiante"]["direccion"]={"sector":data_d[0],"parroquia":data_d[1],"casa":data_d[2]}

              elif(id_f=="correo"):
                       if(General.is_valid(valor,constantes.CADENA_CORREO,False)==False):
                           General.show_message("Por Favor Indique un Correo del Representante Valido","correo Invalido")
                           return False
                       data_process["representante"]["correo"]=valor
              elif(id_f=="dir_representante"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           General.show_message("Por Favor Indique la Direccion del Representante separada por ',' en formato xxx,xxxx,xxx","Direccion Invalida")
                           return False
                       data_d=valor.split(",")
                       data_process["representante"]["direccion"]={"sector":data_d[0],"parroquia":data_d[1],"casa":data_d[2]}

              elif(id_f=="parentesco"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,False)==False):
                          General.show_message("Por Favor Indique un Parentesco del Representante Valido","Parentesco Invalido")
                          return False
                      data_process["estudiante"]["parentesco"]=valor.lower()
              elif(id_f=="plantel"):
                      if(General.is_valid(valor,constantes.CADENA_ALFANUMERICA,True,4)==False):
                         General.show_message("Por Favor Indique el Plantel de Procedencia del Estudiante","Plantel Invalido")
                         return False
                      data_process["estudiante"]["plantel"]=valor    
              elif(id_f=="oficio"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True)==False):
                            General.show_message("Por Favor Indique un Oficio del Representante Valido","Oficio Invalido")
                            return False
                      data_process["representante"]["oficio"]=valor.lower()
          if(General.is_valid(birthdate_stud,constantes.CADENA_FECHA,False)==False):
             General.show_message("Por Favor Indique el Año de Nacimiento del Estudiante","Año de Nacimiento Invalido")
             return False
          data_process["estudiante"]["año_nacimiento"]=birthdate_stud                            
          data_process["estudiante"]["genero"]=data[3]
          data_process["estudiante"]["year_estud"]=data[4]
          data_process["estudiante"]["estatus"]=data[5]
          if(data[2]=="elejir" or data[2]=="elegir"):
             General.show_message("Por Favor Indique el Estado de Salud del Estudiante","Estado de Salud Invalido")
             return False
          data_process["estudiante"]["salud"]=data[2]
          Process_Manager.set_data_process(data_process)
          return True
   
   
    #Verify if the Data for Request Inscription is Valid     
    @classmethod
    def validar_solicit_inscrip(cls,data):
        from conexion_bd import conexion_bd
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
    
class Register_Validator:

    #Verify if the Cargo Code Is Valid 
    @classmethod
    def verify_cargo_code(cls,val):
       if(len(val)<6):
            return False
          
       first_part=""
       second_part=""
       last_number_Index=4
       last_val=val[3]
       if(last_val.upper()=="A" or last_val.upper()=="C" or last_val.upper()=="B"):
          last_number_Index=3
       for i in range(0,len(val)):
            if(i<last_number_Index):
               first_part=first_part+(val[i])
            else:
               second_part=second_part+(val[i]).upper()
       if(General.is_valid(first_part,constantes.CADENA_SOLONUMERO,False)==False):
            return False
       if(General.is_valid(second_part,constantes.CADENA_ALFANUMERICA,False)==False):
           return False       
       return True
       
    #Verify the Data for Register/Update a Worker
    @classmethod
    def validate_worker_data(cls,data,update):
        id_number=data["cedula"].split("-")[1]
        if(General.is_valid(id_number,constantes.CADENA_SOLONUMERO,False,4)==False):
           General.show_message("Por Favor Indique una Cedula de Trabajador Valida","Cedula Invalida")
           return False
        name=data["nombre"].split(" ")
        for val in name:
          if(General.is_valid(val,constantes.CADENA_SOLOTEXTO,False,2)==False):
              General.show_message("Por Favor Indique un nombre Valido","Nombre Invalido")
              return False
              
        apellid=data["apellido"].split(" ")
        for val in apellid:
          if(General.is_valid(val,constantes.CADENA_SOLOTEXTO,False,2)==False):
              General.show_message("Por Favor Indique un Apellido Valido","Apellido Invalido")
              return False
        telef=data["telefono"]
        mail=data["correo"]
        if(telef!=""):
           if(General.is_valid(telef,constantes.CADENA_TELEFONO,False)==False):
                General.show_message("Por Favor Indique el Telefono del Trabajador Correctamente","Telefono Invalido")
                return False
        if(mail!=""):
            if(General.is_valid(mail,constantes.CADENA_CORREO,False)==False):
                General.show_message("Por Favor Indique el Correo del Trabajador Correctamente","Correo Invalido")
                return False
        if(data["cargo"]=="elegir"):
           General.show_message("Por Favor Indique el Cargo del Trabajador","Cargo Invalido")
           return False
        if(data["cargo_ministerio"]=="elegir"):
           General.show_message("Por Favor Indique el Cargo segun el Ministerio","Cargo Invalido")
           return False
        cargo_cod=data["cargo_cod"]
        if(cls.verify_cargo_code(cargo_cod)==False):
           General.show_message("Por Favor Ingrese un Codigo del Cargo Valido","Codigo del Cargo Invalido")
           return False
           
        src=data["destino_file"]
        src_photo=data["destino_foto"]
        if(src!="" ):
            if(src.endswith(".zip")==False ):
                 General.show_message("El Expediente solo puede ser Archivos ZIP","Expediente Invalido")
                 return False
        if(src_photo!=""):
            if(src_photo.endswith(".png")==False and src_photo.endswith(".jpg")==False and src_photo.endswith(".jpeg")==False):
                 General.show_message("Solo se Admite Archivos PNG y JPG para la Foto del Expediente","Foto de Expediente Invalido")
                 return False
        if(data["cargo_ministerio"].startswith("Docente")):
            if(len(data["Areas"])<=0):
                  General.show_message("Los Profesores deben Tener Almenos 1 Area de Formacion Asignada","Areas de Formacion Invalidas")
                  return False
        temp_date=data["fecha_ingreso"]
        if(General.is_valid(temp_date,constantes.CADENA_FECHA,False)==False):
           General.show_message("Por Favor Indique la Fecha de Ingreso al Ministerio","Fecha Ingreso Invalida")
           return False
        if(update):
           if(data["estatus"]=="elegir"):
               General.show_message("Por Favor Indique el Estatus del Trabajador","Estatus Invalido")
               return False
               
        return True
    #Verify if the Data for TimeTables Register/Update is Valid
    @classmethod
    def validate_timetable_data(cls,data):
        is_worker=False
        if(data["Type"]=="elegir"):
            General.show_message("Por Favor Indique El tipo de Horario","Data Invalida")
            return [False,False]
        if(data["Type"]!="seccion"):
           is_worker=True
           
        if(data["turno"]=="elegir"):
             General.show_message("Por Favor Indique el Turno del Horario","Datos Invalidos")
             return [False,False]
        src=data["src"]
        if(src.endswith(".pdf")==False ):
            General.show_message("el Horario Solo Puede ser Archivos PDF","Datos Invalidos")
            return [False,False]
          
        if(is_worker==False):
            if(data["section_value"]=="elegir"):
               General.show_message("Por Favor Indique la Seccion del Horario","Datos Invalidos")
               return [False,False]
        else:
             if(data["worker_value"]=="elegir"):
               General.show_message("Por Favor Indique el Trabajador el Horario","Datos Invalidos")
               return [False,False]
            
        return [True,is_worker]
    
    #Verify if the Data for Register/Update of Formation Area is Valid
    @classmethod
    def validate_formation_area_data(cls,data):
        area=data["Area"]
        if(area=="elegir"):
           General.show_message("Por Favor Indique el Area de Formacion","Area Invalida")
           return False
        if(data["Num_Years"]<=0):
            General.show_message("El Area de Formacion debe estar disponible en almenos 1 año de Curso","Datos Invalidos")
            return False
        new_areaName=data["Change_AreaName"]
        if(new_areaName!=area or area=="nueva"):
           if(General.is_valid(new_areaName,constantes.CADENA_SOLOTEXTO,True,2)==False or new_areaName=="nueva"):
               General.show_message("Por Favor Indique un Nuevo Nombre de Area de Formacion Valido","Datos Invalidos")
               return False
               
           from conexion_bd import conexion_bd
           conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
           if(conexion_bd.id_exist(constantes.CLAVE_AREA_FORMACION,new_areaName)):
              General.show_message("El Nombre del Area de Formacion Indicado ya Existe","Nombre del Area de Formacion Invalido")
              return False
        return True
        
    #Verify if the Data for Format Register is Valid
    @classmethod
    def validate_format_data(cls,data,update):
       format_name=data["Format"]
       if(format_name=="elegir"):
           General.show_message("Por Favor Indique el Formato","Formato Invalido")
           return False
       if(format_name=="nuevo"):
          if(General.is_valid(data["New_Format"],constantes.CADENA_ALFANUMERICA,True,4)==False or data["New_Format"]=="nuevo"):
             General.show_message("Por Favor Indique un Nombre Valido al Nuevo Formato","Nuevo Formato Invalido")
             return False
       src=data["Src"]
       if(src.endswith(".pdf")==False and src.endswith(".xlsx")==False):
           General.show_message("El Formato solo puede ser un Archivo PDF o XLSX","Archivo Invalido")
           return False
       return True
       
    #Verify if the Data for Disponibilty of TimeTables Register/Update is Valid     
    @classmethod
    def validate_timeTables_Disponibility(cls,data,update):
       worker=data["Worker"]
       time_object=tiempo()
       if(worker=="elegir"):
           General.show_message("Por Favor Indique el Trabajador","Trabajador Invalido")
           return [False,""]
       id_worker=""    
       temp_id=worker.split("-")
       if(len(temp_id)==3):
          id_worker=temp_id[0]+"-"+temp_id[1]
       elif(len(temp_id)==2):
          id_worker=temp_id[0]
       if(id_worker==""):
           General.show_error("Error en formato de la Id del Trabajador"," Cedula Invalida")
           return [False,""]           
          
       days=data["Days"]
       num_disp=0
       for key in days:
           day_name=key.split("disp_")[1]
           target_disp=days[key]
           if(target_disp[0]=="no disponible" and target_disp[1]=="no disponible"):
               continue
           num_disp+=1
           if(target_disp[0]=="no disponible" or target_disp[1]=="no disponible"):
              General.show_message(f"Por Favor Indique Correctamente desde que hora hasta que hora esta disponbile el dia {day_name}","Disponibilidad Invalida")
              return [False,""]
           time_from=target_disp[0]
           time_to=target_disp[1]
           if(time_from=="" or time_to==""):
              General.show_error("Error Obteniendo Datos del la Disponibilidad de Horario","Disponibilidad Invalida")
              return [False,""]
             
           temp_time=time_from[0:len(time_from)-2]+":00"
           if(time_from.endswith("PM")):
              hours=int(temp_time.split(":")[0])
              add_hours=0
              if(hours!=12):
                 add_hours=12
              temp_time=str(hours+add_hours)+":"+temp_time.split(":")[1]+":00"
           time_from=temp_time
           temp_time=time_to[0:len(time_to)-2]+":00"
           if(time_to.endswith("PM")):
              hours=int(temp_time.split(":")[0])
              add_hours=0
              if(hours!=12):
                 add_hours=12
              temp_time=str(hours+add_hours)+":"+temp_time.split(":")[1]+":00"
           time_to=temp_time
           if(time_object.is_previous_time(time_from,time_to)==False):
               General.show_message(f"La Hora de Disponibilidad Inicio del dia {day_name} debe ser Anteriro a la de Fin","Horas Invalidas")
               return [False,""]
       if(num_disp<=0):
           General.show_message("Debe Indicar la Disponibilidad para almenos un dia de la Semana","Disponibilidad Invalida")
           return [False,"",""]           
       return [True,id_worker]
          