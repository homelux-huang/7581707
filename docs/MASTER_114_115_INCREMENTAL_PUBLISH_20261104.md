# 7581707 MASTER — 114/115 incremental publisher integration (2026-11-04)

## Scope

User directs incremental student release **only after full per-question evidence**, without waiting for 410 questions. This candidate is **security-only**: it adds no READY state, original WebP, official answer, lesson, approved JSON, reviewer registration, SQLite change, or student admission.

- Protected main base: `ba2f3f0757dbf81eaaf125bd610b0f38de52fea9`.
- Prior MASTER year-routing PR: #141, exact HEAD `01e342b1902c030a9678836ae4de7d0f5cb3be4c`.
- E independent static review: #141 COMMENT, #153 separate source-code hardening (closed without merge); both require normal authenticated code review for main.
- Combined main-target Draft integration PR: #155, includes both 114/115 official schema year routing and named-114 final answer image evidence binding.
- Original five approved 115 Math B Q02/Q03/Q04/Q05/Q09 stay unchanged, 114 approved remains zero. Test fixtures are not official release receipts.

## Safety changes

1. Remove `if year != 115: return False` source-notice gate and source-index 115-only hardcodes. Permit only official 114 and 115 TCTE annual indexes, exact same-year evidence path and date-pattern, reviewed notice SHA/page and question ID.
2. Check 114 historically four document review flags and 115 historically three document review flags separately. Non-corrected questions in corrected papers require *individual* no-correction scope, not fictitious paper-wide no-objection.
3. For an actually **named 114 correction**, require BOTH the individual official proof final-answer-image QA flag AND the named notice-ledger item `publishedFinalAnswerImageIndependentlyVerified is True`. Missing, false, string, numeric, fabricated flag cannot pass; existing original 114 E26 false remains blocked. E11/E12 are unaffected individual English QIDs and retain their original unchanged notice path.
4. Never change independent AI reviewer trust policy, `trustedAiReviewReceipts`, protected GitHub review or main/Pages safety gates. Both 114 and 115 have positive/negative synthetic regressions. They are **not** a proxy for true official sources.

## Required before code integration

- Fresh exact HEAD mandatory GitHub PR checks (including publisher/notice regression, security admission, V4 browser); compare source code and test SHA on the candidate head.
- Authorized code review under protected main. E GitHub COMMENT alone is **not** GitHub APPROVED.
- Only normal protected PR merge after all requirements pass, followed by Pages same-SHA verification. No direct push or force.

## Required before any *new student question* is admitted

For each QID separately: Role A original single WebP + question/options/official final answer/correction + exact canonical JSON/manifest/SQLite provenance; Role B/C current dual-level four-choice teaching and full math steps; independent Role E different-session reviewed current sourceRevision + WebP SHA + teaching digest + MASTER trust registration; Role D true publisher emitted source-data 8 viewport × 2 theme Chrome (no QA-only interception) bound to `testedTeachingDigest`; final publisher G0–G10 and official CI; protected merge, Pages same SHA plus real student answer check. Track per-Q states via Issue #36 and only PR30 as sole canonical delivery ledger.

The currently source-staged 114 E12/E11 have not been imported into their 205-row canonical JSON and SQLite due to lease arbitration, so remain blocked. 115 MB20–23 staged technical UI and E lessons similarly **are not newly READY**. Work on the earliest actually releasable QID first, keep others quarantined.

Master assignment and explicit conflict lease arbitration: [Issue #36](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623998156), [shared-file arbitration](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623987391).
