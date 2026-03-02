"""Animation helpers for the curses UI."""
from __future__ import annotations
import curses
from typing import Callable, List, Protocol, Set, Tuple
import time


class CursesWindow(Protocol):
    """Subset of curses window methods used here."""

    def timeout(self, delay: int) -> None: ...

    def nodelay(self, flag: bool) -> None: ...

    def getch(self) -> int: ...


def animate_path(
    stdscr: CursesWindow,
    path: List[Tuple[int, int]],
    draw_frame: Callable[[Set[Tuple[int, int]]], None],
    delay_ms: int = 30,
    initial_pause: float = 0.7,
) -> None:
    """Animate the path by drawing partial prefixes."""

    total_steps = len(path)
    if total_steps == 0:
        return

    curses.flushinp()
    time.sleep(initial_pause)

    stdscr.timeout(0)
    for step in range(1, total_steps + 1):
        draw_frame(set(path[:step]))
        curses.napms(delay_ms)
        stdscr.nodelay(True)
        key = stdscr.getch()
        stdscr.nodelay(False)
        if key in (ord("q"), ord("Q")):
            stdscr.timeout(-1)
            return
    stdscr.timeout(-1)
