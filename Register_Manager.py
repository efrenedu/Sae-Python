from General import General
from conexion_bd import conexion_bd
from tiempo import tiempo
from constantes import constantes
import requests
import os

#Manage the Operations Required for the Registers of System
class Register_Manager:

    #Verify the data required for timetables registers
    @classmethod 
    def verify_disponibilty_data(cls,first_index,second_index,data,val):
    
        if(data[first_index]!="no disponible" and val=="no disponible"):
            return -7
        if(data[first_index]=="no disponible" and val!="no disponible"):
           return -8  
        if(data[first_index]==val):
           if(val=="no disponible"):
              return 1
           else:
              return -6 
        time_object=tiempo()        
        first_time=""
        second_time=""
        validas_horas=False
        if(data[second_index]=="tarde"):
            temp1=data[first_index].split("PM")[0]
            temp2=val.split("PM")[0]
            if(len(temp1)>1 and len(temp2)>1):
                horas1=int(temp1.split(":")[0])
                horas2=int(temp2.split(":")[0])
                if(horas1!=12):
                    horas1=horas1+12
                if(horas2!=12):
                    horas2=horas2+12
                first_time=str(horas1)+":"+temp1.split(":")[1]+":00"
                second_time=str(horas2)+":"+temp1.split(":")[1]+":00"  
        else:
            first_val=data[first_index]
            if(len(first_val.split("AM"))>1):
                first_time=first_val.split("AM")[0]+":00"
            else:            
                first_time=first_val.split("PM")[0]+":00"
            if(len(val.split("AM"))>1):
                second_time=val.split("AM")[0]+":00"
            else:
               second_time=val.split("PM")[0]+":00"
        if(first_time!="" and second_time!=""):       
            if(time_object.is_previous_time(first_time,second_time)==True):
                validas_horas=True     
        if(validas_horas==True):
            data[first_index]+="-"+val
            return 0
        else:
            return -9
                   
    #Register or Update the Data for Disponibilty of TimeTables for Workers
    @classmethod
    def registrar_dispHorario(cls,user,vent,update=False):
        from event_manager import Event_manager 
        pnl=vent.panelActual
        combos=pnl.get_comps_byTag("combo")
        lista=pnl.get_comp_byName("lista_personal")
        radios=pnl.get_comp_byTag("radio")
        time_object=tiempo()
        data=["","","","","","","","",time_object.get_fecha()]
        valido=0
        conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
        dias_asignados=0

        if(lista.get_count()>0):
           empleado=lista.get_selected_value()
           if(empleado!="elejir" and empleado!="elegir"):
              ced=empleado.split("-")
              if(len(ced)==3):
                 ced=ced[0]+"-"+ced[1]
              elif(len(ced)==2):
                 ced=ced[0]
              data[1]=ced
           else:
              valido=-2  
        else:
          valido=-1
          
        if(update==False ):
          if(valido==0):
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[1]],"conditions_Verify":["="]}              
            data_hors=conexion_bd.get_allData([],cond_data)
            if(data_hors==[]):
              data[0]=conexion_bd.generate_id()
            else:
              valido=-3
        else:
           if(valido==0 and data[1]!=""):
              conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
              cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[1]],"conditions_Verify":["="]}              
              data[0]=conexion_bd.get_allData([constantes.CLAVE_DISP_HORARIO],cond_data,["and"])[0][0]
        data[2]=radios.get_selected_value()
        
        #Verifications over days
        for i in range(0,len(combos)):
            if(combos[i].get_id()=="desde_L"):
               data[3]=combos[i].get_selected_value()
            elif(combos[i].get_id()=="hasta_L" and valido==0 ):
               valor=combos[i].get_selected_value()
               valido=cls.verify_disponibilty_data(3,2,data,valor)
               if(valido==0 or valido==1):
                  if(valido==1):
                     valido=0
                  else:
                     dias_asignados+=1
            elif(combos[i].get_id()=="desde_M" ):
               data[4]=combos[i].get_selected_value() 
            elif(combos[i].get_id()=="hasta_M" and valido==0):
               valor=combos[i].get_selected_value()
               valido=cls.verify_disponibilty_data(4,2,data,valor)
               if(valido==0 or valido==1):
                  if(valido==1):
                     valido=0
                  else:
                     dias_asignados+=1
            elif(combos[i].get_id()=="desde_Mi"):
                data[5]=combos[i].get_selected_value()  
            elif(combos[i].get_id()=="hasta_Mi" and valido==0):
               valor=combos[i].get_selected_value()
               valido=cls.verify_disponibilty_data(5,2,data,valor)
               if(valido==0 or valido==1):
                  if(valido==1):
                     valido=0
                  else:
                     dias_asignados+=1
            elif(combos[i].get_id()=="desde_J"):
                data[6]=combos[i].get_selected_value() 
            elif(combos[i].get_id()=="hasta_J" and valido==0): 
                valor=combos[i].get_selected_value()
                valido=cls.verify_disponibilty_data(6,2,data,valor)
                if(valido==0 or valido==1):
                  if(valido==1):
                     valido=0
                  else:
                     dias_asignados+=1
            elif(combos[i].get_id()=="desde_V"):
               data[7]=combos[i].get_selected_value()
            elif(combos[i].get_id()=="hasta_V" and valido==0):
                valor=combos[i].get_selected_value()
                valido=cls.verify_disponibilty_data(7,2,data,valor)
                if(valido==0 or valido==1):
                  if(valido==1):
                     valido=0
                  else:
                     dias_asignados+=1
            if(valido!=0):
                   i=len(combos)
                   
        if(dias_asignados<=0 and valido==0):
            valido=-4
        if(valido==0):
            if(General.show_confirmDialog("registrar disponibilidad de horario?","registrar")!=True):
               return
            conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
            if(update==False):
                #Update the Register
                conexion_bd.add_data(data)
                user.add_action_historial(["registro de desiponib. horario",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","disponib. horario","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("disponibilidad de horario registrada satisfactoriamente","registro exitoso")
                vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
                
            else:
                #Make the Register
                conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
                vals_update={"turno":data[2],"disp_lunes":data[3],"disp_martes":data[4],"disp_miercoles":data[5],"disp_jueves":data[6],"disp_viernes":data[7],"modificado":time_object.get_fecha()}
                cond_data={"conditions_Names":[constantes.CLAVE_DISP_HORARIO],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
                conexion_bd.update_data(vals_update,cond_data)
                user.add_action_historial(["actualizar disponib. horario",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","disponib. horario","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("disponibilidad de horario actualizada satisfactoriamente","registro exitoso")
                vent.update_pantallas(constantes.PANTALLA_WELCOME,user) 
        else:
            if(valido==-1):
               General.show_message("error,no hay personal registrado  ","no existe personal")
            elif(valido==-2):
               General.show_message("por favor seleccione un miembro del personal","no se ha seleccionado personal") 
            elif(valido==-3):
               General.show_message("ya se ha registrado disponibilidad de horario para este empleado","disponibilidad de horario ya existente") 
            elif(valido==-4):
               General.show_message("por favor asigne disponilidad para al menos un dia de la semana","no se ha asignado ningun dia") 
            elif(valido==-5):
               General.show_message("nombre del empleado seleccionado erroneo","error de data empleado") 
            elif(valido==-6):
                General.show_message("Las horas de entrada y salida no deben coincidir", "Horas de entrada y salida no validas")
            elif(valido==-7):
                General.show_message("por favor indique una hora de salida valida","hora de salida invalida")
            elif(valido==-8):
                 General.show_message("por favor indique una hora de entrada valida","hora de entrada invalida")
            elif(valido==-9):
                 General.show_message("la hora de entrada debe ser inferior a la de salida","horas invalidas")
    
    #Register or Update a Format
    @classmethod
    def registrar_formato(cls,user,vent,update=False):
       from event_manager import Event_manager
       pnl=vent.panelActual
       fields=pnl.get_comps_byTag("field")
       valido=0
       time_object=tiempo()
       data=["","",time_object.get_fecha()]
       tipo_value=""
       combo=pnl.get_comp_byTag("combo")
       tipo_value=combo.get_selected_value()
       data[0]= tipo_value
       conexion_bd.set_tabla(constantes.TABLA_FORMATO)
       for i in range(0,len(fields)):
          if(valido==0):
                if(fields[i].get_id()=="destino_file"):
                    valor=fields[i].get_text()
                    temp_name=valor.split("/")
                    temp_valor="formatos/"+ temp_name[len(temp_name)-1]
                    conexion_bd.set_tabla(constantes.TABLA_FORMATO)
                    cond_data={"conditions_Names":["src_form"],"condition_Types":["and"],"conditions_Values":[temp_valor],"conditions_Verify":["="]}              
                    temp_dat=conexion_bd.get_allData([],cond_data)
                    if(len(temp_dat)>=1):   
                        if(update==False):
                            valido=-8
                        else:
                            cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
                            data_form=conexion_bd.get_allData([],cond_data)
                            if((data_form[0][1]==temp_valor)==False):
                                valido=-8
                    if(valido==0):
                        if(valor.endswith(".pdf")):
                            data[1]=valor
                        elif(valor.endswith(".xlsx")):
                            data[1]=valor
                        else:
                           valido=-3
       if((tipo_value=="elejir" or tipo_value=="elegir") and valido==0):
            valido=-4
       else:
          if(update==False):
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            if(valido==0):
              cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[tipo_value],"conditions_Verify":["="]}              
              if(conexion_bd.get_allData([],cond_data)!=[]):
                 valido=-7
              else:
                data[0]=tipo_value   
       if(valido==0):
          if(data[0]=="nuevo"):
             data[0]=pnl.get_comp_byName("nombre_val").get_text()
             if(General.is_valid(data[0],constantes.CADENA_SOLOTEXTO,True,3)==False):
                     General.show_message("por favor indique un nombre de formato valido","nombre de formato invalido")
                     return
             if(data[0]=="nuevo"):
                  General.show_message("por favor indique un nombre valido al nuevo tipo de formato","nombre de formato no valido")
                  return        
          if(update==False): 
            if(General.show_confirmDialog("registrar formato?","registrar")!=True):
               return
            url=constantes.SERVER+"upload.php"
            with open(data[1],"rb") as temp_file:
               files={'file':temp_file}
               response=requests.post(url,files=files)
               res=response.text.strip()
               data[1]=res 
            conexion_bd.set_tabla(constantes.TABLA_FORMATO)
            conexion_bd.add_data(data)
            user.add_action_historial(["registrar formato",time_object.get_tiempo()])
            conexion_bd.set_tabla(constantes.TABLA_REPORTE)
            id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
            data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","formato","",time_object.get_fecha()]
            conexion_bd.add_data(data_hist,True) 
            General.show_message("formato registrado satisfactoriamente","registro exitoso" )     
            vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
          else:
             if(General.show_confirmDialog("Modificar archivos del formato?","modificar")!=True):
               return
             cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}                 
             old_src=conexion_bd.get_allData(["src_form"],cond_data)[0][0]           
             conexion_bd.set_tabla(constantes.TABLA_FORMATO)
             cond_data={"conditions_Names":["src_form"],"condition_Types":["and"],"conditions_Values":[old_src],"conditions_Verify":["="]}              
             data_form=conexion_bd.get_allData([],cond_data)
             if(data[1].startswith("formatos")==False):
                if(len(data_form)<=1):
                  url_delete=constantes.SERVER+"delete_file.php"
                  path={"directorio":"./","nombre":old_src}
                  response_del=requests.post(url_delete,params=path)
                  res_delete=response_del.text.strip()
                url=constantes.SERVER+"upload.php"
                with open(data[1],"rb") as temp_file:
                    files={'file':temp_file}
                    response=requests.post(url,files=files)
                    res=response.text.strip()
                    data[1]=res  
             id_form=data[0]             
             conexion_bd.set_tabla(constantes.TABLA_FORMATO)
             values={"src_form":data[1],"modificado":data[2]}
             cond_data={"conditions_Names":[constantes.CLAVE_FORMATO],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
             conexion_bd.update_data(values,cond_data)
             user.add_action_historial(["actualizar formato",time_object.get_tiempo()])
             conexion_bd.set_tabla(constantes.TABLA_REPORTE)
             id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
             data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","formato","",time_object.get_fecha()]
             conexion_bd.add_data(data_hist,True)
             General.show_message("formato actualizado satisfactoriamente","registro exitoso" )     
             user.reset_data_process(0)
             vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
           if(valido==-1):
                General.show_message("por favor escriba un nombre valido para el formato","nombre de formato no valido" )
           elif(valido==-2):
                General.show_message("el nombre del formato ya se ha registrado","formato ya existe" )
           elif(valido==-3):
                General.show_message("el formato debe ser un archivo .pdf  o .xlsx","formato del archivo no valido" )
           elif(valido==-4):
                General.show_message("por favor seleccione el tipo de formato a registrar","valor del tipo de formato no valido" )
           elif(valido==-5):
                General.show_message("por favor suba una firma en formato .png","formato de firma invalido")
           elif(valido==-6):
                General.show_message("por favor escriba un numero en el indicador de la fila de fin del encabezado ","valor invalido en el indicador de fila de fin de encabezado")
           elif(valido==-7):
               General.show_message("ya existe un formato de "+tipo_value,"tipo de formato ya existente")
           elif(valido==-8):
               General.show_message("archivo ya existe en servidor, por favor suba un archivo con otro nombre","archivo repetido en el servidor")

  
    #Register a Calification
    @classmethod
    def registrar_calificacion(cls,user,vent):  
       from estudiante import estudiante
       from event_manager import Event_manager
       pnl=vent.panelActual
       valido=0  
       motivo_comp=pnl.get_comp_byName("motivo")
       calif_comp=pnl.get_comp_byName("calific_val")
       motivo=""
       calif_val=""
       if(motivo_comp!=None):
         motivo=motivo_comp.get_text()
       if(calif_comp!=None):
          calif_val=calif_comp.get_text() 
       if(General.is_valid(calif_val,constantes.CADENA_SOLONUMERO,False,0)==False):
           valido=-1    
       val_num=0    
              
       if(valido==0):
          val_num=int(calif_val)
          if((val_num>=0 and val_num<=20)==False):
             valido=-2
       
       if(valido==0):
            time_object=tiempo()
            data=["","",calif_val,"",time_object.get_fecha()]
            dat_rend=user.get_data_process()[0]
            if(General.show_confirmDialog("registrar Nueva Calificacion?","registrar")!=True):
               return
            estud=estudiante()
            res=estud.nueva_calific(data,dat_rend,time_object.get_fecha())
            if(res[0]==0):
                user.add_action_historial(["registro de calificacion",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"proceso","nueva calificacion",motivo,time_object.get_fecha()]
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
            else:
                if(res[0]==-1):
                    General.show_message("error al guardar data","error inesperado")
                elif(res[0]==-2):
                    General.show_message("el estudiante ya tiene registrada una calificacion para el area, momento academico y numero de evaluacion indicada","calificacion ya registrada")       
       else:
          if(valido==-1):
              General.show_message("por favor ingrese un valor numerico","calificacion invalida")
          elif(valido==-2):
             General.show_message("la calificacion debe ser un valor entre 1 y 20","calificacion invalida")
    
    
    #Register or Update a Formation Area
    @classmethod
    def registar_area(cls,user,vent,update=False):
       pnl=vent.panelActual
       fields=pnl.get_comps_byTag("field")
       list_areas=pnl.get_comp_byName("areas")
       selected_area=""
       if(list_areas!=None):
          selected_area=list_areas.get_selected_value()
       pnl=vent.panelActual
       time_object=tiempo()
       data_disp_areas=["","","","","","",time_object.get_fecha()]
       data=["","","",time_object.get_fecha()]
       valido=0
       modificada=""
       old_a=""
       conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
       for i in range(0,len(fields)):
          if(fields[i].get_id()=="area_ra"):
              val=fields[i].get_text().lower()
              data[0]=val
              if(General.is_valid(val,constantes.CADENA_SOLOTEXTO,True,1)==False):
                   valido=-1
                   break
              if(valido==0 and update==False):
                 existe=conexion_bd.id_exist(constantes.CLAVE_AREA_FORMACION,val)
                 if(existe):
                     valido=-2
       if(update==True):
          data[1]=pnl.get_comp_byName("incorporada").get_selected_value()
       else:         
         data[1]="Si"  
       checks=pnl.get_comps_byTag("check")
       count=1
       years_disp=0
       for i in range(0,len(checks)):
           if(checks[i].is_selected()):
                data_disp_areas[count]="True"
                years_disp=years_disp+1
           else:
                data_disp_areas[count]="False"
           count+=1
           
       if(years_disp==0):
            General.show_message("el area de formacion debe estar disponible para al menos 1 año de curso","años incrporados invalidos")
            return
       if(valido==0):
           if(update==False):
               if(data[0]=="nuevo" or data[0]=="nueva"):
                  General.show_message("por favor escriba un nombre de area valido","nombre de area de formacion invalido")
                  return
               if(General.show_confirmDialog("registrar area de formacion?","registrar")!=True):
                 return
               conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
               data_disp_areas[0]=conexion_bd.generate_id(True,constantes.CLAVE_AÑOS_INCORPORADOS)
               conexion_bd.add_data(data_disp_areas)
               data[2]=data_disp_areas[0]
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               conexion_bd.add_data(data)
               user.add_action_historial(["registro de area de formacion",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","area form.","",time_object.get_fecha()]
               conexion_bd.add_data(data_hist,True) 
               General.show_message("area de formacion registrada satisfactoriamente","registro exitoso")
               if(modificada!=""):
                  General.show_message("el nombre del area fue modificado de "+old_a+" a "+modificada,"nombre de area modificado")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
           else:
               if(General.show_confirmDialog("actualizar area de formacion?","actualizar")!=True):
                 return
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                 
               if(data[0]!=selected_area):
                  #Modify Id of Formation Area
                  cond_data={"conditions_Names":[constantes.CLAVE_AREA_FORMACION],"condition_Types":["and"],"conditions_Values":[selected_area],"conditions_Verify":["="]}              
                
                  old_dat=conexion_bd.get_allData([],cond_data)
                  if(old_dat==[]):
                    General.show_message("Error al Actualizar Nombre del Area","Nombre del Area Invalido")
                    return
                  next_data=[data[0],old_dat[0][1],old_dat[0][2],old_dat[0][3]]
                  
                  conexion_bd.add_data(next_data)
                  conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
                  conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:data[0]},cond_data)
                  conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                  conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:data[0]},cond_data)
                  conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                  conexion_bd.update_data({constantes.CLAVE_AREA_FORMACION:data[0]},cond_data)
                  conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
                  conexion_bd.delete_data(cond_data)

               cond_data={"conditions_Names":[constantes.CLAVE_AREA_FORMACION],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
               fields_values={"incorporada":data[1],"modificado":time_object.get_fecha()}
               conexion_bd.update_data(fields_values,cond_data)
               id_inc=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],cond_data)
               conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
               values_years={"1_año":data_disp_areas[1],"2_año":data_disp_areas[2],"3_año":data_disp_areas[3],"4_año":data_disp_areas[4],"5_año":data_disp_areas[5],"modificado":time_object.get_fecha()}
               cond_data={"conditions_Names":[constantes.CLAVE_AÑOS_INCORPORADOS],"condition_Types":["and"],"conditions_Values":[id_inc[0][0]],"conditions_Verify":["="]}              
               conexion_bd.update_data(values_years,cond_data)
               user.add_action_historial(["actualizar area de formacion",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","area form.","",time_object.get_fecha()]
               conexion_bd.add_data(data_hist,True) 
               General.show_message("area de formacion actualizada satisfactoriamente","actualizacion exitosa")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
           if(valido==-1):
               General.show_message("por favor ingrese un nombre valido","valor invalido")
           elif(valido==-2):
               General.show_message("el area de formacion ya se ha registrado","area ya existe") 
           elif(valido==-3):
               General.show_message("por favor seleccione el area a modificar","area no seleccionada") 
         
    #Register or Update a timeTable for a Worker or Section
    @classmethod
    def registrar_horario(cls,user,vent,update=False):
        time_object=tiempo()
        pnl=vent.panelActual
        data=["","","",time_object.get_fecha()]
        destinatario=""
        fields=pnl.get_comps_byTag("field")
        combos=pnl.get_comps_byTag("combo")
        valido=0
        is_worker=False
        for i in range(0,len(combos)):
          if(valido==0):
            if(combos[i].get_state()==True):
               valor_comp=combos[i].get_selected_value()
               id_comb=combos[i].get_id()
               if(valor_comp!="elejir" and valor_comp!="elegir"):
                  if(id_comb=="tipo_rh"):
                     if(valor_comp!="seccion"):
                        is_worker=True
                  elif(id_comb=="turno_rh"):
                     data[2]=valor_comp
                  elif(id_comb=="secc_rh"):
                      destinatario=valor_comp
                  elif(id_comb=="personal_rh"):
                       destinatario=valor_comp
               else:
                  if(id_comb=="tipo_rh"):
                     valido=-1
                  elif(id_comb=="turno_rh"):
                     valido=-2
                  elif(id_comb=="secc_rh" and is_worker==False):
                     valido=-3
                  elif(id_comb=="personal_rh" and is_worker==True):
                     valido=-4

        for i in range(0,len(fields)):
         if(valido==0):
           valor_temp=fields[i].get_text()
           if(fields[i].get_id()=="destino_file"):
               if(valor_temp!="" and valor_temp!=" "):
                   if(valor_temp.endswith(".pdf")==False):
                      valido=-6
                   else:
                      data[1]=valor_temp
               else:
                  valido=-6
    
        conexion_bd.set_tabla(constantes.TABLA_HORARIO)
        if(update==False):
          data[0]=conexion_bd.generate_id(True,constantes.CLAVE_HORARIO)
        id_dest=""
        id_name=""
        tabla_dest=""       

        if(is_worker):
            if(valido==0):
              id_t=destinatario.split("-")
              if(len(id_t)==3):
                  id_t=id_t[0]+"-"+id_t[1]
              elif(len(id_t)==2):
                 id_t=id_t[0]
              else:
                 id_t=""
              tabla_dest=constantes.TABLA_TRABAJADOR
              conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
              cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[id_t],"conditions_Verify":["="]}              
              data_t=conexion_bd.get_allData([],cond_data)
              if(update==False):
                  id_dest=id_t
                  id_name=constantes.CLAVE_TRABAJADOR
                  if(data_t[0][5]!="default"):
                       valido=-13
              else:
                  data[0]=data_t[0][5]                  
        else:
            if(valido==0):
              data[2]=pnl.get_comp_byName("turno_seccion").get_text()
              conexion_bd.set_tabla(constantes.TABLA_SECCION)
              cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[destinatario],"conditions_Verify":["="]}              
              data_secc=conexion_bd.get_allData([],cond_data)  
              tabla_dest=constantes.TABLA_SECCION
              if(data_secc!=[]):
                  if(update==False):
                    id_dest=data_secc[0][0]
                    id_name=constantes.CLAVE_SECCION
                    if(data_secc[0][3]!="default" and update==False):
                          valido=-12
                  else:
                     data[0]=data_secc[0][3]
              else:
                valido=-11
        if((valido==0 and id_dest!="" and update==False) or (valido==0 and update==True)):    
            conexion_bd.set_tabla(constantes.TABLA_HORARIO)
            if(update==False):
               #Register
               filename=data[1].split("/")
               if(conexion_bd.id_exist("src_hor","horarios/"+filename[len(filename)-1])):
                   General.show_message("el documento del horario esta ya registrado en el servidor, cambie el nombre e intentelo de nuevo","documento ya existente")
                   return 
               if(General.show_confirmDialog("registrar horario?","registrar")!=True):
                   return    
               url=constantes.SERVER+"upload_horarios.php"
               with open(data[1],"rb") as temp_file:                
                  files={'file':temp_file}
                  response=requests.post(url,files=files)
                  res=response.text.strip()
                  data[1]=res
               conexion_bd.add_data(data)
               conexion_bd.set_tabla(tabla_dest)
               cond_data={"conditions_Names":[id_name],"condition_Types":["and"],"conditions_Values":[id_dest],"conditions_Verify":["="]}              
                
               conexion_bd.update_data({constantes.CLAVE_HORARIO:data[0],"modificado":time_object.get_fecha()},cond_data)
               user.add_action_historial(["registrar horario",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","horario","",time_object.get_fecha()]
               conexion_bd.add_data(data_hist,True)
               General.show_message("registro del horarior realizado satisfactoriamente","horario registrado")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
            else:
               #Update
               if(General.show_confirmDialog("actualizar horario?","actualizar")!=True):
                   return
               conexion_bd.set_tabla(constantes.TABLA_HORARIO)
               if(data[1].startswith("horarios")==False):
                  filename=data[1].split("/")
                  if(conexion_bd.id_exist("src_hor","horarios/"+filename[len(filename)-1])):
                    cond_data={"conditions_Names":[constantes.CLAVE_HORARIO,"src_hor"],"condition_Types":["and","and"],"conditions_Values":[data[0],"horarios/"+filename[len(filename)-1]],"conditions_Verify":["=","="]}              
                    dat_hrs=conexion_bd.get_allData([constantes.CLAVE_HORARIO],cond_data)
                    if(dat_hrs==[]):
                         General.show_message("el documento del horario esta ya registrado en el servidor, cambie el nombre e intentelo de nuevo","documento ya existente")
                         return 
                  url=constantes.SERVER+"upload_horarios.php"
                  with open(data[1],"rb") as temp_file:                
                     files={'file':temp_file}
                     response=requests.post(url,files=files)
                     res=response.text.strip()
                     data[1]=res
                  
               values_fields={"src_hor":data[1],"turno":data[2],"modificado":time_object.get_fecha()}
               cond_data={"conditions_Names":[constantes.CLAVE_HORARIO],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
               conexion_bd.update_data(values_fields,cond_data)
               user.add_action_historial(["actualizar horario",time_object.get_tiempo()])
               conexion_bd.set_tabla(constantes.TABLA_REPORTE)
               id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
               data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","horario","",time_object.get_fecha()]
               conexion_bd.add_data(data_hist,True)
               General.show_message("Actualizacion del horarior realizado satisfactoriamente","horario registrado")
               vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
        else:
            if(valido==-1):
                General.show_message("por favor seleccione el tipo de horario","seleccion un tipo de horario")
            elif(valido==-2):
                General.show_message("por favor seleccione el turno del horario","seleccion un turno para el horario")
            elif(valido==-3):
                General.show_message("por favor seleccione la seccion a la que asignara el horario ","seccion no valida")
            elif(valido==-4):
                General.show_message("por favor seleccione el trabajado al que asignara el horario","trabajador no valido")
            elif(valido==-6):
                 General.show_message("por favor elija un archivo en formato pdf","formato del archivo no valido")
            elif(valido==-7):
                General.show_message("el trabajador ya tiene un horario asignado","horario ya existe")
            elif(valido==-8):
                General.show_message("la seccion ya tiene un horario asignado","horario ya existe")
            elif(valido==-9):
                General.show_message("fallo encontrando datos trabajador","fallo de base de datos")
            elif(valido==-10):
                General.show_message("error de formato del nombre del trabajdor","mal formato de nombre")
            elif(valido==-11):
                 General.show_message("error encontrando data de la seccion","seccion no encontrada")
            elif(valido==-12):
                 General.show_message("la seccion ya tiene un horario registrado","horario de seccion ya registrado")
            elif(valido==-13):
                 General.show_message("el trabajador  ya tiene un horario asignado","horario de trbajador ya registrado")
        
    #Upload Expedent data
    @classmethod
    def upload_expedent(cls,data,index_expedent,index_photo,update,zip_name=""):
        if(data[index_expedent]=="..." or data[index_expedent]==""):
            if(os.path.exists(constantes.FOLDER_DOCUMENTS+zip_name) and zip_name!=""):
                os.remove(constantes.FOLDER_DOCUMENTS+zip_name)        
            return True              
        #Upload Expedent
        if(data[index_expedent].startswith("expedientes/")==False):
           url=constantes.SERVER+"upload_expediente.php"
           old_path=data[index_expedent]
           fail_upload=False
           with open(data[index_expedent],"rb") as temp_file:                
                  files={'file':temp_file}
                  response=requests.post(url,files=files)
                  res=response.text.strip()
                  data[index_expedent]=res
                  if(res.startswith("expedientes/")==False):
                      data[index_expedent]="..."
                      fail_upload=True
           if(os.path.exists(old_path)):
               os.remove(old_path)                          
           if(fail_upload):
              return False

           
        if(os.path.exists(constantes.FOLDER_DOCUMENTS+zip_name) and zip_name!=""):
            os.remove(constantes.FOLDER_DOCUMENTS+zip_name)                     
        if(data[index_photo]=="..." or data[index_photo]=="" ):
            if(data[0]!="" and data[0]!="..." ):
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}                             
                dat_expedent=conexion_bd.get_allData(["src_foto"],cond_data)
                if(dat_expedent!=[] ):
                    val_f=dat_expedent[0][0]
                    if(val_f.startswith("fotos/")):
                        data[index_photo]=val_f                   
            return True           
        #upload photo
        if(data[index_photo].startswith("fotos/")==False):
           url=constantes.SERVER+"upload_foto.php"
           with open(data[index_photo],"rb") as temp_photo:          
           
                dict_foto={"file":temp_photo}
                respond=requests.post(url,files=dict_foto)          
                res=respond.text.strip()
                data[index_photo]=res
                if(res.startswith("fotos/")==False):
                    data[index_photo]="..."
                    return False       
        return True                   
    
    #update the worker 
    @classmethod
    def update_profesor_data(cls,cargo_val,data_cargo,data,areas_selected,update):
        time_object=tiempo()
        res=0
        if(update==False):
            if(cargo_val.lower()!="obrero" and cargo_val.lower()!="secretaria"):
                conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
                data_prof=[conexion_bd.generate_id(True,constantes.CLAVE_PROFESOR),data[0],"default",time_object.get_fecha()]
                conexion_bd.add_data(data_prof) 
                conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
                for i in range(0,len(areas_selected)):
                    data_areas=[data_prof[0]+"-"+areas_selected[i],data_prof[0],areas_selected[i],time_object.get_fecha()]
                    temp_res=conexion_bd.add_data(data_areas)
                    if(temp_res==-1):
                        res=-1
                        break 
        else:
           conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
           is_docente=False
           if(conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,data[0])==True):
              is_docente=True
           if(is_docente==False and(data_cargo[1].lower()!="obrero" and data_cargo[1].lower()!="secretaria")==True):
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
               data_profesor=["",data[0],"default",time_object.get_fecha()]
               data_profesor[0]=conexion_bd.generate_id(True,constantes.CLAVE_PROFESOR)
               conexion_bd.add_data(data_profesor)
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               for i in range(0,len(areas_selected)):
                   data_areas=[data_profesor[0]+"-"+areas_selected[i],data_profesor[0],areas_selected[i],time_object.get_fecha()]
                   conexion_bd.add_data(data_areas)  
           elif(is_docente==True and (data_cargo[1].lower()=="obrero" or data_cargo[1].lower()=="secretaria")==True):
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)     
               cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
               data_prof=conexion_bd.get_allData([constantes.CLAVE_PROFESOR],cond_data)       
               cond_data={"conditions_Names":[constantes.CLAVE_PROFESOR],"condition_Types":["and"],"conditions_Values":[data_prof[0][0]],"conditions_Verify":["="]}              
               conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:"default"},cond_data)
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               conexion_bd.delete_data(cond_data)
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)   
               conexion_bd.delete_data(cond_data)
           elif(is_docente==True and(data_cargo[1].lower()!="obrero" and data_cargo[1].lower()!="secretaria")==True):
               conexion_bd.set_tabla(constantes.TABLA_PROFESOR)     
               cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
               data_prof=conexion_bd.get_allData([constantes.CLAVE_PROFESOR],cond_data)       
               conexion_bd.set_tabla(constantes.TABLA_AREA_DOCENTE)
               cond_data={"conditions_Names":[constantes.CLAVE_PROFESOR],"condition_Types":["and"],"conditions_Values":[data_prof[0][0]],"conditions_Verify":["="]}              
               conexion_bd.delete_data(cond_data)
               for i in range(0,len(areas_selected)):
                   data_areas=[data_prof[0][0]+"-"+areas_selected[i],data_prof[0][0],areas_selected[i],time_object.get_fecha()]
                   conexion_bd.add_data(data_areas)                           
        return res
    
    #Validate 'Cargo' Code of a Worker
    @classmethod
    def validate_name(cls,valor):
        if(len(valor)<6):
            return -12
        else:   
            first_part=""
            second_part=""
            last_number=4
            last_val=valor[3]
            if(last_val.upper()=="A" or last_val.upper()=="C" or last_val.upper()=="B"):
                last_number=3
            for i in range(0,len(valor)):
                if(i<last_number):
                    first_part=first_part+(valor[i])
                else:
                    second_part=second_part+(valor[i]).upper()
            if(General.is_valid(first_part,constantes.CADENA_SOLONUMERO,False)==False ):
                return -12
            elif(General.is_valid(second_part,constantes.CADENA_SOLOTEXTO,False)==False and General.is_valid(second_part,constantes.CADENA_SOLONUMERO,False)==False ):
                return -12
            else:                          
                return 0 
                
    #Validate File of Expedent 
    @classmethod
    def validate_file_expedent(cls,valor,id_value,is_photo,update):
        field_verify_expedent=""
        value_verify_expedent=""
        valid_file=True
        if(valor=="" or valor=="..."):
           return 0
        if(is_photo==False):
           field_verify_expedent="src_exp"
           value_verify_expedent="expedientes/"
           if(valor.endswith(".rar") or valor.endswith(".zip")):
                path=valor.split("/")
                filename=path[len(path)-1]
                value_verify_expedent=value_verify_expedent+filename
           else:         
              return -8 
        else:
           field_verify_expedent="src_foto"
           value_verify_expedent="fotos/"
           if(valor.endswith(".jpg") or valor.endswith(".jpeg") or valor.endswith(".png")):
                path=valor.split("/")
                filename=path[len(path)-1]
                value_verify_expedent=value_verify_expedent+filename
           else:
              return -17   
        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
        if(conexion_bd.id_exist(field_verify_expedent,value_verify_expedent)==True):
            if(update==False):
                if(is_photo==False):
                   return -19
                else:
                   return  -18
            else:
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[id_value],"conditions_Verify":["="]}              
                dat_worker=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],cond_data)
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[dat_worker[0][0]],"conditions_Verify":["="]}              
                expedent=conexion_bd.get_allData([field_verify_expedent],cond_data)
                if(( expedent[0][0]==value_verify_expedent)==False):
                    if(is_photo==False):
                        return -19 
                    else:
                        return -18
        return 0                        
       
    #Register or Update a worker
    @classmethod
    def registrar_trabajador(cls,user,vent,update=False):
       from event_manager import Event_manager
       pnl=vent.panelActual
       destino=pnl.get_comp_byName("destino_file")
       time_object=tiempo()
       areas_selected=[]
       data_exp=["","...","...",time_object.get_fecha(),time_object.get_fecha()]
       empl=pnl.get_comp_byName("empleado").get_selected_value()
       if(empl=="nuevo" and update==True):
          General.show_message("por favor seleccione un empleado actualizar","empleado invalido")
          return
       elif(empl!="nuevo" and update==False):
          General.show_message("no se puede registrar un empleado ya existente","empleado ya registrado")
          return
       valido=0
       data_estatus=["","","","",time_object.get_fecha()]
       data_nombre=["","","","","",time_object.get_fecha()]
       data=["","","","","...","default","","",time_object.get_fecha()]
       fields=pnl.get_comps_byTag("field")
       nacionalidad=pnl.get_comp_byName("nacionalidad").get_selected_value()
       if(nacionalidad.lower()=="venezolano"):
           nacionalidad="V"
       else:
           nacionalidad="E"
       modify_id=False
       cedula_comp=pnl.get_comp_byName("cedula")
       list_works=pnl.get_comp_byName("empleado")
       if(list_works.get_selected_value()!="nuevo"):
          work_data=list_works.get_selected_value().split("-")
          initial_id=work_data[1]
          initial_nacionalidad=work_data[0]
       if(cedula_comp!=None and list_works!=None):
          valor=cedula_comp.get_text()
          if(General.is_valid(valor,constantes.CADENA_SOLONUMERO,False,6)==False):
             General.show_message("por escriba un valor valido a la cedula","cedula invalida")
             return
          valor=f"{nacionalidad}-{valor}"
          if(update==False):
              conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
              id_exist=conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,valor)
              if(id_exist==True):
                   General.show_message("la CI del personal ya se ha registrado","CI ya existe")
                   return
              data[0]=valor
          else:
             if(nacionalidad=="V" and initial_nacionalidad=="E"):
                modify_id=True
             data[0]=valor
             
       for i in range(0,len(fields)):
            valor=fields[i].get_text()
            if(fields[i].get_id()=="nombre"):
                if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                     valido=-2
                     break
                else:
                  temp_name=valor.split(" ")
                  if(len(temp_name)==2):
                    data_nombre[1]=temp_name[0].lower()
                    data_nombre[2]=temp_name[1].lower()
                  elif(len(temp_name)==1):
                     data_nombre[1]=temp_name[0].lower()
                  else:
                     valido=-2
                     break
            elif(fields[i].get_id()=="apellido"):
                if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                     valido=-3
                     break
                else:
                  temp_apell=valor.split(" ")
                  if(len(temp_apell)==2):
                    data_nombre[3]=temp_apell[0].lower()
                    data_nombre[4]=temp_apell[1].lower()
                  elif(len(temp_apell)==1):
                     data_nombre[3]=temp_apell[0].lower()
                  else:
                     valido=-3
                     break
            elif(fields[i].get_id()=="telefono"):
                if(valor=="" or valor==" "):
                     data[3]="..."
                else:
                    if(General.is_valid(valor,constantes.CADENA_TELEFONO,False)==False):
                           valido=-9
                           break
                    else:                           
                       data[3]=valor
            elif(fields[i].get_id()=="correo"):
                if(valor=="" or valor==" "):
                     data[2]="..."
                else:
                     if(General.is_valid(valor,constantes.CADENA_CORREO,False)==False):
                           valido=-10 
                           break
                     else:                           
                       data[2]=valor 
            elif(fields[i].get_id()=="destino_file"):
                 if(valor!=""):
                     valido=cls.validate_file_expedent(valor,data[0],False,update)
                     if(valido!=0):
                        break
                     data_exp[1]=valor
                     
            elif(fields[i].get_id()=="destino_foto"):
                 if(valor!=""):
                    valido=cls.validate_file_expedent(valor,data[0],True,update)
                    if(valido!=0):
                       break
                    data_exp[2]=valor
                   
            elif(fields[i].get_id()=="cargo_cod"):
                valido=cls.validate_name(valor)
                if(valido!=0):
                   break                
                data[6]=valor+":"            
              
       combo=pnl.get_comp_byName("cargo")
       minist=pnl.get_comp_byName("cargo_minist").get_selected_value()
       if((minist=="elejir" or minist=="elegir")and valido==0):
          valido= -13
       selected=combo.get_selected_value()
       data[6]=minist+":"+data[6]+selected+":"
       err_upload=False
       if(update==True and valido==0):
         combo_estatus=pnl.get_comp_byName("estatus").get_selected_value()
         if(combo_estatus!="elejir" and combo_estatus!="elegir"):
           data_estatus[1]=combo_estatus
         else:
           valido=-20
       data_cargo=[]
       if(valido==0):
         temp_cargo=data[6].split(":")
         conexion_bd.set_tabla(constantes.TABLA_CARGO)
         if(len(temp_cargo)>=3):
            data_cargo=[conexion_bd.generate_id(True,constantes.CLAVE_CARGO),temp_cargo[2],temp_cargo[0],time_object.get_fecha(),temp_cargo[1]]
            data[6]=data_cargo[0]
            if(update==False):
              if(conexion_bd.id_exist(constantes.CLAVE_CARGO,data_cargo[0])==True):
                 valido=-15
         else:
            valido=-16
       docente=False
       if(valido==0):
          if(selected=="elejir" or selected=="elegir"):
                valido=-4
          elif(selected.lower()!="obrero" and selected.lower()!="secretaria"):
             lista_areas=pnl.get_comp_byTag("list")
             areas_selected=lista_areas.get_all_values()
             if(areas_selected==[]):
                 valido=-7

       fecha_ingreso=pnl.get_comp_byName("service_years")
       if(fecha_ingreso!=None and valido==0):
          fecha_value=fecha_ingreso.get_text()
          if(General.is_valid(fecha_value,constantes.CADENA_FECHA,False)==False):
              valido=-14
          else:                           
              data_estatus[3]=fecha_value
              data_estatus[2]=time_object.get_diference_years(fecha_value)

       if(valido==0):
            res=0
            res2=0
            if(General.show_confirmDialog("registrar/Actualizar tarbajador?","registrar")!=True):
                  return
            if(modify_id):
                valor_id=data[0]               
                initial_id=f"{initial_nacionalidad}-{initial_id}"
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                id_exist=conexion_bd.id_exist(constantes.CLAVE_TRABAJADOR,valor_id)
                if(id_exist==True):
                   General.show_message("no se puede modificar la cedula del trabajador por una ya existente","cedula ya existente")
                   return
                 
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[initial_id],"conditions_Verify":["="]}                             
                old_dat_work=conexion_bd.get_allData([],cond_data)
                if(len(old_dat_work)>0):
                    next_data=list(old_dat_work[0])
                    next_data[0]=valor_id
                    conexion_bd.add_data(next_data)
                    conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                    conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:valor_id},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
                    conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:valor_id},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_DISP_HORARIO)
                    conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:valor_id},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_DESCARGA_DOCUMENTO)
                    conexion_bd.update_data({constantes.CLAVE_TRABAJADOR:valor_id},cond_data)
                    conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                    conexion_bd.delete_data(cond_data)
            if(update==False):
               if(cls.upload_expedent(data_exp,1,2,update)==False):
                 General.show_message("Error al Subir El Expedient al servidor","Error del Expedient")
                 return
               conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
               data_exp[0]=conexion_bd.generate_id(True,constantes.CLAVE_EXPEDIENTE)
               
               conexion_bd.add_data(data_exp)
               data[4]=data_exp[0]
               conexion_bd.set_tabla(constantes.TABLA_CARGO)
               conexion_bd.add_data(data_cargo)
               conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
               data_nombre[0]=conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE)
               conexion_bd.add_data(data_nombre)
               data[1]=data_nombre[0]
               conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
               data_estatus[0]=conexion_bd.generate_id(True,constantes.CLAVE_ESTATUS_TRABAJ)
               data_estatus[1]="activo"
               conexion_bd.add_data(data_estatus)
               data[7]=data_estatus[0]
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               res=conexion_bd.add_data(data)
               res2=cls.update_profesor_data(selected,data_cargo,data,areas_selected,update)
               if(res==-1 or res2==-1):
                  General.show_error("error agregando data","error en la base de datos")
               else:
                  user.add_action_historial(["registro de personal",time_object.get_tiempo()])
                  conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                  id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                  data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"registro","personal","",time_object.get_fecha()]
                  conexion_bd.add_data(data_hist,True)
                  General.show_message("registro exitoso del personal","registro exitoso")
                  vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
            else:
                if(cls.upload_expedent(data_exp,1,2,update,data[0]+".zip")==False):
                    General.show_message("Error al Subir El Expedient al servidor","Error del Expedient")
                    return   
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
                dat_t=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE,constantes.CLAVE_CARGO,constantes.CLAVE_NOMBRE,constantes.CLAVE_ESTATUS_TRABAJ],cond_data)
                id_exp=dat_t[0][0]
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)        
                data_exp[0]=id_exp
                id_cargo=dat_t[0][1]
                id_nombre=dat_t[0][2]
                id_estatus=dat_t[0][3]
                cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[data_exp[0]],"conditions_Verify":["="]}              
                conexion_bd.update_data({"src_exp":data_exp[1],"src_foto":data_exp[2],"modificado":time_object.get_fecha()},cond_data)
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
                temp_t=conexion_bd.get_allData([constantes.CLAVE_CARGO],cond_data)
                actual_cargo=temp_t[0][0]
                cls.update_profesor_data(selected,data_cargo,data,areas_selected,update)    
                conexion_bd.set_tabla(constantes.TABLA_CARGO)
                cond_data={"conditions_Names":[constantes.CLAVE_CARGO],"condition_Types":["and"],"conditions_Values":[actual_cargo],"conditions_Verify":["="]}              
                conexion_bd.update_data({"cargo":data_cargo[1],"cargo_ministerio":data_cargo[2],"modificado":time_object.get_fecha(),"codigo_cargo":data_cargo[4]},cond_data)
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[id_nombre],"conditions_Verify":["="]}                   
                conexion_bd.update_data({"nombre":data_nombre[1],"s_nombre":data_nombre[2],"apellido":data_nombre[3],"s_apellido":data_nombre[4],"modificado":time_object.get_fecha()},cond_data)
                conexion_bd.set_tabla(constantes.TABLA_ESTATUS_TRABAJ)
                cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_TRABAJ],"condition_Types":["and"],"conditions_Values":[id_estatus],"conditions_Verify":["="]}              
                conexion_bd.update_data({"estatus":data_estatus[1],"service_years":data_estatus[2],"fecha_ingreso":data_estatus[3],"modificado":time_object.get_fecha()},cond_data)
                conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                values_update={"correo":data[2],"telefono":data[3],"modificado":time_object.get_fecha()}
                cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[data[0]],"conditions_Verify":["="]}              
                conexion_bd.update_data(values_update,cond_data)
                user.add_action_historial(["actualizar personal",time_object.get_tiempo()])
                conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                id_hist=conexion_bd.generate_id(True,constantes.CLAVE_REPORTE)
                data_hist=[ id_hist,user.user,time_object.get_fecha(),time_object.get_tiempo(),"actualizacion","personal","",time_object.get_fecha()]
                conexion_bd.add_data(data_hist,True)
                General.show_message("actualizacion exitosa del personal","actualizacion exitosa")
                vent.update_pantallas(constantes.PANTALLA_WELCOME,user)
       else:
          if(valido==-2):
             General.show_message("por escriba un valor valido al nombre","nombre invalido")
          elif(valido==-3):
             General.show_message("por escriba un valor valido al apellido","apellido invalido")
          elif(valido==-4):
             General.show_message("por escriba un seleccione un cargo","cargo del personal invalido")
          elif(valido==-5):
             General.show_message("por escriba indique el id del fichero a donde se guardara el expediente","expediente invalido")
          elif(valido==-7):
              General.show_message("por favor agregue almenos 1 area de formacion a la lista","area de formacion no asignadas")
          elif(valido==-8):
              General.show_message("el expdiente debe ser un archivo .RAR o .ZIP","formato de archivo del expediente invalido")
          elif(valido==-9):
              General.show_message("por favor indique un telefono valido","telefono invalido ")
          elif(valido==-10):
              General.show_message("por favor indique un correo valido","correo invalido ")
          elif(valido==-11):
              General.show_message("por favor indique estado de salud","estado de salud invalido ")
          elif(valido==-12):
              General.show_message("por favor escriba un codigo del ministerio valido(4 numeros y 2 letras)","codigo del ministerio invalido ")
          elif(valido==-13):
              General.show_message("por favor seleccione un cargo del ministerio valido","cargo del ministerio invalido ")
          elif(valido==-14):
              General.show_message("por favor escriba una fecha de ingreso al ministerio valida ","fecha de ingreso invalidos ")
          elif(valido==-15):
              General.show_message("el codigo del cargo ya se ha registrado","codigo de cargo ya existente")
          elif(valido==-16):
             General.show_message("datos del cargo en formato equivocado ","error en los datos del cargo")
          elif(valido==-17):
             General.show_message("la foto del expediente debe ser una imagen .JPG o .PNG","archivo de foto invalido")
          elif(valido==-18):
             General.show_message("el archivo de la foto ya existe en servidor, por favor cambie el nombre al archivo y vuelve a intentarlo","foto ya existente")
          elif(valido==-19):
             General.show_message("el archivo del expediente ya existe en servidor, por favor cambie el nombre al archivo y vuelve a intentarlo","expediente ya existente")
          elif(valido==-20):
             General.show_message("por favor seleccione el estatus del trabajador","estatus invalido")

          