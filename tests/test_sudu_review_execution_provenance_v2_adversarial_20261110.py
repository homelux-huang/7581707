"""MASTER adversarial diagnostics against an EXPERIMENTAL, NON-ADMITTING V2.

These tests demonstrate what a *syntactically valid offline signature* cannot
prove. They deliberately use self-generated TEST KEYS and fabricated metadata.
Passing these tests means limits were demonstrated, NOT G6/G7 or release PASS.
"""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from scripts import sudu_review_execution_provenance_v2_candidate as v2


class V2NotExternalTrustDiagnostics(unittest.TestCase):
    def setUp(self):
        # Existing test fixture is intentionally synthetic. No real provider is contacted.
        from test_sudu_review_execution_provenance_v2_candidate import CandidateProvenanceTests
        self.case = CandidateProvenanceTests(
            "test_good_distinct_signed_chain_is_not_release_authority"
        )
        self.case.setUp()

    def assert_structure_only(self):
        accepted, why = self.case.check()
        self.assertTrue(accepted, why)
        self.assertEqual(why, v2.NOT_PRODUCTION_AUTHORIZATION)
        self.assertFalse(v2.is_student_release_authorized(
            self.case.chain, self.case.trust, self.case.binding
        ))

    def test_self_signed_but_unretrieved_provider_response_id_is_accepted(self):
        signed = self.case.chain["BLIND_SOLVER"]["signed"]
        # This syntactically valid ID is invented solely for this test.
        signed["providerResponseId"] = "resp_fabricated_test_20261110_01"
        self.case.resign("BLIND_SOLVER")
        self.assert_structure_only()

    def test_blind_output_missing_full_a_b_c_d_reasons_is_accepted(self):
        record = self.case.chain["BLIND_SOLVER"]
        # Long enough to satisfy string-length check but gives no A/B/D rationale.
        record["output"] = (
            "First guess: C. My only claim is that the reusable item is convenient. "
            "This text provides no analysis of the other options at all."
        )
        record["signed"]["outputSha256"] = v2.sha(record["output"])
        self.case.resign("BLIND_SOLVER")
        self.assert_structure_only()

    def test_rephrased_answer_leak_in_prompt_is_not_detected(self):
        record = self.case.chain["BLIND_SOLVER"]
        record["prompt"] += "\nEarlier internal grading label: option letter C was selected."
        record["signed"]["promptSha256"] = v2.sha(record["prompt"])
        self.case.resign("BLIND_SOLVER")
        self.assert_structure_only()

    def test_validly_signed_self_asserted_times_do_not_prove_provider_chronology(self):
        record = self.case.chain["BLIND_SOLVER"]
        record["signed"]["startedAt"] = "2026-11-07T20:02:10+00:00"
        record["signed"]["completedAt"] = "2026-11-07T20:02:15+00:00"
        self.case.resign("BLIND_SOLVER")
        self.assert_structure_only()

    def test_same_chain_can_be_accepted_twice_without_persistent_replay_ledger(self):
        accepted_first, why_first = self.case.check()
        accepted_second, why_second = self.case.check()
        self.assertTrue(accepted_first, why_first)
        self.assertTrue(accepted_second, why_second)
        self.assertEqual(why_first, v2.NOT_PRODUCTION_AUTHORIZATION)
        self.assertEqual(why_second, v2.NOT_PRODUCTION_AUTHORIZATION)
        self.assertFalse(v2.is_student_release_authorized())

    def test_valid_chain_has_no_expiry_after_many_years(self):
        accepted, why = v2.verify_offline_structure(
            self.case.chain,
            self.case.trust,
            self.case.binding,
            now=datetime(2035, 1, 1, tzinfo=timezone.utc),
        )
        self.assertTrue(accepted, why)
        self.assertEqual(why, v2.NOT_PRODUCTION_AUTHORIZATION)
        self.assertFalse(v2.is_student_release_authorized())


if __name__ == "__main__":
    unittest.main()
