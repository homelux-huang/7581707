#!/usr/bin/env python3
"""Stage Econ34 exact canonical source and human-readable original WebP in V4, QA ONLY.

No release is conferred: builds public_question with a substantive *reviewed*
teaching candidate on the existing frozen production adapter and official data.
"""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
WORK=HERE.parent
SOURCE=WORK/"candidate"
MAIN=WORK/"current-main"
BASE=SOURCE/"sudu/data/processed/115"
OUT=WORK/"econ34-stage"
OUT.mkdir(exist_ok=True)
QID="115-09-2-34"
QSHA="162c9a4f4d16d25e77a6c09034eb87f9a27b1b5775ac334274f6447c3c957cc8"
WSHA="5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(buf): return hashlib.sha256(buf).hexdigest()
def objsha(o): return sha(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8"))
def commit(p): return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True).strip()

assert commit(MAIN)=="31adda6c3973ee73387c767d4a8ba56af1fd81b8"
bank=load(BASE/"questions.json")
q=next(x for x in bank["questions"] if x["questionId"]==QID)
item=next(x for x in load(BASE/"webp-manifest.json")["items"] if x["questionId"]==QID)
blind=load(BASE/"review-evidence/115-09-2-34-blind-original-20261024.json")
official=load(BASE/"review-evidence/115-09-2-34-official-visual-20261024.json")
review=load(BASE/"review-evidence/115-09-2-34-pedagogy-candidate-20261024.json")
corrections=load(BASE/"official-confirmation-status.json")
spec=importlib.util.spec_from_file_location("published",MAIN/"scripts/sudu_verified_publish.py")
pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
revision=pub.text_revision(q,item["sha256"])
assert revision==QSHA==review["canonicalQuestionRevisionSha256"]
assert q["questionId"]==blind["questionId"]==official["questionId"]==review["questionId"]
assert item["sha256"]==blind["originalWebpSha256"]==official["sourceOriginalQuestionWebpSha256"]==review["sourceImageSha256"]==WSHA
assert item["qaStatus"]=="PASS" and pub.visual_certificate(SOURCE,item,QID)
print("IMAGE_PROOF_DIAG",json.dumps({
 "imageProofWithNoShared":pub.image_proof(q,item,{},SOURCE),
 "individualImage":pub.individual_image_proof(q,item,SOURCE),
 "sharedIds":pub.shared_material_ids(q),
 "assets":q.get("assets"),"manifestFile":item.get("output"),
 "manifestImageSha":item.get("sha256"),
 "sourceOriginalSha":item.get("sourceSha256")
},ensure_ascii=False,sort_keys=True),flush=True)
assert pub.image_proof(q,item,{},SOURCE) and pub.certified_visual_assets(SOURCE,q,item,{})
assert q["question"].startswith("假設人工智慧") and "寡占市場中僅存在兩間廠商" in q["question"]
assert q["options"]==blind["sourceOptionsFromOriginalImage"]
assert q["answerMatched"] is True and q["answer"]==blind["answer"]==review["correctAnswer"]==official["officialFinalOptionReadVisually"]=="A"
assert blind["officialAnswerHiddenDuringSolve"] and blind["solvedWithoutOfficialAnswer"] and not blind["officialComparisonNotPerformedYet"] is False
assert blind["sourceImageOnlyNoKeyAtSolve"] and blind["sourceQuestionTranscriptionFromOriginalImage"]!=q["question"]
assert official["genuinePreKeyInitialSolveCommit"]=="33aa3228077d9cd7ad4ec2f59890d46013b976f7"
assert official["officialVisualCheckRunId"]==40086437762 and official["match"] is True
assert q["answerProvenance"]["pdfSha256"]==official["sourceAnswerPdfSha256"]
assert corrections["confirmations"]["09-2"]["revisionDocumentContent"]=="SHA_BOUND_OFFICIAL_PDF_ALL_PAGES_REVIEWED"
assert not official["question34MentionedInConfirm"]
assert q.get("questionVerified") is not True and q.get("answerVerified") is not True
assert QID not in pub.reviewed_student_batches(SOURCE,115)
for file in (SOURCE/item["output"],MAIN/f"sudu/data/approved/webp/115/{QID}.webp"):
 assert file.is_file() and sha(file.read_bytes())==WSHA, str(file)
teaching=review["teaching"]
assert review["teachingQaStatus"]=="AI_CONTENT_REVIEW_PASS_NOT_RELEASE_CERTIFICATE"
assert review["studentReleaseApproved"] is False and review["deploy"] is False
assert teaching["hasExamCalculation"] is False and teaching["examCalculation"] is None
assert teaching["calculationReviewed"] is True
assert set(teaching["optionExplanations"])==set("ABCD")
assert [k for k in "ABCD" if teaching["optionExplanations"][k]["isCorrect"]]==["A"]
for k in "ABCD":
 assert all(teaching["optionExplanations"][k][field] for field in ("teacher","elementary","reason"))
assert len(teaching["extra"]["解題判斷步驟"].split("\n"))>=4
temp={**q,"teaching":teaching,"teachingQaStatus":"PASS","uiQaStatus":"PASS",
 "studentReleaseApproved":True,"teachingQaEvidence":{"reviewer":review["reviewer"],"reviewedAt":review["reviewedAt"],
 "evidencePath":"sudu/data/processed/115/review-evidence/115-09-2-34-pedagogy-candidate-20261024.json",
 "allFourOptionsReviewed":True,"calculationReviewed":True}}
assert pub.teaching_complete(temp,"經濟學","A"),"positive curriculum/teaching gate must pass without bypass"
published=pub.public_question({**q,"teaching":teaching,"officialFinalAnswer":"A"},115,"經濟學",
 f"data/approved/webp/115/{QID}.webp")
out={"schemaVersion":1,"year":115,"approvedCount":1,"expected":205,
 "questions":[published],"QA_ONLY_UNPUBLISHABLE":True}
(OUT/"115.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
info={"questionId":QID,"sourceQaCommit":commit(SOURCE),"mainV4Commit":commit(MAIN),
 "canonicalSourceRevisionSha256":revision,"originalWebpSha256":WSHA,
 "teachingSha256":objsha(teaching),
 "preKeyInitialCommit":official["genuinePreKeyInitialSolveCommit"],
 "blindOriginalSha256":sha((BASE/"review-evidence/115-09-2-34-blind-original-20261024.json").read_bytes()),
 "officialAnswerVisualSha256":official["sourceAnswerPageWebpSha256"],
 "officialEvidenceSha256":sha((BASE/"review-evidence/115-09-2-34-official-visual-20261024.json").read_bytes()),
 "pedagogyCandidateSha256":sha((BASE/"review-evidence/115-09-2-34-pedagogy-candidate-20261024.json").read_bytes()),
 "noStudentAdmission":True,"uiValidationPending":True,"sourceAndOfficialCanonicalSource":True,
 "actualUnmodifiedPublicQuestionMapper":True}
(OUT/"input-digests.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ECON34_STAGED_SOURCE_TEACHING",json.dumps(info,ensure_ascii=False,sort_keys=True),flush=True)
