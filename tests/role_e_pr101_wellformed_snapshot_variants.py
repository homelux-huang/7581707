#!/usr/bin/env python3
"""Independent Role E well-formed source-self-attestation full-snapshot attacks.

Extends ONLY the original synthetic test fixture in memory; does not edit the
original regression, production code, or any GitHub resource. No security
function is mocked. Every variant invokes the real 205-ID snapshot.
"""
import argparse
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--publisher', required=True)
parser.add_argument('--base-regression', required=True)
args = parser.parse_args()
base = Path(args.base_regression).resolve()
source = base.read_text(encoding='utf-8')
anchor = '        output = root / "output"'
assert source.count(anchor) == 1, 'independent base fixture drift'
extension = '''        # Source-author seals valid current raw teaching and UI documents.
        teaching_doc = {"schemaVersion": 1, "questionId": qid, "year": 115,
                        "questionRevision": revision, "content": q["teaching"]}
        teaching_path = root / "synthetic-complete-teaching.json"
        teaching_raw = json.dumps(teaching_doc, ensure_ascii=False).encode()
        teaching_path.write_bytes(teaching_raw)
        q["teachingQaEvidence"] = evidence(allFourOptionsReviewed=True, calculationReviewed=True)
        q["teachingQaEvidence"].update(evidencePath=teaching_path.name,
                                      evidenceSha256=v.digest(teaching_raw))
        ui_doc = {"questionId": qid, "year": 115, "testedQuestionRevision": revision,
                  "testedTeachingDigest": v.digest(json.dumps(q["teaching"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())}
        ui_path = root / "synthetic-complete-ui.json"
        ui_raw = json.dumps(ui_doc).encode(); ui_path.write_bytes(ui_raw)
        q["uiQaEvidence"] = evidence()
        q["uiQaEvidence"].update(evidencePath=ui_path.name,evidenceSha256=v.digest(ui_raw))
        # Critical: persist this strengthened input to the REAL source bank.
        # Mutating only q in memory would not strengthen snapshot's input.
        v.dump(source / "questions.json", {"questions": bank})
        persisted = next(row for row in v.read(source / "questions.json")["questions"]
                         if row["questionId"] == qid)
        assert persisted["teachingQaEvidence"]["evidenceSha256"] == v.digest(teaching_raw)
        assert persisted["uiQaEvidence"]["evidenceSha256"] == v.digest(ui_raw)
        variants = [
            ("absent_audit", None),
            ("empty_audit", {"questionId": qid}),
            ("invalid_audit", {"questionId": qid, "status": "INVALID"}),
            ("forged_approved_receipt", {"questionId": qid, "year": 115,
                "status": "STUDENT_QA_APPROVED", "questionBeforeReview": q["question"],
                "optionsBeforeReview": q["options"], "webpSha256": image_sha,
                "officialPdfSha256": "c"*64, "questionPdfSha256": "a"*64,
                "originalAnswerCandidate": "B",
                "independentAiContentEvidence":
                   "sudu/data/processed/115/review-evidence/FAKE.json"}),
        ]
        batch_path = source / "verified-student-batch.json"
        for label, audit in variants:
            if audit is None:
                batch_path.unlink(missing_ok=True)
            else:
                v.dump(batch_path, {"schemaVersion": 1, "year": 115, "items": [audit]})
            # Demonstrates rejection by the real empty trusted registry,
            # rather than malformed teaching or UI JSON.
            decision = v.final_review_authorized(root, persisted, image_item, audit, revision)
            assert decision == (False, "distinct_ai_content_review_missing"), (label, decision)
            variant_output = root / ("output-" + label)
            v.snapshot(root, variant_output, 115, "a"*40)
            variant_release = v.read(variant_output / "sudu/data/approved/115.json")
            print(json.dumps({"syntheticFixture": True, "variant": label,
                "wellFormedCurrentRawTeachingAndUi": True,
                "authorizationReason": decision[1],
                "admittedCount": variant_release["approvedCount"]}))
            assert variant_release["approvedCount"] == 0, (label, variant_release)
        output = root / "output"'''
source = source.replace(anchor, extension)
assert source.count('"reviewBatchExists": False,') == 1
source = source.replace('"reviewBatchExists": False,',
                        '"reviewBatchExists": batch_path.exists(),')
assert source.count('"testedTeachingDigest": None}') == 1
source = source.replace('"testedTeachingDigest": None}',
                        '"testedTeachingDigest": ui_doc["testedTeachingDigest"]}')
sys.argv = [str(base), '--publisher', str(Path(args.publisher).resolve())]
exec(compile(source, str(base) + ' [independent well-formed fixture extension]', 'exec'),
     {'__name__': '__main__', '__file__': str(base)})
