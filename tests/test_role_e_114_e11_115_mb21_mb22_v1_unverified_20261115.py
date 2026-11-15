"""Fail-closed ROLE E receipt preflight for actual E11, MB21, MB22. NOT V1 trust admission."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("114-00-E-11", 114, "00-E", "webp-v1", "20261107", "20261113",
     "ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0",
     "646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036",
     "ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb",
     "f8d316fcf6c44dbce476f394e5537692ea7b45bf957dd2187c547e74bae5c034",
     "e767d4c5eb60dced6b2a86b73b29167b8d7b47430925da60f13a1bb6c7c8cbbf",
     "67f15c7afd096d379b96b42cd30f7032ae3e6a2a58bf9e94f7aff0fbf879001b", "A"),
    ("115-00-MB-21", 115, "00-MB", "webp-v2", "20261108", "20261114",
     "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693",
     "817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9",
     "4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4",
     "fd8e0b2f60f60c69d40250a13449bef8fbfd28a9fd686239854f126c6fa6c6be",
     "227f14b683dcdb165bc1526bca5fdbef081b7af15ea80546e67aeaf68f08bb14",
     "1f4c4aa7ff14bb3be0065a87f5c6f7e6b81990a7310db8c72295641012d93587", "A"),
    ("115-00-MB-22", 115, "00-MB", "webp-v2", "20261108", "20261114",
     "3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55",
     "7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17",
     "5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600",
     "7b08398714a4c459cca4824db600ef00370c143365af09a89eb3fed86f6540fd",
     "9505ef9f63389cf517b8ffdc6c66c337756c56e9af08c3bd70ee4a249f5f12f7",
     "415a715d211a87b44c8042586abf1d0f8fc3b6269943e88d16ddbc42de73a003", "B"),
)
NOTES = ROOT / "sudu/data/processed/115/review-evidence/role-e-20261115/E11-MB21-MB22-INDEPENDENT-G1-G5-PIXEL-HASH-CURRENT.md"
NOTES_SHA = "7818395a34750cd72090df845f0315f7d93e0555107b06617573311f7a936bc8"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def read_json(path):
    return json.loads(path.read_bytes())

class IndependentReceiptPreflight(unittest.TestCase):
    def test_sha256_implementation(self):
        self.assertEqual(digest(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_real_material_bytes_and_fail_closed_v1(self):
        self.assertEqual(digest(NOTES.read_bytes()), NOTES_SHA)
        policy_path = ROOT / "sudu/release-governance/independent-review-policy.json"
        if policy_path.exists():
            policy = read_json(policy_path)
        else:
            # QA branch does not own trusted policy: fetch GitHub protected main
            # read-only in CI, NEVER substitute an E-authored registry.
            import subprocess
            raw = subprocess.check_output([
                "git", "show", "refs/remotes/origin/main:sudu/release-governance/independent-review-policy.json"
            ], cwd=ROOT)
            policy = json.loads(raw)
        self.assertEqual(policy["reviewMode"], "DISTINCT_AI_CONTENT_RECEIPT_V1")
        self.assertEqual(policy["trustedAiReviewReceipts"], {})
        for (qid,year,paper,webpdir,g2date,g5date,webpsha,revision,tdigest,g2sha,g3sha,g5sha,answer) in CASES:
            with self.subTest(qid=qid):
                base = ROOT / f"sudu/data/processed/{year}"
                webp = base / webpdir / paper / f"{qid}.webp"
                self.assertEqual(digest(webp.read_bytes()), webpsha)
                evidence = base / "review-evidence"
                g2path = evidence / f"{qid}-ocr-publisher-{g2date}.json"
                g3path = evidence / f"{qid}-official-publisher-{g2date}.json"
                g5path = evidence / f"{qid}-teaching-publisher-{g5date}.json"
                self.assertEqual(digest(g2path.read_bytes()), g2sha)
                self.assertEqual(digest(g3path.read_bytes()), g3sha)
                self.assertEqual(digest(g5path.read_bytes()), g5sha)
                g2, g3, g5 = map(read_json, (g2path, g3path, g5path))
                source_seed = {"question":g2["question"], "options":g2["options"],
                               "singleQuestionWebpSha256":webpsha}
                self.assertEqual(digest(canonical(source_seed)), revision)
                self.assertEqual(g2["questionRevision"], revision)
                self.assertEqual(g3["finalAnswer"], answer)
                self.assertTrue(g3["correctionNoticeReviewed"])
                self.assertEqual(g5["questionRevision"], revision)
                self.assertEqual(g5["webpSha256"], webpsha)
                self.assertEqual(digest(canonical(g5["content"])), tdigest)
                self.assertEqual(g5["canonicalTeachingSha256"], tdigest)
                self.assertIsNone(g5["sourceAuthorSessionId"])
                draft = read_json(evidence / f"role-e-20261115/{qid}-V1-UNVERIFIED-DRAFT.json")
                self.assertEqual(draft["reviewTaskId"], "E-114E11-MB21-MB22-V1-CURRENT-G1-G5-20261115-01")
                self.assertEqual(draft["reviewIssueCommentId"], 6888758328)
                self.assertEqual(draft["sourceCommit"], "fec4ff58fbe63170fb42b4c47ad76c08848e8ece")
                self.assertEqual(draft["officialEvidenceSha256"], g3sha)
                self.assertEqual(draft["teachingEvidenceSha256"], g5sha)
                self.assertEqual(draft["teachingDigest"], tdigest)
                self.assertEqual(draft["reviewNotesSha256"], NOTES_SHA)
                self.assertEqual(set(draft["optionByOptionFindings"]), set("ABCD"))
                self.assertTrue(all(len(draft["optionByOptionFindings"][v]) >= 20 for v in "ABCD"))
                self.assertIsNone(draft["sourceAuthorSessionId"])
                self.assertIsNone(draft["reviewerSessionId"])
                self.assertTrue(draft["neverRegisterInTrustedMain"])
                self.assertFalse(draft["trustPass"])
                self.assertFalse(draft["firstBlindSolveVerified"])
                self.assertFalse(draft["studentReady"])
                self.assertFalse(draft["studentLive"])

if __name__ == "__main__":
    unittest.main()
