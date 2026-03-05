"""Main curses-based maze renderer with interactive gameplay."""
import curses
import random
from typing import List, Optional, Set, Tuple

from .maze_generator import Maze
from .path_finder import bfs_find_path
from .output_writer import write_output_file
from .animate_path import animate_path
from .colors import initialize_colors
from .maze_drawing import build_cell_line, build_wall_line, compute_wall_grids
from .player_movement import handle_movement
from .ui_utils import (
    terminal_big_enough,
    show_terminal_too_small,
    loop_color_message,
    draw_maze_line,
    draw_bottom_panel,
)
from .utils import safe_addstr as _safe_addstr

MAZE_ROWS_MULTIPLIER: int = 2
MAZE_COLS_MULTIPLIER: int = 4
MAZE_LAYOUT_OFFSET: int = 1


def compute_layout_size(width: int, height: int) -> Tuple[int, int]:
    """Compute maze display dimensions.

    Args:
        width: Maze width in cells
        height: Maze height in cells
    Returns:
        Tuple of (min_rows, min_cols) needed for display
    """
    min_rows = height * MAZE_ROWS_MULTIPLIER + MAZE_LAYOUT_OFFSET
    min_cols = width * MAZE_COLS_MULTIPLIER + MAZE_LAYOUT_OFFSET
    return min_rows, min_cols


STATUS_READY: str = "Ready to play (Use ARROWS)"
STATUS_PATH_ON: str = "Path display ON."
STATUS_PATH_OFF: str = "Path display OFF."
STATUS_MAZE_REGENERATED: str = "Maze regenerated. \
    And ready to play (use ARROWS)"
STATUS_NEW_GAME: str = "New Game Started."
STATUS_PERFECT_ON: str = "Perfect mode ON."
STATUS_PERFECT_OFF: str = "Perfect mode OFF."
STATUS_NO_OUTPUT_FILE: str = "Error: no output file configured."
STATUS_SAVED: str = "Saved to {output_file}."
STATUS_SAVE_ERROR: str = "Error: {error}"
STATUS_COLORS_CHANGED: str = "Colors changed (wall pair { \
    wall}, 42 pair {pattern})."
STATUS_SEED_UPDATED: str = "Seed updated: {seed}."
STATUS_WON: str = "You won! Press R to play again or Q to quit."
STATUS_ANIMATING: str = "Animating path... (press Q to skip)"
STATUS_ALGO_CHANGED: str = "Algorithm set to { \
    algo} and ready to play (use ARROWS)."


ALGO_CYCLE: List[str] = ["dfs", "prim", "hunt"]
MAX_SEED: int = 2**31 - 1

COLOR_PATTERN_MIN: int = 3
COLOR_PATTERN_WRAP: int = 5
COLOR_WALL_MIN: int = 4
COLOR_WALL_WRAP: int = 4
COLOR_PLAYER_DISPLAY: int = 6
COLOR_PATH_DISPLAY: int = 1

WALL_ROW_OFFSET: int = 2
CELL_COL_OFFSET: int = 4
PLAYER_MARKER: str = " ⦻ "
EMPTY_CELL: str = "   "

KEY_QUIT: List[int] = [ord('q'), ord('Q')]
KEY_RESTART: List[int] = [ord('r'), ord('R')]
KEY_TOGGLE_PATH: List[int] = [ord('p'), ord('P')]
KEY_CHANGE_ALGORITHM: List[int] = [ord('a'), ord('A')]
KEY_CHANGE_SEED: List[int] = [ord('s'), ord('S')]
KEY_CHANGE_COLOR: List[int] = [ord('c'), ord('C')]


def setup_phase(
    stdscr: "curses.window",
    config_start: Optional[Tuple[int, int]],
    config_end: Optional[Tuple[int, int]],
) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """Setup phase for configuring entry/exit before gameplay."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    try:
        curses.mousemask(0)
        curses.mouseinterval(0)
    except curses.error:
        pass
    initialize_colors()

    loop_color_message(
        stdscr,
        """
░█████╗░░░░░░░███╗░░░███╗░█████╗░███████╗███████╗░░░░░░██╗███╗░░██╗░██████╗░
██╔══██╗░░░░░░████╗░████║██╔══██╗╚════██║██╔════╝░░░░░░██║████╗░██║██╔════╝░
███████║█████╗██╔████╔██║███████║░░███╔═╝█████╗░░█████╗██║██╔██╗██║██║░░██╗░
██╔══██║╚════╝██║╚██╔╝██║██╔══██║██╔══╝░░██╔══╝░░╚════╝██║██║╚████║██║░░╚██╗
██║░░██║░░░░░░██║░╚═╝░██║██║░░██║███████╗███████╗░░░░░░██║██║░╚███║╚██████╔╝
╚═╝░░╚═╝░░░░░░╚═╝░░░░░╚═╝╚═╝░░╚═╝╚══════╝╚══════╝░░░░░░╚═╝╚═╝░░╚══╝░╚═════╝░
""".strip("\n"),
    )
    loop_color_message(
        stdscr,
        """

██████╗░░█████╗░░██╗░░░░░░░██╗███████╗██████╗░███████╗██████╗░  
██╔══██╗██╔══██╗░██║░░██╗░░██║██╔════╝██╔══██╗██╔════╝██╔══██╗  
██████╔╝██║░░██║░╚██╗████╗██╔╝█████╗░░██████╔╝█████╗░░██║░░██║  
██╔═══╝░██║░░██║░░████╔═████║░██╔══╝░░██╔══██╗██╔══╝░░██║░░██║  
██║░░░░░╚█████╔╝░░╚██╔╝░╚██╔╝░███████╗██║░░██║███████╗██████╔╝  
╚═╝░░░░░░╚════╝░░░░╚═╝░░░╚═╝░░╚══════╝╚═╝░░╚═╝╚══════╝╚═════╝░  

    ██████╗░██╗░░░██╗  ██╗
    ██╔══██╗╚██╗░██╔╝  ╚═╝
    ██████╦╝░╚████╔╝░  ░░░
    ██╔══██╗░░╚██╔╝░░  ░░░
    ██████╦╝░░░██║░░░  ██╗
    ╚═════╝░░░░╚═╝░░░  ╚═╝

███╗░░░███╗███████╗██╗░░░░░░░░░░░░█████╗░░██████╗██╗░░░░░░█████╗░  
████╗░████║██╔════╝██║░░░░░░░░░░░██╔══██╗██╔════╝██║░░░░░██╔══██╗  
██╔████╔██║█████╗░░██║░░░░░█████╗███████║╚█████╗░██║░░░░░███████║  
██║╚██╔╝██║██╔══╝░░██║░░░░░╚════╝██╔══██║░╚═══██╗██║░░░░░██╔══██║  
██║░╚═╝░██║███████╗███████╗░░░░░░██║░░██║██████╔╝███████╗██║░░██║  
╚═╝░░░░░╚═╝╚══════╝╚══════╝░░░░░░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝  

████████╗██╗░░░░░░█████╗░░██████╗░██╗░░██╗███████╗░█████╗░██╗░░░░░░░░
╚══██╔══╝██║░░░░░██╔══██╗██╔════╝░██║░░██║╚════██║██╔══██╗██║░░░░░░░░
░░░██║░░░██║░░░░░███████║██║░░██╗░███████║░░███╔═╝███████║██║░░░░░░░░
░░░██║░░░██║░░░░░██╔══██║██║░░╚██╗██╔══██║██╔══╝░░██╔══██║██║░░░░░░░░
░░░██║░░░███████╗██║░░██║╚██████╔╝██║░░██║███████╗██║░░██║███████╗██╗
░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝╚═╝
    """.strip("\n"))
    return config_start, config_end


def render_maze_curses(
    stdscr: "curses.window",
    maze: Maze,
    start: Optional[Tuple[int, int]] = None,
    end: Optional[Tuple[int, int]] = None,
    algo: str = "dfs",
    seed: Optional[int] = None,
    perfect: bool = True,
    output_file: Optional[str] = None,
) -> None:
    """Render maze using curses with keyboard controls."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    try:
        curses.mousemask(0)
        curses.mouseinterval(0)
    except curses.error:
        pass

    initialize_colors()

    min_rows, min_cols = compute_layout_size(maze.width, maze.height)
    if not terminal_big_enough(stdscr, min_rows, min_cols):
        show_terminal_too_small(stdscr, min_rows, min_cols)
        return

    height_var = maze.height
    color_42 = COLOR_PATTERN_MIN
    color_wall = COLOR_WALL_MIN
    current_algo = algo if algo in ALGO_CYCLE else "dfs"
    current_perfect = perfect
    current_seed = seed

    status_msg = [""]
    start, end = setup_phase(stdscr, start, end)
    if start is None or end is None:
        return

    path_set: Set[Tuple[int, int]] = set()
    path_ref: List[Optional[List[Tuple[int, int]]]] = [None]
    path_found_ref = [False]

    player_pos = list(start)
    prev_player_pos = list(start)
    show_path = True
    needs_full_redraw = [False]
    horiz, vert = compute_wall_grids(maze)
    maze_rows = height_var * MAZE_ROWS_MULTIPLIER + MAZE_LAYOUT_OFFSET
    maze_cols = maze.width * MAZE_COLS_MULTIPLIER + MAZE_LAYOUT_OFFSET

    def _compute_layout(max_y: int, max_x: int) -> Tuple[int, int, int, int]:
        maze_left = max(0, (max_x - maze_cols) // 2)
        maze_top = max(0, (max_y - maze_rows) // 2)
        panel_left = max_x + 1
        panel_width = 0
        return maze_top, maze_left, panel_left, panel_width

    def _draw_bottom_panel_wrapper(
        max_y: int,
        max_x: int,
        display_status: str,
    ) -> None:
        try:
            maze_top_calc = max(0, (max_y - maze_rows) // 2)
            draw_bottom_panel(
                stdscr,
                max_y,
                max_x,
                display_status,
                show_path,
                current_algo,
                current_perfect,
                maze_rows,
                maze_top_calc,
            )
        except Exception:
            return

    def _update_player_cell(x: int, y: int, is_player: bool) -> None:
        """Update a single cell for player movement."""
        try:
            max_y, max_x = stdscr.getmaxyx()
            maze_top, maze_left, _, _ = _compute_layout(max_y, max_x)
            row = maze_top + y * WALL_ROW_OFFSET + 1
            if row >= max_y:
                return
            color = color_wall
            if is_player:
                content = PLAYER_MARKER
                color = COLOR_PLAYER_DISPLAY
            elif show_path and (x, y) in path_set:
                content = EMPTY_CELL
                color = COLOR_PATH_DISPLAY
            else:
                content = EMPTY_CELL
            col = maze_left + x * CELL_COL_OFFSET + 1
            _safe_addstr(stdscr, row, col, content, curses.color_pair(color))
            try:
                stdscr.refresh()
            except curses.error:
                pass
        except curses.error:
            pass

    def _render_frame(
        current_path_set: Optional[Set[Tuple[int, int]]] = None,
        override_status: Optional[str] = None,
        full_clear: bool = True,
    ) -> None:
        if full_clear:
            stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        maze_top, maze_left, _, \
            _ = _compute_layout(max_y, max_x)
        row = maze_top
        path_to_show = (
            current_path_set
            if current_path_set is not None
            else (path_set if show_path else set())
        )
        for jy in range(height_var + 1):
            if row >= max_y:
                break

            line_wall = build_wall_line(
                maze, jy, color_wall, horiz, vert
            )
            draw_maze_line(stdscr, row, line_wall, maze_left, max_x)
            row += 1

            if jy == height_var or row >= max_y:
                break

            line_cell = build_cell_line(
                maze, jy, player_pos, end, path_to_show,
                True if current_path_set is not None else show_path,
                color_42, color_wall, vert
            )
            draw_maze_line(stdscr, row, line_cell, maze_left, max_x)
            row += 1

        display_status = (
            override_status if override_status is not None else status_msg[0]
        )
        _draw_bottom_panel_wrapper(max_y, max_x, display_status)

        stdscr.refresh()

    def _update_path_state() -> None:
        try:
            new_path = bfs_find_path(maze, start, end)
            path_ref[0] = new_path
            path_set.clear()
            if new_path:
                path_set.update(new_path)
            path_found_ref[0] = bool(new_path)
        except (ValueError, Exception):
            path_ref[0] = None
            path_set.clear()
            path_found_ref[0] = False

    def _regenerate_maze(status: str) -> None:
        # Keep path generation strictly after maze generation.
        path_set.clear()
        path_ref[0] = None
        path_found_ref[0] = False
        maze.generate_maze(
            seed=current_seed,
            algo=current_algo,
            perfect=current_perfect
        )
        _update_path_state()
        new_horiz, new_vert = compute_wall_grids(maze)
        horiz[:] = new_horiz
        vert[:] = new_vert
        player_pos[:] = [start[0], start[1]]
        prev_player_pos[:] = [start[0], start[1]]
        status_msg[0] = status
        needs_full_redraw[0] = True

    def _animate_current_path() -> None:
        if not path_ref[0]:
            return
        saved_path = list(path_ref[0])
        path_set.clear()
        _render_frame(
            current_path_set=set(),
            override_status=STATUS_ANIMATING,
        )
        animate_path(
            stdscr,
            saved_path,
            lambda partial: _render_frame(
                current_path_set=partial,
                override_status=STATUS_ANIMATING
            ),
        )
        path_set.update(saved_path)
        needs_full_redraw[0] = True
    _regenerate_maze(STATUS_READY)
    if path_ref[0]:
        _animate_current_path()
    needs_full_redraw[0] = True
    while True:
        if needs_full_redraw[0]:
            _render_frame()
            prev_player_pos = list(player_pos)
            needs_full_redraw[0] = False

        win_handled = False
        if player_pos == [end[0], end[1]] and path_found_ref[0]:
            show_path = True
            status_msg[0] = STATUS_WON
            _render_frame()
            while True:
                key = stdscr.getch()
                if key in KEY_QUIT:
                    return
                if key in KEY_RESTART:
                    _regenerate_maze(STATUS_NEW_GAME)
                    _animate_current_path()
                    needs_full_redraw[0] = True
                    win_handled = True
                    break
        if win_handled:
            continue
        key = stdscr.getch()
        if key == curses.KEY_MOUSE:
            continue
        if key in KEY_QUIT:
            break
        if key in KEY_TOGGLE_PATH:
            show_path = not show_path
            status_msg[0] = STATUS_PATH_ON if show_path else STATUS_PATH_OFF
            needs_full_redraw[0] = True
        elif key in KEY_RESTART:
            _regenerate_maze(STATUS_MAZE_REGENERATED)
            _animate_current_path()
        elif key in KEY_CHANGE_ALGORITHM:
            idx = ALGO_CYCLE.index(current_algo)
            current_algo = ALGO_CYCLE[(idx + 1) % len(ALGO_CYCLE)]
            _regenerate_maze(
                STATUS_ALGO_CHANGED.format(algo=current_algo))
        elif key in [ord('t'), ord('T')]:
            current_perfect = not current_perfect
            status_text = STATUS_PERFECT_ON if current_perfect \
                else STATUS_PERFECT_OFF
            _regenerate_maze(status_text)
        elif key in KEY_CHANGE_SEED:
            if output_file is None:
                status_msg[0] = STATUS_NO_OUTPUT_FILE
            else:
                try:
                    write_output_file(output_file, maze, start, end)
                    status_msg[0] = STATUS_SAVED.format(
                        output_file=output_file)
                except Exception as e:
                    status_msg[0] = STATUS_SAVE_ERROR.format(error=str(e))
            needs_full_redraw[0] = True
        elif key in KEY_CHANGE_COLOR:
            color_42 = COLOR_PATTERN_MIN + (color_42 % COLOR_PATTERN_WRAP)
            color_wall = COLOR_WALL_MIN + ((
                color_wall - COLOR_WALL_MIN + 1) % COLOR_WALL_WRAP)
            status_msg[0] = STATUS_COLORS_CHANGED.format(
                wall=color_wall, pattern=color_42
            )
            needs_full_redraw[0] = True
        elif key in [ord('g'), ord('G')]:
            new_seed = random.randint(0, MAX_SEED - 1)
            if current_seed is None:
                current_seed = new_seed
            else:
                while new_seed == current_seed:
                    new_seed = random.randint(0, MAX_SEED - 1)
                current_seed = new_seed
            _regenerate_maze(STATUS_SEED_UPDATED.format(seed=current_seed))
            _animate_current_path()
        elif key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT,
                     curses.KEY_RIGHT]:
            _update_player_cell(prev_player_pos[0], prev_player_pos[1], False)
            handle_movement(key, maze, player_pos)
            _update_player_cell(player_pos[0], player_pos[1], True)
            prev_player_pos = list(player_pos)
        else:
            handle_movement(key, maze, player_pos)
