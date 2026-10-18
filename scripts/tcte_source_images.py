#!/usr/bin/env python3
"""Render official PDF pages to shared, compact WebP. Never perform OCR.
Existing question IDs, answers and verification flags are left completely untouched.
Whole pages intentionally preserve diagrams, preceding passages and neighbouring context.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import io
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
import fitz
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sudu/data/original'
ALLOWED = {'web1.tcte.edu.tw', 'www.tcte.edu.tw', 'tcte.edu.tw'}
VERSION = 1

def official(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED:
        raise ValueError('Not an official HTTPS PDF source')
    return url

def download(task):
    year, paper, url, questions = task
    for attempt in range(2):
        try:
            current = official(url)
            for _ in range(4):
                response = requests.get(current, timeout=(15, 55), allow_redirects=False,
                                        headers={'User-Agent': '7581707 educational original-PDF renderer/1.0'})
                if response.is_redirect:
                    current = official(urljoin(current, response.headers.get('Location', '')))
                    continue
                response.raise_for_status()
                data = response.content
                if len(data) > 40_000_000 or not data.startswith(b'%PDF'):
                    raise ValueError('Invalid or oversized PDF')
                return task, data, None
            raise ValueError('Too many source redirects')
        except Exception as exc:
            if attempt:
                return task, None, str(exc)[:200]
            time.sleep(1)

def render_pdf(data, year, paper, questions, source, width=1400, quality=66):
    digest = hashlib.sha256(data).hexdigest()
    folder = OUT / str(year) / paper
    folder.mkdir(parents=True, exist_ok=True)
    pages, anchors = [], {}
    with fitz.open(stream=data, filetype='pdf') as pdf:
        if not 1 <= len(pdf) <= 100:
            raise ValueError('Unexpected page count')
        for ix, page in enumerate(pdf):
            # This reads only an existing PDF text layer for optional page navigation.
            # No image-to-text operation or OCR dependency is used.
            text = page.get_text('text')
            is_cover = ix == 0 and ('考試開始鈴' in text or '試卷說明' in text)
            if not is_cover:
                for match in re.finditer(r'(?m)^\s*(\d{1,3})[.．、]\s*\S', text):
                    anchors.setdefault(int(match.group(1)), []).append(ix + 1)
            scale = width / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY, alpha=False)
            image = Image.frombytes('L', (pix.width, pix.height), pix.samples)
            file = folder / ('p%03d-%s.webp' % (ix + 1, digest[:10]))
            image.save(file, 'WEBP', quality=quality, method=6)
            # Re-open: catches partial encodes and records actual decoded dimensions.
            with Image.open(file) as check:
                check.load()
                if check.width < 600 or check.height < 100:
                    raise ValueError('Rendered page resolution is too small')
            pages.append({'page': ix + 1, 'src': str(file.relative_to(ROOT / 'sudu')).replace('\\', '/'),
                          'width': image.width, 'height': image.height, 'bytes': file.stat().st_size})
    mapped = {}
    for q in questions:
        native = sorted(set(anchors.get(q.get('number'), [])))
        existing = q.get('page')
        if len(native) == 1:
            selected, method = native[0], 'native_pdf_text_anchor_no_ocr'
        elif isinstance(existing, int) and 1 <= existing <= len(pages):
            selected, method = existing, 'existing_page_index_needs_visual_review'
        else:
            selected, method = None, 'whole_paper_page_location_pending'
        mapped[q['id']] = {'page': selected, 'mapping': method, 'questionVerified': False}
    keep = {Path(p['src']).name for p in pages}
    for old in folder.glob('*.webp'):
        if old.name not in keep:
            old.unlink()
    return {'year': year, 'paper': paper, 'source': source, 'pdfSha256': digest,
            'format': 'webp', 'mode': 'original_full_page', 'ocrUsed': False,
            'pages': pages, 'questions': mapped, 'renderVersion': VERSION}

def run(years):
    OUT.mkdir(parents=True, exist_ok=True)
    index = OUT / 'index.json'
    report = json.loads(index.read_text('utf-8')) if index.exists() else {'schema': 1, 'papers': {}}
    tasks, errors = [], []
    for year in years:
        file = ROOT / 'sudu/data/years' / (str(year) + '.json')
        if not file.exists():
            errors.append({'year': year, 'reason': 'Annual JSON unavailable'})
            continue
        data = json.loads(file.read_text('utf-8'))
        for paper in data.get('papers', []):
            code = paper.get('paper', '')
            if not re.fullmatch(r'[A-Z0-9-]{2,20}', code):
                continue
            if year < 100 and not (code.startswith('BIZ-') or code.startswith('00-')):
                continue  # Old 09 was NOT the modern commerce group.
            source = paper.get('questionPdf')
            if not source:
                source = next((q.get('source') for q in paper.get('questions', []) if q.get('source')), None)
            if not source:
                errors.append({'year': year, 'paper': code, 'reason': 'No official original PDF URL'})
                continue
            tasks.append((year, code, source, paper.get('questions', [])))
    # Network work only in threads. PDF rendering is kept serial (PyMuPDF is not thread-safe).
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for task, data, error in pool.map(download, tasks):
            year, code, source, questions = task
            key = str(year) + '/' + code
            if error:
                errors.append({'year': year, 'paper': code, 'reason': error})
                print('SOURCE_IMAGE_FAILED', key, error, flush=True)
                continue
            try:
                item = render_pdf(data, year, code, questions, source)
                report['papers'][key] = item
                size = sum(p['bytes'] for p in item['pages'])
                print('ORIGINAL_IMAGES', key, len(item['pages']), 'pages', size, 'bytes; OCR=0', flush=True)
                index.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), 'utf-8')
            except Exception as exc:
                errors.append({'year': year, 'paper': code, 'reason': str(exc)[:200]})
    report['generatedAt'] = datetime.now(timezone.utc).isoformat()
    report['ocrUsed'] = False
    report['errors'] = errors
    report['summary'] = {'papers': len(report['papers']),
                         'pages': sum(len(p['pages']) for p in report['papers'].values()),
                         'questionLinks': sum(len(p['questions']) for p in report['papers'].values()),
                         'bytes': sum(pg['bytes'] for p in report['papers'].values() for pg in p['pages'])}
    index.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    print('ORIGINAL_IMAGE_SUMMARY', json.dumps(report['summary']), 'errors', len(errors), flush=True)
    # A partial run is explicitly reported, not silently described as full coverage.
    if not report['papers']:
        raise SystemExit('No official originals could be rendered')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--years', nargs='+', type=int, default=list(range(90, 116)))
    args = parser.parse_args()
    if any(y < 90 or y > 115 for y in args.years):
        raise SystemExit('Expected years 90 through 115')
    run(args.years)
