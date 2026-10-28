"""Role A exact original 114 English Q13,Q14 4-option source evidence only.

This test enforces immutable original source and prior 205 bank, does NOT make
A author an independent E teaching reviewer or approve formal source flag.
"""
import copy
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path
from PIL import Image, ImageChops
from scripts import sudu_verified_publish as pub

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/114"
PAGE=ROOT/"sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp"
ANSWERPAGE=ROOT/"sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp"
SOURCE_SHA="51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb"
SRC_BLOB="5ff21a726938e64e0b7efe3bb8abda65e55e1d4f"
ANS_SHA="a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863"
SRC_PDF="1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf"
CONFIRM_PDF="79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc"
PINS={
  13:{"sha":"81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7",
      "blob":"d3a37cc4ecb6c72b06fa19919a376a34203ed739",
      "crop":[90,870,1310,1120],"rev":"074fb9847eda936d31dfd4503f3a7a12cbde9f89ddc888957d8eba4f17fa746c",
      "answer":"A","dg":"e62d80dd377d6dcd8872b416f2499dc6c1c6f185f14644b5bdab188ff5a910d1","bpr":44,
      "options":["Are they fresh?","How much are they?","Do you plant them?","How do you cook them?"]},
  14:{"sha":"388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94",
      "blob":"2ec99e4912ac49b6c70e84183caadcdb402136bb",
      "crop":[90,1118,1310,1369],"rev":"6164a310c7d38229aaaf52df678121ee88f6242cf6611310badfb5b1b46714dd",
      "answer":"D","dg":"88aa9992f062197be0f930dda08ad61e71b9dcc21f1b10eb48cd12a125e07644","bpr":106,
      "options":["Which theater do you prefer?","Which movie are we going to see?",
                 "How much do you pay for two adults?","How can you even think of doing that?"]},
}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def gitsha(b):return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))

class RoleA114Source13And14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qbank=read(BASE/"questions.json")
        cls.byq={q["questionId"]:q for q in cls.qbank["questions"]}
        cls.mbank=read(BASE/"webp-manifest.json")
        cls.bym={q["questionId"]:q for q in cls.mbank["items"]}
        cls.old=next(p for p in read(ROOT/"sudu/data/years/114.json")["papers"] if p["paper"]=="00-E")
        cls.qarecs={x["questionId"]:x for x in read(BASE/"QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json")["items"]}
        cls.notices=next(x for x in read(BASE/"QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json")["docs"] if x["paperCode"]=="00-E")
        cls.ev={n:read(BASE/f"review-evidence/114-00-E-{n:02d}-source-text-20261028.json") for n in PINS}
        cls.ans={n:read(BASE/f"review-evidence/114-00-E-{n:02d}-official.json") for n in PINS}
        assert len(cls.byq)==len(cls.qbank["questions"])==len(cls.bym)==205

    def test_shared_original_page_sha_original_webp_and_no_new_pdf_rehash(self):
        self.assertEqual(sha(PAGE.read_bytes()),SOURCE_SHA)
        self.assertEqual(gitsha(PAGE.read_bytes()),SRC_BLOB)
        self.assertEqual(sha(ANSWERPAGE.read_bytes()),ANS_SHA)
        with Image.open(PAGE) as pic:
            pic.load()
            self.assertEqual(pic.format,"WEBP")
            self.assertEqual(pic.size,(1400,1981))
        for n,ex in self.ev.items():
            with self.subTest(n=n):
                source=ex["official"]
                self.assertEqual(source["originalSourcePageSha256"],SOURCE_SHA)
                self.assertEqual(source["originalSourcePageGitBlob"],SRC_BLOB)
                self.assertEqual(source["originalPaperSourcePdfShaPreviouslyRecorded"],SRC_PDF)
                self.assertFalse(source["originalPdfBytesRehashedNow"])
                self.assertEqual(source["paperCode"],"00-E")
                self.assertEqual(source["page"],3)

    def test_two_exact_webps_rgb_identical_unchanged_sha_printed_A_D_and_no_neighbor(self):
        with Image.open(PAGE) as original:
            original.load()
            for n,pin in PINS.items():
                qid=f"114-00-E-{n:02d}"
                q,m,e=self.byq[qid],self.bym[qid],self.ev[n]
                with self.subTest(qid=qid):
                    self.assertEqual(m["qaStatus"],"PASS") # historic assistant QA
                    self.assertEqual(m["sha256"],pin["sha"])
                    self.assertEqual(m["crop"],pin["crop"])
                    self.assertEqual(m["sourceSha256"],SOURCE_SHA)
                    path=ROOT/m["output"]
                    raw=path.read_bytes()
                    self.assertEqual(sha(raw),pin["sha"])
                    self.assertEqual(gitsha(raw),pin["blob"])
                    with Image.open(path) as img:
                        img.load()
                        self.assertEqual(img.format,"WEBP")
                        self.assertEqual(list(img.size),m["outputSize"])
                        crop=original.convert("RGB").crop(tuple(pin["crop"]))
                        self.assertIsNone(ImageChops.difference(crop,img.convert("RGB")).getbbox())
                    self.assertEqual(e["official"]["originalSingleWebpSha256"],pin["sha"])
                    self.assertEqual(e["official"]["originalSingleWebpGitBlob"],pin["blob"])
                    self.assertEqual(e["official"]["originalCropPixels"],pin["crop"])
                    obs=e["directPrintedSourceObservation"]
                    for key in ["actualVisualCheck","allFourChoicesComplete","wholeQuestionComplete",
                                "dialogueRolesAndBlankComplete","noAdjacentQuestionOrWholePage",
                                "noGraphicOrSharedArticleRequired","originalPixelRGBMatchRequired"]:
                        self.assertTrue(obs[key],(qid,key))
                    self.assertEqual(obs["sourceImageVisualQa"],
                        "PASS_ROLE_A_DIRECT_VISUAL_SOURCE_ORIGINAL_PIXELS_NOT_ROLE_E")
                    self.assertFalse(e["authoritativeSourceQuestionVerified"])

    def test_actual_114_raw_year_and_canonical_stem_four_options_match_true_p3(self):
        for n,pin in PINS.items():
            qid=f"114-00-E-{n:02d}"
            q=self.byq[qid]
            raw=self.old["questions"][n-1]
            e=self.ev[n]["directPrintedSourceObservation"]
            with self.subTest(qid=qid):
                self.assertEqual(q["questionId"],qid)
                self.assertEqual(q["originalQuestionNumber"],n)
                self.assertEqual(q["sourcePage"],3)
                self.assertEqual(q["paperCode"],"00-E")
                self.assertEqual(q["question"],raw["question"])
                self.assertEqual(q["options"],raw["options"])
                self.assertEqual(q["question"],e["exactCanonicalQuestion"])
                self.assertEqual(q["options"],e["exactPrintedOptions"])
                self.assertEqual(q["options"],pin["options"])
                self.assertFalse(raw["answerVerified"])
                self.assertFalse(raw["questionVerified"])
                self.assertEqual(q["sharedMaterialIds"],[])
                self.assertEqual(q["assets"]["sharedMaterialIds"],[])
                self.assertFalse(q["questionVerified"])
                self.assertTrue(q["answerVerified"]) # PR94, NOT this source note
        self.assertIn("chemical free",self.byq["114-00-E-13"]["question"])
        self.assertIn("what about the eggs",self.byq["114-00-E-13"]["question"])
        self.assertIn("cut in line",self.byq["114-00-E-14"]["question"])
        self.assertIn("July:",self.byq["114-00-E-14"]["question"])

    def test_publisher_revision_and_bad_option_or_source_sha_fail_closed(self):
        for n,pin in PINS.items():
            qid=f"114-00-E-{n:02d}"
            q=self.byq[qid];e=self.ev[n]["bindings"]
            with self.subTest(qid=qid):
                self.assertEqual(pub.text_revision(q,pin["sha"]),pin["rev"])
                self.assertEqual(e["sourceRevisionExpected"],pin["rev"])
                bad=copy.deepcopy(q)
                bad["options"][0]+=" and fabricated text"
                self.assertNotEqual(pub.text_revision(bad,pin["sha"]),pin["rev"])
                bad=copy.deepcopy(q);bad["question"]+=" wrong"
                self.assertNotEqual(pub.text_revision(bad,pin["sha"]),pin["rev"])
                self.assertNotEqual(pub.text_revision(q,"0"*64),pin["rev"])

    def test_original_prior_image_assistant_qa_pass_is_not_new_teacher_or_e_qa(self):
        for n,pin in PINS.items():
            qid=f"114-00-E-{n:02d}";qa=self.qarecs[qid];m=self.bym[qid]
            with self.subTest(qid=qid):
                self.assertEqual(qa["reviewedWebpSha256"],pin["sha"])
                self.assertEqual(qa["cropPixels"],pin["crop"])
                self.assertEqual(qa["sourcePageSha256"],SOURCE_SHA)
                self.assertEqual(qa["result"],"PASS")
                self.assertTrue(all(qa["criteria"].values()))
                self.assertFalse(qa["independentHumanReview"])
                self.assertFalse(qa["answerVerified"])
                self.assertFalse(qa["questionVerified"])
                self.assertFalse(qa["integrationReady"])
                self.assertEqual(m["visualReviewEvidence"]["reviewedSha256"],pin["sha"])

    def test_existing_pr94_official_A_D_valid_notice_scope_E26_only_no_promotions(self):
        self.assertEqual(self.notices["pdfSha256"],CONFIRM_PDF)
        self.assertEqual([r["questionId"] for r in self.notices["confirmed"]],["114-00-E-26"])
        for n,pin in PINS.items():
            qid=f"114-00-E-{n:02d}"
            q,ans,ex=self.byq[qid],self.ans[n],self.ev[n]
            with self.subTest(qid=qid):
                self.assertEqual(q["answer"],pin["answer"])
                self.assertEqual(ans["finalAnswer"],pin["answer"])
                self.assertEqual(ans["officialAnswerImageSha256"],ANS_SHA)
                self.assertEqual(ans["reviewedSingleQuestionWebpSha256"],pin["sha"])
                self.assertEqual(ans["confirmationPdfSha256"],CONFIRM_PDF)
                self.assertTrue(ans["noCorrectionForThisQuestion"])
                self.assertFalse(ans["noObjectionForPaper"])
                self.assertTrue(pub.official_notice_scope_certified(ROOT,114,q,ans))
                bad=copy.deepcopy(ans);bad["confirmationPdfSha256"]="0"*64
                self.assertFalse(pub.official_notice_scope_certified(ROOT,114,q,bad))
                self.assertTrue(ex["bindings"]["originalAnswerVerifiedInPR94"])
                self.assertFalse(ex["newOfficialAnswerReviewGranted"])
                self.assertFalse(ex["newQuestionVerifiedGranted"])
                self.assertEqual(ex["bindings"]["officialEnglishOnlyNamedConfirmationId"],"114-00-E-26")

    def test_205_canonical_114_sqlite_raw_payloads_are_unchanged(self):
        bankpath=BASE/"question-bank.sqlite3"
        with sqlite3.connect(bankpath.as_uri()+"?mode=ro",uri=True) as cx:
            self.assertEqual(cx.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual([x[1] for x in cx.execute("PRAGMA table_info(questions)")],
                ["question_id","year","paper_code","original_number","subject","payload_json","payload_sha256"])
            rows=cx.execute("SELECT question_id,payload_json,payload_sha256 FROM questions").fetchall()
        self.assertEqual(len(rows),205)
        self.assertEqual({r[0] for r in rows},set(self.byq))
        for qid,payload,digest in rows:
            with self.subTest(qid=qid):
                self.assertEqual(sha(payload.encode("utf-8")),digest)
                self.assertEqual(json.loads(payload),self.byq[qid])
                self.assertEqual(payload,canonical(self.byq[qid]))
        self.assertEqual(gitsha(bankpath.read_bytes()),"27314572b3d18fd0bd20003297bccadbc6c59737")
        self.assertEqual(gitsha((BASE/"questions.json").read_bytes()),"1535754345a08d25636e00b4ba3270a1f764bf66")
        self.assertEqual(gitsha((BASE/"webp-manifest.json").read_bytes()),"249a41d5a64558ccaa3084b21f915922a55c6a1b")

    def test_independent_B_digests_unmodified_but_E14_latest_requires_new_E_and_D(self):
        for n,pin in PINS.items():
            e=self.ev[n];b=e["previousRoleBAuthorReadOnly"]
            with self.subTest(n=n):
                self.assertEqual(b["pr"],pin["bpr"])
                self.assertEqual(b["authorComposedTeachingDigestCandidate"],pin["dg"])
                self.assertFalse(b["independentEPostAuthorRevisionTrusted"])
                self.assertFalse(b["actualPublisherProducedV4Browser8x2SameDigest"])
                self.assertFalse(e["teacherIdentityClaimed"])
                self.assertFalse(e["newQuestionVerifiedGranted"])
                self.assertFalse(e["newOfficialAnswerReviewGranted"])
                self.assertEqual(e["newReady"],e["newLive"])
                self.assertEqual(e["newReady"],0)
                self.assertTrue(e["sourceQuestionsJSONUnchanged"])
                self.assertTrue(e["originalWebpUnchanged"])
        self.assertEqual(read(ROOT/"sudu/data/approved/114.json")["approvedCount"],0)

if __name__=="__main__":unittest.main()
