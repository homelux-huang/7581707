"""Regression tests: candidate extraction is not answer, E, D, READY or LIVE approval."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from importlib.util import module_from_spec, spec_from_file_location

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sudu_free_first_progress.py"
spec = spec_from_file_location("free_first", SCRIPT)
free_first = module_from_spec(spec)
spec.loader.exec_module(free_first)


def fake_repo(root: Path):
    for year in free_first.YEARS:
        location = root / "sudu" / "data" / "years"
        location.mkdir(parents=True, exist_ok=True)
        papers = []
        for paper in sorted(free_first.PAPER_CODES):
            qid = f"{year}-{paper}-01"
            papers.append({
                "paper": paper,
                "questions": [{
                    "id": qid, "paper": paper, "year": year,
                    "question": "自動擷取待複核",
                    "answerMatched": True,
                    "answerVerified": False,
                    "questionVerified": False,
                    "teachingVerified": False,
                    "issues": [],
                }]
            })
        doc = {
            "year": year,
            "sourceIndex": f"https://web1.tcte.edu.tw/EXAM/{year}_4y/",
            "papers": papers,
            "questionsFound": 4,
        }
        (location / f"{year}.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        if year in free_first.APPROVED_YEARS:
            folder = root / "sudu" / "data" / "approved"
            folder.mkdir(parents=True, exist_ok=True)
            qs = [{
                "canonicalId": f"{year}-00-C-01",
                "imageSha256": "a" * 64,
            }] if year == 115 else []
            approved = {
                "year": year, "expected": 5, "approvedCount": len(qs),
                "sourceSha": "original-source-immutable-placeholder",
                "questions": qs,
            }
            (folder / f"{year}.json").write_text(
                json.dumps(approved), encoding="utf-8")


class FreeFirstTest(unittest.TestCase):
    def test_real_year_archive_not_automatic_ready(self):
        root = Path(__file__).resolve().parents[1]
        result = free_first.build_report(root, "audit")
        self.assertEqual(len(result["years"]), 12)
        self.assertEqual([x["year"] for x in result["years"]],
                         list(range(104, 116)))
        self.assertGreater(result["totals"]["rawSourceCandidatesNotOfficialCompleteness"], 2000)
        self.assertGreaterEqual(result["totals"]["mainApprovedAllowlist114115"], 5)
        self.assertIsNone(result["totals"]["newReadyNotProven"])
        self.assertIsNone(result["totals"]["newLiveNotProven"])
        self.assertFalse(result["guards"]["modelInferenceUsed"])
        self.assertFalse(result["guards"]["writesToRepository"])
        self.assertFalse(result["guards"]["chargesPaidAI"])
        self.assertTrue(all(x["incrementalLiveVerified"] is None for x in result["years"]))
        self.assertTrue(all(x["officialCompleteQuestionCount"] is None for x in result["years"]))

    def test_sample_legacy_matched_cannot_be_promoted(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            fake_repo(root)
            result = free_first.build_report(root, "static")
            y115 = next(x for x in result["years"] if x["year"] == 115)
            y113 = next(x for x in result["years"] if x["year"] == 113)
            self.assertEqual(y115["legacyAutoAnswerMatchedNOTFinalQA"], 5)
            self.assertEqual(y115["legacyAnswerVerifiedFlagOnly"], 0)
            self.assertEqual(y115["legacyQuestionVerifiedFlagOnly"], 0)
            self.assertEqual(y115["mainApprovedAllowlistCount"], 1)
            self.assertEqual(y115["pendingCandidateCountNOTReady"], 4)
            self.assertEqual(y113["mainApprovedAllowlistCount"], 0)
            self.assertIsNone(y113["mainApprovalPercentOfExpected"])
            text = free_first.markdown_report(result)
            self.assertIn("NOT verified", text)
            self.assertIn("Main approved 114/115", text)

    def test_duplicate_source_id_fails_closed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            fake_repo(root)
            file = root / "sudu/data/years/114.json"
            doc = json.loads(file.read_text(encoding="utf-8"))
            doc["papers"][0]["questions"].append(doc["papers"][0]["questions"][0])
            file.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate candidate ID"):
                free_first.build_report(root, "static")

    def test_fake_approved_count_or_source_id_fails_closed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            fake_repo(root)
            file = root / "sudu/data/approved/115.json"
            doc = json.loads(file.read_text(encoding="utf-8"))
            doc["approvedCount"] = 2
            file.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "approvedCount disagrees"):
                free_first.build_report(root, "static")
            doc["approvedCount"] = 1
            doc["questions"][0]["canonicalId"] = "115-00-MB-99"
            file.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not in annual candidate"):
                free_first.build_report(root, "static")

    def test_unexpected_official_source_or_pixel_sha_fail_closed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            fake_repo(root)
            file = root / "sudu/data/years/113.json"
            doc = json.loads(file.read_text(encoding="utf-8"))
            doc["sourceIndex"] = "https://not-official.example/113/"
            file.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unexpected official source"):
                free_first.build_report(root, "static")
            doc["sourceIndex"] = "https://web1.tcte.edu.tw/EXAM/113_4y/"
            file.write_text(json.dumps(doc), encoding="utf-8")
            af = root / "sudu/data/approved/115.json"
            approved = json.loads(af.read_text(encoding="utf-8"))
            approved["questions"][0]["imageSha256"] = "not-sha"
            af.write_text(json.dumps(approved), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "original image hash"):
                free_first.build_report(root, "static")

    def test_historical_header_mismatch_is_reported_not_falsely_fixed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            fake_repo(root)
            result = free_first.build_report(root, "static")
            self.assertTrue(all(y["countDiscrepancy"] == 1
                                for y in result["years"]))
            self.assertTrue(all(y["stage"] == "RAW_CANDIDATES__NOT_QA_CERTIFIED"
                                for y in result["years"]))
            self.assertEqual(result["totals"]["newReadyNotProven"], None)


if __name__ == "__main__":
    unittest.main()
