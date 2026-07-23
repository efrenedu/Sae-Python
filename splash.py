from tkinter import *
from tkinter import font
import tkinter as tk
from PIL import Image,ImageDraw, ImageFont, ImageTk
import time
from constantes import *
import customtkinter as ctk
import json
import os
import requests 
from componentes import Label_Image

#the Splash withe the Logo of Institution to show When the System is Loaded
class SplashP:
    #Build the Window 
    def __init__(self,vent,size_win):
        self.root= ctk.CTkToplevel()
        self.root.configure(fg_color="white")
        self.vent=vent
        width_of_window = size_win["Width"]
        height_of_window = size_win["Height"]
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width_of_window / 2)
        y_coordinate = (screen_height / 2) - (height_of_window / 2)
        self.root.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))
        self.root.overrideredirect(1)
        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_columnconfigure(0,weight=1)
        self.Mainframe=ctk.CTkFrame(self.root,fg_color="white",bg_color='white')
        self.Mainframe.grid(row=0,column=0,sticky="",padx=20,pady=20)
        self.configure_splash()
             
        self.root.update_idletasks()
        self.root.mainloop()

    #Configure the Components
    def configure_splash(self):
        url=f"{constantes.SERVER}UI_Json/Splash_Panel.json"
        response=requests.get(url)
        if(response.status_code>400):
           General.show_error("Panel not Found","Json File Not Found")
           return
        raw_data=response.content  
        from io import BytesIO
        temp_file=BytesIO(raw_data)  
        data=json.load(temp_file)
        widgets=data["Widgets"]
        for element in widgets:
          posicion=element["Posicion"]
          props=element["Propiedades"]
          widget_type=element["Type"]
          self.add_component(posicion,props,widget_type)
          
    #Add a Component to the Windows
    def add_component(self,pos,props,widget_type):
       if(widget_type=="CTkLabel"):          
           text=props["Text"]      
           colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"]}
           ev=None
           font_data=props["Font"]
           font_lbl=ctk.CTkFont(family=font_data["Name"],size=int(font_data["Size"]),weight=font_data["Style"])
           lbl = ctk.CTkLabel(self.Mainframe, text=text, text_color=props["Text_Color"], fg_color=props["Fg_Color"],font=font_lbl)
           lbl.grid(row=pos["row"],column=pos["column"],sticky=pos["sticky"],padx=pos["padx"],pady=pos["pady"])
       elif(widget_type=="CTkButton"):
          text=props["Text"]
          colors=props["Colors"]
          ev=None
          corner_radius=int(props["Corner_Radious"])
          font_data=props["Font"]
          font_btn=ctk.CTkFont(family=font_data["Name"],size=int(font_data["Size"]),weight=font_data["Style"])
          btn=ctk.CTkButton(self.Mainframe,text=text,fg_color=colors["Fg"],text_color=colors["Text"],hover_color=colors["Hover"],corner_radius=int(corner_radius),font=font_btn)
          btn.grid(row=pos["row"],column=pos["column"],sticky=pos["sticky"],padx=pos["padx"],pady=pos["pady"])
          if(props["Id"]=="btn_continue"):
            btn.configure(command=self.on_continue)  
       elif(widget_type=="CTkImage"):
          src=props["Source"]
          bg_color=props["Fg_Color"]
          for i in range(0,len(src)):
             temp_src=src[i]
             url=f"{constantes.SERVER}{temp_src}"
             src[i]=url
          w=int(props["Width"])
          h=int(props["Heigth"])
          is_icon=False if props["Interactuable"]=="False" else True
          tag="image"
          default_state=True
          image=Label_Image(pos,self.Mainframe,src,w,h,bg_color,is_icon,props["Id"],tag,default_state)
          image.set_active(True)
           
    #Destroy the Splah and Show the Main Windows       
    def on_continue(self):
         self.root.destroy()  
         self.vent.activar()
       