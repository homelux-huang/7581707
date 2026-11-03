"""114 Chinese C16–18 original TCTE three lamps images + shared actual-pixel source (NO RELEASE)."""
import copy, hashlib, json, sqlite3, unittest
from pathlib import Path
from PIL import Image, ImageChops
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sudu/data/processed/114"
EV = BASE / "review-evidence/114-00-C-16-18-original-lamps-20261103.json"
G1_SHAS = {
16:"d04b2f4b9bd7bb2a1212fdb12da4ee7d9b0cee14afd3e17d4bd1733061952d4a",
17:"9fd277ec092fe55fb9bc12080b6bce9749ffe9f6b7cb468e33439ae5b23c985e",
18:"50c3718fc832c152e735ad773272fd4466888d57cc18b6b319c85218773c53ed",
}
GIT_BLOBS = {
16:"07698a20aa5b8fafbb8fa234989f7a8c5add388c",
17:"7fe2f81756e4b6a631a3f5a0327f95b58bffbe23",
18:"fbca5e2317f8e99f4f817ea528122d8af8c7a61a",
}
PRINTED = {16:"B",17:"D",18:"A"}
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def read(p): return json.loads(p.read_text(encoding="utf-8"))
def valid(r):
    records=r["questionImageRecords"]; shared=r["sharedMaterial"]; notice=r["officialNotice"]
    if [x["number"] for x in records]!=[16,17,18]: raise ValueError("invalid scope")
    if [x["officialAnswer"] for x in records]!=["B","D","A"]: raise ValueError("wrong printed answers")
    if [x["sha256"] for x in records] != [G1_SHAS[i] for i in (16,17,18)]: raise ValueError("image SHA altered")
    if shared["id"] != "114-00-C-SHARED-16-19" or shared["claimedQuestionIds"]!=[16,17,18]: raise ValueError("shared scope")
    if shared["cropPixels"] != [90,155,1310,1360] or shared["cropWidthHeight"]!=[1220,1205]:raise ValueError("crop geometry")
    if shared["q19SourceQaInThisTask"]!="NOT_REVIEWED_OR_PROMOTED":raise ValueError("Q19 inherited QA")
    if notice["namedChineseCorrections"]!=["114-00-C-14","114-00-C-24","114-00-C-28","114-00-C-30"]: raise ValueError("wrong notice")
    if notice["claimedQuestionsListedInNotice"] or notice["formalG3QuestionAnswersPromoted"]: raise ValueError("fake formal G3")
    if any(r["downstream"][k] for k in ("canonicalBankEdited","canonicalSqliteEdited","manifestEdited","rawOcrEdited","otherQ19Edited","EContentReview","DV4EightByTwo","ready","approved","live")):
        raise ValueError("unsafe release")
    return True
class RoleA114LampsSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.ev = read(EV)
    def test_three_original_single_images_unchanged(self):
        r=self.ev
        self.assertTrue(valid(r))
        manifest=read(BASE/"webp-manifest.json")
        for item in r["questionImageRecords"]:
            n=item["number"]
            with self.subTest(q=n):
                content=(ROOT/item["image"]).read_bytes()
                self.assertEqual(content[:4],b"RIFF")
                self.assertEqual(content[8:12],b"WEBP")
                self.assertEqual(sha(content),G1_SHAS[n])
                self.assertEqual(blob(content),GIT_BLOBS[n])
                m=next(x for x in manifest["items"] if x["questionId"]==item["qid"])
                self.assertEqual(m["sha256"],G1_SHAS[n])
                self.assertEqual(m["qaStatus"],"DRAFT_NEEDS_DIRECT_VISUAL_QA")
                self.assertEqual(item["g1Review"],"AI_ASSISTANT_DIRECT_VISUAL_SOURCE_IMAGE_CANDIDATE")
                self.assertFalse(item["formalG3"])
    def test_official_pages_and_answer_original_git_sha(self):
        r=self.ev
        for p in r["officialQuestionImages"]:
            raw=(ROOT/p["path"]).read_bytes()
            self.assertEqual(blob(raw),p["blob"])
            self.assertEqual(sha(raw),p["sha256"])
        answer=r["originalAnswerPage"]
        raw=(ROOT/answer["path"]).read_bytes()
        self.assertEqual(blob(raw),answer["blob"])
        self.assertEqual(answer["directReadAnswerForClaimedQuestions"],{"114-00-C-16":"B","114-00-C-17":"D","114-00-C-18":"A"})
        self.assertEqual(r["sourceOfficialPaperPDFSha256Recorded"],"f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74")
        self.assertFalse(r["pdfDownloadedOrRehashedThisTask"])
    def test_shared_lossless_cropped_from_true_original_page6_and_never_q16(self):
        shared=self.ev["sharedMaterial"]
        crop=tuple(shared["cropPixels"]); self.assertLessEqual(crop[3],1360)
        with Image.open(ROOT/shared["sourcePage"]) as im:
            original=im.convert("RGB").crop(crop)
        with Image.open(ROOT/shared["isolatedSharedWebp"]) as im:
            actual=im.convert("RGB")
        self.assertEqual(original.size,tuple(shared["cropWidthHeight"]))
        self.assertIsNone(ImageChops.difference(actual,original).getbbox())
        raw=(ROOT/shared["isolatedSharedWebp"]).read_bytes()
        self.assertEqual(sha(raw),shared["sha256"])
        self.assertEqual(blob(raw),shared["gitBlob"])
        seed="ROLE_A_114_LAMPS_SHARED_G1_V1\n"+shared["sha256"]+"\n"+"\n".join(r["sha256"] for r in self.ev["questionImageRecords"])
        self.assertEqual(shared["sourceRevisionSeed"],seed)
        self.assertEqual(shared["sourceRevisionSha256"],sha(seed.encode("utf-8")))
        self.assertFalse(shared["containsQ16Question"])
    def test_source_confirmation_nothing_in_16_to18_without_fabrication(self):
        r=self.ev
        notice=BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json"
        self.assertEqual(blob(notice.read_bytes()),"6b9a919f224bec8dc3659052a404b4173b6ef366")
        c=next(x for x in read(notice)["docs"] if x["paperCode"]=="00-C")
        self.assertEqual(c["pdfSha256"],"afc4ad2e67004a40539d05406813ff361d99696607cf6fc71c62484cc3001a71")
        ids=[x["questionId"] for x in c["confirmed"]]
        self.assertEqual(ids,r["officialNotice"]["namedChineseCorrections"])
        self.assertTrue(set(ids).isdisjoint({"114-00-C-16","114-00-C-17","114-00-C-18"}))
        self.assertFalse(r["officialNotice"]["formalG3QuestionAnswersPromoted"])
    def test_mutation_gates(self):
        for x in ("answer","image","scope","g3","release","shared_q19","crop","notice"):
            with self.subTest(case=x):
                r=copy.deepcopy(self.ev)
                if x=="answer":r["questionImageRecords"][0]["officialAnswer"]="D"
                elif x=="image":r["questionImageRecords"][1]["sha256"]="0"*64
                elif x=="scope":r["questionImageRecords"].append(r["questionImageRecords"][0])
                elif x=="g3":r["officialNotice"]["formalG3QuestionAnswersPromoted"]=True
                elif x=="release":r["downstream"]["ready"]=True
                elif x=="shared_q19":r["sharedMaterial"]["q19SourceQaInThisTask"]="PASS"
                elif x=="crop":r["sharedMaterial"]["cropPixels"]=[90,155,1310,1500]
                elif x=="notice":r["officialNotice"]["namedChineseCorrections"].append("114-00-C-17")
                with self.assertRaises(ValueError):valid(r)
    def test_original_db_integrity_not_rewritten(self):
        path=BASE/"question-bank.sqlite3"
        con=sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True)
        try:self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0],"ok")
        finally:con.close()
        self.assertFalse(self.ev["downstream"]["canonicalSqliteEdited"])
if __name__=="__main__":unittest.main()
