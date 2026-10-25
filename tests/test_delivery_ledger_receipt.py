"""Guard the PR32 receipt against losing or silently approving coordinator entries.

Baseline digests use sorted compact UTF-8 JSON from coordinator commit
38fb73138e7efa89d932f134cad4dff00cd739bf. No remote or historical Git fetch
is needed in CI. Intentional later delivery updates must review these guards.
"""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/114-115-QUESTION-DELIVERY-LEDGER.json"
QUESTION_ID = "115-00-MB-23"


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate ledger key: {key}")
        result[key] = value
    return result


def digest(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


class DeliveryReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"),
                               object_pairs_hook=reject_duplicate_keys)
        cls.entries = cls.ledger["questionEntries"]
        cls.mb23 = cls.entries[QUESTION_ID]

    def test_preserves_410_unique_question_ids(self):
        self.assertEqual(len(self.entries), 410)
        self.assertEqual(set(self.entries),
                         {entry["questionId"] for entry in self.entries.values()})
        self.assertEqual(sum(e["year"] == 114 for e in self.entries.values()), 205)
        self.assertEqual(sum(e["year"] == 115 for e in self.entries.values()), 205)

    def test_other_409_entries_are_unchanged(self):
        others = {k: v for k, v in self.entries.items() if k != QUESTION_ID}
        self.assertEqual(digest(others),
                         "1142b4c1f409ee1f30d66db13b610fdcf1256405043628d3951d4e3cf4e255c5")

    def test_mb23_source_and_all_admission_stages_remain_unchanged(self):
        protected = {k: v for k, v in self.mb23.items()
                     if k not in ("teachingDraft", "candidateReceipts")}
        self.assertEqual(digest(protected),
                         "c553ce15fbd35a6423c2b6163197b0d6ae808972cd6fdc68f202e1e1e2108981")

    def test_receipt_distinguishes_table_candidate_from_text_source(self):
        receipt, = self.mb23["candidateReceipts"]
        draft = self.mb23["teachingDraft"]
        self.assertEqual(draft["sourcePR"], 32)
        self.assertEqual(draft["sourceCommit"],
                         "2e7677411749a8a32a2ab1ecc065ab7e3e971f97")
        self.assertEqual(receipt["previousTeachingDraft"]["sourcePR"], 28)
        self.assertEqual(receipt["previousTeachingDraft"]["sourceCommit"],
                         "f04b26de83931ca384443eeee72de1f9ff468423")
        self.assertEqual(receipt["previousCandidateFileSha256"],
                         "b7a572fc106c726e11ad89a0751b9e18b24f653b26ee5bb8c5d1dabbf6b175aa")
        self.assertEqual(receipt["candidateFileSha256"],
                         "cfbff0c1f7b2f338187d0b739033eb7d08f2c95004e1f1b1d522a2c7dcceafb3")
        self.assertEqual(receipt["sourceTextRevisionWithoutTable"],
                         self.mb23["source"]["questionRevision"])
        self.assertEqual(receipt["sourceTextRevisionWithTable"],
                         "c3df98d4c15185803c1b17294c514a19496395d0087364825d2bdce144a10b92")
        self.assertNotEqual(receipt["sourceTextRevisionWithTable"],
                            self.mb23["source"]["questionRevision"])
        self.assertEqual(receipt["sourceTables"],
                         [self.mb23["source"]["originalSourceTableCandidate"]])
        self.assertEqual(draft["teachingDigest"],
                         receipt["previousTeachingDraft"]["teachingDigest"])
        for key in ("upstreamSourceIntegrated", "formalIndependentSourceTableQa",
                    "exactDigestUiQa"):
            self.assertIs(receipt[key], False)

    def test_no_new_release_or_qa_claims(self):
        self.assertTrue(all(e["ready"]["newReady"] is False
                            for e in self.entries.values()))
        for key in ("newReady", "newIndependentTeachingQa", "newUiQa", "newMain", "newLive"):
            self.assertEqual(self.ledger["supplementalReceipt"][key], 0)
        self.assertTrue(self.ledger["reviewerGovernance"]["requireHumanTeacher"])
        self.assertEqual(self.ledger["reviewerGovernance"]["authorizedReviewerCount"], 0)


if __name__ == "__main__":
    unittest.main()
