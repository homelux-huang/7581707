#!/usr/bin/env python3
"""Stage immutable 114 Chinese Q19 and Q20-23 shared-passage WebP candidates.

DRAFT ONLY: never promotes image QA, answers, questionVerified, or release.
Does not modify any pre-existing images, student data, main, or UI.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
YEAR = ROOT / 'sudu/data/processed/114'
SOURCE = ROOT / 'sudu/data/original/114/00-C/p007-f7c8a4b732-v2-w1400-q66.webp'
SOURCE_SHA256 = '63d68af4507fd198cd045a5a24b4efd4f33f95b1c234e991fe0f9ed65c76bfa2'
OFFICIAL_PDF_SHA256 = 'f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74'
DESTINATIONS = (
    ('114-00-C-19', 'webp-v2/00-C/114-00-C-19.webp', (90, 284, 1310, 563)),
    ('114-00-C-SHARED-20-23', 'webp-v2/shared/114-00-C-SHARED-20-23.webp', (90, 565, 1310, 1020)),
)
EVIDENCE = YEAR / 'qa-drafts/UNVERIFIED_114_C19_SHARED_20_23_20261023.json'


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage():
    if not SOURCE.is_file():
        raise FileNotFoundError('Official-page WebP is missing: '+str(SOURCE))
    if file_sha(SOURCE) != SOURCE_SHA256:
        raise ValueError('G0 source SHA256 mismatch; refuse crop')
    generated = []
    with Image.open(SOURCE) as img:
        if img.size != (1400, 1981):
            raise ValueError('Unexpected source dimensions')
        for identifier, relpath, bounds in DESTINATIONS:
            path = YEAR / relpath
            if not (0 <= bounds[0] < bounds[2] <= img.width and
                    0 <= bounds[1] < bounds[3] <= img.height):
                raise ValueError('Invalid source crop bounds')
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                # Exact decoded source pixels; lossless encoding avoids new text artifacts.
                img.crop(bounds).convert('RGB').save(path, 'WEBP', lossless=True, method=6)
            with Image.open(path) as out:
                if out.size != (bounds[2]-bounds[0], bounds[3]-bounds[1]):
                    raise ValueError('Existing draft has incompatible dimensions; never overwrite')
            generated.append({
                'id': identifier,
                'sourcePageWebpPath': SOURCE.relative_to(ROOT).as_posix(),
                'sourcePageWebpSha256': SOURCE_SHA256,
                'sourcePdfSha256Recorded': OFFICIAL_PDF_SHA256,
                'sourcePage': 7,
                'cropSourcePixelBounds': list(bounds),
                'output': path.relative_to(ROOT).as_posix(),
                'outputSha256': file_sha(path),
                'qaStatus': 'DRAFT_PENDING_DIRECT_ORIGINAL_VISUAL_QA',
                'independentVisualReviewCompleted': False,
                'answerVerified': False,
                'questionVerified': False,
                'integrationReady': False,
            })
    report = {
        'schemaVersion': 1,
        'year': 114,
        'scope': 'Q19 single-question crop and Q20-23 independent shared passage',
        'method': 'pixel_crop_existing_SHA_pinned_official_page_webp',
        'generated': generated,
        'warning': 'DRAFT ONLY; bounds are candidates, not visual QA PASS',
        'imageQaPassAdded': 0,
        'answerVerifiedAdded': 0,
        'questionVerifiedAdded': 0,
        'integrationReady': False,
        'releaseAllowed': False,
    }
    payload = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if EVIDENCE.exists():
        if EVIDENCE.read_text(encoding='utf-8') != payload:
            raise ValueError('Existing QA draft evidence differs; refuse overwrite')
    else:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(payload, encoding='utf-8')
    print('DRAFT only; 2 candidate WebP SHA256 pinned; QA PASS added=0')


if __name__ == '__main__':
    stage()
