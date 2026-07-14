from tkinter import *
from tkinter import font
import tkinter as tk
from PIL import Image,ImageDraw, ImageFont, ImageTk
import time
from constantes import *
import customtkinter as ctk

#the Splash withe the Logo of Institution to show When the System is Loaded
class SplashP:
    #Build the Window 
    def __init__(self,vent):
        self.w = tk.Toplevel()
        self.vent=vent
        width_of_window = 527
        height_of_window = 450
        screen_width = self.w.winfo_screenwidth()
        screen_height = self.w.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width_of_window / 2)
        y_coordinate = (screen_height / 2) - (height_of_window / 2)
        self.w.geometry("%dx%d+%d+%d" % (width_of_window, height_of_window, x_coordinate, y_coordinate))
        self.w.overrideredirect(1)
        Frame(self.w, width=527, height=450, bg='white').place(x=0, y=0)
        label_welcome = Label(self.w, text='BIENVENIDO(A)', fg='black', bg='white', padx=21, pady=4,)
        label_welcome.configure(font=("Arial", 22,'bold'))
        label_welcome.place(x=140, y=10)
        import requests
        response=requests.get(constantes.SERVER+"images/logo_institucion.png")
        loaded=True
        if(response.status_code>400):
              loaded=False
        self.logo_image = None
        self.logo_photo=None
        if(loaded==True):
           from io import BytesIO
           data=BytesIO(response.content) 
           self.logo_image = Image.open(data)   
        else:
          try:
               self.logo_image = Image.open('logo_institucion.png')
          except:
               self.logo_image=None
               
        #Load and Resize the Logo
        if(self.logo_image!=None):          
            self.logo_image = self.logo_image.resize((200, 200))
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            label_logo = ctk.CTkLabel(self.w, image=self.logo_photo,fg_color="transparent" ,bg_color="transparent")
            label_logo.place(x=180, y=65)  
        label_phone = Label(self.w, text='Teléfono de contacto: 0000-0000000 / 0000-0000000', fg='black', bg='white')
        label_phone.configure(font=("Arial", 13))
        label_phone.place(x=80, y=290)
        label_mail = Label(self.w, text='Correo de contacto: Correo@gmail.com', fg='black', bg='white', padx=17, pady=4)
        label_mail.configure(font=("Arial", 13))
        label_mail.place(x=80, y=315)
        # Build the Button "Continuar/Continue" 
        continue_button = Button(self.w, text="Continuar", command=self.on_continue)
        continue_button.configure(font=("Arial", 13))
        continue_button.pack(pady=180)
        continue_button.place(x=235, y=395)
        self.w.mainloop()

    #Destroy the Splah and Show the Main Windows       
    def on_continue(self):
         self.w.destroy()  
         self.vent.activar()
       