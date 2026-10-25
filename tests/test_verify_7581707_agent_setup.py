from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT / '.github/workflows/7581707-role-agent.md'
DOC=ROOT / 'docs/7581707-ADMIN-AUTONOMOUS-AGENT-SETUP.md'

class GhAwBootstrapTest(unittest.TestCase):
    def test_source_has_codex_and_read_only_permissions(self):
        text=SRC.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        fm=text.split('---',2)[1]
        self.assertIn('engine: codex',fm)
        self.assertIn('contents: read',fm)
        self.assertIn('issues: read',fm)
        self.assertIn('pull-requests: read',fm)
        self.assertNotIn('contents: write',fm)
        self.assertNotIn('issues: write',fm)
        self.assertIn('safe-outputs:',fm)
        self.assertIn('create-issue: false',fm)
        self.assertIn('report-failure-as-issue: false',fm)
        self.assertIn('report-failed-jobs: false',fm)
        for forbidden in ('create-pull-request:', 'add-comment:', 'create-issue: true'):
            self.assertNotIn(forbidden,fm)
    def test_not_misrepresented_as_running(self):
        source=SRC.read_text(encoding='utf-8')
        doc=DOC.read_text(encoding='utf-8')
        self.assertIn('gh aw compile',doc)
        self.assertIn('CODEX_API_KEY',doc)
        self.assertIn('protected=true',doc)
        self.assertIn('not executable Actions YAML',doc)
        self.assertIn('read-only',source)
        self.assertIn('never',source.lower())
    def test_no_raw_secrets_or_main_release_directives(self):
        source=SRC.read_text(encoding='utf-8')
        self.assertNotIn('sk-proj-',source)
        self.assertNotIn('gh pr merge ',source)
        self.assertNotIn('git push origin main',source)
        self.assertIn('104',source)
        self.assertIn('115',source)

if __name__=='__main__':
    unittest.main()
