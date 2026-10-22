"""Automated final-release admission tests: empty QA is not a green light."""
import tempfile
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as v


class VerifiedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.q = {
            "questionId":"115-09-2-27","year":115,"paperCode":"09-2",
            "originalQuestionNumber":27,"subject":"經濟學",
            "question":"買兩份各30元的點心，總花費多少？",
            "options":["30","60","90","120"],
            "officialFinalAnswer":"B","answerVerified":True,"officialCorrectionChecked":True,
            "questionVerified":True,"textQaStatus":"PASS","teachingQaStatus":"PASS","uiQaStatus":"PASS",
            "studentReleaseApproved":True,
            "questionProvenance":{"officialPdfSha256":"a"*64,"pixelSourceSha256":"b"*64},
            "answerProvenance":{"officialPdfSha256":"c"*64},
            "teaching":{
                "teacherSummary":"依題目條件，數量乘單價","elementarySummary":"每個三十，買兩個就加兩次",
                "memory":"單價乘數量","concept":"乘法","extension":"也能用重複加法",
                "source":"高職課本｜頁數待核對",
                "optionExplanations":{l:{"teacher":"代回題目驗算","elementary":"一個一個數","reason":"與題意比較"} for l in "ABCD"},
                "calculationReviewed":True,"hasExamCalculation":True,
                "examCalculation":{"given":["2份","每份30元"],"formulaUse":"總價＝單價×數量",
                    "substitution":["30元×2"],"steps":["30＋30＝60"],"result":"60",
                    "unit":"元","option":"B"},
            },
            "teachingQaEvidence":{"reviewer":"reviewer","reviewedAt":"2026-10-22",
                                  "evidencePath":"audit.md","allFourOptionsReviewed":True,
                                  "calculationReviewed":True},
        }
        self.revision=v.text_revision(self.q,"d"*64)
        self.q["textQaEvidence"]={"questionRevision":self.revision,"sourceImageSha256":"b"*64,
                                  "reviewer":"reviewer","reviewedAt":"2026-10-22","evidencePath":"ocr-audit.md"}
        self.q["officialFinalQaEvidence"]={"answerPdfSha256":"c"*64,"finalCorrectionsReviewed":True,
                                           "reviewer":"reviewer","reviewedAt":"2026-10-22","evidencePath":"official-audit.md"}
        self.q["independentSolve"]={"solvedWithoutOfficialAnswer":True,"officialAnswerHiddenDuringSolve":True,
                 "questionRevision":self.revision,"solvedAt":"2026-10-22","solver":"independent-model",
                 "reasoning":"Two units at 30 each make 60","auditEvidencePath":"blind-solve.md","answer":"B"}

    def test_canonical_subject_split(self):
        self.assertEqual(v.stable(self.q,115),("115-09-2-27","經濟學"))
        self.assertEqual(v.subject_for(114,"09-1",26),"數位科技")
        self.assertIsNone(v.stable(self.q,114))

    def test_independent_answer_mismatch_not_approved(self):
        self.assertEqual(v.independently_solved(self.q,self.revision),"matched")
        self.q["independentSolve"]["answer"]="C"
        self.assertEqual(v.independently_solved(self.q,self.revision),"mismatch")
        self.q["independentSolve"]["solvedWithoutOfficialAnswer"]=False
        self.assertEqual(v.independently_solved(self.q,self.revision),"not_checked")

    def test_version_change_invalidates_answer(self):
        self.q["question"]="changed prompt"
        self.assertEqual(v.independently_solved(self.q,v.text_revision(self.q,"d"*64)),"not_checked")

    def test_calculation_only_when_really_calculated(self):
        self.assertTrue(v.teaching_complete(self.q,"經濟學","B"))
        public=v.public_question(self.q,115,"經濟學","data/approved/webp/115/test.webp")
        self.assertTrue(public["examCalculation"]["hasExamCalculation"])
        self.assertIn("代入：30元×2",public["examCalculation"]["lines"])
        self.q["teaching"]["hasExamCalculation"]=False
        self.assertFalse(v.teaching_complete(self.q,"經濟學","B"))
        self.q["teaching"]["examCalculation"]=None
        self.assertTrue(v.teaching_complete(self.q,"經濟學","B"))
        self.assertIsNone(v.public_question(self.q,115,"經濟學","x.webp")["examCalculation"])

    def test_answer_and_ocr_require_independent_evidence(self):
        self.assertEqual(v.source_proof(self.q,True,True,self.revision),(True,True))
        self.assertEqual(v.source_proof(self.q,False,True,self.revision),(False,True))
        self.q["answerVerified"]=False
        self.assertFalse(v.source_proof(self.q,True,True,self.revision)[1])

    def test_public_serialization_rejects_incomplete_options(self):
        self.q["teaching"]["optionExplanations"].pop("D")
        self.assertFalse(v.teaching_complete(self.q,"經濟學","B"))

    def test_image_preview_certificate_is_not_answer_qa(self):
        import hashlib, json
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=root/"sudu/data/processed/114/visual-review.json"
            path.parent.mkdir(parents=True)
            record={"questionId":"114-00-C-02","webpSha256":"f"*64,
                    "webpPath":"sudu/data/processed/114/webp-v1/00-C/114-00-C-02.webp",
                    "result":"PASS"}
            path.write_text(json.dumps({"records":[record]}))
            item={"sha256":"f"*64,"output":record["webpPath"],
                  "visualReviewEvidence":{"reference":str(path.relative_to(root)),
                                          "reviewedSha256":"f"*64}}
            self.assertTrue(v.visual_certificate(root,item,record["questionId"]))
            record["result"]="PENDING"
            path.write_text(json.dumps({"records":[record]}))
            self.assertFalse(v.visual_certificate(root,item,record["questionId"]))
            record["result"]="PASS"
            path.write_text(json.dumps({"records":[record]}))
            item["visualReviewEvidence"]["referenceSha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertTrue(v.visual_certificate(root,item,record["questionId"]))
            item["visualReviewEvidence"]["referenceSha256"]="0"*64
            self.assertFalse(v.visual_certificate(root,item,record["questionId"]))

    def test_zero_does_not_mean_year_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for year in (114,115):
                v.dump(root/f"sudu/data/approved/{year}.json",{"year":year,"expected":205,"questions":[],"approvedCount":0})
            for year in (114,115):
                v.dump(root/f"sudu/data/approved/preview/{year}.json",{
                    "schemaVersion":1,"year":year,"expected":205,
                    "imagePreviewCount":0,"questions":[]
                })
            v.dump(root/"sudu/data/approved/progress.json",{
                "years":{"114":{"approvedCount":0,"imagePreviewCount":0},
                         "115":{"approvedCount":0,"imagePreviewCount":0}}
            })
            self.assertIsNotNone(v.site_check(root))

    def test_114_115_aliases_and_cross_question_path_traversal(self):
        self.assertEqual(v.image_sha({"assets":{"sha256":"e"*64}}),"e"*64)
        self.assertEqual(v.pdf_sha({"questionProvenance":{"pdfSha256":"a"*64}},"question"),"a"*64)
        self.assertTrue(v.asset_rel_ok("sudu/data/processed/115/webp-v2/09-2/115-09-2-27.webp",115,"115-09-2-27","single"))
        self.assertFalse(v.asset_rel_ok("sudu/data/processed/115/webp-v2/09-2/115-09-2-28.webp",115,"115-09-2-27","single"))
        self.assertFalse(v.asset_rel_ok("../../private/secrets.webp",115,"115-09-2-27","single"))
        self.assertFalse(v.asset_rel_ok("sudu/data/processed/114/webp-v1/09-2/114-09-2-27.webp",115,"115-09-2-27","single"))
        self.assertEqual(v.shared_material_ids({"sharedMaterialId":"115-00-C-SHARED-11-15"}),("115-00-C-SHARED-11-15",))
        self.assertEqual(v.shared_material_ids({"assets":{"sharedMaterialIds":["114-09-2-SHARED-1-2"]}}),("114-09-2-SHARED-1-2",))


if __name__ == "__main__":
    unittest.main()
