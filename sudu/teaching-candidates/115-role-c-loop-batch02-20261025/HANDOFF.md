# 115 Role C / Issue 36 – bounded five NEW teaching lessons, no release

## Task lease / base
- taskId `C-115-NEW-FIVE-20261025-02`; role C author; claim GitHub issue comment https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393644385; authoritative GitHub claimedAt `2026-10-25T04:54:20Z`.
- Branch `teaching/115-role-c-loop-batch02-20261025`, base PR41 exact `3356e53c94c1ac0aae9f5aeb2b325b66698bf8a5`; master source PR35 `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`.
- Source JSON Git blob `216bc43d57501bc1c3e5842b48413a8967456cda`, manifest Git blob `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`; do NOT misreport as independently certified PDF.
- New lessons **115-00-C-06**, **115-00-E-29**, **115-00-E-39/40/41** were absent from fixed 128 historical teaching JSON filenames; this batch adds actual four A/B/C/D high-school + elementary justifications, conceptual steps, bold/highlights, mnemonic, applicable vocabulary IPA, 初級/中級/高級 graded synonym/antonym *with contextual limits*, English+Chinese separately sourced news learning examples with ACTUAL bold surface form. No numeric exam calculation; `examCalculation=null` so V4 hides it.
- Source image paths, SHA256 and source revisions are in batch.json and each lesson; no original WebP/PDF/OCR modified and this author did NOT re-open/re-hash original image bytes in this round. The exact original question/options came from frozen PR35 source JSON. Known answer candidates were read beforehand; **NOT blind**.

## Deliberate fail-closed source blockers
1. All five individual crop manifest entries are `PASS` as historical assistant image QA candidates, **NOT** independent authorized image review or current source admission.
2. C06: manifest image `PASS` but `questions.json assets.visualQa` still says `PENDING_INDIVIDUAL_VISUAL_QA`; and legacy source `answerVerified=true` while `questionVerified=false`. Wrapper mirrors real upstream flags and explicitly keeps formalSourceAdmission=false. Role A must reconcile the factual difference, not force-match by flipping a flag.
3. E29 shared `115-00-E-SHARED-29-30` WebP SHA `e932d3fc246b55604cabd6fa1716d0fa6f8f67d658ed6a16c6d88f91bfdb49b6` is `PENDING_INDIVIDUAL_VISUAL_QA`.
4. E39, E40, E41 shared `115-00-E-SHARED-39-42` WebP SHA `5cbbcf60882e7a3eef6ad4304c68a20cfc5c5930e06722ae0c20faf36138640b` also pending individual review. E42 **not** included because legacy answer D was contaminated by next-page material.
5. E29 and E39–41 `answerVerified=false`, `questionVerified=false` in source record. Official final answer/notice must be directly independently checked; textbook edition/page unresolved.
6. Teacher content authored by GPT-6 role C (post-answer); requires **real distinct authorized human teacher** review + signed and GitHub APPROVED event, not C or another AI impersonating human. Governance `requireHumanTeacher=true`, `authorizedReviewers={}` unchanged. D must test exact matching digest, 8 viewport ×2 theme seven-subject V4; E then independently audits; master alone can integrate incrementally.

## Externally checked credible example sources (teaching paraphrases, not quotes)
- E29 UNICEF Asia Pacific, 2025-06-05, https://www.unicef.org/asia-pacific/place-for-parents/netiquettes-your-child (family privacy and online safety, **families**).
- E39/E40 Taiwan Ministry of Economic Affairs 2026-09-02 SEMICON news https://mnscdn.moea.gov.tw/MNS/Populace/news/News.aspx?kind=1&menu_id=40&news_id=123853 (advanced packaging / AI data-center power / local supply chain, **progress**, **important** both are English authored paraphrases).
- E41 Taiwan MOEA English 2026-09-14 Semicon Network Summit https://mnscdn.moea.gov.tw/Mns/english/news/News.aspx?kind=6&menu_id=176&news_id=123966 (AI opportunities and challenges, **take advantage of** written pedagogically, NOT verbatim).
- All four English examples deliberately mark a literal **highlighted surface form** present in the example and preserve a Chinese translation; context-derived paraphrases are distinct from the original reporting text.

## Future coordination
Send source revisions and WebP/teaching digests to role A (source and shared material QA), E + genuine independent teacher (content review), D (V4 UI); let master receive this stacked Draft PR only. No main, no Pages deploy, no PASS, no READY, no LIVE.
