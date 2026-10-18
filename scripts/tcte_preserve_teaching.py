#!/usr/bin/env python3
"""Preserve separately reviewed teaching/answers; archive changes without touching student data.

Repeated merges are idempotent. PDF/source/answer changes invalidate dependent
verification and scoring, while immutable previous versions remain in the corpus.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ['explanation','principle','steps','wrongOptions','extension','practice','textbook','topic',
          'sourceNote','teachingStatus','teachingVerified','teachingGeneratedAt','teachingReviewedBy',
          'teachingReviewedAt','questionVerified','questionReviewedBy','questionReviewedAt',
          'answerVerified','answerMatched','answerReviewedBy','answerReviewedAt','answerVerificationLegacy',
          'textbookVerified','textbookReviewedBy','textbookReviewedAt','verification','verificationHistory']
SNAPSHOT_FIELDS = FIELDS + ['id','year','paper','number','subject','question','options','answer','acceptedAnswers',
                            'officialAnswerCandidate','source','answerSource','sourceVersion']

def normalize(s): return re.sub(r'\s+', ' ', str(s or '')).strip()
def digest(value): return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def question_key(q):
    source = q.get('sourceVersion') or {}
    return digest({'stem':normalize(q.get('question')),'options':[normalize(x) for x in q.get('options',[])],
                   'source':q.get('source'),'pdf':source.get('questionPdfSha256'),'subject':q.get('subject'),
                   'year':q.get('year'),'paper':q.get('paper'),'number':q.get('number')})

def answer_key(q):
    source = q.get('sourceVersion') or {}
    return digest({'answer':q.get('answer'),'accepted':sorted(q.get('acceptedAnswers') or []),
                   'candidate':q.get('officialAnswerCandidate'),'source':q.get('answerSource'),
                   'pdf':source.get('answerPdfSha256')})

def stable_key(q): return digest({'question':question_key(q),'answer':answer_key(q)})

def archive_version(q, reason):
    snapshot = {k:copy.deepcopy(q[k]) for k in SNAPSHOT_FIELDS if k in q and k != 'verificationHistory'}
    return {'versionId':digest(snapshot),'reason':reason,'snapshot':snapshot}

def review_evidence(q, part):
    v=(q.get('verification') or {}).get(part,{})
    if not isinstance(v,dict):v={}
    return bool((q.get(part+'ReviewedBy') or v.get('reviewedBy')) and (q.get(part+'ReviewedAt') or v.get('reviewedAt')))

def merge_year(old, new):
    old_q={q.get('id'):q for p in old.get('papers',[]) for q in p.get('questions',[])}
    reused=reset=0; retained=set()
    for paper in new.get('papers',[]):
        for q in paper.get('questions',[]):
            previous=old_q.get(q.get('id'))
            if not previous:continue
            retained.add(q['id'])
            if stable_key(previous) == stable_key(q):
                changed=False
                for field in FIELDS:
                    if field in previous and q.get(field) != previous[field]:
                        q[field]=copy.deepcopy(previous[field]);changed=True
                # An old automatic pairing can never regain a reviewed flag.
                if q.get('answerVerified') and not review_evidence(q,'answer'):
                    q['answerMatched']=True;q['answerVerified']=False;changed=True
                if changed:reused+=1
                continue
            reason='question_source_changed' if question_key(previous)!=question_key(q) else 'official_answer_changed'
            history=copy.deepcopy(previous.get('verificationHistory') or [])
            for item in q.get('verificationHistory') or []:
                if item.get('versionId') not in {v.get('versionId') for v in history}:history.append(item)
            archived=archive_version(previous,reason)
            if archived['versionId'] not in {v.get('versionId') for v in history}:history.append(archived)
            q['verificationHistory']=history
            q['questionVerified']=False
            q['answerVerified']=False
            q['teachingVerified']=False
            q['textbookVerified']=False
            q['teachingStatus']='source_changed_needs_review'
            q['scoringNeedsReview']=True
            issues=q.setdefault('issues',[])
            if 'source_changed_teaching_requires_new_review' not in issues:issues.append('source_changed_teaching_requires_new_review')
            reset+=1
    # Re-importers must not silently erase questions that were present before.
    retired=copy.deepcopy(old.get('retiredQuestionVersions') or [])
    for item in new.get('retiredQuestionVersions') or []:
        if item.get('versionId') not in {v.get('versionId') for v in retired}:retired.append(item)
    for qid, previous in old_q.items():
        if qid not in retained:
            archived=archive_version(previous,'question_missing_from_new_import')
            if archived['versionId'] not in {v.get('versionId') for v in retired}:retired.append(archived);reset+=1
    if retired:new['retiredQuestionVersions']=retired
    # Migration evidence is independent of generated teaching, preserve it too.
    for field in ('verificationMigrations',):
        if field in old and field not in new:new[field]=copy.deepcopy(old[field])
    return reused,reset

def main():
    p=argparse.ArgumentParser();p.add_argument('--from-dir',type=Path,required=True);p.add_argument('--to-dir',type=Path,required=True)
    a=p.parse_args();reuse=reset=errors=0
    for path in sorted(a.to_dir.glob('*.json')):
        old_path=a.from_dir/path.name
        if not old_path.exists():continue
        try:
            old=json.loads(old_path.read_text('utf-8'));new=json.loads(path.read_text('utf-8'))
            before=json.dumps(new,ensure_ascii=False,sort_keys=True);x,y=merge_year(old,new)
            if before!=json.dumps(new,ensure_ascii=False,sort_keys=True):path.write_text(json.dumps(new,ensure_ascii=False,separators=(',',':')),'utf-8')
            reuse+=x;reset+=y
        except Exception as exc:print('ERROR',path.name,exc);errors+=1
    print(f'TEACHING_PRESERVED {reuse}; INVALIDATED_BY_CHANGED_SOURCE {reset}; ERRORS {errors}')
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
