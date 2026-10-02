from conexion_bd import conexion_bd
from constantes import *

#Base Class for Save User data 
class usuario:
    def __init__(self):
        self.user=""
        self.id_trabaj=""
        self.historia=historial("")
        self.icon=""
        self.permiso=""
        self.token=""
     
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
            return [False,None]
        foto_user=json_content["Foto_User"]
        nivel_acceso=json_content["Acces_User"]
        self.user=usr 
        self.id_trabaj=json_content["CI_trabaj"]
        self.permiso=nivel_acceso  
        self.icon=foto_user
        self.token=json_content["TokenSession"]
        return [True,self.permiso]        

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
       
             