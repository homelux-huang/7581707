"""Role A 114 E12 original printed official answer and official notice exact scope (NO RELEASE)."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
EVIDENCE = BASE / "review-evidence/114-00-E-12-official-20261102.json"
OLD_QA = BASE / "QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json"
IMAGE_QA = BASE / "QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
NOTICE = BASE / "QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
STATUS = BASE / "official-confirmation-status.json"
E12_SHA = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
E12_BLOB = "def397fcc0693d90de40b051fdf4c7c85b4567ce"
PAGE_SHA = "51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
PAGE_BLOB = "5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
ANSWER_SHA = "a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
ANSWER_BLOB = "5f2920313607af4e756095cd3d6098c8a3ab7440"
OLD_QA_BLOB = "0ae35ec3baac7ee4709ea652103db5666fee45a9"
IMAGE_QA_BLOB = "c1154562fa30cb4b2720a6000a970cf09ef460ff"
NOTICE_BLOB = "6b9a919f224bec8dc3659052a404b4173b6ef366"
STATUS_BLOB = "ecfb5663d5af6008fb71f721ec5f23c69d557f5f"
NOTICE_SHA = "79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"
EXPECTED_CHANGES = {
    "sudu/data/processed/114/review-evidence/114-00-E-12-official-20261102.json",
    "sudu/data/processed/114/QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json",
    "tests/test_role_a_114_e12_final_official.py",
    ".github/workflows/role-a-114-e12-final-official.yml",
    "docs/ROLE_A_114_E12_FINAL_OFFICIAL_20261102.md",
}

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def git_blob(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def q12_qa():
    return next(x for x in load(OLD_QA)["items"] if x["questionId"] == "114-00-E-12")

def validate(r):
    if r["questionId"] != "114-00-E-12": raise ValueError("wrong scope")
    if r["publishedOfficialAnswer"]["answer"] != "C": raise ValueError("wrong answer")
    if r["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishQuestionIds"] != ["114-00-E-26"]:
        raise ValueError("wrong official notice question scope")
    if r["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishAnswer"] != "C":
        raise ValueError("wrong E26 confirmation")
    if r["finalOfficialNoticeScope"]["q12ListedInOfficialCorrection"]:
        raise ValueError("falsely claim E12 correction")
    if r["finalOfficialNoticeScope"]["q12NewPublishedAnswerChangeObserved"]:
        raise ValueError("falsely claim new Q12 answer")
    if r["finalOfficialNoticeScope"]["formalQuestionAnswerVerifiedFlagSet"]:
        raise ValueError("premature G3 formal approval")
    if r["publishedOfficialAnswer"]["oldAnswerQaOfficialCorrectionsChecked"]:
        raise ValueError("historical QA silently retroactively changed")
    if r["publishedOfficialAnswer"]["oldAnswerQaAnswerVerified"]:
        raise ValueError("historical answerVerified silently changed")
    if r["publishedOfficialAnswer"]["oldHistoricalQaRewritten"]:
        raise ValueError("historical QA bytes overwritten")
    if r["publishedOfficialAnswer"]["originalAnswerWebpSha256"] != ANSWER_SHA:
        raise ValueError("original official image changed")
    if r["originalQuestion"]["originalSingleWebpSha256"] != E12_SHA:
        raise ValueError("original question image changed")
    if any(r["handoff"][k] for k in ("ready","approved","live","canonicalQuestionsJsonEdited","canonicalSqliteEdited","otherQuestionIdsEdited")):
        raise ValueError("unlicensed student admission")
    return True

class E12OriginalOfficial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = load(EVIDENCE)

    def test_exact_one_question_and_no_student_release(self):
        r = self.r
        self.assertTrue(validate(r))
        self.assertEqual(r["status"], "ROLE_A_OFFICIAL_PUBLISHED_ANSWER_AND_NOTICE_SCOPE_SOURCE_RECEIPT_CANDIDATE_NO_RELEASE")
        self.assertEqual(r["claim"], "https://github.com/homelux-huang/7581707/issues/36#issuecomment-6569192015")
        self.assertFalse(r["review"]["independentRoleEContentReview"])

    def test_original_pixels_unchanged_exact_webp_and_gitblob(self):
        r = self.r
        for path, s, blob in (
            (r["originalQuestion"]["originalSingleWebp"], E12_SHA, E12_BLOB),
            (r["originalQuestion"]["archivedOriginalPageWebp"], PAGE_SHA, PAGE_BLOB),
            (r["publishedOfficialAnswer"]["originalAnswerWebp"], ANSWER_SHA, ANSWER_BLOB),
        ):
            with self.subTest(path=path):
                raw = (ROOT / path).read_bytes()
                self.assertEqual(raw[:4], b"RIFF")
                self.assertEqual(raw[8:12], b"WEBP")
                self.assertEqual(sha256(raw), s)
                self.assertEqual(git_blob(raw), blob)
        self.assertEqual(r["originalQuestion"]["originalPixelCrop"], [90, 589, 1310, 872])
        self.assertFalse(r["originalQuestion"]["originalImageRecroppedOrRecreated"])

    def test_existing_question_g1_pass_but_g2_g3_not_promoted(self):
        self.assertEqual(git_blob(IMAGE_QA.read_bytes()), IMAGE_QA_BLOB)
        qa = next(i for i in load(IMAGE_QA)["items"] if i["questionId"] == "114-00-E-12")
        self.assertEqual(qa["result"], "PASS")
        self.assertEqual(qa["reviewedWebpSha256"], E12_SHA)
        self.assertFalse(qa["answerVerified"])
        self.assertFalse(qa["questionVerified"])
        self.assertEqual(qa["sourcePage"], 3)

    def test_restore_exact_existing_answer_image_qa_without_rewriting_flags(self):
        self.assertEqual(git_blob(OLD_QA.read_bytes()), OLD_QA_BLOB)
        old = q12_qa()
        self.assertEqual(old["officialVisualAnswerCandidate"], "C")
        self.assertEqual(old["officialAnswerImageWebpSha256"], ANSWER_SHA)
        self.assertFalse(old["officialCorrectionsChecked"])
        self.assertFalse(old["answerVerified"])
        self.assertFalse(old["integrationReady"])

    def test_exact_english_official_confirmation_names_only_e26(self):
        self.assertEqual(git_blob(NOTICE.read_bytes()), NOTICE_BLOB)
        d = load(NOTICE)
        self.assertEqual(d["year"], 114)
        en = next(x for x in d["docs"] if x["paperCode"] == "00-E")
        self.assertEqual(en["pdfSha256"], NOTICE_SHA)
        self.assertTrue(en["allPagesVisuallyReviewed"])
        self.assertTrue(en["noticeScopeOnly"])
        self.assertEqual(en["pageCount"], 1)
        self.assertEqual(len(en["confirmed"]), 1)
        self.assertEqual(en["confirmed"][0]["questionId"], "114-00-E-26")
        self.assertEqual(en["confirmed"][0]["officialConfirmedAnswer"], "C")
        self.assertEqual(en["confirmed"][0]["changeFromExistingOfficialPdfTextCandidate"], "NONE_OBSERVED")
        self.assertNotIn("114-00-E-12", [x["questionId"] for x in en["confirmed"]])

    def test_independent_status_record_same_e26_scope(self):
        self.assertEqual(git_blob(STATUS.read_bytes()), STATUS_BLOB)
        en = load(STATUS)["confirmations"]["00-E"]
        self.assertEqual(en["confirmedQuestionIds"], ["114-00-E-26"])
        self.assertEqual(en["revisionDocumentSha256"], NOTICE_SHA)
        self.assertFalse(en["perQuestionReleaseCertified"])

    def test_printed_stem_options_original_image(self):
        q = self.r["originalQuestion"]["questionTextAsPrinted"]
        self.assertEqual(q["options"]["C"], "That’s why I always carry my own water bottle.")
        self.assertEqual(q["dialogue"][2], "Lucy: I agree. ______.")
        self.assertEqual(len(q["options"]), 4)
        self.assertEqual(q["options"]["B"], "So I keep using plastic straws for all my drinks.")

    def test_negative_tampering_fails_closed(self):
        for case in ("answer","notice_e12","notice_q26","notice_answer","promote_g3","promote_ready","promote_live","old_flag","old_rewrite","wrong_image"):
            with self.subTest(case=case):
                r = copy.deepcopy(self.r)
                if case == "answer": r["publishedOfficialAnswer"]["answer"] = "A"
                elif case == "notice_e12": r["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishQuestionIds"].append("114-00-E-12")
                elif case == "notice_q26": r["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishQuestionIds"] = []
                elif case == "notice_answer": r["finalOfficialNoticeScope"]["onlyExplicitlyNamedEnglishAnswer"] = "B"
                elif case == "promote_g3": r["finalOfficialNoticeScope"]["formalQuestionAnswerVerifiedFlagSet"] = True
                elif case == "promote_ready": r["handoff"]["ready"] = True
                elif case == "promote_live": r["handoff"]["live"] = True
                elif case == "old_flag": r["publishedOfficialAnswer"]["oldAnswerQaAnswerVerified"] = True
                elif case == "old_rewrite": r["publishedOfficialAnswer"]["oldHistoricalQaRewritten"] = True
                elif case == "wrong_image": r["originalQuestion"]["originalSingleWebpSha256"] = "0"*64
                with self.assertRaises(ValueError): validate(r)

    def test_database_integrity_and_scoped_write_lease(self):
        db = BASE / "question-bank.sqlite3"
        self.assertTrue(db.is_file())
        con = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True)
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        finally:
            con.close()
        diff = subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,
                              check=True,capture_output=True,text=True)
        self.assertEqual(set(diff.stdout.splitlines()), EXPECTED_CHANGES)
        self.assertFalse(self.r["handoff"]["canonicalSqliteEdited"])

if __name__ == "__main__":
    unittest.main()
