"""Synthetic custody tests only; no authentic E/G6/G8 credential is generated."""
import base64
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

import test_sudu_g8_release_bridge as fixtures
from scripts import sudu_g8_archive as a
from scripts import sudu_g8_release_bridge as b
from scripts import sudu_independent_review_gate as gate
from scripts import sudu_verified_publish as p


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BridgeTests('runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        f.stage_it()
        self.manifest, _, self.report, self.entry = f.make_report()
        now = datetime.now(timezone.utc)
        self.records = {
            'run': {'id': 123, 'path': b.FORMAL_WORKFLOW, 'event': 'workflow_dispatch', 'head_branch': 'main',
                    'head_sha': self.entry['codeCommit'], 'status': 'completed', 'conclusion': 'success'},
            'job': {'id': 456, 'name': 'formal_g8', 'run_id': 123, 'head_sha': self.entry['codeCommit'], 'conclusion': 'success'},
            'artifact': {'id': 789, 'expired': False, 'digest': 'sha256:' + self.entry['artifactSha256'],
                         'workflow_run': {'id': 123}, 'created_at': '2020-01-01T00:00:03Z',
                         'expires_at': (now + timedelta(days=1)).isoformat()}}
        self.dest = f.root / 'sudu-g8-capture'

    def capture(self):
        with patch.object(b, 'github', side_effect=[self.records[k] for k in ('run', 'job', 'artifact')]):
            return a.capture(self.entry, self.fixture.qid, self.fixture.report / 'artifact.zip', self.dest)

    def owner(self):
        self.capture()
        self.owner_entry = json.loads((self.dest / 'G8_OWNER_REVIEW_CANDIDATE.json').read_bytes())
        self.spec = self.owner_entry['durableArchive']
        self.captured = self.dest / self.spec['capturePath']
        self.original = self.dest / self.spec['archivePath']
        return self.owner_entry

    def validate_owner(self):
        owner_policy = {'trustedG8Receipts': {self.fixture.qid: self.owner_entry}}
        def blob(head, rel, expected):
            raw = (self.dest / rel).read_bytes()
            b.require(gate.blob_oid(raw) == expected, 'SYNTHETIC pinned blob changed')
            return raw
        with patch.object(a, 'current_policy', return_value=('a' * 40, owner_policy)), \
             patch.object(a, 'blob_at', side_effect=blob), \
             patch.object(b, 'github', side_effect=lambda url: copy.deepcopy(self.records['run' if '/runs/' in url else 'job']) if '/artifacts/' not in url else (_ for _ in ()).throw(AssertionError('expired artifact must not be queried'))):
            return a.verify_owned(self.owner_entry)

    def test_capture_is_only_candidate_and_never_grants_trust(self):
        result = self.capture()
        self.assertFalse(result['trusted'])
        self.assertFalse(result['deployed'])
        self.assertEqual(result['status'], 'CAPTURED_PENDING_INDEPENDENT_OWNER_REVIEW')
        self.assertNotIn('durableArchive', self.fixture.policy['trustedG8Receipts'][self.fixture.qid])
        candidate = json.loads((self.dest / 'G8_OWNER_REVIEW_CANDIDATE.json').read_bytes())
        self.assertTrue((self.dest / candidate['durableArchive']['archivePath']).is_file())
        self.assertEqual(len(list(self.dest.rglob('*.*'))), 3)

    def test_capture_rejects_expired_failed_wrong_run_and_bad_archive(self):
        for kind, key, value in [('artifact', 'expired', True), ('run', 'conclusion', 'failure'),
                                 ('job', 'id', 999), ('artifact', 'digest', 'sha256:' + '0' * 64),
                                 ('artifact', 'expires_at', '2020-01-02T00:00:00Z')]:
            old = self.records[kind][key]
            self.records[kind][key] = value
            with self.subTest(kind=kind, key=key):
                with self.assertRaises(b.Hold):
                    self.capture()
                self.assertFalse(self.dest.exists())
            self.records[kind][key] = old
        (self.fixture.report / 'artifact.zip').write_bytes(b'changed')
        with self.assertRaises(b.Hold):
            self.capture()

    def test_owner_pinned_original_remains_verifiable_after_actions_expiry(self):
        self.owner()
        proof = json.loads(self.captured.read_bytes())
        proof['capturedAt'] = '2020-01-02T00:00:00Z'
        proof['actionsAtCapture']['artifact']['expires_at'] = '2020-01-03T00:00:00Z'
        self.captured.write_bytes(b.serialized(proof))
        self.spec['captureGitBlobSha'] = gate.blob_oid(self.captured.read_bytes())
        result = self.validate_owner()
        self.assertEqual(result['archiveSha256'], self.entry['artifactSha256'])
        self.assertEqual(result['runId'], 123)
        self.records['run']['head_sha'] = 'f' * 40
        with self.assertRaisesRegex(b.Hold, 'actual original run'):
            self.validate_owner()

    def test_durable_original_drives_real_native_promotion_without_expired_actions(self):
        self.owner()
        proof = json.loads(self.captured.read_bytes())
        proof['capturedAt'] = '2020-01-02T00:00:00Z'
        proof['actionsAtCapture']['artifact']['expires_at'] = '2020-01-03T00:00:00Z'
        self.captured.write_bytes(b.serialized(proof))
        self.spec['captureGitBlobSha'] = gate.blob_oid(self.captured.read_bytes())
        f = self.fixture
        f.policy['trustedG8Receipts'][f.qid] = self.owner_entry
        def blob(head, rel, expected):
            raw = (self.dest / rel).read_bytes()
            b.require(gate.blob_oid(raw) == expected, 'SYNTHETIC pinned blob changed')
            return raw
        with patch.object(a, 'current_policy', return_value=('a' * 40, f.policy)), \
             patch.object(a, 'blob_at', side_effect=blob), \
             patch.object(b, 'github', side_effect=lambda url: copy.deepcopy(self.records['run' if '/runs/' in url else 'job']) if '/artifacts/' not in url else (_ for _ in ()).throw(AssertionError('expired artifact must not be queried'))):
            out = f.root / 'sudu-g8-durable-promotion'
            result = b.promote(f.source, f.stage, f.private, f.report, out)
        self.assertEqual(result['status'], 'PROMOTION_CANDIDATE_NOT_DEPLOYED')
        self.assertEqual((out / 'sudu/data/approved/115.json').read_bytes(),
                         (f.stage / 'site/sudu/data/approved/115.json').read_bytes())
        self.assertFalse((f.source / 'sudu/data/approved').exists())

    def test_owner_absence_revocation_or_changed_receipt_is_rejected(self):
        self.owner()
        for entries in [{}, {self.fixture.qid: {**self.owner_entry, 'reportSha256': '0' * 64}}]:
            with patch.object(a, 'current_policy', return_value=('a' * 40, {'trustedG8Receipts': entries})):
                with self.assertRaisesRegex(b.Hold, 'current protected owner registry'):
                    a.verify_owned(self.owner_entry)

    def test_changed_capture_or_zip_and_capture_after_expiry_rejected(self):
        self.owner()
        for file in (self.captured, self.original):
            raw = file.read_bytes()
            file.write_bytes(raw + b'changed')
            with self.assertRaises(b.Hold):
                self.validate_owner()
            file.write_bytes(raw)
        proof = json.loads(self.captured.read_bytes())
        proof['capturedAt'] = '2020-01-04T00:00:00Z'
        proof['actionsAtCapture']['artifact']['expires_at'] = '2020-01-03T00:00:00Z'
        self.captured.write_bytes(b.serialized(proof))
        self.spec['captureGitBlobSha'] = gate.blob_oid(self.captured.read_bytes())
        with self.assertRaisesRegex(b.Hold, 'chronology'):
            self.validate_owner()

    def test_wrong_snapshot_code_or_extra_zip_rejected_even_with_matching_hash(self):
        self.records['run']['head_sha'] = 'f' * 40
        with self.assertRaises(b.Hold):
            self.capture()
        self.records['run']['head_sha'] = self.entry['codeCommit']
        with zipfile.ZipFile(self.fixture.report / 'artifact.zip', 'a') as z:
            z.writestr('unexpected-private.txt', b'SYNTHETIC not allowed')
        self.entry['artifactSha256'] = gate.digest((self.fixture.report / 'artifact.zip').read_bytes())
        self.records['artifact']['digest'] = 'sha256:' + self.entry['artifactSha256']
        with self.assertRaises(b.Hold):
            self.capture()

    def test_tree_proof_cannot_use_unprotected_or_missing_symlink_blob(self):
        with patch.object(a, 'get_json', return_value={'name': 'main', 'protected': False}):
            with self.assertRaises(b.Hold):
                a.protected_head()
        a.immutable_tree.cache_clear()
        with patch.object(a, 'get_json', return_value={'tree': []}):
            with self.assertRaises(b.Hold):
                a.blob_at('a' * 40, a.PREFIX + 'original.zip', 'b' * 40)
        a.immutable_tree.cache_clear()
        with patch.object(a, 'get_json', return_value={'tree': [{'path': 'sudu', 'type': 'blob', 'mode': '120000', 'sha': 'b' * 40}]}):
            with self.assertRaises(b.Hold):
                a.blob_at('a' * 40, a.PREFIX + 'original.zip', 'b' * 40)
        a.immutable_tree.cache_clear()

    def test_pinned_code_can_read_current_policy_and_explicit_forged_policy_fails(self):
        remote = {**self.fixture.policy, 'trustedG8Receipts': {'SYNTHETIC_LATER_APPROVAL': {}}}
        with patch.object(a, 'current_policy', return_value=('c' * 40, remote)), \
             patch.object(gate, '_ai_registry_exactly_matches_protected_main_policy', return_value=True):
            # Bypass ONLY the fixture's mocked b.trusted_policy for this production function test.
            from importlib import util
            spec = util.spec_from_file_location('synthetic_policy_function', b.ROOT / 'scripts/sudu_g8_release_bridge.py')
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(module.trusted_policy(), remote)
        with patch.object(gate, '_ai_registry_exactly_matches_protected_main_policy', return_value=False):
            with self.assertRaisesRegex(ValueError, 'explicit publisher policy'):
                p.stage(self.fixture.source, self.fixture.root / 'never-created', 'a' * 40, review_policy=remote)
        self.assertFalse((self.fixture.root / 'never-created').exists())


if __name__ == '__main__':
    unittest.main()
