"""Role A original 115-00-C-18 G1 source image and G2 chart/cross-page negative gates (NO RELEASE)."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
EVID = BASE / "review-evidence/115-00-C-18-G1-G2-TABLE-CROSSPAGE-20261102.json"
IMAGE_BLOB = "3bb1ae6740746959a74c22cf9c8e70fbc19eed6e"
IMAGE_SHA = "d62b403392a55eaf435a3d58f8ffa3113b94efa2de4df34090ce29b53bae8f32"
PAGE6_BLOB = "442195469f22bf49c993271633f24ad9eafbc937"
PAGE6_SHA = "8b6c781a75a864b7220f686532225171b2f53346c68f5131470371f82731e6c6"
PAGE7_BLOB = "3d9d530fcb5939c0697a7fb2791dcab2fb0defca"
PAGE7_SHA = "bc13fa1e97391a69c1a72f5d2c0653f12e36f77f10b218a3a92dd0f803a17039"
ANSWER_BLOB = "aecdee7444cba6b0eba738dc6b7c58f0bb793be8"
ANSWER_SHA = "5422c00920ef4f18fa32fffd51c7edb78acd80aac84974713a61e2a02987126f"
CONFIRM_BLOB = "1a21701647627bc1dcaa39a835bf90a4459c9424"
SHARED_REV = "c82824bbc016fbe0649bb8220be6afd2ffffdf90287968712139ed5a7aa39d12"
EXPECTED_CHANGE = {
  "sudu/data/processed/115/webp-v2/00-C/115-00-C-18.webp",
  "sudu/data/processed/115/review-evidence/115-00-C-18-G1-G2-TABLE-CROSSPAGE-20261102.json",
  "tests/test_role_a_115_c18_original_table_source.py",
  ".github/workflows/role-a-115-c18-original-table.yml",
  "docs/ROLE_A_115_C18_G1_G2_TABLE_20261102.md",
}

def digest(raw):
    return hashlib.sha256(raw if isinstance(raw, bytes) else raw.encode("utf-8")).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def rebuild(s):
    chart = s["chart"]
    return "\n".join([
      "18. " + s["question"],
      "【" + chart["leftTitle"] + "】",
      chart["intro"],
      *(r["label"] + "、" + r["text"] for r in chart["emotionalLeverage"]),
      "【" + chart["rightTitle"] + "】",
      *(r["label"] + r["text"] for r in chart["replies"]),
      "【選項對應表：回擊甲／回擊乙】",
      *( "(" + r["option"] + ") " + r["responseForJia"] + "／" + r["responseForYi"] for r in s["optionRows"]),
    ])

def validate(r):
    s = r["g2StructuredSource"]
    if not r["questionId"] == "115-00-C-18": raise ValueError("wrong question")
    if len(s["chart"]["emotionalLeverage"]) != 2 or len(s["chart"]["replies"]) != 4: raise ValueError("missing source chart")
    if [r["label"] for r in s["chart"]["replies"]] != ["①", "②", "③", "④"]: raise ValueError("numbered replies")
    pairs = [(o["option"], o["responseForJia"], o["responseForYi"]) for o in s["optionRows"]]
    if pairs != [("A","①","③"),("B","①","④"),("C","②","③"),("D","②","④")]:
        raise ValueError("A-D table mismatch")
    if s["correctedOptions"] != ["回擊甲①；回擊乙③","回擊甲①；回擊乙④",
                                  "回擊甲②；回擊乙③","回擊甲②；回擊乙④"]:
        raise ValueError("corrupted answer options")
    if s["correctedCanonicalText"] != rebuild(s): raise ValueError("text doesn't roundtrip table")
    if any(fragment in s["correctedCanonicalText"] for fragment in ("第19-22", "專家座談會", "鄭之鄙人", "公告試題僅供參考")):
        raise ValueError("next-page content leaked into Q18")
    if digest(s["correctedCanonicalText"]) != s["correctedCanonicalTextSha256"]:
        raise ValueError("text SHA mismatch")
    seed = "ROLE_A_115_C18_G2_STRUCTURED_CHART_V1\n" + s["correctedCanonicalTextSha256"] + "\n" + IMAGE_SHA + "\n" + SHARED_REV
    if s["sourceRevisionSeed"] != seed or digest(seed) != s["sourceRevision"]:
        raise ValueError("source revision mismatch")
    if r["officialAnswer"]["candidateAndOfficialPrinted"] != "D":
        raise ValueError("official answer not D")
    if r["officialAnswer"]["formalG3AnswerVerifiedFlagSet"]:
        raise ValueError("unlicensed G3 release")
    d = r["downstream"]
    if d["ready"] or d["approved"] or d["live"] or d["canonicalQuestionBankEdited"] or d["sqliteEdited"]:
        raise ValueError("illegal admission")
    return True

class RoleA115C18OriginalSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(EVID.read_text(encoding="utf-8"))

    def test_exact_one_question_source_and_not_release(self):
        r = self.rec
        self.assertTrue(validate(r))
        self.assertEqual(r["status"], "SOURCE_G1_AI_VISUAL_QA_AND_G2_STRUCTURED_REPAIR_CANDIDATE_NO_RELEASE")
        self.assertEqual(r["sourceImage"]["originalManifestQaStatus"], "DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(r["g2StructuredSource"]["upstreamSharedMaterialG2Status"],
                         "ROLE_A_C16_C17_SOURCE_CANDIDATE_NOT_INDEPENDENTLY_ACCEPTED_FOR_C18")
        self.assertEqual(r["downstream"]["independentRoleEReview"], "PENDING_NEW_SOURCE_REVISION")

    def test_true_immutable_single_webp_page6_and_page7_boundary(self):
        r = self.rec
        for rel, expected_sha, expected_blob in [
          (r["sourceImage"]["path"], IMAGE_SHA, IMAGE_BLOB),
          (r["officialSource"]["page6Webp"], PAGE6_SHA, PAGE6_BLOB),
          (r["officialSource"]["nextPageWebp"], PAGE7_SHA, PAGE7_BLOB),
          (r["officialAnswer"]["publishedAnswerImage"], ANSWER_SHA, ANSWER_BLOB),
        ]:
            with self.subTest(path=rel):
                raw = (ROOT / rel).read_bytes()
                self.assertEqual(raw[:4], b"RIFF")
                self.assertEqual(raw[8:12], b"WEBP")
                self.assertEqual(digest(raw), expected_sha)
                self.assertEqual(git_blob(raw), expected_blob)
        self.assertEqual(r["sourceImage"]["crop"], [90, 1433, 1310, 1768])
        self.assertEqual(r["sourceImage"]["sizePixels"], [1220, 335])
        self.assertTrue(r["sourceImage"]["originalBinaryReused"])

    def test_legacy_q18_raw_is_preserved_not_overwritten(self):
        r = self.rec
        year = json.loads((ROOT / "sudu/data/years/115.json").read_text(encoding="utf-8"))
        raw = next(q for p in year["papers"] if p["paper"] == "00-C"
                   for q in p["questions"] if q["id"] == "115-00-C-18")
        old = r["rawOcr"]
        self.assertEqual(raw["question"], old["oldQuestion"])
        self.assertEqual(raw["options"], old["oldOptions"])
        self.assertFalse(raw["answerVerified"])
        self.assertFalse(raw["questionVerified"])
        self.assertIn("第19-22", old["oldOptions"][3])
        self.assertIn("專家座談會會議紀錄", old["oldOptions"][3])
        old_text = "\n".join([raw["question"], "--- 原始四選項 OCR ---"]+
                             ["(%s) %s" % (chr(65+i), option) for i, option in enumerate(raw["options"])])
        self.assertEqual(old_text, old["oldQuestionAndOptionsText"])
        self.assertEqual(digest(old_text), old["oldQuestionAndOptionsTextSha256"])

    def test_diagram_and_original_table_all_columns_four_rows(self):
        s = self.rec["g2StructuredSource"]
        ch = s["chart"]
        self.assertEqual(ch["leftTitle"], "趙姨娘的情勒術")
        self.assertEqual(ch["intro"], "因為我們是親人，所以：")
        self.assertEqual(ch["emotionalLeverage"], [
          {"label":"甲","text":"親人應多照顧親人。"},
          {"label":"乙","text":"我若沒面子，探春你也沒面子。"},
        ])
        self.assertEqual(ch["rightTitle"], "探春思考：用什麼回擊？")
        self.assertEqual(ch["replies"], [
          {"label":"①","text":"府裡人多嘴雜，照顧必招閒話。"},
          {"label":"②","text":"人人按禮守分，何須格外照顧。"},
          {"label":"③","text":"您向來形象差，早已無面子可言。"},
          {"label":"④","text":"我若當家犯錯，才是讓您沒面子。"},
        ])
        self.assertEqual(s["optionColumns"], ["選項", "回擊甲", "回擊乙"])
        self.assertEqual(len(s["optionRows"]), 4)
        self.assertTrue(validate(self.rec))

    def test_manifest_draft_cannot_be_falsely_upgraded_to_ready(self):
        man = json.loads((BASE / "webp-manifest.json").read_text(encoding="utf-8"))
        row = next(x for x in man["items"] if x["questionId"] == "115-00-C-18")
        self.assertEqual(row["sha256"], IMAGE_SHA)
        self.assertEqual(row["qaStatus"], "DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(row["outputSize"], [1220,335])
        self.assertEqual(row["crop"], [90,1433,1310,1768])
        self.assertFalse(self.rec["downstream"]["canonicalImageManifestEdited"])

    def test_official_published_d_and_confirmation_unchanged_not_fake_g3(self):
        r = self.rec["officialAnswer"]
        self.assertEqual(r["publishedAnswerImageSha256Recorded"], ANSWER_SHA)
        confirmation = BASE / "QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
        self.assertEqual(git_blob(confirmation.read_bytes()), CONFIRM_BLOB)
        d = json.loads(confirmation.read_text(encoding="utf-8"))
        c = next(x for doc in d["docs"] if doc["paperCode"] == "00-C"
                 for x in doc["confirmed"] if x["questionId"] == "115-00-C-18")
        self.assertEqual(c["officialConfirmedAnswer"], "D")
        self.assertEqual(c["pdfPageNumbers"], [4,5])
        self.assertEqual(c["changeFromPublishedAnswer"], "NONE_OBSERVED")
        self.assertFalse(r["formalG3AnswerVerifiedFlagSet"])
        self.assertFalse(r["reDownloadedOrRehashedPdfThisTask"])

    def test_before_after_source_diff_is_complete_and_sha_bound(self):
        r = self.rec
        s = r["g2StructuredSource"]
        before = r["rawOcr"]["oldQuestionAndOptionsText"].split("\n")
        after = s["correctedCanonicalText"].split("\n")
        expected = "\n".join(["--- raw-115-00-C-18-question-options","+++ corrected-115-00-C-18-original-table",
                              "@@ -1,%d +1,%d @@" % (len(before),len(after))]
                             + ["-"+x for x in before] + ["+"+x for x in after]) + "\n"
        self.assertEqual(s["rawToCorrectedUnifiedDiff"], expected)
        self.assertEqual(digest(s["correctedCanonicalText"]), s["correctedCanonicalTextSha256"])
        self.assertNotEqual(s["correctedCanonicalTextSha256"], r["rawOcr"]["oldQuestionAndOptionsTextSha256"])

    def test_can_reuse_separate_shared_g1_without_inheriting_q16_17_g2_status(self):
        source = json.loads((BASE / "review-evidence/115-00-C-SHARED-16-18-G2-COLUMNS-20261102.json").read_text(encoding="utf-8"))
        self.assertEqual(source["g2SourceText"]["sharedMaterialRevision"], SHARED_REV)
        self.assertEqual(self.rec["g2StructuredSource"]["upstreamSharedMaterialRevision"], SHARED_REV)
        self.assertEqual(self.rec["downstream"]["roleMasterCanonicalSourceAndSqliteIntegration"], "PENDING")

    def test_negative_mutations_fail_instead_of_faking_approval(self):
        for case in ("wrong_answer","mixed_q19","missing_reply","missing_option","bad_sha","wrong_shared_rev","promoted_g3","released"):
            with self.subTest(case=case):
                r = copy.deepcopy(self.rec)
                s = r["g2StructuredSource"]
                if case=="wrong_answer": r["officialAnswer"]["candidateAndOfficialPrinted"]="C"
                elif case=="mixed_q19": s["correctedCanonicalText"]+="\n▲閱讀下文，回答第19-22題\n"
                elif case=="missing_reply": s["chart"]["replies"].pop()
                elif case=="missing_option": s["optionRows"].pop()
                elif case=="bad_sha": s["correctedCanonicalTextSha256"]="0"*64
                elif case=="wrong_shared_rev": s["sourceRevisionSeed"]="obsolete"
                elif case=="promoted_g3": r["officialAnswer"]["formalG3AnswerVerifiedFlagSet"]=True
                else: r["downstream"]["approved"]=True
                with self.assertRaises(ValueError): validate(r)

    def test_bank_database_integrity_and_claimed_file_scope(self):
        db = BASE / "question-bank.sqlite3"
        self.assertTrue(db.exists())
        con = sqlite3.connect("file:"+str(db)+"?mode=ro",uri=True)
        try: self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
        finally: con.close()
        r = subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,
                           capture_output=True,text=True,check=True)
        self.assertEqual(set(r.stdout.splitlines()), EXPECTED_CHANGE)
        self.assertFalse(self.rec["downstream"]["sqliteEdited"])
        self.assertFalse(self.rec["downstream"]["canonicalQuestionBankEdited"])

if __name__=="__main__":
    unittest.main()
