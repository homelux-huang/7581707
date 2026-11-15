"""Durable G8 custody: retain authentic public report/PNGs, never private G6.

Capture is a review candidate, not a trust grant. Acceptance requires exact
Git blobs and the complete G8 receipt to be pinned at protected main.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import io
import json
import os
from functools import lru_cache
from pathlib import Path
import re
import zipfile
from urllib.request import Request, urlopen

from scripts import sudu_independent_review_gate as gate

SCHEMA = 'G8_DURABLE_CUSTODY_V1'
PREFIX = 'sudu/release-governance/g8-archives/'
MAX_ZIP = 64 * 1024 * 1024
MAX_MEMBER = 20 * 1024 * 1024
RECEIPT_FIELDS = ('stageManifestSha256', 'payloadSha256', 'rowSha256',
                  'authorizationSha256', 'reportSha256', 'codeBindings',
                  'codeCommit', 'runId', 'jobId', 'artifactId', 'artifactSha256')


def bridge():
    from scripts import sudu_g8_release_bridge
    return sudu_g8_release_bridge


def require(ok, message):
    bridge().require(ok, 'archive: ' + message)


def get_json(path):
    require(re.fullmatch(r'/branches/main|/contents/sudu/release-governance/independent-review-policy[.]json\?ref=[0-9a-f]{40}|/git/blobs/[0-9a-f]{40}|/git/trees/[0-9a-f]{40}', path), 'unsupported GitHub endpoint')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': '7581707-G8-custody'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    request = Request('https://api.github.com/repos/' + gate.REPO + path, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read(MAX_ZIP * 2), object_pairs_hook=gate._no_duplicate_keys)


def protected_head():
    main = get_json('/branches/main')
    require(main.get('name') == 'main' and main.get('protected') is True, 'protected main required')
    head = main['commit']['sha']
    require(gate.HEX40.fullmatch(head), 'invalid protected commit')
    return head


def decoded_blob(doc, expected):
    require(doc.get('encoding') == 'base64', 'expected GitHub raw base64 blob')
    raw = base64.b64decode(''.join(doc['content'].split()), validate=True)
    require(len(raw) <= MAX_ZIP and doc.get('sha') == expected == gate.blob_oid(raw), 'GitBlob bytes mismatch')
    return raw


def current_policy():
    """Use current protected policy without changing the pinned code checkout."""
    head = protected_head()
    doc = get_json('/contents/sudu/release-governance/independent-review-policy.json?ref=' + head)
    raw = decoded_blob(doc, doc.get('sha'))
    policy = json.loads(raw, object_pairs_hook=gate._no_duplicate_keys)
    require(policy.get('schemaVersion') == 1 and policy.get('githubRepository') == gate.REPO
            and policy.get('reviewMode') == 'DISTINCT_AI_CONTENT_RECEIPT_V1'
            and policy.get('requireHumanTeacher') is False, 'protected V1 policy required')
    return head, policy


@lru_cache(maxsize=256)
def immutable_tree(sha):
    return get_json('/git/trees/' + sha)


def blob_at(head, rel, expected):
    """Check tree membership before reading a blob; no source branch or raw URL."""
    require(rel.startswith(PREFIX) and '\\' not in rel and '..' not in Path(rel).parts
            and not Path(rel).is_absolute() and gate.HEX40.fullmatch(str(expected)), 'invalid custody path/blob')
    tree_sha = head
    parts = rel.split('/')
    for index, part in enumerate(parts):
        tree = immutable_tree(tree_sha)
        matches = [x for x in tree['tree'] if x.get('path') == part]
        require(len(matches) == 1, 'custody path absent from protected commit')
        node = matches[0]
        if index < len(parts) - 1:
            require(node.get('type') == 'tree' and node.get('mode') == '040000', 'custody path is not directory')
            tree_sha = node['sha']
        else:
            require(node.get('type') == 'blob' and node.get('mode') == '100644' and node.get('sha') == expected,
                    'custody file not owner-pinned regular GitBlob')
    return decoded_blob(get_json('/git/blobs/' + expected), expected)


def receipt(entry):
    data = {key: entry[key] for key in RECEIPT_FIELDS}
    for field in ('stageManifestSha256', 'payloadSha256', 'rowSha256', 'authorizationSha256', 'reportSha256', 'artifactSha256'):
        require(gate.SHA.fullmatch(str(data[field])), 'invalid receipt SHA256')
    require(gate.HEX40.fullmatch(str(data['codeCommit'])), 'invalid code commit')
    require(isinstance(data['codeBindings'], dict) and data['codeBindings'], 'missing code bindings')
    for key in ('runId', 'jobId', 'artifactId'):
        require(type(data[key]) is int and data[key] > 0, 'actual numeric Actions identifier required')
    return data


def metadata_valid(entry, records):
    """Same initial live-run checks also apply to the owner-pinned capture."""
    run, job, artifact = (records[k] for k in ('run', 'job', 'artifact'))
    b = bridge()
    require(str(run.get('path', '')).split('@')[0] == b.FORMAL_WORKFLOW
            and run.get('event') == 'workflow_dispatch' and run.get('head_branch') == 'main', 'formal protected workflow required')
    require(run.get('id') == entry['runId'] and run.get('head_sha') == entry['codeCommit']
            and run.get('status') == 'completed' and run.get('conclusion') == 'success', 'successful exact-code run required')
    require(job.get('id') == entry['jobId'] and job.get('name') == 'formal_g8'
            and job.get('run_id') == entry['runId'] and job.get('head_sha') == entry['codeCommit']
            and job.get('conclusion') == 'success', 'successful exact formal job required')
    require(artifact.get('id') == entry['artifactId'] and artifact.get('expired') is False
            and artifact.get('digest') == 'sha256:' + entry['artifactSha256']
            and (artifact.get('workflow_run') or {}).get('id') == entry['runId'], 'original unexpired artifact digest required')


def archive_valid(raw, entry):
    """Validate in memory, never extract ZIP paths or load private raw evidence."""
    require(len(raw) <= MAX_ZIP and gate.digest(raw) == entry['artifactSha256'], 'original ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == 17 and len(set(names)) == 17 and 'report.json' in names, 'exact report and sixteen PNG members required')
        for info in archive.infolist():
            mode = (info.external_attr >> 16) & 0o170000
            require(info.filename == Path(info.filename).name and '\\' not in info.filename
                    and not info.is_dir() and mode != 0o120000 and info.file_size <= MAX_MEMBER,
                    'unsafe archive member')
        report_raw = archive.read('report.json')
        require(gate.digest(report_raw) == entry['reportSha256'], 'original report bytes mismatch')
        report = json.loads(report_raw, object_pairs_hook=gate._no_duplicate_keys)
        b = bridge()
        require(report.get('schema') == b.SCHEMA and report.get('status') == 'FORMAL_G8'
                and report.get('runId') == entry['runId'] and report.get('errors') == [], 'successful original report required')
        for field in ('codeCommit', 'codeBindings', 'stageManifestSha256', 'payloadSha256'):
            require(report.get(field) == entry[field], 'report binding ' + field)
        completed = gate._time(report.get('completedAt'))
        require(completed <= datetime.now(timezone.utc), 'future report completion')
        cases = report.get('cases')
        require(isinstance(cases, list) and len(cases) == 16, 'complete sixteen cases required')
        expected = {'report.json'}
        matrix = set()
        from PIL import Image
        for case in cases:
            key = (case.get('width'), case.get('height'), case.get('theme'))
            require(key in b.MATRIX and key not in matrix and case.get('result') == 'PASS', 'unique sixteen matrix required')
            matrix.add(key)
            name = case['screenshot']
            require(name.endswith('.png') and name in names and name not in expected, 'unique original PNG required')
            expected.add(name)
            for field in ('stageManifestSha256', 'payloadSha256'):
                require(case.get(field) == entry[field], 'case bytes binding')
            png = archive.read(name)
            require(gate.digest(png) == case.get('screenshotSha256'), 'PNG bytes changed')
            with Image.open(io.BytesIO(png)) as image:
                require(image.format == 'PNG' and image.size == key[:2], 'PNG viewport mismatch')
                image.load()
        require(matrix == set(b.MATRIX) and set(names) == expected, 'unexpected archive member or missing matrix')
        return report


def capture(entry, qid, archive_path, dest):
    """Validate real live Actions before expiry; output an UNTRUSTED PR candidate."""
    b = bridge()
    require(b.pub.QID.fullmatch(qid), 'invalid QID')
    clean = receipt(entry)
    records = {kind: b.github('/actions/' + route + '/' + str(clean[field]))
               for kind, route, field in [('run', 'runs', 'runId'), ('job', 'jobs', 'jobId'), ('artifact', 'artifacts', 'artifactId')]}
    metadata_valid(clean, records)
    now = datetime.now(timezone.utc)
    artifact = records['artifact']
    require(gate._time(artifact.get('created_at')) <= now < gate._time(artifact.get('expires_at')), 'capture must precede real expiry')
    raw = Path(archive_path).read_bytes()
    report = archive_valid(raw, clean)
    require(gate._time(report['completedAt']) <= gate._time(artifact['created_at']), 'report after artifact creation')
    # Keep only evidence-relevant API fields, never user profiles, URLs or tokens.
    keys = {'run': ['id', 'path', 'event', 'head_branch', 'head_sha', 'status', 'conclusion'],
            'job': ['id', 'name', 'run_id', 'head_sha', 'conclusion'],
            'artifact': ['id', 'expired', 'digest', 'workflow_run', 'created_at', 'expires_at']}
    sanitized = {kind: {key: records[kind][key] for key in fields} for kind, fields in keys.items()}
    sanitized['artifact']['workflow_run'] = {'id': clean['runId']}
    proof = {'schema': SCHEMA, 'qid': qid, 'status': 'CAPTURED_PENDING_INDEPENDENT_OWNER_REVIEW',
             'capturedAt': now.isoformat(), 'receipt': clean, 'actionsAtCapture': sanitized}
    folder = PREFIX + qid + '/' + clean['artifactSha256'] + '/'
    capture_raw = b.serialized(proof)
    spec = {'schema': SCHEMA, 'qid': qid, 'capturePath': folder + 'capture.json',
            'captureGitBlobSha': gate.blob_oid(capture_raw), 'archivePath': folder + 'original.zip',
            'archiveGitBlobSha': gate.blob_oid(raw)}
    dest = b.private_new(dest, b.ROOT)
    dest.mkdir(mode=0o700)
    b.put(dest, spec['capturePath'], capture_raw)
    b.put(dest, spec['archivePath'], raw)
    candidate = copy.deepcopy(clean)
    candidate['durableArchive'] = spec
    b.put(dest, 'G8_OWNER_REVIEW_CANDIDATE.json', b.serialized(candidate))
    return {'status': 'CAPTURED_PENDING_INDEPENDENT_OWNER_REVIEW', 'qid': qid,
            'archiveGitBlobSha': spec['archiveGitBlobSha'], 'trusted': False, 'deployed': False}


def verify_owned(entry):
    """Protected main is the revocable trust root, not artifact retention TTL."""
    spec = entry.get('durableArchive')
    require(isinstance(spec, dict) and spec.get('schema') == SCHEMA, 'owner-pinned durable custody required')
    qid = spec.get('qid')
    require(isinstance(qid, str) and bridge().pub.QID.fullmatch(qid), 'invalid owner QID')
    head, policy = current_policy()
    require((policy.get('trustedG8Receipts') or {}).get(qid) == entry, 'custody receipt not current protected owner registry')
    clean = receipt(entry)
    folder = PREFIX + str(qid) + '/' + clean['artifactSha256'] + '/'
    require(spec.get('capturePath') == folder + 'capture.json' and spec.get('archivePath') == folder + 'original.zip', 'exact owner custody paths required')
    capture_raw = blob_at(head, spec['capturePath'], spec.get('captureGitBlobSha'))
    proof = json.loads(capture_raw, object_pairs_hook=gate._no_duplicate_keys)
    require(proof.get('schema') == SCHEMA and proof.get('qid') == qid
            and proof.get('status') == 'CAPTURED_PENDING_INDEPENDENT_OWNER_REVIEW'
            and proof.get('receipt') == clean, 'owner-pinned capture binding')
    captured = gate._time(proof.get('capturedAt'))
    metadata_valid(clean, proof['actionsAtCapture'])
    artifact = proof['actionsAtCapture']['artifact']
    require(gate._time(artifact.get('created_at')) <= captured < gate._time(artifact.get('expires_at'))
            and captured <= datetime.now(timezone.utc), 'capture chronology/expiry')
    raw = blob_at(head, spec['archivePath'], spec.get('archiveGitBlobSha'))
    report = archive_valid(raw, clean)
    require(gate._time(report['completedAt']) <= gate._time(artifact['created_at']), 'report chronology')
    return {'protectedCommit': head, 'archiveSha256': clean['artifactSha256'], 'runId': clean['runId']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entry', type=Path, required=True)
    parser.add_argument('--qid', required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--dest', type=Path, required=True)
    args = parser.parse_args()
    try:
        entry = json.loads(args.entry.read_bytes(), object_pairs_hook=gate._no_duplicate_keys)
        print(json.dumps(capture(entry, args.qid, args.archive, args.dest), sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        parser.exit(2, str(error) + '\n' if isinstance(error, bridge().Hold) else 'G8_ARCHIVE_HOLD: unavailable or invalid original evidence\n')


if __name__ == '__main__':
    main()
