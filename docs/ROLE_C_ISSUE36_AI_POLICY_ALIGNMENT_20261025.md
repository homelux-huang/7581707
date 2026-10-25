# Role C | Issue #36 independent-AI review-policy metadata alignment | 2026-10-25

## Exact task lease and scope
TaskId: `C-115-AI-REVIEW-POLICY-METADATA-20261025-03`; role C = AI teaching AUTHOR. Claim: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393712683; authoritative GitHub claim UTC `2026-10-25T05:02:56Z`. Separate author-only branch `teaching/115-role-c-independent-ai-pending-20261025`, baseSHA `f454fbf9cdeae5a50303970151ae0551b64ece90`, stacking on C's existing PR45 and PR41. DO NOT write shared coordinator ledger, other author's files, publisher, governance, main or Pages.

## Binding authority (latest supersedes previous)
Issue36 top-level user amendment 2026-10-25: **professional high-school teaching voice is not a real teacher claim**. Human qualification/Ed25519 teacher/GitHub teacher APPROVED are not teaching prerequisites. The actual audit and publisher must be migrated by the MASTER (separate PR46 governance work), not C. A **distinct AI reviewer**, different from the lesson author, must perform an attributable and substantive review. Required contract: reviewer identity + exact questionId + official original answer/correction proof SHA, sourceTextRevision, original image SHA256, teaching digest + per-option dual-level rationale + calculations + news source/IPA when applicable, and specific review notes. Missing evidence, self-review, changed source or copied old UI certificate must reject a READY claim.

Role C edited only existing author-owned candidate wrappers, review metadata, batch **fileSha256** manifests, own local regression tests and handoff. Former human-only blockers were replaced with `DISTINCT_INDEPENDENT_AI_CONTENT_REVIEW_EVIDENCE_PENDING`. All review states PENDING, reviewer identity and official evidence SHA null; this is **not an independent review**. Teaching objects, `teachingCanonicalSha256`, actual source questions/options, source revisions, original image paths, official PDFs and image hashes are unchanged. No false PASS/approval/trusted reviewer inserted. `studentReleaseApproved=false`, `deploy=false` for all seven, new READY=0, LIVE=0.

## Seven exact review subjects and immutable source+teaching refs
| Question | Source revision | WebP SHA256 | Teaching digest |
|---|---|---|---|
| 115-00-E-03 | c7e7262a3d5283d547f1dda35f1070c21d432314069286b305265aad9fa8977e | 16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd | c7bce2469356f95e929b19d5275cd3ca1a4ff8f2c9f89cd858b61e5c8cdc3316 |
| 115-09-2-34 | 162c9a4f4d16d25e77a6c09034eb87f9a27b1b5775ac334274f6447c3c957cc8 | 5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02 | 968607d17fa6a9dfd8ca913f958e5afb9536e3f4dd57bbca1722b32707d19fe3 |
| 115-00-C-06 | d072001630c98baa5ce22cc4939fe01149cc96345e1c89960ee0efbc09f625ba | f031f108b2805bffd737479bb019a682439db5ef31bf1e8082b8a65c4942691c | c4ddbe70969b738bd0435d830bfafacd918a9dd2796a74a86c51c1e6106ccbb6 |
| 115-00-E-29 | 23952dc29ed2622029cce5b7a431e4c9209ca99c41f25fc7eea5b15af56f883d | 200722eaba0530fc8f3963cfe9c72e2749630de188ad538d5ce23200d949717d | 50ceae4c440af17b06d0ef31ac4bd7c83edca796fe153f26a0e2c339665912d6 |
| 115-00-E-39 | 9a098b1db2de04ecdf3af694a686e30a573ba4d63356dbf1dfe39e7ea230956a | 0e71395b101b6e255d48b3eea86e8a4a1086cafabab62104ade3474b32f11d3c | 7f98f96420a9304518172d206eafc1c88fd932e47b214f00212aef13d6b082ad |
| 115-00-E-40 | 1066b79c8271d1882e9f443609665de1dab0f6a0a49553349e1d65904091fb31 | afa2a88eb2574bae17aad8d4a16f662e889b906f024b8950e45439f12210fbef | 5816e15304cd0e7084c41347cc4a40a3d9afd995ed132848bfd717eeca53556b |
| 115-00-E-41 | b5b2282057f093845c8745986a9e034e1bdfb6e6df10c18ab8d445507a68f0fd | b10a8ba84292df22dc481107280522e8f8dc168ef0496f9af3f4bf71329740a4 | b46c697373efc8e2641b42c4c9df6e6eda14848faf8f2bd4f9f0aa94c2f20f6c |

The full wrapper file SHA256 changed because non-content review metadata changed. Exactly updated hashes are separately recorded and read-back checked in the two C-owned `batch.json` files. The author did not independently rehash the original WebP bytes or official PDF content.

## Remaining concrete blockers
- Source A: official PDF final answer/correction coverage and source text/image version admission per question. C06 legacy source q.assets.visualQa pending despite individual manifest PASS, and source questionVerified false though answerVerified true; **no status change by C**.
- Shared source images: 115-00-E-SHARED-29-30 and 115-00-E-SHARED-39-42 are still independent visual QA PENDING; current E29/E39-41 not release ready.
- Distinct AI author/reviewer: E or separate reviewer needs actual independent, SHA-bound substantive notes, not C author self-approval or fictional human account.
- Master: PR46 policy/publisher integration and fail-closed test alignment before publisher accepts any independent AI review; C candidate metadata alone is insufficient.
- D: V4 actual 35-demo subject-specific 8 viewport ×2 themes, same source and teaching digests, and no blank calculation box for conceptual questions.
- MASTER-only verified official gate, QA, CI, main merge, Pages and same-SHA LIVE check. No autonomous deployment by C.

## Test claims
Two existing C-only Python suites validate full-file & canonical teaching/source digests, four-option dual-level explanation, valid bilingual word-form highlight, content tampering negatives and shared image QA no-promotion. This branch extends their assertions to require distinct AI review PENDING and forbid author self-approval. CI PASS on this exact HEAD must be checked separately; passing unit tests never implies completed reviewer/official/image/UI gates.
