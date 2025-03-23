import subprocess
import os
import re
import requests

efi = ""
root_partition = "/dev/mapper/cryptroot"
crypy_root = ""

def obtener_locale_timezone():
    try:
        locale = requests.get("https://ipapi.co/languages").text.split(',')[0]
        timezone = requests.get("https://ipapi.co/timezone").text
        return locale, timezone
    except requests.RequestException:
        print("Error obteniendo locale y timezone.")
        return None, None

def configurar_teclado_idioma(locale):
    print("Configurando el teclado y el idioma...")
    locale_gen_path = "/mnt/etc/locale.gen"
    with open(locale_gen_path, "r") as file:
        lines = file.readlines()
    
    updated_lines = [
        re.sub(f"^#{locale}.UTF-8", f"{locale}.UTF-8", line) for line in lines
    ]
    
    with open(locale_gen_path, "w") as file:
        file.writelines(updated_lines)
    
    subprocess.run(["locale-gen"], check=True)
    print("El teclado y el idioma se han configurado correctamente.")
    rfkill_unblock()

def rfkill_unblock():
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
            print(f"Desbloqueado dispositivo con ID {device_id} a nivel de software.")
        if hard_blocked:
            print(f"El dispositivo con ID {device_id} está bloqueado a nivel de hardware. No se puede desbloquear automáticamente.")
    
    connect_to_internet()

def connect_to_internet():
    try:
        subprocess.run(["ping", "-c1", "8.8.8.8"], check=True, stdout=subprocess.DEVNULL)
        print("Conexión a Internet: OK")
    except subprocess.CalledProcessError:
        print("No hay conexión a Internet. Sigue las instrucciones para conectarte manualmente usando 'iwctl'.")
        input("Presiona Enter para iniciar el proceso de conexión a Internet.")
        subprocess.run(["iwctl"], check=True)
    
    subprocess.run(["timedatectl", "set-ntp", "true"], check=True)
    particion_disco()

def particion_disco():
    disks_output = subprocess.run(["lsblk", "-dno", "NAME,SIZE"], capture_output=True, text=True).stdout
    print("Discos disponibles:")
    print(disks_output)
    
    disk_name = input("Selecciona el disco a particionar: ")
    commands = [
        "g", "n", "1", "", "+512M", "t", "1", "n", "2", "", "", "w"
    ]
    
    process = subprocess.Popen(["fdisk", f"/dev/{disk_name}"], stdin=subprocess.PIPE, text=True)
    process.communicate("\n".join(commands))
    print("Particiones creadas:")
    subprocess.run(["lsblk", f"/dev/{disk_name}"], check=True)
    disk_formating(disk_name)

def disk_formating(disk_name):
    global efi, root_partition
    interface = subprocess.run(
        ["lsblk", "-o", "NAME,TRAN"], capture_output=True, text=True
    ).stdout.splitlines()
    
    if "sata" in interface:
        efi = f"{disk_name}1"
        root_partition = f"{disk_name}2"
    elif "nvme" in interface:
        efi = f"{disk_name}p1"
        root_partition = f"{disk_name}p2"
    else:
        print(f"No se pudo determinar la interfaz de {disk_name}.")
        return
    
    subprocess.run(["mkfs.fat", "-F32", f"/dev/{efi}"], check=True)
    encripting(root_partition)

def encripting(root_partition):
    print("Encriptando el disco...")
    luks_pass = input("Introduce la contraseña LUKS: ")
    luks_pass_confirm = input("Confirma la contraseña LUKS: ")
    
    if luks_pass != luks_pass_confirm:
        print("Error: Las contraseñas no coinciden.")
        return
    
    subprocess.run(["cryptsetup", "erase", f"/dev/{root_partition}"], check=True)
    subprocess.run(
        ["cryptsetup", "-y", "-v", "luksFormat", "--type", "luks2", "--force-password", f"/dev/{root_partition}"],
        input=luks_pass, text=True, check=True
    )
    subprocess.run(["cryptsetup", "open", f"/dev/{root_partition}", "cryptroot"], check=True)
    btrfs_partition()

def btrfs_partition():
    print("Formateando con BTRFS...")
    global crypy_root
    crypy_root = f"/dev/mapper/cryptroot"
    subprocess.run(["mkfs.btrfs", crypy_root], check=True)
    os.makedirs("/mnt", exist_ok=True)
    subprocess.run(["mount", crypy_root, "/mnt"], check=True)
    
    for subvolume in ["@", "@home", "@snapshots", "@var_log", "@swap"]:
        subprocess.run(["btrfs", "subvolume", "create", f"/mnt/{subvolume}"], check=True)
    
    mount_partitions()

def mount_partitions():
    subprocess.run(["umount", "/mnt"], check=True)
    mount_options = "noatime,compress=zstd,space_cache=v2"
    subprocess.run(["mount", "-o", f"{mount_options},subvol=@", crypy_root, "/mnt"], check=True)
    os.makedirs("/mnt/boot", exist_ok=True)
    subprocess.run(["mount", f"/dev/{efi}", "/mnt/boot"], check=True)
    print("Particiones montadas.")
    instalar_sistema()

def instalar_sistema():
    cpu_brand = subprocess.run(
        ["lscpu"], capture_output=True, text=True
    ).stdout.splitlines()
    packages = [
        "base", "linux-zen", "linux-zen-headers", "linux-firmware",
        "btrfs-progs", "efibootmgr", "grub", "os-prober", "networkmanager"
    ]
    subprocess.run(["pacstrap", "/mnt"] + packages, check=True)
    print("Sistema instalado.")

if __name__ == "__main__":
    locale, timezone = obtener_locale_timezone()
    if locale and timezone:
        configurar_teclado_idioma(locale)
