"""Independent E: a rename into approved/ must not hide an outside deletion."""
import argparse
import importlib.util
from pathlib import Path
import subprocess

def check(root):
    spec=importlib.util.spec_from_file_location('e_pr102_rename_fixture',root/'tests/test_sudu_sync_candidate.py')
    fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    x=fixture.CandidateTests('test_real_git_candidate_and_idempotent_pr_never_move_main');x.setUp()
    try:
        x.git('reset','HEAD','--','sudu/data/approved/115.json')
        (x.repo/'outside.py').write_text('original source code outside allowed area')
        x.git('add','outside.py');x.git('commit','-m','outside baseline')
        x.base=x.git('rev-parse','HEAD');x.git('push','origin','main')
        x.git('add','sudu/data/approved/115.json')
        x.git('mv','outside.py','sudu/data/approved/renamed.py')
        raw=subprocess.check_output(['git','diff','--cached','--no-renames','--name-only','-z'],cwd=x.repo)
        assert b'outside.py' in raw.split(b'\0'),repr(raw)
        rejected=False
        try:x.execute()
        except ValueError as exc:
            assert 'Only approved' in str(exc),str(exc)
            rejected=True
        assert rejected,'P1: outside source deletion hidden by Git rename detection created candidate'
        assert b'sync/qa-approved-' not in subprocess.check_output(['git','ls-remote','origin','refs/heads/*'],cwd=x.repo)
        print('PASS: cross-boundary rename rejected before candidate push')
    finally:x.doCleanups()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    check(parser.parse_args().root.resolve())
