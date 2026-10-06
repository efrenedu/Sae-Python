from constantes import *
from General import General

#Save the Data of a Student
class estudiante:


    #Build the Student 
    def __init__(self):
        self.data_inscrip=[]
	
    #Get the Data of Inscription Associated to the Student
    def get_data_inscrip(self):
        return self.data_inscrip

    #get the data of Student (Student , Expedent and  Representant Data)
    def get_data_estud(self,cedula,repres=""):
        dat=[]
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)        
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}                
        data_estud=conexion_bd.get_allData([],cond_data)
        conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
        data_repres=[]
        if(data_estud!=[] and repres!=""):
            cond_data={"conditions_Names":[constantes.CLAVE_REPRESENTANTE],"condition_Types":["and"],"conditions_Values":[repres],"conditions_Verify":["="]}              
            data_repres_temp=conexion_bd.get_allData([],cond_data)
            if(data_repres_temp!=[]):
                for col in range(0,len(data_repres_temp[0])):
                    if(col==1):
                        id_nomb=data_repres_temp[0][col]
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[id_nomb],"conditions_Verify":["="]}              
                        data_nomb_repres=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],cond_data)
                        nombre=data_nomb_repres[0][0]
                        apellido=data_nomb_repres[0][1]
                        if(data_nomb_repres[0][2]!="" and data_nomb_repres[0][2]!="..."):
                            nombre=nombre+" "+data_nomb_repres[0][2]
                        if(data_nomb_repres[0][3]!="" and data_nomb_repres[0][3]!="..."):
                            apellido=apellido+" "+data_nomb_repres[0][3]  
                        data_repres.append(nombre)
                        data_repres.append(apellido)
                    else:    
                       data_repres.append(data_repres_temp[0][col])
        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
        data_exp=[]
        if(data_estud!=[]):
            cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[data_estud[0][4]],"conditions_Verify":["="]}              
            
            data_exp=conexion_bd.get_allData([],cond_data)
            temp_estud=[]
            for i in range(0,len(data_estud[0])):
                if(i==1):
                   conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                   cond_data={"conditions_Names":[constantes.CLAVE_NOMBRE],"condition_Types":["and"],"conditions_Values":[data_estud[0][i]],"conditions_Verify":["="]}              
                   data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],cond_data)
                   for j in range(0,len(data_nombre[0])):
                      temp_estud.append(data_nombre[0][j])  
                else:
                   temp_estud.append(data_estud[0][i])
            dat.append(temp_estud)
        if(data_repres!=[]):
            dat.append(data_repres)
        if(data_exp!=[]):
            dat.append(data_exp)        
        return dat
    

    #Get the Academic Data of Student    
    def get_data_curso(self,cedula):
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
        mat_pends={"Required":"False","List":[]}
        data_repitiendo={"Required":"False","List":[]}
        repitiendo=False
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}                    
        id_estatus=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],cond_data)[0][0]  
        conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTATUS_ESTUD],"condition_Types":["and"],"conditions_Values":[id_estatus],"conditions_Verify":["="]}                          
        data_estatus=conexion_bd.get_allData(["last_year"],cond_data)
        year_curso=data_estatus[0][0]
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}                         
        data_pendiente=conexion_bd.get_allData([],cond_data)
        if(data_pendiente!=[]):
            repitiendo=True
            data_repitiendo["Required"]="True"
            mat_pends["Required"]="True"
            num_pends=len(data_pendiente)
            for old_pend in data_pendiente:
                mat_pends["List"].append([old_pend[3],old_pend[4]]) 
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año"],"condition_Types":["and","and"],"conditions_Values":[cedula,year_curso],"conditions_Verify":["=","="]}              
            
        data_califs=conexion_bd.get_allData([],cond_data) 
        data_califs_old=[]
        if(int(year_curso)>1):
          cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año"],"condition_Types":["and","and"],"conditions_Values":[cedula,str(int(year_curso)-1)],"conditions_Verify":["=","="]}              
          data_califs_old=conexion_bd.get_allData([],cond_data) 
        if(repitiendo==False):
            num_pends=0
            mat_pends["Required"]="False"
        if(data_califs!=[] or data_califs_old!=[]):
            #Student with Definitive Califications
            if(repitiendo==False):
                if(data_califs!=[]):
                    for i in range(0,len(data_califs)):
                       valor=data_califs[i][4]
                       if(int(valor)<10):
                          if(num_pends<2):
                              num_pends+=1
                              mat_pends["List"].append([data_califs[i][3],data_califs[i][2]])
                              data_repitiendo["List"].append(data_califs[i][3]+"-"+data_califs[i][2])
                          else:
                            if(repitiendo==False):
                               repitiendo=True
                               data_repitiendo["Required"]="True"
                            num_pends+=1
                            data_repitiendo["List"].append(data_califs[i][3]+"-"+data_califs[i][2])
                            mat_pends={"Required":"False","List":[]}
                if(data_califs_old!=[]):
                    for j in range(0,len(data_califs_old)):
                       valor=data_califs_old[j][4]
                       if(int(valor)<10):
                          if(num_pends<2):
                              num_pends+=1
                              mat_pends["List"].append([data_califs_old[j][3],data_califs_old[j][2]])
                              data_repitiendo["List"].append(data_califs_old[j][3]+"-"+data_califs_old[j][2])
                          else:
                            if(repitiendo==False):
                               repitiendo=True
                               data_repitiendo["Required"]="True"
                            num_pends+=1
                            data_repitiendo["List"].append(data_califs_old[j][3]+"-"+data_califs_old[j][2])
                            mat_pends={"Required":"False","List":[]}
            else:
                if(data_califs!=[]):
                    for i in range(0,len(data_califs)):
                        data_repitiendo["List"].append(data_califs[i][3]+"-"+data_califs[i][2])                                
        else:
            return ["1",mat_pends,data_repitiendo]
     
        if(num_pends<=2 ):
            if(num_pends>0):
                mat_pends["Required"]="True"     
            if(repitiendo==False):
               year_curso=str(int(year_curso)+1)  
        return[year_curso,mat_pends,data_repitiendo]                             
                                        
    #Execute Inscription of Student                     
    def inscribir(self,data):
      
        data_inscrip=data
        from tiempo import tiempo
        from conexion_bd import conexion_bd
        import requests
        import time
        time_object=tiempo()
        conexion_bd.set_tabla(constantes.TABLA_SECCION)
        data_secc=data_inscrip["seccion"]
        register_secc={}
        register_hor={}
        update_secc={}
        id_secc=""
        if(data_secc["Action"]=="Register"):
            register_secc=data_secc["data"]
            register_hor=data_secc["horario"]
            secc_exist=conexion_bd.id_exist(constantes.CLAVE_SECCION,register_secc["id_secc"])
            if(secc_exist==True):
               general.show_error("La seccion ya se ha Registrado","Error")
               return False
            id_secc=register_secc["id_secc"]
        else:
            update_secc=data_secc["data"]
            secc_exist=conexion_bd.id_exist(constantes.CLAVE_SECCION,update_secc["id_secc"])
            if(secc_exist==False):
               general.show_error("La seccion ya indicada no existe","Error")
               return 
            id_secc=update_secc["id_secc"]
               
        if(data_inscrip["tipo_inscripcion"]!="Regular"):
           #Student 'Nuevo Ingreso'
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           id_dire=f"DirStudent-{data_inscrip['estudiante']['CI_estudiante']}"      
           estudent_dir=data_inscrip["estudiante"]["direccion"]
           estudent_dir[constantes.CLAVE_DIRECCION]=id_dire
           estudent_dir["modificado"]=time_object.get_fecha()           
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           id_exp=f"ExpedentStudent-{data_inscrip['estudiante']['CI_estudiante']}"               
           exp={"id_exp":id_exp,"src_exp":data_inscrip["estudiante"]["expediente_src"],"src_foto":data_inscrip["estudiante"]["foto_expediente"],"fecha_registro":time_object.get_fecha(),"modificado":time_object.get_fecha()}
           
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           id_nombre=f"NameStudent-{data_inscrip['estudiante']['CI_estudiante']}"
           data_nombre={constantes.CLAVE_NOMBRE:id_nombre,"nombre":data_inscrip["estudiante"]["nombre"],"s_nombre":data_inscrip["estudiante"]["s_nombre"],"apellido":data_inscrip["estudiante"]["apellido"],"s_apellido":data_inscrip["estudiante"]["s_apellido"],"modificado":time_object.get_fecha()}
          
          
           update_represent={}
           representant_name_data={}
           update_name_representant={}
           representant_direccion_data={}
           update_direccion_representant={}
           add_represent={}
               
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)     
           if(conexion_bd.id_exist(constantes.CLAVE_REPRESENTANTE,data_inscrip["representante"]["CI_representante"])==False):
                #Add data of Representant
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                id_nombre_representant=f"NameRepresentant-{data_inscrip['representante']['CI_representante']}"
                representant_name_data={constantes.CLAVE_NOMBRE:id_nombre_representant,"nombre":data_inscrip["representante"]["nombre"],"s_nombre":data_inscrip["representante"]["s_nombre"],"apellido":data_inscrip["representante"]["apellido"],"s_apellido":data_inscrip["representante"]["s_apellido"],"modificado":time_object.get_fecha()}
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                id_dir_representant=f"DirRepresentant-{data_inscrip['representante']['CI_representante']}"
                representant_direccion_data=data_inscrip["representante"]["direccion"]
                representant_direccion_data[constantes.CLAVE_DIRECCION]=id_dir_representant
                representant_direccion_data["modificado"]=time_object.get_fecha()
                conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                add_represent={constantes.CLAVE_REPRESENTANTE:data_inscrip["representante"]["CI_representante"],constantes.CLAVE_NOMBRE:id_nombre_representant,"telef":data_inscrip["representante"]["telefono"],"correo":data_inscrip["representante"]["correo"],"ocupacion":data_inscrip["representante"]["oficio"],constantes.CLAVE_DIRECCION:id_dir_representant,"modificado":time_object.get_fecha()}              
           else:
                update_represent={"telef":data_inscrip["representante"]["telefono"],"correo":data_inscrip["representante"]["correo"],"ocupacion":data_inscrip["representante"]["oficio"] ,"modificado":time_object.get_fecha()}
                update_name_representant={"nombre":data_inscrip["representante"]["nombre"],"apellido":data_inscrip["representante"]["apellido"],"s_nombre":data_inscrip["representante"]["s_nombre"],"s_apellido":data_inscrip["representante"]["s_apellido"],"modificado":time_object.get_fecha()}
                update_direccion_representant=data_inscrip["representante"]["direccion"]
                update_direccion_representant["modificado"]=time_object.get_fecha()
                
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           temp_estado=data_inscrip["estudiante"]["estatus"]
           estado=data_inscrip["estudiante"]["estatus"]
           if(estado=="irregular"):
              estado="activo"
           id_estatus= f"estatus_{data_inscrip['estudiante']['CI_estudiante']}"
           data_estatus={constantes.CLAVE_ESTATUS_ESTUD:id_estatus,"estatus":estado,"salud":data_inscrip["estudiante"]["salud"],"cedulado":data_inscrip["estudiante"]["cedulado"],"last_year":data_inscrip["estudiante"]["year_estud"],"fecha_inscrip":time_object.get_fecha(),"fecha_ingreso":time_object.get_fecha(),"plantel_procedencia":data_inscrip["estudiante"]["plantel"],"modificado":time_object.get_fecha()}
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           estud={constantes.CLAVE_ESTUDIANTE:data_inscrip["estudiante"]["CI_estudiante"],constantes.CLAVE_NOMBRE:id_nombre,constantes.CLAVE_ESTATUS_ESTUD:id_estatus,constantes.CLAVE_SECCION:id_secc,constantes.CLAVE_EXPEDIENTE:id_exp,constantes.CLAVE_REPRESENTANTE:data_inscrip["representante"]["CI_representante"],"genero":data_inscrip["estudiante"]["genero"],"nacimiento":data_inscrip["estudiante"]["año_nacimiento"],constantes.CLAVE_DIRECCION:id_dire,"parentesco":data_inscrip["estudiante"]["parentesco"],"modificado":time_object.get_fecha()}
          
           add_califics=[]
           if(temp_estado=="irregular"):
             #inscription Irregular (Nuevo Ingreso But not First Year)
             num_years=int(data_inscrip["estudiante"]["year_estud"])-1
             for i in range(0,num_years):
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               join_data={}
               field_year=str(i+1)+"_año"
               join_cond={"conditions_Names":[field_year],"condition_Types":["and"],"conditions_Values":["True"],"conditions_Verify":["="]}              
               join_data["años_incorporados"]={"query_field":[],"share_fields":{"field":constantes.CLAVE_AÑOS_INCORPORADOS,"table_reference":"area_formacion"},"Conditions_join":join_cond}
               cond_data={"conditions_Names":["incorporada"],"condition_Types":["and"],"conditions_Values":["Si"],"conditions_Verify":["="]}              
               areas_data=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],cond_data,join_data,True)
               for area in areas_data:
                  next_register_calific={constantes.CLAVE_CALIFICACION_FINAL:data_inscrip["estudiante"]["CI_estudiante"]+"-"+area[constantes.CLAVE_AREA_FORMACION]+str(i+1),constantes.CLAVE_ESTUDIANTE:data_inscrip["estudiante"]["CI_estudiante"],"año":str(i+1),"nomb_area":area[constantes.CLAVE_AREA_FORMACION],"valor":"0","modificado":time_object.get_fecha()}
                  add_califics.append(next_register_calific)
               num_areas_year=len(areas_data)
               if(num_areas_year<=0):
                  General.show_error(f"Areas para el Año {(i+1)} no Registradas","Error")
                  return False     
           #Add Expedent Data
           if(exp["src_exp"]!="" and exp["src_exp"]!="..."):
               try:
                  if(exp["src_exp"].startswith("expedientes/")==False):
                    url=constantes.SERVER+"upload_expediente.php"
                    with open(exp["src_exp"],"rb") as temp_file:
                      dict_exp={"file":temp_file}
                      data_exp={"token":data_inscrip["usuario"],"timestamp":str(int(time.time()))}
                      response=requests.post(url,files=dict_exp,data=data_exp)
                      res=response.text.strip()
                      exp["src_exp"]=res
                      if(res.startswith("expedientes/")==False):
                         exp["src_exp"]="..."
                         General.show_error(f"Error subiendo Expediente , Valor Recibido:{res}","Error Subiendo Foto")              
                         return False
               except:
                    General.show_error("Error Subiendo Datos del Expediente al Servidor","Error")
                    return False
           if(exp["src_foto"]!="" and exp["src_foto"]!="..."):
               try:  
                                 
                  if(exp["src_foto"].startswith("fotos/")==False):
                    format_foto=""
                    if(exp["src_foto"].endswith(".png")):
                      format_foto="png"
                    elif(exp["src_foto"].endswith(".jpg")):
                      format_foto="jpg"
                    else:
                      General.show_error("La foto puede ser solo PNG o JPG ","Foto Invalida")
                      return False
                    url=constantes.SERVER+"upload_foto.php"
                    with open(exp["src_foto"],"rb") as temp_foto:
                      dict_foto={"file":temp_foto}
                      
                      data_send={"token":data_inscrip["usuario"],"timestamp":str(int(time.time())),"identificador":"Estudiante_"+data_inscrip["estudiante"]["CI_estudiante"],"format":format_foto,"target":"Student"}
                      response=requests.post(url,files=dict_foto,data=data_send)
                      res=response.text.strip()
                      exp["src_foto"]=res
                      if(res.startswith("fotos/")==False):
                         exp["src_foto"]="..."
                         General.show_error(f"Error subiendo foto , Valor Recibido:{res}","Error Subiendo Foto")              
                         return False
               except:
                   General.show_error("Error Subiendo Datos de la Foto al Servidor","Error")
                   return False  
                         
           #Request Updates to Data Base      
           if(register_secc!={}):
              conexion_bd.set_tabla(constantes.TABLA_HORARIO)
              conexion_bd.add_data(register_hor)
              conexion_bd.set_tabla(constantes.TABLA_SECCION)
              conexion_bd.add_data(register_secc)
           else:
              conexion_bd.set_tabla(constantes.TABLA_SECCION)
              cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[update_secc["id_secc"]],"conditions_Verify":["="]}              
              conexion_bd.update_data({"total_estud":update_secc["new_cant"]},cond_data,None)               
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           conexion_bd.add_data(data_nombre)
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           conexion_bd.add_data(estudent_dir)
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           conexion_bd.add_data(exp)
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           conexion_bd.add_data(data_estatus)  
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
           if(len(add_represent)>0):
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                conexion_bd.add_data(representant_name_data)
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                conexion_bd.add_data(representant_direccion_data)
                conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                conexion_bd.add_data(add_represent)
           else:
               join_data={}
               join_data["nombre"]={"query_field":update_name_representant,"share_fields":{"field":"id_nombre","table_reference":"representante"},"Conditions_join":None}
               join_data["direccion"]={"query_field":update_direccion_representant,"share_fields":{"field":"id_dir","table_reference":"representante"},"Conditions_join":None}
               cond_data_representant={"conditions_Names":["CI_repres"],"condition_Types":["and"],"conditions_Values":[data_inscrip["representante"]["CI_representante"]],"conditions_Verify":["="]}              
               conexion_bd.update_data(update_represent,cond_data_representant,join_data)
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           conexion_bd.add_data(estud)
           conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
           for register in add_califics:
               conexion_bd.add_data(register)
           return True
           
        else:
             #Regular Student
            
             estudent_update_dat={}
             estudent_update_dir=data_inscrip["estudiante"]["direccion"]
             estudent_update_dir["modificado"]=time_object.get_fecha()
             estudent_update_name={"nombre":data_inscrip["estudiante"]["nombre"],"s_nombre":data_inscrip["estudiante"]["s_nombre"],"apellido":data_inscrip["estudiante"]["apellido"],"s_apellido":data_inscrip["estudiante"]["s_apellido"],"modificado":time_object.get_fecha()}
             estudent_update_status={"salud":data_inscrip["estudiante"]["salud"],"fecha_inscrip":time_object.get_fecha(),"modificado":time_object.get_fecha(),"last_year":data_inscrip["estudiante"]["year_estud"],"estatus":"activo"}
             representant_update_name={}
             representant_update_dir={}
             representant_update_data={}
             update_califics=[]
             materias_pendientes=[]
             remove_materias_pendientes={}
                           
            
             representant_update_data={"telef":data_inscrip["representante"]["telefono"],"correo":data_inscrip["representante"]["correo"],"ocupacion":data_inscrip["representante"]["oficio"] ,"modificado":time_object.get_fecha()}
             representant_update_name={"nombre":data_inscrip["representante"]["nombre"],"apellido":data_inscrip["representante"]["apellido"],"s_nombre":data_inscrip["representante"]["s_nombre"],"s_apellido":data_inscrip["representante"]["s_apellido"],"modificado":time_object.get_fecha()}
             representant_update_dir=data_inscrip["representante"]["direccion"]
             representant_update_dir["modificado"]=time_object.get_fecha()
            
             estudent_update_dat={constantes.CLAVE_SECCION:id_secc,"parentesco":data_inscrip["estudiante"]["parentesco"],constantes.CLAVE_REPRESENTANTE:data_inscrip["representante"]["CI_representante"],"modificado":time_object.get_fecha()}
                                   
             #reset califications of last year of student if is neccesary
            
             if(data_inscrip["areas_repitiendo"]["Required"]!="False"):
                clear_year=data_inscrip["estudiante"]["year_estud"]
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año"],"condition_Types":["and","and"],"conditions_Values":[data_inscrip["estudiante"]["CI_estudiante"],clear_year],"conditions_Verify":["=","="]}              
                list_areas_year=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION],cond_data,None,True)
                for area in list_areas_year:
                   update_califics.append({"Area":area[constantes.CLAVE_AREA_FORMACION],"Year":clear_year,constantes.CLAVE_ESTUDIANTE:data_inscrip["estudiante"]["CI_estudiante"]})

             #Remove Old Materials Pendientes
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
             cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[data_inscrip["estudiante"]["CI_estudiante"]],"conditions_Verify":["="]}              
             temp_pendent=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],cond_data,None,True)             
             for register in temp_pendent:
                conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[register[constantes.CLAVE_MATERIA_PENDIENTE]],"conditions_Verify":["="]}              
                id_mat_pend=register[constantes.CLAVE_MATERIA_PENDIENTE]
                dat_califs_pends=conexion_bd.get_allData([constantes.CLAVE_CALIF_PENDIENTE],cond_data,None)
                remove_materias_pendientes[id_mat_pend]=[]
                for dat in dat_califs_pends:
                   remove_materias_pendientes[id_mat_pend].append(dat[constantes.CLAVE_CALIF_PENDIENTE])
                  
             #Add New Materias Pendientes
             if(data_inscrip["materia_pendiente"]["Required"]!="False"): 
                 areas_pendiente=data_inscrip["materia_pendiente"]["List"]
                 conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE) 
                 for i in range(0,len(areas_pendiente)):
                    id_mat_pend=f"MateriaPendiente_{areas_pendiente[i][0]}_{areas_pendiente[i][1]}Year_{data_inscrip['estudiante']['CI_estudiante']}"
                    next_mat_pendiente={constantes.CLAVE_MATERIA_PENDIENTE:id_mat_pend,constantes.CLAVE_ESTUDIANTE:data_inscrip["estudiante"]["CI_estudiante"],"max_calif":"0","nomb_area":areas_pendiente[i][0],"año":areas_pendiente[i][1],"modificado":time_object.get_fecha()}
                    materias_pendientes.append(next_mat_pendiente)
        
             
             #Update Data Base
             if(register_secc!={}):
                conexion_bd.set_tabla(constantes.TABLA_HORARIO)
                conexion_bd.add_data(register_hor)
                conexion_bd.set_tabla(constantes.TABLA_SECCION)
                conexion_bd.add_data(register_secc)
             else:
                conexion_bd.set_tabla(constantes.TABLA_SECCION)
                cond_data={"conditions_Names":[constantes.CLAVE_SECCION],"condition_Types":["and"],"conditions_Values":[update_secc["id_secc"]],"conditions_Verify":["="]}              
                conexion_bd.update_data({"total_estud":update_secc["new_cant"]},cond_data,None)               
             conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
             join_data={}
             join_data["nombre"]={"query_field":representant_update_name,"share_fields":{"field":"id_nombre","table_reference":"representante"},"Conditions_join":None}
             join_data["direccion"]={"query_field":representant_update_dir,"share_fields":{"field":"id_dir","table_reference":"representante"},"Conditions_join":None}
             cond_data_representant={"conditions_Names":["CI_repres"],"condition_Types":["and"],"conditions_Values":[data_inscrip["representante"]["CI_representante"]],"conditions_Verify":["="]}              
             conexion_bd.update_data(representant_update_data,cond_data_representant,join_data)
             
             conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
             cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[data_inscrip["estudiante"]["CI_estudiante"]],"conditions_Verify":["="]}              
             join_data={}
             join_data["nombre"]={"query_field":estudent_update_name,"share_fields":{"field":"id_nombre","table_reference":"estudiante"},"Conditions_join":None}
             join_data["direccion"]={"query_field":estudent_update_dir,"share_fields":{"field":"id_dir","table_reference":"estudiante"},"Conditions_join":None}  
             join_data["estatus_estud"]={"query_field":estudent_update_status,"share_fields":{"field":"id_est","table_reference":"estudiante"},"Conditions_join":None}  
             
             conexion_bd.update_data(estudent_update_dat,cond_data,join_data)
             
              
             
             conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
             for register in update_califics:
                 cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[register[constantes.CLAVE_ESTUDIANTE],register["Area"],register["Year"]],"conditions_Verify":["=","=","="]}              
                 conexion_bd.update_data({"valor":"01","modificado":time_object.get_fecha()},cond_data)             
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
             for id_mat_pend in remove_materias_pendientes:
                list_califics=remove_materias_pendientes[id_mat_pend]
                conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                for calific_id in list_califics:
                   cond_data={"conditions_Names":[constantes.CLAVE_CALIF_PENDIENTE],"condition_Types":["and"],"conditions_Values":[calific_id],"conditions_Verify":["="]}              
                   conexion_bd.delete_data(cond_data)
                conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[id_mat_pend],"conditions_Verify":["="]}              
                conexion_bd.delete_data(cond_data)
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE) 
             for register in materias_pendientes:
                conexion_bd.add_data(register)
             return True
            

    #Verify if The Modification in the Student is Valid (Update Student Panel)
    def is_valid_modific(self,cedula,cedulado,data_estud,data_repres,data_exp,data_dir):
        
        from General import General
        from conexion_bd import conexion_bd
        data_estud_valid=[cedula,"","","","",cedulado,"","","","","","","",""]
        data_repres_valid=["","","","","","","","",""]
        data_exp_valid=["",""]
        data_dir_valid=["","",""]
        data_dir_repres_valid=["","",""]
        update_ced=[False,""]
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
        d_estud=conexion_bd.get_allData([constantes.CLAVE_SECCION,constantes.CLAVE_EXPEDIENTE,constantes.CLAVE_REPRESENTANTE,constantes.CLAVE_DIRECCION],cond_data)
        data_estud_valid[6]=d_estud[0][0]
        data_estud_valid[7]=d_estud[0][1]
        data_estud_valid[8]=d_estud[0][2]
        data_estud_valid[13]=d_estud[0][3]
        
      
        for i in range(1,len(data_estud)):
           valor=data_estud[i]
           if(i==1):
              if(valor==""):
                return [-1]
              fullname=valor.split(" ")
              if(len(fullname)>=3 or len(fullname)==0):
                 return [-1]
              if(len(fullname)==2):
                if(General.is_valid(fullname[0],constantes.CADENA_SOLOTEXTO,False,2)==False):
                  return [-1]
                elif(General.is_valid(fullname[1],constantes.CADENA_SOLOTEXTO,False,2)==False):
                  return [-1]
                data_estud_valid[1]=fullname[0].lower()
                data_estud_valid[2]=fullname[1].lower()
              else:
                data_estud_valid[1]=fullname[0].lower()
           elif(i==2):
              if(valor==""):
                return [-2]
              fullapell=valor.split(" ")
              if(len(fullapell)>=3 or len(fullapell)==0 ):
                 return [-2]
              if(len(fullapell)==2):
                if(General.is_valid(fullapell[0],constantes.CADENA_SOLOTEXTO,False,2)==False):
                  return [-2]
                elif(General.is_valid(fullapell[1],constantes.CADENA_SOLOTEXTO,False,2)==False):
                  return [-2]
                data_estud_valid[3]=fullapell[0].lower()
                data_estud_valid[4]=fullapell[1].lower()
              else:
                 data_estud_valid[2]=fullapell[0].lower()
           elif(i==3):
              if(General.is_valid(valor,constantes.CADENA_FECHA,False)==False):
                 return [-3]
              data_estud_valid[12]=valor
           elif(i==4):
              st=valor.split("-")
              st1=st[0]
              st2=st[1]
              if(st2!="elejir" and st2!="elegir"):
                 data_estud_valid[9]=st2
              else:
                 data_estud_valid[9]=st1
                 
              if(st1=="irregular" and (st2!="elejir" and st2!="elegir")):
                  return [-4]
           elif(i==5):
                 if(valor=="elejir" or valor=="elegir"):
                    return [-5]
                 data_estud_valid[10]=valor
           elif(i==6):
                 data_estud_valid[11]=valor
           elif(i==7):
               if(cedulado.lower()=="false" or cedulado.lower()=="no"):
                  if(valor!=""):
                        if(General.is_valid(valor,constantes.CADENA_SOLONUMERO,False,6)==False):
                            return [-6]
                        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                        if(conexion_bd.id_exist(constantes.CLAVE_ESTUDIANTE,valor)==True):
                           return[-16]
                           
                        update_ced=[True,valor]
                                  
        for  j in range(0,len(data_repres)): 
           valor=data_repres[j]
           if(j==0):
               temp_valor=valor
               if(temp_valor.startswith("v-") or temp_valor.startswith("V-") or temp_valor.startswith("e-") or temp_valor.startswith("E-")):
                   temp_valor=temp_valor.split("-")[1]
               if(General.is_valid(temp_valor,constantes.CADENA_SOLONUMERO,False,6)==False):
                   return [-7 ] 
               data_repres_valid[0]=valor 
               
           elif(j==1):
               fullname_r=valor.split(" ")
               if(len(fullname_r)>=3 or len(fullname_r)==0 ):
                    return[-8]
               if(len(fullname_r)==1):  
                   if(General.is_valid(fullname_r[0],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-8 ] 
                   data_repres_valid[1]=fullname_r[0].lower()   
               elif(len(fullname_r)==2):  
                   if(General.is_valid(fullname_r[0],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-8 ] 
                   if(General.is_valid(fullname_r[1],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-8 ] 
                   data_repres_valid[1]=fullname_r[0].lower() 
                   data_repres_valid[2]=fullname_r[1].lower()
                   
           elif(j==2):
               fullapell_r=valor.split(" ")
               if(len(fullapell_r)>=3 or len(fullapell_r)==0 ):
                    return[-9]
               if(len(fullapell_r)==1):  
                   if(General.is_valid(fullapell_r[0],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-9 ] 
                   data_repres_valid[3]=fullapell_r[0].lower()    
               elif(len(fullname_r)==2):  
                   if(General.is_valid(fullapell_r[0],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-9 ] 
                   if(General.is_valid(fullapell_r[1],constantes.CADENA_SOLOTEXTO,False,3)==False):
                       return [-9 ] 
                   data_repres_valid[3]=fullapell_r[0].lower()
                   data_repres_valid[4]=fullapell_r[1].lower() 
           
           elif(j==3):
               if(General.is_valid(valor,constantes.CADENA_TELEFONO,False)==False):
                   return [-10] 
               data_repres_valid[5]=valor
           
           elif(j==4):
               
               if(General.is_valid(valor,constantes.CADENA_CORREO,False)==False):
                     return[-17]
               else:
                  data_repres_valid[6]=valor
           
           elif(j==5):
                if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                     return[-18]
                dir_r=valor.split(",")
                if(len(dir_r)!=3):
                   return[-18]
                data_dir_repres_valid=[dir_r[0].lower(),dir_r[1].lower(),dir_r[2].lower()]
                
           elif(j==6):
              if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,False,2)==False):
                     return[-19]
              data_repres_valid[7]=valor.lower()
                
           elif(j==7):
               if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,2)==False):
                     return[-20]
               data_repres_valid[8]=valor.lower()
               
        if(data_dir!=""):
           if(General.is_valid(data_dir,constantes.CADENA_DIRECCION,True)==False):
              return [-11]
              
           dire=data_dir.split(",")
           if(len(dire)!=3):
               return [-11]
           data_dir_valid=[dire[0].lower(),dire[1].lower(),dire[2].lower()]
         
        else:
           return [-11] 

        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
        id_exp=data_estud_valid[7]
        cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[id_exp],"conditions_Verify":["="]}              
        d_e=conexion_bd.get_allData(["src_exp","src_foto"],cond_data)[0]
        
        if(data_exp[0]!=""):
           
           if(data_exp[0].endswith(".rar") or data_exp[0].endswith(".zip")):
               data_exp_valid[0]=data_exp[0]
           else:
              return [-12]  
              
        if(data_exp[1]!=""):
           if(data_exp[1].endswith(".png") or data_exp[1].endswith(".jpg")):
              data_exp_valid[1]=data_exp[1]
           else:
              return [-13]    
        return [True,data_estud_valid,update_ced,data_repres_valid,data_exp_valid,data_dir_valid,data_dir_repres_valid]
    
    
    #Estimulate an Area of Formacion of Studente     
    def estimular_area(self,data,fecha):
        from General import General
        from conexion_bd import conexion_bd
        val_estimul=int(data["Estimulacion_Promedio"])
        val_estimul2=int(data["Estimulacion_Areas"])
        total_estimul=val_estimul+val_estimul2
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data["Year"]],"conditions_Verify":["=","=","="]}                         
        join_data={}
        cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[data["Momento"]],"conditions_Verify":["="]}                         
        join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM,"estimulacion","prom","definitiva"],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join}
        data_calific_mom=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,join_data,True)    
        if(len(data_calific_mom)<=0):
             [False,None,None]  
        id_f=data_calific_mom[0][constantes.CLAVE_CALIFICACION_FINAL]
        id_calific_mom=data_calific_mom[0][constantes.CLAVE_CALIF_MOM]
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_calific_mom],"conditions_Verify":["="]}              
        conexion_bd.update_data({"estimulacion":str(val_estimul+val_estimul2),"modificado":fecha},cond_data,None,True)
        new_calific= self.recalculate_calification(id_f)
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL) 
        cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[id_f],"conditions_Verify":["="]}                   
        conexion_bd.update_data({"valor":new_calific,"modificado":fecha},cond_data,None,True)
        prom_data=[data_calific_mom[0]["prom"],data_calific_mom[0]["definitiva"],str(total_estimul),data_calific_mom[0]["definitiva"],str(int(data_calific_mom[0]["definitiva"])+total_estimul)]   
        return [True,prom_data]
  
           
    #Modify a Calification Definitive (Student 'Nuevo Ingreso' with Califications from Another Institute)    
    def modific_calif_final(self,data,fecha): 
       from conexion_bd import conexion_bd 
       area=data["Area"]
       year=data["Year"]   
       new_calif=data["Calification"]
       val=int(new_calif)              
       if(val<1):
          val=1
       str_val=str(val)
       if(len(str_val)<2):
          str_val="0"+str_val  
          
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],area,year],"conditions_Verify":["=","=","="]}                
       conexion_bd.update_data({"valor":str_val,"modificado":fecha},cond_data,None)
       
       
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"valor"],"condition_Types":["and","and"],"conditions_Values":[data["Id_Estud"],"0"],"conditions_Verify":["=","="]}                
       pendientes_modify=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data)
       
       #Register or Remove Materia Pendiente if is Neccesary Associated to the New Calification
       conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],area,year],"conditions_Verify":["=","=","="]}              
       data_pend=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],cond_data,None,True) 
       if(data_pend!=[]):
           conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
           cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[data_pend[0][constantes.CLAVE_MATERIA_PENDIENTE]],"conditions_Verify":["="]}              
           conexion_bd.delete_data(cond_data)
           conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
           conexion_bd.delete_data(cond_data)                    
       if(val<10):
          conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
          data_pend={constantes.CLAVE_MATERIA_PENDIENTE:f"materiaPendiente_{area}_{year}Year_{dat[0]}",constantes.CLAVE_ESTUDIANTE:dat[0],"max_calif":"0.0",constantes.CLAVE_AREA_FORMACION:area,"año":year,"modificado":fecha}
          conexion_bd.add_data(data_pend)    
       
       if(len(pendientes_modify)<=0):
          return False
       else :
          return True
       

    #Calculate new Calification  for The Indicated Area When the Calification of An Academic Moment Change
    def recalculate_calification(self,id_calification,replace_calif=None):   
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[id_calification],"conditions_Verify":["="]}                       
        all_moments=conexion_bd.get_allData([constantes.CLAVE_CALIF_MOM,"definitiva","estimulacion"],cond_data,None,True)
        suma=0.0
        for dat_mom in all_moments:
            val=int(dat_mom["definitiva"])
            if(replace_calif!=None):
               if(dat_mom[constantes.CLAVE_CALIF_MOM]==replace_calif["Id"]):
                   val=int(replace_calif["Value"])
                   
            suma+=val+int(dat_mom["estimulacion"])       
        if(suma>0.0):
           suma/=len(all_moments)
           suma=int(round(suma))
        str_suma=str(suma)
        if(len(str_suma)<2):
           str_suma="0"+str_suma  
        return str_suma
        
    #Calculate new Calification of for The Indicated Area On the Academic Moment After Make a Modification
    def calculate_calif_mom(self,id_mom,area,momento,replace_calif=None,ignore_calif=None):  
        from conexion_bd import conexion_bd
        prom=0.0
        data_calif=[]
        num_evals=0
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_mom],"conditions_Verify":["="]}              
        list_calif=conexion_bd.get_allData(["valor","numero"],cond_data,None,True)
        for i in range(0,len(list_calif)):
           calif=list_calif[i]["valor"]
           if(replace_calif!=None):
                if(replace_calif["Numero"]==list_calif[i]["numero"]):
                    calif=replace_calif["Value"]
           if(ignore_calif!=None):
                 if(ignore_calif["Numero"]==list_calif[i]["numero"]): 
                      continue                 
           prom+=float(calif)
           num_evals+=1
           dat_row=[list_calif[i]["numero"], area,momento,calif]
           data_calif.append(dat_row)
        if(prom>0.0 and num_evals>0):
          prom/=num_evals
          prom=round(prom,2)
        return {"Promedio":prom,"Data_Califications":data_calif}
        
    #Modify a Calification    
    def modific_calif(self,data,fecha):
        from General import General
        from conexion_bd import conexion_bd

        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data["Year"]],"conditions_Verify":["=","=","="]}                         
        join_data={}
        cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[data["Momento"]],"conditions_Verify":["="]}                         
        join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM,"estimulacion"],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join}
        data_calific_mom=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,join_data,True)    
        if(len(data_calific_mom)<=0):
             [False,None,None]  
        id_f=data_calific_mom[0][constantes.CLAVE_CALIFICACION_FINAL]
        id_calific_mom=data_calific_mom[0][constantes.CLAVE_CALIF_MOM]
        
        val_cal=data["Calification"]
        if(int(val_cal)<1):
           val_cal="01"
        else:
          if(len(val_cal)<2):
             val_cal="0"+val_cal 

        prom=0.0
        list_calif=[]
        prom_data=[0.0,0.0,0,0.0]     
        
        new_calif_mom=self.calculate_calif_mom(id_calific_mom,data["Area"],data["Momento"],{"Numero":data["Evaluation"],"Value":val_cal})
        prom=new_calif_mom["Promedio"]
        list_calif=new_calif_mom["Data_Califications"]
        if(prom<=0.0):
            [False,None,None]  
        calif_mom=int(round(prom)) 
        estimul=int(data_calific_mom[0]["estimulacion"])
        str_prom=""
        str_calif=""
        str_calif=str(calif_mom)
        str_prom=str(prom)
        if(len(str_calif)<2):
           str_calif="0"+str_calif                   
        prom_data=[prom,calif_mom,estimul,calif_mom+estimul]   
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM) 
        cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_calific_mom],"conditions_Verify":["="]}              
        join_data={}
        cond_join={"conditions_Names":["numero"],"condition_Types":["and"],"conditions_Values":[data["Evaluation"]],"conditions_Verify":["="]}                         
        join_data["calificacion"]={"query_field":{"valor":val_cal,"modificado":fecha},"share_fields":{"field":constantes.CLAVE_CALIF_MOM,"table_reference":"calif_momento"},"Conditions_join":cond_join}      
        conexion_bd.update_data({"prom":str_prom,"definitiva":str_calif,"modificado":fecha},cond_data,join_data)   
        
        #Update Definitive Calification (Calification Final)
        new_calific= self.recalculate_calification(id_f,{"Id":id_calific_mom,"Value":str_calif})
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[id_f],"conditions_Verify":["="]}                       
        conexion_bd.update_data({"valor":new_calific,"modificado":fecha},cond_data)
        
        return [True,list_calif,prom_data]            
    
    #Remove a Calification
    def delete_calif(self,data,fecha):
       from conexion_bd import conexion_bd
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data["Year"]],"conditions_Verify":["=","=","="]}                         
       join_data={}
       cond_join={"conditions_Names":[constantes.CLAVE_MOMENTO],"condition_Types":["and"],"conditions_Values":[data["Momento"]],"conditions_Verify":["="]}                         
       join_data["calif_momento"]={"query_field":[constantes.CLAVE_CALIF_MOM,"estimulacion"],"share_fields":{"field":constantes.CLAVE_CALIFICACION_FINAL,"table_reference":"calificacion_final"},"Conditions_join":cond_join}
       data_calific_mom=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,join_data,True)    
       if(len(data_calific_mom)<=0):
             [False,None,None]  
       id_f=data_calific_mom[0][constantes.CLAVE_CALIFICACION_FINAL]
       id_calific_mom=data_calific_mom[0][constantes.CLAVE_CALIF_MOM]
        
       prom=0.0
       list_calif=[]
       prom_data=[0.0,0.0,0,0.0]
        
       new_calif_mom=self.calculate_calif_mom(id_calific_mom,data["Area"],data["Momento"],None,{"Numero":data["Evaluation"]})
       prom=new_calif_mom["Promedio"]
       list_calif=new_calif_mom["Data_Califications"]
       if(prom<=0.0):
          prom=1.0
          
       calif_mom=int(round(prom)) 
       estimul=int(data_calific_mom[0]["estimulacion"])
       str_prom=""
       str_calif=""
       str_calif=str(calif_mom)
       str_prom=str(prom)
       if(len(str_calif)<2):
           str_calif="0"+str_calif                   
       prom_data=[prom,calif_mom,estimul,calif_mom+estimul] 
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
       cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM,"numero"],"condition_Types":["and","and"],"conditions_Values":[id_calific_mom,data["Evaluation"]],"conditions_Verify":["=","="]}              
       conexion_bd.delete_data(cond_data)  
       conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM) 
       cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_calific_mom],"conditions_Verify":["="]}              
       conexion_bd.update_data({"prom":str_prom,"definitiva":str_calif,"modificado":fecha},cond_data)   
       
       #Update Definitive Calificacion Value (Calification Final)
       new_calific= self.recalculate_calification(id_f,{"Id":id_calific_mom,"Value":str_calif})
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[id_f],"conditions_Verify":["="]}                       
       conexion_bd.update_data({"valor":new_calific,"modificado":fecha},cond_data)
       return [True,list_calif,prom_data]  
              
        
    #Add a Try for Materia Pendiente  , return True if Success
    def mat_pendiente(self,data,fecha):
        from General import General
        from conexion_bd import conexion_bd
        calif=data["Calificacion_Value"]
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],"condition_Types":["and","and"],"conditions_Values":[data["Id_Estud"],data["Area"]],"conditions_Verify":["=","="]}              
        data_m_pen=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE,"año","max_calif"],cond_data,None,True)               
        res_msg=""
        res_msg_title=""
        if(int(calif)>=10):
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            cond_data={"conditions_Names":[constantes.CLAVE_MATERIA_PENDIENTE],"condition_Types":["and"],"conditions_Values":[data_m_pen[0][constantes.CLAVE_MATERIA_PENDIENTE]],"conditions_Verify":["="]}              
            conexion_bd.delete_data(cond_data)
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            conexion_bd.delete_data(cond_data)
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data_m_pen[0]["año"]],"conditions_Verify":["=","=","="]}              
            conexion_bd.update_data({"valor":calif,"modificado":fecha},cond_data)
            res_msg="materia pendiente del estudiante aprobada existosamente"
            res_msg_title="estudiante aprobado"
        else:
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            codigo_c=f"califMatPendiente_{data_m_pen[0][constantes.CLAVE_MATERIA_PENDIENTE]}_{data['Intento_Id']}"
            valores={constantes.CLAVE_CALIF_PENDIENTE:codigo_c,constantes.CLAVE_MATERIA_PENDIENTE:data_m_pen[0][constantes.CLAVE_MATERIA_PENDIENTE],"intento":data["Intento_Id"],"valor":calif,"fecha":fecha,"modificado":fecha}
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            conexion_bd.add_data(valores)
            max_calif=data_m_pen[0]["max_calif"]
            if(max_calif=="" or max_calif==" " or max_calif=="0.0"):
                max_calif="0"
            max_calif=int(max_calif)
            if(max_calif<int(calif)):
                conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],"condition_Types":["and","and"],"conditions_Values":[data["Id_Estud"],data["Area"]],"conditions_Verify":["=","="]}                         
                conexion_bd.update_data({"max_calif":calif,"modificado":fecha},cond_data)           
            res_msg="calificacion de materia pendiente o revision registrada satisfactoriamente"
            res_msg_title="registro exitoso de materia pendiente o revision"
        return [res_msg,res_msg_title]
        

    #Get The Calification Required for Certify Califications as a List
    def get_calif_certific(self,cedula):
         from conexion_bd import conexion_bd        
         
         #Get Student Name,Id and Last Year of Inscription
         conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)    
         cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[cedula],"conditions_Verify":["="]}              
         join_data={}
         join_data["estatus_estud"]={"query_field":["last_year"],"share_fields":{"field":constantes.CLAVE_ESTATUS_ESTUD,"table_reference":"estudiante"},"Conditions_join":None}
         join_data["nombre"]={"query_field":["nombre","s_nombre","apellido","s_apellido"],"share_fields":{"field":constantes.CLAVE_NOMBRE,"table_reference":"estudiante"},"Conditions_join":None}
         
         data_estud=conexion_bd.get_allData([constantes.CLAVE_ESTUDIANTE],cond_data,join_data,True)
         if(len(data_estud)<=0):
            return [False,"Error Obteneiendo Data del Estudiante"]
         target_nameFields=["nombre","s_nombre","apellido","s_apellido"]
         dat_name=[]
         for target in target_nameFields:
             val_target=data_estud[0][target]
             if(val_target!="" and val_target!="..."):
                 dat_name.append(val_target)     
         fullname=" ".join(dat_name)
         last_year=int(data_estud[0]["last_year"])
         
         conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
         orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","fsn","ov","gcrp"]     
         res=[True]
         info=[]
         info.append(data_estud[0][constantes.CLAVE_ESTUDIANTE])  
         info.append(fullname.upper())
         res.append(info)
         have_califics=False         
         
         #Get the Califications of Student in Order
         for i in range(0,last_year):
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,"año"],"condition_Types":["and","and"],"conditions_Values":[cedula,str(i+1)],"conditions_Verify":["=","="]}              
            data_temp=conexion_bd.get_allData([constantes.CLAVE_AREA_FORMACION,"valor"],cond_data,None,True)          
            if(len(data_temp)<=0):
               continue
            if(have_califics==False):
                 have_califics=True
            next_row=[]
            next_row.append(str(i+1))
            for name_area in orden:
                for calific in (data_temp):
                    if(name_area==calific[constantes.CLAVE_AREA_FORMACION].lower()):
                        next_row.append([calific[constantes.CLAVE_AREA_FORMACION],calific["valor"]])
                        break
            res.append(next_row)
         if(have_califics==False):
             return [False,"El Estudiante no Tiene Ninguna Calificacion Registrada"]
         return res      
    
    #Add a New Calification
    def new_calific(self,data,fecha):
        from conexion_bd import conexion_bd
        from General import General
        
        #Get Calification Final Associated to the Formation Area if Exist
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],"condition_Types":["and","and","and"],"conditions_Values":[data["Id_Estud"],data["Area"],data["Year"]],"conditions_Verify":["=","=","="]}              
        data_calif_f=conexion_bd.get_allData([constantes.CLAVE_CALIFICACION_FINAL],cond_data,None,True)                
        id_calif_f=""
        if(len(data_calif_f)>0):
           id_calif_f=data_calif_f[0][constantes.CLAVE_CALIFICACION_FINAL]
        else:
           #Estudent without Calification On the Formation Area
           id_calif_f= data["Id_Estud"]+"-"+ data["Area"]+ data["Year"]
           data_calific_final={constantes.CLAVE_CALIFICACION_FINAL:id_calif_f,constantes.CLAVE_ESTUDIANTE:data["Id_Estud"],"año":data["Year"],constantes.CLAVE_AREA_FORMACION:data["Area"],"valor":"01","modificado":fecha}
           res_add=conexion_bd.add_data(data_calific_final,True)
           if(res_add<0):
              return False
        
        #Get Calification Associated to the Formation Area and Academic Momento if Exist
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],"condition_Types":["and","and"],"conditions_Values":[id_calif_f,data["Momento"]],"conditions_Verify":["=","="]}               
        data_calific_mom=conexion_bd.get_allData([constantes.CLAVE_CALIF_MOM,constantes.CLAVE_MOMENTO,"estimulacion"],cond_data,None,True)
        id_calif_mom=""
        estimul=""
        if(len(data_calific_mom)<=0):
            #Estudent without Califications On the Academic Moment
            id_calif_mom=f"MomentCalification_{id_calif_f}_{data['Momento']}_{data['Year']}"
            data_mom=[ id_calif_mom,data["Momento"],id_calif_f,"1.0","01","0",data["Year"],fecha]
            estimul="0"
            res_add=conexion_bd.add_data(data_mom,True)
            if(res_add<0):
              return False
        else: 
            estimul=data_calific_mom[0]["estimulacion"]
            id_calif_mom=data_calific_mom[0][constantes.CLAVE_CALIF_MOM]
        
        
        #Make the Register
        data_register={}           
        data_register[constantes.CLAVE_CALIF_MOM]=id_calif_mom
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_calif_mom],"conditions_Verify":["="]}               
        evals=conexion_bd.get_allData(["numero"],cond_data)
        num_eval=len(evals)+1
        if(num_eval>constantes.MAXIMO_EVALUACIONES):
            General.show_message("el maximo de evaluaciones posibles es diez evaluacion","demasiadas evaluaciones")
            return False
        data_register["numero"]="evaluacion "+str(num_eval)
        calif_register=data["Calification"]
        if(int(calif_register)<1):
            calif_register="01"
        else:
            if(len(calif_register)<2):
               calif_register="0"+calif_register
        data_register["valor"]=calif_register
        data_register[constantes.CLAVE_CALIFICACION]=f"calificacion_{data_register['numero']}_{id_calif_mom}"
        data_register["modificado"]=fecha
        res_add=conexion_bd.add_data(data_register,True)
        if(res_add<0):
           return False
           
        #Calculate New Values of Calificacions for the Definitive (Calification Final) and Academic Momento
        prom=0.0
        new_calif_mom=self.calculate_calif_mom(id_calif_mom,data["Area"],data["Momento"])
        prom=new_calif_mom["Promedio"]
        if(prom<=0.0):
           General.show_error("Error Calculando Nueva Calificacion para el Momento Academico","Error")
           return False
          
        calif_mom=int(round(prom)) 
        estimul=int(estimul)
        str_prom=""
        str_calif=""
        str_calif=str(calif_mom)
        str_prom=str(prom)
        if(len(str_calif)<2):
            str_calif="0"+str_calif                   
        prom_data=[prom,calif_mom,estimul,calif_mom+estimul] 
        
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM) 
        cond_data={"conditions_Names":[constantes.CLAVE_CALIF_MOM],"condition_Types":["and"],"conditions_Values":[id_calif_mom],"conditions_Verify":["="]}              
        conexion_bd.update_data({"prom":str_prom,"definitiva":str_calif,"modificado":fecha},cond_data)   
       
        new_calific= self.recalculate_calification(id_calif_f,{"Id":id_calif_mom,"Value":str_calif})
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        cond_data={"conditions_Names":[constantes.CLAVE_CALIFICACION_FINAL],"condition_Types":["and"],"conditions_Values":[id_calif_f],"conditions_Verify":["="]}                       
        conexion_bd.update_data({"valor":new_calific,"modificado":fecha},cond_data)
        return True
        
        
                          