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

   
   #Generate a Report
   @classmethod
   def generar_reporte(cls,pnl,tipo,usr,receive_data=None,secc=None):
       time_object=tiempo()
       from event_manager import Event_manager 
       vent=Event_manager.vent 
       raiz=vent.raiz
       if(tipo=="asistencia seccion" or tipo=="evaluacion continua" or tipo=="lista de la seccion"):
           clave=""
           if(secc==None):
               clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           else:
              clave=secc
           
           if(clave==" "):
              General.show_message("por favor seleccione una seccion","seccion no valida")
              return
           conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
           data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and"])
           if(data_formato==[]):
              General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
              return
           src=data_formato[0][0]
           url=constantes.SERVER+src
           response=requests.get(url)
           if(response.status_code>400):
               General.show_error("error obteniendo data del servidor","error de data del server")
               return
           data_form=response.content
           conexion_bd.set_tabla(constantes.TABLA_SECCION)
           curso=conexion_bd.get_allData(["año"],1,[constantes.CLAVE_SECCION],[clave],["and"])[0][0]
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           data_seccion=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_SECCION],[clave],["and"])
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           if(data_seccion==[]):
               General.show_message("seccion sin estudiantes registrados","seccion vacia o inexistente")
               return
           num_estud=len(data_seccion)
           data_nomina=[]
           for i in range(0,num_estud):
               ci=data_seccion[i][0]
               data_nombre=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_seccion[i][1]],["and"])
               fullname=""
               for j in range(0,4):
                   if(data_nombre[0][j]!="" and data_nombre[0][j]!=" "):
                       fullname+=data_nombre[0][j]+" "
               data_nomina.append([ci,fullname])     
           s=clave.split("(")
           nomb_secc=s[0]
           turno=""
           letra=s[1].split(")")[0]
           if(letra.lower()=="t"):
               turno="tarde"
           else:
               turno="mañana"
           data_replace=[]
           data_replace.append(["Seccion:",nomb_secc])
           data_replace.append(["Turno:",turno])
           data_replace.append(["Fecha:",time_object.get_fecha()])
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],1)
           if(data_cronog!=[]):
               data_replace.append(["periodo escolar:",data_cronog[0][0]])                     
           filename=tipo+" "+clave+".xlsx"
           path=constantes.FOLDER_DOCUMENTS+filename
           msg_end=False
           documento.request(pnl.win,[path,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_estud,data_nomina,"Nº",2,data_replace,msg_end],True)    
       elif(tipo=="inscripcion"):
          conexion_bd.set_tabla(constantes.TABLA_FORMATO)
          data_form=conexion_bd.get_allData(["src_form"],1,[constantes.CLAVE_FORMATO],[tipo],["and"])
          if(data_form==[]):
              General.show_error("sin formato de inscripcion","formato de isncripcion no registrado")
              return
          url=constantes.SERVER+data_form[0][0]
          response=requests.get(url)
          if(response.status_code>400):
              General.show_error("error obteniendo data del servidor","error de data del server")
              return
          data_raw=response.content
          replace=[]
          if(receive_data[1][10]!="" and receive_data[1][10]!="..."):
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              data_e=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[receive_data[0][0]],["and"])
              if(data_e!=[]):
                  conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                  data_f=conexion_bd.get_allData(["src_foto"],1,[constantes.CLAVE_EXPEDIENTE],[data_e[0][0]],["and"])
                  if(data_f!=[]):
                      if(data_f[0][0]!="" and data_f[0][0]!="..."):
                          replace.append(["FOTO:",constantes.SERVER+data_f[0][0]])
                      else:
                          replace.append(["FOTO:","not found"])
          else: 
               replace.append(["FOTO:","not found"])        
          nombres=""
          apellidos=""
          if(receive_data[1][0]!="" and receive_data[1][0]!="..."):
               nombres=receive_data[1][0]
          if(receive_data[1][1]!="" and receive_data[1][1]!="..."):
               apellidos=receive_data[1][1]
          if(receive_data[1][2]!="" and receive_data[1][2]!="..."):
               nombres=nombres+" "+receive_data[1][2]
          if(receive_data[1][3]!="" and receive_data[1][3]!="..."):
               apellidos=apellidos+" "+receive_data[1][3]
          dir_estud=receive_data[3][2]+","+receive_data[3][3]+","+receive_data[3][4] 
          nombre_repres=receive_data[2][2]
          if(receive_data[2][12]!="" and receive_data[2][12]!="..."):
             nombre_repres=nombre_repres+" "+receive_data[2][12]
          nombre_repres=nombre_repres+" "+receive_data[2][1]
          if(receive_data[2][11]!="" and receive_data[2][11]!="..."):
             nombre_repres=nombre_repres+" "+receive_data[2][11]
          replace.append(["Apellidos y Nombres:",apellidos+" "+nombres])
          replace.append(["Fecha de Nacimiento:",receive_data[1][8]])
          replace.append(["Domicilio:",dir_estud]) 
          replace.append(["Representante:",nombre_repres])
          id_representant=receive_data[2][0]
          if(id_representant.startswith("v-")==False and id_representant.startswith("V-")==False and id_representant.startswith("e-")==False and id_representant.startswith("E-")==False):
                id_representant="V-"+id_representant
          replace.append(["CI:",id_representant])
          replace.append(["Telefono:",receive_data[2][3]])
          dir_repres=receive_data[2][7]+","+receive_data[2][8]+","+receive_data[2][9]
          replace.append(["Domicilio del Representante:",dir_repres])
          replace.append(["Correo del Representante:",receive_data[2][4]])
          edad=str(time_object.get_edad(receive_data[1][8]))
          replace.append(["Parentesco:",receive_data[2][10]])
          replace.append(["Oficio:",receive_data[2][13]])
          replace.append(["Cedula:",receive_data[0][0]])
          replace.append(["Plantel de Procedencia:",receive_data[1][11]])
          replace.append(["NN",""])
          replace.append(["Edad:",edad])
          replace.append(["Yo:",nombre_repres])
          replace.append(["de:",nombres+" "+apellidos])
          fech=time_object.get_fecha()
          fech=list(fech.split("/"))
          fech[1]=time_object.get_mes(int(fech[1]))
          replace.append(["Inscripcion Realizada a los:","Inscripcion Realizada a los "+fech[0]+" dias "+"del mes de "+fech[1]+" del Año "+fech[2]])
          secc=""
          secc_temp=receive_data[4][1]
          if(secc_temp.endswith("(M)")):
              secc_temp=secc_temp.split("(M)")[0]
              secc=secc_temp
          else:
              secc_temp=secc_temp.split("(T)")[0]
              secc=secc_temp
          num_replace=len(replace)
          filename=data_form[0][0].split("/")
          filename=receive_data[0][0]+"-"+filename[len(filename)-1]
          ruta=constantes.FOLDER_DOCUMENTS+filename
          data_cells=[]
          year_inscription=int(receive_data[1][9])
          conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
          data_cronog=conexion_bd.get_allData(None,None)
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
                if(receive_data[5][0]!="False"):
                    con_pendientes=True                   
                    for pd in range(1,len(receive_data[5])):
                        pends=pends+receive_data[5][pd][0].lower()+","
                if(receive_data[7][0]!="False"):
                    for rept in range(1,len(receive_data[7])):
                        areas=areas+receive_data[7][rept].lower()+","
                temp_data[4]=pends
                temp_data[3]=areas                        
             data_cells.append(temp_data)
             
          if(usr.data_expediente!=[]):
               for ex in usr.data_expediente:
                 if(ex!=False):
                      replace.append([ex,"X"])
          else:
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              dat_expedent=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[receive_data[0][0]],["and"])
              if(dat_expedent!=[]):
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                expedent=conexion_bd.get_allData(["src_exp"],1,[constantes.CLAVE_EXPEDIENTE],[dat_expedent[0][0]],["and"])
                if(expedent!=[]):
                    conseguido=False
                    proceder=False  
                    response=None                         
                    if(expedent[0][0]!="" and expedent[0][0]!="..." and expedent[0][0].endswith(".zip")):
                        proceder=True 
                    if(proceder):
                        conseguido=True
                        url_exp=constantes.SERVER+expedent[0][0]
                        response=requests.get(url_exp)   
                        if(response.status_code>400 or (url_exp.endswith(".zip")==False)):
                            conseguido=False
                    if(conseguido==True):
                        ruta_zip=constantes.FOLDER_ZIP+"temp_zip.zip"
                        f_temp=open(ruta_zip,"wb")
                        f_temp.write(response.content)
                        f_temp.close()
                        if sys.version_info >= (3, 7):
                            import zipfile
                        else:
                            import zipfile37 as zipfile
                        dir_extraccion=constantes.FOLDER_ZIP
                        Zip= zipfile.ZipFile(ruta_zip, 'r')
                        Zip.extractall(dir_extraccion)
                        Zip.close()
                        data_zip=[False,False,False,False,False,False,False,False,False]                                        
                        info_z=open(dir_extraccion+"info.txt","r")
                        for linea in info_z:
                            linea_split=linea.split(":")
                            if(linea.startswith("fotocopia de la cedula")):
                                data_zip[0]="copia de Cedula de Identidad"
                            elif(linea.startswith("copia de la partida de nacimiento")):
                                data_zip[1]="Copia de Partida de Nacimiento Original"
                                data_zip[2]="partida de nacimiento Original"
                            elif(linea.startswith("Documento de Aprobacion de sexto grado")):
                                 data_zip[3]="Boleta del periodos escolar anterior de ser neceario"
                            elif(linea.startswith("calificaciones certificadas de Años cursados")):
                                data_zip[4]="Notas Cerificadas"
                            elif(linea.startswith("Carta de Residencia")):
                                data_zip[5]="Carta de Residencia"
                            elif(linea.startswith("fotocopia de la cedula del representante")):
                                data_zip[6]="Copia de Cedula"
                            elif(linea.startswith("foto del representante")):
                                 data_zip[7]="2 Fotos"
                            elif(linea.startswith("foto")):
                                data_zip[8]="2 fotos del estudiante"
                        info_z.close()
                        import threading
                        hilo=threading.Thread(target=Event_manager.reset_zip_files)
                        hilo.start()
                        for ex in data_zip:
                            if(ex!=False):
                                replace.append([ex,"X"])                
          documento.request(raiz,[ruta,data_raw],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[len(data_cells),data_cells,"NN",6,replace,False],True)
       elif(tipo=="info estudiante"):
           clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           if(clave==" "):
              General.show_message("por favor seleccione un estudiante","estudiante no valido")
              return
           conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
           data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
           if(data_formato==[]):
              General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
              return
           src=data_formato[0][0]
           url=constantes.SERVER+src
           response=requests.get(url)
           if(response.status_code>400):
               General.show_error("error obteniendo data del servidor","error de data del server")
               return
           data_form=response.content
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[str(clave)],["and"])
           if(data_estud==[]):
                General.show_message("cedula del estudiante no registrada","estudiante inexistente")
                return
           num_estud=0
           data_modif=[]
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][1]],["and"])
           nombre=""
           apellido=""
           for index_name in range(0,len(data_nombre[0])):
               if(index_name <2):
                  if(data_nombre[0][index_name]!="" and data_nombre[0][index_name]!="..."):
                      nombre=nombre+data_nombre[0][index_name]+" "
               else:
                  if(data_nombre[0][index_name]!="" and data_nombre[0][index_name]!="..."):
                      apellido=apellido+data_nombre[0][index_name]+" "             
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_ESTUD,len(constantes.CAMPOS_ESTATUS_ESTUD),[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][2]],["and"])
           data_modif.append(["NOMBRES:",nombre])
           data_modif.append(["APELLIDOS:",apellido])
           data_modif.append(["CEDULA:",data_estud[0][0]])
           data_modif.append(["GENERO:",data_estud[0][6]])
           data_modif.append(["NACIMIENTO:",data_estud[0][7]])
           valor_ced="Si"
           if(data_estatus[0][3]=="False"):
                valor_ced="No"          
           data_modif.append(["CEDULADO:",valor_ced])
           estado=data_estatus[0][1]
           if(estado=="irregular"):
               estado="activo"
           data_modif.append(["ESTATUS:",estado])
           data_modif.append(["ESTADO SALUD:",data_estatus[0][2]])
           data_modif.append(["AÑO DE CURSO:",data_estatus[0][4]])
           data_modif.append(["FECHA DE INGRESO:",data_estatus[0][6]])
           data_modif.append(["ULTIMA INSCRIPCION:",data_estatus[0][5]])
           data_modif.append(["PLANTEL DE PROCEDENCIA:",data_estatus[0][7]])
           secc=""
           if(data_estud[0][3].lower()=="default"):
              secc=""
           elif(data_estud[0][3].endswith("(M)")):
               temp_secc=data_estud[0][3].split("(M)")[0]
               secc=temp_secc+" "+"(Mañana)"
           else:
                temp_secc=data_estud[0][3].split("(T)")[0]
                secc=temp_secc+" "+"(Tarde)"
           data_modif.append(["SECCION:",secc])
           conexion_bd.set_tabla(constantes.TABLA_SECCION)
           data_secc=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION),[constantes.CLAVE_SECCION],[data_estud[0][3]],["and"])
           if(data_secc!=[]):
                if(data_secc[0][0].lower()!="default"):
                    conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                    data_hor=conexion_bd.get_allData(constantes.CAMPOS_HORARIO,len(constantes.CAMPOS_HORARIO),[constantes.CLAVE_HORARIO],[data_secc[0][3]],["and"])
                    if(data_hor!=[]):
                      data_modif.append(["TURNO:",data_hor[0][2]])
                else:
                    data_modif.append(["TURNO:",""])
                
           conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
           data_pendiente=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE],[data_estud[0][0]],["and"])
           id_representant=data_estud[0][5]
           if(id_representant.startswith("v-")==False and id_representant.startswith("V-")==False and id_representant.startswith("e-")==False and id_representant.startswith("E-")==False):
                id_representant="V-"+id_representant        
           data_modif.append(["MATERIAS PENDIENTE:",str(len(data_pendiente))+" materias"])
           data_modif.append(["CEDULA_R:",id_representant])
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           data_repres=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[data_estud[0][5]],["and"])
           if(data_repres==[]):
                General.show_error("error de datos del representante","representante invalido")
                return
                      
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           data_nomb_r=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_repres[0][1]],["AND"])
           nombre_r=""
           apellido_r=""
           for name_index in range(0,4):
                if(name_index<2):
                   if(data_nomb_r[0][name_index]!="" and data_nomb_r[0][name_index]!="..."):
                        nombre_r=nombre_r+data_nomb_r[0][name_index]+" "
                else:
                   apellido_r=apellido_r+data_nomb_r[0][name_index]+" "         
           data_modif.append(["NOMBRE:",nombre_r])
           data_modif.append(["APELLIDO:",apellido_r])
           data_modif.append(["TELEFONO:",data_repres[0][2]])
           data_modif.append(["CORREO:",data_repres[0][3]])
           data_modif.append(["PARENTESCO:",data_estud[0][9]])
           data_modif.append(["OCUPACION:",data_repres[0][4]])
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           data_dir_representant=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[data_repres[0][5]],["and"])
           direcc_repres=data_dir_representant[0][1]+","+data_dir_representant[0][2]+","+data_dir_representant[0][3]
           data_modif.append(["DIRECCION REPRESENTANTE:",direcc_repres])
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           data_exp=conexion_bd.get_allData(constantes.CAMPOS_EXPEDIENTE,len(constantes.CAMPOS_EXPEDIENTE),[constantes.CLAVE_EXPEDIENTE],[data_estud[0][4]],["and"])
           if(data_exp==[]):
                data_modif.append(["FOTO:","not found"])
           else:
                if(data_exp[0][2]!="" and data_exp[0][2]!="..."):
                    data_modif.append(["FOTO:",constantes.SERVER+data_exp[0][2]]) 
                else:
                   data_modif.append(["FOTO:","not found"])
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           data_dir=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),[constantes.CLAVE_DIRECCION],[data_estud[0][8]],["and"])
           if(data_dir==[]):
                General.show_error("error de datos de la direccion","representante invalido")
                return
           dire=data_dir[0][1]+","+data_dir[0][2]+","+data_dir[0][3]
           data_modif.append(["DIRECCION:",dire])
           filename=tipo+" "+str(clave)+".xlsx"
           ruta=constantes.FOLDER_DOCUMENTS+filename
           documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"CEDULA:",0,data_modif,False],True)

       elif(tipo=="lista de trabajadores"):
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            trabajs=conexion_bd.get_allData(None,None)
            data_nomina=[]
            if(trabajs==[]):
                General.show_message("no existen trabajadores registrados")
                return
            for tr in trabajs:
                conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                dat_expedent=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[tr[7]],["and"])
                if(dat_expedent!=[] and tr[0]!="000" and tr[0]!="001"):
                    #prevent get default worker of Admin User
                    if(dat_expedent[0][0]!="inactivo"):
                        conexion_bd.set_tabla(constantes.TABLA_CARGO)
                        data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[tr[6]],["and"])
                        if(data_cargo!=[]):
                            data_row=[tr[0],"",data_cargo[0][1],data_cargo[0][4]]
                            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                            data_nomb=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[tr[1]],["and"])
                            nombre=""
                            if(data_nomb!=[]):
                                nombre=data_nomb[0][0]
                                for i in range(1,4):
                                    if(data_nomb[0][i]!="" and  data_nomb[0][i]!=" "):
                                        nombre=nombre+" "+data_nomb[0][i]
                                nombre=nombre.upper()
                                data_row[1]=nombre
                                data_nomina.append(data_row)
            num_rows=len(data_nomina)
            num_cols=0
            if(num_rows>0):
               num_cols=len(data_nomina[0])
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            data_form=conexion_bd.get_allData( ["src_form"],1,["tipo"],[tipo],["and"])
            if(data_form==[]):
                General.show_error("formato de nomina de trabajadores no registrado","formato no registrado")
                return   
            url=constantes.SERVER+data_form[0][0]
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            raw_data=response.content
            form_name=data_form[0][0].split("/")
            filename=form_name[len(form_name)-1]+"_"+time_object.get_fecha()
            filename=filename.replace("/","-")
            ruta=constantes.FOLDER_DOCUMENTS+filename+".xlsx"
            documento.request(raiz,[ruta,raw_data],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,data_nomina,"Nº",num_cols,data_replace,False],True) 
       elif(tipo=="info trabajador"):
           clave=pnl.get_comp_byName("table1_cp").get_row_selectedData()[0]
           if(clave==" "):
             General.show_message("por favor seleccione un trabajador","trabajador no valido")
           conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
           data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
           if(data_formato==[]): 
               General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
               return
           src=data_formato[0][0]
           url=constantes.SERVER+src
           response=requests.get(url)
           if(response.status_code>400):
               General.show_error("error obteniendo data del servidor","error de data del server")
               return
           data_form=response.content
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[str(clave)],["and"])
           if(data_trabaj==[]):
              General.show_message("cedula del trabajador no registrada","trabajador inexistente") 
              return
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
           data_estatus=conexion_bd.get_allData(constantes.CAMPOS_ESTATUS_TRABAJ,len(constantes.CAMPOS_ESTATUS_TRABAJ),[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][7]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])
           num_trabaj=0
           data_modif=[]
           nombre=""
           apellido=""
           for name_index in range(0,len(data_nombre[0])):
               nomb=data_nombre[0][name_index]
               if(name_index<2):
                  if(nomb!="" and nomb!="..."):
                     nombre=nombre+nomb+" "
               else:
                 if(nomb!="" and nomb!="..."):
                    apellido=apellido+nomb+" "
                   
           data_modif.append(["NOMBRES:",nombre])
           data_modif.append(["APELLIDOS:",apellido])
           data_modif.append(["CEDULA:",data_trabaj[0][0]])
           if(data_trabaj[0][2]!="" and data_trabaj[0][2]!="..."):
               data_modif.append(["CORREO:",data_trabaj[0][2]])
           if(data_trabaj[0][3]!="" and data_trabaj[0][3]!="..."):
               data_modif.append(["TELEFONO:",data_trabaj[0][3]])  
           conexion_bd.set_tabla(constantes.TABLA_USUARIO)
           data_user=conexion_bd.get_allData(constantes.CAMPOS_USUARIO,len(constantes.CAMPOS_USUARIO),[constantes.CLAVE_TRABAJADOR],[data_trabaj[0][0]],["and"])
           if(data_user!=[]):
               data_modif.append(["USUARIO ASIGNADO:",data_user[0][0]])
           conexion_bd.set_tabla(constantes.TABLA_CARGO)
           data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[data_trabaj[0][6]],["and"])
           if(data_cargo==[]):
                General.show_error("error en data del cargo","data de cargo invalida")
                return                     
           cargo=data_cargo[0][1].lower()
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
           data_modif.append(["CODIGO CARGO:",data_cargo[0][4]])
           data_modif.append(["CARGO:",cargo])
           data_modif.append(["CARGO MINIST:",data_cargo[0][2]])
           data_modif.append(["ESTATUS:",data_estatus[0][1]])
           data_modif.append(["AÑOS DE SERVICIO:",data_estatus[0][2]])
           data_modif.append(["FECHA DE INGRESO:",data_estatus[0][3]])
           conexion_bd.set_tabla(constantes.TABLA_HORARIO)
           data_hor=conexion_bd.get_allData(constantes.CAMPOS_HORARIO,len(constantes.CAMPOS_HORARIO),[constantes.CLAVE_HORARIO],[data_trabaj[0][5]],["and"])
           if(data_hor!=[]):
              data_modif.append(["TURNO:",data_hor[0][2]])
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           data_prof=conexion_bd.get_allData(constantes.CAMPOS_PROFESOR,len(constantes.CAMPOS_PROFESOR),[constantes.CLAVE_TRABAJADOR],[data_trabaj[0][0]],["and"])
           if(data_prof!=[]):
              data_modif.append(["DOCENTE:","Si"])
              if(data_prof[0][2]!="" and data_prof[0][2]!="..." and data_prof[0][2]!="default"):
                 data_modif.append(["SECCION GUIA:",data_prof[0][2]])
              conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
              data_areas=conexion_bd.get_allData(constantes.CAMPOS_AREA_DOCENTE,len(constantes.CAMPOS_AREA_DOCENTE),[constantes.CLAVE_PROFESOR],[data_prof[0][0]],["and"])
              if(data_areas!=[]):
                areas_profesor=""
                for i in range(0,len(data_areas)):
                    areas_profesor+=areas_profesor+data_areas[i][2]
                    if(i<len(data_areas)-1):
                      areas_profesor+=" , "      
                data_modif.append(["AREAS DICTADAS:",areas_profesor])
           else:
              data_modif.append(["DOCENTE:","No"])
                     
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           data_exp=conexion_bd.get_allData(constantes.CAMPOS_EXPEDIENTE,len(constantes.CAMPOS_EXPEDIENTE),[constantes.CLAVE_EXPEDIENTE],[data_trabaj[0][4]],["and"])
           if(data_exp==[]):
                data_modif.append(["FOTO:","not found"])
           else:
               if(data_exp[0][2]!="" and data_exp[0][2]!="..."):
                  data_modif.append(["FOTO:",constantes.SERVER+data_exp[0][2]]) 
               else:
                  data_modif.append(["FOTO:","not found"])  
           filename=tipo+" "+str(clave)+".xlsx"
           ruta=constantes.FOLDER_DOCUMENTS+filename
           documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"CEDULA:",0,data_modif,False],True)

       elif(tipo=="disp horario"):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
               General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
               return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            disp_data=conexion_bd.get_allData(constantes.CAMPOS_DISP_HORARIO,len(constantes.CAMPOS_DISP_HORARIO))
            if(disp_data==[]):
                General.show_message("no hay disponibilidad de horarios registradas","disponibilidad de horarios inexistentes")
                return
            data_nomina=[]
            num_trabaj=0
            for i in range(0,len(disp_data)):
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                id_trabaj=disp_data[i][1]
                name=""
                data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[id_trabaj],["and"])
                if(data_trabaj!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                    data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][7]],["AND"])
                    if(data_estatus[0][0]!="inactivo"):
                        num_trabaj+=1
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        data_nombre=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])
                        for j in range(0,4):
                            if(data_nombre[0][j]!="" and data_nombre[0][j]!="..."):
                                 name=name+data_nombre[0][j]+" "
                        disps=["","","","","",""]
                        for k in range(2,8):
                              if(disp_data[i][k].lower()=="no disponible"):
                                  disps[k-2]="NO DISP."
                              else:
                                 disps[k-2]=disp_data[i][k]
                        data_nomina.append([id_trabaj,name,disps[0], disps[1],disps[2],disps[3],disps[4],disps[5]])                              
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],1)
            if(data_cronog!=[]):
                data_replace.append(["periodo escolar:",data_cronog[0][0]])
            filename=tipo+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_trabaj,data_nomina,"Nº",8,data_replace,False],True)    
       elif(tipo=="materia pendiente"):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
                 General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
                 return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            mat_pend=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE))
            if(mat_pend==[]):
                General.show_message("no hay Materias Pendientes Registradas","Materias Pendientes inexistentes")            
                return
            data_nomina=[]
            num_materias=len(mat_pend)
            for i in range(0,len(mat_pend)):
                conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                id_estud=mat_pend[i][1]
                name=""
                data_estud=conexion_bd.get_allData([constantes.CLAVE_NOMBRE],1,[constantes.CLAVE_ESTUDIANTE],[id_estud],["and"])
                if(data_estud!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                    data_nombre=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][0]],["and"])
                    if(data_nombre!=[]):
                        for j in range(0,4):
                            if(data_nombre[0][j]!="" and data_nombre[0][j]!="..."):
                                name=name+data_nombre[0][j]+" "
                conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                data_intentos=conexion_bd.get_allData(constantes.CAMPOS_CALIF_PENDIENTE,len(constantes.CAMPOS_CALIF_PENDIENTE),[constantes.CLAVE_MATERIA_PENDIENTE],[mat_pend[i][0]],["and"])
                data_f=[]
                data_f.append(id_estud)
                data_f.append(name)
                data_f.append(mat_pend[i][3]+"-"+mat_pend[i][4]+" Año")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                data_f.append("ND")
                if(data_intentos!=[]):
                    for k in range(0,len(data_intentos)):
                        if(data_intentos[k][2]=="intento 1"):
                              data_f[3]=data_intentos[k][3]
                              data_f[4]=data_intentos[k][4]
                        elif(data_intentos[k][2]=="intento 2"):
                              data_f[5]=data_intentos[k][3]
                              data_f[6]=data_intentos[k][4]
                        elif(data_intentos[k][2]=="intento 3"):
                              data_f[7]=data_intentos[k][3]
                              data_f[8]=data_intentos[k][4]
                        elif(data_intentos[k][2]=="intento 4"):
                              data_f[9]=data_intentos[k][3]
                              data_f[10]=data_intentos[k][4]
                        elif(data_intentos[k][2]=="revision"):
                              data_f[11]=data_intentos[k][3]
                              data_f[12]=data_intentos[k][4]
                data_nomina.append(data_f)                                
            data_replace=[]
            data_replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],1)
            if(data_cronog!=[]):
                data_replace.append(["periodo escolar:",data_cronog[0][0]])
            filename=tipo+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_materias,data_nomina,"Nº",13,data_replace,False],True)
       elif(tipo=="constancias" or tipo=="constancia"):
              is_estud=False
              is_out=False
              cedula=""
              tipo=""
              if(pnl.id_panel==constantes.PANTALLA_DESCARGAR_CONSTANCIAS):
                trab=pnl.get_comp_byName("trabajador").get_selected_value()
                is_out=True
                tipo="constancia de prestacion de servicios"
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
                 if(pnl.id_panel==constantes.PANTALLA_CONSULTA_ESTUDIANTES):
                    is_estud=True
                    tipo="constancia de estudio"
                 else:
                    tipo="constancia de prestacion de servicios"
                 tabl=pnl.get_comp_byTag("table")
                 dat_tabla=tabl.get_row_selectedData()
                 if(dat_tabla==" "):
                      msg="por favor indique el"
                      msg_title=""
                      if(is_estud):
                         msg=msg+" estudiante"
                         msg_title="estudiante invalido"
                      else:
                         msg=msg+" trabajador"
                         msg_title="trabajador invalido" 
                      General.show_message(msg,msg_title)
                      return
                 cedula=str(dat_tabla[0])
                 if(dat_tabla[5]=="inactivo"):
                      General.show_message("no se puede generar constancia de un estudiante/trabajador inactivo","estudiasnte/trabajador invalido")
                      return  
                      
              conexion_bd.set_tabla(constantes.TABLA_FORMATO)
              data_form=conexion_bd.get_allData(["src_form"],1,[constantes.CLAVE_FORMATO],[tipo],["and"])
              raw_data=None
              if(data_form==[]):
                 General.show_message("formato de "+tipo+" no registrada","formato no registrado")
                 return
              url=constantes.SERVER+data_form[0][0]
              response=requests.get(url)
              if(response.status_code>400):
                   General.show_error("error obteniendo data del servidor","error de data del server")
                   return
              raw_data=response.content
              replace=[]
              nombre_directivo=""
              apellido_directivo=""
              cedula_directivo=""
              conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
              data_empleados=conexion_bd.get_allData(None,None)
              conexion_bd.set_tabla(constantes.TABLA_CARGO)
              found_dire=False
              if(data_form[0][0].endswith(".pdf")==True):
                  General.show_message("No se puede Escribir una Constancia en un formato PDF, Por Favor Registrar un Arch","Formato del Archivo Invalido") 
                  return
              #Get Directivo Id and Full Name
              for empl in data_empleados:
                 if(empl[0]!="000" and empl[0]!="001"):
                    #Prevent get the Default worker of Admin User
                    conexion_bd.set_tabla(constantes.TABLA_CARGO)
                    data_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[empl[6]],["and"])      
                    if(data_cargo[0][0].lower()=="director"):
                        found_dire=True
                        cedula_directivo=empl[0]
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        data_nomb=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[empl[1]],["and"])
                        for directive_name_index in range(0,4):
                            nomb_directivo=""
                            if(data_nomb[0][directive_name_index]!="" and data_nomb[0][directive_name_index]!="..."):
                               nomb_directivo=data_nomb[0][directive_name_index]
                            if(directive_name_index==0):
                               nombre_directivo=nomb_directivo.upper()                          
                            elif(directive_name_index==1):
                                apellido_directivo=nomb_directivo.upper()
                            elif(directive_name_index==2):
                                nombre_directivo=nombre_directivo+" "+nomb_directivo.upper()
                            else:
                                apellido_directivo=apellido_directivo+" "+nomb_directivo.upper()               
              if(found_dire==False):
                  General.show_message("no existe director rgistrado en el sistem","director inexistente")
                  return 
              replace.append(["     Quien suscribe Prof(a),",apellido_directivo+" "+nombre_directivo,12,"bold"])
              replace.append(["Directivo",apellido_directivo+" "+nombre_directivo,12,"bold"])
              replace.append(["identidad ,",cedula_directivo,12,"bold"])
              replace.append(["CI dire",cedula_directivo,12,"bold"])                
              fech=time_object.get_fecha().split("/")
              dia=fech[0]
              mes=fech[1]
              mes=time_object.get_mes(int(mes))
              año=fech[2]                           
              if(is_estud):
                   #Constancia for Students
                   conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)              
                   data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
                   if(data_estud==[]):
                        General.show_message("la cedula indicada no pertenece a ningun estudiante","estudiante no valido")
                        return
                   else:
                       conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                       data_estatus=conexion_bd.get_allData(["estatus","last_year"],2,[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][2]],["and"])
                       if(data_estatus[0][0]=="inactivo" or data_estatus[0][0]=="graduado"):
                           General.show_message("el estudiante no es un estudiante activo","estudiante no valido")
                           return
                   conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                   data_nombre=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][1]],["and"])                   
                   nombr=""
                   nombre_estud=""
                   apellido_estud=""
                   for i in range(0,4):
                       nomb=""
                       if(data_nombre[0][i]!="" and data_nombre[0][i]!="..."):
                              nomb=data_nombre[0][i]
                       if(i==0):
                          nombre_estud=nomb.upper()
                       elif(i==1):
                          apellido_estud=nomb.upper()
                       elif(i==2):
                          nombre_estud=nombre_estud+" "+nomb.upper()
                       elif(i==3):
                         apellido_estud=apellido_estud+" "+nomb.upper()
                   
                   replace.append(["el(la) estudiante :",apellido_estud+" "+nombre_estud,12,"bold"])
                   if(tipo=="constancia de estudio"):
                         año_escolar=""
                         conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA) 
                         data_cronog=conexion_bd.get_allData(None,None)
                         if(data_cronog!=[]):
                            año_escolar=data_cronog[0][0]
                         replace.append(["del Año Escolar:",año_escolar,12,"bold"])
                         replace.append(["Año Escolar:",año_escolar,12,"bold"])
                         replace.append(["escolar:",cedula,12,"bold"])
                         curso=data_estatus[0][1]
                         if(curso=="1"):
                            curso="Primer"
                         elif(curso=="2"):
                            curso="Segundo"
                         elif(curso=="3"):
                            curso="Tercer"
                         elif(curso=="4"):
                            curso="Cuarto"
                         else:
                            curso="Quinto"
                         replace.append(["cursa estudios en nuestra institucion en el:",curso+" Año ",12,"bold"])     
              else:
                   #Constancia for Workers
                   conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)              
                   data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[cedula],["and"])
                   if(data_trabaj==[]):
                        General.show_message("la cedula indicada no pertenece a ningun miembro del personal","trabajdor no valido")
                        return
                   else:
                       conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                       data_estatus=conexion_bd.get_allData(["estatus","fecha_ingreso"],2,[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][7]],["and"])
                       if(data_estatus[0][0]=="inactivo"):
                           General.show_message("el miembro del personal no esta activo","trabajador no valido")
                           return
                   conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                   data_nombre=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])                   
                   nombre_t=""
                   apellido_t=""
                   nombr=""
                   for i in range(0,4):
                       nomb=""
                       if(data_nombre[0][i]!="" and data_nombre[0][i]!="..."):
                              nomb=data_nombre[0][i]
                       if(i==0):
                          nombre_t=nomb.upper()
                       elif(i==1):
                          apellido_t=nomb.upper()
                       elif(i==2):
                          nombre_t=nombre_t+" "+nomb.upper()
                       elif(i==3):
                          apellido_t=apellido_t+" "+nomb.upper()
                   replace.append(["el(la) ciudadano(a) :",apellido_t+" "+nombre_t,12,"bold"])
                   if(tipo=="constancia de trabajo" or tipo=="constancia de prestacion de servicios"):
                         temp_ingreso=data_estatus[0][1].split("/")
                         ingreso=""
                         for ing in range(0,len(temp_ingreso)):
                            valor_ingreso=temp_ingreso[ing]
                            if(len(valor_ingreso)<2):
                               valor_ingreso="0"+valor_ingreso
                            ingreso=ingreso+valor_ingreso
                            if(ing<2):
                               ingreso=ingreso+"/"
                         
                         replace.append(["desde el:",ingreso,12,"bold"])
                         conexion_bd.set_tabla(constantes.TABLA_CARGO)
                         data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[data_trabaj[0][6]],["and"])
                         cargo=""
                         cargo_minist=""
                         codigo_cargo=""
                         if(data_cargo!=[]):
                            cargo=data_cargo[0][1].upper()
                            codigo_cargo=data_cargo[0][4].upper()
                            cargo_minist=data_cargo[0][2].upper()
                        
                         cargo1=""
                         cargo2=""
                         if(cargo.lower().startswith("profesor") or cargo.lower().startswith("docente")):
                            cargo1="DOCENTE"
                            if(cargo.lower().endswith("aula")):
                                cargo2="/AULA"
                         else:
                            if(cargo.lower()=="director"):
                                cargo1="DIRECTOR(A)"
                            elif(cargo.lower().startswith("sub director") or cargo.lower().startswith("subdirector")):
                                cargo1="SUB DIRECTOR(A)"
                                if(cargo.endswith("academico")):
                                    cargo1=cargo1+" ACADEMICO"
                                else:
                                    cargo1=cargo1+" ADMINISTRATIVO"
                            elif(cargo.lower().startswith("coordinador")):
                                cargo1="COORDINADOR(A)"
                                if(cargo.endswith("evaluacion")):
                                    cargo1=cargo1+" DE EVALUACION"
                                else:
                                    cargo1=cargo1+" DE ORIENTACION"    
                                cargo1=cargo.upper()
                         cargof=cargo1
                         if(cargo2!=""):
                             cargof=cargof+"/"+cargo2
                         replace.append(["se desempeña como:",cargof,12,"bold"])
                         replace.append(["code",codigo_cargo,12,"bold"])
                         replace.append([" de la CI:",cedula,12,"bold"])                        
                         if(is_out==True):
                             #Document Request is not from a User
                             conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                             data_descarga=[conexion_bd.generate_id(True,constantes.CLAVE_DESCARGA_DOCUMENTO), data_trabaj[0][0],tipo,time_object.get_fecha(),time_object.get_tiempo(),"constancia",time_object.get_fecha()]
                             conexion_bd.add_data(data_descarga)
              new_date=dia+" de "+mes+" del "+año
              replace.append(["Aguas Calientes,",new_date,12,"bold"])
              replace.append(["a los",new_date,12,"bold"])
              ruta=constantes.FOLDER_DOCUMENTS+tipo+"-"+cedula+".xlsx"              
              documento.request(raiz,[ruta,raw_data],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"UNIDAD EDUCATIVA 28 DE OCTUBRE",0,replace,False],True)         
       elif(tipo=="sabana de notas" or tipo=="notas finales del año"):
           if(receive_data==None):
               General.show_error("sin data para reporte","sin data")           
               return
           conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
           data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
           if(data_formato==[]):
                General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
                return
           src=data_formato[0][0]
           url=constantes.SERVER+src
           response=requests.get(url)
           if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
           data_form=response.content 
           info=receive_data[0]
           replace=[]
           for i in range(0,len(receive_data[1])):
                replace.append(["Area N"+str(i+1),receive_data[1][i]])
           replace.append(["Seccion:",receive_data[2]])
           replace.append(["Año:",receive_data[3]+" AÑO"])
           replace.append(["Fecha:",time_object.get_fecha()])
           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
           data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],1)
           if(data_cronog!=[]):
                replace.append(["periodo escolar:",data_cronog[0][0]])
           col_count=len(info[0])
           filename=tipo+" "+receive_data[2]+".xlsx"
           ruta=constantes.FOLDER_DOCUMENTS+filename  
           num_rows=len(info)              
           documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)
       elif(tipo=="notas finales"):
            from estudiante import estudiante
            estud=estudiante()
            ced=pnl.get_comp_byName("identificador").get_text()
            res=estud.get_calif_certific(ced)
            if(res==-1):
                General.show_message("cedula del estudiante inexistente","cedula invalida")
                return
            elif(res==-2):
                General.show_message("estudiante sin calificaciones","calificaciones no registradas")
                return
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
                General.show_error("formato de reporte de notas finales no registrado","formato no registrado")
                return               
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content 
            replace=[]
            replace.append(["Estudiante:",res[0][1]])
            replace.append(["Fecha:",time_object.get_fecha()])
            replace.append(["Cedula:",res[0][0]])
            col_count=2
            num_rows=10
            data_send=[]
            for i in range(1,len(res)):
                data_send.append(res[i])   
            if(data_send==[]):
                General.show_error("sin datos para reporte","datos inexistentes")
                return
            filename="notas finales-"+res[0][0]+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_NOTAS_CERTIFICADAS,[num_rows,data_send,["1 AÑO","2 AÑO","3 AÑO","4 AÑO","5 AÑO"],col_count,replace,False],True)
       elif(tipo=="reporte de usuarios"):
           
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
               General.show_error("error no hay formato el reporte de "+tipo,"formato de reporte de usuarios inexistente")
               return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content  
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            data_reporte=conexion_bd.get_allData(None,None)
            info=[]
            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
            for i in range(0,len(data_reporte)):
                data_user=conexion_bd.get_allData([constantes.CLAVE_TRABAJADOR],1,[constantes.CLAVE_USUARIO],[data_reporte[i][1]],["and"])
                    
                data_row=[]
                if(data_user!=[]):
                    if(data_user[0][0]!="000" and  data_user[0][0]!="001"):
                        #prevent append Work id of Default User of Admin User
                        data_row.append(data_user[0][0])
                    else:
                        data_row.append("")

                data_row.append(data_reporte[i][1])
                data_row.append(data_reporte[i][5])
                data_row.append(data_reporte[i][2])
                data_row.append(data_reporte[i][3])
                data_row.append(data_reporte[i][6])
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
  
       elif(tipo=="reporte de descargas"):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
               General.show_error("error no hay formato el reporte de "+tipo,"formato de reporte de descargas inexistente")
               return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content  
            conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
            data_reporte=conexion_bd.get_allData(None,None)
            info=[]
            for i in range(0,len(data_reporte)):
                data_row=[]
                data_row.append(data_reporte[i][1])
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                data_t=conexion_bd.get_allData([constantes.CLAVE_NOMBRE],1,[constantes.CLAVE_TRABAJADOR],[data_reporte[i][1]],["and"])
                nombre=""
                if(data_t!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                    data_n=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_t[0][0]],["and"])
                    if(data_n!=[]):
                        for j in range(0,4):
                            if(data_n[0][j]!="" and data_n[0][j]!="..."):
                                nombre=nombre+data_n[0][j]+" "
                data_row.append(nombre)       
                data_row.append(data_reporte[i][2])
                data_row.append(data_reporte[i][3])
                data_row.append(data_reporte[i][4])
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
   
       elif(tipo=="notas del momento"):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and","and"])
            if(data_formato==[]):
                General.show_error("error no hay formato el reporte de "+tipo,"formato de nomina inexistente")
                return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content 
            cedula=pnl.get_comp_byName("cedula_p1").get_text()
            if(cedula=="" or cedula==" "):
                General.show_message("por favor indique el estudiante ","estudiante no identificado")
                return
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            data_estud=conexion_bd.get_allData([constantes.CLAVE_NOMBRE],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
            data_nomb=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][0]],["and"])
            fullname="" 
            for dn in data_nomb[0]:
                if(dn!="" and dn!="..."):
                      fullname=fullname+dn+" "                     
            year=pnl.get_comp_byName("year").get_text()  
            momento=pnl.get_comp_byName("mom_p1").get_selected_value()
            if(momento=="elejir" or momento=="elegir"):
                General.show_message("por favor indique el momento academico ","momento invalido")
                return
            areas=[]
            conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
            temp_areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_AÑOS_INCORPORADOS],2,["incorporada"],["Si"],["and"])
            conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
            for t_area in temp_areas:
                    field_y=year+"_año"
                    data_y=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],1,[constantes.CLAVE_AÑOS_INCORPORADOS,field_y],[t_area[1],"True"],["and","and"])               
                    if(data_y!=[]):
                         areas.append(t_area[0])
            orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","fsn","ov","gcrp"]     
            data_areas=[]
            for temp_orden in orden:
                for i in range(0,len(areas)):
                    if(areas[i].lower()== temp_orden):
                            data_areas.append(areas[i])
            info=[]             
            for dat_areas in data_areas:   
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                data_calif=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],1,[constantes.CLAVE_ESTUDIANTE,"año",constantes.CLAVE_AREA_FORMACION],[cedula,year,dat_areas],["and","and","and"])
                conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                if(data_calif!=[]):
                    data_calific_moms=conexion_bd.get_allData([constantes.CLAVE_CALIF_MOM,"definitiva"],2,[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[data_calif[0][0],momento],["and","and"])
                    if(data_calific_moms!=[]):
                        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
                        data_calific=conexion_bd.get_allData(["valor","numero"],2,[constantes.CLAVE_CALIF_MOM],[data_calific_moms[0][0]],["and"])
                        new_data=[dat_areas]
                        for evaluation_index in range(0,constantes.MAXIMO_EVALUACIONES):
                             new_data.append("evaluacion "+str(evaluation_index+1)) 
                           
                        for j in range(1,len(new_data)):
                            old_val=new_data[j]
                            for k in range(0,len(data_calific)):
                                if(data_calific[k][1]==new_data[j]):
                                     new_data[j]=data_calific[k][0]
                            if(old_val==new_data[j]):
                                new_data[j]=""
                        new_data.append(data_calific_moms[0][1])
                        info.append(new_data)
                    else:
                        new_data=[dat_areas]
                        for evaluation_index in range(0,constantes.MAXIMO_EVALUACIONES):
                            new_data.append("") 
                        new_data.append("05")
                        info.append(new_data)   
                else:
                    new_data=[dat_areas]
                    for evaluation_index in range(0,constantes.MAXIMO_EVALUACIONES):
                        new_data.append("") 
                    new_data.append("05")
                    info.append(new_data)                    
            replace=[]
            replace.append(["Nombres y apellidos:",fullname])
            replace.append(["Cedula:",cedula])
            replace.append(["Momento:",momento])
            replace.append(["Año:",year+" año"])
            replace.append(["Fecha:",time_object.get_fecha()])
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA],1)
            if(data_cronog!=[]):
               replace.append(["periodo escolar:",data_cronog[0][0]])
            col_count=len(info[0])
            filename="reporte de calificaciones-"+momento+".xlsx"
            ruta=constantes.FOLDER_DOCUMENTS+filename  
            num_rows=len(info)              
            documento.request(raiz,[ruta,data_form],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[num_rows,info,"Nº",col_count,replace,False],True)

       elif(tipo=="carnet"):
            
            pnl=pnl
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and"])
            if(data_formato==[]):
                General.show_message("por favor registre un formato de carnet","formato de carnet no registrado")
                return 
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
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
                if(pnl.id_panel==constantes.PANTALLA_CONSULTA_ESTUDIANTES):
                    is_estud=True
                tabl=pnl.get_comp_byTag("table")
                dat_tabla=tabl.get_row_selectedData()
                if(dat_tabla==" "):
                    msg="por favor indique el"
                    msg_title=""
                    if(is_estud):
                         msg=msg+" estudiante"
                         msg_title="estudiante invalido"
                    else:
                         msg=msg+" trabajador"
                         msg_title="trabajador invalido" 
                    General.show_message(msg,msg_title)
                    return
                cedula=str(dat_tabla[0])
                if(dat_tabla[5]=="inactivo"):
                    General.show_message("no se puede generar carnet de un estudiante/trabajador inactivo","estudiasnte/trabajador invalido")
                    return                  
            raw_data=response.content
            replace=[]
            nombre_directivo=""
            cedula_directivo=""
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            data_empleados=conexion_bd.get_allData(None,None)
            conexion_bd.set_tabla(constantes.TABLA_CARGO)
            nomb_directivo=""
            found_directivo=False
            for empl in data_empleados:
                if(empl[0]!="000" and empl[0]!="001"):
                    #Prevent get data form Default Worker of Admin User
                    conexion_bd.set_tabla(constantes.TABLA_CARGO)
                    data_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[empl[6]],["and"])
                    if(data_cargo[0][0].lower()=="director"):
                        cedula_directivo=empl[0]
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        data_nomb=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[empl[1]],["and"])
                        found_directivo=True
                        for directive_name_index in range(0,4):
                            nomb_d=""
                            if(data_nomb[0][directive_name_index]!="" and data_nomb[0][directive_name_index]!="..."):
                                nomb_d=data_nomb[0][directive_name_index]
                            if(directive_name_index==0):
                                nomb_directivo=nomb_directivo+nomb_d.upper()+" "
                            elif(directive_name_index==1):
                                nomb_directivo=nomb_directivo+nomb_d.upper()+" "
                            elif(directive_name_index==2):
                                nomb_directivo=nomb_directivo+nomb_d.upper()+" "
                            else:
                                nomb_directivo=nomb_directivo+nomb_d.upper()+" " 
            if(found_directivo==False):
                General.show_message("no existe director rgistrado en el sistem","director inexistente")
                return 
            replace.append(["DIRECTOR",nomb_directivo])              
            replace.append(["CEDULA_DIRE",cedula_directivo,12,"bold"])
            fech=time_object.get_fecha()
            vencimiento=time_object.get_next_date4(fech,1)
            replace.append(["fecha_v",vencimiento,12,"bold"])
            if(is_estud==False): 
                #Worker Carnet  
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)              
                data_trabaj=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),[constantes.CLAVE_TRABAJADOR],[cedula],["and"])
                if(data_trabaj==[]):
                    General.show_message("la cedula indicada no pertenece a ningun miembro del personal","trabajdor no valido")
                    return
                else:
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                    data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][7]],["and"])
                    if(data_estatus[0][0]=="inactivo"):
                        General.show_message("el miembro del personal no esta activo","trabajador no valido")
                        return
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                data_nombre=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])                   
                nombr=""
                nomb_trabaj=""
                for i in range(0,4):
                    nomb=""
                    if(data_nombre[0][i]!="" and data_nombre[0][i]!="..."):
                        nomb=data_nombre[0][i]
                    if(i==0):
                        nomb_trabaj=nomb_trabaj+nomb.upper()+" "
                    elif(i==1):
                        nomb_trabaj=nomb_trabaj+nomb.upper()+" "
                    elif(i==2):
                        nomb_trabaj=nomb_trabaj+nomb.upper()+" "
                    elif(i==3):
                        nomb_trabaj=nomb_trabaj+nomb.upper()+" "
                replace.append(["NOMBRES_C",nomb_trabaj])
                replace.append(["CEDULA_C",cedula])
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                data_exp=conexion_bd.get_allData(["src_foto"],1,[constantes.CLAVE_EXPEDIENTE],[data_trabaj[0][4]],["and"])
                foto_existe=False
                if(data_exp!=[]):
                    if(data_exp[0][0]!="" and data_exp[0][0]!="..."):
                        foto_existe=True  
                if(foto_existe==False):
                        General.show_message("no se puede emitir carnet de un trabajador sin foto","foto no registrada")
                        return
                url_foto=constantes.SERVER+data_exp[0][0]
                replace.append(["FOTO:",url_foto])
                conexion_bd.set_tabla(constantes.TABLA_CARGO)
                data_cargo=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),[constantes.CLAVE_CARGO],[data_trabaj[0][6]],["and"])
                cargo=""
                if(data_cargo!=[]):
                   cargo=data_cargo[0][1]
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
                    data_descarga=[conexion_bd.generate_id(True,constantes.CLAVE_DESCARGA_DOCUMENTO), data_trabaj[0][0],tipo,time_object.get_fecha(),time_object.get_tiempo(),"carnet",time_object.get_fecha()]
                    conexion_bd.add_data(data_descarga)   
                ruta=constantes.FOLDER_DOCUMENTS+tipo+"-"+cedula+".xlsx"
                documento.request(raiz,[ruta,raw_data],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"UNIDAD EDUCATIVA 28 DE OCTUBRE",0,replace,False],True)
                
            else: 
                #Student Carnet
                conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)              
                data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
                if(data_estud==[]):
                    General.show_message("la cedula indicada no pertenece a ningun estudiante","estudiante no valido")
                    return
                else:
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                    data_estatus=conexion_bd.get_allData(["estatus","last_year"],2,[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][2]],["and"])
                    if(data_estatus[0][0]=="inactivo" or data_estatus[0][0]=="graduado"):
                        General.show_message("el estudiante no es un estudiante activo","estudiante no valido")
                        return
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                data_nombre=conexion_bd.get_allData(["apellido","s_apellido","nombre","s_nombre"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][1]],["and"])                   
                nombr=""
                nombre_estud=""
                for i in range(0,4):
                    nomb=""
                    if(data_nombre[0][i]!="" and data_nombre[0][i]!="..."):
                        nomb=data_nombre[0][i]
                    if(i==0):
                        nombre_estud=nombre_estud+data_nombre[0][i].upper()+" "
                    elif(i==1):
                        nombre_estud=nombre_estud+data_nombre[0][i].upper()+" "
                    elif(i==2):
                       nombre_estud=nombre_estud+data_nombre[0][i].upper()+" "
                    elif(i==3):
                       nombre_estud=nombre_estud+data_nombre[0][i].upper()+" "
                       replace.append(["CEDULA_C",cedula])   
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                data_exp=conexion_bd.get_allData(["src_foto"],1,[constantes.CLAVE_EXPEDIENTE],[data_estud[0][4]],["and"])
                foto_existe=False
                if(data_exp!=[]):
                    if(data_exp[0][0]!="" and data_exp[0][0]!="..."):
                        foto_existe=True
                          
                if(foto_existe==False):
                    General.show_message("no se puede emitir carnet de un estudiante sin foto","foto no registrada")
                    return
                url_foto=constantes.SERVER+data_exp[0][0]      
                replace.append(["FOTO:",url_foto])
                replace.append(["NOMBRES_C",nombre_estud])      
                curso=data_estatus[0][1]
                if(curso=="1"):
                    curso="Primer Año"
                elif(curso=="2"):
                    curso="Segundo Año"
                elif(curso=="3"):
                    curso="Tercer Año"
                elif(curso=="4"):
                    curso="Cuarto Año"
                else:
                    curso="Quinto Año"
                replace.append(["CARGO_C","ESTUDIANTE",12,"bold"])    
                replace.append(["fecha_e",fech,12,""])
                ruta=constantes.FOLDER_DOCUMENTS+tipo+"-"+cedula+".xlsx"
                documento.request(raiz,[ruta,raw_data],constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT,[0,[],"UNIDAD EDUCATIVA 28 DE OCTUBRE",0,replace,False],True)
                   
       elif(tipo=="cronograma"):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO) 
            data_formato=conexion_bd.get_allData(["src_form"],1,["tipo"],[tipo],["and"])
            if(data_formato==[]):
                General.show_error("sin formatos de cronograma ","formato de cronograma no registrado")
                return
            src=data_formato[0][0]
            url=constantes.SERVER+src
            response=requests.get(url)
            if(response.status_code>400):
                General.show_error("error obteniendo data del servidor","error de data del server")
                return
            data_form=response.content 
            conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
            data_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA))
            data_replace=[[],[],[]]
            data_content=[[],[],[]]
            data_replace[0].append(["NN","",12,"bold"])
            data_replace[1].append(["NN","",12,"bold"])
            data_replace[2].append(["NN","",12,"bold"])
            data_replace[0].append(["Año Escolar:",data_cronog[0][0],12,"bold"])
            data_replace[1].append(["Año Escolar:",data_cronog[0][0],12,"bold"])
            data_replace[2].append(["Año Escolar:",data_cronog[0][0],12,"bold"])
            data_replace[0].append(["año_e",data_cronog[0][1],12,"bold"])
            data_replace[0].append(["cierre_e",data_cronog[0][2],12,"bold"])
            moms=["False","False","False"]
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            pages=[]
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            data_moms=conexion_bd.get_allData(None,None)
            if(data_moms==[]):
                General.show_error("error no hay momento registrados","error de cronograma")
                return    
            conexion_bd.set_tabla(constantes.TABLA_FECHA)
            orden_mom1=[["I CONSEJO GENERAL DOCENTES","consejo de docentes"],
            ["REUNION DE REPRESANTES","reunion de representantes"],
            ["ENTREGA DE PLANIFICACION A SUBDIRECCION ACADEMICA","entrega de planificaciones a subdireccion academica"],
            ["EVALUACION CONTINUA(ARTICULO 44LOE) DE LASAREAS DE FORMACION EN FUNCION DE LOS TEMAS GENERADORESY REFERENTES TEORICO PRACTIVOS DE CADA AREA","evaluacion continua"],
            ["EVALUACION I MOMENTO MATERIA PENDIENTE","materia pendiente 1"],
            ["SEMANA ANIVERSARIO 28 DE OCTUBRE","semana aniversario"],
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
            for i in range(0,3):
                if(i<len(data_moms)):
                    if(data_moms[i][0]=="momento 1"):
                        periodo=""
                        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                        data_periodo=conexion_bd.get_allData(["fecha_inicio","fecha_limite"],2,[constantes.CLAVE_MOMENTO],[data_moms[i][0]],["and"])
                        if(data_periodo!=[]):
                            periodo= data_periodo[0][0]+"-"+ data_periodo[0][1] 
                        conexion_bd.set_tabla(constantes.TABLA_FECHA)                       
                        for j in range(0,len(orden_mom1)):
                            if(j==4 or j==7):
                                #materias pendientes
                                data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom1[j][1],data_moms[i][0],data_cronog[0][0]],["and","and","and"])
                                if(data_fecha!=[] and orden_mom1[j][1]!=""):
                                    fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                    data_content[0].append([fecha])
                                else:
                                    data_content[0].append([""])
                                   
                            else:
                                data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom1[j][1],data_moms[i][0],data_cronog[0][0]],["and","and","and"])
                                if(data_fecha!=[]):
                                    fecha=""
                                    if(data_fecha[0][0]==data_fecha[0][1]):
                                       fecha=data_fecha[0][0]
                                       data_content[0].append([fecha]) 
                                    else:
                                       fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                       data_content[0].append([fecha])
                        moms[0]="True"
                        data_replace[0].append(["xperiodox",periodo,14,""])
                    elif(data_moms[i][0]=="momento 2"):
                        periodo=""
                        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                        data_periodo=conexion_bd.get_allData(["fecha_inicio","fecha_limite"],2,[constantes.CLAVE_MOMENTO],[data_moms[i][0]],["and"])
                        if(data_periodo!=[]):
                            periodo= data_periodo[0][0]+"-"+ data_periodo[0][1] 
                        conexion_bd.set_tabla(constantes.TABLA_FECHA)                       
                        for j in range(0,len(orden_mom2)):
                            if(j==3):
                                #materias pendientes
                                data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom2[j][1],"momento 1",data_cronog[0][0]],["and","and","and"])
                                if(data_fecha!=[] and orden_mom1[j][1]!=""):
                                    fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                    data_content[1].append([fecha])
                                else:
                                    data_content[1].append([""]) 
                            else:
                                data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom2[j][1],data_moms[i][0],data_cronog[0][0]],["and","and","and"])
                                if(data_fecha!=[]):
                                    fecha=""
                                    if(data_fecha[0][0]==data_fecha[0][1]):
                                       fecha=data_fecha[0][0]
                                       data_content[1].append([fecha]) 
                                    else:
                                       fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                       data_content[1].append([fecha])
                        moms[1]="True"
                        data_replace[1].append(["xperiodox",periodo,14,""])
                    elif(data_moms[i][0]=="momento 3"):
                        periodo=""
                        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                        data_periodo=conexion_bd.get_allData(["fecha_inicio","fecha_limite"],2,[constantes.CLAVE_MOMENTO],[data_moms[i][0]],["and"])
                        if(data_periodo!=[]):
                            periodo= data_periodo[0][0]+"-"+ data_periodo[0][1] 
                        conexion_bd.set_tabla(constantes.TABLA_FECHA)                       
                        for j in range(0,len(orden_mom3)):
                               if(j==3 or j==8):
                                 #materias pendientes
                                 data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom3[j][1],"momento 1",data_cronog[0][0]],["and","and","and"])
                                 if(data_fecha!=[] and orden_mom1[j][1]!=""):
                                   
                                    fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                    data_content[2].append([fecha])
                                 else:
                                    data_content[2].append([""])  
                               else:
                                  data_fecha=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO,constantes.CLAVE_CRONOGRAMA],[orden_mom3[j][1],data_moms[i][0],data_cronog[0][0]],["and","and","and"])
                                  if(data_fecha!=[]):
                                    fecha=""
                                    if(data_fecha[0][0]==data_fecha[0][1]):
                                       fecha=data_fecha[0][0]
                                       data_content[2].append([fecha]) 
                                    else:
                                       fecha=data_fecha[0][0]+" AL "+data_fecha[0][1]
                                       data_content[2].append([fecha])         
                        moms[2]="True"
                        data_replace[2].append(["xperiodox",periodo,14,""])
            for moment in range(0,3):
                if(moms[moment]!="True"):
                    if(moment==0):
                        data_replace[0].append(["xperiodox","",14,""])
                    elif(moment==1):
                         data_replace[1].append(["xperiodox","",14,""])  
                    else:
                        data_replace[2].append(["xperiodox","",14,""])    
            counts_rows[0]=len(data_content[0])
            counts_rows[1]=len(data_content[1])
            counts_rows[2]=len(data_content[2])
            ruta=constantes.FOLDER_DOCUMENTS+tipo+data_cronog[0][0]+".xlsx"
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
            id_exp=""
            if(tipo==cls.DOCUMENT_EXPEDENT_STUDENT):
               #Student Expedent
               conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
               id_exp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[str(id_selected[0])],["and"])[0][0]
            else:
               #Worker Expedent
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               id_exp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_TRABAJADOR],[str(id_selected[0])],["and"])[0][0]
            if(id_exp==""):
                if(tipo==cls.DOCUMENT_EXPEDENT_STUDENT):
                   General.show_message("por favor seleccione un estudiante","estudiante no seleccionado")
                else:
                   General.show_message("por favor seleccione un trabajador","trabjador no seleccionado")
                return
            conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
            data_exp=conexion_bd.get_allData(["src_exp"],1,[constantes.CLAVE_EXPEDIENTE],[id_exp],["and"])
            if(data_exp==[]):
                General.show_error("error de registro de expediente","expediente no registrado")
                return
            url=constantes.SERVER+data_exp[0][0]
            if(data_exp[0][0]=="..." or data_exp[0][0]==""):
                General.show_message("aun no se ha subido los archivos del expediente al servidor","expediente sin data")
                return
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
            if(id_selected==" "):
              if(tipo==cls.DOCUMENT_TIMETABLES_SECTION):
                General.show_message("por favor seleccione una seccion","seccion no seleccionado")
              else:
                General.show_message("por favor seleccione un trabajador","trabjador no seleccionado")
              return
            id_hor=""
            if(tipo==cls.DOCUMENT_TIMETABLES_SECTION):
                #Timetables for Sections
                conexion_bd.set_tabla(constantes.TABLA_SECCION)
                id_hor=conexion_bd.get_allData([constantes.CLAVE_HORARIO],1,[constantes.CLAVE_SECCION],[str(id_selected[0])],["and"])[0][0]
            else:
                 #Timetables for Workers
                 conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                 id_hor=conexion_bd.get_allData([constantes.CLAVE_HORARIO],1,[constantes.CLAVE_TRABAJADOR],[str(id_selected[0])],["and"])[0][0]
            if(id_hor=="default"):
                if(tipo==cls.DOCUMENT_TIMETABLES_SECTION):
                    General.show_message("la seccion no tiene horario asignado","seccion sin horario")
                else:
                    General.show_message("el trabajador no tiene horario asignado","trabjadorsin horario")
                return
            conexion_bd.set_tabla(constantes.TABLA_HORARIO)
            data_hor=conexion_bd.get_allData(["src_hor"],1,[constantes.CLAVE_HORARIO],[id_hor],["and"])
            if(data_hor==[]):
                 General.show_error("error de registro de expediente","expediente no registrado")
                 return
            url=constantes.SERVER+data_hor[0][0]
            if(data_hor[0][0]=="..." or data_hor[0][0]==""):
                General.show_message("aun no se ha subido los archivos del expediente al servidor","expediente sin data")
                return
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
        filter_list=[None,None,None]
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
            if(selected=="cedula"):
               if(opcion==cls.CONSULT_WORKERS):
                  selected=constantes.CLAVE_TRABAJADOR
               elif(opcion==cls.CONSULT_STUDENTS):
                  selected=constantes.CLAVE_ESTUDIANTE
            elif(selected=="CI trabajador"):
                selected=constantes.CLAVE_TRABAJADOR
            elif(selected=="CI estudiante" or selected=="CI estud."):
                 selected=constantes.CLAVE_ESTUDIANTE
            elif(selected=="seccion"):
                 selected=constantes.CLAVE_SECCION
            elif(selected=="dir_digital"):
                 selected="src_hor"
            elif(selected=="representante"):
                 selected=constantes.CLAVE_REPRESENTANTE
            elif(selected=="num_momento" or selected=="momento"):
                 selected=constantes.CLAVE_MOMENTO
                 if(len(filtro_val)==1):
                     filtro_val="momento "+filtro_val
            elif(selected=="lunes"):
                 selected="disp_lunes"
            elif(selected=="martes"):
                 selected="disp_martes"
            elif(selected=="miercoles"):
                selected="disp_miercoles"
            elif(selected=="jueves"):
                selected="disp_jueves"
            elif(selected=="viernes"):
               selected="disp_viernes"
            elif(selected=="planif. al dia"):
                selected="planific_dia"
            elif(selected.endswith("año") and opcion==cls.CONSULT_FORMATION_AREAS):
                 temp_sel=selected.split(" ")
                 selected=temp_sel[0]+"_"+"año"
            elif(selected=="CI Personal"):
                 selected=constantes.CLAVE_TRABAJADOR
            elif(selected=="nombre_area" or selected=="area formacion" or selected=="area form." ):
                 selected=constantes.CLAVE_AREA_FORMACION
            elif(selected=="docente"):
                 selected=constantes.CLAVE_PROFESOR
            elif(selected=="seccion"):
                 selected=constantes.CLAVE_SECCION
            elif(selected=="planific_al_dia"):
                 selected="planif_dia"
            elif(selected=="CI_emisor" or selected=="CI usuario"):
                selected=constantes.CLAVE_TRABAJADOR
            elif(selected=="codigo reporte"):
                selected=constantes.CLAVE_REPORTE            
            elif(selected=="CI_Docente"):
                selected=constantes.CLAVE_TRABAJADOR
            elif(selected=="CI_coordinador"):
               selected="secc_guia"
            elif(selected =="CI_coordinador"):
               selected="CI_coord"
            elif(selected=="area_formacion"):
               selected=constantes.CLAVE_AREA_FORMACION
            elif(selected=="prof guia"):
               selected="prof_guia"
            elif(selected=="momento"):
               selected="id_mom"
            elif(selected=="numero de estudiantes"):
               selected="total_estud"
            elif(selected=="calificacion"):
                 selected="definitiva"
            elif(selected=="año escolar"):
                 selected="año_escolar"
            elif(selected=="fecha de cierre"):
                 selected="fecha_cierre"
            elif(selected=="codigo horario"):
                 selected=constantes.CLAVE_HORARIO
            elif(selected=="num horas"):
                 selected="num_horas"
            elif(selected=="destinatario"):
                if(selected_radio=="seccion"):
                   selected=constantes.CLAVE_SECCION
                else:
                   selected=constantes.CLAVE_TRABAJADOR    
            filter_list=[[selected],[filtro_val],["and"]]
            #filtros de radio buttons adicionales
            if(selected_radio=="cedulado"):
               filter_list[0].append(selected_radio)
               filter_list[1].append("True")
               filter_list[2].append("and")
            elif(selected_radio=="no cedulado"):
               filter_list[0].append("cedulado")
               filter_list[1].append("False")
               filter_list[2].append("and")
            elif(selected_radio=="incorporada"):
               filter_list[0].append("incorporada")
               filter_list[1].append("Si")
               filter_list[2].append("and")
            elif(selected_radio=="no incorporada"): 
               filter_list[0].append("incorporada")
               filter_list[1].append("No")
               filter_list[2].append("and")  
            elif(selected_radio=="docente" or selected_radio=="docente" or selected_radio=="seccion"):
                filter_list[0].append("tipo")
                filter_list[1].append(selected_radio)
                filter_list[2].append("and")              
        else:
            #No filters from ComboBox and TextField
            #Verify Radio Buttons Filter
            if(selected_radio=="cedulado"):
                filter_list=[["cedulado"],["True"],["and"]]
            elif(selected_radio=="no cedulado"):
               filter_list=[["cedulado"],["False"],["and"]]
            elif(selected_radio=="incorporada"):
               filter_list=[["incorporada"],["Si"],["and"]]
            elif(selected_radio=="no incorporada"): 
               filter_list=[["incorporada"],["No"],["and"]] 
            elif(selected_radio=="docente" or selected_radio=="no docente" or selected_radio=="seccion"):
                 filter_list=[["tipo"],[selected_radio],["and"]] 
        return filter_list
   #Consults to the Data Base Information
   @classmethod
   def consultar(cls,vent,opcion):
        pnl=vent.panelActual
        tabla=pnl.get_comp_byTag("table")
        filter_list=cls.get_filterData(pnl,vent,opcion)
        radio=pnl.get_comp_byTag("radio")
        selected_radio=""
        selected=""
        combo=pnl.get_comp_byTag("combo")
        if(radio!=None):
           selected_radio=radio.get_selected_value()
        if(combo!=None):
           selected=combo.get_selected_value()
        if(opcion==cls.CONSULT_WORKERS):
          conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
          fields=[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_NOMBRE,constantes.CLAVE_CARGO,"correo","telefono",constantes.CLAVE_ESTATUS_TRABAJ]
          requiere_cargos=False
          requiere_estatus=False
          cargo_index=[-1,-1]
          estatus_val=""
          cargos=[]
          if(filter_list[0]!=None):
            for i in range(0,len(filter_list[0])):
               if(filter_list[0]!=None):
                  if(filter_list[0][i]=="cargo"):
                      filter_list[0][i]=constantes.CLAVE_CARGO
                      requiere_cargos=True
                      cargo_index[0]=i
                  elif(filter_list[0][i]=="tipo"):
                      cargo_index[1]=i
                      filter_list[0][i]=constantes.CLAVE_CARGO
                  elif(filter_list[0][i]=="estatus"):
                        requiere_estatus=True                  
                        estatus_val=filter_list[1][i]
                        filter_list=[None,None,None]                        
          if(requiere_cargos):
             #Filter By 'cargo'
             valid_cargo=False
             valor_carg=filter_list[1][cargo_index[0]]
             if(selected_radio=="docente"):
                cargos=["docente","docente de aula","coordinador de evaluacion","coordinador de orientacion","director","sub director academico","sub director administrativo"]
             else:
                cargos=["obrero","secretaria"]
             conexion_bd.set_tabla(constantes.TABLA_CARGO)
             data=[]
             codes=[]
             valores=[]
             valid_cargo=False
             for i in range(0,len(cargos)):
               if(cargos[i]==valor_carg.lower()):
                  data_cargs=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),["cargo"],[cargos[i]],["and"])            
                  for j in range(0,len(data_cargs)):
                     codes.append(data_cargs[j][0])
                     valores.append(data_cargs[j][1])
             conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)  
             for k in range(0,len(codes)):
                 dat_worker=conexion_bd.get_allData(fields,len(fields),[constantes.CLAVE_CARGO],[codes[k]],["and"])
                 if(dat_worker!=[]):
                    if(dat_worker[0][0]!="000" and dat_worker[0][0]!="001"):
                       #Prevent get data from Default Worker of User Admin
                       temp_dat=list(dat_worker[0])
                       conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                       data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[dat_worker[0][1]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                       data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[dat_worker[0][5]],["and"])
                       temp_dat[2]=valores[k]
                       temp_dat[1]=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                       temp_dat[5]=data_estatus[0][0]
                       data.append(temp_dat)   
          else:
            if(selected_radio=="docente"):
              cargos=["docente","docente de aula","coordinador de evaluacion","coordinador de orientacion","director","sub director academico","sub director administrativo"]
            else:
              cargos=["obrero","secretaria"]
            conexion_bd.set_tabla(constantes.TABLA_CARGO)
            data=[]
            codes=[]
            cargs=[]
            for i in range(0,len(cargos)):
              data_cargs=conexion_bd.get_allData(constantes.CAMPOS_CARGO,len(constantes.CAMPOS_CARGO),["cargo"],[cargos[i]],["and"])            
              for j in range(0,len(data_cargs)):
                 codes.append(data_cargs[j][0])
                 cargs.append(data_cargs[j][1])    
            for k in range(0,len(codes)):
                if(cargo_index[1]!=-1 or estatus_val!=""):
                   if(cargo_index[1]!=-1):
                       filter_list[1][cargo_index[1]]=codes[k]
                   else:
                     filter_list=[[constantes.CLAVE_CARGO],[codes[k]],["and"]]
                   conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR) 
                   dat_worker=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
                   if(dat_worker!=[]):
    
                     if(dat_worker[0][0]!="000" and dat_worker[0][0]!="001"):
                       #Prevent get data from Default Worker of User Admin
                       conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                       data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[dat_worker[0][1]],["and"])
                       conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                       data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[dat_worker[0][5]],["and"])
                       if(requiere_estatus and estatus_val!=""):
                           if(data_estatus[0][0]==estatus_val):
                              temp_dat=list(dat_worker[0])
                              temp_dat[2]=cargs[k]
                              temp_dat[1]=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                              temp_dat[5]=data_estatus[0][0]
                              data.append(temp_dat)
                       else:
                          temp_dat=list(dat_worker[0])
                          temp_dat[2]=cargs[k]
                          temp_dat[1]=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()
                          temp_dat[5]=data_estatus[0][0]
                          data.append(temp_dat)
                else:
                   break
                     
        elif(opcion==cls.CONSULT_STUDENTS):
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           fields=[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_ESTUD,constantes.CLAVE_SECCION,constantes.CLAVE_REPRESENTANTE,"genero"]           
           data=[]
           second_filter=[None,None,None]
           filter_estatus=None
           filter_year=None
           if(filter_list[0]!=None):
               if(len(filter_list[0])>1 and len(filter_list[1])>1):
                   if(filter_list[0][0]!="estatus" and filter_list[0][0]!="salud" and filter_list[0][0]!="año"):
                        second_filter=[[filter_list[0][0]],[filter_list[1][0]],["and"]]
                   else:
                      if(filter_list[0][0]=="estatus"):
                        filter_estatus=["estatus",filter_list[1][0]]
                      elif(filter_list[0][0]=="salud"):
                         filter_estatus=["salud",filter_list[1][0]]
                      elif(filter_list[0][0]=="año"):
                          filter_year=["año",filter_list[1][0]]
           tempdata=conexion_bd.get_allData(fields,len(fields),second_filter[0],second_filter[1],second_filter[2])
           if(tempdata!=[]):
              for estud in tempdata:
                  conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                  data_estatus=conexion_bd.get_allData(["estatus","cedulado","salud"],3,[constantes.CLAVE_ESTATUS_ESTUD],[estud[2]],["and"])
                  conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                  data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[estud[1]],["and"])
                  nombre=""
                  apellido=""
                  for name_index in range(0,len(data_nombre[0])):
                     if(name_index<2):
                         if(data_nombre[0][name_index]!="" and data_nombre[0][name_index]!="..."):
                             nombre=nombre+data_nombre[0][name_index].capitalize()+" "
                     else:
                        if(data_nombre[0][name_index]!="" and data_nombre[0][name_index]!="..."):
                             apellido=apellido+data_nombre[0][name_index].capitalize()+" "
                  if(filter_list[0]!=None):
                    if(data_estatus[0][1]==filter_list[1][len(filter_list[1])-1]):
                        valido=True
                        if(filter_estatus!=None):
                            if(filter_estatus[0]=="estatus"):
                               if(data_estatus[0][0]!=filter_estatus[1]):
                                  valido=False
                            elif(filter_estatus[0]=="salud"):
                              if(data_estatus[0][2]!=filter_estatus[1]):
                                  valido=False
                        elif(filter_year!=None):
                            conexion_bd.set_tabla(constantes.TABLA_SECCION)
                            data_secc=conexion_bd.get_allData([constantes.CLAVE_SECCION],1,["año",constantes.CLAVE_SECCION],[ filter_year[1],estud[3]],["and","and"])
                            if(data_secc==[]):
                                valido=False
                        if(valido):
                            conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                            fields2=[constantes.CLAVE_REPRESENTANTE,"telef"]
                            data2=conexion_bd.get_allData(fields2,len(fields2),[constantes.CLAVE_REPRESENTANTE],[estud[4]],["and"])
                            secc_asign=""
                            if(estud[3]!="default"):
                               secc_asign=estud[3]
                            estado=data_estatus[0][0]
                            if(estado=="irregular"):
                              estado="activo"
                            data_row=[estud[0],apellido,nombre,secc_asign,data2[0][0],estado,data_estatus[0][2],estud[5]]
                            data.append(data_row)
                 
        elif(opcion==cls.CONSULT_TEACHERS):
            fields=[constantes.CLAVE_TRABAJADOR,"seccion_guia",]
            estatus_val=""
            seccion_val=""
            if(filter_list[0]!=None):
               if(filter_list[0][0]=="estatus"):
                  estatus_val=filter_list[1][0]
                  filter_list=[None,None,None]
               elif(filter_list[0][0]=="seccion_guia"):
                  seccion_val=filter_list[1][0]
                  filter_list=[None,None,None]               
            data_temp=[]
            conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
            data_tr=conexion_bd.get_allData(constantes.CAMPOS_TRABAJADOR,len(constantes.CAMPOS_TRABAJADOR),filter_list[0],filter_list[1],filter_list[2])
            if(data_tr!=[]):
                for i in range(0,len(data_tr)):
                    if(data_tr[i][0]!="000" and data_tr[i][0]!="001"):
                        #Prevent get data from Default worker of Admin User
                        cargo=data_tr[i][6]
                        conexion_bd.set_tabla(constantes.TABLA_CARGO)
                        dat_cargo=conexion_bd.get_allData(["cargo"],1,[constantes.CLAVE_CARGO],[cargo],["and"])
                        if(dat_cargo[0][0]!="secretaria" and dat_cargo[0][0]!="obrero" ):
                            conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
                            dat_prof=conexion_bd.get_allData(constantes.CAMPOS_PROFESOR,len(constantes.CAMPOS_PROFESOR),[constantes.CLAVE_TRABAJADOR],[data_tr[i][0]],["and"])
                            if(dat_prof!=[]):
                                if(seccion_val=="" or seccion_val==dat_prof[0][2]):
                                    dat=[data_tr[i][0],dat_prof[0][2]]
                                    data_temp.append(dat)                               
            data=[]
            if(data_temp!=[]):
                fields_trabaj=[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_TRABAJ]
                for i in range(0,len(data_temp)):
                    conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                    data_trabaj=conexion_bd.get_allData(fields_trabaj,len(fields_trabaj),[constantes.CLAVE_TRABAJADOR],[data_temp[i][0]],["and"])
                    if(data_trabaj!=[]):
                      if(data_trabaj[0][0]!="000" and data_trabaj[0][0]!="001"):
                          conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                          data_nomb=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_trabaj[0][1]],["and"])
                          conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                          data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_TRABAJ],[data_trabaj[0][2]],["and"])
                          secc_guia=""
                          if(data_temp[i][1]!="default" and data_temp[i][1]!="..."):
                              secc_guia=data_temp[i][1]
                          nomb=data_nomb[0][0].capitalize()+" "+data_nomb[0][1].capitalize()
                          if(estatus_val==""):
                             data_row=[data_temp[i][0],nomb,secc_guia,data_estatus[0][0]]
                             data.append(data_row)
                          else:
                            if(data_estatus[0][0]==estatus_val):
                                   data_row=[data_temp[i][0],nomb,secc_guia,data_estatus[0][0]]
                                   data.append(data_row)
                     
        elif(opcion==cls.CONSULT_SECTIONS):
            fields=[constantes.CLAVE_SECCION,"año","letra","total_estud"] 
            data=[]   
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            temp_data=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])  
            for i in range(0,len(temp_data)):
               if(temp_data[i][0]!="default"):
                  data.append(temp_data[i])               
 
        elif(opcion==cls.CONSULT_ACADEMIC_MOMENTS):
            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
            fields=[constantes.CLAVE_MOMENTO,"abierto","fecha_inicio","fecha_limite"]
            if(filter_list[0]!=None):
               for i in range(0,len(filter_list[0])):
                  if(filter_list[0][i]=="estatus"):
                       val_filter=filter_list[1][i]
                       if(val_filter=="abierto" or val_filter=="cerrado"):
                           filter_list[0][i]="abierto"
                           if(val_filter=="abierto"):
                              filter_list[1][i]="true" 
                           elif(val_filter=="cerrado"):
                              filter_list[1][i]="false"                  
            data=[]
            temp_data=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])    
            if(temp_data!=[]):
                 for i in range(0,len(temp_data)):
                     data_row=[]
                     data_row.append(temp_data[i][0])
                     if(temp_data[i][1]=="true"):
                        data_row.append("abierto")
                     else:
                        data_row.append("cerrado")
                     if(temp_data[i][2]!="" and temp_data[i][3]!=""):
                        data_row.append(temp_data[i][2])
                        data_row.append(temp_data[i][3])
                     else:
                        data_row.append("no defininida")
                        data_row.append("no defininida")
                     data.append(data_row)   
                     
        elif(opcion==cls.CONSULT_TIMETABLES_DISPONIBILITY):
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            data=[]
            temp_dat=[]            
            fields=[constantes.CLAVE_TRABAJADOR,"turno","disp_lunes","disp_martes","disp_miercoles","disp_jueves","disp_viernes"]
            if(filter_list[0]!=None):
              if(filter_list[0][0].startswith("disp") and filter_list[1][0]=="disponible"):
                 d=conexion_bd.get_allData(fields,len(fields))
                 camp=filter_list[0][0]
                 for va in d:
                    if(va[2]!="no disponible" and camp=="disp_lunes"):
                      temp_dat.append(va)
                    elif(va[3]!="no disponible" and camp=="disp_martes"):
                       temp_dat.append(va)
                    elif(va[4]!="no disponible" and camp=="disp_miercoles"):
                      temp_dat.append(va)
                    elif(va[5]!="no disponible" and camp=="disp_jueves"):
                      temp_dat.append(va)
                    elif(va[6]!="no disponible" and camp=="disp_viernes"):
                      temp_dat.append(va)
              else:
                temp_dat=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
            else:
                temp_dat=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
            for k in range(0,len(temp_dat)):
                  row=[]
                  for l in range(0,len(temp_dat[k])):
                     if(l<2):
                        row.append(temp_dat[k][l])
                     else:
                       if(temp_dat[k][l]!="no disponible"):
                           row.append("disponible") 
                       else:
                          row.append(temp_dat[k][l])
                  data.append(row)
   
        elif(opcion==cls.CONSULT_FORMATION_AREAS):

            conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
            fields_area=[constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_AÑOS_INCORPORADOS]
            data=[]   
            temp_data=conexion_bd.get_allData(fields_area,len(fields_area),filter_list[0],filter_list[1],filter_list[2])
            conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
            if(temp_data!=[]):
               for i in range(0,len(temp_data)):
                   data_row=[temp_data[i][0]]
                   years=conexion_bd.get_allData(constantes.CAMPOS_AÑOS_INCORPORADOS,len(constantes.CAMPOS_AÑOS_INCORPORADOS),[constantes.CLAVE_AÑOS_INCORPORADOS],[temp_data[i][1]],["and"])
                   for j in range(1,len(years[0])-1):
                      val_field=years[0][j]
                      if(val_field=="True"):
                           val_field="disponible"
                      if(val_field=="False"):
                           val_field="no disponible"
                      data_row.append(val_field)
                   data.append(data_row)
     
        elif(opcion==cls.CONSULT_USERS_HISTORIAL):
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            buscar_fecha=False
            buscar_razon=False
            razon_ingresada=""
            fecha_inicio=""
            fecha_cierre=""
            tipo_fecha=-1
            razon=""
            tipo=""
            target_date=""
            if(filter_list[0]!=None):
               is_date=False
               if(filter_list[0][0]=="desde - hasta" or filter_list[0][0]=="antes de" or filter_list[0][0]=="despues de"):
                  is_date=True
                  target_date=filter_list[0][0]
                  
               if(filter_list[0][0]=="accion" or filter_list[0][0]=="accion realizada"):
                  buscar_razon=True
                  razon_ingresada=filter_list[1][0]
                  filter_list=[None,None,None]       
               if(is_date):
                    buscar_fecha=True
                    fecha_inicio=pnl.get_comp_byName("fecha1").get_text()
                    fecha_cierre=pnl.get_comp_byName("fecha2").get_text()
                    filter_list=[None,None,None]
            else:
                is_date=False
                if(selected=="desde - hasta" or selected=="antes de" or selected=="despues de"):
                  is_date=True
                  target_date=selected
                          
                if(is_date):
                      buscar_fecha=True
                      fecha_inicio=pnl.get_comp_byName("fecha1").get_text()
                      fecha_cierre=pnl.get_comp_byName("fecha2").get_text()
                      filter_list=[None,None,None]
                else:
                   val_identify=pnl.get_comp_byName("identificador_cp2").get_selected_value()
                   if(val_identify=="elejir" or val_identify=="elegir"):
                      if(pnl.get_comp_byName("filtros_cp").get_selected_value()=="accion realizada"):
                           General.show_message("por favor indique una accion", "accion invalida")
                           return
                      elif(pnl.get_comp_byName("filtros_cp").get_selected_value()=="usuario"):
                          General.show_message("por favor indique un usuario","usuario invalido")
                          return          
            data=[]
            fields=[constantes.CLAVE_USUARIO,"fecha","hora","tipo","razon"]
            data_temp=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
            for d_temp in data_temp:
               temp_categoria=d_temp[3]
               temp_razon=d_temp[4]
               if(temp_categoria=="actualizacion"):
                     temp_categoria="actualizar"
               elif(temp_categoria=="proceso"):
                     temp_categoria=""
               elif(temp_categoria=="servicio"):
                     temp_categoria=""
               elif(temp_categoria=="gestion usuario"):
                    temp_categoria=""
               elif(temp_categoria=="base de datos"):
                    temp_razon="bd"
                    temp_categoria=d_temp[4]
               elif(temp_categoria=="registro"):
                      temp_categoria="registro de"
               if(buscar_fecha==False and buscar_razon==False):
                  data.append([d_temp[0],d_temp[1],d_temp[2],temp_categoria+" "+temp_razon])
               elif(buscar_fecha==False and buscar_razon==True):
                    if(razon_ingresada.startswith(temp_categoria)):
                        if(razon_ingresada.endswith(temp_razon)):
                            data.append([d_temp[0],d_temp[1],d_temp[2],temp_categoria+" "+temp_razon]) 
               elif(buscar_fecha==True and buscar_razon==False):
                  time_object=tiempo()
                  valida_fecha=False
                  if(General.is_valid(fecha_inicio,constantes.CADENA_FECHA,False,2)==False and fecha_inicio!=""):
                      General.show_message("por favor ingrese una fecha de inicio de la forma xx/xx/xxxx","fecha invalida")
                      return
                  if(General.is_valid(fecha_cierre,constantes.CADENA_FECHA,False,2)==False and fecha_cierre!=""):
                      General.show_message("por favor ingrese una fecha de cierre de la forma xx/xx/xxxx","fecha invalida")
                      return  
                  if(fecha_cierre=="" and fecha_inicio==""):
                       valida_fecha=True  
                  else:
                      if(target_date=="desde - hasta"):
                         if(time_object.is_previous(d_temp[1],fecha_cierre,False) and time_object.is_previous(fecha_inicio,d_temp[1],False)):
                              valida_fecha=True
                      elif(target_date=="antes de"):
                         if(time_object.is_previous(d_temp[1],fecha_inicio,False)):
                              valida_fecha=True
                      elif(target_date=="despues de"):
                         if(time_object.is_previous(d_temp[1],fecha_inicio,False)==False):
                              valida_fecha=True
                  if(valida_fecha):     
                       data.append([d_temp[0],d_temp[1],d_temp[2],temp_categoria+" "+temp_razon]) 
        
        elif(opcion==cls.CONSULT_FORMATION_AREAS_TEACHERS):
              conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
              fields_prof=[constantes.CLAVE_PROFESOR,constantes.CLAVE_TRABAJADOR]
              filtro_ci=False
              data_prof=[]
              if(filter_list[0]!=None):
                 if(filter_list[0][0]==constantes.CLAVE_TRABAJADOR):
                    filtro_ci=True
              if(filtro_ci):
                data_prof=conexion_bd.get_allData(fields_prof,len(fields_prof),[constantes.CLAVE_TRABAJADOR],filter_list[1],filter_list[2])
              else:
                data_prof=conexion_bd.get_allData(fields_prof,len(fields_prof))
              if(data_prof==[]):
                 return
              data=[]  
              for i in range(0,len(data_prof)):
                 id_prof=data_prof[i][0]
                 ci_prof=data_prof[i][1]
                 conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
                 fields=[constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_PROFESOR]
                 data_temp=[]
                 if(filtro_ci==False):
                   data_temp=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
                 else:
                   data_temp=conexion_bd.get_allData(fields,len(fields),[constantes.CLAVE_PROFESOR],[id_prof],["and"])
                 if(data_temp!=[]):
                   for dat_a in data_temp:
                     if(dat_a[1]==id_prof):
                       conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                       fields_trabaj=[constantes.CLAVE_NOMBRE]
                       data_trabaj=conexion_bd.get_allData(fields_trabaj,len(fields_trabaj),[constantes.CLAVE_TRABAJADOR],[ci_prof],["and"])
                       if( data_trabaj!=[]):
                         conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                         data_nombre=conexion_bd.get_allData(["apellido","nombre"],2,[constantes.CLAVE_NOMBRE],[data_trabaj[0][0]],["AND"])
                         nomb=data_nombre[0][0].capitalize()+" "+data_nombre[0][1].capitalize()          
                         data_row=[ci_prof,nomb,dat_a[0]]
                         data.append(data_row)
                         
        elif(opcion==cls.CONSULT_MATERIA_PENDIENTE):
             data=[]
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
             fields=[constantes.CLAVE_MATERIA_PENDIENTE,constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"]
             data_temp=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
             if(data_temp!=[]):
                for i in range(0,len(data_temp)):
                   data_row=[]
                   data_row.append(data_temp[i][1])
                   data_row.append(data_temp[i][2])
                   data_row.append(data_temp[i][3])
                   conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                   data_calif=conexion_bd.get_allData(constantes.CAMPOS_CALIF_PENDIENTE,len(constantes.CAMPOS_CALIF_PENDIENTE),[constantes.CLAVE_MATERIA_PENDIENTE],[data_temp[i][0]],["and"])
                   if(data_calif!=[]):
                     sz=len(data_calif)
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente")
                     for j in range(0,sz):
                        if(data_calif[j][2]=="intento 1"):
                           data_row[3]=data_calif[j][3]
                        elif(data_calif[j][2]=="intento 2"):
                            data_row[4]=data_calif[j][3]
                        elif(data_calif[j][2]=="intento 3"):
                            data_row[5]=data_calif[j][3]
                        elif(data_calif[j][2]=="intento 4"): 
                            data_row[6]=data_calif[j][3]
                        elif(data_calif[j][2]=="revision"):
                            data_row[7]=data_calif[j][3]
                   else:
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                     data_row.append("pendiente") 
                   data.append(data_row)      
        
        elif(opcion==cls.CONSULT_DOWNLOADS):
             conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
             if(filter_list[0]!=None):
               if(filter_list[0][0]=="tipo formato"):
                  filter_list[0][0]=constantes.CLAVE_FORMATO
               elif(filter_list[0][0]=="tipo doc"):
                  filter_list[0][0]="tipo_descarga"
               elif(filter_list[0][0]=="CI trabajador"):
                  filter_list[0][0]=constantes.CLAVE_TRABAJADOR
             data=[]
             fields=[constantes.CLAVE_TRABAJADOR,constantes.CLAVE_FORMATO,"tipo_descarga","fecha","hora"]
             data=conexion_bd.get_allData(fields,len(fields),filter_list[0],filter_list[1],filter_list[2])
            
        tabla.reset()
        if(data!=[]):
           for i in range(0,len(data)):
               tabla.add_row(data[i])
        
    
