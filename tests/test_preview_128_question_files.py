#!/usr/bin/env python3
"""Regression: a sidecar audit JSON must not count as a 129th question."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from preview_128_question_files import canonical_question_json_files


class FrozenQuestionFilenameTests(unittest.TestCase):
    def test_sidecar_is_excluded_but_unknown_question_is_not(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in (
                "115-00-MB-05.json", "114-00-C-02.json", "115-09-2-28.json",
                "115-00-MB-26.json",
                "115-00-MB-05-pedagogy-review-20261024.json",
                "115-00-MB-05-source-evidence-01.json",
            ):
                (folder / name).write_text("{}", encoding="utf-8")
            self.assertEqual(
                [p.stem for p in canonical_question_json_files(folder)],
                ["114-00-C-02", "115-00-MB-05", "115-00-MB-26", "115-09-2-28"],
            )

    def test_exact_frozen_128_question_set(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / "sudu/teaching-drafts/preview-128-20261023"
        frozen = json.loads((folder / "progress.json").read_text(encoding="utf-8"))
        expected = {x["questionId"] for x in frozen["items"]}
        self.assertEqual(len(expected), 128)
        self.assertEqual({p.stem for p in canonical_question_json_files(folder)}, expected)


if __name__ == "__main__":
    unittest.main()
