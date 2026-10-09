import json
import unittest
from pathlib import Path

import grade

ROOT = Path(__file__).resolve().parents[1]


class LocateRepairTest(unittest.TestCase):
    def test_gold_location_passes(self) -> None:
        for task in grade.TASKS:
            claim = grade.gold_location(task)
            ok, reason = grade.grade_locate(task, claim)
            self.assertTrue(ok, f"{task}: {reason}")

    def test_filename_only_fails(self) -> None:
        ok, reason = grade.grade_locate("path-notes", {"file": "store.py"})
        self.assertFalse(ok, reason)
        self.assertIn("symbol", reason)

    def test_wrong_line_fails(self) -> None:
        claim = grade.gold_location("export-cap")
        claim["line"] = 1
        ok, reason = grade.grade_locate("export-cap", claim)
        self.assertFalse(ok, reason)
        self.assertIn("line", reason)

    def test_gold_repairs_pass_and_buggy_files_fail(self) -> None:
        for task in grade.TASKS:
            filename = grade.gold_location(task)["file"]
            folder = ROOT / "tasks" / task
            ok, reason = grade.grade_repair(task, folder / "gold" / filename)
            self.assertTrue(ok, f"{task} gold: {reason}")
            ok, reason = grade.grade_repair(task, folder / "buggy" / filename)
            self.assertFalse(ok, f"{task} buggy should fail, got {reason}")

    def test_demo_exits_clean(self) -> None:
        self.assertEqual(grade.demo(), 0)

    def test_location_json_matches_loader(self) -> None:
        for task in grade.TASKS:
            path = ROOT / "tasks" / task / "gold" / "location.json"
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["file"], grade.gold_location(task)["file"])


if __name__ == "__main__":
    unittest.main()
