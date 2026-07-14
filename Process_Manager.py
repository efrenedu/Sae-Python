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
    
    #Return the Section to Assign the Student On the Inscription 
    @classmethod
    def get_seccion(cls,year,turno):
        last_secc=""
        conexion_bd.set_tabla(constantes.TABLA_SECCION)   
        nueva_secc=False
        total_secc="0"
        max_secc="30"
        min_secc="15"
        data_seccion_estud=[]
        if(conexion_bd.is_empty()==False):
            data_seccs=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION),["año"],[year],["and"])
            num_seccs=len(data_seccs)
            if(data_seccs!=[]):
                asignada=-1
                letra=""
                code_letra=-1
                for i in range(0,len(data_seccs)):
                    conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                    data_hor=conexion_bd.get_allData(constantes.CAMPOS_HORARIO,len(constantes.CAMPOS_HORARIO),[constantes.CLAVE_HORARIO],[data_seccs[i][3]],["and"])
                    if(data_hor[0][2]==turno and data_seccs[i][0]!="default" and asignada==-1):
                        total1=data_seccs[i][4]
                        limite1=data_seccs[i][5]
                        minimo1=data_seccs[i][6]
                        another_seccion=False
                        total2=-1
                        limite2=-1
                        minimo2=-1
                        id_secc2=""
                        letra2=""
                        for j in range(0,len(data_seccs)):
                            if(data_seccs[i][0]!=data_seccs[j][0] and another_seccion==False and data_seccs[j][0]!="default"):
                                data_hor2=conexion_bd.get_allData(constantes.CAMPOS_HORARIO,len(constantes.CAMPOS_HORARIO),[constantes.CLAVE_HORARIO],[data_seccs[j][3]],["and"])
                                if(data_hor2[0][2]==turno):
                                    total2=data_seccs[j][4]
                                    limite2=data_seccs[j][5]
                                    minimo2=data_seccs[j][6]
                                    id_secc2=data_seccs[j][0]
                                    letra2=data_seccs[j][2]
                                    another_seccion=True
                            else:
                                if(another_seccion==True):
                                    break            
                        if(another_seccion==True):
                                  if(int(total1)+1<=int(minimo1)):
                                  
                                     asignada=data_seccs[i][0]
                                     letra=data_seccs[i][2]
                                     total_secc=str(int(total1)+1)
                                  elif(int(total2)+1<=int(minimo2)):
                                    
                                     asignada=id_secc2
                                     letra=letra2
                                     total_secc=str(int(total2)+1)
                                  else:
                                     if(int(total1)+1<=int(limite1)):
                                      
                                       asignada=data_seccs[i][0]
                                       letra=data_seccs[i][2]
                                       total_secc=str(int(total1)+1)
                                     elif(int(total2)+1<=int(limite2)):
                                     
                                       asignada=id_secc2
                                       letra=letra2
                                       total_secc=str(int(total2)+1)
                                     else:
                                        
                                        code_letraA=ord(data_seccs[i][2])
                                        code_letraB=ord(letra2)
                                        if(code_letraA<code_letraB):
                                            last_secc=letra2
                                        else:
                                            last_secc=data_seccs[i][2]
                              
                        else:
                                 
                                 if(int(total1)+1<=int(minimo1)):
                                   asignada=data_seccs[i][0]
                                   letra=data_seccs[i][2]
                                   total_secc=str(int(total1)+1)
                                 else:
                                    code_letra=ord(data_seccs[i][2][0])
                                    last_secc=data_seccs[i][2]
                if(asignada==-1):
                    nueva_secc=True
                    if(last_secc==""):
                         last_secc="None"
                else:
                    data_seccion_estud=["False",str(asignada),year,letra,total_secc,max_secc,min_secc,turno]
                         
            else:
                nueva_secc=True
                last_secc="None"
        else:
            nueva_secc=True
            last_secc="None"       
        if(nueva_secc):                   
            letra_secc=""
            if(last_secc=="None"):
                letra_secc="A"
            else:    
               letra_secc=str(chr(ord(last_secc[0])+1))
            codigo=year+"-"+letra_secc
            if(turno=="mañana"):
               codigo=codigo+"(M)"
            else:
               codigo=codigo+"(T)"
            data_seccion_estud=["True",codigo,year,letra_secc,"1",max_secc,min_secc,turno]
        return data_seccion_estud

    #Execute the Action Required for Inscription Process
    @classmethod
    def inscribir(cls,usr,vent,type_i,fase):
      pnl=vent.panelActual    
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
        time_object=tiempo()
        año_escolar=""
        hoy=time_object.get_fecha()
        fecha_inscrip=time_object.get_fecha()
        fecha_cierre=time_object.get_fecha()
        fecha_inscrip_nuevo=time_object.get_fecha()
        fecha_cierre_nuevo=time_object.get_fecha()
        
        #verificamos cronograma si existe
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        data_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA))
        if(data_cronog!=[]):
           data_fechas=[]
           conexion_bd.set_tabla(constantes.TABLA_FECHA)
           data_fechas=conexion_bd.get_allData(["razon","fecha","fecha_cierre"],3,[constantes.CLAVE_CRONOGRAMA],[data_cronog[0][0]],["and"] )                
           if(data_fechas!=[]):
              for i in range(0,len(data_fechas)):
                 if(data_fechas[i][0]=="inscripcion nuevo ingreso"):
                     fecha_inscrip_nuevo=data_fechas[i][1]
                     fecha_cierre_nuevo=data_fechas[i][2]
                 elif(data_fechas[i][0]=="inscripcion estudiantes regulares"):
                     fecha_inscrip=data_fechas[i][1]
                     fecha_cierre=data_fechas[i][2]
           else:
              fecha_actual=hoy.split("/")
              if(len(fecha_actual)==3):
                 year=fecha_actual[2]
                 fecha_inscrip="16/09/"+year
                 fecha_cierre="15/03/"+str(int(year)+1)
                 fecha_inscrip_nuevo="16/09/"+year
                 fecha_cierre_nuevo="15/12/"+year
               
        else:
          #set default date inscripcion
          fecha_actual=hoy.split("/")
          if(len(fecha_actual)==3):
            year=fecha_actual[2]
            fecha_inscrip="16/09/"+year
            fecha_cierre="15/03/"+str(int(year)+1)
            fecha_inscrip_nuevo="16/09/"+year
            fecha_cierre_nuevo="15/12/"+year
        estud=estudiante()
        data_estud=[
            type_i,
            radios.get_selected_value(),
            pnl.get_comp_byName("cedula").get_text(),
            pnl.get_comp_byName("cedula_repres").get_text(),
            pnl.get_comp_byName("año").get_text(),
            time_object,
            fecha_inscrip,
            fecha_cierre,
            fecha_inscrip_nuevo,
            fecha_cierre_nuevo,
            hoy,
            radios2.get_selected_value()
        ]
        valido=estud.validar_solicit_inscrip(data_estud)
        if(valido==0):
          usr.data_expediente=[]
          data_valid=estud.get_data_inscrip()
          usr.recibe_data_process(data_valid)
          if(type_i==cls.INSCRIPTION_NUEVO_INGRESO):
                vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_2)
                Event_manager.set_data_estud(data_valid[0],False,data_estud[3])   
          else:
                vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_3)
                Event_manager.set_data_estud(data_valid[0],True,data_estud[3])                           
        else:
          if(valido==-1):
            General.show_message("por favor escriba una CI valida","cedula invalida")
          elif(valido==-2):
            General.show_message("estudiante no registrado","cedula inexistente")
          elif(valido==-3):
             General.show_message("por favor escriba una CI del representante valida","cedula representante invalida")
          elif(valido==-4):
             General.show_message("por favor escriba un año de nacimiento valido","año de nacimiento invalido")
          elif(valido==-5):
             General.show_message("el estudiante ya se ha registrado","estudiante inscrito")
          elif(valido==-6):
             General.show_message("el estudiante ya se ha inscrito este año","estudiante inscrito")
          elif(valido==-7):
             General.show_message("las inscripciones de estudiantes regulares estan cerradas","inscripciones cerradas")
          elif(valido==-8):
             General.show_message("las inscripciones de estudiantes nuevo ingreso estan cerradas","inscripciones cerradas")
          elif(valido==-9):
             General.show_message("el estudiante tiene calificaciones pendientes de otra institucion por actualizar","calificaciones no actualizadas")
          elif(valido==-10):
             General.show_message("el estudiante ya se ha graduado","estudiante graduado")      
      else:
          if(fase==cls.INSCRIPTION_VERIFY_DATA_STUDENT):
             data_estud=[]
             data_pendiente=["False"]
             data_repitiendo=["False"]
             data_seccion=[]
             last_dat=usr.get_data_process()
             year_curso=""
             turno=pnl.get_comp_byName("turno").get_selected_value()
             if(turno=="elejir" or turno=="elegir"):
                General.show_message("por favor seleccione un turno","turno invalido")
                return
                
             estatus="activo"
             if(last_dat[0][2]=="True"):
                year_curso=pnl.get_comp_byName("curso").get_selected_value().split(" ")[0] 
                if(int(year_curso)>1):
                    estatus="irregular"    
             else:
                 estud=estudiante()
                 data_curso=estud.get_data_curso(last_dat[0][0])
                 year_curso=data_curso[0]
                 data_pendiente=data_curso[1]
                 data_repitiendo=data_curso[2]
                 
             #Verify Formation Areas  
             conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
             areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_AÑOS_INCORPORADOS],2,["incorporada"],["Si"],["and"])
             if(areas==[]):
                    General.show_error("error no existen areas de formacion incorporadas","sin areas de formacion disponibles")
                    return
             conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
             cants=[0,0,0,0,0]                                
             for ar in areas:
                for i in range(0,int(year_curso)):
                    ar_in=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],1,[constantes.CLAVE_AÑOS_INCORPORADOS,str(i+1)+"_año"],[ar[1],"True"],["and","and"]) 
                    if(ar_in!=[]):
                         cants[i]=cants[i]+1
             for j in range(0,int(year_curso)):
                 if(cants[j]==0):
                     General.show_error("faltan areas de formacion disponibles para "+str(j+1)+" año ","año sin areas de formacion")
                     return    
             data_seccion=cls.get_seccion(year_curso,turno)                      
             fields=pnl.get_comps_byTag("field")
             data_estud.append(fields)
             data_estud.append(pnl.get_comp_byName("salud").get_selected_value())
             data_estud.append(pnl.get_comp_byName("genero").get_selected_value())
             data_estud.append(year_curso)
             data_estud.append(estatus)
             data_verificada=usr.validar_inscripcion(data_estud)
             valido=data_verificada[0]
             if(valido==0):
                if(last_dat[0][2]=="True" or (data_pendiente[0]=="False" and data_repitiendo[0]=="False")):
                    if(General.show_confirmDialog("esta seguro que desea inscribir el estudiante","inscribir estudiante")!=True):
                       return
               
                usr.recibe_data_process(data_verificada[1])
                usr.recibe_data_process(data_verificada[2])
                usr.recibe_data_process(data_verificada[3])
                usr.recibe_data_process(data_seccion)
                usr.recibe_data_process(data_pendiente)
                data_areas=[]
                year_area=year_curso+"_año"
                conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                areas=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],1,["incorporada"],["Si"],["and"])           
                usr.recibe_data_process(data_areas)
                usr.recibe_data_process(data_repitiendo)
                
                if(last_dat[0][2]!="True" and (data_pendiente[0]!="False" or data_repitiendo[0]!="False")):
                    vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION_4)
                    pnl=vent.panelActual
                    pnl.get_comp_byName("seccion").set_text("seccion:"+data_seccion[3])
                    pnl.get_comp_byName("year").set_text("año:"+year_curso+" año")
                    if(data_pendiente[0]!="False"):
                        temp_pendiente=[]
                        for i in range(1,len(data_pendiente)):
                            temp_pendiente.append(data_pendiente[i][0] +" - "+data_pendiente[i][1]+" año")
                        pnl.get_comp_byName("pendientes").set_values(temp_pendiente)         
                    if(data_repitiendo[0]!="False"):
                        temp_repitiendo=[]
                        for rep in range(1,len(data_repitiendo)):
                           temp_repitiendo.append(data_repitiendo[rep])
                        pnl.get_comp_byName("areas").set_values(temp_repitiendo)
                else:  
                    estud=estudiante()
                    estud.inscribir(usr.get_data_process())
                    conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                    Event_manager.generar_reporte("inscripcion",usr.get_data_process())
                    time_object=tiempo()
                    usr.add_action_historial(["inscripcion de estudiante",time_object.get_tiempo()])
                    conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                    id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                    data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","inscripcion","",time_object.get_fecha()]
                    conexion_bd.add_data(data_hist)
                    General.show_message("inscripcion realizada satisfactoriamente","inscripcion finalizada")
                    vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION)
                    usr.reset_data_process(0)
             else:
                 if(valido==-1):
                   General.show_message("por favor escriba un nombre valido","nombre invalido")                   
                 elif(valido==-2):
                   General.show_message("por favor escriba un apellido valido","apellido invalido")
                 elif(valido==-3):
                   General.show_message("por favor abra una carpeta con un expediente valido","expediente invalido")
                 elif(valido==-4):
                   General.show_message("por favor escriba un cedula de representante valida","cedula de representante invalido")
                 elif(valido==-5):
                   General.show_message("por favor escriba un telefono de representante valido","telefono de representante invalido")
                 elif(valido==-6):
                   General.show_message("por favor escriba un nombre de representante valido","nombre de representante invalido")
                 elif(valido==-7):
                   General.show_message("por favor escriba un apellido de representante valido","apellido de representante invalido")
                 elif(valido==-8):
                   General.show_message("por favor elija un estatus valido","estatus invalido")
                 elif(valido==-9):
                   General.show_message("por favor elija un estado de salud valido","estado de salud invalido")
                 elif(valido==-10):
                   General.show_message("por favor indique la direccion separada por comas","direccion invalida")
                 elif(valido==-11):
                   General.show_message("por favor escriba una fecha de nacimiento valida","fecha invalida")
                 elif(valido==-12):
                   General.show_message("la foto debe ser un archivo en formato .JPG o .PNG","formato de foto invalido")
                 elif(valido==-13):
                    General.show_message("el expediente debe ser un archivo .RAR o .ZIP ","formato de expediente invaldo")
                 elif(valido==-14):
                   General.show_message("el archivo de la foto ya existe en servidor, por favor cambie el nombre al archivo y vuelve a intentarlo","foto ya existente")
                 elif(valido==-15):
                    General.show_message("el archivo del expediente ya existe en servidor, por favor cambie el nombre al archivo y vuelve a intentarlo","expediente ya existente")
                 elif(valido==-16):
                    General.show_message("por favor escriba un correo del representante valido","correo invalido")
                 elif(valido==-17):
                    General.show_message("por favor escriba una direccion del representate de la siguiente maner: xxxxx,xxxx,xxxx","direccion del representante no valida")
                 elif(valido==-18):
                    General.show_message("por favor escriba un parentesco valido del representante","parentesco invalido")
                 elif(valido==-19):
                     General.show_message("por favor escriba un oficio valido del representante","oficio invalido")
                 elif(valido==-20):                 
                     General.show_message("por indique el plantel de procedencia del estudiante","plantel invalido")
               
          elif(fase==cls.INSCRIPTION_CONFIRM_INSCRIPTION):
            if(General.show_confirmDialog("esta seguro que desea inscribir el estudiante","inscribir estudiante")!=True):
               return
               
            estud=estudiante()
            estud.inscribir(usr.get_data_process())
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            Event_manager.generar_reporte("inscripcion",usr.get_data_process())                    
            time_object=tiempo()           
            usr.add_action_historial(["inscripcion de estudiante",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","inscripcion","",time_object.get_fecha()]
            conexion_bd.add_data(data_hist)
            General.show_message("inscripcion realizada satisfactoriamente","inscripcion finalizada")
            vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION)
            usr.reset_data_process(0)   


    #Determine and execute the Action Required for 'Rendimiento' Process
    @classmethod
    def set_rendimiento(cls,usr,vent,opcion):
        pnl=vent.panelActual
        user_t=usr.get_credentials()[2]
        is_secretaria=False
        
        if(user_t!="admin" and user_t!="coordinador"):
            is_secretaria=True
        if(opcion<=4):
           cls.verificar_caudicidad(usr,vent)
        
        if(opcion==0):
            #gestion de calific 1
            vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA)
            usr.reset_data_process(0)            
        elif(opcion==1):
            #sabana de notas
            if(is_secretaria==False):
                vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_SABANA_NOTAS)
                usr.reset_data_process(0)
            else:
               General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
        elif(opcion==3):
            #materia pendiente 1
            if(is_secretaria==False):
               vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND)
               usr.reset_data_process(0)
            else:
               General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
        elif(opcion==4):
            #notas finales.
             if(is_secretaria==False):
                 vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF_FINALES)
                 usr.reset_data_process(0)
             else:
                 General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")  
        elif(opcion==5):
            #materia pendiente 2
            data_proces=[]
            ced=pnl.get_comp_byName("cedula_p3").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            if(conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[ced],["and"])==[]):
                General.show_message("cedula del estudiante invalida","cedula invalida")
                return
                
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            if(conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE],[ced],["and"])==[]):
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
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_MAT_PEND)
              pnl=vent.panelActual
              pnl.get_comp_byName("area_p4").set_text(data_proces[1])
              conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
              data_pend=conexion_bd.get_allData(["max_calif"],1,[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[data_proces[0],data_proces[1],str(int(data_proces[3])-1)],["and","and","and"])
              nota=data_pend[0][0]
              if(len(nota)<2):
                 nota="0"+nota
              pnl.get_comp_byName("best_nota").set_text(nota+" pts")
            else:
                if(valido==-1):
                   General.show_message("estudiante no inscrito","estudiante invalido")
                elif(valido==-2):
                   General.show_message("por favor seleccione un area de formacion","estudiante invalido")
        elif(opcion==6):
            #gestion de calific 2
            if(is_secretaria==True):
                General.show_message("no se puede acceder a esta opcion siendo un usuario secretaria","acceso invalido")
                return
            ced=pnl.get_comp_byName("cedula_p1").get_text()
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            if(conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[ced],["and"])==[]):
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
              vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_GESTION_CALIF)
            else:
               if(valido==-1):
                   General.show_message("estudiante no inscrito","estudiante invalido")
               elif(valido==-2):
                   General.show_message("por favor seleccione un area de formacion","estudiante invalido")
               elif(valido==-3):
                   General.show_message("por favor seleccione un momento academico","momento invalido")
        elif(opcion==7):
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
                 if(valido[1]==True):
                    General.show_message("materia pendiente del estudiante aprobada existosamente","estudiante aprobado")
                 else:
                    General.show_message("calificacion de materia pendiente o revision registrada satisfactoriamente","registro exitoso de materia pendiente o revision")
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","mat. pendiente",motivo,time_object.get_fecha()]
                 conexion_bd.add_data(data_hist)  
                 vent.update_pantallas(constantes.PANTALLA_RENDIMIENTO_IDENTIFIC_MATERIA_PEND)
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
    
    
    #Remove a Calification Associated to an Academic Moment
    @classmethod
    def delete_calification(cls,usr,vent):
        pnl=vent.panelActual
        field=pnl.get_comp_byName("calific_num_p2")
        motivo=pnl.get_comp_byName("motivo").get_text()
        if(field.get_text()=="" or field.get_text()==" "):
             General.show_message("por favor seleccione una calificacion de la lista","calificacion invalida")
             return
        if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return  
        id_calific=field.get_text()
        time_object=tiempo()
        estud=estudiante()
        temp_dat=usr.get_data_process()[0]
        data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],field.get_text()]
        if(General.show_confirmDialog("esta seguro que desea borrar esta calificacion?","borrar calificacion")!=True):
            return  
        valido=estud.delete_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           tabla=pnl.get_comp_byName("table1_p1")
           tabla.reset()
           calificaciones=valido[1]
           for i in range(0,len(calificaciones)):
              tabla.add_row(calificaciones[i])
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
           field.set_text("")
           pnl.get_comp_byName("calific_val_p2").set_text("")
           pnl.get_comp_byName("motivo").set_text("")
           usr.add_action_historial(["borrar calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","borrar calificacion",motivo,time_object.get_fecha()]
           conexion_bd.add_data(data_hist)  
           General.show_message("calificacion borrada satisfactoriamente","calificacion borrada")
        else:
          if(valido[0]==-1):
             General.show_message("por favor seleccione la calificacion a borrar","numero de evaluacion no valido")
   
    #Modify the Calification Associated to an Academic Moment  
    @classmethod
    def update_calification(cls,usr,vent):
        pnl=vent.panelActual
        motivo=pnl.get_comp_byName("motivo").get_text()
        if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return
        if(General.show_confirmDialog("esta seguro que desea modificar esta calificacion?","modificar calificacion")!=True):
            return
        field1=pnl.get_comp_byName("calific_val_p2")
        field2=pnl.get_comp_byName("calific_num_p2")
        next_calific=field1.get_text()
        id_calif=field2.get_text()
        time_object=tiempo()
        estud=estudiante()
        temp_dat=usr.get_data_process()[0]
        data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],id_calif,next_calific]
        valido=estud.modific_calif(data_estud,time_object.get_fecha())
        if(valido[0]==True):
           tabla=pnl.get_comp_byName("table1_p1")
           tabla.reset()
           calificaciones=valido[1]
           for i in range(0,len(calificaciones)):
               tabla.add_row(calificaciones[i])
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
           field1.set_text("")
           field2.set_text("")
           pnl.get_comp_byName("motivo").set_text("")
           usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
           conexion_bd.set_tabla(constantes.TABLA_REPORTE)
           id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
           data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar calificacion",motivo,time_object.get_fecha()]
           conexion_bd.add_data(data_hist)  
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
         field1=pnl.get_comp_byName("estimul_p2")
         field2=pnl.get_comp_byName("estimul_p3")
         time_object=tiempo()
         estud=estudiante()
         temp_dat=usr.get_data_process()[0]
         data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4],field1.get_text(),field2.get_text()]
         valido=estud.estimular_area(data_estud,time_object.get_fecha())
         if(valido[0]==True):
            field1.set_text("")
            field2.set_text("")  
            prom_data=valido[1]
            pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
            pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+str(prom_data[1])+"pts")
            pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
            pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+str(prom_data[3])+"pts")
            pnl.get_comp_byName("motivo").set_text("")
            usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","calificacion estimulada",motivo,time_object.get_fecha()]
            conexion_bd.add_data(data_hist)  
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
                
    #Remove Estimulation Points Associated to an Academic Moment
    @classmethod
    def remover_estimulacion_mom(cls,usr,vent):
        pnl=vent.panelActual
        motivo=pnl.get_comp_byName("motivo").get_text()
        if(motivo=="" or motivo==" "):
             General.show_message("por favor escriba un motivo de la modificacion","motivo de modificacion invalido")
             return   
        if(General.show_confirmDialog("esta seguro que desea remover la estimulacion de esta area?","borrar calificacion")!=True):
            return  
        time_object=tiempo()  
        estud=estudiante()
        temp_dat=usr.get_data_process()[0]
        data_estud=[temp_dat[0],temp_dat[1],temp_dat[2],temp_dat[4]]
        valido=estud.borrar_estimulacion(data_estud,time_object.get_fecha())
        if(valido[0]==True):
            prom_data=valido[1]
            pnl.get_comp_byName("calific_m_p1_1").set_text("promedio:"+str(prom_data[0])+"pts")
            pnl.get_comp_byName("calific_m_p1_2").set_text("calificacion:"+str(prom_data[1])+"pts")
            pnl.get_comp_byName("calific_m_p1_3").set_text("estimulacion:"+str(prom_data[2])+"pts")
            pnl.get_comp_byName("calific_m_p1_4").set_text("definitiva:"+str(prom_data[3])+"pts")
            pnl.get_comp_byName("motivo").set_text("")
            usr.add_action_historial(["modificacion de calificacion",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","eliminar estimulacion",motivo,time_object.get_fecha()]
            conexion_bd.add_data(data_hist)
            General.show_message("estimulacion removida satisafactoriamente","estimulacion removida")
        else:
          if(valido[0]==-1):
            General.show_message("el area de formacion no tiene puntos de estimulacion que se puedan quitar","area sin puntos de estimulacion")
          elif(valido[0]==-2):
            General.show_message("el estudiante no tiene calificacion en esta area del momento academico indicado","estudiante sin calificacion")
     
    #Modify Definitive Calification fo Especial Cases
    @classmethod
    def modific_calif_final(cls,usr,vent):
       pnl=vent.panelActual
       ced=pnl.get_comp_byName("identificador").get_text()
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[ced],["and"])
       area=pnl.get_comp_byName("area").get_text()
       year=pnl.get_comp_byName("year").get_text()
       tabla=pnl.get_comp_byName("table1_p1")
       old_calif=tabla.get_row_selectedData()
       if(old_calif==" "):
         General.show_message("por favor seleccione una calificacion de la lista","calificacion no seleccionada")
         return
         
       new_calif=pnl.get_comp_byName("calif").get_text() 
       time_object=tiempo()
       estud=estudiante()
       valido=estud.modific_calif_final([ced,area,year,old_calif,new_calif],time_object.get_fecha())        
       if(valido>=0):
           flds=pnl.get_comps_byTag("field")
           for fl in flds:
              if(fl.get_id()=="area" or fl.get_id()=="year" or fl.get_id()=="calif"):
                  fl.set_text("")
           tabla.reset()
           conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
           data_calif=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE],[ced],["and"])
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
              conexion_bd.add_data(data_hist)
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
            id_secc=year[0]+"-"+letra+"("
            if(turno=="mañana"):
                id_secc=id_secc+"M)"
            else:
               id_secc=id_secc+"T)"
            data_secc=conexion_bd.get_allData(constantes.CAMPOS_SECCION,len(constantes.CAMPOS_SECCION),[constantes.CLAVE_SECCION],[id_secc],["and"])
            if(data_secc!=[]):
                conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                data_areas=[]
                data_areas_temp=conexion_bd.get_allData(constantes.CAMPOS_AREA_FORMACION,len(constantes.CAMPOS_AREA_FORMACION),["incorporada"],["Si"],["and"])
                conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                for ar in data_areas_temp:
                   id_years=ar[2]
                   field_in=year[0]+"_año"
                   data_years=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],1,[constantes.CLAVE_AÑOS_INCORPORADOS,field_in],[id_years,"True"],["and","and"])
                   if(data_years!=[]):
                       data_areas.append(ar[0])
                if(data_areas!=[]):
                    conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                    data_estuds=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_SECCION],[data_secc[0][0]],["and"])
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
                            data_estatus=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_ESTUD],[data_estuds[i][2]],["and"])
                            conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                            data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_estuds[i][1]],["and"])
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
                                    calif=conexion_bd.get_allData(["valor"],1,[constantes.CLAVE_ESTUDIANTE,"año",constantes.CLAVE_AREA_FORMACION],[data_estuds[i][0],year[0],temp_area],["and","and","and"]) 
                                    if(calif!=[]):
                                        if(con_notas):
                                             temp_data.append(calif[0][0])
                                    else:
                                        if(con_notas):
                                             temp_data.append("05")
                                        id_next_calif=data_estuds[i][0]+"-"+temp_area+year[0]
                                        data_next_calif=[id_next_calif,data_estuds[i][0],year[0],temp_area,"05",time_object.get_fecha()]
                                        conexion_bd.add_data(data_next_calif)
                                        
                                nombres.append(temp_data)  
                        dat=[nombres,areas_list,year[0]+"-"+letra+" ("+turno+")",year[0]]                        
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
        fields=pnl.get_comps_byTag("field")
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
             dat_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA))
             if(parte=="mat pendiente"):
                 conexion_bd.set_tabla(constantes.TABLA_FECHA)
                 for i in range(0,len(data_send)):                     
                     data_send[i][1]=time_object.get_next_date2(data_send[i][1],4)
                     data_fecha=[dat_cronog[0][0]+"-momento1-"+razones_send[i][0],"momento 1",dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]
                     if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                         conexion_bd.add_data(data_fecha)
                     else:
                        conexion_bd.update_data(["fecha","fecha_cierre","modificado"],[data_fecha[4],data_fecha[5],time_object.get_fecha()],3,[ constantes.CLAVE_FECHA],[data_fecha[0]],["and"]) 
             elif(parte=="general"):
                   conexion_bd.set_tabla(constantes.TABLA_FECHA)
                   for i in range(0,len(data_send)):
                      data_fecha=[dat_cronog[0][0]+"-momento 1-"+razones_send[i][0],"momento 1",dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]           
                      if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                         conexion_bd.add_data(data_fecha)
                      else:
                        conexion_bd.update_data(["fecha","fecha_cierre","modificado"],[data_fecha[4],data_fecha[5],time_object.get_fecha()],3,[ constantes.CLAVE_FECHA],[data_fecha[0]],["and"])    
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
                              data_mom1=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 1"],["and"])
                              if(data_mom1[0][2]=="true"):
                                 abierto="true"
                          elif(mom=="momento 3"):
                              data_mom2=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 2"],["and"])
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
                             conexion_bd.update_data(["fecha_limite","hora_limite","fecha_inicio","modificado"],[data_send[i][1],"00:00:00",data_send[i][0],time_object.get_fecha()],4,[constantes.CLAVE_MOMENTO],[mom],["and"])
                      else:
                          conexion_bd.set_tabla(constantes.TABLA_FECHA)   
                          data_fecha=[dat_cronog[0][0]+"-"+mom+"-"+razones_send[i][0],mom,dat_cronog[0][0],razones_send[i][0],data_send[i][0],data_send[i][1],time_object.get_fecha()]           
                          if(conexion_bd.id_exist(constantes.CLAVE_FECHA,data_fecha[0])==False):
                             conexion_bd.add_data(data_fecha)
                          else:
                            conexion_bd.update_data(["fecha","fecha_cierre","modificado"],[data_fecha[4],data_fecha[5],data_fecha[6]],3,[constantes.CLAVE_FECHA],[data_fecha[0]],["and"])             
             usr.add_action_historial(["editar cronograma",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","editar cronograma","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist) 
             General.show_message("cronograma actualizado exitosamente","cronograma actualizado") 
             usr.reset_data_process(0)
             vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1)
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
            vent.update_pantallas(constantes.PANTALLA_WELCOME)
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
                 conexion_bd.add_data(data_hist) 
                 General.show_message("cronograma registrado satisfactoriamente","cronograma registrado")
             else:
                 #Crongram Update
                 if(General.show_confirmDialog("actualizar el cronograma indicado?","registrar cronograma")!=True):
                      return
                 conexion_bd.update_data(["inicio","cierre","modificado"],[inicio,cierre,time_object.get_fecha()],3,[constantes.CLAVE_CRONOGRAMA],[periodo],["and"])
                 usr.add_action_historial(["modificar cronograma",time_object.get_fecha()])
                 conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                 id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                 data_hist=[ id_hist,usr.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","modificar cronograma","",time_object.get_fecha()]
                 conexion_bd.add_data(data_hist) 
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
             mom_dat=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO))
             if(mom_dat!=[]):
               for i in range(0,len(mom_dat)):
                  if(mom_dat[i][0]=="momento 3"):
                      if(mom_dat[i][2]=="true"):
                             last_moment_close=True      
               if(last_moment_close==False):
                 conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                 if(conexion_bd.get_allData(-1,-1)!=[]):
                    General.show_error("no se puede eliminar el cronograma","cronograma no borrable")
                    return   
             conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
             id_cronog=pnl.get_comp_byName("año_escolar").get_text()
             data_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA),[constantes.CLAVE_CRONOGRAMA],[id_cronog],["and"])
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
             conexion_bd.add_data(data_hist) 
             General.show_message("cronograma borrado exitosamente","cronograma borrado")
             cls.show_planificar_cronogOption(usr,vent,True)         
             pnl.get_comp_byName("acciones").set_selected_index(0)

        else:
           if(accion.startswith("editar fechas: momento")):
              mom=""
             
              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
              dat_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 1"],["and"])
              if(dat_mom!=[]):
                  if(accion=="editar fechas: momento1"):
                     mom="momento 1"
                     if(dat_mom[0][2]=="false"):
                       vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG4)
                       if(dat_mom[0][6]=="" or dat_mom[0][6]==" "):
                           pnl=vent.panelActual
                           conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                           d_crong=conexion_bd.get_allData(None,None)
                           if(d_crong!=[]):
                              inicio_c=d_crong[0][1].split("/")
                              conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                              pnl.get_comp_byName("inicio").set_text(str(inicio_c[0])+"/"+str(inicio_c[1])+"/"+str(inicio_c[2]))
                     else:
                        General.show_message("el momento academico ya ha culminado","cronograma de momento no modificable")
                        return  
                  elif(accion=="editar fechas: momento 2"):
                      mom="momento 2"
                      dat_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 2"],["and"])
                      if(dat_mom!=[]):
                         if(dat_mom[0][2]=="false"):
                            vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG5)
                         else:
                           General.show_message("el segundo momento academico ya ha culminado","cronograma de momento no modificable")
                           return
                      else:
                         vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG5)    
                  elif(accion=="editar fechas: momento 3"):
                      mom="momento 3"
                      dat_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 2"],["and"])
                      if(dat_mom!=[]):
                            dat_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO],["momento 3"],["and"])
                            if(dat_mom!=[]):
                                if(dat_mom[0][2]=="false"):
                                     vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG6)
                                else:
                                    General.show_message("el tercer momento  academico ya ha culminado ","cronograma de momento no modificable")
                                    return
                            else:
                               vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG6)
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
                  data_mom=conexion_bd.get_allData(["fecha_inicio","fecha_limite","abierto","culminado"],4,[constantes.CLAVE_MOMENTO],[mom],["and"])
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
                    data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_MOMENTO],[razones[i],mom],["and","and"])
                    if(data_t!=[]):
                       comp=pnl.get_comp_byName(razones[i])
                       comp.set_text(data_t[0][0])
                       if(double_fields[i]==True):
                         comp_s=pnl.get_comp_byName("cierre "+razones[i])
                         comp_s.set_text(data_t[0][1])
           else:
           
             if(accion=="editar fechas: materia pend."):
                vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG3)
                conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                dat_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA))
                pnl=vent.panelActual 
                conexion_bd.set_tabla(constantes.TABLA_FECHA)
                razones=["materia pendiente 1","materia pendiente 2","materia pendiente 3","materia pendiente 4","revision"]
                for i in range(0,len(razones)):
                  data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_CRONOGRAMA],[razones[i],dat_cronog[0][0]],["and","and"])
                  if(data_t!=[]):
                      comp= pnl.get_comp_byName(razones[i])
                      comp.set_text(data_t[0][0])
             elif(accion=="editar fechas: inscripcion"):
                vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG2)
                conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                dat_cronog=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"inicio","cierre"],3)
                pnl=vent.panelActual   
                pnl.get_comp_byName("inicio").set_text(dat_cronog[0][1])
                pnl.get_comp_byName("cierre").set_text(dat_cronog[0][2])
                conexion_bd.set_tabla(constantes.TABLA_FECHA)
                razones=["inscripcion nuevo ingreso","inscripcion estudiantes regulares"]
                doble_field=[True,True]
                for i in range(0,len(razones)):
                  data_t=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_CRONOGRAMA],[razones[i],dat_cronog[0][0]],["and","and"])
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
                   vent.update_pantallas(constantes.PANTALLA_PROCESO_PLANIFICACION)
                   return
            vent.update_pantallas(constantes.PANTALLA_PLANIFIC_CRONOG1)
            pnl=vent.panelActual
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        data_cronog=conexion_bd.get_allData(constantes.CAMPOS_CRONOGRAMA,len(constantes.CAMPOS_CRONOGRAMA))
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
        conexion_bd.delete_data([constantes.CLAVE_CRONOGRAMA],[id_cronog],["and"])
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        conexion_bd.delete_data([constantes.CLAVE_CRONOGRAMA],[id_cronog],["and"])
        #Reset Sections
        for i in range(0,5):
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            if(conexion_bd.id_exist("año",str(i+1))==True):
                seccs_year=conexion_bd.get_allData([constantes.CLAVE_HORARIO,constantes.CLAVE_SECCION],2,["año"],[str(i+1)],["and"])
                conexion_bd.update_data(["total_estud","modificado"],["0",time_object.get_fecha()],2,["año"],[str(i+1)],["and"])
                for secc in seccs_year:
                    clave_secc=secc[1]
                    clave_hor=secc[0]
                    conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                    conexion_bd.update_data(["src_hor"],[""],1,[constantes.CLAVE_HORARIO],[clave_hor],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)   
                    d_estud=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],1,[constantes.CLAVE_SECCION],[clave_secc],["and"])
                    conexion_bd.update_data([constantes.CLAVE_SECCION],["default"],1,[constantes.CLAVE_SECCION],[clave_secc],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                    for estud in d_estud:
                        estatus_estud=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estud[0]],["and"])
                        if(estatus_estud!=[]):
                            if(estatus_estud[0][0]!="graduado"):
                                conexion_bd.update_data(["estatus"],["inactivo"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estud[0]],["and"])
               
                              
        #Reset Temporal Califications               
        conexion_bd.set_foregein_check(False)      
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        conexion_bd.reset_table()
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        conexion_bd.reset_table()
        conexion_bd.set_foregein_check(True) 
               
        #Reset Academic Moments
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        for i in range(0,3):
            if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,"momento "+str(i+1))==True):
                conexion_bd.delete_data([constantes.CLAVE_MOMENTO],["momento "+str(i+1)],["and"])
               
    #Determine and Execute the Required Actions for The Planification of Formats Process
    @classmethod
    def Determine_Action_Planification_format(cls,usr,vent):
        pnl=vent.panelActual
        accion=pnl.get_comp_byName("accion_box").get_selected_value()
        time_object=tiempo()
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
                vent.update_pantallas(constantes.PANTALLA_PLANIF_FORMATO2)  
                pnl=vent.panelActual
                src=dat[0][3]
                url=constantes.SERVER+src
                response=requests.get(url)
                if(response.status_code>400):
                   General.show_error("error obteniendo data del servidor","error de data del server")
                   return
                data_doc=[constantes.PANTALLA_PLANIF_FORMATO2,"cols_list",refe]
                file_dat=response.content
                documento.request(vent.raiz,file_dat,3,data_doc)
              else:
                General.show_message("por favor seleccione un formato","formato no valido")        
          elif(accion=="eliminar formato"):
              if(dat!=[]):
                id_f=dat[0][0]
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                if(General.show_confirmDialog("esta seguro que desea eliminar este formato?","borrar formato")!=True):
                     return
               
                data_form=conexion_bd.get_allData(constantes.CAMPOS_FORMATO,len(constantes.CAMPOS_FORMATO),["src_form"],[dat[0][3]],["and"])
                if(len(data_form)<=1):
                  url_delete=constantes.SERVER+"delete_file.php"
                  path={"directorio":"./","nombre":usr.get_data_process()[0][3]}
                  response_del=requests.post(url_delete,params=path)
                  res_delete=response_del.text.strip()
                conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                conexion_bd.delete_data([constantes.CLAVE_FORMATO],[id_f],["and"]) 
                conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                conexion_bd.delete_data([constantes.CLAVE_FORMATO],[id_f],["and"]) 
                lista=pnl.get_comp_byName("formatos_list")
                data_form=conexion_bd.get_allData(constantes.CAMPOS_FORMATO,len(constantes.CAMPOS_FORMATO))
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
                conexion_bd.add_data(data_hist)
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
               documento.request(vent.raiz,ruta,10,[src],True)
             else:
               General.show_message("por favor seleccione un formato","formato no valido")
        else:
          General.show_message("por favor seleccione una accion","accion invalida")
          
       
    #Verify if Finish The Cronogram or Academic Moments When the an User Loggin
    @classmethod
    def verificar_caudicidad(cls,usr,vent):
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cronogs=conexion_bd.get_allData([constantes.CLAVE_CRONOGRAMA,"cierre"],2)
        time_object=tiempo()
        user_t=usr.get_credentials()[2]
        
        #Verifications Over Cronogram
        if(cronogs!=[] and (user_t=="admin" or user_t=="coordinador")==True):
            fecha_culminado=cronogs[0][1]
            if(time_object.is_previous(time_object.get_fecha(),fecha_culminado)==False ):
               #Academic Year is Finished
               if(General.show_confirmDialog("cronograma finalizado,desea borrarlo?","borrar cronograma")==True):
                   conexion_bd.set_tabla(constantes.TABLA_FECHA)
                   conexion_bd.delete_data([constantes.CLAVE_CRONOGRAMA],[cronogs[0][0]],["and"])
                   conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
                   conexion_bd.delete_data([constantes.CLAVE_CRONOGRAMA],[cronogs[0][0]],["and"])
                   #Reset Section
                   for i in range(0,5):
                      conexion_bd.set_tabla(constantes.TABLA_SECCION)
                      if(conexion_bd.id_exist("año",str(i+1))==True):
                          seccs_year=conexion_bd.get_allData([constantes.CLAVE_HORARIO,constantes.CLAVE_SECCION],2,["año"],[str(i+1)],["and"])
                          conexion_bd.update_data(["total_estud","modificado"],["0",time_object.get_fecha()],2,["año"],[str(i+1)],["and"])
                          for secc in seccs_year:
                             clave_secc=secc[1]
                             clave_hor=secc[0]
                             conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                             conexion_bd.update_data(["src_hor"],[""],1,[constantes.CLAVE_HORARIO],[clave_hor],["and"])
                             conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)   
                             d_estud=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],1,[constantes.CLAVE_SECCION],[clave_secc],["and"])
                             conexion_bd.update_data([constantes.CLAVE_SECCION],["default"],1,[constantes.CLAVE_SECCION],[clave_secc],["and"])
                             conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
                             for estud in d_estud:
                                estatus_estud=conexion_bd.get_allData(["estatus"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estud[0]],["and"])
                                if(estatus_estud!=[]):
                                     if(estatus_estud[0][0]!="graduado"):
                                         conexion_bd.update_data(["estatus"],["inactivo"],1,[constantes.CLAVE_ESTATUS_ESTUD],[estud[0]],["and"])
                                  
                   #Reset Temporals Califications
                   conexion_bd.set_foregein_check(False)      
                   conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                   conexion_bd.reset_table()
                   conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
                   conexion_bd.reset_table()
                   conexion_bd.set_foregein_check(True) 
                   #Reset Academic Moments
                   conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                   for i in range(0,3):
                      if(conexion_bd.id_exist(constantes.CLAVE_MOMENTO,"momento "+str(i+1))==True):
                         conexion_bd.delete_data([constantes.CLAVE_MOMENTO],["momento "+str(i+1)],["and"])
                   General.show_message("cronograma borrado exitosamente","cronograma borrado")
            
         
        #Verifications Over Academic Moments
        conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
        moms=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO))
        if(moms!=[]):
            momentos_activos=0
            for i in range(0,len(moms)):
               if(moms[i][2]=="false" and moms[i][1]=="true" and moms[i][4]!=""):
                       momentos_activos+=1
                       limite=moms[i][4]
                       if(time_object.is_previous(time_object.get_fecha(),limite)==False):
                            #Academic Moment is Finished and Activate the Next Moment
                            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                            conexion_bd.update_data(["abierto","culminado"],["false","true"],2,[constantes.CLAVE_MOMENTO],[moms[i][0]],["and"])
                            if(moms[i][0]=="momento 1"):
                               next_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO,"culminado","abierto"],["momento 2","false","false"],["and","and","and"])
                               if(next_mom!=[]):
                                  if(next_mom[0][6]!=""):
                                     next_inicio=next_mom[0][6]
                                     if(time_object.is_previous(next_inicio,time_object.get_fecha(),False)==True):
                                        conexion_bd.update_data(["abierto"],["true"],1,[constantes.CLAVE_MOMENTO],[next_mom[0][0]],["and"])
                            elif(moms[i][0]=="momento 2"):
                         
                                  next_mom=conexion_bd.get_allData(constantes.CAMPOS_MOMENTO,len(constantes.CAMPOS_MOMENTO),[constantes.CLAVE_MOMENTO,"culminado","abierto"],["momento 3","false","false"],["and","and","and"])
                                  if(next_mom!=[]):
                                     if(next_mom[0][6]!=""):
                                        next_inicio=next_mom[0][6]
                                        if(time_object.is_previous(next_inicio,time_object.get_fecha(),False)==True):
                                            conexion_bd.update_data(["abierto"],["true"],1,[constantes.CLAVE_MOMENTO],[next_mom[0][0]],["and"])
               elif(moms[i][2]=="true" and moms[i][1]=="true"):
                  if(moms[i][4]!="" and moms[i][5]!=""):
                      if(time_object.is_previous(moms[i][4],time_object.get_fecha(),False)):
                         if(time_object.is_previous_time(moms[i][5],time_object.get_tiempo())):
                             conexion_bd.update_data(["abierto"],["false"],1,[constantes.CLAVE_MOMENTO],[moms[i][0]],["and"])
            if(momentos_activos==0):
               activado=False
               for i in range(0,len(moms)):
                 if(activado==False):
                    if(moms[i][2]=="false" and moms[i][1]=="false" and moms[i][6]!=""):
                         inicio=moms[i][6]
                         if(time_object.is_previous(inicio,time_object.get_fecha(),False)==True):
                            conexion_bd.set_tabla(constantes.TABLA_MOMENTO)
                            conexion_bd.update_data(["abierto"],["true"],1,[constantes.CLAVE_MOMENTO],[moms[i][0]],["and"])
                            activado=True
                            break
             