"""Breadth-First Search pathfinder and move sequence generator."""

from collections import deque
from typing import Deque, List, Tuple, Optional

from .maze_generator import Maze
from .utils import is_wall_between


def bfs_find_path(
    maze: Maze,
    start: Tuple[int, int],
    end: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """Find the shortest path avoiding blocked cells and walls."""

    xs, ys = start
    xe, ye = end

    if not maze.in_bounds(xe, ye) or maze.is_blocked(xe, ye):
        return None
    if not maze.in_bounds(xs, ys) or maze.is_blocked(xs, ys):
        return None

    d: Deque[Tuple[int, int, List[Tuple[int, int]]]] = deque()
    d.append((xs, ys, [start]))
    visited = {start}

    directions = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0),
    ]

    while d:
        x, y, path = d.popleft()
        if (x, y) == end:
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (
                maze.in_bounds(nx, ny)
                and not maze.is_blocked(nx, ny)
                and (nx, ny) not in visited
                and not is_wall_between(maze, x, y, dx, dy)
            ):
                visited.add((nx, ny))
                d.append((nx, ny, path + [(nx, ny)]))

    return None


def path_to_moves(path: List[Tuple[int, int]]) -> str:
    """Convert a list of coordinates into a N/E/S/W direction string."""
    if not path or len(path) < 2:
        return ""

    moves = []
    dir_map = {
        (0, -1): "N",
        (1, 0): "E",
        (0, 1): "S",
        (-1, 0): "W",
    }

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        move = dir_map.get((x2 - x1, y2 - y1))
        if move:
            moves.append(move)

    return "".join(moves)
