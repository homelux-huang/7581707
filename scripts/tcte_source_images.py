#!/usr/bin/env python3
"""Render official PDF pages to shared, compact WebP. Never perform OCR.
Existing question IDs and answers are preserved. A changed source PDF archives
prior reviews and invalidates dependent flags. Whole pages preserve all context.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import io
import json
import os
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
import fitz
import requests
from PIL import Image
from check_tcte_corpus import COVER, in_scope
from tcte_preserve_teaching import archive_version

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sudu/data/original'
ALLOWED = {'web1.tcte.edu.tw', 'www.tcte.edu.tw', 'tcte.edu.tw'}
VERSION = 2

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
            is_cover = ix == 0 and ('考試開始鈴' in text or '試卷說明' in text or
                                    ('本試題均為' in text and '2B' in text))
            if not is_cover:
                for match in re.finditer(r'(?m)^\s*(\d{1,3})[.．、]\s*\S', text):
                    anchors.setdefault(int(match.group(1)), []).append(ix + 1)
            scale = width / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
            image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            # Render settings are part of the name. Re-rendering must not silently
            # overwrite the bytes used by an earlier reviewed question/version.
            file = folder / ('p%03d-%s-v%d-w%d-q%d.webp' % (ix + 1, digest[:10], VERSION, width, quality))
            encoded = io.BytesIO()
            image.save(encoded, 'WEBP', quality=quality, method=6)
            payload = encoded.getvalue()
            # Validate before publishing and replace atomically: a concurrent
            # build or synchronizer must never observe an empty/partial page.
            with Image.open(io.BytesIO(payload)) as check:
                check.load()
                if check.width < 600 or check.height < 100:
                    raise ValueError('Rendered page resolution is too small')
            with tempfile.NamedTemporaryFile(dir=folder, suffix='.tmp', delete=False) as temporary:
                temporary.write(payload)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            try:
                temporary_path.replace(file)
            finally:
                temporary_path.unlink(missing_ok=True)
            if file.read_bytes() != payload:
                raise ValueError('Written WebP bytes differ from validated encode')
            pages.append({'page': ix + 1, 'src': str(file.relative_to(ROOT / 'sudu')).replace('\\', '/'),
                          'width': image.width, 'height': image.height, 'bytes': len(payload),
                          'sha256': hashlib.sha256(payload).hexdigest()})
    mapped = {}
    for q in questions:
        native = sorted(set(anchors.get(q.get('number'), [])))
        existing = q.get('page')
        cover_suspect = q.get('questionPresentation') == 'original_image_required' or bool(COVER.search(q.get('question', '').strip()))
        if cover_suspect:
            selected, method = None, 'cover_instruction_mapping_rejected_use_whole_paper'
        elif len(native) == 1:
            selected, method = native[0], 'native_pdf_text_anchor_no_ocr'
        elif isinstance(existing, int) and 1 <= existing <= len(pages):
            selected, method = existing, 'existing_page_index_needs_visual_review'
        else:
            selected, method = None, 'whole_paper_page_location_pending'
        mapped[q['id']] = {'page': selected, 'mapping': method, 'questionVerified': False,
                           'candidatePages': native, 'contextStatus': 'shared_passage_and_cross_page_pending_review'}
    # Keep old source/render versions. They may support an already submitted
    # assessment or a teacher review; unreferenced files are not student data.
    return {'year': year, 'paper': paper, 'source': source, 'pdfSha256': digest,
            'format': 'webp', 'mode': 'original_full_page', 'ocrUsed': False,
            'pages': pages, 'questions': mapped, 'renderVersion': VERSION,
            'generatedAt': datetime.now(timezone.utc).isoformat(), 'sourceBytes': len(data),
            'renderSettings': {'width': width, 'quality': quality, 'colorspace': 'RGB', 'method': 6}}


def preserve_image_version(previous, item):
    """Keep source/layout evidence without duplicating histories on repeated runs."""
    if not previous:
        return item
    history = list(previous.get('history', []))
    old = {k: v for k, v in previous.items() if k != 'history'}
    signature = lambda record: (record.get('pdfSha256'), record.get('renderVersion'),
                                json.dumps(record.get('renderSettings'), sort_keys=True))
    if signature(old) != signature(item) and not any(signature(h) == signature(old) for h in history):
        history.append(old)
    if history:
        item['history'] = history
    if previous.get('pdfSha256') == item.get('pdfSha256'):
        # A routine recompression must not discard a reviewed page location.
        # Pixel crops are excluded: changed render dimensions would need review.
        valid_pages = {p['page'] for p in item.get('pages', [])}
        for qid, mapping in previous.get('questions', {}).items():
            if (qid in item.get('questions', {}) and mapping.get('questionVerified') is True
                    and mapping.get('reviewedBy') and mapping.get('reviewedAt')
                    and mapping.get('page') in valid_pages and not mapping.get('crop')):
                item['questions'][qid] = mapping
        if previous.get('sourceChangedNeedsReview'):
            item['sourceChangedNeedsReview'] = True
    if previous.get('pdfSha256') != item.get('pdfSha256'):
        item['sourceChangedNeedsReview'] = True
    return item


def invalidate_changed_source(year, code, role, previous, item):
    """Source bytes changed: archive reviews and block stale grading, never erase answers."""
    if not previous or previous.get('pdfSha256') == item.get('pdfSha256'):
        return
    path = ROOT / 'sudu/data/years' / (str(year) + '.json')
    annual = json.loads(path.read_text('utf-8'))
    for paper in annual.get('papers', []):
        if paper.get('paper') != code:
            continue
        for question in paper.get('questions', []):
            archived = archive_version(question, role + '_pdf_source_changed')
            history = question.setdefault('verificationHistory', [])
            if archived['versionId'] not in {h.get('versionId') for h in history}:
                history.append(archived)
            if role == 'question':
                question['questionVerified'] = False
                question['questionPresentation'] = 'original_image_required'
            question['answerVerified'] = False
            question['answerMatched'] = False
            question['teachingVerified'] = False
            question['textbookVerified'] = False
            question['scoringNeedsReview'] = True
            question['sourceChangePending'] = {'role': role, 'oldPdfSha256': previous.get('pdfSha256'),
                                                'newPdfSha256': item.get('pdfSha256')}
        paper['complete'] = False
    path.write_text(json.dumps(annual, ensure_ascii=False, separators=(',', ':')), 'utf-8')

def run(years, paper_codes=None):
    OUT.mkdir(parents=True, exist_ok=True)
    index = OUT / 'index.json'
    report = json.loads(index.read_text('utf-8')) if index.exists() else {'schema': 1, 'papers': {}}
    tasks, errors = [], []
    requested = set(years)
    old_errors = [e for e in report.get('errors', []) if e.get('year') not in requested or
                  (paper_codes and e.get('paper') not in paper_codes)]
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
            if paper_codes and code not in paper_codes:
                continue
            if not in_scope(year, code):
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
                previous = report['papers'].get(key)
                item = preserve_image_version(previous, render_pdf(data, year, code, questions, source))
                invalidate_changed_source(year, code, 'question', previous, item)
                report['papers'][key] = item
                size = sum(p['bytes'] for p in item['pages'])
                print('ORIGINAL_IMAGES', key, len(item['pages']), 'pages', size, 'bytes; OCR=0', flush=True)
                index.write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), 'utf-8')
            except Exception as exc:
                errors.append({'year': year, 'paper': code, 'reason': str(exc)[:200]})
    report['generatedAt'] = datetime.now(timezone.utc).isoformat()
    report['ocrUsed'] = False
    report['errors'] = old_errors + errors
    report['lastRun'] = {'years': years, 'paperCodes': paper_codes, 'attempted': len(tasks), 'failures': len(errors)}
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
    parser.add_argument('--papers', nargs='+', help='Optional existing paper codes for a targeted run')
    args = parser.parse_args()
    if any(y < 90 or y > 115 for y in args.years):
        raise SystemExit('Expected years 90 through 115')
    run(args.years, args.papers)
