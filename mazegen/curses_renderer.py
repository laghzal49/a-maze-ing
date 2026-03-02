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

    min_rows = maze.height * 2 + 1
    min_cols = maze.width * 4 + 1
    if not terminal_big_enough(stdscr, min_rows, min_cols):
        show_terminal_too_small(stdscr, min_rows, min_cols)
        return

    h = maze.height
    color_42 = 3
    color_wall = 4
    algo_cycle = ["dfs", "prim", "hunt"]
    current_algo = algo if algo in algo_cycle else "dfs"
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
    maze_rows = h * 2 + 1
    maze_cols = maze.width * 4 + 1

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
            row = maze_top + y * 2 + 1  # Account for wall rows
            if row >= max_y:
                return
            color = color_wall
            if is_player:
                content = " ⦻ "
                color = 6
            elif show_path and (x, y) in path_set:
                content = "   "
                color = 1
            else:
                content = "   "
            col = maze_left + x * 4 + 1
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
        for jy in range(h + 1):
            if row >= max_y:
                break

            line_wall = build_wall_line(
                maze, jy, color_wall, horiz, vert
            )
            draw_maze_line(stdscr, row, line_wall, maze_left, max_x)
            row += 1

            if jy == h or row >= max_y:
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
            override_status="Animating path... (press Q to skip)",
        )
        animate_path(
            stdscr,
            saved_path,
            lambda partial: _render_frame(
                current_path_set=partial,
                override_status="Animating path... (press Q to skip)"
            ),
        )
        path_set.update(saved_path)
        needs_full_redraw[0] = True
    _regenerate_maze("Ready to play (Use ARROWS)")
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
            status_msg[0] = "You won! Press R to play again or Q to quit."
            _render_frame()
            while True:
                key = stdscr.getch()
                if key in [ord('q'), ord('Q')]:
                    return
                if key in [ord('r'), ord('R')]:
                    _regenerate_maze("New Game Started.")
                    _animate_current_path()
                    needs_full_redraw[0] = True
                    win_handled = True
                    break
        if win_handled:
            continue
        key = stdscr.getch()
        if key == curses.KEY_MOUSE:
            continue
        if key in [ord('q'), ord('Q')]:
            break
        if key in [ord('p'), ord('P')]:
            show_path = not show_path
            status_msg[0] = f"Path display {'ON' if show_path else 'OFF'}."
            needs_full_redraw[0] = True
        elif key in [ord('r'), ord('R')]:
            _regenerate_maze(
                "Maze regenerated. And ready to play (use ARROWS)")
            _animate_current_path()
        elif key in [ord('a'), ord('A')]:
            idx = algo_cycle.index(current_algo)
            current_algo = algo_cycle[(idx + 1) % len(algo_cycle)]
            _regenerate_maze(
                f"Algorithm set to"
                f" {current_algo} and ready to play (use ARROWS).")
        elif key in [ord('t'), ord('T')]:
            current_perfect = not current_perfect
            _regenerate_maze(
                f"Perfect mode {'ON' if current_perfect else 'OFF'}."
            )
        elif key in [ord('s'), ord('S')]:
            if output_file is None:
                status_msg[0] = "Error: no output file configured."
            else:
                try:
                    write_output_file(output_file, maze, start, end)
                    status_msg[0] = f"Saved to {output_file}."
                except Exception as e:
                    status_msg[0] = f"Error: {e}"
            needs_full_redraw[0] = True
        elif key in [ord('c'), ord('C')]:
            color_42 = 3 + (color_42 % 5)
            color_wall = 4 + ((color_wall - 4 + 1) % 4)
            status_msg[0] = (
                f"Colors changed (wall pair {color_wall}, 42 pair {color_42})."
            )
            needs_full_redraw[0] = True
        elif key in [ord('g'), ord('G')]:
            new_seed = random.randint(0, 2**31 - 1)
            if current_seed is None:
                current_seed = new_seed
            else:
                while new_seed == current_seed:
                    new_seed = random.randint(0, 2**31 - 1)
                current_seed = new_seed
            _regenerate_maze(f"Seed updated: {current_seed}.")
            _animate_current_path()
        elif key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT,
                     curses.KEY_RIGHT]:
            _update_player_cell(prev_player_pos[0], prev_player_pos[1], False)
            handle_movement(key, maze, player_pos)
            _update_player_cell(player_pos[0], player_pos[1], True)
            prev_player_pos = list(player_pos)
        else:
            handle_movement(key, maze, player_pos)
