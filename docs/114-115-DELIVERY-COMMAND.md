# 114–115 Delivery Command — master coordination (2026-10-25)

## Authority and immutable baseline
- Repository: homelux-huang/7581707; only student UI: `sudu/v4-115-multisubject-review-demo.html`.
- This document is a coordination candidate on a dedicated branch, NOT a merge, admission, deployment, or independent review.
- Actual PR inspection: #21 and #22 open; #23–#28 open Draft. Integration candidate #26 at `33ca5b26b333f3913a63bd0e61f75f33557c3668`; QA candidate #25 at `fbd7756b995e3d27dc31a99ecc54fe66af4d82c6`; teaching candidate #28 at `f04b26de83931ca384443eeee72de1f9ff468423`; UI candidate #27 at `cb215a771df74dec485774a4e74fd691fbb03e77`.
- Re-read actual heads/diffs and source files immediately before every integration. Historical counts and PR claims are **not** independent acceptance.
- Exact official question inventory, paper boundaries and source SHA still require source extraction/verification against year-specific TCTE PDFs. Never mark year complete from publisher's hard-coded `COUNT`.

## Executable delegation / ownership
| Role | Work branch or candidate | Responsibility | Reviewer |
|---|---|---|---|
| A | PR #21/#25, canonical QA branch | 114/115 official paper numbering, source WebP original SHA, OCR/text, official corrections/answer PDF, SQLite exact roundtrip, MB23 table | E for source evidence; distinct teacher for teaching |
| B | New 114 teaching Draft PR | Per-question, four-option dual-level lessons and calculations where applicable, lesson digest, provenance | Independent authorized teacher, never B |
| C | PR #28, 115 teaching branch | Six MB20–25 candidate lessons and subsequent 115 subjects, source-bound full calculations | Independent authorized teacher, never C |
| D | PR #27 and compatible part of PR #24 | Existing 35-Demo seven-subject V4 parity, per-question 8 viewport × 2 theme browser traces and same digest | E for evidence validity |
| E | PR #23/#26 policy and admission inspection | Source/reviewer provenance, diff, approved GitHub reviewer event + signature, publisher and same-SHA LIVE evidence | Not same author as lesson, no AI persona as human |

No autonomous other-Session instructions were delivered by this document. All roles are assigned workstreams; no actual human assignee is implied.

## Single ledger and release sequence
`docs/114-115-QUESTION-DELIVERY-LEDGER.json` is the single coordinator ledger. Its entries use separate source, draft, independent QA, UI QA, READY, main and LIVE stages; unknown never maps to PASS. Populate remaining IDs only from fresh canonical paper inventory and compare actual original numbers per year.
1. Ground each question in official original paper and final answer/correction applicability, QA-bound WebP SHA and corrected structured text/SQLite. MB23 requires original 2×3 table as part of revision.
2. Author A/B/C evidence separately. Require genuinely distinct authorized human teacher for new lesson sign-off. The current policy at #26 explicitly says `requireHumanTeacher=true`, `authorizedReviewers={}`: new admissions blocked.
3. D checks matching Demo subject UI, answer interaction, explanation and exact version digest across viewports/themes.
4. E independently validates reviewer roster, GitHub identity and actual approved event, signed evidence, SHA, policy validity and full LIVE checks.
5. On passing **all** gates, integrate only necessary file diffs via Draft PR; run original publisher, mandatory CI, Pages deployment and same-SHA LIVE verification. Do not manually flip readiness, bypass assert, directly overwrite runtime or main, or treat image-only previews as teachable questions.

## Known blocking chain
- #21 source English 114-00-E-07/08/09 claims QA candidates; #22 year-specific official correction gate pending main acceptance and independent teacher approval.
- #25 corrected source MB20–25 on isolated QA branch; #28 candidate lessons on separate teaching branch: align source text revision, digest and full browser QA after accepted integration.
- #24 MB23 table and source revision must accompany source and UI; a prior V4 pass against a different digest is invalid.
- #23/#26 trusted teacher roster empty; five exact historical 115 MB02/03/04/05/09 may remain grandfathered **only when** original source revision, WebP SHA and teaching blob remain identical. They are not new approvals.
- Merge conflicts among #22/#23/#24/#26/#27 must be resolved at file/diff level, then all affected tests rerun; no whole-file replacement of publisher/runtime.

## Owner-only governance dependency
Provide independently verifiable teacher's GitHub account ID and role/qualification evidence; teacher authorization scope and effective/revocation dates; repository protection/ruleset and CODEOWNERS approval path; Ed25519 **public** key plus offline custody proof for **private** signing key; distinct real review event tied to exact PR HEAD and lesson/source revisions. Never upload private keys or simulate teacher signatures.

## Current release judgment
No new READY or new release is authorized by this coordination document. The public 35-Demo and previously deployed items remain a separate observable LIVE status, to be reverified with current main and public Pages SHA before making a fresh claim.
