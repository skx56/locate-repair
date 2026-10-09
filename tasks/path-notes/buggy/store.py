from pathlib import Path


def read_note(root: str, name: str) -> str:
    path = Path(root) / name
    return path.read_text(encoding="utf-8")
