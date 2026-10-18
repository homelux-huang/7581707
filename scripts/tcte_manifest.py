#!/usr/bin/env python3
"""Backward-compatible year manifest with independent evidence counters."""
import json
from datetime import datetime, timezone
from pathlib import Path
from check_tcte_corpus import audit, in_scope
ROOT=Path(__file__).resolve().parents[1]

def main():
    report=audit(ROOT,False)
    if report['errors']:
        for error in report['errors']:print('ERROR',error)
        raise SystemExit(1)
    summary={'schema':2,'generatedAt':datetime.now(timezone.utc).isoformat(),
             'notice':'officialAnswers 是程式配對；officialAnswersReviewed 才是有覆核證據的答案。圖片覆蓋不代表題幹核實。','years':[]}
    for yr in report['years']:
        y=yr['year'];path=ROOT/f'sudu/data/years/{y}.json';c=yr['counts']
        if not path.exists():
            summary['years'].append({'year':y,'available':False,'questions':0,'papers':0,'officialAnswers':0,
                'completePapers':0,'teachingVerified':0,'errors':['尚未收錄年度資料']});continue
        annual=json.loads(path.read_text('utf-8'))
        row={'year':y,'available':True,'questions':c['rawRecords'],'inScopeQuestions':c['inScopeRecords'],
             'excludedLegacyQuestions':c['excludedLegacyRecords'],'papers':c['papers'],
             'officialAnswers':c['answersMatched'],'officialAnswersReviewed':c['answersReviewed'],
             'questionVerified':c['questionVerified'],'completePapers':c['scoreablePapers'],
             'teachingDrafts':c['teachingDrafts'],'completeOptionReasons':c['completeOptionReasons'],
             'teachingVerified':c['teachingVerified'],'textbookVerified':c['textbookVerified'],
             'questionWebpAvailable':c['questionWebpAvailable'],'questionPageLocated':c['questionPageLocated'],
             'answerWebpAvailable':c['answerWebpAvailable'],'verifiedScoringRules':c['verifiedScoringRules'],
             'paperCodes':[p['paper'] for p in annual.get('papers',[]) if in_scope(y,p.get('paper'))],
             'errors':annual.get('errors',[]),'pending':yr['pending']}
        summary['years'].append(row)
    (ROOT/'sudu/data/index.json').write_text(json.dumps(summary,ensure_ascii=False,separators=(',',':')),'utf-8')
    print('COVERAGE',json.dumps(summary['years'],ensure_ascii=False))
if __name__=='__main__':main()
