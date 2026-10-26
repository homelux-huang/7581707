"""Independent E path-integrity regression. Real Git, existing explicit gh fixture.
Exit nonzero if whitespace trimming lets outside staged paths enter candidate PR.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

def check(root):
    spec=importlib.util.spec_from_file_location('e_pr102_fixture',root/'tests/test_sudu_sync_candidate.py')
    fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    for prefix in [' ', '\n', '\t']:
        x=fixture.CandidateTests('test_real_git_candidate_and_idempotent_pr_never_move_main')
        x.setUp()
        try:
            name=prefix+'sudu/data/approved/escape.py'
            p=x.repo/name;p.parent.mkdir(parents=True);p.write_text('OUTSIDE_ALLOWED_PREFIX')
            x.git('add','--',name)
            raw=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=x.repo)
            assert name.encode() in raw.split(b'\0'),repr(raw)
            rejected=False
            try:x.execute()
            except ValueError as exc:
                assert 'Only approved' in str(exc),str(exc)
                rejected=True
            if not rejected:
                receipt=json.loads((x.root/'artifact/receipt.json').read_text())
                actual=subprocess.check_output(['git','diff','--name-only','-z',x.base,receipt['candidateSha']],cwd=x.repo)
                print('P1_PATH_SCOPE_BYPASS',json.dumps({'rawIndex':repr(raw),'receiptPaths':receipt['paths'],'rawCandidatePaths':repr(actual)}))
                raise AssertionError('outside-prefix staged file created a candidate PR')
            remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/*'],cwd=x.repo)
            assert b'sync/qa-approved-' not in remote
            assert x.git('rev-parse','HEAD')==x.base
            print('PASS: rejected original filename prefix',repr(prefix))
        finally:x.doCleanups()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    check(parser.parse_args().root.resolve())
