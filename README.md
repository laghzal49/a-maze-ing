# A-Maze-ing --- This is the Way

*Created as part of the 42 curriculum by **tlaghzal** and **mel-asla***

------------------------------------------------------------------------

## Overview

**A-Maze-ing** is a Python 3.10+ maze generator and terminal renderer.

It: - Reads a configuration file\
- Generates a maze using multiple algorithms\
- Optionally embeds a visible "42" blocked pattern\
- Computes the shortest path (BFS)\
- Exports a compact hex-encoded maze file\
- Renders the maze using curses (interactive) or ASCII fallback

The project works both as: - A runnable application (`a_maze_ing.py`) -
A reusable Python module (`mazegen/`)

------------------------------------------------------------------------

## Quick Start

python3 a_maze_ing.py config.txt

------------------------------------------------------------------------

## Makefile Targets

make install\
make run\
make debug\
make lint\
make clean\
make build

# If python3 -m venv fails:

python3 -m pip install --user virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate

------------------------------------------------------------------------

## Configuration File

Each line is:

KEY=VALUE

Mandatory:

WIDTH=20\
HEIGHT=15\
ENTRY=0,0\
EXIT=19,14\
OUTPUT_FILE=maze.txt\
PERFECT=True

Optional:

SEED=42\
ALGO=dfs\
DELAY=0.05

------------------------------------------------------------------------

## Algorithms

-   DFS (Recursive Backtracker)\
-   Prim's Algorithm\
-   Hunt-and-Kill

If PERFECT=False, random loops are added.

------------------------------------------------------------------------

## Maze Model

Each cell uses 4-bit wall encoding:

North = 1\
East = 2\
South = 4\
West = 8

Initial value = 15 (all walls closed).

------------------------------------------------------------------------

## Output Format

-   One hex digit per cell (0--F)\
-   One row per line

After a blank line:

entry_x,entry_y\
exit_x,exit_y\
NESW path string

------------------------------------------------------------------------

## Team Contributions

**tlaghzal** - Maze generation algorithms\
- Perfect/non-perfect logic\
- Bitmask wall system\
- Config parsing & validation

**mel-asla** - Rendering system (curses + ASCII)\
- UI controls\
- Output writer\
- Integration & packaging
- Bonus
------------------------------------------------------------------------

## AI Usage

AI assisted with documentation drafting and reviewing edge cases.\
All core logic and rendering systems were implemented and verified by
the team.