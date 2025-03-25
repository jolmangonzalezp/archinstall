import curses
import os
import re
import subprocess

import pexpect
import requests

data = ""
disk_name = ""
efi = ""
root_partition = ""
locale = ""
timezone = ""
hostname = ""

enter = "\npresione enter para continuar"

################################################################################
##################################### Main #####################################
################################################################################

def main(stdscr):
    global data
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.clear()
    data = get_ipapi_data(stdscr)
    set_locale(stdscr, root="")
    stdscr.refresh()    

    menu = ['Particionar el disco', 'Formatear', 'Encriptar', 'Particionar BTRFS', 'Montar particiones', 'Memoria de intercambio', 'Install el sistema', 'Salir']
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
            if menu[current_row] == 'Particionar el disco':
                stdscr.clear()
                disk_partitioning(stdscr)
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Formatear':
                stdscr.clear()
                format_disk(stdscr)
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Encriptar':
                stdscr.clear()
                encrypt_disk(stdscr)
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Particionar BTRFS':
                stdscr.clear()
                btrfs_partitioning(stdscr)
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Montar particiones':
                stdscr.clear()
                mount_partitions()
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Memoria de intercambio':
                stdscr.clear()
                swap(stdscr)
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Install el sistema':
                stdscr.clear()
                install(stdscr)
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
            return data
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
    global data
    env = os.environ.copy()
    env["LANG"] = f"{data['languages']}.UTF-8"
    print("Configurando el teclado y el idioma...")
    locale_gen_path = f"{root}/etc/locale.gen"
    locale_conf_path = f"{root}/etc/locale.conf"
    with open(locale_gen_path, "r") as file:
        lines = file.readlines()  
    updated_lines = [
        re.sub(f"^#{data['languages']}.UTF-8 UFT-8", f"{data['languages']}.UTF-8 UTF-8", line) for line in lines
    ]
    with open(locale_gen_path, "w") as file:
        file.writelines(updated_lines)
    with open(locale_conf_path, "w") as file:
        file.write(f"LANG={data['languages']}.UTF-8")
    subprocess.run(["locale-gen"], check=True)
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
    global disk_name
    disks_output = subprocess.run(["lsblk", "-dno", "NAME,SIZE"], capture_output = True, text = True).stdout
    stdscr.addstr(3, 2, f"Discos disponibles: \n{disks_output}", curses.color_pair(1))
    stdscr.addstr(10, 3, "Selecciona el disco a particionar: ", curses.color_pair(1))
    curses.curs_set(1)
    stdscr.refresh()
    
    ## I have to validate the disk name
    disk_name = stdscr.getstr(12, 3, 7).decode("utf-8")
    stdscr.addstr(13, 3, f"Has escrito: {disk_name}")
    stdscr.refresh()
    ##
    message(stdscr, "")
    stdscr.getch()
    commands = [
        "g", "n", "1", "", "+512M", "t", "1", "n", "2", "", "", "w"
    ]
    process = subprocess.Popen(["fdisk", f"/dev/{disk_name}"], stdin=subprocess.PIPE, text=True)
    process.communicate("\n".join(commands))
    stdscr.addstr(10, 3, "Particiones creadas:", curses.color_pair(1))
    subprocess.run(["lsblk", f"/dev/{disk_name}"], check=True)

################################################################################
################################## Formatting ##################################
################################################################################

def format_disk(stdscr):
    global efi, root_partition, disk_name
    interface = ""
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,TRAN"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith(disk_name + " "):
                interface = line.split()[1]

        if "sata" in interface:
            efi = f"{disk_name}1"
            root_partition = f"{disk_name}2"
        elif "nvme" in interface:
            efi = f"{disk_name}p1"
            root_partition = f"{disk_name}p2"
            print(f"Interfaz de {disk_name}: {interface}")
        else:
            print(f"No se pudo determinar la interfaz de {disk_name}.")
            
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar lsblk: {e}")
        interface = None
    except Exception as e:
        print(f"Error inesperado: {e}")
        interface = None
    
    
    subprocess.run(["mkfs.fat", "-F32", f"/dev/{efi}"], check=True)

################################################################################
############################# Encrypting ######################################
################################################################################

def encrypt_disk(stdscr):
    global root_partition, disk_name
    stdscr.addstr(10, 3, "Encriptando el disco...", curses.color_pair(1))
    try:
        subprocess.run(["cryptsetup", "erase", f"/dev/{root_partition}"], check=True)
    except subprocess.CalledProcessError as e:
        message(stdscr, f"No se pudo limpiar el disco. {e}")
    stdscr.addstr(11, 3, "Ingrese la contraseña LUKS:", curses.color_pair(1))
    luks_pass = stdscr.getstr(12, 3).decode("utf-8")
    stdscr.addstr(11, 3, "Compruebe la contraseña LUKS:", curses.color_pair(1))
    luks_pass_confirm = stdscr.getstr(12, 3).decode("utf-8")
    
    if luks_pass != luks_pass_confirm:
        message(stdscr, "Error: Las contraseñas no coinciden.")
    else:
        message(stdscr, f"Contraseña LUKS correcta. La constraseña LUKS es: {luks_pass}\n\tIniciando encriptación...")

    try:
        # Comando para ejecutar
        command = f"cryptsetup -y -v luksFormat --type luks2 --force-password /dev/{root_partition}"
        process = pexpect.spawn(command)
        # Manejar las interacciones del proceso
        process.expect("Are you sure\\? .*YES.*:")
        process.sendline("YES")  # Responder "YES" a la advertencia
        process.expect("Enter passphrase for .*:")
        process.sendline(luks_pass)  # Enviar la contraseña
        process.expect("Verify passphrase:")
        process.sendline(luks_pass)  # Confirmar la contraseña

        # Esperar a que termine el comando
        process.wait()
        print(f"El disco /dev/{root_partition} fue cifrado exitosamente.")

    except pexpect.EOF:
        print(f"Comando terminado inesperadamente: {process.before.decode().strip()}")
    except pexpect.ExceptionPexpect as e:
        message( f"Error al ejecutar el comando: {e}")

    # subprocess.run(["cryptsetup", "-y", "-v", "luksFormat", "--type", "luks2", "--force-password", f"/dev/{root_partition}"], input=f"YES\n{luks_pass}\n{luks_pass}", text=True, check=True )
    subprocess.run(["cryptsetup", "luksOpen", f"/dev/{root_partition}","root"], input=luks_pass, text=True, check=True)
    root_partition = "/dev/mapper/root"

def btrfs_partitioning(stdscr):
    global root_partition
    stdscr.addstr(10, 3, "Particiones BTRFS:", curses.color_pair(1))
    subprocess.run(["mkfs.btrfs", root_partition], check=True)
    os.makedirs("/mnt", exist_ok=True)
    subprocess.run(["mount", root_partition, "/mnt"], check=True)
    
    for subvolume in ["@", "@home", "@snapshots", "@var_log", "@swap"]:
        subprocess.run(["btrfs", "subvolume", "create", f"/mnt/{subvolume}"], check=True)

def mount_partitions():
    global root_partition, efi
    subprocess.run(["umount", "/mnt"], check=True)
    mount_options = "noatime,compress=zstd,space_cache=v2"
    subvolumes = ["@", "@home", "@snapshots", "@var_log", "@swap"]
    mount_points = ["", "home", "snapshots", "var/log", "swap"]

    for point in mount_points:
        os.makedirs(f"/mnt/{point}", exist_ok=True)

    for subvolume, point in zip(subvolumes, mount_points):
        subprocess.run(["mount", "-o", f"{mount_options},subvol={subvolume}", root_partition, f"/mnt/{point}"], check=True)

    os.makedirs("/mnt/boot", exist_ok=True)
    subprocess.run(["mount", f"/dev/{efi}", "/mnt/boot"], check=True)
    print("Particiones montadas.")

def swap(stdscr):
    global root_partition
    swap_size = ""
    size = subprocess.run(
        ["awk", "/MemTotal/ {print $2/1024}", "/proc/meminfo"], 
        capture_output=True, 
        text=True
    ).stdout.strip()
    size = float(size)
    if size > 8192:
        swap_size = (size/2)*1024
    elif size <= 8192 and size > 2048:
        swap_size = size*1024
    else:
        swap_size = size*2

    subprocess.run(
        ["btrfs", "filesystem", "mkswapfile", "--size", f"{swap_size}M", "--uuid", "clear", "./swapfile"],
        check=True
    )
    message(stdscr , f"Archivo de swap creado con tamaño {swap_size} MB.")
    subprocess.run(["swapon", "./swapfile"], check=True)

def install(stdscr):
    cpu_brand = ""
    result = subprocess.run(
        ["lscpu"], capture_output=True, text=True, check=True
    )
    # Filtrar la línea con "Vendor ID:" y extraer la tercera columna
    for line in result.stdout.splitlines():
        if "Vendor ID:" in line:
            cpu_brand = line.split()[2]
    packages = []
    if cpu_brand == "AuthenticAMD":
        packages = [
        "base", "base-devel", "linux-zen", "linux-zen-headers", "linux-firmware", "btrfs-progs", "efibootmgr", "grub", "grub-btrfs", "os-prober", "networkmanager", "openssh", "sudo","dhcpcd", "zsh", "zsh-completions", "vim", "git", "curl", "wget", "man-db", "man-pages", "dosfstools", "e2fsprogs", "exfat-utils", "ntfs-3g", "smartmontools", "dialog", "man-db", "man-pages", "texinfo", "pacman-contrib", "snapper", "xdg-user-dirs", "xdg-utils", "tlp", "reflector", "neofetch", "amd-ucode", "inotify-tools", "pipewire", "pipewire-alsa", "pipewire-pulse", "pipewire-jack", "zsh-autosuggestions", "zsh-syntax-highlighting", "net-tools", "ifplugd", "iw", "wireless_tools", "wpa_supplicant", "dialog", "wireless-regdb", "bluez", "bluez-alsa", "bluez-cups", "bluez-firmware", "bluez-utils"
        ]
    elif cpu_brand == "GenuineIntel":
        packages = [
        "base", "base-devel", "linux-zen", "linux-zen-headers", "linux-firmware", "btrfs-progs", "efibootmgr", "grub", "grub-btrfs", "os-prober", "networkmanager", "openssh", "sudo","dhcpcd", "zsh", "zsh-completions", "vim", "git", "curl", "wget", "man-db", "man-pages", "dosfstools", "e2fsprogs", "exfat-utils", "ntfs-3g", "smartmontools", "dialog", "man-db", "man-pages", "texinfo", "pacman-contrib", "snapper", "xdg-user-dirs", "xdg-utils", "tlp", "reflector", "neofetch", "intel-ucode", "inotify-tools", "pipewire", "pipewire-alsa", "pipewire-pulse", "pipewire-jack", "zsh-autosuggestions", "zsh-syntax-highlighting", "net-tools", "ifplugd", "iw", "wireless_tools", "wpa_supplicant", "dialog", "wireless-regdb", "bluez", "bluez-alsa", "bluez-cups", "bluez-firmware", "bluez-utils"
        ]
    else:
        packages = [
        "base", "base-devel", "linux-zen", "linux-zen-headers", "linux-firmware", "btrfs-progs", "efibootmgr", "grub", "grub-btrfs", "os-prober", "networkmanager", "openssh", "sudo","dhcpcd", "zsh", "zsh-completions", "vim", "git", "curl", "wget", "man-db", "man-pages", "dosfstools", "e2fsprogs", "exfat-utils", "ntfs-3g", "smartmontools", "dialog", "man-db", "man-pages", "texinfo", "pacman-contrib", "snapper", "xdg-user-dirs", "xdg-utils", "tlp", "reflector", "neofetch", "amd-ucode", "intel-ucode", "inotify-tools", "pipewire", "pipewire-alsa", "pipewire-pulse", "pipewire-jack", "zsh-autosuggestions", "zsh-syntax-highlighting", "net-tools", "ifplugd", "iw", "wireless_tools", "wpa_supplicant", "dialog", "wireless-regdb", "bluez", "bluez-alsa", "bluez-cups", "bluez-firmware", "bluez-utils"
        ]

    try:
        subprocess.run(
            ["pacstrap", "/mnt"] + packages,
            check=True
        )
        message(stdscr, "Sistema base instalado correctamente.")
    except subprocess.CalledProcessError as e:
        message(stdscr, f"Error al ejecutar pacstrap: {e}")
    except Exception as e:
        message(stdscr, f"Error inesperado: {e}")
    
   
    

curses.wrapper(main)


# subprocess.run(["systemctl", "enable", "systemd-networkd"], check=True)
#     subprocess.run(["systemctl", "enable", "systemd-timesyncd"], check=True)
#     subprocess.run(["systemctl", "enable", "systemd-resolved"], check=True)
#     subprocess.run(["systemctl", "enable", "NetworkManager"], check=True)
#     subprocess.run(["systemctl", "enable", "sshd"], check=True)