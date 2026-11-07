"""MASTER 114 E12 admission diagnosis: execute original publisher, never authorize release."""
import hashlib
import json
import subprocess
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import sudu_verified_publish as pub
from scripts import sudu_independent_review_gate as independent

QA_SHA = "682e02e1084325a0422c117d90b70451fdd9ea22"
B_SHA = "57d969888c57fdcd2b16c933e92c7a2c9eebb3a5"
QID = "114-00-E-12"
SRC = Path("_qa_source")
AUTHOR = Path("_author_b")
OUT = Path("_diagnostic_output")
EXPECTED_WEBP = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
EXPECTED_REV = "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
EXPECTED_G2 = "8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc"
EXPECTED_G3 = "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"
G2 = "sudu/data/processed/114/review-evidence/114-00-E-12-ocr-publisher-20261107.json"
G3 = "sudu/data/processed/114/review-evidence/114-00-E-12-official-publisher-20261107.json"
B_FILE = "sudu/teaching-candidates/114-role-b-20261025-batch02/114-00-E-12.json"

def emit(gate, ok, *, reason="", field="", path="", sha="", owner=""):
    print(json.dumps({"qid": QID,"gate": gate,"pass": bool(ok), "reason": reason,
                      "field": field,"path": path,"sha": sha,"responsible": owner},ensure_ascii=False),flush=True)

def rev(path):
    return subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()

assert rev(SRC) == QA_SHA, "QA source moved: pin mismatch"
assert rev(AUTHOR) == B_SHA, "B lesson moved: pin mismatch"
bank = pub.read(SRC / "sudu/data/processed/114/questions.json")
manifest = pub.read(SRC / "sudu/data/processed/114/webp-manifest.json")
inventory = pub.read(SRC / "sudu/data/processed/114/inventory.json")
qs = bank["questions"]
items = manifest["items"]
q = next(x for x in qs if x.get("questionId")==QID)
item = next(x for x in items if x.get("questionId")==QID)
shared = {x["sharedMaterialId"]:x for x in manifest.get("sharedMaterialCrops",[])}
revision = pub.text_revision(q,item["sha256"])
assert len(qs)==len(items)==205 and len({x["questionId"] for x in qs})==205
emit("G0_bank_sqlite",bool(inventory.get("sqlite",{}).get("roundtripPass")) and inventory.get("sqlite",{}).get("rows")==205,
     field="inventory.sqlite",path="sudu/data/processed/114/inventory.json",owner="A")
emit("G1_image_exact",pub.image_proof(q,item,shared,SRC) and pub.verify_bytes(SRC,item["output"],EXPECTED_WEBP),
     field="manifest.sha256 + imageQaStatus",path=item["output"],sha=EXPECTED_WEBP,owner="A")
emit("G1_visual_certificate",pub.visual_certificate(SRC,item,QID),
     field="visualReviewEvidence.referenceSha256",path=item["visualReviewEvidence"]["reference"],
     sha=item["visualReviewEvidence"].get("referenceSha256"),owner="A")
emit("G2_source_revision",revision==EXPECTED_REV and q.get("questionVerified") is True,
     field="questionVerified + text_revision",path="sudu/data/processed/114/questions.json",
     sha=revision,owner="A")
ocr_ok, official_ok = pub.source_proof(q,True,True,revision)
emit("G2_source_text_ocr",ocr_ok,field="textQaEvidence + questionVerified",
     path="sudu/data/processed/114/questions.json",owner="A")
emit("G3_source_answer",official_ok,field="officialFinalQaEvidence + answerVerified",
     path="sudu/data/processed/114/questions.json",owner="A")
g2 = pub.review_document(SRC,114,G2,QID)
g3 = pub.review_document(SRC,114,G3,QID)
emit("G2_issuer_document",bool(g2 and g2[1]==EXPECTED_G2 and g2[0].get("questionRevision")==EXPECTED_REV),
     field="evidence.ocr",path=G2,sha=(g2[1] if g2 else ""),owner="A / MASTER")
emit("G3_issuer_official_document",bool(g3 and g3[1]==EXPECTED_G3 and pub.official_notice_scope_certified(SRC,114,q,g3[0])),
     field="evidence.official",path=G3,sha=(g3[1] if g3 else ""),owner="A / MASTER")
audit = pub.reviewed_student_batches(SRC,114).get(QID)
emit("G4_review_batch",audit is not None,reason="verified-student-batch.json absent or QID not admitted" if audit is None else "",
     field="verified-student-batch.items[questionId]",path="sudu/data/processed/114/verified-student-batch.json",owner="MASTER")
lesson=pub.read(AUTHOR / B_FILE)
canonical_digest=independent.digest(independent.canonical(lesson["teaching"]))
emit("G5_B_lesson_frozen",lesson.get("teachingCanonicalSha256")==canonical_digest and
     lesson.get("composedTeachingSha256")=="fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4",
     field="teachingCanonicalSha256",path=B_FILE,sha=canonical_digest,owner="B")
emit("G5_issuer_teaching",bool(audit and (audit.get("evidence") or {}).get("teaching") and
     pub.review_document(SRC,114,audit["evidence"]["teaching"],QID)),
     reason="missing formal SHA-bound teaching issuer JSON" if not audit else "",
     field="evidence.teaching",path="sudu/data/processed/114/review-evidence/",owner="B / MASTER")
solver=pub.independently_solved(q,revision)
emit("G6_blind_solve",solver=="matched",reason="no verified blind solve; historical E saw answer" if solver!="matched" else "",
     field="independentSolve + evidence.blind",path="sudu/data/processed/114/verified-student-batch.json",
     owner="independent blind solver / E")
policy=independent.policy_from_trusted_main()
emit("G7_protected_trusted_E",bool(policy and QID in (policy.get("trustedAiReviewReceipts") or {})),
     reason="trustedAiReviewReceipts has no E12 entry" if policy and QID not in (policy.get("trustedAiReviewReceipts") or {}) else "",
     field="trustedAiReviewReceipts."+QID,path="sudu/release-governance/independent-review-policy.json",owner="independent E + MASTER")
teaching_doc={"questionRevision":revision,"content":lesson["teaching"]}
authorized,reason=independent.certified(SRC,audit,q,item,teaching_doc,
    (AUTHOR / B_FILE).read_bytes(),policy=policy)
emit("G7_independent_review_gate",authorized,reason=reason,
     field="reviewerSessionId/sourceAuthorSessionId, evidenceGitBlobSha, Issue36 RETURN",
     path="scripts/sudu_independent_review_gate.py",owner="E + MASTER")
emit("G8_formal_emitted_16of16",bool(audit and (audit.get("evidence") or {}).get("ui") and
     pub.review_document(SRC,114,audit["evidence"]["ui"],QID)),
     reason="real same-SHA emitted browser 8x2 positive evidence unavailable",
     field="evidence.ui, testedQuestionRevision, testedTeachingDigest",
     path="sudu/data/processed/114/review-evidence/",owner="D")
emit("G9_full_QA_certificates",pub.certificates_complete(SRC,q,item,shared),
     field="SHA-bound original+OCR+answer+blind+teaching+UI",path="sudu/data/processed/114/",owner="A/B/E/D")
final_ok,final_reason=pub.final_review_authorized(SRC,q,item,audit,revision)
emit("G9_final_admission",final_ok,reason=final_reason,
     field="studentReleaseApproved / final_review_authorized",path="scripts/sudu_verified_publish.py",owner="MASTER")
report=pub.stage(SRC,OUT,QA_SHA)
pub.site_check(OUT)
approved_114=pub.read(OUT/"sudu/data/approved/114.json")
approved_115=pub.read(OUT/"sudu/data/approved/115.json")
e12_live=any(x.get("canonicalId")==QID for x in approved_114["questions"])
emit("G10_publisher_actual_stage",not e12_live,reason="expected genuine HOLD; no E12 in approved output",
     field="approved/114.json.questions",path="_diagnostic_output/sudu/data/approved/114.json",owner="MASTER")
print(json.dumps({"status":"EXPECTED_FAIL_CLOSED_NOT_LIVE","qaSourceSha":QA_SHA,
    "authorSha":B_SHA,"publisherSha256":pub.digest(Path("scripts/sudu_verified_publish.py").read_bytes()),
    "approved114":report["years"]["114"]["approvedCount"],"approved115":report["years"]["115"]["approvedCount"],
    "e12Allowed":e12_live,"snapshotReason":next((x for x in report["years"]["114"]["pendingReasonCounts"]),""),
    "policy":policy.get("reviewMode") if policy else None,
    "trustedE12":bool(policy and QID in (policy.get("trustedAiReviewReceipts") or {}))},
    ensure_ascii=False),flush=True)
assert not e12_live, "Unexpected E12 admission; investigate immediately"
assert approved_114["approvedCount"]==0 and approved_115["approvedCount"]==5
