# MASTER — explicit authorized PR handoff for 114/115 approved sync
Date: 2026-11-04
Owner: MASTER task MASTER-P0-SYNC-EXPLICIT-MANUAL-PR-HANDOFF-20261104-02, Issue #36 claim #6631192619.

## Why this matters
Main Actions run 41786121113 (commit e4895fe6297ea8ff4fc92ecb5759521a796ab8da) generated the correct, SHA-pinned approval candidate and persisted an artifact, but GitHub returned `GitHub Actions is not permitted to create or approve pull requests (HTTP 403)` on POST /pulls by the stock `GITHUB_TOKEN`. A separately authenticated GitHub connector opened the exact existing branch as PR #162. PR #162 passed 9 exact-head checks and was normal protected-merge to main `cca0fd6d6d3666ee9edf475353cf84cce5e1ebba`. This was metadata-only publisher provenance, NOT a new student QID or a permanent grant of token privileges.

## Explicit pipeline behavior
The auto-sync workflow now uses `python scripts/sudu_sync_candidate.py --pr-mode manual`. It:
- runs the unchanged strict annual publisher/source admission checks, per-QID allowlist, SHA-pinned tree+patch, path scope, stale-base and symlink/rename guards;
- pushes *only* a deterministic, isolated `sync/qa-approved-BASESHA-TREESHA` candidate branch, never main;
- keeps `_sync_candidate/candidate.patch` and `receipt.json` for GitHub Actions artifact retention;
- checks whether an already-open PR exactly matches candidate head, base and branch; if so, records its URL and `DRAFT_PR_PENDING_INDEPENDENT_REVIEW_AND_CI`;
- otherwise does **not** POST /pulls with the known-disallowed Actions token. Emits conspicuous GitHub `::warning`, `MANUAL_PR_HANDOFF_REQUIRED`, `needsAuthorizedPrCreation=true`, and `handoffUrl` in the persisted receipt, with `ready=false` and `deployed=false`.

This means **the GitHub Actions job may succeed at securely staging a handoff** while the human/connector PR operation remains REQUIRED. The `MANUAL_PR_HANDOFF_REQUIRED` receipt and Actions warning are *not* CI acceptance, PR created, independent teaching QA, student READY, or LIVE. MASTER must use an authorized GitHub connector to create a normal Draft PR from the exact branch, then confirm real PR-triggered CI and actual authorized review; no admin bypass, no PAT, no impersonated GitHub APPROVED. Existing tests keep API mode for authorized independent clients; unknown gh API errors in API mode still raise and fail.

## Rollout and negative checks
Run `python -m unittest discover -s tests -p test_sudu_sync_candidate.py -v`, publisher 114/115 regression, required PR gate and Chromium/browser workflows at exact head. New actual-local-Git tests ensure manual mode never issues POST, same SHA/candidate receipt is idempotent, a separately authorized exact-head Draft PR is recognized, and a mismatched PR SHA is rejected. Existing tests continue checking forged paths (leading-space, control character, traversal and rename), stale main and symlinks. The workflow's `pull-requests` permission is reduced from write to read.

## Still the student release chain
A source original WebP, official answer/correction, 205-row canonical/SQLite proof; B/C current source-bound lesson; independent E receipt adopted by MASTER; D true publisher-emitted non-intercepted 8-size x 2-theme QA; approved one QID, required PR CI, normal protected main, Pages verify_live. A manual PR handoff cannot bypass ANY of those stages. Maintain 114/115 priority, defer 104-113 new development.

No approved JSON, student UI, trusted review registry, source images, lesson/SQLite or published QIDs change in this engineering PR.
