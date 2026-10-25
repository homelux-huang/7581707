# Role D — 114/115 V4 exact-source browser acceptance checkpoint (2026-10-25)

## Verified read boundary and ownership

- Only student HTML is sudu/v4-115-multisubject-review-demo.html. The seven-subject layout and behavior originate in the actual 35-question Demo, pinned in docs/ROLE_D_V4_DEMO_35_BASELINE_20261025.json.
- Inspected GitHub main at 57d766e841235b937babf3fe10a8ff44606c7c41, Draft PR #27 at cb215a771df74dec485774a4e74fd691fbb03e77 and PR #26 containing pending original MB23 source-table fix. The master command was located in Draft PR #30 at 27f13aef46588e0eacd9c50edddae90f982e0d86; it is NOT yet on main.
- This Role D branch is based on PR #27's exact HEAD and changes only test evidence, workflow, and this handoff/baseline; it does not rewrite HTML, runtime, official source, answer, teaching approvals, approved question files, publisher, Pages or user history.
- PR #26's original 2×3 MB23 semantic table is not silently copied into or overwritten by PR #27. Master must resolve #26 + #27 at file-level and then re-run tests against the resulting exact source/teaching bytes.

## Seven-subject provenance: counts in the unchanged branch input

Numbers below are counts *from this checkout's approved/ and approved/preview/ JSON files*. Preview is image-only, NOT ready to answer. There is no extrapolation from OCR, raw source, CI success or cached historical counts.

| 科目 | 114 approved | 114 WebP-only preview | 115 approved | 115 WebP-only preview |
|---|---:|---:|---:|---:|
| 國文 | 0 | 9 | 0 | 9 |
| 英文 | 0 | 0 | 0 | 28 |
| 數學 B | 0 | 0 | 5 | 25 |
| 商業概論 | 0 | 0 | 0 | 5 |
| 數位科技 | 0 | 0 | 0 | 7 |
| 會計學 | 0 | 0 | 0 | 21 |
| 經濟學 | 0 | 0 | 0 | 24 |

All unavailable year/subject combinations are recorded NOT_TESTABLE_NO_QUALIFIED_SOURCE rather than receiving a per-question PASS. PR #21 114 English 07–09 and PR #28 115 Math B20–25 are *candidates* outside current approved source. They cannot be copied to the playable runtime or counted in this test without accurate source digest, official final answer, independent review and admission.

## Automated real 8 × 2 acceptance (new files)

- tests/sudu_role_d_per_question_browser.cjs reads the existing V4 HTML#demoData (35 real Demo questions), actual approved/114.json, approved/115.json, actual image-only preview JSON, and WebP asset bytes. It never populates mock questions or sets approved flags.
- Each actual question is exercised with real Playwright browser mouse click at desktop widths and real touch tap for widths 360,375,390,412,430. The 768,1024,1440 widths use mouse. Both theme states are traversed using the site's actual theme control. A browser screenshot is written per question per dimension/theme to test-results/role-d.
- Checks: exactly matched original number, subject, source text, option A/B/C/D, WebP URL + SHA-256 of original local bytes *and* HTTP-served bytes, images decode/aspect, required shared materials, no horizontal overflow/text clipping; answer red/green styles, correct-option jump and four explanations; full no-duplicate calculations and actual highlighted substrings; subject-specific English ordering; original 35-Demo semantics; mistake-review preservation, yearly localStorage namespace and real viewport/browser exceptions.
- For answerable original 115 questions, the test independently constructs the teaching digest from the complete exact original lesson fields and compares it against the object actually loaded in the V4 JavaScript runtime. The report contains checkout SHA, main base SHA, HTML/runtime SHA-256, source-revision metadata, source file SHA-256, image SHA, per-question teaching digest, GitHub Actions run ID, viewport, theme, input type, screenshot file and result.
- New read-only workflow .github/workflows/sudu-role-d-per-question-ui-qa.yml uses a 21-entry year × subject matrix and pins actions/checkout to the PR head SHA (never the synthetic GitHub merge SHA). Missing qualified sources are explicitly not exerciseable; jobs do not deploy, change records, promote READY or merge.
- Failures produce failing CI with per-question screenshots and errors rather than a dummy PASS. All changes to HTML/runtime/teaching/source SHA invalidate previous results; re-run the exact matrix on the newly integrated HEAD.

## Current decision and next handoff

- At commit creation time this document is a TEST DESIGN + BASELINE checkpoint, not a signed proof that the matrix has completed. Inspect the exact PR-head Actions run, archived JSON and screenshots before crediting any cases.
- Only human-authorized distinct independent teacher review and other G0–G10 gates permit new student-ready content. The roster is currently empty. This role must never flip approval flags. A Playwright PASS, prior staging green check, or PR DRAFT cannot be treated as LIVE.
- Merge order and branch protection remain master/E decisions. E must verify source/image digest matches and evidence integrity; master integrates reviewed diffs, runs exact-SHA release checks and verifies public GitHub Pages separately.
