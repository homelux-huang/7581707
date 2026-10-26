import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/'.github/workflows/tcte-full-import.yml'

class ProtectedMainImportWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=WORKFLOW.read_text(encoding='utf-8')

    def test_never_pushes_or_deploys_directly_to_main(self):
        self.assertNotIn('git push origin HEAD:main',self.text)
        self.assertNotIn('gh workflow run pages.yml',self.text)
        self.assertNotIn('gh workflow run tcte-data-audit.yml',self.text)

    def test_candidate_is_lease_safe_and_reviewable(self):
        self.assertIn('pull-requests: read',self.text)
        self.assertIn('automation/tcte-original-image-candidate',self.text)
        self.assertIn('--force-with-lease=',self.text)
        self.assertNotIn('gh pr create',self.text)
        self.assertIn('gh pr list',self.text)
        self.assertIn('GitHub Actions PR creation is intentionally disabled',self.text)
        self.assertIn('--base main',self.text)

    def test_original_no_ocr_and_audit_gates_remain(self):
        for token in (
            "assert 'pytesseract' not in source",
            'scripts/tcte_source_images.py --years',
            'scripts/tcte_manifest.py',
            'check_tcte_corpus.py --decode-images',
            'actions/upload-artifact@v4',
        ):
            self.assertIn(token,self.text)

if __name__=='__main__':
    unittest.main()

