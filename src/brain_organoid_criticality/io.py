from pathlib import Path


def validate_path(path: str | Path) -> Path:
    """Return a Path object and raise an error if it does not exist."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    return p