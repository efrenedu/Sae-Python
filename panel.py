from tkinter import *   
from tkinter import ttk 

import customtkinter as ctk
from tkinter import messagebox          
from tkinter import font             
from constantes import *
from PIL import Image,ImageDraw, ImageFont, ImageTk

#the Panels of the Main Windows
class panel:
    #Build the Panel
    def __init__(self,win,color,id_p):
        self.win=win
        self.tags=[]
        self.comps=[]
        self.names=[]
        self.positions=[]
        self.background=color
        self.last_component=0
        self.id_panel=id_p
        self.container=ctk.CTkFrame(self.win,fg_color=color)
       # self.container.grid(row=1,column=0,sticky="nsew")
      #  self.set_active(True)
        self.set_TopLeft_margins()
    
    #Set top Left Margins on the Panel    
    def set_TopLeft_margins(self):
      self.container.grid_columnconfigure(0,minsize=constantes.MIN_SIZE_EMPTY_COLUMN,weight=0)
      self.container.grid_rowconfigure(0,minsize=constantes.MIN_SIZE_EMPTY_ROW,weight=0)
    
    #Set Bottom Right Margins on the Panel    
    def set_BottomRight_margins(self):
        max_column=0
        max_row=0
        for i in range(0,len(self.positions)):
           temp_pos=self.positions[i]
           if(temp_pos[0]>max_row):
               max_row=temp_pos[0]
           if(temp_pos[1]>max_column):
               max_column=temp_pos[1]
        max_column+=1
        max_row+=1
        self.container.grid_columnconfigure(max_column,minsize=constantes.MIN_SIZE_EMPTY_COLUMN,weight=0)
        self.container.grid_rowconfigure(max_row,minsize=constantes.MIN_SIZE_EMPTY_ROW,weight=0)
    

    #Get the Background Color of the Panel
    def get_background(self):
       return self.background
       
        
    #Return the Comp By Index         
    def get_comp_byIndex(self,index):
        res=None
        if(index>=0 and index<self.last_component-1):
           res=self.comps[index]      
        return res
    
    
    #Get the First Component with the Indicated Tag     
    def get_comp_byTag(self,tag):
        res=None
        for i in range(0,self.last_component):
            if(self.tags[i]!="frame"):
                if(self.tags[i]==tag):
                  res=self.comps[i]
                  return res
            elif(self.tags[i]=='frame'):
               temp_res=self.comps[i].get_comp_byTag(tag)
               if(temp_res!=None):
                  return temp_res     
        return None
        
    #Get the Component with the Indicated Name    
    def get_comp_byName(self,nam,only_comp=True):
        res=None
        for i in range(0,self.last_component):
            if(self.names[i]==nam and self.tags[i]!='frame' ):
                res=self.comps[i]
                return res
            elif( self.tags[i]=='frame'):
               if(only_comp):
                 #Look for the component insde Internal frame
                 res_cont=self.comps[i].get_comp_ByName(nam)
                 if(res_cont!=None):
                     return res_cont
               else:
                  #Look for Internal Frame
                  if(self.names[i]==nam):
                     return self.comps[i]
                  else:
                     #Look for a Internal frame Inside another Internal Frame
                     res_f= self.comps[i].get_comp_ByName(nam,False)
                     if(res_f!=None):
                         return res_f
        return None
     
    #Get the Components by the Indicated Tag as a List 
    def get_comps_byTag(self,tag):
        res=[]
        for i in range(0,self.last_component):
            if(self.tags[i]==tag):
                res.append(self.comps[i])
            elif(self.tags[i]=='frame'):
                temp_res=self.comps[i].get_comp_ByTags(tag)
                for j in range(0,len(temp_res[0])):
                    res.append(temp_res[0][j])
        return res
     
    #Add a Component to the Panel 
    def add_comp(self,comp,name,tag,have_master=False,master_pos=[0,0],pos=[0,0],intern_pos=[0,0]):
        index=-1
        inside_frame=False
        for i in range(0,self.last_component):
           if(name==self.names[i]):
                index=i
                break
           if(have_master):
              if(self.positions[i][0]==master_pos[0] and self.positions[i][1]==master_pos[1]):
                 index=i
                 if(self.tags[i]=="frame"):
                    inside_frame=True
                 break
           else:
              if(self.positions[i][0]==pos[0] and self.positions[i][1]==pos[1]):
                 index=i
                 break
       
              
        if(index==-1):
            
            self.tags.append(tag)
            self.comps.append(comp)
            self.names.append(name)
            self.positions.append(pos)
            self.comps[self.last_component].set_active(True)
            self.last_component+=1
            if(tag=="frame"):
               column_weight=comp.pos["column_weight"]
               row_weight=comp.pos["row_weight"]
               self.container.grid_rowconfigure(pos[0],weight=column_weight)
               self.container.grid_columnconfigure(pos[1],weight=row_weight)
        else:
            if(inside_frame):
                self.comps[index].add_comp(comp,name,tag,pos,intern_pos)
            else:
                self.comps[index]=comp
                self.names[index]=name
                self.tags[index]=tag
                self.positions[index]=[pos[0],pos[1]]
                self.comps[index].set_active(True)
    
    #Limit Internal Panels
    def limit_Internal_panels(self,w_limit,h_limit):
       for i in range(0,self.last_component):
           if(self.tags[i]=="frame"):
               comp=self.comps[i]
               comp.container.update_idletasks()
               comp.limit_panel(w_limit,h_limit)               
               
    #Destroy Component and Free Memory
    def free_Memory(self):
        for i in range(0,self.last_component):
          self.comps[i].free_Memory()  
        self.container.grid_forget()
        self.container.destroy()
       
        
    #Set Active or Inactive the Panel and Its Components   
    def set_active(self,value):
    
        if(value==True):
           self.container.grid(row=1,column=0,sticky="nsew")
           for i in range(0,self.last_component):
              if(self.comps[i].is_initial_active()):
                  self.comps[i].set_active(True)
        else:
           self.container.grid_forget()
           for i in range(0,self.last_component):
              self.comps[i].set_active(False)
