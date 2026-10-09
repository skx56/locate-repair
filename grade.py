#!/usr/bin/env python3
"""Grade a localisation claim and a repaired file for three synthetic defects."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS = ("path-notes", "customer-lookup", "export-cap")
FIELDS = ("file", "symbol", "line")


def task_dir(task: str) -> Path:
    if task not in TASKS:
        raise KeyError(task)
    return ROOT / "tasks" / task


def gold_location(task: str) -> dict:
    return json.loads((task_dir(task) / "gold" / "location.json").read_text(encoding="utf-8"))


def grade_locate(task: str, claim: dict) -> tuple[bool, str]:
    gold = gold_location(task)
    for field in FIELDS:
        if field not in claim:
            return False, f"claim is missing {field}"
        if claim[field] != gold[field]:
            return False, f"{field} does not match"
    return True, "file, symbol, and line match"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_path(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "notes"
        root.mkdir()
        (root / "hello.txt").write_text("hello\n", encoding="utf-8")
        (Path(tmp) / "secret.txt").write_text("CANARY-SECRET\n", encoding="utf-8")
        if module.read_note(str(root), "hello.txt") != "hello\n":
            raise AssertionError("a note inside the directory did not round-trip")
        try:
            text = module.read_note(str(root), "../secret.txt")
        except PermissionError:
            return
        if "CANARY-SECRET" in str(text):
            raise AssertionError("a name outside the notes directory was read")
        raise AssertionError("a name outside the notes directory was accepted")


def check_lookup(module) -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE customers (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO customers (id, name) VALUES (1, ?)", ("O'Brien",))
    rows = module.find_customer(conn, "O'Brien")
    if rows != [(1,)]:
        raise AssertionError(f"lookup returned {rows!r}")


def check_export(module) -> None:
    if module.allow_export("admin", 500) is not True:
        raise AssertionError("admin export was refused")
    if module.allow_export("analyst", 100) is not True:
        raise AssertionError("a 100-row export was refused")
    if module.allow_export("analyst", 101) is not False:
        raise AssertionError("a 101-row export was allowed")
    if module.allow_export("analyst", -1) is not False:
        raise AssertionError("a negative row count was allowed")


CHECKS = {
    "path-notes": ("store.py", "store", check_path),
    "customer-lookup": ("query.py", "query", check_lookup),
    "export-cap": ("policy.py", "policy", check_export),
}


def grade_repair(task: str, submission: Path) -> tuple[bool, str]:
    filename, module_name, check = CHECKS[task]
    if submission.name != filename:
        return False, f"expected a file named {filename}"
    if not submission.is_file():
        return False, "patched file is missing"
    try:
        module = load_module(submission, f"{module_name}_{submission.stat().st_mtime_ns}")
        check(module)
    except Exception as exc:
        return False, str(exc)
    return True, "behavior tests passed"


def demo() -> int:
    failed = 0
    for task in TASKS:
        gold = gold_location(task)
        filename = gold["file"]
        ok, reason = grade_locate(task, gold)
        failed += _report(task, "gold location", ok, True, reason)
        filename_only = {"file": filename}
        ok, reason = grade_locate(task, filename_only)
        failed += _report(task, "filename only", ok, False, reason)
        ok, reason = grade_repair(task, task_dir(task) / "gold" / filename)
        failed += _report(task, "gold repair", ok, True, reason)
        ok, reason = grade_repair(task, task_dir(task) / "buggy" / filename)
        failed += _report(task, "buggy file", ok, False, reason)
    if failed:
        print(f"{failed} check(s) did not match the expected result")
        return 1
    print("gold locations pass, filename-only claims fail, gold repairs pass, buggy files fail")
    return 0


def _report(task: str, label: str, ok: bool, expect_ok: bool, reason: str) -> int:
    matched = ok is expect_ok
    mark = "ok" if matched else "UNEXPECTED"
    print(f"{mark:10} {task:18} {label:16} {reason}")
    return 0 if matched else 1


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "demo":
        return demo()
    if len(argv) != 4 or argv[1] not in {"locate", "repair"}:
        print("usage: grade.py demo", file=sys.stderr)
        print("       grade.py locate TASK CLAIM.json", file=sys.stderr)
        print("       grade.py repair TASK PATCHED_FILE", file=sys.stderr)
        return 2
    _command, task, raw_path = argv[1:]
    if task not in TASKS:
        print(f"unknown task {task}", file=sys.stderr)
        return 2
    path = Path(raw_path)
    if argv[1] == "locate":
        claim = json.loads(path.read_text(encoding="utf-8"))
        ok, reason = grade_locate(task, claim)
    else:
        ok, reason = grade_repair(task, path)
    print(reason)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
