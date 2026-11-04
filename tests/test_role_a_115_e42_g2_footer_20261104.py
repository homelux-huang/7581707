"""ROLE A Q42 original-pixel G2 correction without new student approval."""
import copy,hashlib,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
RECEIPT=BASE/"review-evidence/115-00-E-42-G2-D-FOOTER-CORRECTION-20261104.json"
QID="115-00-E-42"
IND="sudu/data/processed/115/webp-v2/00-E/115-00-E-42.webp"
SHARED="sudu/data/processed/115/webp-v3/shared/115-00-E-SHARED-39-42.webp"
ANSWER="sudu/data/original/115/00-E-answers/p001-185b1c8503-v2-w1400-q66.webp"
G1="sudu/data/processed/115/review-evidence/115-00-E-42-original-shared-G1-20261103.json"
NOTICE="sudu/data/processed/115/QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json"
IMG_BLOB="ee72360d9aad58fade391fa260269b0222efcc0c"
IMG_SHA="a7af2b810230975781ad2831b47ac2c977e70d0e4c4d42d263f7af5f1689e7d0"
SHARED_BLOB="4aaac02b7ed9390b8ff7c8a4c4272e74996bd595"
SHARED_SHA="5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b"
G1_BLOB="da429905c376db05432d09ae556f478f32a2dc6e"
ANSWER_BLOB="b8da0d2f8024eb8da2bdb2b096f97d59c0a6609d"
NOTICE_BLOB="1a21701647627bc1dcaa39a835bf90a4459c9424"
SHARED_REV="c94b849dc5750a92106c4b5892007010a8ce8b0b41f3cdc9e20d6e590e9353b2"
EXPECTED={
"sudu/data/processed/115/review-evidence/115-00-E-42-G2-D-FOOTER-CORRECTION-20261104.json",
"tests/test_role_a_115_e42_g2_footer_20261104.py",
".github/workflows/role-a-115-e42-g2-footer-20261104.yml",
"docs/ROLE_A_115_E42_G2_FOOTER_20261104.md"}
def sha(data):return hashlib.sha256(data if isinstance(data,bytes) else data.encode("utf-8")).hexdigest()
def blob(data):return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def get(s):return json.loads((ROOT/s).read_text(encoding="utf-8"))
def canon(q,options):return "\n".join([q]+["(%s) %s"%(chr(65+i),op) for i,op in enumerate(options)])
def accepted(r):
    if r["questionId"]!=QID:return False
    if r["source"]["originalSingleSha256"]!=IMG_SHA or r["source"]["originalSharedSha256"]!=SHARED_SHA:return False
    if r["g2"]["correctedQuestion"]!=r["legacy"]["oldQuestion"]:return False
    if len(r["g2"]["correctedOptions"])!=4:return False
    if r["g2"]["correctedOptions"][:3]!=r["legacy"]["oldOptions"][:3]:return False
    if r["g2"]["correctedOptions"][3]!="Contract manufacturers in the early days designed new products for customers.":return False
    if "二、 非選擇題" not in r["legacy"]["oldOptions"][3]:return False
    if "二、 非選擇題" in r["g2"]["correctedOptions"][3]:return False
    if r["g2"]["correctedCanonicalQuestionAndOptionsText"]!=canon(r["g2"]["correctedQuestion"],r["g2"]["correctedOptions"]):return False
    if sha(r["g2"]["correctedCanonicalQuestionAndOptionsText"])!=r["g2"]["correctedCanonicalTextSha256"]:return False
    seed="ROLE_A_115_E42_D_ONLY_G2_V1\n"+r["g2"]["correctedCanonicalTextSha256"]+"\n"+IMG_SHA+"\n"+SHARED_SHA+"\n"+SHARED_REV
    if r["g2"]["sourceRevisionSeed"]!=seed or sha(seed)!=r["g2"]["sourceRevisionSha256"]:return False
    if r["officialAnswer"]["originalAnnouncedAnswer"]!="C" or r["officialAnswer"]["officialNoticeNamedQuestionIds"]!=["115-00-E-34"]:return False
    if r["officialAnswer"]["formalCanonicalAnswerVerifiedChanged"] or r["officialAnswer"]["q42IsNamedCorrection"]:return False
    if any(r["downstream"][f] for f in ("READY","APPROVED","LIVE","canonical205JSONModified","sqlite205Modified","roleCAuthorPR147FileModified")):return False
    return True
class SourceReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=get(RECEIPT.relative_to(ROOT).as_posix())
    def test_exact_original_source_image_sha_and_git_identity(self):
        for path,wsha,wblob in [
          (IND,IMG_SHA,IMG_BLOB),(SHARED,SHARED_SHA,SHARED_BLOB)]:
            raw=(ROOT/path).read_bytes()
            self.assertEqual(raw[:4],b"RIFF")
            self.assertEqual(raw[8:12],b"WEBP")
            self.assertEqual(sha(raw),wsha)
            self.assertEqual(blob(raw),wblob)
        src=self.r["source"]
        self.assertEqual(src["originalSingleOriginalPixelCrop"],[90,1436,1310,1623])
        self.assertTrue(src["noImagesRecroppedOrReOcr"])
        self.assertEqual(src["oldSharedSourceG1Revision"],SHARED_REV)
    def test_existing_A_G1_source_exact_blob(self):
        self.assertEqual(blob((ROOT/G1).read_bytes()),G1_BLOB)
        old=get(G1)
        self.assertEqual(old["questionId"],QID)
        self.assertEqual(old["singleQuestion"]["sha256"],IMG_SHA)
        self.assertEqual(old["sharedMaterial"]["sha256"],SHARED_SHA)
        self.assertEqual(old["officialAnswer"]["publishedAnswer"],"C")
        self.assertFalse(old["downstream"]["masterReady"])
    def test_original_raw_ocr_preserved_and_only_D_option_changed(self):
        year=get("sudu/data/years/115.json")
        old=next(q for p in year["papers"] if p["paper"]=="00-E"
                 for q in p["questions"] if q["id"]==QID)
        r=self.r
        self.assertEqual(r["legacy"]["oldQuestion"],old["question"])
        self.assertEqual(r["legacy"]["oldOptions"],old["options"])
        self.assertEqual(r["legacy"]["oldAnswerNumeric"],2)
        self.assertFalse(old["questionVerified"])
        self.assertFalse(old["answerVerified"])
        self.assertEqual(sha(canon(old["question"],old["options"])),r["legacy"]["oldRawQuestionAndOptionsTextSha256"])
        self.assertEqual(r["g2"]["correctedOptions"][:3],old["options"][:3])
        self.assertEqual(r["g2"]["correctedOptions"][3],"Contract manufacturers in the early days designed new products for customers.")
        self.assertIn("二、 非選擇題",old["options"][3])
        self.assertNotIn("二、 非選擇題",r["g2"]["correctedOptions"][3])
        self.assertTrue(accepted(r))
    def test_original_published_C_and_english_confirmation_only_E34(self):
        self.assertEqual(blob((ROOT/ANSWER).read_bytes()),ANSWER_BLOB)
        self.assertEqual(blob((ROOT/NOTICE).read_bytes()),NOTICE_BLOB)
        row=next(x for x in get(NOTICE)["docs"] if x["paperCode"]=="00-E")
        self.assertEqual(row["confirmed"][0]["questionId"],"115-00-E-34")
        self.assertEqual(len(row["confirmed"]),1)
        self.assertEqual(row["pdfSha256"],"bd6405814955e2c997ad5c7e69e34a10a5fcc22462b4227eabba0067760aa1a6")
        self.assertFalse(self.r["officialAnswer"]["q42IsNamedCorrection"])
        self.assertFalse(self.r["officialAnswer"]["formalCanonicalAnswerVerifiedChanged"])
        self.assertFalse(self.r["officialAnswer"]["noOfficialPdfDownloadedOrRehashedThisTask"] is False)
    def test_negative_mutation_all_fail_closed(self):
        for mode in ("sha","option","footer","notice","release","correctletter","revision","reading"):
            r=copy.deepcopy(self.r)
            if mode=="sha":r["source"]["originalSingleSha256"]="0"*64
            elif mode=="option":r["g2"]["correctedOptions"].pop()
            elif mode=="footer":r["g2"]["correctedOptions"][3]+="\n二、 非選擇題"
            elif mode=="notice":r["officialAnswer"]["officialNoticeNamedQuestionIds"].append(QID)
            elif mode=="release":r["downstream"]["READY"]=True
            elif mode=="correctletter":r["officialAnswer"]["originalAnnouncedAnswer"]="B"
            elif mode=="revision":r["g2"]["sourceRevisionSha256"]="0"*64
            else:r["source"]["originalSharedSha256"]="0"*64
            with self.subTest(mode=mode): self.assertFalse(accepted(r))
    def test_exact_four_new_paths_no_approval(self):
        diff=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True)
        self.assertEqual(set(diff.stdout.splitlines()),EXPECTED)
        self.assertEqual(get("sudu/data/approved/115.json")["approvedCount"],5)
        self.assertFalse(self.r["downstream"]["sqlite205Modified"])
        self.assertFalse(self.r["downstream"]["canonical205JSONModified"])
        self.assertEqual(self.r["downstream"]["fullShared39To42SourceG2"],"PENDING_SEPARATE_TEXT_QA_FOR_Q38_LINK")
if __name__=="__main__":
    unittest.main()
