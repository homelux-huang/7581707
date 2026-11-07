#!/usr/bin/env python3
"""ROLE D read-only real MASTER private emitter <-> current V4 integration audit.

No browser, no synthetic approved JSON, no mocked E trust or blind solver.
The audit only reads exact pinned repositories and emits a FAIL-CLOSED contract
report.  It must never mark UIQA PASS, READY or LIVE.
"""
from __future__ import annotations

import ast
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "_master_private"
QA = ROOT / "_qa_source"
OUT = ROOT / "test-results" / "role-d-private-emitter-contract-20261107"
QID = "114-00-E-12"
PIN_MAIN = "5546a603abfe0af2e62c0e5f63f775be0bfb24cf"
PIN_MASTER = "0384933b97fe2eaa9372f99b4549b4a5d45d0076"
PIN_QA = "3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2"
REV = "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec"
IMAGE_SHA = "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60"
TEACHING_SHA = "c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a"
EVIDENCE = {
    "ocr": ("114-00-E-12-ocr-publisher-20261107.json", "8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc"),
    "official": ("114-00-E-12-official-publisher-20261107.json", "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"),
    "teaching": ("114-00-E-12-teaching-publisher-20261107.json", "6a9235ac6c1af701c9e414ec106ebc2e56b905ad3c61373041d5cb05b2f2714f"),
}

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        if tag not in ("link", "script"):
            return
        for k, value in attrs:
            if k in ("href", "src") and isinstance(value, str) and value.startswith("./"):
                self.refs.append(value[2:].split("?", 1)[0])

def git(*a, cwd):
    return subprocess.check_output(["git", *a], cwd=cwd, encoding="utf-8").strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate():
    problems, checks = [], []
    def check(value, code, message, *, serious=True):
        checks.append({"code": code, "ok": bool(value), "detail": message})
        if not value and serious:
            problems.append({"code": code, "reason": message})
        return bool(value)

    report = {
        "schemaVersion": 1, "role": "D", "questionId": QID,
        "taskId": "D-114-E12-PRIVATE-EMITTER-CONTRACT-20261107-02",
        "formalUiqaPassed": False, "newReady": False, "newLive": False,
        "ranChromium": False, "ranOldHoldOr24Negatives": False,
        "source": {"mainBase": PIN_MAIN, "privateEmitterHead": PIN_MASTER, "qaSourceAfterPR177": PIN_QA},
    }
    check(git("rev-parse", "HEAD", cwd=MASTER) == PIN_MASTER,
          "PRIVATE_HEAD_DRIFT", "MASTER private issuer must be re-audited on exact head")
    check(git("rev-parse", "HEAD", cwd=QA) == PIN_QA,
          "QA_HEAD_DRIFT", "QA teaching/G2/G3 must be audited on exact post-PR177 head")
    actual_main = git("rev-parse", "refs/remotes/origin/main", cwd=ROOT)
    check(actual_main == PIN_MAIN, "PROTECTED_MAIN_DRIFT",
          "Review protected main again and refresh exact SHA pins before any claim")

    private_src = (MASTER / "scripts/sudu_private_candidate_issuer.py").read_text(encoding="utf-8")
    parsed = ast.parse(private_src)
    issuer = next((x for x in parsed.body if isinstance(x, ast.FunctionDef) and x.name == "emit_private"), None)
    gate = next((x for x in parsed.body if isinstance(x, ast.FunctionDef) and x.name == "evaluate"), None)
    check(bool(issuer and gate), "NATIVE_ISSUER_REQUIRED", "MASTER must provide both emit_private and evaluate")
    runtime = []
    if issuer:
        for node in ast.walk(issuer):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "runtime" for t in node.targets):
                runtime = ast.literal_eval(node.value)
    check(bool(runtime), "PRIVATE_COPY_LIST_ABSENT",
          "Private emitter must declare exact V4 runtime files copied into ephemeral directory")
    src_html = (ROOT / "sudu/v4-115-multisubject-review-demo.html").read_text(encoding="utf-8")
    parser = Tags()
    parser.feed(src_html)
    actual_refs = sorted(set(parser.refs))
    missing_assets = sorted(ref for ref in actual_refs if ref not in runtime)
    for asset in missing_assets:
        check(False, "PRIVATE_ASSET_NOT_COPIED:" + asset,
              "V4 references " + asset + " but private emitter does not copy it")
    # Production build injects the current verified-year adapter at </body>;
    # original HTML lacks that adapter. Copying the JS file alone cannot start
    # real 114-year verified data mode, even if approved/114.json is present.
    build_src = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
    adapter = "verified-questions-runtime.js"
    production_adapter = 'verified-questions-runtime.js?v=' in build_src and "original_v4.replace(" in build_src
    raw_has_adapter = bool(re.search(r'<script[^>]+src=["\'][^"\']*verified-questions-runtime[.]js', src_html))
    issuer_has_adapter = ('verified-questions-runtime.js?v=' in private_src and
                          ("replace(" in private_src or "write_text(" in private_src))
    check(production_adapter, "PRODUCTION_ADAPTER_NOT_IDENTIFIED",
          "Need the real build.py adapter injection as immutable V4 integration reference")
    if production_adapter and not raw_has_adapter and not issuer_has_adapter:
        check(False, "PRIVATE_ADAPTER_NOT_INJECTED",
              "Private emitter copies source HTML and adapter JS but never injects adapter script tag; protected build.py injects it only when building")
    report["v4Assets"] = {
        "referenced": actual_refs, "privateCopied": runtime,
        "missing": missing_assets, "productionAdapterBuildInjection": production_adapter,
        "rawHtmlAlreadyContainsAdapter": raw_has_adapter, "privateInjectorFound": issuer_has_adapter,
        "mainV4GitBlob": git("hash-object", "sudu/v4-115-multisubject-review-demo.html", cwd=ROOT),
    }

    native = "pub.public_question(" in private_src and "pub.site_check(" in private_src
    check(native, "NOT_ORIGINAL_PUBLISHER_ASSEMBLER",
          "Private issuer must use the exact original public_question() and site_check()")
    protections = ("RUNNER_TEMP" in private_src and
                   "destination.is_relative_to(ROOT.resolve())" in private_src and
                   "NONPUBLIC" in private_src)
    check(protections, "PRIVATE_OUTPUT_CONTAINMENT_UNVERIFIED",
          "Private output must remain under runner-private temp, never approved/main/Pages")
    mainpub = ROOT / "scripts/sudu_verified_publish.py"
    constants = {}
    for node in parsed.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try: constants[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, MemoryError): pass
    pins_ok = all((
        constants.get("QID") == QID, constants.get("REV") == REV,
        constants.get("WEBP") == IMAGE_SHA,
        constants.get("TEACHING_CANONICAL") == TEACHING_SHA,
        constants.get("QA_MIN_SHA") == PIN_QA,
        constants.get("EXPECTED_MAIN_PUBLISHER") == sha(mainpub),
    ))
    check(pins_ok, "PRIVATE_PIN_DRIFT",
          "Original publisher SHA, E12 QID/revision/WebP/canonical lesson, QA HEAD must match exact source")
    report["publisherSha256"] = sha(mainpub)

    evidence = {}
    for field, (name, digest) in EVIDENCE.items():
        p = QA / "sudu/data/processed/114/review-evidence" / name
        actual = sha(p) if p.is_file() else None
        check(actual == digest, "QA_EVIDENCE_BYTES_" + field.upper(),
              "Exact real PR177 post-merge "+field+" issuer bytes must be SHA pinned")
        evidence[field] = {"path": str(p.relative_to(QA)), "expectedSha256": digest,
                           "actualSha256": actual}
    report["immutableQaEvidence"] = evidence
    teaching = json.loads((QA/"sudu/data/processed/114/review-evidence"/EVIDENCE["teaching"][0]).read_text(encoding="utf-8"))
    check(teaching.get("questionId") == QID and teaching.get("questionRevision") == REV
          and teaching.get("webpSha256") == IMAGE_SHA and
          teaching.get("canonicalTeachingSha256") == TEACHING_SHA
          and teaching.get("studentReleaseApproved") is False,
          "NATIVE_TEACHING_NOT_SHA_BOUND",
          "PR177 native teaching is source/image/content bound, with studentReleaseApproved false")

    policy = json.loads((ROOT/"sudu/release-governance/independent-review-policy.json").read_text(encoding="utf-8"))
    registered = QID in (policy.get("trustedAiReviewReceipts") or {})
    # This state is an expected external HOLD. Never create/mutate E receipts.
    blind_unimplemented = bool(gate and any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "require"
        and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value is False
        for n in ast.walk(gate)
    ))
    report["externalGateState"] = {
        "protectedMainE12TrustPresent": registered,
        "externalProviderBlindAttestationStillHardBlocked": blind_unimplemented,
        "genuineBlindEvidenceAuthenticated": False,
        "preUiCandidateIssued": False,
    }
    # Do not mark any status as "formal" or "PASS"; no browser ran here.
    report["checks"] = checks
    report["integrationBlockers"] = problems
    report["status"] = "PRIVATE_CONTRACT_BLOCKED_AND_EXTERNAL_E_HOLD" if problems or blind_unimplemented or not registered else "PRIVATE_STATIC_CONTRACT_PRESENT_BUT_NOT_UIQA"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"private-emitter-contract-report.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status":report["status"], "masterHead": PIN_MASTER,
                      "qaHead": PIN_QA, "contractFailures":[x["code"] for x in problems],
                      "protectedETrust": registered,
                      "externalBlindHardBlock":blind_unimplemented,
                      "formalUiqaPassed":False}, ensure_ascii=False))
    # Integrity violations beyond the two known integration gaps must fail CI.
    allowed = {"PRIVATE_ASSET_NOT_COPIED:v4-score-feedback.css", "PRIVATE_ADAPTER_NOT_INJECTED"}
    unexpected = [x["code"] for x in problems if x["code"] not in allowed]
    if unexpected:
        raise AssertionError("Unexpected private issuer source/contract drift: "+", ".join(unexpected))
    if not problems:
        print("STATIC INTEGRATION CONTRACT SATISFIED BUT EXTERNAL E/BLIND REMAINS HOLD.")
    else:
        print("EXPECTED REAL INTEGRATION BLOCKERS DETECTED; NO PRIVATE EMISSION OR BROWSER QA.")
    return report

if __name__ == "__main__":
    validate()
