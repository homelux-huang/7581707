"""Strict standalone verified-student overlay QA: tests only synthetic inputs."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publish


class StudentOverlayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source=Path(self.tmp.name)
        self.year=115
        # The real publisher now checks the per-paper TCTE correction-status
        # ledger in addition to the independent answer and image certificates.
        # Model that mandatory external evidence ONLY in this synthetic test
        # directory. Its absence must still fail closed.
        publish.dump(
            self.source/"sudu/data/processed/115/official-confirmation-status.json",
            {"schemaVersion":1,"year":115,
             "confirmations":{"00-MB":{
                 "officialStatus":"no_objection_submitted",
                 "revisionDocumentContent":"not_applicable"}}})
        self.question={
            "questionId":"115-00-MB-03","year":115,"paperCode":"00-MB",
            "originalQuestionNumber":3,"subject":"數學B",
            "question":"已知 L₁: 2x+3y=4，L₂ 平行，求 x 截距及斜率。",
            "options":["(2,−2/3)","(2,2/3)","(4/3,−2/3)","(4/3,2/3)"],
            "answer":"A","answerMatched":True,
            "assets":{"singleQuestionWebp":"sudu/data/processed/115/webp-v2/00-MB/115-00-MB-03.webp",
                      "sourceSha256":"c"*64,"sha256":"f"*64},
            "questionProvenance":{"pdfSha256":"b"*64},
            "answerProvenance":{"pdfSha256":"a"*64}
        }
        self.manifest={"sha256":"f"*64}
        self.revision=publish.text_revision(self.question,self.manifest["sha256"])
        self.docs={
            "ocr":{"questionRevision":self.revision,"webpSha256":"f"*64,
                   "question":self.question["question"],"options":self.question["options"],
                   "visualTextCompared":True},
            "official":{"officialPdfSha256":"a"*64,"finalAnswer":"A","correctionNoticeReviewed":True,
                        "officialPage":"https://web1.tcte.edu.tw/EXAM/115_4y/",
                        "noObjectionForPaper":True},
            "blind":{"questionRevision":self.revision,"webpSha256":"f"*64,
                     "officialAnswerHiddenDuringSolve":True,"solvedWithoutOfficialAnswer":True,
                     "answer":"A","blindReasoning":"x=2 and slope = −2/3","solvedAt":"2026-10-23",
                     "solver":"Independent assistant"},
            "teaching":{"questionRevision":self.revision,"allFourOptionsReviewed":True,
                        "calculationReviewed":True,"content":{
                            "teacherSummary":"截距代 y=0；斜率用斜截式",
                            "elementarySummary":"先找交點，再算坡度","memory":"截距代零","concept":"直線方程式",
                            "extension":"檢查正負號","source":"課本頁數待核對",
                            "optionExplanations":{c:{"teacher":"計算核對","elementary":"再算一次",
                                  "reason":"檢核各選項"} for c in "ABCD"},
                            "hasExamCalculation":True,"calculationReviewed":True,
                            "examCalculation":{"given":["2x+3y=4"],"formulaUse":"斜率和截距",
                                                "substitution":["y=0"],"steps":["x=2"],
                                                "result":"(2,-2/3)","option":"A"}}},
            "ui":{"testedQuestionRevision":self.revision,"browserSmokePassed":True,
                  "rwdPassed":True,"verifiedYearQaMode":True,
                  "ciRunUrl":"https://github.com/homelux-huang/7581707/actions/runs/123"}
        }
        self.evidence={}
        for name,content in self.docs.items():
            p=f"sudu/data/processed/115/review-evidence/115-00-MB-03-{name}.json"
            self.evidence[name]=p
            publish.dump(self.source/p,{"schemaVersion":1,"year":115,"questionId":"115-00-MB-03",
                                         "reviewer":"Test","reviewedAt":"2026-10-23",**content})
        self.audit={"year":115,"questionId":"115-00-MB-03","status":"STUDENT_QA_APPROVED",
                    "questionBeforeReview":self.question["question"],
                    "optionsBeforeReview":self.question["options"],
                    "webpSha256":"f"*64,"officialPdfSha256":"a"*64,
                    "questionPdfSha256":"b"*64,"originalAnswerCandidate":"A","evidence":self.evidence}

    def admitted(self,audit=None):
        return publish.apply_independently_certified_review(
            self.source,115,self.question,self.manifest,self.audit if audit is None else audit)

    def test_complete_evidence_is_per_question_student_eligible(self):
        q=self.admitted()
        self.assertIsNot(q,self.question)
        self.assertEqual(q["officialFinalAnswer"],"A")
        self.assertEqual(q["textQaStatus"],"PASS")
        self.assertEqual(q["teachingQaStatus"],"PASS")
        self.assertEqual(q["independentSolve"]["reasoning"],"x=2 and slope = −2/3")
        self.assertTrue(q["studentReleaseApproved"])
        self.assertEqual(publish.source_proof(q,True,True,self.revision),(True,True))
        self.assertEqual(publish.independently_solved(q,self.revision),"matched")
        self.assertTrue(publish.teaching_complete(q,"數學 B","A"))
        self.assertTrue(publish.certificates_complete(self.source,q,{"visualReviewEvidence":{
            "reference":self.evidence["ocr"],
            "referenceSha256":publish.digest((self.source/self.evidence["ocr"]).read_bytes())
        }},{}))
        self.assertFalse(self.question.get("answerVerified",False),"Do not mutate OCR original")

    def test_missing_official_notice_status_never_admits(self):
        notice=self.source/"sudu/data/processed/115/official-confirmation-status.json"
        original=notice.read_bytes()
        notice.unlink()
        self.assertIs(self.admitted(),self.question)
        notice.write_bytes(original)
        self.assertIsNot(self.admitted(),self.question)

    def test_unapproved_doc_is_never_admitted(self):
        audit={**self.audit,"status":"QA_PENDING"}
        self.assertIs(self.admitted(audit),self.question)

    def test_image_or_question_or_official_change_invalidates_certificate(self):
        for key,bad in [("webpSha256","0"*64),("questionBeforeReview","changed"),
                        ("originalAnswerCandidate","B"),("officialPdfSha256","d"*64)]:
            a={**self.audit,key:bad}
            self.assertIs(self.admitted(a),self.question)

    def test_missing_ui_or_blind_doc_never_releases(self):
        for name in ("ui","blind"):
            path=self.source/self.evidence[name]
            original=path.read_bytes()
            path.unlink()
            self.assertIs(self.admitted(),self.question)
            path.write_bytes(original)

    def test_official_and_blind_are_distinct(self):
        p=self.source/self.evidence["blind"]
        item=json.loads(p.read_text())
        item["officialAnswer"]="A"
        publish.dump(p,item)
        self.assertIs(self.admitted(),self.question)
        item.pop("officialAnswer")
        item["answer"]="C"
        publish.dump(p,item)
        q=self.admitted()
        self.assertEqual(publish.independently_solved(q,self.revision),"mismatch")

    def test_reading_batch_fails_closed_for_duplicate_ids(self):
        root=self.source/"sudu/data/processed/115/verified-student-batch.json"
        publish.dump(root,{"schemaVersion":1,"year":115,"items":[self.audit]})
        self.assertIn("115-00-MB-03",publish.reviewed_student_batches(self.source,115))
        publish.dump(root,{"schemaVersion":1,"year":115,"items":[self.audit,self.audit]})
        with self.assertRaises(ValueError):
            publish.reviewed_student_batches(self.source,115)


if __name__=="__main__":
    unittest.main()
