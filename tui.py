import curses

def main(stdscr):
    # Configurar colores
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    # Opciones del menú
    menu = ["Decir Hola", "Sumar Números", "Salir"]
    seleccion = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Usa las flechas para navegar y Enter para seleccionar.", curses.color_pair(2))

        # Mostrar las opciones del menú
        for idx, item in enumerate(menu):
            if idx == seleccion:
                stdscr.addstr(idx + 2, 0, f"> {item}", curses.color_pair(1))
            else:
                stdscr.addstr(idx + 2, 0, f"  {item}")

        # Actualizar la pantalla
        stdscr.refresh()

        # Leer entrada del usuario
        tecla = stdscr.getch()

        # Navegar por el menú
        if tecla == curses.KEY_UP and seleccion > 0:
            seleccion -= 1
        elif tecla == curses.KEY_DOWN and seleccion < len(menu) - 1:
            seleccion += 1
        elif tecla == curses.KEY_ENTER or tecla in [10, 13]:  # Enter
            if menu[seleccion] == "Decir Hola":
                stdscr.clear()
                stdscr.addstr(0, 0, "¡Hola! Presiona cualquier tecla para volver al menú.", curses.color_pair(2))
                stdscr.refresh()
                stdscr.getch()
            elif menu[seleccion] == "Sumar Números":
                stdscr.clear()
                stdscr.addstr(0, 0, "Ingresa dos números para sumar:", curses.color_pair(2))
                stdscr.addstr(2, 0, "Primer número: ")
                stdscr.refresh()
                curses.echo()  # Habilitar entrada visible
                num1 = stdscr.getstr(2, 15).decode()
                stdscr.addstr(3, 0, "Segundo número: ")
                stdscr.refresh()
                num2 = stdscr.getstr(3, 16).decode()
                curses.noecho()  # Ocultar entrada de nuevo

                try:
                    suma = float(num1) + float(num2)
                    stdscr.addstr(5, 0, f"La suma es: {suma}", curses.color_pair(2))
                except ValueError:
                    stdscr.addstr(5, 0, "Entrada inválida. Presiona cualquier tecla para continuar.", curses.color_pair(3))
                stdscr.refresh()
                stdscr.getch()
            elif menu[seleccion] == "Salir":
                break

curses.wrapper(main)
