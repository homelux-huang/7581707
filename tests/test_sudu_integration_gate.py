"""Staging QA must not be confused with student publication."""
import unittest
from pathlib import Path
from scripts import sudu_integration_gate as gate
from scripts.build import included

class IntegrationGateTests(unittest.TestCase):
    def test_demo_mapping_never_rekeys_student_history(self):
        keys = gate.demo_id_map()
        self.assertEqual(len(keys), 35)
        self.assertEqual(keys["會計學|2"], "115-09-2-02")
        self.assertEqual(keys["數學 B|12"], "115-00-MB-12")

    def test_no_official_copy_counts_as_independent_ai(self):
        q = {"answer": "A", "officialFinalAnswer": "A", "questionRevision": "v1"}
        self.assertEqual(gate.independent_comparison(q), "not_checked")
        q["independentSolve"] = {
            "answer": "B", "solvedWithoutOfficialAnswer": True,
            "solvedAt": "2026-10-22", "questionRevision": "v1",
        }
        self.assertEqual(gate.independent_comparison(q), "mismatch")
        q["questionRevision"] = "v2"
        self.assertEqual(gate.independent_comparison(q), "not_checked")

    def test_fail_closed_when_ocr_or_official_qa_absent(self):
        q = {"questionProvenance": {"officialPdfSha256":"abc"},
             "answerProvenance": {"officialPdfSha256":"def"},
             "questionVerified":True,"answerVerified":True}
        self.assertFalse(gate.source_data_eligible(q, True, True))
        self.assertFalse(gate.student_eligible(q, True))

    def test_no_processed_db_json_webp_becomes_public(self):
        for path in (
            "sudu/data/processed/115/questions.json",
            "sudu/data/processed/115/question-bank.sqlite3",
            "sudu/data/processed/115/webp-v2/00-C/115-00-C-01.webp",
            "sudu/data/QA_114_115_OFFICIAL_ANSWER_VISUAL_2026-10-22.json",
        ):
            self.assertFalse(included(Path(path)),path)

    def test_real_staged_corpus_fail_closed(self):
        r = gate.report()
        self.assertEqual(r["candidateQuestions"],205)
        self.assertEqual(r["imageManifestPass"],133)
        self.assertEqual(r["sharedImageTotal"],20)
        self.assertFalse(r["issues"],r["issues"])
        self.assertEqual(r["studentReady"],0)
        self.assertEqual(r["dataReady"],0)
        self.assertFalse(r["officialRevisionsAllChecked"])
        self.assertEqual(r["aiAgreement"].get("not_checked"),205)

if __name__=="__main__":
    unittest.main()
