#!/usr/bin/env python3
"""Render original official answer sheets; keep sources and old versions. Never OCR.

Targeted reruns retain failures for untouched years. An HTML answer table is
reported as HTML, not retried as a fake PDF or advertised as complete coverage.
"""
import argparse, concurrent.futures, json, re
from datetime import datetime, timezone
from pathlib import Path
from tcte_source_images import ROOT, OUT, download, render_pdf, preserve_image_version, invalidate_changed_source
from check_tcte_corpus import in_scope

def run(years=None, paper_codes=None):
    years=years or list(range(90,116));tasks=[];errors=[]
    catalog_file=ROOT/'sudu/data/official-paper-catalog.json'
    catalog=json.loads(catalog_file.read_text('utf-8')) if catalog_file.exists() else {}
    index=OUT/'answers.json';report=json.loads(index.read_text('utf-8')) if index.exists() else {'schema':1,'papers':{}}
    old_errors=[e for e in report.get('errors',[]) if e.get('year') not in years or (paper_codes and e.get('paper') not in paper_codes)]
    for year in years:
        file=ROOT/'sudu/data/years'/(str(year)+'.json')
        if not file.exists():errors.append({'year':year,'error':'annual_json_missing'});continue
        for paper in json.loads(file.read_text('utf-8')).get('papers',[]):
            code=paper.get('paper','')
            if not re.fullmatch(r'[A-Z0-9-]{2,20}',code) or not in_scope(year,code) or (paper_codes and code not in paper_codes):continue
            from_catalog=next((p.get('answerSource') for p in catalog.get('years',{}).get(str(year),{}).get('papers',[]) if p.get('paper')==code),None)
            url=paper.get('answerPdf') or next((q.get('answerSource') for q in paper.get('questions',[]) if q.get('answerSource')),None) or from_catalog
            if not url:errors.append({'year':year,'paper':code,'error':'official_answer_source_not_identified'});continue
            if re.search(r'\.html?(?:[?#]|$)',url,re.I):
                errors.append({'year':year,'paper':code,'source':url,'error':'official_source_is_html_table_not_pdf','sourceFormat':'html'});continue
            tasks.append((year,code,url,[]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for task,data,error in pool.map(download,tasks):
            year,code,url,_=task;key=f'{year}/{code}'
            if error:errors.append({'year':year,'paper':code,'source':url,'error':error});continue
            try:
                previous=report['papers'].get(key)
                multi=year==91 and url.endswith('91-4y-answer-new.pdf')
                item=render_pdf(data,year,code+'-answers',[],url,width=3500 if multi else 1400,quality=75 if multi else 66)
                item['paper']=code;item['role']='official_answer_sheet';item['answerScope']='multi_subject_full_page' if multi else 'paper_full_page'
                item=preserve_image_version(previous,item);invalidate_changed_source(year,code,'answer',previous,item)
                report['papers'][key]=item
                index.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),'utf-8')
                print('OFFICIAL_ANSWER_IMAGES',year,code,len(item['pages']),'OCR=0',flush=True)
            except Exception as exc:errors.append({'year':year,'paper':code,'source':url,'error':str(exc)[:180]})
    report['generatedAt']=datetime.now(timezone.utc).isoformat();report['ocrUsed']=False;report['errors']=old_errors+errors
    report['lastRun']={'years':years,'paperCodes':paper_codes,'attempted':len(tasks),'failures':len(errors)}
    report['summary']={'papers':len(report['papers']),'pages':sum(len(p['pages']) for p in report['papers'].values()),
                       'bytes':sum(pg['bytes'] for p in report['papers'].values() for pg in p['pages'])}
    index.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),'utf-8')
    print('ANSWER_IMAGE_SUMMARY',json.dumps(report['summary']),'errors',len(report['errors']),flush=True)
    if not report['papers']:raise SystemExit('No official answer sheets could be rendered')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--years',nargs='+',type=int,default=list(range(90,116)));p.add_argument('--papers',nargs='+')
    a=p.parse_args()
    if any(y<90 or y>115 for y in a.years):raise SystemExit('Expected years 90 through 115')
    run(a.years,a.papers)
