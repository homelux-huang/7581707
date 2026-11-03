"""Read-only legacy 104-113 source candidate inventory; NOT a student release gate.

This intentionally does not turn source entry/answerMatched into an official verified
answer, an original WebP QA receipt, teaching, independent review or LIVE approval.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YEARS = range(104, 114)
PAPERS = {"00-C", "00-E", "00-MB", "09-1", "09-2"}


def summary(year):
    path = ROOT / "sudu" / "data" / "years" / f"{year}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    paper_records = doc.get("papers", [])
    candidates = [q for p in paper_records for q in p.get("questions", [])]
    counters = Counter()
    for q in candidates:
        if q.get("answerMatched") is True:
            counters["automatic_answer_matched"] += 1
        if q.get("answerVerified") is True:
            counters["independent_answer_verified"] += 1
        if q.get("questionVerified") is True:
            counters["source_question_verified"] += 1
        if q.get("teachingVerified") is True:
            counters["teaching_verified"] += 1
        if str(q.get("explanation", "")).strip():
            counters["lesson_explanation_nonempty"] += 1
        if q.get("issues"):
            counters["source_issue_questions"] += 1
    return doc, paper_records, candidates, counters


class ArchivedSourceInventoryTests(unittest.TestCase):
    def test_years_have_original_paper_index_and_distinct_ids(self):
        for year in YEARS:
            with self.subTest(year=year):
                doc, papers, candidates, counters = summary(year)
                self.assertEqual(doc.get("year"), year)
                self.assertEqual(doc.get("courseType"), "09商管群")
                self.assertEqual(
                    doc.get("sourceIndex"),
                    f"https://web1.tcte.edu.tw/EXAM/{year}_4y/",
                )
                self.assertEqual({p.get("paper") for p in papers}, PAPERS)
                self.assertEqual(len(papers), 5)
                self.assertGreater(len(candidates), 0)
                ids = [q.get("id") for q in candidates]
                self.assertEqual(len(ids), len(set(ids)), f"{year} duplicated candidate ID")
                for paper in papers:
                    self.assertTrue(paper.get("questionPdf"))
                    self.assertTrue(paper.get("answerPdf"))
                    for q in paper.get("questions", []):
                        self.assertRegex(q.get("id", ""), rf"^{year}-{re.escape(paper['paper'])}-[0-9]+$")
                self.assertGreaterEqual(len(candidates), doc.get("questionsFound", 0))
                # No source-field pairing or historical migration flag grants release.
                print(json.dumps({
                    "year": year, "source_candidates": len(candidates),
                    "legacy_reported_questionsFound": doc.get("questionsFound"),
                    "legacy_count_gap": len(candidates) - doc.get("questionsFound", 0),
                    **counters
                }, ensure_ascii=False, sort_keys=True))

    def test_paper_envelope_is_not_seven_subject_student_approval(self):
        # Two professional 09 papers are not yet mapped to the four corresponding
        # subject-specific 35-Demo renderers. The original paper labels are preserved.
        for year in YEARS:
            _, papers, candidates, _ = summary(year)
            by_code = {p["paper"]: p for p in papers}
            self.assertIn("09-1", by_code)
            self.assertIn("09-2", by_code)
            self.assertTrue(by_code["09-1"].get("questions"))
            self.assertTrue(by_code["09-2"].get("questions"))
            for q in candidates:
                self.assertIn(q.get("subject"), {p.get("subject") for p in papers})

    def test_manual_quality_is_distinct_from_legacy_automatic_matching(self):
        total, automatic, source_qa, final_answer_qa, lessons = 0, 0, 0, 0, 0
        for year in YEARS:
            _, _, candidates, c = summary(year)
            total += len(candidates)
            automatic += c["automatic_answer_matched"]
            source_qa += c["source_question_verified"]
            final_answer_qa += c["independent_answer_verified"]
            lessons += c["teaching_verified"]
        self.assertGreater(total, 0)
        # This invariant is semantic, not a manufactured future release PASS.
        self.assertLessEqual(automatic, total)
        self.assertLessEqual(source_qa, total)
        self.assertLessEqual(final_answer_qa, total)
        self.assertLessEqual(lessons, total)
        print(json.dumps({
            "years": "104-113", "raw_candidate_questions": total,
            "automatic_answer_matches_not_final_qa": automatic,
            "questionVerified_true": source_qa,
            "answerVerified_true": final_answer_qa,
            "teachingVerified_true": lessons,
            "release_status": "UNVERIFIED__NO_STUDENT_RELEASE_ASSIGNED"
        }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
