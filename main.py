import os
from archinstall.AppsInstall import *
from archinstall.Menu import ConfigMenu

if not os.geteuid():
    print("Bienvenido a PyArchInstall")
    if os.path.exists("/var/lib/pacman/db.lck"):
        print("El archivo existe")
        os.system("sudo rm /var/lib/pacman/db.lck")
    else:
        print("El archivo no existe")
        appsInstall = ConfigMenu()
else:
    print("Vuelve cuando seas root")
    exit()


    