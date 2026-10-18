#!/usr/bin/env python3
"""Build source-backed official group/subject catalog from yearly official indexes. No OCR."""
import argparse, concurrent.futures, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from tcte_auto import guarded_get, year_url, decoded_input_links, legacy_links
ROOT=Path(__file__).resolve().parents[1]

def fetch(year):
    url=year_url(year);response=guarded_get(url)
    soup=BeautifulSoup(response.content,'html.parser');text=re.sub(r'\s+','',soup.get_text(' ',strip=True))
    m=re.search(r'(14|13|09)(商業與管理群|商業類|商管群)',text)
    expected='14' if year<=91 else '13' if year<=97 else '09'
    html=str(soup);links=decoded_input_links(html,url) or legacy_links(html,url)
    if year==90 and not m:
        commerce=[p for p in links if p['paper'].startswith('BIZ-')]
        if len(commerce)!=2 or '商業類專一' not in text or '商業類專二' not in text:
            raise ValueError('90: official commerce labels/PDF links require review')
        label='商業類（官方卷檔名代碼14）'
    else:
        if not m:raise ValueError(f'{year}: commerce group title not identified')
        if m.group(1)!=expected:raise ValueError(f'{year}: official group differs; review required')
        label=m.group(0)
    ps={}
    for link in links:
        code=link['paper']
        if code.startswith('00-M') and code not in {'00-MB','00-M-OLD'}:continue
        p=ps.setdefault(code,{'paper':code,'subjects':[],'subjectStatus':'pending_original_cover_review'})
        p['questionSource' if link['kind']=='exam' else 'answerSource']=link['url']
        if code=='00-C':p['subjects']=['國文'];p['subjectStatus']='official_index'
        elif code=='00-E':p['subjects']=['英文'];p['subjectStatus']='official_index'
        elif code=='00-MB':p['subjects']=['數學 B'];p['subjectStatus']='official_index'
        elif code=='00-M-OLD':p['subjects']=['數學（舊制共卷，分卷範圍待核實）'];p['subjectStatus']='official_index_requires_variant_review'
    if year==91:
        for p in ps.values():p.setdefault('answerSource',url+'91-4y-answer-new.pdf');p['answerImageScope']='multi_subject_full_page'
    return str(year),{'year':year,'sourceIndex':url,'sourceSha256':hashlib.sha256(response.content).hexdigest(),
        'checkedAt':datetime.now(timezone.utc).isoformat(),'officialCommerceCode':expected,'groupLabel':label,
        'allowedPaperCodes':sorted(ps),'papers':sorted(ps.values(),key=lambda p:p['paper'])}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--years',nargs='+',type=int,default=list(range(90,116)))
    args=parser.parse_args();years={};errors=[];previous={}
    existing=ROOT/'sudu/data/official-paper-catalog.json'
    if existing.exists():
        previous=json.loads(existing.read_text('utf-8'))
        years={k:v for k,v in previous.get('years',{}).items() if int(k) not in args.years}
        errors=[e for e in previous.get('errors',[]) if e.get('year') not in args.years]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(fetch,y):y for y in args.years}
        for job in concurrent.futures.as_completed(jobs):
            try:
                key,value=job.result()
                old_papers={p['paper']:p for p in previous.get('years',{}).get(key,{}).get('papers',[])}
                image_path=ROOT/'sudu/data/original/index.json'
                image_index=json.loads(image_path.read_text('utf-8')) if image_path.exists() else {}
                for p in value['papers']:
                    old=old_papers.get(p['paper'],{});review=old.get('coverReview') or {}
                    img=image_index.get('papers',{}).get(key+'/'+p['paper'],{})
                    if review and review.get('questionSource')==p.get('questionSource') and review.get('pdfSha256')==img.get('pdfSha256'):
                        for field in ('subjects','subjectStatus','questionSubjectMapping','coverReview'):
                            if field in old:p[field]=old[field]
                    elif review:p['coverReviewHistory']=(old.get('coverReviewHistory') or [])+[review]
                years[key]=value;print('CATALOG',key,value['groupLabel'],len(value['papers']),flush=True)
            except Exception as exc:errors.append({'year':jobs[job],'reason':str(exc)})
    out={'schema':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'method':'official_year_index_no_ocr',
        'notice':'科別依官方年度目錄；未核對原卷封面與分題邊界時，不假設現行科目或按題號對半分科。',
        'years':dict(sorted(years.items(),key=lambda x:int(x[0]))),'errors':errors}
    (ROOT/'sudu/data/official-paper-catalog.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
    if errors:print('CATALOG_ERRORS',json.dumps(errors,ensure_ascii=False));raise SystemExit(1)
if __name__=='__main__':main()
