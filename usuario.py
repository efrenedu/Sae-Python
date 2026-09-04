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
        self.token=""
        
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
        import time
        import requests
        import json
        url_login=f"{constantes.SERVER}login.php"
        timestamp=str(int(time.time()))
        data_send={"password":passw,"timestamp":timestamp,"user_client":usr}
        response=requests.post(url_login,data=data_send)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return [-1,None]
        foto_user=json_content["Foto_User"]
        nivel_acceso=json_content["Acces_User"]
        self.user=usr 
        self.id_trabaj=json_content["CI_trabaj"]
        self.permiso=nivel_acceso  
        self.icon=foto_user
        self.token=json_content["TokenSession"]
        return [0,self.permiso]        

    #Get the Credentials of User: Id, worker id, access level, icon , password
    def get_credentials(self):
         return [self.user,self.id_trabaj,self.permiso,self.icon,self.token]

    #Get the Historial of Actions of User  
    def get_historia(self):
         return self.historia.get_historia()
         
    #Method for Overrid return the Permit Matrix of User for the Menus
    def get_permiso_matrix(self):
      return[[False,False,False,False],[False,False,False,False,False,False],[False,False,False,False],[False,False,False,False,False,False,False,False,False,False,False,False],[False,False,False,False,False,False,False,False],[False,False,False]]
    
    #add an Action to the Historial of User
    def add_action_historial(self,action_data):
       self.historia.add_action(action_data[0],action_data[1])
    
    
    #Validate Cronogram
    def validar_cronograma(self,data):
    
        from tiempo import tiempo
        from General import General
        time_object=tiempo()
        
        if(len(data)<1):
           return -1
        conexion_bd.set_tabla(constantes.TABLA_CRONOGRAMA)
        dat_cronog=conexion_bd.get_allData([])
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
       self.token=credentials[4]
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
       self.token=credentials[4]
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
       self.token=credentials[4]
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
       self.token=credentials[4]
       self.historia.set_user(self.user)
    
    #Return permit matrix of User    
    def get_permiso_matrix(self):
      return[[True,True,True,True],[True,False,True,False,False,False],[True,True,False,False],[True,True,True,True,True,True,True,True,True,True,False],[True,False,False,False,True,False,False,False],[True,True,True]]

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
       
             