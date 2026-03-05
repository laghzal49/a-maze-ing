"""Configuration parser for maze generation."""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any


@dataclass
class MazeConfig:
    """Configuration for maze generation."""
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algo: str = "dfs"


def _parse_bool(value: str) -> bool:
    value_lower = value.strip().lower()
    if value_lower == "true":
        return True
    if value_lower == "false":
        return False
    raise ValueError("PERFECT must be True or False")


def _validate_config(config: Dict[str, Any]) -> MazeConfig:
    width = config.get("width")
    height = config.get("height")
    entry = config.get("entry")
    exit_pos = config.get("exit")
    output_file = config.get("output_file")
    perfect = config.get("perfect")

    if width is None or height is None:
        raise ValueError("WIDTH and HEIGHT are required")
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("WIDTH and HEIGHT must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive")

    def _validate_point(name: str, p: Any) -> Tuple[int, int]:
        if p is None:
            raise ValueError(f"{name} is required")
        if not isinstance(p, tuple) or len(p) != 2:
            raise ValueError(f"{name} must be in x,y format")
        x, y = p
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"{name} coordinates must be integers")
        return x, y

    ex, ey = _validate_point("ENTRY", entry)
    xx, xy = _validate_point("EXIT", exit_pos)

    if (ex, ey) == (xx, xy):
        raise ValueError("ENTRY and EXIT must be different")
    if not (0 <= ex < width and 0 <= ey < height):
        raise ValueError("ENTRY is out of bounds")
    if not (0 <= xx < width and 0 <= xy < height):
        raise ValueError("EXIT is out of bounds")

    if output_file is None:
        raise ValueError("OUTPUT_FILE is required")
    if not isinstance(output_file, str) or not output_file.strip():
        raise ValueError("OUTPUT_FILE must be a non-empty filename")

    if perfect is None:
        raise ValueError("PERFECT is required")
    if not isinstance(perfect, bool):
        raise ValueError("PERFECT must be True or False")

    algo = config.get("algo", "dfs")
    if not isinstance(algo, str):
        raise ValueError("ALGO must be a string")
    algo_l = algo.lower()
    if algo_l not in {"dfs", "prim", "hunt"}:
        raise ValueError("ALGO must be 'dfs', 'prim', or 'hunt'")
    algo = algo_l

    seed = config.get("seed")
    if seed is not None and not isinstance(seed, int):
        raise ValueError("SEED must be an integer")
    return MazeConfig(
        width=width,
        height=height,
        entry=(ex, ey),
        exit=(xx, xy),
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algo=algo,
    )


def parse_dict(raw: Dict[str, Any]) -> MazeConfig:
    """Parse configuration from a dict (tests/helpers)."""
    return _validate_config(raw)


def parse_file(filepath: str) -> MazeConfig:
    """Parse configuration from text file.

    File format (one key=value per line):
    WIDTH=30
    HEIGHT=20
    ENTRY=0,0
    EXIT=29,19
    SEED=42
    ALGO=dfs

    Args:
        filepath: Path to configuration file

    Returns:
        MazeConfig: Configuration object

    Raises:
        FileNotFoundError: If file not found
        ValueError: If parsing fails
    """
    config: Dict[str, Any] = {}

    def set_once(name: str, val: Any, line_num: int) -> None:
        if name in config:
            raise ValueError(
                f"Line {line_num}: Duplicate key '{name.upper()}'")
        config[name] = val

    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Line {line_num}: Invalid format, expected KEY=VALUE"
                )

            key, value = line.split("=", 1)
            key = key.strip().upper()
            value = value.strip()

            try:
                if key == "WIDTH":
                    set_once("width", int(value), line_num)
                elif key == "HEIGHT":
                    set_once("height", int(value), line_num)
                elif key == "ENTRY":
                    coords = tuple(map(int, value.split(",")))
                    if len(coords) != 2:
                        raise ValueError("Must have exactly 2 coordinates")
                    set_once("entry", coords, line_num)
                elif key == "EXIT":
                    coords = tuple(map(int, value.split(",")))
                    if len(coords) != 2:
                        raise ValueError("Must have exactly 2 coordinates")
                    set_once("exit", coords, line_num)
                elif key == "OUTPUT_FILE":
                    set_once("output_file", value, line_num)
                elif key == "PERFECT":
                    set_once("perfect", _parse_bool(value), line_num)
                elif key == "SEED":
                    set_once("seed", int(value), line_num)
                elif key == "ALGO":
                    set_once("algo", value.lower(), line_num)
                else:
                    raise ValueError(f"Unknown key '{key}'")
            except ValueError as e:
                raise ValueError(f"Line {line_num}: {e}")

    return _validate_config(config)
