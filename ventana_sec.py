import customtkinter as ctk
from tkinter import *
import tkinter as tk
from tkinter import ttk
from constantes import *
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter.font import Font
from componentes import Lienzo_dibujo, Labl, TextField, Boton, componente, Internal_Frame
from CTkCalendar import CTkCalendar as CTkDatePicker
from panel import panel
import requests
import json
import time

#Stadistic Windows
class Stadistic_Windows:

    def __init__(self, parent, dim, colors,usr):
        self.raiz = ctk.CTkToplevel()
        self.raiz.configure(fg_color=colors)
        self.parent = parent
        self.colors = colors
        self.raiz.title("Estadisticas del Sistema")
        wtotal = self.raiz.winfo_screenwidth()
        htotal = self.raiz.winfo_screenheight()
        pwidth = round(wtotal / 2 - dim["Width"] / 2)
        pheight = round(htotal / 2 - dim["Height"] / 2)
        self.raiz.geometry(str(dim["Width"]) + "x" + str(dim["Height"]) + "+" + str(pwidth) + "+" + str(pheight))
        self.raiz.withdraw()
        if(self.configure_components(usr)==False):
            self.parent.secundaria = None
            self.raiz.destroy()
        else:
           self.raiz.deiconify()
           self.raiz.attributes("-topmost", True)
           self.raiz.grab_set()
           self.raiz.focus_force()
           self.raiz.after(10, lambda: self.raiz.attributes("-topmost", False))

    def configure_components(self,usr):
        if(usr==None):
           General.show_error("usuario invalido","Error")
           return False
        import time
        timestamp=str(int(time.time()))
        data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "target_panel":"Stadistics_Windows"
        }
        from General import General
        url_send=f"{constantes.SERVER}panel_manager.php"
        response=requests.post(url_send,data=data_user)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return False
        elif(json_content["status"]=="Invalid Access" or json_content["status"]=="Invalid Token"):
           General.show_message(json_content["message"],"Alerta")
           return False
        redirect=json_content["Redirect_Panel"] 
        if(redirect!="No Redirect"):
            return False
        data_json=json_content["data"] 
        widgets = data_json["Widgets"]
        for element in widgets:
            posicion = element["Posicion"]
            props = element["Propiedades"]
            widget_type = element["Type"]
            self.read_component(posicion, props, widget_type)
        return True

    def read_component(self, pos, props, widget_type):
        if widget_type == "CanvasStadistics":
            id = props["Id"]
            tag = "canvas"
            dim = props["Dimension"]
            colors = props["Colors"]
            font_sizes = props["Font_Sizes"]
            self.canvas = Lienzo_dibujo(self.raiz, pos, colors, dim, font_sizes, id, tag)
            self.canvas.canvas.pack()
        elif widget_type == "CTkButton":
            text = props["Text"]
            font_data = props["Font"]
            font = ctk.CTkFont(family=(font_data["Name"]), size=(int(font_data["Size"])), weight=(font_data["Style"]))
            colors = props["Colors"]
            id = props["Id"]
            tag = "button"
            default_state = True
            corner_radius = int(props["Corner_Radious"])
            btn = Boton(pos, self.raiz, text, font, colors, id, tag, default_state, corner_radius)
            btn.boton.pack(side=BOTTOM)
            if id == "close":
                btn.boton.configure(command=(self.destroy_win))

    def draw_text(self, pos, font_data, text_color, texto):
        if self.canvas != None:
            self.canvas.draw_text(pos, font_data, text_color, texto)

    def destroy_win(self, delete_zips=False):
        self.parent.secundaria = None
        self.raiz.destroy()

    def clear_canvas(self):
        self.canvas.reset()

    def draw_torta(self, valores, title, labels, label_casos='total de casos'):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        import matplotlib.pyplot as plt
        modo = ctk.get_appearance_mode()
        colors = self.canvas.get_colors()
        size_texts = self.canvas.get_font_Sizes()
        fg_color = ""
        text_color = ""
        title_color = ""
        pie_colors = []
        if modo == "Dark":
            fg_color = colors["Fg"][1]
            text_color = colors["Text"][1]
            pie_colors = colors["Pie_Chart"]["Dark_Mode"]
        else:
            fg_color = colors["Fg"][0]
            text_color = colors["Text"][0]
            pie_colors = colors["Pie_Chart"]["Light_Mode"]
        labels_torta = []
        valores_torta = []
        colors_torta = []
        total = 0
        for i in range(0, len(valores)):
            if int(valores[i]) > 0:
                labels_torta.append(labels[i])
                valores_torta.append(valores[i])
                colors_torta.append(pie_colors[i])
                total = total + int(valores[i])

        self.canvas.canvas.pack_forget()
        self.canvas = None
        frameChartsLT = ctk.CTkFrame((self.raiz), fg_color=(self.colors))
        frameChartsLT.pack()
        fig = Figure()
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(fg_color)
        ax.set_facecolor(fg_color)
        texts_pie = {'color':text_color, 
         'fontsize':size_texts["Labels"],  'weight':"bold"}
        ax.pie(valores_torta, labels=labels_torta, textprops=texts_pie, radius=1.0, colors=colors_torta, autopct="%.0f%%", pctdistance=0.8)
        circle_center = plt.Circle((0, 0), 0.65, fc=fg_color)
        ax.add_artist(circle_center)
        ax.set_title((title.upper()), color=text_color, fontsize=(size_texts["Title"]), fontweight="bold")
        ax.text(0, 0, (label_casos + ":" + str(total)), ha="center", va="center", color=text_color, fontsize=(size_texts["Texts"]))
        chart1 = FigureCanvasTkAgg(fig, frameChartsLT)
        chart1.get_tk_widget().pack()


#Expedent Windows 
class Expedent_Windows:

    def __init__(self, parent, dim, colors,usr, data=None):
        self.dim = dim
        self.background = colors[0]
        self.raiz = tk.Toplevel()
        self.raiz.configure(bg=(colors[0]))
        self.parent = parent
        self.raiz.title("Expediente")
        self.comps = []
        self.requireds = {}
        self.raiz.protocol("WM_DELETE_WINDOW",self.destroy_sec)
       
        wtotal = self.raiz.winfo_screenwidth()
        htotal = self.raiz.winfo_screenheight()
        pwidth = round(wtotal / 2 - dim[0] / 2)
        pheight = round(htotal / 2 - dim[1] / 2)
        self.raiz.geometry(str(dim[0]) + "x" + str(dim[1]) + "+" + str(pwidth) + "+" + str(pheight))
        self.raiz.grid_rowconfigure(0, weight=0)
        self.raiz.grid_rowconfigure(1, weight=1)
        self.raiz.grid_rowconfigure(2, weight=0)
        self.raiz.grid_columnconfigure(0, weight=1)
        self.raiz.bind("<Configure>", self.on_configure)
        if( self.assign_components(colors,usr,data)==False):
           General.show_error("Error Cargando datos de la Pantalla de Expediente","Error de Datos")
           self.parent.secundaria = None
           self.raiz.destroy()
        else:
            self.panel.set_active(True)

    #Add a UI Component
    def add_expedent_component(self, pos, props, widget_type):
        id = props["Id"]
        initial_state = True
        internal_pos = props["Intern_Position"]
        ev = None
        tag = ""
        parent = props["Master"]
        parent_comp = None
        have_master = False
        pos_master = [0, 0]
        pos_comp = [0, 0]
        inter_pos = [0, 0]
        inter_pos = [internal_pos["Row"], internal_pos["Column"]]
        pos_comp = [pos["row"], pos["column"]]
        if parent != "None":
            parent_comp = self.panel.get_comp_byName(parent, False)
        if parent_comp == None:
            parent_comp = self.panel
        else:
            have_master = True
            pos_master = [parent_comp.pos["row"], parent_comp.pos["column"]]
        if type(parent_comp).__name__ == "Internal_Frame":
            if widget_type != "CTkFrame":
                parent_comp = parent_comp.container
        
        if widget_type == "CTkFrame":
            border_color = props["Border_Color"]
            if border_color == "None":
                border_color = None
            colors = {'Fg':props["Color"], 'Border':border_color,  'Scrollbar':props["ScrollBar_Color"],  'Scrollbar_Hover':props["ScrollBar_Hover_Color"]}
            scrollable = props["Scroll"]
            if(scrollable=="True"):
               scrollable="Full"
            corner_radius = int(props["Corner_Radious"])
            frame = Internal_Frame(pos, parent_comp, colors, id, "frame", initial_state, scrollable, ev, corner_radius)
            self.panel.add_comp(frame, id, "frame", have_master, pos_master, pos_comp, inter_pos)
        if widget_type == "CTkLabel":
            tag = "label"
            text = props["Text"]
            colors = {'Fg':props["Fg_Color"],  'Text':props["Text_Color"]}
            font_data = props["Font"]
            font_labl = ctk.CTkFont(family=(font_data["Name"]), size=(int(font_data["Size"])), weight=(font_data["Style"]))
            label = Labl(pos, parent_comp, text, font_labl, colors, id, tag, initial_state, ev)
            self.comps.append(label)
            self.panel.add_comp(label, id, "label", have_master, pos_master, pos_comp, inter_pos)
        elif widget_type == "CTkText_field":
            tag = "text"
            placeholder_text = props["Placeholder_Text"]
            colors = {'Fg':props["Fg_Color"],  'Text':props["Text_Color"],  'Placeholder_Text':props["Placeholder_Text_Color"],  'Fg_Focus':props["Fg_Focus"],  'Text_Focus':props["Text_Focus"],  'Disabled':props["Disabled_Color"],  'Disabled_Text':props["Disabled_TextColor"]}
            if colors["Placeholder_Text"] == "":
                colors["Placeholder_Text"] = "gray"
            corner_radius = int(props["Corner_Radious"])
            font_data = props["Font"]
            font_fld = ctk.CTkFont(family=(font_data["Name"]), size=(int(font_data["Size"])), weight=(font_data["Style"]))
            field = TextField(pos, parent_comp, font_fld, colors, id, tag, initial_state, ev, placeholder_text, corner_radius)
            self.comps.append(field)
            self.panel.add_comp(field, id, "field", have_master, pos_master, pos_comp, inter_pos)
        elif widget_type == "CTkButton":
            tag = "button"
            text = props["Text"]
            colors = props["Colors"]
            corner_radius = int(props["Corner_Radious"])
            font_data = props["Font"]
            font_btn = ctk.CTkFont(family=(font_data["Name"]), size=(int(font_data["Size"])), weight=(font_data["Style"]))
            btn = Boton(pos, parent_comp, text, font_btn, colors, id, tag, initial_state, corner_radius)
            self.comps.append(btn)
            self.panel.add_comp(btn, id, "button", have_master, pos_master, pos_comp, inter_pos)

    #Build the Components of the Windows
    def assign_components(self, colors,usr, data):
        if(data==None or usr==None):
           return False
        import time
        target_panel=""
        if(data["Is_Student"] ==True):
            target_panel="expediente_students"
        else:
            target_panel="expediente_workers"
        timestamp=str(int(time.time()))
        data_user={
          "token":usr.get_credentials()[4],
          "timestamp":timestamp,
          "target_panel":target_panel
        }
        from General import General
        url_send=f"{constantes.SERVER}panel_manager.php"
        response=requests.post(url_send,data=data_user)
        json_content=json.loads(response.content)
        if(json_content["status"]=="Error"):
            General.show_error(json_content["message"],"Error")
            return False
        elif(json_content["status"]=="Invalid Access" or json_content["status"]=="Invalid Token"):
           General.show_message(json_content["message"],"Alerta")
           return False
        redirect=json_content["Redirect_Panel"] 
        if(redirect!="No Redirect"):
            return False
        data_json=json_content["data"] 
        self.panel = panel(self.raiz, colors, "")
        widgets = data_json["Widgets"]
        for element in widgets:
            posicion = element["Posicion"]
            props = element["Propiedades"]
            widget_type = element["Type"]
            self.add_expedent_component(posicion, props, widget_type)

        self.add_data = data
        if data["Is_Student"] == True:
            self.requireds["fotocopia"] = True
            self.requireds["partid_nac"] = True
            self.requireds["docs_aprob"] = False
            self.requireds["califics"] = False
            self.requireds["carta_resid"] = True
            self.requireds["vacunacion"] = False
            self.requireds["fotocopia_repres"] = False
            self.requireds["foto_repres"] = False
            self.requireds["foto"] = False
            if data["Nuevo_Ingreso"] == constantes.NUEVO_INGRESO_FIRST_YEAR:
               comp_label = self.panel.get_comp_byName("docs_aprob_label")
               if comp_label != None:
                   old_text = comp_label.get_text()
                   comp_label.set_text(f"{old_text} * ")
               self.requireds["docs_aprob"] = True
            elif data["Nuevo_Ingreso"] == constantes.NUEVO_INGRESO_NO_FIRST_YEAR:
                self.requireds["califics"] = True
                comp_label = self.panel.get_comp_byName("califics_label")
                if comp_label != None:
                    old_text = comp_label.get_text()
                    comp_label.set_text(f"{old_text} * ")
        else:
            self.requireds["Fondo_Negro"] = True
            self.requireds["Fondo_Blanco"] = True
            self.requireds["cuenta_bank"] = True
            self.requireds["fotocopia_ced"] = True
            self.requireds["sintesis"] = True
            self.requireds["Boucher"] = False
            self.requireds["credenciales"] = True
            self.requireds["foto"] = False
        self.raiz.update_idletasks()
        self.raiz.event_generate("<Configure>")
        from event_manager import Event_manager
        for j in range(0, len(self.comps)):
            self.comps[j].set_active(True)
            tag = self.comps[j].get_tag()
            if tag == "button":
               self.add_event(self.comps[j])
            if tag == "text":
               self.comps[j].On_load()
        try:
            self.asignar_old_files_expediente()
        except:
            General.show_error("fallo al leer el expediente de la bd , por favor intentelo de nuevo", "error de lectura")
            self.destroy_sec(True)
        return True
        
    #Event On Configure    
    def on_configure(self, ev):
        if ev.widget == self.raiz:
            w_limit = self.raiz.winfo_width()
            h_limit = self.raiz.winfo_height()
            if w_limit <= 1 or h_limit <= 1:
                return
            self.panel.limit_Internal_panels(w_limit, h_limit)

    #Add Events to the Buttons of Expedent Windows
    def add_event(self, comp):
        if comp.get_id().startswith("boton"):
            comp.boton.configure(command=(lambda: self.open_file(comp.get_id())))
        elif comp.get_id() == "finalizar":
            comp.boton.configure(command=(lambda: self.asignar_expediente()))
        elif comp.get_id() == "cerrar":
            comp.boton.configure(command=(lambda: self.destroy_sec(True)))

    #Verify if exist old Expedent On Bd and Assign files Values to the fields components
    def asignar_old_files_expediente(self):
        from conexion_bd import conexion_bd
        import requests
        if sys.version_info >= (3, 7):
            import zipfile
        else:
            import zipfile37 as zipfile
        url_zip = ""
        if self.add_data["Is_Student"] == True:
            conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
            cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[self.add_data["cedula"]],"conditions_Verify":["="]}              
            data_estud = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], cond_data)
            if(len(data_estud)<=0):
               return
            conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
            cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[data_estud[0][0]],"conditions_Verify":["="]}              
            data_exp = conexion_bd.get_allData(["src_exp"], cond_data)
            if(len(data_exp)<=0):
               return
            url_zip = constantes.SERVER + data_exp[0][0]
        else:
           conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
           cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[self.add_data["cedula"]],"conditions_Verify":["="]}              
           data_trabaj = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], cond_data)
           if(len(data_trabaj)<=0):
              return
           conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
           cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[data_trabaj[0][0]],"conditions_Verify":["="]}              
           data_exp = conexion_bd.get_allData(["src_exp"], cond_data)
           if (len(data_exp)<=0):
               return
           url_zip = constantes.SERVER + data_exp[0][0]
        if url_zip == "" or url_zip.endswith(".zip") == False:
           return
        response = requests.get(url_zip)
        if response.status_code > 400:
           return
        raw_data = response.content
        direccion = constantes.FOLDER_DOCUMENTS + self.add_data["cedula"] + ".zip"
        file_val = open(direccion, "wb")
        file_val.write(raw_data)
        file_val.close()
        dir_extraccion = constantes.FOLDER_ZIP
        Zip = zipfile.ZipFile(direccion, "r")
        Zip.extractall(dir_extraccion)
        Zip.close()
        file_info = open(dir_extraccion + "info.txt", "r")
        files_list = ["","","","","","","","",""]
        files_ids = ["","","","","","","","",""]
        for linea in file_info:
            linea_split = linea.split(":")
            if self.add_data["Panel_Id"] == constantes.PANTALLA_REGISTRO_PERSONAL:
                if linea.startswith("Fondo Negro"):
                      files_list[0] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[0] = "Fondo_Negro"
                elif linea.startswith("Fondo Blanco"):
                      files_list[1] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[1] = "Fondo_Blanco"
                elif linea.startswith("Cuenta Bancaria"):
                      files_list[2] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[2] = "cuenta_bank"
                elif linea.startswith("fotocopia de la cedula"):
                      files_list[3] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[3] = "fotocopia_ced"
                elif linea.startswith("sintesis"):
                      files_list[4] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[4] = "sintesis"
                elif linea.startswith("Ultimo Baucher"):
                      files_list[5] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[5] = "Boucher"
                elif linea.startswith("Credenciales"):
                      files_list[6] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[6] = "credenciales"
                elif linea.startswith("foto"):
                      files_list[7] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[7] = "foto"
            else:

                if linea.startswith("fotocopia de la cedula"):
                      files_list[0] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[0] = "fotocopia"
                elif linea.startswith("copia de la partida de nacimiento"):
                      files_list[1] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[1] = "partid_nac"
                elif linea.startswith("Documento de Aprobacion de sexto grado"):
                      files_list[2] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[2] = "docs_aprob"
                elif linea.startswith("calificaciones certificadas de A??cursados"):
                      files_list[3] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[3] = "califics"
                elif linea.startswith("Carta de Residencia"):
                      files_list[4] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[4] = "carta_resid"
                elif linea.startswith("Tarjeta de Vacunacion"):
                      files_list[5] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[5] = "vacunacion"
                elif linea.startswith("fotocopia de la cedula del representante"):
                      files_list[6] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[6] = "fotocopia_repres"
                elif linea.startswith("foto del representante"):
                      files_list[7] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                      files_ids[7] = "foto_repres"
                elif linea.startswith("foto"):
                          files_list[8] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                          files_ids[8] = "foto"

        file_info.close()
        from event_manager import Event_manager
        data_old = []
        for i in range(0, len(files_list)):
             if files_list[i] != "":
                data_old.append([files_ids[i], files_list[i]])

        for dat in data_old:
            for j in range(0, len(self.comps)):
                if self.comps[j].get_id() == dat[0]:
                    self.comps[j].set_text(dat[1])

    def asignar_expediente(self):
        from General import General
        from conexion_bd import conexion_bd
        num_files = 0
        files_paths = [None,None,None,None,None,None,None,None,None]
        foto = ""
        files_expe = [False,False,False,False,False,False,False,False,False]
        target_comps = []
        for comp in self.comps:
            if comp.get_tag() == "text":
                if((comp.get_id() in self.requireds)==False):
                     General.show_message("Error:Existen Campos de Textos con Ids Invalidas","Error")
                     return
                valor=comp.get_text() 
                required=self.requireds[comp.get_id()]              
                
                if(required):
                    if(valor==""):
                           General.show_message("faltan documentos del expediente", "documentos insuficinetes")
                           self.raiz.focus_force()
                           return
                    valid_file=False               
                    available_formats=[".pdf",".doc",".docx",".xlsx",".png",".jpg",".jpeg"]
                    for available in available_formats:
                       if(valor.endswith(available)):
                           valid_file=True
                           break
                    if valid_file == False:
                        General.show_message("por favor seleccione una documento o imagen escaneada del documento valida", "documento invalido")
                        self.raiz.focus_force()
                        return  
                target_comps.append(comp)
                if comp.get_id().endswith("foto"):
                    #Try to Get the Photo Value of Data Base
                    dat_temp = []
                    if self.add_data["Panel_Id"] != constantes.PANTALLA_REGISTRO_PERSONAL:
                        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                        cond_data={"conditions_Names":[constantes.CLAVE_ESTUDIANTE],"condition_Types":["and"],"conditions_Values":[self.add_data["cedula"]],"conditions_Verify":["="]}              
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], cond_data)
                    else:
                        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                        cond_data={"conditions_Names":[constantes.CLAVE_TRABAJADOR],"condition_Types":["and"],"conditions_Values":[self.add_data["cedula"]],"conditions_Verify":["="]}              
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], cond_data)
                    if (dat_temp == []):
                        continue
                    conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                    cond_data={"conditions_Names":[constantes.CLAVE_EXPEDIENTE],"condition_Types":["and"],"conditions_Values":[dat_temp[0][0]],"conditions_Verify":["="]}              
                    dat_expedent = conexion_bd.get_allData(["src_foto"], cond_data)
                    if(dat_expedent==[]):
                       continue                    
                    val_fot = dat_expedent[0][0]
                    if val_fot.startswith("fotos/"):
                          foto = val_fot

        for i in range(0, len(target_comps)):
            num_files = num_files + 1
            valor_id = target_comps[i].get_id()
            valor_path=target_comps[i].get_text()
            if (valor_id.endswith("foto") and valor_path!=""):
                 foto = valor_path
            
            if(valor_path==""):
                valor_path=None
            if self.add_data["Panel_Id"] == constantes.PANTALLA_REGISTRO_PERSONAL:
                if valor_id == "Fondo_Negro":
                    files_paths[1] =valor_path
                elif valor_id == "Fondo_Blanco":
                    files_paths[2] = valor_path
                elif valor_id == "cuenta_bank":
                    files_paths[3] = valor_path
                elif valor_id == "fotocopia_ced":
                    files_paths[0] =valor_path
                elif valor_id == "sintesis":
                    files_paths[4] = valor_path
                elif valor_id == "Boucher":
                    files_paths[5] = valor_path
                elif valor_id == "credenciales":
                    files_paths[6] = valor_path
                elif valor_id == "foto":
                    files_paths[7] = valor_path
            else:                  
                if valor_id == "fotocopia":
                    files_expe[3] = "copia de Cedula de Identidad"
                    files_paths[0] = valor_path
                elif valor_id == "partid_nac":
                    files_expe[0] = "Copia de Partida de Nacimiento Original"
                    files_expe[2] = "partida de nacimiento Original"
                    files_paths[1] = valor_path
                elif valor_id == "docs_aprob":
                    files_expe[5] = "Boleta del periodos escolar anterior de ser neceario"
                    files_paths[2] = valor_path
                elif valor_id == "califics":
                    files_expe[4] = "Notas Cerificadas"
                    files_paths[3] = valor_path
                elif valor_id == "carta_resid":
                    files_expe[8] = "Carta de Residencia"
                    files_paths[4] = valor_path
                elif valor_id == "vacunacion":
                    files_paths[5] = valor_path
                elif valor_id == "fotocopia_repres":
                    files_expe[7] = "Copia de Cedula"
                    files_paths[6] = valor_path
                elif valor_id == "foto_repres":
                    files_expe[6] = "2 Fotos"
                    files_paths[7] = valor_path
                elif valor_id == "foto":
                    files_expe[1] = "2 fotos del estudiante"
                    files_paths[8] = valor_path

        for j in range(0, len(files_paths)):
            if files_paths[j] == None:
               continue
            for k in range(0, len(files_paths)):
                if(j==k):
                   break
                if files_paths[k] == None:
                    continue
                if files_paths[j] == files_paths[k]:
                    General.show_message("existen archivos repetidos en el expediente", "archivos repetidos")
                    self.raiz.focus_force()
                    return

        if General.show_confirmDialog("construir expediente con estos archivos?", "asignar expediente") != True:
            self.raiz.focus_force()
            return
        from event_manager import Event_manager
        Event_manager.assign_expediente([self.add_data["cedula"], num_files, files_paths, foto, files_expe])
        self.destroy_sec()

    #Assign the Path of a File to the Correct Field
    def open_file(self, source):
        from General import General
        res = General.get_fileSource()
        self.raiz.focus_force()
        destino = None
        target_name=source.split("boton_")
        if(len(target_name)<2):
           return
        target_name=target_name[1]
        for i in range(0, len(self.comps)):
            tag = self.comps[i].get_tag()
            if tag == "text":
               
                if (self.comps[i].get_id()==target_name):
                    destino = self.comps[i]
                    break
        if destino != None:
            if destino.get_tag() == "text":
                destino.set_text(res)

    #Destroy the Windows
    def destroy_sec(self, delete_zips=False):
        self.panel.free_Memory()
        self.parent.secundaria = None
        self.raiz.destroy()
        if delete_zips == True:
            import threading
            from event_manager import Event_manager
            thread = threading.Thread(target=(Event_manager.reset_zip_files))
            thread.start()


class Frame_Loading:

    def __init__(self, root, fg_color, msg, text_size,text_color):
        self.frame = ctk.CTkFrame(root, fg_color=fg_color)
        font=ctk.CTkFont(family="Arial",size=text_size,weight="bold")
        self.frame.grid_columnconfigure(0,weight=1)
        self.frame.grid_rowconfigure(0,weight=1)
        self.label=ctk.CTkLabel(self.frame,text=msg,text_color=text_color,font=font,fg_color="transparent")
        self.label.grid(row=0,column=0,sticky="nsew")

    def show_frame(self):
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame.lift()

    def hide_frame(self):
        self.frame.place_forget()

class Date_Windows:   
    def __init__(self, root, colors,initial_size,corner_radius):
        self.colors=colors
        self.date_container=ctk.CTkToplevel()
        self.date_container.configure(fg_color=colors["Fg"])
        self.date_container.geometry("%dx%d+%d+%d" % (initial_size[0],initial_size[1], 0, 0))
        self.date_container.transient(root)
        self.date_container.overrideredirect(1)
        self.date_container.attributes("-topmost",True)
        self.frame_container=ctk.CTkFrame(self.date_container,fg_color=colors["Fg"])
        self.frame_container.pack()
        values_years=[]
        local_tm=time.localtime(time.time())
        end_year=local_tm.tm_year 
        start_year=end_year-120
        count_years=0

        for i in range(start_year,end_year):
           values_years.append(str(end_year-count_years))
           count_years=count_years+1
        self.list_years=ctk.CTkOptionMenu(self.frame_container,values=values_years,command=self.set_year)
        self.list_years.set(values_years[0])
        self.list_years.pack()
        self.comp_required=None
        self.date_pick=CTkDatePicker(self.frame_container, fg_color=self.colors["Fg"],corner_radius=corner_radius)
        self.date_pick.pack()
        self.date_container.update_idletasks()
        self.dim_date=(self.frame_container.winfo_reqwidth(),self.frame_container.winfo_reqheight())
        self.date_container.withdraw()
        self.prepare_navigators(self.date_pick)
        self.link_buttons(self.date_pick)
        self.list_years._canvas.bind("<ButtonPress-1>",self.automatic_Scroll,add="+")
   
         
    #Automatic Scroll When Mouse Button is Pressed
    def automatic_Scroll(self,event):
       pos_y=event.y
       h_canvas=self.list_years._canvas.winfo_height()
       dir=0
       if(pos_y<(h_canvas*0.15)):
          dir=1
       elif(pos_y>(h_canvas*0.85)):
          dir=-1
       else:
         return
       self.list_years._canvas.yview_scroll(dir,"units")
       
    #Calendar Change of Month or Year    
    def on_change(self,initiaL_command):
       if(initiaL_command):
           initiaL_command()
       self.date_container.after(30,lambda:self.link_buttons(self.date_pick))
    
    #Link Navegation Buttons to Re Call Link_buttons Fuction
    def prepare_navigators(self,widget):
        for child in widget.winfo_children():
           if(isinstance(child,(ctk.CTkButton))):
               text=child.cget("text")
               if not (text.isdigit() and 1<=int(text)<=31):
                  initial_command=child.cget("command")
                  child.configure(command=lambda cmd=initial_command: self.on_change(cmd))
           if(child.winfo_children()):
               self.prepare_navigators(child)
    
    #Link Events to the Calendar Days Buttons    
    def link_buttons(self,widget):
       for child in widget.winfo_children():
           if(isinstance(child,(ctk.CTkButton,ctk.CTkLabel))):
               text=child.cget("text")
               if(text and text.isdigit() and 1<=int(text)<=31):
                   child.bind("<Button-1>",lambda event, btn=child:self.set_date_field(btn),add="+")
           if(child.winfo_children()):
               self.link_buttons(child)
               
    #Set the date On the Required Text Field           
    def set_date_field(self,btn):
       day=str(btn.cget("text")).zfill(2)
       month=str(self.date_pick.current_month).zfill(2)
       year=str(self.date_pick.current_year).zfill(2)
       if(self.comp_required!=None):
          self.comp_required.set_text(f"{day}/{month}/{year}")
          self.comp_required.field.master.focus()
       self.date_container.after(50,self.date_container.withdraw)
       
    #Click Event On Windows
    def On_Click(self,event):
       if(self.date_container==None or self.comp_required==None):
          return
       if not self.date_container.winfo_viewable(): 
          return
       clickx=event.widget.winfo_pointerx()
       clicky=event.widget.winfo_pointery()
       topx1=self.date_container.winfo_rootx()
       topx2=topx1+self.date_container.winfo_width()
       topy1=self.date_container.winfo_rooty()
       topy2=topy1+self.date_container.winfo_height()
       
       field=self.comp_required.field
       fldx1=field.winfo_rootx()
       fldx2=fldx1+field.winfo_width()
       fldy1=field.winfo_rooty()
       fldy2=fldy1+field.winfo_height()
       
       on_top=(topx1<=clickx <=topx2) and (topy1<=clicky<=topy2)
       on_entry=(fldx1<=clickx<=fldx2) and (fldy1<=clicky<=fldy2)
       if not on_top and not on_entry:
         event.widget.focus_force()
         self.date_container.withdraw()
         
    #Set the Year 
    def set_year(self,year_selected):
       year=int(year_selected)
       self.date_pick.current_year=year
       self.date_pick.update_month_year()
       self.date_pick._draw()
       self.date_pick.update_idletasks()
       self.prepare_navigators(self.date_pick)
       self.link_buttons(self.date_pick)
       
    def show_Windows(self,comp_required):
        self.comp_required=comp_required
        field=comp_required.field
        x=field.winfo_rootx()
        y=field.winfo_rooty()
        h=field.winfo_height()
        w=field.winfo_width()
        y=y+h
        h_container=self.dim_date[0]+70
        w_container=self.dim_date[1]
        self.date_container.geometry(f"{w_container}x{h_container}+{x}+{y}")
        self.date_container.deiconify()


    def hide_Windows(self,force_focus=False):
        if(self.comp_required!=None and force_focus):
           self.comp_required.field.master.focus_force()
           self.comp_required=None
        self.date_container.withdraw()
        
    #Destroy Component and Free Memory  
    def free_Memory(self):
          self.date_pick.pack_forget()
          self.date_pick.destroy()
          self.frame_container.pack_forget()
          self.frame_container.destroy()
          self.date_container.destroy()
          self.date_container=None
          