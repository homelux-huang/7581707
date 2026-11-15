#!/usr/bin/env python3
"""106 English Q13-18: preserve first already-run English OCR and direct-image corrected text.

Only six images initially without OCR/text. Does NOT redo OCR on identical SHA.
Manual correction checked against original official page and its exact WebP,
not a teaching explanation. Updates isolated processed/106 QA JSON+SQLite only.
"""
import argparse,difflib,hashlib,json,sqlite3,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("sudu/data/processed/106")
BRANCH="qa/114-115-official-visual-review"
EVIDENCE=BASE/"qa-drafts/QA_106_EN_Q13_18_DIRECT_VISUAL_SHA_20261023.json"
OUT=BASE/"qa-drafts/QA_106_EN_Q13_18_OCR_DIRECT_TEXT_20261023.json"
TEXT={
13:{
"question":"Clerk: How can I help you?\nCustomer: Yes, this desk lamp was broken when I tried to turn it on at home.\nClerk: ________\nCustomer: Great, thanks for your assistance.",
"options":["Believe it or not, it’s just been bought.","I’m sorry, but I can replace it for you.","It seems you’re interested in the house.","The mechanic will fix your car in no time."],
"raw":"13. Clerk: How can I help you?\nCustomer: Yes, this desk lamp was broken when I tried to turn it on at home.\nClerk:\nCustomer: Great, thanks for your assistance.\n(A) Believe it or not, it’s just been bought.\n(B) I’m sorry, but I can replace it for you.\n(C) It seems you’re interested in the house.\n(D) The mechanic will fix your car in no time.\n",
"note":"Tesseract omitted the blank response line; restored exact original fill-in blank."
},
14:{
"question":"Fred: Oops! I left my workbook at home!\nJamie: ________ Ms. Kim reminded us just yesterday about it.\nFred: There isn’t much I can do. It’s too late for me to go back home now.\nJamie: Ms. Kim will be very upset.",
"options":["Salaries have not gone up.","You are in trouble, my friend.","He left the bookstore yesterday.","Consider the assignment done."],
"raw":"14. Fred: — Oops! I left my workbook at home!\nJamie: Ms. Kim reminded us just yesterday about it.\nFred: There isn’t much I can do. It’s too late for me to go back home now.\nJamie: Ms. Kim will be very upset.\n(A) Salaries have not gone up. (B) You are in trouble, my friend.\n(C) He left the bookstore yesterday. (D) Consider the assignment done.\n",
"note":"Tesseract omitted blank and inserted stray dash before Oops; split two-column choices into exact A-D."
},
15:{
"question":"Zax: What are today’s headlines?\nClaire: Super Junior canceled tomorrow’s concert.\nZax: ________\nClaire: You bet. So many fans like me were very excited about seeing their show.",
"options":["It sounds like you’re not into music.","How many fans will be attending it?","Who are the members of the band?","You must feel terribly disappointed."],
"raw":"15. Zax: What are today’s headlines?\nClaire: Super Junior canceled tomorrow’s concert.\nZax:\nClaire: You bet. So many fans like me were very excited about seeing their show.\n(A) It sounds like you’re not into music.\n(B) How many fans will be attending it?\n(C) Who are the members of the band?\n(D) You must feel terribly disappointed.\n",
"note":"Restored Zax's visible original blank response line."
},
16:{
"question":"Dora: Where can I get that novel?\nDavid: I just ordered it online.\nDora: ________\nDavid: Anyone can! It’s so easy to use online bookstores nowadays.",
"options":["I’m amazed you can do that.","How’s the store’s service quality?","It’s actually about storytelling.","The system has a virus, doesn’t it?"],
"raw":"16. Dora: Where can I get that novel?\nDavid: I just ordered it online.\nDora:\nDavid: Anyone can! It’s so easy to use online bookstores nowadays.\n(A) P'm amazed you can do that. (B) How’s the store’s service quality?\n(C) It’s actually about storytelling. (D) The system has a virus, doesn’t it?\n",
"note":"Corrected OCR misread (A) P'm -> I’m; restored missing blank and separated two-column answer choices."
},
17:{
"question":"Jill: When is your monthly test?\nLarry: Next Thursday. Oh, I’m running out of time!\nJill: Relax! There are still five more days to prepare.\nLarry: Easy for you to say. ________\nJill: I have confidence in you.",
"options":["I can’t believe he spoke to you this way.","I’m not sure if I can be ready by that time.","But it’s kind of dangerous to run here.","The monthly treatment takes too long."],
"raw":"17. Jill: When is your monthly test?\nLarry: Next Thursday. Oh, I’m running out of time!\nJill: Relax! There are still five more days to prepare.\nLarry: Easy for you to say.\nJill: Ihave confidence in you.\n(A) I can’t believe he spoke to you this way.\n(B) I’m not sure if I can be ready by that time.\n(C) But it’s kind of dangerous to run here.\n(D) The monthly treatment takes too long.\n",
"note":"OCR omitted Larry's answer blank and joined 'Ihave'; confirmed all choices against original image."
},
18:{
"question":"Operator: City Hall. How may I direct your call?\nCitizen: ________\nOperator: And the reason for your call?\nCitizen: Well, the park in our neighborhood looks terrible. I mean, there’s litter everywhere and nobody has picked it up.\nOperator: I see. One moment please.",
"options":["I’d like to speak to Environmental Services, please.","Yes, you may hand the problem to our department.","Read it before you hand it in to the director, please.","Please turn right at the next corner to find the center."],
"raw":"18. Operator: City Hall. How may I direct your call?\n\nCitizen:\n\nOperator: And the reason for your call?\n\nCitizen: Well, the park in our neighborhood looks terrible. I mean, there’s litter everywhere\nand nobody has picked it up.\n\nOperator: Isee. One moment please.\n\n(A) I'd like to speak to Environmental Services, please.\n\n(B) Yes, you may hand the problem to our department.\n\n(C) Read it before you hand it in to the director, please.\n\n(D) Please turn right at the next corner to find the center.\n",
"note":"Restored the citizen's original fill-in blank and fixed OCR joined 'Isee'; normalized source apostrophe."
}
}
def f(path):
    res=(ROOT/path).resolve()
    if not res.is_relative_to(ROOT):raise RuntimeError("Path outside QA repo")
    return res
def load(path):return json.loads(f(path).read_text("utf8"))
def sha(path):return hashlib.sha256(f(path).read_bytes()).hexdigest()
def index(rows):
    d={x["questionId"]:x for x in rows}
    assert len(d)==len(rows)
    return d
def normalized(n,row):
    q=row["question"];opts=row["options"]
    return str(n)+". "+q+"\n"+"\n".join("("+letter+") "+option for letter,option in zip("ABCD",opts))+"\n"
def get_record(id,row):
    n=int(id[-2:])
    if n not in TEXT:return None
    diff="".join(difflib.unified_diff(TEXT[n]["raw"].splitlines(keepends=True),
        normalized(n,TEXT[n]).splitlines(keepends=True),fromfile="ocr-raw",tofile="corrected"))
    return {"questionId":id,"year":106,"paperCode":"00-E","originalQuestionNumber":n,
        "sourceQuestionWebpSha256":row["reviewedWebpSha256"],"sourceQuestionWebpPath":row["reviewedWebpPath"],
        "sourcePage":3,"sourcePageSha256":row["sourcePageSha256"],
        "ocrRaw":TEXT[n]["raw"],"ocrEngine":"Tesseract 5 English psm6 original first pass 2026-10-23",
        "ocrCorrected":TEXT[n]["question"],"correctedOptions":TEXT[n]["options"],
        "rawToCorrectedUnifiedDiff":diff,"visualCorrectionNote":TEXT[n]["note"],
        "method":"direct visual comparison original official p3 and exact source crop, no guesses",
        "qaReviewer":"ChatGPT assistant","qaReviewedAt":"2026-10-23",
        "textQaStatus":"PASS_DIRECT_ORIGINAL_SOURCE_QA", "questionVerified":True,
        "answerVerified":False,"integrationReady":False}
def run(stage=False):
    assert subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()==BRANCH
    ledger=load(EVIDENCE);img=index(ledger["items"])
    assert len(img)==6
    bank=load(BASE/"questions.json")
    original=load(BASE/"ocr-raw-candidates.json")
    vis=load(BASE/"VISUAL_QA.json")
    inv=load(BASE/"inventory.json")
    val=load(BASE/"VALIDATION.json")
    qs=index(bank["questions"]);ocr=index(original["items"]);review=index(vis["items"])
    assert len(qs)==len(ocr)==len(review)==204
    assert inv["visualQaPass"]==6 and inv["answerOfficialFinalVerified"]==0
    pending=[]
    records=[]
    for n in sorted(TEXT):
        id=f"106-00-E-{n:02d}"
        assert id in img and id in qs and id in ocr and id in review
        x=img[id];q=qs[id];o=ocr[id];v=review[id]
        assert q["imageQaStatus"]=="PASS" and v["status"]=="PASS"
        assert q["assets"]["sha256"]==x["reviewedWebpSha256"]
        assert sha(x["reviewedWebpPath"])==x["reviewedWebpSha256"]
        assert not q.get("answerVerified") and not q.get("integrationReady")
        assert len(TEXT[n]["options"])==4 and all(TEXT[n]["options"])
        rec=get_record(id,x);records.append(rec)
        if q.get("questionVerified"):
            assert q.get("textQaEvidence")==OUT.as_posix()
            assert o.get("rawOcrText")==rec["ocrRaw"]
            assert o.get("correctedQuestion")==rec["ocrCorrected"]
            assert o.get("correctedOptions")==rec["correctedOptions"]
            assert q["options"]==rec["correctedOptions"] and q["question"]==rec["ocrCorrected"]
        else:
            assert q.get("questionVerified") is False
            assert o["rawOcrText"] is None and o["qaStatus"]=="PENDING"
            assert not q["options"] and q["question"].startswith("本題原卷文字")
            pending.append(id)
    if len(pending) not in (0,6):
        raise RuntimeError("Partially applied OCR: manual reconciliation needed")
    payload={"schemaVersion":1,"year":106,"subject":"英文","paperCode":"00-E",
        "reviewedAt":"2026-10-23","reviewer":"ChatGPT assistant",
        "method":"Tesseract original raw preserved + manual correction directly from official p3/6 original-pixel WebPs",
        "imageQAExisting":6,"ocrCorrectedAndQuestionVerifiedAdded":6,
        "officialAnswerVerifiedAdded":0,"releaseAllowed":False,"integrationReady":False,
        "records":records}
    wire=(json.dumps(payload,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    if f(OUT).exists() and f(OUT).read_bytes()!=wire:
        raise RuntimeError("Refusing to overwrite differing immutable OCR evidence")
    if stage and not f(OUT).exists():
        f(OUT).parent.mkdir(parents=True,exist_ok=True);f(OUT).write_bytes(wire)
    if not pending or not stage:
        return {"mode":"CHECK" if not stage else "IDEMPOTENT","pending":len(pending),
           "rawOcrPreserved":len(records),"imageQaPass":6,"answerVerifiedAdded":0}
    for id in pending:
        rec=next(x for x in records if x["questionId"]==id)
        q=qs[id];o=ocr[id]
        q["legacyUnverifiedQuestion"]=q["question"]
        q["question"]=rec["ocrCorrected"]
        q["options"]=rec["correctedOptions"]
        q["ocrStatus"]="PASS_REVIEWED_ORIGINAL_IMAGE"
        q["textQaStatus"]="PASS"
        q["textQaEvidence"]=OUT.as_posix()
        q["questionVerified"]=True
        q["answerVerified"]=False
        q["integrationReady"]=False
        o["rawOcrText"]=rec["ocrRaw"]
        o["rawOrigin"]=rec["ocrEngine"]
        o["correctedQuestion"]=rec["ocrCorrected"]
        o["correctedOptions"]=rec["correctedOptions"]
        o["diff"]=rec["rawToCorrectedUnifiedDiff"]
        o["imageSha256"]=rec["sourceQuestionWebpSha256"]
        o["qaStatus"]="PASS"
        o["qaReviewer"]="ChatGPT assistant"
        o["qaReviewedAt"]="2026-10-23"
        o["qaEvidencePath"]=OUT.as_posix()
    inv["ocrTextIndependentlyVerified"]=6
    inv["textQaPass"]=6
    val["ocrTextVerified"]=6
    val["releaseAllowed"]=val["integrationReady"]=False
    assert sum(bool(x.get("questionVerified")) for x in bank["questions"])==6
    assert sum(x.get("qaStatus")=="PASS" for x in original["items"])==6
    assert inv["visualQaPass"]==6 and inv["answerOfficialFinalVerified"]==0
    assert all(not(x.get("answerVerified") or x.get("integrationReady")) for x in bank["questions"])
    if stage:
        db=f(BASE/"question-bank.sqlite3")
        with sqlite3.connect(db) as cx:
            cols={r[1] for r in cx.execute("PRAGMA table_info(questions)")}
            assert {"question_id","payload_sha256"}<=cols
            field="payload" if "payload" in cols else "payload_json"
            assert field in cols
            tables={r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "student_answers" not in tables and "student_results" not in tables
            for id in sorted(pending):
                raw=json.dumps(qs[id],ensure_ascii=False,sort_keys=True,separators=(",",":"))
                assert cx.execute(f"UPDATE questions SET {field}=?,payload_sha256=? WHERE question_id=?",
                   (raw,hashlib.sha256(raw.encode("utf8")).hexdigest(),id)).rowcount==1
            assert cx.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            assert cx.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==204
            for id,raw,h in cx.execute(f"SELECT question_id,{field},payload_sha256 FROM questions"):
                assert hashlib.sha256(raw.encode("utf8")).hexdigest()==h and json.loads(raw)["questionId"]==id
        for fn,obj in (("questions.json",bank),("ocr-raw-candidates.json",original),
                      ("inventory.json",inv),("VALIDATION.json",val)):
            f(BASE/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"mode":"STAGE","ocrSourceImages":6,"ocrCorrectedPassAdded":6,
            "questionVerifiedAdded":6,"imagePassPreserved":6,
            "officialAnswerVerifiedAdded":0,"releaseAllowed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    a=p.parse_args()
    print(json.dumps(run(stage=a.stage),ensure_ascii=False))
