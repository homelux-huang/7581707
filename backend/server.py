#!/usr/bin/env python3
"""Private student API. Public Pages never contains its database, credentials or backups."""
from __future__ import annotations
import base64
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.environ.get("SUDU_DB_PATH", str(ROOT / "backend/private.sqlite3")))
ADMIN = os.environ.get("SUDU_ADMIN_USER", "admin")
BOOTSTRAP = os.environ.get("SUDU_ADMIN_INITIAL_PASSWORD", "")
DEV = os.environ.get("SUDU_DEV_ALLOW_ADMIN_ADMIN") == "1"
PUBLIC_BASE = os.environ.get("SUDU_ADMIN_PUBLIC_URL", "").rstrip("/")
ORIGINS = {x.strip() for x in os.environ.get("SUDU_ALLOWED_ORIGINS", "https://homelux-huang.github.io").split(",") if x.strip()}
LOCK = threading.RLock()
FAILURES = {}
MAX_BODY = 8_000_000
SESSION_SECONDS = 8 * 3600
PAPER_KEY = re.compile(r"(\d{2,3})/([A-Za-z0-9_-]{1,40})")
OFFICIAL_URL = re.compile(r"^https://(?:[^/]+\.)?tcte\.edu\.tw/")


def now(): return int(time.time())
def stamp(t=None): return datetime.fromtimestamp(now() if t is None else t, timezone.utc).isoformat()
def digest(token): return hashlib.sha256(token.encode()).hexdigest()
def finite(value): return type(value) in (int, float) and math.isfinite(value)
def valid_choice(value): return type(value) is int and 0 <= value <= 3


def password_hash(secret, salt=None):
    salt = salt or secrets.token_bytes(16)
    return base64.b64encode(salt).decode() + ":" + hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 450_000).hex()


def verify(secret, stored):
    try:
        salt, expected = stored.split(":", 1)
        return hmac.compare_digest(password_hash(secret, base64.b64decode(salt)).split(":", 1)[1], expected)
    except (ValueError, TypeError):
        return False


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    os.chmod(DB, 0o600)
    return conn


def initialize():
    if DEV and PUBLIC_BASE and urlparse(PUBLIC_BASE).hostname not in ("localhost", "127.0.0.1", "::1"):
        raise RuntimeError("admin/admin development mode cannot use a public service URL")
    if not BOOTSTRAP and not DEV:
        raise RuntimeError("Set SUDU_ADMIN_INITIAL_PASSWORD privately; there is no public default password")
    secret = BOOTSTRAP or "admin"
    if not DEV and (len(secret) < 12 or secret.lower() == "admin"):
        raise RuntimeError("Production admin password must be 12+ characters and not 'admin'")
    if PUBLIC_BASE and not DEV and not valid_https(PUBLIC_BASE):
        raise RuntimeError("Production service URL must use HTTPS")
    with LOCK, connect() as db:
        existing_columns = {row[1] for row in db.execute("PRAGMA table_info(adjustments)")}
        if existing_columns and not {"submission_id", "rule_version", "official_score"} <= existing_columns:
            # Snapshot an existing private database BEFORE additive schema migration.
            snapshot = DB.with_name(DB.stem + "-before-schema2-" + str(now()) + "-" + secrets.token_hex(3) + ".sqlite3")
            fd = os.open(snapshot, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            with sqlite3.connect(snapshot) as saved:
                db.backup(saved)
                if saved.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise RuntimeError("Pre-migration private backup failed integrity check")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admins(username TEXT PRIMARY KEY,password TEXT NOT NULL,must_change INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,username TEXT NOT NULL,csrf TEXT NOT NULL,expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS students(id TEXT PRIMARY KEY,token_hash TEXT NOT NULL,nickname TEXT NOT NULL,created INTEGER NOT NULL,updated INTEGER NOT NULL,state_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS adjustments(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,paper_key TEXT NOT NULL,old_score REAL,new_score REAL NOT NULL,reason TEXT NOT NULL,source TEXT NOT NULL,created INTEGER NOT NULL,admin TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS shares(token_hash TEXT PRIMARY KEY,student_id TEXT NOT NULL,paper_key TEXT,expires INTEGER NOT NULL,created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT NOT NULL,action TEXT NOT NULL,student_id TEXT,paper_key TEXT,created INTEGER NOT NULL,detail_json TEXT NOT NULL);
        """)
        columns = {r[1] for r in db.execute("PRAGMA table_info(adjustments)")}
        for field, kind in [("submission_id", "TEXT"), ("rule_version", "TEXT"), ("official_score", "REAL")]:
            if field not in columns:
                db.execute(f"ALTER TABLE adjustments ADD COLUMN {field} {kind}")
        if not db.execute("SELECT 1 FROM admins WHERE username=?", (ADMIN,)).fetchone():
            db.execute("INSERT INTO admins VALUES(?,?,1)", (ADMIN, password_hash(secret)))
        db.commit()


def audit(db, actor, action, student_id=None, paper_key=None, **detail):
    db.execute("INSERT INTO audit(actor,action,student_id,paper_key,created,detail_json) VALUES(?,?,?,?,?,?)",
               (actor, action, student_id, paper_key, now(), json.dumps(detail, ensure_ascii=False)))


def valid_https(raw):
    try:
        parsed = urlparse(raw)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def parse_time(raw):
    if not isinstance(raw, str) or len(raw) > 40:
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return value.timestamp() if value.tzinfo else None
    except (ValueError, OverflowError):
        return None


def clean_time(raw):
    return raw if parse_time(raw) is not None else None


@lru_cache(maxsize=40)
def _year_questions(path, modified):
    try:
        return json.loads(Path(path).read_text("utf-8"))
    except (ValueError, OSError):
        return {"papers": []}


def year_questions(year):
    if not re.fullmatch(r"\d{2,3}", str(year)):
        return {"papers": []}
    p = ROOT / "sudu/data/years" / (str(year) + ".json")
    return _year_questions(str(p), p.stat().st_mtime_ns) if p.is_file() else {"papers": []}


def load_question(qid):
    match = re.fullmatch(r"(\d{2,3})-[A-Za-z0-9_-]{1,160}", str(qid))
    if not match:
        return None
    for paper in year_questions(match[1]).get("papers", []):
        for question in paper.get("questions", []):
            if question.get("id") == qid:
                return question
    return None


def load_paper(key):
    match = PAPER_KEY.fullmatch(str(key))
    if not match:
        return None
    return next((p for p in year_questions(match[1]).get("papers", []) if p.get("paper") == match[2]), None)


def accepted(q):
    values = q.get("acceptedAnswers") or [q.get("answer")]
    return [x for x in values if valid_choice(x)] if isinstance(values, list) else []


def valid_selection(value, question=None):
    if isinstance(value, list):
        return bool(value) and all(valid_choice(x) for x in value) and len(set(value)) == len(value) and (question is None or question.get("questionType") == "multiple-choice")
    return valid_choice(value) and (question is None or question.get("questionType") != "multiple-choice")


def answer_is_correct(question, choice):
    return sorted(choice) == sorted(accepted(question)) if isinstance(choice, list) else choice in accepted(question)


def gradeable(q):
    options = q.get("options") or []
    presentable = len(options) == 4 and all(isinstance(x, str) and x.strip() for x in options) or q.get("official") is True and bool(OFFICIAL_URL.match(q.get("source") or ""))
    suspect = q.get("questionPresentation") == "original_image_required" or "cover_instruction_extraction_suspected" in (q.get("issues") or [])
    return q.get("answerVerified") is True and q.get("questionVerified") is True and bool(accepted(q)) and presentable and not suspect


def fingerprint(q):
    """Matches the browser change detector. This is not an authentication signature."""
    fields = ["id", "number", "source", "question", "options", "answer", "acceptedAnswers", "questionVerified", "answerVerified", "sourceRevision", "sourceChangePending", "questionPresentation"]
    text = json.dumps([q.get(k) for k in fields], ensure_ascii=False, separators=(",", ":"))
    raw = text.encode("utf-16-le")
    n = 2166136261
    for i in range(0, len(raw), 2):
        n = ((n ^ int.from_bytes(raw[i:i + 2], "little")) * 16777619) & 0xffffffff
    return format(n, "x")


def official_score_details(paper_key, entry):
    pending = lambda reason, **extra: {"score": None, "maxScore": None, "status": "pending-verification", "reason": reason, **extra}
    try:
        match = PAPER_KEY.fullmatch(paper_key)
        source = load_paper(paper_key)
        if not match or not source or parse_time(entry.get("submittedAt")) is None:
            return pending("缺少有效送出快照或原卷")
        items = source.get("questions", [])
        expected = source.get("expectedCount")
        if type(expected) is not int or expected < 1 or len(items) != expected or not all(gradeable(q) for q in items):
            return pending("正式原題與官方答案尚待完整覆核")
        if len({q["id"] for q in items}) != expected or len({q["number"] for q in items}) != expected:
            return pending("原卷題號或 ID 重複")
        rules = json.loads((ROOT / "sudu/data/scoring-rules.json").read_text("utf-8"))
        rule = next(x for x in reversed(rules["rules"]) if str(x.get("year")) == match[1] and x.get("paper") == match[2])
        if rule.get("verified") is not True or rule.get("type") != "per-question" or rule.get("expectedCount") != expected:
            return pending("正式配分規則待核實")
        if not rule.get("reviewedBy") or not rule.get("reviewedAt") or not OFFICIAL_URL.match(rule.get("sourceUrl") or ""):
            return pending("配分缺少官方來源與覆核證據")
        if entry.get("ruleVersion") and entry["ruleVersion"] != (rule.get("version") or rule["reviewedAt"]):
            return pending("官方配分版本已變更，歷史成績須重新覆核")
        if not entry.get("questionVersions") or any(entry["questionVersions"].get(q["id"]) != fingerprint(q) for q in items):
            return pending("原題／答案版本已變更或舊快照無版本證據，需重新覆核")
        weights, choices = rule.get("points") or {}, entry.get("choices") or {}
        if len(choices) != expected or len(weights) != expected:
            return pending("作答快照或逐題配分不完整")
        total, objective_max = 0., 0.
        for q in items:
            weight, choice = weights.get(str(q["number"])), choices.get(q["id"])
            item_rule = (rule.get("itemRules") or {}).get(str(q["number"]), {})
            if not finite(weight) or weight < 0:
                return pending("無效逐題配分")
            objective_max += weight
            multiple = q.get("questionType") == "multiple-choice"
            if not (isinstance(choice, list) and choice and all(valid_choice(c) for c in choice) and len(set(choice)) == len(choice) if multiple else valid_choice(choice)):
                return pending("無效作答選項")
            if item_rule.get("fullCredit") is True:
                total += weight
            elif multiple:
                if item_rule.get("method") == "official-subsets":
                    points = (item_rule.get("subsetPoints") or {}).get(",".join(str(c) for c in sorted(choice)))
                    if not finite(points) or not 0 <= points <= weight:
                        return pending("多選題缺少對應官方部分給分規則")
                    total += points
                elif item_rule.get("method") == "all-or-nothing":
                    total += weight if sorted(choice) == sorted(accepted(q)) else 0
                else:
                    return pending("多選題配分方式待核實")
            elif choice in accepted(q):
                total += weight
        manual = rule.get("manualSections") or []
        if not isinstance(manual, list) or any(not isinstance(x, dict) or not x.get("id") or not finite(x.get("maxScore")) or x["maxScore"] < 0 for x in manual):
            return pending("非選擇題配分待核實")
        maximum = objective_max + sum(x["maxScore"] for x in manual)
        if maximum <= 0 or not finite(rule.get("maxScore")) or abs(maximum - rule["maxScore"]) > 0.001:
            return pending("配分合計與整卷滿分不一致")
        extra = {"maxScore": maximum, "objectiveScore": round(total, 2), "objectiveMax": objective_max,
                 "source": rule["sourceUrl"], "ruleVersion": rule.get("version") or rule["reviewedAt"]}
        if manual or rule.get("scope") == "objective-section":
            return pending("非選擇題待授權人工閱卷，選擇題小計不是整卷分數", **extra, status="pending-marking")
        return {"score": round(total, 2), "status": "scored", "reason": None, **extra}
    except (OSError, ValueError, KeyError, StopIteration, TypeError):
        return pending("正式配分規則或完整原題尚待核實")


def official_score(paper_key, entry):
    result = official_score_details(paper_key, entry)
    return result if result["status"] == "scored" else None


def clean_events(raw):
    if not isinstance(raw, dict) or len(raw) > 20_000:
        raise ValueError("Invalid attempt history")
    out = {}
    for qid, events in raw.items():
        if not isinstance(qid, str) or len(qid) > 180 or not isinstance(events, list) or len(events) > 5000:
            raise ValueError("Invalid question history")
        question = load_question(qid)
        cleaned = []
        for event in events:
            if not isinstance(event, dict) or not valid_selection(event.get("choice"), question):
                continue
            choice = event["choice"]
            corrected = answer_is_correct(question, choice) if question and gradeable(question) else None
            cleaned.append({"choice": choice, "correct": corrected, "at": clean_time(event.get("at")),
                            "reportedCorrect": event.get("correct") if type(event.get("correct")) is bool else None,
                            "gradingStatus": "server-verified" if corrected is not None else "pending-verification",
                            "questionVersion": fingerprint(question) if corrected is not None else None})
        out[qid] = cleaned
    return out


def clean_submission(key, raw):
    if not isinstance(raw, dict) or not PAPER_KEY.fullmatch(str(key)) or not isinstance(raw.get("choices"), dict):
        return None
    submitted_at = clean_time(raw.get("submittedAt"))
    if not submitted_at:
        return None
    source = load_paper(key)
    items = source.get("questions", []) if source else []
    expected = source.get("expectedCount") if source else None
    choices = raw["choices"]
    if type(expected) is not int or expected < 1 or len(items) != expected or set(choices) != {q.get("id") for q in items}:
        return None
    if any(not valid_selection(choices[q["id"]], q) for q in items):
        return None
    started_at = clean_time(raw.get("startedAt"))
    # An absent legacy duration remains unknown; never substitute zero or the current time.
    elapsed = raw.get("elapsedMs")
    if not finite(elapsed) or elapsed < 0 or not started_at:
        elapsed = None
    elif abs(elapsed - (parse_time(submitted_at) - parse_time(started_at)) * 1000) > 1000:
        elapsed = None
    versions = raw.get("questionVersions") if isinstance(raw.get("questionVersions"), dict) else {}
    year, paper = key.split("/", 1)
    return {"id": str(raw.get("id") or "legacy-" + submitted_at)[:100], "year": year, "paper": paper,
            "startedAt": started_at, "submittedAt": submitted_at, "elapsedMs": elapsed, "activeMs": None,
            "timingBasis": "client-reported-elapsed-including-away" if elapsed is not None else "unknown",
            "questionCount": len(choices), "choices": choices, "questionVersions": {q["id"]: str(versions.get(q["id"], ""))[:100] for q in items},
            "ruleVersion": str(raw.get("ruleVersion") or "")[:100] or None, "receivedAt": stamp()}


def clean_state(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid study state")
    out = {"attempts": clean_events(data.get("attempts") or {}), "reviewHistory": clean_events(data.get("reviewHistory") or {}), "examSubmissions": {}, "examSubmissionHistory": {}}
    for field in ("examSubmissions", "examSubmissionHistory"):
        raw = data.get(field) or {}
        if not isinstance(raw, dict) or len(raw) > 300:
            raise ValueError("Invalid submissions")
        for key, value in raw.items():
            values = value if field == "examSubmissionHistory" else [value]
            if not isinstance(values, list) or len(values) > 100:
                raise ValueError("Invalid submission history")
            entries = [cleaned for v in values if (cleaned := clean_submission(key, v)) is not None]
            if entries:
                out[field][key] = entries if field == "examSubmissionHistory" else entries[0]
    return out


def merge_state(old, new):
    """Append-only sync: stopping, repeating or sending an older backup cannot erase server history."""
    result = json.loads(json.dumps(old))
    for field in ("attempts", "reviewHistory"):
        result.setdefault(field, {})
        for qid, entries in new.get(field, {}).items():
            existing = result[field].setdefault(qid, [])
            key = lambda a: json.dumps([a.get("at"), a.get("choice")], ensure_ascii=False)
            available = Counter(key(a) for a in existing)
            for event in entries:
                token = key(event)
                if available[token]:
                    available[token] -= 1
                else:
                    existing.append(event)
    result.setdefault("examSubmissions", {})
    result.setdefault("examSubmissionHistory", {})
    for field in ("examSubmissions", "examSubmissionHistory"):
        for key, raw in new.get(field, {}).items():
            for entry in raw if isinstance(raw, list) else [raw]:
                known = ([result["examSubmissions"][key]] if key in result["examSubmissions"] else []) + result["examSubmissionHistory"].get(key, [])
                if any((x.get("id") == entry.get("id")) if x.get("id") and entry.get("id") else (x.get("submittedAt") == entry.get("submittedAt")) for x in known):
                    continue
                if not known:
                    result["examSubmissions"][key] = entry
                else:
                    result["examSubmissionHistory"].setdefault(key, []).append(entry)
    return result


def original_images(q):
    path = ROOT / "sudu/data/original/index.json"
    if not path.is_file():
        return []
    index = _year_questions(str(path), path.stat().st_mtime_ns)
    paper = index.get("papers", {}).get(f"{q.get('year')}/{q.get('paper')}", {})
    mapping = paper.get("questions", {}).get(q.get("id"), {})
    page = mapping.get("page")
    # A native-text anchor is a candidate page, never a verified question crop.
    selected = [p for p in paper.get("pages", []) if p.get("page") == page] if type(page) is int else paper.get("pages", [])
    output = []
    for image in selected:
        src = image.get("src", "")
        if re.fullmatch(r"data/original/(?:answers/)?\d{2,3}/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.webp", src):
            output.append({"url": "https://homelux-huang.github.io/7581707/sudu/" + src, "page": image.get("page"), "mapping": "頁碼對應待核實；可開啟官方原卷覆核"})
    return output


def question_in_scope(qid, paper_key):
    if not paper_key:
        return True
    q = load_question(qid)
    return bool(q and f"{q.get('year')}/{q.get('paper')}" == paper_key)


def current_event(event, question):
    """Review-time projection only; original event and its old grading evidence stay immutable."""
    if not isinstance(event, dict):
        return None
    result = dict(event)
    current = question and gradeable(question) and event.get("questionVersion") == fingerprint(question) and event.get("gradingStatus") == "server-verified" and valid_selection(event.get("choice"), question)
    if current:
        result["correct"] = answer_is_correct(question, event["choice"])
    else:
        if result.get("correct") is False:
            result["reportedCorrect"] = False
        result["correct"] = None
        result["gradingStatus"] = "pending-verification"
    return result


def summarize(student, db, include_details=False, paper_key=None, shared=False):
    state = json.loads(student["state_json"])
    attempts = {k: v for k, v in state.get("attempts", {}).items() if question_in_scope(k, paper_key)}
    reviews = {k: v for k, v in state.get("reviewHistory", {}).items() if question_in_scope(k, paper_key)}
    submitted = {k: v for k, v in state.get("examSubmissions", {}).items() if not paper_key or k == paper_key}
    first_wrong, events, first_try_wrong = [], [], 0
    for qid in dict.fromkeys([*attempts, *reviews]):
        q = load_question(qid)
        project = lambda items: [result for event in items if (result := current_event(event, q)) is not None] if isinstance(items, list) else []
        log = project(attempts.get(qid, []))
        all_events = log + project(reviews.get(qid, []))
        events.extend(all_events)
        wrong = [a for a in all_events if isinstance(a, dict) and a.get("correct") is False and a.get("gradingStatus") == "server-verified"]
        pending_wrong = [a for a in all_events if isinstance(a, dict) and a.get("gradingStatus") != "server-verified" and (a.get("reportedCorrect") is False or a.get("correct") is False)]
        first_try_wrong += bool(log and log[0].get("correct") is False and log[0].get("gradingStatus") == "server-verified")
        if not wrong and not pending_wrong:
            continue
        if not q:
            continue
        candidates = wrong + pending_wrong
        first = min(candidates, key=lambda a: parse_time(a.get("at")) if parse_time(a.get("at")) is not None else float("inf"))
        textbook = q.get("textbook") if isinstance(q.get("textbook"), dict) else {}
        first_wrong.append({"id": qid, "paper": f"{q.get('year')}/{q.get('paper')}", "question": q.get("question"), "options": q.get("options"), "subject": q.get("subject"),
                            "firstChoice": first.get("choice"), "firstAt": first.get("at"), "answer": accepted(q) if gradeable(q) else None,
                            "wrongCount": len(wrong), "reportedWrongCount": len(pending_wrong), "gradingStatus": "server-verified" if wrong else "pending-verification", "originalImages": original_images(q), "explanation": q.get("explanation") if q.get("teachingVerified") else "白話詳解待核實",
                            "principle": q.get("principle") if q.get("teachingVerified") else "N/A", "steps": q.get("steps") if q.get("teachingVerified") else "N/A",
                            "optionReasons": q.get("optionReasons") if q.get("teachingVerified") else "N/A", "practice": q.get("practice") if q.get("teachingVerified") else None,
                            "source": q.get("source"), "page": q.get("page"), "chapter": textbook.get("chapter") if q.get("textbookVerified") else "精確章節待核實"})
    scores = []
    for key, first in submitted.items():
        entries = [first] + state.get("examSubmissionHistory", {}).get(key, [])
        for entry in entries:
            correction = db.execute("SELECT * FROM adjustments WHERE student_id=? AND paper_key=? AND (submission_id=? OR submission_id IS NULL) ORDER BY id DESC LIMIT 1", (student["id"], key, entry.get("id"))).fetchone()
            computed = official_score_details(key, entry)
            scores.append({"paper": key, "submissionId": entry.get("id"), "submittedAt": entry.get("submittedAt"), "startedAt": entry.get("startedAt"), "elapsedMs": entry.get("elapsedMs"), "activeMs": None,
                           "questionCount": entry.get("questionCount"), "score": computed["score"], "maxScore": computed.get("maxScore"), "objectiveScore": computed.get("objectiveScore"), "objectiveMax": computed.get("objectiveMax"),
                           "scoreStatus": "官方規則計算" if computed["status"] == "scored" else computed["reason"], "ruleVersion": computed.get("ruleVersion"),
                           "adjustedScore": correction["new_score"] if correction else None, "adjustmentReason": correction["reason"] if correction else None, "isOfficialScore": computed["status"] == "scored"})
    dates = [a["at"] for a in events if isinstance(a, dict) and parse_time(a.get("at")) is not None]
    result = {"nickname": "指定範圍學習報告" if shared else student["nickname"], "scope": paper_key or "all-consented-study-records",
              "answeredQuestions": sum(bool(attempts.get(qid) or reviews.get(qid)) for qid in set(attempts) | set(reviews)), "submittedPapers": len(submitted), "submissionCount": len(scores),
              "firstWrongCount": len(first_wrong), "verifiedWrongQuestionCount": sum(q["wrongCount"] > 0 for q in first_wrong), "reportedWrongQuestionCount": sum(q["reportedWrongCount"] > 0 for q in first_wrong), "firstAttemptWrongCount": first_try_wrong, "wrongEventCount": sum(q["wrongCount"] for q in first_wrong),
              "pendingGradingEvents": sum(a.get("correct") is None for a in events if isinstance(a, dict)),
              "firstAt": min(dates, key=parse_time) if dates else None, "lastAt": max(dates, key=parse_time) if dates else None, "scores": scores}
    if not shared:
        result.update(id=student["id"], updatedAt=stamp(student["updated"]))
    if include_details:
        result["firstWrong"] = first_wrong
        if not shared:
            result["adjustments"] = [dict(r) for r in db.execute("SELECT id,paper_key,old_score,new_score,reason,source,created,admin,submission_id,rule_version,official_score FROM adjustments WHERE student_id=? ORDER BY id", (student["id"],))]
    return result


def limited(key, limit, window=300):
    with LOCK:
        recent = [x for x in FAILURES.get(key, []) if x > now() - window]
        if len(recent) >= limit:
            return True
        FAILURES[key] = recent + [now()]
        if len(FAILURES) > 10_000:
            for k in list(FAILURES):
                if not any(t > now() - 3600 for t in FAILURES[k]):
                    FAILURES.pop(k, None)
        return False


class Handler(BaseHTTPRequestHandler):
    server_version = "SUDUAdmin/2.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, *args):
        pass  # Access paths can contain private share tokens.

    def common_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        if not DEV:
            self.send_header("Strict-Transport-Security", "max-age=31536000")

    def reply(self, code, payload, headers=None):
        raw = b"" if code == 204 else json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.common_headers()
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        origin = self.headers.get("Origin", "")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "authorization, content-type, x-csrf-token")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if raw:
            self.wfile.write(raw)

    def read_json(self):
        if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/json":
            raise ValueError("Content-Type must be application/json")
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_BODY:
            raise ValueError("Invalid request size")
        value = json.loads(self.rfile.read(length), parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Non-finite number")))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def origin_ok(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        host = self.headers.get("Host", "")
        parsed = urlparse(origin)
        return origin in ORIGINS or (parsed.scheme == ("http" if DEV else "https") and parsed.netloc == host and not parsed.path)

    def session(self):
        match = re.search(r"(?:^|;\s*)sudu_session=([A-Za-z0-9_-]{20,120})(?:;|$)", self.headers.get("Cookie", ""))
        if not match:
            return None
        with LOCK, connect() as db:
            return db.execute("SELECT s.* FROM sessions s JOIN admins a ON a.username=s.username WHERE token_hash=? AND expires>?", (digest(match[1]), now())).fetchone()

    def guard(self, write=False):
        session = self.session()
        if not session or write and not hmac.compare_digest(self.headers.get("X-CSRF-Token", ""), session["csrf"]):
            return None
        return session

    def student(self, db):
        header = self.headers.get("Authorization", "")
        if not re.fullmatch(r"Bearer [A-Za-z0-9_-]{30,120}", header):
            return None
        return db.execute("SELECT * FROM students WHERE token_hash=?", (digest(header[7:]),)).fetchone()

    def cookie(self, token, age=SESSION_SECONDS):
        return "sudu_session=" + token + "; HttpOnly; SameSite=Strict; Path=/; Max-Age=" + str(age) + ("" if DEV else "; Secure")

    def do_OPTIONS(self):
        self.reply(204 if self.origin_ok() else 403, {})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.reply(200, {"status": "ok", "service": "7581707 private admin API", "schema": 2})
            return
        if path in ("/admin", "/admin/") or re.fullmatch(r"/share/[A-Za-z0-9_-]{30,120}", path):
            content = (ROOT / "sudu" / ("share.html" if path.startswith("/share/") else "admin.html")).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' https://homelux-huang.github.io; base-uri 'none'; frame-ancestors 'none'")
            self.common_headers()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if path.startswith("/api/share/"):
            token = path.split("/")[-1]
            with LOCK, connect() as db:
                share = db.execute("SELECT * FROM shares WHERE token_hash=? AND expires>?", (digest(token), now())).fetchone()
                student = db.execute("SELECT * FROM students WHERE id=?", (share["student_id"],)).fetchone() if share else None
                if not student:
                    self.reply(404, {"error": "分享連結不存在、已撤銷或已到期"})
                    return
                self.reply(200, {"report": summarize(student, db, True, share["paper_key"], True), "expiresAt": stamp(share["expires"])})
            return
        if path.startswith("/api/admin/"):
            session = self.guard()
            if not session:
                self.reply(401, {"error": "未授權，請先登入"})
                return
            with LOCK, connect() as db:
                account = db.execute("SELECT must_change FROM admins WHERE username=?", (session["username"],)).fetchone()
                if path == "/api/admin/me":
                    self.reply(200, {"username": session["username"], "mustChange": bool(account["must_change"]), "csrf": session["csrf"]})
                    return
                if account["must_change"]:
                    self.reply(403, {"error": "必須先更改初始密碼"})
                    return
                if path == "/api/admin/students":
                    rows = db.execute("SELECT * FROM students ORDER BY updated DESC LIMIT 200").fetchall()
                    self.reply(200, {"students": [summarize(row, db) for row in rows]})
                    return
                sid = parse_qs(urlparse(self.path).query).get("id", [""])[0]
                student = db.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
                if path == "/api/admin/student":
                    self.reply(200 if student else 404, {"student": summarize(student, db, True)} if student else {"error": "找不到學生"})
                    return
                if path == "/api/admin/shares" and student:
                    rows = db.execute("SELECT token_hash AS shareId,paper_key AS paper,expires,created FROM shares WHERE student_id=? ORDER BY created DESC", (sid,)).fetchall()
                    self.reply(200, {"shares": [dict(r) for r in rows]})
                    return
        self.reply(404, {"error": "Unknown endpoint"})

    def do_POST(self):
        if not self.origin_ok():
            self.reply(403, {"error": "Origin not allowed"})
            return
        try:
            data = self.read_json()
        except (ValueError, TypeError, UnicodeError) as error:
            self.reply(400, {"error": str(error)})
            return
        path = urlparse(self.path).path
        if path == "/api/students/enroll":
            if limited("enroll:" + self.client_address[0], 20, 3600):
                self.reply(429, {"error": "建立紀錄次數過多，請稍後"})
                return
            sid, token = "stu_" + secrets.token_urlsafe(16), secrets.token_urlsafe(32)
            with LOCK, connect() as db:
                db.execute("INSERT INTO students VALUES(?,?,?,?,?,?)", (sid, digest(token), str(data.get("nickname") or "學習者")[:50], now(), now(), json.dumps({"attempts": {}, "examSubmissions": {}})))
                audit(db, sid, "enroll-consent", sid)
                db.commit()
            self.reply(201, {"studentId": sid, "accessToken": token})
            return
        if path.startswith("/api/students/"):
            with LOCK, connect() as db:
                row = self.student(db)
                if not row:
                    self.reply(401, {"error": "學習同步權杖無效或已撤銷"})
                    return
                if path == "/api/students/sync":
                    try:
                        cleaned = clean_state(data.get("state"))
                        merged = merge_state(json.loads(row["state_json"]), cleaned)
                        serialized = json.dumps(merged, ensure_ascii=False, allow_nan=False)
                        if len(serialized.encode()) > MAX_BODY * 4:
                            raise ValueError("Server history capacity exceeded; contact the administrator without deleting existing records")
                    except (ValueError, TypeError) as error:
                        self.reply(400, {"error": str(error)})
                        return
                    db.execute("UPDATE students SET nickname=?,updated=?,state_json=? WHERE id=?", (str(data.get("nickname") or row["nickname"])[:50], now(), serialized, row["id"]))
                    db.commit()
                    self.reply(200, {"ok": True, "syncedAt": stamp(), "notice": "判分由伺服器核對；未核實題目保留作答並標待核對"})
                    return
                if path in ("/api/students/revoke", "/api/students/delete"):
                    db.execute("DELETE FROM shares WHERE student_id=?", (row["id"],))
                    if path.endswith("delete"):
                        db.execute("DELETE FROM adjustments WHERE student_id=?", (row["id"],))
                        db.execute("DELETE FROM audit WHERE student_id=?", (row["id"],))
                        db.execute("DELETE FROM students WHERE id=?", (row["id"],))
                    else:
                        db.execute("UPDATE students SET token_hash='',updated=? WHERE id=?", (now(), row["id"]))
                        audit(db, row["id"], "revoke-student-token-and-shares", row["id"])
                    db.commit()
                    self.reply(200, {"ok": True, "deleted": path.endswith("delete"), "revoked": True})
                    return
            self.reply(404, {"error": "Unknown student action"})
            return
        if path == "/api/admin/login":
            rate_key = "login:" + self.client_address[0]
            if limited(rate_key, 5):
                self.reply(429, {"error": "登入次數過多，請稍後"})
                return
            username, password = str(data.get("username", ""))[:100], str(data.get("password", ""))[:1000]
            with LOCK, connect() as db:
                account = db.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
                if not account or not verify(password, account["password"]):
                    self.reply(401, {"error": "帳號或密碼錯誤"})
                    return
                FAILURES.pop(rate_key, None)
                token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
                db.execute("DELETE FROM sessions WHERE expires<=?", (now(),))
                db.execute("INSERT INTO sessions VALUES(?,?,?,?)", (digest(token), username, csrf, now() + SESSION_SECONDS))
                audit(db, username, "admin-login")
                db.commit()
            self.reply(200, {"username": username, "mustChange": bool(account["must_change"]), "csrf": csrf}, {"Set-Cookie": self.cookie(token)})
            return
        if path.startswith("/api/admin/"):
            session = self.guard(True)
            if not session:
                self.reply(401, {"error": "未登入、Session 到期或 CSRF 驗證失敗"})
                return
            with LOCK, connect() as db:
                account = db.execute("SELECT * FROM admins WHERE username=?", (session["username"],)).fetchone()
                if path == "/api/admin/logout":
                    db.execute("DELETE FROM sessions WHERE token_hash=?", (session["token_hash"],))
                    audit(db, session["username"], "admin-logout")
                    db.commit()
                    self.reply(200, {"ok": True}, {"Set-Cookie": self.cookie("", 0)})
                    return
                if path == "/api/admin/change-password":
                    password = str(data.get("newPassword", ""))
                    if not 12 <= len(password) <= 1000 or password == str(data.get("oldPassword", "")):
                        self.reply(400, {"error": "新密碼需至少 12 字元，且不能與舊密碼相同"})
                        return
                    if limited("change-password:" + session["username"], 5) or not verify(str(data.get("oldPassword", "")), account["password"]):
                        self.reply(403, {"error": "原密碼不正確或嘗試次數過多"})
                        return
                    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
                    db.execute("UPDATE admins SET password=?,must_change=0 WHERE username=?", (password_hash(password), session["username"]))
                    db.execute("DELETE FROM sessions WHERE username=?", (session["username"],))
                    db.execute("INSERT INTO sessions VALUES(?,?,?,?)", (digest(token), session["username"], csrf, now() + SESSION_SECONDS))
                    audit(db, session["username"], "change-password-and-rotate-session")
                    db.commit()
                    self.reply(200, {"ok": True, "csrf": csrf}, {"Set-Cookie": self.cookie(token)})
                    return
                if account["must_change"]:
                    self.reply(403, {"error": "必須先修改初始密碼"})
                    return
                sid = str(data.get("studentId", ""))
                student = db.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
                if not student:
                    self.reply(404, {"error": "學生紀錄不存在或未同意同步"})
                    return
                state = json.loads(student["state_json"])
                if path == "/api/admin/adjust":
                    paper, reason, source = str(data.get("paper", ""))[:60], str(data.get("reason", "")).strip()[:300], str(data.get("source", ""))[:1000]
                    points = data.get("score")
                    entries = ([state["examSubmissions"][paper]] if paper in state.get("examSubmissions", {}) else []) + state.get("examSubmissionHistory", {}).get(paper, [])
                    entry = next((x for x in entries if x.get("id") == data.get("submissionId")), None) if data.get("submissionId") else (entries[-1] if entries else None)
                    if not entry or not finite(points) or not 0 <= points <= 1000 or len(reason) < 8 or not valid_https(source):
                        self.reply(400, {"error": "須選已送出試卷，填寫有效分數、至少 8 字理由及 HTTPS 依據"})
                        return
                    computed = official_score_details(paper, entry)
                    if finite(computed.get("maxScore")) and points > computed["maxScore"]:
                        self.reply(400, {"error": "調整分數不可高於已核實整卷滿分"})
                        return
                    old = db.execute("SELECT new_score FROM adjustments WHERE student_id=? AND paper_key=? AND submission_id=? ORDER BY id DESC LIMIT 1", (sid, paper, entry.get("id"))).fetchone()
                    old_score = old["new_score"] if old else computed["score"]
                    db.execute("INSERT INTO adjustments(student_id,paper_key,old_score,new_score,reason,source,created,admin,submission_id,rule_version,official_score) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (sid, paper, old_score, points, reason, source, now(), session["username"], entry.get("id"), computed.get("ruleVersion"), computed["score"]))
                    audit(db, session["username"], "adjust-score", sid, paper, oldScore=old_score, newScore=points, submissionId=entry.get("id"), ruleVersion=computed.get("ruleVersion"), reason=reason, source=source)
                    db.commit()
                    self.reply(200, {"ok": True, "notice": "管理員調整與官方計算分數分開留存，未修改學生答案"})
                    return
                if path == "/api/admin/share":
                    paper = str(data.get("paper") or "")[:60] or None
                    has_scope = not paper or paper in state.get("examSubmissions", {}) or any(question_in_scope(qid, paper) for qid in set(state.get("attempts", {})) | set(state.get("reviewHistory", {})))
                    if not has_scope or paper and not PAPER_KEY.fullmatch(paper):
                        self.reply(400, {"error": "指定試卷不存在於此學生的同意同步紀錄"})
                        return
                    token, expires = secrets.token_urlsafe(30), now() + 7 * 86400
                    db.execute("INSERT INTO shares VALUES(?,?,?,?,?)", (digest(token), sid, paper, expires, now()))
                    audit(db, session["username"], "create-scoped-share", sid, paper, shareId=digest(token), expires=expires)
                    db.commit()
                    base = PUBLIC_BASE or (f"http://127.0.0.1:{self.server.server_port}" if DEV else "")
                    self.reply(201, {"url": base + "/share/" + token if base else None, "token": token, "shareId": digest(token), "expiresAt": stamp(expires)})
                    return
                if path == "/api/admin/revoke-share":
                    db.execute("DELETE FROM shares WHERE student_id=? AND token_hash=?", (sid, str(data.get("shareId", ""))))
                    audit(db, session["username"], "revoke-share", sid, shareId=str(data.get("shareId", ""))[:100])
                    db.commit()
                    self.reply(200, {"ok": True})
                    return
                if path == "/api/admin/delete-student":
                    db.execute("DELETE FROM shares WHERE student_id=?", (sid,))
                    db.execute("DELETE FROM adjustments WHERE student_id=?", (sid,))
                    db.execute("DELETE FROM audit WHERE student_id=?", (sid,))
                    db.execute("DELETE FROM students WHERE id=?", (sid,))
                    audit(db, session["username"], "delete-student-record", deletedRecords=1)
                    db.commit()
                    self.reply(200, {"ok": True, "deleted": True})
                    return
        self.reply(404, {"error": "Unknown endpoint"})


if __name__ == "__main__":
    initialize()
    host, port = ("127.0.0.1" if DEV else "0.0.0.0"), int(os.environ.get("PORT", "8787"))
    print(f"SUDU private admin listening on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
