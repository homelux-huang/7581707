"""Fail-closed separate, signed reviewer authorization on new student admissions.

Evidence JSON and reviewer strings are self-editable by source authors. Trusted
keys and exact grandfathered original data are governed by main publisher, NEVER
read from QA sources. This code contains no private signing key.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"sudu/release-governance/independent-review-policy.json"
SHA=re.compile(r"^[0-9a-f]{64}$")

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def digest(x):
    return hashlib.sha256(x).hexdigest()

def blob_oid(x):
    return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\x00"+x).hexdigest()

def policy_from_trusted_main():
    try:
        data=json.loads(POLICY.read_text(encoding="utf-8"))
        return data if data.get("schemaVersion")==1 else None
    except (ValueError,OSError,AttributeError):
        return None

def substantive_notes_verified(source,rel,sha):
    if (not isinstance(rel,str) or not rel.startswith("sudu/data/processed/")
            or ".." in Path(rel).parts or Path(rel).is_absolute()
            or not rel.endswith(".md") or not SHA.fullmatch(str(sha))):
        return False
    root=Path(source)
    target=root/rel
    try:
        return (target.resolve().is_relative_to(root.resolve())
                and target.is_file() and not target.is_symlink()
                and digest(target.read_bytes())==sha)
    except (OSError,ValueError):
        return False

def certified(source,audit,question,manifest,teaching_document,raw_teaching,*,policy=None):
    """Return (approved,reason); signature verification is *additional* to all G0-G10."""
    trust=policy if policy is not None else policy_from_trusted_main()
    if not isinstance(trust,dict) or trust.get("schemaVersion")!=1:
        return False,"trusted_review_policy_missing"
    qid=question.get("questionId")
    revision=teaching_document.get("questionRevision")
    webp=(manifest or {}).get("sha256")
    if (not isinstance(qid,str) or not SHA.fullmatch(str(revision))
            or not SHA.fullmatch(str(webp))
            or not isinstance(teaching_document.get("content"),dict)
            or not isinstance(raw_teaching,(bytes,bytearray))):
        return False,"invalid_review_source"
    previous=(trust.get("legacyAlreadyPublished") or {}).get(qid)
    if previous is not None:
        if (previous.get("year")==question.get("year")
                and previous.get("questionRevision")==revision
                and previous.get("webpSha256")==webp
                and previous.get("teachingEvidenceGitBlob")==blob_oid(raw_teaching)):
            return True,"exact_five_historical_students_preserved"
        return False,"legacy_content_changed_must_be_reapproved"
    att=(audit or {}).get("independentReviewAttestation")
    if not isinstance(att,dict):
        return False,"not_independently_attested"
    keys=trust.get("authorizedReviewers")
    signer=keys.get(att.get("keyId")) if isinstance(keys,dict) and isinstance(att.get("keyId"),str) else None
    if not isinstance(signer,dict) or signer.get("enabled") is not True:
        return False,"no_externally_authorized_reviewer_key"
    statement=att.get("payload")
    if not isinstance(statement,dict):
        return False,"no_signed_statement"
    expected={
        "schemaVersion":1,"year":question.get("year"),"questionId":qid,
        "questionRevision":revision,"webpSha256":webp,
        "teachingDigest":digest(canonical(teaching_document["content"])),
        "teachingEvidenceSha256":digest(raw_teaching),
        "reviewerLogin":signer.get("login"),"reviewerRole":signer.get("role")
    }
    if any(statement.get(k)!=v for k,v in expected.items()):
        return False,"signed_material_or_identity_mismatch"
    author=statement.get("sourceAuthorLogin")
    if not isinstance(author,str) or not author.strip() or author.casefold()==str(signer.get("login","")).casefold():
        return False,"not_distinct_from_author"
    if (trust.get("requireHumanTeacher") is True
            and signer.get("role")!="qualified_human_teacher"):
        return False,"qualified_teacher_required"
    if signer.get("organizationVerified") is not True:
        return False,"no_offline_reviewer_identity_validation"
    if not isinstance(statement.get("reviewedAt"),str) or not statement["reviewedAt"].strip():
        return False,"review_timestamp_missing"
    options=statement.get("optionByOptionFindings")
    if (not isinstance(options,dict) or set(options)!=set("ABCD")
            or any(not isinstance(options[k],str) or len(options[k].strip())<12 for k in "ABCD")):
        return False,"no_substantive_four_option_review"
    if (statement.get("teacherAndElementaryReviewed") is not True
            or statement.get("reviewedCalculationOrNoncalculation") is not True):
        return False,"no_complete_teaching_review"
    if not substantive_notes_verified(source,statement.get("reviewNotesPath"),statement.get("reviewNotesSha256")):
        return False,"signed_independent_review_notes_absent_or_changed"
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        pub=base64.b64decode(signer.get("ed25519PublicKey",""),validate=True)
        sig=base64.b64decode(att.get("signature",""),validate=True)
        if len(pub)!=32 or len(sig)!=64:
            return False,"malformed_signature"
        Ed25519PublicKey.from_public_bytes(pub).verify(sig,canonical(statement))
    except (ValueError,TypeError,ImportError,InvalidSignature):
        return False,"signed_review_not_validated"
    return True,"trusted_distinct_reviewer_signed_material_and_substantive_notes"
