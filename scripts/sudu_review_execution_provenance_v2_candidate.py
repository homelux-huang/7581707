"""EXPERIMENTAL only. Never integrated into publisher or production trusted registry.

An offline signature-and-binding validator for a proposed independent AI
execution proof. A positive result is NOT authorization to release a QID:
provider retrieval, external issuer ownership, main-trust policy and existing
content/UI/source gates still must be independently checked.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROLES = ("B_AUTHOR", "BLIND_SOLVER", "E_REVIEWER")
RESPONSE_ID = re.compile(r"^resp_[a-zA-Z0-9_-]{6,}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
QID = re.compile(r"^(114|115)-(00-C|00-E|00-MB|09-1|09-2)-[0-9]{2}$")
NOT_PRODUCTION_AUTHORIZATION = "SIGNED_STRUCTURE_ONLY_EXTERNAL_PROVIDER_UNVERIFIED"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha(data):
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()

def _date(value):
    if not isinstance(value, str):
        raise ValueError("missing_time")
    v = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if v.tzinfo is None:
        raise ValueError("unauthenticated_time")
    return v.astimezone(timezone.utc)

def _check_envelope(envelope, trusted, role, binding, now):
    if not isinstance(envelope, dict) or set(envelope) != {"signed", "signature", "prompt", "output"}:
        return None, "incomplete_execution_envelope"
    st = envelope["signed"]
    if not isinstance(st, dict):
        return None, "invalid_signed_payload"
    issuer = trusted.get(st.get("issuerKeyId"))
    if not isinstance(issuer, dict) or issuer.get("authorized") is not True or issuer.get("revoked") is not False:
        return None, "issuer_not_authorized_or_revoked"
    if issuer.get("role") != role or issuer.get("principalId") != st.get("principalId"):
        return None, "issuer_role_or_principal_mismatch"
    if st.get("schemaVersion") != 2 or st.get("role") != role:
        return None, "execution_schema_or_role_mismatch"
    for key in ("questionId", "questionRevision", "webpSha256", "teachingDigest"):
        if st.get(key) != binding.get(key):
            return None, "exact_source_or_teaching_binding_mismatch_" + key
    if (not isinstance(st.get("principalId"), str) or not st["principalId"].strip()
            or not isinstance(st.get("executionId"), str) or len(st["executionId"]) < 12
            or not RESPONSE_ID.fullmatch(str(st.get("providerResponseId")))):
        return None, "execution_identity_or_provider_id_missing"
    prompt, output = envelope["prompt"], envelope["output"]
    if (not isinstance(prompt, str) or not prompt.strip()
            or not isinstance(output, str) or not output.strip()
            or st.get("promptSha256") != sha(prompt)
            or st.get("outputSha256") != sha(output)):
        return None, "prompt_or_output_bytes_tampered"
    if (role == "BLIND_SOLVER" and (
            st.get("answerKeyExposed") is not False
            or any(label in prompt.casefold() for label in (
                "official answer:", "correct answer:", "answer key:",
                "officialanswer", "answerkey", "knownanswercandidate")))):
        return None, "blind_prompt_has_answer_or_exposure"
    if role == "BLIND_SOLVER" and (
            st.get("firstAnswer") not in ("A", "B", "C", "D")
            or len(output.strip()) < 60):
        return None, "blind_first_answer_or_reasoning_missing"
    if role == "E_REVIEWER":
        if st.get("officialEvidenceSha256") != binding.get("officialEvidenceSha256"):
            return None, "official_document_sha_mismatch"
        f = st.get("optionByOptionFindings")
        if (not isinstance(f, dict) or set(f) != set("ABCD")
                or any(not isinstance(f[x],str) or len(f[x].strip()) < 20 for x in "ABCD")
                or len(set(f.values())) != 4
                or st.get("teacherAndElementaryReviewed") is not True):
            return None, "independent_four_option_teaching_review_incomplete"
    try:
        started = _date(st.get("startedAt"))
        completed = _date(st.get("completedAt"))
        if completed > now or started > completed:
            return None, "unverifiable_execution_chronology"
        key = base64.b64decode(issuer["ed25519PublicKey"], validate=True)
        sig = base64.b64decode(envelope["signature"], validate=True)
        if len(key) != 32 or len(sig) != 64:
            return None, "invalid_issuer_key_or_signature_size"
        Ed25519PublicKey.from_public_bytes(key).verify(sig, canonical(st))
    except Exception:
        return None, "invalid_issuer_signature_or_time"
    return {"signed": st, "started": started, "completed": completed}, "signed_structure_ok"

def verify_offline_structure(chain, trusted, binding, *, now=None):
    """Return signature/binding viability, not a student admission certificate.

    A production caller must obtain 'trusted' from protected-main owner-controlled
    issuer registry, verify provider response and exact input items via API,
    validate non-self-review independently, and preserve all existing G0-G10.
    This function does none of those external network steps.
    """
    if not isinstance(chain, dict) or set(chain) != set(ROLES):
        return False, "missing_independent_execution_roles"
    if not isinstance(trusted, dict) or not isinstance(binding, dict):
        return False, "invalid_external_issuer_registry_or_material"
    if (not QID.fullmatch(str(binding.get("questionId")))
            or any(not SHA.fullmatch(str(binding.get(k))) for k in
                   ("questionRevision", "webpSha256", "teachingDigest", "officialEvidenceSha256"))):
        return False, "invalid_material_sha_or_question_id"
    now = now or datetime.now(timezone.utc)
    results = {}
    for role in ROLES:
        record, why = _check_envelope(chain[role], trusted, role, binding, now)
        if record is None:
            return False, role + ":" + why
        results[role] = record
    signed = [results[r]["signed"] for r in ROLES]
    if len({s["principalId"] for s in signed}) != 3:
        return False, "not_distinct_external_execution_principals"
    if len({s["issuerKeyId"] for s in signed}) != 3:
        return False, "not_distinct_independent_issuer_keys"
    if len({s["executionId"] for s in signed}) != 3 or len({s["providerResponseId"] for s in signed}) != 3:
        return False, "replayed_or_duplicate_provider_execution"
    if not (results["B_AUTHOR"]["completed"] <= results["BLIND_SOLVER"]["started"]
            and results["BLIND_SOLVER"]["completed"] <= results["E_REVIEWER"]["started"]):
        return False, "blind_not_frozen_before_independent_review"
    return True, NOT_PRODUCTION_AUTHORIZATION

def is_student_release_authorized(*_args, **_kwargs):
    """Never allow this experimental V2 module to bypass the current V1 gate."""
    return False
