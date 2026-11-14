# 115 MB24 source-only admission — 2026-11-14

Task `A-115-MB24-NATIVE-SOURCE-ADMISSION-20261114-01`; baseline official QA
`4e365a75ed98e73223987d81041693a476196881`. This is source admission only,
not an authenticated ROLE E receipt, teaching approval, UI result or student release.

Original PR157 source stage is reused byte-identically (Blob
`88faf4ee767b20c15db603e91aa250bc59eba84c`). Original v2 image and page 8
crop match with zero RGB pixel difference. Full original fractions and A–D replace
broken extracted text; raw OCR and original images remain intact. Official answer C
and the existing Math B no-objection record remain SHA/Blob-bound.

- Source revision: `9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267`.
- Original image SHA256: `c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb`.
- Native G2 raw SHA256: `1caa3da4d5d6ce523f371709f944edaaacc2e5e2abf1240a545a385bfe1743ba`.
- Native G3 raw SHA256: `73ec23f02bd01ca625aca64b25641a4e46d224018d34ae6040d62eeaa2225ea4`.
- Bank SHA256: `7480aaa332a26aff785a94d80acd21d8137a05c16cf332d2aa9ec04ad48e4253`.
- SQLite SHA256: `30f0cb04ae821afd578a9a681b8c69d69613bbf9e20eca8c0add14b4440c0204`.

Local verification: exact protected-main publisher Blob
`64db5dd620dec230287ff0ea92a64b6e181e45a9`, native G1/G2/G3 positive checks,
source/official/image/notice/cross-QID/false-release negatives, five source tests PASS.
205 JSON/14-column SQLite full payload/hash/projection parity PASS; only MB24 complete
tuple changed; all other 204 tuples and canonical objects, database schema/shared rows,
original full manifest and the previous denormalized projection repair are preserved.
`git diff --check` PASS. GitHub CI is pending until the branch is uploaded and run.

The five historical snapshot tests require `MB24_FROZEN_SOURCE_ADMISSION=1`, set
only in the dedicated MB24 source workflow. Ordinary global unittest discovery
skips them so a later valid MB25 admission cannot be compared against MB24's old
204-unchanged snapshot. Current QA's ordinary 205-row/14-column integrity workflow
continues to check the cumulative database without this historical restriction.

MASTER must independently review and verify exact-head CI before a QA-only merge.
MB25 remains unchanged and needs a separate source admission after this task.
E11/MB21/MB22/MB24 still need genuine independent author/reviewer provenance and
trusted exact-SHA receipt. Formal D emitter 16/16, publisher admission and Pages
same-SHA validation remain outstanding. `studentReady=false`, `newLive=false`.
