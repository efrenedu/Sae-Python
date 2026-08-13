from constantes import constantes
from event_manager import Event_manager
from tkinter import *   
import tkinter as tk
from tkinter import ttk 
from tkinter.font import Font
import json
import os



#Build the Panels and Graphic Components
class UI:
    @classmethod  
    def init_UI(cls,ventana):
        cls.vent=ventana
        cls.add_menu()
     
    #Build the Menu and Add it to the Main Windows 
    @classmethod  
    def add_menu(cls):  
    
        #Add the Bar and the List of Menus
        fuente=Font(family="Arial", size=14)        
        barra=tk.Menu(cls.vent.raiz)
        cls.vent.raiz.config(menu=barra) 
        m_usuario=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_usuario,label='usuario',font=fuente)
        m_registros=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_registros,label='registros',font=fuente)
        m_procesos=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_procesos,label='procesos',font=fuente)
        m_consultas=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_consultas,label='consultas',font=fuente)
        m_servicios=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_servicios,label='servicios',font=fuente)
        m_ayuda=tk.Menu(barra,tearoff=False)
        barra.add_cascade(menu=m_ayuda,label='ayuda',font=fuente)       
        
        items_userMenu=3
        items_RegisterMenu=5
        items_ProcessMenu=3
        items_ConsultMenu=10
        items_ServiceMenu=7
        items_helpMenu=2
        
        #Add the Items to the List of Menus and set it disabled as default value
        m_usuario.add_command(label='inicio',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_WELCOME,None,True),accelerator="Ctrl+a",font=fuente)
        m_usuario.add_command(label='logout',command=Event_manager.logout,accelerator="Ctrl+a",font=fuente)
        m_usuario.add_command(label='modificar informacion',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_UPDATE_USER,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_userMenu):
           m_usuario.entryconfig(i,state=tk.DISABLED)   
        m_registros.add_command(label='registrar personal',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_PERSONAL,None,True),accelerator="Ctrl+a",font=fuente)
        m_registros.add_command(label='registrar disponibilidad de horario',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_DISP_HORARIO,None,True),accelerator="Ctrl+a",font=fuente)
        m_registros.add_command(label='registrar formato',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_FORMATO,None,True),accelerator="Ctrl+a",font=fuente)
        m_registros.add_command(label='registrar area de formacion',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_AREA_FORMACION,None,True),accelerator="Ctrl+a",font=fuente)
        m_registros.add_command(label='registrar horario',command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_REGISTRO_HORARIO,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_RegisterMenu):
           m_registros.entryconfig(i,state=tk.DISABLED) 
        m_procesos.add_command(label="inscripcion",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_INSCRIPCION,None,True),accelerator="Ctrl+a",font=fuente)
        m_procesos.add_command(label="planificacion",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_PLANIFICACION,None,True),accelerator="Ctrl+a",font=fuente)
        m_procesos.add_command(label="rendimiento",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_PROCESO_RENDIMIENTO,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_ProcessMenu):
           m_procesos.entryconfig(i,state=tk.DISABLED) 
        m_consultas.add_command(label="personal",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_PERSONAL,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="estudiantes",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_ESTUDIANTES,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="docentes",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_PROFESORES,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="secciones",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_SECCIONES,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="momentos",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_MOMENTOS,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="disponibilidad de horarios",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_DISP_HORARIO,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="areas de formacion",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_AREAS_FORMACION,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="areas dictadas por docentes",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_AREAS_DOCENTE,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="materia pendiente",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_MAT_PEND,None,True),accelerator="Ctrl+a",font=fuente)
        m_consultas.add_command(label="descargas de trabajadores",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_CONSULTA_DESCARGAS,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_ConsultMenu):
           m_consultas.entryconfig(i,state=tk.DISABLED)
        m_servicios.add_command(label="respaldo de bd",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_RESPALDO_BD,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="gestion de usuarios",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_GESTION_USUARIO,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="auditorias",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_AUDITORIA,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="estadisticas",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_ESTADISTICA,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="actualizar estudiantes",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_UPDATE_ESTUDIANTE,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="reactivar momento",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_REACTIVAR_MOMENTO,None,True),accelerator="Ctrl+a",font=fuente)
        m_servicios.add_command(label="reorganizar secciones",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_SERVICIO_REORGANIZAR_SECCIONES,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_ServiceMenu):
           m_servicios.entryconfig(i,state=tk.DISABLED)           
        m_ayuda.add_command(label="manual de usuario",command=lambda:Event_manager.download_manual(),accelerator="Ctrl+a",font=fuente)
        m_ayuda.add_command(label="informacion de institucion",command=lambda:cls.vent.update_pantallas(constantes.PANTALLA_AYUDA_INFORMACION,None,True),accelerator="Ctrl+a",font=fuente)
        for i in range(0,items_helpMenu):
           m_ayuda.entryconfig(i,state=tk.DISABLED)
        barra.entryconfig("usuario",state=tk.DISABLED)
        barra.entryconfig("registros",state=tk.DISABLED)
        barra.entryconfig("procesos",state=tk.DISABLED)
        barra.entryconfig("consultas",state=tk.DISABLED)
        barra.entryconfig("servicios",state=tk.DISABLED)
        barra.entryconfig("ayuda",state=tk.DISABLED)        
        cls.vent.set_menu([barra,m_usuario,m_registros,m_procesos,m_consultas,m_servicios,m_ayuda])
        cls.vent.raiz.config(menu="")
        
    #Read the data of a Json data of a panel
    @classmethod  
    def read_Jsondata(cls,panel_name,usr):
        import time
        timestamp=str(int(time.time()))
        data_user={
          "token":"",
          "timestamp":timestamp,
          "target_panel":panel_name
        }
        if(usr!=None):
           data_user["token"]=usr.get_credentials()[4] 
        res=0
        import requests 
        from General import General
        url_send=f"{constantes.SERVER}panel_manager.php"
        response=requests.post(url_send,data=data_user)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return -1
        elif(json_content["status"]=="Invalid Access" or json_content["status"]=="Invalid Token"):
           General.show_message(json_content["message"],"Alerta")
           if(json_content["status"]=="Invalid Token"):
               res=-3
           else:
              res=-2
        redirect=json_content["Redirect_Panel"] 
        if(redirect!="No Redirect"):
            panel_name=redirect
        data=json_content["data"]       
        cls.vent.build_panel(constantes.FG_DEFAULT_BACKGROUND,panel_name)
        widgets=data["Widgets"]
        for element in widgets:
              posicion=element["Posicion"]
              props=element["Propiedades"]
              widget_type=element["Type"]
              cls.add_component(posicion,widget_type,props)
        cls.vent.activate_MainPanel()
        return res
   
    #add the component Required to the Panel 
    @classmethod  
    def add_component(cls,pos,widget_type,props):
       id=props["Id"]
       initial_state=props["Initial_state"]
       initial_state=True if initial_state=="True" else False
  
       internal_pos=props["Intern_Position"]
       parent=props["Master"]
       ev=None
       parent_comp=None
       if(parent!="None"):
          pnl=cls.vent.panelActual
          if(pnl!=None):
             parent_comp=pnl.get_comp_byName(parent,False)

       if(widget_type=="CTkFrame"):
          border_color=props["Border_Color"]
          scrollbar_color=props["ScrollBar_Color"]
          scrollbar_hover_color=props["ScrollBar_Hover_Color"]
          if(border_color=="None"):
             border_color=None
          colors={"Fg":props["Color"],"Border":border_color,"Scrollbar":scrollbar_color,"Scrollbar_Hover":scrollbar_hover_color}
          scrollable="False"
          if(props["Scroll"]=="True" or props["Scroll"]=="Full"):
            scrollable="Full"  
          elif(props["Scroll"]=="Y Axis"):
            scrollable="Y Axis"
                      
          corner_radius=int(props["Corner_Radious"])
          cls.vent.add_Internal_Panel(pos,colors,id,corner_radius,ev,initial_state,parent_comp,internal_pos,scrollable)
       elif(widget_type=="CTkLabel"):
          
           text=props["Text"]
           if ("+" in text):
              #Contant Integrate in Text
              text_list=text.split("+")
              temp_list=[]
              for i in range(0,len(text_list)):
                 val=text_list[i]
                 if(val.startswith("constantes")):
                    try:
                       val=val.strip()
                       temp_val=val.split(".")[1]
                       val_number=getattr(constantes,temp_val,"")
                       val=str(val_number)
                    except AttributeError:
                       val=""
                 temp_list.append(val)
              text="".join(temp_list)
                 
           colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"]}
           ev=cls.interprete_event(props["Ev"],None)
           font_data=props["Font"]
           cls.vent.add_label(pos,text,colors,font_data,id,ev,initial_state,parent_comp,internal_pos)
       elif(widget_type=="CTkButton"):
          text=props["Text"]
          colors=props["Colors"]
          ev=cls.interprete_event(props["Ev"],None)
          corner_radius=int(props["Corner_Radious"])
          font_data=props["Font"]
          cls.vent.add_button(pos,text,corner_radius,colors,font_data,id,ev,initial_state,parent_comp,internal_pos)
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
          cls.vent.add_image(pos,src,w,h,bg_color,is_icon,id,ev,initial_state,parent_comp,internal_pos)    
       elif(widget_type=="CTkText_field"):
          placeholder_text=props["Placeholder_Text"]
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Placeholder_Text":props["Placeholder_Text_Color"],"Fg_Focus":props["Fg_Focus"],"Text_Focus":props["Text_Focus"],"Disabled":props["Disabled_Color"],"Disabled_Text":props["Disabled_TextColor"]}
          if(colors["Placeholder_Text"]==""):
            colors["Placeholder_Text"]="gray"
          corner_radius=int(props["Corner_Radious"])
          font_data=props["Font"]
          ev=cls.interprete_event(props["Ev"],None)
          cls.vent.add_text_field(pos,colors,font_data,corner_radius,placeholder_text,ev,id,initial_state,parent_comp,internal_pos)
       elif(widget_type=="CTkPass_field"):
          placeholder_text=props["Placeholder_Text"]
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Placeholder_Text":props["Placeholder_Text_Color"],"Fg_Focus":props["Fg_Focus"],"Text_Focus":props["Text_Focus"],"Disabled":props["Disabled_Color"],"Disabled_Text":props["Disabled_TextColor"]}
          if(colors["Placeholder_Text"]==""):
            colors["Placeholder_Text"]="gray"
          corner_radius=int(props["Corner_Radious"])
          ev=cls.interprete_event(props["Ev"],None)
          font_data=props["Font"]
          cls.vent.add_text_field(pos,colors,font_data,corner_radius,placeholder_text,ev,id,initial_state,parent_comp,internal_pos,True)
       elif(widget_type=="CTkCombobox"):
          data=props["Data"].split(",")
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Hover":props["Hover_Color"],"Fg_Item":props["Fg_Item"],"Text_Item":props["Text_Item"],"Button":props["Button_Color"],"Disabled":props["Disabled_Color"],"Disabled_Text":props["Disabled_TextColor"],"Disabled_Button":props["Disabled_ButtonColor"]}
          corner_radius=int(props["Corner_Radious"])
          font_data=props["Font"]
          ev=cls.interprete_event(props["Ev"],None)
          width_bar=props["Force_Width"]
          if(width_bar!=""):
             width_bar=int(width_bar)
          else:
             width_bar=None
          cls.vent.add_comboBox(pos,data,font_data,colors,id,ev,initial_state,parent_comp,internal_pos,width_bar)
       elif(widget_type=="CTkTable"):
          items=props["data"]
          items=items.split(",") if items!="" else []
          data_Ids=props["data_Ids"]
          data_Ids=data_Ids.split(",") if data_Ids!="" else []
          colors=props["Colors"]
          width_column=int(props["Width_Column"])
          height_table=int(props["Heigth_Table"])
          ev=cls.interprete_event(props["Ev"],None)
          cls.vent.add_table(pos,items,data_Ids,width_column,height_table,colors,id,ev,initial_state,parent_comp,internal_pos)
       elif(widget_type=="CTkRadiobutton"):
          ev=cls.interprete_event(props["Ev"],None)
          direction=props["Direction"]
          btn_count=int(props["Button_Count"])
          btns_texts=props["Buttons_Texts"]
          border_width={"Check":6,"Uncheck":12}
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Border":props["Border_Color"],"Hover":props["Hover_Color"],"Disabled":props["Disabled_Color"],"Disabled_Text":props["Disabled_TextColor"]}
          font_data=props["Font"]
          cls.vent.add_radioButton(pos,direction,btn_count,btns_texts,colors,font_data,id,ev,initial_state,parent_comp,internal_pos,border_width)
       elif(widget_type=="CTkCheckbutton"):
          ev=cls.interprete_event(props["Ev"],None)
          text=props["Text"]
          border_width=10
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Border":props["Border_Color"],"Hover":props["Hover_Color"],"CheckMark":props["Check Mark_Color"]}
          font_data=props["Font"]
          cls.vent.add_checkButton(pos,text,colors,font_data,id,ev,initial_state,parent_comp,internal_pos,border_width)
       elif(widget_type=="CTkListbox"):
          ev=cls.interprete_event(props["Ev"],None)
          values=[] if props["Data"]=="" else props["Data"].split(",")
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Scrollbar":props["ScrollBar_Color"],"Scrollbar_Hover":props["ScrollBar_Hover_Color"],"Selected_Fg":props["Selected_Color"],"Selected_Text":props["Selected_Text_Color"]}
          heigth_list=int(props["Heigth"])
          font_data=props["Font"]
          cls.vent.add_ListBox(pos,values,font_data,colors,heigth_list,id,ev,initial_state,parent_comp,internal_pos)
       elif(widget_type=="CTkDate"):
          placeholder_text=props["Placeholder_Text"]
          colors={"Fg":props["Fg_Color"],"Text":props["Text_Color"],"Placeholder_Text":props["Placeholder_Text_Color"],"Fg_Focus":props["Fg_Focus"],"Text_Focus":props["Text_Focus"],"Disabled":props["Disabled_Color"],"Disabled_Text":props["Disabled_TextColor"]}
          if(colors["Placeholder_Text"]==""):
            colors["Placeholder_Text"]="gray"
          corner_radius=int(props["Corner_Radious"])
          font_data=props["Font"]
          ev=cls.interprete_event(props["Ev"],None)
          cls.vent.add_date_field(pos,colors,font_data,corner_radius,placeholder_text,ev,id,initial_state,parent_comp,internal_pos)
     
         
       
  
    #Read the value of event in string format an return it as integer value
    @classmethod
    def interprete_event(cls,ev_str,default_value):
        res=default_value
        if(ev_str=="None"):
            res=None
        elif(ev_str.startswith("constantes.")):
           try:
              temp_val=ev_str.split(".")[1]
              val_number=getattr(constantes,temp_val,default_value)
              res=val_number
           except AttributeError:
              res=None
        else:
           res=int(ev_str)
        
        return res   
    