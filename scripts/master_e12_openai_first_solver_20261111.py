"""E12 active-provider G6 evidence capture, fail-closed.

One original OpenAI Responses POST, no prior chat, no tools, no official answer
in model input. Real first HTTP bytes and runner chronology are captured before
a separate G3 retrieval. This NEVER certifies G6, G7, V1 or student release.

Operational proof requires a real independent operator and separately
authenticated provider project; source control and this script alone are not
provider attestation or B/E identity evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

QID = "114-00-E-12"
G2_PATH = Path("docs/evidence-inputs/114-00-E-12-G6-answer-free-G2-first-input-20261111.txt")
G2_BLOB = "29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff"
G2_SHA256 = "8dfc4a2e8c2cb62d1fe3c95318bfaae6fa9bb83e4937b25df1359f41b52063e0"
G3_URL = (
    "https://raw.githubusercontent.com/homelux-huang/7581707/"
    "15108e8e657d070724889f1df3d3a6ae6da96d97/"
    "sudu/data/processed/114/review-evidence/"
    "114-00-E-12-official-publisher-20261107.json"
)
G3_SHA256 = "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"
API = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.5"
OUT = Path(os.getenv("E12_EVIDENCE_DIR", "_e12_openai_first_run")).resolve()
INSTRUCTIONS = (
    "Solve the provided exam question from first principles using only its text. "
    "Give the very first selected answer as 'First answer: X'. "
    "Then write FOUR separate lines 'A: ...', 'B: ...', 'C: ...', 'D: ...', "
    "each fully explaining why that choice is correct or incorrect. "
    "Also explain the dialogue reasoning, answer confidence and any ambiguity. "
    "Do not ask for hints. Do not access external tools, previous chats or an answer key."
)


def verified_operator_gate() -> dict:
    """Reject real inference without OWNER-armed environment + distinct GitHub actor.

    GitHub actors/environment variables are runner observations, NOT proof that
    historic B and E used different independent execution sessions. Environment
    reviewers and secret-policy rules must be separately verified by a real
    security reviewer. No synthetic run can mint a V1 trusted receipt.
    """
    expected_actor = os.getenv("E12_G6_OWNER_OPERATOR_LOGIN", "").strip()
    owner_armed = os.getenv("E12_G6_OWNER_ARMED", "")
    actor = os.getenv("GITHUB_ACTOR", "")
    triggering_actor = os.getenv("GITHUB_TRIGGERING_ACTOR", "")
    checks = {
        "owner_armed": owner_armed == "INDEPENDENT_OPERATOR_REVIEWED_ONE_SHOT",
        "operator_configured": bool(expected_actor)
            and expected_actor not in ("github-actions[bot]", "dependabot[bot]"),
        "actor_separation": bool(actor) and actor == expected_actor,
        "triggering_actor": bool(triggering_actor) and triggering_actor == expected_actor,
        "correct_repo": os.getenv("GITHUB_REPOSITORY") == "homelux-huang/7581707",
        "correct_branch": os.getenv("GITHUB_REF")
            == "refs/heads/security/master-e12-openai-first-response-harness-20261111",
        "only_push": os.getenv("GITHUB_EVENT_NAME") == "push",
        "first_run_only": os.getenv("GITHUB_RUN_ATTEMPT") == "1",
        "original_40hex_gitsha": bool(
            re.fullmatch(r"[0-9a-f]{40}", os.getenv("GITHUB_SHA", ""))
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(
            "OWNER_OPERATOR_GATE_NOT_AUTHORIZED__NO_PROVIDER_CALL__"
            + ",".join(k for k, value in checks.items() if not value)
        )
    return {
        "operatorGithubActorClaim": actor,
        "githubRunAttempt": "1",
        "ownerApprovedOperatorLoginClaim": expected_actor,
        "operatorGateType": "GITHUB_ENVIRONMENT_VARIABLE_AND_ACTOR_CHECK__NOT_A_SIGNED_ATTESTATION",
    }


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def write_once(filename: str, data: bytes) -> dict:
    """Exclusive-write, flushed bytes. No prior evidence may be replaced."""
    if "/" in filename or not filename:
        raise ValueError("basename only")
    OUT.mkdir(parents=True, exist_ok=True, mode=0o700)
    dest = OUT / filename
    with dest.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return {"file": filename, "byteLength": len(data), "sha256": sha(data), "gitBlobOid": blob(data)}


def write_json(filename: str, record: dict) -> dict:
    return write_once(
        filename,
        (json.dumps(record, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def verified_g2() -> bytes:
    raw = G2_PATH.read_bytes()
    if blob(raw) != G2_BLOB or sha(raw) != G2_SHA256:
        raise ValueError("FROZEN_G2_ORIGINAL_BYTES_NOT_MATCHED")
    text = raw.decode("utf-8", errors="strict")
    if len(re.findall(r"(?m)^\s*\([ABCD]\)\s", text)) != 4:
        raise ValueError("FROZEN_G2_MISSING_FOUR_OPTIONS")
    if re.search(r"(?i)(official\s+answer|answer\s+key|correct\s+option\s*:)", text):
        raise ValueError("FROZEN_G2_KEY_CONTAMINATION")
    return raw


def request_bytes(g2: bytes) -> bytes:
    doc = {
        "model": MODEL,
        "instructions": INSTRUCTIONS,
        "input": g2.decode("utf-8"),
        "max_output_tokens": 1400,
        "store": True,
        "stream": False,
    }
    if any(k in doc for k in ("previous_response_id", "tools", "tool_choice")):
        raise ValueError("STATE_OR_TOOLS_FORBIDDEN")
    return json.dumps(doc, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


def first_answer_text(obj: dict) -> str | None:
    parts = []
    for item in obj.get("output", []):
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message" or item.get("role") != "assistant":
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                parts.append(content["text"])
    text = "\n".join(parts)
    return text if text.strip() else None


def labels_present(text: str) -> bool:
    return bool(re.search(r"(?im)^\s*First answer\s*:\s*[ABCD]\b", text)) and all(
        re.search(r"(?m)^\s*" + x + r"\s*:\s*\S", text) for x in "ABCD"
    )


def preflight():
    g2 = verified_g2()
    body = request_bytes(g2)
    print(json.dumps({
        "status": "PREFLIGHT_ONLY_NO_MODEL_REQUEST",
        "G2_sha256": sha(g2), "G2_git_blob": blob(g2),
        "provider": API, "model": MODEL,
        "request_without_key_sha256": sha(body),
        "g6": "UNVERIFIED", "g7": "UNVERIFIED",
    }, sort_keys=True))


def first():
    g2 = verified_g2()
    body = request_bytes(g2)
    input_file = write_once("answer_free_g2.original", g2)
    request_file = write_once("provider_first_request.body", body)
    key = os.environ.get("E12_G6_OPENAI_API_KEY", "")
    if not key:
        write_json("provider_error.json", {
            "status": "HOLD_NO_INDEPENDENT_EXTERNAL_API_KEY",
            "atUtc": utc(), "questionId": QID,
            "input": input_file, "request": request_file,
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        })
        raise RuntimeError("MISSING_PROVIDER_SECRET__NO_INFERENCE_ATTEMPTED")
    try:
        operator_gate = verified_operator_gate()
    except RuntimeError as error:
        write_json("operator_gate_denied.json", {
            "questionId": QID,
            "status": "OWNER_OPERATOR_GATE_DENIED_NO_INFERENCE",
            "reasonCodes": str(error),
            "atUtc": utc(), "g6": "UNVERIFIED", "g7": "UNVERIFIED",
            "blindPass": False, "ready": False, "live": False,
        })
        raise
    client_id = "e12-" + os.environ.get("GITHUB_RUN_ID", "unknown") + "-" + str(uuid.uuid4())
    started_utc = utc()
    started_ns = time.monotonic_ns()
    req = urllib.request.Request(
        API,
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Client-Request-Id": client_id,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as http:
            status = http.status
            response_headers = {
                k.lower(): http.headers.get(k) for k in (
                    "content-type", "date", "x-request-id", "openai-processing-ms"
                )
            }
            raw = http.read()
    except urllib.error.HTTPError as error:
        raw_error = error.read()
        raw_error_file = write_once("provider_http_error.body", raw_error)
        write_json("provider_error.json", {
            "status": "HOLD_PROVIDER_HTTP_ERROR", "code": error.code,
            "clientRequestId": client_id,
            "providerRequestIdIfReturned": error.headers.get("x-request-id"),
            "startedUtc": started_utc, "completedUtc": utc(),
            "durationNs": time.monotonic_ns() - started_ns,
            "httpErrorRaw": raw_error_file,
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        })
        raise RuntimeError("PROVIDER_HTTP_ERROR__SEE_SECURE_ARTIFACT") from None
    except Exception as error:
        write_json("provider_error.json", {
            "status": "HOLD_PROVIDER_TRANSPORT_ERROR",
            "errorClass": type(error).__name__,
            "clientRequestId": client_id,
            "startedUtc": started_utc, "completedUtc": utc(),
            "durationNs": time.monotonic_ns() - started_ns,
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        })
        raise RuntimeError("PROVIDER_TRANSPORT_ERROR__SEE_SECURE_ARTIFACT") from None
    completed_utc = utc()
    response_file = write_once("provider_first_response.body", raw)
    json_valid = False
    result = {}
    try:
        if status != 200 or "application/json" not in (response_headers["content-type"] or "").lower():
            raise ValueError("NON_JSON_OR_NON_200_PROVIDER_RESPONSE")
        result = json.loads(raw, object_pairs_hook=no_duplicate_keys)
        if not isinstance(result, dict):
            raise ValueError("INVALID_PROVIDER_JSON_ROOT")
        json_valid = True
    except (ValueError, TypeError):
        pass
    text = first_answer_text(result) if json_valid else None
    text_file = write_once("provider_first_answer.utf8", text.encode("utf-8")) if text else None
    provider_response_id = result.get("id") if isinstance(result.get("id"), str) else None
    provider_model = result.get("model") if isinstance(result.get("model"), str) else None
    created = result.get("created_at") if isinstance(result.get("created_at"), (int, float)) else None
    structurally_complete = bool(text and labels_present(text))
    record = {
        "schemaVersion": 1, "questionId": QID,
        "attempt": "EXTERNAL_FIRST_MODEL_RESPONSE_CANDIDATE_NOT_A_V1_RECEIPT",
        "endpoint": API, "requestedModel": MODEL,
        "providerReturnedResponseId": provider_response_id,
        "providerReturnedModel": provider_model,
        "providerCreatedAtUnix": created,
        "providerServerRequestId": response_headers.get("x-request-id"),
        "providerResponseHeadersSelected": response_headers,
        "clientRequestId": client_id,
        "httpStatus": status,
        "originalInput": input_file,
        "originalRequest": request_file,
        "originalFirstHttpResponse": response_file,
        "firstModelAnswerContent": text_file,
        "firstAnswerAllFourOptionLabelsPresent": structurally_complete,
        "jsonValid": json_valid,
        "runnerStartedUtc": started_utc,
        "runnerFirstResponseSavedUtc": completed_utc,
        "runnerDurationNs": time.monotonic_ns() - started_ns,
        "githubRunId": os.getenv("GITHUB_RUN_ID"),
        "githubRunAttempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "githubHeadSha": os.getenv("GITHUB_SHA"),
        "githubOperatorGateRunnerObservations": operator_gate,
        "officialAnswerReadAfterFirstResponse": "NOT_YET_READ",
        "providerServerRecordIndependentlyRetrieved": False,
        "runnerChronologyProviderSigned": False,
        "distinctBAuthorEReviewerIdentitiesVerified": False,
        "qualifiedG6": False, "qualifiedG7": False,
        "trustedV1Receipt": False,
        "blindPass": False, "ready": False, "live": False,
    }
    record_file = write_json("first_exchange_frozen.json", record)
    print(json.dumps({
        "status": "RAW_EXTERNAL_RESPONSE_FROZEN__NOT_G6_PASS",
        "providerResponseIdIfReturned": provider_response_id,
        "providerRequestIdIfReturned": response_headers.get("x-request-id"),
        "httpStatus": status,
        "rawSha256": response_file["sha256"],
        "rawGitBlob": response_file["gitBlobOid"],
        "firstExchangeManifestSha256": record_file["sha256"],
        "allOptionLabelsPresent": structurally_complete,
        "g6": "UNVERIFIED", "g7": "UNVERIFIED",
    }, sort_keys=True))
    if not (json_valid and provider_response_id and text and structurally_complete):
        raise RuntimeError("INVALID_FIRST_MODEL_REPLY__RETAIN_RAW_NO_RETRY")


def reveal_after():
    first_file = OUT / "first_exchange_frozen.json"
    raw_file = OUT / "provider_first_response.body"
    if not (first_file.is_file() and raw_file.is_file()):
        raise RuntimeError("NO_FROZEN_FIRST_REPLY__OFFICIAL_ANSWER_FORBIDDEN")
    manifest = json.loads(first_file.read_bytes(), object_pairs_hook=no_duplicate_keys)
    if sha(raw_file.read_bytes()) != manifest["originalFirstHttpResponse"]["sha256"]:
        raise RuntimeError("FROZEN_FIRST_RESPONSE_SHA_CHANGED")
    if not manifest["firstAnswerAllFourOptionLabelsPresent"]:
        raise RuntimeError("FIRST_ANSWER_NOT_STRUCTURALLY_COMPLETE")
    before_official = utc()
    with urllib.request.urlopen(G3_URL, timeout=30) as response:
        g3 = response.read()
    if sha(g3) != G3_SHA256:
        raise RuntimeError("G3_FROZEN_ORIGINAL_SHA_MISMATCH")
    answer_doc = json.loads(g3, object_pairs_hook=no_duplicate_keys)
    if answer_doc.get("finalAnswer") not in ("A", "B", "C", "D"):
        raise RuntimeError("OFFICIAL_G3_ANSWER_NOT_VERIFIED")
    official_file = write_once("official_g3_retrieved_only_after_first.body", g3)
    chronology_file = write_json("post_response_key_disclosure.json", {
        "questionId": QID,
        "firstExchangeManifestSha256": sha(first_file.read_bytes()),
        "firstResponseRawSha256": sha(raw_file.read_bytes()),
        "runnerBeforeOfficialReadUtc": before_official,
        "runnerAfterOfficialReadUtc": utc(),
        "officialG3": official_file,
        "officialAnswer": answer_doc["finalAnswer"],
        "chronologyType": "GITHUB_RUNNER_OBSERVATION_NOT_PROVIDER_SIGNED",
        "qualifiedG6": False, "qualifiedG7": False,
        "trustedV1Receipt": False, "ready": False, "live": False,
    })
    print(json.dumps({
        "status": "G3_OBSERVED_AFTER_FIRST_RESPONSE_NOT_SECURITY_ACCEPTANCE",
        "chronologySha256": chronology_file["sha256"],
        "g6": "UNVERIFIED", "g7": "UNVERIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["preflight", "first", "reveal-after"])
    opts = parser.parse_args()
    {"preflight": preflight, "first": first, "reveal-after": reveal_after}[opts.phase]()
