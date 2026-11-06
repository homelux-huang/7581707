#!/usr/bin/env python3
"""108 Math B 11-15: direct original-page text QA, never official-final G3 or release.

Manual transcription was made by a separate assistant session with the original
TCTE-derived page-3 raster and five exact single-question WebPs visibly open.
Preserve raw OCR provenance (none), original placeholders, SHA and unified diff.
No new G1/image PASS claim: all 5 source images already had G1 PASS on input.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import io
import json
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageChops
from stage_108_all_26_missing_original_page_webps import db_rebuild
from audit_105_115_sqlite_readonly import audit_year

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "qa/114-115-official-visual-review"
BASE = "sudu/data/processed/108/"
PAGE = "sudu/data/original/108/00-MB/p003-bcda540c72-v2-w1400-q66.webp"
PAGE_GIT_BLOB = "98769b8e7b656bde3abd55264667ef60c876ec7d"
PAGE_SHA256 = "3599ba878ebce5fa685c590b1872ff74a1019d4c8f750e64978294969651f585"
SOURCE_PDF_SHA = "bcda540c72f5d88f400aed994d58496e66761466aa5438e54d156c773b25722c"
EVIDENCE = BASE + "qa-drafts/TEXT_QA_108_MATH_B11_15_ORIGINAL_IMAGE_20261024.json"

# The four choices remain positional A, B, C, D. Fraction notation is
# rendered in the original single-question WebP as the authoritative fallback.
TEXT = {
    11: (
        "一顆雞蛋從生產到運送至超市販售，所需的成本為4元，在超市的售價為5元，其獲利由蛋農與超市平分；但運送過程中破裂或超過保存期限等因素，超市會將雞蛋銷毀，雞蛋即無法成功銷售，超市亦不付蛋農任何款項。若一顆雞蛋無法成功銷售的機率為0.006，則蛋農一顆雞蛋之獲利的期望值為多少元？",
        ["0.473", "0.5", "0.967", "0.97"],
        "A", [90, 169, 1310, 351],
        "84f81cbb1674801ce9fc16b15771eb938f38b8c000f9e9cfbbb08e068ab37993",
    ),
    12: (
        "在理想環境下，將一球自離地面30公尺處垂直落下，球只會上下垂直來回彈跳。若每次反彈高度為前一次高度的2/5，則此球靜止前所經過的路程為多少公尺？",
        ["50", "60", "70", "80"],
        "C", [90, 352, 1310, 524],
        "01a04ced7ea78bae93dffbbcd61b50bb098820922c139a5c9d6cfec580c709bc",
    ),
    13: (
        "某校校長想知道全校學生贊成取消早自習的比例p，並將p在95%的信心水準下之信賴區間簡稱95%信賴區間，現從所有學生中隨機抽取樣本數為36的一組樣本，利用這36位學生的意見求得p之95%信賴區間為[0.642,0.914]。若學生對早自習是否取消的意見是固定不變的，則下列何者為正確解讀？",
        [
            "該校約有95%的學生贊成取消早自習",
            "p落在64.2%與91.4%之間的機率為95%",
            "若進行1000次抽樣調查，每次皆隨機抽取樣本數為36的一組樣本，共可算得1000個p之95%信賴區間，其中約有950個區間會包含p",
            "若進行1000次抽樣調查，每次皆隨機抽取樣本數為36的一組樣本，共可算得1000個學生贊成取消早自習的樣本比例，其中約有950個會落在64.2%與91.4%之間",
        ],
        "C", [90, 525, 1310, 918],
        "2b4b72f7b08e0ed7d64483001315b01df29982009498f51f173944a9aa1f837e",
    ),
    14: (
        "若拋物線y=ax²+b之開口向上且與x軸沒有交點，則下列敘述何者正確？",
        ["a>0，b>0", "a>0，b<0", "a<0，b>0", "a<0，b<0"],
        "A", [90, 919, 1310, 1060],
        "4e488da14604b8b00158c3825fb404ad03f70f862834f1ebdb26a59b4976e188",
    ),
    15: (
        "已知直線L₁為y=m₁x、直線L₂為y=m₂x。若m₁、m₂的值皆為2、1/2或−1/2三種數字之一，彼此取值互為獨立，且三種數字出現的機率相同，則L₁和L₂相互垂直的機率為何？",
        ["4/9", "1/3", "2/9", "1/9"],
        "C", [90, 1061, 1310, 1248],
        "ea6e4129de7bdcd929549adf2d769c4a4b04bf3b86de02bf1216d1248da01ee9",
    ),
}
PLACEHOLDER = "本題原卷文字、圖表或公式尚未成功擷取，請點選原始 PDF 對照，不能把此提示當作正式題幹。"


def at(relative: str) -> Path:
    p = (ROOT / relative).resolve()
    assert p.is_relative_to(ROOT.resolve())
    return p


def load(relative: str):
    return json.loads(at(relative).read_text(encoding="utf-8"))


def save(relative: str, value):
    at(relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def index(items):
    result = {row["questionId"]: row for row in items}
    assert len(result) == len(items)
    return result


def check_image(page, page_raw, m, num, coords, expected_sha):
    assert m["questionId"] == f"108-00-MB-{num:02d}"
    assert m["qaStatus"] == "PASS", "G2 may not grant image G1"
    assert m["sourcePage"] == 3 and m["source"] == PAGE
    assert m["officialQuestionPdfSha256"] == SOURCE_PDF_SHA
    assert m["sourcePageWebpSha256"] == sha(page_raw) == PAGE_SHA256
    assert m["cropPixels"] == coords
    assert m["outputSha256"] == expected_sha
    proof = m["visualReviewEvidence"]
    assert proof["reviewedSha256"] == expected_sha
    assert proof["independentHumanReview"] is False, "Do not relabel historical AI as human"
    data = at(m["output"]).read_bytes()
    assert sha(data) == expected_sha
    with Image.open(io.BytesIO(data)) as crop:
        crop.load()
        assert crop.size == (coords[2]-coords[0], coords[3]-coords[1])
        assert ImageChops.difference(
            page.crop(tuple(coords)).convert("RGB"), crop.convert("RGB")
        ).getbbox() is None
    return m["output"]


def execute(stage: bool):
    assert subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == BRANCH
    names = ["questions.json", "ocr-raw-candidates.json", "webp-manifest.json",
             "VISUAL_QA.json", "inventory.json", "VALIDATION.json", "release-manifest.json"]
    data = {name: load(BASE+name) for name in names}
    bank, ocr, manifest = (data["questions.json"], data["ocr-raw-candidates.json"],
                           data["webp-manifest.json"])
    visual, inventory = data["VISUAL_QA.json"], data["inventory.json"]
    validation, release = data["VALIDATION.json"], data["release-manifest.json"]
    assert len(bank["questions"]) == len(ocr["items"]) == len(manifest["items"]) == len(visual["items"]) == 204
    assert inventory["webpGeneratedDrafts"] == 204
    assert inventory["visualQaPass"] == validation["imageVisualQaPass"] == visual["passCount"] == 26
    assert inventory["answerOfficialFinalVerified"] == validation["answerOfficialFinalVerified"] == 0
    assert release["releaseAllowed"] is False and release["integrationReady"] is False
    assert validation["releaseAllowed"] is False and validation["integrationReady"] is False
    rows, ocr_rows, images, vis = map(index, [bank["questions"], ocr["items"], manifest["items"], visual["items"]])
    assert set(rows) == set(ocr_rows) == set(images) == set(vis)
    assert set(TEXT) == {11, 12, 13, 14, 15}

    page_raw = at(PAGE).read_bytes()
    assert sha(page_raw) == PAGE_SHA256
    git_blob = hashlib.sha1(b"blob "+str(len(page_raw)).encode()+b"\0"+page_raw).hexdigest()
    assert git_blob == PAGE_GIT_BLOB
    existing = {num for num in TEXT if rows[f"108-00-MB-{num:02d}"].get("textQaStatus") == "PASS"}
    assert existing in (set(), set(TEXT)), "Partial candidate / concurrent edits must be reviewed"
    assert inventory["ocrTextIndependentlyVerified"] == validation["ocrTextVerified"] == len(existing)
    assert not any(q["answerVerified"] or q["integrationReady"] for q in bank["questions"])
    records = []
    now = datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds")
    with Image.open(io.BytesIO(page_raw)) as page:
        page.load()
        assert page.size == (1400, 1980) and page.format == "WEBP"
        for num, (stem, options, original_answer_candidate, coords, expected_sha) in TEXT.items():
            ident = f"108-00-MB-{num:02d}"
            q, o, m = rows[ident], ocr_rows[ident], images[ident]
            output = check_image(page, page_raw, m, num, coords, expected_sha)
            assert q["imageQaStatus"] == vis[ident]["status"] == "PASS"
            assert q["assets"]["sha256"] == expected_sha == o["imageSha256"]
            assert q["answer"] == original_answer_candidate and q["answerMatched"] is True
            assert q["answerVerified"] is False and q["integrationReady"] is False
            assert o["rawOcrText"] is None, "Never synthesize OCR raw output"
            assert len(options) == 4 and all(v.strip() for v in options)
            old_stem, old_options = o["legacyQuestion"], o["legacyOptions"]
            assert old_stem == PLACEHOLDER and old_options == []
            unified = "".join(difflib.unified_diff(
                ([old_stem+"\n"] + [x+"\n" for x in old_options]),
                ([stem+"\n"] + [x+"\n" for x in options]),
                fromfile="legacy-placeholders-preserved", tofile="direct-image-reviewed-text",
            ))
            assert unified and old_stem not in stem
            rec = {
                "questionId": ident, "originalPageNumber": 3, "sourcePageWebp": PAGE,
                "sourcePageWebpSha256": PAGE_SHA256, "sourcePageGitBlob": PAGE_GIT_BLOB,
                "originalQuestionPdfSha256Claim": SOURCE_PDF_SHA,
                "cropPixels": coords, "singleQuestionWebp": output, "singleQuestionWebpSha256": expected_sha,
                "sourcePixelDifferenceZero": True,
                "rawOcrText": None, "rawOcrNeverFabricated": True,
                "originalLegacyQuestion": old_stem, "originalLegacyOptions": old_options,
                "correctedQuestion": stem, "correctedOptions": options, "unifiedDiff": unified,
                "status": "PASS_DIRECT_IMAGE_TEXT_REVIEW",
                "officialFinalAnswerVerified": False, "questionNumberAndFourOptionsDirectlyCompared": True,
            }
            records.append(rec)
            if existing:
                assert q["question"] == stem and q["options"] == options
                assert o["correctedQuestion"] == stem and o["correctedOptions"] == options
                assert q["questionVerified"] is True and o["qaStatus"] == "PASS"
            elif stage:
                assert q["question"] == PLACEHOLDER and q["options"] == []
                q["legacyUnverifiedQuestion"] = q["question"]
                q["legacyUnverifiedOptions"] = q["options"]
                q["legacyUnverifiedIssues"] = list(q.get("issues", []))
                q.update({
                    "question": stem, "options": options, "ocrStatus": "PASS_REVIEWED_ORIGINAL_PAGE_IMAGE",
                    "textQaStatus": "PASS", "textQaEvidence": EVIDENCE,
                    "questionVerified": True
                })
                # Preserve original OCR status and raw (not acquired), do not spoof Tesseract.
                o.update({
                    "correctedQuestion": stem, "correctedOptions": options,
                    "diff": unified, "qaStatus": "PASS", "qaReviewer": "ChatGPT assistant",
                    "qaReviewedAt": now, "qaEvidencePath": EVIDENCE,
                    "imageSha256": expected_sha
                })
    if existing:
        assert at(EVIDENCE).is_file()
        print(json.dumps({"mode":"IDEMPOTENT", "newG2":0, "existingG2":5, "newG1":0, "newG3":0, "NO_RELEASE":True}))
        return

    payload = {
        "schemaVersion":1, "year":108, "paperCode":"00-MB",
        "reviewer":"ChatGPT assistant", "independentHumanReview":False,
        "reviewedAt":now,
        "method":"Visible assistant reading of immutable official-source page3 raster and each exact single-question WebP; pixel SHA check executed by CI",
        "sourcePdfBytesIndependentlyDownloadedThisRun":False,
        "officialFinalAnswersIndependentlyVerifiedThisRun":0,
        "newTextQaPass":5, "newImageQaPass":0, "originalPagePixelSha256":PAGE_SHA256,
        "g2RequiresOriginalWebpWhenMathNotationLosesTypesetting":True,
        "preserveHistoricalRawOcr":True,
        "questionsStillBlockedForOfficialFinalAnswer":True,
        "releaseAllowed":False, "integrationReady":False,
        "records":records
    }
    if stage:
        inventory["ocrTextIndependentlyVerified"] = 5
        inventory["textQaPass"] = 5
        validation["ocrTextVerified"] = 5
        release["questionTextQA"] = "PARTIAL_5_OF_204"
        for name in names:
            save(BASE+name, data[name])
        save(EVIDENCE, payload)
        db_rebuild(bank)
        report = load("sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json")
        years = [audit_year(y) for y in range(105,116)]
        assert len(years) == 11 and all(x["g5Pass"] and x["sandboxImportPasses"] == 2 for x in years)
        report.update({"years":years, "yearsG5Pass":11, "yearsReviewed":11,
                       "sourceDatabasesModified":True, "studentDataTouched":False, "released":False})
        save("sudu/data/processed/105-115-SQLITE_G5_READONLY_AUDIT.json", report)
    print(json.dumps({"mode":"STAGED" if stage else "CHECK", "year":108, "questionIds":[r["questionId"] for r in records],
                      "newG2":5, "year108G1Unchanged":26, "newOfficialFinalVerified":0,
                      "g5YearsRequired":11, "integrationReady":False, "releaseAllowed":False},
                      ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    execute(args.stage)
