import subprocess


def format_disk():
    global efi, root_partition, disk_name
    # interface = subprocess.run(
    #     ["lsblk", "-o", "NAME,TRAN"], capture_output=True, text=True
    # ).stdout.splitlines()
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
    
format_disk()