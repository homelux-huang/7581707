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

    def test_importer_sha_revokes_stale_schema_snapshots(self):
        import hashlib
        provenance=v.publication_provenance("f"*40, "e"*64)
        self.assertEqual(provenance["commit"], "f"*40)
        self.assertEqual(provenance["sourceTreeSignature"], "e"*64)
        self.assertEqual(provenance["publisherCodeSha256"],
                         hashlib.sha256(Path(v.__file__).read_bytes()).hexdigest())

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


class PerQuestionOfficialCorrectionScopeTests(unittest.TestCase):
    """Prove correction papers fail closed; other questions are not blocked."""

    def fixture(self,root,confirmation=True):
        p=root/"sudu/data/processed/115"
        p.mkdir(parents=True,exist_ok=True)
        official_sha="b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133"
        v.dump(p/"official-confirmation-status.json",{
            "confirmations":{
                "00-MB":{"officialStatus":"no_objection_submitted",
                         "revisionDocumentContent":"not_applicable"},
                "09-2":{"officialStatus":"question_or_answer_confirmation_document_exists",
                        "revisionDocumentContent":"SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED",
                        "revisionDocumentSha256":official_sha,"revisionDocumentPages":3}
            },
            "officialNoticeEvidencePath":"sudu/data/processed/115/QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
        })
        if confirmation:
            v.dump(p/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json",{
                "schemaVersion":1,"year":115,"allPagesInThreeDocumentsReviewed":True,
                "sourceIndexUrl":"https://web1.tcte.edu.tw/EXAM/115_4y/",
                "docs":[{"paperCode":"09-2","pdfSha256":official_sha,
                         "pageCount":3,"noticeScopeOnly":True,
                         "confirmed":[
                             {"questionId":"115-09-2-06","officialConfirmedAnswer":"D",
                              "comparedToOfficialPublishedTableCandidate":"MATCHED",
                              "changeFromPublishedAnswer":"NONE_OBSERVED"},
                             {"questionId":"115-09-2-28","officialConfirmedAnswer":"A",
                              "comparedToOfficialPublishedTableCandidate":"MATCHED",
                              "changeFromPublishedAnswer":"NONE_OBSERVED"},
                             {"questionId":"115-09-2-44","officialConfirmedAnswer":"A",
                              "comparedToOfficialPublishedTableCandidate":"MATCHED",
                              "changeFromPublishedAnswer":"NONE_OBSERVED"}
                         ]}]
            })
        return official_sha

    def test_09_2_q34_is_unaffected_but_not_no_objection_paper(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            sha=self.fixture(root)
            q={"questionId":"115-09-2-34","paperCode":"09-2","answer":"A"}
            proof={"noCorrectionForThisQuestion":True,"confirmationPdfSha256":sha,"finalAnswer":"A"}
            self.assertTrue(v.official_notice_scope_certified(root,115,q,proof))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,{
                **proof,"noObjectionForPaper":True}))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,{
                **proof,"confirmationPdfSha256":"0"*64}))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,{
                **proof,"noCorrectionForThisQuestion":False}))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,proof))

    def test_named_notice_q28_is_never_accidentally_unaffected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            sha=self.fixture(root)
            q={"questionId":"115-09-2-28","paperCode":"09-2","answer":"A"}
            base={"noCorrectionForThisQuestion":True,"confirmationPdfSha256":sha,"finalAnswer":"A"}
            self.assertFalse(v.official_notice_scope_certified(root,115,q,base))
            self.assertTrue(v.official_notice_scope_certified(root,115,q,{
                **base,"noCorrectionForThisQuestion":False,"correctionForQuestionReviewed":True}))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,{
                **base,"noCorrectionForThisQuestion":False,"correctionForQuestionReviewed":True,
                "finalAnswer":"C"}))

    def test_00_mb_no_objection_requires_actual_official_no_objection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.fixture(root)
            q={"questionId":"115-00-MB-05","paperCode":"00-MB","answer":"B"}
            self.assertTrue(v.official_notice_scope_certified(root,115,q,{"noObjectionForPaper":True}))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,{"noCorrectionForThisQuestion":True}))

    def test_no_ledger_or_incomplete_notice_blocks_any_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            sha=self.fixture(root,confirmation=False)
            q={"questionId":"115-09-2-34","paperCode":"09-2","answer":"A"}
            proof={"noCorrectionForThisQuestion":True,"confirmationPdfSha256":sha,"finalAnswer":"A"}
            self.assertFalse(v.official_notice_scope_certified(root,115,q,proof))
            self.fixture(root,confirmation=True)
            file=root/"sudu/data/processed/115/QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
            data=v.read(file);data["allPagesInThreeDocumentsReviewed"]=False;v.dump(file,data)
            self.assertFalse(v.official_notice_scope_certified(root,115,q,proof))



class Year114OfficialCorrectionScopeTests(unittest.TestCase):
    """Real 114 reviewed ledger, one question at a time, no shortcut by other years."""

    def fixture114(self, root):
        p=root/"sudu/data/processed/114"
        p.mkdir(parents=True,exist_ok=True)
        sha="a"*64
        v.dump(p/"official-confirmation-status.json",{
            "year":114,
            "confirmations":{
                "00-MB":{"officialStatus":"no_objection_submitted",
                    "revisionDocumentContent":"not_applicable",
                    "perQuestionOfficialNoticeScopeEvidenceComplete":True},
                "00-E":{"officialStatus":"question_or_answer_confirmation_document_exists",
                    "revisionDocumentContent":"SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED",
                    "revisionDocumentSha256":sha,"revisionDocumentPages":1,
                    "perQuestionOfficialNoticeScopeEvidenceComplete":True}
            },
            "officialNoticeEvidencePath":
                "sudu/data/processed/114/QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
        })
        v.dump(p/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json",{
            "schemaVersion":1,"year":114,"allPagesInFourDocumentsReviewed":True,
            "sourceIndexUrl":"https://web1.tcte.edu.tw/EXAM/114_4y/",
            "docs":[{"paperCode":"00-E","pdfSha256":sha,"noticeScopeOnly":True,
                "allPagesVisuallyReviewed":True,"pageCount":1,"confirmed":[
                    {"questionId":"114-00-E-26","officialConfirmedAnswer":"C",
                     "comparedToExistingOfficialPdfTextCandidate":"MATCHED",
                     "changeFromExistingOfficialPdfTextCandidate":"NONE_OBSERVED"}
                ]}]
        })
        return p,sha

    def test_114_english_unlisted_must_pin_pdf_and_not_claim_paper_no_objection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p,sha=self.fixture114(root)
            q={"questionId":"114-00-E-07","paperCode":"00-E","answer":"A"}
            proof={"noCorrectionForThisQuestion":True,"confirmationPdfSha256":sha,"finalAnswer":"A"}
            self.assertTrue(v.official_notice_scope_certified(root,114,q,proof))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{**proof,"noObjectionForPaper":True}))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{**proof,"confirmationPdfSha256":"0"*64}))
            self.assertFalse(v.official_notice_scope_certified(root,115,q,proof))
            (p/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json").unlink()
            self.assertFalse(v.official_notice_scope_certified(root,114,q,proof))

    def test_114_named_question_requires_independent_final_image_proof(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.fixture114(root)
            q={"questionId":"114-00-E-26","paperCode":"00-E","answer":"C"}
            proof={"correctionForQuestionReviewed":True,"confirmationPdfSha256":"a"*64,"finalAnswer":"C"}
            self.assertFalse(v.official_notice_scope_certified(root,114,q,proof))
            self.assertTrue(v.official_notice_scope_certified(root,114,q,{
                **proof,"officialFinalAnswerImageQaPassed":True}))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{
                **proof,"officialFinalAnswerImageQaPassed":True,"finalAnswer":"A"}))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{
                **proof,"officialFinalAnswerImageQaPassed":True,"noObjectionForPaper":True}))

    def test_114_math_b_requires_official_index_no_objection_not_115(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p,sha=self.fixture114(root)
            q={"questionId":"114-00-MB-02","paperCode":"00-MB","answer":"A"}
            self.assertTrue(v.official_notice_scope_certified(root,114,q,{"noObjectionForPaper":True}))
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{"noCorrectionForThisQuestion":True}))
            status=v.read(p/"official-confirmation-status.json")
            status["confirmations"]["00-MB"]["perQuestionOfficialNoticeScopeEvidenceComplete"]=False
            v.dump(p/"official-confirmation-status.json",status)
            self.assertFalse(v.official_notice_scope_certified(root,114,q,{"noObjectionForPaper":True}))

    def test_114_bad_year_scope_and_incomplete_ledger_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p,sha=self.fixture114(root)
            q={"questionId":"114-00-E-07","paperCode":"00-E","answer":"A"}
            proof={"noCorrectionForThisQuestion":True,"confirmationPdfSha256":sha}
            ledger=p/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
            data=v.read(ledger)
            data["sourceIndexUrl"]="https://web1.tcte.edu.tw/EXAM/115_4y/"
            v.dump(ledger,data)
            self.assertFalse(v.official_notice_scope_certified(root,114,q,proof))
            data["sourceIndexUrl"]="https://web1.tcte.edu.tw/EXAM/114_4y/"
            data["allPagesInFourDocumentsReviewed"]=False
            v.dump(ledger,data)
            self.assertFalse(v.official_notice_scope_certified(root,114,q,proof))

if __name__ == "__main__":
    unittest.main()
