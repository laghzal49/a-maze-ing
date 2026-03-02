"""Maze output writer for hexadecimal encoding."""

from typing import List, Tuple

from .maze_generator import Maze
from .path_finder import bfs_find_path, path_to_moves


def maze_to_hex_rows(maze: Maze) -> List[str]:
    """Convert maze walls to hex rows."""
    rows: List[str] = []
    for y in range(maze.height):
        row = "".join(format(cell, "X") for cell in maze.walls[y])
        rows.append(row)
    return rows


def write_output_file(
    output_file: str,
    maze: Maze,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
) -> str:
    """Write maze to output file and return the shortest path moves."""
    path = bfs_find_path(maze, entry, exit_pos)
    if not path:
        raise ValueError("No valid path between ENTRY and EXIT")

    moves = path_to_moves(path)
    lines = maze_to_hex_rows(maze)
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_pos[0]},{exit_pos[1]}")
    lines.append(moves)

    with open(output_file, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")

    return moves
