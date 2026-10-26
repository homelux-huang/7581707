#!/usr/bin/env python3
"""Independent Role E regression: source self-attestation must not admit a student.

Synthetic TEMPORARY 205-ID corpus only. No official question, genuine QA,
production mutation, human review or student release is represented here.
Run: python e-pr101-snapshot-bypass.py --publisher scripts/sudu_verified_publish.py
Vulnerable publisher prints admittedCount=1 then FAILS the final assertion.
Fixed publisher must produce zero admissions while preserving other assertions.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image


def reproduce(publisher_path):
    path = Path(publisher_path).resolve()
    sys.path.insert(0, str(path.parent.parent))
    spec = importlib.util.spec_from_file_location("role_e_publisher_under_audit", path)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    qid = "115-09-2-27"
    q = {
        "questionId": qid, "year": 115, "paperCode": "09-2",
        "originalQuestionNumber": 27, "subject": "經濟學",
        "question": "SYNTHETIC: two units cost thirty each; total?",
        "options": ["30", "60", "90", "120"], "answer": "B",
        "officialFinalAnswer": "B", "answerVerified": True,
        "officialCorrectionChecked": True, "questionVerified": True,
        "textQaStatus": "PASS", "teachingQaStatus": "PASS",
        "uiQaStatus": "PASS", "studentReleaseApproved": True,
        "questionProvenance": {"officialPdfSha256": "a" * 64,
                               "pixelSourceSha256": "b" * 64},
        "answerProvenance": {"officialPdfSha256": "c" * 64},
        "teaching": {
            "teacherSummary": "SYNTHETIC teacher-style explanation: multiply units by price",
            "elementarySummary": "SYNTHETIC simple explanation: add thirty twice",
            "memory": "SYNTHETIC unit price times quantity",
            "concept": "SYNTHETIC multiplication",
            "extension": "SYNTHETIC repeated addition",
            "source": "SYNTHETIC source, not a textbook or official evidence",
            "optionExplanations": {
                letter: {"teacher": "SYNTHETIC option explanation " + letter,
                         "elementary": "SYNTHETIC easy explanation " + letter,
                         "reason": "SYNTHETIC reason " + letter}
                for letter in "ABCD"
            },
            "calculationReviewed": True, "hasExamCalculation": True,
            "examCalculation": {"given": ["2 units", "30 each"],
                                "formulaUse": "SYNTHETIC total = price times quantity",
                                "substitution": ["30 * 2"], "steps": ["30 + 30 = 60"],
                                "result": "60", "unit": "SYNTHETIC units", "option": "B"},
        },
    }
    with tempfile.TemporaryDirectory(prefix="role-e-synthetic-snapshot-") as temporary:
        root = Path(temporary)
        source = root / "sudu/data/processed/115"
        source.mkdir(parents=True)
        image_relative = "sudu/data/processed/115/webp-v2/09-2/" + qid + ".webp"
        image_path = root / image_relative
        image_path.parent.mkdir(parents=True)
        Image.new("RGB", (100, 60), "white").save(image_path, "WEBP")
        image_sha = hashlib.sha256(image_path.read_bytes()).hexdigest()
        q["assets"] = {"singleQuestionWebp": image_relative, "sha256": image_sha}
        q["questionProvenance"]["webpSha256"] = image_sha
        revision = v.text_revision(q, image_sha)
        fake = root / "fake-author-qa.md"
        fake.write_text("SYNTHETIC AUTHOR SELF-ATTESTATION; NOT A REAL QA", encoding="utf-8")
        fake_sha = hashlib.sha256(fake.read_bytes()).hexdigest()
        def evidence(**extra):
            return {"reviewer": "SYNTHETIC_SOURCE_AUTHOR_NOT_E",
                    "reviewedAt": "2026-10-26", "evidencePath": "fake-author-qa.md",
                    "evidenceSha256": fake_sha, **extra}
        q["textQaEvidence"] = evidence(questionRevision=revision, sourceImageSha256="b" * 64)
        q["officialFinalQaEvidence"] = evidence(answerPdfSha256="c" * 64,
                                               finalCorrectionsReviewed=True)
        q["teachingQaEvidence"] = evidence(allFourOptionsReviewed=True, calculationReviewed=True)
        q["uiQaEvidence"] = evidence()  # Intentionally NO testedTeachingDigest.
        q["independentSolve"] = {
            "solvedWithoutOfficialAnswer": True, "officialAnswerHiddenDuringSolve": True,
            "questionRevision": revision, "solvedAt": "2026-10-26",
            "solver": "SYNTHETIC_SOURCE_AUTHOR_NOT_A_BLIND_SOLVER",
            "reasoning": "SYNTHETIC thirty plus thirty equals sixty",
            "auditEvidencePath": "fake-author-qa.md", "auditEvidenceSha256": fake_sha,
            "answer": "B",
        }
        image_item = {
            "questionId": qid, "qaStatus": "PASS", "output": image_relative,
            "sha256": image_sha,
            "visualReviewEvidence": {"reference": "fake-author-qa.md",
                                     "referenceSha256": fake_sha, "reviewedSha256": image_sha},
        }
        bank, items = [], []
        for paper, count in [("00-C", 38), ("00-E", 42), ("00-MB", 25),
                             ("09-1", 50), ("09-2", 50)]:
            for number in range(1, count + 1):
                identity = f"115-{paper}-{number:02d}"
                bank.append(q if identity == qid else {
                    "questionId": identity, "year": 115, "paperCode": paper,
                    "originalQuestionNumber": number,
                    "subject": v.subject_for(115, paper, number),
                })
                items.append(image_item if identity == qid else {
                    "questionId": identity, "qaStatus": "DRAFT"})
        assert len(bank) == len(items) == 205
        v.dump(source / "questions.json", {"questions": bank})
        v.dump(source / "webp-manifest.json", {"items": items, "expected": 205})
        v.dump(source / "inventory.json", {"expected": 205})
        v.dump(source / "VALIDATION.json", {"sqlite": "SQLITE_ROUNDTRIP_PASS"})
        (source / "question-bank.sqlite3").touch()
        # These source-side assertions are NOT actual QA; they model attacker input.
        assert not (root / "sudu/release-governance/independent-review-policy.json").exists()
        assert not list(source.glob("review-evidence/*"))
        assert q["uiQaEvidence"].get("testedTeachingDigest") is None
        output = root / "output"
        v.snapshot(root, output, 115, "a" * 40)
        released = v.read(output / "sudu/data/approved/115.json")
        result = {"syntheticFixture": True, "publisherPath": str(path),
                  "admittedCount": released["approvedCount"],
                  "admittedIds": [item["canonicalId"] for item in released["questions"]],
                  "sourceRegistryExists": False, "reviewBatchExists": False,
                  "testedTeachingDigest": None}
        print(json.dumps(result, ensure_ascii=False))
        assert released["approvedCount"] == 0, (
            "P0: source-author self-attestation bypassed final distinct-AI admission gate: "
            + repr(result["admittedIds"]))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publisher", required=True)
    reproduce(parser.parse_args().publisher)
