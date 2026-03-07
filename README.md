# A-Maze-ing — This is the Way

*This project has been created as part of the 42 curriculum by tlaghzal, mel-asla*

---

## Description

**A-Maze-ing** is a Python 3.10+ maze generator and interactive terminal renderer.

Given a configuration file, it generates a random maze using one of three algorithms, optionally embeds a visible **"42" pattern** made of fully blocked cells, computes the shortest path using BFS, and exports the maze in a compact hex-encoded format. The maze can be explored interactively in the terminal using curses, or rendered as plain ASCII.

The project is split into two parts:
- A runnable application (`a_maze_ing.py`) that reads a config file and drives the full experience
- A reusable Python package (`mazegen/`) that can be installed via pip and used independently

---

## Instructions

### Requirements

- Python 3.10 or later
- pip

### Install dependencies

```bash
make install
```

### Run

```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

### Debug

```bash
make debug
```

### Lint

```bash
make lint         # standard checks
make lint-strict  # strict mypy
```

### Clean

```bash
make clean
```

### Build the reusable package

```bash
make build
```

This produces `dist/mazegen-1.0.0-py3-none-any.whl`.

### Virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

---

## Configuration File

The program takes a single argument: a plain text config file with `KEY=VALUE` pairs.  
Lines starting with `#` are treated as comments and ignored.

### Mandatory keys

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates | `ENTRY=0,0` |
| `EXIT` | Exit coordinates | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Single path between entry and exit | `PERFECT=True` |

### Optional keys

| Key | Description | Example |
|---|---|---|
| `SEED` | Seed for reproducibility | `SEED=42` |
| `ALGO` | Algorithm: `prim`, `dfs`, `hunt` | `ALGO=dfs` |

### Example config

```
# A-Maze-ing config
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGO=prim
```

---

## Maze Generation Algorithms

### Prim's Algorithm (default)

Grows the maze outward from a starting cell by randomly picking from a pool of candidate passages at the frontier of the visited area. Produces wide, branchy mazes with many short dead ends.

### Depth-First Search (Recursive Backtracker)

Walks randomly from a starting cell, backtracking when stuck. Produces mazes with long winding corridors and fewer branches.

### Hunt-and-Kill

Walks randomly until stuck (kill phase), then scans the grid for the first unvisited cell touching the existing maze and reconnects from there (hunt phase). Produces a mix of long corridors and occasional sharp branches.

### Why these algorithms?

We chose these three because they represent fundamentally different generation strategies — frontier expansion, depth-first walk, and scan-and-reconnect — which produce visually distinct mazes. Prim's was chosen as the default because it tends to produce the most balanced and visually interesting results. All three support seeded reproducibility and optional loop injection for imperfect mazes.

---

## Maze Model

Each cell stores its wall state as a 4-bit integer:

| Direction | Bit | Value |
|---|---|---|
| North      | 0  | 1 |
| East       | 1  | 2 |
| South      | 2  | 4 |
| West       | 3  | 8 |

Initial state is `15` (all walls closed, binary `1111`). Carving a passage clears the corresponding bits on both sides of the wall.

---

## Output File Format

- One hexadecimal digit per cell (`0`–`F`)
- One row per line
- After a blank line, three additional lines:
  - Entry coordinates: `x,y`
  - Exit coordinates: `x,y`
  - Shortest path as a string of directions: `N`, `E`, `S`, `W`

### Example

```
fbe...
...
19,14
EESSWW...
```

---

## Reusable Module

The `mazegen` package can be installed independently and used in other projects.

### Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen.maze_generator import Maze

# Create and generate a maze
maze = Maze(width=20, height=15)
maze.generate_maze(seed=42, algo="prim", perfect=True)

# Access wall data
walls = maze.walls[y][x]  # 4-bit int per cell

# Check if a cell is blocked (part of the 42 pattern)
maze.is_blocked(x, y)

# Check bounds
maze.in_bounds(x, y)

# Pattern metadata
maze.pattern_origin  # (ox, oy) tuple or None
maze.pattern_size    # (width, height) tuple or None
```

### Custom parameters

```python
# Different algorithms
maze.generate_maze(algo="dfs")   # Depth-First Search
maze.generate_maze(algo="hunt")  # Hunt-and-Kill
maze.generate_maze(algo="prim")  # Prim's (default)

# Imperfect maze with loops
maze.generate_maze(seed=42, perfect=False)

# Reproducible — same seed always gives the same maze
maze.generate_maze(seed=42)
```

### Access the solution

```python
from mazegen.path_finder import find_path

path = find_path(maze, start=(0, 0), end=(19, 14))
# Returns list of (x, y) tuples, or None if no path exists
```

---

## Interactive Controls

| Key | Action |
|---|---|
| Arrow keys | Move player |
| `P` | Toggle shortest path display |
| `R` | Regenerate maze |
| `A` | Cycle algorithm |
| `T` | Toggle perfect/imperfect |
| `G` | Set seed |
| `S` | Save maze to file |
| `C` | Toggle wall colour / 42 pattern |
| `Q` | Quit |

---

## Team & Project Management

### Roles

**tlaghzal**
- Maze generation algorithms (Prim, DFS, Hunt-and-Kill)
- Bitmask wall system
- Perfect / imperfect maze logic
- Configuration parsing and validation
- Output file writer

**mel-asla**
- Rendering system (curses + ASCII fallback)
- UI controls and player movement
- Integration, packaging, and bonuses

### Planning

We began by designing the maze data model and wall encoding before writing any generation code. The first working version used only DFS, which we then extended to Prim and Hunt-and-Kill. The curses renderer was developed in parallel once the maze structure was stable. Integration took longer than expected due to edge cases in the 42 pattern sizing logic and the hex output format. We managed the project using Git with feature branches and daily syncs.

### What worked well

- Separating generation logic from rendering from the start made both easier to develop and test independently
- Using a seed-based `random.Random` instance made debugging reproducible
- The reusable module structure was planned early, which avoided a messy refactor at the end

### What could be improved

- We underestimated the time needed for the curses UI edge cases
- More unit tests from the beginning would have caught the wall coherence bugs earlier

### Tools used

- Python 3.10, curses, mypy, flake8
- pytest for unit testing
- Git / GitHub for version control
- VS Code as main editor

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth — Maze algorithms](https://www.astrolog.org/labyrnth/algrithm.htm)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [BFS shortest path — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)

### AI usage

AI was used to assist with documentation drafting, reviewing edge cases in algorithm logic, and identifying bugs in the wall encoding system. All core generation algorithms, rendering code, and output formatting were implemented and verified by the team. AI-generated suggestions were always reviewed, tested, and understood before being included.