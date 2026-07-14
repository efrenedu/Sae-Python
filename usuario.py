from conexion_bd import conexion_bd
from constantes import *

#Base Class for Save User data and the information required for Execute the process of System
class usuario:
    def __init__(self):
        self.user=""
        self.id_trabaj=""
        self.historia=historial("")
        self.icon=""
        self.permiso=""
        self.data_process=[]
        self.data_expediente=[]
        self.passwd=""
    
    #change the password data
    def change_password(self,new_val):
        self.passwd=new_val
        
    #Save data from Process of System
    def recibe_data_process(self,dat):
          self.data_process.append(dat)
          
    #Return the Data of Current Process of System
    def get_data_process(self):  
          return self.data_process   

    #Reset the data saved from Process of System
    def reset_data_process(self,last_item):
        temp_data=[]
        for i in range(0,last_item):
            temp_data.append(self.data_process[i])
        self.data_process=[]       
        for i in range(0,last_item):
            self.data_process.append(temp_data[i])
        if(len(self.data_process)<=0 ):
            self.data_expediente=[]       
        
    #Execute the Loggin Request from a User        
    def login(self,usr,passw):
        from General import General
        passw=General.encriptar(passw)
        conexion_bd.set_tabla(constantes.TABLA_USUARIO)
        res=conexion_bd.get_allData(constantes.CAMPOS_USUARIO,len(constantes.CAMPOS_USUARIO),conditions=["usuario","password"],values=[usr,passw],condition_types=["and","and"])
        invalid_credentials=-1
        bloqueado=False
        valido=False
        from tiempo import tiempo
        time_object=tiempo()
        hora=time_object.get_tiempo()
        fecha=time_object.get_fecha()
        
        if(usr=="" and passw==""):
             invalid_credentials=2   
        elif(usr=="" and passw!=""):
             invalid_credentials=0
        elif(passw=="" and usr!=""):
             invalid_credentials=1      
        elif(res!=[]):
           #verify User
           if(res[0][6]=="False"):
             #user No Locked
             self.user=res[0][0] #id user
             self.id_trabaj=res[0][2]  #cedula
             self.permiso=res[0][3]  #permiso
             self.icon=res[0][4]  #foto
             self.passwd=res[0][1]
             valido=True
             conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
             data_intentos=conexion_bd.get_allData(constantes.CAMPOS_INTENTOS_USUARIO,len(constantes.CAMPOS_INTENTOS_USUARIO),[constantes.CLAVE_INTENTOS_USUARIO],[res[0][5]],["and"])
             if(int(data_intentos[0][1])>0):
                #Loggin Success ,Remove Failed Try to Loggin 
                conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],[str(0),"",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res[0][5]],["and"])
             conexion_bd.set_tabla(constantes.TABLA_USUARIO)       
           else:
                #user Locked, Verify if is Time to Unlock him
                bloq=True
                conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                data_intentos=conexion_bd.get_allData(constantes.CAMPOS_INTENTOS_USUARIO,len(constantes.CAMPOS_INTENTOS_USUARIO),[constantes.CLAVE_INTENTOS_USUARIO],[res[0][5]],["and"])
                last_tiempo=data_intentos[0][3]
                last_fecha=data_intentos[0][2]
                next_date=time_object.get_next_date3(last_fecha,last_tiempo,20)
                next_date_bloq=time_object.get_next_date3(last_fecha,last_tiempo,60)
                if(time_object.is_previous(next_date_bloq[0],fecha)):
                    num_intentos=0
                    bloq=False
                    conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res[0][5]],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                    conexion_bd.update_data(["bloqueado",],["False"],1,["usuario"],[usr],["and"])              
                elif(time_object.is_previous(next_date_bloq[0],fecha,False)):
                     if(time_object.is_previous_time(next_date_bloq[1],hora)):
                        num_intentos=0
                        bloq=False
                        conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res[0][5]],["and"])
                        conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                        conexion_bd.update_data(["bloqueado",],["False"],1,["usuario"],[usr],["and"])    
                bloqueado=bloq
                if(bloqueado==True):
                   valido=False
                else:
                   self.user=res[0][0] #id user
                   self.id_trabaj=res[0][2]  #cedula
                   self.permiso=res[0][3]  #permiso
                   self.icon=res[0][4]  #foto
                   valido=True
          
        else:
           #Failed Try to login, Veify if Add Failed Try to the Count or Lock Him
           res2=conexion_bd.get_allData(constantes.CAMPOS_USUARIO,len(constantes.CAMPOS_USUARIO),conditions=["usuario"],values=[usr],condition_types=["and"])
           if(res2!=[]):
                conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                data_intentos=conexion_bd.get_allData(constantes.CAMPOS_INTENTOS_USUARIO,len(constantes.CAMPOS_INTENTOS_USUARIO),[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                num_intentos=int(data_intentos[0][1])
                bloq=res2[0][6]
                last_tiempo=data_intentos[0][3]
                last_fecha=data_intentos[0][2]
                next_date=time_object.get_next_date3(last_fecha,last_tiempo,20)
                next_date_bloq=time_object.get_next_date3(last_fecha,last_tiempo,60)
                if(next_date!=" " and bloq=="False"):
                    if(time_object.is_previous(next_date[0],fecha)):
                        conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                        num_intentos=0
                    elif(time_object.is_previous(next_date[0],fecha,False)):
                        if(time_object.is_previous_time(next_date[1],hora)):
                            conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                            num_intentos=0
                elif(next_date_bloq!=" " and bloq=="True"): 
                    if(time_object.is_previous(next_date_bloq[0],fecha)):
                        num_intentos=0
                        bloq="False"
                        conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                        conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                        conexion_bd.update_data(["bloqueado",],["False"],1,["usuario"],[usr],["and"])   
                    elif(time_object.is_previous(next_date_bloq[0],fecha,False)):
                        if(time_object.is_previous_time(next_date_bloq[1],hora)):
                            num_intentos=0
                            bloq="False"
                            conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["0","",""],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                            conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                            conexion_bd.update_data(["bloqueado",],["False"],1,["usuario"],[usr],["and"])
                if(bloq=="True"):
                    bloqueado=True
                if(bloq=="False" and num_intentos>=3):
                    conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                    conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],["3",fecha,hora],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                    conexion_bd.update_data(["bloqueado",],["True"],1,["usuario"],[usr],["and"])
                    bloqueado=True
                    conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                    conexion_bd.add_data([conexion_bd.generate_id(True,constantes.CLAVE_REPORTE),usr,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","bloqueo de usuario","",time_object.get_fecha()])
                    conexion_bd.set_tabla(constantes.TABLA_USUARIO)
                elif(bloq=="False" and num_intentos<3):
                    conexion_bd.set_tabla(constantes.TABLA_INTENTOS_USUARIO)
                    conexion_bd.update_data(["num_intentos","last_fecha","last_hora"],[str(num_intentos+1),fecha,hora],3,[constantes.CLAVE_INTENTOS_USUARIO],[res2[0][5]],["and"])
                    conexion_bd.set_tabla(constantes.TABLA_REPORTE)
                    conexion_bd.add_data([conexion_bd.generate_id(True,constantes.CLAVE_REPORTE),usr,time_object.get_fecha(),time_object.get_tiempo(),"gestion usuario","inicio de sesion fallido","",time_object.get_fecha()])
                    conexion_bd.set_tabla(constantes.TABLA_USUARIO)
        if(valido):
           #login valid
           return [0,self.permiso]
        else:
           #login invalid
           if(bloqueado==False):
              if(invalid_credentials!=-1):
                   if(invalid_credentials==0):
                       return [-1,None]
                   elif(invalid_credentials==1):
                        return [-2,None]
                   else:
                        return [-3,None]
              else:
                  return [-4,None]
           else:
                 return [-5,None]
    
    #Get the Credentials of User: Id, worker id, access level, icon , password
    def get_credentials(self):
         return [self.user,self.id_trabaj,self.permiso,self.icon,self.passwd]

    #Get the Historial of Actions of User  
    def get_historia(self):
         return self.historia.get_historia()
         
    #Method for Overrid return the Permit Matrix of User
    def get_permiso_matrix(self):
      #matriz de permisos del usuario coordinador
      return[[False,False,False,False],[False,False,False,False,False,False],[False,False,False,False],[False,False,False,False,False,False,False,False,False,False,False,False],[False,False,False,False,False,False,False,False],[False,False,False]]
    
    #add an Action to the Historial of User
    def add_action_historial(self,action_data):
       self.historia.add_action(action_data[0],action_data[1])
    
    #Verify data of Student in Inscription process   
    def validar_inscripcion(self,data):
       
          from General import General
          from conexion_bd import conexion_bd
          data_estud=["","","","","","","","","",data[3],"",""]
          data_repres=["","","","","","","","","","","","","",""]
          data_dir=["","","",""]
          valido=0
          old_exp=[]
          fields=data[0]
          for i in range(0,len(fields)):
              id_f=fields[i].get_id()
              valor=fields[i].get_text()
              if(id_f=="cedula_estud"):
                 conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                 d_e=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[valor],["and"])
                 if(d_e!=[]):
                     conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                     d_exp=conexion_bd.get_allData(["src_exp","src_foto"],2,[constantes.CLAVE_EXPEDIENTE],[d_e[0][0]],["and"])
                     old_exp=[d_exp[0][0],d_exp[0][1]]
              if(valido==0 and id_f!="cedula_estud"):
                  if(id_f=="nombre"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          valido=-1   
                      else:
                          fullname=valor.split(" ")
                          if(len(fullname)==1):
                             data_estud[0]=fullname[0].lower()
                          elif(len(fullname)==2):
                             data_estud[0]=fullname[0].lower()
                             data_estud[2]=fullname[1].lower()
                          else:
                             valido=-1      
                  elif(id_f=="apellido"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          valido=-2
                      else:
                          fullapell=valor.split(" ")
                          if(len(fullapell)==1):
                             data_estud[1]=fullapell[0].lower()
                          elif(len(fullapell)==2):
                             data_estud[1]=fullapell[0].lower()
                             data_estud[3]=fullapell[1].lower()
                          else:
                             valido=-2                   
                  elif(id_f=="destino_file"):
                      if(valor==""):
                          data_estud[7]="..."
                      else: 
                          #verificaraca expediente
                           if(valor.endswith(".rar") or valor.endswith(".zip")):
                             data_estud[7]=valor
                             ruta=valor.split("/")
                             filename=ruta[len(ruta)-1]
                             conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                             if(conexion_bd.id_exist("src_exp","expedientes/"+filename)==True): 
                                  if(old_exp==[]):
                                     valido=-15
                                  else:
                                    if((old_exp[0]==("expedientes/"+filename))==False):
                                          valido=-15
                           else:
                             valido=-13   
                  elif(id_f=="destino_foto"):
                      if(valor==""):
                          data_estud[10]="..."
                      else: 
                          #verificaraca expediente
                          if(valor.endswith(".jpg") or valor.endswith(".jpeg") or valor.endswith(".png")):
                             data_estud[10]=valor
                             ruta=valor.split("/")
                             filename=ruta[len(ruta)-1]
                             conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                             if(conexion_bd.id_exist("src_foto","fotos/"+filename)==True):
                                 
                                  if(old_exp==[]):
                                    valido=-14
                                  else:
                                    if((old_exp[1]==("fotos/"+filename))==False):
                                          valido=-14
                          else:
                             valido=-12
                  elif(id_f=="CIrepres"):
                      temp_v=valor
                      if(temp_v.startswith("v-") or temp_v.startswith("V-") or temp_v.startswith("e-") or temp_v.startswith("E-")):
                         temp_v=valor.split("-")[1]
                      if(General.is_valid(temp_v,constantes.CADENA_SOLONUMERO,False,6)==False):
                          valido=-4
                      else:
                         data_repres[0]=valor
                  elif(id_f=="telef"):
                      if(General.is_valid(valor,constantes.CADENA_TELEFONO,False)==False):
                          valido=-5
                      else:
                          data_repres[3]=valor 
                  elif(id_f=="nombre_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          valido=-6
                      else:
                          temp_nomb=valor.split(" ")
                          if(len(temp_nomb)==1):
                               data_repres[1]=temp_nomb[0].lower()
                          elif(len(temp_nomb)==2):
                              data_repres[1]=temp_nomb[0].lower()
                              data_repres[11]=temp_nomb[1].lower() 
                          else:
                             valido=-6
                  elif(id_f=="apellido_repres"):
                      if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True,3)==False):
                          valido=-7
                      else:
                          temp_apell=valor.split(" ")
                          if(len(temp_apell)==1):
                               data_repres[2]=temp_apell[0].lower()
                          elif(len(temp_apell)==2):
                              data_repres[2]=temp_apell[0].lower()
                              data_repres[12]=temp_apell[1].lower()
                          else:
                             valido=-7    
                  elif(id_f=="direccion"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           valido=-10
                       else:
                          data_d=valor.split(",")
                          for drt in range(0,len(data_d)):
                             temp_dire=""
                             for dr in range(0,len(data_d[drt])):
                               if(dr==0):
                                 if(data_d[drt][dr]!=" "):
                                    temp_dire=temp_dire+data_d[drt][dr]
                               elif(dr==len(data_d[drt])-1):
                                 if(data_d[drt][dr]!=" "):
                                    temp_dire=temp_dire+data_d[drt][dr]
                               else:
                                   temp_dire=temp_dire+data_d[drt][dr]
                             data_d[drt]=temp_dire.lower() 
                          id_d=""
                          conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                          res=conexion_bd.get_allData(constantes.CAMPOS_DIRECCION,len(constantes.CAMPOS_DIRECCION),["sector","parroquia","casa"],[data_d[0],data_d[1],data_d[2]],["and","and","and"])
                          if(res==[]):
                              id_d=conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION)
                              data_dir=[True,id_d,data_d[0],data_d[1],data_d[2]]
                          else:
                               id_d=res[0][0]
                               data_dir=[False,id_d,data_d[0],data_d[1],data_d[2]]
                  elif(id_f=="fecha"):
                       if(General.is_valid(valor,constantes.CADENA_FECHA,False)==False):
                           valido=-11
                       else:
                           data_estud[8]=valor
                  elif(id_f=="correo"):
                       if(General.is_valid(valor,constantes.CADENA_CORREO,False)==False):
                           valido=-16
                       else:
                           data_repres[4]=valor
                  elif(id_f=="dir_representante"):
                       if(General.is_valid(valor,constantes.CADENA_DIRECCION,True)==False):
                           valido=-17
                       else:
                           dir_r=valor.split(",")
                           
                           for t_dr in range(0,len(dir_r)):
                             temp_dire=""
                             for drre in range(0,len(dir_r[t_dr])):
                               if(drre==0):
                                 if(dir_r[t_dr][drre]!=" "):
                                    temp_dire=temp_dire+dir_r[t_dr][drre]
                               elif(drre==len(dir_r[t_dr])-1):
                                 if(dir_r[t_dr][drre]!=" "):
                                    temp_dire=temp_dire+dir_r[t_dr][drre]
                               else:
                                   temp_dire=temp_dire+dir_r[t_dr][drre]
                             dir_r[t_dr]=temp_dire.lower()
                             
                           conexion_bd.set_tabla(constantes.TABLA_DIRECCION)
                           temp_domicilio=conexion_bd.get_allData([constantes.CLAVE_DIRECCION,"sector","parroquia","casa"],4,["sector","parroquia","casa"],[dir_r[0],dir_r[1],dir_r[2]],["and","and","and"])
                           if(temp_domicilio!=[]):
                              data_repres[5] =True
                              data_repres[6]=temp_domicilio[0][0]
                              data_repres[7]=temp_domicilio[0][1]
                              data_repres[8]=temp_domicilio[0][2]
                              data_repres[9]=temp_domicilio[0][3]
                           else:  
                              data_repres[5] =False                           
                              data_repres[6]=conexion_bd.generate_id(True,constantes.CLAVE_DIRECCION)
                              data_repres[7]=dir_r[0]
                              data_repres[8]=dir_r[1]
                              data_repres[9]=dir_r[2]
                  elif(id_f=="parentesco"):
                           if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,False)==False):
                              valido=-18
                           else:
                              data_repres[10]=valor.lower()
                  elif(id_f=="plantel"):
                      if(General.is_valid(valor,constantes.CADENA_ALFANUMERICA,True,4)==False):
                         valido=-20
                      else:
                         data_estud[11]=valor      
                  elif(id_f=="oficio"):
                         if(General.is_valid(valor,constantes.CADENA_SOLOTEXTO,True)==False):
                              valido=-19
                         else:
                              data_repres[13]=valor.lower()               
          data_estud[6]=data[2]
          data_estud[4]=data[4]
          if(data[1]=="elejir" or data[1]=="elegir"):
             if(valido==0):
               valido=-9
          else:
             data_estud[5]=data[1]
          return [valido,data_estud,data_repres,data_dir]

    #Validate Cronogram
    def validar_cronograma(self,data):
    
        from tiempo import tiempo
        from General import General
        time_object=tiempo()
        
        if(len(data)<1):
           return -1
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        dat_cronog=conexion_bd.get_allData(None,None)
        init_cronog=""
        if(dat_cronog!=[]): 
            init_cronog=dat_cronog[0][1]
        for i in range(0,len(data)):
            inicio=data[i][0]
            cierre=data[i][1]
            strict=data[i][2]
            if(init_cronog!=""):
               if(time_object.is_previous(inicio,init_cronog)):
                       return -5
            if(General.is_valid(inicio,constantes.CADENA_FECHA,False)==False):
               return -2
            elif(General.is_valid(cierre,constantes.CADENA_FECHA,False)==False):
               return -3
            else:
              if(time_object.is_previous(inicio,cierre,strict)==False):
                  return -4 
        return True
        
    #Verify if the Year of Cronogram is Valid   
    def is_validYear(self,periodo,inicio,cierre):
        from General import General
        year=periodo.split("-")
        if(len(year)!=2):
           return -1
        elif(General.is_valid(year[0],constantes.CADENA_SOLONUMERO,False,3)==False):
           return -1
        elif(General.is_valid(year[1],constantes.CADENA_SOLONUMERO,False,3)==False):
           return -1
        else:
            if(len(year[0])!=4):
                 return -1
            elif(len(year[1])!=4):
                 return -1            
        if(General.is_valid(inicio,constantes.CADENA_FECHA,False)==False):
           return -2
        elif(General.is_valid(cierre,constantes.CADENA_FECHA,False)==False):
           return -2
        else:
           from tiempo import tiempo
           time_object=tiempo()
           temp_inicio=inicio.split("/")
           if(temp_inicio[1]!="09" and temp_inicio[1]!="9"):
                return -4
                
           if(time_object.is_previous(inicio,cierre)!=True):
              return -3
        return True
        
    #Organizate Sections A and B of Students   
    def organizar_secciones(self,data):
      
       from conexion_bd import conexion_bd
       conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
       #Organizate Section A
       for i in range(0,len(data[1])):
          id_estudent=data[1][i].split("-")
          if(len(id_estudent)==3):
             id_estudent=id_estudent[0]+"-"+id_estudent[1]
          elif(len(id_estudent)==2):
             id_estudent=id_estudent[0]
          else:
              id_estudent=""
          conexion_bd.update_data([constantes.CLAVE_SECCION],[data[0]],1,[constantes.CLAVE_ESTUDIANTE],[id_estudent],["and"])
       
       #Organizate Section B
       for j in range(0,len(data[4])):
          id_estudent=data[4][j].split("-")
          if(len(id_estudent)==3):
             id_estudent=id_estudent[0]+"-"+id_estudent[1]
          elif(len(id_estudent)==2):
             id_estudent=id_estudent[0]
          else:
              id_estudent=""
          conexion_bd.update_data([constantes.CLAVE_SECCION],[data[3]],1,[constantes.CLAVE_ESTUDIANTE],[id_estudent],["and"])
       
       conexion_bd.set_tabla(constantes.TABLA_PROFESOR)
       conexion_bd.update_data(["seccion_guia"],["default"],1,["seccion_guia"],[data[0]],["and"])
       id_prof=data[2].split("-")
       if(len(id_prof)==3):
          id_prof=id_prof[0]+"-"+id_prof[1]
       elif(len(id_prof)==2):
          id_prof=id_prof[0]
       else:
          id_prof=""
          
       conexion_bd.update_data(["seccion_guia"],[data[0]],1,[constantes.CLAVE_TRABAJADOR],[id_prof],["and"])
       conexion_bd.set_tabla(constantes.TABLA_SECCION)
       conexion_bd.update_data(["total_estud"],[str(len(data[1]))],1,[constantes.CLAVE_SECCION],[data[0]],["and"])
       conexion_bd.update_data(["total_estud"],[str(len(data[4]))],1,[constantes.CLAVE_SECCION],[data[3]],["and"])
        
#User with Access Level Coordinator       
class coordinador(usuario):
    #Build a User with Level of Access :Coordinator
    def __init__(self):
	    super().__init__()
    
    #Set Loggin data of User    
    def set_login(self,credentials):
       self.data_process=[]
       self.user=credentials[0] 
       self.id_trabaj=credentials[1]  
       self.permiso=credentials[2]  
       self.icon=credentials[3] 
       self.passwd=credentials[4]
       self.historia.set_user(self.user)
       
    #Return permit matrix of User   
    def get_permiso_matrix(self):
      return[[True,True,True,True],[True,False,True,True,False,True],[True,True,True,True],[True,True,True,True,True,True,True,True,True,True,False],[True,False,False,False,True,True,False,True],[True,True,True]]

#User with Access Level Admin
class admin(usuario):
    #Build a User with Level of Access :Admin
    def __init__(self):
        super().__init__()
    
    #Set Loggin data of User       
    def set_login(self,credentials):      
       self.data_process=[]
       self.user=credentials[0] 
       self.id_trabaj=credentials[1]  
       self.permiso=credentials[2]  
       self.icon=credentials[3]
       self.passwd=credentials[4]
       self.historia.set_user(self.user)
    
    #Return permit matrix of User    
    def get_permiso_matrix(self):
          return[[True,True,True,True],[True,True,True,True,True,True],[True,True,True,True],[True,True,True,True,True,True,True,True,True,True,True],[True,True,True,True,True,True,True,True],[True,True,True]]


#User with Access Level Directivo
class directivo(usuario):
    #Build a User with Level of Access :Directivo
    def __init__(self):
        super().__init__()
    
    #Set Loggin data of User       
    def set_login(self,credentials):
       self.data_process=[]
       self.user=credentials[0] 
       self.id_trabaj=credentials[1]  
       self.permiso=credentials[2]  
       self.icon=credentials[3] 
       self.passwd=credentials[4]
       self.historia.set_user(self.user) 
    
    #Return permit matrix of User        
    def get_permiso_matrix(self):
          return[[True,True,True,True],[True,True,True,False,True,False],[False,False,False,False],[True,True,True,True,True,True,True,True,True,True,False],[True,False,False,False,True,False,False,False],[True,True,True]]
    
#User with Access Level Secretaria  
class secretaria(usuario):
    #Build a User with Level of Access :Secretaria
    def __init__(self):
	    super().__init__()
    
    #Set Loggin data of User        
    def set_login(self,credentials):
       self.data_process=[]
       self.user=credentials[0] 
       self.id_trabaj=credentials[1]  
       self.permiso=credentials[2]  
       self.icon=credentials[3]
       self.passwd=credentials[4]
       self.historia.set_user(self.user)
    
    #Return permit matrix of User    
    def get_permiso_matrix(self):
      return[[True,True,True,True],[True,False,True,False,False,False],[True,True,False,True],[True,True,True,True,True,True,True,True,True,True,False],[True,False,False,False,True,False,False,False],[True,True,True]]

#Save the Actions data of a User
class historial:
    #Build the Historial
    def __init__(self,usr):
       self.user=usr
       self.data=[]
       self.dates=[]
    
    #Reset the Historial
    def reset(self):
       self.user=""
       self.data=[]
       self.dates=[]
    
    #Set the User Associated to the Historial 
    def set_user(self,usr):
       self.reset()
       self.user=usr
    
    #Return the Historial data    
    def get_historia(self):
       if(self.data!=[]):
         temp_hist=[]
         for i in range(len(self.data)-1,-1,-1):
            temp_hist.append([self.data[i],self.dates[i]])
         return temp_hist
       else:
          return []
    
    #Add an Action to the Historial    
    def add_action(self,action,date):
        self.data.append(action)
        self.dates.append(date)
       
             