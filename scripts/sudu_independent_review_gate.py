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
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"sudu/release-governance/independent-review-policy.json"
REPO="homelux-huang/7581707"
HEX40=re.compile(r"^[0-9a-f]{40}$")

def _no_duplicate_keys(pairs):
    result={}
    for k,v in pairs:
        if k in result:
            raise ValueError("duplicate signed reviewer configuration key")
        result[k]=v
    return result

def _time(value):
    if not isinstance(value,str):
        raise ValueError("missing ISO8601 UTC offset")
    ts=datetime.fromisoformat(value.replace("Z","+00:00"))
    if ts.tzinfo is None:
        raise ValueError("naive reviewer authorization time")
    return ts.astimezone(timezone.utc)

def _github_json(path):
    # External identity is verified from GitHub itself. No authored certificate
    # can substitute its own GitHub PR author, commits or APPROVED review event.
    if not path.startswith("/pulls/") or ".." in path:
        raise ValueError("invalid GitHub review API path")
    headers={"Accept":"application/vnd.github+json","User-Agent":"7581707-release-review/1"}
    token=os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"]="Bearer "+token
    request=Request("https://api.github.com/repos/"+REPO+path,headers=headers)
    with urlopen(request,timeout=15) as response:
        if response.status!=200:
            raise ValueError("GitHub verification unavailable")
        return json.loads(response.read())

def _author_and_github_review_verified(payload,signer):
    number=payload.get("reviewPullRequestNumber")
    review_id=payload.get("approvedReviewId")
    head=payload.get("reviewHeadSha")
    source_login=payload.get("sourceAuthorLogin")
    if (type(number) is not int or number<=0 or type(review_id) is not int
            or review_id<=0 or not HEX40.fullmatch(str(head))
            or not isinstance(source_login,str) or not source_login.strip()
            or source_login.casefold()==str(signer.get("login","")).casefold()):
        return False
    try:
        pr=_github_json(f"/pulls/{number}")
        review=_github_json(f"/pulls/{number}/reviews/{review_id}")
        total=pr.get("commits")
        if type(total) is not int or total<1 or total>100:
            return False  # large PR must be separately attested/paginated, not guessed
        commits=_github_json(f"/pulls/{number}/commits?per_page=100")
        author=pr.get("user") or {}
        actor=review.get("user") or {}
        if (pr.get("draft") is True or (pr.get("base",{}).get("repo",{}) or {}).get("full_name")!=REPO
                or (pr.get("head",{}) or {}).get("sha")!=head
                or (author.get("login") or "").casefold()!=source_login.casefold()
                or author.get("id")!=payload.get("sourceAuthorGithubId")
                or (actor.get("login") or "").casefold()!=str(signer.get("login","")).casefold()
                or actor.get("id")!=signer.get("githubUserId")
                or review.get("id")!=review_id
                or review.get("state")!="APPROVED" or review.get("commit_id")!=head
                or type(commits) is not list or len(commits)!=total):
            return False
        if _time(review.get("submitted_at")) > _time(payload.get("reviewedAt")):
            return False
        if _time(payload.get("reviewedAt")) > datetime.now(timezone.utc):
            return False
        all_contributors=set()
        for commit in commits:
            if commit.get("sha") is None or not HEX40.fullmatch(commit["sha"]):
                return False
            # Refuse unverifiable authors/committers, especially bot/self reviews.
            for part in ("author","committer"):
                person=commit.get(part) or {}
                login=person.get("login")
                if not isinstance(login,str) or not login:
                    return False
                all_contributors.add(login.casefold())
        if source_login.casefold() not in all_contributors:
            return False
        if str(signer.get("login","")).casefold() in all_contributors:
            return False
        if not any(c["sha"]==head for c in commits):
            return False
        return True
    except (OSError,ValueError,TypeError,KeyError,TimeoutError,UnicodeError):
        return False

def _official_document_sha(source,audit,qid):
    e=(audit or {}).get("evidence") or {}
    rel=e.get("official")
    if (not isinstance(rel,str) or not rel.startswith("sudu/data/processed/")
            or ".." in Path(rel).parts or Path(rel).is_absolute()
            or not rel.endswith(".json")):
        return None
    root=Path(source)
    path=root/rel
    try:
        if (not path.resolve().is_relative_to(root.resolve())
                or not path.is_file() or path.is_symlink()):
            return None
        raw=path.read_bytes()
        doc=json.loads(raw)
        if doc.get("questionId")!=qid:
            return None
        return digest(raw)
    except (OSError,ValueError,UnicodeError,AttributeError):
        return None

SHA=re.compile(r"^[0-9a-f]{64}$")

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def digest(x):
    return hashlib.sha256(x).hexdigest()

def blob_oid(x):
    return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\x00"+x).hexdigest()

def policy_from_trusted_main():
    try:
        data=json.loads(POLICY.read_text(encoding="utf-8"),object_pairs_hook=_no_duplicate_keys)
        return data if data.get("schemaVersion")==1 and data.get("githubRepository")==REPO else None
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
    if trust.get("githubRepository")!=REPO:
        return False,"wrong_trusted_repository"
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
    # Revocation and expiration must be enforced by the owner-controlled
    # registry even if old signed payloads were once approved.
    if signer.get("revokedAt") is not None:
        return False,"reviewer_key_revoked"
    if type(signer.get("githubUserId")) is not int or signer["githubUserId"]<=0:
        return False,"reviewer_github_identity_not_proven"
    try:
        now=datetime.now(timezone.utc)
        earliest=_time(signer.get("validFrom"))
        latest=_time(signer.get("expiresAt"))
        if not earliest<=now<latest:
            return False,"reviewer_key_outside_authorization_window"
    except (ValueError,TypeError):
        return False,"reviewer_authorization_dates_invalid"
    statement=att.get("payload")
    if not isinstance(statement,dict):
        return False,"no_signed_statement"
    official_sha=_official_document_sha(source,audit,qid)
    if not official_sha or not isinstance(question.get("answer"),str):
        return False,"signed_official_document_missing"
    expected={
        "schemaVersion":1,"year":question.get("year"),"questionId":qid,
        "questionRevision":revision,"webpSha256":webp,
        "teachingDigest":digest(canonical(teaching_document["content"])),
        "teachingEvidenceSha256":digest(raw_teaching),
        "officialAnswer":question.get("answer"),
        "officialEvidenceSha256":official_sha,
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
    try:
        reviewed=_time(statement["reviewedAt"])
        if not _time(signer["validFrom"])<=reviewed<_time(signer["expiresAt"]):
            return False,"review_outside_signer_authorization"
    except (ValueError,TypeError):
        return False,"review_time_unverified"
    if not _author_and_github_review_verified(statement,signer):
        return False,"github_pr_author_or_review_event_unverified"
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
