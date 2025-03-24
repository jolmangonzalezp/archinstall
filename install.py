import curses

import requests

enter = "\npresione enter para continuar"

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.clear()
    stdscr.refresh()    

    menu = ['Locale', 'Network', 'Disk', 'Salir']
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

        # Leer entrada del usuario
        tecla = stdscr.getch()

        # Navegar por el menú
        if tecla == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif tecla == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif tecla == curses.KEY_ENTER or tecla in [10, 13]:
            if menu[current_row] == 'Locale':
                stdscr.clear()
                stdscr.addstr(1, 2, "Definiendo idioma...", curses.color_pair(1))
                get_locale, get_timezone = locale(stdscr)
                message(stdscr, f"Idioma: {get_locale}, Zona horaria: {get_timezone}")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == "Salir":
                break

def message(stdscr, message):
    stdscr.addstr(3, 2, message+enter, curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()

def locale(stdscr):
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            locale = data.get("languages").split(',')[0].split('-')[0].lower()
            timezone = data.get("timezone").split(',')[0].split('-')[0].lower()
            message(stdscr, f"Idioma: {locale}, Zona horaria: {timezone}")
            return locale, timezone
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


curses.wrapper(main)