import customtkinter as ctk
from tkinter import *   
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox          
from tkinter.font import Font               
from panel import panel
from componentes import*
from event_manager import Event_manager
from constantes import *
from PIL import Image,ImageDraw, ImageFont, ImageTk
from ui import UI
import faulthandler
from datetime import datetime
from ventana_sec import Frame_Loading

#the Main Windows of System
class ventana:
    #Build the Windows
    def __init__(self,name_win):
        self.raiz=ctk.CTk() 
        self.loading_panel=False
        self.load_frame=None
        
        self.active_panel=0
        self.last_panel=0
        self.id_active_user=""
        self.raiz.title(name_win)
        self.panels_list=[]   
        width_screen=self.raiz.winfo_screenwidth()
        height_screen=self.raiz.winfo_screenheight()
        target_width=width_screen*constantes.WIDTH_PORCENT
        target_height= height_screen*constantes.HEIGTH_PORCENT
        target_width=round(target_width)
        self.last_size=[0,0]
      
        self.raiz.geometry(str(target_width)+"x"+str(target_height)+"+0+0")
        self.raiz.configure(bg='black')
        actual_time=datetime.now().hour
        if(actual_time>=6 and actual_time <18):
           ctk.set_appearance_mode("Light")
        else:
           ctk.set_appearance_mode("Dark")
        self.raiz.grid_rowconfigure(0,weight=0)
        self.raiz.grid_rowconfigure(1,weight=1)
        self.raiz.grid_rowconfigure(2,weight=0)
        self.raiz.grid_columnconfigure(0,weight=1)
        self.raiz.bind("<Configure>",self.limit_panels)
        self.activa=False
        self.secundaria=None
        Event_manager.vent=self
        self.menus=None
        self.panelActual=None
        self.panelActual_str=""
       # faulthandler.enable()
        self.raiz.withdraw()    
    
    def limit_fromWindow(self):
        w_limit=self.raiz.winfo_width()
        h_limit=self.raiz.winfo_height()
        if(w_limit<=1 or h_limit<=1):
          self.last_size=[0,0]
          self.limit_fromWindow()
          return
        if(w_limit!=self.last_size[0] or h_limit!=self.last_size[1]):
           self.last_size=[w_limit,h_limit]   
          
           if(self.panelActual!=None):
               self.panelActual.limit_Internal_panels(w_limit,h_limit)
               self.raiz.update_idletasks()
           
    #Limit Panels Size
    def limit_panels(self,event):
       if(event.widget==self.raiz):
           w_limit=event.width
           h_limit=event.height         
           if(w_limit<=1 or h_limit<=1):
               self.last_size=[0,0]
               self.limit_fromWindow()
               return
           if(w_limit!=self.last_size[0] or h_limit!=self.last_size[1]):
              self.last_size=[w_limit,h_limit]  
                     
              if(self.panelActual!=None):
                  self.panelActual.limit_Internal_panels(w_limit,h_limit)
                  
    #set the Menu
    def set_menu(self,menu_win):
         self.menus=menu_win
    
    #Return the Menu     
    def get_menu(self):
         return self.menus
       
    #Activate the Windows       
    def activar(self): 
        self.update_pantallas(constantes.PANTALLA_INICIO)
        self.raiz.deiconify()
        self.raiz.update()
        self.activa=True
        self.raiz.mainloop()
    
    #Build a New Panel on the Windows
    def build_panel(self,bg_color,panel_id):
        if(self.panelActual!=None):
           self.panelActual=None 
           self.panelActual_str=""           
        self.panelActual_str=panel_id
        self.panelActual=panel(self.raiz,bg_color,panel_id) 
        
    #Activate Components of Panel
    def activate_MainPanel(self):
        if(self.panelActual!=None):
            # self.panelActual.set_active(True)
             self.panelActual.set_BottomRight_margins()          
    
    #Add a Intern Panel 
    def add_Internal_Panel(self,posicion,color,id,corner_radius,ev,initial_state,parent,internal_position,scrollable):       
        master=self.panelActual if parent==None else parent
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[0,0]
        pos_master=[0,0]
        tag="frame"
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]
           have_master=True
        next_frame=Internal_Frame(posicion,master,color,id,tag,initial_state,scrollable,ev,corner_radius)
        self.panelActual.add_comp(next_frame,id,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
    #Add a Button to the Indicated Panel    
    def add_button(self,posicion,text,corner_radius,colors,font_data,id_name,ev,initial_state,parent,intern_pos):
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="button"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        boton=Boton(posicion,master,text,font,colors,id_name,tag,initial_state,corner_radius)
        self.panelActual.add_comp(boton,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
        #Assign the Event if is Neccesary
        if(ev!=None):
            boton.boton.configure(command=lambda:Event_manager.determine_event(ev,0))

        
    #Add a Label to the Indicated Panel
    def add_label(self,posicion,text,colors,font_data,id_name,ev,initial_state,parent,intern_pos):       
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="label"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]          
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        
        labl=Labl(posicion,master,text,font,colors,id_name,tag,initial_state,ev)
        self.panelActual.add_comp(labl,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
    #Add a Image to the Indicated Panel    
    def add_image(self,posicion,img_source,w,h,bg_color,is_icon,id_name,ev,initial_state,parent,intern_pos):     

        master=self.panelActual if parent==None else parent
        tag="image"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]          
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        img=Label_Image(posicion,master,img_source,w,h,bg_color,is_icon,id_name,tag,initial_state)
        self.panelActual.add_comp(img,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
    #Add a Text Field to the Indicated Panel
    def add_text_field(self,posicion,colors,font_data,corner_radius,placeholder_text,event,id_name,initial_state,parent,intern_pos,pass_field=False):
         
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="field"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        if(pass_field):
           tag="pass"
        text_fld=TextField(posicion,master,font,colors,id_name,tag,initial_state,event,placeholder_text,corner_radius,pass_field)
        self.panelActual.add_comp(text_fld,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
    
    #Add a ComboBox to the Indicated Panel   
    def add_comboBox(self,posicion,items,font_data,colors,id_name,ev,initial_state,parent,intern_pos,force_width):
       
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="combo"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        select_firstOnActive=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        if(self.panelActual_str!=constantes.PANTALLA_UPDATE_USER):
           select_firstOnActive=True
        combo = Combo_box(posicion,master,items,font,id_name,tag,colors,initial_state,ev,force_width,select_firstOnActive)
        self.panelActual.add_comp(combo,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
     
    #Add a Radio Button to the Indicated Panel
    def add_radioButton(self,posicion,orient,num,texts,colors,font_data,id_name,ev,initial_state,parent,intern_pos,border_width):
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="radio"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
       
        radio=Radio(posicion,orient,master,num,font,colors,texts,id_name,tag,initial_state,ev,border_width)
        self.panelActual.add_comp(radio,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
     
       
    #Add a Check Button to the Indicated Panel
    def add_checkButton(self,posicion,text,colors,font_data,id_name,ev,initial_state,parent,intern_pos,border_width):
       
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="check"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        check=Check_Button(posicion,master,text,colors,font,id_name,tag,initial_state,border_width)
        self.panelActual.add_comp(check,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
      
      
    
    #Add a Table to the Indicated Panel
    def add_table(self,posicion,headers,ids,ancho_column,alto_tabla,colors,id_name,ev,initial_state,parent,intern_pos):
       
        master=self.panelActual if parent==None else parent
        tag="table"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        fg_master=master.get_background()
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        frame=ctk.CTkFrame(master,fg_color="white")    
        tabl=Tabla(posicion,frame,colors,headers,ancho_column,ids,alto_tabla,id_name,tag,initial_state,ev)
          
        if(initial_state):
          tabl.set_active(True)
        if(ev!=constantes.TABLE_LOAD_DATA_CALIFICATIONS_STUDENTS and tabl!=None and frame!=None):
           vsb = ctk.CTkScrollbar(frame, orientation="vertical", command=tabl.table.yview)
           vsb.configure(button_color=colors["ScrollBar"],button_hover_color=colors["ScrollBar_Hover"],fg_color=fg_master)
           vsb.grid(row=0, column=2, sticky='ns')
           tabl.table.configure(yscrollcommand=vsb.set)
        self.panelActual.add_comp(tabl,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
     

    #add a List Box to the Indicated Panel
    def add_ListBox(self,posicion,values,font_data,colors,alto,id_name,ev,initial_state,parent,intern_pos):
        
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="list"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        fg_master=master.get_background()
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        lista=List_Box(posicion,master,len(values),values,fg_master,colors,font,alto,id_name,tag,initial_state,ev)
        self.panelActual.add_comp(lista,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
    #add a date field
    def add_date_field(self,posicion,colors,font_data,corner_radius,ev,id_name,initial_state,parent,intern_pos):
        font=ctk.CTkFont(family=font_data["Name"], size=int(font_data["Size"]),weight=font_data["Style"] ) 
        master=self.panelActual if parent==None else parent
        tag="date"
        pos_comp=[posicion["row"],posicion["column"]]
        intern_pos_comp=[intern_pos["Row"],intern_pos["Column"]]
        pos_master=[0,0]
        have_master=False
        if(parent!=None):
           pos_master=[master.pos["row"],master.pos["column"]]   
           if(type(master).__name__=="Internal_Frame"):
              master=master.container
           have_master=True
        date_fld=DateField(posicion,master,font,colors,id_name,tag,initial_state,ev,corner_radius)
        self.panelActual.add_comp(date_fld,id_name,tag,have_master,pos_master,pos_comp,intern_pos_comp)
    
         
    #Hide Load Panel
    def hide_load_Panel(self):
       self.panelActual.set_active(True)
       self.load_frame.hide_frame()
       self.loading_panel=False
       
    def redraw_load(self,ev=None):
       self.load_frame.lift()
       self.raiz.update_idletasks()
       if(self.loading_panel==True):
           self.raiz.after(10,self.redraw_load)
       
    #update the Panels states 
    def update_pantallas(self,next_p,from_menu=False):
        if(next_p!=""): 
           
           self.loading_panel=True
           if(self.panelActual!=None):
              self.panelActual.free_Memory() 
           if(self.load_frame==None):
               self.load_frame=Frame_Loading(self.raiz,constantes.FG_DEFAULT_BACKGROUND,"Cargando...",32,["#FFFFFF","#FFFFFF"])           
           self.load_frame.show_frame()

           #self.load_frame.bind("<Map>",self.redraw_load)
           self.raiz.update() 
                      
           UI.read_Jsondata(next_p)           
           self.raiz.update_idletasks()     
           self.raiz.event_generate("<Configure>")  
           
           self.raiz.after(100,self.hide_load_Panel)
           if(from_menu and self.panelActual_str==constantes.PANTALLA_WELCOME):
              Event_manager.show_data_user()
        
    #Close the Windows    
    def close(self):
        self.raiz.destroy()
