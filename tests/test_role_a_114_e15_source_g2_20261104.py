"""114 English E15 original single question Q15 source G2 D option cross-page repair; NO RELEASE."""
import copy,hashlib,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
REC=BASE/"source-stage/114-00-E-15-g2-source-20261104.json"
G1=BASE/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
OFF=BASE/"QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json"
NOTICE=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
IMAGE_SHA="16b4efd7b6aea92cd8b2c734e109989f0844a111273100753f030ba2f0032b04"
IMAGE_BLOB="3351b9f4101bff452baf1f0cc7cc600adb254e4f"
PAGE_SHA="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
PAGE_BLOB="5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
ANSWER_SHA="a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
ANSWER_BLOB="5f2920313607af4e756095cd3d6098c8a3ab7440"
G1_BLOB="c1154562fa30cb4b2720a6000a970cf09ef460ff"
OFF_BLOB="0ae35ec3baac7ee4709ea652103db5666fee45a9"
NOTICE_BLOB="6b9a919f224bec8dc3659052a404b4173b6ef366"
EXPECTED={
"sudu/data/processed/114/webp-v1/00-E/114-00-E-15.webp",
"sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json",
"sudu/data/processed/114/QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json",
"sudu/data/processed/114/QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json",
"sudu/data/processed/114/source-stage/114-00-E-15-g2-source-20261104.json",
"tests/test_role_a_114_e15_source_g2_20261104.py",
".github/workflows/role-a-114-e15-original-g2.yml",
"docs/ROLE_A_114_E15_SOURCE_G2_20261104.md"}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def guard(r):
    if r["questionId"]!="114-00-E-15":return False
    if r["original"]["originalSingleWebpSha256"]!=IMAGE_SHA or r["original"]["originalSingleWebpGitBlob"]!=IMAGE_BLOB:return False
    if r["G3"]["originalOfficialPublishedAnswer"]!="A" or r["G3"]["englishNoticeNamedQuestionIds"]!=["114-00-E-26"]:return False
    if r["G3"]["canonicalNewAnswerVerifiedSet"] or r["G3"]["q15InNamedCorrection"]:return False
    if r["G2"]["correctedQuestion"]!=r["raw"]["question"]:return False
    if len(r["G2"]["correctedOptions"])!=4:return False
    if r["G2"]["correctedOptions"][:3]!=r["raw"]["options"][:3]:return False
    if r["G2"]["correctedOptions"][3]!="You should ask questions about the job.":return False
    if "第4 頁" not in r["raw"]["rawDOption"] or "第4 頁" in r["G2"]["correctedOptions"][3]:return False
    if any(r["downstream"][k] for k in ("READY","APPROVED","LIVE","mainAndPagesModified")):return False
    return True
class ExactQ15(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=read(REC)
    def test_original_pixels_and_source_provenance(self):
        r=self.r
        for path,s,g in [
        (r["original"]["originalSingleWebp"],IMAGE_SHA,IMAGE_BLOB),
        (r["original"]["sourcePageWebp"],PAGE_SHA,PAGE_BLOB),
        (r["G3"]["officialAnswerTableImage"],ANSWER_SHA,ANSWER_BLOB)]:
            raw=(ROOT/path).read_bytes()
            self.assertEqual(raw[:4],b"RIFF")
            self.assertEqual(raw[8:12],b"WEBP")
            self.assertEqual(sha(raw),s)
            self.assertEqual(blob(raw),g)
        self.assertEqual(r["original"]["originalPixelCrop"],[90,1367,1310,1653])
        self.assertTrue(r["original"]["noRecropOrOCRRegenerate"])
    def test_original_G1_is_prior_assistant_visual_not_E(self):
        self.assertEqual(blob(G1.read_bytes()),G1_BLOB)
        x=next(i for i in read(G1)["items"] if i["questionId"]=="114-00-E-15")
        self.assertEqual(x["result"],"PASS")
        self.assertEqual(x["reviewedWebpSha256"],IMAGE_SHA)
        self.assertEqual(x["sourcePageSha256"],PAGE_SHA)
        self.assertFalse(x["answerVerified"])
        self.assertFalse(x["questionVerified"])
        self.assertFalse(x["integrationReady"])
        self.assertFalse(x["independentHumanReview"])
    def test_actual_legacy_OCR_D_tail_only_removed(self):
        raw=read(ROOT/"sudu/data/years/114.json")
        q=next(x for p in raw["papers"] if p["paper"]=="00-E" for x in p["questions"] if x["id"]=="114-00-E-15")
        self.assertEqual(q["question"],self.r["raw"]["question"])
        self.assertEqual(q["options"],self.r["raw"]["options"])
        self.assertFalse(q["answerVerified"])
        self.assertFalse(q["questionVerified"])
        self.assertEqual(self.r["G2"]["correctedOptions"][:3],q["options"][:3])
        self.assertEqual(self.r["G2"]["correctedOptions"][3],"You should ask questions about the job.")
        self.assertNotIn("第4 頁",self.r["G2"]["correctedOptions"][3])
        self.assertIn("第4 頁",q["options"][3])
        self.assertIn("-"+q["options"][3],self.r["G2"]["optionDBeforeAfterDiff"])
        self.assertIn("+"+self.r["G2"]["correctedOptions"][3],self.r["G2"]["optionDBeforeAfterDiff"])
        self.assertTrue(guard(self.r))
    def test_correct_original_announcement_A_and_scoped_notice_E26_only(self):
        self.assertEqual(blob(OFF.read_bytes()),OFF_BLOB)
        self.assertEqual(blob(NOTICE.read_bytes()),NOTICE_BLOB)
        q=next(i for i in read(OFF)["items"] if i["questionId"]=="114-00-E-15")
        self.assertEqual(q["officialVisualAnswerCandidate"],"A")
        self.assertFalse(q["officialCorrectionsChecked"])
        self.assertFalse(q["answerVerified"])
        english=next(x for x in read(NOTICE)["docs"] if x["paperCode"]=="00-E")
        self.assertEqual(english["pdfSha256"],"79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc")
        self.assertEqual(len(english["confirmed"]),1)
        self.assertEqual(english["confirmed"][0]["questionId"],"114-00-E-26")
        self.assertNotIn("114-00-E-15",[x["questionId"] for x in english["confirmed"]])
        self.assertFalse(self.r["G3"]["canonicalNewAnswerVerifiedSet"])
    def test_negative_mutations_fail_closed(self):
        for n in ["wrong_answer","bad_sha","lost_option","no_footer_provenance","false_notice","promote","not_clean"]:
            r=copy.deepcopy(self.r)
            if n=="wrong_answer":r["G3"]["originalOfficialPublishedAnswer"]="B"
            elif n=="bad_sha":r["original"]["originalSingleWebpSha256"]="0"*64
            elif n=="lost_option":r["G2"]["correctedOptions"].pop()
            elif n=="no_footer_provenance":r["raw"]["rawDOption"]="You should ask questions about the job."
            elif n=="false_notice":r["G3"]["englishNoticeNamedQuestionIds"].append("114-00-E-15")
            elif n=="promote":r["downstream"]["READY"]=True
            else:r["G2"]["correctedOptions"][3]+=" 第4 頁"
            with self.subTest(case=n):
                self.assertFalse(guard(r))
    def test_no_shared_canonical_and_exact_8_scoped_new_paths(self):
        approved=read(ROOT/"sudu/data/approved/114.json")
        self.assertEqual(approved["approvedCount"],0)
        self.assertFalse(self.r["downstream"]["mainAndPagesModified"])
        self.assertEqual(self.r["downstream"]["masterCanonicalTextRevisionAndSqliteRow"],
          "PENDING_EXCLUSIVE_SHARED_FILE_LEASE_114_C27")
        out=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,
                           capture_output=True,text=True,check=True)
        self.assertEqual(set(out.stdout.splitlines()),EXPECTED)
if __name__=="__main__":
    unittest.main()
