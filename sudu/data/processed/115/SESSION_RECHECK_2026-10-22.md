# 115 題庫｜2026-10-22 新 Session GitHub 接手稽核（尚未完成圖片位元組複驗）

Repository: homelux-huang/7581707
Branch: data/115-full-year-question-assets
Baseline head inspected: 05246954739b4c5ac839d416809741a27b1cc946
main inspected: e9f8cc1db0a91519cf0d1ee081ca0257fa00a64d
PR #1: Open / Draft; no merge or deployment.

## B2 嚴格核對（第一階段：manifest metadata）
- B2: 60 questions, 60 PASS_ASSISTANT_VISUAL_QA.
- 60/60 canonical question IDs locate unique manifest records.
- 60/60 `asset` == manifest `output`; 60/60 `assetSha256` == manifest `sha256`.
- 0 existing `qaStatus=PASS` among this batch. No duplicates counted.
- Important: SHA **string** comparison is complete; actual WebP bytes and original source bytes have **not yet** been rehashed in this Session. Do not promote to PASS on this metadata-only check.
- Current authoritative manifest: 73 PASS, 132 DRAFT; conditional after actual hash verification and apply script: 133 PASS, 72 remaining, not yet an achieved state.
- `questionVerified` and `answerVerified` must remain false.

## Blocking issues
1. `115-09-2-22`: `webp-v2/09-2/115-09-2-22.webp`, SHA `bec66d6e605d661e8d619905372a6fedbee12deb60b236ae696134ebc83c8652`, contains neighboring Q23–24 shared material per B2 historical failure. Current manifest correctly remains DRAFT. No verified v6 replacement found in the current manifest. Do not mark PASS until new version is present, pixel-checked, and SHA-verified.
2. `115-09-2-SHARED-49-50`: not in current manifest; only 19 shared material records currently, vs required 20. Do not claim this shared table has been shipped.
3. Run 39740772682: full assets workflow failed final check `AssertionError: 115-00-E-07` in PASS evidence/hash validation, not crop/OCR/SQLite setup. Latest committed manifest now has Q07 as DRAFT. That alone is not proof the workflow regeneration passes. Reproduce and investigate actual rebuilt evidence before changing asserts.
4. Latest successful run 39747821993 belongs to `tcte-data-audit.yml` (data quality), **not** the full 115 assets workflow.
5. Source branch is ahead 67 / behind 4 vs main. Do not force-push or merge.

## Verification boundaries
This report records GitHub connector inspection only. It does not assert actual WebP visual comparison, source image byte digest, SQLite re-run, workflow repair, or independent official answer verification. Current existing 205 images and 73 PASS remain unchanged. Main, platform UI, student records and LIVE untouched.

## Next executable checks
- Rehash B2's 60 actual WebPs and source WebPs on the same branch; invoke the existing `scripts/apply_115_visual_qa.py` with real source files present.
- Generate a **new version** for accounting Q22 with no Q23/24 content; never overwrite original.
- Crop the official p011 shared exchange/production table for economics Q49–50; add both links, source/crop/output hashes, and separate visual QA.
- Re-run full `115-data-assets.yml`, diagnose Q07 if still reproducible, and update inventory/validation/SQLite from actual successful run.
- Continue remaining 72 or more pending items based on actual `qaStatus` after successful replay, never estimated totals.
