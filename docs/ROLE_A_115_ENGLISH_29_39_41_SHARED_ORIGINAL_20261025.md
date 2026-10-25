# Role A — Existing 115 English 29/39/40/41 image receipts and unresolved original shared passage candidates

**Task:** `A-115-E29-E39-41-ORIGINAL-PASSAGE-ASSETS-20261025-07`. **Branch:** `qa/role-a-115-e29-e39-41-original-source-20261025`, on exact unchanged PR35 source integration base `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`. No main/Pages/deploy, no teacher signature and **no new individual or shared image QA PASS**. Latest user policy in Issue #36 replaces human-credential pedagogic approval with distinct independent AI content review, preserving all technical and release gates.

## Four original individual exam WebPs — already historically AI-reviewed at same SHA

| QID | Original WebP SHA-256 | Original Git blob SHA-1 | Original source revision | Existing C-authored teaching digest |
|---|---|---|---|---|
| `115-00-E-29` | `200722eaba0530fc8f3963cfe9c72e2749630de188ad538d5ce23200d949717d` | `122436f959d7ed8ce5e8c2f8f5e5c2711f81f889` | `23952dc29ed2622029cce5b7a431e4c9209ca99c41f25fc7eea5b15af56f883d` | `50ceae4c440af17b06d0ef31ac4bd7c83edca796fe153f26a0e2c339665912d6` |
| `115-00-E-39` | `0e71395b101b6e255d48b3eea86e8a4a1086cafabab62104ade3474b32f11d3c` | `6af1245cc9e866192eef312be9c3463739b31282` | `9a098b1db2de04ecdf3af694a686e30a573ba4d63356dbf1dfe39e7ea230956a` | `7f98f96420a9304518172d206eafc1c88fd932e47b214f00212aef13d6b082ad` |
| `115-00-E-40` | `afa2a88eb2574bae17aad8d4a16f662e889b906f024b8950e45439f12210fbef` | `63a608f38943cd3919afb31a628cd00b2104ad93` | `1066b79c8271d1882e9f443609665de1dab0f6a0a49553349e1d65904091fb31` | `5816e15304cd0e7084c41347cc4a40a3d9afd995ed132848bfd717eeca53556b` |
| `115-00-E-41` | `b10a8ba84292df22dc481107280522e8f8dc168ef0496f9af3f4bf71329740a4` | `cfb8001f89418c2f5a12cf7c68384aa9d48230a4` | `b5b2282057f093845c8745986a9e034e1bdfb6e6df10c18ab8d445507a68f0fd` | `b46c697373efc8e2641b42c4c9df6e6eda14848faf8f2bd4f9f0aa94c2f20f6c` |

All images copied **unchanged original Git blobs** from `qa/mb20-25-latest-source-sync-20261025` into PR35 source candidate paths `sudu/data/processed/115/webp-v2/00-E/{115-00-E-29,115-00-E-39,115-00-E-40,115-00-E-41}.webp`. Existing PR35 questions, visual QA manifest and authored C lessons already reference those exact paths/SHA. 115 English official original PDF question SHA-256 `c13e298c3b05b890c410deac4f8f694905f19fcd3a63bb4fcc0662ee6cb2768a` was **previously recorded**; this task does not redownload/re-hash original PDF. Original page six WebP SHA256 `b34b9c3c8d94d8d54589634a4403cfa14810b8736e1a9a3202b240a1490423df`; page ten WebP SHA256 `6c86c1fa3edd0eef061ac08c1f4155fa11fc442452efb603061badcc0358388c`, rehash and decode in CI.

The original **historical AI individual image visual-QA** evidence has Git blob `1b3b0f7667dd1534b385698d5875d74c0db768cf`, raw SHA-256 `9a28eefef299d2b50f81c623cd4316b51f0091c0ecb705055c8bf12ba1815aa5`, at `sudu/data/processed/115/VISUAL_QA_2026-10-22_B2.json`. It already records these four original individual question images **PASS_ASSISTANT_VISUAL_QA** at exact SHA, for question number/stem/four choices/no adjacent question. This is **image-only old AI review, NOT independent AI E teaching QA** and not a newly assigned PASS.

## Two original shared passage images: exact pixels restored, **both DRAFT/UNAPPROVED**

| Original shared material | Exact manifest crop/file version | Git blob SHA-1 | SHA256 | Status remains |
|---|---|---|---|---|
| `115-00-E-SHARED-29-30` | `webp-v2/shared`; page 6 crop `[90,165,1310,1498]` | `1938fe2a22233a82528c111547ec3f1a522d201b` | `e932d3fc246b55604cabd6fa1716d0fa6f8f67d658ed6a16c6d88f91bfdb49b6` | `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA` |
| `115-00-E-SHARED-39-42` | **v3** `webp-v3/shared`; page 10 crop `[90,166,1310,978]` | `4aaac02b7ed9390b8ff7c8a4c4272e74996bd595` | `5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b` | `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA` |

Never use the older **v2** `115-00-E-SHARED-39-42` instead of manifest v3, never assume shared article completeness just from SHA/decode. These are reading passages without which even a historically individual-image PASS does **not** suffice for a student-ready question. The source Chinese/English question text QA, original final published answer/correction and distinct AI content reviewer remain separate. All four authored C lessons in PR45 remain author drafts with no new approval; q.answerVerified and q.questionVerified remain false; shared material independent QA remains pending. Do **not** change `qaStatus`, `questionVerified`, `answerVerified`, `READY`, or original OCR from this source-file receipt.

## Validation and owner handoff

Original only modifications: four single WebPs, two exact shared **DRAFT** WebPs and one previously written B2 QA JSON (all original byte-identical Git objects). Additional own `tests/test_role_a_115_english_original_shared_receipts.py`, `.github/workflows/role-a-115-english-original-shared-receipts.yml` and this handoff. 8 strict tests require actual RIFF/WEBP/Pillow decoding and exact SHA-1 Git/SHA-256 for each original, two official page WebPs, existing per-question B2 QA, exact unchanged question+option source revision matching Role C, candidate-shared QA is still DRAFT with no passing visual certificate, 205-row SQLite exact payload/PRAGMA integrity and SHA/option negative cases. Read-only no-deploy workflow; record actual same-HEAD CI outcome. No V4, teaching, lesson digest, source bank, SQLite, manifest, governance or published data changed.

**Master/Role E next:** Review this exact immutable source receipt and import without overwriting PR35. The shared originals must be visually independently checked for full article/graphic, no adjacent question, original page SHA and exact bounds **before** being separately approved; any issue must remain quarantined. Obtain original official answer/correction scopes, distinct AI E actual four-option high-school + elementary content audit and same digest V4 8×2 CI; then sole master may incrementally publish only READY questions. **NEW READY=0; NEW LIVE=0**.
