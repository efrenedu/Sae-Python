from documento import documento
from tiempo import tiempo
from conexion_bd import conexion_bd
from constantes import constantes
from General import General
import requests
import os
import sys


#Manage the Consult,Reports and downloads of System
class Consult_Manager:

   #Constants for Consults
   CONSULT_WORKERS=0
   CONSULT_STUDENTS=1
   CONSULT_TEACHERS=2
   CONSULT_SECTIONS=3
   CONSULT_ACADEMIC_MOMENTS=7
   CONSULT_TIMETABLES_DISPONIBILITY=8
   CONSULT_FORMATION_AREAS=9
   CONSULT_USERS_HISTORIAL=10
   CONSULT_FORMATION_AREAS_TEACHERS=11
   CONSULT_MATERIA_PENDIENTE=12
   CONSULT_DOWNLOADS=13
   DOCUMENT_EXPEDENT_STUDENT=0
   DOCUMENT_EXPEDENT_WORKER=1
   DOCUMENT_TIMETABLES_WORKER=2
   DOCUMENT_TIMETABLES_SECTION=3
   offset_consult=0
   limit_consult=20
   actual_page=0
   limit_pages=1
   consult_limits_targets={
      "consultaPersonal":[constantes.TABLA_TRABAJADOR,constantes.CLAVE_TRABAJADOR],
      "consultaEstudiantes":[constantes.TABLA_ESTUDIANTE,constantes.CLAVE_ESTUDIANTE],
      "consultaProf":[],
      "consultaSecciones":[],
      "consulta_momentos":[],
      "consultaDisp":[],
      "consultaAreas":[],
      "consultaAreasDocente":[],
      "consultaMatPend":[],
      "consultar_descargas":[],
      "auditoria":[constantes.TABLA_REPORTE,constantes.CLAVE_USUARIO]
   }


   #set the Limit of Pages of Consult Panel
   @classmethod
   def get_limit_pages(cls,pnl_id,pnl):
      from conexion_bd import conexion_bd
      import math
      key_target=""
      table_target=""
      cls.actual_page=0
      if(pnl_id in cls.consult_limits_targets):
         dat=cls.consult_limits_targets[pnl_id]
         if(len(dat)<=0):
            cls.limit_pages=1
            return
         table_target=dat[0]
         key_target=dat[1]
      else:
         cls.limit_pages=1
         return
         
      conexion_bd.set_tabla(table_target)
      res=conexion_bd.get_allData([key_target])
      number_register=len(res)
      cls.limit_pages=int(math.ceil(float(number_register)/float(cls.limit_consult)))
      if(cls.limit_pages<1):
         cls.limit_pages=1
     
      
   #Change Page of Consults and Reports
   @classmethod
   def change_ConsultPage(cls,next_page):
     if(next_page==True):
        if(cls.actual_page+1<cls.limit_pages):
            cls.actual_page+=1
     else:
       if(cls.actual_page-1>=0):
          cls.actual_page-=1   
     cls.offset_consult=cls.actual_page*cls.limit_consult
     
     
   #Interprete the Action to execute for the Consult
   @classmethod
   def interprete_consult(cls,vent,usr,consult_type):
       pnl=vent.panelActual
       accion=pnl.get_comp_byName("Accion_consulta")
       accion_str=""
       if(accion!=None):
          accion_str=accion.get_selected_value()
       else:
          accion_str="Buscar"
       if(accion_str=="Buscar"):
          cls.consultar(vent,consult_type)
          return
          
       if(consult_type==cls.CONSULT_STUDENTS):
           if(accion_str.startswith("Ver")):
              cls.generar_reporte(pnl,"info estudiante",usr)
           elif(accion_str.startswith("Generar")):
               cls.generar_reporte(pnl,"notas del momento",usr)
           else:
              if(accion_str=="Descargar Constancia"):
                 cls.generar_reporte(pnl,"constancia de estudio",usr)
              elif(accion_str=="Descargar Carnet"):
                 cls.generar_reporte(pnl,"carnet",usr)
              elif(accion_str=="Descargar Expediente"):
                 cls.download_doc(pnl,cls.DOCUMENT_EXPEDENT_STUDENT)
       elif(consult_type==cls.CONSULT_WORKERS):
           if(accion_str.startswith("Ver")):
               cls.generar_reporte(pnl,"info trabajador",usr)
           elif(accion_str.startswith("Generar")):
               cls.generar_reporte(pnl,"lista de trabajadores",usr) 
           else:
               if(accion_str=="Descargar Constancia"):
                 cls.generar_reporte(pnl,"constancia de prestacion de servicios",usr)
               elif(accion_str=="Descargar Carnet"):
                 cls.generar_reporte(pnl,"carnet",usr)
               elif(accion_str=="Descargar Horario"):
                 cls.download_doc(pnl,cls.DOCUMENT_TIMETABLES_WORKER)
               elif(accion_str=="Descargar Expediente"):
                 cls.download_doc(pnl,cls.DOCUMENT_EXPEDENT_WORKER)          
       elif(consult_type==cls.CONSULT_SECTIONS):
           if(accion_str=="Descargar Horario"):
              cls.download_doc(pnl,cls.DOCUMENT_TIMETABLES_SECTION)
           elif(accion_str=="Descargar Lista de la Seccion"):
              cls.generar_reporte(pnl,"lista de la seccion",usr)
           elif(accion_str=="Descargar Lista de Asistencia"):
              cls.generar_reporte(pnl,"asistencia seccion",usr)
           elif(accion_str=="Descargar Lista de Evaluacion Continua"):
              cls.generar_reporte(pnl,"evaluacion continua",usr)
       elif(consult_type==cls.CONSULT_TIMETABLES_DISPONIBILITY):
           cls.generar_reporte(pnl,"disp horario",usr)
       elif(consult_type==cls.CONSULT_MATERIA_PENDIENTE):
           cls.generar_reporte(pnl,"materia pendiente",usr)
       elif(consult_type==cls.CONSULT_DOWNLOADS):
            cls.generar_reporte(pnl,"reporte de descargas",usr)
    
   #Consult the Expedent Data for Inscription Report
   @classmethod
   def Consult_expedent_Data(cls,id_student,result):
       index_photo=len(result)
       result.append(["FOTO","not found"]) 
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[id_student],"conditions_Verify":["="]}              
       join_data={}
       join_data["expediente"]={"query_field":["src_exp","src_foto"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"estudiante"},"Conditions_join":None}
       dat_expedent=conexion_bd.get_allData([],cond_data,join_data,True)
       if(len(dat_expedent)<=0):
          return result  
       
       if(dat_expedent[0]["src_foto"]!="" and dat_expedent[0]["src_foto"]!="..."):
          result[index_photo]=["FOTO:",constantes.SERVER+dat_expedent[0]["src_foto"]]            
       if( dat_expedent[0]["src_exp"].endswith(".zip")==False):
          return result
          
       url_exp=constantes.SERVER+dat_expedent[0]["src_exp"]
       response=requests.get(url_exp)   
       if(response.status_code>400):
           return result
       
       #Get Expedent Data from Zip of Server
       ruta_zip=constantes.FOLDER_ZIP+"temp_zip.zip"
       with open(ruta_zip,"wb") as f_temp:
          f_temp.write(response.content)
       if sys.version_info >= (3, 7):
          import zipfile
       else:
           import zipfile37 as zipfile
       dir_extraccion=constantes.FOLDER_ZIP
       Zip= zipfile.ZipFile(ruta_zip, 'r')
       Zip.extractall(dir_extraccion)
       Zip.close()
       expedent_files=[False,False,False,False,False,False,False,False,False]                                        
       info_z=open(dir_extraccion+"info.txt","r")
       for linea in info_z:
          linea_split=linea.split(":")
          if(linea.startswith("fotocopia de la cedula")):
              expedent_files[0]="copia de Cedula de Identidad"
          elif(linea.startswith("copia de la partida de nacimiento")):
              expedent_files[1]="Copia de Partida de Nacimiento Original"
              expedent_files[2]="partida de nacimiento Original"
          elif(linea.startswith("Documento de Aprobacion de sexto grado")):
             expedent_files[3]="Boleta del periodos escolar anterior de ser neceario"
          elif(linea.startswith("calificaciones certificadas de Años cursados")):
             expedent_files[4]="Notas Cerificadas"
          elif(linea.startswith("Carta de Residencia")):
             expedent_files[5]="Carta de Residencia"
          elif(linea.startswith("fotocopia de la cedula del representante")):
            expedent_files[6]="Copia de Cedula"
          elif(linea.startswith("foto del representante")):
             expedent_files[7]="2 Fotos"
          elif(linea.startswith("foto")):
             expedent_files[8]="2 fotos del estudiante"
       info_z.close()
       import threading
       hilo=threading.Thread(target=Event_manager.reset_zip_files)
       hilo.start()
       for ex in expedent_files:
          if(ex!=False):
              result.append([ex,"X"])
       return result
   
   #Generate a Report
   @classmethod
   def generar_reporte(cls,pnl,type_form,usr,receive_data=None,secc=None):
       time_object=tiempo()
       from event_manager import Event_manager 
       vent=Event_manager.vent 
       raiz=vent.raiz
       
       #get format Data
       conexion_bd.set_tabla(constantes.TABLA_FORMATO)
       cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[type_form],"conditions_Verify":["="]}                          
       data_formato=conexion_bd.get_allData(["src_form"],cond_data,None,True)
       if(len(data_formato)<=0):
           General.show_error(f"Error no hay Formato para el Reporte de {type_form} ","Formato No Registrado")
           return
       src=data_formato[0]["src_form"]
       if(src.endswith(".pdf")==True):
           General.show_message("Solo se puede Generar Reportes en formatos XLSX de Excel","Formato Invalido") 
           return
       url=constantes.SERVER+src
       response=requests.get(url)
       if(response.status_code>400):
           General.show_error("Error obteniendo data Formato","Error")
           return   
       data_form=response.content
       
       #Verifications Over Format Type       
       if(type_form=="asistencia seccion" or type_form=="evaluacion continua" or type_form=="lista de la seccion"):
           clave=""
           if(secc==None):
               clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           else:
              clave=secc
           
           if(clave==" "):
              General.show_message("por favor seleccione una seccion","seccion no valida")
              return
           
           conexion_bd.set_tabla(constantes.TABLA_SECCION)
           cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}              
           join_data={}
           join_data["horario"]={"query_field":["turno"],"share_fields":{"field":constantes.CLAVE_HORARIO,"table_reference":"seccion"},"Conditions_join":None} 
           dat_curso=conexion_bd.get_allData([],cond_data,join_data,True)
           if(len(dat_curso)<=0):
               General.show_error("Error Obteniendo Datos de la Seccion","Seccion Inexistente")
               return
           turno=dat_curso[0]["turno"]
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[clave],"conditions_Verify":["="]}                 
           join_data={}
           join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None}
           data_seccion=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data,join_data,True)
           if(len(data_seccion)<=0):
               General.show_message("seccion sin estudiantes registrados","seccion vacia o inexistente")
               return
           num_estud=len(data_seccion)
           data_estuds=[]
           for i in range(0,num_estud):
               ci=data_seccion[i][constantes.CLAVE_ESTUDIANTE]
               fullname=""
               search_fields=["nombre","s_nombre","apellido","s_apellido"]
               for j in range(0,len(search_fields)):
                   target_field=search_fields[j]
                   if(data_seccion[0][target_field]!="" and data_seccion[0][target_field]!=" "):
                       fullname+=data_seccion[0][target_field]+" "
               data_estuds.append([ci,fullname])     
           nomb_secc=clave
           data_replace=[]
           data_replace.append(["Seccion:",nomb_secc])
           data_replace.append(["Turno:",turno])
           data_replace.append(["Fecha:",time_object.get_fecha()])
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA])
           if(data_cronog!=[]):
               data_replace.append(["periodo escolar:",data_cronog[0][0]])                     
           filename=type_form+" "+clave+".xlsx"
           path=constantes.FOLDER_DOCUMENTS+filename
           msg_end=False
           documento.request(pnl.win,[path,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_estud,data_estuds,"Nº",2,data_replace,msg_end],True)    
       elif(type_form=="inscripcion"):
          replace=[]
          replace=cls.Consult_expedent_Data(receive_data["estudiante"]["CI_estudiante"],replace)          
          #Get the Name of Representant and Student plus the Direction of Student
          name_student=""
          name_representant=""
          targets_names=["nombre","s_nombre","apellido","s_apellido"]
          target_name_representant=["nombre","s_nombre","apellido","s_apellido"]
          names_list=[]
          representant_name_list=[]
          for target in targets_names:
              val=receive_data["estudiante"][target]
              if(val=="" or val=="..."):
                  continue
              names_list.append(val)
          for target in target_name_representant:
              val=receive_data["representante"][target]
              if(val=="" or val=="..."):
                  continue
              representant_name_list.append(val)
          name_student=" ".join(names_list)
          dir_list=[receive_data["estudiante"]["direccion"]["sector"],receive_data["estudiante"]["direccion"]["parroquia"],receive_data["estudiante"]["direccion"]["casa"]]
          dir_estud=",".join(dir_list)
          dir_list_representant=[receive_data["representante"]["direccion"]["sector"],receive_data["representante"]["direccion"]["parroquia"],receive_data["representante"]["direccion"]["casa"]]
          dir_representant=",".join(dir_list)
          
          name_representant=" ".join(representant_name_list)
          
          #Set Replace Values of Document
          replace.append(["Apellidos y Nombres:",name_student])
          replace.append(["Fecha de Nacimiento:",receive_data["estudiante"]["año_nacimiento"]])
          replace.append(["Domicilio:",dir_estud]) 
          replace.append(["Representante:",name_representant])
          id_representant=receive_data["representante"]["CI_representante"]
          if(id_representant.lower().startswith("v-")==False and id_representant.lower().startswith("e-")==False ):
              id_representant="V-"+id_representant
          replace.append(["CI:",id_representant])
          replace.append(["Telefono:",receive_data["representante"]["telefono"]])
          replace.append(["Domicilio del Representante:",dir_representant])
          replace.append(["Correo del Representante:",receive_data["representante"]["correo"]])
          edad=str(time_object.get_edad(receive_data["estudiante"]["año_nacimiento"]))
          replace.append(["Parentesco:",receive_data["estudiante"]["parentesco"]])
          replace.append(["Oficio:",receive_data["representante"]["oficio"]])
          replace.append(["Cedula:",receive_data["estudiante"]["CI_estudiante"]])
          replace.append(["Plantel de Procedencia:",receive_data["estudiante"]["plantel"]])
          replace.append(["NN",""])
          replace.append(["Edad:",edad])
          replace.append(["Yo:",name_representant])
          replace.append(["de:",name_student])
          fech=time_object.get_fecha()
          fech=list(fech.split("/"))
          fech[1]=time_object.get_mes(int(fech[1]))
          replace.append(["Inscripcion Realizada a los:",fech[0]+" dias "+"del mes de "+fech[1]+" del Año "+fech[2]])
          secc=receive_data["seccion"]["data"]["id_secc"]
         
          #Filename of Report
          num_replace=len(replace)
          filename=f"Inscripcion-{receive_data['estudiante']['CI_estudiante']}.xlsx"
          path=constantes.FOLDER_DOCUMENTS+filename
          data_cells=[]
          year_inscription=int(receive_data["estudiante"]["year_estud"])
          conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
          data_cronog=conexion_bd.get_allData([])
          periodo=""
          if(data_cronog!=[]):
              periodo=data_cronog[0][0]
          
          for j in range(0,5):
             temp_data=["",str(j+1)+"º","","","",""]
             if((j+1)==year_inscription):
                temp_data[0]=periodo
                temp_data[2]=secc
                areas=""
                pends=""
                con_pendientes=False
                if(receive_data["materia_pendiente"]["Required"]!="False"):
                    con_pendientes=True 
                    list_areas=receive_data["materia_pendiente"]["List"]                    
                    for pd in range(0,len(list_areas)):
                        pends=pends+list_areas[pd][0].lower()+","
                if(receive_data["areas_repitiendo"]["Required"]!="False"):
                    list_areas=receive_data["areas_repitiendo"]["List"]
                    for rept in range(0,len(list_areas)):
                        areas=areas+list_areas[rept].lower()+","
                temp_data[4]=pends
                temp_data[3]=areas                        
             data_cells.append(temp_data)
          #Generate Report
          documento.request(raiz,[path,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[len(data_cells),data_cells,"NN",6,replace,False],True)
       elif(type_form=="info estudiante"):
           clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           if(clave==" "):
              General.show_message("por favor seleccione un estudiante","estudiante no valido")
              return
           
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[str(clave)],"conditions_Verify":["="]}                
           join_data={}
           join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None} 
           join_data["estatus_estud"]={"query_field":["estatus","cedulado","salud","last_year","fecha_inscrip","fecha_ingreso","plantel_procedencia"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":None} 
           join_data["direccion"]={"query_field":["sector","parroquia","casa"],"share_fields":{"field":constantes.CLAVE_DIRECCION,"table_reference":"estudiante"},"Conditions_join":None} 
           join_data["expediente"]={"query_field":["src_foto"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"estudiante"},"Conditions_join":None} 
          
           data_student=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,"genero","nacimiento","parentesco",constantes.CLAVE_SECCION,constantes.CLAVE_REPRESENTANTE],cond_data,join_data,True)
           if(len(data_student)<=0):
                General.show_message("Datos del Estudiante no Encontrados","Estudiante Inexistente")
                return
           num_estud=0
           data_modif=[]
           targets_names=["nombre","s_nombre"]
           targets_apellidos=["apellido","s_apellido"]
           name_values_list=[]
           apellidos_values_list=[]
           for target in targets_names:
             if(data_student[0][target]=="" or data_student[0][target]==" "):
                 continue
             name_values_list.append(data_student[0][target])
           for target in targets_apellidos:
             if(data_student[0][target]=="" or data_student[0][target]==" "):
                 continue
             apellidos_values_list.append(data_student[0][target])
           name_student=" ".join(name_values_list)
           apellido_student=" ".join(apellidos_values_list)
           
           data_modif.append(["NOMBRES:",name_student])
           data_modif.append(["APELLIDOS:",apellido_student])
           data_modif.append(["CEDULA:",data_student[0][constantes.CLAVE_ESTUDIANTE]])
           data_modif.append(["GENERO:",data_student[0]["genero"]])
           data_modif.append(["NACIMIENTO:",data_student[0]["nacimiento"]])
           valor_ced="Si"
           if(data_student[0]["cedulado"]=="False"):
                valor_ced="No"          
           data_modif.append(["CEDULADO:",valor_ced])
           status=data_student[0]["estatus"]
           if(status=="irregular"):
               status="activo"
           data_modif.append(["ESTATUS:",status])
           data_modif.append(["ESTADO SALUD:",data_student[0]["salud"]])
           data_modif.append(["AÑO DE CURSO:",data_student[0]["last_year"]])
           data_modif.append(["FECHA DE INGRESO:",data_student[0]["fecha_ingreso"]])
           data_modif.append(["ULTIMA INSCRIPCION:",data_student[0]["fecha_inscrip"]])
           data_modif.append(["PLANTEL DE PROCEDENCIA:",data_student[0]["plantel_procedencia"]])
           secc=data_student[0][constantes.CLAVE_SECCION]
           if(secc.lower()=="default"):
              secc=""
           
           data_modif.append(["SECCION:",secc])
           conexion_bd.set_tabla(constantes.TABLA_SECCION)
           cond_data={"conditions_Names":[constantes.CLAVE_SECCION,constantes.CLAVE_SECCION],"condition_Types":["and","and"],"conditions_Values":[secc,"default"],"conditions_Verify":["=","!="]}                 
           join_data={}
           join_data["horario"]={"query_field":["turno"],"share_fields":{"field":constantes.CLAVE_HORARIO,"table_reference":"seccion"},"Conditions_join":None} 
          
           data_secc=conexion_bd.get_allData([],cond_data,join_data,True)
           
           if(len(data_secc)>0):
              data_modif.append(["TURNO:",data_secc[0]["turno"]])
           else:
             data_modif.append(["TURNO:",""])
                
           conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
           cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[data_student[0][constantes.CLAVE_ESTUDIANTE]],"conditions_Verify":["="]}              
           data_pendiente=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],cond_data)
           data_modif.append(["MATERIAS PENDIENTE:",str(len(data_pendiente))+" materias"])
           
           id_representant=data_student[0][constantes.CLAVE_REPRESENTANTE]
           if(id_representant.lower().startswith("v-")==False and id_representant.lower().startswith("e-")==False):
                id_representant="V-"+id_representant        
           data_modif.append(["CEDULA_R:",id_representant])
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[data_student[0][constantes.CLAVE_REPRESENTANTE]],"conditions_Verify":["="]}              
           join_data={}
           join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"representante"},"Conditions_join":None} 
           join_data["direccion"]={"query_field":["sector","parroquia","casa"],"share_fields":{"field":constantes.CLAVE_DIRECCION,"table_reference":"representante"},"Conditions_join":None} 
           
           data_repres=conexion_bd.get_allData(["telef","correo","ocupacion"],cond_data,join_data,True)
           if(len(data_repres)<=0):
                General.show_error("error de datos del representante","representante invalido")
                return    
                
           representant_name=""
           representant_apellido=""
           representant_name_list=[]
           representant_apellido_list=[]
           for target in targets_names:
             if(data_repres[0][target]=="" or data_repres[0][target]==" "):
                 continue
             representant_name_list.append(data_repres[0][target])
           for target in targets_apellidos:
             if(data_repres[0][target]=="" or data_repres[0][target]==" "):
                 continue
             representant_apellido_list.append(data_repres[0][target])
           representant_name=" ".join(representant_name_list)
           representant_apellido=" ".join(representant_apellido_list)
           
           data_modif.append(["NOMBRE:",representant_name])
           data_modif.append(["APELLIDO:",representant_apellido])
           data_modif.append(["TELEFONO:",data_repres[0]["telef"]])
           data_modif.append(["CORREO:",data_repres[0]["correo"]])
           data_modif.append(["PARENTESCO:",data_student[0]["parentesco"]])
           data_modif.append(["OCUPACION:",data_repres[0]["ocupacion"]])
           
           
           targets_direccion=["sector","parroquia","casa"]
           direccion_representant=""
           direccion_student=""
           direccion_representant_list=[]
           direccion_student_list=[]
           for target in targets_direccion:
              direccion_representant_list.append(data_repres[0][target])
              direccion_student_list.append(data_student[0][target])
           direccion_student=",".join(direccion_student_list)
           direccion_representant=",".join(direccion_representant_list)
           data_modif.append(["DIRECCION REPRESENTANTE:",direccion_representant])
           data_modif.append(["DIRECCION:",direccion_student])
           if(data_student[0]["src_foto"]!="" and data_student[0]["src_foto"]!="..."):
                data_modif.append(["FOTO:",constantes.SERVER+data_student[0]["src_foto"]]) 
           else:
               data_modif.append(["FOTO:","not found"])
           
           data_modif.append(["Fecha:",time_object.get_fecha()])
           filename=f"Reporte_Estudiante_{str(clave)}.xlsx"
           path=constantes.FOLDER_DOCUMENTS+filename
           documento.request(raiz,[path,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"CEDULA:",0,data_modif,False],True)

       elif(type_form=="lista de trabajadores"):
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}                
            join_data={}
            cond_join={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":["inactivo"],"conditions_Verify":["!="]}                
            join_data["estatus_trabaj"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":cond_join} 
            join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
            join_data["cargo"]={"query_field":["cargo","codigo_cargo"],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None} 
           
            trabajs=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
            data_nomina=[]
            if(len(trabajs)<=0):
                General.show_message("no existen trabajadores registrados","Trabajadores Inexistentes")
                return
            target_fields=["nombre","s_nombre","apellido","s_apellido"]
            for tr in trabajs:
                name=""
                name_val_list=[]
                for target in target_fields:
                   if(tr[target]!="" and tr[target]!=" "):
                        name_val_list.append(tr[target])
                name=" ".join(name_val_list)
                data_row=[tr[constantes.CLAVE_TRABAJADOR],name,tr["cargo"],tr["codigo_cargo"]]
                data_nomina.append(data_row)
                
            num_rows=len(data_nomina)
            num_cols=0
            if(num_rows>0):
               num_cols=len(data_nomina[0])
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            filename=f"{type_form}_{time_object.get_fecha()}"
            filename=filename.replace("/","-")
            path=constantes.FOLDER_DOCUMENTS+filename+".xlsx"
            documento.request(raiz,[path,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,data_nomina,"Nº",num_cols,data_replace,False],True) 
       elif(type_form=="info trabajador"):
           clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           if(clave==" "):
             General.show_message("por favor seleccione un trabajador","trabajador no valido")
           
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[str(clave)],"conditions_Verify":["="]}              
           join_data={}
           join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
           join_data["estatus_trabaj"]={"query_field":["estatus","service_years","fecha_ingreso"],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":None} 
           join_data["cargo"]={"query_field":["cargo","cargo_ministerio","codigo_cargo"],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None} 
           join_data["expediente"]={"query_field":["src_foto"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"trabajador"},"Conditions_join":None} 
           join_data["horario"]={"query_field":["turno"],"share_fields":{"field":constantes.CLAVE_HORARIO,"table_reference":"trabajador"},"Conditions_join":None} 
                
           data_trabaj=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR,"correo","telefono"],cond_data,join_data,True)
           if(len(data_trabaj)<=0):
              General.show_message("Trabajador no Encontrado","trabajador inexistente") 
              return
           
           data_modif=[]
           name=""
           apellido=""
           temp_list=[]
           target_fields=["nombre","s_nombre"]
           for target in target_fields:
              val=data_trabaj[0][target]
              if(val=="" or val=="..."):
                  continue
              temp_list.append(val)
           name=" ".join(temp_list)
           temp_list=[]
           target_fields=["apellido","s_apellido"]
           for target in target_fields:
              val=data_trabaj[0][target]
              if(val=="" or val=="..."):
                  continue
              temp_list.append(val)
           apellido=" ".join(temp_list)
           
           
           data_modif.append(["NOMBRES:",name])
           data_modif.append(["APELLIDOS:",apellido])
           data_modif.append(["CEDULA:",data_trabaj[0][constantes.CLAVE_TRABAJADOR]])
           data_modif.append(["CORREO:",data_trabaj[0]["correo"]])
           data_modif.append(["TELEFONO:",data_trabaj[0]["telefono"]])  
                            
           cargo=data_trabaj[0]["cargo"].lower()
           if(cargo=="director"):
               cargo="DIRECTOR(A)"
           elif(cargo.startswith("coordinador")):
                if(cargo.endswith("evaluacion")):
                     cargo="COORDINADOR(A) DE EVALUACION"
                else:
                    cargo="COORDINADOR(A) DE ORIENTACION"
           elif(cargo.startswith("subdirector") or cargo.startswith("sub director")):
                if(cargo.endswith("academico")):
                     cargo="SUB DIRECTOR(A) ACADEMICO"
                else:
                    cargo="SUB DIRECTOR(A) ADMINISTRATIVO"               
           data_modif.append(["CODIGO CARGO:",data_trabaj[0]["codigo_cargo"]])
           data_modif.append(["CARGO:",cargo])
           data_modif.append(["CARGO MINIST:",data_trabaj[0]["cargo_ministerio"]])
           data_modif.append(["ESTATUS:",data_trabaj[0]["estatus"]])
           data_modif.append(["AÑOS DE SERVICIO:",data_trabaj[0]["service_years"]])
           data_modif.append(["FECHA DE INGRESO:",data_trabaj[0]["fecha_ingreso"]])
           data_modif.append(["TURNO:",data_trabaj[0]["turno"]])
           
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data_trabaj[0][constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
           join_data={}
           join_data["area_dictada_docentes"]={"query_field":[constantes.CLAVE_AREA_FORMACION],"share_fields":{"field":constantes.CLAVE_PROFESOR,"table_reference":"profesor"},"Conditions_join":None} 
           
           data_prof=conexion_bd.get_allData(["seccion_guia"],cond_data,join_data,True)
           if(len(data_prof)>0):
              data_modif.append(["DOCENTE:","Si"])
              data_modif.append(["SECCION GUIA:",data_prof[0]["seccion_guia"]])
              areas_profesor=""
              temp_list=[]
              for i in range(0,len(data_prof)):
                  temp_list.append(data_prof[i][constantes.CLAVE_AREA_FORMACION])
              areas_profesor=",".join(temp_list)
              data_modif.append(["AREAS DICTADAS:",areas_profesor])
           else:
              data_modif.append(["DOCENTE:","No"])
                     
           if(data_trabaj[0]["src_foto"]!="" and data_trabaj[0]["src_foto"]!="..."):
              data_modif.append(["FOTO:",constantes.SERVER+data_trabaj[0]["src_foto"]]) 
           else:
             data_modif.append(["FOTO:","not found"])  
           data_modif.append(["Fecha:",time_object.get_fecha()])
           filename=type_form+" "+str(clave)+".xlsx"
           ruta=constantes.FOLDER_DOCUMENTS+filename
           documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"CEDULA:",0,data_modif,False],True)

       elif(type_form=="disp horario"):
            
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}              
            disp_data=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR,"turno","disp_lunes","disp_martes","disp_miercoles","disp_jueves","disp_viernes"],cond_data,None,True)
            
            if(len(disp_data)<=0):
                General.show_message("no hay disponibilidad de horarios registradas","disponibilidad de horarios inexistentes")
                return
            data_nomina=[]
            num_trabaj=0
            tagets_fields_name=["nombre","s_nombre","apellido","s_apellido"]
            target_fields=["disp_lunes","disp_martes","disp_miercoles","disp_jueves","disp_viernes"]
            for i in range(0,len(disp_data)):
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                join_data={}
                join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
                cond_join={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":["inactivo"],"conditions_Verify":["!="]}              
                join_data["estatus_trabaj"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":cond_join} 
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[disp_data[i][constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
                trabaj_data=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
                if(len(trabaj_data)<=0):
                   continue
                num_trabaj+=1   
                temp_list=[]
                for target in tagets_fields_name:
                   val=trabaj_data[0][target]
                   if(val=="" or val=="..."):
                       continue
                   temp_list.append(val)
                   
                name=" ".join(temp_list)
                temp_data=[disp_data[i][constantes.CLAVE_TRABAJADOR],name,disp_data[i]["turno"]]
                for target in target_fields:
                   val=disp_data[i][target]
                   if(val.lower()=="no disponible"):
                      val="NO DISP."
                   temp_data.append(val)
                data_nomina.append(temp_data)
                             
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA])
            if(data_cronog!=[]):
                data_replace.append(["periodo escolar:",data_cronog[0][0]])
            filename=type_form+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_trabaj,data_nomina,"Nº",8,data_replace,False],True)    
       elif(type_form=="materia pendiente"):
            
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)  
            mat_pend=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_MATERIA_PENDIENTE,"año"],None,None,True)
            if(len(mat_pend)<=0):
                General.show_message("no hay Materias Pendientes Registradas","Materias Pendientes inexistentes")            
                return
            data_nomina=[]
            num_materias=len(mat_pend)
            targets_names=["nombre","s_nombre","apellido","s_apellido"]
            for i in range(0,len(mat_pend)):
                conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                id_estud=mat_pend[i][constantes.CLAVE_ESTUDIANTE]
                name=""
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[id_estud],"conditions_Verify":["="]}              
                join_data={}
                join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None} 
                data_estud=conexion_bd.get_allData([],cond_data,join_data,True)
                if(len(data_estud)<=0):
                   continue
                temp_list=[]
                for target in targets_names:
                   val=data_estud[0][target]
                   if(val=="" or val=="..."):
                       continue
                   temp_list.append(val)
                name=" ".join(temp_list)
                temp_list=[]                
                
                conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[mat_pend[i][constantes.CLAVE_MATERIA_PENDIENTE]],"conditions_Verify":["="]}              
                data_intentos=conexion_bd.get_allData(["intento","valor","fecha"],cond_data,None,True)
                identific_matPend=f"{mat_pend[i][constantes.CLAVE_AREA_FORMACION]}-{mat_pend[i]['año']}"
                data_row=[id_estud,name,identific_matPend,"ND","ND","ND","ND","ND","ND","ND","ND","ND","ND"]

                for dat in data_intentos:
                    id_intento=dat["intento"]
                    index_value=-1
                    index_date=-1
                    if(id_intento=="intento 1"):
                       index_value=3
                       index_date=4
                    elif(id_intento=="intento 2"):
                       index_value=5
                       index_date=6
                    elif(id_intento=="intento 3"):
                       index_value=7
                       index_date=8
                    elif(id_intento=="intento 4"):
                       index_value=9
                       index_date=10
                    elif(id_intento=="revision"):
                       index_value=11
                       index_date=12
                    if(index_value!=-1 and index_date!=-1):
                         data_row[index_value]=dat["valor"]
                         data_row[index_date]=dat["fecha"]
                data_nomina.append(data_row)                                
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA])
            if(data_cronog!=[]):
                data_replace.append(["periodo escolar:",data_cronog[0][0]])
            filename=type_form+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_materias,data_nomina,"Nº",13,data_replace,False],True)
       elif(type_form=="constancia de estudio" or type_form=="constancia de prestacion de servicios"):
              
              is_student=False
              is_out=False
              cedula=""
              #Get Target Id
              if(pnl.id_panel==constantes.PANTALLA_DESCARGAR_CONSTANCIAS):
                trab=pnl.get_comp_byName("trabajador").get_selected_value()
                is_out=True
                if(trab=="elejir" or trab=="elegir"):
                     General.show_message("por favor indique el trabajador ","trabajador invalido")
                     return
                cedula=trab.split("-")
                if(len(cedula)==3):
                   cedula=cedula[0]+"-"+cedula[1]
                elif(len(cedula)==2):
                   cedula=cedula[0]
                else:
                   cedula=""
              else:
                 tabl=pnl.get_comp_byTag("table")
                 dat_tabla=tabl.get_row_selectedData()
                 if(pnl.id_panel==constantes.PANTALLA_CONSULTA_ESTUDIANTES):
                    is_student=True
                    if(dat_tabla==" "):
                        General.show_message("Por favor indique el Estudiante","Estudiante Invalido")
                        return
                 else:
                    if(dat_tabla==" "):
                        General.show_message("Por favor indique el Trabajador","Trabajador Invalido")
                        return
                 cedula=str(dat_tabla[0])
                 if(dat_tabla[5]=="inactivo"):
                      General.show_message("Solo se puede Generar Constancias de Estudiantes/Trabajadores Activos","estudiasnte/trabajador Inactivo")
                      return  
                      
              #Get Director Data
              replace=[]
              nombre_directivo=""
              cedula_directivo=""
              temp_list=[]
              conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR) 
              cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}              
              join_data={}
              join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
              cond_join={"conditions_Names":["cargo"],"condition_Types":["and"],"conditions_Values":["director"],"conditions_Verify":["="]}              
              join_data["cargo"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":cond_join} 
                 
              data_director=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
              if(len(data_director)<=0):
                 General.show_error("No hay Director Registrado en el Sistema","Director Inexistente")
                 return
              target_names=["apellido","s_apellido","nombre","s_nombre"]
              
              for target in target_names:
                 val=data_director[0][target]
                 if(val=="" or val=="..."):
                    continue
                 temp_list.append(val)
              nombre_directivo=" ".join(temp_list)
              temp_list=[]
              cedula_directivo=data_director[0][constantes.CLAVE_TRABAJADOR]
              
              replace.append(["   Quien suscribe Prof(a),",nombre_directivo,12,"bold"])
              replace.append(["Directivo",nombre_directivo,12,"bold"])
              replace.append(["identidad ,",cedula_directivo,12,"bold"])
              replace.append(["CI dire",cedula_directivo,12,"bold"])                
              fech=time_object.get_fecha().split("/")
              dia=fech[0]
              mes=fech[1]
              mes=time_object.get_mes(int(mes))
              año=fech[2]     
              
              #Get Target Data
              if(is_student):
                   #Constancia for Students
                   conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)              
                   cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
                   join_data={}
                   join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None} 
                   cond_join={"conditions_Names":["estatus","estatus"],"condition_Types":["and","and"],"conditions_Values":["inactivo","graduado"],"conditions_Verify":["!=","!="]}                                
                   join_data["estatus_estud"]={"query_field":["last_year"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":cond_join} 
               
                   data_student=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data,join_data,True)
                   if(len(data_student)<=0):
                        General.show_message("Id del Estudiante no Registrada o Estudiante Inactivo","Estudiante Invalido")
                        return  
                   
                   for target in target_names:
                      val=data_student[0][target]
                      if(val=="" or val=="..."):
                         continue
                      temp_list.append(val)
                   name_student=" ".join(temp_list)
                   temp_list=[]
                   
                   replace.append(["el(la) estudiante :",name_student,12,"bold"])
                   año_escolar=""
                   conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA) 
                   data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],None,None,True)
                   if(len(data_cronog)<=0):
                       General.show_message("Aun no se ha Registrado un Cronograma","Cronograma no Registrado")
                       return
                   año_escolar=data_cronog[0][constantes.CLAVE_CRONOGRAMA]
                   replace.append(["del Año Escolar:",año_escolar,12,"bold"])
                   replace.append(["Año Escolar:",año_escolar,12,"bold"])
                   replace.append(["escolar:",cedula,12,"bold"])
                   curso_number=data_student[0]["last_year"]
                   available_cursos={"1":"Primer","2":"Segundo","3":"Tercer","4":"Cuarto","5":"Quinto"}
                   curso=available_cursos[curso_number]
                   replace.append(["cursa estudios en nuestra institucion en el:",curso+" Año ",12,"bold"])     
              else:
                   #for Workers
                   conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)              
                   cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
                   join_data={}
                   join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
                   cond_join={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":["inactivo"],"conditions_Verify":["!="]}              
                   join_data["estatus_trabaj"]={"query_field":["fecha_ingreso"],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":cond_join} 
                   join_data["cargo"]={"query_field":["cargo","cargo_ministerio","codigo_cargo"],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None} 
               
                   data_trabaj=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
                   if(len(data_trabaj)<=0):
                        General.show_message("Trabajador no Registrado o Inactivo","Trabajador Invalido")
                        return
                   for target in target_names:
                      val=data_trabaj[0][target]
                      if(val=="" or val=="..."):
                          continue
                      temp_list.append(val)
                   name_worker=" ".join(temp_list)
                   temp_list=[]
                   replace.append(["el(la) ciudadano(a) :",name_worker,12,"bold"])
                   temp_ingreso=data_trabaj[0]["fecha_ingreso"].split("/")
                   ingreso=""
                   for ing in range(0,len(temp_ingreso)):
                      valor_ingreso=temp_ingreso[ing]
                      if(len(valor_ingreso)<2):
                            valor_ingreso="0"+valor_ingreso
                      ingreso=ingreso+valor_ingreso
                      if(ing<2):
                         ingreso=ingreso+"/"
                         
                   replace.append(["desde el:",ingreso,12,"bold"])
                   cargo=data_trabaj[0]["cargo"].upper()
                   codigo_cargo=data_trabaj[0]["codigo_cargo"].upper()
                   cargo_minist=data_trabaj[0]["cargo_ministerio"].upper()
                   cargo_firstPart=cargo
                   cargo_SecondPart=""
                   if(cargo.lower().startswith("profesor") or cargo.lower().startswith("docente")):
                      cargo_firstPart="DOCENTE"
                      if(cargo.lower().endswith("aula")):
                          cargo_SecondPart=" AULA"
                   else:
                      if(cargo.lower()=="director"):
                         cargo_firstPart="DIRECTOR(A)"
                      elif(cargo.lower().startswith("sub director") or cargo.lower().startswith("subdirector")):
                          cargo_firstPart="SUB DIRECTOR(A)"
                          if(cargo.endswith("academico")):
                             cargo_SecondPart=" ACADEMICO"
                          else:
                            cargo_SecondPart=" ADMINISTRATIVO"
                      elif(cargo.lower().startswith("coordinador")):
                          cargo_firstPart="COORDINADOR(A)"
                          if(cargo_SecondPart.endswith("evaluacion")):
                             cargo_SecondPart=" DE EVALUACION"
                          else:
                             cargo_SecondPart=" DE ORIENTACION"    
                                
                       
                   
                   cargo=cargo_firstPart+cargo_SecondPart
                   replace.append(["se desempeña como:",cargo,12,"bold"])
                   replace.append(["code",codigo_cargo,12,"bold"])
                   replace.append([" de la CI:",cedula,12,"bold"])                        
                   if(is_out==True):
                      #Document Request is not from a User
                      conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                      data_descarga=[f"download_{data_trabaj[0][constantes.CLAVE_TRABAJADOR]}_{time_object.get_full_time_str()}", data_trabaj[0][constantes.CLAVE_TRABAJADOR],type_form,time_object.get_fecha(),time_object.get_tiempo(),"constancia",time_object.get_fecha()]
                      conexion_bd.add_data(data_descarga,True)
              #Generate Report
              new_date=dia+" de "+mes+" del "+año
              replace.append(["Aguas Calientes,",new_date,12,"bold"])
              replace.append(["a los",new_date,12,"bold"])
              ruta=constantes.FOLDER_DOCUMENTS+type_form+"-"+cedula+".xlsx"              
              ref_cell="Unused"
              documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],ref_cell,0,replace,False],True)         
       elif(type_form=="sabana de notas" or type_form=="notas finales del año"):
           if(receive_data==None):
               General.show_error("Error Generando data del Reporte","Error")           
               return
           
           info=receive_data[0]
           replace=[]
           for i in range(0,len(receive_data[1])):
                replace.append(["Area N"+str(i+1),receive_data[1][i]])
           replace.append(["Seccion:",receive_data[2]])
           replace.append(["Año:",receive_data[3]+" AÑO"])
           replace.append(["Fecha:",time_object.get_fecha()])
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA])
           if(data_cronog!=[]):
                replace.append(["periodo escolar:",data_cronog[0][0]])
           col_count=len(info[0])
           filename=type_form+" "+receive_data[2]+".xlsx"
           ruta=constantes.FOLDER_DOCUMENTS+filename            
           num_rows=len(info)              
           documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)
       elif(type_form=="notas finales"):
            from estudiante import estudiante
            estud=estudiante()
            field_ced=pnl.get_comp_byName("cedula_estudiante")
            nacionaliad_comp=pnl.get_comp_byName("nacionalidad")
            cedula_estud=""
            if(field_ced!=None and nacionaliad_comp!=None):
               nacionalidad_value=nacionaliad_comp.get_selected_value()
               if(nacionalidad_value.lower()=="venezolano"):
                   cedula_estud=f"V-{field_ced.get_text()}"
               else:
                   cedula_estud=f"E-{field_ced.get_text()}"
            res=estud.get_calif_certific(cedula_estud)
            if(res[0]==False):
                General.show_message(res[1],"Error")
                return
            replace=[]
            replace.append(["Estudiante:",res[1][1]])
            replace.append(["Fecha:",time_object.get_fecha()])
            replace.append(["Cedula:",res[1][0]])
            col_count=2
            num_rows=10
            offset_res=2
            data_send=[]
            for i in range(offset_res,len(res)):
                data_send.append(res[i])   
            if(len(data_send)<=0):
                General.show_error("sin datos para reporte","datos inexistentes")
                return
            filename="notas finales-"+res[1][0]+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_NOTAS_CERTIFICADAS,[num_rows,data_send,["1 AÑO","2 AÑO","3 AÑO","4 AÑO","5 AÑO"],col_count,replace,False],True)
       elif(type_form=="reporte de usuarios"):
           
            
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            data_reporte=conexion_bd.get_allData([constantes.CLAVE_USUARIO,"razon","fecha","hora","motivo"],None,None,True)
            info=[]
            for i in range(0,len(data_reporte)):
                data_row=[]
                data_row.append(data_reporte[i][constantes.CLAVE_USUARIO])
                data_row.append(data_reporte[i]["razon"])
                data_row.append(data_reporte[i]["fecha"])
                data_row.append(data_reporte[i]["hora"])
                data_row.append(data_reporte[i]["motivo"])
                info.append(data_row)
            replace=[]
            replace.append(["Fecha:",time_object.get_fecha()])
            col_count=0
            if(len(info)>0):
                col_count=len(info[0])
            fecha=time_object.get_fecha().split("/")
            new_fecha=fecha[0]+"-"+fecha[1]+"-"+fecha[2]
            filename="reporte de usuarios,"+new_fecha+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename  
            num_rows=len(info)              
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)
  
       elif(type_form=="reporte de descargas"):
            
            conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
            data_reporte=conexion_bd.get_allData([],None,None,True)
            info=[]
            targets_names=["nombre","s_nombre","apellido","s_apellido"]
            for i in range(0,len(data_reporte)):
                data_row=[]
                data_row.append(data_reporte[i][constantes.CLAVE_TRABAJADOR])
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data_reporte[i][constantes.CLAVE_TRABAJADOR]],"conditions_Verify":["="]}              
                join_data={}
                join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
                data_trabaj=conexion_bd.get_allData([constantes.CLAVE_NOMBRE],cond_data,join_data,True)
                name=""
                if(len(data_trabaj)<=0):
                    continue
                temp_list=[]
                for target in targets_names:
                  val=data_trabaj[0][target]
                  if(val=="" or val=="..."):
                     continue
                  temp_list.append(val)
                name=" ".join(temp_list)
                    
                data_row.append(name)       
                data_row.append(data_reporte[i][constantes.CLAVE_FORMATO])
                data_row.append(data_reporte[i]["fecha"])
                data_row.append(data_reporte[i]["hora"])
                info.append(data_row)
            replace=[]
            replace.append(["Fecha:",time_object.get_fecha()])
            col_count=0
            if(len(info)>0):
                   col_count=len(info[0])
            fecha=time_object.get_fecha().split("/")
            new_fecha=fecha[0]+"-"+fecha[1]+"-"+fecha[2]
            filename="reporte de usuarios,"+new_fecha+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename  
            num_rows=len(info)              
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)
   
       elif(type_form=="notas del momento"):
            
            cedula=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
            replace=[]
            if(cedula=="" or cedula==" "):
              General.show_message("Por favor Seleccione un Estudiante","Estudiante Invalido")
              return
              
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],None,None,True)
            if(len(data_cronog)<=0):
               General.show_message("No Existe un Cronograma Registrado","Cronograma Invalido")
               return              
            replace.append(["periodo escolar:",data_cronog[0][constantes.CLAVE_CRONOGRAMA]])
            
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)  
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
            join_data={}
            join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None} 
            join_data["seccion"]={"query_field":["año"],"share_fields":{"field":constantes.CLAVE_SECCION,"table_reference":"estudiante"},"Conditions_join":None} 
               
            data_student=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_SECCION],cond_data,join_data,True)
            if(len(data_student)<=0):
               General.show_message("Estudiante no Registrado","Estudiante Invalido")
               return
            fullname="" 
            year=data_student[0]["año"]
            targets_names=["nombre","s_nombre","apellido","s_apellido"]
            temp_list=[]
            for target in targets_names:
               val=data_student[0][target]
               if(val=="" or val=="..."):
                  continue
               temp_list.append(val)
            fullname=" ".join(temp_list)
             
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            cond_data={"conditions_Names":["abierto"],"condition_Types":["and"],"conditions_Values":["true"],"conditions_Verify":["="]}                
            data_moms=conexion_bd.get_allData([constantes.CLAVE_MOMENTO],cond_data,None,True) 
            momento=""
            if(len(data_moms)<=0):
                General.show_message("No Existe un Momento Academico Activo ","Momentos Academicos Cerrados")
                return
            momento=data_moms[0][constantes.CLAVE_MOMENTO]        
            areas=[]
            conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
            cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":["Si"],"conditions_Verify":["="]}              
            join_data={}
            cond_join={"conditions_Names":[f"{year}_año"],"condition_Types":["and"],"conditions_Values":["True"],"conditions_Verify":["="]}              
            join_data["años_incorporados"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":cond_join} 
           
            temp_areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],cond_data,join_data,True)
            for t_area in temp_areas:
                areas.append(t_area[constantes.CLAVE_AREA_FORMACION])
            orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","fsn","ov","gcrp"]     
            data_areas=[]
            for temp_orden in orden:
                for i in range(0,len(areas)):
                    if(areas[i].lower()== temp_orden):
                            data_areas.append(areas[i])
            info=[]   
            for dat_areas in data_areas:   
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[cedula,dat_areas,year],"conditions_Verify":["=","=","="]}              
                join_data={}
                cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[momento],"conditions_Verify":["="]}              
                join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM,"definitiva"],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join} 
                data_calif=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,join_data,True)
                if(len(data_calif)>0):
                   conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
                   cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[data_calif[0][constantes.CLAVE_CALIF_MOM]],"conditions_Verify":["="]}              
                   data_calific=conexion_bd.get_allData(["valor","numero"],cond_data,None,True)
                   new_data=[dat_areas]
                   for evaluation_index in range(0,constantes.MAXIMO_EVALUACIONES):
                       new_data.append("evaluacion "+str(evaluation_index+1)) 
                   offset_data=1        
                   for j in range(offset_data,len(new_data)):
                      old_val=new_data[j]
                      for register_calific in data_calific:
                          if(register_calific ["numero"]==new_data[j]):
                              new_data[j]=register_calific ["valor"]
                      if(old_val==new_data[j]):
                          new_data[j]=""
                   new_data.append(data_calif[0]["definitiva"])
                   info.append(new_data)
                     
                else:
                    new_data=[dat_areas]
                    for evaluation_index in range(0,constantes.MAXIMO_EVALUACIONES):
                        new_data.append("") 
                    new_data.append("01")
                    info.append(new_data)                    
            
            replace.append(["Nombres y apellidos:",fullname])
            replace.append(["Cedula:",cedula])
            replace.append(["Momento:",momento])
            replace.append(["Año:",year+" año"])
            replace.append(["Fecha:",time_object.get_fecha()])
            col_count=len(info[0])
            filename="reporte de calificaciones-"+momento+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename  
            num_rows=len(info)              
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)

       elif(type_form=="carnet"):
            is_estud=False
            is_out=False
            cedula=""
            if(pnl.id_panel==constantes.PANTALLA_DESCARGAR_CARNETS):
                trab=pnl.get_comp_byName("trabajador").get_selected_value()
                is_out=True
                if(trab=="elejir" or trab=="elegir"):
                    General.show_message("por favor indique el trabajador ","trabajador invalido")
                    return
                cedula=trab.split("-")
                if(len(cedula)==3):
                    cedula=cedula[0]+"-"+cedula[1]
                elif(len(cedula)==2):
                    cedula=cedula[0]
                else:
                    cedula=""
            else:
                tabl=pnl.get_comp_byTag("table")
                dat_tabla=tabl.get_row_selectedData() 
                if(pnl.id_panel==constantes.PANTALLA_CONSULTA_ESTUDIANTES):
                    is_estud=True
                    if(dat_tabla==" "):
                       General.show_message("Por Favor Indique el Estudiante","Estudainte Invalido")
                       return
                else:
                   if(dat_tabla==" "):
                        General.show_message("Por Favor Indique el Trabajador","Trabajador Invalido")
                        return
                
                cedula=str(dat_tabla[0])
                if(dat_tabla[5]=="inactivo"):
                    General.show_message("no se puede generar carnet de un estudiante/trabajador inactivo","estudiasnte/trabajador invalido")
                    return 
                   
            #Get Director Data
            replace=[]
            nombre_directivo=""
            cedula_directivo=""
            temp_list=[]
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR) 
            cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}              
            join_data={}
            join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
            cond_join={"conditions_Names":["cargo"],"condition_Types":["and"],"conditions_Values":["director"],"conditions_Verify":["="]}              
            join_data["cargo"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":cond_join} 
                 
            data_director=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
            if(len(data_director)<=0):
                 General.show_error("No hay Director Registrado en el Sistema","Director Inexistente")
                 return
            target_names=["apellido","s_apellido","nombre","s_nombre"]
              
            for target in target_names:
                 val=data_director[0][target]
                 if(val=="" or val=="..."):
                    continue
                 temp_list.append(val)
            nombre_directivo=" ".join(temp_list)
            temp_list=[]
            cedula_directivo=data_director[0][constantes.CLAVE_TRABAJADOR]
            replace.append(["DIRECTOR",nombre_directivo])              
            replace.append(["CEDULA_DIRE",cedula_directivo,12,"bold"])
            fech=time_object.get_fecha()
            vencimiento=time_object.get_next_date4(fech,1)
            replace.append(["fecha_v",vencimiento,12,"bold"])
            
            #Get Target Data
            if(is_estud==False): 
                #Worker Carnet  
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)              
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
                data_trabaj=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data)
                join_data={}
                join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None} 
                cond_join={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":["inactivo"],"conditions_Verify":["!="]}              
                join_data["estatus_trabaj"]={"query_field":["fecha_ingreso"],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":cond_join} 
                join_data["cargo"]={"query_field":["cargo","cargo_ministerio","codigo_cargo"],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None} 
                join_data["expediente"]={"query_field":["src_foto"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"trabajador"},"Conditions_join":None} 
               
                data_trabaj=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],cond_data,join_data,True)
                if(len(data_trabaj)<=0):
                    General.show_message("Trabajador no Registrado o Inactivo","Trabajador Invalido")
                    return
                for target in target_names:
                    val=data_trabaj[0][target]
                    if(val=="" or val=="..."):
                        continue
                    temp_list.append(val)
                name_worker=" ".join(temp_list)
                temp_list=[]
                
                replace.append(["NOMBRES_C",name_worker])
                replace.append(["CEDULA_C",cedula])
                if(data_trabaj[0]["src_foto"]=="" or data_trabaj[0]["src_foto"]=="..."):
                    General.show_message("No se puede Emitir Carnet de un Trabajador sin Foto","Foto no Registrada")
                    return
                url_foto=constantes.SERVER+data_trabaj[0]["src_foto"]
                replace.append(["FOTO:",url_foto])
                cargo=data_trabaj[0]["cargo"]
                if(cargo.lower()!="secretaria" and cargo.lower()!="obrero"):
                    if(cargo.lower()=="director" or cargo.lower().startswith("sub director") or cargo.lower().startswith("subdirector")):
                        cargo="DIRECTIVO"
                    else:
                        cargo="DOCENTE"   
                else:
                    if(cargo.lower()=="secretaria"):  
                         cargo=cargo.upper()+"/ADMINISTRATIVO"                        
                    else:
                        cargo="OBRERO"                
                replace.append(["CARGO_C",cargo,12,"bold"])
                replace.append(["fecha_e",fech,12,""])       
                if(is_out==True):
                    #Carnet Request is Not from User
                    conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                    data_descarga=[f"download_{data_trabaj[0][constantes.CLAVE_TRABAJADOR]}_{time_object.get_full_time_str()}", data_trabaj[0][constantes.CLAVE_TRABAJADOR],type_form,time_object.get_fecha(),time_object.get_tiempo(),"carnet",time_object.get_fecha()]
                    conexion_bd.add_data(data_descarga,True)   
                ruta=constantes.FOLDER_DOCUMENTS+type_form+"-"+cedula+".xlsx"
                documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"unused",0,replace,False],True)
                
            else: 
                #Student Carnet
                conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)              
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
                join_data={}
                join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None} 
                cond_join={"conditions_Names":["estatus","estatus"],"condition_Types":["and","and"],"conditions_Values":["inactivo","graduado"],"conditions_Verify":["!=","!="]}                                
                join_data["estatus_estud"]={"query_field":["last_year"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":cond_join} 
                join_data["expediente"]={"query_field":["src_foto"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":"estudiante"},"Conditions_join":None} 
               
                data_student=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data,join_data,True)
                if(len(data_student)<=0):
                    General.show_message("Id del Estudiante no Registrada o Estudiante Inactivo","Estudiante Invalido")
                    return               
                for target in target_names:
                   val=data_student[0][target]
                   if(val=="" or val=="..."):
                       continue
                   temp_list.append(val)
                name_student=" ".join(temp_list)
                temp_list=[]
                replace.append(["CEDULA_C",cedula])   
                if(data_student[0]["src_foto"]=="" or data_student[0]["src_foto"]=="..."):
                     General.show_message("No se Puede Emit Carnet a un Estudiante sin Foto","Foto no Registrada")
                     return
                url_foto=constantes.SERVER+data_student[0]["src_foto"]      
                replace.append(["FOTO:",url_foto])
                replace.append(["NOMBRES_C",name_student])  
                available_cursos={"1":"Primer Año","2":"Segundo Año","3":"Tercer Año","4":"Cuarto Año","5":"Quinto Año"}                
                curso=available_cursos[data_student[0]["last_year"]]
                
                replace.append(["CARGO_C","ESTUDIANTE",12,"bold"])    
                replace.append(["fecha_e",fech,12,""])
                ruta=constantes.FOLDER_DOCUMENTS+type_form+"-"+cedula+".xlsx"
                documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"unused",0,replace,False],True)
                   
       elif(type_form=="cronograma"):
             
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            join_data={}
            
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"inicio","cierre"],None,None,True)
            if(len(data_cronog)<=0):
                General.show_message("No Existe Cronogramas Registrados","Cronograma Inexistente")
                return
            data_replace=[[],[],[]]
            data_content=[[],[],[]]
            data_replace[0].append(["NN","",12,"bold"])
            data_replace[1].append(["NN","",12,"bold"])
            data_replace[2].append(["NN","",12,"bold"])
            escolar_year=data_cronog[0][constantes.CLAVE_CRONOGRAMA]
            data_replace[0].append(["Año Escolar:",escolar_year,12,"bold"])
            data_replace[1].append(["Año Escolar:",escolar_year,12,"bold"])
            data_replace[2].append(["Año Escolar:",escolar_year,12,"bold"])
            data_replace[0].append(["año_e",data_cronog[0]["inicio"],12,"bold"])
            data_replace[0].append(["cierre_e",data_cronog[0]["cierre"],12,"bold"])
            moms=["False","False","False"]
            pages=[]
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            data_moms=conexion_bd.get_allData([constantes.CLAVE_MOMENTO,"fecha_inicio","fecha_limite"],None,None,True)
            if(len(data_moms)<=0):
                General.show_error("No Existent Momentos Academicos Registrados","Momentos Academicos Inexistentes")
                return    
                
            conexion_bd.set_tabla(constantes.TABLA_FECHA)
            orden_mom1=[["I CONSEJO GENERAL DOCENTES","consejo de docentes"],
            ["REUNION DE REPRESANTES","reunion de representantes"],
            ["ENTREGA DE PLANIFICACION A SUBDIRECCION ACADEMICA","entrega de planificaciones a subdireccion academica"],
            ["EVALUACION CONTINUA(ARTICULO 44LOE) DE LAS AREAS DE FORMACION EN FUNCION DE LOS TEMAS GENERADORESY REFERENTES TEORICO PRACTIVOS DE CADA AREA","evaluacion continua"],
            ["EVALUACION I MOMENTO MATERIA PENDIENTE","materia pendiente 1"],
            ["SEMANA ANIVERSARIO NOMBRE INSITUTO","semana aniversario"],
            ["ENTREGA DE NOTAS AL DEPARTAMENTO DE EVALUACION","entrega de calificacion a departamento de evaluacion"],
            ["EVALUACION II MOMENTO MATERIA PENDIENTE","materia pendiente 2"],
            ["CIERRE PEDAGOGICO I MOMENTO","cierre pedagogico"],
            ["CONSEJO DE CURSO","consejo de curso"],
            ["ENTREGA DE BOLETINES","entrega de boletas a representantes"],
            ["ASUETO DE NAVIDAD","asueto de navidad"],
            ] 
               
            orden_mom2=[["REUNION DE REPRESANTES","reunion de representantes"],
            ["ENTREGA DE PLANIFICACION A SUBDIRECCION ACADEMICA","entrega de planificaciones a subdireccion academica"],
            ["EVALUACION CONTINUA(ARTICULO 44 LOE) DE LASAREAS DE FORMACION EN FUNCION DE LOS TEMAS GENERADORESY REFERENTES TEORICO PRACTIVOS DE CADA AREA","evaluacion continua"],
            ["EVALUACION III MOMENTO MATERIA PENDIENTE","materia pendiente 3"],
            ["ASUETO DE CARNAVAL","asueto de carnaval"],
            ["ENTREGA DE NOTAS AL DEPARTAMENTO DE EVALUACION","entrega de calificacion a departamento de evaluacion"],
            ["CIERRE PEDAGOGICO II MOMENTO","cierre pedagogico"],
            ["CONSEJO DE CURSO","consejo de curso"],
            ["ENTREGA DE BOLETINES","entrega de boletas a representantes"]
            ]
            orden_mom3=[
            ["REUNION DE REPRESANTES","reunion de representantes"],
            ["ENTREGA DE PLANIFICACION A SUBDIRECCION ACADEMICA","entrega de planificaciones a subdireccion academica"],
            ["EVALUACION CONTINUA(ARTICULO 44LOE) DE LAS AREAS DE FORMACION EN FUNCION DE LOS TEMAS GENERADORESY REFERENTES TEORICO PRACTIVOS DE CADA AREA","evaluacion continua"],
            ["EVALUACION IV MOMENTO MATERIA PENDIENTE","materia pendiente 4"],
            ["ENTREGA DE NOTAS AL DEPARTAMENTO DE EVALUACION","entrega de calificacion a departamento de evaluacion"],
            ["CIERRE PEDAGOGICO III MOMENTO","cierre pedagogico"],
            ["CONSEJO DE CURSO","consejo de curso"],
            ["ENTREGA DE BOLETINES","entrega de boletas a representantes"],
            ["PROCESO DE REVISION ACOMPAÑADO DE ACTIVIDADES DE SUPERACIONPEDAGOGICA","revision"],
            ["MISA GRADUANDO","misa graduandos"],
            ["ACTO DE GRADO","acto de grado"],
            ]
            counts_rows=[0,0,0]
            count_moments=3
            conexion_bd.set_tabla(constantes.TABLA_FECHA)                       
                      
            for i in range(0,count_moments):
               if(i>=len(data_moms)):
                   data_replace[i].append(["xperiodox","",14,""])
                   continue
                
               periodo=f"{data_moms[i]['fecha_inicio']}-{data_moms[i]['fecha_limite']}"
               data_replace[i].append(["xperiodox",periodo,14,""]) 
               target_order=[]
               indexs_materia_pendientes=[]
               if(i==0):
                 target_order=orden_mom1
                 indexs_materia_pendientes=[4,7]
               elif(i==1):
                 indexs_materia_pendientes=[3]
                 target_order=orden_mom2
               elif(i==2):
                 indexs_materia_pendientes=[3,8]
                 target_order=orden_mom3
               for j in range(0,len(target_order)):
                   is_materia_pendiente=False
                   for index in indexs_materia_pendientes:
                       if(index==j):
                           is_materia_pendiente=True
                           break
                   moment_key=data_moms[i][constantes.CLAVE_MOMENTO]
                   razon=target_order[j][1]
                   if(is_materia_pendiente):
                      moment_key="momento 1"
                   cond_data={"conditions_Names":["razon",constantes.CLAVE_MOMENTO],"condition_Types":["and","and"],"conditions_Values":[razon,moment_key],"conditions_Verify":["=","="]}              
                   data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],cond_data,None,True)
                   if(len(data_fecha)>0):
                       
                       fecha=data_fecha[0]["fecha"]
                       second_fecha=""
                       if(data_fecha[0]["fecha_cierre"]!=fecha):
                         second_fecha=f"AL {data_fecha[0]['fecha_cierre']}"
                       full_date=f"{fecha} {second_fecha}"
                       data_content[i].append([full_date])
                   else:
                       data_content[i].append([""])
                               
                   
            counts_rows[0]=len(data_content[0])
            counts_rows[1]=len(data_content[1])
            counts_rows[2]=len(data_content[2])
            ruta=constantes.FOLDER_DOCUMENTS+type_form+data_cronog[0][constantes.CLAVE_CRONOGRAMA]+".xlsx"
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_CRONOGRAM,[counts_rows,data_content,"Razon",1,data_replace,False],True)          

   #Download User Manual
   @classmethod
   def download_manual(cls,url,doc_name):
        response=requests.get(url)
        if(response.status_code>400):
           General.show_error("error no existe el manual en el servidor","manual inexistente")
           return
        raw_data=response.content       
        direccion=constantes.FOLDER_DOCUMENTS+doc_name
        temp_file=open(direccion,"wb")
        temp_file.write(raw_data)
        temp_file.close()
        os.startfile(direccion)
   #Download a Document
   @classmethod
   def download_doc(cls,pnl,tipo):
        if(tipo==cls.DOCUMENT_EXPEDENT_STUDENT or tipo==cls.DOCUMENT_EXPEDENT_WORKER):
          #Expedent Download
          id_selected=pnl.get_comp_byTag("table").get_row_selectedData()
          if(id_selected!=" " ):
             src_exp=""
             target_table=constantes.TABLA_ESTUDIANTE
             target_id=constantes.CLAVE_ESTUDIANTE
             target_table_str="estudiante"
             if(tipo!=cls.DOCUMENT_EXPEDENT_STUDENT):
                 target_table=constantes.TABLA_TRABAJADOR
                 target_id=constantes.CLAVE_TRABAJADOR
                 target_table_str="trabajador"
             conexion_bd.set_tabla(target_table)
             cond_data={"conditions_Names":[target_id],"condition_Types":["and"],"conditions_Values":[str(id_selected[0])],"conditions_Verify":["="]}                    
             join_data={}
             join_data["expediente"]={"query_field":["src_exp"],"share_fields":{"field":constantes.CLAVE_EXPEDIENTE,"table_reference":target_table_str},"Conditions_join":None} 
             data_exp=conexion_bd.get_allData([target_id],cond_data,join_data,True)
             if(len(data_exp)<=0):
                   General.show_message("Error Accediendo al Expediente del Estudiante/Trabajador","Error")
                   return
             if(data_exp[0]["src_exp"]=="..." or data_exp[0]["src_exp"]==""):
                General.show_message("Aun no se ha Subido el Expediente del Trabajador/Estudiante al Servidor","Expediente Invalido")
                return
             url=constantes.SERVER+data_exp[0]["src_exp"]
             response=requests.get(url)
             if(response.status_code>400):
                  General.show_error("error obteniendo data del servidor","error de data del server")
                  return
             data_raw=response.content
             filename=url.split("/")
             ruta=constantes.FOLDER_DOCUMENTS+filename[len(filename)-1]
             temp_file=open(ruta,"wb")
             temp_file.write(data_raw)
             temp_file.close()
             General.show_message("expediente descargado en la carpeta documentos","expediente descargado exitosamente")    
             os.startfile(constantes.FOLDER_DOCUMENTS)
        elif(tipo==cls.DOCUMENT_TIMETABLES_SECTION or tipo==cls.DOCUMENT_TIMETABLES_WORKER):
            #Download for timeTables
            
            id_selected=pnl.get_comp_byTag("table").get_row_selectedData()
            target_table=constantes.TABLA_SECCION
            target_key=constantes.CLAVE_SECCION
            target_table_str="seccion"
            
            if(id_selected==" "):
              General.show_message("por favor Indique la Seccion/Trabajador","Seccion/Trabajador Invalido")
              return
            
            if(tipo!=cls.DOCUMENT_TIMETABLES_SECTION):
                target_table=constantes.TABLA_TRABAJADOR
                target_key=constantes.CLAVE_TRABAJADOR
                target_table_str="trabajador"
            conexion_bd.set_tabla(target_table)
            join_data={}
            cond_join={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":["default"],"conditions_Verify":["!="]}                                      
            join_data["horario"]={"query_field":["src_hor"],"share_fields":{"field":constantes.CLAVE_HORARIO,"table_reference":target_table_str},"Conditions_join":cond_join} 
            cond_data={"conditions_Names":[target_key],"condition_Types":["and"],"conditions_Values":[str(id_selected[0])],"conditions_Verify":["="]}                                     
            data_timeTable=conexion_bd.get_allData([target_key],cond_data,join_data,True)
            if(len(data_timeTable)<=0):
               General.show_message("Seccion/Trabajador sin Horario Registrado","Horario Invalido")
               return
            src_timeTable=data_timeTable[0]["src_hor"]
            if(src_timeTable=="" or src_timeTable=="..."):
               General.show_message("Horario sin Documento Registrado","Documento Invalido")
               return
            
            url=constantes.SERVER+src_timeTable
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("Error obteniendo Data del Servidor","Documento no Encontrado")
                return
            data_raw=response.content
            filename=url.split("/")
            ruta=constantes.FOLDER_DOCUMENTS+filename[len(filename)-1]
            temp_file=open(ruta,"wb")
            temp_file.write(data_raw)
            temp_file.close()
            os.startfile(ruta)    
    
   #Return the Filter data for Consults
   @classmethod
   def get_filterData(cls,pnl,vent,opcion):
        combo=pnl.get_comp_byTag("combo")
        selected=combo.get_selected_value()
        radio=pnl.get_comp_byTag("radio")
        selected_radio=""
        if(radio!=None):
           selected_radio=radio.get_selected_value()
        field=pnl.get_comp_byTag("field")
        filtro_val=field.get_text()
        data=[]
        fields=[]
        clave=[]
        filter_list=[None,None]
        alternative=pnl.get_comp_byName("identificador_cp2")
        if(alternative!=None):
             if(alternative.get_state()==True):
                 filtro_val=alternative.get_selected_value()
        if(filtro_val=="elejir" or filtro_val=="elegir"):
              filtro_val=""
        if(filtro_val!="" and (selected=="elejir" or selected=="elegir")):
            General.show_message("por favor indique el tipo de filtro","filtro no valido")
            return filter_list
            
        if(filtro_val!="" and selected!="elejir" and selected!="elegir" ):
            #filtros aplicar a los datos
            if((selected=="cedula" and opcion==cls.CONSULT_STUDENTS) or selected=="CI estud."):
               selected=constantes.CLAVE_ESTUDIANTE
            elif((selected=="cedula" and opcion==cls.CONSULT_WORKERS) or selected=="CI trabajador"):
                selected=constantes.CLAVE_TRABAJADOR
            elif(selected=="seccion"):
                 selected=constantes.CLAVE_SECCION
            elif(selected=="momento"):
                 selected=constantes.CLAVE_MOMENTO
                 if(len(filtro_val)==1):
                     filtro_val="momento "+filtro_val
            elif( selected=="area formacion" or selected=="area_formacion" or selected=="area form."):
                 selected=constantes.CLAVE_AREA_FORMACION           
            elif(selected=="CI_Docente"):
                selected=constantes.CLAVE_TRABAJADOR
            filter_list=[[selected],[filtro_val]]
            #filtros de radio buttons adicionales
            if(selected_radio=="cedulado"):
               filter_list[0].append(selected_radio)
               filter_list[1].append("True")
            elif(selected_radio=="no cedulado"):
               filter_list[0].append("cedulado")
               filter_list[1].append("False")
            elif(selected_radio=="incorporada"):
               filter_list[0].append("incorporada")
               filter_list[1].append("Si")
            elif(selected_radio=="no incorporada"): 
               filter_list[0].append("incorporada")
               filter_list[1].append("No")              
            elif(selected_radio=="docente" or selected_radio=="no docente" or selected_radio=="seccion"):
                filter_list[0].append("tipo")
                filter_list[1].append(selected_radio)              
        else:
            #No filters from ComboBox and TextField
            #Verify Radio Buttons Filter
            if(selected_radio=="cedulado"):
                filter_list=[["cedulado"],["True"]]
            elif(selected_radio=="no cedulado"):
               filter_list=[["cedulado"],["False"]]
            elif(selected_radio=="incorporada"):
               filter_list=[["incorporada"],["Si"]]
            elif(selected_radio=="no incorporada"): 
               filter_list=[["incorporada"],["No"]] 
            elif(selected_radio=="docente" or selected_radio=="no docente" or selected_radio=="seccion"):
                 filter_list=[["tipo"],[selected_radio]] 
        return filter_list
   #Consults to the Data Base Information
   @classmethod
   def consultar(cls,vent,opcion):
        pnl=vent.panelActual
        filter_list=cls.get_filterData(pnl,vent,opcion)
        data=[]
        tabla=pnl.get_comp_byTag("table")
        if(opcion==cls.CONSULT_WORKERS):
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           join_data={}
           join_data["nombre"]={"query_field":["nombre","apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None}
           join_data["estatus_trabaj"]={"query_field":["estatus"],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":None}
           join_data["cargo"]={"query_field":["cargo"],"share_fields":{"field":constantes.CLAVE_CARGO,"table_reference":"trabajador"},"Conditions_join":None}
           index=len(filter_list[0])-1
           if(index<0):
              General.show_error("Formato de filtros Invalido","Error")
              return
           worker_type=filter_list[1][index]
           cargos_conector_type=["and","and"]
           filter_cargos=["Secretaria","Obrero"]
           filter_cargos_fields=["cargo","cargo"]
           cargos_verify_type=["!=","!="]           
           if(worker_type!="docente"):
              filter_cargos_fields=["cargo","cargo","cargo","cargo","cargo","cargo","cargo"]
              filter_cargos=["Docente","Docente de Aula","Director","Coordinador de Orientacion","Coordinador de Evaluacion","Sub Director Academico","Sub Director Administrativo"]
              cargos_verify_type=["!=","!=","!=","!=","!=","!=","!="]           
              cargos_conector_type=["and","and","and","and","and","and","and"]
           cond_cargo={"conditions_Names":filter_cargos_fields,"condition_Types":cargos_conector_type,"conditions_Values":filter_cargos,"conditions_Verify":cargos_verify_type}
           cond_status=None
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}
        
           
           filter_field=""
           filter_val=""
           if(len(filter_list[0])>1):
              filter_field=filter_list[0][0]
              filter_val=filter_list[1][0]
              
           if(filter_val!="" and filter_field!=""):
               if(filter_field=="estatus"):
                   cond_status={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}
               elif(filter_field=="cargo"):
                   cond_cargo["conditions_Names"].append("cargo")
                   cond_cargo["condition_Types"].append("and")
                   cond_cargo["conditions_Values"].append(filter_val)
                   cond_cargo["conditions_Verify"].append("=")
               else:
                   cond_data["conditions_Names"].append(filter_field)
                   cond_data["condition_Types"].append("and")
                   cond_data["conditions_Values"].append(filter_val)
                   cond_data["conditions_Verify"].append("=")
                  
           join_data["cargo"]["Conditions_join"]=cond_cargo
           join_data["estatus_trabaj"]["Conditions_join"]=cond_status
          
           fields=[constantes.CLAVE_TRABAJADOR,"correo","telefono"]           
           tempdata=conexion_bd.get_allData(fields,cond_data,join_data,True)
           targets_names=["nombre","apellido"]
           for worker in tempdata:
                temp_list=[]
                for target in targets_names:
                    val=worker[target]
                    if(val=="" or val=="..."):
                       continue
                    temp_list.append(val)
                name=" ".join(temp_list)
                temp_list=[]
                data_row=[worker[constantes.CLAVE_TRABAJADOR],name,worker["cargo"],worker["correo"],worker["telefono"],worker["estatus"]]
                data.append(data_row) 
                     
        elif(opcion==cls.CONSULT_STUDENTS):
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           join_data={}
           join_data["nombre"]={"query_field":["nombre","apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None}
           join_data["estatus_estud"]={"query_field":["estatus","salud"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":None}
           index=len(filter_list[0])-1
           if(index<0):
              General.show_error("Formato de filtros Invalido","Error")
              return
           cedulado_val=filter_list[1][index]  
           cond_join={"conditions_Names":["cedulado"],"condition_Types":["and"],"conditions_Values":[cedulado_val],"conditions_Verify":["="]}
           cond_data=None
           
           filter_field=""
           filter_val=""
           if(len(filter_list[0])>1):
              filter_field=filter_list[0][0]
              filter_val=filter_list[1][0]
              
           if(filter_val!="" and filter_field!=""):
               if(filter_field=="estatus"):
                   cond_join["conditions_Names"].append(filter_field)
                   cond_join["condition_Types"].append("and")
                   cond_join["conditions_Values"].append(filter_val)
                   cond_join["conditions_Verify"].append("=")
               else:
                   cond_data={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}
           
           join_data["estatus_estud"]["Conditions_join"]=cond_join
           fields=[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_SECCION,constantes.CLAVE_REPRESENTANTE,"genero"]           
           #order_consult={"field":constantes.CLAVE_ESTUDIANTE,"type":"ASC"}          
           #tempdata=conexion_bd.get_allData(fields,cond_data,join_data,True,cls.limit_consult,cls.offset_consult,order_consult)
          
           tempdata=conexion_bd.get_allData(fields,cond_data,join_data,True)
           for estud in tempdata:
                data_row=[estud[constantes.CLAVE_ESTUDIANTE],estud["apellido"],estud["nombre"],estud[constantes.CLAVE_SECCION],estud[constantes.CLAVE_REPRESENTANTE],estud["estatus"],estud["salud"],estud["genero"]]
                data.append(data_row) 
        elif(opcion==cls.CONSULT_TEACHERS):
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           join_data={}
           join_data["nombre"]={"query_field":["nombre","apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"trabajador"},"Conditions_join":None}
           join_data["estatus_trabaj"]={"query_field":["estatus"],"share_fields":{"field":constantes.CLAVE_ESTATUS_TRABAJ,"table_reference":"trabajador"},"Conditions_join":None}
           join_data["profesor"]={"query_field":["seccion_guia"],"share_fields":{"field":constantes.CLAVE_TRABAJADOR,"table_reference":"trabajador"},"Conditions_join":None}
           cond_status=None
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_TRABAJADOR],"condition_Types":["and","and"],"conditions_Values":["000","001"],"conditions_Verify":["!=","!="]}
           cond_teacher=None
           
           filter_field=""
           filter_val=""
           if(filter_list[0]!=None):
              if(len(filter_list[0])>0):
                 filter_field=filter_list[0][0]
                 filter_val=filter_list[1][0]  
           if(filter_val!="" and filter_field!=""):
               if(filter_field=="estatus"):
                   cond_status={"conditions_Names":["estatus"],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}
               elif(filter_field=="seccion_guia"):
                   cond_teacher={"conditions_Names":["seccion_guia"],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}             
               else:
                   cond_data["conditions_Names"].append(filter_field)
                   cond_data["condition_Types"].append("and")
                   cond_data["conditions_Values"].append(filter_val)
                   cond_data["conditions_Verify"].append("=")
                  
           join_data["profesor"]["Conditions_join"]=cond_teacher
           join_data["estatus_trabaj"]["Conditions_join"]=cond_status
          
           fields=[constantes.CLAVE_TRABAJADOR]           
           tempdata=conexion_bd.get_allData(fields,cond_data,join_data,True)
           targets_names=["nombre","apellido"]
           for worker in tempdata:
                temp_list=[]
                for target in targets_names:
                    val=worker[target]
                    if(val=="" or val=="..."):
                       continue
                    temp_list.append(val)
                name=" ".join(temp_list)
                temp_list=[]
                secc_guia=worker["seccion_guia"]
                if(secc_guia=="default"):
                   secc_guia=""
                data_row=[worker[constantes.CLAVE_TRABAJADOR],name,secc_guia,worker["estatus"]]
                data.append(data_row) 
            
        elif(opcion==cls.CONSULT_SECTIONS):
            fields=[constantes.CLAVE_SECCION,"año","letra","total_estud"]  
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":["default"],"conditions_Verify":["!="]}                                     
            
            filter_field=""
            filter_val=""
            if(filter_list[0]!=None):
               if(len(filter_list[0])>0):
                  filter_field=filter_list[0][0]
                  filter_val=filter_list[1][0] 
                              
            if(filter_val!="" and filter_field!=""):
                cond_data["conditions_Names"].append(filter_field)
                cond_data["condition_Types"].append("and")
                cond_data["conditions_Values"].append(filter_val)
                cond_data["conditions_Verify"].append("=")
               
            temp_data=conexion_bd.get_allData(fields,cond_data,None,True)  
            for section in temp_data:
                next_row=[section[constantes.CLAVE_SECCION],section["año"],section["letra"],section["total_estud"]]
                data.append(next_row)               
 
        elif(opcion==cls.CONSULT_ACADEMIC_MOMENTS):
            
            fields=[constantes.CLAVE_MOMENTO,"abierto","fecha_inicio","fecha_limite"] 
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            cond_data=None           
            filter_field=""
            filter_val=""
            if(filter_list[0]!=None):
               if(len(filter_list[0])>0):
                  filter_field=filter_list[0][0]
                  filter_val=filter_list[1][0] 
                              
            if(filter_val!="" and filter_field!=""):
                if(filter_field=="estatus"):
                   filter_field="abierto"
                   if(filter_val=="abierto"):
                      filter_val="true"
                   elif(filter_val=="cerrado"):
                      filter_val="false"
                cond_data={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
            
            temp_data=conexion_bd.get_allData(fields,cond_data,None,True)  
            for mom in temp_data:
                estatus="abierto" if mom["abierto"]=="true" else "cerrado"
                next_row=[mom[constantes.CLAVE_MOMENTO],estatus,mom["fecha_inicio"],mom["fecha_limite"]]
                data.append(next_row) 
            
                     
        elif(opcion==cls.CONSULT_TIMETABLES_DISPONIBILITY):
            
            
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            fields=[constantes.CLAVE_TRABAJADOR,"turno","disp_lunes","disp_martes","disp_miercoles","disp_jueves","disp_viernes"]         
            cond_data=None
            filter_field=""
            filter_val=""
            if(filter_list[0]!=None):
               if(len(filter_list[0])>0):
                  filter_field=filter_list[0][0]
                  filter_val=filter_list[1][0] 
                              
            if(filter_val!="" and filter_field!=""):                
                cond_data={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
            
            temp_dat=conexion_bd.get_allData(fields,cond_data,None,True)
            fields_days=["disp_lunes","disp_martes","disp_miercoles","disp_jueves","disp_viernes"]
            for worker in temp_dat:
               next_row=[worker[constantes.CLAVE_TRABAJADOR],worker["turno"]]
               for target in fields_days:
                  val=worker[target]
                  if(val!="no disponible"):
                        val="disponible"
                  next_row.append(val)
               data.append(next_row)
            
        elif(opcion==cls.CONSULT_FORMATION_AREAS):

            conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
            fields_area=[constantes.CLAVE_AREA_FORMACION]
            join_data={}
            join_data["años_incorporados"]={"query_field":["1_año","2_año","3_año","4_año","5_año"],"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":None} 
            index=len(filter_list[0])-1
            if(index<0):
               General.show_error("Formato de filtros Invalido","Error")
               return
            incorp_val=filter_list[1][index]
            cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":[incorp_val],"conditions_Verify":["="]}                                     
            filter_field=""
            filter_val=""
            if(filter_list[0]!=None):
               if(len(filter_list[0])>1):
                  filter_field=filter_list[0][0]
                  filter_val=filter_list[1][0] 
                              
            if(filter_val!="" and filter_field!=""):
                cond_data["conditions_Names"].append(filter_field)
                cond_data["condition_Types"].append("and")
                cond_data["conditions_Values"].append(filter_val)
                cond_data["conditions_Verify"].append("=")                
              
            temp_data=conexion_bd.get_allData(fields_area,cond_data,join_data,True)
            for area in temp_data:
               next_row=[area[constantes.CLAVE_AREA_FORMACION],area["1_año"],area["2_año"],area["3_año"],area["4_año"],area["5_año"]]
               data.append(next_row)
     
        elif(opcion==cls.CONSULT_USERS_HISTORIAL):
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            first_date=pnl.get_comp_byName("fecha1")
            second_date=pnl.get_comp_byName("fecha2")
            options_comp=pnl.get_comp_byName("filtros_cp")
            field_filters=pnl.get_comp_byName("identificador_cp")
            if(field_filters==None or options_comp==None or first_date==None or second_date==None ):
                General.show_error("Faltan Elementos del Formulario","Error de UI")
                return
            selected_option=options_comp.get_selected_value()
            fecha_inicio=""
            fecha_cierre=""     
            is_date=False
            cond_data=None
            if(selected_option!="elegir"):
               if(selected_option=="desde - hasta" or selected_option=="antes de" or selected_option=="despues de"):
                  is_date=True
                  fecha_inicio=first_date.get_text()
                  fecha_cierre=second_date.get_text()
                  
                  if(General.is_valid(fecha_inicio,constantes.CADENA_FECHA,False,2)==False):
                      General.show_message("por favor ingrese una fecha de inicio","fecha invalida")
                      return
                  if(selected_option=="desde - hasta"):
                     if(General.is_valid(fecha_cierre,constantes.CADENA_FECHA,False,2)==False):
                         General.show_message("por favor ingrese una fecha de cierre","fecha invalida")
                         return  
               else:
                  val_filter=field_filters.get_text()
                  if(General.is_valid(val_filter,constantes.CADENA_ALFANUMERICA,True,3)==False):
                     General.show_message("Por Favor Indique el Valor a Filtrar ","Valor del Filtro Invalido")
                     return
                     
                  if(selected_option=="usuario"):
                     cond_data={"conditions_Names":[constantes.CLAVE_USUARIO],"condition_Types":["and"],"conditions_Values":[val_filter],"conditions_Verify":["="]}                                     
                  elif(selected_option=="accion realizada"):
                      cond_data={"conditions_Names":["tipo"],"condition_Types":["and"],"conditions_Values":[val_filter],"conditions_Verify":["="]}                                     
            fields=[constantes.CLAVE_USUARIO,"fecha","hora","tipo","razon"]
            #order_consult={"field":"tipo","type":"ASC"}
            #data_temp=conexion_bd.get_allData(fields,cond_data,None,True,cls.limit_consult,cls.offset_consult,order_consult)
           
            data_temp=conexion_bd.get_allData(fields,cond_data,None,True)
            for register in data_temp:
               
               if(is_date):
                  time_object=tiempo()
                  valid_date=False
                  if(selected_option=="desde - hasta"):
                     if(time_object.is_previous(register["fecha"],fecha_cierre,False) and time_object.is_previous(fecha_inicio,register["fecha"],False)):
                        valid_date=True
                  elif(selected_option=="antes de"):
                     if(time_object.is_previous(register["fecha"],fecha_inicio,False)):
                          valid_date=True
                  elif(selected_option=="despues de"):
                     if(time_object.is_previous(register["fecha"],fecha_inicio,False)==False):
                         valid_date=True
                  if(valid_date==False):
                      continue
               data.append([register[constantes.CLAVE_USUARIO],register["fecha"],register["hora"],register["tipo"]]) 
        
        elif(opcion==cls.CONSULT_FORMATION_AREAS_TEACHERS):
              conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
              fields_prof=[constantes.CLAVE_TRABAJADOR]
              join_data={}
              join_data["trabajador"]={"query_field":[constantes.CLAVE_NOMBRE],"share_fields":{"field":constantes.CLAVE_TRABAJADOR,"table_reference":"profesor"},"Conditions_join":None}
              join_data["area_dictada_docentes"]={"query_field":[constantes.CLAVE_AREA_FORMACION],"share_fields":{"field":constantes.CLAVE_PROFESOR,"table_reference":"profesor"},"Conditions_join":None}
              cond_data=None
              cond_join=None
              filter_field=""
              filter_val=""
              if(filter_list[0]!=None):
                 if(len(filter_list[0])>0):
                    filter_field=filter_list[0][0]
                    filter_val=filter_list[1][0] 
                              
              if(filter_val!="" and filter_field!=""):  
                  if(filter_field==constantes.CLAVE_AREA_FORMACION):
                      cond_join={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
                  else:                  
                      cond_data={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
              join_data["area_dictada_docentes"]["Conditions_join"]=cond_join
              temp_data=conexion_bd.get_allData(fields_prof,cond_data,join_data,True)
              conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
              for prof in temp_data:
                 cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[prof[constantes.CLAVE_NOMBRE]],"conditions_Verify":["="]}                                     
                 name_dat=conexion_bd.get_allData(["nombre","apellido"],cond_data,None,True)
                 if(len(name_dat)<=0):
                     continue
                 temp_list=[name_dat[0]["nombre"],name_dat[0]["apellido"]]
                 name=" ".join(temp_list)
                 temp_list=[]
                 next_row=[prof[constantes.CLAVE_TRABAJADOR],name,prof[constantes.CLAVE_AREA_FORMACION]]
                 data.append(next_row)
                         
        elif(opcion==cls.CONSULT_MATERIA_PENDIENTE):
             data=[]
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
             fields=[constantes.CLAVE_MATERIA_PENDIENTE,constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"]
             cond_data=None
             filter_field=""
             filter_val=""
             if(filter_list[0]!=None):
                if(len(filter_list[0])>0):
                    filter_field=filter_list[0][0]
                    filter_val=filter_list[1][0] 
                              
             if(filter_val!="" and filter_field!=""):  
                 cond_data={"conditions_Names":[filter_field],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
             temp_data=conexion_bd.get_allData(fields,cond_data,None,True)
             conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
             associated_indexs={"1 intento":3,"2 intento":4,"3 intento":5,"4 intento":6,"revision":7}
             for register in temp_data:
               cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[register[constantes.CLAVE_MATERIA_PENDIENTE]],"conditions_Verify":["="]}                                     
               data_pend=conexion_bd.get_allData(["intento","valor"],cond_data,None,True)
               next_row=[register[constantes.CLAVE_ESTUDIANTE],register[constantes.CLAVE_AREA_FORMACION],register["año"],"ND","ND","ND","ND","ND"]
               index_intentos=3
               for calif in data_pend:
                  if(calif["intento"] in associated_indexs):
                      next_row[associated_indexs[calif["intento"]]]=calif["valor"]                  
               data.append(next_row)  
        
        elif(opcion==cls.CONSULT_DOWNLOADS):
              conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
              cond_data=None
              fields=[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_FORMATO,"tipo_descarga","fecha","hora"]
              
              filter_field=""
              filter_val=""
              if(filter_list[0]!=None):
                 if(len(filter_list[0])>0):
                    filter_field=filter_list[0][0]
                    filter_val=filter_list[1][0] 
                              
              if(filter_val!="" and filter_field!=""):  
                  if(filter_field=="tipo formato"):    
                      cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
                  elif(filter_field=="tipo doc"):             
                      cond_data={"conditions_Names":["tipo_descarga"],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
                  elif(filter_field==constantes.CLAVE_TRABAJADOR):
                      cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[filter_val],"conditions_Verify":["="]}                                     
            
              fields=[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_FORMATO,"tipo_descarga","fecha","hora"]
              temp_data=conexion_bd.get_allData(fields,cond_data,None,True)
              for register in temp_data:
                 next_row=[register[constantes.CLAVE_TRABAJADOR],register[constantes.CLAVE_FORMATO],register["tipo_descarga"],register["fecha"],register["hora"]]
                 data.append(next_row)
        tabla.reset()
        if(data!=[]):
           for i in range(0,len(data)):
               tabla.add_row(data[i])
        
    
