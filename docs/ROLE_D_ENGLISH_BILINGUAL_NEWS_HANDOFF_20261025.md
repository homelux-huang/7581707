# Role D — Annual English bilingual news renderer, exact-source scoped patch (2026-10-25)
  
## Control room and lease
- Issue #36 taskId: `D-ENGLISH-BILINGUAL-V4-20261025-01` (CLAIMED in GitHub comment 6393598820).
- Role: D (V4 front-end and browser presentation), not an independent auditor or teacher.
- Branch: `fix/role-d-114-english-bilingual-news-20261025`. Base: PR #35 `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`. Original main SHA `57d766e841235b937babf3fe10a8ff44606c7c41`.
- Authority: current PR #30 master command and unique question ledger; **do not add a second ledger**.
- Scope: minimal in-place fix to existing V4 HTML for source-bound Chinese news translations; new tests and read-only workflow. No changed original source, teacher lesson, answer, WebP, database, reviewer, approved data, publisher, runtime or Pages.
- Parallel D leases for source-image resolver and lazy WebP readiness cover `tests/sudu_role_d_per_question_browser.cjs` and its workflow. This patch does not touch those files.

## Reproduced exact defect and repair
- `formatStudyValue(q,'新聞時事例句', ...)` on formal-year `q.canonicalId` displayed only the English source and `mark.exam-highlight`; `guideEntries()` separately suppressed `新聞時事中文翻譯` if a news sentence was present.
- Thus when genuine annual English lessons were later admitted, their actual bilingual candidate `q.extra['新聞時事中文翻譯']` would vanish, even when present and reviewer-provided.
- The annual-English branch now embeds the exact translation in the **same original guide field** as the English sentence via `<span class="news-zh"><b>中文：</b>...</span>` and HTML-escapes it. When the translation is absent, it invents none. It never queries the Demo news by numeric ID for formal-year questions. Demo behavior and per-subject guide ordering remain unchanged.
- The existing independent `requireHumanTeacher=true` / empty authorized reviewer roster policy and every approved gating assert are unmodified.

## True source-bound candidates (NOT admitted)
  
| Question | Source revision SHA-256 | Raw WebP SHA-256 | Exact candidate teaching digest | Highlight |
| --- | --- | --- | --- | --- |
| `114-00-E-07` | `8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c` | `0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc` | `f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b` | automatically |
| `114-00-E-08` | `09a56002bd224815a9d413ad9a5db3565af0837e16c58ec031bd851f17d69b6c` | `5a9ebec3dbb4cacf3bbb2cd2f6121f69319d042e3c716f41fdbe96f30bfd9c85` | `7415aab85aa8b693ff430b63dde9ebe641652b985a577ee93854aa50493bb3f5` | stood out as |
| `114-00-E-09` | `0346c84990c84812b9705adcfab7bb6d51877dce1e07c7ba4cc3e74797583cdd` | `393dbdbfbd59220a18fd11d2c09d1b07cd9daf5816d32bbe91a6ec1a335c204b` | `d9af8ba1bc7f023f17b9a8f150cdb7a08f1b9163b4665de199cf0a96beca4952` | Apparently |

These are Role-B candidate digests, **not** final approved lesson digests or signed independent reviews. The source PDF, image and structured OCR are checked against real PR #35 files in the test; the news English/Chinese sentences and English highlight words come directly from the actual candidate enrichment records, not fabricated text.

## Verification contract
- `tests/sudu_role_d_english_bilingual_news.cjs`: uses the actual three 114 English candidate JSON records, three official-source OCR records, prior 114 evidence, exact local source image WebP bytes (SHA256), and complete four original option strings. It checks candidate answer and source revision agreement, checks teaching digest, then opens original V4 Demo to test **only the annual-news formatter/guide component** without inserting any candidate into `QUESTIONS` or `approved/`.
- Across 360×800, 375×812, 390×844, 412×915, 430×932, 768×1024, 1024×768 and 1440×900 (both themes), the component checks true English and Chinese text, actual highlight substring, no Demo fallback, no duplicate news heading, browser exceptions, no overflow/clipped bilingual span. Emits 48 browser screenshots and JSON evidence with HEAD, main base, HTML/runtime SHA256, all source revisions, WebP SHA, teaching digest, run ID.
- The workflow `.github/workflows/sudu-role-d-english-news-gate.yml` pins checkout to the actual PR HEAD, builds existing Pages assets locally without deploying, uploads results, and never sets PASS/READY flags.
- This is **component regression, not a full original-question UI QA certificate**. Until actual admitted questions, real four-option answer interactions, source table/figures, independent teacher gates, the full 8×2 test matrix, and same-SHA LIVE validation pass, all 114 English 07–09 remain BLOCKED.
  
## Next step (for master)
Independently inspect exact final PR-head Chromium run and report/artifact, cherry-pick only this HTML hunk after conflict checking against #35/other D PRs, then rerun all affected original Demo and eventual approved English per-question 8×2 checks. Do not merge or publish based solely on this isolated renderer result.
