#!/usr/bin/env python3
"""Stage ONLY genuine MB05 student content from canonical source and reviewed draft.

Build through the formal publisher's public_question mapper, without modifying
approved data, releasing flags, or substituting hand-authored question fixtures.
"""
import hashlib
import importlib.util
import json
import subprocess
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
WORKSPACE=HERE.parent
SRC=WORKSPACE/"current-qa-source"
MAIN=WORKSPACE/"current-main"
BASE=SRC/"sudu/data/processed/115"
OUT=WORKSPACE/"mb05-stage"
OUT.mkdir(exist_ok=True)
QID="115-00-MB-05"

def sha(x): return hashlib.sha256(x).hexdigest()
def canonical(x): return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def head(p): return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True).strip()

assert head(SRC)=="aad909a726a201e2841b86b2c35634e5d5f4afe5","source QA changed; repin and re-review"
bank=load(BASE/"questions.json")
q=next(x for x in bank["questions"] if x["questionId"]==QID)
manifest=load(BASE/"webp-manifest.json")
item=next(x for x in manifest["items"] if x["questionId"]==QID)
corrected=load(BASE/"review-evidence/115-00-MB-05-source-text-applied-20261024.json")
blind=load(BASE/"review-evidence/115-00-MB-05-blind-original-20261024.json")
official=load(BASE/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json")
reply=next(x for x in official["records"] if x["questionId"]==QID)
assert q["question"]==corrected["correctedText"]["question"]==blind["sourceQuestionTranscriptionFromImage"]
assert q["options"]==corrected["correctedText"]["options"]==blind["sourceOptionsFromImage"]
assert q["answer"]==blind["answer"]==reply["officialFinalAnswerReadDirectlyFromPublishedImage"]=="B"
assert reply["qaStatus"]=="PASS_DIRECT_VISUAL_AND_NO_OFFICIAL_OBJECTION"
assert item["qaStatus"]=="PASS"
original=SRC/item["output"]
asset=HERE/f"sudu/data/approved/webp/115/{QID}.webp"
liveasset=MAIN/f"sudu/data/approved/webp/115/{QID}.webp"
for path in (original,asset,liveasset):
 assert path.is_file() and sha(path.read_bytes())==item["sha256"],f"{path} original WebP changed"
review=load(HERE/f"sudu/teaching-drafts/preview-128-20261023/{QID}-pedagogy-review-20261024.json")
assert review["correctAnswer"]==q["answer"]=="B"
assert review["sourceImageSha256"]==item["sha256"]
assert review["studentReleaseApproved"] is False and review["deploy"] is False
assert review["teachingQaStatus"]=="AI_CONTENT_REVIEW_PASS_NOT_RELEASE_CERTIFICATE"
assert review["uiQaStatus"]=="PENDING"
options=review["optionExplanations"]
assert list(options)==list("ABCD")
assert [key for key in "ABCD" if options[key]["isCorrect"]] == ["B"]
for letter in "ABCD":
 assert all(options[letter].get(k) for k in ("teacher","elementary","reason"))
calc=review["examCalculation"]
assert calc["option"]=="B" and calc["result"]=="(3/2,-7/2)"
A=(-1,0);B=(0,-5);D=(2,3)
C=(B[0]+D[0]-A[0],B[1]+D[1]-A[1])
M=(Fraction(B[0]+C[0],2),Fraction(B[1]+C[1],2))
assert C==(3,-2) and M==(Fraction(3,2),Fraction(-7,2))
assert len(calc["steps"])>=5 and len(calc["substitution"])>=3 and len(calc["given"])>=3
teaching={
 "topic":"平行四邊形｜中點座標",
 "teacherSummary":review["teacherSummary"],"elementarySummary":review["elementarySummary"],
 "memory":review["memory"],"concept":review["concept"],"extension":review["extension"],
 "source":review["source"],"formula":calc["formulaUse"],
 "optionExplanations":options,"calculationReviewed":True,"hasExamCalculation":True,
 "examCalculation":{k:calc[k] for k in ("given","formulaUse","substitution","steps","result","option","unit")},
 "highlights":review["highlights"]
}
spec=importlib.util.spec_from_file_location("publisher",MAIN/"scripts/sudu_verified_publish.py")
pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
revision=pub.text_revision(q,item["sha256"])
assert revision=="3b0a4236f9298edd225b445592faee3b222c8ecfc1b62425278a0de576cc1df9"
assert pub.image_proof(q,item,{},SRC)
assert pub.teaching_complete({**q,"teaching":teaching,"teachingQaStatus":"PASS","uiQaStatus":"PASS",
 "studentReleaseApproved":True,"teachingQaEvidence":{"reviewer":"GPT-6 source checked","reviewedAt":"2026-10-24",
 "evidencePath":"sudu/data/processed/115/review-evidence/115-00-MB-05-teaching.json",
 "allFourOptionsReviewed":True,"calculationReviewed":True}}, "數學 B","B")
payload=pub.public_question({**q,"teaching":teaching,"officialFinalAnswer":"B"},115,"數學 B",
 f"data/approved/webp/115/{QID}.webp")
result={"schemaVersion":1,"year":115,"approvedCount":1,"expected":205,"questions":[payload],
 "QA_ONLY_UNPUBLISHABLE":True}
(OUT/"115.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
note={"questionId":QID,"sourceQaCommit":head(SRC),"publisherCommit":head(MAIN),
 "draftCommit":head(HERE),"originalWebpSha256":item["sha256"],
 "canonicalSourceRevisionSha256":revision,"teachingSha256":canonical(teaching),
 "sourceCorrectionEvidenceSha256":sha((BASE/"review-evidence/115-00-MB-05-source-text-applied-20261024.json").read_bytes()),
 "preKeyOriginalEvidenceSha256":sha((BASE/"review-evidence/115-00-MB-05-blind-original-20261024.json").read_bytes()),
 "officialSourceEvidenceSha256":sha((BASE/"QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json").read_bytes()),
 "sourceAdmissionYetApproved":False,"teachingStudentReleaseApproved":False,"browserValidationPending":True,
 "qaInputIsExactCanonicalSource":True,"qaOutputUsesActualPublisherMapper":True,"sourceImageFromOriginalWebp":True}
(OUT/"input-digests.json").write_text(json.dumps(note,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(note,ensure_ascii=False,sort_keys=True))
