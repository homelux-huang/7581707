# ROLE D | 114 E12 真正 V4 8x2 前置 gate | 2026-11-07

## Scope and governance

Task ID: D-114-E12-REAL-EMITTER-20261107-01. New exclusive [Issue #36 CLAIM #6712543705](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6712543705), continuing existing D-only [Draft PR #167](https://github.com/homelux-huang/7581707/pull/167); earlier D [RETURN #6689165590](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6689165590) released prior lease.

The only five D-owned changes are:
- tests/sudu_role_d_emitted_only_8x2_20261106.cjs
- tests/sudu_role_d_e12_trusted_receipt_negatives_20261107.cjs
- tests/sudu_role_d_114_e12_unreleased_chromium_20261107.cjs
- .github/workflows/role-d-emitted-only-preflight-20261106.yml
- docs/ROLE_D_EMITTED_ONLY_PREFLIGHT_20261106.md

No existing V4 HTML/runtime, demo, MASTER publisher, original 205 JSON/SQLite, original WebP, B/C author lesson, ROLE E review, protected review policy, approved, main or Pages modification. No release decision.

## Actual upstream source status

Protected main on 2026-11-07: 5546a603abfe0af2e62c0e5f63f775be0bfb24cf.
Main approved year 114: 0/205; year 115: 5/205 historic MB02/03/04/05/09. Trusted AI reviewer registry is EMPTY. Current reviewMode=DISTINCT_AI_CONTENT_RECEIPT_V1 and requireHumanTeacher=false.

Current authoritative QA importer source HEAD at audit: 682e02e1084325a0422c117d90b70451fdd9ea22 after MERGED PR168 canonical/source 205 SQLite, PR169 QA importer bridge, PR171 original visual receipt, PR175 original official G3 issuer, PR176 original answer-hidden OCR G2 issuer.

For 114-00-E-12:
- Original source revision: 0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec
- Original single-question WebP SHA256: 99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60
- Original official answer: C (114 English correction names E26 only)
- Official G2 issuer file SHA256: 8130e621a4328d006dab880fe62e9115899049a3fb4751020a0c1570c49ea2fc
- Official G3 issuer file SHA256: 63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12
- Original immutable ROLE B PR107 author lesson HEAD: 57d969888c57fdcd2b16c933e92c7a2c9eebb3a5

IMPORTANT digest difference: Current official Python publisher compares testedTeachingDigest to SHA256 of the canonical teaching CONTENT, which is c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a. The earlier B composedTeachingSha256 fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4 also hashes source/image/enrichment and IS NOT the formal UIQA testedTeachingDigest. This exact difference is verified on real PR107 JSON by Actions; the historical composed digest is separately retained for audit but never substituted for canonical content SHA. A real IPA change to the B author file requires refreezing the impacted digest.

ROLE E [PR #173](https://github.com/homelux-huang/7581707/pull/173) and [RETURN #6710069163](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6710069163): authentic substantive four-option review completed, but FORMAL TRUST HOLD because distinct Session provenance, genuine blind solver, publisher teaching evidence and protected trusted registry are not validated. No synthetic approval or forged session IDs.

## Verified new test contract

1. The precheck reads real approved year JSON and local review policy; with SUDU_D_REQUIRE_PROTECTED_ROOT=1, it fetches origin/main read-only and rejects any candidate source/PR policy blob different from the protected-main policy GitBlob. Formal mode also requires an exact SUDU_D_PROTECTED_MAIN_SHA pin.
2. A truthy trustedAiReviewReceipts[QID] is NOT sufficient. All required reviewer evidence fields must be structured: sourceRevision, original WebP SHA, canonical teaching SHA, official G3 SHA, evidence GitBlob, reviewer notes hash, actual E task and Issue36 RETURN, distinct author/reviewer provenance, authenticated GitHub reviewer metadata. The independent official publisher still performs its stronger actual GitHub trust verification. D-only structural validation is not certification.
3. Negative test uses actual immutable B PR107 question author JSON and recomputes canonical and composed SHAs; 24 in-memory invalid/stale/malicious trusted receipt fixtures must all be rejected. No real approved or protected trust files are modified.
4. Real HOLD browser regression uses actual unchanged V4, python scripts/build.py and local HTTP server; it performs genuine Chromium on 8 viewports (360x800,375x812,390x844,412x915,430x932,768x1024,1024x768,1440x900) times light/dark. No HTTP page.route interception, no mock or provisional approved E12. Each case checks year 114 image-only readonly state, answer/guide/calculation areas absent, current preview image decode and preview QID matching, no visible E12 answer, no horizontal scrolling, JS/HTTP errors, and saves HOLD-NOT-UIQA screenshot SHA256. Passing 16 such HOLD negatives is NOT a formal E12 UIQA 16/16 pass.
5. Future formal runner additionally checks current original source/official answer/teaching SHA and protected E registry plus actual publisher-emitted approved QID; only then runs true 8x2 browser and captures screenshot hashes. Historical composed source/enrichment proof is optional in the formal bundle, since the official publisher requires canonical teaching digest only.

## Exact future formal run, after true upstream admission

First fetch origin/main and preserve the exact protected SHA:
  git fetch --no-tags --depth=1 origin +refs/heads/main:refs/remotes/origin/main

Then with existing non-public publisher-emitted student build running at the supplied HTTP server, set:
  SUDU_D_MODE=formal
  SUDU_D_QID=114-00-E-12
  SUDU_D_EXPECT_SHA=(exact current git HEAD)
  SUDU_D_PROTECTED_MAIN_SHA=(actual refs/remotes/origin/main SHA)
  SUDU_D_FORMAL_EVIDENCE_PATH=(real SHA-pinned E12 issuer evidence JSON)
  SUDU_D_FORMAL_EVIDENCE_SHA256=(actual real evidence bytes SHA256)
  SUDU_D_SITE=(real student emitter HTTP root)

Execute node tests/sudu_role_d_emitted_only_8x2_20261106.cjs. No synthetic approval, page.route or QA-only receipt. D may RETURN true 16/16 PASS only with all screenshots/CI at the same source/text/author SHA. MASTER alone decides protected release and same-SHA Pages verify_live.

**Critical publisher dependency requiring MASTER:** Existing Python apply_independently_certified_review() requires an UI receipt before emitting the new approved E12, but real D formal UIQA expects an emitted E12. MASTER must define a safe, isolated non-public candidate / two-phase attestation route without main/approved mutation or bypassing final G0-G10. D cannot manufacture an approved E12 to break this circular dependency.

## Next owners

ROLE B: PR107 IPA and real author-provenance; genuinely independent blind solver if missing.
ROLE E: exact current teacher content SHA, actual separate E review identity and genuine Issue36 RETURN with official/bindings.
MASTER: source overlay OCR/official/blind/teaching/UI evidence and accepted trusted main receipt; non-public candidate emitter, no final bypass.
ROLE D: when true source/E publisher emitted same SHA, run real Chromium 16/16; otherwise RETURN HOLD.
MASTER: protected one-Q release PR/CI and Pages verify_live, then E11, 115 MB21/22/23.

Current state: D guard code + actual Chromium negative HOLD tests complete; E12 FORMAL_UIQA_HOLD; NEW READY=0, NEW LIVE=0.


## 2026-11-07 B/E evidence refresh after original precheck

- ROLE B E12 true [RETURN #6712537831](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6712537831) verified Cambridge US full-phrase water bottle IPA including unusual secondary stress/space exactly matches immutable PR107 lesson. No B edit and no SHA reset. The prior IPA concern is **resolved**, not a publication blocker. Author ChatGPT Session provenance remains unverified.
- ROLE E [RETURN #6712572797](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6712572797) and [exact-head CI addendum #6712592139](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6712592139) independently re-verified real G2/G3 bytes and withdrew the erroneous IPA concern. PR173 head ee9ced6c916427a9dea283d475fa875970110e99. Distinct genuine Session provenance, honest blinded solve, issuer teaching document, protected E receipt, and formal D emitted 16/16 remain HOLD.
- B next-year [E11 frozen lesson RETURN #6712547567](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6712547567) gives **actual canonical teaching SHA** ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb, while historical composed SHA remains 3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee. D pin now stores these separately and the negative suite verifies both against original B PR107 source bytes, without pretending E11's canonical source is approved.
