#!/usr/bin/env python3
"""107 English Q36/37 exact source-image G1 plus full four-option text G2.

Q37 OLD v1 cropped in the unrelated Q38-41 robots passage. Only v2 new
question-only WebP may PASS. Historical v1 and raw PDF-layer text are retained.
AI visual review is NOT independent human; G3/annual G6 remain forbidden.
"""
from __future__ import annotations
import argparse,difflib,hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
import sqlite3,tempfile,shutil,os
from audit_105_115_sqlite_readonly import audit_year,canonical,digest

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
BASE="sudu/data/processed/107/"
PAGE="sudu/data/original/107/00-E/p007-6fa77b536c-v2-w1400-q66.webp"
PAGE_SHA="89997a38a422f25589afd9632ad558f76f44684c2c0aa75c3f15429020ac8fac"
PAGE_BLOB="dacba885baae37a8290476026df3a2cf0eda2be3"
PDF_SHA="6fa77b536c5a991af6ad12f33427d362614109fad4f7d701ec25bc453dec7440"
DRAFT=BASE+"qa-drafts/DRAFT_107_E37_Q38_ARTICLE_REMOVED_V2_20261024.json"
EVIDENCE=BASE+"qa-drafts/DIRECT_VISUAL_AND_TEXT_107_E36_E37_20261024.json"
SHARED_ID="107-00-E-SHARED-34-37"

TARGETS={
  36:{
    "crop":[90,156,1310,372],
    "path":"sudu/data/processed/107/webp-v1/00-E/107-00-E-36.webp",
    "sha":"2814146a40347909f38095c125c14fab019893dcfc683bff899bb62d00f202f8",
    "question":"Which of the following is NOT true when Chi was making Beyond Beauty: Taiwan from Above?",
    "options":[
      "Chi refused to accept funds from others.",
      "Chi tried to borrow money from banks.",
      "Chi had a hard time finding enough money.",
      "Chi spent all his money producing the film.",
    ],
    "answerCandidate":"A",
    "visualObservation":"Q36 NOT and full Beyond Beauty: Taiwan from Above stem and A-D present, no Q37",
  },
  37:{
    "crop":[90,372,1310,568],
    "path":"sudu/data/processed/107/qa-drafts/webp-v2/00-E/107-00-E-37.webp",
    "sha":"7d6e7f7203012b161b7e2598a6f56e6a4c271fe91cc1fedaff28d669b63557a6",
    "question":"What is this passage mainly about?",
    "options":[
      "Chi and his concern about the environment.",
      "The success of Chi’s documentary abroad.",
      "What Chi went through to save typhoon victims.",
      "The scenery recorded by Chi in his documentary.",
    ],
    "answerCandidate":"A",
    "visualObservation":"Q37 stem A-D complete, unrelated Q38-41 reading header and robots article excluded in new v2; old v1 preserved",
  },
}

def path(rel):
    loc=(ROOT/rel).resolve()
    assert loc.is_relative_to(ROOT.resolve())
    return loc
def read(rel):
    return json.loads(path(rel).read_text("utf8"))
def write(rel, data):
    path(rel).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def idx(rows):
    out={v["questionId"]:v for v in rows}
    assert len(out)==len(rows)
    return out
def glyph_lines(q,opts):
    return [q+"\n"]+[v+"\n" for v in opts]

def update_db_107(bank):
    """G5: update a disposable 107 DB, including ALL currently present shared material IDs.

    The old E32-35 helper assumed exactly 2 shared records. Since the Chinese
    107 batch, that fixed count is stale. Require exact equality with the current
    canonical bank, not a lowered bound; never alter the source DB on failure.
    """
    dbfile=path(BASE+"question-bank.sqlite3")
    expected_questions={q["questionId"]:q for q in bank["questions"]}
    expected_shared={s["sharedMaterialId"]:s for s in bank["sharedMaterials"]}
    assert len(expected_questions)==len(bank["questions"])==204
    assert len(expected_shared)==len(bank["sharedMaterials"])
    with tempfile.TemporaryDirectory(dir=dbfile.parent) as td:
        staged=Path(td)/"question-bank.sqlite3"
        shutil.copyfile(dbfile,staged)
        with sqlite3.connect(staged) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            old_count=db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
            assert old_count==204
            for turn in (1,2):
                for q in bank["questions"]:
                    payload=canonical(q)
                    cursor=db.execute(
                        "UPDATE questions SET payload=?,payload_sha256=? WHERE question_id=?",
                        (payload,digest(payload.encode("utf8")),q["questionId"]))
                    assert cursor.rowcount==1, q["questionId"]
                for material in bank["sharedMaterials"]:
                    db.execute(
                        "INSERT INTO shared_materials(material_id,payload) VALUES (?,?) "
                        "ON CONFLICT(material_id) DO UPDATE SET payload=excluded.payload",
                        (material["sharedMaterialId"],canonical(material)))
                db.commit()
                assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
                assert db.execute("SELECT COUNT(*) FROM shared_materials").fetchone()[0]==len(expected_shared)
                assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            rows=db.execute("SELECT question_id,payload,payload_sha256 FROM questions").fetchall()
            assert len(rows)==204
            for id,payload,hsh in rows:
                assert id in expected_questions and json.loads(payload)==expected_questions[id]
                assert digest(payload.encode("utf8"))==hsh
            shared_rows=db.execute("SELECT material_id,payload FROM shared_materials").fetchall()
            assert len(shared_rows)==len(expected_shared)
            for id,payload in shared_rows:
                assert id in expected_shared and json.loads(payload)==expected_shared[id]
        os.replace(staged,dbfile)


def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    names=["questions.json","webp-manifest.json","ocr-raw-candidates.json","VISUAL_QA.json",
           "inventory.json","VALIDATION.json","release-manifest.json"]
    files={name:read(BASE+name) for name in names}
    qs=files["questions.json"];m=files["webp-manifest.json"]
    o=files["ocr-raw-candidates.json"];v=files["VISUAL_QA.json"]
    inv=files["inventory.json"];val=files["VALIDATION.json"];rel=files["release-manifest.json"]
    assert len(qs["questions"])==len(m["items"])==len(o["items"])==len(v["items"])==204
    assert inv["webpGeneratedDrafts"]==204 and inv["answerOfficialFinalVerified"]==0
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    qrow,mrow,orow,vrow=map(idx,[qs["questions"],m["items"],o["items"],v["items"]])
    shared={s["sharedMaterialId"]:s for s in m["sharedMaterialCrops"]}
    assert shared[SHARED_ID]["qaStatus"]=="PASS","Shared source passage must have own G1 QA"
    assert shared[SHARED_ID]["visualReviewEvidence"]["independentHumanReview"] is False

    draft=read(DRAFT)
    assert draft["candidateReviewStatus"]=="DRAFT_AWAITING_NEW_INDIVIDUAL_VISUAL_G1"
    assert draft["candidateCropPixels"]==TARGETS[37]["crop"]
    assert draft["candidateSha256"]==TARGETS[37]["sha"]
    assert draft["officialSourcePdfFreshlyRedownloaded"] is False
    assert sha(path(draft["historicalLegacyCrop"]).read_bytes())==draft["historicalLegacySha256"]

    original=path(PAGE).read_bytes()
    assert sha(original)==PAGE_SHA
    assert hashlib.sha1(b"blob "+str(len(original)).encode()+b"\0"+original).hexdigest()==PAGE_BLOB
    done=all(mrow[f"107-00-E-{n}"]["qaStatus"]=="PASS" for n in TARGETS)
    expect_g1=21 if done else 19
    expect_g2=7 if done else 5
    assert inv["visualQaPass"]==val["imageVisualQaPass"]==v["passCount"]==expect_g1
    assert inv["ocrTextIndependentlyVerified"]==val["ocrTextVerified"]==expect_g2
    assert not any(z["answerVerified"] or z["integrationReady"] for z in qs["questions"])
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    reviewed=[]
    with Image.open(io.BytesIO(original)) as page:
        page.load();assert page.format=="WEBP" and page.size==(1400,1980)
        for n,info in TARGETS.items():
            id=f"107-00-E-{n:02d}"
            q,img,ocr,visual=qrow[id],mrow[id],orow[id],vrow[id]
            assert img["source"]==PAGE and img["sourcePage"]==7
            assert img["officialQuestionPdfSha256"]==PDF_SHA
            assert img["sourcePageWebpSha256"]==PAGE_SHA
            assert q["sharedMaterialIds"]==[SHARED_ID]
            assert q["answer"]==info["answerCandidate"] and q["answerMatched"]
            assert not q["answerVerified"] and not q["integrationReady"]
            assert ocr["rawOcrText"] is None
            assert img["qaStatus"]==("PASS" if done else "DRAFT_NEEDS_DIRECT_VISUAL_QA")
            assert visual["status"]==("PASS" if done else "PENDING")
            if n==36 or done:
                assert img["output"]==info["path"]
                assert img["outputSha256"]==info["sha"]
            else:
                assert img["output"]==draft["historicalLegacyCrop"]
                assert img["outputSha256"]==draft["historicalLegacySha256"]
            candidate=path(info["path"]).read_bytes()
            assert sha(candidate)==info["sha"]
            with Image.open(io.BytesIO(candidate)) as crop:
                crop.load();assert crop.size==(info["crop"][2]-info["crop"][0],info["crop"][3]-info["crop"][1])
                assert ImageChops.difference(page.crop(tuple(info["crop"])).convert("RGB"),crop.convert("RGB")).getbbox() is None
            raw_q,raw_options=ocr["legacyQuestion"],ocr["legacyOptions"]
            diff="".join(difflib.unified_diff(glyph_lines(raw_q,raw_options),
                 glyph_lines(info["question"],info["options"]),
                 fromfile="legacy-extraction-preserved",tofile="new-direct-image-reviewed"))
            assert len(info["options"])==4 and all(z.strip() for z in info["options"])
            if n==37:
                assert "In 2017" in raw_options[3] and "In 2017" not in info["options"][3]
                assert "閱讀下文" in raw_options[3]
            record={
              "questionId":id,"sourcePage":7,
              "sourcePageWebp":PAGE,"sourcePageSha256":PAGE_SHA,
              "sourceGitBlob":PAGE_BLOB,
              "officialPdfSha256FromExistingRepository":PDF_SHA,
              "cropPixels":info["crop"],
              "reviewedCurrentCandidate":info["path"],"reviewedSha256":info["sha"],
              "pixelDifferenceZero":True,"observed":info["visualObservation"],
              "legacyQuestion":raw_q,"legacyOptions":raw_options,
              "correctedQuestion":info["question"],"correctedOptions":info["options"],
              "legacyToCorrectedUnifiedDiff":diff,
              "originalRawOcrText":None,"newG1HumanCertification":False,
              "textQaResult":"PASS_ASSISTANT_SOURCE_PAGE_DIRECT_TEXT"}
            reviewed.append(record)
            if done:
                assert q["question"]==info["question"] and q["options"]==info["options"]
                assert q["textQaStatus"]=="PASS" and q["questionVerified"] is True
                assert ocr["qaStatus"]=="PASS" and ocr["correctedOptions"]==info["options"]
                continue
            assert q["questionVerified"] is False
            assert ocr["qaStatus"]=="PENDING"
            if stage:
                proof={"reference":EVIDENCE,"reviewer":"ChatGPT assistant",
                       "reviewedAt":now,"independentHumanReview":False,
                       "method":"assistant_direct_original_page7_and_current_crop_visual_plus_CI_zero_pixel_diff",
                       "sourceSha256":PAGE_SHA,"reviewedSha256":info["sha"],
                       "sourcePage":7,"cropPixels":info["crop"]}
                img["qaStatus"]="PASS";img["visualReviewEvidence"]=proof
                if n==37:
                    img["sourceGitBlob"]=PAGE_BLOB
                    img["generationVersion"]="assistant-v2-article-boundary-repaired-20261024"
                    img["cropPixels"]=info["crop"]
                    img["output"]=info["path"]
                    img["outputSha256"]=info["sha"]
                    img["outputSize"]=[1220,196]
                q["imageQaStatus"]="PASS"
                q["legacyUnverifiedQuestion"]=q["question"]
                q["legacyUnverifiedOptions"]=q["options"]
                q.update({"question":info["question"],"options":info["options"],
                          "questionVerified":True,"textQaStatus":"PASS",
                          "textQaEvidence":EVIDENCE,
                          "ocrStatus":"PASS_REVIEWED_ORIGINAL_PAGE_IMAGE"})
                if n==37:
                    q["legacySingleQuestionWebpV1"]=draft["historicalLegacyCrop"]
                    q["legacySingleQuestionWebpV1Sha256"]=draft["historicalLegacySha256"]
                    q["assets"]["singleQuestionWebp"]=info["path"]
                    q["assets"]["sha256"]=info["sha"]
                visual.update({"status":"PASS","reviewer":"ChatGPT assistant",
                               "visualEvidence":EVIDENCE})
                if n==37:
                    visual["candidateWebp"]=info["path"]
                    visual["candidateSha256"]=info["sha"]
                ocr.update({"correctedQuestion":info["question"],
                            "correctedOptions":info["options"],"diff":diff,
                            "qaStatus":"PASS","qaReviewer":"ChatGPT assistant",
                            "qaReviewedAt":now,"qaEvidencePath":EVIDENCE,
                            "imageSha256":info["sha"]})
    if done:
        assert path(EVIDENCE).exists()
        print(json.dumps({"mode":"IDEMPOTENT","G1":21,"G2":7,"G3":0,"NO_RELEASE":True}))
        return
    if stage:
        inv["visualQaPass"]=v["passCount"]=val["imageVisualQaPass"]=21
        inv["ocrTextIndependentlyVerified"]=inv["textQaPass"]=val["ocrTextVerified"]=7
        rel["imageQA"]="PARTIAL_21_OF_204"
        rel["questionTextQA"]="PARTIAL_7_OF_204"
        evidence={"schemaVersion":1,"year":107,"paperCode":"00-E","reviewer":"ChatGPT assistant",
            "independentHumanReview":False,"reviewedAt":now,"sourceOfficialPageSha256":PAGE_SHA,
            "officialPdfBytesFreshDownloaded":False,"newIndividualG1Pass":2,
            "newG2Pass":2,"newG3AnswerVerified":0,"releaseAllowed":False,
            "integrationReady":False,"Q37LegacyImageContaminationWasRepaired":True,
            "relatedExistingSharedMaterialId":SHARED_ID,"sharedMaterialQaNoChange":True,
            "Q38To41OwnReviewStatusesNotModified":True,"records":reviewed}
        for name in names:write(BASE+name,files[name])
        write(EVIDENCE,evidence)
        update_db_107(qs)
        audits=[audit_year(year) for year in range(105,116)]
        assert len(audits)==11 and all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in audits)
        aggregate="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
        report=read(aggregate)
        report.update({"years":audits,"yearsG5Pass":11,"yearsReviewed":11,
                       "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
        write(aggregate,report)
    print(json.dumps({"mode":"STAGED" if stage else "CHECK","newG1":2,"newG2":2,
          "107G1":21,"107G2":7,"Q37NewWebpSha256":TARGETS[37]["sha"],
          "newG3":0,"releaseAllowed":False,"integrationReady":False}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--stage",action="store_true")
    run(p.parse_args().stage)
