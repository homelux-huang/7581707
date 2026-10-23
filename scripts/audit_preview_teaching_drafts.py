#!/usr/bin/env python3
"""Read-only integrity audit for the frozen 128 teaching drafts; not teaching approval."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / 'sudu/teaching-drafts/preview-128-20261023'

def audit():
    errors, pending = [], []
    evidence = json.loads((DRAFT / 'official-final-evidence-20261023.json').read_text())['questions']
    records = {p.stem: json.loads(p.read_text()) for p in DRAFT.glob('1??-*.json')}
    if len(records) != 128 or set(records) != set(evidence):
        errors.append('Frozen 128-question scope differs from official evidence registry')
    manifest = json.loads((DRAFT / 'progress.json').read_text())
    items = {item['questionId']: item for item in manifest['items']}
    if manifest['scopeTotal'] != 128 or len(manifest['items']) != 128 or set(items) != set(records):
        errors.append('Frozen manifest must list exactly 128 unique draft records')
    verified_image_hashes = {}

    def actual_sha256(repo_path):
        if repo_path not in verified_image_hashes:
            binary = ROOT / 'sudu' / repo_path
            verified_image_hashes[repo_path] = (
                hashlib.sha256(binary.read_bytes()).hexdigest() if binary.is_file() else None
            )
        return verified_image_hashes[repo_path]

    for q, d in records.items():
        t, comparison = d['teaching'], d['answerComparison']
        image = ROOT / 'sudu' / d['image']
        if actual_sha256(d['image']) != d['imageSha256']:
            errors.append(q + ': original image digest mismatch')
        registry_item = items.get(q, {})
        if registry_item.get('image') != d['image'] or registry_item.get('imageSha256') != d['imageSha256']:
            errors.append(q + ': draft image path or SHA differs from frozen manifest')
        shared = registry_item.get('sharedImages', [])
        for ref in shared:
            if actual_sha256(ref['image']) != ref['sha256']:
                errors.append(q + ': shared image digest mismatch: ' + ref['image'])
        if d.get('sharedImages') is not None and d.get('sharedImages') != shared:
            errors.append(q + ': shared image association differs from frozen manifest')
        if d.get('deploy') is not False or d.get('studentReleaseApproved') is not False:
            errors.append(q + ': draft release gate unexpectedly open')
        if comparison.get('officialAnswer') != evidence[q]['officialAnswer']:
            errors.append(q + ': official answer differs from evidence registry')
        if d['aiAnswer'] != evidence[q]['officialAnswer'] and not comparison.get('conflictWarningRequired'):
            errors.append(q + ': differing AI answer lacks warning')
        options = t.get('optionExplanations', {})
        if set(options) != set('ABCD') or any(not v.get('teacher') or not v.get('elementary') for v in options.values()):
            errors.append(q + ': incomplete four-option dual-level explanations')
        correctly_labeled = [key for key, option in options.items() if option.get('isCorrect') is True]
        if correctly_labeled != [evidence[q]['officialAnswer']]:
            errors.append(q + ': exactly one option must match verified official answer')
        if d['qa'].get('officialFinalEvidence', {}).get('officialAnswer') != evidence[q]['officialAnswer']:
            errors.append(q + ': official QA evidence differs from registry')
        if t.get('hasExamCalculation') is False and t.get('examCalculation') not in (None, {}):
            errors.append(q + ': hidden calculation has unexpected payload')
        if t.get('hasExamCalculation') is True:
            calc = t.get('examCalculation') or {}
            if not calc.get('substitutionAndSteps') or not calc.get('result'):
                errors.append(q + ': calculation lacks steps or result')
        if d['qa'].get('independentTeachingReview') != 'PASS' or d['qa'].get('uiReview') != 'PASS':
            pending.append(q)
    js = (DRAFT / 'solution-steps-128.js').read_text()
    bundle = json.loads(js[js.index('{'):js.rindex('}') + 1])
    for item in bundle['byQuestion'].values():
        if item != records[item['questionId']]['teaching']['stepByStep']:
            errors.append(item['questionId'] + ': generated step bundle differs from record')
    return {'records': len(records), 'errors': errors, 'pendingFullAcceptanceCount': len(pending),
            'meaning': 'Integrity only; no OCR, no new visual/teaching approval, no deployment'}

if __name__ == '__main__':
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
