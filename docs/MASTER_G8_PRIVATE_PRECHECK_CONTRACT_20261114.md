# MASTER | G8 cycle-safe private native technical precheck | 2026-11-14

**Task**: MASTER-G8-PRIVATE-NATIVE-PRECHECK-20261114-01  
**Role**: MASTER (publisher-contract owner)  
**Claim**: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6880273508  
**Protected main base SHA**: 0bc2b05ada43ef02983d56fc45ec3448189a318b  
**Pinned read-only official QA data SHA**: 7140fa078cb51dcceaa98a0a4b07bac1f5feb29f

## Problem and safe initial delivery

ROLE D's independently checked cycle analysis in PR #199 explains why the existing publisher wants a verified UI document before admitting a student row while the formal D runner accepts only genuinely publisher-emitted student rows. Neither an old 16-HOLD screenshot nor a synthetic trusted receipt is an acceptable positive solution.

This Draft PR **does not yet resolve the final authenticated G8 admission cycle**. It implements only a **private, reproducible, production-serializer technical precheck** that D can reuse to catch malformed V4-shaped data while genuine B/C/E/G6 evidence is still being collected. A separate, owner-reviewed two-stage **admission** bridge is required before FORMAL_G8 can be attempted. Never treat these previews as final publisher rows.

## Files and narrow permissions

- New scripts/sudu_g8_private_precheck_20261114.py
  - Imports actual protected-main scripts.sudu_verified_publish.public_question; never copies the production serializer by hand.
  - Reads QA branch data as inert JSON/WebP ONLY; never executes its branch scripts.
  - Requires correct 205 question IDs and 205 manifest IDs, native original source and official verification, correct notice, original WebP binary SHA and QA evidence, source QREV, original answer candidate agreement, real native OCR/official G2/G3 evidence and **original author G5 issuer** with canonical teaching digest and full A–D/math.
  - Creates one per-QID **TECHNICAL_PRECHECK_ONLY** record only outside the repository, under an OS temporary folder named sudu-private-g8-*, with mode 0700 directories / 0600 files and exclusive create. It **contains answer key material**; never publish, upload, commit or paste it into logs. Console output is metadata/hashes only.
  - Explicit flags: studentReleaseApproved=false, distinctAiReviewAuthorized=false, firstBlindProven=false, formalG8=false, pagesEligible=false. No trust or student release interface.
- New tests/test_sudu_g8_private_precheck_20261114.py
  - Mandatory negative cases: wrong year/QID/commit SHA, missing 205-source, non-temp/approved path, symlink, re-write attempt, missing A–D or false mathematics, false admission label.
- New .github/workflows/master-private-g8-precheck-20261114.yml
  - **permissions: contents: read**, fixed QA SHA, pinned original publisher GitBlob.
  - Runs honest unit negatives, then tests only **114 E11, 115 MB21, 115 MB22** against authentic QA images/native G2/G3/G5 in a runner-temp private directory.
  - NO artifact upload, NO Pages, NO main writes, NO OpenAI API, NO secrets, NO trusted receipt.
- This coordination document.

All original 114/115 bank JSON, SQLite, inventory, manifest, WebP, teacher content, E evidence, V4, main publisher, protected review policy, approved students, Pages and original five exception records remain untouched.

## Currently frozen source/author pins (to be verified byte-for-byte by CI)

| QID | official | QREV | original WebP SHA256 | teaching SHA256 |
|---|---|---|---|---|
| 114-00-E-11 | A | 646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036 | ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0 | ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb |
| 115-00-MB-21 | A | 817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9 | b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693 | 4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4 |
| 115-00-MB-22 | B | 7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17 | 3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55 | 5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600 |

## Explicit remaining gap before a real new student LIVE

1. Distinct authenticated original B/C-vs-E ChatGPT Session provenance: **UNVERIFIED**. ROLE E PR200 only CONTENT notes (already QA merged), no V1 authorization.
2. Genuine FIRST answer-hidden G6 model response, original raw bytes, provider/session/timestamp and independent evidence: **UNVERIFIED**. E12 separate one-shot remains OWNER_CONFIG_HOLD.
3. Protected main V1 trustedAiReviewReceipts currently empty; no 114 or new 115 QID has a registered legitimate E receipt.
4. Owner-reviewed typed G1-G7 **authorization** + private official pre-G8 batch and UI preflight witness + real final staging-emitter two-phase bridge **NOT YET IMPLEMENTED**. This new PRIVATE technical precheck is *not* that bridge.
5. ROLE D publisher-emitted FORMAL 8 viewport sizes × Light/Dark screenshots, 16/16 per new QID, still **PENDING**. D PR #167 is Draft, unmerged to main.
6. Separate protected PR + same-SHA GitHub Pages VERIFY_LIVE, 114 now 0/205 and 115 original five 5/205.

## STOP conditions and RETURN

If actual QA source or native issuer fails, script emits TECHNICAL_PRECHECK_HOLD with no output. Do not repair source or lessons under this MASTER code lease; report the precise QID to A/C. CI success from this PR is ONLY a private serializer compatibility check, not G8, E, G6, READY, or LIVE.

Once CI green and security review, stage a **separate** bounded publisher-contract PR that defines the typed authenticated two-stage handoff and preserves existing fail-closed G0-G10 and historical five. No synthetic or downgraded trust.
