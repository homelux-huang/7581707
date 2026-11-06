#!/usr/bin/env python3
"""Apply SIX newly *directly visually reviewed* 115 Chinese crops + shared article.

Only the isolated QA branch; no changes to original images, answers, teaching,
student records, UI, main or LIVE. SHA and pixel exactness are independently
checked before QA metadata promotion. Official final answer stays UNVERIFIED.
"""
import argparse
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("sudu/data/processed/115")
BRANCH = "qa/114-115-official-visual-review"
EVIDENCE = BASE / "QA_115_C_Q06_Q11_15_DIRECT_VISUAL_20261023.json"
IDS = {"115-00-C-06", *{f"115-00-C-{n:02d}" for n in range(11,16)}}
SHARED_ID = "115-00-C-SHARED-11-15"
ANSWER_PAGE_SHA = "5422c00920ef4f18fa32fffd51c7edb78acd80aac84974713a61e2a02987126f"
FILES = ("questions.json", "webp-manifest.json", "inventory.json", "VALIDATION.json")
REQUIRED_CRITERIA = (
    "official_original_question_number", "complete_stem", "all_A_to_D",
    "formula_image_and_units", "no_other_question", "no_page_header_or_footer",
    "readable", "exact_source_and_webp_sha256", "exact_pixel_crop_verified_in_ci"
)

def full(path):
    p = (ROOT / path).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError("Attempted access outside repository")
    return p

def load(path):
    return json.loads(full(path).read_text(encoding="utf8"))

def sha(path):
    return hashlib.sha256(full(path).read_bytes()).hexdigest()

def index(rows,key):
    d={r[key]:r for r in rows}
    if len(d)!=len(rows):
        raise RuntimeError("Duplicate "+key)
    return d

def test_immutable_image(source, expected_source, crop, expected_crop, box):
    assert sha(source)==expected_source and sha(crop)==expected_crop, crop
    with Image.open(full(source)) as a, Image.open(full(crop)) as b:
        a.load();b.load()
        assert a.format=="WEBP" and b.format=="WEBP"
        section=a.crop(tuple(box))
        assert section.size==b.size
        assert ImageChops.difference(section.convert("RGB"),b.convert("RGB")).getbbox() is None, crop

def run(stage=False):
    current=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if current!=BRANCH:
        raise RuntimeError("Not the isolated QA branch")
    e=load(EVIDENCE); qbank=load(BASE/"questions.json")
    manifest=load(BASE/"webp-manifest.json")
    inv=load(BASE/"inventory.json"); val=load(BASE/"VALIDATION.json")
    if (e["year"]!=115 or e["questionWebpPassAdded"]!=6 or e["sharedMaterialPassAdded"]!=1
        or e["answerVerifiedAdded"]!=0 or e["questionVerifiedAdded"]!=0
        or e["releaseAllowed"] or e["integrationReady"] or e["independentHumanReview"]):
        raise RuntimeError("Unapproved evidence")
    records=index(e["items"],"questionId")
    assert set(records)==IDS
    qs=index(qbank["questions"],"questionId")
    mi=index(manifest["items"],"questionId")
    assert len(qs)==len(mi)==205 and set(qs)==set(mi)
    shared = next(s for s in manifest["sharedMaterialCrops"] if s["sharedMaterialId"]==SHARED_ID)
    assert sum(x["sharedMaterialId"]==SHARED_ID for x in manifest["sharedMaterialCrops"])==1
    er=e["sharedMaterials"]
    assert len(er)==1 and er[0]["sharedMaterialId"]==SHARED_ID and er[0]["result"]=="PASS"
    sr=er[0]
    for key,expected in (("source",sr["sourcePagePath"]),("sourceSha256",sr["sourcePageSha256"]),
                        ("output",sr["reviewedWebpPath"]),("sha256",sr["reviewedWebpSha256"]),
                        ("crop",sr["cropPixels"]),("sourcePage",sr["sourcePage"])):
        assert shared[key]==expected, "Shared material SHA/crop mismatch: "+key
    assert all(v is True for v in sr["criteria"].values())
    test_immutable_image(sr["sourcePagePath"],sr["sourcePageSha256"],
                         sr["reviewedWebpPath"],sr["reviewedWebpSha256"],sr["cropPixels"])
    answer_page="sudu/data/original/115/00-C-answers/p001-ec9871b659-v2-w1400-q66.webp"
    assert sha(answer_page)==ANSWER_PAGE_SHA
    matching={"115-00-C-06":"B","115-00-C-11":"D","115-00-C-12":"C",
              "115-00-C-13":"D","115-00-C-14":"B","115-00-C-15":"B"}
    prev_pass=sum(x.get("qaStatus")=="PASS" for x in manifest["items"])
    if prev_pass not in (135,141):
        raise RuntimeError(f"Unexpected concurrent 115 image QA count: {prev_pass}")
    assert inv["imageVisualQaPass"] in (135,141)
    assert inv["officialAnswerIndependentVerified"]==0
    assert val["stats"]["國文"]["officialAnswerIndependentlyVerified"]==0
    assert sum(x["visualQaPass"] for x in inv["perSubject"].values())==prev_pass
    for id in sorted(IDS):
        r=records[id]; m=mi[id]; q=qs[id]
        assert r["result"]=="PASS" and not r["independentHumanReview"]
        assert r["officialAnswerImage"]["imageMatchesCandidate"] is True
        assert r["officialAnswerImage"]["visuallyReadValue"]==matching[id]
        assert r["officialAnswerImage"]["candidateValue"]==matching[id]
        assert r["officialAnswerImage"]["sourcePageSha256"]==ANSWER_PAGE_SHA
        assert r["officialCorrectionContentReviewed"] is False
        assert not (r["answerVerified"] or r["questionVerified"] or r["integrationReady"])
        assert all(r["criteria"].get(key) is True for key in REQUIRED_CRITERIA)
        expected={"source":r["sourcePagePath"],"sourceSha256":r["sourcePageSha256"],
                  "sourcePage":r["sourcePage"],"sourcePdfSha256":r["sourceOfficialPdfSha256"],
                  "crop":r["cropPixels"],"output":r["reviewedWebpPath"],"sha256":r["reviewedWebpSha256"]}
        for key,v in expected.items():
            if m.get(key)!=v:
                raise RuntimeError(f"{id} current SHA/path/crop diverges: {key}")
        if sorted(r["sharedMaterialIds"])!=([SHARED_ID] if m["originalQuestionNumber"]>=11 else []):
            raise RuntimeError("Incorrect source article linkage: "+id)
        test_immutable_image(m["source"],m["sourceSha256"],m["output"],m["sha256"],m["crop"])
        if q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady"):
            raise RuntimeError("Refusing to change released question "+id)
        if m.get("qaStatus")=="PASS":
            if m.get("visualReviewEvidence",{}).get("reviewedSha256")!=m["sha256"]:
                raise RuntimeError("Already PASS with different SHA: "+id)
    if shared.get("qaStatus")=="PASS" and shared.get("visualReviewEvidence",{}).get("reviewedSha256")!=shared["sha256"]:
        raise RuntimeError("Shared material previously approved with different SHA")
    pending={id for id in IDS if mi[id].get("qaStatus")!="PASS"}
    if len(pending) not in (0,6):
        raise RuntimeError("Partially promoted batch; manual reconciliation needed")
    if not stage or not pending:
        return {"stage":stage,"alreadyApplied":not pending,"passedBefore":prev_pass,
                "passedAfter":prev_pass+len(pending),"newImagePass":len(pending),
                "answerVerifiedAdded":0,"releaseAllowed":False}
    reference=EVIDENCE.as_posix()
    for id in sorted(IDS):
        r=records[id];m=mi[id];q=qs[id]
        m["qaStatus"]="PASS"
        m["visualReviewEvidence"]={
            "reference":reference,"reviewedAt":"2026-10-23","reviewer":"ChatGPT assistant",
            "independentHumanReview":False,"method":"direct_original_page_vs_individual_WebP",
            "reviewedSha256":m["sha256"],"sourceSha256":m["sourceSha256"],
            "sharedMaterialId":SHARED_ID if m["originalQuestionNumber"]>=11 else None
        }
        q["imageQaStatus"]="PASS"
        q.setdefault("assets",{})["imageQaEvidence"]=reference
        # Intentionally never promote text, answers, teaching, release.
    shared["qaStatus"]="PASS"
    shared["visualReviewEvidence"]={
        "reference":reference,"reviewedAt":"2026-10-23",
        "reviewer":"ChatGPT assistant","independentHumanReview":False,
        "reviewedSha256":shared["sha256"],"sourceSha256":shared["sourceSha256"],
        "method":"direct_original_page_vs_shared_material_WebP"
    }
    after=sum(x.get("qaStatus")=="PASS" for x in manifest["items"])
    if after!=141 or prev_pass!=135:
        raise RuntimeError("Expected 135 existing + 6 new")
    inv["imageVisualQaPass"]=after
    inv["pendingVisualReviewIds"]=[id for id in inv["pendingVisualReviewIds"] if id not in IDS]
    inv["perSubject"]["國文"]["visualQaPass"]+=6
    inv["perSubject"]["國文"]["needsFullVisualReview"]-=6
    val["stats"]["國文"]["visualQaPass"]+=6
    val["stats"]["國文"]["needsFullVisualReview"]-=6
    val["published"]="NO";val["integration"]="NO"
    manifest.setdefault("qaDirectVisualComparison",{})["additionalBatch115C20261023"]=reference
    assert len(inv["pendingVisualReviewIds"])==205-after
    assert sum(s["visualQaPass"] for s in inv["perSubject"].values())==after
    assert val["stats"]["國文"]["visualQaPass"]==15
    assert val["stats"]["國文"]["needsFullVisualReview"]==23
    assert all(not (q.get("answerVerified") or q.get("questionVerified") or q.get("integrationReady"))
               for q in qbank["questions"])
    # Preserve staging DB/JSON consistency; no student tables are allowed.
    if stage:
        db=full(BASE/"question-bank.sqlite3")
        with sqlite3.connect(db) as cx:
            cols={c[1] for c in cx.execute("PRAGMA table_info(questions)")}
            assert "question_id" in cols and "payload_sha256" in cols
            field="payload" if "payload" in cols else "payload_json"
            assert field in cols
            assert not any(row[0] in ("student_answers","student_results") for row in cx.execute("SELECT name FROM sqlite_master WHERE type='table'"))
            for id in sorted(IDS):
                raw=json.dumps(qs[id],ensure_ascii=False,sort_keys=True,separators=(",",":"))
                assert cx.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                                  (raw,hashlib.sha256(raw.encode("utf8")).hexdigest(),id)).rowcount==1
            assert cx.execute("SELECT count(*) FROM questions").fetchone()[0]==205
            assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            for id,raw,hx in cx.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
                assert hashlib.sha256(raw.encode("utf8")).hexdigest()==hx and json.loads(raw)["questionId"]==id
        for fn,obj in (("questions.json",qbank),("webp-manifest.json",manifest),
                       ("inventory.json",inv),("VALIDATION.json",val)):
            full(BASE/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"stage":True,"passedBefore":prev_pass,"passedAfter":after,
            "newImagePass":len(pending),"sharedMaterialPassAdded":1,
            "answerVerifiedAdded":0,"questionVerifiedAdded":0,"integrationReady":False}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check",action="store_true")
    modes.add_argument("--stage",action="store_true")
    args=parser.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
