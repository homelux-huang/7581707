#!/usr/bin/env python3
"""Preserve provenance-reviewed teaching across re-OCR only for unchanged original questions and answers.
Usage: python scripts/tcte_preserve_teaching.py --from-dir <old-data-dir> --to-dir <new-data-dir>.
"""
import argparse,json,re,hashlib
from pathlib import Path
FIELDS=["explanation","principle","steps","wrongOptions","extension","practice","textbook","topic",
        "sourceNote","teachingStatus","teachingVerified","teachingGeneratedAt","teachingReviewedBy",
        "teachingReviewedAt","questionVerified"]
def normalize(s):
    return re.sub(r"\s+","",str(s or ""))
def stable_key(q):
    """SHA256 source question and answer; any change forces teaching re-check."""
    data=json.dumps({"stem":normalize(q.get("question")),
                     "options":[normalize(x) for x in q.get("options",[])],
                     "answer":q.get("answer"),
                     "accepted":sorted(q.get("acceptedAnswers",[]))},
                    ensure_ascii=False,sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()
def merge_year(old,new):
    old_q={q.get("id"):q for p in old.get("papers",[]) for q in p.get("questions",[])}
    reused=reset=0
    for paper in new.get("papers",[]):
        for q in paper.get("questions",[]):
            previous=old_q.get(q.get("id"))
            if not previous:continue
            if stable_key(previous)!=stable_key(q):
                if previous.get("teachingStatus") or previous.get("teachingVerified"):
                    q.setdefault("issues",[]).append("source_changed_teaching_requires_new_review")
                    reset+=1
                continue
            for field in FIELDS:
                if field in previous:q[field]=previous[field]
            if previous.get("teachingStatus") or previous.get("teachingVerified"):reused+=1
    return reused,reset
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--from-dir",type=Path,required=True)
    parser.add_argument("--to-dir",type=Path,required=True)
    args=parser.parse_args()
    reuse=reset=0
    for new_path in sorted(args.to_dir.glob("*.json")):
        old_path=args.from_dir/new_path.name
        if not old_path.exists():continue
        try:
            old=json.loads(old_path.read_text("utf8"))
            new=json.loads(new_path.read_text("utf8"))
            a,b=merge_year(old,new)
            if a or b:new_path.write_text(json.dumps(new,ensure_ascii=False,separators=(",",":")),encoding="utf8")
            reuse+=a;reset+=b
        except Exception as exc:print("ERROR",new_path.name,exc)
    print(f"TEACHING_PRESERVED {reuse}; INVALIDATED_BY_CHANGED_SOURCE {reset}")
if __name__=="__main__":main()
