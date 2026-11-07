"""Strict source-only regression: 114 E12 changes alone, E/D release stay denied."""
import importlib.util, json, sqlite3, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts/master_114_e12_qa_source_bridge_20261107.py"
spec=importlib.util.spec_from_file_location("e12_source_rescue",SOURCE)
e12=importlib.util.module_from_spec(spec);spec.loader.exec_module(e12)
BASE_SHA="16d04a0d642fb433de289417a22c3050aa3e52b6"
BASE=ROOT/"sudu/data/processed/114"
STAGE=ROOT/"_role_a_e12_stage"

def git_old(rel):
    return subprocess.check_output(["git","show",BASE_SHA+":"+rel],cwd=ROOT)
class SourceE12(unittest.TestCase):
    def test_exact_qid_and_other_204_unchanged(self):
        old=json.loads(git_old("sudu/data/processed/114/questions.json"))
        new=json.loads((BASE/"questions.json").read_bytes())
        self.assertEqual(len(old["questions"]),len(new["questions"]))
        self.assertEqual(len(new["questions"]),205)
        oldd={q["questionId"]:q for q in old["questions"]}
        newd={q["questionId"]:q for q in new["questions"]}
        self.assertEqual(set(oldd),set(newd))
        self.assertEqual({k:v for k,v in oldd.items() if k!=e12.QID},
                         {k:v for k,v in newd.items() if k!=e12.QID})
        q=newd[e12.QID]
        self.assertTrue(q["questionVerified"])
        self.assertTrue(q["answerVerified"])
        self.assertEqual(q["textQaStatus"],"PASS")
        self.assertEqual(q["officialFinalAnswer"],"C")
        self.assertEqual(q["textQaEvidence"]["questionRevision"],e12.EXPECTED_REVISION)
        self.assertFalse(q.get("studentReleaseApproved",False))
        self.assertNotEqual(q.get("teachingQaStatus"),"PASS")
        self.assertNotEqual(q.get("uiQaStatus"),"PASS")
        self.assertEqual(git_old("sudu/data/processed/114/webp-manifest.json"),
                         (BASE/"webp-manifest.json").read_bytes())

    def test_real_sqlite_all_205_other_204_byte_equal(self):
        with tempfile.TemporaryDirectory() as tmp:
            old=Path(tmp)/"old.sqlite3"
            old.write_bytes(git_old("sudu/data/processed/114/question-bank.sqlite3"))
            with sqlite3.connect("file:"+old.as_posix()+"?mode=ro",uri=True) as db:
                before=db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
            with sqlite3.connect("file:"+(BASE/"question-bank.sqlite3").as_posix()+"?mode=ro",uri=True) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                after=db.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
            self.assertEqual(len(before),205)
            self.assertEqual(len(after),205)
            self.assertEqual({q:(v,h) for q,v,h in before if q!=e12.QID},
                             {q:(v,h) for q,v,h in after if q!=e12.QID})
            q=json.loads((BASE/"questions.json").read_text())["questions"]
            q=next(x for x in q if x["questionId"]==e12.QID)
            payload,hashval=next((v,h) for name,v,h in after if name==e12.QID)
            self.assertEqual(json.loads(payload),q)
            self.assertEqual(e12.sha(payload.encode("utf-8")),hashval)

    def test_source_provenance_and_no_release(self):
        proof=e12.load(ROOT/e12.REPORT)
        self.assertEqual(proof["gate"],"SOURCE_G1_G2_G3_ONLY_NOT_STUDENT_ADMISSION")
        self.assertEqual(proof["officialPublishedAnswer"],"C")
        self.assertEqual(proof["other204SqlitePayloadsUnchanged"],True)
        self.assertEqual(proof["other204JsonRecordsUnchanged"],True)
        self.assertEqual(proof["correctionNamedOnly"],["114-00-E-26"])
        for key in ["studentReady","independentRoleETrustedReceipt",
                    "roleDFormalEmitter16of16","mainApprovedOrLive"]:
            self.assertIs(proof[key],False)
        e12.main(STAGE,False)  # exact real source evidence still verifies after mutation

    def test_sqlite_inventory_hashes_are_true(self):
        inv=json.loads((BASE/"inventory.json").read_text(encoding="utf-8"))
        bank=(BASE/"questions.json").read_bytes()
        rawdb=(BASE/"question-bank.sqlite3").read_bytes()
        s=inv["sqlite"]
        self.assertTrue(s["roundtripPass"])
        self.assertEqual(s["rows"],205)
        self.assertEqual(s["sourceQuestionsSha256"],e12.sha(bank))
        self.assertEqual(s["dbSha256"],e12.sha(rawdb))
        self.assertEqual(s["evidencePath"],
            "sudu/data/processed/114/SQLITE_QA_E12_SOURCE_BRIDGE_20261107.json")
        proof=json.loads((ROOT/s["evidencePath"]).read_text(encoding="utf-8"))
        self.assertEqual(proof["databaseSha256"],s["dbSha256"])
        self.assertEqual(proof["sourceQuestionsSha256"],s["sourceQuestionsSha256"])
        self.assertEqual(proof["other204PayloadsUnchanged"],True)
        self.assertFalse(proof["studentReleaseApproved"])

    def test_negative_receipt_mutations_fail_closed(self):
        files=[e12.STAGE_RECEIPT,e12.OFFICIAL_RECEIPT]
        for path,field in [(e12.STAGE_RECEIPT,"wrong-source-A-D"),
                           (e12.OFFICIAL_RECEIPT,"wrong-published-answer")]:
            with self.subTest(field=field),tempfile.TemporaryDirectory() as tmp:
                tmp=Path(tmp)
                for f in files:
                    dest=tmp/f
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes((STAGE/f).read_bytes())
                target=tmp/path
                d=json.loads(target.read_text())
                if path==e12.STAGE_RECEIPT:
                    d["source"]["options"][2]="Tampered original"
                else:
                    d["publishedOfficialAnswer"]["answer"]="A"
                target.write_text(json.dumps(d),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"SOURCE_HOLD"):
                    e12.main(tmp,False)

if __name__=="__main__": unittest.main()
