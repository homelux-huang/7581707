"""One genuine GitHub Models HTTP attempt: original first bytes, no prior chat.

NOT V1/V2 TRUST_PASS. No account/session authorship of ROLE B/E is authenticated.
The model receives exactly one stateless API call with the frozen G2 prompt.
The official answer is retrieved in a SEPARATE phase AFTER original HTTP bytes
and the first-run SHA metadata have been persisted to disk.
No retry, no key sent to the model, no unrelated repository material read.
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
from datetime import datetime, timezone
from pathlib import Path

G2_PATH = Path("docs/evidence-inputs/114-00-E-12-G6-answer-free-G2-first-input-20261110.txt")
G2_GIT_BLOB = "29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff"
API = "https://models.github.ai/inference/chat/completions"
MODEL = "openai/gpt-4.1-mini"
G3_URL = (
    "https://raw.githubusercontent.com/homelux-huang/7581707/"
    "15108e8e657d070724889f1df3d3a6ae6da96d97/"
    "sudu/data/processed/114/review-evidence/"
    "114-00-E-12-official-publisher-20261107.json"
)
G3_SHA256 = "63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12"
OUT = Path(os.environ.get("E12_EVIDENCE_DIR", "_e12_first_solver_evidence")).resolve()
SYSTEM = (
    "You are solving one unseen multiple-choice exam question. "
    "Reply ONCE with your first selected option (A, B, C, or D), then give "
    "four explicitly labeled explanations A, B, C, D (each why correct or "
    "incorrect), dialogue reasoning, confidence and any ambiguity. "
    "Do not ask for more input. Use only the provided question."
)


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def save(name: str, raw: bytes):
    if not isinstance(raw, bytes):
        raise TypeError("raw bytes required")
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    if p.exists():
        raise RuntimeError("immutable first-response file already exists: " + name)
    p.write_bytes(raw)
    return {"path": name, "bytes": len(raw), "sha256": sha(raw), "git_blob": blob(raw)}


def save_json(name, data):
    return save(name, (json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def first():
    # These file pins are strong evidence of supplied input, not model-history innocence.
    question = G2_PATH.read_bytes()
    if blob(question) != G2_GIT_BLOB:
        raise ValueError("G2 official-answer-free original Git Blob does not match")
    text = question.decode("utf-8", errors="strict")
    if len(text) < 200 or len(re.findall(r"(?m)^\s*\([ABCD]\)", text)) != 4:
        raise ValueError("original four options absent")
    if re.search(r"(?i)(official\s+answer\s*[:=]|answer\s+key\s*[:=]|correct\s+answer\s*[:=])", text):
        raise ValueError("answer key appears in supplied user prompt")
    request_doc = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        "temperature": 0,
        "max_tokens": 1400,
        "stream": False,
    }
    # Bytes written EXACTLY as subsequently sent via HTTPS in this request.
    request_body = json.dumps(
        request_doc, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    input_record = save("g2_question_input.raw", question)
    request_record = save("provider_http_request_body.raw", request_body)
    token = os.environ.get("GITHUB_MODELS_TOKEN")
    if not token:
        save_json("provider_error.json", {
            "error_type": "TOKEN_UNAVAILABLE",
            "at_utc": now_utc(),
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        })
        raise ValueError("GitHub Actions built-in models:read token unavailable")
    req = urllib.request.Request(
        API, data=request_body, method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    started = now_utc()
    started_ns = time.monotonic_ns()
    try:
        # Exactly ONE provider attempt. No backoff, retry, cache or other agent.
        with urllib.request.urlopen(req, timeout=55) as response:
            status = response.status
            headers = {
                str(k).lower(): str(v) for k, v in response.headers.items()
                if str(k).lower() in (
                    "date", "content-type", "x-request-id",
                    "x-github-request-id", "x-ms-request-id",
                    "x-ms-correlation-request-id",
                )
            }
            raw = response.read()
    except urllib.error.HTTPError as error:
        raw = error.read()
        error_info = {
            "error_type": "PROVIDER_HTTP_ERROR",
            "status": error.code, "at_utc": now_utc(),
            "duration_ns": time.monotonic_ns() - started_ns,
            "raw_error": save("provider_http_error.raw", raw),
            "input": input_record, "http_request": request_record,
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        }
        save_json("provider_error.json", error_info)
        raise
    except Exception as error:
        save_json("provider_error.json", {
            "error_type": type(error).__name__,
            "at_utc": now_utc(),
            "duration_ns": time.monotonic_ns() - started_ns,
            "input": input_record, "http_request": request_record,
            "g6": "UNVERIFIED", "g7": "UNVERIFIED",
        })
        raise
    completed = now_utc()
    response_record = save("provider_first_http_response.raw", raw)
    try:
        doc = json.loads(raw)
        model_text = (doc.get("choices") or [{}])[0].get("message", {}).get("content")
    except (ValueError, TypeError, AttributeError, IndexError):
        doc, model_text = {}, None
    if not isinstance(model_text, str):
        model_text = None
    if model_text:
        reply_record = save("provider_first_model_content.utf8", model_text.encode("utf-8"))
    else:
        reply_record = None
    provider_id = doc.get("id") if isinstance(doc.get("id"), str) else None
    provider_model = doc.get("model") if isinstance(doc.get("model"), str) else None
    provider_created = doc.get("created")
    if not isinstance(provider_created, (int, float)):
        provider_created = None
    first_result = {
        "schemaVersion": 1,
        "questionId": "114-00-E-12",
        "provider": "github-models-https-api",
        "endpoint": API,
        "requestedModel": MODEL,
        "providerReturnedModel": provider_model,
        "providerReturnedCompletionId": provider_id,
        "providerReturnedCreatedUnix": provider_created,
        "providerHttpStatus": status,
        "providerResponseHeadersSelected": headers,
        "runtimeUtcBeforeRequest": started,
        "runtimeUtcAfterFirstResponseStored": completed,
        "runtimeDurationNs": time.monotonic_ns() - started_ns,
        "githubActionRunId": os.environ.get("GITHUB_RUN_ID"),
        "githubActionRunAttempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "githubActionWorkflowSha": os.environ.get("GITHUB_SHA"),
        "originalG2": input_record,
        "originalHttpRequestBody": request_record,
        "originalProviderFirstHttpResponse": response_record,
        "originalFirstModelContent": reply_record,
        "firstAnswerTextHasABCDLabels": bool(model_text and all(
            re.search(r"(?mi)^\s*(?:\([{}]\)|[{}][\).:-])".format(ch, ch), model_text)
            for ch in "ABCD"
        )),
        "firstResponseStoredBeforeOfficialKeyFetched": True,
        "officialAnswerWasInApiMessage": False,
        "otherConversationProvided": False,
        "statelessSingleProviderHttpAttempt": True,
        "modelHadNoHiddenPretrainingKnowledge": "NOT_PROVABLE",
        "providerIdentityExternallyRetrievableAndSigned": "UNVERIFIED",
        "separateBAndEExecutingPrincipalsAuthenticated": False,
        "qualifiedG6Blind": False,
        "qualifiedG7Trusted": False,
        "studentReady": False,
        "studentLive": False,
    }
    record = save_json("first_http_exchange_frozen.json", first_result)
    # Only the after-response action is permitted to fetch the key.
    print(json.dumps({
        "status": "ONE_EXTERNAL_HTTP_RESPONSE_STORED_NOT_G6_PASS",
        "httpStatus": status,
        "providerReturnedCompletionId": provider_id,
        "providerReturnedModel": provider_model,
        "rawResponseSha256": response_record["sha256"],
        "rawResponseGitBlob": response_record["git_blob"],
        "firstResponseRecordSha256": record["sha256"],
        "firstResponseHasABCDLabels": first_result["firstAnswerTextHasABCDLabels"],
        "g6": "UNVERIFIED", "g7": "UNVERIFIED",
    }, sort_keys=True))
    if status != 200 or not model_text:
        raise RuntimeError("provider did not return a usable first response")


def reveal_after():
    # Run ONLY after first stage terminated. Source question/answer never added to model input.
    frozen = OUT / "first_http_exchange_frozen.json"
    response = OUT / "provider_first_http_response.raw"
    if not frozen.is_file() or not response.is_file():
        raise RuntimeError("cannot disclose official key without original first answer")
    first_record = json.loads(frozen.read_bytes())
    if sha(response.read_bytes()) != first_record["originalProviderFirstHttpResponse"]["sha256"]:
        raise RuntimeError("first model response was modified after its freeze")
    before_fetch = now_utc()
    with urllib.request.urlopen(G3_URL, timeout=30) as req:
        raw = req.read()
    if sha(raw) != G3_SHA256:
        raise RuntimeError("frozen official G3 issuer bytes mismatch")
    doc = json.loads(raw)
    disclosed_key = doc.get("finalAnswer")
    if disclosed_key not in ("A", "B", "C", "D"):
        raise RuntimeError("official G3 answer not recognized")
    g3_record = save("official_g3_retrieved_after_first_response.raw", raw)
    record = save_json("key_disclosure_chronology_runner_observation.json", {
        "schemaVersion": 1,
        "questionId": "114-00-E-12",
        "firstResponseFrozenRecordSha256": sha(frozen.read_bytes()),
        "firstResponseBytesSha256": sha(response.read_bytes()),
        "officialG3": g3_record,
        "officialKeyRevealedInSeparateWorkflowStep": disclosed_key,
        "utcBeforeG3NetworkRead": before_fetch,
        "utcAfterG3Write": now_utc(),
        "executionChronology": "GITHUB_RUNNER_STEPS_ONLY__NOT_PROVIDER_SIGNED",
        "externalProviderReplayCheck": "NOT_AVAILABLE",
        "g6Qualified": False,
        "g7Qualified": False,
        "trustedV1Receipt": False,
    })
    print(json.dumps({
        "status": "POST_RESPONSE_KEY_READ_RECORDED__NOT_G6_APPROVAL",
        "officialG3Sha256": g3_record["sha256"],
        "chronologySha256": record["sha256"],
        "g6": "UNVERIFIED", "g7": "UNVERIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("first", "reveal-after"))
    args = p.parse_args()
    if args.phase == "first":
        first()
    else:
        reveal_after()
