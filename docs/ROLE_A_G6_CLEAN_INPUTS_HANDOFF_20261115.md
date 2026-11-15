# 7581707 ROLE A — Original source / G6 answer-hidden operator handoff (2026-11-15)

This is **A source-only preparation, not a G6 run, independent ROLE E review, or student release**. Original G2/G3 are read-only. Source QA base: `fec4ff58fbe63170fb42b4c47ad76c08848e8ece`. Protected main: `ceda0a0248cb7dc99941758e9e16582e463516ca`.

## Deliverable
`scripts/role_a_g6_clean_input_pack_20261115.py` derives exactly **nine** independent QID folders from existing verified G2 and original WebP bytes. Each folder contains **only** `question.txt` (original stem, all four A–D; MB23 additionally includes exact original 3-column × 2-data-row table) and `original.webp` (exact image). No G3, answer, known reasoning, teaching, GitHub/Issue URL, SHA manifest or reviewer hints can appear in the solver folder. The original MB20 **webp-v5** and MB23 original complete **2×3 data table** are required; do not use old MB20 v1/v2.

A separate `operator-only/manifest.json` includes source revision, G2 GitBlob and raw SHA256, original WebP SHA256 and GitBlob, and text SHA256, and is **never** passed to the solving model. The CI uploads solver-only and operator-only archives as two different artifacts; do not combine them.

The G6 operator must:
1. Choose **one** QID, supply only that `question.txt` and its same-QID `original.webp` into a **new answer-hidden** solver context (no history, memory, browsing, source repo, official answer, previous attempts, E/B/C analysis or Issue #36).
2. Configure response format **outside the source input** to capture first answer, A–D rationale, confidence and ambiguity. Keep first request and first response **raw original bytes**, actual timestamp, model/provider response/run identifiers; do not edit the original response or claim it is blind when the environment is not actually isolated.
3. Return only genuine independently auditable G6/G7 evidence to MASTER/ROLE E. The existence of this pack alone proves **zero** independent solves and cannot be used for E trust, READY or LIVE.

## Immutable source pins (operator-only; do not feed to solver)

| QID | Source QREV SHA256 | G2 GitBlob SHA1 | G3 GitBlob SHA1 | Original WebP SHA256 |
|---|---|---|---|---|
| `114-00-E-07` | `8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c` | `0f15f815042afd2520144343db6b75ef2e7dbe32` | `02fc841c21213dd3849adce563a4d56e4a8c2e20` | `0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc` |
| `114-00-E-11` | `646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036` | `b9afe6661d89558310b930acf94afeec58464a05` | `9c2bb26760a83b69ad5bd81fd38542016ec7e89d` | `ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0` |
| `114-00-E-12` | `0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec` | `7f1fd3c95f11cafc561d740c2bac6188ef80da5c` | `f546c855abc69160d924d91c6510010326d7e2ad` | `99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60` |
| `115-00-MB-20` | `2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c` | `90dfde966be01d01674f1419ab3730b9750fb451` | `ff5a1acdc0f340796c4dcd2a52cbfacbbee5957f` | `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf` |
| `115-00-MB-21` | `817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9` | `d738f2eec5b9337721b7a959b0418cce38b6baa6` | `364b47aa32df1acaed558bb3edee80531fbf251f` | `b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693` |
| `115-00-MB-22` | `7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17` | `234f2f77007785f8dcc06ec4f485576a1e4e81e4` | `fc6c054212580bb3ecdf665219f30df733ba9a20` | `3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55` |
| `115-00-MB-23` | `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4` | `58937614cce5f404f69aa05ba05a94e9f26f9ddf` | `43756219d98a96f661d06a777585d1e45e3c520b` | `2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51` |
| `115-00-MB-24` | `9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267` | `7999ac501848acd5d1898e9a9a44db44e94c857e` | `22a630e6c13246e60a3019dc8d7d086488ae0ea0` | `c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb` |
| `115-00-MB-25` | `8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f` | `aea980db08c02d4ac1abfe4b183a78a6d7bd6cd5` | `ddab91ca53f3cc9ce7263916de7fe81d0e8d5038` | `92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896` |

G2 and G3 exact paths: `sudu/data/processed/<YEAR>/review-evidence/<QID>-ocr-publisher-<DATE>.json` and `<QID>-official-publisher-<DATE>.json`. Dates for 114 E07=20261115, E11/E12=20261107; 115 MB20/23=20261110, MB21/22=20261108, MB24/25=20261114. G2 and G3 paths were actually read from official QA directory and JSON before construction.

Source banks: 114 `sudu/data/processed/114/questions.json` GitBlob `dd4d822b8b875a488c38518dc25b0409b1f7ed20` (205 unique); 115 corresponding bank GitBlob `7abb956b6b4beee49513f8f8304a2d15199eb5e2` (205 unique). Native source DBs: `sudu/data/processed/114/question-bank.sqlite3` (7-column schema) and `sudu/data/processed/115/question-bank.sqlite3` (14-column schema). The new packaging script reads but never writes these files.

Official 114 English paper PDF SHA256: `1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf`; 114 official answer PDF `ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325`; 114 English correction PDF `79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc`, historical only E26. Official 115 Math B original paper PDF `e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082`; 115 Math B official answer PDF `d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95`, 115 Math B source correction status `no_objection_submitted`. These **are archived source pins**, not freshly downloaded by this packaging task.

## 114 E08 → E09 next (not yet qualified G6 input)

E08 `114-00-E-08`: current `questionVerified=false`, `answerVerified=false`; original WebP SHA256 `5a9ebec3dbb4cacf3bbb2cd2f6121f69319d042e3c716f41fdbe96f30bfd9c85`; sourceRevision candidate `09a56002bd224815a9d413ad9a5db3565af0837e16c58ec031bd851f17d69b6c`.

E09 `114-00-E-09`: current `questionVerified=false`, `answerVerified=false`; original WebP SHA256 `393dbdbfbd59220a18fd11d2c09d1b07cd9daf5816d32bbe91a6ec1a335c204b`; sourceRevision candidate `0346c84990c84812b9705adcfab7bb6d51877dce1e07c7ba4cc3e74797583cdd`.

Before writing E08, get a **separate exclusive single-QID CLAIM** covering only E08 canonical 114 object, one 7-column SQL row, required 114 inventory and manifest updates, and new G2/G3/test/report paths. Re-download and compare the official source/answer/correction PDFs, open original image, preserve other 204 FULL canonical objects and all SQL columns, negative-test notice scope and wrong SHA, stage via separate Draft PR to QA. Release E08 lease before sequential E09. **Do not** reuse the G6 pack task's new-file lease as authority to write source banks. No Sites; no teacher/G6/E/D/READY/LIVE self-approval.

## Limits
The G6 pack CI actually performs only G2/source text equality, exact original WebP binary SHA256 + GitBlob, 205 JSON rows each year, MB20 v5, MB23 original 3-column / 2-data-row, generated file allowlists and mutated-text/metadata/image negative tests. It **does not** rerun full SQLite 205 × all-column binary tests or independently re-download source/answer PDFs. Existing historical A source CI proves those separately at their respective SHA. No new student questions are authorized by this PR.
