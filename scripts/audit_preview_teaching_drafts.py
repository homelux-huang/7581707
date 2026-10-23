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
    for q, d in records.items():
        t, comparison = d['teaching'], d['answerComparison']
        image = ROOT / 'sudu' / d['image']
        if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != d['imageSha256']:
            errors.append(q + ': original image digest mismatch')
        if d.get('deploy') is not False or d.get('studentReleaseApproved') is not False:
            errors.append(q + ': draft release gate unexpectedly open')
        if comparison.get('officialAnswer') != evidence[q]['officialAnswer']:
            errors.append(q + ': official answer differs from evidence registry')
        if d['aiAnswer'] != evidence[q]['officialAnswer'] and not comparison.get('conflictWarningRequired'):
            errors.append(q + ': differing AI answer lacks warning')
        options = t.get('optionExplanations', {})
        if set(options) != set('ABCD') or any(not v.get('teacher') or not v.get('elementary') for v in options.values()):
            errors.append(q + ': incomplete four-option dual-level explanations')
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
