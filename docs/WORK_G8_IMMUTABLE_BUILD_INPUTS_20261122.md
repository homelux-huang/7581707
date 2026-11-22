# WORK G8 committed build inputs — 2026-11-22

Task: `WORK-G8-IMMUTABLE-BUILD-INPUTS-20261122-01`

Base: PR216, `895eebef582f2a3294d55a05e1d587e7258563e9` on
`fix/work-g8-actual-webp-testc-20261115`.

## Problem and resulting behavior

PR215 independently rebuilds a stage and rejects a resealed file map that differs
from the reconstructed site. However, the real builder previously enumerated
the mutable code checkout. `code_bindings()` pins selected tracked code files,
but does not cover every public SVG, JSON file, crop configuration, crop source,
or untracked/ignored public file. Both the initial build and reconstruction
could therefore consume the same uncommitted bytes while retaining identical
`codeCommit` and `codeBindings` values.

The bridge now builds from the selected commit's Git object tree. It exports
the existing public allowlist plus explicit committed crop dependencies into
a private temporary snapshot. Each input must be a regular committed blob.
Every exported file is checked against its expected Git blob hash; transformed,
omitted, duplicate, symlink or unexpected archive entries are rejected. The
snapshot also supplies the catalog and index template. Its release marker is
bound to `codeCommit`, independent of `SUDU_BUILD_SHA` in the calling environment.

`build.build()` accepts an explicit source root and revision for this bridge
path. Existing callers retain their default behavior. The bridge retains the
existing complete stage reconstruction and native approved-data merge.

## Verification

Five new tests use a real temporary Git repository and the real builder:

1. A clean committed site and crop build successfully and bind the exact commit.
2. Untracked root HTML and ignored public assets never enter the expected site;
   adding and resealing them in a stage is rejected.
3. Modified tracked SVG, JSON, crop configuration and original crop bytes do not
   change the pinned output; a resealed modified asset is rejected.
4. Missing or symlinked worktree asset files do not replace committed bytes.
5. A committed public symlink or `export-ignore`/`export-subst` transformation
   fails closed.

The new tests deliberately reuse synthetic unit authority. They do not create
genuine author/reviewer receipts, model responses, G1–G7 eligibility or G8
approval. PR216's actual MB20-v5 / MB23-table tests remain separate and retain
their explicit synthetic-authority limitation.

Before commit, the full local `test_sudu*.py` discovery completed with 143 tests,
142 passed and one skipped. The independent code reviewer also ran 35 focused
tests (the five new regressions, 17 bridge tests, four public-build tests and nine
archive tests) and found no blocking code issue. This is a code review, not a
formal GitHub approval, ROLE E content review, G6 execution or G8 credential.

The read-only CI workflow now runs the full regression suite, verifies that a
clean public build equals two committed-snapshot builds byte for byte, runs the
four actual-image TEST C checks, and verifies that current protected policy
still admits only the historical five questions. The exact commit/run result
must be read from the PR; this document does not predeclare CI success.

## Scope and remaining release dependencies

This change covers build inputs only. It changes neither native lesson/source
content nor admission rules, protected trust policy, approved payloads, branch
protection, publishing workflows or deployments. The CI workflow has only
`contents: read` and `actions: read` and does not invoke a model or publish.

The current main/QA check found no accepted new independent content receipts or
G6/G7 evidence. A separate read-only audit also identified the E11 native G5
envelope/content `calculationReviewed` incompatibility. No schema acceptance
change is included here. E12 remains a separate HOLD.

Normal review of the stacked bridge PRs, genuine E and G6/G7 evidence, formal G8,
protected promotion and HTTP/Pages verification remain prerequisites for any
new LIVE claim. This patch does not declare a new eligible or LIVE question.
