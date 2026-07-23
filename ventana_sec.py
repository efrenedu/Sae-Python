import customtkinter as ctk
from tkinter import *
import tkinter as tk
from tkinter import ttk
from constantes import *
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter.font import Font
from componentes import Lienzo_dibujo, Labl, TextField, Boton, componente, Internal_Frame
from panel import panel
import requests
import json

class Stadistic_Windows:

    def __init__(self, parent, dim, colors):
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
        self.configure_components()
        self.raiz.deiconify()
        self.raiz.attributes("-topmost", True)
        self.raiz.grab_set()
        self.raiz.focus_force()
        self.raiz.after(10, lambda: self.raiz.attributes("-topmost", False))

    def configure_components(self):
        url = f"{constantes.SERVER}UI_Json/Stadistics_Windows.json"
        response = requests.get(url)
        if response.status_code > 400:
            return
        raw_data = response.content
        from io import BytesIO
        temp_file = BytesIO(raw_data)
        data_json = json.load(temp_file)
        widgets = data_json["Widgets"]
        for element in widgets:
            posicion = element["Posicion"]
            props = element["Propiedades"]
            widget_type = element["Type"]
            self.read_component(posicion, props, widget_type)

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


class Expedent_Windows:

    def __init__(self, parent, dim, colors, data=None):
        self.dim = dim
        self.background = colors[0]
        self.raiz = tk.Toplevel()
        self.raiz.configure(bg=(colors[0]))
        self.parent = parent
        self.raiz.title("Expediente")
        self.comps = []
        self.requireds = {}
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
        self.assign_components(colors, data)
        self.panel.set_active(True)

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
            scrollable = False
            if props["Scroll"] == "True":
                scrollable = True
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

    def assign_components(self, colors, data):
        if data != None:
            self.add_data = data
            if data["Is_Student"] == True:
                self.panel = panel(self.raiz, colors, "")
                url = f"{constantes.SERVER}UI_Json/expediente_students.json"
                response = requests.get(url)
                if response.status_code > 400:
                    return
                raw_data = response.content
                from io import BytesIO
                temp_file = BytesIO(raw_data)
                data_json = json.load(temp_file)
                widgets = data_json["Widgets"]
                for element in widgets:
                    posicion = element["Posicion"]
                    props = element["Propiedades"]
                    widget_type = element["Type"]
                    self.add_expedent_component(posicion, props, widget_type)

                self.requireds["exp_1"] = True
                self.requireds["exp_2"] = True
                self.requireds["exp_3"] = False
                self.requireds["exp_4"] = False
                self.requireds["exp_5"] = True
                self.requireds["exp_6"] = False
                self.requireds["exp_7"] = False
                self.requireds["exp_8"] = False
                self.requireds["exp_f"] = False
                if data["Nuevo_Ingreso"] == constantes.NUEVO_INGRESO_FIRST_YEAR:
                    comp_label = self.panel.get_comp_byName("docs_aprob_label")
                    if comp_label != None:
                        old_text = comp_label.get_text()
                        comp_label.set_text(f"{old_text} * ")
                    self.requireds["exp_3"] = True
                elif data["Nuevo_Ingreso"] == constantes.NUEVO_INGRESO_NO_FIRST_YEAR:
                    self.requireds["exp_4"] = True
                    comp_label = self.panel.get_comp_byName("califics_label")
                    if comp_label != None:
                        old_text = comp_label.get_text()
                        comp_label.set_text(f"{old_text} * ")
            else:
                self.panel = panel(self.raiz, colors, "")
                url = f"{constantes.SERVER}UI_Json/expediente_workers.json"
                response = requests.get(url)
                if response.status_code > 400:
                    return
                raw_data = response.content
                from io import BytesIO
                temp_file = BytesIO(raw_data)
                data_json = json.load(temp_file)
                widgets = data_json["Widgets"]
                for element in widgets:
                    posicion = element["Posicion"]
                    props = element["Propiedades"]
                    widget_type = element["Type"]
                    self.add_expedent_component(posicion, props, widget_type)

                self.requireds["exp_1"] = True
                self.requireds["exp_2"] = True
                self.requireds["exp_3"] = True
                self.requireds["exp_4"] = True
                self.requireds["exp_5"] = True
                self.requireds["exp_6"] = False
                self.requireds["exp_7"] = True
                self.requireds["exp_f"] = False
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

    def on_configure(self, ev):
        if ev.widget == self.raiz:
            w_limit = self.raiz.winfo_width()
            h_limit = self.raiz.winfo_height()
            if w_limit <= 1 or h_limit <= 1:
                return
            self.panel.limit_Internal_panels(w_limit, h_limit)

    def add_event(self, comp):
        if comp.get_id().startswith("boton"):
            comp.boton.configure(command=(lambda: self.open_file(comp.get_id())))
        elif comp.get_id() == "finalizar":
            comp.boton.configure(command=(lambda: self.asignar_expediente()))
        elif comp.get_id() == "cerrar":
            comp.boton.configure(command=(lambda: self.destroy_sec(True)))

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
            data_estud = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_ESTUDIANTE], [self.add_data["cedula"]], ["and"])
            if data_estud != []:
                conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                data_exp = conexion_bd.get_allData(["src_exp"], 1, [constantes.CLAVE_EXPEDIENTE], [data_estud[0][0]], ["and"])
                if data_exp != []:
                    url_zip = constantes.SERVER + data_exp[0][0]
        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
        data_trabaj = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_TRABAJADOR], [self.add_data["cedula"]], ["and"])
        if data_trabaj != []:
            conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
            data_exp = conexion_bd.get_allData(["src_exp"], 1, [constantes.CLAVE_EXPEDIENTE], [data_trabaj[0][0]], ["and"])
            if data_exp != []:
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
                        files_ids[0] = "exp_1"
                    elif linea.startswith("Fondo Blanco"):
                        files_list[1] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[1] = "exp_2"
                    elif linea.startswith("Cuenta Bancaria"):
                        files_list[2] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[2] = "exp_3"
                    elif linea.startswith("fotocopia de la cedula"):
                        files_list[3] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[3] = "exp_4"
                    elif linea.startswith("Hoja de Vida"):
                        files_list[4] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[4] = "exp_5"
                    elif linea.startswith("Ultimo Baucher"):
                        files_list[5] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[5] = "exp_6"
                    elif linea.startswith("Credenciales"):
                        files_list[6] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[6] = "exp_7"
                    elif linea.startswith("foto"):
                        files_list[7] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[7] = "exp_f"
                elif linea.startswith("fotocopia de la cedula"):
                    files_list[0] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[0] = "exp_1"
                elif linea.startswith("copia de la partida de nacimiento"):
                    files_list[1] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[1] = "exp_2"
                elif linea.startswith("Documento de Aprobacion de sexto grado"):
                    files_list[2] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[2] = "exp_3"
                elif linea.startswith("calificaciones certificadas de A??cursados"):
                    files_list[3] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[3] = "exp_4"
                elif linea.startswith("Carta de Residencia"):
                    files_list[4] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[4] = "exp_5"
                elif linea.startswith("Tarjeta de Vacunacion"):
                    files_list[5] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[5] = "exp_6"
                elif linea.startswith("fotocopia de la cedula del representante"):
                    files_list[6] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[6] = "exp_7"
                elif linea.startswith("foto del representante"):
                    files_list[7] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                    files_ids[7] = "exp_8"
                else:
                    if linea.startswith("foto"):
                        files_list[8] = constantes.FOLDER_ZIP + linea_split[1].split("\n")[0]
                        files_ids[8] = "exp_f"

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
                if comp.get_text() != "":
                    target_comps.append(comp)
                if comp.get_id() in self.requireds:
                    if self.requireds[comp.get_id()] == True:
                        General.show_message("faltan documentos del expediente", "documentos insuficinetes")
                        self.raiz.focus_force()
                        return
                if comp.get_id().endswith("f"):
                    dat_temp = []
                    if self.add_data["Panel_Id"] != constantes.PANTALLA_REGISTRO_PERSONAL:
                        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_ESTUDIANTE], [self.add_data["cedula"]], ["and"])
                    else:
                        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_TRABAJADOR], [self.add_data["cedula"]], ["and"])
                    if dat_temp != []:
                        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                        dat_expedent = conexion_bd.get_allData(["src_foto"], 1, [constantes.CLAVE_EXPEDIENTE], [dat_temp[0][0]], ["and"])
                        if dat_expedent != []:
                            val_fot = dat_expedent[0][0]
                            if val_fot.startswith("fotos/"):
                                foto = val_fot

        for i in range(0, len(target_comps)):
            num_files = num_files + 1
            if target_comps[i].get_id().endswith("f"):
                if foto == "":
                    foto = target_comps[i].get_text()
                if foto.endswith(".png") == False:
                    if foto.endswith(".jpg") == False:
                        if foto.endswith(".jpeg") == False:
                            General.show_message("por favor seleccione una foto valida", "foto invalida")
                            self.raiz.focus_force()
                            return
                    dat_temp = []
                    if self.add_data["Panel_Id"] != constantes.PANTALLA_REGISTRO_PERSONAL:
                        conexion_bd.set_tabla(constantes.TABLA_ESTUDIANTE)
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_ESTUDIANTE], [self.add_data["cedula"]], ["and"])
                    else:
                        conexion_bd.set_tabla(constantes.TABLA_TRABAJADOR)
                        dat_temp = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE], 1, [constantes.CLAVE_TRABAJADOR], [self.add_data["cedula"]], ["and"])
                    if dat_temp != [] and foto.startswith("C:/"):
                        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                        data_exps = conexion_bd.get_allData([constantes.CLAVE_EXPEDIENTE, "src_foto"], 2)
                        for dat_expedent in data_exps:
                            if dat_expedent[0] != dat_temp[0][0]:
                                if (dat_expedent[1] != "" and dat_expedent[1] != "...") == True:
                                    src_temp = dat_expedent[1].split("/")[1]
                                    src_fot = foto.split("/")
                                    src_fot = src_fot[len(src_fot) - 1]
                                    if src_fot == src_temp:
                                        General.show_message("la foto ya existe en el servidor,por favor suba una foto con otro nombre", "imagen ya existe en server")
                                        self.raiz.focus_force()
                                        return

                    elif foto.startswith("C:/"):
                        conexion_bd.set_tabla(constantes.TABLA_EXPEDIENTE)
                        data_expe = conexion_bd.get_allData(["src_foto"], 1)
                        if data_expe != []:
                            source1 = foto.split("/")
                            source1 = source1[len(source1) - 1]
                            for dat_expedent in data_expe:
                                source2 = dat_expedent[0].split("/")
                                source2 = source2[len(source2) - 1]
                                if source1 == source2:
                                    General.show_message("la foto ya existe en el servidor,por favor suba una foto con otro nombre", "imagen ya existe en server")
                                    self.raiz.focus_force()
                                    return

            else:
                valor = target_comps[i].get_text()
            if valor.endswith(".pdf") == False:
                if valor.endswith(".doc") == False:
                    if valor.endswith(".docx") == False:
                        if valor.endswith(".xlsx") == False:
                            if valor.endswith(".png") == False:
                                if valor.endswith(".jpg") == False:
                                    if valor.endswith(".jpeg") == False:
                                        General.show_message("por favor seleccione una documento o imagen escaneada del documento valida", "documento invalido")
                                        self.raiz.focus_force()
                                        return
                                    valor = target_comps[i].get_id()
                                    if self.add_data["Panel_Id"] == constantes.PANTALLA_REGISTRO_PERSONAL:
                                        if valor == "exp_1":
                                            files_paths[1] = target_comps[i].get_text()
                                        elif valor == "exp_2":
                                            files_paths[2] = target_comps[i].get_text()
                                        elif valor == "exp_3":
                                            files_paths[3] = target_comps[i].get_text()
                                        elif valor == "exp_4":
                                            files_paths[0] = target_comps[i].get_text()
                                        elif valor == "exp_5":
                                            files_paths[4] = target_comps[i].get_text()
                                        elif valor == "exp_6":
                                            files_paths[5] = target_comps[i].get_text()
                                        elif valor == "exp_7":
                                            files_paths[6] = target_comps[i].get_text()
                                        elif valor == "exp_f":
                                            files_paths[7] = target_comps[i].get_text()
                                    elif valor == "exp_1":
                                        files_expe[3] = "copia de Cedula de Identidad"
                                        files_paths[0] = target_comps[i].get_text()
                                    elif valor == "exp_2":
                                        files_expe[0] = "Copia de Partida de Nacimiento Original"
                                        files_expe[2] = "partida de nacimiento Original"
                                        files_paths[1] = target_comps[i].get_text()
                                    elif valor == "exp_3":
                                        files_expe[5] = "Boleta del periodos escolar anterior de ser neceario"
                                        files_paths[2] = target_comps[i].get_text()
                                    elif valor == "exp_4":
                                        files_expe[4] = "Notas Cerificadas"
                                        files_paths[3] = target_comps[i].get_text()
                                    elif valor == "exp_5":
                                        files_expe[8] = "Carta de Residencia"
                                        files_paths[4] = target_comps[i].get_text()
                                    elif valor == "exp_6":
                                        files_paths[5] = target_comps[i].get_text()
                                    elif valor == "exp_7":
                                        files_expe[7] = "Copia de Cedula"
                                        files_paths[6] = target_comps[i].get_text()
                                    elif valor == "exp_8":
                                        files_expe[6] = "2 Fotos"
                                        files_paths[7] = target_comps[i].get_text()
                                    else:
                                        if valor == "exp_f":
                                            files_expe[1] = "2 fotos del estudiante"
                                            files_paths[8] = target_comps[i].get_text()

        for j in range(0, len(files_paths)):
            if files_paths[j] != None:
                for k in range(0, len(files_paths)):
                    if j != k:
                        if files_paths[k] != None:
                            if files_paths[j] == files_paths[k]:
                                General.show_message("existen archivos repetidos en el expediente", "archivos repetidos")
                                self.raiz.focus_force()
                                return

        if General.show_confirmDialog("construir expediente con estos archivos?", "asignar expediente") != True:
            self.raiz.focus_force()
            return
        from event_manager import Event_manager
        Event_manager.asign_expediente([self.add_data["cedula"], num_files, files_paths, foto, files_expe])
        self.destroy_sec()

    def open_file(self, source):
        from General import General
        res = General.get_fileSource()
        self.raiz.focus_force()
        destino = None
        for i in range(0, len(self.comps)):
            tag = self.comps[i].get_tag()
            if tag == "text":
                if self.comps[i].get_id().endswith(source[len(source) - 1]):
                    destino = self.comps[i]
                    break

        if destino != None:
            if destino.get_tag() == "text":
                destino.set_text(res)

    def destroy_sec(self, delete_zips=False):
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
