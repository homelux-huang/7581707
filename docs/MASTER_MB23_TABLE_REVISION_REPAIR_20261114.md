# MASTER / 7581707 | Original MB23 2×3 table-aware publisher QREV | 2026-11-14

**Task:** MASTER-MB23-TABLE-REVISION-PUBLISHER-20261114-01
**Issue #36 CLAIM:** https://github.com/homelux-huang/7581707/issues/36#issuecomment-6880437447
**Protected main original base:** 0bc2b05ada43ef02983d56fc45ec3448189a318b
**Actual source-only QA branch read-only SHA:** f9a6bc84531b5a6a8b5d57cde3828323e500cbbc
**Scope:** Correct one real producer-consumer source-revision contract mismatch without changing source G2/G3/teacher bytes, protected trusted V1, actual student READY or LIVE.

## The real bug (frozen, reproducible)

Original QA A source [PR185](https://github.com/homelux-huang/7581707/pull/185), C original author PR143 and final native G5 PR201 confirm 115-00-MB-23 original **table (二) has 3 columns × 2 data rows**. An original 115 MB23 source G2 revision is not the usual table-free \`SHA256(JSON(question,options,WebP))\`.

- Wrong **table-less** QREV emitted by protected original publisher: \`4dc7a376e0b9e5929a0a0df3e652ea0811d3b662ddce431eff4ebc539c859731\`
- Correct actually admitted **table-inclusive** A G2 QREV: \`9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4\`
- Exact original corrected \`SHA256(UTF8(JSON.stringify({question, options, table})))\`: \`3ae20c9b53eb5ba38ffa354cbda868806bb7716700548bbe88618e0104a89088\`.
- Original single-question WebP SHA256: \`2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51\`.
- Original published answer PDF SHA256 (document identity, not the option letter): \`d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95\`.
- Original source table evidence immutable Git Blob: \`0f63d6a5f91015dd2b146731c48dce08668c1fa2\`, path \`sudu/data/processed/115/review-evidence/115-00-MB-23-table-source-20261103.json\`.
- Original A source revision seed: \`ROLE_A_115_MB23_TABLE_G2_G3_SOURCE_EVIDENCE_V1\n{tableTextSha256}\n{singleWebpSha256}\n{officialAnswerPdfSha256}\`. SHA256 over exactly this UTF-8 text equals correct table-inclusive QREV.

The source original archive includes a page/image/table G1 and G2, official G3 B, the actual original C teaching SHA \`13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6\`, original WebP SHA and 205-row bank/SQLite. **Do not rewrite, recrop, strip table, or use 4dc7 old value**. Source proof must keep the original answer hidden until independent first solve. Computing QREV uses **PDF document SHA**, never the answer choice text.

## Precisely bounded publisher code change

- Existing protected-main \`scripts/sudu_verified_publish.py\`: add optional trusted read-only \`source: Path\` to \`text_revision(q,sha_webp,source=None)\`; the unchanged original legacy digest remains for questions without explicitly pinned original table overlay. If table-marked 115 MB23, read only the exact original QA evidence JSON and compare its RAW Git Blob, three headers/two rows, corrected original question/options, original table correction-overlay, SHA256 of corrected question/options/table, original WebP digest, official answer **PDF SHA** and original seed, then return the computed correct source revision. Any missing, stale, tampered, symlink or inconsistent evidence returns empty invalid revision (FAIL CLOSED), never falls back to table-less digest. No other table QIDs are allowed to self-authorize a new hash mode.
- Change the existing **two** calling sites \`apply_independently_certified_review\` and \`snapshot\` to pass the source root.
- NO changes to original stored QA source question, G2/G3, SQLite, WebP, manifest, original C teaching, E, D, trusted policy, approved, release governance, student LIVE.
- No change to the current five exact historical already-published student exceptions. This repair alone cannot create a new reviewed-student batch or bypass G6/E/G8.

## Meaningful exact-head tests

- New \`tests/test_sudu_mb23_table_revision_20261114.py\`: real QA source original raw GitBlob and seed/3x2 check; correct MB23 revision and \`source_proof=(True,True)\`; old wrong digest must be rejected.
- Tamper negatives: original source table rows, columns, question/options, published answer PDF SHA, WebP SHA, overlay source tables/digest/evidence path, source QREV, question ID and year, missing/symlink/changed source evidence. Every attempt must return invalid QREV; no fallback.
- Five OTHER 115 MB20/21/22/24/25 canonical source revisions must remain exact, plus 205 candidate bank/manifest identities unchanged.
- Dedicated Actions \`.github/workflows/master-mb23-table-revision-20261114.yml\` pins exact real QA SHA, executes true tests and the original native publisher staging operation into **runner /tmp only**, then checks \`114=0/205\`, \`115=5/205\`, exact original MB02/03/04/05/09 and no new MB23 admission. No uploaded artifacts, no Pages or main edits.

## Separate unsolved UI G8 dependency

D identified the real **FORMAL_G8 vs publisher approved-emit cycle**; this table-specific fix is an independent prerequisite, not a shortcut. [MASTER Draft PR202](https://github.com/homelux-huang/7581707/pull/202) has demonstrated six QID **TECHNICAL_PRECHECK_ONLY** outputs (no student admission) with MB23 intentional HOLD before this fix. Authentic original author Session and distinct E Session IDs remain UNVERIFIED; no trustworthy first-answer G6 raw provenance, V1 trusted registry receipt, actual fully SHA-bound verified student batch, formal D emitted 16/16, or protected main/Pages release exists.

**This is a Draft PR / source-contract code fix only**. Require independent security review, full negative tests, normal protected-main PR gate and final staged LIVE test before any merge. READY=false, LIVE unchanged.
