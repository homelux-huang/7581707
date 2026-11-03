"""Role A exact original 115 English p6/p10 shared reading G1 direct-source visual receipts (NO RELEASE)."""
import copy, hashlib, json, sqlite3, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
EVID=BASE/"review-evidence/115-00-E-29-30-39-41-shared-G1-20261103.json"
def rawsha(d):return hashlib.sha256(d).hexdigest()
def gitblob(d):return hashlib.sha1(b"blob "+str(len(d)).encode("ascii")+b"\0"+d).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
EXPECTED_Q={29:"A",30:"C",39:"B",40:"D",41:"D"}
SHARED_SHAS={
"115-00-E-SHARED-29-30":"e932d3fc246b55604cabd6fa1716d0fa6f8f67d658ed6a16c6d88f91bfdb49b6",
"115-00-E-SHARED-39-42":"5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b"
}
EXPECTED_REFS={
"115-00-E-SHARED-29-30":"1938fe2a22233a82528c111547ec3f1a522d201b",
"115-00-E-SHARED-39-42":"4aaac02b7ed9390b8ff7c8a4c4272e74996bd595"
}
def validate(x):
  q=x["questionRecords"];s=x["shared"];notice=x["officialNotice"];down=x["downstream"]
  if [i["number"] for i in q]!=[29,30,39,40,41]:raise ValueError("wrong task scope")
  if [i["originalAnswer"] for i in q]!=["A","C","B","D","D"]:raise ValueError("published answer contradiction")
  if [i["sharedId"] for i in q]!=[s[0]["id"],s[0]["id"],s[1]["id"],s[1]["id"],s[1]["id"]]:
    raise ValueError("shared material relation")
  if [i["id"] for i in s]!=["115-00-E-SHARED-29-30","115-00-E-SHARED-39-42"]:raise ValueError("incorrect shared ID")
  if [i["sha256"] for i in s] != [SHARED_SHAS[i["id"]] for i in s]:raise ValueError("shared image mismatch")
  if not all(z["newReview"]=="PASS_AI_ASSISTANT_DIRECT_ORIGINAL_VISUAL_SOURCE_ONLY" and z["contentsComplete"] for z in s):
    raise ValueError("unverified original shared")
  if s[1]["unreviewedQid"]!="115-00-E-42" or down["q42IndividualG1G2G3State"]!="NOT_REVIEWED_IN_THIS_TASK":
    raise ValueError("Q42 inherited review")
  if notice["namedQids"]!=["115-00-E-34"] or notice["namedOfficialAnswer"]!="B":
    raise ValueError("official correction scope wrong")
  if not notice["noNamedNoticeForClaimedQids"] or notice["formalG3AdmissionPerformed"]:
    raise ValueError("formal G3 approval wrongly issued")
  if any(down[k] for k in ("canonical205BankEdited","sqliteEdited","manifestQaStatusChanged","roleCTeachingEdited","roleEIndependentContent","roleDReal8x2","masterAdmittedToReady","approved","live")):
    raise ValueError("illegal student/source promotion")
  return True
class RoleA115EnglishSourceQA(unittest.TestCase):
  @classmethod
  def setUpClass(cls):cls.ev=read(EVID)
  def test_true_existing_original_shared_images_and_source_pages(self):
    self.assertTrue(validate(self.ev))
    manifest=read(BASE/"webp-manifest.json")
    for x in self.ev["shared"]:
      with self.subTest(id=x["id"]):
        imgdata=(ROOT/x["path"]).read_bytes()
        self.assertEqual(imgdata[:4],b"RIFF")
        self.assertEqual(imgdata[8:12],b"WEBP")
        self.assertEqual(rawsha(imgdata),SHARED_SHAS[x["id"]])
        self.assertEqual(gitblob(imgdata),EXPECTED_REFS[x["id"]])
        source=(ROOT/x["source"]).read_bytes()
        self.assertEqual(rawsha(source),x["sourceSha256"])
        self.assertEqual(gitblob(source),x["sourceBlob"])
        with Image.open(ROOT/x["path"]) as im:
          self.assertEqual(im.format,"WEBP")
          self.assertEqual(list(im.size),x["outputSize"])
        expectedWidth=x["crop"][2]-x["crop"][0]
        expectedHeight=x["crop"][3]-x["crop"][1]
        self.assertEqual(x["outputSize"],[expectedWidth,expectedHeight])
        m=next(a for a in manifest["sharedMaterialCrops"] if a["sharedMaterialId"]==x["id"])
        self.assertEqual(m["sha256"],x["sha256"])
        self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA")
        self.assertEqual(m["crop"],x["crop"])
        seed="ROLE_A_115_ENGLISH_SHARED_G1_V1\n"+x["sha256"]+"\n"+x["sourceSha256"]
        self.assertEqual(x["sourceRevisionSeed"],seed)
        self.assertEqual(x["sourceRevisionSha256"],rawsha(seed.encode("utf-8")))
        self.assertFalse(x["otherQidsQAChanged"])
  def test_five_true_original_single_assets_and_official_published_answers(self):
    man=read(BASE/"webp-manifest.json")
    for x in self.ev["questionRecords"]:
      with self.subTest(id=x["questionId"]):
        data=(ROOT/x["image"]).read_bytes()
        self.assertEqual(rawsha(data),x["sha256"])
        self.assertEqual(gitblob(data),x["gitBlob"])
        q=next(a for a in man["items"] if a["questionId"]==x["questionId"])
        self.assertEqual(q["sha256"],x["sha256"])
        self.assertEqual(q["qaStatus"],"PASS")
        self.assertEqual(EXPECTED_Q[x["number"]],x["originalAnswer"])
  def test_pdf_source_sha_and_original_year_answer_candidates(self):
    year=read(ROOT/"sudu/data/years/115.json")
    paper=next(p for p in year["papers"] if p["paper"]=="00-E")
    qids={q["id"]:q for q in paper["questions"]}
    for x in self.ev["questionRecords"]:
      with self.subTest(qid=x["questionId"]):
        source=qids[x["questionId"]]
        self.assertEqual(source["sourceVersion"]["questionPdfSha256"],self.ev["officialSource"]["officialOriginalQuestionPdfSha256PreviouslyRecorded"])
        self.assertEqual(source["sourceVersion"]["answerPdfSha256"],self.ev["officialSource"]["officialStandardAnswerPdfSha256PreviouslyRecorded"])
        self.assertEqual(source["officialAnswerCandidate"],x["originalAnswer"])
        self.assertFalse(source["answerVerified"])

  def test_no_q42_falsely_inherited(self):
    s=self.ev["sharedReviewScope"]
    self.assertFalse(s["sharedContainsQuestion42ButQ42QaThisTask"])
    self.assertEqual(s["roleAQuestionIds"],["115-00-E-29","115-00-E-30","115-00-E-39","115-00-E-40","115-00-E-41"])
  def test_official_announcement_and_notice_exact_scope(self):
    a=self.ev["officialSource"]
    data=(ROOT/a["officialAnswerOriginalPage"]).read_bytes()
    self.assertEqual(gitblob(data),a["answerOriginalGitBlob"])
    notice=BASE/"QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
    self.assertEqual(gitblob(notice.read_bytes()),self.ev["officialNotice"]["confirmationLedgerGitBlob"])
    en=next(d for d in read(notice)["docs"] if d["paperCode"]=="00-E")
    self.assertEqual(en["pdfSha256"],self.ev["officialNotice"]["officialEnglishConfirmationPdfSha256PreviouslyRecorded"])
    self.assertEqual([c["questionId"] for c in en["confirmed"]],["115-00-E-34"])
    self.assertEqual(en["confirmed"][0]["officialConfirmedAnswer"],"B")
    self.assertTrue(self.ev["officialNotice"]["pdfNotRedownloadedOrRehashed"])
  def test_old_source_versions_and_canonical_205_bank_unchanged(self):
    source=read(BASE/"webp-manifest.json")
    self.assertEqual(len(source["items"]),205)
    con=sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True)
    try:self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    finally:con.close()
    self.assertFalse(self.ev["downstream"]["canonical205BankEdited"])
    self.assertFalse(self.ev["downstream"]["manifestQaStatusChanged"])
  def test_negative_gates_do_not_allow_unvalidated_source_or_release(self):
    for case in ("missing_q","changed_answer","changed_webp","wrong_shared","q42","wrong_notice","formal_g3","released"):
      with self.subTest(case=case):
        x=copy.deepcopy(self.ev)
        if case=="missing_q":x["questionRecords"].pop()
        elif case=="changed_answer":x["questionRecords"][0]["originalAnswer"]="D"
        elif case=="changed_webp":x["shared"][0]["sha256"]="0"*64
        elif case=="wrong_shared":x["questionRecords"][2]["sharedId"]="115-00-E-SHARED-29-30"
        elif case=="q42":x["downstream"]["q42IndividualG1G2G3State"]="PASS"
        elif case=="wrong_notice":x["officialNotice"]["namedQids"].append("115-00-E-29")
        elif case=="formal_g3":x["officialNotice"]["formalG3AdmissionPerformed"]=True
        else:x["downstream"]["approved"]=True
        with self.assertRaises(ValueError):validate(x)
if __name__=="__main__":unittest.main()
