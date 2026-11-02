"""Role A exact official C16/C17 shared G2 split-source receipt, no student admission."""
import copy
import hashlib
import json
import sqlite3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/115"
EVID = BASE / "review-evidence/115-00-C-SHARED-16-18-G2-COLUMNS-20261102.json"
G1 = BASE / "qa-drafts/DIRECT_VISUAL_SHARED_115_C_16_18_V4_20261023.json"
OLD_SHA = "cf44ba29b44872af4bed426dd6d2c50489b12ed7b8e0b64482915c9b37c82f25"
NEW_IMAGE_SHA = "f1a3eac89b4f1db5d32a6511f070ef463a8759116a780257a7c213ab5d1fd77c"
NEW_IMAGE_BLOB = "6a844f0bd1e843a22f972d425be7c0167bec37c3"
PAGE_SHA = "8b6c781a75a864b7220f686532225171b2f53346c68f5131470371f82731e6c6"
PAGE_BLOB = "442195469f22bf49c993271633f24ad9eafbc937"
CERT_BLOB = "c4566ac2857f1f5ab3920c48c1a7809b35261e83"
ALLOWED = {
    "sudu/data/processed/115/review-evidence/115-00-C-SHARED-16-18-G2-COLUMNS-20261102.json",
    "sudu/data/processed/115/qa-drafts/webp-v4/shared/115-00-C-SHARED-16-18.webp",
    "sudu/data/processed/115/qa-drafts/DIRECT_VISUAL_SHARED_115_C_16_18_V4_20261023.json",
    "tests/test_role_a_115_c16_c17_shared_g2.py",
    ".github/workflows/role-a-115-c16-c17-g2.yml",
    "docs/ROLE_A_115_C16_C17_SHARED_G2_20261102.md",
}

def sha(raw):
    return hashlib.sha256(raw if isinstance(raw, bytes) else raw.encode("utf-8")).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def text(d):
    left = [d["header"]]
    for turn in d["dialogueTurns"]:
        left.append(("探 春" if turn["speaker"] == "探春" else turn["speaker"]) + "：" + turn["text"])
    left.append(d["byline"])
    return "\n".join(left + ["【右欄方框旁註】"] + ["■" + n for n in d["rightColumnBoxedNotes"]])

def validate(record):
    s, raw = record["g2SourceText"], record["rawOcr"]
    if len(s["dialogueTurns"]) != 16 or len(s["rightColumnBoxedNotes"]) != 4:
        raise ValueError("missing or extra original dialogue/note")
    if [t["speaker"] for t in s["dialogueTurns"]] != ["趙姨娘","探春"] * 8:
        raise ValueError("speaker order")
    if s["correctedSourceText"] != text(s):
        raise ValueError("source text does not roundtrip")
    if any("■" in t["text"] or "【右欄" in t["text"] for t in s["dialogueTurns"]):
        raise ValueError("right column mixed into dialogue")
    if "鴛鴦是趙姨娘：" in s["correctedSourceText"] or "賈母的丫鬟。探 春：" in s["correctedSourceText"]:
        raise ValueError("old cross-column OCR pollution")
    if sha(s["correctedSourceText"]) != s["correctedTextSha256"]:
        raise ValueError("corrected source SHA invalid")
    if sha(raw["rawSourceText"]) != raw["rawSourceTextSha256"] or raw["rawSourceTextSha256"] != OLD_SHA:
        raise ValueError("old raw OCR SHA invalid")
    seed = "ROLE_A_G2_TWO_COLUMN_V1\n" + s["correctedTextSha256"] + "\n" + NEW_IMAGE_SHA + "\n" + PAGE_SHA
    if seed != s["sharedMaterialRevisionSeed"] or sha(seed) != s["sharedMaterialRevision"]:
        raise ValueError("source revision not SHA-pinned")
    if record["downstream"]["ready"] or record["downstream"]["approved"] or record["downstream"]["live"]:
        raise ValueError("illegal student approval")
    if record["downstream"]["individualQuestion18G2"] != "NOT_REVIEWED":
        raise ValueError("Q18 gate improperly inherited")
    return True

class RoleAC16C17OriginalSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(EVID.read_text(encoding="utf-8"))

    def test_source_scope_and_fail_closed(self):
        r = self.rec
        self.assertEqual(r["questionIds"], ["115-00-C-16", "115-00-C-17"])
        self.assertEqual(r["sharedMaterialId"], "115-00-C-SHARED-16-18")
        self.assertEqual(r["alsoReferencedByUnreviewedQuestion"], "115-00-C-18")
        self.assertEqual(r["status"], "ROLE_A_SOURCE_G2_ASSISTANT_VISUAL_REPAIR_CANDIDATE_NO_RELEASE")
        self.assertEqual(r["g2SourceText"]["officialFinalAnswerG3"], "PENDING_SEPARATE_PER_QUESTION_CORRECTION_SCOPE_VALIDATION")
        self.assertFalse(r["downstream"]["sqliteModified"])
        self.assertFalse(r["downstream"]["canonicalQuestionsJsonModified"])
        self.assertFalse(r["downstream"]["roleCOriginalTeachingModified"])
        self.assertTrue(validate(r))

    def test_preserve_actual_raw_ocr_and_nonempty_true_diff(self):
        r, s = self.rec, self.rec["g2SourceText"]
        raw = r["rawOcr"]["rawSourceText"]
        self.assertEqual(sha(raw), OLD_SHA)
        self.assertIn("鴛鴦是趙姨娘：鴛鴦母親呢？", raw)
        self.assertIn("賈母的丫鬟。探 春：也是四十。", raw)
        self.assertNotIn("鴛鴦是趙姨娘：", s["correctedSourceText"])
        self.assertNotEqual(s["correctedTextSha256"], OLD_SHA)
        before, after = raw.split("\n"), s["correctedSourceText"].split("\n")
        expected = "\n".join(["--- raw-PR112-shared-sourceText", "+++ role-A-corrected-two-column-sourceText",
                              "@@ -1,%d +1,%d @@" % (len(before), len(after))]
                             + ["-" + ln for ln in before] + ["+" + ln for ln in after]) + "\n"
        self.assertEqual(s["beforeAfterUnifiedDiff"], expected)

    def test_all_sixteen_dialogue_turns_in_printed_order(self):
        s = self.rec["g2SourceText"]
        self.assertEqual(len(s["dialogueTurns"]), 16)
        self.assertEqual(s["dialogueTurns"][0]["text"], "姑娘當家理事，頭一樁，發放了二十兩喪葬銀子，這是給誰的呀？")
        self.assertEqual(s["dialogueTurns"][6]["text"], "鴛鴦母親呢？")
        self.assertEqual(s["dialogueTurns"][7]["text"], "也是四十。")
        self.assertIn("斬釘截鐵乾乾淨淨", s["dialogueTurns"][10]["text"])
        self.assertIn("探春當家，豈能逾矩？", s["dialogueTurns"][13]["text"])
        self.assertEqual(s["dialogueTurns"][-1]["text"], "我怎麼忘了？叫我怎樣拉拔？哪有個行端理正的，要人拉拔？")
        self.assertEqual(s["byline"], "（王安祈〈紅樓夢中人‧探春〉）")

    def test_right_column_four_original_boxed_notes_separated(self):
        ns = self.rec["g2SourceText"]["rightColumnBoxedNotes"]
        self.assertEqual(ns, [
            "趙姨娘原是賈府小廝的女兒，後為賈政之妾。",
            "文中「夫人」、「太太」指賈政正室王夫人。",
            "「老祖宗」指賈政母親。",
            "襲人是賈寶玉的丫鬟，鴛鴦是賈母的丫鬟。",
        ])
        for note in ns:
            self.assertNotIn(note, "\n".join(t["text"] for t in self.rec["g2SourceText"]["dialogueTurns"]))

    def test_actual_immutable_original_source_pixels(self):
        r = self.rec
        image = (ROOT / r["sourceImage"]["path"]).read_bytes()
        self.assertEqual(image[:4], b"RIFF")
        self.assertEqual(image[8:12], b"WEBP")
        self.assertEqual(sha(image), NEW_IMAGE_SHA)
        self.assertEqual(git_blob(image), NEW_IMAGE_BLOB)
        page = (ROOT / r["officialSource"]["originalPageWebp"]).read_bytes()
        self.assertEqual(sha(page), PAGE_SHA)
        self.assertEqual(git_blob(page), PAGE_BLOB)
        self.assertEqual(r["sourceImage"]["cropOriginalPixels"], [90, 161, 1310, 1059])
        self.assertFalse(r["sourceImage"]["originalWebpRecreated"])

    def test_original_g1_certificate_is_exact_git_blob(self):
        raw = G1.read_bytes()
        self.assertEqual(git_blob(raw), CERT_BLOB)
        obj = json.loads(raw)
        self.assertEqual(obj["newWebpSha256"], NEW_IMAGE_SHA)
        self.assertEqual(obj["sourcePageWebpSha256"], PAGE_SHA)
        self.assertEqual(obj["result"], "PASS_DIRECT_ORIGINAL_OFFICIAL_PAGE_SHARED_MATERIAL_VISUAL")
        self.assertFalse(obj["releaseAllowed"])
        self.assertEqual(obj["questionIds"], ["115-00-C-16", "115-00-C-17", "115-00-C-18"])

    def test_new_revision_recomputes_and_is_not_stale(self):
        r = self.rec
        self.assertTrue(validate(r))
        self.assertNotEqual(r["g2SourceText"]["sharedMaterialRevision"], r["rawOcr"]["oldSharedMaterialRevision"])
        self.assertEqual(r["g2SourceText"]["correctedTextSha256Method"], "SHA256(UTF8(correctedSourceText))")

    def test_negative_mutations_cannot_pass(self):
        for mutation in ("lost_dialogue","lost_note","mixed","badsha","oldrevision","promote18","approve"):
            with self.subTest(mutation=mutation):
                r = copy.deepcopy(self.rec)
                s = r["g2SourceText"]
                if mutation == "lost_dialogue":
                    s["dialogueTurns"].pop()
                elif mutation == "lost_note":
                    s["rightColumnBoxedNotes"].pop()
                elif mutation == "mixed":
                    s["correctedSourceText"] = s["correctedSourceText"].replace("鴛鴦母親呢？", "鴛鴦是趙姨娘：鴛鴦母親呢？")
                elif mutation == "badsha":
                    s["correctedTextSha256"] = "0" * 64
                elif mutation == "oldrevision":
                    s["sharedMaterialRevision"] = r["rawOcr"]["oldSharedMaterialRevision"]
                elif mutation == "promote18":
                    r["downstream"]["individualQuestion18G2"] = "PASS"
                else:
                    r["downstream"]["approved"] = True
                with self.assertRaises(ValueError):
                    validate(r)

    def test_existing_sqlite_is_not_corrupted_by_source_receipt(self):
        db = BASE / "question-bank.sqlite3"
        self.assertTrue(db.is_file())
        con = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True)
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            self.assertTrue(tabs)
            self.assertTrue(any("question" in tab.lower() for tab in tabs))
        finally:
            con.close()

    def test_commit_changes_only_claimed_files(self):
        run = subprocess.run(["git", "diff", "--name-only", "HEAD^", "HEAD"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        actual = set(run.stdout.splitlines())
        self.assertEqual(actual, ALLOWED, "Unleased changes detected: %s" % sorted(actual - ALLOWED))

if __name__ == "__main__":
    unittest.main()
