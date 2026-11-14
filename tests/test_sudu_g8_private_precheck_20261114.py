"""Security regressions for the private technical precheck (NOT G8)."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sudu_g8_private_precheck_20261114 as stage


def valid_lesson():
    entry = {
        "teacher": "Teacher explanation that uses the correct option.",
        "elementary": "Plain-language explanation for younger students.",
        "reason": "Independently states why this choice fits or does not."
    }
    return {
        "teacherSummary": "A teacher-style summary of the reasoning.",
        "elementarySummary": "A younger student's understandable summary.",
        "memory": "Remember the key condition and final operation.",
        "concept": "Relevant mathematical or language principle.",
        "extension": "A short reverse or alternative check.",
        "source": "A source-bound official exam description.",
        "optionExplanations": {x: dict(entry) for x in "ABCD"},
        "hasExamCalculation": False,
        "examCalculation": None,
    }


class PrivateG8ContractTests(unittest.TestCase):
    def test_precheck_status_is_not_approval(self):
        self.assertEqual(stage.STATE, "TECHNICAL_PRECHECK_ONLY")
        self.assertNotEqual(stage.STATE, "STUDENT_QA_APPROVED")
        self.assertNotEqual(stage.STATE, "FORMAL_G8_16_OF_16")

    def test_valid_four_option_nonmath_and_calc(self):
        lesson = valid_lesson()
        self.assertTrue(stage._valid_author_teaching(lesson))
        lesson["hasExamCalculation"] = True
        lesson["examCalculation"] = {
            "given": ["A=2", "B=3"], "formulaUse": "C=A+B",
            "substitution": ["C=2+3"], "steps": ["2+3=5"],
            "result": "5", "option": "B"
        }
        self.assertTrue(stage._valid_author_teaching(lesson))

    def test_reject_missing_option_and_fake_maths(self):
        lesson = valid_lesson()
        del lesson["optionExplanations"]["D"]
        self.assertFalse(stage._valid_author_teaching(lesson))
        lesson = valid_lesson()
        lesson["hasExamCalculation"] = True
        self.assertFalse(stage._valid_author_teaching(lesson))
        lesson["examCalculation"] = {"given": ["x"], "formulaUse": "f",
                                     "substitution": [], "steps": ["x"],
                                     "result": "1", "option": "A"}
        self.assertFalse(stage._valid_author_teaching(lesson))
        lesson["hasExamCalculation"] = False
        lesson["examCalculation"] = {"given": ["should be hidden"]}
        self.assertFalse(stage._valid_author_teaching(lesson))

    def test_private_destination_must_be_os_temp_and_explicit_name(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "readonly-source"
            source.mkdir()
            private = Path(root) / "sudu-private-g8-test"
            self.assertEqual(stage._private_location(private, source), private)
            for target in (
                Path(root), Path(root) / "g8-not-private",
                Path.cwd() / "sudu-private-g8-forbidden",
                Path(root) / "sudu-private-g8-test" / "approved",
                source / "sudu-private-g8-forbidden"
            ):
                with self.subTest(target=target):
                    with self.assertRaises(stage.PrecheckHold):
                        stage._private_location(target, source)

    def test_reject_symlink_in_private_path(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "readonly-source"
            source.mkdir()
            actual = Path(root) / "actual"
            actual.mkdir()
            link = Path(root) / "sudu-private-g8-link"
            link.symlink_to(actual, target_is_directory=True)
            with self.assertRaises(stage.PrecheckHold):
                stage._private_location(link, source)

    def test_exclusive_local_file_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "private.txt"
            stage._exclusive_write(path, b"first")
            self.assertEqual(path.read_bytes(), b"first")
            with self.assertRaises(FileExistsError):
                stage._exclusive_write(path, b"forged")
            self.assertEqual(path.read_bytes(), b"first")
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_refuse_invalid_qid_and_fake_commit_before_read(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "source"
            source.mkdir()
            target = Path(root) / "sudu-private-g8-validation"
            with self.assertRaisesRegex(stage.PrecheckHold, "QID"):
                stage.build_private_precheck(
                    source, target, "116-00-E-11", "a" * 40, "b" * 64
                )
            with self.assertRaisesRegex(stage.PrecheckHold, "commit"):
                stage.build_private_precheck(
                    source, target, "114-00-E-11", "fake-commit", "b" * 64
                )
            with self.assertRaisesRegex(stage.PrecheckHold, "teaching"):
                stage.build_private_precheck(
                    source, target, "114-00-E-11", "a" * 40, "not-a-hash"
                )

    def test_no_preview_without_original_205_source_and_real_issuer(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "source"
            source.mkdir()
            destination = Path(root) / "sudu-private-g8-empty-source"
            with self.assertRaisesRegex(stage.PrecheckHold, "directory"):
                stage.build_private_precheck(
                    source, destination, "114-00-E-11", "a" * 40, "b" * 64
                )
            self.assertFalse(destination.exists())

    def test_private_stage_cannot_be_reinterpreted_as_trusted_v1(self):
        # This module must not insert a certificate into the trusted policy.
        self.assertFalse(hasattr(stage, "approve"))
        self.assertFalse(hasattr(stage, "write_trusted_registry"))
        self.assertFalse(hasattr(stage, "mark_student_ready"))
        self.assertEqual(stage.STATE, "TECHNICAL_PRECHECK_ONLY")


if __name__ == "__main__":
    unittest.main()
