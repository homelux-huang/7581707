# Role A | 115-09-2-34 Official Source Evidence Receipt | 2026-10-25

This is a **source-evidence-only, NO RELEASE** handoff for Issue #36 task `A-115-ECON34-OFFICIAL-SOURCE-20261025-02`; based on PR35 exact `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`. **Do not merge direct to main or deploy.**

## Exact source and original file proofs
| Source object | Existing immutable evidence SHA |
|---|---|
| canonical ID | `115-09-2-34` |
| canonical text+four choices+WebP `scripts/sudu_verified_publish.py:text_revision` | `162c9a4f4d16d25e77a6c09034eb87f9a27b1b5775ac334274f6447c3c957cc8` |
| original single-question WebP SHA-256 | `5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02` |
| original page-8 WebP SHA-256 | `defcfedf7cbc0f117d0731854efee59da41547716b0a88805454d9972da92ee5` |
| official **question** PDF SHA-256 (recorded earlier, not newly downloaded) | `fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e` |
| official **final answer** PDF SHA-256 (recorded earlier, not newly downloaded) | `6a2aacc705eb06edaf59c7ab6abe594763822e595e396bc0c279eef37235b9bc` |
| official answer sheet rendered original page WebP SHA-256 | `60482dbb1ac147d23e57b113790a1c2867c798a56e67611c5aa58c096c3cce67` |
| 115 `09-2` correction/confirmation PDF SHA-256 | `b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133` |
| original AI visual transcription Git blob | `5cd52d374259e1d808d4b12973e49f90e1058384` |
| original official answer visual AI evidence Git blob | `ca8bbac18e2d39bfe0f0374ff40ce96ac961843f` |
| original official notice+final-answer QA candidate Git blob | `1df0e78c2e38036923d47f39e8e9bb02558523c1` |
| genuine pre-official-answer first-look blind record Git blob | `a7e2c64f397c51be3db8457659ac5976ceb8a7af` |

## Evidence handling and constraints
- These four documents existed in `qa/econ34-prekey-image-only-20261024`, but PR35 source integration did not include them. This branch restores their **original Git blob objects unchanged**, not newly authored OCR or newly created pre-key reasoning. Source `questions.json`, `question-bank.sqlite3`, raw OCR, WebP and manifest are **not changed**.
- Official answer candidate is **A**, recorded by earlier SHA-locked original answer-sheet AI visual check (not new human approval). The 115 `09-2` formal confirmation **names only 06, 28 and 44**, so Q34 has **no named correction**, not a whole-paper no-objection claim. A record of automatic PDF text-answer match alone never sets `answerVerified=true`.
- Original first-look solution captured before viewing the answer accidentally omitted the single character **「中」** from the question. The canonical source text retains **「寡占市場中僅存在兩間廠商」**. The old blind record remains original and never represented as a newly performed blind solve.
- CI verifies SHA-256 of real original single-question, page and official-answer WebP bytes; source digest; 205 JSON/SQLite per-row payload parity and integrity; actual publisher annual correction-scope `official_notice_scope_certified` positive and adversarial negative cases; Git blob identities and no-approval flags. Earlier official PDF SHAs are **recorded provenance** only unless physical PDF bytes are downloaded and rehashed by a separate task.

## Exact lesson consumer and release handoff
- Role C Draft PR #41 owns latest ECON34 teaching candidate: `teaching/115-role-c-loop-batch01-20261025` at `3356e53c94c1ac0aae9f5aeb2b325b66698bf8a5`, content digest `968607d17fa6a9dfd8ca913f958e5afb9536e3f4dd57bbca1722b32707d19fe3`; this task does not edit lesson, digest, UI, publisher or role E notes.
- Current Issue #36 **newer user policy** cancels mandatory real-teacher verification. Independent **different author AI** substantive source/teaching review remains necessary along with all correct content, calculation, original-image and exact-digest UI checks. Role A does not modify governance or assume the policy code is updated. Existing author-only records are not formal independent review.
- Formal SOURCE_QA for Q34 remains pending independent separate acceptance; candidate `answerVerified=false`, `questionVerified=false`, no new `integrationReady`, READY=0 / LIVE=0. PR35/base/main unmodified; need coordinator reconcile these original records, then teacher-style dual audience lesson review / exact UI and strict publish gates without any fake credentials.

All evidence paths are in `sudu/data/processed/115/review-evidence/`. One bounded source task only; no 410-candidate batch PASS.
