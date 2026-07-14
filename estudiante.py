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

    #get the data of Student
    def get_data_estud(self,cedula,repres=""):
        dat=[]
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)        
        data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
        conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
        data_repres=[]
        if(data_estud!=[] and repres!=""):
            data_repres_temp=conexion_bd.get_allData(constantes.CAMPOS_REPRESENTANTE,len(constantes.CAMPOS_REPRESENTANTE),[constantes.CLAVE_REPRESENTANTE],[repres],["and"])
            if(data_repres_temp!=[]):
                for col in range(0,len(data_repres_temp[0])):
                    if(col==1):
                        id_nomb=data_repres_temp[0][col]
                        conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                        data_nomb_repres=conexion_bd.get_allData(["nombre","apellido","s_nombre","s_apellido"],4,[constantes.CLAVE_NOMBRE],[id_nomb],["and"])
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
            data_exp=conexion_bd.get_allData(constantes.CAMPOS_EXPEDIENTE,len(constantes.CAMPOS_EXPEDIENTE),[constantes.CLAVE_EXPEDIENTE],[data_estud[0][4]],["and"])
            temp_estud=[]
            for i in range(0,len(data_estud[0])):
                if(i==1):
                   conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                   data_nombre=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][i]],["and"])
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
    
    #Verify if is a Valid Student for the Inscription
    def validar_solicit_inscrip(self,data):
 
        from General import General
        from conexion_bd import conexion_bd   
        valido=0
        cedulado=True
        cedula_estud=""

        #Verification Over Student Id
        nacionalidad=""
        if(data[11].lower()=="venezolano"):
            nacionalidad="V-"
        elif(data[11].lower()=="extranjero"):
            nacionalidad="E-"
        if(data[1]=="Si"):
            #Student with Id
            valor_CI=str(data[2])
            if(General.is_valid(valor_CI,constantes.CADENA_SOLONUMERO,False,6)==False):
               valido=-1
            else:
              valor_CI=nacionalidad+valor_CI
              cedula_estud=valor_CI
              self.data_inscrip.append(valor_CI)
              self.data_inscrip.append("True")
        else:
           #estud Without Id
            valor_CI=str(data[3])
            if(valor_CI.startswith("v-") or valor_CI.startswith("V-") or valor_CI.startswith("e-") or valor_CI.startswith("E-")):
               valor_CI=valor_CI.split("-")[1]
            year=data[4]
            cedulado=False
            if(General.is_valid(valor_CI,constantes.CADENA_SOLONUMERO,False,6)==False):
               valido=-3
            elif(General.is_valid(year,constantes.CADENA_YEAR,False)==False):
               valido=-4
            else:   
              cedula_estud=nacionalidad+"1"+year[2]+year[3]+valor_CI
              cedula_repres=data[3]
              self.data_inscrip.append(cedula_estud)
              self.data_inscrip.append("False") 
        if(cedula_estud==""):
           return valido
        
        if(data[0]==0):
           #inscription Nuevo Ingreso
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           if(conexion_bd.id_exist(constantes.CLAVE_ESTUDIANTE,cedula_estud)==True ):
              valido=-5
           else:
               if((data[5].is_previous(data[10],data[9],False)==True and data[5].is_previous(data[8],data[10],False)==True)==False):
                  valido=-8
               else:   
                 self.data_inscrip.append("True")
        else:
           #inscription Regular Student
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           if(conexion_bd.id_exist(constantes.CLAVE_ESTUDIANTE,cedula_estud)==True):               
             self.data_inscrip.append("False")
             data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula_estud],["and"])
             conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
             data_califs=conexion_bd.get_allData(["valor","año"],2,[constantes.CLAVE_ESTUDIANTE],[cedula_estud],["and"])
             aprobadas=True
             have_5_califs=False
             if(data_califs!=[]):
                for cal in data_califs:
                   if(int(cal[0])<1):
                       return -9
                   elif(int(cal[0])<10):
                       aprobadas=False
                   if(cal[1].startswith("5")):
                       have_5_califs=True
             else:
                 aprobadas=False
             if(have_5_califs==False):
                 aprobadas=False
             clave_estatus=data_estud[0][2]
             conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
             data_estatus=conexion_bd.get_allData(["estatus","fecha_inscrip","last_year"],3,[constantes.CLAVE_ESTATUS_ESTUD],[clave_estatus],["and"])[0]
             if(data_estatus[0]=="graduado"):
                return -10
             else:
                if(aprobadas==True):
                    if(data_estatus[2].startswith("5")):
                        conexion_bd.update_data(["estatus"],["graduado"],1,[constantes.CLAVE_ESTATUS_ESTUD],[clave_estatus],["and"])
                        return -10           
             last_inscrip=data_estatus[1]
             if(data[5].is_previous(last_inscrip,data[6])==False):
                valido=-6
             elif((data[5].is_previous(data[10],data[7],False)==True and data[5].is_previous(data[6],data[10],False)==True)==False):
                valido=-7
           else:
              valido=-2
        return valido
    
    
    #Get the Academic Data of Student    
    def get_data_curso(self,cedula):
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
        mat_pends=["False"]
        data_repitiendo=["False"]
        repitiendo=False
        id_estatus=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],1,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])[0][0]  
        conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
        data_estatus=conexion_bd.get_allData(["last_year"],1,[constantes.CLAVE_ESTATUS_ESTUD],[id_estatus],["and"])
        year_curso=data_estatus[0][0]
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        data_pendiente=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
        if(data_pendiente!=[]):
            repitiendo=True
            data_repitiendo=["True"]
            mat_pends=["True"]
            num_pends=len(data_pendiente)
            for old_pend in data_pendiente:
                mat_pends.append([old_pend[3],old_pend[4]]) 
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        data_califs=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,"año"],[cedula,year_curso],["and","and"]) 
        data_califs_old=[]
        if(int(year_curso)>1):
          data_califs_old=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,"año"],[cedula,str(int(year_curso)-1)],["and","and"]) 
        if(repitiendo==False):
            num_pends=0
            mat_pends=["False"]
        if(data_califs!=[] or data_califs_old!=[]):
            #Student with Definitive Califications
            if(repitiendo==False):
                if(data_califs!=[]):
                    for i in range(0,len(data_califs)):
                       valor=data_califs[i][4]
                       if(int(valor)<10):
                          if(num_pends<2):
                              num_pends+=1
                              mat_pends.append([data_califs[i][3],data_califs[i][2]])
                              data_repitiendo.append(data_califs[i][3]+"-"+data_califs[i][2])
                          else:
                            if(repitiendo==False):
                               repitiendo=True
                               data_repitiendo[0]="True"
                            num_pends+=1
                            data_repitiendo.append(data_califs[i][3]+"-"+data_califs[i][2])
                            mat_pends=["False","estudiante repitiendo año"]
                if(data_califs_old!=[]):
                    for j in range(0,len(data_califs_old)):
                       valor=data_califs_old[j][4]
                       if(int(valor)<10):
                          if(num_pends<2):
                              num_pends+=1
                              mat_pends.append([data_califs_old[j][3],data_califs_old[j][2]])
                              data_repitiendo.append(data_califs_old[j][3]+"-"+data_califs_old[j][2])
                          else:
                            if(repitiendo==False):
                               repitiendo=True
                               data_repitiendo[0]="True"
                            num_pends+=1
                            data_repitiendo.append(data_califs_old[j][3]+"-"+data_califs_old[j][2])
                            mat_pends=["False","estudiante repitiendo año"]
            else:
                if(data_califs!=[]):
                    for i in range(0,len(data_califs)):
                        data_repitiendo.append(data_califs[i][3]+"-"+data_califs[i][2])                                
        else:
            return ["1",mat_pends,data_repitiendo]
     
        if(num_pends<=2 ):
            if(num_pends>0):
                mat_pends[0]="True"     
            if(repitiendo==False):
               year_curso=str(int(year_curso)+1)  
        return[year_curso,mat_pends,data_repitiendo]                             
                                        
    #Execute Inscription of Student                     
    def inscribir(self,data):
      
        data_inscrip=data
        from tiempo import tiempo
        from conexion_bd import conexion_bd
        import requests
        time_object=tiempo()
        
        if(data_inscrip[4][0]=="True"):
            conexion_bd.set_tabla(constantes.TABLA_HORARIO)
            data_hor=[conexion_bd.generate_id(True,constantes.CLAVE_HORARIO),"...",data_inscrip[4][7],time_object.get_fecha()]
            conexion_bd.add_data(data_hor)
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            secc=[data_inscrip[4][1],data_inscrip[4][2],data_inscrip[4][3],data_hor[0],data_inscrip[4][4],data_inscrip[4][5],data_inscrip[4][6],time_object.get_fecha()]
            conexion_bd.add_data(secc)     
        else:
            conexion_bd.set_tabla(constantes.TABLA_SECCION)
            conexion_bd.update_data(["total_estud","modificado"],[data_inscrip[4][4],time_object.get_fecha()],2,[constantes.CLAVE_SECCION],[data_inscrip[4][1]],["and"])
        if(data_inscrip[0][2]=="True"):
           #Student 'Nuevo Ingreso'
           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
           estudent_dir=[conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION),data_inscrip[3][2],data_inscrip[3][3],data_inscrip[3][4],time_object.get_fecha()]
           conexion_bd.add_data(estudent_dir)
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           id_exp=conexion_bd.generate_id(True,constantes.CLAVE_EXPEDIENTE)
           exp=[]
           try:
                exp=[id_exp,data_inscrip[1][7],data_inscrip[1][10],time_object.get_fecha(),time_object.get_fecha()]
           except:
                print("excepcion en expediente")
                print(data_inscrip)
                exp=[id_exp,"...","...",time_object.get_fecha(),time_object.get_fecha()]
           
           #Add Expedent Data
           if(exp[1]!="" and exp[1]!="..."):
               try:
                  if(exp[1].startswith("expedientes/")==False):
                    url=constantes.SERVER+"upload_expediente.php"
                    with open(exp[1],"rb") as temp_file:
                      dict_exp={"file":temp_file}
                      response=requests.post(url,files=dict_exp)
                      res=response.text.strip()
                      exp[1]=res
                      if(res.startswith("expedientes/")==False):
                         exp[1]="..."
                         General.show_error("error subiendo expediente, por favor vuelva a subirlo desde la opcion actualizar extudiante","error de expediente")      
              
               except:
                    print("excepcion de lectura expediente")
                    exp[1]="..."
            
           if(exp[2]!="" and exp[2]!="..."):
               try:   
                  if(exp[2].startswith("fotos/")==False):
                    url=constantes.SERVER+"upload_foto.php"
                    with open(exp[2],"rb") as temp_foto:
                      dict_foto={"file":temp_foto}
                      response=requests.post(url,files=dict_foto)
                      res=response.text.strip()
                      exp[2]=res
                      if(res.startswith("fotos/")==False):
                         exp[2]="..."
                         General.show_error("error subiendo foto del expediente, por favor vuelva a subirlo desde la opcion actualizar extudiante","error de expediente")              
               except:
                    print("excepcion de letura foto")
                    exp[2]="..."               
           conexion_bd.add_data(exp)
           conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)     
           if(conexion_bd.id_exist(constantes.CLAVE_REPRESENTANTE,data_inscrip[2][0])==False):
                #Add data of Representant
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                data_nombre_representant=[conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE),data_inscrip[2][1],data_inscrip[2][11],data_inscrip[2][2],data_inscrip[2][12],time_object.get_fecha()]
                conexion_bd.add_data(data_nombre_representant)
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                dir_representant_code=conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION)
                conexion_bd.add_data([dir_representant_code,data_inscrip[2][7],data_inscrip[2][8],data_inscrip[2][9],time_object.get_fecha()])
                conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                repres=[data_inscrip[2][0],data_nombre_representant[0],data_inscrip[2][3],data_inscrip[2][4],data_inscrip[2][13],dir_representant_code,time_object.get_fecha()]               
                conexion_bd.add_data(repres)
           else:
                conexion_bd.update_data(["telef","correo","ocupacion","modificado"],[data_inscrip[2][3],data_inscrip[2][4],data_inscrip[2][13] ,time_object.get_fecha()],4,[constantes.CLAVE_REPRESENTANTE],[data_inscrip[2][0]],["and"])
                old_representant=conexion_bd.get_allData([constantes.CLAVE_NOMBRE,constantes.CLAVE_DIRECCION],2,[constantes.CLAVE_REPRESENTANTE],[ data_inscrip[2][0]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                conexion_bd.update_data(["nombre","apellido","s_nombre","s_apellido","modificado"],[data_inscrip[2][1],data_inscrip[2][2],data_inscrip[2][11],data_inscrip[2][12],time_object.get_fecha()],5,[constantes.CLAVE_NOMBRE],[old_representant[0][0]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                conexion_bd.update_data(["sector","parroquia","casa","modificado"],[data_inscrip[2][7],data_inscrip[2][8],data_inscrip[2][9],time_object.get_fecha()],4,[constantes.CLAVE_DIRECCION],[old_representant[0][1]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
           data_nombre=[conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE),data_inscrip[1][0],data_inscrip[1][2],data_inscrip[1][1],data_inscrip[1][3],time_object.get_fecha()]
           conexion_bd.add_data(data_nombre)
           conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
           temp_estado=data_inscrip[1][4]
           estado=data_inscrip[1][4]
           if(estado=="irregular"):
              estado="activo"
           data_estatus=[conexion_bd.generate_id(True,constantes.CLAVE_ESTATUS_ESTUD),estado,data_inscrip[1][5],data_inscrip[0][1],data_inscrip[1][9],time_object.get_fecha(),time_object.get_fecha(),data_inscrip[1][11],time_object.get_fecha()]
           conexion_bd.add_data(data_estatus)
           conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
           estud=[data_inscrip[0][0],data_nombre[0],data_estatus[0],data_inscrip[4][1],exp[0],data_inscrip[2][0],data_inscrip[1][6],data_inscrip[1][8],estudent_dir[0],data_inscrip[2][10],time_object.get_fecha()]
           conexion_bd.add_data(estud)
           if(temp_estado=="irregular"):
             #inscription Irregular (Nuevo Ingreso But not First Year)
             num_years=int(data_inscrip[1][9])-1
             for i in range(0,num_years):
               conexion_bd.set_tabla(constantes.TABLA_AREA_FORMACION)
               areas_incorp=conexion_bd.get_allData(constantes.CAMPOS_AREA_FORMACION,len(constantes.CAMPOS_AREA_FORMACION),["incorporada"],["Si"],["and"])
               for j in range(0,len(areas_incorp)):
                  field_year=str(i+1)+"_año"
                  conexion_bd.set_tabla(constantes.TABLA_AÑOS_INCORPORADOS)
                  data_yrs=conexion_bd.get_allData([constantes.CLAVE_AÑOS_INCORPORADOS],1,[constantes.CLAVE_AÑOS_INCORPORADOS,field_year],[areas_incorp[j][2],"True"],["and","and"])
                  if(data_yrs!=[]):
                     conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                     conexion_bd.add_data([data_inscrip[0][0]+"-"+areas_incorp[j][0]+str(i+1),data_inscrip[0][0],str(i+1),areas_incorp[j][0],"0",time_object.get_fecha()]) 
        else:
             #Regular Student
          try:       
             conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
             old_estatus=conexion_bd.get_allData([constantes.CLAVE_ESTATUS_ESTUD],1,[constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])
             if(old_estatus==[]):
                General.show_error("error obtenido data de estatus, vuelva a intentarlo","error de datos")
                return                
             conexion_bd.update_data([constantes.CLAVE_SECCION,"parentesco"],[data_inscrip[4][1],data_inscrip[2][10]],2,[constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])
             conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
             conexion_bd.update_data(["salud","fecha_inscrip","modificado","last_year","estatus"],[data_inscrip[1][5],time_object.get_fecha(),time_object.get_fecha(),data_inscrip[1][9],"activo"],5,[constantes.CLAVE_ESTATUS_ESTUD],[old_estatus[0][0]],["and"])  
             conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)     
             if(conexion_bd.id_exist(constantes.CLAVE_REPRESENTANTE,data_inscrip[2][0])==False):
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                data_nombre_representant=[conexion_bd.generate_id(True,constantes.CLAVE_NOMBRE),data_inscrip[2][1],data_inscrip[2][11],data_inscrip[2][2],data_inscrip[2][12],time_object.get_fecha()]
                conexion_bd.add_data(data_nombre_representant)
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                dir_representant_code=conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION)
                conexion_bd.add_data([dir_representant_code,data_inscrip[2][7],data_inscrip[2][8],data_inscrip[2][9],time_object.get_fecha()])
                conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)   
                repres=[data_inscrip[2][0],data_nombre_representant[0],data_inscrip[2][3],data_inscrip[2][4],data_inscrip[2][13],dir_representant_code,time_object.get_fecha()]
                conexion_bd.add_data(repres)
             else:
                conexion_bd.update_data(["telef","correo","ocupacion","modificado"],[data_inscrip[2][3],data_inscrip[2][4],data_inscrip[2][13] ,time_object.get_fecha()],4,[constantes.CLAVE_REPRESENTANTE],[data_inscrip[2][0]],["and"])
                old_representant=conexion_bd.get_allData([constantes.CLAVE_NOMBRE,constantes.CLAVE_DIRECCION],2,[constantes.CLAVE_REPRESENTANTE],[ data_inscrip[2][0]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                conexion_bd.update_data(["nombre","apellido","s_nombre","s_apellido","modificado"],[data_inscrip[2][1],data_inscrip[2][2],data_inscrip[2][11],data_inscrip[2][12],time_object.get_fecha()],5,[constantes.CLAVE_NOMBRE],[old_representant[0][0]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                conexion_bd.update_data(["sector","parroquia","casa","modificado"],[data_inscrip[2][7],data_inscrip[2][8],data_inscrip[2][9],time_object.get_fecha()],4,[constantes.CLAVE_DIRECCION],[old_representant[0][1]],["and"])
             conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
             old_data_estud=conexion_bd.get_allData([constantes.CLAVE_REPRESENTANTE,constantes.CLAVE_DIRECCION,constantes.CLAVE_NOMBRE],3,[constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])
             if(old_data_estud!=[]):
                if(data_inscrip[2][0]!=old_data_estud[0][0]):
                        old_repres=old_data_estud[0][0]
                        conexion_bd.update_data([constantes.CLAVE_REPRESENTANTE],[data_inscrip[2][0]],1,[constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])                      
                        resto=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_REPRESENTANTE],[old_repres],["and"])
                        if(len(resto)<=0):
                            conexion_bd.set_tabla(constantes.TABLA_REPRESENTANTE)
                            old_dat_representant=conexion_bd.get_allData([constantes.CLAVE_NOMBRE,constantes.CLAVE_DIRECCION],2,[constantes.CLAVE_REPRESENTANTE],[old_repres],["and"])
                            conexion_bd.delete_data([constantes.CLAVE_REPRESENTANTE],[old_repres],["and"])
                            if(old_dat_representant!=[]):
                                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                                conexion_bd.delete_data([constantes.CLAVE_NOMBRE],[old_dat_representant[0][0]],["and"])
                                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                                conexion_bd.delete_data([constantes.CLAVE_DIRECCION],[old_dat_representant[0][1]],["and"])       
                conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                conexion_bd.update_data(["sector","parroquia","casa","modificado"],[data_inscrip[3][2],data_inscrip[3][3],data_inscrip[3][4],time_object.get_fecha()],4,[constantes.CLAVE_DIRECCION],[old_data_estud[0][1]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
                conexion_bd.update_data(["nombre","s_nombre","apellido","s_apellido","modificado"],[data_inscrip[1][0],data_inscrip[1][2],data_inscrip[1][1],data_inscrip[1][3],time_object.get_fecha()],5,[constantes.CLAVE_NOMBRE],[old_data_estud[0][2]],["and"])
             if(data_inscrip[7][0]!="False"):
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                for reprobad_index in range(1,len(data_inscrip[7])):
                   temp_reprobad=data_inscrip[7][reprobad_index].split("-")
                   area=temp_reprobad[0]
                   year=temp_reprobad[1]
                   conexion_bd.delete_data([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[data_inscrip[0][0],area,year],["and","and","and"])
             conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
             temp_pendent=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])
             if(temp_pendent!=[]):
                conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
                for i in range(0,len(temp_pendent)):
                     conexion_bd.delete_data([constantes.CLAVE_MATERIA_PENDIENTE],[temp_pendent[i][0]],["and"])
                conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)  
             conexion_bd.delete_data([constantes.CLAVE_ESTUDIANTE],[data_inscrip[0][0]],["and"])
          except:
              General.show_error("error inesperado obtiendo data del servidor,renicie el programa vuelva a intentarlo","error inesperado")
              return
        if(data_inscrip[5][0]!="False"): 
            pendiente=data_inscrip[5]
            for i in range(1,len(pendiente)):
                 conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                 pend=[conexion_bd.generate_id(),data_inscrip[0][0],"0",pendiente[i][0],pendiente[i][1],time_object.get_fecha()]
                 conexion_bd.add_data(pend)
            
    #Verification for data Assocated to Rendimiento Process of a Student
    def verificar_data_rendimiento(self,data,tipo):
        from General import General
        if(tipo==0):
          if(data[0]=="" or data[0]==" "):
             return -1
          if(data[3]=="elejir" or data[3]=="elegir"):
             return -1
          if(data[4]=="" or data[4]==" "):
             return -1 
          if(data[5]=="" or data[5]==" "):
             return -1 

          if(data[1]=="elejir" or data[1]=="elegir"):
             return -2
          if(data[2]=="elegir" or data[2]=="elejir"):
             return -3

        elif(tipo==1):
          if(data[0]=="" or data[0]==" "):
             return -1
          if(data[2]=="elejir" or data[2]=="elegir"):
             return -1
          if(data[3]=="" or data[3]==" "):
             return -1 
          if(data[4]=="" or data[4]==" "):
             return -1 

          if(data[1]=="elejir" or data[1]=="elegir"):
             return -2 
        return True 

    #Verify if The Modification in the St
    def is__valid_modific(self,cedula,cedulado,data_estud,data_repres,data_exp,data_dir):
        
        from General import General
        from conexion_bd import conexion_bd
        data_estud_valid=[cedula,"","","","",cedulado,"","","","","","","",""]
        data_repres_valid=["","","","","","","","",""]
        data_exp_valid=["",""]
        data_dir_valid=["","",""]
        data_dir_repres_valid=["","",""]
        update_ced=[False,""]
        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
        d_estud=conexion_bd.get_allData([constantes.CLAVE_SECCION,constantes.CLAVE_EXPEDIENTE,constantes.CLAVE_REPRESENTANTE,constantes.CLAVE_DIRECCION],4,[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
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
   
        d_e=conexion_bd.get_allData(["src_exp","src_foto"],2,[constantes.CLAVE_EXPEDIENTE],[id_exp],["and"])[0]
        
        if(data_exp[0]!=""):
           
           if(data_exp[0].endswith(".rar") or data_exp[0].endswith(".zip")):
               filename=data_exp[0].split("/")
               f="expedientes/"+filename[len(filename)-1]
               if(conexion_bd.id_exist("src_exp",f)==True):
                  
                  if((d_e[0]==f)==False):
                     return [-14]
                  else:
                    data_exp_valid[0]=data_exp[0]
               else:
                 data_exp_valid[0]=data_exp[0]
           else:
              return [-12]  
              
        if(data_exp[1]!=""):
           if(data_exp[1].endswith(".png") or data_exp[1].endswith(".jpg")):
              filename=data_exp[1].split("/")
              f="fotos/"+filename[len(filename)-1]
              if(conexion_bd.id_exist("src_foto",f)==True):
                
                 if((d_e[1]==f)==False):
                     return [-15]
                 else:
                    data_exp_valid[1]=data_exp[1]
              else:
                data_exp_valid[1]=data_exp[1]
           else:
              return [-13]    

           
        return [True,data_estud_valid,update_ced,data_repres_valid,data_exp_valid,data_dir_valid,data_dir_repres_valid]
    
    #Remove Calification Estimulation for an Area of Formation    
    def borrar_estimulacion(self,dat_rend,fecha):
        from General import General
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        data_calif_final=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],dat_rend[3]],["and","and","and"])
        if(data_calif_final==[]):
           return[-2,"",""]
        id_calif_final=data_calif_final[0][0]
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        data_area_actual=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_calif_final,dat_rend[2]],["and","and"])
        if(data_area_actual!=[]):  
            if(int(data_area_actual[0][5])>0):        
                conexion_bd.update_data(["estimulacion","modificado"],["0",fecha],2,[constantes.CLAVE_CALIF_MOM],[data_area_actual[0][0]],["and"])
                all_califs=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_calif_final],["and"])
                suma=0
                for calif_mom in all_califs:
                    suma+=int(calif_mom[4])+int(calif_mom[5])
                if(suma>0):
                   suma=int(suma/len(all_califs))
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                conexion_bd.update_data(["valor","modificado"],[str(suma),fecha],2,[constantes.CLAVE_CALIFICACION_FINAL],[id_calif_final],["and"])
                valor_momento=["","","",""]
                valor_momento[0]=float(data_area_actual[0][3])
                valor_momento[1]=int(data_area_actual[0][4])
                valor_momento[2]=0
                valor_momento[3]=int(data_area_actual[0][4])
                return[True,valor_momento,]
            else:
              return [-1,"",""]
        else:
           return[-2,"",""]
     
    #Estimulate an Area of Formacion of Studente     
    def estimular_area(self,dat_rend,fecha):
        from General import General
        from conexion_bd import conexion_bd
        continuar=True
        result=[-1,"",""]
        
        if(dat_rend[4]!=""):
           if(General.is_valid(dat_rend[4],constantes.CADENA_SOLONUMERO,False,0)==False ):
                  continuar=False
        if(dat_rend[5]!=""):
            if(General.is_valid(dat_rend[5],constantes.CADENA_SOLONUMERO,False,0)==False ):
                  continuar=False
        if(dat_rend[4]=="" and dat_rend[5]==""): 
           continuar=False
           
        if(continuar==True):
            max_val=2
            val_estimul=0
            val_estimul2=0
            if(dat_rend[4]!=""):
                val_estimul=int(dat_rend[4])
            if(dat_rend[5]!=""):
                val_estimul2=int(dat_rend[5])
            val_estimul_actual=0
            if(val_estimul>1 or val_estimul2>1):
                 return[-7,"",""]
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            data_f=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],dat_rend[3]],["and","and","and"])    
            if(data_f==[]):
               return[-3,"",""]
            id_f=data_f[0][0]
            data_areas=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,"año"],[dat_rend[0],dat_rend[3]],["and","and"])
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            if(data_areas==[]):
               return[-2,"",""]
            data_area_actual=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_f,dat_rend[2]],["and","and"])
            if(data_area_actual==[]):
                return[-3,"",""]
            val_estimul_actual=0                
            for i in range(0,len(data_areas)):
                dat_mom=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[data_areas[i][0],dat_rend[2]],["and","and"])
                pt_estimul=0
                if(dat_mom!=[] ):
                    if(dat_mom[0][0]!=data_area_actual[0][0]):
                       pt_estimul=int(dat_mom[0][5])
                       if(pt_estimul>0 and max_val>0):
                           max_val-=pt_estimul
                           if(max_val<0):
                               max_val=0
            if((val_estimul+val_estimul2)<0 or (val_estimul+val_estimul2)>2):
                     return[-4,"",""]
            if((val_estimul+val_estimul2)>max_val):
                return[-5,"",""]
            if((int(data_area_actual[0][6])+(val_estimul+val_estimul2))>20 or int(data_area_actual[0][6])>=20):
                 return[-6,"",""]   
            if(General.show_confirmDialog("esta seguro que desea estimular la calificacion de esta area?","borrar calificacion")!=True):
                return["","",""]
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            conexion_bd.update_data(["estimulacion","modificado"],[str(val_estimul+val_estimul2),fecha],2,[constantes.CLAVE_CALIF_MOM],[data_area_actual[0][0]],["and"])
            data_nueva=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIF_MOM],[data_area_actual[0][0]],["and"])
            all_califs=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            suma=0
            for calific_mom in all_califs:
                suma+=int(calific_mom[4])+int(calific_mom[5])
            if(suma>0):
                suma=int(suma/len(all_califs))
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[str(suma),fecha],2,[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            data_califs=[0.0,0.0,0,0.0]
            if(data_nueva!=[]):
                data_califs[0]=float(data_nueva[0][3])
                data_califs[1]=int(data_nueva[0][4])
                data_califs[2]=int(data_nueva[0][5])
                data_califs[3]=data_califs[1]+data_califs[2]
            return [True,data_califs]
        return result
           
    #Modify a Calification Definitive      
    def modific_calif_final(self,dat,fecha): 
       from conexion_bd import conexion_bd
       from General import General
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[dat[0]],["and"])
       if(data_estud==[]):
          return -1
       
       conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
       data_estatus=conexion_bd.get_allData(["estatus","last_year"],2,[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][2]],["AND"])
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       data_califs=conexion_bd.get_allData(["valor"],1,[constantes.CLAVE_ESTUDIANTE],[dat[0]],["and"])   
       if(data_califs==[]):
           return -2
       num_pends=0
       for cal in data_califs:
          if(int(cal[0])<1):
            num_pends=num_pends+1
            break        
       if(num_pends==0):
            return -2         
       area=dat[1]
       year=dat[2]
       if(area=="" or year==""):
           return -3
       old_calif=int(dat[3][2])
       if(int(data_estatus[0][1])==int(year)):
           return -4      
       new_calif=dat[4]
       if(General.is_valid(new_calif,constantes.CADENA_SOLONUMERO,False)==False):
           return -5  
       val=int(new_calif)
       if((val>=0 and val<=20)==False):
           return -6
       if(General.show_confirmDialog("esta seguro que de desea modificar la calificacion final?","modificar calificacion")!=True):
           return -7               
       if(val<5):
          val=5
       str_val=str(val)
       if(len(str_val)<2):
          str_val="0"+str_val                      
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       conexion_bd.update_data(["valor","modificado"],[str_val,fecha],2,["año",constantes.CLAVE_AREA_FORMACION,constantes.CLAVE_ESTUDIANTE],[year,area,dat[0]],["and","and","and"])
       pendientes_calif=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,"valor"],[dat[0],"0"],["and","and"])
       conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
       data_pend=conexion_bd.get_allData([constantes.CLAVE_MATERIA_PENDIENTE],1,[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat[0],area,year],["and","and","and"]) 
       if(data_pend!=[]):
           conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
           conexion_bd.delete_data([constantes.CLAVE_MATERIA_PENDIENTE],[data_pend[0][0]],["and"])
           conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
           conexion_bd.delete_data([constantes.CLAVE_MATERIA_PENDIENTE],[data_pend[0][0]],["and"])                    
       if(val<10):
          conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
          data_pend=[conexion_bd.generate_id(True,constantes.CLAVE_MATERIA_PENDIENTE),dat[0],"0.0",area,year,fecha]
          conexion_bd.add_data(data_pend)
                 
       if(len(pendientes_calif)<=0):
          return 1
       else :
          return 0
                  
    #Modify a Calification    
    def modific_calif(self,dat_rend,fecha):
        from General import General
        from conexion_bd import conexion_bd
        if(dat_rend[4]=="" or dat_rend[4]==" "):
            return [-1,"",""]
        if(General.is_valid(dat_rend[5],constantes.CADENA_CALIFICACION,False,0)==True):
              val_cal=float(dat_rend[5])
              if((val_cal>=0.0 and val_cal<=20.0)==False):
                   return [-3,"",""]
        else:
          return [-2,"",""]
        
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        data_f=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],dat_rend[3]],["and","and","and"])    
        id_f=data_f[0][0]
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        data_calific_mom=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_f,dat_rend[2]],["and","and"])
        if(data_calific_mom==[]):
            return [-4,"",""]  
        id_calific=data_calific_mom[0][0]
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        val_cal=dat_rend[5]
        if(int(val_cal)<5):
           val_cal="05"
        else:
          if(len(val_cal)<2):
             val_cal="0"+val_cal                 
        conexion_bd.update_data(["valor","modificado"],[val_cal,fecha],2,[constantes.CLAVE_CALIF_MOM,"numero"],[id_calific,dat_rend[4]],["and","and"])  
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        calificaciones=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])
        prom=0.0
        calif=0
        list_calif=[]
        prom_data=[0.0,0.0,0,0.0]
        if(calificaciones!=[]):
            for i in range(0,len(calificaciones)):
                prom+=float(calificaciones[i][2])
                dat_row=[calificaciones[i][3], dat_rend[1],dat_rend[2],calificaciones[i][2]]
                list_calif.append(dat_row)
            prom/=len(calificaciones)
            prom=round(prom,2)
            calif=int(round(prom)) 
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            estimul=int(data_calific_mom[0][5])
            str_prom=""
            str_calif=""
            if(calif<5):
               str_calif="05"
               str_prom="5.0"
               prom=5.0
               calif=5
            else:
               str_calif=str(calif)
               str_prom=str(prom)
               if(len(str_calif)<2):
                  str_calif="0"+str_calif                   
            prom_data=[prom,calif,estimul,calif+estimul]
            conexion_bd.update_data(["prom","definitiva","modificado"],[str_prom,str_calif,fecha],3,[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])            
            all_moments=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            suma=0.0
            for dat_mom in all_moments:
               suma+=int(dat_mom[4])+int(dat_mom[5])       
            if(suma>0.0):
               suma/=len(all_moments)
               suma=int(round(suma))
            str_suma=str(suma)
            if(len(str_suma)<2):
               str_suma="0"+str_suma              
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],1,[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
        else:
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            conexion_bd.update_data(["prom","definitiva","modificado"],[str(0.0),str(0),fecha],3,[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])            
            all_moments=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            suma=0.0
            for dat_mom in all_moments:
               suma+=int(dat_mom[4])+int(dat_mom[5])    
            if(suma>0.0):
               suma/=len(all_moments)
               suma=int(round(suma))
            if(suma<5):
                suma=5 
            str_suma=str(suma)
            if(len(str_suma)<2):
                 str_suma="0"+str_suma            
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],1,[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
        return [True,list_calif,prom_data]            
    
    #Remove a Calification
    def delete_calif(self,dat_rend,fecha):
       if(dat_rend[4]=="" or dat_rend[4]==" "):
          return [-1,"",""]
       if(dat_rend[3]=="" or dat_rend[3]==" "):
          return [-1,"",""]
       from conexion_bd import conexion_bd
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
       data_f=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],dat_rend[3]],["and","and","and"])    
       id_f=data_f[0][0]
       conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
       data_calific_mom=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_f,dat_rend[2]],["and","and"])
       if(data_calific_mom==[]):
           return [-4,"",""]    
       id_calific=data_calific_mom[0][0]
       conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
       conexion_bd.delete_data([constantes.CLAVE_CALIF_MOM,"numero"],[id_calific,dat_rend[4]],["and","and"])
       calificaciones=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])
       calif_list=[]
       prom_data=[0.0,0.0,0,0.0]
       if(calificaciones!=[]):
            prom=0.0
            calif=0
            count=0
            for i in range(0,len(calificaciones)):
                prom+=float(calificaciones[i][2])
                evaluacion_n="evaluacion "+str(count+1)
                dat_row=[evaluacion_n, dat_rend[1],dat_rend[2],calificaciones[i][2]]
                calif_list.append(dat_row)
                conexion_bd.update_data(["numero"],[evaluacion_n],1,[constantes.CLAVE_CALIFICACION],[calificaciones[i][0]],["and"])
                count+=1
            prom/=len(calificaciones)
            prom=round(prom,2)
            calif=int(round(prom))
            str_calif=""
            str_prom=""
            if(calif<5):
                str_calif="05"
                str_prom="5.0"
                calif=5
                prom=5.0
            else:
              str_calif=str(calif)
              str_prom=str(prom)
              if(len(str_calif)<2):
                 str_calif="0"+str_calif     
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            estimul=int(data_calific_mom[0][5])
            prom_data=[prom,calif,estimul,calif+estimul]
            conexion_bd.update_data(["prom","definitiva","modificado"],[str_prom,str_calif,fecha],3,[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])             
            all_moments=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            suma=0.0
            for dat_mom in all_moments:
               suma+=int(dat_mom[4])+int(dat_mom[5])         
            if(suma>0.0):
                suma/=len(all_moments)
                suma=int(round(suma))
            if(suma<5):
                suma=5
            str_suma=str(suma)
            if(len(str_suma)<2):
               str_suma="0"+str_suma              
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],1,[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])            
       else:
            prom_data=[5.0,5,0,5]
            conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
            conexion_bd.update_data(["prom","definitiva","modificado"],["5.0","05",fecha],3,[constantes.CLAVE_CALIF_MOM],[id_calific],["and"])            
            all_moments=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])
            suma=0.0
            for dat_mom in all_moments:
               suma+=int(dat_mom[4])+int(dat_mom[5])       
            if(suma>0.0):
               suma/=len(all_moments)
               suma=int(round(suma))
            if(suma<5):
                  suma=5.0
            str_suma=str(suma)
            if(len(str_suma)<2):
                 str_suma="0"+str_suma              
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],1,[constantes.CLAVE_CALIFICACION_FINAL],[id_f],["and"])     
       return [True,calif_list,prom_data]          
        
    #Add a Try for Materia Pendiente   
    def mat_pendiente(self,dat_rend,fecha):
        from General import General
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
        data_m_pen=conexion_bd.get_allData(constantes.CAMPOS_MATERIA_PENDIENTE,len(constantes.CAMPOS_MATERIA_PENDIENTE),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],[dat_rend[0],dat_rend[1]],["and","and"])               
        intento_val=dat_rend[3]
        conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
        data_c_pen=conexion_bd.get_allData(constantes.CAMPOS_CALIF_PENDIENTE,len(constantes.CAMPOS_CALIF_PENDIENTE),[constantes.CLAVE_MATERIA_PENDIENTE,"intento"],[data_m_pen[0][0],intento_val],["and","and"])               
        year_pend=data_m_pen[0][4]
        if(data_c_pen!=[]):
           #el intento de materia pendiente o revision ya existe
             return [-1,""]
        calif=dat_rend[4]
        if(General.is_valid(calif,constantes.CADENA_SOLONUMERO,False)==False):
            return [-2,""]
        elif((int(calif)>=0 and int(calif)<=20)==False):
            return [-3,""]
        rg_valid=True
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        cronog=conexion_bd.get_allData(None,None)
        if(cronog==[]):
            General.show_error("no existe un cronograma activo","cronograma inexistente")
            return         
        conexion_bd.set_tabla(constantes.TABLA_FECHA)
        razon="materia pendiente "+intento_val[len(intento_val)-1]
        if(intento_val=="revision"):
            razon=intento_val       
        data_cronog=conexion_bd.get_allData(["fecha","fecha_cierre"],2,["razon",constantes.CLAVE_CRONOGRAMA],[razon,cronog[0][0]],["and","and"])
        if(data_cronog!=[]):
            inicio=data_cronog[0][0]
            cierre=data_cronog[0][1]
            from tiempo import tiempo
            time_object=tiempo()
            if(time_object.is_previous(time_object.get_fecha(),inicio)==True or time_object.is_previous(cierre,time_object.get_fecha())==True):
               return[-5,""]
       
        else:
            return[-4,""]        
        if(int(calif)>=10):
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            conexion_bd.delete_data([constantes.CLAVE_MATERIA_PENDIENTE,],[data_m_pen[0][0],],["and",])
            conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
            conexion_bd.delete_data([constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],[dat_rend[0],dat_rend[1]],["and","and"])
            conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
            conexion_bd.update_data(["valor","modificado"],[calif,fecha],1,[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[dat_rend[0],dat_rend[1],year_pend],["and","and","and"])
            return [True,True]
                       
        else:
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            codigo_c=conexion_bd.generate_id(True,constantes.CLAVE_CALIF_PENDIENTE)
            valores=[codigo_c,data_m_pen[0][0],intento_val,calif,fecha,fecha]
            conexion_bd.set_tabla(constantes.TABLA_CALIF_PENDIENTE)
            conexion_bd.add_data(valores)
            temp_v=data_m_pen[0][2]
            if(temp_v=="" or temp_v==" " or temp_v=="0.0"):
                temp_v="0"
            temp_v=int(temp_v)
            if(temp_v<int(calif)):
                conexion_bd.set_tabla(constantes.TABLA_MATERIA_PENDIENTE)
                conexion_bd.update_data(["max_calif","modificado"],[calif,fecha],1,[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION],[dat_rend[0],dat_rend[1]],["and","and"])           
            return [True,False]
                 
    #Get the Califiactions of a Student for an Area, momento and year of Study
    def get_calificaciones(self,cedula,area,mom,year,fecha):
        from conexion_bd import conexion_bd
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        data_calific_f=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[cedula,area,year[0]],["and","and","and"])
        if(data_calific_f!=[]):
          id_calific_f=data_calific_f[0][0]
          conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
          data_calific_moms=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_calific_f],["and","and"])
          if(data_calific_moms!=[]):
             suma=0
             calif_mom=0
             encontrado=False
             for i in range(0,len(data_calific_moms)):
                valor=int(data_calific_moms[i][4])+int(data_calific_moms[i][5])
                if(valor<5):
                   valor=5
                suma+=valor
                if(data_calific_moms[i][1]==mom):
                   encontrado=True
                   calif_mom=int(data_calific_moms[i][4])
                   if(calif_mom<5):
                      calif_mom=5                     
             if(suma!=0):
                suma=int(suma/3)
             if(suma<5):
                 suma=5              
             if(calif_mom==0 and encontrado==False):
                 return -3       
             str_suma=str(suma)
             if(len(str_suma)<2):
                str_suma="0"+str_suma
             str_calif=str(calif_mom)
             if(len(str_calif)<2):
                str_calif="0"+str_calif 
             conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
             conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],2,[constantes.CLAVE_CALIFICACION_FINAL],[id_calific_f],["and"])             
             return str_calif 
          else:
            return -2
        return -1
    
    #Get The Calification Required for Certify Califications as a List
    def get_calif_certific(self,cedula):
         from conexion_bd import conexion_bd        
         conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
         data_estud=conexion_bd.get_allData(constantes.CAMPOS_ESTUDIANTE,len(constantes.CAMPOS_ESTUDIANTE),[constantes.CLAVE_ESTUDIANTE],[cedula],["and"])
         if(data_estud==[]):
            return -1
         conexion_bd.set_tabla(constantes.TABLA_ESTATUS_ESTUD)
         data_estatus=conexion_bd.get_allData(["last_year"],1,[constantes.CLAVE_ESTATUS_ESTUD],[data_estud[0][2]],["AND"])
         conexion_bd.set_tabla(constantes.TABLA_NOMBRE)
         data_nomb=conexion_bd.get_allData(["nombre","s_nombre","apellido","s_apellido"],4,[constantes.CLAVE_NOMBRE],[data_estud[0][1]],["and"])        
         fullname="" 
         for dat_name in data_nomb[0]:
           if(dat_name !="" and dat_name !="..."):
               fullname=fullname+dat_name +" "    
         last_year=int(data_estatus[0][0])
         conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
         orden=["lengua y literatura","castellano","idiomas","ingles","matematica","matematicas","ed fisica","educacion fisica","arte y patrimonio","biologia","biologia ambiente y tecnologia","fisica","quimica","cs tierra","ciencias de la tierra","ghc","fsn","ov","gcrp"]     
         califics=[]
         info=[]
         info.append(data_estud[0][0])  
         info.append(fullname.upper())
         califics.append(info)
         have_califics=False         
         for i in range(0,last_year):
            data_temp=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,"año"],[cedula,str(i+1)],["and","and"])          
            if(data_temp!=[]):
                have_califics=True
                next_row=[]
                next_row.append(str(i+1))
                for j in range(0,len(orden)):
                   for k in range(0,len(data_temp)):
                      if(orden[j]==data_temp[k][3].lower()):
                          next_row.append([data_temp[k][3],data_temp[k][4]])
                califics.append(next_row)
         if(have_califics==False):
             return -2
         return califics      
    
    #Add a New Calification
    def nueva_calific(self,data,dat_rend,fecha):
        from conexion_bd import conexion_bd
        from General import General
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
        data_calif_f=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION_FINAL,len(constantes.CAMPOS_CALIFICACION_FINAL),[constantes.CLAVE_ESTUDIANTE,constantes.CLAVE_AREA_FORMACION,"año"],[ dat_rend[0], dat_rend[1], dat_rend[4]],["and","and","and"])                
        id_calif_f=""
        if(data_calif_f!=[]):
           id_calif_f=data_calif_f[0][0]
        else:
           #Register Definitive Calification if Not Exist
           id_calif_f= dat_rend[0]+"-"+ dat_rend[1]+ dat_rend[4]
           data_f=[id_calif_f,dat_rend[0],dat_rend[4],dat_rend[1],"05",fecha]
           conexion_bd.add_data(data_f)
        conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
        data_calific_mom=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL,constantes.CLAVE_MOMENTO],[id_calif_f,dat_rend[2]],["and","and"])
        id_calif_mom=""
        if(data_calific_mom==[]):
            #Register Calification of Academic Moment if Not Exist
            id_calif_mom=conexion_bd.generate_id(True,constantes.CLAVE_CALIF_MOM)
            data_mom=[ id_calif_mom,dat_rend[2],id_calif_f,"5.0","05","0",dat_rend[4],fecha]
            conexion_bd.add_data(data_mom)
        else: 
            id_calif_mom=data_calific_mom[0][0]
                    
        data[1]=id_calif_mom
        conexion_bd.set_tabla(constantes.TABLA_CALIFICACION)
        evals=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM,],[id_calif_mom],["and"])
        num_eval=len(evals)+1
        if(num_eval>constantes.MAXIMO_EVALUACIONES):
            General.show_message("el maximo de evaluaciones posibles es diez evaluacion","demasiadas evaluaciones")
            return [-3]
        data[3]="evaluacion "+str(num_eval)
        if(int(data[2])<5):
            data[2]="05"
        else:
            if(len(data[2])<2):
               data[2]="0"+data[2]
                    
        data_cal=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM,"numero"],[data[1],data[3]],["and","and"])
        if(data_cal==[]):
            data[0]=conexion_bd.generate_id(True,constantes.CLAVE_CALIFICACION)
            conexion_bd.add_data(data)
            data_calific=conexion_bd.get_allData(constantes.CAMPOS_CALIFICACION,len(constantes.CAMPOS_CALIFICACION),[constantes.CLAVE_CALIF_MOM],[data[1]],["and"])                
            if(data_calific!=[]):
                nota_mom=0
                prom_mom=0.0
                for i in range(0,len(data_calific)):
                    valor=float(data_calific[i][2])
                    prom_mom+=valor
                prom_mom/=len(data_calific)
                prom_mom=round(prom_mom,2)
                nota_mom=int(round(prom_mom))
                str_prom=""
                str_nota=""
                str_def=""
                if(nota_mom<5):
                    str_nota="05"
                    str_prom="5.0"
                else:
                    str_nota=str(nota_mom)
                    str_prom=str(prom_mom)
                    if(len(str_nota)<2):
                        str_nota="0"+str_nota                          
                conexion_bd.set_tabla(constantes.TABLA_CALIF_MOM)
                conexion_bd.update_data(["prom","definitiva","modificado"],[str_prom,str_nota,fecha],3,[constantes.CLAVE_CALIF_MOM],[data[1]],["and"])
                all_moments=conexion_bd.get_allData(constantes.CAMPOS_CALIF_MOM,len(constantes.CAMPOS_CALIF_MOM),[constantes.CLAVE_CALIFICACION_FINAL],[id_calif_f],["and"])
                suma=0.0
                for dat_mom in all_moments:
                    suma+=int(dat_mom[4])+int(dat_mom[5])
                      
                if(suma>0.0):
                    suma/=len(all_moments)
                    suma=int(round(suma))
                if(suma<5):
                    suma=5
                str_suma=str(suma)
                if(len(str_suma)<2):
                    str_suma="0"+str_suma
                conexion_bd.set_tabla(constantes.TABLA_CALIFICACION_FINAL)
                conexion_bd.update_data(["valor","modificado"],[str_suma,fecha],1,[constantes.CLAVE_CALIFICACION_FINAL],[id_calif_f],["and"])
                return [0]      
            else:
                return [-1]
                General.show_message("error al guardar data","error inesperado")
        else:
             return [-2]
             General.show_message("el estudiante ya tiene registrada una calificacion para el area, momento academico y numero de evaluacion indicada","calificacion ya registrada")
                       
                                   