"""Player movement and position management for curses gameplay."""
import curses
from typing import List

from .maze_generator import Maze

# Direction mappings: key -> (dx, dy, wall_bit, index_to_update)
DIRECTION_MAP = {
    curses.KEY_UP: (0, -1, Maze.N, 1),
    curses.KEY_DOWN: (0, 1, Maze.S, 1),
    curses.KEY_LEFT: (-1, 0, Maze.W, 0),
    curses.KEY_RIGHT: (1, 0, Maze.E, 0),
}


def handle_movement(
    key: int,
    maze: Maze,
    player_pos: List[int],
) -> None:
    """Handle player movement keys using direction mappings."""
    if key not in DIRECTION_MAP:
        return

    dx, dy, wall_bit, coord_index = DIRECTION_MAP[key]
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy

    if not (maze.in_bounds(new_x, new_y) and
            not maze.is_blocked(new_x, new_y)):
        return

    cell = maze.walls[player_pos[1]][player_pos[0]]
    if not (cell & wall_bit):
        player_pos[coord_index] += (dx if coord_index == 0 else dy)
