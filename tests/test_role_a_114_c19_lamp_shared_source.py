"""ROLE A Q19 missing official lamp shared association source-only receipt (NO RELEASE)."""
import copy,hashlib,json,sqlite3,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
EVID=BASE/"review-evidence/114-00-C-19-lamp-shared-link-20261103.json"
QSHA="4c549405cfef2061a42abdac873c6146bb61e52a5cccae2f232d1a5ca35baff1"
QBLOB="3e72b0581ad4908bc24487d115f670c8af793939"
SHAS="b27e23f0c33fdfc4843dac6b6b5aff8fae5a40254c986b8705d73813c147e403"
SBLOB="000a72926ff25cfbd4016cce5378ecd194534deb"
SHARE_REV="0d7aa9c1ccf627e326aa2edac0e6c61b4436d49e9313246275365f2d41be27eb"
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def validate(r):
  s=r["sourceImage"];m=r["sharedMaterial"];a=r["officialAnswer"]
  if r["questionId"]!="114-00-C-19":raise ValueError("incorrect source QID")
  if s["sha256"]!=QSHA or s["gitBlob"]!=QBLOB:raise ValueError("wrong Q19 original")
  if s["rejectedOldWebpSha256"] == s["sha256"]:raise ValueError("reverted to polluted v1")
  if m["id"]!="114-00-C-SHARED-16-19" or m["sourceRevision"]!=SHARE_REV:raise ValueError("wrong shared reading")
  if m["explicitlyForbiddenDifferentSharedId"]!="114-00-C-SHARED-20-23":raise ValueError("lost C20–23 negative gate")
  if m["sha256"]!=SHAS or m["gitBlob"]!=SBLOB or not m["question19UsesThisShared"]:raise ValueError("physical shared missing")
  if a["printedAnswer"]!="B" or a["noticeForQ19"] or a["formalG3SourceAdmitted"]:raise ValueError("official answer discrepancy")
  if a["noticeNamesOnly"]!=["114-00-C-14","114-00-C-24","114-00-C-28","114-00-C-30"]:raise ValueError("notice scope")
  seed="ROLE_A_114_C19_LAMP_LINK_G1_V1\n"+QSHA+"\n"+SHAS+"\n"+SHARE_REV
  if r["sourceLinkRevisionSeed"]!=seed or r["sourceLinkRevisionSha256"]!=sha(seed.encode("utf-8")):raise ValueError("revision")
  if any(r["downstream"][k] for k in ("canonical114JsonEdited","canonical114SqliteEdited","manifestEdited","q20To23MaterialEdited","roleBPr105LessonEdited","roleEIndependentContentApproval","roleDReal8x2","formalG3Approved","ready","approved","live")):
    raise ValueError("unlicensed approval")
  return True
class RoleA114C19(unittest.TestCase):
  @classmethod
  def setUpClass(cls):cls.rec=read(EVID)
  def test_exact_original_q19_true_g1_source(self):
    r=self.rec;s=r["sourceImage"]
    self.assertTrue(validate(r))
    raw=(ROOT/s["originalSingleWebp"]).read_bytes()
    self.assertEqual(raw[:4],b"RIFF");self.assertEqual(raw[8:12],b"WEBP")
    self.assertEqual(sha(raw),QSHA);self.assertEqual(blob(raw),QBLOB)
    page=(ROOT/s["originalOfficialPageWebp"]).read_bytes()
    self.assertEqual(blob(page),s["originalOfficialPageGitBlob"])
    self.assertEqual(sha(page),s["originalOfficialPageSha256"])
    with Image.open(ROOT/s["originalSingleWebp"]) as img:self.assertEqual(img.size,(1220,279))
    self.assertEqual(s["crop"],[90,284,1310,563])
    self.assertFalse(s["newImageCreated"])
  def test_historical_source_visual_and_raw_ocr_are_unchanged(self):
    r=self.rec;s=r["sourceImage"]
    g1=ROOT/s["oldG1CertificatePath"]
    g2=ROOT/s["oldG2RawQaPath"]
    self.assertEqual(blob(g1.read_bytes()),s["oldG1CertificateGitBlob"])
    self.assertEqual(blob(g2.read_bytes()),s["oldG2RawQaGitBlob"])
    a=read(g1)
    row=next(x for x in a["items"] if x["questionId"]=="114-00-C-19")
    self.assertEqual(row["reviewedWebpSha256"],QSHA)
    self.assertEqual(r["sourceG2FullText"],"NOT_NEWLY_VERIFIED_IN_THIS_TASK")
  def test_full_lamp_shared_true_pixels_not_c20_to23_article(self):
    r=self.rec;m=r["sharedMaterial"]
    raw=(ROOT/m["path"]).read_bytes()
    self.assertEqual(sha(raw),SHAS);self.assertEqual(blob(raw),SBLOB)
    prior=read(BASE/"review-evidence/114-00-C-16-18-original-lamps-20261103.json")
    self.assertEqual(prior["sharedMaterial"]["sha256"],SHAS)
    self.assertEqual(prior["sharedMaterial"]["sourceRevisionSha256"],SHARE_REV)
    self.assertEqual(prior["sharedMaterial"]["visualReviewStatus"],"PASS_AI_ASSISTANT_DIRECT_VISUAL_ORIGINAL")
    self.assertEqual(m["sourceOriginalPage"],6)
    self.assertEqual(m["sourcePixelsCrop"],[90,155,1310,1360])
  def test_abstract_answer_scope_and_sqlite_integrity(self):
    a=self.rec["officialAnswer"]
    self.assertEqual(blob((ROOT/a["answerPage"]).read_bytes()),a["answerPageGitBlob"])
    notice=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
    self.assertEqual(blob(notice.read_bytes()),a["confirmationLedgerGitBlob"])
    doc=next(x for x in read(notice)["docs"] if x["paperCode"]=="00-C")
    self.assertEqual([x["questionId"] for x in doc["confirmed"]],a["noticeNamesOnly"])
    con=sqlite3.connect("file:"+str(BASE/"question-bank.sqlite3")+"?mode=ro",uri=True)
    try:self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    finally:con.close()
    self.assertFalse(self.rec["downstream"]["canonical114SqliteEdited"])
  def test_original_manifest_pass_with_v2_and_no_old_v1_reversion(self):
    m=read(BASE/"webp-manifest.json")
    item=next(x for x in m["items"] if x["questionId"]=="114-00-C-19")
    self.assertEqual(item["qaStatus"],"PASS")
    self.assertEqual(item["sha256"],QSHA)
    self.assertEqual(item["output"],self.rec["sourceImage"]["originalSingleWebp"])
    self.assertEqual(item["oldAssetBeforeDirectVisualRepair"]["qaStatus"],"BLOCKED_VISUAL_NEIGHBOR_SHARED_PASSAGE")
  def test_negative_mismatches_remain_blocked(self):
    for mode in ("wrong_q","old_image","wrong_shared","wrong_lamp_sha","changed_notice","wrong_answer","approve","q20_edited"):
      with self.subTest(mode=mode):
        x=copy.deepcopy(self.rec)
        if mode=="wrong_q":x["questionId"]="114-00-C-20"
        elif mode=="old_image":x["sourceImage"]["sha256"]=x["sourceImage"]["rejectedOldWebpSha256"]
        elif mode=="wrong_shared":x["sharedMaterial"]["id"]="114-00-C-SHARED-20-23"
        elif mode=="wrong_lamp_sha":x["sharedMaterial"]["sha256"]="0"*64
        elif mode=="changed_notice":x["officialAnswer"]["noticeNamesOnly"].append("114-00-C-19")
        elif mode=="wrong_answer":x["officialAnswer"]["printedAnswer"]="D"
        elif mode=="approve":x["downstream"]["approved"]=True
        else:x["downstream"]["q20To23MaterialEdited"]=True
        with self.assertRaises(ValueError):validate(x)
if __name__=="__main__":unittest.main()
