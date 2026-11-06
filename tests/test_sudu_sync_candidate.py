"""Real local Git transport; gh is an explicit isolated API fixture, not CI proof."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/sudu_sync_candidate.py'
spec=importlib.util.spec_from_file_location('sync_candidate',SCRIPT)
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);self.root=root
        self.repo=root/'repo';self.repo.mkdir()
        self.git('init','--bare',str(root/'remote.git'),cwd=root)
        self.git('init','-b','main',cwd=self.repo)
        self.git('config','user.name','test');self.git('config','user.email','test@example.invalid')
        p=self.repo/'sudu/data/approved/115.json';p.parent.mkdir(parents=True);p.write_text('old')
        self.git('add','.');self.git('commit','-m','base')
        self.base=self.git('rev-parse','HEAD')
        self.git('remote','add','origin',str(root/'remote.git'));self.git('push','origin','main')
        p.write_text('candidate');self.git('add','sudu/data/approved')
        bindir=root/'bin';bindir.mkdir()
        gh=bindir/'gh'
        gh.write_text('''#!/usr/bin/env python3
import json,os,subprocess,sys
from pathlib import Path
state=Path(os.environ['GH_FIXTURE_STATE'])
args=sys.argv[1:]
if os.environ.get('GH_FIXTURE_FAIL'): sys.exit(1)
if args[args.index('-X')+1]=='GET':
 print('['+state.read_text()+']' if state.exists() else '[]')
else:
 branch=next(x[5:] for x in args if x.startswith('head='))
 sha=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+branch],text=True).split()[0]
 data={'head':{'sha':sha},'base':{'ref':'main'},'draft':True,'html_url':'https://example.invalid/fixture-pr'}
 state.write_text(json.dumps(data));print(json.dumps(data))
''');gh.chmod(0o755)
        self.env={'PATH':str(bindir)+os.pathsep+os.environ['PATH'],'GH_FIXTURE_STATE':str(root/'pr.json')}

    def git(self,*args,cwd=None):
        return subprocess.check_output(['git',*args],cwd=cwd or self.repo,text=True,stderr=subprocess.DEVNULL).strip()

    def execute(self,fail=False,pr_mode='api'):
        old=Path.cwd()
        try:
            os.chdir(self.repo)
            with patch.dict(os.environ,{**self.env,**({'GH_FIXTURE_FAIL':'yes'} if fail else {})}):
                sync.publish(self.root/'artifact',pr_mode=pr_mode)
        finally:os.chdir(old)

    def test_real_git_candidate_and_idempotent_pr_never_move_main(self):
        self.execute();one=json.loads((self.root/'artifact/receipt.json').read_text())
        self.execute();two=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(one,two)
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.base)
        self.assertEqual(self.git('rev-parse','HEAD'),self.base)
        self.assertEqual(self.git('show','-s','--format=%P',one['candidateSha']),self.base)
        self.assertFalse(one['ready']);self.assertFalse(one['deployed']);self.assertTrue(one['ciRequired'])
        self.assertFalse(one['botPrTriggersCi'])

    def test_manual_pr_handoff_no_post_and_repeated_identical_candidate(self):
        self.execute(pr_mode='manual')
        a=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(a['status'],'MANUAL_PR_HANDOFF_REQUIRED')
        self.assertTrue(a['needsAuthorizedPrCreation'])
        self.assertFalse(a['ready'])
        self.assertFalse(a['deployed'])
        self.assertTrue(a['ciRequired'])
        self.assertIn('pull/new/sync/qa-approved-',a['handoffUrl'])
        self.assertFalse((self.root/'pr.json').exists())
        self.assertTrue((self.root/'artifact/candidate.patch').read_bytes())
        self.execute(pr_mode='manual')
        b=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(a,b)
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.base)
        self.assertEqual(self.git('rev-parse','HEAD'),self.base)

    def test_manual_mode_recognizes_authorized_existing_exact_draft_pr(self):
        self.execute(pr_mode='manual')
        a=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(a['status'],'MANUAL_PR_HANDOFF_REQUIRED')
        # External authorized connector creates exact SHA-pinned PR.
        # The script then GETs it; manual mode never does POST.
        fixture={'head':{'sha':a['candidateSha']},'base':{'ref':'main'},
                 'draft':True,'html_url':'https://example.invalid/existing-pr'}
        (self.root/'pr.json').write_text(json.dumps(fixture))
        self.execute(pr_mode='manual')
        b=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(b['status'],'DRAFT_PR_PENDING_INDEPENDENT_REVIEW_AND_CI')
        self.assertEqual(b['prUrl'],'https://example.invalid/existing-pr')
        self.assertFalse(b['ready'])
        self.assertFalse(b['deployed'])
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.base)

    def test_manual_mode_rejects_mismatched_existing_pr(self):
        self.execute(pr_mode='manual')
        fixture={'head':{'sha':'a'*40},'base':{'ref':'main'},
                 'draft':True,'html_url':'https://example.invalid/wrong-pr'}
        (self.root/'pr.json').write_text(json.dumps(fixture))
        with self.assertRaisesRegex(ValueError,'Existing PR revision mismatch'):
            self.execute(pr_mode='manual')
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.base)

    def test_permission_failure_keeps_patch_and_blocks_no_main_change(self):
        with self.assertRaises(subprocess.CalledProcessError):self.execute(fail=True)
        r=json.loads((self.root/'artifact/receipt.json').read_text())
        self.assertEqual(r['status'],'BRANCH_PENDING_DRAFT_PR')
        self.assertTrue((self.root/'artifact/candidate.patch').read_bytes())
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.base)

    def test_stale_base_fails_before_any_candidate_push(self):
        self.git('commit','--allow-empty','-m','advance')
        self.git('push','origin','main')
        self.git('reset','--soft',self.base)
        with self.assertRaisesRegex(ValueError,'STALE_BASE'):self.execute()
        self.assertNotIn('sync/qa-approved-',self.git('ls-remote','origin','refs/heads/*'))

    def test_unrelated_staged_file_is_rejected(self):
        (self.repo/'scripts.py').write_text('not data');self.git('add','scripts.py')
        with self.assertRaisesRegex(ValueError,'Only approved'):self.execute()
        self.assertNotIn('sync/qa-approved-',self.git('ls-remote','origin','refs/heads/*'))

    def test_symlink_output_rejected(self):
        (self.repo/'sudu/data/approved/link').symlink_to('/tmp/elsewhere')
        self.git('add','sudu/data/approved/link')
        with self.assertRaisesRegex(ValueError,'Symlink'):self.execute()

    def test_real_leading_space_outside_path_is_not_normalized(self):
        path=self.repo/' sudu/data/approved/escape.py'
        path.parent.mkdir(parents=True);path.write_text('outside')
        self.git('add','.')
        raw=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=self.repo)
        self.assertIn(b' sudu/data/approved/escape.py\0',raw)
        with self.assertRaisesRegex(ValueError,'Only approved'):self.execute()
        self.assertNotIn('sync/qa-approved-',self.git('ls-remote','origin','refs/heads/*'))

    def test_control_character_path_is_rejected_before_push(self):
        path=self.repo/'sudu/data/approved/escape\n.py'
        path.write_text('control')
        self.git('add','.')
        with self.assertRaisesRegex(ValueError,'Only approved'):self.execute()
        self.assertNotIn('sync/qa-approved-',self.git('ls-remote','origin','refs/heads/*'))

    def test_rename_from_outside_prefix_cannot_hide_source_deletion(self):
        self.git('reset','--hard',self.base)
        (self.repo/'outside.py').write_text('outside source')
        self.git('add','outside.py');self.git('commit','-m','existing outside file')
        self.base=self.git('rev-parse','HEAD');self.git('push','origin','main')
        self.git('mv','outside.py','sudu/data/approved/inside.py')
        with self.assertRaisesRegex(ValueError,'Only approved'):self.execute()
        self.assertNotIn('sync/qa-approved-',self.git('ls-remote','origin','refs/heads/*'))

    def test_invalid_oids_and_path_traversal_rejected(self):
        with self.assertRaises(ValueError):sync.branch_name('main','a'*40)
        with self.assertRaises(ValueError):sync.validate_paths(['sudu/data/approved/../else'])

    def test_workflow_manual_pr_handoff_is_executable_shell_line(self):
        # Regression for a literal backslash-n embedded in a YAML run comment.
        # The workflow can pass 'updated=false' CI while this path stays broken.
        workflow=(SCRIPT.parent.parent/'.github/workflows/sudu-verified-autopublish.yml').read_text()
        step=workflow.split('      - name: Pin candidate and emit authorized Draft PR handoff (NO RELEASE)',1)[1]
        step=step.split('      - name: Retain pinned candidate even if token cannot create a PR',1)[0]
        shell_lines=step.splitlines()
        invoke='python scripts/sudu_sync_candidate.py --artifact-dir _sync_candidate --pr-mode manual'
        matches=[line for line in shell_lines if line.strip()==invoke]
        self.assertEqual(len(matches),1,'Manual Draft PR handoff must be a distinct executable shell line')
        self.assertNotIn('\\\\n',step,'YAML run block may not hide invocation inside a literal escaped newline')
        self.assertIn('          git add -A sudu/data/approved',shell_lines)
        self.assertTrue(any(line.strip().startswith('# The repository forbids') for line in shell_lines))

if __name__=='__main__':unittest.main()
