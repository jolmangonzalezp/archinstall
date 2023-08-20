import os
from archinstall.AppsInstall import *
from archinstall.Menu import ConfigMenu

if not os.geteuid():
    print("Bienvenido a PyArchInstall")
    if os.path.exists("/var/lib/pacman/db.lck"):
        os.system("sudo rm /var/lib/pacman/db.lck")
    else:
        appsInstall = ConfigMenu()
else:
    print("Vuelve cuando seas root")
    exit()


    