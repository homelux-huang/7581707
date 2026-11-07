"""Security-only synthetic tests. No fake receipt is usable for students."""
import base64
import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from scripts import sudu_review_execution_provenance_v2_candidate as v2

ROLES=v2.ROLES
QID="114-00-E-12"

class CandidateProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026, 11, 7, 21, tzinfo=timezone.utc)
        self.binding={"questionId":QID,
            "questionRevision":"0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec",
            "webpSha256":"99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60",
            "teachingDigest":"c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a",
            "officialEvidenceSha256":"63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"}
        self.keys={r:Ed25519PrivateKey.generate() for r in ROLES}
        self.trust={}
        self.chain={}
        times=(("2026-11-07T20:00:00+00:00","2026-11-07T20:01:00+00:00"),
               ("2026-11-07T20:02:00+00:00","2026-11-07T20:03:00+00:00"),
               ("2026-11-07T20:04:00+00:00","2026-11-07T20:05:00+00:00"))
        for n,r in enumerate(ROLES):
            issuer="issuer_"+str(n)
            principal="distinct_issuer_role_"+str(n)
            pub=self.keys[r].public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw)
            self.trust[issuer]={"authorized":True,"revoked":False,
                "role":r,"principalId":principal,"ed25519PublicKey":base64.b64encode(pub).decode()}
            prompt=(
                "The original author wrote a detailed four-option teaching lesson, without a model key."
                if r=="B_AUTHOR" else
                "Lucy: Plastics may take 20 years to break down. John: We need to use less plastic. "
                "Lucy: ____ John: Great idea, I'll try that too. "
                "(A) I prefer plastic containers. (B) I use plastic straws. "
                "(C) I carry my water bottle. (D) I throw everything away."
                if r=="BLIND_SOLVER" else
                "Independently check the exact original lesson, source QID, four options and official source evidence."
            )
            output=(
                "Original B full lesson evidence hash is frozen and only authored by its own task."
                if r=="B_AUTHOR" else
                "First conclusion is option C because carrying a reusable water bottle reduces plastic use; "
                "A and B increase disposable plastic, D creates more waste rather than reducing consumption."
                if r=="BLIND_SOLVER" else
                "Independent E substantive check of high-school and elementary four-option explanations."
            )
            st={"schemaVersion":2,"role":r,"issuerKeyId":issuer,"principalId":principal,
                "questionId":QID,"questionRevision":self.binding["questionRevision"],
                "webpSha256":self.binding["webpSha256"],"teachingDigest":self.binding["teachingDigest"],
                "executionId":"execution_"+str(n)+"_20261107","providerResponseId":"resp_test"+str(n)+"123456",
                "promptSha256":v2.sha(prompt),"outputSha256":v2.sha(output),
                "startedAt":times[n][0],"completedAt":times[n][1]}
            if r=="BLIND_SOLVER":
                st.update(answerKeyExposed=False,firstAnswer="C")
            if r=="E_REVIEWER":
                st.update(officialEvidenceSha256=self.binding["officialEvidenceSha256"],
                    teacherAndElementaryReviewed=True,
                    optionByOptionFindings={
                        "A":"Buying new plastic containers increases plastic use, inconsistent with reducing waste.",
                        "B":"Continued use of disposable plastic straws contradicts the plan to reduce plastic.",
                        "C":"Carrying a reusable water bottle is a concrete action to reduce single-use plastic.",
                        "D":"Throwing away purchased goods increases waste and does not reduce plastic consumption."})
            self.chain[r]={"signed":st,"prompt":prompt,"output":output,"signature":""}
            self.resign(r)
    def resign(self,r):
        st=self.chain[r]["signed"]
        self.chain[r]["signature"]=base64.b64encode(self.keys[r].sign(v2.canonical(st))).decode()
    def check(self):
        return v2.verify_offline_structure(self.chain,self.trust,self.binding,now=self.now)
    def test_good_distinct_signed_chain_is_not_release_authority(self):
        yes,why=self.check()
        self.assertTrue(yes,why)
        self.assertEqual(why,v2.NOT_PRODUCTION_AUTHORIZATION)
        self.assertFalse(v2.is_student_release_authorized(self.chain,self.trust,self.binding))
    def test_reject_missing_blind_or_reviewer_role(self):
        del self.chain["BLIND_SOLVER"]
        self.assertEqual(self.check()[1],"missing_independent_execution_roles")
    def test_reject_forged_signature(self):
        self.chain["E_REVIEWER"]["signature"]=self.chain["B_AUTHOR"]["signature"]
        self.assertIn("signature",self.check()[1])
    def test_reject_different_question_revision_even_with_valid_signature(self):
        self.chain["E_REVIEWER"]["signed"]["questionRevision"]="b"*64
        self.resign("E_REVIEWER")
        self.assertIn("exact_source_or_teaching_binding_mismatch",self.check()[1])
    def test_reject_mutated_original_prompt(self):
        self.chain["B_AUTHOR"]["prompt"]+=" INJECTED BY OTHER ACTOR"
        self.assertIn("prompt_or_output_bytes_tampered",self.check()[1])
    def test_reject_shared_principal_even_if_two_keys(self):
        p=self.chain["B_AUTHOR"]["signed"]["principalId"]
        s=self.chain["E_REVIEWER"]["signed"]
        self.trust[s["issuerKeyId"]]["principalId"]=p
        s["principalId"]=p
        self.resign("E_REVIEWER")
        self.assertEqual(self.check()[1],"not_distinct_external_execution_principals")
    def test_reject_replayed_provider_id_even_if_signed(self):
        self.chain["E_REVIEWER"]["signed"]["providerResponseId"]=self.chain["BLIND_SOLVER"]["signed"]["providerResponseId"]
        self.resign("E_REVIEWER")
        self.assertEqual(self.check()[1],"replayed_or_duplicate_provider_execution")
    def test_reject_untrusted_or_revoked_issuer(self):
        self.trust["issuer_2"]["revoked"]=True
        self.assertIn("issuer_not_authorized_or_revoked",self.check()[1])
    def test_reject_blind_answer_leak_even_with_valid_signature(self):
        self.chain["BLIND_SOLVER"]["prompt"]+=" Official answer: C"
        self.chain["BLIND_SOLVER"]["signed"]["promptSha256"]=v2.sha(self.chain["BLIND_SOLVER"]["prompt"])
        self.resign("BLIND_SOLVER")
        self.assertEqual(self.check()[1],"BLIND_SOLVER:blind_prompt_has_answer_or_exposure")
    def test_reject_post_key_blind_claim(self):
        self.chain["BLIND_SOLVER"]["signed"]["answerKeyExposed"]=True
        self.resign("BLIND_SOLVER")
        self.assertIn("blind_prompt_has_answer_or_exposure",self.check()[1])
    def test_reject_reviewer_before_blind_freeze(self):
        self.chain["E_REVIEWER"]["signed"]["startedAt"]="2026-11-07T20:02:30+00:00"
        self.resign("E_REVIEWER")
        self.assertEqual(self.check()[1],"blind_not_frozen_before_independent_review")
    def test_reject_four_option_missing_E_findings(self):
        del self.chain["E_REVIEWER"]["signed"]["optionByOptionFindings"]["D"]
        self.resign("E_REVIEWER")
        self.assertIn("four_option",self.check()[1])
    def test_reject_unsigned_official_sha_change(self):
        self.chain["E_REVIEWER"]["signed"]["officialEvidenceSha256"]="9"*64
        self.resign("E_REVIEWER")
        self.assertEqual(self.check()[1],"E_REVIEWER:official_document_sha_mismatch")
    def test_reject_missing_provider_response(self):
        self.chain["BLIND_SOLVER"]["signed"]["providerResponseId"]="not-verifiable"
        self.resign("BLIND_SOLVER")
        self.assertIn("provider_id_missing",self.check()[1])
    def test_production_publisher_not_wired_to_experimental_candidate(self):
        main=Path("scripts/sudu_verified_publish.py").read_text(encoding="utf-8")
        active=Path("scripts/sudu_independent_review_gate.py").read_text(encoding="utf-8")
        self.assertNotIn("sudu_review_execution_provenance_v2_candidate",main+active)
        self.assertFalse(v2.is_student_release_authorized())
if __name__=="__main__":
    unittest.main()
