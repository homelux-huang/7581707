# ROLE A MB25 original radius / native source admission — 2026-11-14

Task `A-115-MB25-NATIVE-SOURCE-ADMISSION-20261114-01`; original QA baseline `75fe4d015c15b9b0c30b5ac3f765cd575c99474b`.
Original frozen PR157 stage Blob `cf1ef0d369e3aced81886a518b47cdeddd4ad175` reused without edits.
Original page8 and Q25 single WebP were opened and visually compared this task:
radius √2, full figure(7), all four options (-59,-16,-10,10), no page footer in crop.
Published official answer image Q25 C was opened and read. This is source review,
not independent E teaching QA or an answer-hidden first solve.

Pixel comparison of the original page crop (90,1102,1310,1557) and existing
1220x455 original v2 WebP has zero RGB differences. Native G1/G2/G3 passed with
protected-main publisher Blob64db5dd620dec230287ff0ea92a64b6e181e45a9.
Preserved raw OCR and original image bytes; corrected canonical radius and D footer
text only using the frozen original G2. Formula verifies h=4,a=-14,h+a=-10 (C).

- Source revision: `8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f`
- Original WebP SHA256: `92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896`
- G2 raw SHA256: `eca8ece0babeae6886297dca98bd58ace45018cb289f925f44f3d9c44766a464`
- G3 raw SHA256: `2179203705d3a089a1d43e3b4e8beb73eb3dffff6ce0a43e3c16149cf6e5a125`
- Bank SHA256: `79aebbee28f83d31fa6d99ecce186973b0f4157284ba664a8072d250dca51c17`
- DB SHA256: `f1f4e42d648ccbdb0bf897b5f24eba961490468f9aff2f4333e8b3e9533be9b3`

Actual local tests: five meaningful source acceptance/tamper/cross-QID/no-release
checks PASS. Both114/115 have205 unique JSON/SQLite/manifest IDs and payload/hash
parity;115 all14 projected columns pass. Other204 complete SQL tuples and canonical
objects, schema/shared-material rows and manifest bytes unchanged, including the
newly admitted MB24 and immutable C MB21/22 issuers. Git diff check PASS.
Historical MB25 frozen tests only run with dedicated MB25_FROZEN_SOURCE_ADMISSION=1;
constant current-state integrity remains separately enforced. Exact remote CI pending.

No C teaching modification, E receipt/trust registration, G6 first-answer claim,
formal D emitted16/16, approved dataset or Pages modification. integrationReady=false,
formalETrust=false,formalDRealEmitter16=false,studentReady=false,newLive=false.
MASTER must review exact-head CI for QA-only merge. C may then freeze existing
same-revision MB24/25 author teaching without rewriting it; real independent E
provenance/receipt, blind solve, formal native emitter and D/Pages remain gates.
