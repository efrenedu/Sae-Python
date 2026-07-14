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
       from ventana_sec import ventana_splash
       splsh=ventana_splash(vent,[500,500],["#6C39B7","white"],["Arial","bold",25],3000)       
       UI.init_UI(vent,splsh)
       splsh.destroy_splash()
       sp=SplashP(vent)
    else:
      General.show_error("error loading data from server","error")
    return 0



if __name__ == '__main__':
    main()

