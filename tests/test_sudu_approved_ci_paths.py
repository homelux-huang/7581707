"""Trigger contract for actual PR103 data paths; no workflow execution implied."""
from fnmatch import fnmatchcase
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
FILES=['sudu-browser-test.yml','sudu-verified-integration-checks.yml']
PR103=['sudu/data/approved/114.json','sudu/data/approved/115.json',
       'sudu/data/approved/preview/114.json','sudu/data/approved/preview/115.json',
       'sudu/data/approved/progress.json']

def event_text(name,event):
    text=(ROOT/'.github/workflows'/name).read_text()
    match=re.search(r'^  '+event+r':\n(.*?)(?=^  [a-z_]+:|^permissions:)',text,re.M|re.S)
    if not match:raise AssertionError('Missing event '+event)
    return match.group(1)

def filters(text,key):
    inline=re.search(r'^    '+key+r': \[(.*?)\]$',text,re.M)
    if inline:return [v.strip().strip("'\"") for v in inline.group(1).split(',')]
    block=re.search(r'^    '+key+r':\n((?:      - .*\n)+)',text,re.M)
    return [v.strip().strip("'\"") for v in re.findall(r'^      - (.*)$',block.group(1),re.M)] if block else []

def triggered(name,event,branch,paths):
    text=event_text(name,event)
    branches=filters(text,'branches');allowed=filters(text,'paths')
    return ((not branches or any(fnmatchcase(branch,p) for p in branches))
            and (not allowed or any(fnmatchcase(f,p) for f in paths for p in allowed)))

class ApprovedCiPaths(unittest.TestCase):
    def test_every_actual_pr103_json_triggers_both_main_pr_checks(self):
        for name in FILES:
            self.assertIn('sudu/data/approved/**',filters(event_text(name,'pull_request'),'paths'))
            for path in PR103:
                with self.subTest(name=name,path=path):
                    self.assertTrue(triggered(name,'pull_request','main',[path]))

    def test_nested_webp_and_future_approved_years_are_covered(self):
        for name in FILES:
            self.assertTrue(triggered(name,'pull_request','main',['sudu/data/approved/webp/114/114-00-E-11.webp']))
            self.assertTrue(triggered(name,'pull_request','main',['sudu/data/approved/113.json']))

    def test_main_pr_scope_not_broadened_to_other_targets_or_docs(self):
        for name in FILES:
            self.assertFalse(triggered(name,'pull_request','unrelated',PR103))
            self.assertFalse(triggered(name,'pull_request','main',['docs/notes.md']))

    def test_actual_sync_candidate_push_triggers_both_without_main_push(self):
        branch='sync/qa-approved-'+'a'*40+'-'+'b'*40
        for name in FILES:
            self.assertTrue(triggered(name,'push',branch,PR103))

    def test_integration_push_branch_allowlist_remains_explicit(self):
        name='sudu-verified-integration-checks.yml'
        self.assertFalse(triggered(name,'push','unrelated',PR103))
        self.assertFalse(triggered(name,'push','sync/not-approved-abc',PR103))
        self.assertTrue(triggered(name,'push','integration/114-115-auto-verified-pages',PR103))

    def test_existing_ui_code_and_manual_dispatch_remain(self):
        for name in FILES:
            for path in ['sudu/v4-115-multisubject-review-demo.html','scripts/sudu_verified_publish.py']:
                self.assertTrue(triggered(name,'pull_request','main',[path]))
            text=(ROOT/'.github/workflows'/name).read_text()
            self.assertIn('  workflow_dispatch:',text)
            self.assertIn('  contents: read',text)
            self.assertNotIn('contents: write',text)

if __name__=='__main__':unittest.main()
