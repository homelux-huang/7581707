"""Issue36 current owner policy: distinct AI E evidence, never human signer gate.

All positive examples in this file are SYNTHETIC dispatch/immutability fixtures,
NOT real independent content review, READY, Pages or human-teacher approval.
"""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sudu_independent_review_gate as gate
from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "sudu/release-governance/independent-review-policy.json"
EXPECTED_FIVE = {f"115-00-MB-{n:02d}" for n in (2, 3, 4, 5, 9)}


class OwnerAiReviewPolicyMigrationTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.question = {"year": 115, "questionId": "115-09-2-34", "answer": "A"}
        self.manifest = {"sha256": "b" * 64}
        self.teaching = {"questionRevision": "a" * 64, "content": {
            "teacherSummary": "AI teaching-style explanation, not an actual teacher",
            "elementarySummary": "Explain in easy spoken language"}}
        self.raw = json.dumps(self.teaching, ensure_ascii=False).encode("utf-8")
        self.audit = {
            "independentReviewAttestation": {"keyId": "FAKE_HUMAN_SIGNATURE"},
            "humanTeacherVerified": True,
            "review": {"reviewerRole": "qualified_human_teacher", "status": "PASS"}}

    def review(self, policy=None):
        return gate.certified(ROOT, self.audit, self.question, self.manifest,
                              self.teaching, self.raw,
                              policy=self.policy if policy is None else policy)

    def test_policy_is_explicit_new_ai_mode_without_teacher_roster(self):
        self.assertIs(self.policy["requireHumanTeacher"], False)
        self.assertEqual(self.policy["reviewMode"], "DISTINCT_AI_CONTENT_RECEIPT_V1")
        self.assertNotIn("authorizedReviewers", self.policy)
        self.assertEqual(self.policy["trustedAiReviewReceipts"], {})
        self.assertEqual(set(self.policy["legacyAlreadyPublished"]), EXPECTED_FIVE)
        for row in self.policy["legacyAlreadyPublished"].values():
            self.assertEqual(len(row["questionRevision"]), 64)
            self.assertEqual(len(row["webpSha256"]), 64)
            self.assertEqual(len(row["teachingEvidenceGitBlob"]), 40)
        public114=json.loads((ROOT/"sudu/data/approved/114.json").read_text())
        public115=json.loads((ROOT/"sudu/data/approved/115.json").read_text())
        self.assertEqual(public114["approvedCount"], 0)
        self.assertEqual(public115["approvedCount"], 5)
        self.assertEqual({q["canonicalId"] for q in public115["questions"]}, EXPECTED_FIVE)

    def test_fake_human_teacher_signature_and_author_self_pass_do_not_admit(self):
        self.assertEqual(self.review(), (False, "distinct_ai_content_review_missing"))
        self.audit["independentAiContentEvidence"] = (
            "sudu/data/processed/115/review-evidence/115-09-2-34-FAKE.json")
        self.audit["review"]["status"] = "APPROVED"
        self.assertEqual(self.review(), (False, "distinct_ai_content_review_missing"))

    def test_legacy_five_stay_exact_blob_exceptions_not_blanket_approved(self):
        q = {"year": 115, "questionId": "115-00-MB-02", "answer": "A"}
        original = b'SYNTHETIC_LEGACY_TEST_EVIDENCE_NOT_STUDENT_CONTENT'
        teaching = {"questionRevision": "a"*64, "content": {"teacherSummary": "fixture"}}
        manifest = {"sha256": "b"*64}
        policy = copy.deepcopy(self.policy)
        policy["legacyAlreadyPublished"][q["questionId"]] = {
            "year": 115, "questionRevision": "a"*64, "webpSha256": "b"*64,
            "teachingEvidenceGitBlob": gate.blob_oid(original)}
        self.assertEqual(gate.certified(ROOT, None, q, manifest, teaching,
                                        original, policy=policy)[1],
                         "exact_five_historical_students_preserved")
        self.assertEqual(gate.certified(ROOT, None, q, manifest, teaching,
                                        original + b"edited", policy=policy)[1],
                         "legacy_content_changed_must_be_reapproved")
        manifest["sha256"]="c"*64
        self.assertFalse(gate.certified(ROOT,None,q,manifest,teaching,
                                        original,policy=policy)[0])

    def test_registration_without_real_protected_main_never_grants(self):
        self.policy["trustedAiReviewReceipts"] = {self.question["questionId"]: {
            "evidenceGitBlobSha": "d"*40}}
        with patch.object(gate, "_ai_registry_exactly_matches_protected_main_policy",
                          return_value=False) as pinned:
            self.assertEqual(self.review(),
                             (False, "ai_review_registry_not_verified_against_protected_main"))
            pinned.assert_called_once()

    def test_registered_exact_ai_e_receipt_uses_new_branch_not_signed_teacher(self):
        self.policy["trustedAiReviewReceipts"] = {self.question["questionId"]: {
            "reviewerRole": "E", "evidenceGitBlobSha": "d"*40}}
        with patch.object(gate, "_ai_registry_exactly_matches_protected_main_policy",
                          return_value=True), patch.object(
                          gate,"separate_ai_content_receipt_verified",
                          return_value=(False,"ai_review_author_or_reviewer_not_distinct")
                          ) as verifier:
            self.assertEqual(self.review(),
                             (False,"ai_review_author_or_reviewer_not_distinct"))
            verifier.assert_called_once()
        # This mocked unit-only POSITIVE proves that the new mode can dispatch;
        # all original publisher G0-G10 gates remain independent and active.
        with patch.object(gate,"_ai_registry_exactly_matches_protected_main_policy",
                          return_value=True), patch.object(
                          gate,"separate_ai_content_receipt_verified",
                          return_value=(True,"SYNTHETIC_DISPATCH_NOT_STUDENT_READY")):
            self.assertEqual(self.review()[1], "SYNTHETIC_DISPATCH_NOT_STUDENT_READY")

    def test_spoofed_false_mode_or_reintroduced_teacher_requirement_rejected(self):
        self.policy["reviewMode"]="SIGNED_TEACHER_BACKDOOR"
        self.assertEqual(self.review()[1], "unknown_new_admission_review_mode")
        self.policy["reviewMode"]="DISTINCT_AI_CONTENT_RECEIPT_V1"
        self.policy["requireHumanTeacher"]=True
        self.assertEqual(self.review()[1], "ai_review_policy_has_legacy_teacher_requirement")

    def test_registry_must_exactly_match_protected_main_git_blob(self):
        raw=POLICY.read_bytes()
        response={"path":"sudu/release-governance/independent-review-policy.json",
                  "encoding":"base64","content":base64.b64encode(raw).decode(),
                  "sha":gate.blob_oid(raw)}
        with patch.object(gate,"_protected_main_trust_verified",return_value=True), \
             patch.object(gate,"_github_json",return_value=response):
            self.assertTrue(gate._ai_registry_exactly_matches_protected_main_policy(
                self.policy))
            tampered=copy.deepcopy(self.policy)
            tampered["trustedAiReviewReceipts"][self.question["questionId"]]={
                "madeUp": True}
            self.assertFalse(gate._ai_registry_exactly_matches_protected_main_policy(
                tampered))
            modified=copy.deepcopy(response)
            modified["sha"]="0"*40
            with patch.object(gate,"_github_json",return_value=modified):
                self.assertFalse(gate._ai_registry_exactly_matches_protected_main_policy(
                    self.policy))
        with patch.object(gate,"_protected_main_trust_verified",return_value=False):
            self.assertFalse(gate._ai_registry_exactly_matches_protected_main_policy(
                self.policy))

    def test_publisher_requires_owner_ai_mode_and_still_checks_source(self):
        q={**self.question,"question":"What is true?",
           "options":["A choice","B choice","C choice","D choice"],
           "answerMatched":True,
           "questionProvenance":{"officialPdfSha256":"e"*64},
           "answerProvenance":{"officialPdfSha256":"f"*64}}
        a={"status":"STUDENT_QA_APPROVED","questionId":q["questionId"],"year":115,
           "questionBeforeReview":q["question"],"optionsBeforeReview":q["options"],
           "webpSha256":self.manifest["sha256"],
           "officialPdfSha256":"f"*64,"questionPdfSha256":"e"*64,
           "originalAnswerCandidate":"A","evidence":{}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ("ocr","official","blind","teaching","ui"):
                rel=f"sudu/data/processed/115/review-evidence/{name}.json"
                a["evidence"][name]=rel
                publisher.dump(root/rel,{
                    "schemaVersion":1,"year":115,"questionId":q["questionId"]})
            with patch.object(gate,"policy_from_trusted_main",
                              return_value={"reviewMode":"OLD_SIGNED_HUMAN_ONLY"}), \
                 patch.object(gate,"certified") as signer:
                self.assertEqual(publisher.apply_independently_certified_review(
                    root,115,q,self.manifest,a),q)
                signer.assert_not_called()
            with patch.object(gate,"policy_from_trusted_main",
                              return_value=self.policy), \
                 patch.object(gate,"certified",
                              return_value=(True,"SYNTHETIC_NOT_APPROVED")) as reviewer:
                # Even with fake reviewer True, missing source QA, official
                # correction, true solve and browser docs cannot be promoted.
                self.assertEqual(publisher.apply_independently_certified_review(
                    root,115,q,self.manifest,a),q)
                reviewer.assert_called_once()
            self.assertNotIn("studentReleaseApproved",q)
            self.assertNotIn("questionVerified",q)


    def test_exact_v4_teaching_digest_blocks_missing_or_stale_ui(self):
        """Artificial complete-document pipeline; E decision is TEST-mocked.

        Role D's separate PR58 exercises the REAL distinct AI verifier and this
        same publisher together. This test pins the narrow UI digest guard and
        is never a real student approval.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            q={**self.question,
               "question": "SYNTHETIC only: two items priced 30 each",
               "options": ["30", "60", "90", "120"],
               "answer": "B", "answerMatched":True,
               "questionProvenance":{"officialPdfSha256":"e"*64},
               "answerProvenance":{"officialPdfSha256":"f"*64}}
            manifest={"sha256":"c"*64}
            rev=publisher.text_revision(q,manifest["sha256"])
            content={"teacherSummary":"Two times thirty is sixty",
                     "elementarySummary":"Think of thirty plus thirty",
                     "optionExplanations":{x:{"teacher":"Artificial option check "+x,
                                              "elementary":"Artificial easy reason "+x}
                                           for x in "ABCD"},
                     "calculationReviewed":True}
            base={
                "ocr":{"questionRevision":rev,"webpSha256":manifest["sha256"],
                       "question":q["question"],"options":q["options"],
                       "visualTextCompared":True},
                "official":{"officialPdfSha256":"f"*64,"finalAnswer":"B",
                            "correctionNoticeReviewed":True,
                            "officialPage":"https://web1.tcte.edu.tw/EXAM/115_4y/"},
                "blind":{"questionRevision":rev,"webpSha256":manifest["sha256"],
                         "officialAnswerHiddenDuringSolve":True,
                         "solvedWithoutOfficialAnswer":True,
                         "blindReasoning":"30 + 30 equals 60","answer":"B"},
                "teaching":{"questionRevision":rev,"allFourOptionsReviewed":True,
                            "calculationReviewed":True,"content":content},
                "ui":{"testedQuestionRevision":rev,
                      "testedTeachingDigest":gate.digest(gate.canonical(content)),
                      "browserSmokePassed":True,"rwdPassed":True,
                      "verifiedYearQaMode":True,
                      "ciRunUrl":"https://github.com/homelux-huang/7581707/actions/runs/1"}
            }
            audit={"status":"STUDENT_QA_APPROVED","questionId":q["questionId"],
                   "year":115,"questionBeforeReview":q["question"],
                   "optionsBeforeReview":q["options"],
                   "webpSha256":manifest["sha256"],
                   "officialPdfSha256":"f"*64,"questionPdfSha256":"e"*64,
                   "originalAnswerCandidate":"B","evidence":{}}
            for name in base:
                audit["evidence"][name]=(
                    f"sudu/data/processed/115/review-evidence/synthetic-{name}.json")
            for variant in ("matching", "missing", "stale", "new_lesson_old_ui"):
                with self.subTest(variant=variant):
                    docs=copy.deepcopy(base)
                    if variant=="missing":
                        docs["ui"].pop("testedTeachingDigest")
                    elif variant=="stale":
                        docs["ui"]["testedTeachingDigest"]="0"*64
                    elif variant=="new_lesson_old_ui":
                        docs["teaching"]["content"]["elementarySummary"]+=(
                            " Different content needing exact new browser QA.")
                    for name,document in docs.items():
                        publisher.dump(root/audit["evidence"][name],{
                            "schemaVersion":1,"year":115,
                            "questionId":q["questionId"],
                            "reviewer":"AI unit-test fixture only",
                            "reviewedAt":"2026-10-24T14:00:00Z",**document})
                    with patch.object(gate,"policy_from_trusted_main",
                                      return_value=self.policy), \
                         patch.object(gate,"certified",
                                      return_value=(True,"SYNTHETIC_E_APPROVED_NOT_REAL")), \
                         patch.object(publisher,"official_notice_scope_certified",
                                      return_value=True):
                        result=publisher.apply_independently_certified_review(
                            root,115,q,manifest,audit)
                    if variant=="matching":
                        self.assertIsNot(result,q)
                        self.assertIs(result["studentReleaseApproved"],True)
                    else:
                        self.assertIs(result,q,"stale UI should not be promoted")
                        self.assertNotIn("studentReleaseApproved",result)


if __name__=="__main__":
    unittest.main()
