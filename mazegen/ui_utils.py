"""UI utilities and display functions for curses rendering."""
import curses
import time
from typing import List, Tuple

from .utils import safe_addstr as _safe_addstr


def terminal_big_enough(
    stdscr: "curses.window",
    min_rows: int,
    min_cols: int,
) -> bool:
    """Check if terminal can display the maze UI."""
    max_y, max_x = stdscr.getmaxyx()
    return max_y >= min_rows and max_x >= min_cols


def show_terminal_too_small(
    stdscr: "curses.window",
    min_rows: int,
    min_cols: int,
) -> None:
    """Show a clear warning when terminal is too small, then exit."""
    max_y, max_x = stdscr.getmaxyx()
    message = "\n".join([
        "Terminal too small for maze UI.",
        f"Required: {min_cols}x{min_rows} (cols x rows)",
        f"Current : {max_x}x{max_y}",
        "Resize terminal and run again.",
        "Press any key to exit.",
    ])
    draw_centered_message(
        stdscr,
        message,
        curses.color_pair(5),
        clear_first=True,
    )
    stdscr.refresh()
    stdscr.getch()


def draw_centered_message(
    stdscr: "curses.window",
    message: str,
    attr: int = 0,
    clear_first: bool = False,
) -> None:
    """Draw a multi-line message centered on screen."""
    max_y, max_x = stdscr.getmaxyx()
    lines = message.splitlines() or [""]

    if clear_first:
        stdscr.clear()

    start_y = max(0, (max_y - len(lines)) // 2)

    for i, line in enumerate(lines):
        y = start_y + i
        if y >= max_y:
            break
        x = max(0, (max_x - len(line)) // 2)
        _safe_addstr(stdscr, y, x, line, attr, max_x)


def loop_color_message(stdscr: "curses.window", message: str) -> None:
    """Display a message cycling through different colors."""
    colors = [1, 2, 3, 4, 5, 6, 7]

    for color in colors:
        draw_centered_message(
            stdscr,
            message,
            curses.color_pair(color),
            clear_first=True,
        )
        try:
            stdscr.refresh()
        except curses.error:
            pass
        time.sleep(0.25)


def draw_maze_line(
    stdscr: "curses.window",
    row: int,
    line_parts: List[Tuple[str, int]],
    start_col: int,
    max_x: int,
) -> None:
    """Draw a single line of the maze."""
    col = start_col
    for text, color in line_parts:
        if col >= max_x:
            break
        written = _safe_addstr(stdscr, row, col, text, color, max_x)
        if written == 0:
            break
        col += written


def draw_bottom_panel(
    stdscr: "curses.window",
    max_y: int,
    max_x: int,
    display_status: str,
    show_path: bool,
    current_algo: str,
    current_perfect: bool,
    maze_rows: int,
    maze_top_calc: int,
) -> None:
    """Draw the right-side control panel."""
    try:
        status_row = max(0, min(max_y - 2, maze_top_calc + maze_rows))
        menu_row = max(0, max_y - 1)

        status_text = display_status if display_status else "Ready."
        avail_width = max_x - 2
        if avail_width > 0:
            clipped_status = status_text[:avail_width]
            status_x = max(0, (max_x - len(clipped_status)) // 2)
            _safe_addstr(
                stdscr, status_row, status_x, clipped_status,
                curses.color_pair(2), max_x
            )
        path_status = "ON" if show_path else "OFF"
        perfect_status = "ON" if current_perfect else "OFF"
        commands = [
            "Arrows:Move",
            f"P:Path({path_status})",
            "R:Reset",
            f"A:Algo({current_algo})",
            f"T:Perfect({perfect_status})",
            "G:Seed",
            "S:Save",
            "C:Wall + 42 Pattern",
            "Q:Quit",
        ]
        menu_line = " | ".join(commands)
        if len(menu_line) > max_x - 2:
            menu_line = menu_line[: max_x - 2]
        menu_x = max(0, (max_x - len(menu_line)) // 2)
        _safe_addstr(
            stdscr, menu_row, menu_x, menu_line, curses.color_pair(4),
            max_x
        )
    except Exception:
        return
