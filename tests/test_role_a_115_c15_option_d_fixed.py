"""Role A Q15 surgically corrected JSON+SQLite, independent source text QA still pending.

Strict negative/immutability checks against real Git base (PR61 exact SHA).
Only canonical Q15 structured D is cleaned; raw extraction remains original contaminated.
"""
import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import sudu_verified_publish as publisher

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="2bc5122a7edd4ba5a357cb62458003a2e31856d4"
QID="115-00-C-15"
ORIGINAL_WEBP_SHA="74dc7bb966f1ee508456a962a6fbcff0f42a15b2ffdd8db747477a55b831405f"
CORRECT_D="拘泥禮法 ／ 不知變通"
SRC=ROOT/"sudu/data/processed/115"
BANK=SRC/"questions.json"
DB=SRC/"question-bank.sqlite3"
REPORT=SRC/"QA_115_C15_OPTION_D_CROSSPAGE_CORRECTION_20261025.json"

def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def old_git_file(name):
    r=subprocess.run(["git","show",BASE_SHA+":"+name],cwd=ROOT,capture_output=True)
    assert r.returncode==0, (name,r.stderr[:300])
    return r.stdout

class OnlyQ15TextAndDBCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=json.loads(BANK.read_text(encoding="utf-8"))
        cls.old=json.loads(old_git_file("sudu/data/processed/115/questions.json").decode("utf-8"))
        cls.qmap={q["questionId"]:q for q in cls.current["questions"]}
        cls.omap={q["questionId"]:q for q in cls.old["questions"]}
        assert len(cls.current["questions"])==len(cls.qmap)==len(cls.old["questions"])==len(cls.omap)==205
        cls.report=json.loads(REPORT.read_text(encoding="utf-8"))

    def test_exact_canonical_ids_and_single_original_option_diff_only(self):
        self.assertEqual(set(self.qmap),set(self.omap))
        self.assertEqual(self.current["year"],115)
        for qid,orig in self.omap.items():
            with self.subTest(qid=qid):
                target=self.qmap[qid]
                if qid==QID:
                    oldopts=orig["options"]
                    expect=json.loads(json.dumps(orig,ensure_ascii=False))
                    expect["options"][3]=CORRECT_D
                    self.assertEqual(target,expect)
                    self.assertEqual(target["options"][:3],oldopts[:3])
                else:
                    self.assertEqual(target,orig)

    def test_q15_removed_page_footer_and_next_examination_group_only(self):
        q=self.qmap[QID]
        self.assertEqual(q["options"][3],CORRECT_D)
        self.assertEqual(len(q["options"]),4)
        self.assertNotIn("第6 頁",q["options"][3])
        self.assertNotIn("▲閱讀下文",q["options"][3])
        self.assertNotIn("公告試題僅供參考",q["options"][3])
        self.assertTrue(self.omap[QID]["options"][3].startswith(CORRECT_D))
        self.assertIn("▲閱讀下文，回答第16-18 題",self.omap[QID]["options"][3])
        self.assertIn("公告試題僅供參考",self.omap[QID]["options"][3])
        self.assertEqual(q["extraction"]["rawOptions"],self.omap[QID]["extraction"]["rawOptions"])
        self.assertIn("▲閱讀下文，回答第16-18 題",q["extraction"]["rawOptions"][3])

    def test_full_strict_crypto_image_source_and_manifest_no_mutation(self):
        p=ROOT/"sudu/data/processed/115/webp-v2/00-C/115-00-C-15.webp"
        self.assertEqual(sha(p.read_bytes()),ORIGINAL_WEBP_SHA)
        man=json.loads((SRC/"webp-manifest.json").read_text(encoding="utf-8"))
        im=next(x for x in man["items"] if x["questionId"]==QID)
        self.assertEqual(im["sha256"],ORIGINAL_WEBP_SHA)
        self.assertEqual(im["qaStatus"],"PASS") # original historical image-only status
        self.assertEqual(im["crop"],[90,1421,1310,1660])
        self.assertEqual(self.qmap[QID]["assets"]["sha256"],ORIGINAL_WEBP_SHA)
        self.assertEqual(self.qmap[QID]["questionProvenance"],self.omap[QID]["questionProvenance"])
        self.assertEqual(self.qmap[QID]["answerProvenance"],self.omap[QID]["answerProvenance"])

    def test_source_revision_tamper_proof_and_precise_evidence(self):
        original=self.omap[QID]
        fixed=self.qmap[QID]
        prev=publisher.text_revision(original,ORIGINAL_WEBP_SHA)
        now=publisher.text_revision(fixed,ORIGINAL_WEBP_SHA)
        self.assertNotEqual(now,prev)
        self.assertEqual(self.report["taskId"],"A-115-C15-OPTION-D-CROSSPAGE-SQLITE-20261025-09")
        self.assertEqual(self.report["sourceRevisionBefore"],prev)
        self.assertEqual(self.report["sourceRevisionAfter"],now)
        self.assertEqual(self.report["originalRawOptionDSha256"],sha(original["options"][3].encode("utf-8")))
        self.assertEqual(self.report["correctedOptionDSha256"],sha(CORRECT_D.encode("utf-8")))
        self.assertEqual(self.report["sourceOriginalSingleWebpSha256"],ORIGINAL_WEBP_SHA)
        self.assertTrue(self.report["preservedRawExtraction"])
        self.assertFalse(self.report["studentReleaseApproved"])
        self.assertEqual(self.report["newReady"],0)
        self.assertEqual(self.report["newLive"],0)

    def test_all_205_sqlite_records_match_corrected_json_and_valid_hash(self):
        with sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True) as cx:
            self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            rows=cx.execute("""SELECT question_id,question,payload_json,payload_sha256,answer,
                               answer_verified,question_verified FROM questions""").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({r[0] for r in rows},set(self.qmap))
        denormalized_drift=[]
        for id_,stem,payload,digest,answer,av,qv in rows:
            with self.subTest(question=id_):
                q=self.qmap[id_]
                self.assertEqual(stem,q["question"])
                self.assertEqual(payload,canonical(q))
                self.assertEqual(sha(payload.encode("utf-8")),digest)
                self.assertEqual(json.loads(payload),q)
                self.assertEqual(answer,q["answer"])
                self.assertIn(av,(0,1))
                self.assertIn(qv,(0,1))
                if bool(av)!=q["answerVerified"] or bool(qv)!=q["questionVerified"]:
                    denormalized_drift.append(id_)
        self.assertEqual(denormalized_drift,self.report["preexistingSqliteDenormalizedFlagDivergences"])
        self.assertEqual(len(denormalized_drift),self.report["preexistingSqliteDenormalizedFlagDivergenceCount"])

    def test_only_q15_sql_payload_changed_against_exact_original_git_base(self):
        with tempfile.TemporaryDirectory() as td:
            original_db=Path(td)/"previous.sqlite3"
            original_db.write_bytes(old_git_file("sudu/data/processed/115/question-bank.sqlite3"))
            with sqlite3.connect(original_db.as_uri()+"?mode=ro",uri=True) as cx:
                past={id_:(body,digest,av,qv) for id_,body,digest,av,qv in cx.execute("SELECT question_id,payload_json,payload_sha256,answer_verified,question_verified FROM questions")}
            with sqlite3.connect(DB.as_uri()+"?mode=ro",uri=True) as cx:
                curr={id_:(body,digest,av,qv) for id_,body,digest,av,qv in cx.execute("SELECT question_id,payload_json,payload_sha256,answer_verified,question_verified FROM questions")}
            self.assertEqual(set(past),set(curr))
            self.assertEqual({qid for qid in past if past[qid]!=curr[qid]},{QID})
            self.assertEqual({qid for qid in past if past[qid][2:]!=curr[qid][2:]},set())
            self.assertEqual(self.report["sqliteCorrectedPayloadSha256"],curr[QID][1])

    def test_historical_answer_flags_no_lesson_or_student_release_promotion(self):
        q=self.qmap[QID];prior=self.omap[QID]
        self.assertEqual(q["answer"],"B")
        self.assertTrue(q["answerVerified"])
        self.assertFalse(q["questionVerified"])
        self.assertFalse(q["integrationReady"])
        self.assertEqual(q["answerQaEvidence"],prior["answerQaEvidence"])
        self.assertEqual(q["imageQaStatus"],"PASS")
        self.assertEqual(q["assets"]["visualQa"],prior["assets"]["visualQa"])
        self.assertEqual(q["reviewStatus"],prior["reviewStatus"])
        approved=json.loads((ROOT/"sudu/data/approved/115.json").read_text(encoding="utf-8"))
        self.assertEqual(approved["approvedCount"],5)
        self.assertNotIn(QID,{x["canonicalId"] for x in approved["questions"]})

    def test_wrong_corrected_option_or_wrong_webp_source_revision_fails(self):
        import copy
        mutated=copy.deepcopy(self.qmap[QID])
        mutated["options"][3]+=" fake-page"
        self.assertNotEqual(publisher.text_revision(mutated,ORIGINAL_WEBP_SHA),
                            self.report["sourceRevisionAfter"])
        self.assertNotEqual(publisher.text_revision(self.qmap[QID],"0"*64),
                            self.report["sourceRevisionAfter"])

if __name__=="__main__":
    unittest.main()
