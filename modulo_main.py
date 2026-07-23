from ui import UI
from ventana import ventana
from conexion_bd import*
from General import General
from constantes import constantes
from splash import SplashP

#Modulo Main : Init the System : Data Base, UI,Windows,
def main():
    if(conexion_bd.init()==True):
       vent=ventana("Sae Python")
       UI.init_UI(vent)
       splash=SplashP(vent,{"Width":520,"Height":450})
    else:
      General.show_error("error loading data from server","error")
    return 0



if __name__ == '__main__':
    main()

