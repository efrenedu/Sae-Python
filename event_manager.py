from constantes import constantes
from tkinter import *   
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox          
from tkinter.font import Font               
from panel import panel
import glob
from componentes import Tabla
from componentes import TextField
from componentes import Radio
from componentes import Labl
from componentes import Label_Image
from componentes import Check_Button
from componentes import Combo_box
from componentes import Boton
from componentes import List_Box
from componentes import Lienzo_dibujo
from ventana_sec import ventana_secundaria
from General import General
from conexion_bd import conexion_bd
from documento import documento
import os
import sys
from tiempo import tiempo
import requests
from usuario import *
from estudiante import estudiante


#Manage the Events of System
class Event_manager:
    user=usuario()                          #user data
    vent=None                               #windows with the panels data
    
    #Trigger the actions Based in Event type
    @classmethod	  
    def determine_event(cls,type_e,pantalla=0):
        if(type_e>=constantes.EV_LOGIN and type_e<=constantes.EV_EXIT):
           #System Event
           if(type_e==constantes.EV_EXIT):
              cls.exit_application()
           elif(type_e==constantes.EV_LOGIN):
              cls.login()
           elif(type_e==constantes.EV_LOGOUT):
              cls.logout()
        elif(type_e>=constantes.EV_REGISTRAR_PERSONAL and type_e<=constantes.EV_UPDATE_AREA):
           #Register Event
           if(type_e==constantes.EV_REGISTRAR_PERSONAL):
               cls.registrar_personal()
           elif(type_e==constantes.EV_REGISTRAR_AREA_FORMACION):
               cls.registrar_area()
           elif(type_e==constantes.EV_REGISTRAR_DISP_HORARIO):
               cls.registrar_dispHorario()
           elif(type_e==constantes.EV_REGISTRAR_FORMATO):
               cls.registrar_formato()
           elif(type_e==constantes.EV_REGISTRAR_HORARIO):
               cls.registrar_horario() 
           elif(type_e==constantes.EV_UPDATE_AREA):
               cls.registrar_area(True)    
           elif(type_e==constantes.EV_UPDATE_HORARIO):
               cls.registrar_horario(True) 
           elif(type_e==constantes.EV_UPDATE_DISP):
               cls.registrar_dispHorario(True)
           elif(type_e==constantes.EV_UPDATE_TRABAJADOR):
               cls.registrar_personal(True)  
           elif(type_e==constantes.EV_UPDATE_FORMATO):
             cls.registrar_formato(True)               
        elif(type_e>=constantes.EV_AUDITORIA and type_e<=constantes.EV_REESTABLECER_MOMENTO):
           #Service Event
           from Service_Manager import Service_Manager
           from Consult_Manager import Consult_Manager
           if(type_e==constantes.EV_AUDITORIA):
              cls.consultar(Consult_Manager.CONSULT_USERS_HISTORIAL)
           elif(type_e==constantes.EV_VER_ESTADITICA):
              cls.estadistica()
           elif(type_e==constantes.EV_ACTIVAR_MOM):
              cls.activar_momento()
           elif(type_e==constantes.EV_REGISTRAR_USUARIO):
              cls.registrar_usuario()
           elif(type_e==constantes.EV_SERVICIO_RESPALDO_BD):
               cls.respaldar() 
           elif(type_e==constantes.EV_GESTION_USER_DESBLOQUEAR):
               cls.gestion_usuario(Service_Manager.USER_UNLOCK)
           elif(type_e==constantes.EV_GESTION_USER_RESTORE_PASS):
               cls.gestion_usuario(Service_Manager.USER_RESET_PASSWORD)
           elif(type_e==constantes.EV_GESTION_USER_DELETE_USER):
               cls.gestion_usuario(Service_Manager.USER_REMOVE)   
           elif(type_e==constantes.EV_GESTION_USER_CHANGE_PERMISOS):
               cls.gestion_usuario(Service_Manager.USER_CHANGE_ACCESS_LEVEL)
           elif(type_e==constantes.EV_UPDATE_ESTUDIANTE):
               cls.update_estudiante()    
           elif(type_e==constantes.EV_REESTABLECER_MOMENTO):
               cls.reestablecer_momento()
           elif(type_e==constantes.EV_NUEVO_USUARIO):
              cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_USUARIO)
           elif(type_e==constantes.EV_UPDATE_PASS):
               cls.recuperar_pass(Service_Manager.RECOVER_PASS_CHANGE_PASSWORD) 
           elif(type_e==constantes.EV_UPDATE_USER):
               cls.update_user()
           elif(type_e==constantes.EV_UPDATE_SECCION):      
               cls.organizar_seccion(Service_Manager.UPDATE_SECTIONS) 
        elif(type_e>=constantes.EV_ACTIVAR_ACTUALIZAR_PERSONAL and type_e<=constantes.EV_VOLVER):
           #UI Event
            from Service_Manager import Service_Manager
            if(type_e==constantes.EV_ACTIVAR_COMPS_UPDATE):
               cls.activar_comps_update()
            elif(type_e==constantes.EV_AGREGAR_AREA_DOCENTE):
               cls.agregar_area_docente()
            elif(type_e==constantes.EV_BORRAR_AREA_DOCENTE):
               cls.borrar_area_docente()
            elif(type_e==constantes.EV_LOAD_LOGIN):
               cls.load_login()
            elif(type_e==constantes.EV_LOAD_INICIO):
               cls.load_inicio()
            elif(type_e==constantes.EV_ABRIR_FILE_SINGLE):
               cls.set_file()
            elif(type_e==constantes.EV_ABRIR_FOTO):
               cls.set_file(True)
            elif(type_e==constantes.EV_RESET):
               cls.reset()  
            elif(type_e==constantes.EV_VOLVER):
               cls.volver()   
            elif(type_e==constantes.EV_MOVER_ESTUD):
                cls.organizar_seccion(Service_Manager.CHANGE_STUDENT_SECTION1_TO_SECTION2) 
            elif(type_e==constantes.EV_INTERCAMBIAR_ESTUDS):
                cls.organizar_seccion(Service_Manager.INTERAMBIATE_STUDENTS)  
            elif(type_e==constantes.EV_INCORPORAR_ESTUD):
                cls.organizar_seccion(Service_Manager.CHANGE_STUDENT_SECTION2_TO_SECTION1) 
            elif(type_e==constantes.EV_ACTIVAR_ACTUALIZAR_PERSONAL):
               cls.activar_update(0)
            elif(type_e==constantes.EV_ACTIVAR_ACTUALIZAR_ESTUDIANTE):
                cls.activar_update(1)
            elif(type_e==constantes.EV_ACTIVAR_ACTUALIZAR_HORARIO):
                cls.activar_update(2)
            elif(type_e==constantes.EV_ACTIVAR_ACTUALIZAR_DISP):
               cls.activar_update(3)
            elif(type_e==constantes.EV_ACTIVAR_ACTUALIZAR_AREA):
               cls.activar_update(4)  
            elif(type_e==constantes.EV_ACTIVAR_RECUPERAR_PASS1):
               cls.recuperar_pass(Service_Manager.RECOVER_PASS_LOAD_FIRST_PANEL)        
            elif(type_e==constantes.EV_ACTIVAR_RECUPERAR_PASS2):
               cls.recuperar_pass(Service_Manager.RECOVER_PASS_VERIFY_SECRET_QUESTIONS) 
            elif(type_e==constantes.EV_ACTIVAR_DOWNLOAD_FORMATOS):
                cls.activar_download(0)
            elif(type_e==constantes.EV_ACTIVAR_DOWNLOAD_CARNETS):
                cls.activar_download(1)
            elif(type_e==constantes.EV_ACTIVAR_DOWNLOAD_CONSTANCIAS):
                cls.activar_download(2)          
        elif(type_e>=constantes.EV_CONSULTAR_PERSONAL and type_e<=constantes.EV_CONSULTAR_MAT_PEND):
           #Consult Event
           from Consult_Manager import Consult_Manager
           opcion=-1
           if(type_e==constantes.EV_CONSULTAR_PERSONAL):
               opcion=Consult_Manager.CONSULT_WORKERS
           elif(type_e==constantes.EV_CONSULTAR_ESTUDIANTE):
               opcion=Consult_Manager.CONSULT_STUDENTS
           elif(type_e==constantes.EV_CONSULTAR_PROFESORES):
               opcion=Consult_Manager.CONSULT_TEACHERS
           elif(type_e==constantes.EV_CONSULTAR_SECCIONES):
              opcion=Consult_Manager.CONSULT_SECTIONS
           elif(type_e==constantes.EV_CONSULTAR_MOMENTOS):
               opcion=Consult_Manager.CONSULT_ACADEMIC_MOMENTS
           elif(type_e==constantes.EV_CONSULTAR_DISP_HORARIO):
               opcion=Consult_Manager.CONSULT_TIMETABLES_DISPONIBILITY
           elif(type_e==constantes.EV_CONSULTAR_AREA_FORMACION):
               opcion=Consult_Manager.CONSULT_FORMATION_AREAS          
           elif(type_e==constantes.EV_CONSULTAR_AREAS_DOCENTES):
               opcion=Consult_Manager.CONSULT_FORMATION_AREAS_TEACHERS
           elif(type_e==constantes.EV_CONSULTAR_MAT_PEND):
               opcion=Consult_Manager.CONSULT_MATERIA_PENDIENTE
           elif(type_e==constantes.EV_CONSULTAR_DESCARGAS):
              opcion=Consult_Manager.CONSULT_DOWNLOADS
           if(opcion!=-1):   
              cls.consultar(opcion)
        elif(type_e>=constantes.EV_FINALIZAR_PROCESO and type_e<=constantes.EV_SEARCH_ESTUD):
           #General process Event
           if(type_e==constantes.EV_SEARCH_ESTUD):
               cls.search_estud()
        elif(type_e>=constantes.EV_INSCRIPCION_NUEVO_INGRESO and type_e<=constantes.EV_INIT_EXPEDIENTE):
           #Inscription Event
           from Process_Manager import Process_Manager
           if(type_e==constantes.EV_INSCRIPCION_NUEVO_INGRESO):
               cls.inscribir(Process_Manager.INSCRIPTION_NUEVO_INGRESO)
           elif(type_e==constantes.EV_INSCRIPCION_REGULAR):
               cls.inscribir(Process_Manager.INSCRIPTION_REGULAR)
           elif(type_e==constantes.EV_NEXT_INSCRIP):
               cls.inscribir(Process_Manager.INSCRIPTION_UNDEFINED,Process_Manager.INSCRIPTION_VERIFY_DATA_STUDENT)
           elif(type_e==constantes.EV_FINISH_INSCRIP):
               cls.inscribir(Process_Manager.INSCRIPTION_UNDEFINED,Process_Manager.INSCRIPTION_CONFIRM_INSCRIPTION)
           elif(type_e==constantes.EV_INIT_EXPEDIENTE):
               cls.asign_expediente()  
        elif(type_e>=constantes.EV_PLANIFIC_CRONOGRAMA and type_e<=constantes.EV_MODIFIC_CONTENT_FORMATO):
           #Planification Event
           if(type_e==constantes.EV_PLANIFIC_FORMATOS):
               cls.planificar_forms()  
           elif(type_e==constantes.EV_PLANIFIC_CRONOGRAMA):
              cls.planificar_cronog()
           elif(type_e==constantes.EV_GESTION_CRONOG1):
              cls.validar_cronog("general")
           elif(type_e==constantes.EV_GESTION_CRONOG2):
              cls.validar_cronog("mat pendiente")
           elif(type_e==constantes.EV_GESTION_CRONOG3):
              cls.validar_cronog("momento 1")
           elif(type_e==constantes.EV_GESTION_CRONOG4): 
              cls.validar_cronog("momento 2")
           elif(type_e==constantes.EV_GESTION_CRONOG5):
              cls.validar_cronog("momento 3")
           elif(type_e==constantes.EV_ADD_COL_FORMAT):
               cls.agregar_columna()
           elif(type_e==constantes.EV_DELETE_COL_FORMAT):
               cls.eliminar_columna()
           elif(type_e==constantes.EV_MODIF_COL_FORMAT):
               cls.modif_col() 
           elif(type_e==constantes.EV_REPORTE_CRONOG):
               cls.generar_reporte("cronograma") 
           elif(type_e==constantes.EV_GESTION_FORMATOS):
               cls.next_formatos()
           elif(type_e==constantes.EV_MODIFIC_SOURCE_FORMATO):             
               cls.registrar_formato(True)
           elif(type_e==constantes.EV_MODIFIC_CONTENT_FORMATO):             
               cls.update_formato()    
           elif(type_e==constantes.EV_INIT_GESTION_CRONOG):
               cls.set_cronog()  
        elif(type_e>=constantes.EV_RENDIMIENTO_GESTION_CALIFIC and type_e<=constantes.EV_REGISTRAR_CALIFICACION):
           #Rendimiento Event
           if(type_e==constantes.EV_RENDIMIENTO_GESTION_CALIFIC):
              cls.set_rendimiento(0)
           elif(type_e==constantes.EV_RENDIMIENTO_SABANA):
              cls.set_rendimiento(1)
           elif(type_e==constantes.EV_RENDIMIENTO_MATERIA_PEND):
              cls.set_rendimiento(3)
           elif(type_e==constantes.EV_RENDIMIENTO_NOTAS_CERTIFIC):
              cls.set_rendimiento(4)
           elif(type_e==constantes.EV_GESTIONAR_MAT_PEND):
              cls.set_rendimiento(5)
           elif(type_e==constantes.EV_GESTIONAR_CALIF):
               cls.set_rendimiento(6)
           elif(type_e==constantes.EV_REGISTRAR_INTENTO_MAT_PEND):
              cls.set_rendimiento(7)
           elif(type_e==constantes.EV_MODIFIC_CALIF_FINAL):
             cls.modific_calif_final()
           elif(type_e==constantes.EV_REPORTE_NOTAS):
              cls.generar_reporte("notas finales")
           elif(type_e==constantes.EV_REPORTE_NOTAS_AÑO):
              cls.sabana_notas(True)
           elif(type_e==constantes.EV_REPORTE_NOTAS_MOMENTO):
              cls.generar_reporte("notas del momento")
           elif(type_e==constantes.EV_REPORTE_EVALUACION_SECCION):
              cls.generar_reporte("evaluacion continua")
           elif(type_e==constantes.EV_REGISTRAR_CALIFICACION):
              cls.registrar_calificacion()
           elif(type_e==constantes.EV_MODIFIC_CALIFIC):
              cls.modific_calific_mom()
           elif(type_e==constantes.EV_ESTIMULAR_AREA):
               cls.estimular_mom()
           elif(type_e==constantes.EV_DELETE_CALIFIC):
               cls.delete_calific()
           elif(type_e==constantes.EV_REMOVE_ESTIMULACION):
               cls.remover_estimulacion_mom()
           elif(type_e==constantes.EV_GENERAR_SABANA):
               cls.sabana_notas()  
        elif(type_e>=constantes.EV_REPORTE_NOMINA_SECCION and type_e<=constantes.EV_LIMPIAR_REPORTES):
           from Consult_Manager import Consult_Manager
           #Report and Download Event
           if(type_e==constantes.EV_REPORTE_ASISTENCIA_SECCION):
              cls.generar_reporte("asistencia seccion")
           elif(type_e==constantes.EV_REPORTE_NOMINA_SECCION):
              cls.generar_reporte("lista de la seccion")
           elif(type_e==constantes.EV_REPORTE_INFO_ESTUDIANTE):
              cls.generar_reporte("info estudiante")
           elif(type_e==constantes.EV_REPORTE_INFO_TRABAJADOR):
              cls.generar_reporte("info trabajador")
           elif(type_e==constantes.EV_REPORTE_DISPONIBILIDAD_HORARIO):
              cls.generar_reporte("disp horario")
           elif(type_e==constantes.EV_REPORTE_ESTUDIANTE_MAT_PENDIENTE):
              cls.generar_reporte("materia pendiente")
           elif(type_e==constantes.EV_DOWNLOAD_EXPEDIENTE_ESTUD):
              cls.download_doc(Consult_Manager.DOCUMENT_EXPEDENT_STUDENT) 
           elif(type_e==constantes.EV_DOWNLOAD_EXPEDIENTE_PERSONAL):
              cls.download_doc(Consult_Manager.DOCUMENT_EXPEDENT_WORKER) 
           elif(type_e==constantes.EV_DESCARGAR_HORARIO):
               cls.download_doc(Consult_Manager.DOCUMENT_TIMETABLES_WORKER)     
           elif(type_e==constantes.EV_DESCARGAR_HORARIO_SECCION):
               cls.download_doc(Consult_Manager.DOCUMENT_TIMETABLES_SECTION)   
           elif(type_e==constantes.EV_DESCARGAR_CONSTANCIA):
               cls.generar_reporte("constancias")        
           elif(type_e==constantes.EV_DESCARGA_CARNET):
              cls.generar_reporte("carnet")
           elif(type_e==constantes.EV_REPORTE_ACCIONES_USUARIOS):
              cls.generar_reporte("reporte de usuarios")
           elif(type_e==constantes.EV_REPORTE_DESCARGAS):
              cls.generar_reporte("reporte de descargas")    
           elif(type_e==constantes.EV_LIMPIAR_REPORTES):
              cls.clear_reportes()
           elif(type_e==constantes.EV_DESCARGAR_FORMATO_ANONIMO):
              cls.descargar_formato()
           elif(type_e==constantes.EV_GENERAR_NOMINA_TRABAJ):
              cls.generar_reporte("lista de trabajadores")        

    #Determine and execute the Action Required for 'Rendimiento' Process
    @classmethod 
    def set_rendimiento(cls,opcion):
        #determina que evento de rendimiento academico se ejecutar
        from Process_Manager import Process_Manager
        Process_Manager.set_rendimiento(cls.user,cls.vent,opcion)

    #Activate the panel for format Planification
    @classmethod 
    def planificar_forms(cls):
        pnl=cls.vent.panelActual
        cls.vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO1)
    
    #Update a Format File in the Server
    @classmethod 
    def finish_update_formato(cls,archivo):
        url=constantes.SERVER+"upload.php"
        temp_file=open(archivo,"rb")
        dict_file={"file":temp_file}
        response=requests.post(url,files=dict_file)
        temp_file.close()
        if(response.status_code>400):
           General.show_error("error al actualizar datos","error inesperado")
           os.remove(archivo)
           return 
        os.remove(archivo)
        time_object=tiempo()
        cls.user.add_action_historial(["modificacion de formato",time_object.get_tiempo()])
        conexion_bd.set_tabla(constantes.TABLA_REPORTE)
        id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
        data_hist=[ id_hist,cls.user.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar formato","",time_object.get_fecha()]
        conexion_bd.add_data(data_hist)
        General.show_message("actualizacion del contenido del formato realizada exitsamente","actualizacion exitosa")
        cls.vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO1)
        cls.user.reset_data_process(0)
        
    #Request Update a format file of Server    
    @classmethod 
    def update_formato(cls):
        pnl=cls.vent.panelActual
        data_process=cls.user.get_data_process()
        url=constantes.SERVER+data_process[0][3]
        response=requests.get(url)
        if(response.status_code>400):
            General.show_error("error obteniendo data del servidor","error de data del server")
            return
        if(General.show_confirmDialog("modificar el contenido del formato?","modificar formato")!=True):
            return 
        old_file=data_process[0][3].split("/")[1]               
        lista=pnl.get_comp_byName("cols_list")
        valores=lista.get_all_values()
        reference=data_process[1][0]
        row=data_process[1][1]      
        data=[valores,reference,row,cls.vent.panelActual_str]
        file_dat=[response.content,old_file]
        documento.request(cls.vent.raiz,file_dat,8,data)
        
    #Determine and Execute the Actions in Planifications of Formats Process
    @classmethod 
    def next_formatos(cls):
        from Process_Manager import Process_Manager
        Process_Manager.Determine_Action_Planification_format(cls.user,cls.vent)
        
    #Validate the Cronogram Values For Planification process   
    @classmethod 
    def validar_cronog(cls,parte):
        from Process_Manager import Process_Manager
        Process_Manager.verify_cronogram(cls.user,cls.vent,parte)
                
    #Interprete the the Action  in  Cronogram Planification
    @classmethod 
    def set_cronog(cls):
        from Process_Manager import Process_Manager
        Process_Manager.set_cronogram(cls.user,cls.vent)
     
    #Reset the Cronogram
    @classmethod 
    def reset_cronog(cls,id_cronog,last_moment_close):
        from Process_Manager import Process_Manager
        Process_Manager.reset_cronogram(cls.user,cls.vent,last_moment_close)        
    
    #Show the Available Options for the Planification of Cronogram   
    @classmethod 
    def planificar_cronog(cls,autollamado=False): 
        from Process_Manager import Process_Manager
        if(autollamado==False):
           cls.vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1)
           cls.vent.raiz.after(200,Process_Manager.show_planificar_cronogOption,cls.user,cls.vent,autollamado)
           return
        Process_Manager.show_planificar_cronogOption(cls.user,cls.vent,autollamado)
    
    #Remove a Calification Associated to an Academic Moment
    @classmethod 
    def delete_calific(cls):
        from Process_Manager import Process_Manager
        Process_Manager.delete_calification(cls.user,cls.vent)
    
    #Modify the Calification Associated to an Academic Moment  
    @classmethod 
    def modific_calific_mom(cls):
        from Process_Manager import Process_Manager
        Process_Manager.update_calification(cls.user,cls.vent)
    
    #Remove Estimulation Point Associated to an Academic Moment
    @classmethod 
    def remover_estimulacion_mom(cls):   
        from Process_Manager import Process_Manager
        Process_Manager.remover_estimulacion_mom(cls.user,cls.vent)
    
    #Assign Estimulation Point Associated to an Academic Moment   
    @classmethod 
    def estimular_mom(cls):        
         from Process_Manager import Process_Manager
         Process_Manager.estimular_mom(cls.user,cls.vent)
                        
    #Modify Definite Calification for Especials cases
    @classmethod      
    def modific_calif_final(cls):
       from Process_Manager import Process_Manager
       Process_Manager.modific_calif_final(cls.user,cls.vent)
                   
    #Generate the document "sabana de notas"
    @classmethod 
    def sabana_notas(cls,con_notas=False):
       from Process_Manager import Process_Manager
       Process_Manager.generate_sabana_notas(cls.user,cls.vent,con_notas)
     
    #Make a Inscription for a Student 
    @classmethod
    def inscribir(cls,type_i,fase=0):
      from Process_Manager import Process_Manager
      Process_Manager.inscribir(cls.user,cls.vent,type_i,fase)
            
    #Set the Data of Student in the required Components
    @classmethod
    def set_data_estud(cls,cedula_estud,regular,cedula_repres="",alternative_data=[]):
        pnl=cls.vent.panelActual
        if(regular): 
            cedulado=True
            estud=estudiante()           
            dat=estud.get_data_estud(cedula_estud,cedula_repres)
            if(dat!=[]):
              if(len(dat)==3 or len(dat)==2):
                data_estud=dat[0]
                data_repres=[]
                data_exp=[]
                dire=""
                if(len(dat)==3):
                   cedulado=False
                   data_repres=dat[1]
                   data_exp=dat[2][0]
                else:
                   data_exp=dat[1][0]
                   conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                   data_repres_temp=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[data_estud[8]],["and"])
                   if(data_repres_temp!=[]):
                     for representant_field in range(0,len(data_repres_temp[0])):
                        if(representant_field==1):
                            id_nomb=data_repres_temp[0][representant_field]
                            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                            data_n_representant=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[id_nomb],["and"])
                            nombre=data_n_representant[0][0]
                            apellido=data_n_representant[0][1]
                            if(data_n_representant[0][2]!="" and data_n_representant[0][2]!="..."):
                                 nombre=nombre+" "+data_n_representant[0][2]
                            if(data_n_representant[0][3]!="" and data_n_representant[0][3]!="..."):
                                 apellido=apellido+" "+data_n_representant[0][3]
                            data_repres.append(nombre)
                            data_repres.append(apellido)
                        else:
                            data_repres.append(data_repres_temp[0][representant_field])     
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                data_dire=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[data_estud[11]],["and"])[0]
                dire=data_dire[1]+","+data_dire[2]+","+data_dire[3]
                conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_ESTUD,len(constantes.CAMPOS_ESTATUS_ESTUD),[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[5]],["and"])
                fields=pnl.get_comps_byTag("field")
                for i in range(0,len(fields)):                
                    if(fields[i].get_id()=="cedula_estud"):
                        fields[i].set_text(data_estud[0])
                    elif(fields[i].get_id()=="nombre"):
                        if(data_estud[2]!=""):
                             fields[i].set_text(data_estud[1]+" "+data_estud[2])
                        else:
                             fields[i].set_text(data_estud[1])    
                    elif(fields[i].get_id()=="apellido"):
                        if(data_estud[4]!=""):
                             fields[i].set_text(data_estud[3]+" "+data_estud[4])
                        else:
                             fields[i].set_text(data_estud[3])   
                    elif(fields[i].get_id()=="CIrepres"):
                        fields[i].set_text(data_repres[0])
                        if(cedulado==False):
                             fields[i].set_state("readonly")  
                        else:
                             fields[i].set_state("normal")                       
                    elif(fields[i].get_id()=="telef"):
                        fields[i].set_text(data_repres[3])    
                    elif(fields[i].get_id()=="nombre_repres"):
                        fields[i].set_text(data_repres[1]) 
                        if(cedulado==False):
                             fields[i].set_state("readonly")  
                        else:
                             fields[i].set_state("normal") 
                    elif(fields[i].get_id()=="apellido_repres"):
                        fields[i].set_text(data_repres[2])
                        if(cedulado==False):
                             fields[i].set_state("readonly")  
                        else:
                             fields[i].set_state("normal")                          
                    elif(fields[i].get_id()=="destino_file"):
                        if(data_exp[1]!="" and data_exp[1]!="..."):
                             fields[i].set_text(data_exp[1])                            
                    elif(fields[i].get_id()=="destino_foto"):
                        if(data_exp[2]!="" and data_exp[2]!="..."):
                             fields[i].set_text(data_exp[2])   
                    elif(fields[i].get_id()=="fecha"):
                        fields[i].set_text(data_estud[10])
                        fields[i].set_state("readonly")   
                    elif(fields[i].get_id()=="direccion"):
                         fields[i].set_text(dire)
                    elif(fields[i].get_id()=="dir_representante"):
                        dir_code=data_repres[6]
                        conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                        data_dir_r=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[dir_code],["and"])[0]
                        direccion_r=data_dir_r[1]+","+data_dir_r[2]+","+data_dir_r[3]
                        fields[i].set_text(direccion_r)
                    elif(fields[i].get_id()=="correo"):
                        fields[i].set_text(data_repres[4])
                    elif(fields[i].get_id()=="oficio"):
                        fields[i].set_text(data_repres[5])
                    elif(fields[i].get_id()=="parentesco"):
                        fields[i].set_text(data_estud[12])
                combos=pnl.get_comps_byTag("combo")
                for i in range(0,len(combos)):
                    if(combos[i].get_id()=="salud"):
                        combos[i].set_value(data_estatus[0][2]) 
                radio= pnl.get_comp_byName("genero") 
                radio.set_value(data_estud[9]) 
              else:
                  General.show_error("error datos incompletos","error de datos")           
            else:
                General.show_error("error cargando data","error de datos")        
        else:           
            d_repres=[]
            if(cedula_repres!=""):
                 conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                 d_repres=[]
                 d_repres_temp=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[cedula_repres],["and"])
                 if(d_repres_temp!=[]):
                     for representant_field in range(0,len(d_repres_temp[0])):
                        if(representant_field==1):
                            id_nomb=d_repres_temp[0][representant_field]
                            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                            data_n_representant=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[id_nomb],["and"])
                            nombre=data_n_representant[0][0]
                            apellido=data_n_representant[0][1]
                            if(data_n_representant[0][2]!="" and data_n_representant[0][2]!="..."):
                                 nombre=nombre+" "+data_n_representant[0][2]
                            if(data_n_representant[0][3]!="" and data_n_representant[0][3]!="..."):
                                 apellido=apellido+" "+data_n_representant[0][3]
                            d_repres.append(nombre)
                            d_repres.append(apellido)
                        else:
                            d_repres.append(d_repres_temp[0][representant_field])
            fields=pnl.get_comps_byTag("field")       
            for i in range(0,len(fields)):
                if(fields[i].get_id()=="destino_file"):
                    fields[i].set_state("readonly")
                elif(fields[i].get_id()=="destino_foto"):
                     fields[i].set_state("readonly") 
                elif(fields[i].get_id()=="fecha"):
                    fields[i].set_state("normal") 
                    if(alternative_data!=[]):
                        fields[i].set_text(alternative_data[1][8])                        
                elif(fields[i].get_id()!="cedula_estud"):
                   fields[i].set_state("normal")
                   if(d_repres!=[]):
                      if(fields[i].get_id()=="CIrepres"):
                           fields[i].set_text(d_repres[0])
                           fields[i].set_state("readonly")
                      elif(fields[i].get_id()=="nombre_repres"):
                           fields[i].set_text(d_repres[1])
                           fields[i].set_state("readonly")  
                      elif(fields[i].get_id()=="apellido_repres"):
                           fields[i].set_text(d_repres[2])
                           fields[i].set_state("readonly")  
                      elif(fields[i].get_id()=="telef"):
                           fields[i].set_text(d_repres[3])
                      elif(fields[i].get_id()=="dir_representante"):
                           dir_code=d_repres[6]
                           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                           data_dir_r=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[dir_code],["and"])[0]
                           direccion_r=data_dir_r[1]+","+data_dir_r[2]+","+data_dir_r[3]
                           fields[i].set_text(direccion_r)
                      elif(fields[i].get_id()=="oficio"):
                           fields[i].set_text(d_repres[5])                    
                      elif(fields[i].get_id()=="correo"):
                           fields[i].set_text(d_repres[4])
                   elif(alternative_data!=[]):
                      if(fields[i].get_id()=="CIrepres"): 
                           fields[i].set_text(alternative_data[2][0])
                           if(alternative_data[0][2].lower()=="true"):
                                fields[i].set_state("readonly")
                      elif(fields[i].get_id()=="nombre_repres"):
                           temp_name=alternative_data[2][1]
                           if(alternative_data[2][11]!=""):
                              temp_name=temp_name+" "+alternative_data[2][11]
                           fields[i].set_text(temp_name)
                           if(alternative_data[0][2].lower()=="true"):
                                fields[i].set_state("readonly")
                      elif(fields[i].get_id()=="apellido_repres"):
                           temp_dat=alternative_data[2][2]
                           if(alternative_data[2][12]!=""):
                               temp_dat=temp_dat+" "+alternative_data[2][12]
                           fields[i].set_text(temp_dat)
                           if(alternative_data[0][2].lower()=="true"):
                               fields[i].set_state("readonly")
                      elif(fields[i].get_id()=="telef"):
                           fields[i].set_text(alternative_data[2][3])
                      elif(fields[i].get_id()=="dir_representante"):
                           direccion_r=alternative_data[2][7]+","+alternative_data[2][8]+","+alternative_data[2][9]
                           fields[i].set_text(direccion_r)
                      elif(fields[i].get_id()=="oficio"):
                           fields[i].set_text(alternative_data[2][13])                  
                      elif(fields[i].get_id()=="correo"):
                           fields[i].set_text(alternative_data[2][4]) 
                      elif(fields[i].get_id()=="parentesco"):
                           fields[i].set_text(alternative_data[2][10])  
                      elif(fields[i].get_id()=="direccion"):
                           dire=alternative_data[3][2]+","+alternative_data[3][3]+","+alternative_data[3][4]
                           fields[i].set_text(dire)   
                      elif(fields[i].get_id()=="nombre"):
                             temp_name=alternative_data[1][0]
                             if(alternative_data[1][2]!=""):
                                 temp_name=temp_name+" "+alternative_data[1][2] 
                             fields[i].set_text(temp_name) 
                      elif(fields[i].get_id()=="apellido"):                             
                             temp_data=alternative_data[1][1]
                             if(alternative_data[1][3]!=""):
                                 temp_data=temp_data+" "+alternative_data[1][3] 
                             fields[i].set_text(temp_data)    
                else:
                   fields[i].set_text(cedula_estud)                
    
    #Download the Data of a Format Indicated in the Respective ComboBox Component
    @classmethod 
    def descargar_formato(cls):
       pnl=cls.vent.panelActual
       form=pnl.get_comp_byName("formatos").get_selected_value()
       seccion_nomina=""
       trabaj=pnl.get_comp_byName("trabajador").get_selected_value()
       if(trabaj=="elejir" or trabaj=="elegir"):
           General.show_message("por favor indique el trabajador que descargar el formato","trabajador no valido")
           return           
       id_trabaj=trabaj.split("-")
       if(len(id_trabaj)==3):
          id_trabaj=id_trabaj[0]+"-"+id_trabaj[1]
       elif(len(id_trabaj)==2):
          id_trabaj=id_trabaj[0]
       else:
          id_trabaj=""
       if(form=="elejir" or form=="elegir"):
           General.show_message("por favor seleccione un formato","formato no valido")
           return
       if(form=="evaluacion continua" or form=="lista de la seccion" or form=="asistencia seccion"):
          s=pnl.get_comp_byName("seccion").get_selected_value()
          if(s!="elejir" and s!="elegir"):
             seccion=s
             cls.generar_reporte(form,None,seccion)
             ti=tiempo()
             conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
             data_descarga=[conexion_bd.generate_id(True,constantes.CLAVE_DESCARGA_DOCUMENTO), id_trabaj,form,ti.get_fecha(),ti.get_tiempo(),"formato",ti.get_fecha()]
             conexion_bd.add_data(data_descarga)
          else:          
            General.show_message("por favor seleccione una seccion","seccion no valida")
          return             
       conexion_bd.set_tabla(constantes.TABLA_FORMATO)
       data_form=conexion_bd.get_allData(["src_form"],1,[constantes.CLAVE_FORMATO],[form],["and"])
       time_object=tiempo()
       if(data_form!=[]):
          src_form=data_form[0][0]
          url=constantes.SERVER+src_form
          response=requests.get(url)
          if(response.status_code>400):
             General.show_error("error descargando data","error de conexion")
             return
          raw=response.content
          extension=src_form.split(".")[1]
          ruta=constantes.FOLDER_DOCUMENTS+form+"."+extension
          temp_file=open(ruta,"wb")
          temp_file.write(raw)
          temp_file.close()         
          conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
          data_descarga=[conexion_bd.generate_id(True,constantes.CLAVE_DESCARGA_DOCUMENTO), id_trabaj,form,time_object.get_fecha(),time_object.get_tiempo(),"formato",time_object.get_fecha()]
          conexion_bd.add_data(data_descarga)
          os.startfile(ruta)  
       else:
         General.show_message("error encontrando data del formato","formato no encontrado")
    
    #Manage the Password Recovery from a User
    @classmethod  
    def recuperar_pass(cls,fase):
        from Service_Manager import Service_Manager
        Service_Manager.recuperar_password(cls.user,cls.vent,fase)
    
    #Verify the Academic Moments and Change their Status
    @classmethod
    def verificar_momentos(cls):
       conexion_bd.set_tabla(constantes.TABLA_FECHA_MOM)
       data=conexion_bd.get_allData(None,None)      
       for i in range(0,len(data)):
          terminado=False
          if(data[i][2]=="cierre momento"):
              ti=tiempo()
              fecha=ti.get_fecha().split("/")
              tiemp=ti.get_tiempo().split(":")
              fecha2=data[i][3].split("/")
              tiempo2=data[i][4].split(":")              
              is_date=False
              terminado=False
              if(int(fecha[2])>int(fecha2[2])):
                  is_date=True
                  terminado=False
              elif(int(fecha[1])>int(fecha2[1]) and int(fecha[2])==int(fecha2[2])):
                  is_date=True
                  terminado=False
              elif(int(fecha[0])>=int(fecha2[0]) and int(fecha[1])==int(fecha2[1]) and int(fecha[2])==int(fecha2[2])):
                  is_date=True
                  if(int(fecha[0])==int(fecha2[0])):
                     if(int(tiemp[0])>int(tiempo2[0])):
                         terminado=True  
                     elif(int(tiemp[1])>int(tiempo2[1]) and int(tiemp[0])==int(tiempo2[0])):
                         terminado=True
                     elif(int(tiemp[2])>=int(tiempo2[2]) and int(tiemp[1])==int(tiempo2[1]) and int(tiemp[0])==int(tiempo2[0])):
                         terminado=True                       
                  else:
                    terminado=True                                                   
              if(terminado and is_date):
                 conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                 conexion_bd.update_data(["abierto"],["False"],1,[constantes.CLAVE_MOMENTO],[data[i][1]],["and"])
                 
    #Search and Verify if the Student with the Indicated Student Id Exist  
    @classmethod   
    def search_estud(cls,cedula="",nombre=""):
       pnl=cls.vent.panelActual
       pantalla=cls.vent.panelActual_str
       if(pantalla==constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA):
          if(cedula!=""):
             pnl.get_comp_byName("cedula_p1").set_text(cedula)
             pnl.get_comp_byName("nombre_p1").set_text(nombre)
             conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
             data_areas=conexion_bd.get_allData(constantes.CAMPOS_AREA_FORMACION,len(constantes.CAMPOS_AREA_FORMACION),["incorporada"],["Si"],["and"])             
             lista_areas=["elegir"]
             curso=pnl.get_comp_byName("year").get_text()
             if(curso!=""):
                 if(data_areas!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                    for area in data_areas:
                        
                       data_year=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],1,[constantes.CLAVE_AÑOS_INCORPORADOS,curso+"_año"],[area[2],"True"],["and","and"]) 
                       if(data_year!=[]):
                           lista_areas.append(area[0])         
             pnl.get_comp_byName("area_form").set_values(lista_areas)
             pnl.get_comp_byName("area_form").set_selected_index(0)
          else:
             lista_areas=["elegir"]
             pnl.get_comp_byName("cedula_p1").set_text("")
             pnl.get_comp_byName("nombre_p1").set_text("")
             pnl.get_comp_byName("area_form").set_values(lista_areas)
             pnl.get_comp_byName("area_form").set_selected_index(0)
       elif(pantalla==constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND):
           if(cedula!=""):
               pnl.get_comp_byName("cedula_p3").set_text(cedula)
               pnl.get_comp_byName("nombre_p3").set_text(nombre)
               conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
               data_areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])             
               lista_areas=["elegir"]
               if(data_areas!=[]):
                    for area in data_areas:
                        lista_areas.append(area[0])       
               pnl.get_comp_byName("area_form").set_values(lista_areas)
               pnl.get_comp_byName("area_form").set_selected_index(0)
           else:
             lista_areas=["elegir"]
             pnl.get_comp_byName("cedula_p3").set_text("")
             pnl.get_comp_byName("nombre_p3").set_text("")
             pnl.get_comp_byName("area_form").set_values(lista_areas)
             pnl.get_comp_byName("area_form").set_selected_index(0)
       elif(pantalla==constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF_FINALES):      
            field_ced4=pnl.get_comp_byName("identificador")
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            data_estud=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_ESTATUS_ESTUD],2,[constantes.CLAVE_ESTUDIANTE],[field_ced4.get_text()],["and"])          
            if(data_estud!=[]):
               conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
               data_estatus=conexion_bd.get_allData(["last_year","estatus"],2,[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][1]],["and"])
               conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
               data_califs=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE],[data_estud[0][0]],["and"])
               if(data_califs!=[]):
                   t=pnl.get_comp_byName("table1_p1")
                   t.reset()
                   for i in range(0,len(data_califs)):
                      dat=[data_califs[i][3],data_califs[i][2],data_califs[i][4]]
                      t.add_row(dat)
                   pnl.get_comp_byName("year_estud1").set_text(data_estatus[0][0])
               else:
                 pnl.get_comp_byName("year_estud1").set_text("")
                 General.show_message("estudiante sin ningun registro de calificaciones","sin registros")
            else:
              pnl.get_comp_byName("year_estud1").set_text("")
              General.show_message("cedula del estudiante inexistente","cedula invalida")
   
   
   #Manage the Operation in User Gestion Panel except Register New User            
    @classmethod 
    def gestion_usuario(cls,opcion):
       from Service_Manager import Service_Manager
       Service_Manager.gestion_usuario(cls.user,cls.vent,opcion)
       
    #Make a Consult to the Data Base Information        
    @classmethod 
    def consultar(cls,opcion):
        from Consult_Manager import Consult_Manager
        Consult_Manager.consultar(cls.vent,opcion)

    #Load the Data of Student and set it On a ComboBox
    @classmethod 
    def load_estuds_combobox(cls):
            pnl=cls.vent.panelActual
            estud_lista=pnl.get_comp_byName("estudiantes")
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            estuds=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE))
            new_data=["elegir"]
            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
            for i in range(0,len(estuds)):
               data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[estuds[i][1]],["and"])
               dat=estuds[i][0]+"-"+data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize()
               new_data.append(dat)
            estud_lista.set_values(new_data)
       
    #Manage Security Copies of Data Base
    @classmethod 
    def respaldar(cls):
       from Service_Manager import Service_Manager
       Service_Manager.Security_Copies_Manage(cls.user,cls.vent)
      
    #Reset the Activate value of an Academic Moment    
    @classmethod 
    def reestablecer_momento(cls):
       from Service_Manager import Service_Manager
       Service_Manager.reestablecer_momento(cls.user,cls.vent)
    
    #Reactivate an Academic Moment for a Time Limit    
    @classmethod 
    def activar_momento(cls):  
       from Service_Manager import Service_Manager
       Service_Manager.activar_momento(cls.user,cls.vent)
    
    #Organizate The sections     
    @classmethod 
    def organizar_seccion (cls,opcion):
        from Service_Manager import Service_Manager
        Service_Manager.organizar_secciones(cls.user,cls.vent,opcion)
        
    #Set the Value of Teachuer Guia Component in the Panel for Organizate Sections
    @classmethod 
    def set_guia(cls,valor):  
       pnl=cls.vent.panelActual
       combo=pnl.get_comp_byName("guia")
       combo.set_value(valor)
     
    #Stadistics Service     
    @classmethod 
    def estadistica(cls):
       from Service_Manager import Service_Manager
       Service_Manager.stadistics(cls.user,cls.vent)
           
    
   
    #Reset the Active Panel Components Values
    @classmethod
    def reset(cls):
       pnl=cls.vent.panelActual
       pantalla=cls.vent.panelActual_str
       
       if(pantalla==constantes.PANTALLA_REGISTRO_USUARIO or pantalla==constantes.PANTALLA_UPDATE_USER):
            fields=pnl.get_comps_byTag("field")
            combos=pnl.get_comps_byTag("combo")
            pass_f=pnl.get_comps_byTag("pass")
            for p_f in pass_f:
               p_f.set_text("")
            for fi in fields:
               fi.set_text("")
               id_f=fi.get_id()
               if(id_f.startswith("respuesta")):
                     fi.set_state("readonly")
            for comb in combos:
               comb.set_selected_index(0)
       elif(pantalla==constantes.PANTALLA_INICIO):
           fields=pnl.get_comps_byTag("field")
           pass_f=pnl.get_comps_byTag("pass")
           for p_f in pass_f:
               p_f.set_text("")
           for fi in fields:
               fi.set_text("")
       elif(pantalla==constantes.PANTALLA_REGISTRO_AREA_FORMACION):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           checks=pnl.get_comps_byTag("check")
           for chck in checks:
              chck.set_selected(False)
           combos=pnl.get_comp_byTag("combo")
           combos.set_selected_index(0)
           pnl.get_comp_byName("incorporada_Label").set_active(False)
           pnl.get_comp_byName("incorporada").set_active(False)
           pnl.get_comp_byName("registrar_ru").set_active(True)
           pnl.get_comp_byName("actualizar_ru").set_active(False)
       elif(pantalla==constantes.PANTALLA_REGISTRO_PERSONAL):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           combos=pnl.get_comps_byTag("combo")
           for comb in combos:
             comb.set_selected_index(0)
           pnl.get_comp_byTag("radio").set_value("docente")  
           pnl.get_comp_byName("caja3_rp",False).set_active(False)
           pnl.get_comp_byName("caja_areas",False).set_active(False)
           pnl.get_comp_byName("registrar_rp").set_active(True)
           pnl.get_comp_byName("actualizar_rp").set_active(False)
       elif(pantalla==constantes.PANTALLA_REGISTRO_DISP_HORARIO):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           combos=pnl.get_comps_byTag("combo")
           for comb in combos:
             comb.set_selected_index(0)
           pnl.get_comp_byName("registrar_rdh").set_active(True)
           pnl.get_comp_byName("actualizar_rdh").set_active(False)
       elif(pantalla==constantes.PANTALLA_REGISTRO_FORMATO):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           combos=pnl.get_comps_byTag("combo")
           for comb in combos:
             comb.set_selected_index(0)
           pnl.get_comp_byName("registrar_ru").set_active(True)
           pnl.get_comp_byName("actualizar_ru").set_active(False)
       elif(pantalla==constantes.PANTALLA_REGISTRO_HORARIO):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           pnl.get_comp_byName("turno_rh").set_active(True)
           combos=pnl.get_comps_byTag("combo")
           for comb in combos:
             comb.set_selected_index(0)
           pnl.get_comp_byName("registrar").set_active(True)
           pnl.get_comp_byName("actualizar").set_active(False)
           pnl.get_comp_byName("secc_rh").set_active(False)
           pnl.get_comp_byName("personal_rh").set_active(False)
           pnl.get_comp_byName("secc_label").set_active(False)
           pnl.get_comp_byName("personal_label").set_active(False)
           pnl.get_comp_byName("turno_seccion").set_active(False)
       elif(pantalla==constantes.PANTALLA_UPDATE_ESTUDIANTE):
           fields=pnl.get_comps_byTag("field")
           for fi in fields:
               fi.set_text("")
           combos=pnl.get_comps_byTag("combo")
           for comb in combos:
             comb.set_selected_index(0)
           pnl.get_comp_byTag("radio").set_value("masculino")
           pnl.get_comp_byName("cedulado").set_active(False)
           pnl.get_comp_byName("cedulado_label").set_active(False)
       elif(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_2 or pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_3):
             fields=pnl.get_comps_byTag("field")
             for i in range(0,len(fields)):
                 if(fields[i].get_id()!="cedula_estud"):
                      if(fields[i].get_field_state()!="readonly" and fields[i].get_field_state()!="disabled"):
                              fields[i].set_text("")
                      else:
                          if(fields[i].get_id().startswith("destino")):
                               fields[i].set_text("")
             combos=pnl.get_comps_byTag("combo")
             for j in range(0,len(combos)):
                combos[j].set_selected_index(0)             
             radio=pnl.get_comp_byTag("radio")
             radio.set_value("masculino")
    
    #Assign a Formation Area to the Teacher Workers
    @classmethod   
    def agregar_area_docente(cls):
       pnl=cls.vent.panelActual
       combo=pnl.get_comp_byName("areas")
       valor=combo.get_selected_value()
       if(valor!="elejir" and valor!="elegir"):
         lista=pnl.get_comp_byName("lista_areas")
         lista.insert_value(valor)
         combo.set_selected_index(0)
     
    #Request to Remove a Column to the List of Modifications Over a Excel Format 
    @classmethod 
    def eliminar_columna(cls):
       pnl=cls.vent.panelActual
       field=pnl.get_comp_byName("val_delete_col")
       valor=""
       lista=None
       valor=field.get_text()
       lista=pnl.get_comp_byName("cols_list")
       actuales=lista.get_all_values()
       if(valor!="" and valor!=" "):
            if(valor==cls.user.get_data_process()[1][0]):
               General.show_message("no se puede eliminar la columna de referencia","columna no valida")
               return
            index=-1
            for i in range(0,len(actuales)):
               if(actuales[i]==valor):
                   index=i
                   break
            new_list=[]
            for i in range(0,len(actuales)):
                if(i<index or i>index):
                   new_list.append(actuales[i])
            lista.set_values(new_list) 
            field.set_text("")
            pnl.get_comp_byName("val_col").set_text("") 
            pnl.get_comp_byName("cols_edit").set_text("")                                 
       else:
          General.show_message("por seleccione una columna","columna no invalida")
    
    #Request to Modify a Column to the List of Modifications Over a Excel Format 
    @classmethod 
    def modif_col(cls):
       pnl=cls.vent.panelActual
       field=pnl.get_comp_byName("cols_edit")
       new_val=field.get_text()
       field_modif=pnl.get_comp_byName("val_delete_col")
       select= field_modif.get_text() 
       if(select!=""):          
            if(select==cls.user.get_data_process()[1][0]):
               General.show_message("no se puede modificar la columna de referencia","columna no valida")
               return
            if(new_val=="" or new_val==" "):
               General.show_message("por favor escriba un valor valido para la columna","valor de columna no valido")
               return               
            lista=pnl.get_comp_byName("cols_list")
            lista.modif_selected_item(select,new_val)
            field.set_text("")
            field_modif.set_text("")
            pnl.get_comp_byName("val_col").set_text("")
     
    #Request to Add a Column to the List of Modifications Over a Excel Format 
    @classmethod 
    def agregar_columna(cls):
       pnl=cls.vent.panelActual
       field=pnl.get_comp_byName("val_col")
       valor=""
       valor=field.get_text()
       if(valor==cls.user.get_data_process()[1][0]):
               General.show_message("no se puede agregar una columna con el mismo valor que la de referencia","columna no valida")
               return               
       if(General.is_valid(valor,constantes.CADENA_ALFANUMERICA,False,1)==True):         
          lista=pnl.get_comp_byName("cols_list")
          field.set_text("")
          pnl.get_comp_byName("val_delete_col").set_text("")
          pnl.get_comp_byName("cols_edit").set_text("")
          actuales=lista.get_all_values()
          if(len(actuales)<=0):
             actuales.append(valor)
             lista.set_values(actuales)
          else:                       
              actuales=lista.get_all_values()
              actuales.append(valor)
              lista.set_values(actuales)
       else:
          General.show_message("por favor escriba una valor valido para el encabezado de la columna","encabezado de columna invalido")
          
    #Activate or Desactivate a Component or Panel 
    @classmethod     
    def activar_element(cls,nombre,valor,only_comp=False):
        pnl=cls.vent.panelActual
        pantalla=cls.vent.panelActual_str
        
        if(pantalla==constantes.PANTALLA_SERVICIO_RESPALDO_BD):
             if(nombre=="files"):
                  if(valor!=True):
                    pnl.get_comp_byName("buscar").set_active(valor)
                    fld=pnl.get_comp_byName("destino_file")
                    fld.set_text("")
                    fld.set_active(valor)
                  return                      
        elemento=pnl.get_comp_byName(nombre,only_comp)
        if(valor==True or valor==False):
            elemento.set_active(valor) 
        else:
            if(valor==-1):
                elemento.set_state("normal")
            elif(valor==-2):
                elemento.set_state("readonly")
            elif(valor==-3):
                elemento.set_state("disabled")            
    
    #Remove a Formation Area to a Teacher Worker    
    @classmethod   
    def borrar_area_docente(cls):
       pnl=cls.vent.panelActual
       fld=pnl.get_comp_byName("field_delete")
       valor=fld.get_text()
       if(valor=="" or valor==" "):
          General.show_message("por favor seleccione una area a quitar","elija un item")
          return
       temp_d=valor.split("-")
       index=temp_d[0]
       valor_item=temp_d[1]
       lista=pnl.get_comp_byName("lista_areas")
       lista.delete_element(int(index))
       fld.set_text("")
     
    #Set the File Source in a TextField 
    @classmethod
    def set_file(cls,is_image=False):
        pnl=cls.vent.panelActual
        pantalla=cls.vent.panelActual_str        
        destino=None
        dest=General.get_fileSource()
        destino=None
        if(is_image):
          if(pantalla==constantes.PANTALLA_REGISTRO_FORMATO):
               destino=pnl.get_comp_byName("firma_file")  
          elif(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_3 or pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_2 or pantalla==constantes.PANTALLA_UPDATE_ESTUDIANTE):
              destino=pnl.get_comp_byName("destino_foto")  
          elif(pantalla==constantes.PANTALLA_REGISTRO_PERSONAL):
              destino=pnl.get_comp_byName("destino_foto")
          elif(pantalla==constantes.PANTALLA_UPDATE_USER):
              destino=pnl.get_comp_byName("icono_src")           
        else:
          destino=pnl.get_comp_byName("destino_file")  
        destino.set_text(dest) 


    #set and Show the data of User in Welcome Panel
    @classmethod
    def show_data_user(cls):
        cred=cls.user.get_credentials()
        pnl=cls.vent.panelActual
        if(cred[0]==""):
           return
        icono=pnl.get_comp_byName("logo_inicio")
        url_icono=constantes.SERVER+cred[3]
        icono.change_image(url_icono)
        msg=pnl.get_comp_byName("mensaje")
        msg.set_text("Usuario:"+cred[0]+"\n Tipo de Usuario:"+cred[2])
          
    #User Loggin
    @classmethod            		 
    def login(cls):
        pnl=cls.vent.panelActual
        pantalla=cls.vent.panelActual_str
        datos=["",""]
        field1=pnl.get_comp_byName("usuario_login")
        field2=pnl.get_comp_byName("pass_login")
        datos[0]=field1.get_text()
        datos[1]=field2.get_text()
        temp_user=usuario()
        valido=temp_user.login(datos[0],datos[1])
        if(valido[0]==0):
           #login Succes
           cls.vent.update_pantallas(constantes.PANTALLA_WELCOME)
           cred=temp_user.get_credentials()
           if(valido[1]=="admin"):
                cls.user=admin()
                cls.user.set_login(cred)         
           elif(valido[1]=="coordinador"):
               cls.user=coordinador()
               cls.user.set_login(cred)
           elif(valido[1]=="directivo"):
                cls.user=directivo()
                cls.user.set_login(cred)
           elif(valido[1]=="secretaria"):
                cls.user=secretaria()
                cls.user.set_login(cred)
           mat_permiso=cls.user.get_permiso_matrix()
           cls.verificar_caudicidad()
           pnl=cls.vent.panelActual         
           cls.show_data_user()
           menus=cls.vent.get_menu()
           pnl.set_active(True)
           cls.vent.raiz.config(menu=menus[0])
           for i in range(0,len(mat_permiso)):
              st=0
              if(mat_permiso[i][0]==True):
                 st=tk.NORMAL
              else:
                 st=tk.DISABLED
              menus[0].entryconfig(i+1,state=st)
              for j in range(1,len(mat_permiso[i])):
                 st_m=0
                 if(mat_permiso[i][j]==True):
                    st_m=tk.NORMAL
                 else:
                    st_m=tk.DISABLED  
                 menus[i+1].entryconfig((j-1),state=st_m)
           time_object=tiempo()
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           conexion_bd.add_data([conexion_bd.generate_id(True,constantes.CLAVE_REPORTE),datos[0],time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","inicio de sesion","",time_object.get_fecha()])
        else:
           #login fallido
           if(valido[0]==-1):
              General.show_message("por favor introdusca un usuario ","usuario vacio")
           elif(valido[0]==-2):
              General.show_message("por favor introdusca un password ","password vacio")
           elif(valido[0]==-3):
                General.show_message("por favor introdusca un usuario y password ","usuario y password  vacios")
           elif(valido[0]==-4):
                General.show_message("usuario o contraseña invalida","error de datos")
           elif(valido[0]==-5):
                General.show_message("usuario bloqueado","usuario bloqueado")
                    
    #Verify if The Cronogram is Finished
    @classmethod
    def verificar_caudicidad(cls):
        from Process_Manager import Process_Manager
        Process_Manager.verificar_caudicidad(cls.user,cls.vent)    
    
    #Donwload a Document from System                       
    @classmethod
    def download_doc(cls,tipo):     
        from Consult_Manager import Consult_Manager
        pnl=cls.vent.panelActual
        Consult_Manager.download_doc(pnl,tipo)
    
    #Generate a Reports    
    @classmethod
    def generar_reporte(cls,tipo,receive_data=None,secc=None):
        from Consult_Manager import Consult_Manager
        pnl=cls.vent.panelActual
        Consult_Manager.generar_reporte(pnl,tipo,cls.user,receive_data,secc)
    
    #Return to the old Panel    
    @classmethod		 
    def volver(cls):
        pnl=cls.vent.panelActual
        pantalla=cls.vent.panelActual_str
        if(pantalla==constantes.PANTALLA_UPDATE_ESTUDIANTE):
              cls.user.reset_data_process(0)
              cls.vent.update_pantallas(constantes.PANTALLA_WELCOME)
        
        elif(pantalla==constantes.PANTALLA_RECUPERAR_PASSWORD):
           cls.vent.update_pantallas(constantes.PANTALLA_INICIO)
        elif(pantalla==constantes.PANTALLA_DESCARGAR_FORMATOS or pantalla==constantes.PANTALLA_DESCARGAR_CARNETS or pantalla==constantes.PANTALLA_DESCARGAR_CONSTANCIAS):
           cls.vent.update_pantallas(constantes.PANTALLA_INICIO)
        elif(pantalla==constantes.PANTALLA_REGISTRO_USUARIO):
             cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_GESTION_USUARIO)
        elif(pantalla==constantes.PANTALLA_AYUDA_INFORMACION):
              cls.vent.update_pantallas(constantes.PANTALLA_WELCOME)
        else:
          if(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION):
               cls.user.reset_data_process(0)
               cls.vent.update_pantallas(constantes.PANTALLA_WELCOME)
          elif(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_2 or pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_3):
               cls.user.reset_data_process(0)
               cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION)
          elif(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_4):
               temp_dat=cls.user.get_data_process()
               cls.user.reset_data_process(1)
               ci=temp_dat[0][0]
               if(temp_dat[0][2]=="True"):
                 cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_2)
                 if(temp_dat[0][1]!="True"):
                   cls.set_data_estud(ci,False,"",temp_dat)   
                 else:
                  cls.set_data_estud(ci,False,"",temp_dat)   
               else:
                 cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_3)      
                 cls.set_data_estud(ci,True)   
          elif(pantalla==constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF):
                cls.vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA)
                temp_data=cls.user.get_data_process()
                cls.user.reset_data_process(0)
                pnl=cls.vent.panelActual
                secciones=pnl.get_comp_byName("secciones_p1")
                secciones.set_value(temp_data[0][3])
                secciones.On_select(None)
          elif(pantalla==constantes.PANTALLA_RENDIMIENTO_MAT_PEND):
                cls.vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND)
                temp_data=cls.user.get_data_process()
                cls.user.reset_data_process(0)
                pnl=cls.vent.panelActual
                secciones=pnl.get_comp_byName("secciones")
                secciones.set_value(temp_data[0][2])
                secciones.On_select(None)
          elif(pantalla==constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND or pantalla==constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA):
               cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_RENDIMIENTO)
               cls.user.reset_data_process(0)    
          elif(pantalla==constantes.PANTALLA_RENDIMIENTO_SABANA_NOTAS or pantalla==constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF_FINALES):
               cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_RENDIMIENTO)
               cls.user.reset_data_process(0)               
          elif(pantalla==constantes.PANTALLA_PLANIF_FORMATO1):
                cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_PLANIFICACION)
                cls.user.reset_data_process(0) 
          elif(pantalla==constantes.PANTALLA_PLANIF_FORMATO2 ):
                cls.vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO1)
                cls.user.reset_data_process(0)                  
          elif(pantalla>=constantes.PANTALLA_PLANIFIC_CRONOG2 and pantalla<=constantes.PANTALLA_PLANIFIC_CRONOG6):
              cls.vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1)                         
              cls.planificar_cronog(pantalla)
          elif(pantalla==constantes.PANTALLA_PLANIFIC_CRONOG1):
              cls.user.reset_data_process(0)
              cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_PLANIFICACION)                         
          elif(pantalla!=constantes.PANTALLA_PROCESO_INSCRIPCION and pantalla!=constantes.PANTALLA_PROCESO_PLANIFICACION and pantalla!=constantes.PANTALLA_PROCESO_RENDIMIENTO):
             next_p=-1
             cls.user.reset_data_process(0)
             next_p=constantes.PANTALLA_WELCOME
             cls.vent.update_pantallas(next_p)
             cls.show_data_user()
          else:
              cls.user.reset_data_process(0)
              cls.vent.update_pantallas(constantes.PANTALLA_WELCOME)
              cls.show_data_user()
    
    #The User Loggout           
    @classmethod		
    def logout(cls):       
         if(General.show_confirmDialog("cerrar session?","cerrar session")!=True):
            return       
         userActive_id=""
         cls.vent.update_pantallas(constantes.PANTALLA_INICIO)
         cls.user=usuario()
         mat_permiso=cls.user.get_permiso_matrix()
         menus=cls.vent.get_menu()
         for i in range(0,len(mat_permiso)):
              st=0
              if(mat_permiso[i][0]==True):
                 st=tk.NORMAL
              else:
                 st=tk.DISABLED
              menus[0].entryconfig(i+1,state=st)
              for j in range(1,len(mat_permiso[i])):
                 st_m=0
                 if(mat_permiso[i][j]==True):
                    st_m=tk.NORMAL
                 else:
                    st_m=tk.DISABLED  
                 menus[i+1].entryconfig((j-1),state=st_m)
         cls.vent.raiz.config(menu="")
     
    #Activate Components of Donwload Document Panel 
    @classmethod	     
    def activar_download(cls,opcion):
        pantalla=cls.vent.panelActual_str
        if(opcion==0):
           cls.vent.update_pantallas(constantes.PANTALLA_DESCARGAR_FORMATOS)
           pnl=cls.vent.panelActual
           comp=pnl.get_comp_byName("formatos")
           conexion_bd.set_tabla(constantes.TABLA_FORMATO)
           lista_temp=conexion_bd.get_allData(None,None)
           exclusiones=["disp horario","info estudiante","info trabajador","materia pendiente","sabana de notas","notas finales","notas finales del año","notas del momento","constancia de estudio","constancia de trabajo","constancia de prestacion de servicios","carnet","inscripcion","cronograma","reporte de usuarios","reporte de descargas","lista de trabajadores"]
           forms=["elegir"]
           for i in range(0,len(lista_temp)):
              id_form=lista_temp[i][0]
              valido=0
              for j in range(0,len(exclusiones)):
                  if(id_form==exclusiones[j] and valido==0):
                      valido=-1
              if(valido==0):
                 forms.append(id_form)
           comp.set_values(forms)
        elif(opcion==1):
           cls.vent.update_pantallas(constantes.PANTALLA_DESCARGAR_CARNETS)
        elif(opcion==2):
           cls.vent.update_pantallas(constantes.PANTALLA_DESCARGAR_CONSTANCIAS)
         
    #Load Login Panel 
    @classmethod		
    def load_login(cls):   
        pantalla=cls.vent.panelActual_str
        cls.vent.update_pantallas(constantes.PANTALLA_INICIO)
        
    #Load Init Panel
    @classmethod		
    def load_inicio(cls): 
        pantalla=cls.vent.panelActual_str
        cls.vent.update_pantallas(constantes.PANTALLA_INICIO)

    #Close teh System and Destroy the Windows
    @classmethod		
    def exit_application(cls):
       if(General.show_confirmDialog("Esta Seguro que Desea Salir?","Salir")!=True):
             return 
       cls.vent.close()
      
    #Update Student data from Service Panel 
    @classmethod	   
    def update_estudiante(cls):
        from Service_Manager import Service_Manager
        Service_Manager.update_estudiante(cls.user,cls.vent)
        
    #The User Request Modify the Information of Self Account     
    @classmethod 
    def update_user(cls):        
        from Service_Manager import Service_Manager
        Service_Manager.update_user(cls.user,cls.vent)
    
    #Load the Data of a Student and Set it on the Required Components    
    @classmethod 
    def load_data_estudiante(cls,id_e): 
       pnl=cls.vent.panelActual
       fields=pnl.get_comps_byTag("field") 
       combos=pnl.get_comps_byTag("combo")   
       if(id_e!=""):           
            estud=estudiante()           
            dat=estud.get_data_estud(id_e,"")          
            if(dat!=[]):
              if(len(dat)==3 or len(dat)==2):
                data_estud=dat[0]
                data_repres=[]
                data_exp=[]
                dire=""                
                if(len(dat)==3):                   
                   data_repres=dat[1]
                   data_exp=dat[2][0]
                else:
                   data_exp=dat[1][0]                   
                   conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                   data_repres=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[data_estud[8]],["and"])[0]
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                data_dire=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[data_estud[11]],["and"])[0]
                dire=data_dire[1]+","+data_dire[2]+","+data_dire[3]
                conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_ESTUD,len(constantes.CAMPOS_ESTATUS_ESTUD),[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[5]],["AND"])[0]
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                nombr_r=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_repres[1]],["and"])
                fields=pnl.get_comps_byTag("field")
                for i in range(0,len(fields)):                    
                    if(fields[i].get_id()=="cedula_estud"):
                         fields[i].set_text(data_estud[0])
                    elif(fields[i].get_id()=="nombre"):                         
                          if(data_estud[2]!=""):
                             fields[i].set_text(data_estud[1]+" "+data_estud[2])
                          else:
                             fields[i].set_text(data_estud[1])                             
                    elif(fields[i].get_id()=="apellido"):
                          if(data_estud[4]!=""):
                             fields[i].set_text(data_estud[3]+" "+data_estud[4])
                          else:
                             fields[i].set_text(data_estud[3])                             
                    elif(fields[i].get_id()=="CIrepres"):
                          fields[i].set_text(data_repres[0])
                          if(data_estatus[3]=="False"):
                              fields[i].set_state("readonly")
                          else:
                              fields[i].set_state("normal")                                                     
                    elif(fields[i].get_id()=="telef"):
                          fields[i].set_text(data_repres[2])                             
                    elif(fields[i].get_id()=="nombre_repres"):
                          temp_n=nombr_r[0][0]
                          if(nombr_r[0][1]!="" and nombr_r[0][1]!="..."):
                             temp_n=temp_n+" "+nombr_r[0][1]
                          fields[i].set_text(temp_n)                          
                    elif(fields[i].get_id()=="apellido_repres"):
                          temp_a=nombr_r[0][2]
                          if(nombr_r[0][3]!="" and nombr_r[0][3]!="..."):
                             temp_a=temp_a+" "+nombr_r[0][3]
                          fields[i].set_text( temp_a)                                                 
                    elif(fields[i].get_id()=="destino_file"):
                          if(data_exp[1]!="" and data_exp[1]!="..."):
                             fields[i].set_text(data_exp[1])
                          else:
                            fields[i].set_text("")
                    elif(fields[i].get_id()=="destino_foto"):
                          if(data_exp[2]!="" and data_exp[2]!="..."):
                             fields[i].set_text(data_exp[2])
                          else:
                            fields[i].set_text("")
                    elif(fields[i].get_id()=="fecha"):
                        fields[i].set_text(data_estud[10])
                    elif(fields[i].get_id()=="direccion"):
                         fields[i].set_text(dire)
                    elif(fields[i].get_id()=="estatus"):
                         fields[i].set_text(data_estatus[1])
                    elif(fields[i].get_id()=="correo"):
                         fields[i].set_text(data_repres[3])                      
                    elif(fields[i].get_id()=="dir_representante"):                        
                         dire_r=data_repres[5]
                         conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                         temp_dire_r=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[ dire_r],["and"])[0]
                         direccion_r=temp_dire_r[1]+","+temp_dire_r[2]+","+temp_dire_r[3]
                         fields[i].set_text(direccion_r)
                    elif(fields[i].get_id()=="parentesco"):
                         fields[i].set_text(data_estud[12])
                    elif(fields[i].get_id()=="ocupacion"):
                         fields[i].set_text(data_repres[4])                      
                combos=pnl.get_comps_byTag("combo")
                for j in range(0,len(combos)):
                    id_c=combos[j].get_id()
                    if(id_c=="salud"):
                           combos[j].set_value(data_estatus[2]) 
                    elif(id_c=="estatus2"):
                           combos[j].set_value("elegir")                    
                radio= pnl.get_comp_byName("genero") 
                radio.set_value(data_estud[9])                 
                cedulado=data_estatus[3].lower()
                if(cedulado=="false" or  cedulado=="no"):
                   pnl.get_comp_byName("cedulado_label").set_active(True)
                   pnl.get_comp_byName("cedulado").set_active(True)
                   pnl.get_comp_byName("nacionalidad").set_active(True)
                else:
                  pnl.get_comp_byName("cedulado_label").set_active(False)
                  pnl.get_comp_byName("cedulado").set_active(False)
                  pnl.get_comp_byName("nacionalidad").set_active(False)          
       else:       
         for i in range(0,len(fields)):
           fields[i].set_text("")
         for j in range(0,len(combos)):
           id_c=combos[j].get_id()
           if(id_c!="estudiantes"):
             combos[j].set_selected_index(0)
         pnl.get_comp_byName("cedulado_label").set_active(False)             
         pnl.get_comp_byName("cedulado").set_active(False)
         pnl.get_comp_byName("nacionalidad").set_active(False)
    
    #Load the Data of a Worker and set It on the Required Components    
    @classmethod		   
    def load_data_trabajador(cls,id_t):
        pnl=cls.vent.panelActual
        fields=pnl.get_comps_byTag("field")               
        if(id_t!=""):
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[id_t],["and"])
           conexion_bd.set_tabla(constantes.TABLA_CARGO)
           data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[data_trabaj[0][6]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           data_exp=conexion_bd.get_allData(constantes.CAMPOS_EXPEDIENTE,len(constantes.CAMPOS_EXPEDIENTE),[constantes.CLAVE_EXPEDIENTE],[data_trabaj[0][4]],["and"])
           docente=False
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           data_nombre=conexion_bd.get_allData(constantes.CAMPOS_NOMBRE,len(constantes.CAMPOS_NOMBRE),[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
           data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_TRABAJ,len(constantes.CAMPOS_ESTATUS_TRABAJ),[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][7]],["and"])           
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           if(conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,id_t)):
             docente=True             
           for i in range(0,len(fields)):
              id_f=fields[i].get_id()
              if(id_f=="cedula"):
                  fields[i].set_text(data_trabaj[0][0])
              elif(id_f=="nombre"):
                  nomb=data_nombre[0][1].capitalize()
                  if(data_nombre[0][2]!=""):
                     nomb=nomb+" "+data_nombre[0][2].capitalize()
                  fields[i].set_text(nomb)
              elif(id_f=="apellido"):
                  apell=data_nombre[0][3].capitalize()
                  if(data_nombre[0][4]!=""):
                     apell=apell+" "+data_nombre[0][4].capitalize()
                  fields[i].set_text(apell)
              elif(id_f=="service_years"):
                  fields[i].set_text(data_estatus[0][3])
              elif(id_f=="cargo_cod"):
                  fields[i].set_text(data_cargo[0][4])              
              elif(id_f=="destino_file"):
                 if(data_exp[0][1]!="" and data_exp[0][1]!="..." ):
                    fields[i].set_text(data_exp[0][1])
                 else:
                  fields[i].set_text("")
              elif(id_f=="destino_foto"):
                 if(data_exp[0][2]!="" and data_exp[0][2]!="..." ):
                    fields[i].set_text(data_exp[0][2])
                 else:
                  fields[i].set_text("")
              elif(id_f=="telefono"):
                 if(data_trabaj[0][3]!="" and data_trabaj[0][3]!="..."):
                     fields[i].set_text(data_trabaj[0][3])
                 else:
                   fields[i].set_text("")
              elif(id_f=="correo"):
                 if(data_trabaj[0][2]!="" and data_trabaj[0][2]!="..."):
                     fields[i].set_text(data_trabaj[0][2])
                 else:
                   fields[i].set_text("")
           combos=pnl.get_comps_byTag("combo")   
           radio=pnl.get_comp_byName("personal_tipo")
           radio2=pnl.get_comp_byName("nacionalidad")
           if(id_t.lower().startswith("v")):
              radio2.set_value("venezolano")
           elif(id_t.lower().startswith("e")):
              radio2.set_value("extranjero")
           else:
              radio2.set_value("venezolano")
           box_titulo=pnl.get_comp_byName("caja3_rp",False)
           box_docente=pnl.get_comp_byName("caja_areas",False)
           list_materias=pnl.get_comp_byName("lista_areas")
           values=[]
           have_director=False
           cargo_t=data_cargo[0][1]
           minist_t=data_cargo[0][2]
           if(docente==True):
               radio.set_value("docente")
               box_docente.set_active(True)
               box_titulo.set_active(True)
               pnl.get_comp_byName("field_delete").set_active(True)
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
               id_prof=conexion_bd.get_allData([constantes.CLAVE_PROFESOR],1,[constantes.CLAVE_TRABAJADOR],[id_t],["and"])[0][0]
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               data_areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],1,[constantes.CLAVE_PROFESOR],[id_prof],["and"])
               areas=[]
               if(data_areas!=[]):
                  for j in range(0,len(data_areas)):
                      areas.append(data_areas[j][0])
               list_materias.set_values(areas)
               
               values=["elegir","Docente","Docente de Aula",]
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               lista_trabaj=conexion_bd.get_allData([constantes.CLAVE_CARGO,constantes.CLAVE_TRABAJADOR],2)
               posibles=["Coordinador de Evaluacion","Coordinador de Orientacion","Sub Director Academico","Sub Director Administrativo"]
               conexion_bd.set_tabla(constantes.TABLA_CARGO)         
               for posibl in posibles:
                  valid_carg=True                
                  for worker in lista_trabaj:                                       
                       data_carg=conexion_bd.get_allData([constantes.CLAVE_CARGO,"cargo","cargo_ministerio"],3,[constantes.CLAVE_CARGO],[worker[0]],["and"])                     
                       if(data_carg==[]):
                           continue
                       if(id_t!=worker[1]):
                           if(data_carg[0][1].lower()==posibl.lower()):
                              valid_carg=False
                       else:                               
                           if(data_carg[0][1].lower()=="director" and have_director==False):
                               #tiene cargo de director
                               have_director=True
                               values.append(data_carg[0][1])                                                 
                  if(valid_carg==True):
                      values.append(posibl) 
           else:
              radio.set_value("no docente")
              box_docente.set_active(False)
              box_titulo.set_active(False)
              list_materias.set_values([])
              pnl.get_comp_byName("field_delete").set_active(True)
              values=["elegir","Obrero","Secretaria"]
           for i in range(0,len(combos)):
                id_comb=combos[i].get_id()
              
                if(id_comb!="empleado" and id_comb!="areas" and id_comb!="estatus"):              
                   if(docente==True):
                      if(id_comb!="cargo_minist"):              
                           combos[i].set_values(values)
                           if(have_director):
                                #Is the Director
                                combos[i].set_state("disabled")
                                radio.set_state("disabled")
                           else:
                               combos[i].set_state("normal")
                               radio.set_state("normal")
                           combos[i].set_value(cargo_t)                               
                      else:
                           combos[i].set_values(["elegir","Docente I","Docente II","Docente III","Docente IV","Docente V","Docente VI"])
                           
                           if(have_director):
                                #Is the Director
                                combos[i].set_state("disabled")
                           else:
                               combos[i].set_state("normal")
                           combos[i].set_value(minist_t)     
                   else:
                      #Not is a Teacher
                      if(id_comb!="cargo_minist"): 
                          combos[i].set_values(values)
                          combos[i].set_state("normal")
                          radio.set_state("normal")  
                          combos[i].set_value(cargo_t)  
                          
                      else:
                           combos[i].set_values(["elegir","Aseador I","Aseador II","Aseador III","Aseador IV","Bachiller I","Bachiller II","Bachiller III","Bachiller IV","TSU","Cocinera"])
                           combos[i].set_state("normal")
                           combos[i].set_value(minist_t)
                elif(id_comb=="estatus"):
                     combos[i].set_value(data_estatus[0][1])
           
           pnl.get_comp_byName("cedula").set_state("readonly")
           pnl.get_comp_byName("nacionalidad").set_state("disabled")                   
        else:
           pnl.get_comp_byName("cedula").set_state("normal")
           pnl.get_comp_byName("nacionalidad").set_state("normal")
           for i in range(0,len(fields)):
               fields[i].set_text("")
           radio=pnl.get_comp_byName("personal_tipo")
           radio.set_value("docente")
           radio2=pnl.get_comp_byName("nacionalidad")
           radio2.set_value("venezolano")
           combos=pnl.get_comps_byTag("combo")  
           for i in range(0,len(combos)):
                id_comb=combos[i].get_id()
                if(id_comb!="empleado" and id_comb!="areas" and id_comb!="estatus"):
                    if(id_comb!="cargo_minist"):
                       values=["elegir","Docente","Docente de Aula",]
                       conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                       lista_trabaj=conexion_bd.get_allData([constantes.CLAVE_CARGO],1)
                       posibles=["Coordinador de Evaluacion","Coordinador de Orientacion","Sub Director Academico","Sub Director Administrativo"]
                       conexion_bd.set_tabla(constantes.TABLA_CARGO)
                       for temp_cargo in posibles:
                          valid_carg=True                
                          for temp_trabaj in lista_trabaj:                     
                             data_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[temp_trabaj[0]],["and"])
                             if(data_cargo!=[]):          
                                 if(data_cargo[0][0].lower()==temp_cargo.lower()):
                                      valid_carg=False
                          if(valid_carg==True):
                               values.append(temp_cargo)    
                       combos[i].set_values(values)
                       combos[i].set_selected_index(0)
                       combos[i].set_state("readonly")
                       radio.set_state("normal")
                    else:                     
                       combos[i].set_values(["elegir","Docente I","Docente II","Docente III","Docente IV","Docente V","Docente VI"])
                       combos[i].set_selected_index(0)
                       combos[i].set_state("readonly")
    
    #Load the Data of TimeTables Disponibilty of Worker and Set it on the Required Components    
    @classmethod		   
    def load_data_disp(cls,id_t): 
       pnl=cls.vent.panelActual
       listas=pnl.get_comps_byTag("combo")
       turno=pnl.get_comp_byName("turno")
       temp_turno=""
       if(listas!=None):
          disponibilidad=[]          
          if(id_t!=""):             
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            data_disp=conexion_bd.get_allData(constantes.CAMPOS_DISP_HORARIO,len(constantes.CAMPOS_DISP_HORARIO),[constantes.CLAVE_TRABAJADOR],[id_t],["and"])
            if(data_disp!=[]):
               turno.set_value(data_disp[0][2])               
               temp_turno=data_disp[0][2]
               for i in range(3,len(data_disp[0])-1):
                    valor=data_disp[0][i]
                    if(valor=="no disponible"):
                       valor="no disponible-no disponible"
                    disponibilidad.append(valor)
          else:
             turno.set_value("mañana")
          mañana=["no disponible","7:30AM","8:15AM","9:00AM","9:45AM","10:30AM","11:15AM","12:00PM"]
          tarde=["no disponible","12:00PM","12:45PM","1:30PM","2:15PM","3:00PM","3:45PM","4:30PM","5:15PM"]
          for i in range(0,len(listas)):
             if(listas[i].get_id()!="lista_personal"):
               if(id_t==""):
                  listas[i].set_values(mañana)
                  listas[i].set_value("no disponible")
               else:
                  id_l=listas[i].get_id()                 
                  if(temp_turno=="mañana" or temp_turno==""):
                     listas[i].set_values(mañana)
                  else:
                     listas[i].set_values(tarde)                   
                  if(id_l.endswith("L")):
                     val=disponibilidad[0].split("-")
                     if(len(val)==2):
                         if(id_l.startswith("desde")):
                             listas[i].set_value(disponibilidad[0].split("-")[0])
                         else:
                             listas[i].set_value(disponibilidad[0].split("-")[1])
                     else:
                        listas[i].set_value("no disponible")                     
                  elif(id_l.endswith("M")):
                     val=disponibilidad[1].split("-")
                     if(len(val)==2):
                         if(id_l.startswith("desde")):
                            listas[i].set_value(val[0])
                         else:
                            listas[i].set_value(val[1])
                     else:
                        listas[i].set_value("no disponible")
                  elif(id_l.endswith("Mi")):
                     val=disponibilidad[2].split("-")
                     if(len(val)==2):
                         if(id_l.startswith("desde")):
                             listas[i].set_value(val[0])
                         else:
                             listas[i].set_value(val[1])
                     else:
                         listas[i].set_value("no disponible")
                  elif(id_l.endswith("J")):
                     val=disponibilidad[3].split("-")
                     if(len(val)==2):
                         if(id_l.startswith("desde")):
                             listas[i].set_value(val[0])
                         else:
                             listas[i].set_value(val[1])
                     else:
                         listas[i].set_value("no disponible")
                  elif(id_l.endswith("V")):
                     val=disponibilidad[4].split("-")
                     if(len(val)==2):
                         if(id_l.startswith("desde")):
                             listas[i].set_value(val[0])
                         else:
                             listas[i].set_value(val[1])
                     else:
                         listas[i].set_value("no disponible")
    
    #Set the value of the Secret Question in the required Text Field
    @classmethod		   
    def set_respuesta_secr(cls,name,val):
       pnl=cls.vent.panelActual
       comp=pnl.get_comp_byName(name)
       if(comp!=None):
           if(val!="."):
              comp.set_state("normal")
              comp.set_text(val)
           else:
              comp.set_state("readonly")
              comp.set_text("")
    
    #Change the Value of a Component 
    @classmethod		   
    def set_comp_values(cls,name,values):  
        #Name: the Tag or Id of Component    
        pnl=cls.vent.panelActual
        setting_index_combo=True        
        if(name.endswith("-")):
           #The Id have Indicative Character "-" :for Prevent set First Index in Combobox Component
           name=name.split("-")[0]
           setting_index_combo=False 
        if(name[0]!="*"): 
          #Single Element
          comp=pnl.get_comp_byName(name)
          if(type(comp).__name__=="Combo_box" or type(comp).__name__=="List_Box"):
              if(setting_index_combo==True):
                comp.set_values(values)
                if(type(comp).__name__=="Combo_box"):
                    comp.set_selected_index(0)
                comp. On_select(None)
              else:
                if(type(comp).__name__=="Combo_box"):
                   comp.set_value(values)
          elif(type(comp).__name__=="Labl"):
               comp.set_text(values)
          elif(type(comp).__name__=="TextField"):
               comp.set_text(values) 
          elif(type(comp).__name__=="tabla_celda"):
              if(type(values).__name__=="list"):
                 comp.asign_first_col(values)
              else:
                 comp.assign_selection(values)
          elif(type(comp).__name__=="Radio"):
              comp.set_value(values)
          elif(type(comp).__name__=="Check_Button"):
              comp.set_selected(values)     
        else:
           #Multiple Elements
           tag=""
           for i in range(1,len(name)):
               if(name[i]!="*"):
                 tag+=name[i]
           comps=pnl.get_comps_byTag(tag)
           for i in range(0,len(comps)):
              comps[i].set_values(values)
              comps[i].set_selected_index(0)
              comps[i]. On_select(None)
    
    
    #Register the User in User Gestion Panel
    @classmethod		
    def registrar_usuario(cls,update=False):
       from Service_Manager import Service_Manager
       Service_Manager.registrar_usuario(cls.user,cls.vent)
    

    #Register a Time Table for a Worker or  a Section           
    @classmethod
    def registrar_horario(cls,update=False):
        #se ejecuta al darle registrar a un horario
        from Register_Manager import Register_Manager
        Register_Manager.registrar_horario(cls.user,cls.vent,update)
        
    #Register or Update a Formation Area   
    @classmethod
    def registrar_area(cls,update=False): 
        from Register_Manager import Register_Manager
        Register_Manager.registar_area(cls.user,cls.vent,update)

    #Register or Update the Workers  
    @classmethod		
    def registrar_personal(cls,update=False):
       from Register_Manager import Register_Manager
       Register_Manager.registrar_trabajador(cls.user,cls.vent,update)
    
    #Register a Calification    
    @classmethod		
    def registrar_calificacion(cls):
       from Register_Manager import Register_Manager
       Register_Manager.registrar_calificacion(cls.user,cls.vent)
           
    #Register or update a Format           
    @classmethod		
    def registrar_formato(cls,update=False):
       from Register_Manager import Register_Manager
       Register_Manager.registrar_formato(cls.user,cls.vent,update)
               
    #Register or Update the Timetables of a Worker   
    @classmethod
    def registrar_dispHorario(cls,update=False):
        from Register_Manager import Register_Manager
        Register_Manager.registrar_dispHorario(cls.user,cls.vent,update)
     
    #Read the Expedent File and Assign the data Value to the Required TextFields     
    @classmethod
    def asign_expediente(cls,data=None):
       pnl=cls.vent.panelActual
       pantalla=cls.vent.panelActual_str
       cedula=""
       estudiante=False
       nuevo_ing=constantes.NUEVO_INGRESO_FIRST_YEAR
       
       if(data!=None):          
          cedula=data[0]
          num_files=data[1]
          file_sources=data[2]
          foto=data[3]         
          zip_path=constantes.FOLDER_DOCUMENTS+"expediente-"+cedula+".zip"
          try:
              if(os.path.exists(zip_path)):
                   os.remove(zip_path)
          except:
              print("zip ocupado")
                
          if sys.version_info >= (3, 7):
               import zipfile
          else:
              import zipfile37 as zipfile          
          zip_info=["","","","","","","","",""]
          for j in range(0,len(file_sources)):
              if(file_sources[j]!=None):                  
                  source_split=None
                  if(file_sources[j].startswith("C:/")):
                     source_split= file_sources[j].split("/")
                  else:
                     source_split= file_sources[j].split(os.sep)                  
                  source=""
                  if(len(source_split)>0):
                      source=source_split[len(source_split)-1]                      
                  if(pantalla==constantes.PANTALLA_REGISTRO_PERSONAL):
                     if(j==0):
                        zip_info[0]="fotocopia de la cedula:"+source
                     elif(j==1):
                        zip_info[1]="Fondo Negro:"+source
                     elif(j==2):
                        zip_info[2]="Fondo Blanco:"+source
                     elif(j==3):
                        zip_info[3]="Cuenta Bancaria:"+source
                     elif(j==4):
                        zip_info[4]="Hoja de Vida:"+source
                     elif(j==5):
                        zip_info[5]="Ultimo Baucher:"+source
                     elif(j==6):
                        zip_info[6]="Credenciales:"+source
                     elif(j==7):
                        zip_info[7]="foto:"+source                                 
                  else:
                     if(j==0):
                        zip_info[0]="fotocopia de la cedula:"+source
                     elif(j==1):
                        zip_info[1]="copia de la partida de nacimiento:"+source
                     elif(j==2):
                        zip_info[2]="Documento de Aprobacion de sexto grado:"+source
                     elif(j==3):
                        zip_info[3]="calificaciones certificadas de Años cursados:"+source
                     elif(j==4):
                        zip_info[4]="Carta de Residencia:"+source
                     elif(j==5):
                        zip_info[5]="Tarjeta de Vacunacion:"+source
                     elif(j==6):
                        zip_info[6]="fotocopia de la cedula del representante:"+source
                     elif(j==7):
                        zip_info[7]="foto del representante:"+source
                     elif(j==8):
                        zip_info[8]="foto:"+source
                                       
          info_file=open(constantes.FOLDER_DOCUMENTS+"info.txt","w")
          for inf in zip_info:
              if(inf!=""):
                  info_file.write(inf+"\n")
          info_file.close()         
          num_files=num_files+1
          file_sources.append(constantes.FOLDER_DOCUMENTS+"info.txt")
          Zip=zipfile.ZipFile(zip_path, "w",compression=zipfile.ZIP_DEFLATED ) 
          for i in range(0,len(file_sources)):
                 if(file_sources[i]!=None):
                     Zip.write(file_sources[i],arcname=os.path.basename(file_sources[i]))
          Zip.close()
          import threading
          hilo=threading.Thread(target=cls.reset_zip_files)
          hilo.start()                   
          pnl.get_comp_byName("destino_file").set_text(zip_path)
          if(foto!=""):
               if(foto.startswith(constantes.FOLDER_ZIP)==False):
                    pnl.get_comp_byName("destino_foto").set_text(foto)
          else:
               d_foto=pnl.get_comp_byName("destino_foto")
               if(d_foto.get_text().startswith("fotos/")==False):
                    pnl.get_comp_byName("destino_foto").set_text("")
        
          if(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_2):
                
                cls.user.data_expediente=data[4]                                     
       else:      
            if(pantalla==constantes.PANTALLA_REGISTRO_PERSONAL):
              cedula=pnl.get_comp_byName("cedula").get_text()
              if(cedula=="" or cedula==" "):
                 General.show_message("por favor indique la cedula del trabajador","cedula no indicada")
                 return              
            else:               
               estudiante=True
               cedula=pnl.get_comp_byName("cedula_estud").get_text()               
               if(pantalla==constantes.PANTALLA_PROCESO_INSCRIPCION_2):
                   y_i=pnl.get_comp_byName("curso").get_selected_value()
                   if(y_i.startswith("1")==False):
                      nuevo_ing=constantes.NUEVO_INGRESO_NO_FIRST_YEAR
               elif(pantalla==constantes.PANTALLA_UPDATE_ESTUDIANTE):
                     nuevo_ing=constantes.NUEVO_INGRESO_UPDATE
                      
               if(cedula=="" or cedula==" "):
                 General.show_message("por favor indique el estudiante","cedula de estudiante no indicada")
                 return
            sec=ventana_secundaria(cls.vent.raiz,[600,600],['#004AAD'],True,False,None,["#FFCE88","#060000","red","yellow","green","white"],"Arial",12,{"cedula":cedula,"Panel_Id":pantalla,"Is_Student":estudiante,"Nuevo_Ingreso":nuevo_ing})
    
    #Remove the Files of Zip Folder    
    @classmethod
    def reset_zip_files(cls): 
          if(os.path.exists(constantes.FOLDER_DOCUMENTS+"info.txt")):
               os.remove(constantes.FOLDER_DOCUMENTS+"info.txt")
          files_from_zip=os.listdir(constantes.FOLDER_ZIP)         
          for zp in files_from_zip:
              d_zp=os.path.join(constantes.FOLDER_ZIP,zp)
              os.remove(d_zp)
    
    #Clear the User Reports of System( Actions of User) 
    @classmethod          
    def clear_reportes(cls):    
       pass_admin=General.show_password_message("por favor escriba su password","password de administrado")
       valid_admin=False
       if(pass_admin=="" or pass_admin==None):
             return          
       if(pass_admin!=None and pass_admin!="" and pass_admin!=" "):
            p_user=General.desencriptar(cls.user.get_credentials()[4])
                   
            if(p_user==pass_admin):
                valid_admin=True                                          
       if(valid_admin==False):
            General.show_error("operacion invalida, por favor confirme que es el administrador","password invalido")
            return
       pnl=cls.vent.panelActual
       if(General.show_confirmDialog("esta seguro que desea limpiar los reportes del sistema?","limpiar reportes")!=True):
            return       
       conexion_bd.set_tabla(constantes.TABLA_REPORTE)
       conexion_bd.reset_table()
       pnl.get_comp_byName("table1_cp").reset()
       General.show_message("reportes del sistema limpiados satisfactoriamente","reportes limpiados")
       
    #download the User Manual   
    @classmethod
    def download_manual(cls):
        user_type=cls.user.get_credentials()[2]
        doc_name="manual_usuario_"+user_type+".pdf"
        url=constantes.SERVER+doc_name
        from Consult_Manager import Consult_Manager
        Consult_Manager.download_manual(url,doc_name)
        
        
        
