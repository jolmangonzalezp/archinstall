import curses
import re
import subprocess

import requests

global get_locale

enter = "\npresione enter para continuar"

################################################################################
##################################### Main #####################################
################################################################################

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.clear()
    stdscr.refresh()    

    menu = ['Locale', 'Disk Partition', 'Salir']
    current_row = 0
    
    while True:
        stdscr.clear()
        stdscr.addstr(1, 3, "Instalacion de Arch Linux...", curses.color_pair(1))
        stdscr.addstr(7, 4, "Selecciona una opción:", curses.color_pair(1))

        for idx, item in enumerate(menu):
            if idx == current_row:
                stdscr.addstr(idx + 3, 0, f"> {item}", curses.color_pair(1))
            else:
                stdscr.addstr(idx + 3, 0, f"  {item}")

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == 'Locale':
                stdscr.clear()
                stdscr.addstr(1, 2, "Definiendo idioma...", curses.color_pair(1))
                get_locale = get_ipapi_data(stdscr)
                set_locale(stdscr, root="")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Disk Partition':
                stdscr.clear()
                stdscr.addstr(1, 2, "Particionando disco...", curses.color_pair(1))
                disk_partitioning(stdscr)
                stdscr.refresh()
                stdscr.getch()
            else:
                break

################################################################################
################################### Messages ###################################
################################################################################

def message(stdscr, message):
    stdscr.addstr(3, 2, message+enter, curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()


################################################################################
######################## Definir idioma y zona horaria #########################
################################################################################

def get_ipapi_data(stdscr): 
    try:
        headers = {
        "User-Agent": "curl/7.68.0"
    } 
        response = requests.get('https://ipapi.co/json/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            locale = data.get("languages")
            return locale
        else:
            message(stdscr, f"Error: Código de estado {response.status_code}")
            return None, None
    except requests.ConnectionError:
        message(stdscr, "Error: No se pudo conectar al servidor.")
        return None, None
    except requests.Timeout:
        message(stdscr, "Error: La solicitud tardó demasiado en completarse.")
        return None, None
    except requests.RequestException as e:
        message(stdscr, f"Error: {e}")
        return None, None
    
def set_locale(stdscr, root=""):
    print("Configurando el teclado y el idioma...")
    locale_gen_path = f"{root}/etc/locale.gen"
    locale_conf_path = f"{root}/etc/locale.conf"
    with open(locale_gen_path, "r") as file:
        lines = file.readlines()  
    updated_lines = [
        re.sub(f"^#{get_locale}.UTF-8", f"{get_locale}.UTF-8", line) for line in lines
    ]
    with open(locale_gen_path, "w") as file:
        file.writelines(updated_lines)
    with open(locale_conf_path, "w") as file:
        file.write(f"LANG={get_locale}.UTF-8")
    subprocess.run(["locale-gen"], check=True)
    subprocess.run(["export", f"LANG={get_locale}.UTF-8"], check=True)
    message(stdscr, "El teclado y el idioma se han configurado correctamente.")

################################################################################
############################## Connect to Internet #############################
################################################################################

def rfkill_unblock(stdscr):
    rfkill_output = subprocess.run(["rfkill", "list"], capture_output=True, text=True).stdout
    device_ids = re.findall(r"^(\d+):", rfkill_output, re.MULTILINE)
    
    for device_id in device_ids:
        soft_blocked = "yes" in subprocess.run(
            ["rfkill", "list", device_id], capture_output=True, text=True
        ).stdout.split("Soft blocked: ")[-1].split("\n")[0]
        
        hard_blocked = "yes" in subprocess.run(
            ["rfkill", "list", device_id], capture_output=True, text=True
        ).stdout.split("Hard blocked: ")[-1].split("\n")[0]
        
        if soft_blocked:
            subprocess.run(["rfkill", "unblock", device_id], check=True)
            message(stdscr, f"Desbloqueado dispositivo con ID {device_id} a nivel de software.")
        if hard_blocked:
            message(stdscr, f"El dispositivo con ID {device_id} está bloqueado a nivel de hardware. No se puede desbloquear automáticamente.")

def connect_to_internet(stdscr):
    try:
        subprocess.run(["ping", "-c1", "8.8.8.8"], check=True, stdout=subprocess.DEVNULL)
        message(stdscr, "Conexión a Internet: OK")
    except subprocess.CalledProcessError:
        message(stdscr, "No hay conexión a Internet. Sigue las instrucciones para conectarte manualmente usando 'iwctl'.\n'device list'\n'station wlan0 scan'\n'station wlan0 get-networks'\n'station wlan0 connect NOMBRE_RED'\n'station wlan0 connect-hidden NOMBRE_RED | En caso de que la red sea oculta'\n\n y por último, exit\n\nPresiona Enter para iniciar el proceso de conexión a Internet.")
        subprocess.run(["iwctl"], check=True)
    
    subprocess.run(["timedatectl", "set-ntp", "true"], check=True)

################################################################################
############################# Disk Partitioning ################################
################################################################################

def disk_partitioning(stdscr):
    disks_output = subprocess.run(["lsblk", "-dno", "NAME,SIZE"], capture_output=True, text=True).stdout
    message(stdscr ,f"Discos disponibles: \n{disks_output}")
    stdscr.addstr(10, 3, "Selecciona el disco a particionar: ", curses.color_pair(1))
    disk_name = stdscr.getstr(12, 3, 7, curses.color_pair(1)).decode("utf-8")
    commands = [
        "g", "n", "1", "", "+512M", "t", "1", "n", "2", "", "", "w"
    ]
    
    process = subprocess.Popen(["fdisk", f"/dev/{disk_name}"], stdin=subprocess.PIPE, text=True)
    process.communicate("\n".join(commands))
    print("Particiones creadas:")
    subprocess.run(["lsblk", f"/dev/{disk_name}"], check=True)

curses.wrapper(main)