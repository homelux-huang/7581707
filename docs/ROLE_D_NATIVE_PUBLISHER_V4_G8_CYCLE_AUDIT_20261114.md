# ROLE D | Native Publisher / V4 G8 cycle audit and execution contract | 2026-11-14

Task: `D-114E11-115MB21-22-EMITTED-V4-GATE-20261114-01`

## Immutable observations (not a formal admission)

- Protected main HEAD: `0bc2b05ada43ef02983d56fc45ec3448189a318b`.
- Official QA source HEAD checked: `333de134181dc7bb923560de5dd26524e4c0f5bf`.
- Main publisher Git Blob: `64db5dd620dec230287ff0ea92a64b6e181e45a9`.
- Main V4 HTML Git Blob: `3021bcb7846c80f74090b3c3c358c734c5a374f8`.
- Main runtime Git Blob: `6e83938eb4bc4f23e1417742f87a3fc6681e0616`.
- Protected policy Git Blob: `c77ee2ec8ca1381388fbbbe6bd36e679750678eb`, `trustedAiReviewReceipts={}`.
- Existing main student rows: 114=0, 115=5 historic MB02/03/04/05/09. NO NEW READY/LIVE.
- D child PR #199 exact tested HEAD `4c648e5583f5bb4717a117d39211dd21f779e0cc`: real Actions run https://github.com/homelux-huang/7581707/actions/runs/43612428780 COMPLETED SUCCESS. Jobs `132500149552` fail-closed protected-policy 6-QID preflight, and `132500149747` E12 real Chromium unreleased 8x2 *negative* test both SUCCESS. Artifacts `14120369262` (emitter formal HOLD) and `14120532624` (16 E12 HOLD screenshots). NO FORMAL G8 executed.

## Reproducible publisher/G8 dependency cycle

Current `scripts/sudu_verified_publish.py`:
- `teaching_complete()`, lines 218-222, requires `uiQaStatus == PASS` and `studentReleaseApproved is True` before release.
- `apply_independently_certified_review()`, lines 531-635, requires a SHA-pinned UI evidence JSON from the five-document `STUDENT_QA_APPROVED` batch. It insists on `testedQuestionRevision`, canonical `testedTeachingDigest`, `browserSmokePassed`, `rwdPassed`, `verifiedYearQaMode` and actual CI URL, *in addition to distinct AI E*.
- `snapshot()`, lines 693-781, only after the preceding gates writes the student-approved data. V4 `sudu/verified-questions-runtime.js` fetches exclusively `data/approved/{year}.json`; candidate teaching/source JSON cannot be graded there.
- Existing ROLE D emitted-only formal runner demands actual publisher-emitted approved QID and protected E evidence, and correctly fails closed if absent.

As presently stated, **FORMAL_UI_PASS requires the emitted row, while admission requires prior UI PASS**. Never solve this using mocked trusted receipts, route interception, fake approved rows, self-set `studentReleaseApproved`, stale SHA, or changing original demo. A previous successful 8x2 HOLD screenshot run does not solve the dependency.

## Proposed safe owner-reviewed two-phase publisher contract

1. **Evidence admission phase (MASTER owner):** verify G1-G7 independently, exact source revision, original WebP SHA, final official answer, original B/C canonical G5 digest, actual distinct E content provenance/receipt under protected main, and legitimate answer-hidden first-solve. Missing any input => fail closed.
2. **Quarantined native PREVIEW EMIT phase (publisher-owner change only):** create a new *non-public* single-QID QA-only output using the *same production serializer/public-question shape and unchanged immutable content*, but never update `sudu/data/approved`, Pages, source bank, `studentReleaseApproved`, trusted policy, or official receipt. Require non-web-exposed artifact with machine-readable `PRE_G8_ONLY`, exact source/teaching/image/code SHA pins, PR/commit/job and expiration. This is *real production code shape*, but **NOT actual final approved emission** and **NOT FORMAL G8**.
3. **D browser preflight:** run 8 widths x 2 themes on isolated private preview with no route interception or edited student JSON; verify V4 renderer compatibility, official WebP bytes and full A-D, teacher/elementary, marks, formulas or noncalc card hidden, interaction, theme/RWD/error-free. Store screenshot and report SHA with explicit `PRE_G8_ONLY`.
4. **Owner independently review/pin final UI evidence** to the actual preflight SHA and current candidate; introduce explicit typed approval / UI evidence contract binding the preflight and immutable material, avoiding circular admission. Merely setting the previous UI PASS boolean does not constitute proof.
5. **Native strict final publisher:** run unchanged G1-G7, protected E V1 and exact revision/digest/asset plus owner-authorized UI-preflight receipt checks, then emit one genuinely admitted student QID to a safe staging output. Do not promote to Pages yet.
6. **D FORMAL G8:** run existing fail-closed emitted-only 8x2 runner against exact publisher staging artifact; bind page/runtime HTML Blob/SHA, release input commit, questionRevision, teachingDigest, original WebP SHA, tested publisher output SHA and screenshot SHA for all 16 runs. If formal fails, block deployment and invalidate approval; on pass, MASTER may separately assess protected PR/approved/Pages and same SHA LIVE verification. No direct main write.
7. **Contract integrity negative tests:** missing E/solve/UI preflight; stale teaching/image/revision/HTML/runtime; altered or synthetic preview; changed approval between preflight and final; wrong QID/year; missing screenshot/job; Pages promotion before formal; old five unchanged. All must reject.

**Owner decision needed:** The current publisher recognizes only UI evidence prior to admission; MASTER must own a bounded publisher-contract PR adding private two-stage candidate emission and typed UI-preflight-to-final binding. ROLE D should own only V4/harness and screenshot/test changes. Until then status is CONTRACT_CYCLE_HOLD.

## Fixed formal Chromium matrix

Widths/heights: `360x800`, `375x812`, `390x844`, `412x915`, `430x932`, `768x1024`, `1024x768`, `1440x900`; each Light and Dark => 16 contexts per QID.

Test exact QID, original 4 choices, official image sha bytes/decoding, question and option text, answer feedback and correct answer, four teacher/elementary explanations, highlight and typography, subject-specific math cards (math: formula, substitution, steps, units, reverse check; E11: zero calculation steps), horizontal overflow, mobile/touch/tablet, JS/HTTP errors, app origin, no network substitution, and demo preserved.

### Frozen candidate pins (not assertion of freshly rehashed raw WebP)

| QID | sourceRevision | original WebP SHA256 | canonical teachingDigest | expected answer |
| --- | --- | --- | --- | --- |
| 114-00-E-11 | 646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036 | ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0 | ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb | A |
| 115-00-MB-21 | 817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9 | b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693 | 4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4 | A |
| 115-00-MB-22 | 7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17 | 3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55 | 5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600 | B |

These pins must be revalidated against the source QA and original issuer bytes at execution time. Do not replace current originals with summarized values.

## WORK_EXECUTION_PROMPT (only if local Chromium/Actions unavailable)

Use **GitHub Work** only for actual browser/computer control missing from ordinary Chat mode. Repository `homelux-huang/7581707`; use current verified HEAD, not memory. Do not connect Sites. Read Issue #36 leases, D PR #167 and child PR #199, current protected main, official QA and protected E V1 registry. Check whether a real publisher-emitted single-QID artifact exists. If no E trust/G6 or no publisher emission, execute only fail-closed PRECHECK/HOLD, and file exact evidence; never label FORMAL. Use native `scripts/build.py`, `scripts/sudu_verified_publish.py`, `tests/sudu_role_d_emitted_only_8x2_20261106.cjs` and Playwright Chromium. Eligible QIDs E11, MB21, MB22, then MB20/23. When admitted, 8 widths x 2 themes, real approved bundle, authentic local HTTP server, no page.route()/synthetic route, screenshot SHA, source/image/teaching/HTML/runtime SHA, job+artifact and actual errors; do not modify bank, lessons, E/approved/trust/main/Pages. If cycle persists, stop at contract HOLD and request MASTER owner two-phase publisher PR. Return `QID/baseSHA/HEAD/sourceRevision/WebP_SHA/teachingDigest/HTML_SHA/runtime_SHA/16matrix/CI/job/artifacts/errors/status/nextOwner`.
