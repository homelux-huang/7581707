# WORK MASTER 2026-11-14 — current facts and next bounded roles

This is a measured execution return, not a second question ledger or a release certificate.
Repository: https://github.com/homelux-huang/7581707
MASTER CLAIM: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6870682878

## Observed state

- Protected main: `5546a603abfe0af2e62c0e5f63f775be0bfb24cf`; source QA before this patch: `15108e8e657d070724889f1df3d3a6ae6da96d97`.
- Current connected GitHub identity `homelux-huang`, admin=true. Browser control actually connected to the owner's local Edge; the cloud terminal has no gh login. No Windows terminal/system modifications were made.
- E12 environment actually created through GitHub Settings: environment ID `27268060737`, https://github.com/homelux-huang/7581707/settings/environments/27268060737/edit . Readback: administrator bypass unchecked; selected branches has exactly one branch rule `security/master-e12-openai-first-response-harness-20261111`, zero tags; environment variable `E12_G6_OWNER_ARMED=OWNER_CONFIG_HOLD`. Required reviewers still absent: no verified independent operator/reviewer identity supplied. GitHub disables Save protection rules when Required reviewers is selected with an empty reviewer list; Prevent self-review therefore is NOT saved. Operator login and API secret deliberately absent. No inference/paid request performed.
- Main protection read through the owner's actual Settings UI: PR required, required status `7581707 required PR gate` from GitHub Actions, strict up-to-date checks, conversation resolution and no administrator bypass enabled; force push and deletion disabled. Require approvals is unchecked, stale approval dismissal checked. No main protection changes made.
- `python scripts/check_live_release.py --url https://homelux-huang.github.io/7581707/ --expected-sha 5546a603abfe0af2e62c0e5f63f775be0bfb24cf --attempts 1` returned actual `LIVE_VERIFIED`. 114 approved=0/205 (9 image-only previews); 115 approved=5/205 (119 image-only previews). Browser opened the original V4 and displayed MB02/03/04/05/09. New LIVE=0.
- Main V1 policy Blob `c77ee2ec8ca1381388fbbbe6bd36e679750678eb` has `trustedAiReviewReceipts={}`. This blocks all new candidate content admission, independently of E12. No receipt, trust, READY or student data changed.
- The designated ledger and command documents are absent main and current QA. Their original identity exists only in open Draft PR30, HEAD `c89d8f0c681c41022302b7deefaeb4ae5437fd29`; its 410-entry ledger updated 2026-10-27 contains stale policy/status. Preserve it and reconcile through its original branch; do not pretend it is merged/current.

| Candidate | Exact current head / state | Verified progress | Still needed |
| --- | --- | --- | --- |
| 114 E11 | PR189 `06d11e6f8cf4bc5d6ca213fd66d4560fa62360ee`, Draft | QA source admitted; author CI43401592535 success; teaching `ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb` | CI routing, QA author merge, authentic independent receipt, emitter, native UI |
| 115 MB21 | PR181 merged into QA | G2/G3 source, frozen teaching `4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4` | issuer/provenance, receipt, emitter/UI |
| 115 MB22 | PR182 merged into QA | G2/G3 source, frozen teaching `5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600` | issuer/provenance, receipt, emitter/UI |
| 115 MB23 | PR185 `24f8962b7fb51a8baa6f111abb1a7414a4b26420`, Draft | complete 2x3 table, source CI42827387639 success | QA source merge, receipt, emitter/UI |
| 115 MB20 | PR187 `6ff6dd7985af453e8e1ffa59eab240db9a6907ae`, Draft stacked on PR185 | final-head source CI43400875584 success | PR185 first; retarget/preserve original delta, receipt/emitter/UI |
| 115 MB24/25 | PR157 `24decc38...`, Draft | original source staging | canonical/SQLite admission and downstream gates |
| 114 E12 | PR173 `aa77cf6bd2ecfe5e1b4fdf57810be8734ec82161`, Draft | existing semantic/source notes | true G6/G7; external operator and independent reviewer |

## CI repair and limits

Two historical one-question E11/MB21 workflows previously ran fixed old path-whitelist/baseline tests on unrelated later QA PRs. This patch confines those jobs to their original source branch/same-repository PR and retains original acceptance commands/tests. A new read-only workflow verifies current 114/115 banks: 205 unique IDs, actual SQLite integrity, JSON payload equality, payload SHA, core identity fields, manifest IDs and inventory hashes. Eight regression tests cover real current data and corruption rejection. Separate agent code review and MASTER local rerun passed 8/8 and both years 205/205. These are payload-integrity results, NOT full source provenance or student release.

Known preexisting QA115 debt is explicit: 79 denormalized `answer_verified` fields differ from canonical payload, and MB05 denormalized `question`, `question_verified`, `review_status` differ. This patch does not edit them. They require separate A work without overwriting other current rows. Frozen MB23 whole-manifest assertions must likewise stay on its historical snapshot after legitimate MB20 manifest admission; no historical tests should be disabled to falsify source approval.

## Copyable ROLE A prompt

Continue source engineering only. Refresh Issue36 leases and QA HEAD. Review PR185 then stacked PR187 exact snapshots; preserve original 2x3 MB23 table, Q20 v5 original WebP and all 205 complete payloads/other204 tuples. After legitimate QA review/CI, integrate in dependency order. Separately claim and repair the known 115 denormalized SQLite column debt from canonical JSON, archive before/after hashes and changed columns, and prove no payload/answer/source text changes. Do not edit teaching/trust/approved. Keep each historical full-manifest/one-PR assertion bound to its frozen snapshot. Return exact PR/commit/Blob/CI; source merge is not READY.

## Copyable ROLE B prompt

Continue 114 E11 original author work using PR189 and teaching SHA above. Do not rewrite the correct original lesson. After CI routing and QA merge, supply genuine original author provider/session/task provenance admissible under current V1; if unavailable explicitly UNVERIFIED. Coordinate a different authenticated E reviewer. Do not self-approve, alter E records, trust or approved data. E12 remains frozen on its existing digest. Return native issuer exact SHA and actual CI.

## Copyable ROLE C prompt

Continue 115 MB21/22 first, then MB23/20. Preserve frozen correct authored teaching. Supply native publisher-compatible teaching issuer documents and genuine author provenance bound to admitted current G2/G3/WebP/source revisions. Do not infer authenticated identity from a GitHub actor alone. MB24/25 need A canonical source admission first. No E/trust/UI/READY declarations by author.

## Copyable ROLE E prompt

You must be a truly separate authenticated execution subject from B/C and the solver. Refresh official QA and exact source/teaching bytes. Independently verify official answer, all A-D explanations and calculations; preserve raw provider/session/task evidence and Issue36 RETURN. Current main V1 has no trusted receipts. Generate an exact-SHA receipt only when its full authenticated provenance contract is satisfied; missing identity remains UNVERIFIED. Existing semantic notes or MASTER child agents alone cannot replace V1 admissibility. Start E11 or MB22; E12 G6 is separate. Return receipt/blob/issuer evidence without modifying protected registry yourself.

## Copyable ROLE D prompt

Preserve unique V4. Wait for actual protected-policy-admissible content receipt and a genuine native private publisher-emitted candidate. Then run Chromium8 viewports x2 themes per QID, original WebP/digest checks, calculation hide/show and RWD. No page.route/mock approved positive. Return all16 case results, raw screenshots/hashes and tested teaching digest; MASTER alone declares READY and Pages LIVE.

## Copyable independent operator / security reviewer prompt

Owner must name real distinct GitHub operator and reviewer logins with evidence of independence from B/E/MASTER. Environment exists at URL above but is HOLD and incomplete. Configure required reviewer and Prevent self-review, retain no-admin-bypass and exact branch restriction, then safely install dedicated limited-spend project key as environment secret only. Do not post credentials in chat/issues. No ARM or inference until independently verified. Use PR188 frozen answer-free G2 Blob `29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff` only; freeze actual first request/response bytes, provider IDs and chronology before revealing answer. A separate security reviewer verifies provider provenance, custody, separation and replay protection. Do not retry retired GitHub Models or substitute synthetic CI for G6.

## MASTER continuation

After current repair exact-HEAD Actions and code review, merge QA-only repair under normal rules. Review/admit source185, then187, then author189 without changing student release flags. Reconcile original PR30 ledger rather than making another ledger. Obtain genuine admissible E evidence for E11/MB22, then protected registry + native publisher + D16/16 + G0-G10 + protected-main PR + Pages same-SHA verify_live. If identity is unavailable, report concrete missing logins/provenance and continue independent source/CI work. Never count source-only merge or a synthetic passing test as new LIVE.
