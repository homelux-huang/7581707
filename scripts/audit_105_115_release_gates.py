#!/usr/bin/env python3
"""Read-only, fail-closed G0-G6 release audit for 105-115 TCTE data.

Normal CI reports blocked years without failing; --require-ready exits nonzero.
This auditor never modifies QA flags, source assets, or student records.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'sudu/data/processed'


def audit(year):
    base = D / str(year)
    report = {'year': year, 'integrationReady': False, 'gates': {}, 'blockers': []}
    blocks = report['blockers']

    def load(name):
        p = base / name
        if not p.is_file():
            blocks.append('missing:' + name)
            return None
        try:
            value = json.loads(p.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError, OSError):
            blocks.append('invalid_json:' + name)
            return None
        if not isinstance(value, dict):
            blocks.append('invalid_schema:' + name)
            return None
        return value

    inv = load('inventory.json')
    manifest = load('webp-manifest.json')
    bank = load('questions.json')
    answers = load('official-answer-evidence.json')
    visual = load('VISUAL_QA.json')
    if any(v is None for v in (inv, manifest, bank, answers, visual)):
        return report

    qs = bank.get('questions')
    images_list = manifest.get('items')
    answers_list = answers.get('items')
    visual_list = visual.get('questions', visual.get('items'))
    shared = manifest.get('sharedMaterialCrops', [])
    if any(not isinstance(a, list) or any(not isinstance(v, dict) for v in a)
           for a in (qs, images_list, answers_list, visual_list, shared)):
        blocks.append('invalid_ledger_schema')
        return report

    ids = [q.get('questionId') for q in qs]
    n = len(ids)
    if not n or any(not isinstance(qid, str) or not qid for qid in ids) or len(set(ids)) != n:
        blocks.append('invalid_unique_question_inventory')
        return report

    def index(rows, key, label):
        raw = [v.get(key) for v in rows]
        if any(not isinstance(k, str) or not k for k in raw) or len(set(raw)) != len(raw):
            blocks.append('duplicate_or_invalid_' + label)
        if len(rows) != n or set(raw) != set(ids):
            blocks.append(label + '_mismatch')
        return {v.get(key): v for v in rows}

    images = index(images_list, 'questionId', 'image_manifest')
    answer_by_id = index(answers_list, 'questionId', 'official_answer_ledger')
    visual_by_id = index(visual_list, 'questionId', 'visual_qa_ledger')
    identities = [(q.get('year'), q.get('paperCode'), q.get('originalQuestionNumber')) for q in qs]
    if any(y != year or not p or not isinstance(number, int) or isinstance(number, bool)
           or number <= 0 for y, p, number in identities):
        blocks.append('missing_or_wrong_canonical_question_identity')
    if len(set(identities)) != n:
        blocks.append('duplicate_canonical_question_identity')

    # Hash actual checked-out bytes, not only two matching claims in JSON.
    asset_cache = {}

    def asset_matches(rel, expected):
        key = (rel, expected)
        if key in asset_cache:
            return asset_cache[key]
        valid = False
        if isinstance(rel, str) and isinstance(expected, str) and len(expected) == 64:
            try:
                path = (ROOT / rel).resolve()
                if path.is_relative_to(ROOT.resolve()) and path.is_file():
                    digest = hashlib.sha256()
                    with path.open('rb') as asset:
                        for chunk in iter(lambda: asset.read(1024 * 1024), b''):
                            digest.update(chunk)
                    valid = digest.hexdigest() == expected
            except (OSError, ValueError):
                pass
        asset_cache[key] = valid
        return valid

    def correction_proof_valid(q, answer):
        """G3: checked correction PDF OR SHA-bound official no-objection index.

        A subject for which nobody filed an objection has no correction PDF.
        Its notice must be present in both the official-status ledger and
        the source-index evidence ledger with matching SHA and URL.
        """
        pdf_sha = answer.get('officialCorrectionPdfSha256')
        if isinstance(pdf_sha, str) and len(pdf_sha) == 64:
            return True
        page_sha = answer.get('officialCorrectionPageSha256')
        page_url = answer.get('officialCorrectionPageUrl')
        if not (isinstance(page_sha, str) and len(page_sha) == 64 and
                isinstance(page_url, str) and page_url.startswith('https://')):
            return False
        paper_code = q.get('paperCode')
        if not isinstance(paper_code, str):
            return False
        expected = 'OFFICIAL_' + paper_code.replace('-', '_') + '_NO_OBJECTION_SUBMITTED'
        if answer.get('officialCorrectionStatus') != expected:
            return False
        status_file = base / 'official-confirmation-status.json'
        if not status_file.is_file():
            return False
        try:
            status = json.loads(status_file.read_text(encoding='utf-8'))
            papers = status.get('confirmations', {})
            paper = papers.get(q.get('paperCode'), {})
            relative = status.get('officialNoticeEvidencePath')
            if (status.get('year') != year or
                    paper.get('officialStatus') != 'no_objection_submitted' or
                    not isinstance(relative, str)):
                return False
            notice_path = (ROOT / relative).resolve()
            if not notice_path.is_relative_to(ROOT.resolve()):
                return False
            notice = json.loads(notice_path.read_text(encoding='utf-8'))
            return (notice.get('year') == year and
                    notice.get('sourceIndexSha256') == page_sha and
                    notice.get('sourceIndexUrl') == page_url)
        except (OSError, ValueError, TypeError, AttributeError):
            return False

    image_pass = []
    for q in qs:
        qid = q['questionId']
        im = images.get(qid, {})
        vi = visual_by_id.get(qid, {})
        evidence = im.get('visualReviewEvidence') or {}
        if not isinstance(evidence, dict):
            evidence = {}
        sha = im.get('sha256') or im.get('outputSha256')
        source_sha = im.get('sourceSha256') or im.get('sourcePageWebpSha256')
        reviewed_source_sha = evidence.get('sourceSha256') or evidence.get('sourcePageSha256')
        source_ok = (isinstance(source_sha, str) and len(source_sha) == 64
                     and bool(im.get('sourcePage')) and bool(im.get('crop') or im.get('cropPixels'))
                     and bool(im.get('output'))
                     and (not reviewed_source_sha or reviewed_source_sha == source_sha))
        vsha = (vi.get('webpSha256') or vi.get('assetSha256') or
                vi.get('reviewedWebpSha256') or vi.get('candidateSha256'))
        vpass = vi.get('status', vi.get('result')) == 'PASS'
        claimed_pass = im.get('qaStatus') == 'PASS'
        good = (claimed_pass and source_ok and asset_matches(im.get('source'), source_sha)
                and asset_matches(im.get('output'), sha) and isinstance(sha, str) and len(sha) == 64
                and evidence.get('reviewedSha256') == sha
                and bool(evidence.get('reference')) and vpass and vsha == sha)
        if good:
            image_pass.append(qid)
        elif claimed_pass or vpass:
            blocks.append('visual_qa_evidence_mismatch:' + qid)
        # G4: when known, both identity and source/output SHA must agree.
        if im.get('paperCode') is not None and im['paperCode'] != q.get('paperCode'):
            blocks.append('image_paper_mismatch:' + qid)
        if im.get('originalQuestionNumber') is not None and im['originalQuestionNumber'] != q.get('originalQuestionNumber'):
            blocks.append('image_number_mismatch:' + qid)
        qp = q.get('questionProvenance') or {}
        if isinstance(qp, dict) and qp.get('webpSha256') and qp['webpSha256'] != sha:
            blocks.append('question_webp_sha_mismatch:' + qid)
        if isinstance(qp, dict) and qp.get('pixelSourceSha256') and qp['pixelSourceSha256'] != source_sha:
            blocks.append('question_source_sha_mismatch:' + qid)
        pdf_sha = im.get('sourcePdfSha256') or im.get('officialQuestionPdfSha256')
        if isinstance(qp, dict) and qp.get('officialPdfSha256') and pdf_sha and qp['officialPdfSha256'] != pdf_sha:
            blocks.append('question_official_pdf_sha_mismatch:' + qid)
        qa = q.get('assets') or {}
        if isinstance(qa, dict) and qa.get('sha256') and qa['sha256'] != sha:
            blocks.append('question_asset_sha_mismatch:' + qid)
        # G3: only a matching, independently evidenced final answer counts.
        answer = answer_by_id.get(qid, {})
        if q.get('answerVerified') is True:
            if (answer.get('answerVerified') is not True or
                answer.get('officialFinalAnswer') != q.get('answer') or
                answer.get('officialCorrectionChecked') is not True or
                not answer.get('qaEvidencePath') or
                not (answer.get('officialSourceSha256') or answer.get('officialPdfSha256')) or
                not correction_proof_valid(q, answer)):
                blocks.append('official_answer_evidence_mismatch:' + qid)
        if answer.get('answerVerified') is True and q.get('answerVerified') is not True:
            blocks.append('official_answer_flag_mismatch:' + qid)
        ap = q.get('answerProvenance') or {}
        answer_pdf_sha = (answer.get('officialSourceSha256') or answer.get('officialPdfSha256')
                          or answer.get('officialAnswerPdfSha256'))
        if (q.get('answerVerified') is True and isinstance(ap, dict)
                and ap.get('officialPdfSha256') and answer_pdf_sha
                and ap['officialPdfSha256'] != answer_pdf_sha):
            blocks.append('official_answer_source_sha_mismatch:' + qid)
    pending = sorted(set(ids) - set(image_pass))
    if pending:
        blocks.append('image_visual_qa_pending:' + str(len(pending)))

    qa_answers = sum(q.get('answerVerified') is True for q in qs)
    qa_questions = sum(q.get('questionVerified') is True for q in qs)
    if any(q.get('integrationReady') is not True for q in qs):
        blocks.append('question_level_integration_not_ready')
    if qa_answers != n:
        blocks.append('official_final_answer_qa_pending:' + str(n - qa_answers))
    if qa_questions != n:
        blocks.append('question_text_qa_pending:' + str(n - qa_questions))

    shared_pending = []
    ids_set = set(ids)
    for item in shared:
        sid = item.get('sharedMaterialId')
        evidence = item.get('visualReviewEvidence') or {}
        sha = item.get('sha256') or item.get('outputSha256')
        if item.get('qaStatus') != 'PASS':
            shared_pending.append(sid)
        elif (not isinstance(evidence, dict) or not sha or
              evidence.get('reviewedSha256') != sha or not evidence.get('reference')):
            blocks.append('shared_material_evidence_missing:' + str(sid))
        shared_source_sha = item.get('sourceSha256') or item.get('sourcePageWebpSha256')
        evidence_source_sha = (evidence.get('sourceSha256') or evidence.get('sourcePageSha256')
                               if isinstance(evidence, dict) else None)
        if (item.get('qaStatus') == 'PASS' and shared_source_sha and evidence_source_sha
                and shared_source_sha != evidence_source_sha):
            blocks.append('shared_material_source_sha_mismatch:' + str(sid))
        if (item.get('qaStatus') == 'PASS' and
                (not asset_matches(item.get('output'), sha) or
                 not asset_matches(item.get('source'), shared_source_sha))):
            blocks.append('shared_material_asset_sha_mismatch:' + str(sid))
        links = item.get('questionIds')
        if isinstance(links, list) and any(qid not in ids_set for qid in links):
            blocks.append('shared_material_unknown_question:' + str(sid))
    if shared_pending:
        blocks.append('shared_material_qa_pending:' + str(len(shared_pending)))
    if inv.get('integrationReady') is not True:
        blocks.append('inventory_not_release_ready')

    for required in ('ocr-raw-candidates.json', 'question-bank.sqlite3',
                     'REMAINING_QA.md', 'DATA_HANDOFF.md'):
        if not (base / required).is_file():
            blocks.append('missing:' + required)
    dbfile = base / 'question-bank.sqlite3'
    if dbfile.is_file():
        try:
            with sqlite3.connect(dbfile.as_uri() + '?mode=ro', uri=True) as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    blocks.append('sqlite_integrity_failure')
                count = db.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
                if count != n:
                    blocks.append('sqlite_question_count_mismatch')
        except (sqlite3.DatabaseError, OSError, ValueError):
            blocks.append('sqlite_unreadable')
    # Independent G5 evidence must agree with this exact on-disk database.
    g5file = D / '105-115-SQLITE_G5_READONLY_AUDIT.json'
    if not g5file.is_file():
        blocks.append('missing:105-115-SQLITE_G5_READONLY_AUDIT.json')
    else:
        try:
            g5 = json.loads(g5file.read_text(encoding='utf-8'))
            record = next((x for x in g5['years'] if x['year'] == year), None)
            if (g5.get('sourceDatabasesModified') is not False or
                g5.get('studentDataTouched') is not False or
                g5.get('released') is not False or record is None or
                record.get('g5Pass') is not True or record.get('sandboxImportPasses') != 2 or
                record.get('jsonRows') != n or record.get('onDiskRows') != n):
                blocks.append('sqlite_readonly_g5_evidence_failed')
            if (record and dbfile.is_file() and
                record.get('sqliteSha256') != hashlib.sha256(dbfile.read_bytes()).hexdigest()):
                blocks.append('sqlite_readonly_g5_db_sha_stale')
        except (ValueError, KeyError, TypeError, OSError, StopIteration):
            blocks.append('sqlite_readonly_g5_report_invalid')
    db_evidence = inv.get('sqlite') if isinstance(inv.get('sqlite'), dict) else {}
    reimports = db_evidence.get('reimportCount')
    if type(reimports) is not int or reimports < 2:
        blocks.append('sqlite_idempotent_reimport_not_evidenced')
    mismatches = db_evidence.get('shaMismatches')
    if not (type(mismatches) is int and mismatches == 0 or
            type(mismatches) is list and len(mismatches) == 0):
        blocks.append('sqlite_sha_mismatch_or_unverified')

    validation = load('VALIDATION.json')
    release = load('release-manifest.json')
    if validation is None or validation.get('integrationReady') is not True:
        blocks.append('validation_not_release_ready')
    if release is None or release.get('integrationReady') is not True:
        blocks.append('release_manifest_not_release_ready')
    if release is None or release.get('releaseAllowed') is not True:
        blocks.append('release_not_allowed')

    report.update({'candidateQuestions': n, 'webpVisualPass': len(image_pass),
                   'pendingImageIds': pending, 'answerVerified': qa_answers,
                   'questionVerified': qa_questions, 'sharedMaterialsPending': shared_pending,
                   'integrationReady': not blocks})
    report['gates'] = {
        'webp': len(image_pass) == n,
        'answer': qa_answers == n and not any(b.startswith('official_answer_') for b in blocks),
        'text': qa_questions == n,
        'shared': not shared_pending and not any(b.startswith('shared_material_') for b in blocks),
        'databaseAndRelease': not any(b.startswith((
            'missing:', 'invalid_', 'inventory_', 'validation_', 'release_', 'sqlite_',
            'image_', 'question_', 'duplicate_', 'visual_qa_', 'official_answer_')) for b in blocks)
    }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-ready', action='store_true')
    args = parser.parse_args()
    years = [audit(year) for year in range(105, 116)]
    total = sum(x.get('candidateQuestions', 0) for x in years)
    passed = sum(x.get('webpVisualPass', 0) for x in years)
    summary = {'scope': '105-115', 'readOnly': True, 'candidateQuestions': total,
               'imageVisualQaPass': passed, 'imageVisualQaPending': total - passed,
               'yearsReady': sum(x['integrationReady'] for x in years),
               'allYearsReady': all(x['integrationReady'] for x in years),
               'years': years}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.require_ready and not summary['allYearsReady']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
