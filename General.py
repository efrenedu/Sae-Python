import tkinter as tk
from tkinter import messagebox  
from tkinter import filedialog as fd 
from constantes import constantes
from tkinter import simpledialog

#class with support Methods
class General: 

  #Show a Input Message and return the Entry value
  @classmethod
  def show_input_message(cls,msg,title):
     root = tk.Tk()
     root.overrideredirect(1)
     root.withdraw()
     value=simpledialog.askstring(title,msg )
     root.destroy()   
     return value 
  
  #show a Input Password Dialog and Return the Entry Value
  @classmethod	   
  def show_password_message(cls,msg,title):
     root = tk.Tk()
     root.overrideredirect(1)
     root.withdraw()
     value=simpledialog.askstring(title,msg ,show='*')
     root.destroy()   
     return value
     
  #Show a Message Dialog 
  @classmethod	 
  def show_message(cls,msg,title):
     root = tk.Tk()
     root.overrideredirect(1)
     root.withdraw()
     messagebox.showinfo(message=msg, title=title)
     root.destroy()     

  #Encript a String Value
  @classmethod	 
  def encriptar(cls,value):
      encript=""
      abc="abcdefghijklmnñopqrstuvwxyz1234567890ABCDEFGHIJKLMNÑOPQRSTUVWXYZ%$_@&"
      desplaz=3
      for chr in value:
         if(chr in abc):
             index=abc.index(chr)+desplaz 
             if(index>=len(abc)):
                index=index-len(abc)
             encript=encript+abc[index]
         else:
            encript=encript+chr
      return encript
  
  #Desencript a String
  @classmethod	 
  def desencriptar(cls,valor):
      desencript=""
      abc="abcdefghijklmnñopqrstuvwxyz1234567890ABCDEFGHIJKLMNÑOPQRSTUVWXYZ%$_@&"
      desplaz=3
      for chr in valor:
         if(chr in abc):
             index=abc.index(chr)-desplaz 
             if(index<0):
                index=(len(abc)-1)+index
             desencript=desencript+abc[index]
         else:
            desencript=desencript+chr
      return desencript
   
  #Show a Error Message 
  @classmethod	 
  def show_error(cls,msg,title):
     root = tk.Tk()
     root.overrideredirect(1)
     root.withdraw()
     messagebox.showerror(message=msg, title=title)
     root.destroy()     

  #Show a Confirm Dialog 
  @classmethod	
  def show_confirmDialog(cls,msg,title):
     root = tk.Tk()
     root.overrideredirect(1)
     root.withdraw()
     res= messagebox.askyesno(message=msg, title=title)  
     root.destroy()
     return res
  
  #Return the File Source from a File Open Dialog  
  @classmethod	 
  def get_fileSource(cls):
     from event_manager import Event_manager
     vent=Event_manager.vent.raiz
     source=fd.askopenfilename(parent=vent,initialdir=constantes.RUTA_BASE,title="Seleccionar Archivos")
     return source
   
  #Return true if the Character is a Number Using ASCII Code Verification
  @classmethod	 
  def is_number(cls,caracter):
     value=ord(caracter)
     if(value>=48 and value<=57):
         return True
     return False
  
  #Verify if the Character is a Special Character using ASCII Code  
  @classmethod	
  def is_especial(cls,caracter):
      value=ord(caracter)
      if(value==33 ):
          return True
      elif(value>=35 and value<=38):
         return True
      elif(value>=63 and value<=64):
         return True
      elif(value==95):
         return True
      return False
  
  #Verify if the Character is Lower using ASCII Code Verification
  @classmethod	 
  def is_minuscula(cls,caracter):
      if(caracter==" "):
         return True
      value=ord(caracter)
      if(value>=97 and value<=122):
         return True
      return False
      
  #Verify if the Character is Upper using ASCII Code Verification
  @classmethod	   
  def is_mayuscula(cls,caracter):
      if(caracter==" "):
         return True
      value=ord(caracter)
      if(value>=65 and value<=90):
          return True
      return False
  
  #Return True if the String End in Empty Character
  @classmethod	
  def end_inBlanck(cls,str_val):
      index=len(str_val)-1
      if(str_val[index]==' '):
          return True
      return False
  
  #Return True if The String is Valid Entry
  @classmethod	 
  def is_valid(cls,str_val,valid_type,have_blank_spaces,min_caracters=0):
      res=True
      mixto=[False,False,False,False]      #only for password Entry
      num_separators=0
      if(len(str_val)<=min_caracters):
         return False
      if(have_blank_spaces==False):
          for i in range(0,len(str_val)):
              chr=str_val[i]
              if(chr==" "):
                  return False
      str_val_telef=str_val
      if(valid_type==constantes.CADENA_TELEFONO ):
          if(str_val_telef.startswith("0")==False):
              return False          
          if(str_val_telef.find("-")!=-1):
              str_val_telef=str_val_telef.replace("-","")
          if(len(str_val_telef)==11):
              if(str_val_telef.isdigit()):
                  return True
          return False
      if(valid_type==constantes.CADENA_CORREO):
          res=False
          if(str_val.endswith("@gmail.com")):
              if(len(str_val)>=14):
                res=True
          elif(str_val.endswith("@hotmail.com")):
               if(len(str_val)>=15):
                 res=True
          elif(str_val.endswith("@yahoo.com")):
               if(len(str_val)>=14):
                   res=True
          if(str_val.startswith("@")):
             res=False
          elif(str_val.startswith(" ")):
             res=False
          return res   
      if(valid_type==constantes.CADENA_FECHA):
          res=False
          str_vals=str_val.split("/")
          if((len(str_vals)==3)==False):
             return False
          for i in range(0,3):
             cad=str_vals[i]
             if(cad==" " or cad==""):
                 return False
             for j in range(len(cad)):
                 chr=cad[j]
                 if(cls.is_number(chr)==False):
                     return False
             if(i==1):
                if((int(cad)>=1 and int(cad)<=12)==False):
                    return False
             elif(i==0):
                 if((int(cad)>=1 and int(cad)<=31)==False):
                    return False
          return True     
      if(valid_type==constantes.CADENA_DIRECCION ):
          res=False
          str_vals=str_val.split(",")
          if((len(str_vals)==3)==False):
             return False
          for i in range(0,3):
             cad=str_vals[i]
             if(cad==" " or cad==""):
                 return False
             for j in range(len(cad)):
                 chr=cad[j]
                 if(cls.is_especial(chr)):
                     return False
          return True   
      if(valid_type==constantes.CADENA_PASSWORD and len(str_val)<8):
          return False  
      if(valid_type==constantes.CADENA_USER):
          return True
      if(valid_type==constantes.CADENA_YEAR):
         if(len(str_val)!=4):
             return False
         for i in range(0,len(str_val)):
            chr=str_val[i]
            if(cls.is_number(chr)==False):
              return False    
         return True
      
      for i in range(0,len(str_val)):
          chr=str_val[i]
          if(valid_type==constantes.CADENA_SOLOTEXTO):
             if(cls.is_mayuscula(chr)==False and cls.is_minuscula(chr)==False):
                  return False    
          if(valid_type==constantes.CADENA_SOLONUMERO):
             if(cls.is_number(chr)==False):
                 return False
          if(valid_type==constantes.CADENA_CALIFICACION):
              if(chr!='.'):
                  if(cls.is_number(chr)==False):
                       return False                
          if(valid_type==constantes.CADENA_ALFANUMERICA):
              if(cls.is_number(chr)==False and cls.is_minuscula(chr)==False and cls.is_mayuscula(chr)==False):
                    return False      
          if(valid_type==constantes.CADENA_AÑO_ESCOLAR):
              if(cls.is_number(chr)==False and cls.is_minuscula(chr)==False and cls.is_mayuscula(chr)==False and chr!='-'):
                    return False                   
          if(valid_type==constantes.CADENA_PASSWORD ):
              if(cls.is_number(chr) ):
                  if(mixto[0]==False):
                      mixto[0]=True
              else:
                  if(cls.is_especial(chr) ):
                      if(mixto[1]==False):
                          mixto[1]=True
                  else:
                      if(cls.is_mayuscula(chr)):
                          if(mixto[2]==False):
                              mixto[2]=True
                      if(cls.is_minuscula(chr)):
                          if(mixto[3]==False):
                              mixto[3]=True 
      if(valid_type==constantes.CADENA_PASSWORD):
          if(mixto[0]==True and mixto[1]==True and mixto[2]==True and mixto[3]==True):
              return True
          return False
      return res