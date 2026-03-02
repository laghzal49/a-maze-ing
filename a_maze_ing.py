"""A-maze-ing: Maze generator and solver with interactive visualization."""

import sys
import curses
from typing import Tuple

from mazegen.maze_generator import Maze
from mazegen.parser import parse_file
from mazegen.curses_renderer import render_maze_curses
from mazegen.output_writer import write_output_file


def _validate_entry_exit(
    maze: Maze,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
) -> None:
    """Validate Entry and Exit"""
    if entry == exit_pos:
        raise ValueError("ENTRY and EXIT must be different")
    if not (maze.in_bounds(*entry) and maze.in_bounds(*exit_pos)):
        raise ValueError("ENTRY or EXIT out of bounds")
    if maze.is_blocked(*entry) or maze.is_blocked(*exit_pos):
        raise ValueError("ENTRY or EXIT is inside the 42 pattern")


def main() -> None:
    """Main entry point for A-maze-ing interactive maze generator."""
    try:
        config_file = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
        config = parse_file(config_file)

        maze = Maze(config.width, config.height)
        maze.generate_maze(seed=config.seed, algo=config.algo,
                           perfect=config.perfect)

        if maze.pattern_origin is None:
            print(
                "Error: maze too small to place the 42 pattern. "
                "Continuing without it."
            )

        _validate_entry_exit(maze, config.entry, config.exit)

        try:
            write_output_file(config.output_file, maze,
                              config.entry, config.exit)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        curses.wrapper(
            render_maze_curses,
            maze,
            config.entry,
            config.exit,
            config.algo,
            config.seed,
            config.perfect,
            config.output_file,
        )

    except FileNotFoundError:
        print("Error: configuration file not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExited by user.")
        sys.exit(0)
    except AttributeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
