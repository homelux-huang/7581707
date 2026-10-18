#!/usr/bin/env python3
"""Optional scheduled AI tutoring for validated official answers. Never marks textbook chapters verified."""
import argparse,os,json,time,re,datetime
from pathlib import Path
import requests
DIR=Path(__file__).resolve().parents[1]/"sudu/data/years"
API=os.environ.get("OPENAI_API_KEY","")
MODEL=os.environ.get("TCTE_TEACHING_MODEL","gpt-4.1-mini")
INSTRUCTION="""你是臺灣技術型高中統測商管群老師。請依正式原題及經官方標準答案核對的正解，
產生國小六年級也聽得懂的繁體中文白話詳解，不可以改寫原題或猜選項。題目可能是OCR未校對的文字，
絕對不能填虛構的學校課本章名、頁碼、出版社、年度、法規現況。
遇到法規或過時課綱要指出本題只適用原考試當年度。看不懂圖表公式或無法證明答案，設定unable=true且不要硬解。
輸出純JSON物件：unable(bool), topic(string), explanation(string), principle(string), steps(string),
wrongOptions(長度4字串陣列，說明每個選項理由；正確選項也要解釋), extension(string),
practice(包含question、options四個選項字串、answerIndex為0..3、explanation字串),
sourceNote(string，必須說明正式試題來源和未核實的課本章節)。不得輸出Markdown。"""
def eligible(q):
    return q.get("answerVerified") and len(q.get("options") or [])==4 and all(q["options"]) \
       and not q.get("teachingVerified") and not q.get("teachingStatus") \
       and not q.get("ocrUsed") and not any(i in q.get("issues",[]) for i in ["figure_or_table_recheck_pdf","missing_complete_options","missing_A_to_D_options"])
def ask(q):
    payload={
        "model":MODEL,
        "messages":[
          {"role":"system","content":INSTRUCTION},
          {"role":"user","content":json.dumps({
            "year":q.get("year"),"paper":q.get("paper"),"questionNumber":q.get("number"),
            "question":q.get("question"),"options":q.get("options"),
            "officialStandardAnswer":"ABCD"[q["answer"]],
            "sourceExamPdf":q.get("source"),
            "sourceAnswerPdf":q.get("answerSource"),
            "textbookChapter":"尚無可查證的教材頁碼，不准填寫"
          },ensure_ascii=False)}
        ],
        "response_format":{"type":"json_object"},
        "max_tokens":1500
    }
    r=requests.post("https://api.openai.com/v1/chat/completions",json=payload,
                    headers={"Authorization":"Bearer "+API,"Content-Type":"application/json"},timeout=65)
    r.raise_for_status()
    data=json.loads(r.json()["choices"][0]["message"]["content"])
    if data.get("unable") is True:return None
    for x in ["explanation","principle","steps","extension"]:
        if not isinstance(data.get(x),str) or len(data[x])<10:return None
    choices=data.get("wrongOptions")
    if not isinstance(choices,list) or len(choices)!=4 or any(not isinstance(s,str) or len(s)<4 for s in choices):return None
    pr=data.get("practice") or {}
    if not isinstance(pr,dict) or not isinstance(pr.get("options"),list) or len(pr["options"])!=4:return None
    if not isinstance(pr.get("answerIndex"),int) or not 0<=pr["answerIndex"]<=3:return None
    if len(str(pr.get("explanation","")))<10 or len(str(pr.get("question","")))<10:return None
    return data
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--max-questions",type=int,default=30)
    p.add_argument("--years",nargs="*",type=int)
    a=p.parse_args()
    if not API:
        print("TUTORING_SKIPPED: OPENAI_API_KEY GitHub secret not configured. Official PDF import is independent.")
        return
    maximum=min(max(0,a.max_questions),250)
    count=0;errors=0
    for year in (a.years or list(range(115,89,-1))):
        f=DIR/(str(year)+".json")
        if not f.exists():continue
        data=json.loads(f.read_text("utf8"))
        changed=False
        for paper in data.get("papers",[]):
            for q in paper.get("questions",[]):
                if count>=maximum:break
                if not eligible(q):continue
                try:
                    tutor=ask(q)
                    if tutor is None:
                        q["teachingStatus"]="needs_human_review";changed=True;continue
                    q["topic"]=str(tutor.get("topic") or q.get("subject","")).strip()[:80]
                    q["explanation"]=tutor["explanation"]
                    q["principle"]=tutor["principle"]
                    q["steps"]=tutor["steps"]
                    q["wrongOptions"]=tutor["wrongOptions"]
                    q["extension"]=tutor["extension"]
                    p=tutor["practice"]
                    q["practice"]={"question":p["question"],"options":p["options"],
                                   "answer":p["options"][p["answerIndex"]],
                                   "answerIndex":p["answerIndex"],"explanation":p["explanation"]}
                    q["sourceNote"]=str(tutor.get("sourceNote") or "原題及答案以當年官方PDF為準；教材精確章節待核實。")
                    q["teachingStatus"]="ai_draft_needs_verification"
                    q["teachingVerified"]=False
                    q["teachingGeneratedAt"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
                    changed=True;count+=1
                    print("DRAFT",year,paper.get("paper"),q.get("number"),flush=True)
                    time.sleep(0.2)
                except Exception as e:
                    errors+=1
                    print("AI_FAILED",year,paper.get("paper"),q.get("number"),type(e).__name__,str(e)[:140],flush=True)
                    if errors>=4:break
            if count>=maximum or errors>=4:break
        if changed:f.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding="utf8")
        if count>=maximum or errors>=4:break
    print("DRAFT_SUMMARY",count,"errors",errors,flush=True)
if __name__=="__main__":main()
