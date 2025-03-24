import curses


enter = "\npresione enter para continuar"

def message(stdscr, message):
    stdscr.addstr(3, 2, message+enter, curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()
