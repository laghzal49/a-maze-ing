import random
from typing import Optional, Set, Tuple, List


class Maze:
    N, E, S, W = 1, 2, 4, 8
    FULL = N | E | S | W

    four_pattern = [
        (1, 1), (1, 2), (1, 3), (2, 3),
        (3, 3), (3, 4), (3, 5)
    ]

    two_pattern = [
        (0, 1), (1, 1), (2, 1),
        (2, 2),
        (0, 3), (1, 3), (2, 3),
        (0, 4),
        (0, 5), (1, 5), (2, 5)
    ]

    PATTERN_OFFSET = 5

    dirs = [
        (0, -1, N, S),
        (1, 0, E, W),
        (0, 1, S, N),
        (-1, 0, W, E),
    ]

    def __init__(self, width: int, height: int) -> None:
        """Initialize the maze with all walls intact."""
        self.width = width
        self.height = height
        self.walls: List[List[int]] = [[self.FULL for _ in range(width)]
                                       for _ in range(height)]
        self.blocked_cells: Set[Tuple[int, int]] = set()
        self.pattern_origin: Optional[Tuple[int, int]] = None
        self.pattern_size: Optional[Tuple[int, int]] = None

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if (x, y) is within the maze boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x: int, y: int) -> bool:
        """Check if (x, y) is a blocked cell."""
        return (x, y) in self.blocked_cells

    def reset(self) -> None:
        """Reset the maze to its initial state with all walls intact."""
        for y in range(self.height):
            for x in range(self.width):
                self.walls[y][x] = self.FULL
        self.blocked_cells.clear()
        self.pattern_origin = None
        self.pattern_size = None

    def create_42_pattern(self) -> bool:
        """Create the 42 pattern in the maze."""
        self.blocked_cells.clear()
        self.pattern_origin = None
        self.pattern_size = None

        max_four_x = max(dx for dx, _ in self.four_pattern)
        max_four_y = max(dy for _, dy in self.four_pattern)
        max_two_x = max(dx for dx, _ in self.two_pattern) + self.PATTERN_OFFSET
        max_two_y = max(dy for _, dy in self.two_pattern)

        pattern_width = max(max_four_x, max_two_x) + 1
        pattern_height = max(max_four_y, max_two_y) + 1

        ox = self.width // 2 - pattern_width // 2
        oy = self.height // 2 - pattern_height // 2

        if (
            ox < 0 or oy < 0
            or ox + pattern_width > self.width
            or oy + pattern_height > self.height
            or ox > 9 or oy > 9
        ):
            return False

        self.pattern_origin = (ox, oy)
        self.pattern_size = (pattern_width, pattern_height)

        for dx, dy in self.four_pattern:
            self.blocked_cells.add((ox + dx, oy + dy))

        for dx, dy in self.two_pattern:
            self.blocked_cells.add((ox + self.PATTERN_OFFSET + dx, oy + dy))

        for x, y in self.blocked_cells:
            if self.in_bounds(x, y):
                self.walls[y][x] = self.FULL
        return True

    def _carve_passage(
        self,
        cx: int,
        cy: int,
        nx: int,
        ny: int,
        w_bit: int,
        opp_bit: int,
    ) -> None:
        """Carve a passage between two cells by removing the walls."""
        self.walls[cy][cx] &= ~w_bit
        self.walls[ny][nx] &= ~opp_bit

    def _neighbors_all(
        self, x: int, y: int, rng: Optional[random.Random] = None
    ) -> List[Tuple[int, int, int, int]]:
        """All valid (in-bounds, not blocked) neighbors."""
        directions = list(self.dirs)
        if rng is not None:
            rng.shuffle(directions)

        out: List[Tuple[int, int, int, int]] = []
        for dx, dy, w_bit, opp_bit in directions:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and not self.is_blocked(nx, ny):
                out.append((nx, ny, w_bit, opp_bit))
        return out

    def _neighbors_unvisited(
        self, x: int, y: int, visited: Set[Tuple[int, int]],
            rng: Optional[random.Random] = None
            ) -> List[Tuple[int, int, int, int]]:
        """Neighbors that are NOT visited."""
        return [
            n for n in self._neighbors_all(x, y, rng)
            if (n[0], n[1]) not in visited
            ]

    def _neighbors_visited(
            self, x: int, y: int, visited: Set[Tuple[int, int]],
            rng: Optional[random.Random] = None
            ) -> List[Tuple[int, int, int, int]]:
        """Neighbors that ARE visited."""
        return [
            n for n in self._neighbors_all(x, y, rng)
            if (n[0], n[1]) in visited
            ]

    def _first_open_cell(self) -> Optional[Tuple[int, int]]:
        """Return the first non-blocked cell in row-major order."""
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_blocked(x, y):
                    return (x, y)
        return None

    def generate_maze(
        self,
        seed: Optional[int] = None,
        algo: str = "prim",
        perfect: bool = True,
    ) -> None:
        """Generate a maze using the specified algorithm."""
        rng = random.Random(str(seed) if seed is not None else None)
        self.reset()
        self.create_42_pattern()

        algo_map = {
            "prim": self._prim_algo,
            "dfs": self._dfs_algo,
            "hunt": self._hunt_and_kill,
        }

        algo_func = algo_map.get(algo, self._prim_algo)
        algo_func(rng)

        if not perfect:
            self._add_loops(rng, loop_chance=0.1)

    def _dfs_algo(self, rng: random.Random) -> None:
        """Generate a maze using the Depth-First Search algorithm."""
        visited = set(self.blocked_cells)
        start = self._first_open_cell()
        if not start:
            return
        stack = [start]
        visited.add(start)
        while stack:
            cx, cy = stack[-1]
            neighbors = self._neighbors_unvisited(cx, cy, visited, rng)
            if not neighbors:
                stack.pop()
                continue
            nx, ny, w_bit, opp_bit = rng.choice(neighbors)
            self._carve_passage(cx, cy, nx, ny, w_bit, opp_bit)
            visited.add((nx, ny))
            stack.append((nx, ny))

    def _prim_algo(self, rng: random.Random) -> None:
        """Generate a maze using Prim's algorithm."""
        visited: Set[Tuple[int, int]] = set(self.blocked_cells)

        start = self._first_open_cell()
        if not start:
            return

        visited.add(start)
        frontier: List[Tuple[int, int, int, int, int, int]] = []

        def add_frontier(cx: int, cy: int) -> None:
            """Add the neighboring cells of (cx, cy) to the frontier."""
            for nx, ny, w_bit, opp_bit in \
                    self._neighbors_unvisited(cx, cy, visited, rng):
                frontier.append((cx, cy, nx, ny, w_bit, opp_bit))

        add_frontier(start[0], start[1])

        while frontier:
            idx = rng.randrange(len(frontier))
            frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
            cx, cy, nx, ny, w_bit, opp_bit = frontier.pop()
            if (nx, ny) in visited:
                continue
            self._carve_passage(cx, cy, nx, ny, w_bit, opp_bit)
            visited.add((nx, ny))
            add_frontier(nx, ny)

    def _hunt_and_kill(self, rng: random.Random) -> None:
        """Generate a maze using the Hunt-and-Kill algorithm."""
        visited = set(self.blocked_cells)
        start = self._first_open_cell()
        if not start:
            return
        cx, cy = start
        visited.add((cx, cy))

        while True:
            # Kill phase
            while nbrs := self._neighbors_unvisited(cx, cy, visited, rng):
                nx, ny, w, o = rng.choice(nbrs)
                self._carve_passage(cx, cy, nx, ny, w, o)
                cx, cy = nx, ny
                visited.add((cx, cy))

            # Hunt phase — must be INSIDE the outer while True
            found = False
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in visited and not self.is_blocked(x, y):
                        if vn := self._neighbors_visited(x, y, visited, rng):
                            nx, ny, w, o = rng.choice(vn)
                            self._carve_passage(x, y, nx, ny, w, o)
                            cx, cy = x, y
                            visited.add((cx, cy))
                            found = True
                            break
                if found:
                    break

            if not found:
                break

    def _add_loops(self, rng: random.Random, loop_chance: float = 0.1) -> None:
        """Randomly add loops to the maze."""
        for y in range(self.height):
            for x in range(self.width):
                if self.is_blocked(x, y):
                    continue
                if rng.random() >= loop_chance:
                    continue
                choices = list(self._neighbors_all(x, y, rng=rng))
                if not choices:
                    continue
                nx, ny, w_bit, opp_bit = rng.choice(choices)
                self._carve_passage(x, y, nx, ny, w_bit, opp_bit)
