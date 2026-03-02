"""Maze rendering and wall grid computation for curses display."""
import curses
from typing import List, Tuple

from .maze_generator import Maze
from .ascii_renderer import AsciiCorner
from .utils import is_wall_between

LineParts = List[Tuple[str, int]]


def build_cell_line(
    maze: Maze,
    y: int,
    player_pos: List[int],
    end: Tuple[int, int],
    path_set: set,
    show_path: bool,
    color_42: int,
    color_wall: int,
    vert: List[List[bool]],
) -> LineParts:
    """Build the cell content line for a row."""
    line_parts: LineParts = []

    for x in range(maze.width):
        if x == 0:
            wall = "┃" if vert[0][y] else " "
            line_parts.append((wall, curses.color_pair(color_wall)))

        if [x, y] == player_pos:
            line_parts.append((" ⦻ ", curses.color_pair(6)))
        elif (x, y) == end:
            line_parts.append(("[ ]", curses.color_pair(5)))
        elif show_path and (x, y) in path_set:
            line_parts.append((" o ", curses.color_pair(1)))
        elif maze.is_blocked(x, y):
            line_parts.append(("███", curses.color_pair(color_42)))
        else:
            line_parts.append(("   ", curses.color_pair(color_wall)))

        wall = "┃" if vert[x + 1][y] else " "
        line_parts.append((wall, curses.color_pair(color_wall)))

    return line_parts


def build_wall_line(
    maze: Maze,
    y: int,
    color_wall: int,
    horiz: List[List[bool]],
    vert: List[List[bool]],
) -> LineParts:
    """Build the south wall line for a row."""
    line_parts: LineParts = []
    for jx in range(maze.width + 1):
        left = horiz[y][jx - 1] if jx > 0 else False
        right = horiz[y][jx] if jx < maze.width else False
        up = vert[jx][y - 1] if y > 0 else False
        down = vert[jx][y] if y < maze.height else False
        corner = AsciiCorner.get_corner(left, right, up, down)
        line_parts.append((corner, curses.color_pair(color_wall)))
        if jx < maze.width:
            wall = "━━━" if horiz[y][jx] else "   "
            line_parts.append((wall, curses.color_pair(color_wall)))

    return line_parts


def compute_wall_grids(
    maze: Maze,
) -> Tuple[List[List[bool]], List[List[bool]]]:
    """Precompute horizontal and vertical wall
        presence for efficient rendering."""
    horiz = [[False for _ in range(maze.width)]
             for _ in range(maze.height + 1)]
    vert = [[False for _ in range(maze.height)]
            for _ in range(maze.width + 1)]

    for jy in range(maze.height + 1):
        for x in range(maze.width):
            if jy == 0:
                horiz[jy][x] = is_wall_between(maze, x, 0, 0, -1)
            elif jy == maze.height:
                horiz[jy][x] = is_wall_between(
                    maze, x, maze.height - 1, 0, 1)
            else:
                horiz[jy][x] = is_wall_between(maze, x, jy - 1, 0, 1)

    for jx in range(maze.width + 1):
        for y in range(maze.height):
            if jx == 0:
                vert[jx][y] = is_wall_between(maze, 0, y, -1, 0)
            elif jx == maze.width:
                vert[jx][y] = is_wall_between(
                    maze, maze.width - 1, y, 1, 0)
            else:
                vert[jx][y] = is_wall_between(maze, jx - 1, y, 1, 0)

    return horiz, vert
