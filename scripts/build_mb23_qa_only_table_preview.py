#!/usr/bin/env python3
"""MB23 original source, original WebP, original table, LOCAL TEST ONLY.

No source approval. This merely confirms a table can survive the strict real
student publisher mapping and render in existing V4 before any READY decision.
"""
import hashlib
import json
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/sudu_verified_publish.py')
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
SOURCE=ROOT/"_mb23_source"
BASE=SOURCE/"sudu/data/processed/115"
OUT=ROOT/"mb23-qa-only"
OUT.mkdir(exist_ok=True)
load=lambda f:json.loads(Path(f).read_text(encoding="utf-8"))
qid="115-00-MB-23"
q=next(x for x in load(BASE/"questions.json")["questions"] if x["questionId"]==qid)
item=next(x for x in load(BASE/"webp-manifest.json")["items"] if x["questionId"]==qid)
assert q["question"].startswith("某旅行社推出兩種旅遊行程")
assert "如表（二）" in q["question"]
assert q["questionVerified"] is not True and q["studentReleaseApproved"] is not True
assert q.get("formalTextApproval") is False
assert item["sha256"]=="2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51"
assert hashlib.sha256((SOURCE/item["output"]).read_bytes()).hexdigest()==item["sha256"]
table=q["originalSourceTableCandidate"]
assert table["heading"]==["行程","原價","優惠"]
assert len(table["rows"])==2 and all(len(r)==3 for r in table["rows"])
assert table["rows"][0][2].find("3000")>=0
assert "八折" in table["rows"][1][2]
assert p.verified_source_table(table) is not None
rev=p.text_revision(q,item["sha256"])
print("MB23_TABLE_BOUND_SOURCE_REVISION",rev,flush=True)
teaching={
 "topic":"旅遊優惠費用方程式","teacherSummary":"行程Ⅰ兩人共2x－3000；行程Ⅱ是一人原價、一人八折，共1.8(x＋2000)，兩邊相等求 x。",
 "elementarySummary":"兩個人一起旅行，用行程一的總錢減3000，跟行程二打折後一樣多，算每個人的原價。",
 "memory":"表二優惠：行程Ⅰ總額2x－3000；行程Ⅱ1.8(x＋2000)；答案x＝33000。",
 "concept":"解一次方程式前先辨認「兩人中只有一人」享優惠，不可兩人都減3000或兩人都打折。",
 "extension":"若兩個人都八折，總費用才會是1.6(x＋2000)；本題僅一人八折。",
 "source":"115年數學B第23題官方原圖與表（二），教材特定出版社／頁碼待核實。",
 "optionExplanations":{
  "A":{"teacher":"32000代入兩邊費用不同。","elementary":"這個價錢兩種旅行費用不一樣。","reason":"代入不符合兩式相等"},
  "B":{"teacher":"33000符合2x－3000＝1.8(x＋2000)。","elementary":"兩邊算出來剛好一樣。","reason":"逐步求解得唯一x＝33000"},
  "C":{"teacher":"34000代入兩邊費用不同。","elementary":"價錢過高，兩邊不平衡。","reason":"不符合2x－3000＝1.8(x＋2000)"},
  "D":{"teacher":"35000代入兩邊費用不同。","elementary":"算出差額不為零。","reason":"兩種行程總價不相等"} },
 "calculationReviewed":True,"hasExamCalculation":True,
 "examCalculation":{
  "given":["行程Ⅰ：每位 x 元，其中一人減免3000元","行程Ⅱ：每位 x+2000 元，其中一人打八折"],
  "formulaUse":"兩人參加行程Ⅰ費用＝兩人參加行程Ⅱ費用",
  "substitution":["2x－3000＝(x＋2000)＋0.8(x＋2000)"],
  "steps":["2x－3000＝1.8x＋3600","0.2x＝6600","x＝33000"],"result":"33000","unit":"元","option":"B"
 },
 "highlights":["表（二）","一人減免3000元","一人打八折"]
}
stage_q=dict(q)
stage_q.update({"questionVerified":True,"textQaEvidence":{"tableReviewedAgainstOriginalWebp":True},
                "teaching":teaching,"officialFinalAnswer":"B"})
mapped=p.public_question(stage_q,115,"數學 B",f"data/approved/webp/115/{qid}.webp")
assert mapped["sourceTable"]["rows"]==table["rows"]
assert mapped["sourceTable"]["sourceWebpSha256"]==item["sha256"]
assert mapped["answer"]=="B"
out={"schemaVersion":1,"year":115,"approvedCount":1,"questions":[mapped],
     "QA_ONLY_UNPUBLISHABLE":True,"studentReleaseApproved":False}
(OUT/"115.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(OUT/"meta.json").write_text(json.dumps({
    "qid":qid,"originalWebpSha256":item["sha256"],"tableBoundQuestionRevision":rev,
    "originalTable":table,"scope":"V4 table visibility QA ONLY - unapproved source preserved",
    "sourceCandidateFormalTextApproval":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS_MB23_SCHEMA_STAGE_NO_STUDENT_RELEASE",flush=True)
