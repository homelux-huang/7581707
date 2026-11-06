#!/usr/bin/env python3
"""SHA-guarded image-only promotion of three *directly visually reviewed* crops.

Review evidence was recorded separately after comparing official archived page
renders to exact generated WebP candidates. Keep all old versions immutable.
Never verify answers, OCR, shared material or release from image QA alone.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import sqlite3
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BRANCH="qa/114-115-official-visual-review"
LEDGER=Path("sudu/data/processed/114/qa-drafts/DIRECT_VISUAL_114C01_115C16_17_20261023.json")
DRAFT=Path("sudu/data/processed/114/qa-drafts/CROP_REPAIRS_114C01_115C16_17_V20261023.json")
EXACT_IDS={"114-00-C-01","115-00-C-16","115-00-C-17"}

def full(path):
    p=(ROOT/path).resolve()
    assert p.is_relative_to(ROOT)
    return p

def read(path):
    return json.loads(full(path).read_text("utf8"))

def sha(path):
    return hashlib.sha256(full(path).read_bytes()).hexdigest()

def dump(path,obj):
    full(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def index(records,key):
    o={r[key]:r for r in records}
    assert len(o)==len(records)
    return o

def validate_visual():
    l=read(LEDGER);d=read(DRAFT)
    assert l["numberNewImageQaPass"]==3 and not l["answerVerifiedAdded"]
    assert not l["questionVerifiedAdded"] and not l["integrationReady"] and not l["releaseAllowed"]
    assert d["newImageQaPass"]==0 and not d["releaseAllowed"]
    records=index(l["items"],"questionId")
    draft=index(d["items"],"questionId")
    assert set(records)==set(draft)==EXACT_IDS
    source_module=full("scripts/stage_114_115_direct_source_crop_repairs_20261023.py")
    spec=importlib.util.spec_from_file_location("reviewed_crop_generator",source_module)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for qid,r in records.items():
        b=draft[qid]
        assert r["result"]=="PASS_DIRECT_ORIGINAL_PAGE_CROP_VISUAL"
        assert all(x is True for x in r["criteria"].values())
        assert r["independentHumanReview"] is False
        assert r["answerVerified"] is False and r["questionVerified"] is False
        assert r["sourcePagePath"]==b["source"] and r["sourcePageSha256"]==b["sourcePageSha256"]
        assert r["reviewedWebpPath"]==b["candidatePath"] and r["reviewedWebpSha256"]==b["candidateSha256"]
        assert r["previousWebpPath"]==b["oldWebp"] and r["previousWebpSha256"]==b["oldWebpSha256"]
        assert r["sourcePage"]==b["sourcePage"]
        assert sha(r["sourcePagePath"])==r["sourcePageSha256"]
        assert sha(r["reviewedWebpPath"])==r["reviewedWebpSha256"]
        assert sha(r["previousWebpPath"])==r["previousWebpSha256"]
        expected,size=mod.make(r["sourcePagePath"],qid)
        # Exact pixel equivalence also holds if WebP library encoding changes.
        with Image.open(io.BytesIO(expected)) as expected_image, Image.open(full(r["reviewedWebpPath"])) as candidate:
            expected_image.load();candidate.load()
            assert tuple(size)==candidate.size
            assert ImageChops.difference(expected_image.convert("RGB"),candidate.convert("RGB")).getbbox() is None
    return records,draft

def update_db(year,modified,all_questions):
    root=Path(f"sudu/data/processed/{year}")
    dbfile=full(root/"question-bank.sqlite3")
    with sqlite3.connect(dbfile) as db:
        columns={x[1] for x in db.execute("PRAGMA table_info(questions)")}
        assert {"question_id","payload_sha256"}<=columns
        field="payload" if "payload" in columns else "payload_json"
        assert field in columns
        tables={x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert not {"student_answers","student_results","student_progress"}.intersection(tables)
        for qid,q in sorted(modified.items()):
            wire=json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(",",":"))
            payload_hash=hashlib.sha256(wire.encode("utf8")).hexdigest()
            assert db.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                              (wire,payload_hash,qid)).rowcount==1
        assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        assert db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==205
        seen={}
        for question_id,payload,payload_hash in db.execute(
             f"SELECT question_id,{field},payload_sha256 FROM questions"):
            assert hashlib.sha256(payload.encode("utf8")).hexdigest()==payload_hash
            assert json.loads(payload)["questionId"]==question_id
            seen[question_id]=json.loads(payload)
        assert len(seen)==205
        for qid,q in modified.items():
            assert seen[qid]==q

def run(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    records,draft=validate_visual()
    staged={}
    for year in (114,115):
        base=Path(f"sudu/data/processed/{year}")
        bank=read(base/"questions.json")
        manifest=read(base/"webp-manifest.json")
        inv=read(base/"inventory.json")
        val=read(base/"VALIDATION.json")
        release=read(base/"release-manifest.json")
        qs=index(bank["questions"],"questionId")
        mi=index(manifest["items"],"questionId")
        assert len(qs)==len(mi)==205 and set(qs)==set(mi)
        target=[x for x in sorted(EXACT_IDS) if x.startswith(str(year)+"-")]
        pending=[]
        for qid in target:
            r=records[qid];b=draft[qid];m=mi[qid];q=qs[qid]
            assert m["source"]==r["sourcePagePath"] and m["sourceSha256"]==r["sourcePageSha256"]
            assert m["sourcePage"]==r["sourcePage"]
            assert not q.get("answerVerified") and not q.get("integrationReady")
            if m.get("qaStatus")=="PASS":
                assert m["output"]==r["reviewedWebpPath"] and m["sha256"]==r["reviewedWebpSha256"]
                assert m["visualReviewEvidence"]["reference"]==LEDGER.as_posix()
                assert q["imageQaStatus"]=="PASS"
            else:
                assert m["output"]==r["previousWebpPath"] and m["sha256"]==r["previousWebpSha256"]
                assert q.get("imageQaStatus")!="PASS"
                pending.append(qid)
        before=sum(x.get("qaStatus")=="PASS" for x in manifest["items"])
        expected_old=24 if year==114 else 141
        expected_after=25 if year==114 else 143
        assert before==expected_old+sum(qid not in pending for qid in target)
        if not pending:
            staged[year]={"added":0,"total":before,"idempotent":True}
            continue
        if not stage:
            staged[year]={"pending":pending,"totalBefore":before}
            continue
        for qid in pending:
            m=mi[qid];q=qs[qid];r=records[qid];b=draft[qid]
            m["oldAssetBeforeDirectVisualRepair"]={
                "output":m["output"],"sha256":m["sha256"],"crop":m["crop"],
                "qaStatus":m["qaStatus"],"processingVersion":m.get("processingVersion")
            }
            m["output"]=r["reviewedWebpPath"]
            m["sha256"]=r["reviewedWebpSha256"]
            m["crop"]=r["cropSourcePixelBounds"]
            m["outputSize"]=b["candidateSizePixels"]
            m["processingVersion"]="direct-source-pixel-review-2026-10-23"
            m["cropMethod"]=r["compositionMethod"]
            m["issues"]=[]
            m["qaStatus"]="PASS"
            m["visualReviewEvidence"]={
                "reference":LEDGER.as_posix(),"reviewedAt":"2026-10-23",
                "reviewer":"ChatGPT assistant","independentHumanReview":False,
                "method":"direct_visual_official_source_page_render_to_exact_candidate_webp",
                "reviewedSha256":r["reviewedWebpSha256"],
                "sourceSha256":r["sourcePageSha256"],
                "cropSourcePixelBounds":r["cropSourcePixelBounds"],
                "compositionMethod":r["compositionMethod"],
                "note":"Image G1 only. OCR, shared passages and final official answer independently gated."
            }
            q.setdefault("assets",{})["singleQuestionWebp"]=r["reviewedWebpPath"]
            q["assets"]["sha256"]=r["reviewedWebpSha256"]
            q["assets"]["cropCoordinates"]=r["cropSourcePixelBounds"]
            q["assets"]["outputSize"]=b["candidateSizePixels"]
            q["assets"]["processingVersion"]=m["processingVersion"]
            q["assets"]["cropMethod"]=r["compositionMethod"]
            q["assets"]["visualQa"]="PASS_ASSISTANT_DIRECT_ORIGINAL_SOURCE"
            q["assets"]["visualReviewEvidence"]=LEDGER.as_posix()
            q["assets"]["imageQaEvidence"]=LEDGER.as_posix()
            if year==114:
                q["questionProvenance"]["webpSha256"]=r["reviewedWebpSha256"]
            q["imageQaStatus"]="PASS"
            q["questionVerified"]=False
            q["answerVerified"]=False
            q["integrationReady"]=False
            q["issues"]=[s for s in q.get("issues",[]) if s!="single_question_crop_not_yet_generated"]
        after=sum(x.get("qaStatus")=="PASS" for x in manifest["items"])
        assert after==expected_after
        if year==114:
            visual=read(base/"VISUAL_QA.json")
            vi=index(visual["questions"],"questionId")
            v=vi["114-00-C-01"]
            assert v["result"]=="BLOCKED"
            v["previousBlockedCropHistory"]={
                "result":v["result"],"asset":v["asset"],"assetSha256":v["assetSha256"],
                "failureReason":v.get("failureReason")
            }
            v.update({"result":"PASS","asset":records["114-00-C-01"]["reviewedWebpPath"],
                      "assetSha256":records["114-00-C-01"]["reviewedWebpSha256"],
                      "reviewedWebpSha256":records["114-00-C-01"]["reviewedWebpSha256"],
                      "evidenceReference":LEDGER.as_posix(),"reviewedAt":"2026-10-23",
                      "reviewer":"ChatGPT assistant","failureReason":None})
            visual["passCount"]=after
            manifest["visualQaPass"]=after
            inv["webpVisualQaPassed"]=after
            val["imageVisualQaPass"]=after
            val["blockedCropIds"]=[x for x in val.get("blockedCropIds",[]) if x not in pending]
            release["imageQA"]=f"PARTIAL_{after}_OF_205"
            dump(base/"VISUAL_QA.json",visual)
        else:
            inv["imageVisualQaPass"]=after
            inv["pendingVisualReviewIds"]=[qid for qid in inv["pendingVisualReviewIds"] if qid not in pending]
            inv["perSubject"]["國文"]["visualQaPass"]+=len(pending)
            inv["perSubject"]["國文"]["needsFullVisualReview"]-=len(pending)
            val["stats"]["國文"]["visualQaPass"]+=len(pending)
            val["stats"]["國文"]["needsFullVisualReview"]-=len(pending)
            assert len(inv["pendingVisualReviewIds"])==205-after
            assert sum(x["visualQaPass"] for x in inv["perSubject"].values())==after
            release["imageQA"]=f"PARTIAL_{after}_OF_205"
            # Canonical evidence INDEX, not a new invented independent QA review.
            # Older 141 records retain original original visual evidence references.
            v={
                "schemaVersion":1,"year":115,"purpose":"canonical G1 evidence index only",
                "reviewerPolicy":"PASS requires exact SHA-bound original visual evidence",
                "passCount":after,"questionCount":205,"sharedMaterialPassCount":
                   sum(x.get("qaStatus")=="PASS" for x in manifest["sharedMaterialCrops"]),
                "questions":[],
                "sharedMaterials":[{
                    "sharedMaterialId":x["sharedMaterialId"],
                    "qaStatus":x.get("qaStatus","PENDING"),
                    "reference":(x.get("visualReviewEvidence") or {}).get("reference"),
                    "sha256":x.get("sha256")
                } for x in manifest["sharedMaterialCrops"]],
                "legacyEvidenceFiles":["VISUAL_QA_2026-10-22.json","VISUAL_QA_2026-10-22_B2.json"]
            }
            for m in manifest["items"]:
                ev=m.get("visualReviewEvidence") or {}
                valid=(m.get("qaStatus")=="PASS" and ev.get("reviewedSha256")==m.get("sha256") and ev.get("reference"))
                if m.get("qaStatus")=="PASS" and not valid:
                    raise RuntimeError("Missing prior PASS evidence: "+m["questionId"])
                v["questions"].append({
                    "questionId":m["questionId"],
                    "status":"PASS" if valid else "PENDING",
                    "webpSha256":m.get("sha256"),
                    "evidenceReference":ev.get("reference") if valid else None
                })
            assert sum(x["status"]=="PASS" for x in v["questions"])==after
            dump(base/"VISUAL_QA.json",v)
        # G6 stays blocked on incomplete official corrections, OCR and shared material.
        inv["integrationReady"]=False
        val["integrationReady"]=False
        if "releaseAllowed" in val:val["releaseAllowed"]=False
        release["integrationReady"]=False
        release["releaseAllowed"]=False
        for q in bank["questions"]:
            assert not q.get("integrationReady")
        update_db(year,{qid:qs[qid] for qid in pending},bank["questions"])
        for filename,obj in (("questions.json",bank),("webp-manifest.json",manifest),
                              ("inventory.json",inv),("VALIDATION.json",val),
                              ("release-manifest.json",release)):
            dump(base/filename,obj)
        staged[year]={"newImagePass":len(pending),"total":after,"releaseAllowed":False}
    return staged

if __name__=="__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--stage",action="store_true")
    args=p.parse_args()
    print(json.dumps(run(stage=args.stage),ensure_ascii=False))
