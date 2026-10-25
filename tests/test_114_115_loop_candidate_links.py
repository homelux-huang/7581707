"""MASTER/INTEGRATION: verify source↔WebP↔authored candidate links, never READY.

These checks use real 114/115 QA-branch copies and literal image bytes.
A cryptographic hash passing is not an independent exam-answer/teacher/UI review.
"""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
ENG = ("114-00-E-07", "114-00-E-08", "114-00-E-09")
MATH = tuple(f"115-00-MB-{n:02d}" for n in range(20, 26))
PRIORITY = ENG + MATH
SHA = re.compile(r"^[a-f0-9]{64}$")


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CandidateSourceLessonLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q, cls.asset = {}, {}
        for year in (114, 115):
            prefix = f"sudu/data/processed/{year}"
            questions = load(prefix + "/questions.json")["questions"]
            images = load(prefix + "/webp-manifest.json")["items"]
            cls.q.update({row["questionId"]: row for row in questions})
            cls.asset.update({row["questionId"]: row for row in images})
        cls.docs = {}
        for id_ in PRIORITY:
            role = "114-role-b-20261025" if id_ in ENG else "114-115-20261025"
            cls.docs[id_] = load(f"sudu/teaching-candidates/{role}/{id_}.json")

    def test_every_real_source_asset_and_author_revision_agree(self):
        self.assertEqual(len(PRIORITY), 9)
        for id_ in PRIORITY:
            with self.subTest(questionId=id_):
                q, asset, lesson = self.q[id_], self.asset[id_], self.docs[id_]
                self.assertEqual(asset["questionId"], id_)
                self.assertEqual(asset["qaStatus"], "PASS")  # status, not official acceptance
                image = ROOT / asset["output"]
                self.assertTrue(image.is_file(), asset["output"])
                raw = image.read_bytes()
                self.assertEqual(raw[:4], b"RIFF")
                self.assertEqual(raw[8:12], b"WEBP")
                self.assertEqual(file_sha(image), asset["sha256"])
                self.assertEqual(publisher.image_sha(q), asset["sha256"])
                # Preserve BOTH source claims when present; no fallback may hide a conflict.
                for claim in (q.get("questionProvenance") or {}).get("webpSha256"), (q.get("assets") or {}).get("sha256"):
                    if claim is not None:
                        self.assertEqual(claim, asset["sha256"])
                self.assertEqual(q["assets"]["singleQuestionWebp"], asset["output"])
                self.assertRegex(publisher.pdf_sha(q, "question"), SHA)
                self.assertIs(q["questionVerified"], False, id_)
                revision = publisher.text_revision(q, asset["sha256"])
                if id_ in ENG:
                    link = lesson["source"]
                    self.assertEqual(link["questionRevision"], revision)
                    self.assertEqual(link["webpPath"], asset["output"])
                    self.assertEqual(link["webpSha256"], asset["sha256"])
                    self.assertEqual(link["questionPdfSha256"],
                                     q["questionProvenance"]["officialPdfSha256"])
                    self.assertEqual(lesson["answer"], q["answer"])  # candidate parity only
                else:
                    self.assertEqual(lesson["question"], q["question"])
                    self.assertEqual(lesson["options"], q["options"])
                    self.assertEqual(lesson["image"], asset["output"])
                    self.assertEqual(lesson["imageSha256"], asset["sha256"])
                    self.assertIs(lesson["studentReleaseApproved"], False)
                    self.assertIs(lesson["deploy"], False)
                    if id_ == "115-00-MB-23":
                        self.assertEqual(lesson["sourceTextRevisionWithTable"], revision)
                        self.assertIs(lesson["review"]["formalIndependentTableQa"], False)
                    else:
                        self.assertEqual(lesson["sourceTextRevisionWithoutTable"], revision)

    def test_114_original_lesson_or_new_draft_and_enrichment_digest_anchored(self):
        for id_ in ENG:
            with self.subTest(questionId=id_):
                q, asset, lesson = self.q[id_], self.asset[id_], self.docs[id_]
                self.assertEqual(lesson["kind"], "PRESERVE_BASE_AND_ENRICH")
                self.assertIsNone(lesson["teaching"])
                source = lesson["source"]
                raw = (ROOT / source["baseTeachingEvidencePath"]).read_bytes()
                blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                                    + b"\0" + raw).hexdigest()
                self.assertEqual(blob, source["baseTeachingGitBlobSha"])
                original = json.loads(raw)
                self.assertEqual(original["questionRevision"], source["questionRevision"])
                self.assertEqual(canonical_sha(original["content"]),
                                 source["baseTeachingCanonicalSha256"])
                actual = canonical_sha({
                    "questionId": id_,
                    "sourceRevision": publisher.text_revision(q, asset["sha256"]),
                    "webpSha256": asset["sha256"],
                    "teaching": original["content"],
                    "enrichment": lesson["enrichment"],
                })
                self.assertEqual(actual, lesson["composedTeachingSha256"])
                self.assertIs(lesson["review"]["humanTeacherVerified"], False)

    def test_115_exact_teaching_sha_of_six_candidates(self):
        for id_ in MATH:
            with self.subTest(questionId=id_):
                lesson = self.docs[id_]
                self.assertEqual(canonical_sha(lesson["teaching"]),
                                 lesson["teachingCanonicalSha256"])
                self.assertEqual(lesson["review"]["externalIndependentReview"], "PENDING")
                self.assertFalse(lesson["studentReleaseApproved"])
                self.assertNotIn("APPROVED", str(lesson["sourceTextRevisionGate"])
                                 if id_ == "115-00-MB-23" else "PENDING")

    def test_all_text_options_or_webp_byte_changes_invalidate_revision(self):
        for id_ in PRIORITY:
            with self.subTest(questionId=id_):
                q, asset = self.q[id_], self.asset[id_]
                sha = asset["sha256"]
                baseline = publisher.text_revision(q, sha)
                mutated = copy.deepcopy(q)
                mutated["question"] += " [UNTRUSTED_CHANGE]"
                self.assertNotEqual(publisher.text_revision(mutated, sha), baseline)
                mutated = copy.deepcopy(q)
                mutated["options"][0] += " [UNTRUSTED_CHANGE]"
                self.assertNotEqual(publisher.text_revision(mutated, sha), baseline)
                bad_sha = ("0" if sha[0] != "0" else "1") + sha[1:]
                self.assertNotEqual(publisher.text_revision(q, bad_sha), baseline)

    def test_mb23_original_2x3_table_is_versioned_cannot_reuse_text_only(self):
        id_ = "115-00-MB-23"
        q, asset, draft = self.q[id_], self.asset[id_], self.docs[id_]
        expected = q["originalSourceTableCandidate"]
        self.assertEqual(expected["heading"], ["行程", "原價", "優惠"])
        self.assertEqual(len(expected["rows"]), 2)
        self.assertTrue(all(len(row) == 3 for row in expected["rows"]))
        self.assertEqual(draft["sourceTables"], [expected])
        self.assertEqual(draft["originalSourceTableCandidate"], expected)
        old = publisher.text_revision(
            {"question": q["question"], "options": q["options"]}, asset["sha256"])
        full = publisher.text_revision(q, asset["sha256"])
        self.assertEqual(old, draft["sourceTextRevisionWithoutTable"])
        self.assertEqual(full, draft["sourceTextRevisionWithTable"])
        self.assertNotEqual(old, full)
        mutated = copy.deepcopy(q)
        mutated["originalSourceTableCandidate"]["rows"][0][2] += " [UNTRUSTED_CHANGE]"
        self.assertNotEqual(publisher.text_revision(mutated, asset["sha256"]), full)
        self.assertIs(draft["review"]["sourceRevisionAccepted"], False)

    def test_lesson_edits_invalidate_both_candidate_digest_algorithms(self):
        q = self.q["114-00-E-07"]
        m = self.asset[q["questionId"]]
        b = self.docs[q["questionId"]]
        original = load(b["source"]["baseTeachingEvidencePath"])["content"]
        base = canonical_sha({
            "questionId": q["questionId"],
            "sourceRevision": publisher.text_revision(q, m["sha256"]),
            "webpSha256": m["sha256"], "teaching": original,
            "enrichment": b["enrichment"],
        })
        self.assertEqual(base, b["composedTeachingSha256"])
        changed = copy.deepcopy(b["enrichment"])
        changed["highlights"][0]["text"] += " [UNTRUSTED_CHANGE]"
        self.assertNotEqual(canonical_sha({
            "questionId": q["questionId"],
            "sourceRevision": publisher.text_revision(q, m["sha256"]),
            "webpSha256": m["sha256"], "teaching": original,
            "enrichment": changed,
        }), base)
        c = self.docs["115-00-MB-23"]
        teach = copy.deepcopy(c["teaching"])
        teach["teacherSummary"] += " [UNTRUSTED_CHANGE]"
        self.assertNotEqual(canonical_sha(teach), c["teachingCanonicalSha256"])


if __name__ == "__main__":
    unittest.main()
