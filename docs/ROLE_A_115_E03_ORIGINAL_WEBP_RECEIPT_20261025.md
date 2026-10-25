# Role A — 115 English 03 Original WebP Source Receipt (2026-10-25)

**Task:** `A-115-E03-ORIGINAL-WEBP-RECEIPT-20261025-04`, Issue [#36](https://github.com/homelux-huang/7581707/issues/36). **Role:** A, source integrity author, not independent AI reviewer E. **Base PR35:** `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`. This is an isolated source candidate, not main and not a LIVE deployment.

## Exact original image, question and historical visual QA

- Canonical ID: `115-00-E-03`; official paper `115-00-E`, original question number 03, English; existing correct-answer **candidate** B (`equally`), not an independently approved final answer.
- Previously verified original single-question image: `sudu/data/processed/115/webp-v2/00-E/115-00-E-03.webp`. **Exact original Git blob SHA-1** `f511b6b5447c38f4cb91ec14572adef56f79991f` restored unchanged from `qa/mb20-25-latest-source-sync-20261025`; **WebP byte SHA-256** `16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd`.
- Original official PDF page 2 rendered WebP: `sudu/data/original/115/00-E/p002-c13e298c3b-v2-w1400-q66.webp`, page WebP SHA-256 `0ae3b4495aa79c71248e8b554494009d13b24086f0c23fa1a8fd9a32e44ff68c`; paper PDF SHA-256 **previously recorded only, not fetched/rehashed in this batch** `c13e298c3b05b890c410deac4f8f694905f19fcd3a63bb4fcc0662ee6cb2768a`.
- Exact original pixel crop [left,top,right,bottom] `[90,592,1310,706]`; output image `1220×114`. Existing manifest `qaStatus=PASS` is from pre-existing Demo historical visual QA, **not newly assigned in this task**.
- Original historical QA document `sudu/DEMO_VISUAL_QA.md` SHA-256 `50506b98dba9b3da2d58dd485fe2fe64aaf8e4f16b89efbe91313702b7a66124` explicitly lists English #3 `90,592,1310,706`, `1220×114`, `PASS`, same WebP SHA. No need to crop, OCR or re-draw the image.
- Question text and A–D in the unchanged canonical bank are `The teacher treats all her students ... giving every student the same opportunity to succeed.` and `carelessly / equally / instantly / silently`.
- Exact canonical `scripts/sudu_verified_publish.py:text_revision` (question+options+single WebP SHA): `c7e7262a3d5283d547f1dda35f1070c21d432314069286b305265aad9fa8977e`, matches the previously submitted Role C teaching candidate [PR41](https://github.com/homelux-huang/7581707/pull/41); historical teaching digest `c7bce2469356f95e929b19d5275cd3ca1a4ff8f2c9f89cd858b61e5c8cdc3316` is unchanged **and not independently approved by Role A**.
- Recorded official published answer PDF SHA-256 `185b1c8503898290862cc4ba87d220d9969c882e26d52c4939b72db1d3b1af04`, previously extracted answer B; current `officialRevisionChecked=false`, `answerVerified=false`, `questionVerified=false`. The 115 `00-E` confirmation-PDF ledger lists question 34, **not question 03**. No fresh independent final-answer QA was performed here.

## Reason for change and testing

Latest Role E read-only audit at Issue #36 [comment #6393660861](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393660861) found exact original English #3 image **404 in PR35** despite existing manifest and canonical source pointing to the known-good original asset. No new student question can enter UI without actual HTTP original WebP bytes. This task restores only that **one existing Git blob** and adds a dedicated strict test, a read-only GitHub Actions workflow and this handoff. There are no edits to existing 205 questions, original OCR, SQLite, answer, lesson, V4, policy or approved files.

The test `tests/test_role_a_115_e03_original_webp_receipt.py` checks real WebP RIFF/decode/dimensions, Git blob SHA-1, file SHA-256, historical Demo QA SHA, matching source official paper page/crop, exact source-text digest, A–D and answer candidate, all 205 SQLite payload hashes + PRAGMA integrity_check, 115 English correction scope, negative wrong SHA/option/dimensions and no source/official approval promotion. The workflow `.github/workflows/role-a-115-e03-original-webp-qa.yml` is **contents:read**, persist-credentials:false, no deployment. The existing publisher, independent E review and V4 exact-digest UI still must be run **by their respective roles** after master integration.

## Latest user policy and strict separation

Issue #36's top section supersedes old actual-human-teacher requirements. A distinct AI reviewer E with substantive image/source/answer/teaching review and verifiable source/teaching SHA evidence is required; author C cannot self-approve. Current PR35 publisher still has the obsolete teacher-signature admission gate; MASTER is responsible for independent-AI transition [PR46](https://github.com/homelux-huang/7581707/pull/46) and validation. Role A does not change any of it. Do not promote previous AI visual evidence to a new independent review or a publication pass.

**Result stage:** one source image restored / dedicated CI gate pending result; **new READY=0, new LIVE=0**. Master should review this Draft PR, copy exact original blob and associated strict proof to latest isolated integration, run checks, and coordinate Role E/D, then master-only incrementally publish any genuinely READY questions.
