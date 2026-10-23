"""Synthetic-only regressions for the read-only G0-G6 audit.

No real question record, student database, or QA PASS flag is modified.
"""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import importlib.util

SPEC = importlib.util.spec_from_file_location('gates', Path(__file__).with_name('audit_105_115_release_gates.py'))
gates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gates)


class ReleaseGateRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        gates.D = Path(self.temp.name)
        self.base = gates.D / '114'
        self.base.mkdir()
        self.qid = '114-00-C-01'
        self.sha = 'a' * 64
        self.source_sha = 'b' * 64
        self.answer_sha = 'c' * 64
        self.data = {
            'inventory.json': {'integrationReady': True, 'sqlite': {'reimportCount': 2, 'shaMismatches': 0}},
            'questions.json': {'questions': [{
                'questionId': self.qid, 'year': 114, 'paperCode': '00-C',
                'originalQuestionNumber': 1, 'answer': 'A', 'answerVerified': True,
                'questionVerified': True, 'integrationReady': True,
                'assets': {'sha256': self.sha}, 'questionProvenance': {'webpSha256': self.sha}
            }]},
            'webp-manifest.json': {'items': [{
                'questionId': self.qid, 'paperCode': '00-C', 'originalQuestionNumber': 1,
                'qaStatus': 'PASS', 'sha256': self.sha,
                'sourceSha256': self.source_sha, 'sourcePage': 2,
                'crop': [0, 0, 10, 10], 'output': 'fixtures/q.webp',
                'visualReviewEvidence': {'reviewedSha256': self.sha, 'reference': 'proof/visual.json'}
            }], 'sharedMaterialCrops': []},
            'VISUAL_QA.json': {'questions': [{
                'questionId': self.qid, 'status': 'PASS',
                'webpSha256': self.sha, 'evidenceReference': 'proof/visual.json'
            }]},
            'official-answer-evidence.json': {'items': [{
                'questionId': self.qid, 'answerVerified': True,
                'officialFinalAnswer': 'A', 'officialCorrectionChecked': True,
                'officialSourceSha256': self.answer_sha,
                'officialCorrectionPdfSha256': self.source_sha,
                'qaEvidencePath': 'proof/answer.json'
            }]},
            'VALIDATION.json': {'integrationReady': True},
            'release-manifest.json': {'integrationReady': True, 'releaseAllowed': True},
            'ocr-raw-candidates.json': {}
        }
        self.write_files()

    def write_files(self):
        for name, value in self.data.items():
            (self.base / name).write_text(json.dumps(value), encoding='utf-8')
        (self.base / 'REMAINING_QA.md').write_text('All resolved', encoding='utf-8')
        (self.base / 'DATA_HANDOFF.md').write_text('All resolved', encoding='utf-8')
        with sqlite3.connect(self.base / 'question-bank.sqlite3') as con:
            con.execute('CREATE TABLE IF NOT EXISTS questions (questionId TEXT PRIMARY KEY)')
            con.execute('INSERT OR IGNORE INTO questions VALUES (?)', (self.qid,))

    def check(self, expected):
        self.write_files()
        record = gates.audit(114)
        self.assertFalse(record['integrationReady'], record)
        self.assertTrue(any(x.startswith(expected) for x in record['blockers']), record)

    def test_happy_path(self):
        got = gates.audit(114)
        self.assertTrue(got['integrationReady'], got)
        self.assertEqual(got['webpVisualPass'], 1)

    def test_false_release_flag_blocks(self):
        self.data['release-manifest.json']['releaseAllowed'] = False
        self.check('release_not_allowed')

    def test_boolean_reimports_not_accepted(self):
        self.data['inventory.json']['sqlite']['reimportCount'] = True
        self.check('sqlite_idempotent_reimport_not_evidenced')

    def test_boolean_sha_mismatch_not_accepted(self):
        self.data['inventory.json']['sqlite']['shaMismatches'] = False
        self.check('sqlite_sha_mismatch_or_unverified')

    def test_corrupt_json_is_blocked_not_crash(self):
        (self.base / 'inventory.json').write_text('not-json', encoding='utf-8')
        self.assertIn('invalid_json:inventory.json', gates.audit(114)['blockers'])

    def test_visual_ledger_mismatched_hash_blocks(self):
        self.data['VISUAL_QA.json']['questions'][0]['webpSha256'] = 'f' * 64
        self.check('visual_qa_evidence_mismatch:')

    def test_manifest_mismatched_hash_blocks(self):
        self.data['webp-manifest.json']['items'][0]['visualReviewEvidence']['reviewedSha256'] = 'f' * 64
        self.check('visual_qa_evidence_mismatch:')

    def test_question_asset_sha_mismatch_blocks(self):
        self.data['questions.json']['questions'][0]['assets']['sha256'] = 'd' * 64
        self.check('question_asset_sha_mismatch:')

    def test_answer_ledger_false_blocks(self):
        self.data['official-answer-evidence.json']['items'][0]['answerVerified'] = False
        self.check('official_answer_evidence_mismatch:')

    def test_correction_evidence_missing_blocks(self):
        self.data['official-answer-evidence.json']['items'][0].pop('officialCorrectionPdfSha256')
        self.check('official_answer_evidence_mismatch:')

    def test_answer_value_mismatch_blocks(self):
        self.data['official-answer-evidence.json']['items'][0]['officialFinalAnswer'] = 'B'
        self.check('official_answer_evidence_mismatch:')

    def test_shared_pass_without_hash_evidence_blocks(self):
        self.data['webp-manifest.json']['sharedMaterialCrops'] = [
            {'sharedMaterialId': 'SH1', 'qaStatus': 'PASS', 'sha256': self.sha}
        ]
        self.check('shared_material_evidence_missing:')

    def test_wrong_year_identity_blocks(self):
        self.data['questions.json']['questions'][0]['year'] = 115
        self.check('missing_or_wrong_canonical_question_identity')

    def test_duplicate_ledger_id_blocks(self):
        self.data['official-answer-evidence.json']['items'].append(self.data['official-answer-evidence.json']['items'][0].copy())
        self.check('duplicate_or_invalid_official_answer_ledger')

    def test_source_sha_evidence_mismatch_blocks(self):
        self.data['webp-manifest.json']['items'][0]['visualReviewEvidence']['sourceSha256'] = 'f' * 64
        self.check('visual_qa_evidence_mismatch:')

    def test_question_source_sha_mismatch_blocks(self):
        self.data['questions.json']['questions'][0]['questionProvenance']['pixelSourceSha256'] = 'f' * 64
        self.check('question_source_sha_mismatch:')

    def test_question_official_pdf_sha_mismatch_blocks(self):
        self.data['questions.json']['questions'][0]['questionProvenance']['officialPdfSha256'] = 'f' * 64
        self.data['webp-manifest.json']['items'][0]['sourcePdfSha256'] = 'e' * 64
        self.check('question_official_pdf_sha_mismatch:')

    def test_answer_source_sha_mismatch_blocks(self):
        self.data['questions.json']['questions'][0]['answerProvenance'] = {'officialPdfSha256': 'f' * 64}
        self.check('official_answer_source_sha_mismatch:')

    def test_missing_sqlite_blocks(self):
        (self.base / 'question-bank.sqlite3').unlink()
        record = gates.audit(114)
        self.assertFalse(record['integrationReady'])
        self.assertIn('missing:question-bank.sqlite3', record['blockers'])

    def test_legacy_visual_items_schema_accepted(self):
        self.data['VISUAL_QA.json'] = {'items': [{
            'questionId': self.qid, 'status': 'PASS', 'candidateSha256': self.sha,
            'visualEvidence': 'proof/visual.json'}]}
        self.write_files()
        self.assertTrue(gates.audit(114)['integrationReady'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
