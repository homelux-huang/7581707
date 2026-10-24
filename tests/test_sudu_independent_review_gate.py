"""P0 negative/positive reviewer identity and immutable evidence tests."""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from scripts import sudu_independent_review_gate as gate

class DistinctAuthorizedReviewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.rel="sudu/data/processed/115/review-evidence/115-09-2-34-external-review.md"
        f=self.root/self.rel
        f.parent.mkdir(parents=True)
        f.write_text("# Independent review\nPersonally checked image and all A-D, calculations and dual-level teaching.")
        self.private=Ed25519PrivateKey.generate()  # test-only ephemeral, never stored in release policy
        pub=self.private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        self.policy={"schemaVersion":1,"requireHumanTeacher":True,
                     "legacyAlreadyPublished":{},"authorizedReviewers":{
                         "teacher-test-01":{"login":"external-teacher","enabled":True,
                         "role":"qualified_human_teacher","organizationVerified":True,
                         "ed25519PublicKey":base64.b64encode(pub).decode()}}}
        self.q={"questionId":"115-09-2-34","year":115}
        self.manifest={"sha256":"b"*64}
        self.teaching={"questionRevision":"a"*64,
                       "content":{"teacherSummary":"Correct analysis","elementarySummary":"Explained to pupil"}}
        self.raw=json.dumps(self.teaching,sort_keys=True).encode()
        self.statement={
          "schemaVersion":1,"questionId":self.q["questionId"],"year":115,
          "questionRevision":"a"*64,"webpSha256":"b"*64,
          "teachingDigest":gate.digest(gate.canonical(self.teaching["content"])),
          "teachingEvidenceSha256":gate.digest(self.raw),
          "reviewerLogin":"external-teacher","reviewerRole":"qualified_human_teacher",
          "sourceAuthorLogin":"homelux-huang","reviewedAt":"2026-10-24T23:00:00+08:00",
          "teacherAndElementaryReviewed":True,
          "reviewedCalculationOrNoncalculation":True,
          "reviewNotesPath":self.rel,"reviewNotesSha256":gate.digest(f.read_bytes()),
          "optionByOptionFindings":{x:f"Independent comparison for option {x}, true concept and distractor checked." for x in "ABCD"}
        }
        self.audit={}
    def sign(self):
        self.audit["independentReviewAttestation"]={
            "keyId":"teacher-test-01","payload":copy.deepcopy(self.statement),
            "signature":base64.b64encode(self.private.sign(gate.canonical(self.statement))).decode()}
    def verify(self):
        return gate.certified(self.root,self.audit,self.q,self.manifest,self.teaching,self.raw,policy=self.policy)

    def test_signed_real_distinct_review_is_permitted_after_substantive_checks(self):
        self.sign()
        self.assertTrue(self.verify()[0])
        self.assertEqual(self.verify()[1],"trusted_distinct_reviewer_signed_material_and_substantive_notes")
    def test_self_authorized_ai_no_signature_and_editing_reviewer_string_fail(self):
        self.assertFalse(self.verify()[0])
        self.audit={"independentReviewAttestation":{"keyId":"teacher-test-01",
                   "payload":{**self.statement,"reviewerLogin":"pretend-someone-else"},"signature":"nonsense"}}
        self.assertFalse(self.verify()[0])
        self.sign()
        self.audit["independentReviewAttestation"]["payload"]["reviewerLogin"]="other-person"
        self.assertFalse(self.verify()[0])
    def test_wrong_author_or_modified_evidence_fails_even_when_signature_valid(self):
        self.statement["sourceAuthorLogin"]="external-teacher"
        self.sign()
        self.assertFalse(self.verify()[0])
        self.statement["sourceAuthorLogin"]="homelux-huang"
        self.sign()
        self.teaching["content"]["teacherSummary"]="modified new explanation"
        self.assertFalse(self.verify()[0])
        self.teaching["content"]["teacherSummary"]="Correct analysis"
        self.assertTrue(self.verify()[0])
        self.raw=b'changed teaching evidence'
        self.assertFalse(self.verify()[0])
    def test_attested_notes_and_four_options_are_substantive_and_immutable(self):
        self.statement["optionByOptionFindings"]["B"]="BAD"
        self.sign()
        self.assertFalse(self.verify()[0])
        self.statement["optionByOptionFindings"]["B"]="Verified MR curve versus macro inflation gap, correct option rejection."
        self.sign()
        self.assertTrue(self.verify()[0])
        (self.root/self.rel).write_text("content replaced after review")
        self.assertFalse(self.verify()[0])
    def test_unauthorized_or_ai_signer_fails_in_teacher_required_policy(self):
        self.sign()
        self.policy["authorizedReviewers"]["teacher-test-01"]["role"]="ai_assistant"
        self.assertFalse(self.verify()[0])
        self.policy["authorizedReviewers"]["teacher-test-01"]["role"]="qualified_human_teacher"
        self.policy["authorizedReviewers"]["teacher-test-01"]["enabled"]=False
        self.assertFalse(self.verify()[0])
        self.policy["authorizedReviewers"]={}
        self.assertFalse(self.verify()[0])
    def test_legacy_five_only_match_pinned_original_git_blob(self):
        item={"year":115,"questionRevision":"a"*64,
              "webpSha256":"b"*64,"teachingEvidenceGitBlob":gate.blob_oid(self.raw)}
        policy={"schemaVersion":1,"legacyAlreadyPublished":{self.q["questionId"]:item},"authorizedReviewers":{}}
        self.assertTrue(gate.certified(self.root,None,self.q,self.manifest,self.teaching,self.raw,policy=policy)[0])
        self.teaching["content"]["teacherSummary"]="changed"
        self.assertTrue(gate.certified(self.root,None,self.q,self.manifest,self.teaching,self.raw,policy=policy)[0])
        self.raw=b'edited old teaching document'
        self.assertFalse(gate.certified(self.root,None,self.q,self.manifest,self.teaching,self.raw,policy=policy)[0])
    def test_unconfigured_main_policy_cannot_approve_new_questions(self):
        self.sign()
        self.assertFalse(gate.certified(self.root,self.audit,self.q,self.manifest,self.teaching,self.raw,
                   policy={"schemaVersion":1,"requireHumanTeacher":True,"authorizedReviewers":{}})[0])
if __name__=="__main__":
    unittest.main()
