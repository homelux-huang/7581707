# 7581707 MASTER｜114 / 115 official correction scope publisher repair (NO RELEASE)

## User authorization and scope

Issue #36: fix the previously hard-coded `if year != 115: return False`, 115-only TCTE source index and notice filename. Preserve all G0–G10 release gates and **only** admit a QID after independent A/B or C/E/D evidence. This branch is isolated from PR #57/PR #22 and **does not** edit protected main, approved/114.json, approved/115.json, authoritative PR #30 ledger, E policy, published V4, student records or Pages.

## Changes

- The supported years remain `YEARS = (114,115)`; all unknown years are rejected. `official_source_index(year)` forms a *matching four-year exam URL*, not a 115-only string.
- `official_notice_scope_certified` reads the same-year `official-confirmation-status.json` and **only** its declared `officialNoticeEvidencePath`. Exact filename format `QA_<year>_TCTE_OFFICIAL_CONFIRMATION_PDFS_<YYYYMMDD>.json` and valid path within that year's source subtree are required. Historical file dates are not fixed.
- The 114 historical record uses `allPagesInFourDocumentsReviewed`, `comparedToExistingOfficialPdfTextCandidate`, `changeFromExistingOfficialPdfTextCandidate`; 115 uses its historical three-document and published-table keys. A named 114 changed-item requires `officialFinalAnswerImageQaPassed=true` in addition to the other independent final answer gate.
- The exact official source SHA, reviewed notice PDF SHA/page count, same-year/source-index, unique known question ID, named correction answer, document completeness and an actual `no_objection_submitted` status are required. A challenged paper **cannot** be labeled no-objection as a whole; other unaffected QIDs must present a truthful individual `noCorrectionForThisQuestion` flag.
- Cross-year records, wrong-year source index, path traversal, wrong PDF SHA, duplicate named IDs, false visual-review scope and incomplete/missing official ledger **fail closed**.
- The separate independent AI reviewer trust registry is unchanged; `trustedAiReviewReceipts={}` continues to block all NEW admissions. Nothing in this change creates a reviewer token or marks a QID READY.

## Test and release boundaries

`python -m unittest discover -s tests -p test_sudu_verified_publish.py -v`
`python scripts/sudu_verified_publish.py check`

GitHub PR to main triggers Sudu QA admission safety tests and 114/115 verified V4 integration jobs, including existing 35-Demo browser controls. Test fixtures for both years are **synthetic positive and negative validation**; they are not original-question source/answer/E/D acceptance receipts.

NEXT: MASTER obtains exact-head PR CI; ROLE A integrates existing original 114-00-E-12/E-11 blobs + G1–G3/SQLite; different-session ROLE E creates credible per-Q substantive content and independent provenance; ROLE D retests actual published-data emitter digest in 8×2. MASTER merges and verifies Pages **one QID at a time** only if all gates pass. This change alone grants **new READY=0, new main question=0, new LIVE=0**.

Related current SHA: original main `ba2f3f0757dbf81eaaf125bd610b0f38de52fea9`; prior related unmerged Draft PR #57 already contains a narrower two-year fix, to be reconciled in final review without discarding other protected policy changes.
