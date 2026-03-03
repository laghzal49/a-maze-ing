"""ASCII fallback renderer with symbol priority."""

from typing import List

from .maze_generator import Maze


class AsciiCorner:
    """Maps corner wall configurations to Unicode box-drawing characters."""
    
    # Lookup table: (left, right, up, down) -> character
    CORNER_MAP = {
        (True, True, True, True): "╋",
        (True, False, True, True): "┫",
        (False, True, True, True): "┣",
        (True, True, True, False): "┻",
        (True, True, False, True): "┳",
        (True, False, True, False): "┃",
        (False, True, False, False): "━",
        (True, True, False, False): "━",
        (True, False, False, True): "┓",
        (True, False, False, False): "┃",
        (False, True, True, False): "┗",
        (False, True, False, True): "┏",
        (False, False, True, True): "┃",
        (False, False, True, False): "┃",
        (False, False, False, True): "┃",
        (False, False, False, False): " ",
    }

    @staticmethod
    def get_corner(left: bool, right: bool, up: bool, down: bool) -> str:
        """Get box-drawing character for corner configuration."""
        return AsciiCorner.CORNER_MAP.get(
            (left, right, up, down), " "
        )


def render_maze(maze: Maze) -> None:
    """Render a static ASCII version of the maze."""
    from .maze_drawing import compute_wall_grids
    
    horiz, vert = compute_wall_grids(maze)
    w, h = maze.width, maze.height

    for jy in range(h + 1):
        wall_parts: List[str] = []
        for jx in range(w + 1):
            left = horiz[jy][jx - 1] if jx > 0 else False
            right = horiz[jy][jx] if jx < w else False
            up = vert[jx][jy - 1] if jy > 0 else False
            down = vert[jx][jy] if jy < h else False
            wall_parts.append(AsciiCorner.get_corner(left, right, up, down))
            if jx < w:
                wall_parts.append("━━━" if horiz[jy][jx] else "   ")
        print("".join(wall_parts))

        if jy == h:
            break
