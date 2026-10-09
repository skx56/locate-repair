from pathlib import Path


def read_note(root: str, name: str) -> str:
    root_path = Path(root).resolve()
    path = (root_path / name).resolve()
    if path != root_path and root_path not in path.parents:
        raise PermissionError(name)
    return path.read_text(encoding="utf-8")
