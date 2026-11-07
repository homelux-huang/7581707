"""ROLE A 114 Economics Q34 immutable image, direct G2 and printed answer A, strict NO RELEASE."""
import copy,hashlib,json,sqlite3,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
ID="114-09-2-34"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def source_revision(q,m):return sha(json.dumps({"question":q["question"],"options":q["options"],"singleQuestionWebpSha256":m["sha256"]},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def valid(e,q,m,nt):
 s,a,n=e["source"],e["official"],e["next"]
 if e["questionId"]!=ID or q["questionId"]!=ID or m["questionId"]!=ID:raise ValueError("id")
 if s["rawOcrPreserved"]!=q["question"] or s["correctedG2TextSameAsRaw"]!=q["question"] or s["optionsAsPrinted"]!=q["options"] or len(q["options"])!=4:raise ValueError("text")
 if s["originalSingleWebpPath"]!=m["output"] or s["originalSingleWebpSha256"]!=m["sha256"] or s["originalPagePath"]!=m["source"] or s["originalPageSha256"]!=m["sourceSha256"]:raise ValueError("image")
 if s["sourceRevisionB"]!=source_revision(q,m) or e["teaching"]["sourceRevision"]!=s["sourceRevisionB"]:raise ValueError("revision")
 if a["printedAnswer"]!="A" or q["answer"]!="A" or a["officialPublishedAnswerGitBlob"]!="1ed318724f70ad4f81e472a775cdb9e21fcba2fc":raise ValueError("answer")
 noticeIds=[v["questionId"] for v in nt["confirmed"]]
 if ID in noticeIds or a["noticeNamedForThisQuestion"] or a["noticeNamedQuestionIds"]!=noticeIds or a["claimOfEntirePaperFinality"]:raise ValueError("notice")
 if a["formalAnswerVerifiedPromoted"] or a["officialPdfDownloadedOrRehashedThisTask"] or n["READY"] or n["LIVE"]:raise ValueError("release")
 if e["canonical"]["questionVerifiedPrior"] or e["canonical"]["answerVerifiedPrior"] or not e["canonical"]["canonical205QuestionJsonAndSqliteUnchanged"]:raise ValueError("canonical")
 if s["sourceRevised"] or s["originalWebpRecreated"] or not s["noCrossPageOrNeighborQuestion"]:raise ValueError("source")
 return True
class Econ34(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.bank=read(BASE/"questions.json")
  cls.manifest=read(BASE/"webp-manifest.json")
  cls.e=read(BASE/"review-evidence/114-09-2-34-original-20261107.json")
  cls.q=next(x for x in cls.bank["questions"] if x["questionId"]==ID)
  cls.m=next(x for x in cls.manifest["items"] if x["questionId"]==ID)
  cls.nt=next(x for x in read(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")["docs"] if x["paperCode"]=="09-2")
 def test_205_json_sqlite_integrity(self):
  self.assertEqual(len(self.bank["questions"]),205)
  self.assertEqual(len(self.manifest["items"]),205)
  self.assertFalse(self.q["answerVerified"])
  self.assertFalse(self.q["questionVerified"])
  self.assertEqual(self.m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
  with sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True) as con:
   self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
   self.assertEqual(con.execute("SELECT COUNT(*) FROM questions").fetchone()[0],205)
   row=con.execute("SELECT payload_json,payload_sha256 FROM questions WHERE question_id=?",(ID,)).fetchone()
   self.assertIsNotNone(row)
   self.assertEqual(json.loads(row[0]),self.q)
   self.assertEqual(sha(row[0].encode("utf-8")),row[1])
 def test_original_image_answer_notice_and_revision(self):
  self.assertTrue(valid(self.e,self.q,self.m,self.nt))
  s,a=self.e["source"],self.e["official"]
  for path,sha256,git_sha in [(s["originalSingleWebpPath"],s["originalSingleWebpSha256"],s["originalSingleWebpGitBlob"]),(s["originalPagePath"],s["originalPageSha256"],s["originalPageGitBlob"]),(a["officialPublishedAnswerPage"],None,a["officialPublishedAnswerGitBlob"]),(a["noticeLedgerPath"],None,a["noticeLedgerGitBlob"])]:
   b=(ROOT/path).read_bytes()
   self.assertEqual(blob(b),git_sha)
   if sha256:self.assertEqual(sha(b),sha256)
  self.assertEqual(s["crop"],self.m["crop"])
  self.assertEqual(self.e["teaching"]["sourceRevision"],"a32b0c7fef1aa7d30e252bff3393f2c57088101767c4b99430cde4924f562eb8")
 def test_negative_no_release_or_forged_source(self):
  for case in ("wronganswer","wrongrevision","alteredoption","fakeimage","fake_notice","ready","promoted"):
   with self.subTest(case=case):
    d=copy.deepcopy(self.e)
    if case=="wronganswer":d["official"]["printedAnswer"]="B"
    if case=="wrongrevision":d["source"]["sourceRevisionB"]="0"*64
    if case=="alteredoption":d["source"]["optionsAsPrinted"][0]="wrong"
    if case=="fakeimage":d["source"]["originalSingleWebpSha256"]="0"*64
    if case=="fake_notice":d["official"]["noticeNamedForThisQuestion"]=True
    if case=="ready":d["next"]["READY"]=True
    if case=="promoted":d["official"]["formalAnswerVerifiedPromoted"]=True
    with self.assertRaises(ValueError):valid(d,self.q,self.m,self.nt)
 def test_exact_only_four_additive_files(self):
  expected={"sudu/data/processed/114/review-evidence/114-09-2-34-original-20261107.json","tests/test_role_a_114_econ34_source_20261107.py",".github/workflows/role-a-114-econ34-source-20261107.yml","docs/ROLE_A_114_ECON34_SOURCE_20261107.md"}
  r=subprocess.run(["git","diff","--name-only","HEAD~4","HEAD"],text=True,capture_output=True,check=True,cwd=ROOT)
  self.assertEqual(set(r.stdout.splitlines()),expected)
if __name__=="__main__":unittest.main()
