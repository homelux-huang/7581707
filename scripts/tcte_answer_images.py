#!/usr/bin/env python3
"""Render official answer sheets directly as WebP; never recognize image text.
No answer values, existing question data or verification flags are modified.
"""
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from tcte_source_images import ROOT, OUT, download, render_pdf


def run():
    tasks = []
    for year in range(90, 116):
        file = ROOT / 'sudu/data/years' / (str(year) + '.json')
        if not file.exists():
            continue
        for paper in json.loads(file.read_text('utf-8')).get('papers', []):
            code = paper.get('paper', '')
            if year < 100 and not (code.startswith('00-') or code.startswith('BIZ-')):
                continue
            url = paper.get('answerPdf') or next((q.get('answerSource') for q in paper.get('questions', []) if q.get('answerSource')), None)
            if url:
                tasks.append((year, code, url, []))
    index = OUT / 'answers.json'
    report = json.loads(index.read_text('utf-8')) if index.exists() else {'schema': 1, 'papers': {}}
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for task, data, error in pool.map(download, tasks):
            year, code, url, _ = task
            if error:
                errors.append({'year': year, 'paper': code, 'source': url, 'error': error})
                continue
            try:
                item = render_pdf(data, year, code + '-answers', [], url)
                item['paper'] = code
                item['role'] = 'official_answer_sheet'
                report['papers'][str(year) + '/' + code] = item
                index.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), 'utf-8')
                print('OFFICIAL_ANSWER_IMAGES', year, code, len(item['pages']), 'OCR=0', flush=True)
            except Exception as exc:
                errors.append({'year': year, 'paper': code, 'source': url, 'error': str(exc)[:180]})
    report['generatedAt'] = datetime.now(timezone.utc).isoformat()
    report['ocrUsed'] = False
    report['errors'] = errors
    report['summary'] = {'papers': len(report['papers']), 'pages': sum(len(p['pages']) for p in report['papers'].values()),
                         'bytes': sum(pg['bytes'] for p in report['papers'].values() for pg in p['pages'])}
    index.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    print('ANSWER_IMAGE_SUMMARY', json.dumps(report['summary']), 'errors', len(errors), flush=True)
    if not report['papers']:
        raise SystemExit('No original answer sheets could be rendered')

if __name__ == '__main__':
    run()
