"""Test exact original source G1 and old G2/G3 evidence for MB24, MB25; no release."""
import copy,hashlib,json,math,subprocess,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
IMG={24:("c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb","cfe5c8eeaf4496d5d98856f96a2c310186ef5893"),25:("92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896","10adb24ab36c35bd86b63c0d3ab4cb83b757393f")}
G2={24:"ede8ce34695bc9e9429aab40079115f94610d669",25:"6228cca369d369c183cb578519c383257f579f8b"}
OLD_QA_GIT="ab82d2f6f2d6743f0ba9e5ca2eabb2d15c4b9d4e"
OLD_STATUS_GIT="6d21432395294d9ccbcfe1dea8be01f88597bbf3"
ORIG_PAGE_GIT="4c98df22dd3096c5d59178f4f2b6b3e88415bbee"
ORIG_PAGE_SHA="3272c1a1df85614af3e65ae56aac3d819c9d25a7e44366d3a514de4fa8cd0555"
ANSWER_PAGE_GIT="5ea4b86e929506d595f96fa162d1aae021f68440"
ANSWER_PAGE_SHA="1b31bb35bf8b49c19d0845d95fe032ae67cfa86b4b7ecb7be657d66f26dc617d"
PREFIX="sudu/data/processed/115/"
EXPECTED=set([
PREFIX+"webp-v2/00-MB/115-00-MB-24.webp",PREFIX+"webp-v2/00-MB/115-00-MB-25.webp",
PREFIX+"review-evidence/115-00-MB-24-image-transcription-correction-20261024.json",
PREFIX+"review-evidence/115-00-MB-25-image-transcription-correction-20261024.json",
PREFIX+"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json",PREFIX+"official-confirmation-status.json",
PREFIX+"source-stage/115-00-MB-24-stage-20261104.json",PREFIX+"source-stage/115-00-MB-25-stage-20261104.json",
"tests/test_role_a_115_mb24_mb25_original_stage_20261104.py",
".github/workflows/role-a-115-mb24-mb25-original-stage-20261104.yml",
"docs/ROLE_A_115_MB24_MB25_SOURCE_STAGE_20261104.md"
])
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def stage(n):return load(BASE/("source-stage/115-00-MB-%02d-stage-20261104.json"%n))
def orig_g2(n):return load(BASE/("review-evidence/115-00-MB-%02d-image-transcription-correction-20261024.json"%n))
def guard(r,n):
    if r["questionId"]!="115-00-MB-%02d"%n:return False
    if r["sourceOriginal"]["originalSingleSha256"]!=IMG[n][0] or r["sourceOriginal"]["originalSingleGitBlob"]!=IMG[n][1]:return False
    if r["G3"]["printedAnswer"]!="C":return False
    if r["G2"]["correctedTextOptions"]!=orig_g2(n)["correctedText"]["options"]:return False
    if len(r["G2"]["correctedTextOptions"])!=4:return False
    if not r["G3"]["sourceApprovalFlagWasNotChanged"]:return False
    if any(r["gates"][i] for i in ("READY","APPROVED","LIVE")):return False
    if n==24:
        m=r["math"]
        if m["C"]!=14 or m["D"]!=15 or m["correctOption"]!="C":return False
        if "110/r" not in r["G2"]["correctedTextQuestion"] or "log₁₀(3)" not in r["G2"]["correctedTextQuestion"]:return False
        if r["G2"]["correctedTextOptions"]!=["D＝C－1","D＝C","D＝C＋1","D＝C＋2"]:return False
    else:
        m=r["math"]
        if m["radius"]!="√2" or m["radiusSquared"]!=2 or m["h"]!=4 or m["a"]!=-14 or m["hPlusA"]!=-10:return False
        if "√2" not in r["G2"]["correctedTextQuestion"] or "以下空白" in " ".join(r["G2"]["correctedTextOptions"]):return False
        if r["G2"]["correctedTextOptions"]!=["－59","－16","－10","10"]:return False
    return True
class ExactSource(unittest.TestCase):
    def test_original_sources_unmodified(self):
        for rel,want_sha,want_git in [
           ("sudu/data/original/115/00-MB/p008-e82e34d9cd-v2-w1400-q66.webp",ORIG_PAGE_SHA,ORIG_PAGE_GIT),
           ("sudu/data/original/115/00-MB-answers/p001-d705f2c3b4-v2-w1400-q66.webp",ANSWER_PAGE_SHA,ANSWER_PAGE_GIT)]:
            raw=(ROOT/rel).read_bytes()
            self.assertEqual(sha(raw),want_sha)
            self.assertEqual(blob(raw),want_git)
        for n in (24,25):
            s=stage(n)
            data=(ROOT/s["sourceOriginal"]["originalSingleWebp"]).read_bytes()
            self.assertEqual(data[:4],b"RIFF")
            self.assertEqual(data[8:12],b"WEBP")
            self.assertEqual(sha(data),IMG[n][0])
            self.assertEqual(blob(data),IMG[n][1])
            self.assertEqual(s["sourceOriginal"]["existingOriginalCrop"],[90,614,1310,1092] if n==24 else [90,1102,1310,1557])
            self.assertTrue(guard(s,n))
            self.assertFalse(s["sourceOriginal"]["hasImageBeenRecropped"])
    def test_old_raw_ocr_and_corrected_g2_exact_original_json_blob(self):
        legacy=load(ROOT/"sudu/data/years/115.json")
        paper=next(p for p in legacy["papers"] if p["paper"]=="00-MB")
        for n in (24,25):
            s=stage(n)
            path=BASE/("review-evidence/115-00-MB-%02d-image-transcription-correction-20261024.json"%n)
            self.assertEqual(blob(path.read_bytes()),G2[n])
            old=next(q for q in paper["questions"] if q["id"]==s["questionId"])
            g=orig_g2(n)
            self.assertEqual(old["question"],g["legacyUncorrectedSource"]["question"])
            self.assertEqual(old["options"],g["legacyUncorrectedSource"]["options"])
            self.assertEqual(s["G2"]["rawOCRQuestion"],old["question"])
            self.assertEqual(s["G2"]["rawOCROptions"],old["options"])
            self.assertEqual(s["G2"]["correctedTextQuestion"],g["correctedText"]["question"])
            self.assertEqual(s["G2"]["correctedTextOptions"],g["correctedText"]["options"])
            self.assertFalse(old["questionVerified"])
            self.assertFalse(old["answerVerified"])
            self.assertTrue(g["noNewOCR"])
            self.assertTrue(g["noNewWebpCropping"])
    def test_prior_exact_official_answer_image_and_notice_only(self):
        qa=BASE/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json"
        notice=BASE/"official-confirmation-status.json"
        self.assertEqual(blob(qa.read_bytes()),OLD_QA_GIT)
        self.assertEqual(blob(notice.read_bytes()),OLD_STATUS_GIT)
        j=load(qa);status=load(notice)
        self.assertEqual(j["itemCount"],25)
        self.assertFalse(j["releaseAllowed"])
        self.assertEqual(status["confirmations"]["00-MB"]["officialStatus"],"no_objection_submitted")
        for n in (24,25):
            row=next(a for a in j["records"] if a["questionId"]=="115-00-MB-%02d"%n)
            self.assertEqual(row["officialFinalAnswerReadDirectlyFromPublishedImage"],"C")
            self.assertEqual(row["correctionStatus"],"NO_OBJECTION_SUBMITTED_4_00_MB")
            self.assertTrue(row["answerVerified"])
            self.assertFalse(row["integrationReady"])
            self.assertEqual(stage(n)["G3"]["existingOfficial25QAGitBlob"],OLD_QA_GIT)
            self.assertFalse(stage(n)["G3"]["pdfDownloadedOrRehashedHere"])
    def test_numeric_math_independent_and_sqrt2_negative(self):
        p=stage(24)
        a=110/8;b=math.log(3)/math.log(1.08)
        self.assertTrue(1.08**14<3<1.08**15)
        self.assertEqual((math.ceil(a),math.ceil(b)),(14,15))
        self.assertAlmostEqual(b,p["math"]["B"],places=12)
        self.assertTrue(guard(p,24))
        s=stage(25)
        self.assertTrue(guard(s,25))
        self.assertEqual(s["math"]["a"],s["math"]["radiusSquared"]-16)
        self.assertEqual(s["math"]["hPlusA"],s["math"]["h"]+s["math"]["a"])
        self.assertIn("以下空白",s["G2"]["rawOCROptions"][-1])
        self.assertNotIn("以下空白",s["G2"]["correctedTextOptions"][-1])
    def test_negative_tampering_always_fail_closed(self):
        for n in (24,25):
            for kind in ("wrong_answer","wrong_sha","missing_option","approve","math"):
                r=copy.deepcopy(stage(n))
                if kind=="wrong_answer":r["G3"]["printedAnswer"]="A"
                elif kind=="wrong_sha":r["sourceOriginal"]["originalSingleSha256"]="0"*64
                elif kind=="missing_option":r["G2"]["correctedTextOptions"].pop()
                elif kind=="approve":r["gates"]["READY"]=True
                elif n==24:r["math"]["D"]=14
                else:r["math"]["radiusSquared"]=4
                with self.subTest(n=n,kind=kind):
                    self.assertFalse(guard(r,n))
    def test_exact_11_file_lease_and_no_main_live(self):
        diff=subprocess.run(["git","diff","--name-only","HEAD^","HEAD"],cwd=ROOT,
                            capture_output=True,text=True,check=True)
        self.assertEqual(set(diff.stdout.splitlines()),EXPECTED)
        published=load(ROOT/"sudu/data/approved/115.json")
        self.assertEqual(published["approvedCount"],5)
        self.assertEqual(set(q["canonicalId"] for q in published["questions"]),
             {"115-00-MB-02","115-00-MB-03","115-00-MB-04","115-00-MB-05","115-00-MB-09"})
        for n in (24,25):
            self.assertEqual(stage(n)["gates"]["canonical205JSON_SQLite_Import"],"PENDING_EXCLUSIVE_LEASE")
if __name__=="__main__":
    unittest.main()
