"""Turn staged approved output into an unmerged, unapproved Draft PR.

Never pushes main, forces a ref, merges, or deploys. A bot-created PR does not
trigger ordinary PR workflows; MASTER must independently trigger/read real CI.
Artifacts survive permission/API failures. Such failures remain nonzero.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPO = 'homelux-huang/7581707'
PREFIX = 'sudu/data/approved/'

def run(*args, input=None):
    return subprocess.check_output(args, input=input, text=True).strip()

def validate_paths(paths):
    if not paths or any(not p.startswith(PREFIX) or '..' in p.split('/') or any(ord(c)<32 or ord(c)==127 for c in p) for p in paths):
        raise ValueError('Only approved data changes may enter a sync candidate')

def branch_name(base, tree):
    if not all(re.fullmatch('[0-9a-f]{40}', v) for v in (base, tree)):
        raise ValueError('Exact Git OIDs required')
    return 'sync/qa-approved-' + base + '-' + tree

def publish(artifact):
    artifact.mkdir(parents=True, exist_ok=True)
    base = run('git', 'rev-parse', 'HEAD')
    paths = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], text=True).rstrip('\0').split('\0')
    if paths == ['']:
        print('NO_CHANGE: no new approved output')
        return
    validate_paths(paths)
    # Refuse symlink outputs, including a newly staged symlink replacing JSON.
    for entry in run('git', 'ls-files', '--stage', '-z', '--', *paths).split('\0'):
        if entry and entry.startswith('120000 '):
            raise ValueError('Symlink output forbidden')
    tree = run('git', 'write-tree')
    branch = branch_name(base, tree)
    patch = subprocess.check_output(['git', 'diff', '--cached', '--binary'])
    (artifact / 'candidate.patch').write_bytes(patch)
    receipt = {'schemaVersion': 1, 'repository': REPO, 'baseSha': base,
               'treeSha': tree, 'branch': branch, 'paths': paths,
               'patchSha256': hashlib.sha256(patch).hexdigest(),
               'status': 'NOT_PUBLISHED', 'ready': False, 'deployed': False,
               'ciRequired': True, 'botPrTriggersCi': False}
    def save():
        (artifact / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    save()
    # Reject stale base; no rebase can silently change reviewed output.
    run('git', 'fetch', '--no-tags', 'origin', 'main')
    if run('git', 'rev-parse', 'FETCH_HEAD') != base:
        raise ValueError('STALE_BASE: regenerate against latest main')
    existing = run('git', 'ls-remote', '--heads', 'origin', 'refs/heads/'+branch)
    if existing:
        commit = existing.split()[0]
        run('git', 'fetch', '--no-tags', 'origin', 'refs/heads/'+branch)
        if (run('git', 'rev-parse', commit+'^{tree}') != tree
                or run('git', 'show', '-s', '--format=%P', commit) != base):
            raise ValueError('Existing candidate differs: do not overwrite')
    else:
        commit = run('git', '-c', 'user.name=github-actions[bot]', '-c',
                     'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                     'commit-tree', tree, '-p', base,
                     input='Stage QA-approved data for independent review\n')
        run('git', 'push', 'origin', commit+':refs/heads/'+branch)
    receipt.update(candidateSha=commit, status='BRANCH_PENDING_DRAFT_PR')
    save()
    prs = json.loads(run('gh', 'api', '-X', 'GET', 'repos/'+REPO+'/pulls',
                         '-f', 'state=open', '-f', 'base=main',
                         '-f', 'head=homelux-huang:'+branch))
    if not isinstance(prs, list) or len(prs) > 1:
        raise ValueError('Ambiguous PR response')
    if prs:
        pr = prs[0]
        if pr['head']['sha'] != commit or pr['base']['ref'] != 'main':
            raise ValueError('Existing PR revision mismatch')
    else:
        pr = json.loads(run('gh', 'api', '-X', 'POST', 'repos/'+REPO+'/pulls',
                            '-f', 'head='+branch, '-f', 'base=main',
                            '-F', 'draft=true',
                            '-f', 'title=Stage QA-approved question data (NO RELEASE)',
                            '-f', 'body=Candidate '+commit+' on base '+base+'. '
                            'NOT READY: independent MASTER/E review and actual same-head '
                            'PR checks required. GITHUB_TOKEN PR creation does not trigger '
                            'ordinary PR CI. No automatic merge or Pages dispatch.'))
        if pr.get('draft') is not True or pr['head']['sha'] != commit or pr['base']['ref'] != 'main':
            raise ValueError('Created PR does not match pinned Draft candidate')
    receipt.update(prUrl=pr['html_url'], status='DRAFT_PR_PENDING_INDEPENDENT_REVIEW_AND_CI')
    save()
    print(json.dumps(receipt))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact-dir', default='_sync_candidate')
    publish(Path(parser.parse_args().artifact_dir))
