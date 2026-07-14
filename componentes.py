import customtkinter as ctk
from tkinter import *   
import tkinter as tk
from tkinter import ttk 
from tkinter.font import Font
from PIL import Image,ImageDraw, ImageFont, ImageTk
from constantes import constantes

#Component Base Class
class componente:
      #Build the Component
      def __init__(self,nombre,tag,state,parent):
           self.tag=tag
           self.nombre=nombre
           self.default_state=state
           self.state=state
           self.parent=parent
 
      #get the Id of Component           
      def get_id(self):
           return self.nombre
           
      #get the Tag of Component( Component type)
      def get_tag(self):
           return self.tag
      
      #Method for Override in Child class, Set Active or Inactive the Component      
      def set_active(self,value):
          print(value)
      
      #Return the Initial State of a Component      
      def is_initial_active(self):
          return self.default_state
      
      #Return the State of a Component      
      def get_state(self):
          return self.state
       
      #set the Parent
      def set_parent(self,value):
        self.parent=value
        
      #Get the Parent
      def get_parent(self):
          return self.parent
          
      #Destroy Component and Free Memory
      def free_Memory(self):
        print("destroy")
      
#Table Component
class Tabla(componente):
   
    index=1          #Global index of Table for styles
    #Build the Table
    def __init__(self,pos,parent,colors,headers,ancho_column,ids,alto_tabla,nombre,tag,default_state,evento):
        super().__init__(nombre,tag,default_state,parent)
        self.container=parent
        self.cant_headers=len(headers)
        self.table= ttk.Treeview(parent, height=alto_tabla, columns=[f"#{n}" for n in range(0, self.cant_headers-1)])
        self.row_selected=" "
        self.last_row=0
        self.pos=pos
        self.ev=evento
        for i in range(0,self.cant_headers):
            self.table.heading(ids[i], text=headers[i])
            self.table.column(ids[i],width=ancho_column,anchor='c')
        self.table.bind("<B1-Motion>", self.restrictor)
        self.table.bind("<<TreeviewSelect>>", self.On_tree_select)  
        font_text=Font(family="Arial", weight="bold", size=13) 
        style = ttk.Style()
        style_name="Custom"+str(Tabla.index)+".Treeview"
        style_header="Custom"+str(Tabla.index)+".Treeview.Heading"
        style_treeheading="Custom"+str(Tabla.index)+".Treeheading"
        style.element_create( style_treeheading+".border", "from", "default")
        style.layout(style_header, [( style_treeheading+".cell", {'sticky': 'nswe'}),( style_treeheading+".border", {'sticky':'nswe', 'children': [( style_treeheading+".padding", {'sticky':'nswe', 'children': [( style_treeheading+".image", {'side':'right', 'sticky':''}),( style_treeheading+".text", {'sticky':'we'})]})]}),])
        style.configure(style_name,bd=0,font=('Calibri', 11))
        style.configure(style_header,background=colors["Bg"], foreground=colors["Fg"], relief="flat",font=font_text)
        style.map(style_name, background=[('selected',colors["Bg_Select"])],foreground=[('selected',colors["Fg_Select"])],font=[('selected',font_text)])
        style.map(style_header, relief=[('active','groove'),('pressed','sunken')])
        self.table.configure(style=style_name)
        Tabla.index+=1
        
        
    #change the Component Master of Tabla component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]     
        self.container.grid_forget()
        self.table.grid_forget()
        self.container.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        self.table.grid(row=0,column=0)
     
    #Reset the Table
    def reset(self):
        childs=self.table.get_children()
        for i in range(0,len(childs)):
          data=None
          data=self.table.item(childs[i])
          if(data!=None):
              self.table.delete(str(i))  
        self.last_row=0
        self.row_selected=" "

    #Update Value of a Row
    def update_row(self,index,values):
        if(self.last_row<=0):
            return 
        if(index<0 or index>=self.last_row):
            return  
        last_values=[]
        for i in range(0,self.last_row):
            data=None
            data=self.table.item(str(i))
            if(data!=None):
              last_values.append(data["values"])
              self.table.delete(str(i))
        last_values[index]=values
        self.last_row=0
        for i in range(0,len(last_values)):  
            self.add_row(last_values[i])         
                               
    #upodate the table and remove value of Indicated Index  
    def update_Table(self,index_deleted):
    
        last_values=[]
        for i in range(0,self.last_row):
            if(i!=index_deleted):
              data=None
              data=self.table.item(str(i))
              if(data!=None):
                last_values.append(data["values"])
                self.table.delete(str(i)) 
        self.last_row=0
        for i in range(0,len(last_values)):  
            self.add_row(last_values[i])         
                 
    #Delete a Row        
    def delete_row(self,index):
        if(self.last_row<=0):
            return  
        if(index<0 or index>=self.last_row):
           return   
        data=None
        data=self.table.item(str(index))
        if(data!=None):
            self.table.delete(str(index))
            self.update_Table(index)
            self.row_selected=" "
           
    #get the data of Selected Row   
    def get_row_selectedData(self):
        if(self.row_selected==" "):
             return " "
        data=self.table.item(self.row_selected)
        return data["values"]
        
    #get the Data of Indicated Row 
    def get_row_Data(self,row):
        if(row<0 or row>=self.last_row):
            return " "  
        iid=str(row)
        data=self.table.item(iid)
        return data["values"]

    #Add a New Row to the Table    
    def add_row(self,values):
        if(len(values)+1>self.cant_headers):
            #prevent to add a Row withe More values Than Headers
            return  
        temp_list=[]
        valores=()
        #Verify if the Values is a List or a Tuple
        if(type(values)==type(temp_list)):
            valores=tuple(values)
        else:
            valores=valores+values
        self.table.insert("",tk.END,text=str(self.last_row+1),values=valores,iid=str(self.last_row))
        self.last_row+=1
        
    #Event On Select of a Row     
    def On_tree_select(self,event):
        self.row_selected=self.table.focus()
        if(self.ev!=None):
            from UI_Event import UI_Event
            UI_Event.interprete_Table_Event("Select",self.get_id(),self.ev,self.get_row_selectedData())
    
    #Permit Generate Button Release Events On the Table
    def restrictor(self,Event):
        if(str(self.table["cursor"]) == "size_we"):
            self.table.event_generate("<ButtonRelease-1>")

    #On Load Event
    def On_load(self):
       if(self.ev!=None):
            from UI_Event import UI_Event
            UI_Event.interprete_Table_Event("Load",self.get_id(),self.ev,"")
    
    
    #Destroy Component and Free Memory
    def free_Memory(self):
        self.container.grid_forget()
        self.table.grid_forget()
        self.container.destroy()
        self.table.destroy()

        
    #Set Active or Inactive the Table        
    def set_active(self,value):
        self.state=value
        if(value==True):
            if(self.get_parent()!=self.container):
              self.container.grid_forget()
              self.table.grid_forget()
              self.container.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
              self.table.grid(row=0,column=0)
            else:
                self.container.grid(row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
                self.table.grid(row=0,column=0)
            if(self.ev!=None):
                self.On_load()
        else:
            self.container.grid_remove()
            self.table.grid_remove()
            self.reset()
               
              
#Canvas Component                     
class Lienzo_dibujo(componente):
    def __init__(self,parent,bg_c,dim,nombre,tag,default_state=True):
         super().__init__(nombre,tag,default_state,parent)
         self.canvas=ctk.CTkCanvas(parent, bg=bg_c,width=dim[0], height=dim[1])
         self.bg_default=bg_c
         self.dim_lienzo=(dim[0],dim[1])
         self.img=None
         
    #change the Component Master of Canvas component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]     
        self.canvas.grid_forget()
        self.canvas.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
       
    #draw a Image On Canvas       
    def draw_image(self,img,pos):
        try:
          self.canvas.create_image(0, 0,anchor=NE, image=img)   
        except:
          self.reset()
          
    #Draw a Line On Canvas        
    def draw_line(self,p1,p2,width_l,color):
        self.canvas.create_line(p1[0],p1[1],p2[0],p2[1],fill=color,width=width_l)
    
    #draw a Rectangle on Canvas
    def draw_rectangle(self,x,y,w,h,color):
       self.canvas.create_rectangle(x, y, x+w, y-h, fill=color)
       
    #Draw a Text On Canvas   
    def draw_text(self,pos,fuente_name,style_font,size_f,text_color,texto):
       font_text=Font(family=fuente_name,weight=style_font, size=size_f) 
       self.canvas.create_text(pos[0],pos[1],text=texto,fill=text_color,font=font_text)
    
    #Reset the Content of Canvas
    def reset(self):
         self.canvas.delete('all') 
         
    #Destroy Component and Free Memory  
    def free_Memory(self):
       self.canvas.pack_forget()
       self.canvas.destroy()
        
    #Set Active or Inactive the Canvas    
    def set_active(self,value):
        if(value==True):
            self.canvas.pack() 
        else:
            self.canvas.pack_forget()
            self.reset()
            
#Button Component
class Boton(componente):
    #Build The Button
    def __init__(self,pos,parent,text,font,colores,img_sources,num_images,dim_boton,nombre,tag,default_state,corner_radius):
        super().__init__(nombre,tag,default_state,parent)
        self.boton=None
        self.have_image=False
        self.icons_sources=[]
        self.icons=[]
        self.num_images=0
        self.dim_boton=()
        self.colors=colores
        self.disabled=False
        self.configure_button(img_sources,text,font,parent,corner_radius)
        self.pos=pos
 
    #change the Component Master of Button component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]
        self.boton.grid_forget()
        self.boton.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
    
    #Configure the values of Button
    def configure_button(self,img_sources,text,font,parent,corner_radius):
        if(img_sources==None):
            text=text.capitalize()
            temp_text=text.split(" ")
            if(len(temp_text)>=2):
                text=""
                for i in range(0,len(temp_text)):
                    if(len(temp_text[i])>3):
                           temp_text[i]=temp_text[i].capitalize()
                           if(i>0):
                               text=text+" "+temp_text[i].capitalize()
                           else:
                               text=temp_text[i].capitalize() 
                    else:
                        text=text+" "+temp_text[i]
                        
            self.boton=ctk.CTkButton(parent,text=text,fg_color=self.colors["Fg"],font=font,text_color=self.colors["Text"],hover_color=self.colors["Hover"],cursor='hand2',corner_radius=corner_radius)       
            self.boton.bind("<Enter>",self.on_mouse_enter)
            self.boton.bind("<Leave>",self.on_mouse_leave)
        else:
            self.have_image=True 
            self.dim_boton=dim_boton
            self.set_icons(parent,font,img_sources,num_images)
            if(self.num_images>0):            
              self.boton=ctk.CTkButton(parent,image=self.icons[0],fg_color=self.colors["Fg"],hover_color=self.colors["Hover"],relief=FLAT,bd=0,cursor='hand2',corner_radius=corner_radius)
              self.boton.bind("<Button-1>",self.on_click_down)
              self.boton.bind("<ButtonRelease-1>",self.on_click_up)
              self.boton.bind("<Enter>",self.on_mouse_enter)
              self.boton.bind("<Leave>",self.on_mouse_leave)               
        
    #The Mouse Leave the Button
    def on_mouse_leave(self,event):
         if(self.have_image):
           self.boton.configure(image=self.icons[0])
         else:
           self.boton.configure(fg_color=self.colors["Fg"],text_color=self.colors["Text"])
    
    #The Mouse is Over Button    
    def on_mouse_enter(self,event):
         if(self.disabled==False):
           if(self.have_image):
             self.boton.configure(image=self.icons[1])
           else:
              self.boton.configure(fg_color=self.colors["Hover"],text_color=self.colors["Text_Hover"])
    
    #Change the State of Button    
    def set_state(self,st):
         if(st=="normal"):
            self.disabled=False
         else:
            self.disabled=True
         self.boton.configure(state=st) 

    #Change Icon for Click Down Event         
    def on_click_down(self,event):
        self.boton.configure(image=self.icons[2])
    
    #change Icon for Clik Up Event    
    def on_click_up(self, event):
       self.boton.configure(image=self.icons[1])
    
    #change source of Icons    
    def change_images(self,img_sources,num_image):
         self.set_icons(img_sources,num_images)
         if(self.num_images>0):
           self.configure(image=icons[0])
    
    #set and load the Icons     
    def set_icons(self,parent,font,img_sources,num_images):
        if(self.have_image):
            self.icons_sources=[]
            self.icons=[]
            self.num_images=num_images
            try:
              import requests
              from io import BytesIO             
              for i in range(0,self.num_images): 
                 temp_img=None
                 if(img_sources[i].startswith("http")==False):              
                     self.icons_sources.append(constantes.FOLDER_IMAGES+img_sources[i])
                     temp_img=Image.open(self.icons_sources[i])
                 else:
                     self.icons_sources.append(img_sources[i])
                     response=requests.get(self.icons_sources[i])
                     correcto=True
                     if(response.status_code>400):
                        correcto=False                     
                     if(correcto==True):
                        data=response.content
                        temp_img= Image.open(BytesIO(data))                        
                 if(temp_img!=None):
                    resized=temp_img.resize(self.dim_boton)
                    self.icons.append(ImageTk.PhotoImage(resized)) 
                 else:
                    self.have_image=False     
                    self.img_source=None   
                    self.num_images=-1
                    self.colors["Fg"]="white"
                    self.colors["Text"]="black"
                    self.boton=ctk.CTkButton(parent,text="error loading image",bg_color="white",font=font,fg_color="black",hover_color="red",cursor='hand2')       
                    self.boton.bind("<Enter>",self.on_mouse_enter)
                    self.boton.bind("<Leave>",self.on_mouse_leave)                
                  
            except:
                self.have_image=False     
                self.img_source=None   
                self.num_images=-1
                self.colors["Fg"]="white"
                self.colors["Text"]="black"
                self.boton=ctk.CTkButton(parent,text="error loading image",bg_color="white",font=font,fg_color="black",activeforeground="yellow",activebackground="red",cursor='hand2')       
                self.boton.bind("<Enter>",self.on_mouse_enter)
                self.boton.bind("<Leave>",self.on_mouse_leave)                
    
    #Return True if the Button use Icons    
    def is_icon(self):
       return self.have_image
       
    #Destroy Component and Free Memory  
    def free_Memory(self):
        self.boton.grid_forget()
        self.boton.destroy()
           
    #Set Active or Inactive the Button   
    def set_active(self,value):
        self.state=value 
        if(value==True):
            self.boton.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])      
        else:
            self.boton.grid_remove()
            if(self.is_icon()):
              self.boton.configure(image=self.icons[0])
  
#Internal Panel
class Internal_Frame(componente):
    #Build the Inner Panel
    def __init__(self,posicion,master,color,nombre,tag,default_state,scroll,ev,corner_radius):
         super().__init__(nombre,tag,default_state,master.container)  
         self.container=None 
         self.ev=ev
         self.color=color
         self.scroll=scroll
         self.pos=posicion
         if(self.scroll):
            from event_manager import Event_manager
            root=Event_manager.vent.raiz
            self.frame=ctk.CTkFrame(master.container,fg_color=self.color,corner_radius=corner_radius) 
            self.frame.grid(row=self.pos["row"],column=self.pos["column"], padx=self.pos["padx"],pady=self.pos["pady"],sticky="nsew")
            self.frame.grid_columnconfigure(0,weight=1)
            self.frame.grid_rowconfigure(0,weight=1)
            self.canvas=ctk.CTkCanvas(self.frame,highlightthickness=0,bg=root._apply_appearance_mode(self.color))
            self.canvas.grid(row=0,column=0,sticky="nsew" ,padx=8,pady=8)
            self.scroll_y=ctk.CTkScrollbar(self.frame,orientation="vertical",command=self.canvas.yview)
            self.scroll_y.grid(row=0,column=1,sticky="ns",padx=8,pady=8)
            self.scroll_x=ctk.CTkScrollbar(self.frame,orientation="horizontal",command=self.canvas.xview)
            self.scroll_x.grid(row=1,column=0,sticky="ew",padx=8,pady=8)
            self.canvas.configure(yscrollcommand=self.scroll_y.set,xscrollcommand=self.scroll_x.set)
            self.container=ctk.CTkFrame(self.canvas,fg_color=self.color)
            id_vent=self.canvas.create_window((0,0),window=self.container,anchor="nw")
            self.container.bind("<Configure>",self.update_scrolls)       
         else:
           self.container=ctk.CTkFrame(master.container,fg_color=self.color,corner_radius=corner_radius) 
         self.Intelligent_pad=False
         self.porcent_padX=1.0
         self.porcent_padY=1.0
         if(type(self.pos["pady"]).__name__=="float" or  type(self.pos["padx"]).__name__=="float"):
            self.Intelligent_pad=True          
            if(type(self.pos["padx"]).__name__=="list"):
              self.porcent_padX=self.pos["padx"][0]
            else:
                self.porcent_padX=self.pos["padx"]
            
            if(type(self.pos["pady"]).__name__=="list"):
               self.porcent_padY=self.pos["pady"][0]
            else:
                self.porcent_padY=self.pos["pady"]

         self.last_comp=0
         self.color=color
         self.comps=[]
         self.tags=[]
         self.names=[]
         self.pos_comps=[]
         self.master=master
         self.columnspan=None
         self.propagate=True
         self.porcent_parent=self.pos["porcent_parent"]
         if(self.pos["propagate"]=="False"):
            self.propagate=False
         if(self.pos["columnspan"]!="None"):
            temp_val=int(self.pos["columnspan"])
            if(temp_val>0):
                self.columnspan=temp_val
         if(self.columnspan!=None):
             if(self.scroll==False):
                 self.container.grid(row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"],columnspan=self.columnspan)                 
         else:
            if(self.scroll==False):
                self.container.grid(row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])          
         self.container.grid_propagate(self.propagate)
         self.first_Activation=True
   
    #Update scroll for Scrollable Frames
    def update_scrolls(self,event):
        from event_manager import Event_manager
        vent=Event_manager.vent
        vent.raiz.after_idle(lambda:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
       
        
    #Limit Panel Size
    def limit_panel(self,w_limit,h_limit):
       if(w_limit<=1 or h_limit<=1):
           return
       new_w=round(w_limit*self.porcent_parent["Width"])
       new_h=round(h_limit*self.porcent_parent["Height"])
       if(self.scroll==False):
          self.container.configure(width=new_w,height=new_h)
       else:       
          self.canvas.configure(width=new_w,height=new_h)
          self.canvas.update_idletasks()
       
       for i in range(0,self.last_comp):
           if(self.tags[i]=="frame"):
               self.comps[i].limit_panel(w_limit,h_limit)
               self.comps[i].calculate_pad(w_limit,h_limit)
           elif(self.tags[i]=="label"):               
                self.comps[i].resize_pad(w_limit,h_limit)
         
    #Calculate the Correct Pad for Frames with Intelligent Pad 
    def calculate_pad(self,w_parent,h_parent):       
        if(self.Intelligent_pad==False):
            return
        new_padx=w_parent*self.porcent_padX
        new_pady=h_parent*self.porcent_padY
        info_actual=self.container.grid_info()
        pad_actualx=info_actual.get("padx",0)
        pad_actualy=info_actual.get("pady",0)
        dif_margin=2
        if(abs(new_padx-pad_actualx)>dif_margin or abs(new_pady-pad_actualy)>dif_margin):            
           self.pos["padx"]=new_padx
           self.pos["pady"]=new_pady
           self.container.grid(padx=new_padx,pady=new_pady)
       
    #Return the Background    
    def get_background(self):
        return self.color
        
    #Return the Component in the Indicated position
    def check_pos(self,pos):
        for i in range(0,self.last_comp):
           if(self.pos_comps[i][0]==pos[0] and self.pos_comps[i][1]==pos[1]  and self.tags[i]=="frame"):
               return self.comps[i] 
        return None
    
    #Add a Component    
    def add_comp(self,comp,name,tag,pos=[0,0],intern_pos=[0,0]): 
        index=-1
        inside_frame=False
        for i in range(0,self.last_comp):
           if(self.names[i]==name):
               index=i
               break
           if(self.pos_comps[i][0]==pos[0] and self.pos_comps[i][1]==pos[1]):
               index=i
               if(self.tags[i]=="frame"):
                   inside_frame=True
               break
        if(index==-1):
           self.comps.append(comp)
           self.names.append(name)
           self.tags.append(tag)
          
           if(tag=="field" or tag=="combo" or tag=="pass"):            
               self.container.grid_columnconfigure(pos[1],weight=1)
           elif(tag=="list" or tag=="table"):
              self.container.grid_rowconfigure(pos[0],weight=1)
           elif(tag=="frame"):
              self.container.grid_columnconfigure(pos[1],weight=1)
              self.container.grid_rowconfigure(pos[0],weight=1)              
           self.pos_comps.append([pos[0],pos[1]])       
           self.last_comp+=1
           if(tag!="frame"):
                comp.change_master(self.container,pos)
        else:
           if(inside_frame):
              self.comps[index].add_comp(comp,name,tag,intern_pos)
           else:
              print(f"replace {self.names[index] } by {name}")
              self.comps[index]=comp
              self.names[index]=name
              self.tags[index]=tag
              self.pos_comps[index]=[pos[0],pos[1]]
           
        return 0
    
    #Return the First Component with the Indicated tag   
    def get_comp_byTag(self,tag): 
        for i in range(0,self.last_comp):
            if(self.tags[i]!="frame"):
                if(self.tags[i]==tag):
                    return self.comps[i]
            else:
               temp_res=self.comps[i].get_comp_byTag(tag)
               if( temp_res!=None):
                    return temp_res
        return None
                
    #Return the Component at the Indicated Index    
    def get_comp_ByIndex(self,index):
           return self.comps[index]
        
    #Get the Component with the Indicated tag
    def get_comp_ByName(self,nam,only_comp=True):

        for i in range(0,self.last_comp):
            if(self.tags[i]!="frame"):
                if(self.names[i]==nam):
                    return self.comps[i]
            else:
               if(only_comp==True):
                 temp_res=self.comps[i].get_comp_ByName(nam)
                 if( temp_res!=None):
                      return temp_res
               else:
                  if(self.names[i]==nam):
                     return self.comps[i]
        return None
                
    #Get the Components with the Indicated Tag as a Tuple with the components, tag and names         
    def get_comp_ByTags(self,tag):
        res=()
        temp_comps=[]
        temp_tags=[]
        temp_names=[]
        for i in range(0,self.last_comp):
            if(self.tags[i]=="frame"):
                cont_res=self.comps[i].get_comp_ByTags(tag)
                for j in range(0,len(cont_res[0])):
                    temp_comps.append(cont_res[0][j])
                    temp_tags.append(cont_res[1][j])
                    temp_names.append(cont_res[2][j])
            else:
               if(self.tags[i]==tag):
                   temp_comps.append(self.comps[i])
                   temp_tags.append(self.tags[i])
                   temp_names.append(self.names[i])
                   
        res=(temp_comps,temp_tags,temp_names)
        return res
        
   
    #Set Active or Inactive the Inner Panel    
    def set_active(self,active):
      
       if(active):
           
           if(self.columnspan!=None):
              if(self.scroll==False):                                   
                  self.container.grid(in_=self.master.container,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"],columnspan=self.columnspan)                   
           else:
              if(self.scroll==False):           
                 self.container.grid(in_=self.master.container,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])          
          
           for i in range(0,self.last_comp):
                 
                 comp_activate=False
                 if(self.first_Activation==False):
                    comp_activate=True
                 else:
                   if(self.comps[i].is_initial_active()==True):
                        comp_activate=True
                       
                 if(comp_activate):
                     
                     self.comps[i].set_active(True)               
                 else:
                     self.comps[i].set_active(False)
           self.first_Activation=False
       else:
           self.container.grid_remove()
           for i in range(0,self.last_comp):
               self.comps[i].set_active(False)
     
  
#Radio Button Component  
class Radio(componente):
    #Build the Radio Button
    def __init__(self,pos,orient,parent,num_botones,fuente,colors,textos,nombre,tag,default_state,evento,border_width):
        super().__init__(nombre,tag,default_state,parent)
        self.variable=StringVar(value=" ")
        self.count=num_botones
        self.radios=[]
        self.values=[]
        self.pos=pos
        self.orient=orient
        for i in range(0,self.count):
          self.radios.append(ctk.CTkRadioButton(parent,variable=self.variable, text=textos[i],value=textos[i],fg_color=colors["Fg"],border_color=colors["Border"],text_color=colors["Text"],font=fuente,hover_color=colors["Hover"],border_width_checked=border_width["Check"],border_width_unchecked=border_width["Uncheck"]))
          self.values.append(textos[i])
          if(evento!=None):
             self.radios[i].configure(command= self.On_select)   
        self.ev=evento
      
      
             
    #change the Component Master of RadioButtons components
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1] 
        offset=(1,0)
        if(self.orient=="vertical"):
          offset=(0,1)        
        for i in range(0,self.count):
            self.radios[i].grid_forget()
            self.radios[i].grid(in_=new_master, row=self.pos["row"]+(offset[1]*i),column=self.pos["column"]+(offset[0]*i),padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])       
          
    #set the State of Radio Button    
    def set_state(self,valor):
        for rad in self.radios:
              rad.configure(state=valor) 
    
    #On Select Event          
    def On_select(self):
        from UI_Event import UI_Event
        self.set_state("normal")
        if(self.ev==0):
           UI_Event.interprete_RadioButton_Event(self.get_id(),self.variable.get())
    
    #On load Event
    def On_load(self):
       if(self.ev==0 or self.ev==2):
           self.set_selected_index(0)
           self.On_select()
       else:
          self.reset()       
    
    #Return the value of radio Button Selected
    def get_selected_value(self):  
        return self.variable.get()
    
    #reset variable with the value of Radio Button Selected
    def reset(self):       
        self.variable.set(" ")
   
    #selected a Radio Button by Index   
    def set_selected_index(self,index):   
        if(index>=0 and index<self.count):     
            self.variable.set(self.values[index])
     
    #select the radio Button withe the indicated item   
    def set_value(self,item):       
         for i in range(0,self.count):  
            if(self.values[i]==item):
               self.set_selected_index(i)
               
    #Destroy Component and Free Memory  
    def free_Memory(self):
         for i in range(0,self.count):
            self.radios[i].grid_forget()
            self.radios[i].destroy()
       
        
    #Active or Inactive the Component           
    def set_active(self,value):
        offset=(1,0)
        self.state=value  
        if(self.orient=="vertical"):
          offset=(0,1)        
        if(value==True):
            self.On_load()
            for i in range(0,self.count):
                self.radios[i].grid(in_=self.get_parent(),row=self.pos["row"]+(offset[1]*i),column=self.pos["column"]+(offset[0]*i),padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        else:
            for i in range(0,self.count):
                self.radios[i].grid_remove()
            self.reset()


#Combo Box Component
class Combo_box(componente):
    #Build the ComboBox
    def __init__(self,pos,parent,items,fuente,nombre,tag,colors,default_state,evento,force_width,select_firstOnActive):
         super().__init__(nombre,tag,default_state,parent)
         self.combo=ctk.CTkComboBox(parent,state="readonly",values=items,font=fuente,dropdown_font=fuente , command=self.On_select,fg_color=colors["Fg"],text_color=colors["Text"],button_color=colors["Button"],hover=False ,dropdown_fg_color=colors["Fg_Item"],dropdown_hover_color=colors["Hover"],dropdown_text_color=colors["Text_Item"],text_color_disabled="white")
         
         self.count=len(items)
         self.items_list=items
         self.pos=pos
         self.select_firstOnActive=select_firstOnActive
         self.ev=evento
         self.colors=colors
         
         if(force_width!=None):
             self.combo.configure(width=force_width)
         self.set_selected_index(0)
    
    #change the Component Master of ComboBox component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
            
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]     
        self.combo.grid_forget()
        self.combo.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        
    
    #set the State of ComboBox
    def set_state(self,valor): 
          if(valor=="disabled"):
            self.combo.configure(fg_color="red")
          else:
            self.combo.configure(fg_color=self.colors["Fg"])
          self.combo.configure(state=valor)   
    
    #On load Event
    def On_load(self):
        self.set_state("readonly")
        from UI_Event import UI_Event
        if(self.ev!=None):
           UI_Event.interprete_Combobox_Event("Load",self.get_id(),self.ev,"",self.get_state())
           
    #Return the Number of Items
    def get_count(self):
        return self.count
    
    #On Select Event    
    def On_select(self,event):
       from UI_Event import UI_Event
       if(self.ev!=None):
          UI_Event.interprete_Combobox_Event("Select",self.get_id(),self.ev,self.get_selected_value(),self.get_state())
        
    #get the selected value            
    def get_selected_value(self):
        return self.combo.get()
       
    #select a item by Index       
    def set_selected_index(self,index):
        if(index>=0 and index<self.count):
             self.combo.set(self.items_list[index])
    
    #set the Items of ComboBox    
    def set_values(self,items):
        self.combo.configure(values=items)
        self.count=len(items)
        self.items_list=items
    
    #Select the Indicated Item if Exist
    def set_value(self,target_item):
        index=-1
        for i in range(0,self.count):
             temp_item=self.items_list[i]
             if(temp_item==target_item):
                index=i
                break    
        if(index!=-1):
            self.combo.set(self.items_list[index])
    
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.combo.grid_forget()
          self.combo.destroy()
       
    #Set Active or Inactive the Component    
    def set_active(self,value):
       self.state=value
       if(value==True):
           if(self.ev!=None):
                self.On_load()
           if(self.select_firstOnActive):
               self.set_selected_index(0)
           self.combo.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"])
       else:
          self.combo.grid_remove()
          self.set_selected_index(0)


#Label Component
class Labl(componente):
    #Build the Label
    def __init__(self,posicion,parent,texto,fuente,colors,nombre,tag,default_state,evento):
      super().__init__(nombre,tag,default_state,parent)
      texto=self.Capitalize_text(texto)      
      self.variable=StringVar(value=texto)
      self.label=ctk.CTkLabel(parent,text=texto,textvariable=self.variable,font=fuente,fg_color=colors["Fg"],text_color=colors["Text"])
      self.pos=posicion
      self.ev=evento
      self.colors=colors
      self.columnspan=None
      self.Intelligent_pad=False
      self.porcent_padX=1.0
      self.porcent_padY=1.0
      if(self.pos["columnspan"]!="None"):
         temp_val=int(self.pos["columnspan"])
         if(temp_val>0):
             self.columnspan=temp_val
      if(type(self.pos["pady"]).__name__=="float" or  type(self.pos["padx"]).__name__=="float"):
            self.Intelligent_pad=True
            
            if(type(self.pos["padx"]).__name__=="list"):
              self.porcent_padX=self.pos["padx"][0]
            else:
                self.porcent_padX=self.pos["padx"]
            
            if(type(self.pos["pady"]).__name__=="list"):
               self.porcent_padY=self.pos["pady"][0]
            else:
                self.porcent_padY=self.pos["pady"]
         
                   
      if(evento==constantes.LABEL_RECUPERAR_PASS):
        self.label.configure(cursor='hand2')
        self.label.bind("<Button-1>",self.on_click)
    
    #change the Component Master of Label component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]    
        self.label.grid_forget()
        
        if(self.columnspan!=None):
           self.label.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"],columnspan=self.columnspan)   
        else:
            self.label.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
    
    #Resize the pad if it is Intelligent Pad
    def resize_pad(self,w_parent,h_parent):
        if(self.Intelligent_pad==False):
               return
        new_padx=round(w_parent*self.porcent_padX)
        new_pady=round(h_parent*self.porcent_padY)
        self.pos["padx"]=new_padx
        self.pos["pady"]=new_pady
        self.label.grid(padx=new_padx,pady=new_pady)
            
    #Capitalize the Text Converting Only the First Character of each phrase to Upper
    def Capitalize_text(self,texto):
        if(texto.isupper()==False):
          #Set the first Character of each Paragraph as Upper  
          temp_texto=texto.split(" ")
          if(len(temp_texto)>=2):
              texto=""
              for i in range(0,len(temp_texto)):
                  if(len(temp_texto[i])>=3):
                         if(temp_texto[i].isupper()==False):
                             temp_texto[i]=temp_texto[i].capitalize()
                             if(i>0):
                                 texto=texto+" "+temp_texto[i].capitalize()
                             else:
                                 texto=temp_texto[i].capitalize() 
                  else:
                      texto=texto+" "+temp_texto[i]
          else:
             texto=texto.capitalize() 
        return texto 
        
    #On Click Event    
    def on_click(self,arg):
       from event_manager import Event_manager
       if(self.ev==constantes.LABEL_RECUPERAR_PASS):
            Event_manager.recuperar_pass(1)
    
    #On Load Event 
    def On_load(self):
        from UI_Event import UI_Event
        if(self.ev!=None):
           UI_Event.interprete_label_Events(self.get_id(),self.ev,self.get_text())        
        
    #Return the Text of Label     
    def get_text(self):
      return self.variable.get()
      
    #set the Text of Label
    def set_text(self,texto):
      self.variable.set(texto)
 
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.label.grid_forget()
          self.label.destroy()
          
    #set Active or Inactive the Component
    def set_active(self,value):
        self.state=value
        if(value==True):
            if(self.columnspan!=None):
                self.label.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"],columnspan=self.columnspan)         
            else:
               self.label.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
            if(self.ev!=None):
                self.On_load()
        else:
            self.label.grid_remove()

#Images
class Label_Image(componente):
    #Buil the Component
    def __init__(self,pos,parent,img_source,width,heigth,bg_color,is_icon,nombre,tag,default_state):
      super().__init__(nombre,tag,default_state,parent)
      self.w=width
      self.h=heigth
      self.set_source(img_source)
      if(self.img!=None):
        self.label=ctk.CTkLabel(parent,image=self.img,fg_color=bg_color,text="")
      else:
        self.label=ctk.CTkLabel(parent,text="error loading image",fg_color="transparent")
      self.pos=pos
      if(is_icon):
         self.label.configure(cursor='hand2')
         
    #change the Component Master of Label Image
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
            
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]
        self.label.grid_forget()
        self.label.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
    
    #Set the Source of Image    
    def set_source(self,source):
      try:
        if(source.startswith("http")==False):
          #imagen local
          temp_img=Image.open(constantes.FOLDER_IMAGES+source)
          resized=temp_img.resize((self.w,self.h))
          self.img=ImageTk.PhotoImage(resized)
        else:
          #imagen en server
          import requests
          from io import BytesIO
          response=requests.get(source)
          if(response.status_code>400):
            self.img=None  
            return    
          data=response.content
          temp_img= Image.open(BytesIO(data))
          f=open("temp_foto.png","wb")
          f.write(data)
          resized=temp_img.resize((self.w,self.h))
          self.img=ImageTk.PhotoImage(resized)   
      except:
         self.img=None      
    
    #Change the Image
    def change_image(self,source):
         self.set_source(source)
         self.label.configure(image=self.img)
    
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.label.grid_forget()
          self.label.destroy()
          
    #Set Active or Inactive the Component      
    def set_active(self,value):
        self.state=value
        if(value==True):
            self.label.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"])
        else:
            self.label.grid_remove()

#Check Button
class Check_Button(componente):
    #Build the Check Button
    def __init__(self,pos,parent,texto,colors,fuente,nombre,tag,default_state,border_width):
       super().__init__(nombre,tag,default_state,parent)
       self.variable=StringVar(value=" ")  
       self.valor=texto       
       self.check=ctk.CTkCheckBox(parent,variable=self.variable,text=texto, text_color=colors["Text"],border_color=colors["Border"], fg_color=colors["Fg"],font=fuente,hover_color=colors["Hover"], onvalue=self.valor,offvalue=" ", border_width=border_width,checkmark_color=colors["CheckMark"])
       self.pos=pos
    
    #change the Component Master of CheckButton component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]     
        self.check.grid_forget()
        self.check.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        
    #get the Text of Check Button   
    def get_text(self):
       return self.valor
    
    #return True if the Check Button is Selected 
    def is_selected(self):
        valor=self.variable.get()
        if(valor==" "):
          return False
        else:
          return True
        
    #set selected or deselected the CheckButton         
    def set_selected(self,valor):
      if( valor==False):
        self.variable.set(" ")
      else:
        self.variable.set(self.valor)
    
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.check.grid_forget()
          self.check.destroy()
          
    #set Active or Inactive the Check Button    
    def set_active(self,value):
        self.state=value
        if(value==True):
            self.check.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        else:
            self.check.grid_remove() 
            self.set_selected(False)            

#Text Fields           
class TextField(componente):
    #Build the Text Field
    def __init__(self,pos,parent,fuente,colors,nombre,tag,default_state,evento,placeholder_text,corner_radius,password_field=False):      
        super().__init__(nombre,tag,default_state,parent)
        self.fuente=fuente
        self.colors=colors
        self.field= ctk.CTkEntry(parent, fg_color=self.colors["Fg"],text_color=self.colors["Text"],font=self.fuente,corner_radius=corner_radius,placeholder_text=placeholder_text,placeholder_text_color=colors["Placeholder_Text"])
        self.pos=pos 
        self.field.bind("<Key>", self.capture_char)
        self.field.bind("<FocusIn>",self.focus_enter)
        self.field.bind("<FocusOut>",self.focus_exit)
        self.ev=evento
        self.disabled=False
        self.field_state="normal"
        if(password_field):
            self.field.configure(show="*")
            
    #Focus Enter
    def focus_enter(self,event):
       if(self.field_state=="readonly" or self.field_state=="disabled"):
          return
       self.field.configure(fg_color=self.colors["Fg_Focus"],text_color=self.colors["Text_Focus"])
    #Focus Exit
    def focus_exit(self,event):
        if(self.field_state=="readonly" or self.field_state=="disabled"):
          return
        self.field.configure(fg_color=self.colors["Fg"],text_color=self.colors["Text"])
      
    #change the Component Master of TetField component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]    
        self.field.grid_forget()
        self.field.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
     
    #On Load Event 
    def On_load(self): 
        if(self.ev!=None):
            from UI_Event import UI_Event
            UI_Event.interprete_TextField_Events(self.get_id(),self.ev,self.get_text())      

    #get the Text 
    def get_text(self):
        return self.field.get()
    
    #get the field state as string
    def get_field_state(self):
        return self.field_state
      
    #set the state of TextField      
    def set_state(self,st):
         self.field.configure(state=st)
         self.field_state=st
         if(st=="disabled"):
            self.field_state="disabled"
            self.disabled=True
            self.field.configure(fg_color="#B2B2B2")
         else:
            if(st=="readonly"):
              self.field.configure(fg_color="#B2B2B2")
            else:
               self.field.configure(fg_color=self.colors["Fg"])
            self.disabled=False         
        
    #set the Text Value     
    def set_text(self,text):
        old_st=self.field_state
        self.field.configure(state="normal")
        self.field.delete(0,"end")
        if(text!=""):
            self.field.insert(0,text)
        self.field.configure(state=old_st)
      
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.field.grid_forget()
          self.field.destroy()
          
    #set Active or Inactive the Component
    def set_active(self,value):
        self.state=value
        if(value==True): 
            self.field.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"])
            if(self.ev!=None):
                  self.On_load()
        else:
            self.field.grid_remove()
            self.set_text("")
    
    #Update the Text when User Entry BackSpace Key
    def capture_char(self,event):
        if(event.keysym=="BackSpace"):
            self.set_text(self.field.get())


#list box component     
class List_Box(componente):
    #Build the Component
    def __init__(self,pos,parent,num_items,values,colores,fuente,alto,nombre,tag,default_state,evento):
          super().__init__(nombre,tag,default_state,parent)
          self.container=ctk.CTkFrame(parent,fg_color="white")
          self.lista=Listbox(self.container,bg=colores["Fg"],fg=colores["Text"],font=fuente)
          self.lista.grid(row=0,column=0)
          self.scrollBar=ctk.CTkScrollbar(self.container, orientation="vertical",command=self.lista.yview)
          self.scrollBar.grid(row=0, column=2, sticky='ns')
          self.lista.configure(yscrollcommand=self.scrollBar.set)
          self.count=0
          self.set_values(values)
          self.pos=pos
          self.ev=evento
          self.lista.bind("<<ListboxSelect>>",self.On_select)
          self.last_selected=None
   
             
    #change the Component Master of ListBox component
    def change_master(self,new_master,intern_pos):
        if(new_master==None):
            return
        self.set_parent(new_master)
        self.pos["row"]=intern_pos[0]
        self.pos["column"]=intern_pos[1]     
        self.lista.grid_forget()
        self.container.grid_forget()
        self.scrollBar.grid_forget()
        self.container.grid(in_=new_master,row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        self.lista.grid(row=0,column=0)
        self.scrollBar.grid(row=0, column=2, sticky='ns')
          
     
    #get the last item selected      
    def get_last_selected(self):
        return self.last_selected
    
    #On Select Event    
    def On_select(self,evento):
         
        from UI_Event import UI_Event
        if(self.ev!=None):
            UI_Event.interprete_ListBox_Event("Select",self.get_id(),self.ev,self.get_selected_item())
        self.reset_selection()  
    
    #Return the Number of items    
    def get_count(self):
       return self.count
       
    #On Load Event   
    def On_load(self):
         self.last_selected=None
         from UI_Event import UI_Event
         if(self.ev!=None):
            UI_Event.interprete_ListBox_Event("Load",self.get_id(),self.ev,self.get_selected_item())
         
        
    #Add a value  in the Indicated Index or at the End                       
    def insert_value(self,value,index=-1):
        if(index!=-1):
            self.lista.insert(index,value)
            self.count+=1
        else:
            self.lista.insert(tk.END,value)
            self.count+=1
            
    # set the values of the List    
    def set_values(self,values):
          self.reset()
          self.lista.insert(0,*values)
          self.count=self.lista.size()
    
    #Get the Value of Indicated Index    
    def get_value_at(self,index):
          if(index!=-1):
             return self.lista.get(index)
          else:
             return " "
             
    #Get all Values as a List          
    def get_all_values(self):
        values=[]
        for i in range(0,self.count):
            values.append(self.get_value_at(i) ) 
        return values
    
    
    #Delete a Element from the List    
    def delete_element(self,index=-1):
         if(index!=-1):
           self.lista.delete(index)
           self.count-=1
         else:
           self.lista.delete(self.count-1)
           self.count-=1
    
    #Reset the Selection data    
    def reset_selection(self):
        index=self.lista.curselection()
        if(len(index)>0):
           self.lista.selection_clear(self.lista.curselection())
    
    #Reset the List items    
    def reset(self):
        for i in range (0,self.count):
            self.lista.delete(0)
        self.count=0
    
    #Remove the Selected Item    
    def delete_selected_item(self):
        index=self.lista.curselection()
        if(len(index)>0):
           self.delete_element(index)
           return 0
        else:
           return -1
    
    #get the Selected Item Index    
    def get_selected_index(self):
        index=self.lista.curselection()
        if(len(index)>0):
          return index
        else: 
          return " "

    #get the Selected Item as a String      
    def get_selected_item(self):
        index=self.lista.curselection()
        if(len(index)>0):
          return self.get_value_at(index)
        else: 
          return " "
    
    #Modific the Value of Selected Item    
    def modif_selected_item(self,old_val,new_val):
        temp_vals=[0]*self.count
        for i in range(0,self.count):         
          value=self.get_value_at(i)
          if(value==old_val):
             temp_vals[i]=new_val
          else:
            temp_vals[i]=value
        self.set_values(temp_vals)
        
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.container.grid_forget()
          self.lista.grid_forget()
          self.lista.destroy()
          self.container.destroy()
          
    #Set Active or Inactive the Component
    def set_active(self,value):
        self.state=value
        if(value==True):
            if(self.ev!=None):
                 self.On_load()
            self.container.grid(in_=self.get_parent(),row=self.pos["row"],column=self.pos["column"],padx=self.pos["padx"],pady=self.pos["pady"],sticky=self.pos["sticky"])
        else:
            self.container.grid_remove()
            self.reset_selection()
            self.reset()
