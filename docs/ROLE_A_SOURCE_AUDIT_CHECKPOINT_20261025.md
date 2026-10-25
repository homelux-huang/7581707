# Role A | 114/115 official-source checkpoint | 2026-10-25

Status: **BLOCKED / NO RELEASE**. This is a source-evidence routing checkpoint, **not** new visual inspection, official final-answer approval, SQLite re-import proof, or student authorization.

## Isolation and command resolution
- Independent work branch: `agent-a/114-115-source-audit-20261025`, forked from `qa/mb20-25-latest-source-sync-20261025`. Do not merge into main or deploy.
- Requested `docs/114-115-DELIVERY-COMMAND.md` returned GitHub Contents API 404 on `main`, `qa/114-115-official-visual-review`, and `qa/mb20-25-latest-source-sync-20261025` when checked; obtain the actual committed command before asserting full command compliance. Follow the user's current restrictions in the meantime.
- PR #21 (114 English 07-09), #22 (114 official publication gate), #24 (MB23 original table), #25 (115 MB20-25 corrected source / SQLite), #26 (integration candidate), #28 (teaching) are separate candidates; their claims are not merged source/teacher approvals.

## Latest observable source candidate, six exact question IDs
| ID | source WebP SHA-256 | candidate official answer, NOT final QA |
|---|---|---|
| 115-00-MB-20 | f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf | A |
| 115-00-MB-21 | b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693 | A |
| 115-00-MB-22 | 3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55 | B |
| 115-00-MB-23 | 2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51 | B |
| 115-00-MB-24 | c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb | C |
| 115-00-MB-25 | 92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896 | C |

Evidence: `sudu/data/processed/115/review-evidence/MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json` (Git blob SHA `e8d8baece00b0eb489a8e8ea7cb2edeac42894d0`). It explicitly records `formalTextQaPass=false`, `independentTeachingQaPass=false`, `releaseReadyCount=0`. Do NOT promote answer-match or AI visual analysis to independent review.

## Critical MB23 consistency
- Keep the original official **2-row × 3-column trip cost table** and unchanged original WebP SHA `2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`.
- PR #24 fixes candidate table revision binding and accessible semantic display, but is a draft; rebase/port its table schema and source revision into the source candidate before claiming source admission. Any changed table cell must invalidate previous source/teaching approvals.
- Do not rewrite/re-OCR original image or mark it PASS without independently reviewed original cells.

## Year-specific official notice evidence
- 115 `official-confirmation-status.json` Git blob SHA `6d21432395294d9ccbcfe1dea8be01f88597bbf3` (checked 2026-10-23): 00-C confirmation PDF SHA `231f21ac52bb1006717ec6a17b325454a37269317a1f49944dbfd0a31d28c4c0`; 00-E SHA `bd6405814955e2c997ad5c7e69e34a10a5fcc22462b4227eabba0067760aa1a6`; 09-2 SHA `b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133`; 00-MB and 09-1 are recorded as no-objection, **not blanket independent answer QA**.
- 114 PR #19 documents four confirmation PDFs covering 18 specifically named questions; PR #22 year-specific admission must be retained. Never reuse 115 correction scope for 114.
- Official sources: https://web1.tcte.edu.tw/EXAM/114_4y/ and https://web1.tcte.edu.tw/EXAM/115_4y/.

## Next required machine-verifiable work (NOT claimed done in this checkpoint)
1. Fetch current master delivery command from its actual branch/path; compare precise allowed file boundaries.
2. Reconcile PR #24 table-aware MB23 revision with #25's latest six corrected JSON/SQLite; preserve original OCR, 199 unaffected questions and full before/after diffs.
3. Isolated `PRAGMA integrity_check`, exactly 205 row/ID/payload hashes and two independent deterministic SQLite imports; record both DB binary SHA-256. **No live execution was performed when writing this checkpoint.**
4. 114 English 07–09 and 115 economics 34: ingest real source WebP/current manifest SHA, original answer PDF SHA, year-specific named announcement scope and authorized separate image reviewer evidence.
5. Bind evidence to actual fail-closed publisher input field paths; rerun negative tests for changed SHA, missing MB23 table cell, missing correction scope, OCR mismatch.
6. Send exact revised source SHA, official PDF SHA, visual QA reviewer/time, DB proofs and unresolved blockers to Master. No self-approval and no LIVE.

This file is an audit trail only. It intentionally does not modify approved records, student-facing assets, V4, main, or deployment workflows.
