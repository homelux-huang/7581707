# ROLE E｜114 Named Official Correction Final-Answer Image Evidence Gate

Date: 2026-11-04. Owner: independent content/security audit ROLE E (NOT source author A, not publisher MASTER). Branch: `qa/role-e-114-named-image-proof-gate-20261104`, stacked onto [MASTER PR #141](https://github.com/homelux-huang/7581707/pull/141) exact base `01e342b1902c030a9678836ae4de7d0f5cb3be4c`.

## Problem, bounded scope
In PR141's year-routed `official_notice_scope_certified()`, the **114 named official answer-correction branch** accepts the source-authored `officialFinalAnswerImageQaPassed=true` even when the archived official **named correction** ledger item explicitly reports `publishedFinalAnswerImageIndependentlyVerified=false`. The actual archived 114 English E26 record has that exact false value. No claim is made that this alone bypasses the other source, AI-E trust, UI, G0–G10, and protected-main gates.

## Change (no new release)
For year=114 and a **named** official correction, require **both**:
1. SHA-bound official proof `officialFinalAnswerImageQaPassed is True`, already required in PR141.
2. Matching `confirmed[]` row `publishedFinalAnswerImageIndependentlyVerified is True` in the year-specific official correction ledger.

Missing, false, or string `"true"` fails closed. No requirement for a real teacher, named human, signature, GitHub APPROVED or arbitrary self-asserted Session ID. The previous separately reviewed official image ledger is an evidence step, not sufficient to authenticate an actual independent AI execution by itself; MASTER still authenticates provenance and a trusted source SHA.

For a question **not named** in a same-paper correction document (for example, 114 English E11/E12 while only E26 is named), the individual `noCorrectionForThisQuestion` path remains unchanged. Year 115 behavior remains unchanged; cross-year and malformed ledger rejection from PR141 remain intact.

## Tests and release boundary
Changed files: `scripts/sudu_verified_publish.py`, `tests/test_sudu_verified_publish.py`, and this ROLE E documentation. The original strict 114/115 positive/negative tests remain enabled, with a genuine named-114 synthetic fixture now including an independently validated answer-image row. New negative checks cover false/missing/string-true row even when untrusted proof says success. Existing G0–G10, policy, student records and all 205 canonical source data untouched.

**NO RELEASE**: Not a registered protected-main trusted E receipt, not author G2/G3 admission, not an actual 8×2 same emitted teaching SHA, not an independent reviewer APPROVED or MASTER release authorization. No new approved/114 or /115, main, Pages or LIVE update. MASTER must review and merge per protected rules, independently vet this change (the same GitHub actor cannot serve as authenticated separate approver), and run CI + real release gates on exact merged SHA. 114+115 remains priority; 104–113 new development stays paused.

Related: [ROLE E Issue #36 CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623945202).
