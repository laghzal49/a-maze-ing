"""Color initialization and management for curses rendering."""
import curses


COLOR_PATH = 1
COLOR_STATUS = 2
COLOR_WALL_ALT = 3
COLOR_WALL = 4
COLOR_END = 5
COLOR_PLAYER = 6
COLOR_WALL_ALT2 = 7


def initialize_colors() -> None:
    """Initialize curses color pairs."""
    curses.init_pair(COLOR_PATH, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_STATUS, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WALL_ALT, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WALL, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_END, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PLAYER, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WALL_ALT2, curses.COLOR_BLUE, curses.COLOR_BLACK)
