#!/usr/bin/env python3
"""Offline, reproducible corpus and original WebP audit. No OCR and no invented completeness.

Structural failures exit nonzero. Missing/unreviewed content is reported as pending.
Use --decode-images for full Pillow decode; --json/--markdown retain review evidence.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re, struct, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'web1.tcte.edu.tw', 'www.tcte.edu.tw', 'tcte.edu.tw'}
PLACEHOLDER = re.compile(r'本題.*(?:尚未成功擷取|尚未辨識|未辨識題)|不能把此提示當作正式題幹')
COVER = re.compile(r'^(?:請先核對考試科目|本試題共\s*\d+\s*題|本試題均為單一選擇題|考試開始鈴|請依題號順序作答)')
PENDING = re.compile(r'^(?:N/A|待補|待核實|尚待|不符合題意[。！!]?|逐選項說明待補[。！!]?)$', re.I)
FIELDS = ('papers rawRecords inScopeRecords excludedLegacyRecords textCandidates imageOnlyRecords placeholderRecords '
          'coverInstructionSuspects ocrUnreviewed questionVerified officialAnswerCandidates answersMatched '
          'answerVerifiedFlags answersReviewed questionWebpAvailable questionPageLocated questionMappingReviewed '
          'answerWebpAvailable teachingDrafts completeOptionReasons completeTeachingDrafts teachingVerified '
          'textbookVerified expectedCountCandidate expectedCountReviewed expectedCountUnknownPapers '
          'scoringRuleRecords basePointsReviewedRules verifiedScoringRules scoreablePapers missingNumberSlots extraNumberSlots').split()

def read_json(path): return json.loads(path.read_text('utf-8'))
def official_url(url):
    p = urlparse(str(url or ''))
    return p.scheme == 'https' and p.hostname in HOSTS

def in_scope(year, code):
    # Official index evidence: 90-91 commerce=14, 92-97=13, 98 onward=09.
    # BIZ-* aliases and all historical IDs remain stable for student histories.
    return str(code).startswith('00-') or code in ({'BIZ-1', 'BIZ-2'} if int(year) < 98 else {'09-1', '09-2'})

def review_evidence(q, part):
    review = (q.get('verification') or {}).get(part, {})
    if not isinstance(review, dict): review = {}
    return bool((q.get(part+'ReviewedBy') or review.get('reviewedBy')) and
                (q.get(part+'ReviewedAt') or review.get('reviewedAt')))

def answer_indices(q):
    a = q.get('acceptedAnswers') or [q.get('answer')]
    return a if isinstance(a, list) and a and all(type(v) is int and 0 <= v <= 3 for v in a) else []

def four_options(q):
    a = q.get('options')
    return isinstance(a, list) and len(a) == 4 and all(isinstance(s, str) and s.strip() for s in a)

def complete_reasons(q):
    a = q.get('wrongOptions')
    return four_options(q) and isinstance(a, list) and len(a) == 4 and all(
        isinstance(s, str) and s.strip() and not PENDING.fullmatch(s.strip()) for s in a)

def complete_teaching(q):
    p = q.get('practice') or {}
    return bool(complete_reasons(q) and all(q.get(k) for k in ('explanation','principle','steps','extension'))
        and isinstance(p, dict) and p.get('question') and isinstance(p.get('options'), list)
        and len(p['options']) == 4 and all(p['options']) and type(p.get('answerIndex')) is int
        and 0 <= p['answerIndex'] < 4 and p.get('explanation'))

def webp_dimensions(data):
    """Read actual RIFF dimensions, without a Pillow dependency in basic CI."""
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP': raise ValueError('not WebP RIFF')
    if struct.unpack_from('<I', data, 4)[0] + 8 != len(data): raise ValueError('invalid RIFF byte count')
    offset = 12
    while offset + 8 <= len(data):
        kind, size = data[offset:offset+4], struct.unpack_from('<I', data, offset+4)[0]
        body = data[offset+8:offset+8+size]
        if len(body) != size: raise ValueError('truncated WebP chunk')
        if kind == b'VP8X' and len(body) >= 10:
            return int.from_bytes(body[4:7], 'little')+1, int.from_bytes(body[7:10], 'little')+1
        if kind == b'VP8 ' and len(body) >= 10 and body[3:6] == b'\x9d\x01\x2a':
            return struct.unpack_from('<H', body, 6)[0]&0x3FFF, struct.unpack_from('<H', body, 8)[0]&0x3FFF
        if kind == b'VP8L' and len(body) >= 5 and body[0] == 0x2F:
            bits = int.from_bytes(body[1:5], 'little')
            return (bits&0x3FFF)+1, ((bits>>14)&0x3FFF)+1
        offset += 8+size+size%2
    raise ValueError('no image dimensions')

def inspect_images(root, index, role, errors, decode=False):
    r = dict(role=role, papers=0, pages=0, bytes=0, decodedPages=0, validFiles=0,
             missingGenerationMetadataPapers=[], legacyGrayscalePapers=0, errors=index.get('errors', []),
             generatedAt=index.get('generatedAt'), perPaper={})
    Image = None
    if decode:
        from PIL import Image
    methods = collections.Counter()
    for key, paper in index.get('papers', {}).items():
        r['papers'] += 1
        r['legacyGrayscalePapers'] += paper.get('renderVersion') == 1
        if not official_url(paper.get('source')): errors.append(f'{role} {key}: untrusted source')
        if not re.fullmatch('[0-9a-f]{64}', paper.get('pdfSha256', '')): errors.append(f'{role} {key}: no PDF SHA256')
        if not paper.get('generatedAt') or not paper.get('renderSettings'): r['missingGenerationMetadataPapers'].append(key)
        good, seen = set(), set()
        for page in paper.get('pages', []):
            no = page.get('page')
            if type(no) is not int or no < 1 or no in seen: errors.append(f'{role} {key}: duplicate/invalid page {no}')
            seen.add(no)
            path = (root/'sudu'/str(page.get('src', ''))).resolve()
            if not path.is_relative_to((root/'sudu/data/original').resolve()) or path.suffix != '.webp':
                errors.append(f'{role} {key}: unsafe image path'); continue
            try:
                data = path.read_bytes(); width, height = webp_dimensions(data)
                if (width,height) != (page.get('width'),page.get('height')) or len(data) != page.get('bytes'):
                    raise ValueError('dimensions/bytes disagree with index')
                if page.get('sha256') and hashlib.sha256(data).hexdigest() != page['sha256']:
                    raise ValueError('SHA256 disagrees with index')
                if Image:
                    with Image.open(path) as im:
                        im.load()
                        if im.size != (width,height): raise ValueError('decoded dimensions disagree')
                    r['decodedPages'] += 1
                r['validFiles'] += 1; r['bytes'] += len(data); good.add(no)
            except (OSError,ValueError) as exc: errors.append(f'{role} {key} page {no}: {exc}')
            r['pages'] += 1
        for qid, m in paper.get('questions', {}).items():
            methods[m.get('mapping','unknown')] += 1
            if m.get('page') is not None and m.get('page') not in good: errors.append(f'{role} {qid}: bad mapped page')
            if any(p not in good for p in m.get('pages', [])): errors.append(f'{role} {qid}: bad context page')
        r['perPaper'][key] = dict(pageCount=len(seen),validPages=sorted(good),completeFiles=bool(seen) and seen==good,
                                  source=paper.get('source'),pdfSha256=paper.get('pdfSha256'))
    r['mappingMethods'] = dict(methods)
    return r

def audit(root=ROOT, decode=False):
    errors, warnings, rows, totals, issues = [], [], [], collections.Counter({k:0 for k in FIELDS}), collections.Counter()
    fingerprint = hashlib.sha256()
    paths = [root/f'sudu/data/years/{y}.json' for y in range(90,116)]
    paths += [root/'sudu/data'/n for n in ('original/index.json','original/answers.json','scoring-rules.json','official-paper-catalog.json')]
    for p in paths:
        if p.exists(): fingerprint.update(str(p.relative_to(root)).encode()); fingerprint.update(p.read_bytes())
    indexes, images = {}, {}
    for role, name in (('question','index.json'),('answer','answers.json')):
        try: indexes[role] = read_json(root/'sudu/data/original'/name)
        except (OSError,ValueError) as exc: errors.append(f'{role} index: {exc}'); indexes[role] = {}
        images[role] = inspect_images(root,indexes[role],role,errors,decode)
    try: rules = read_json(root/'sudu/data/scoring-rules.json').get('rules', [])
    except (OSError,ValueError) as exc: errors.append(f'scoring rules: {exc}'); rules = []
    global_ids = set()
    for year in range(90,116):
        yc = collections.Counter({k:0 for k in FIELDS}); yr = dict(year=year,counts=yc,papers=[],pending=[])
        try: annual = read_json(root/f'sudu/data/years/{year}.json')
        except (OSError,ValueError) as exc: errors.append(f'{year} annual JSON: {exc}'); rows.append(yr); continue
        if annual.get('year') != year: errors.append(f'{year}: year mismatch')
        codes = set()
        for paper in annual.get('papers', []):
            code = paper.get('paper'); key = f'{year}/{code}'
            if code in codes: errors.append(f'{key}: duplicate paper')
            codes.add(code); c = collections.Counter({k:0 for k in FIELDS}); c['papers'] = 1
            scope = in_scope(year,code); records = paper.get('questions', [])
            qi = indexes['question'].get('papers', {}).get(key, {}); ai = indexes['answer'].get('papers', {}).get(key, {})
            qf = images['question']['perPaper'].get(key, {}); af = images['answer']['perPaper'].get(key, {})
            pending, suspects, numbers, ids = list(paper.get('issues', [])), [], set(), set()
            exp = paper.get('expectedCount')
            if type(exp) is int and exp > 0:
                c['expectedCountCandidate'] = exp
                if paper.get('expectedCountVerified') and paper.get('expectedCountSource'): c['expectedCountReviewed'] = exp
            else: c['expectedCountUnknownPapers'] = 1; pending.append('official_question_count_not_reviewed')
            if not scope: pending.append('old_09_engineering_record_preserved_not_commerce')
            if scope and not qf.get('completeFiles'): pending.append('question_webp_missing_or_incomplete')
            if scope and not af.get('completeFiles'): pending.append('answer_webp_missing_or_incomplete')
            source = paper.get('questionPdf') or next((q.get('source') for q in records if q.get('source')), None)
            if qi and source != qi.get('source'): errors.append(f'{key}: image/current question sources differ')
            ans_src = {q.get('answerSource') for q in records if q.get('answerSource')}
            if paper.get('answerPdf'): ans_src.add(paper['answerPdf'])
            if ai and ans_src and ai.get('source') not in ans_src: errors.append(f'{key}: image/current answer sources differ')
            for q in records:
                qid, number = q.get('id'), q.get('number'); c['rawRecords'] += 1
                c['inScopeRecords' if scope else 'excludedLegacyRecords'] += 1
                if not isinstance(qid,str) or not qid or qid in global_ids: errors.append(f'{key}: invalid/repeated ID {qid}')
                global_ids.add(qid); ids.add(qid)
                if type(number) is not int or number < 1 or number in numbers: errors.append(f'{qid}: invalid/duplicate question number')
                numbers.add(number)
                if q.get('year') != year or q.get('paper') != code: errors.append(f'{qid}: year/paper mismatch')
                if q.get('official') is not True or not official_url(q.get('source')): errors.append(f'{qid}: untrusted original source')
                qi_issues = q.get('issues', []); issues.update(qi_issues)
                placeholder = 'OCR_missing_question' in qi_issues or bool(PLACEHOLDER.search(q.get('question','')))
                cover = bool(COVER.search(q.get('question','').strip()))
                c['imageOnlyRecords'] += not bool(q.get('question','').strip())
                c['placeholderRecords'] += placeholder; c['coverInstructionSuspects'] += cover
                if cover: suspects.append(qid)
                c['textCandidates'] += bool(q.get('question')) and not placeholder and not cover
                c['ocrUnreviewed'] += bool(q.get('ocrUsed')) and not q.get('questionVerified')
                c['questionVerified'] += q.get('questionVerified') is True
                matched = (q.get('answerMatched') is True or q.get('answerVerified') is True) and bool(answer_indices(q))
                c['answerVerifiedFlags'] += q.get('answerVerified') is True
                c['officialAnswerCandidates'] += bool(q.get('officialAnswerCandidate')) or matched
                c['answersMatched'] += matched
                c['answersReviewed'] += q.get('answerVerified') is True and bool(answer_indices(q)) and review_evidence(q,'answer')
                if q.get('answerVerified') and (not four_options(q) or placeholder): errors.append(f'{qid}: false answer verification')
                if q.get('questionVerified') and (placeholder or cover): errors.append(f'{qid}: false question verification')
                m = qi.get('questions', {}).get(qid, {}); located = m.get('page') in qf.get('validPages', [])
                c['questionWebpAvailable'] += bool(qf.get('completeFiles')); c['questionPageLocated'] += located
                c['questionMappingReviewed'] += located and m.get('questionVerified') is True and bool(m.get('reviewedBy') and m.get('reviewedAt'))
                c['answerWebpAvailable'] += bool(af.get('completeFiles'))
                c['teachingDrafts'] += bool(q.get('explanation')) and not q.get('teachingVerified')
                c['completeOptionReasons'] += complete_reasons(q); c['completeTeachingDrafts'] += complete_teaching(q)
                c['teachingVerified'] += q.get('teachingVerified') is True; c['textbookVerified'] += q.get('textbookVerified') is True
                if q.get('teachingVerified') and not complete_teaching(q): errors.append(f'{qid}: verified teaching lacks reasons/practice')
                if q.get('textbookVerified'):
                    book = q.get('textbook') or {}
                    if not isinstance(book,dict) or not all(book.get(k) for k in ('publisher','title','chapter')):
                        errors.append(f'{qid}: textbook lacks publisher/title/chapter')
            if type(exp) is int and exp > 0:
                c['missingNumberSlots'] = len(set(range(1,exp+1))-numbers); c['extraNumberSlots'] = len(numbers-set(range(1,exp+1)))
                if c['extraNumberSlots']: pending.append('expected_count_or_number_extraction_conflict')
            orphan = sorted(set(qi.get('questions', {}))-ids)
            if orphan: pending.append('stale_image_question_links')
            if suspects: pending.append('cover_instructions_misparsed_as_question')
            if c['answersMatched'] > c['answersReviewed']: pending.append('automatic_answer_pairing_requires_independent_review')
            paper_rules = [r for r in rules if str(r.get('year'))==str(year) and r.get('paper')==code]
            c['scoringRuleRecords'] = len(paper_rules)
            c['basePointsReviewedRules'] = sum(r.get('basePointsVerified') is True and official_url(r.get('sourceUrl'))
                and bool(r.get('reviewedBy') and r.get('reviewedAt')) for r in paper_rules)
            vr = [r for r in paper_rules if r.get('verified') is True
                  and official_url(r.get('sourceUrl')) and r.get('reviewedBy') and r.get('reviewedAt')]
            c['verifiedScoringRules'] = len(vr)
            c['scoreablePapers'] = int(bool(scope and vr and exp and len(records)==exp and c['questionVerified']==exp
                                      and c['answersReviewed']==exp and not c['missingNumberSlots'] and not c['extraNumberSlots']))
            if paper.get('complete') and (not exp or len(records)!=exp or c['questionVerified']!=exp or c['teachingVerified']!=exp):
                errors.append(f'{key}: FALSE_COMPLETE')
            yr['papers'].append(dict(key=key,year=year,paper=code,subject=paper.get('subject'),inScope=scope,questionSource=source,
                answerSources=sorted(ans_src),expectedCountCandidate=exp,expectedCountVerified=bool(paper.get('expectedCountVerified') and paper.get('expectedCountSource')),
                counts=dict(c),coverInstructionIds=suspects,orphanImageQuestionIds=orphan,pending=sorted(set(pending)),
                imagePageCount=qf.get('pageCount',0),answerImagePageCount=af.get('pageCount',0)))
            yc.update(c)
        if year < 98 and not {'BIZ-1','BIZ-2'}.issubset(codes): yr['pending'].append('official_commerce_professional_papers_missing')
        if '00-C' not in codes: yr['pending'].append('official_chinese_paper_missing')
        if not any(str(c).startswith('00-M') for c in codes): yr['pending'].append('official_math_paper_missing')
        yr['counts'] = dict(yc); totals.update(yc); rows.append(yr)
    if totals['questionMappingReviewed'] < totals['rawRecords']: warnings.append('Original WebP availability does not prove per-question/cross-page mapping.')
    if totals['answersReviewed'] < totals['answersMatched']: warnings.append('Machine answer matching is separate from independent answer review.')
    if totals['expectedCountReviewed'] < totals['expectedCountCandidate']: warnings.append('Expected counts are unreviewed extraction candidates.')
    try: revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError): revision = None
    return dict(schema=2,generatedAt=datetime.now(timezone.utc).isoformat(),baseCommit=revision,dataFingerprintSha256=fingerprint.hexdigest(),
        decodeImages=decode,status='structural_checks_failed' if errors else 'structural_checks_passed_content_pending',allContentComplete=False,
        totals=dict(totals),years=rows,images=images,questionIssues=dict(issues),warnings=warnings,errors=errors,definitions={
        'rawRecords':'含占位、可疑封面及歷史誤收卷，不是已核實原題數。',
        'answersMatched':'舊answerVerified或新answerMatched的有效答案配對；不是人工覆核。',
        'answersReviewed':'answerVerified及answerReviewedBy/At或verification.answer皆有證據。',
        'questionWebpAvailable':'該卷全部索引原頁可讀；不表示當題裁切、共享題組與頁碼已正確。',
        'questionPageLocated':'候選頁碼指向存在原頁，當題內容尚待人工覆核。',
        'questionMappingReviewed':'候選頁碼另有reviewedBy/At與questionVerified證據。',
        'answerWebpAvailable':'該卷官方答案圖檔完整；不是逐題答案文字已核實。',
        'expectedCountCandidate':'舊自動擷取expectedCount，可能誤讀或混合不同分卷題號。',
        'scoreablePapers':'範圍、題數、原題、答案與官方規則全部覆核，不含人工待閱卷部分。'})

def markdown(r):
    t=r['totals']
    out=['# 統測題庫完整度稽核','',f"產生時間：{r['generatedAt']}。",f"基準 commit：`{r['baseCommit']}`。資料指紋：`{r['dataFingerprintSha256']}`。",'',
        '重跑：`python scripts/check_tcte_corpus.py --decode-images --json sudu/data/corpus-audit.json --markdown docs/SUDU_CORPUS_AUDIT.md`。',
        '結構檢查通過只代表格式、索引及圖檔完整性，不表示所有原題、答案、教學或計分完成。','',
        '## 實際統計','',f"- 26 年／{t['papers']} 卷／{t['rawRecords']:,} 原始紀錄；符合商管及共同科範圍 {t['inScopeRecords']:,}。",
        f"- 原題核實 {t['questionVerified']}，答案程式配對 {t['answersMatched']:,}，具覆核紀錄 {t['answersReviewed']}。",
        f"- 純影像導覽 {t['imageOnlyRecords']}，占位 {t['placeholderRecords']}，封面說明疑似誤當題目 {t['coverInstructionSuspects']}，OCR 未覆核 {t['ocrUnreviewed']}。",
        f"- 教學草稿 {t['teachingDrafts']}／完整四選項理由 {t['completeOptionReasons']}／完整詳解草稿 {t['completeTeachingDrafts']}／教學核實 {t['teachingVerified']}／教材核實 {t['textbookVerified']}。",
        f"- 配分規則紀錄 {t['scoringRuleRecords']}／封面基本配分已覆讀 {t['basePointsReviewedRules']}／完整核實配分規則 {t['verifiedScoringRules']}／完整可評分試卷 {t['scoreablePapers']}。",'', '## 計數定義','']
    out += [f'- `{k}`：{v}' for k,v in r['definitions'].items()]
    out += ['', '## 90–115 年逐年表','', '應有題數是既有自動擷取候選值，不能直接當成全卷已核實題數。WebP 欄計算原頁可存取之紀錄數；當題精確映射另列。','',
        '| 年 | 卷數 | raw／範圍內 | 題數候選／未明卷 | 題幹核實 | 答案配對／覆核 | 原題 WebP／候選頁 | 答案 WebP | 草稿／選項理由 | 教學／教材核實 | 規則／可評分卷 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for y in r['years']:
        c=y['counts'];out.append(f"| {y['year']} | {c['papers']} | {c['rawRecords']}／{c['inScopeRecords']} | {c['expectedCountCandidate']}／{c['expectedCountUnknownPapers']} | {c['questionVerified']} | {c['answersMatched']}／{c['answersReviewed']} | {c['questionWebpAvailable']}／{c['questionPageLocated']} | {c['answerWebpAvailable']} | {c['teachingDrafts']}／{c['completeOptionReasons']} | {c['teachingVerified']}／{c['textbookVerified']} | {c['verifiedScoringRules']}／{c['scoreablePapers']} |")
    out += ['', '## 官方類群代碼證據','',
        '- [90](https://web1.tcte.edu.tw/EXAM/090_4y/)及[91](https://web1.tcte.edu.tw/EXAM/091_4y/)年度目錄：14 商業類。',
        '- [92](https://web1.tcte.edu.tw/EXAM/092_4y/)、[93](https://web1.tcte.edu.tw/EXAM/093_4y/)、[94](https://web1.tcte.edu.tw/EXAM/094_4y/)、[95](https://web1.tcte.edu.tw/EXAM/095_4y/)、[96](https://web1.tcte.edu.tw/EXAM/096_4y/)、[97](https://web1.tcte.edu.tw/EXAM/097_4y/)年度目錄：13 商業類。',
        '- [98](https://web1.tcte.edu.tw/EXAM/098_4y/)及[99](https://web1.tcte.edu.tw/EXAM/099_4y/)已改為 09 商管群，不能用 `<100` 一律排除。歷史錯收工程卷保留 ID 與作答歷史，不當作商管卷。','',
        '## 逐卷證據與待辦','', '| 年／卷 | 範圍 | raw／應有候選 | 答案配對／覆核 | 原頁／候選映射 | 答案頁 | 占位／封面疑義 | 待辦 |', '|---|---|---:|---:|---:|---:|---:|---|']
    for y in r['years']:
        for p in y['papers']:
            c=p['counts'];out.append(f"| {p['key']} | {'商管／共同科' if p['inScope'] else '歷史誤收保留'} | {c['rawRecords']}／{p['expectedCountCandidate'] or '待核實'} | {c['answersMatched']}／{c['answersReviewed']} | {p['imagePageCount']}／{c['questionPageLocated']} | {p['answerImagePageCount']} | {c['placeholderRecords']}／{c['coverInstructionSuspects']} | {'；'.join(p['pending']) or '逐題核實、教學及教材待補'} |")
    out += ['', '## 優先覆核清單','']
    for y in r['years']:
        if y['pending']:out.append(f"- {y['year']}：{'；'.join(y['pending'])}。")
        for p in y['papers']:
            if p['coverInstructionIds']:out.append(f"- {p['key']} 封面疑義：{', '.join(p['coverInstructionIds'])}；保留 ID，以完整原卷核對題幹。")
            if p['counts']['extraNumberSlots']:out.append(f"- {p['key']} 有 {p['counts']['extraNumberSlots']} 個題號超出候選 expectedCount，須核對封面與分卷。")
    out += ['', '## 驗收及阻塞','',f"- 結構錯誤 {len(r['errors'])}；完整影像解碼：{'已執行' if r['decodeImages'] else '未執行，只有 RIFF／尺寸／大小驗證'}。",
        '- 缺乏原題、答案、教材覆核證據的旗標不可自動改為 true；教學草稿不算教師核實。',
        '- 自動文字錨點不代表共享題組及跨頁內容已齊全；未可靠裁切時保留全卷原頁。',
        '- 90 年官方答案為 HTML；91 年為跨科共用單頁，須保留完整標題及科目對照，不猜逐題答案。',
        '- 精確教材章節、逐題教師覆核和各卷正式配分需補外部證據；N/A／待核實持續保留。',
        '- 本報告不宣稱部署完成；commit／Actions／Pages 證據見 SUDU_PROGRESS_TRACKER.md。','']
    out += [f'- ERROR：{e}' for e in r['errors']]
    return '\n'.join(out)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--decode-images',action='store_true');p.add_argument('--json',type=Path);p.add_argument('--markdown',type=Path)
    a=p.parse_args();r=audit(a.root.resolve(),a.decode_images)
    for y in r['years']:
        c=y['counts'];print('AUDIT_YEAR',y['year'],c['rawRecords'],c['answersMatched'],c['teachingVerified'],'questionWebP',c['questionWebpAvailable'],'answerWebP',c['answerWebpAvailable'])
    print('AUDIT_TOTAL',json.dumps(r['totals'],sort_keys=True))
    for w in r['warnings']:print('PENDING',w)
    for e in r['errors']:print('ERROR',e)
    for path,body in ((a.json,json.dumps(r,ensure_ascii=False,indent=2)+'\n'),(a.markdown,markdown(r))):
        if path:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body,'utf-8')
    return bool(r['errors'])
if __name__=='__main__':sys.exit(main())
