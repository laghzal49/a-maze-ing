import curses
from typing import Optional, List, Tuple

from .maze_generator import Maze

# Direction constants used across modules
DIRECTIONS: List[Tuple[int, int]] = [
    (0, -1), (1, 0), (0, 1), (-1, 0)]


def is_wall_between(maze: Maze, x: int, y: int, dx: int, dy: int) -> bool:
    """Return True if there is a wall between (x, y) and (x+dx, y+dy)."""
    nx, ny = x + dx, y + dy
    if not maze.in_bounds(nx, ny):
        return True
    if maze.is_blocked(x, y) or maze.is_blocked(nx, ny):
        return True

    cell = maze.walls[y][x]
    if dx == 0 and dy == -1:
        return bool(cell & maze.N)
    if dx == 1 and dy == 0:
        return bool(cell & maze.E)
    if dx == 0 and dy == 1:
        return bool(cell & maze.S)
    if dx == -1 and dy == 0:
        return bool(cell & maze.W)
    return True


def safe_addstr(
    stdscr: "curses.window",
    y: int,
    x: int,
    text: str,
    attr: Optional[int] = None,
    max_x: Optional[int] = None,
) -> int:
    """Safely add a string to the screen, clipping to max_x and
    swallowing curses.error. Returns number of characters written.
    """
    try:
        if max_x is not None and x >= max_x:
            return 0
        if max_x is not None and x + len(text) > max_x:
            text = text[: max(0, max_x - x)]
        if attr is None:
            stdscr.addstr(y, x, text)
        else:
            stdscr.addstr(y, x, text, attr)
        return len(text)
    except curses.error:
        return 0
