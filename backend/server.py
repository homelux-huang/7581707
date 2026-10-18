#!/usr/bin/env python3
"""7581707 private admin API. Standard library only; deploy separately from public GitHub Pages."""
from __future__ import annotations
import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get("SUDU_DB_PATH",str(ROOT/"backend"/"private.sqlite3")))
ADMIN=os.environ.get("SUDU_ADMIN_USER","admin")
BOOTSTRAP=os.environ.get("SUDU_ADMIN_INITIAL_PASSWORD","")
DEV=os.environ.get("SUDU_DEV_ALLOW_ADMIN_ADMIN")=="1"
PUBLIC_BASE=os.environ.get("SUDU_ADMIN_PUBLIC_URL","").rstrip("/")
ORIGINS=set(x.strip() for x in os.environ.get("SUDU_ALLOWED_ORIGINS","https://homelux-huang.github.io").split(",") if x.strip())
LOCK=threading.RLock()
FAILURES={}
MAX_BODY=1_100_000
def now():return int(time.time())
def stamp(t=None):return datetime.fromtimestamp(t or now(),timezone.utc).isoformat()
def digest(token):return hashlib.sha256(token.encode()).hexdigest()
def password_hash(secret,salt=None):
    salt=salt or secrets.token_bytes(16)
    return base64.b64encode(salt).decode()+":"+hashlib.pbkdf2_hmac("sha256",secret.encode(),salt,450_000).hex()
def verify(secret,stored):
    try:
        salt,hashvalue=stored.split(":",1)
        actual=password_hash(secret,base64.b64decode(salt)).split(":",1)[1]
        return hmac.compare_digest(actual,hashvalue)
    except (ValueError,TypeError):return False
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(str(DB),timeout=20)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn
def initialize():
    if not BOOTSTRAP and not DEV:raise RuntimeError("Set SUDU_ADMIN_INITIAL_PASSWORD in private environment; no public fallback password")
    if not BOOTSTRAP and DEV:secret="admin"
    else:secret=BOOTSTRAP
    if not DEV and (len(secret)<12 or secret=="admin"):raise RuntimeError("Production admin password must be 12+ characters and not 'admin'")
    with LOCK,connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admins(username TEXT PRIMARY KEY, password TEXT NOT NULL, must_change INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,username TEXT NOT NULL,csrf TEXT NOT NULL,expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS students(id TEXT PRIMARY KEY,token_hash TEXT NOT NULL, nickname TEXT NOT NULL,created INTEGER NOT NULL,updated INTEGER NOT NULL,state_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS adjustments(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,paper_key TEXT NOT NULL,old_score REAL,new_score REAL NOT NULL,reason TEXT NOT NULL,source TEXT NOT NULL,created INTEGER NOT NULL,admin TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS shares(token_hash TEXT PRIMARY KEY,student_id TEXT NOT NULL,paper_key TEXT,expires INTEGER NOT NULL,created INTEGER NOT NULL);
        """)
        if not db.execute("SELECT 1 FROM admins WHERE username=?",(ADMIN,)).fetchone():
            db.execute("INSERT INTO admins VALUES(?,?,1)",(ADMIN,password_hash(secret)))
        db.commit()
def load_question(id):
    if not re.fullmatch(r"[A-Za-z0-9_一-龥－—-]{1,180}",str(id)):return None
    m=re.match(r"^(\d{2,3})-",id)
    if not m:return None
    p=ROOT/"sudu"/"data"/"years"/(m[1]+".json")
    if not p.is_file():return None
    try:
        for paper in json.loads(p.read_text("utf-8")).get("papers",[]):
            for q in paper.get("questions",[]):
                if q.get("id")==id:return q
    except (ValueError,OSError):pass
    return None
def summarize(student,db,include_details=False):
    st=json.loads(student["state_json"]);attempts=st.get("attempts") or {};submitted=st.get("examSubmissions") or {}
    count=sum(bool(v) for v in attempts.values() if isinstance(v,list))
    first_wrong=[]
    for id,attempt_list in list(attempts.items())[:20_000]:
        if not isinstance(attempt_list,list) or not attempt_list or not isinstance(attempt_list[0],dict) or attempt_list[0].get("correct") is not False:continue
        q=load_question(id)
        if not q:continue
        first_wrong.append({"id":id,"question":q.get("question"),"subject":q.get("subject"),"firstChoice":attempt_list[0].get("choice"),
         "firstAt":attempt_list[0].get("at"),"answer":q.get("answer") if q.get("answerVerified") else None,
         "wrongCount":sum(a.get("correct") is False for a in attempt_list if isinstance(a,dict)),
         "explanation":q.get("explanation") if q.get("teachingVerified") else "白話詳解待核實",
         "source":q.get("source"),"chapter":q.get("textbook",{}).get("chapter") if isinstance(q.get("textbook"),dict) else "精確章節待核實"})
    scores=[]
    for key,entry in submitted.items():
        if not isinstance(entry,dict):continue
        correction=db.execute("SELECT new_score,reason,created,source FROM adjustments WHERE student_id=? AND paper_key=? ORDER BY id DESC LIMIT 1",(student["id"],key)).fetchone()
        scores.append({"paper":key,"submittedAt":entry.get("submittedAt"),"startedAt":entry.get("startedAt"),"elapsedMs":entry.get("elapsedMs"),"questionCount":entry.get("questionCount"),
                       "score":None,"scoreStatus":"正式配分規則待核實","adjustedScore":correction["new_score"] if correction else None,
                       "adjustmentReason":correction["reason"] if correction else None,"isOfficialScore":False})
    dates=[a.get("at") for log in attempts.values() if isinstance(log,list) for a in log if isinstance(a,dict) and a.get("at")]
    result={"id":student["id"],"nickname":student["nickname"],"updatedAt":stamp(student["updated"]),
            "answeredQuestions":count,"submittedPapers":len(submitted),"firstWrongCount":len(first_wrong),
            "firstAt":min(dates) if dates else None,"lastAt":max(dates) if dates else None,"scores":scores}
    if include_details:result["firstWrong"]=first_wrong[:1000]
    return result
def clean_state(data):
    if not isinstance(data,dict):raise ValueError("Invalid study state")
    attempts=data.get("attempts") or {}
    if not isinstance(attempts,dict) or len(attempts)>20_000:raise ValueError("Invalid attempt history")
    out={}
    for k,v in attempts.items():
        if not isinstance(k,str) or len(k)>180 or not isinstance(v,list):continue
        out[k]=[{"choice":a.get("choice"),"correct":a.get("correct"),"at":str(a.get("at",""))[:40]}
         for a in v[-1200:] if isinstance(a,dict) and type(a.get("choice")) is int and 0<=a["choice"]<=3 and type(a.get("correct")) is bool]
    submissions={}
    for k,v in (data.get("examSubmissions") or {}).items():
        if not isinstance(k,str) or len(k)>60 or not isinstance(v,dict):continue
        submissions[k]={"year":str(v.get("year",""))[:4],"paper":str(v.get("paper",""))[:50],
         "startedAt":str(v.get("startedAt",""))[:40],"submittedAt":str(v.get("submittedAt",""))[:40],
         "elapsedMs":max(0,min(10**10,int(v.get("elapsedMs") or 0))),"questionCount":max(0,min(2000,int(v.get("questionCount") or 0)))}
    return {"attempts":out,"examSubmissions":submissions}
class Handler(BaseHTTPRequestHandler):
    server_version="SUDUAdmin/1.0"
    def log_message(self,*args):pass
    def reply(self,code,payload,headers=None):
        raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
        self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","no-referrer")
        for k,v in (headers or {}).items():self.send_header(k,v)
        origin=self.headers.get("Origin","")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin",origin)
            self.send_header("Vary","Origin")
            self.send_header("Access-Control-Allow-Headers","authorization, content-type, x-csrf-token")
            self.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS")
        self.end_headers();self.wfile.write(raw)
    def read_json(self):
        length=int(self.headers.get("Content-Length","0"))
        if length<=0 or length>MAX_BODY:raise ValueError("Invalid request size")
        return json.loads(self.rfile.read(length))
    def session(self):
        cookie=self.headers.get("Cookie","")
        m=re.search(r"(?:^|;\s*)sudu_session=([A-Za-z0-9_-]{20,120})",cookie)
        if not m:return None
        with LOCK,connect() as db:
            row=db.execute("SELECT * FROM sessions WHERE token_hash=? AND expires>?",(digest(m[1]),now())).fetchone()
            if not row:return None
            return row
    def guard(self,write=False):
        auth=self.session()
        if not auth:return None
        if write and not hmac.compare_digest(self.headers.get("X-CSRF-Token",""),auth["csrf"]):return None
        return auth
    def origin_ok(self):
        origin=self.headers.get("Origin")
        host=self.headers.get("Host","")
        return not origin or origin in ORIGINS or urlparse(origin).netloc==host
    def do_OPTIONS(self):
        if not self.origin_ok():self.reply(403,{"error":"Origin not allowed"});return
        self.reply(204,{})
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health":self.reply(200,{"status":"ok","service":"7581707 private admin API"});return
        if path in ["/admin","/admin/"] or path.startswith("/share/"):
            p=ROOT/"sudu"/("share.html" if path.startswith("/share/") else "admin.html")
            content=p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Content-Length",str(len(content)));self.end_headers();self.wfile.write(content);return
        if path.startswith("/api/share/"):
            token=path.split("/")[-1]
            with LOCK,connect() as db:
                share=db.execute("SELECT * FROM shares WHERE token_hash=? AND expires>?",(digest(token),now())).fetchone()
                if not share:self.reply(404,{"error":"分享連結不存在或已到期"});return
                st=db.execute("SELECT * FROM students WHERE id=?",(share["student_id"],)).fetchone()
                if not st:self.reply(404,{"error":"學習紀錄不存在"});return
                report=summarize(st,db,True)
                if share["paper_key"]:
                    report["scores"]=[q for q in report["scores"] if q["paper"]==share["paper_key"]]
                self.reply(200,{"report":report,"expiresAt":stamp(share["expires"])})
            return
        if path=="/api/admin/me":
            session=self.guard()
            if not session:self.reply(401,{"error":"請先安全登入"});return
            with connect() as db:account=db.execute("SELECT must_change FROM admins WHERE username=?",(session["username"],)).fetchone()
            self.reply(200,{"username":session["username"],"mustChange":bool(account["must_change"]),"csrf":session["csrf"]})
            return
        if path.startswith("/api/admin/"):
            session=self.guard()
            if not session:self.reply(401,{"error":"未授權"});return
            with LOCK,connect() as db:
                account=db.execute("SELECT must_change FROM admins WHERE username=?",(session["username"],)).fetchone()
                if account["must_change"]:self.reply(403,{"error":"必須先更改初始密碼"});return
                if path=="/api/admin/students":
                    rows=db.execute("SELECT * FROM students ORDER BY updated DESC LIMIT 200").fetchall()
                    self.reply(200,{"students":[summarize(x,db) for x in rows]});return
                if path=="/api/admin/student":
                    sid=parse_qs(urlparse(self.path).query).get("id",[""])[0]
                    student=db.execute("SELECT * FROM students WHERE id=?",(sid,)).fetchone()
                    self.reply(200,{"student":summarize(student,db,True)} if student else {"error":"找不到學生"});return
            self.reply(404,{"error":"Unknown endpoint"});return
        self.reply(404,{"error":"Unknown endpoint"})
    def do_POST(self):
        path=urlparse(self.path).path
        if not self.origin_ok():self.reply(403,{"error":"Origin not allowed"});return
        try:data=self.read_json()
        except (ValueError,TypeError) as e:self.reply(400,{"error":str(e)});return
        if path=="/api/students/enroll":
            student_id="stu_"+secrets.token_urlsafe(16);token=secrets.token_urlsafe(32)
            with LOCK,connect() as db:
                db.execute("INSERT INTO students VALUES(?,?,?,?,?,?)",(student_id,digest(token),str(data.get("nickname") or "學習者")[:50],now(),now(),json.dumps({"attempts":{},"examSubmissions":{}})));db.commit()
            self.reply(201,{"studentId":student_id,"accessToken":token,"message":"已建立自願同步記錄；請保管權杖"});return
        if path=="/api/students/sync":
            token=self.headers.get("Authorization","").removeprefix("Bearer ").strip()
            try:clean=clean_state(data.get("state"))
            except (ValueError,TypeError) as e:self.reply(400,{"error":str(e)});return
            with LOCK,connect() as db:
                row=db.execute("SELECT * FROM students WHERE token_hash=?",(digest(token),)).fetchone()
                if not row:self.reply(401,{"error":"學習同步權杖無效"});return
                db.execute("UPDATE students SET nickname=?,updated=?,state_json=? WHERE id=?",
                           (str(data.get("nickname") or row["nickname"])[:50],now(),json.dumps(clean,ensure_ascii=False),row["id"]));db.commit()
            self.reply(200,{"ok":True,"syncedAt":stamp()});return
        if path=="/api/admin/login":
            ip=self.client_address[0]; recent=[x for x in FAILURES.get(ip,[]) if x>now()-300]
            if len(recent)>=5:self.reply(429,{"error":"登入次數過多，請稍後"});return
            username=str(data.get("username",""));secret=str(data.get("password",""))
            with LOCK,connect() as db:account=db.execute("SELECT * FROM admins WHERE username=?",(username,)).fetchone()
            if not account or not verify(secret,account["password"]):
                FAILURES[ip]=recent+[now()];self.reply(401,{"error":"帳號或密碼錯誤"});return
            FAILURES.pop(ip,None)
            token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(24)
            with LOCK,connect() as db:
                db.execute("INSERT INTO sessions VALUES(?,?,?,?)",(digest(token),username,csrf,now()+3600*8));db.commit()
            secure="" if DEV else "; Secure"
            headers={"Set-Cookie":"sudu_session="+token+"; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800"+secure}
            self.reply(200,{"username":username,"mustChange":bool(account["must_change"]),"csrf":csrf},headers);return
        if path.startswith("/api/admin/"):
            session=self.guard(True)
            if not session:self.reply(401,{"error":"未登入或 CSRF 驗證失敗"});return
            with LOCK,connect() as db:
                account=db.execute("SELECT * FROM admins WHERE username=?",(session["username"],)).fetchone()
                if path=="/api/admin/change-password":
                    pw=str(data.get("newPassword",""))
                    if len(pw)<12 or pw.lower()=="admin" or pw==str(data.get("oldPassword","")):
                        self.reply(400,{"error":"新密碼需至少 12 字元，且不能與舊密碼相同"});return
                    if not verify(str(data.get("oldPassword","")),account["password"]):
                        self.reply(403,{"error":"原密碼不正確"});return
                    db.execute("UPDATE admins SET password=?,must_change=0 WHERE username=?",(password_hash(pw),session["username"]))
                    db.execute("DELETE FROM sessions WHERE username=? AND token_hash<>?",(session["username"],self.session()["token_hash"]))
                    db.commit();self.reply(200,{"ok":True});return
                if account["must_change"]:self.reply(403,{"error":"必須先修改初始密碼"});return
                sid=str(data.get("studentId",""));student=db.execute("SELECT * FROM students WHERE id=?",(sid,)).fetchone()
                if not student:self.reply(404,{"error":"學生紀錄不存在或未同意同步"});return
                if path=="/api/admin/adjust":
                    paper=str(data.get("paper",""))[:60];reason=str(data.get("reason","")).strip()[:300];source=str(data.get("source",""))[:400]
                    try:points=float(data.get("score"))
                    except (ValueError,TypeError):points=-1
                    if not (0<=points<=1000) or len(reason)<8 or not paper:
                        self.reply(400,{"error":"分數範圍 0-1000，須填寫試卷及至少 8 字更正理由"});return
                    state=json.loads(student["state_json"])
                    if paper not in (state.get("examSubmissions") or {}):
                        self.reply(400,{"error":"尚未送出的試卷不得人工改分"});return
                    old=db.execute("SELECT new_score FROM adjustments WHERE student_id=? AND paper_key=? ORDER BY id DESC LIMIT 1",(sid,paper)).fetchone()
                    db.execute("INSERT INTO adjustments(student_id,paper_key,old_score,new_score,reason,source,created,admin) VALUES (?,?,?,?,?,?,?,?)",
                               (sid,paper,old["new_score"] if old else None,points,reason,source,now(),session["username"]))
                    db.commit();self.reply(200,{"ok":True,"notice":"管理員修正分數（非官方成績），保留調整稽核紀錄"});return
                if path=="/api/admin/share":
                    paper=str(data.get("paper") or "")[:60] or None
                    token=secrets.token_urlsafe(30)
                    db.execute("INSERT INTO shares VALUES(?,?,?,?,?)",(digest(token),sid,paper,now()+7*86400,now()));db.commit()
                    base=PUBLIC_BASE or ("http://127.0.0.1:"+str(self.server.server_port) if DEV else "")
                    self.reply(201,{"url":base+"/share/"+token if base else None,"token":token,"expiresAt":stamp(now()+7*86400)})
                    return
            self.reply(404,{"error":"Unknown action"});return
        self.reply(404,{"error":"Unknown endpoint"})
if __name__=="__main__":
    initialize()
    host="127.0.0.1" if DEV else "0.0.0.0"
    port=int(os.environ.get("PORT","8787"))
    print("SUDU private admin listening on "+host+":"+str(port),flush=True)
    ThreadingHTTPServer((host,port),Handler).serve_forever()
