#!/usr/bin/env python3
"""Direct original-image 106 Chinese C16 C17 C19 G2 for three unambiguous stems.
Preserve unverified old PDF layer and raw OCR null, with unified diff.
Selected correct image and shared material must already have source-bound G1 PASS.
Does not reinterpret official answers, or promote 114/115/annual release.
"""
import argparse,difflib,hashlib,io,json,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops
from link_106_c14_20_existing_webp_drafts import db_rebuild
from audit_105_115_sqlite_readonly import audit_year
ROOT=Path(__file__).resolve().parents[1]
BASE="sudu/data/processed/106/"
SRC="sudu/data/original/106/00-C/p004-93b8ec6eb3-v2-w1400-q66.webp"
SRC_SHA="b7e6a32272b74c7788caa1f413919b46359589162096f72afe1050c56a4e8bc4"
SRC_BLOB="b325a5fa1ec5073151077503de87929f3681130e"
PDF_SHA="93b8ec6eb319c8c7f5350ffa6267a2b4aed2f7acb1d1a2a7ca89e38f69ec5476"
EVIDENCE=BASE+"qa-drafts/TEXT_QA_106_C16_17_19_ORIGINAL_IMAGE_20261024.json"
TEXT={
16:("「齊其聞之矣」意謂馮諼想讓齊王明白什麼事？",
    ["孟嘗君跳槽恐有後患","孟嘗君果然見利忘義","孟嘗君重視豪奢享受","孟嘗君志在返國奪位"],
    "106-00-C-SHARED-15-16"),
17:("依據上文，友人認為作者能享庭園之樂，主要原因在於：",
    ["怡然自得，不役於物","花開四季，群賢畢至","簞食瓢飲，有志於學","遠離紅塵，遺世獨立"],
    "106-00-C-SHARED-17-18"),
19:("依據右圖，下列敘述何者正確？",
    ["鯊魚體內環境毒素多，唯魚鰭毒稀而可食","鯊魚長壽且繁殖力強，但敵不過人類濫捕",
     "鯊魚割鰭後行動遲緩，故攻擊力不及鱷魚","鯊魚的物體辨識力差，並非專嗜人類獵食"],
    "106-00-C-SHARED-19-20")
}
def at(rel):
    x=(ROOT/rel).resolve()
    assert x.is_relative_to(ROOT.resolve())
    return x
def read(rel):return json.loads(at(rel).read_text(encoding="utf8"))
def write(rel,obj):at(rel).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def sha(data):return hashlib.sha256(data).hexdigest()
def idx(items,key="questionId"):
    v={x[key]:x for x in items}; assert len(v)==len(items)
    return v
def main(stage):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="qa/114-115-official-visual-review"
    names=("questions.json","ocr-raw-candidates.json","webp-manifest.json",
        "VISUAL_QA.json","inventory.json","VALIDATION.json","release-manifest.json")
    d={p:read(BASE+p) for p in names}
    b=d["questions.json"];o=d["ocr-raw-candidates.json"];m=d["webp-manifest.json"]
    v=d["VISUAL_QA.json"];inv=d["inventory.json"];val=d["VALIDATION.json"]
    rel=d["release-manifest.json"]
    assert len(b["questions"])==len(o["items"])==len(m["items"])==len(v["items"])==204
    assert inv["visualQaPass"]==v["passCount"]==val["imageVisualQaPass"]==23
    assert inv["answerOfficialFinalVerified"]==val["answerOfficialFinalVerified"]==0
    assert inv["sharedMaterialsVerified"]==4 and len(m["sharedMaterialCrops"])==4
    assert not rel["releaseAllowed"] and not rel["integrationReady"]
    assert not val["releaseAllowed"] and not val["integrationReady"]
    qs=idx(b["questions"]);oo=idx(o["items"]);im=idx(m["items"]);vs=idx(v["items"])
    ss=idx(m["sharedMaterialCrops"],"sharedMaterialId")
    existing={n for n in TEXT if qs[f"106-00-C-{n:02d}"]["questionVerified"]}
    assert existing in (set(),set(TEXT)),"Partial concurrent G2 change"
    assert inv["ocrTextIndependentlyVerified"]==val["ocrTextVerified"]==10+len(existing)
    src_bytes=at(SRC).read_bytes()
    assert sha(src_bytes)==SRC_SHA
    assert hashlib.sha1(b"blob "+str(len(src_bytes)).encode()+b"\x00"+src_bytes).hexdigest()==SRC_BLOB
    now=datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    proof=[]
    with Image.open(io.BytesIO(src_bytes)) as page:
        page.load()
        assert page.format=="WEBP" and page.size==(1400,1980)
        for n,(stem,options,shared_id) in TEXT.items():
            id=f"106-00-C-{n:02d}"
            q=qs[id];ocr=oo[id];img=im[id]
            assert q["imageQaStatus"]==img["qaStatus"]==vs[id]["status"]=="PASS"
            assert shared_id in q["sharedMaterialIds"] and ss[shared_id]["qaStatus"]=="PASS"
            assert img["source"]==SRC and img["sourcePageWebpSha256"]==SRC_SHA
            assert img["officialQuestionPdfSha256"]==PDF_SHA
            assert q["assets"]["sha256"]==img["outputSha256"]==ocr["imageSha256"]
            assert img["visualReviewEvidence"]["reviewedSha256"]==img["outputSha256"]
            assert q["answerVerified"] is False and q["integrationReady"] is False
            assert ocr["rawOcrText"] is None
            raw=at(img["output"]).read_bytes()
            assert sha(raw)==img["outputSha256"]
            box=img["cropPixels"]
            with Image.open(io.BytesIO(raw)) as crop:
                crop.load()
                assert crop.format=="WEBP" and crop.size==(box[2]-box[0],box[3]-box[1])
                assert ImageChops.difference(page.crop(tuple(box)).convert("RGB"),crop.convert("RGB")).getbbox() is None
            assert len(options)==4 and all(x.strip() for x in options)
            legacy=ocr["legacyQuestion"];legacy_ops=ocr["legacyOptions"]
            diff="".join(difflib.unified_diff(
                [legacy+"\n"]+[x+"\n" for x in legacy_ops],
                [stem+"\n"]+[x+"\n" for x in options],
                fromfile="legacy-PDF-layer-and-placeholder",tofile="original-pixel-text-corrected"))
            assert diff
            proof.append({"questionId":id,"sourcePage":4,"source":SRC,
                "sourcePageSha256":SRC_SHA,"sourceGitBlob":SRC_BLOB,
                "officialPdfSha256FromExistingRepo":PDF_SHA,
                "cropPixels":box,"currentWebp":img["output"],"currentWebpSha256":img["outputSha256"],
                "sharedMaterialId":shared_id,"sharedWebpSha256":ss[shared_id]["outputSha256"],
                "rawOcrText":None,"rawOcrNeverFabricated":True,
                "legacyQuestion":legacy,"legacyOptions":legacy_ops,
                "correctedQuestion":stem,"correctedOptions":options,
                "unifiedDiff":diff,"result":"PASS_DIRECT_SOURCE_IMAGE_TEXT_WITH_SHARED"})
            if existing:
                assert q["question"]==stem and q["options"]==options
                assert ocr["correctedQuestion"]==stem and ocr["correctedOptions"]==options
            elif stage:
                q["legacyUnverifiedQuestion"]=q["question"];q["legacyUnverifiedOptions"]=q["options"]
                q.update({"question":stem,"options":options,"questionVerified":True,
                          "ocrStatus":"PASS_REVIEWED_ORIGINAL_PAGE_IMAGE",
                          "textQaStatus":"PASS","textQaEvidence":EVIDENCE})
                ocr.update({"correctedQuestion":stem,"correctedOptions":options,
                            "diff":diff,"qaStatus":"PASS","qaReviewer":"ChatGPT assistant",
                            "qaReviewedAt":now,"qaEvidencePath":EVIDENCE})
    if existing:
        assert at(EVIDENCE).is_file()
        print(json.dumps({"mode":"IDEMPOTENT","G2":13,"NO_RELEASE":True}))
        return
    if stage:
        inv["ocrTextIndependentlyVerified"]=inv["textQaPass"]=val["ocrTextVerified"]=13
        rel["questionTextQA"]="PARTIAL_13_OF_204"
        doc={"schemaVersion":1,"year":106,"paperCode":"00-C",
            "reviewedAt":now,"reviewer":"ChatGPT assistant","independentHumanReview":False,
            "method":"Source page4 and SHA-bound original-pixel question plus linked reading/artwork examined; preserve legacy/raw and diff",
            "originalTctePdfDownloadedAgain":False,"newG2Pass":3,"newG1Pass":0,
            "newOfficialFinalAnswerVerified":0,"releaseAllowed":False,
            "integrationReady":False,"records":proof}
        for name in names:write(BASE+name,d[name])
        write(EVIDENCE,doc)
        db_rebuild(b)
        g5="sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json"
        a=read(g5);results=[audit_year(y) for y in range(105,116)]
        assert all(x["g5Pass"] and x["sandboxImportPasses"]==2 for x in results)
        a.update({"years":results,"yearsG5Pass":11,"yearsReviewed":11,
                  "sourceDatabasesModified":True,"studentDataTouched":False,"released":False})
        write(g5,a)
    print(json.dumps({"mode":"STAGED" if stage else "CHECK","newTextG2":3,"yearG2":13,
                      "G1":23,"officialAnswerVerifiedAdded":0,"G5":11,"NO_RELEASE":True},ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stage",action="store_true")
    main(p.parse_args().stage)
