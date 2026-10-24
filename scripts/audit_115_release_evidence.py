#!/usr/bin/env python3
"""Read-only evidence inventory against a pinned formal publisher and QA checkout.
This reports existing admission results, not a new pedagogical/UI approval.
"""
import argparse
import hashlib
import importlib.util
import json
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def head(root):
    return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()


def audit(source, publisher):
    script = publisher / 'scripts/sudu_verified_publish.py'
    spec = importlib.util.spec_from_file_location('formal_publisher', script)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    folder = source / 'sudu/data/processed/115'
    bank = gate.read(folder / 'questions.json')['questions']
    manifest = gate.read(folder / 'webp-manifest.json')
    entries = {x['questionId']: x for x in manifest['items']}
    shared = {x['sharedMaterialId']: x for x in manifest.get('sharedMaterialCrops', [])}
    batches = gate.reviewed_student_batches(source, 115)
    with sqlite3.connect((folder / 'question-bank.sqlite3').resolve().as_uri() + '?mode=ro', uri=True) as db:
        integrity = db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        rows = {qid: (json.loads(payload), digest == sha(payload.encode())) for qid, payload, digest in
                db.execute('SELECT question_id,payload_json,payload_sha256 FROM questions')}
    roundtrip = integrity and len(rows) == len(bank) == 205 and all(
        q['questionId'] in rows and rows[q['questionId']] == (q, True) for q in bank)
    results = []
    for original in bank:
        qid = original['questionId']
        item = entries.get(qid, {})
        q = gate.apply_independently_certified_review(source, 115, original, item, batches.get(qid))
        revision = gate.text_revision(q, item.get('sha256', ''))
        image = gate.image_proof(q, item, shared, source)
        text, official = gate.source_proof(q, image, roundtrip, revision)
        asset_bytes = gate.verify_bytes(source, item.get('output', ''), item.get('sha256', ''))
        ids = gate.shared_material_ids(q)
        shared_bytes = ids is not None and all(s in shared and gate.verify_bytes(
            source, shared[s].get('output', ''), shared[s].get('sha256', '')) for s in ids)
        identity = gate.stable(q, 115)
        checks = {
            'identity': bool(identity), 'sqliteRoundtrip': roundtrip,
            'imageEvidence': image, 'webpBytesAndDecode': asset_bytes,
            'sharedWebpBytesAndDecode': shared_bytes,
            'sourceTextAdmission': bool(text), 'officialFinalAdmission': bool(official),
            'independentSolveMatches': gate.independently_solved(q, revision) == 'matched',
            'teachingAndUiAdmission': gate.teaching_complete(q, identity[1] if identity else '', q.get('officialFinalAnswer', '')),
            'allCertificateFilesShaMatch': gate.certificates_complete(source, q, item, shared) if image else False,
        }
        refs = []
        for kind, proof, field, hash_field in [
            ('image', item.get('visualReviewEvidence') or {}, 'reference', 'referenceSha256'),
            *[(k, q.get(k) or {}, 'evidencePath', 'evidenceSha256') for k in
              ('textQaEvidence', 'officialFinalQaEvidence', 'teachingQaEvidence', 'uiQaEvidence')],
            ('independentSolve', q.get('independentSolve') or {}, 'auditEvidencePath', 'auditEvidenceSha256')]:
            refs.append({'kind': kind, 'path': proof.get(field), 'sha256': proof.get(hash_field),
                         'bytesMatch': gate.certificate_exists(source, proof, field, hash_field)})
        candidates = []
        for path in sorted((folder / 'review-evidence').glob(qid + '-*.json')):
            candidates.append({'path': str(path.relative_to(source)), 'sha256': sha(path.read_bytes())})
        results.append({'questionId': qid, 'subject': identity[1] if identity else None,
                        'questionRevision': revision, 'webpSha256': item.get('sha256'),
                        'teachingSha256': canonical(q['teaching']) if q.get('teaching') else None,
                        'existingPublisherAdmissible': all(checks.values()), 'checks': checks,
                        'blockers': [k for k, v in checks.items() if not v],
                        'certificates': refs, 'candidateDocumentsNotApproval': candidates})
    counts = Counter(k for r in results for k in r['blockers'])
    return {'schemaVersion': 1, 'year': 115, 'sourceCommit': head(source),
            'publisherCommit': head(publisher), 'publisherScriptSha256': sha(script.read_bytes()),
            'scope': 'READ_ONLY_EXISTING_EVIDENCE_NOT_NEW_APPROVAL_OR_DEPLOYMENT',
            'questionCount': len(results), 'sqliteRoundtripActual': roundtrip,
            'existingPublisherAdmissible': sum(r['existingPublisherAdmissible'] for r in results),
            'newApprovalsGranted': 0, 'deploymentsPerformed': 0,
            'blockerCounts': dict(sorted(counts.items())), 'questions': results}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--publisher', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    report = audit(args.source.resolve(), args.publisher.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'questions'}, ensure_ascii=False, indent=2))
