"""Role A exact original 114 English E10/E20 source cross-page D clean; no source admission/READY."""
import copy,hashlib,json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
QA=BASE/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json"
ANSWER=BASE/"QA_114_EN_Q06_Q20_OFFICIAL_ANSWER_IMAGE_VISUAL_20261023.json"
NOTICE=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
DIGEST={10:"b0a89c379254466524ff72308a751fe63ade9e85d037f8a46dc03a6727287275",20:"f8699901c5b3de551c8cd870419c9ede5982402b76a9db3c9d52ea7c183c416b"}
IMG_GIT={10:"1117e9450b91f53905b03a007f378a5c6b67f1c4",20:"8c921cabbfe5327704367a183f7b01bc0f8bbd65"}
PAGE_SHA={10:"fd05e4a3f87f69bbd0d0f2a963400342da9752ec8bbef0ef3b26b59e621ae002",20:"d734a051d0c02e76ec26f44537520fd252ccd20dd17ad20daf9aa62f1ba6e3f5"}
PAGE_GIT={10:"82a46f35df5f2a956a1499e3582a91c79dec1ce8",20:"24b3c270e4b357005c4cdc2aeb884fb88328d94a"}
EXPECTED_ANS={10:"C",20:"B"}
EXPECTED_D={10:"run into",20:"So who did he really invite to his home?"}
EXPECTED_G1="c1154562fa30cb4b2720a6000a970cf09ef460ff"
EXPECTED_ANSWER="0ae35ec3baac7ee4709ea652103db5666fee45a9"
EXPECTED_NOTICE="6b9a919f224bec8dc3659052a404b4173b6ef366"
EXPECTED_DIFF={
"sudu/data/processed/114/webp-v1/00-E/114-00-E-10.webp",
"sudu/data/processed/114/webp-v1/00-E/114-00-E-20.webp",
"sudu/data/processed/114/source-stage/114-00-E-10-g2-source-20261104.json",
"sudu/data/processed/114/source-stage/114-00-E-20-g2-source-20261104.json",
"tests/test_role_a_114_e10_e20_source_g2_20261104.py",
".github/workflows/role-a-114-e10-e20-source-g2.yml",
"docs/ROLE_A_114_E10_E20_SOURCE_G2_20261104.md"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def stage(n):return load(BASE/("source-stage/114-00-E-%02d-g2-source-20261104.json"%n))
def guard(r,n):
    if r["questionId"]!="114-00-E-%02d"%n:return False
    if r["original"]["originalSingleSha256"]!=DIGEST[n] or r["original"]["originalSingleGitBlob"]!=IMG_GIT[n]:return False
    if r["official"]["publishedOriginalPrintedAnswer"]!=EXPECTED_ANS[n]:return False
    if r["official"]["englishCorrectionNamedQuestionIds"]!=["114-00-E-26"]:return False
    if r["official"]["formalNewG3FlagSet"] or r["official"]["thisQuestionIsNamedCorrection"]:return False
    x=r["sourceCorrection"]["correctedOptions"]
    if len(x)!=4 or x[:3]!=r["raw"]["options"][:3]:return False
    if x[3]!=EXPECTED_D[n] or r["sourceCorrection"]["correctedQuestion"]!=r["raw"]["question"]:return False
    if "第" not in r["raw"]["oldD"] or "頁" not in r["raw"]["oldD"]:return False
    if "第" in x[3] and "頁" in x[3]:return False
    if any(r["downstream"][k] for k in ("ready","approved","live")):return False
    return True

class Source114E10E20(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g1=load(QA)
        cls.official=load(ANSWER)
        cls.notice=load(NOTICE)
        cls.legacy=load(ROOT/"sudu/data/years/114.json")
    def test_real_immutable_original_webp_bytes_and_source_page(self):
        for n in (10,20):
            r=stage(n);orig=r["original"]
            self.assertTrue(guard(r,n))
            for path,expected,git in [
                (orig["originalSingleQuestionWebp"],DIGEST[n],IMG_GIT[n]),
                (orig["archivedOfficialPageWebp"],PAGE_SHA[n],PAGE_GIT[n]),
            ]:
                raw=(ROOT/path).read_bytes()
                self.assertEqual(raw[:4],b"RIFF")
                self.assertEqual(raw[8:12],b"WEBP")
                self.assertEqual(sha(raw),expected)
                self.assertEqual(blob(raw),git)
            self.assertEqual(orig["originalCrop"],[90,1401,1310,1491] if n==10 else [90,1415,1310,1704])
            self.assertTrue(orig["originalPixelsPreserved"])
        img=(ROOT/"sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp").read_bytes()
        self.assertEqual(blob(img),"5f2920313607af4e756095cd3d6098c8a3ab7440")
        self.assertEqual(sha(img),"a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863")
    def test_historic_g1_source_image_qa_and_answer_image_qa_not_promoted(self):
        self.assertEqual(blob(QA.read_bytes()),EXPECTED_G1)
        self.assertEqual(blob(ANSWER.read_bytes()),EXPECTED_ANSWER)
        for n in (10,20):
            qid="114-00-E-%02d"%n
            g=next(x for x in self.g1["items"] if x["questionId"]==qid)
            a=next(x for x in self.official["items"] if x["questionId"]==qid)
            self.assertEqual(g["reviewedWebpSha256"],DIGEST[n])
            self.assertEqual(g["result"],"PASS")
            self.assertFalse(g["questionVerified"])
            self.assertFalse(g["answerVerified"])
            self.assertEqual(a["officialVisualAnswerCandidate"],EXPECTED_ANS[n])
            self.assertFalse(a["officialCorrectionsChecked"])
            self.assertFalse(a["answerVerified"])
            self.assertFalse(a["integrationReady"])
    def test_complete_old_raw_d_preserved_and_clean_d_only(self):
        paper=next(p for p in self.legacy["papers"] if p["paper"]=="00-E")
        for n in (10,20):
            r=stage(n);row=next(x for x in paper["questions"] if x["id"]==r["questionId"])
            self.assertEqual(r["raw"]["question"],row["question"])
            self.assertEqual(r["raw"]["options"],row["options"])
            self.assertEqual(r["raw"]["oldD"],row["options"][3])
            self.assertFalse(row["questionVerified"])
            self.assertFalse(row["answerVerified"])
            self.assertEqual(r["sourceCorrection"]["correctedOptions"][:3],row["options"][:3])
            self.assertEqual(r["sourceCorrection"]["correctedOptions"][3],EXPECTED_D[n])
            self.assertIn("-"+row["options"][3],r["sourceCorrection"]["rawDToCleanDUnifiedDiff"])
            self.assertIn("+"+EXPECTED_D[n],r["sourceCorrection"]["rawDToCleanDUnifiedDiff"])
            if n==10:
                self.assertIn("Ⅱ. 對話題",row["options"][3])
            else:
                self.assertIn("WorldSkills",row["options"][3])
            self.assertTrue(guard(r,n))
    def test_114_official_english_correction_scope_only_E26_not_e10_e20(self):
        self.assertEqual(blob(NOTICE.read_bytes()),EXPECTED_NOTICE)
        english=next(x for x in self.notice["docs"] if x["paperCode"]=="00-E")
        self.assertEqual(english["pdfSha256"],"79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc")
        self.assertEqual([x["questionId"] for x in english["confirmed"]],["114-00-E-26"])
        for n in (10,20):
            r=stage(n)
            self.assertTrue(r["official"]["originalAnswerNotChanged"])
            self.assertFalse(r["official"]["pdfDownloadedOrRehashedThisTask"])
            self.assertEqual(r["official"]["publishedOriginalPrintedAnswer"],EXPECTED_ANS[n])
            self.assertFalse(r["official"]["formalNewG3FlagSet"])
    def test_mutation_negatives_all_fail(self):
        for n in (10,20):
            for kind in ["bad_sha","wrong_answer","bad_d","fake_notice","wrong_qid","ready","lost_b"]:
                r=copy.deepcopy(stage(n))
                if kind=="bad_sha":r["original"]["originalSingleSha256"]="0"*64
                elif kind=="wrong_answer":r["official"]["publishedOriginalPrintedAnswer"]="A"
                elif kind=="bad_d":r["sourceCorrection"]["correctedOptions"][3]+=" WorldSkills"
                elif kind=="fake_notice":r["official"]["englishCorrectionNamedQuestionIds"].append(r["questionId"])
                elif kind=="wrong_qid":r["questionId"]="114-00-E-99"
                elif kind=="ready":r["downstream"]["ready"]=True
                else:r["sourceCorrection"]["correctedOptions"].pop()
                with self.subTest(n=n,case=kind):
                    self.assertFalse(guard(r,n))
    def test_exact_seven_leased_files_and_formal_ready_not_granted(self):
        approved=load(ROOT/"sudu/data/approved/114.json")
        self.assertEqual(approved["approvedCount"],0)
        for n in (10,20):
            self.assertEqual(stage(n)["downstream"]["masterCanonical205JsonSqlitePending"],"PENDING_114_C27_SHARED_LEASE")
            self.assertTrue(stage(n)["downstream"]["BNeedsNewCanonicalSourceRevisionAndDigest"])
        d=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,
                         capture_output=True,text=True,check=True)
        self.assertEqual(set(d.stdout.splitlines()),EXPECTED_DIFF)
if __name__=="__main__":
    unittest.main()
