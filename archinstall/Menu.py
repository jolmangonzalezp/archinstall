import os

class ConfigMenu ():

    # dm = ("gdm", "lighdm", "lxdm", "sddm", "xdm")

    def __init__(self):
        # self.dm = dm
        self.principal(self)

    def principal (self):
        self.opciones = {
        '1': ('Opción 1', self.accion1),
        '2': ('Opción 2', self.accion2),
        '3': ('Opción 3', self.accion3),
        '4': ('Salir', self.salir)
        }
        self.generar_menu(self.opciones, '4')
    def generar_menu(self, opciones, opcion_salida):
        opcion = None
        while opcion != opcion_salida:
            self.mostrar_menu(self.opciones)
            opcion = self.leer_opcion(self.opciones)
            self.ejecutar_opcion(opcion, self.opciones)
            print() # se imprime una línea en blanco para clarificar la salida por pantalla
    def leer_opcion(opciones):
        while (a := input('Opción: ')) not in opciones:
            print('Opción incorrecta, vuelva a intentarlo.')
        return a
    def mostrar_menu(opciones):
        print('Seleccione una opción:')
        for clave in sorted(opciones):
            print(f' {clave}) {opciones[clave][0]}')
    def accion1 () :
        pass
    def accion2 () :
        pass
    def accion3 () :
        pass
    def salir () :
        pass
