import subprocess


def install():
    cpu_brand = ""
    result = subprocess.run(
        ["lscpu"], capture_output=True, text=True, check=True
    )
    # Filtrar la línea con "Vendor ID:" y extraer la tercera columna
    for line in result.stdout.splitlines():
        if "Vendor ID:" in line:
            cpu_brand = line.split()[2]

    # Imprimir el nombre del procesador
    print(f"Nombre del procesador: {cpu_brand}")
    
install()