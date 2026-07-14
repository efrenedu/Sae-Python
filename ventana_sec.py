import customtkinter as ctk
from tkinter import *   
import tkinter as tk
from tkinter import ttk 
from constantes import *
import os
import sys
from PIL import Image,ImageDraw, ImageFont, ImageTk
from tkinter.font import Font 
from componentes import Lienzo_dibujo,Labl,TextField,Boton,componente 

#For Secondary Windows: Show Stadistics, Manage the Expedent Files
class ventana_secundaria:
    #Build the Secondary Windows
    def __init__(self,parent,dim,colors,active,have_canvas,dim_canvas,colores_button=["white","black","blue","white"],font_name="Arial",font_size=15,data=None):
         self.dim=dim
         self.background=colors[0]
         self.raiz=tk.Toplevel() 
         self.raiz.configure(bg=colors[0])
         self.colors_buttons=colores_button
         self.active=active
         self.parent=parent
         self.raiz.title("second")
         self.comps=[]
         self.requireds={}
         wtotal = self.raiz.winfo_screenwidth()
         htotal = self.raiz.winfo_screenheight()
         pwidth = round(wtotal/2-dim[0]/2)
         pheight = round(htotal/2-dim[1]/2)
         self.raiz.geometry(str(dim[0])+"x"+str(dim[1])+"+"+str(pwidth)+"+"+str(pheight))
         self.canvas=None
         self.assign_components(have_canvas,dim_canvas,colors,data,font_name,font_size,colores_button)
        
    #Build the Required Components of Secondary Windows
    def assign_components(self,have_canvas,dim_canvas,colors,data,font_name,font_size,colores_button):
         if(have_canvas):
             self.canvas=Lienzo_dibujo(self.raiz,colors[1],dim_canvas,"canvas","canvas")
             self.canvas.set_active(self.active)
         if(data!=None):
             self.add_data=data
             self.frame=ctk.CTkFrame(self.raiz,fg_color="white") 
             self.frame.pack(side=TOP)
             font=ctk.CTkFont(family="Arial", size=15,weight="normal") 
             font_t=ctk.CTkFont(family="Arial", size=15, weight="bold") 
             self.comps.append(Labl({"column":1,"row":0,"padx":5,"pady":5,"sticky":"ew"},self.frame,"ASIGNAR EXPEDIENTE",font_t,{"Fg":"white","Text":"black"},"Titulo","label",True,None))
             self.comps.append(Labl({"column":1,"row":1,"padx":5,"pady":5,"sticky":"ew"},self.frame,"campos con * son obligatorios",font,{"Fg":"white","Text":"black"},"Titulo2","label",True,None))
             if(data["Is_Student"]==True):
                #for student Expedent Windows
               
                self.comps.append(Labl({"column":0,"row":2,"padx":5,"pady":5,"sticky":"ew"},self.frame,"fotocopia de la cedula*",font,{"Fg":"white","Text":"black"},"label_1","label",True,None))
                self.comps.append(Labl({"column":0,"row":3,"padx":5,"pady":5,"sticky":"ew"},self.frame,"copia de la partida \n de nacimiento*",font,{"Fg":"white","Text":"black"},"label_2","label",True,None))
                self.comps.append(Labl({"column":0,"row":4,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Documento de Aprobacion \n de sexto grado*",font,{"Fg":"white","Text":"black"},"label_3","label",True,None))
                self.comps.append(Labl({"column":0,"row":5,"padx":5,"pady":5,"sticky":"ew"},self.frame,"calificaciones certificadas\n de Años cursados",font,{"Fg":"white","Text":"black"},"label_4","label",True,None))
                self.comps.append(Labl({"column":0,"row":6,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Carta de Residencia*",font,{"Fg":"white","Text":"black"},"label_5","label",True,None))
                self.comps.append(Labl({"column":0,"row":7,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Tarjeta de Vacunacion",font,{"Fg":"white","Text":"black"},"label_6","label",True,None))
                self.comps.append(Labl({"column":0,"row":8,"padx":5,"pady":5,"sticky":"ew"},self.frame,"fotocopia de la cedula\n del representante",font,{"Fg":"white","Text":"black"},"label_7","label",True,None))
                self.comps.append(Labl({"column":0,"row":9,"padx":5,"pady":5,"sticky":"ew"},self.frame,"foto del representante",font,{"Fg":"white","Text":"black"},"label_8","label",True,None))
                self.comps.append(TextField({"column":1,"row":2,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_1","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":3,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_2","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":4,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_3","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":5,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_4","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":6,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_5","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":7,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_6","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":8,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_7","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":9,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_8","text",True,3,"",8))
                 
                self.requireds["exp_1"]=True
                self.requireds["exp_2"]=True
                if(data["Nuevo_Ingreso"]==constantes.NUEVO_INGRESO_FIRST_YEAR):
                    self.requireds["exp_3"]=True
                    self.requireds["exp_4"]=False
                elif(data["Nuevo_Ingreso"]==constantes.NUEVO_INGRESO_NO_FIRST_YEAR):
                    self.requireds["exp_3"]=False
                    self.requireds["exp_4"]=True
                elif(data["Nuevo_Ingreso"]==constantes.NUEVO_INGRESO_UPDATE):
                    self.requireds["exp_3"]=False
                    self.requireds["exp_4"]=False
                self.requireds["exp_5"]=True
                self.requireds["exp_6"]=False
                self.requireds["exp_7"]=False
                self.requireds["exp_8"]=False
        
                self.comps.append(Boton({"column":2,"row":2,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton1","button",True,8))
                self.comps.append(Boton({"column":2,"row":3,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton2","button",True,8))
                self.comps.append(Boton({"column":2,"row":4,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton3","button",True,8))
                self.comps.append(Boton({"column":2,"row":5,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton4","button",True,8))
                self.comps.append(Boton({"column":2,"row":6,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton5","button",True,8))
                self.comps.append(Boton({"column":2,"row":7,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton6","button",True,8))
                self.comps.append(Boton({"column":2,"row":8,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton7","button",True,8))
                self.comps.append(Boton({"column":2,"row":9,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton8","button",True,8))
             else: 
                #for worker expedent windows
                self.comps.append(Labl({"column":0,"row":3,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Fondo Blanco del Titulo*",font,{"Fg":"white","Text":"black"},"label_2","label",True,None))
                self.comps.append(Labl({"column":0,"row":4,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Cuenta Bancaria*",font,{"Fg":"white","Text":"black"},"label_3","label",True,None))
                self.comps.append(Labl({"column":0,"row":5,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Fotocopia de la Cedula*",font,{"Fg":"white","Text":"black"},"label_4","label",True,None))
                self.comps.append(Labl({"column":0,"row":6,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Sintesis Curricular*",font,{"Fg":"white","Text":"black"},"label_5","label",True,None))
                self.comps.append(Labl({"column":0,"row":7,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Ultimo Boucher",font,{"Fg":"white","Text":"black"},"label_6","label",True,None))
                self.comps.append(Labl({"column":0,"row":8,"padx":5,"pady":5,"sticky":"ew"},self.frame,"Credenciales*",font,{"Fg":"white","Text":"black"},"label_6","label",True,None))
                self.comps.append(TextField({"column":1,"row":3,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_2","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":4,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_3","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":5,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_4","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":6,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_5","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":7,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_6","text",True,3,"",8))
                self.comps.append(TextField({"column":1,"row":8,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Text":"black","Fg":"white","Placeholder_Text":"gray"},"exp_7","text",True,3,"",8))
                
                self.requireds["exp_2"]=True
                self.requireds["exp_3"]=True
                self.requireds["exp_4"]=True
                self.requireds["exp_5"]=True
                self.requireds["exp_6"]=False
                self.requireds["exp_7"]=True
                self.comps.append(Boton({"column":2,"row":3,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton2","button",True,8))
                self.comps.append(Boton({"column":2,"row":4,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton3","button",True,8))
                self.comps.append(Boton({"column":2,"row":5,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton4","button",True,8))
                self.comps.append(Boton({"column":2,"row":6,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton5","button",True,8))
                self.comps.append(Boton({"column":2,"row":7,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton6","button",True,8))
                self.comps.append(Boton({"column":2,"row":8,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"boton7","button",True,8))
             self.comps.append(Labl({"column":0,"row":10,"padx":5,"pady":5,"sticky":"ew"},self.frame,"foto",font,{"Fg":"white","Text":"black"},"label_f","label",True,None))
             self.comps.append(TextField({"column":1,"row":10,"padx":5,"pady":5,"sticky":"ew"},self.frame,font,{"Fg":"white","Text":"black","Placeholder_Text":"gray"},"exp_f","text",True,3,"",8))
             self.requireds["exp_f"]=False
             self.comps.append(Boton({"column":2,"row":10,"padx":15,"pady":5,"sticky":"ew"},self.frame, "abrir",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"botonf","button",True,8))
             self.comps.append(Boton({"column":1,"row":11,"padx":15,"pady":5,"sticky":"ew"},self.frame, "finalizar",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"finalizar","button",True,8))
             self.comps.append(Boton({"column":0,"row":12,"padx":5,"pady":15,"sticky":"ew"},self.frame, "  cerrar  ",font,{"Fg":"white","Text":"black","Hover":"red","Text_Hover":"yellow","Hover_Action":"green","Text_Hover_Action":"white"},None,0,(),"cerrar","button",True,8))
             from event_manager import Event_manager
             for j in range(0,len(self.comps)):
                  self.comps[j].set_active(True)
                  tag=self.comps[j].get_tag()
                  if(tag=="button"):
                       self.add_event(self.comps[j])
                  elif(tag=="text"):
                       self.comps[j].On_load()
             try:         
                  self.asignar_old_files_expediente()
             except:
                  General.show_error("fallo al leer el expediente de la bd , por favor intentelo de nuevo","error de lectura")
                  self.destroy_sec(True)
         else:
              font=ctk.CTkFont(family=font_name, size=font_size,weight="normal") 
              self.cerrar=ctk.CTkButton(self.raiz,text="cerrar",bg_color=colores_button[0],font=font,fg_color=colores_button[1],hover_color=colores_button[3],cursor='hand2',corner_radius=8)       
              self.cerrar.pack(side=BOTTOM)
              self.cerrar.configure(command=self.destroy_sec)
    
    #Draw a Text in the Canvas
    def draw_text(self, pos,fuente_name,style_font,size_f,text_color,texto):
        if(self.canvas!=None):
          self.canvas.draw_text( pos,fuente_name,style_font,size_f,text_color,texto)   
         
    #Add a Event to a Button 
    def add_event(self,comp):
         if(comp.get_id().startswith("boton")):
               comp.boton.configure(command=lambda:self.open_file(comp.get_id()))
         else:
            if(comp.get_id()=="finalizar"):
                 comp.boton.configure(command=lambda:self.asignar_expediente())
            elif(comp.get_id()=="cerrar"):
                comp.boton.configure(command=lambda:self.destroy_sec(True))
    
    #Load the Zip File of Existent Expedent of a Student or Worker and show them as filesource On TextFields
    def asignar_old_files_expediente(self):
        from conexion_bd import conexion_bd
        import requests
        if sys.version_info >= (3, 7):
               import zipfile
        else:
              import zipfile37 as zipfile   
        url_zip=""
        if(self.add_data["Is_Student"]==True):
              conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
              data_estud=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[self.add_data["cedula"]],["and"])
              if(data_estud!=[]):
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                data_exp=conexion_bd.get_allData(["src_exp"],1,[constantes.CLAVE_EXPEDIENTE],[data_estud[0][0]],["and"])
                if(data_exp!=[]):
                    url_zip=constantes.SERVER+data_exp[0][0]         
        else:
               conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
               data_trabaj=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_TRABAJADOR],[self.add_data["cedula"]],["and"])
               if(data_trabaj!=[]):
                  conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                  data_exp=conexion_bd.get_allData(["src_exp"],1,[constantes.CLAVE_EXPEDIENTE],[data_trabaj[0][0]],["and"])
                  if(data_exp!=[]):
                    url_zip=constantes.SERVER+data_exp[0][0]
        if(url_zip=="" or url_zip.endswith(".zip")==False):
            return
        response=requests.get(url_zip)
        if(response.status_code>400):
           return
        raw_data=response.content
        direccion=constantes.FOLDER_DOCUMENTS+self.add_data["cedula"]+".zip"
        file_val=open(direccion,"wb")
        file_val.write(raw_data)
        file_val.close()
        dir_extraccion=constantes.FOLDER_ZIP
        Zip= zipfile.ZipFile(direccion, 'r')
        Zip.extractall(dir_extraccion)
        Zip.close()
        file_info=open(dir_extraccion+"info.txt","r")
        files_list=["","","","","","","","",""]
        files_ids=["","","","","","","","",""]
        for linea in file_info:
            linea_split=linea.split(":")
            if(self.add_data["Panel_Id"]==constantes.PANTALLA_REGISTRO_PERSONAL):
               #worker expedent
               if(linea.startswith("Fondo Negro")):
                     files_list[0]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[0]="exp_1"
               elif(linea.startswith("Fondo Blanco")):
                     files_list[1]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[1]="exp_2"            
               elif(linea.startswith("Cuenta Bancaria")):
                     files_list[2]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[2]="exp_3"  
               elif(linea.startswith("fotocopia de la cedula")):
                     files_list[3]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[3]="exp_4"   
               elif(linea.startswith("Hoja de Vida")):
                     files_list[4]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[4]="exp_5"
               elif(linea.startswith("Ultimo Baucher")):
                     files_list[5]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[5]="exp_6" 
               elif(linea.startswith("Credenciales")):
                     files_list[6]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[6]="exp_7"       
               elif(linea.startswith("foto")):
                     files_list[7]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[7]="exp_f"       
            else:
                #Student Expedent
                if(linea.startswith("fotocopia de la cedula")):
                     files_list[0]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[0]="exp_1"
                elif(linea.startswith("copia de la partida de nacimiento")):
                    files_list[1]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[1]="exp_2" 
                elif(linea.startswith("Documento de Aprobacion de sexto grado")):
                    files_list[2]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[2]="exp_3"
                elif(linea.startswith("calificaciones certificadas de Años cursados")):
                    files_list[3]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[3]="exp_4" 
                elif(linea.startswith("Carta de Residencia")):
                    files_list[4]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[4]="exp_5"
                elif(linea.startswith("Tarjeta de Vacunacion")):
                    files_list[5]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[5]="exp_6"
                elif(linea.startswith("fotocopia de la cedula del representante")):
                    files_list[6]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                    files_ids[6]="exp_7"
                elif(linea.startswith("foto del representante")):
                     files_list[7]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[7]="exp_8"
                elif(linea.startswith("foto")):
                     files_list[8]=constantes.FOLDER_ZIP+linea_split[1].split("\n")[0]
                     files_ids[8]="exp_f"
        file_info.close()
        from event_manager import Event_manager
        data_old=[]
        for i in range(0,len(files_list)):
            if(files_list[i]!=""):
                 data_old.append([files_ids[i],files_list[i]])            
        for dat in data_old:
            for j in range(0,len(self.comps)):
                if(self.comps[j].get_id()==dat[0]):
                      self.comps[j].set_text(dat[1])

    #Assign or Update the Expedent of a Student or Worker and Write Them as Zip File
    def asignar_expediente(self):
         from General import General
         from conexion_bd import conexion_bd
         num_files=0
         files_paths=[None,None,None,None,None,None,None,None,None]
         foto=""
         files_expe=[False,False,False,False,False,False,False,False,False]
         target_comps=[]
         for comp in self.comps:
            if(comp.get_tag()=="text"):
               if(comp.get_text()!=""):
                   target_comps.append(comp)
               else:
                  if(comp.get_id() in self.requireds):
                    #Verify if the Field is Required
                    if(self.requireds[comp.get_id()]==True):
                        General.show_message("faltan documentos del expediente","documentos insuficinetes")
                        self.raiz.focus_force()
                        return 
                  if(comp.get_id().endswith("f")):
                     #Assign foto from  Expedent Data Base if Exist
                     dat_temp=[]
                     if(self.add_data["Panel_Id"]!=constantes.PANTALLA_REGISTRO_PERSONAL):
                        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                        dat_temp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[self.add_data["cedula"]],["and"])
                     else:
                        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                        dat_temp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_TRABAJADOR],[self.add_data["cedula"]],["and"])
                     if(dat_temp!=[]):
                        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                        dat_expedent=conexion_bd.get_allData(["src_foto"],1,[constantes.CLAVE_EXPEDIENTE],[dat_temp[0][0]],["and"])
                        if(dat_expedent!=[]):
                           val_fot=dat_expedent[0][0]
                           if(val_fot.startswith("fotos/")):
                               foto=val_fot                  
                   
         for i in range(0,len(target_comps)):
            num_files=num_files+1
            if(target_comps[i].get_id().endswith("f")):
                #foto textfield
                if(foto==""):
                    foto=target_comps[i].get_text()
                if(foto.endswith(".png")==False and foto.endswith(".jpg")==False and foto.endswith(".jpeg")==False):
                    #Invalid foto format
                    General.show_message("por favor seleccione una foto valida","foto invalida")
                    self.raiz.focus_force()
                    return 
                dat_temp=[]
                if(self.add_data["Panel_Id"]!=constantes.PANTALLA_REGISTRO_PERSONAL):
                    conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                    dat_temp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_ESTUDIANTE],[self.add_data["cedula"]],["and"])
                else:  
                    conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                    dat_temp=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE],1,[constantes.CLAVE_TRABAJADOR],[self.add_data["cedula"]],["and"])
                if(dat_temp!=[] and foto.startswith("C:/")):
                    #update foto in expedent 
                    conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                    data_exps=conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE,"src_foto"],2,)
                    for dat_expedent in data_exps:
                        if(dat_expedent[0]!=dat_temp[0][0] and( dat_expedent[1]!="" and dat_expedent[1]!="...")==True ):
                            src_temp=dat_expedent[1].split("/")[1]
                            src_fot=foto.split("/")
                            src_fot=src_fot[len(src_fot)-1]
                            if(src_fot==src_temp):
                                General.show_message("la foto ya existe en el servidor,por favor suba una foto con otro nombre","imagen ya existe en server")
                                self.raiz.focus_force()
                                return
                else:
                    #Assign Foto in Expedent for new worker o inscripcion nuevo ingreso
                    if(foto.startswith("C:/")):
                        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                        data_expe=conexion_bd.get_allData(["src_foto"],1)
                        if(data_expe!=[]):
                            source1=foto.split("/")
                            source1=source1[len(source1)-1]
                            for dat_expedent in data_expe:
                                source2=dat_expedent[0].split("/")  
                                source2=source2[len(source2)-1] 
                                if(source1==source2):
                                    General.show_message("la foto ya existe en el servidor,por favor suba una foto con otro nombre","imagen ya existe en server")
                                    self.raiz.focus_force()
                                    return                                           
                                                          
            else:
                valor=target_comps[i].get_text()
                if(valor.endswith(".pdf")==False and valor.endswith(".doc")==False and valor.endswith(".docx")==False and valor.endswith(".xlsx")==False and valor.endswith(".png")==False and valor.endswith(".jpg")==False and valor.endswith(".jpeg")==False):
                    #Invalid format for document
                    General.show_message("por favor seleccione una documento o imagen escaneada del documento valida","documento invalido")
                    self.raiz.focus_force()
                    return 
            valor=target_comps[i].get_id()
            if(self.add_data["Panel_Id"]==constantes.PANTALLA_REGISTRO_PERSONAL):
               #Worker Expedent
               if(valor=="exp_1"):
                 files_paths[1]=target_comps[i].get_text()
               elif(valor=="exp_2"):
                 files_paths[2]=target_comps[i].get_text()
               elif(valor=="exp_3"):
                 files_paths[3]=target_comps[i].get_text()
               elif(valor=="exp_4"):
                 files_paths[0]=target_comps[i].get_text()
               elif(valor=="exp_5"):
                 files_paths[4]=target_comps[i].get_text()
               elif(valor=="exp_6"):
                 files_paths[5]=target_comps[i].get_text()
               elif(valor=="exp_7"):
                 files_paths[6]=target_comps[i].get_text()
               elif(valor=="exp_f"):
                 files_paths[7]=target_comps[i].get_text()                           
            else:
               #Student Expedent
               if(valor=="exp_1"):
                  files_expe[3]="copia de Cedula de Identidad"
                  files_paths[0]=target_comps[i].get_text()
               elif(valor=="exp_2"):
                  files_expe[0]="Copia de Partida de Nacimiento Original"
                  files_expe[2]="partida de nacimiento Original"
                  files_paths[1]=target_comps[i].get_text()
               elif(valor=="exp_3"):
                  files_expe[5]="Boleta del periodos escolar anterior de ser neceario"
                  files_paths[2]=target_comps[i].get_text()
               elif(valor=="exp_4"):
                  files_expe[4]="Notas Cerificadas"
                  files_paths[3]=target_comps[i].get_text()
               elif(valor=="exp_5"):
                  files_expe[8]="Carta de Residencia"
                  files_paths[4]=target_comps[i].get_text()
               elif(valor=="exp_6"):
                  files_paths[5]=target_comps[i].get_text()
               elif(valor=="exp_7"):
                  files_expe[7]="Copia de Cedula" 
                  files_paths[6]=target_comps[i].get_text()
               elif(valor=="exp_8"):
                  files_expe[6]="2 Fotos" 
                  files_paths[7]=target_comps[i].get_text()
               elif(valor=="exp_f"):
                  files_expe[1]="2 fotos del estudiante"
                  files_paths[8]=target_comps[i].get_text()                           
                   
         for j in range(0,len(files_paths)):
            if(files_paths[j]!=None):
               for k in range(0,len(files_paths)):
                  if(j!=k and files_paths[k]!=None):
                      if(files_paths[j]==files_paths[k]):
                         #Files Repeateds
                         General.show_message("existen archivos repetidos en el expediente","archivos repetidos")
                         self.raiz.focus_force()
                         return

         if(General.show_confirmDialog("construir expediente con estos archivos?","asignar expediente")!=True):
              self.raiz.focus_force()
              return  
              
         #Send Expedent Data to Data Base
         from event_manager import Event_manager
         Event_manager.asign_expediente([self.add_data["cedula"],num_files,files_paths,foto,files_expe])
         self.destroy_sec() 
                 
    #open a File and set the path in the required component
    def open_file(self,source):
        from General import General
        res=General.get_fileSource()
        self.raiz.focus_force()
        destino=None
        for i in range(0,len(self.comps)):
            tag=self.comps[i].get_tag()
            if(tag=="text"):
               if(self.comps[i].get_id().endswith(source[len(source)-1])):
                  destino=self.comps[i]
                  break
        if(destino!=None):
            if(destino.get_tag()=="text"):
                destino.set_text(res)
     
    #Destroy the Secondary Window     
    def destroy_sec(self,delete_zips=False):
        self.parent.secundaria=None
        self.raiz.destroy()
        if(delete_zips==True):
           import threading
           from event_manager import Event_manager
           thread=threading.Thread(target=Event_manager.reset_zip_files)
           thread.start()
    
    #Clear the Canvas of Secondary Window
    def clear_canvas(self):
        if(self.canvas!=None):
           self.canvas.reset()
    
    #draw a Cake Diagram for stadistics Windows
    def draw_torta(self,valores,title,labels,colors,label_casos="total de casos"):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure 
        labels_torta=[]
        valores_torta=[]
        colors_torta=[]
        total=0
        for i in range(0,len(valores)):
            if(int(valores[i])>0):
                labels_torta.append(labels[i])
                valores_torta.append(valores[i])
                colors_torta.append(colors[i])
                total=total+int(valores[i])    
        self.canvas.canvas.pack_forget()
        self.canvas=None
        #canvas for the Figure
        frameChartsLT = tk.Frame(self.raiz)
        frameChartsLT.pack()
        #figure
        fig = Figure() 
        ax = fig.add_subplot(111) # add an Axes to the figure
        #diagram
        ax.pie(valores_torta, labels = labels_torta, colors = colors_torta, autopct='%.0f%%')
        ax.set_title(title)
        ax.text(1,-1,label_casos+":"+str(total))
        #incrust the diagrama on the canvas
        chart1 = FigureCanvasTkAgg(fig,frameChartsLT)
        chart1.get_tk_widget().pack()
               
#Splash Window to show when the System is Loading, is Automatic Destroyed when Finish the Time Limit 
class ventana_splash:
    #Build the Splash Window
    def __init__(self,ventana_p,dim,colores,font,time_limit):
        self.ventana_p=ventana_p
        self.ventana_p.raiz.withdraw()
        self.raiz=tk.Toplevel() 
        wtotal = self.raiz.winfo_screenwidth()
        htotal = self.raiz.winfo_screenheight()
        pwidth = round(wtotal/2-dim[0]/2)
        pheight = round(htotal/2-dim[1]/2)
        self.raiz.geometry(str(dim[0])+"x"+str(dim[1])+"+"+str(pwidth)+"+"+str(pheight))
        self.porcent=0
        self.raiz.configure(bg=colores[0])
        self.msg="cargando"
        self.canvas=Lienzo_dibujo(self.raiz,colores[0],dim,"canvas","canvas")
        self.canvas.set_active(True)
        self.pos_text=(dim[0]/2,dim[1]/2)
        self.pos_line1=((dim[0]/2)-100,(dim[1]/2)+50)
        self.pos_line2=((dim[0]/2)+100,(dim[1]/2)+50)
        self.font=font
        self.colores=colores
        self.canvas.draw_text( [self.pos_text[0]-10,self.pos_text[1]+100],"Arial","normal",14,self.colores[1],"0% / 100%")   
        self.canvas.draw_text( self.pos_text,self.font[0],self.font[1],self.font[2],self.colores[1],self.msg)   
        self.canvas.draw_line(self.pos_line1,self.pos_line2,1,self.colores[1])
        self.raiz.overrideredirect(True)
        self.redraw()        
        
    #Change the Porcent of Load 
    def set_porcentaje(self,valor):
        self.porcent=valor
        self.redraw()
    
    #Redraw the Canvas of Splash
    def redraw(self):
        self.canvas.reset() 
        self.canvas.draw_text( [self.pos_text[0]-10,self.pos_text[1]+100],"Arial","normal",14,self.colores[1],str(self.porcent)+"% / 100%")   
        self.canvas.draw_text( self.pos_text,self.font[0],self.font[1],self.font[2],self.colores[1],self.msg)   
        self.canvas.draw_line(self.pos_line1,self.pos_line2,1,self.colores[1])
        self.raiz.update()

    #Destroy the Splash Window
    def destroy_splash(self):
        self.raiz.destroy()
        