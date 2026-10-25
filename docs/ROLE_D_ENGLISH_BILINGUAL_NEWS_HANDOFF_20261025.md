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

These are Role-B candidate digests, **not** published/approved lesson digests or an independent AI reviewer receipt. The source PDF, image and structured OCR are checked against real PR #35 files in the test; the news English/Chinese sentences and English highlight words come directly from the actual candidate enrichment records, not fabricated text.

## Verification contract
- `tests/sudu_role_d_english_bilingual_news.cjs`: uses the actual three 114 English candidate JSON records, three official-source OCR records, prior 114 evidence, exact local source image WebP bytes (SHA256), and complete four original option strings. It checks candidate answer and source revision agreement, checks teaching digest, then opens original V4 Demo to test **only the annual-news formatter/guide component** without inserting any candidate into `QUESTIONS` or `approved/`.
- Across 360×800, 375×812, 390×844, 412×915, 430×932, 768×1024, 1024×768 and 1440×900 (both themes), the component checks true English and Chinese text, actual highlight substring, no Demo fallback, no duplicate news heading, browser exceptions, no overflow/clipped bilingual span. Emits 48 browser screenshots and JSON evidence with HEAD, main base, HTML/runtime SHA256, all source revisions, WebP SHA, teaching digest, run ID.
- The workflow `.github/workflows/sudu-role-d-english-news-gate.yml` pins checkout to the actual PR HEAD, builds existing Pages assets locally without deploying, uploads results, and never sets PASS/READY flags.
- This is **component regression, not a full original-question UI QA certificate**. Until actual admitted questions, real four-option answer interactions, source table/figures, separate-author AI content review (Role E), the full 8×2 test matrix, and same-SHA LIVE validation pass, all 114 English 07–09 remain BLOCKED.
  
## Next step (for master)
Independently inspect exact final PR-head Chromium run and report/artifact, cherry-pick only this HTML hunk after conflict checking against #35/other D PRs, then rerun all affected original Demo and eventual approved English per-question 8×2 checks. Do not merge or publish based solely on this isolated renderer result.


## Continued Issue #36 digest-bound rerun after B's real author patch
- taskId: `D-ENGLISH-NEW-DIGEST-UI-20261025-02` (same isolated Draft PR #40; separate Issue36 file lease).
- Reviewer E independently identified that original PR35 E08/E09 teaching digests describe a `teaching=null` candidate and are now superseded by Role B PR31 exact immutable commit `852c6613161f39314d87476b4e201cfe1811f783`.
- We do **NOT** overwrite, copy, or independently approve any B authored JSON. The read-only CI checks out that commit separately under `_role_b_current/`, verifies its exact Git HEAD, re-reads the actual 114 English candidate, original 4 option teaching JSON and WebP. It checks the original teaching Git Blob SHA using a true NUL byte, canonically hashes the original teacher/elementary/option reasons and applies only B's authored reason overrides, then independently recomputes `composedTeachingSha256` with the exact source revision and original WebP SHA. Missing/changed/incorrect digest fails closed.
- Updated expected current candidate digest: `114-00-E-07=f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b`; `114-00-E-08=6dd7125dddf83293dc52a0fcbc35b113918f92f9b2fca9e6b0dc0ca06442d5b1`; `114-00-E-09=45b33a02da4059fc7efc2cae7d9c7914732d53e967c195d004cc879e212fa584`. All three remain `BLOCKED` by official source/answer admission, separate-author AI content review, full-question 8×2 and exact-SHA LIVE requirements; human teacher/signature is explicitly NOT required.
- After this test rewrite, the earlier read-only component CI `40163449898` at SHA `7463792e2f39702940ec498d04ab112bdf357a70` is **historical evidence for old source only**; it cannot be reused as the exact current PR head CI. The current amended SHA must be independently checked in GitHub Actions and its 48 screenshots archived before accepting even candidate-component PASS.

## 2026-10-25 owner policy supersession — Role D scope only

- Task `D-NO-HUMAN-TEACHER-POLICY-ALIGN-20261025-03` was claimed in Issue #36 comment `6393705081`. The **user explicitly removed** educator identity/certification, approved teacher roster, teacher Ed25519 signature, and actual human teacher GitHub APPROVED as lesson-release prerequisites. A high-school teacher is the **teaching perspective**, not a human identity; each A–D option keeps clear reasoning plus elementary-level language.
- **Role D MUST NOT block on missing human teacher.** Candidate lessons continue to require verified original question/images/option source revision, official final answer and applicable correction notice, accurate four-option explanations, calculation steps or automatic hidden no-calculation block, actual highlight substrings, separate-author traceable AI review and exact teaching/image SHA. The sole MASTER handles publisher/governance/ledger migration and LIVE checks; Role D cannot self-approve this work.
- In this isolated test, a missing, null or false legacy `review.humanTeacherVerified` marker is **allowed** (no human-credential requirement). A claimed `true` / `"true"` is rejected as a false assertion of *actual human verification*, **not** because a human signature is required. `review.studentReleaseApproved` and `review.formalReady` remain `false` for these unresolved B author candidates; this is independent of teacher identity.
- New owner policy is already at the top of Issue #36, but PR #30 and PR #35 production publisher/policy still include historical requirements; PR #46 is a candidate-only, inactive AI receipt contract. Role D does **not** directly change policy, register reviewers or deploy. The controller must check actual post-migration commit/CI before upgrading any student-ready record.
- Previous 3×8×2 source-bound bilingual component evidence remains valid only for its exact old head/digest. Rerunning current PR head after this policy-scoped D test change is required before marking even component PASS on the new SHA. Full original-question V4 remains separately pending.
