# 7581707 | MASTER | 114 E12 G6/G7 | NEXT ROLE PROMPTS | 2026-11-13

**Classification:** OPERATIONAL HANDOFF / NOT AUTHORIZED RELEASE  
**Task:** E12 only. Real evidence, not synthetic PASS.  
**Existing branch:** security/master-e12-openai-first-response-harness-20261111  
**Existing PR:** https://github.com/homelux-huang/7581707/pull/188  
**Original E reviewer PR:** https://github.com/homelux-huang/7581707/pull/173  
**MASTER control:** https://github.com/homelux-huang/7581707/issues/36

**Important contamination guard:** This document is for HUMAN / external execution OPERATOR and auditing roles only. **DO NOT paste this document into the blind SOLVER model.** The blind solver must see only the one frozen G2 question plus the neutral solver instruction that the approved script constructs. Never send any prior E12 conversation, answer key, authored teaching, PR review or Issue #36 to the solver.

## Verified state at dispatch

- Protected main: 5546a603abfe0af2e62c0e5f63f775be0bfb24cf.
- ROLE E PR #173 HEAD: aa77cf6bd2ecfe5e1b4fdf57810be8734ec82161.
- Source revision: 0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec.
- Original source WebP SHA256: 99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60.
- Frozen B teaching SHA256: c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a.
- Frozen answer-free solver-input Git Blob: 29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff.
- Frozen answer-free solver-input SHA256: 8dfc4a2e8c2cb62d1fe3c95318bfaae6fa9bb83e4937b25df1359f41b52063e0.
- V1 reviewMode DISTINCT_AI_CONTENT_RECEIPT_V1; protected trustedAiReviewReceipts is empty.
- E content semantic checks already passed, but FIRST external independent solver evidence was not obtained.
- Previous GitHub Models attempt is invalid: provider retired 2026-07-30; Run #42825938647 was 200 text/plain OK, not a model answer.
- Active OpenAI API reachability Run #42944691936: HTTP 401 JSON without key, no model answer.
- Existing PR #188 contract-test CI successful; all real external model jobs so far were deliberately SKIPPED. G6/G7 remain UNVERIFIED, trusted receipt missing and real publisher-emitted Chromium positive 0/16.

## PROMPT 0 — OWNER / GitHub repository administrator (must be completed before model execution)

You are the real repository owner or a duly authorized security administrator, NOT the G6 solver or ROLE E reviewer.

1. Inspect PR #188 exact latest HEAD, its security code and its tests. Do not merge PR #188 into protected main to run G6. Confirm the role-independent operator selected is a **real person/account principal** different from prior B author, E reviewer and MASTER; preserve independent approval records.
2. In GitHub repository Settings > Environments, explicitly **create/configure** environment exactly named: e12-g6-independent-operator. Do not merely reference it in a workflow: GitHub can implicitly create a new unprotected environment.
3. Configure Required reviewers to a separate qualified security reviewer, enable Prevent self-review, disable administrators bypass of deployment protection, and limit allowed deployment branch to security/master-e12-openai-first-response-harness-20261111.
4. In this environment, set **two environment variables** (NOT repository-wide vars):
   - E12_G6_OWNER_OPERATOR_LOGIN = the exact verified independent GitHub login of the operator, not the MASTER account and not a bot.
   - E12_G6_OWNER_ARMED = INDEPENDENT_OPERATOR_REVIEWED_ONE_SHOT
5. In this same restricted environment, install **one Environment Secret**: E12_G6_OPENAI_API_KEY (a revocable, limited-spend key for a dedicated independent OpenAI project). Do not paste any credential into ChatGPT, PR/Issue, Git commit or logs. Set provider project spend and permissions narrowly.
6. Verify separate required reviewer and owner/operator identity configuration through independently saved evidence. GitHub's Environment details cannot presently be read through MASTER's available connector; do not claim it is configured without real proof.
7. Give a real independent operator explicit written permission to initiate exactly one response. This permission is not a signed G6/G7 receipt. After completion, disarm E12_G6_OWNER_ARMED and revoke/rotate scoped credential as appropriate.

RETURN to Issue #36: Environment configured evidence (without secrets), actual operator login, distinct reviewer login, branch policy, self-review/bypass status, credential present (not its value), authorized one-time run decision, approval timestamp/identity, and SHA of reviewed workflow. If any required configuration cannot be verified, RETURN **OWNER_CONFIG_HOLD**, no solver run.

## PROMPT 1 — G6 INDEPENDENT EXTERNAL OPERATOR (P0; different from MASTER/B/E)

You are an independent external operator with an already isolated, no-answer-exposed execution role, a separately authorized GitHub identity and dedicated provider project. You are NOT ROLE B, ROLE E, or MASTER. Treat any previous E12 chats or answer-bearing summaries as disqualifying from personal blind-solving; do not try to 'forget' exposure or rewrite a transcript.

1. After real owner Environment review and approval, refresh Issue #36 and PR #188 current exact HEAD. Verify only the G2 no-answer source Git Blob 29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff enters the model input; DO NOT pass this entire prompt, previous E12 chat, official G3, teacher explanations or prior E review to the solver.
2. Check the approved workflow's mandatory operator guard: GitHub repo, branch, first run attempt, real GITHUB_ACTOR and GITHUB_TRIGGERING_ACTOR must equal owner-configured E12_G6_OWNER_OPERATOR_LOGIN; E12_G6_OWNER_ARMED must equal INDEPENDENT_OPERATOR_REVIEWED_ONE_SHOT. A missing field forbids the provider POST.
3. Make exactly one new commit on the isolated PR #188 head branch, adding only a uniquely named no-answer operator marker in docs/evidence-inputs matching 114-00-E-12-g6-operator-run-marker-*.md. The last commit message MUST exactly equal: execute(e12-g6): approved independent provider first-turn. The approved owner and independent reviewer must verify the exact commit SHA and permissions before approving the GitHub environment job. Do not modify the solver code or input after approval.
4. Use the existing script's stateless OpenAI Responses API one-request execution. Capture the original raw request bytes, initial raw HTTP response bytes, first assistant answer with reasons **A–D**, genuine provider response ID, x-request-id, created_at/model and GitHub Actions ID/time before any official answer lookup. Do not retry an unsuccessful call and describe any failure honestly.
5. The separate official-answer reveal step may run only after original response was frozen. Preserve encrypted or access-controlled originals and record SHA256 and Git Blob OID for each byte artifact. A computed Git Blob OID is not evidence that the file was actually committed to Git.
6. Do NOT self-declare G6 PASS; hand over to separate independent security reviewer. Do NOT set blindPass, TRUST_PASS, READY, LIVE or modify protected-main registry.

RETURN to Issue #36: exact operator identity (not a pseudonymous synthetic ID), provider original request/response references, provider IDs actually returned, raw byte SHA256/GitBlob, GitHub run ID and exact SHA, FIRST answer's four complete A-D rationales, chronology, provider retrieval limitations, and **G6=UNVERIFIED pending independent security review**.

## PROMPT 2 — INDEPENDENT SECURITY REVIEWER (P0; different from operator/B/E/MASTER)

You are independently accountable for attestation, and are not the issuer/operator, teacher author, prior ROLE E or MASTER.

1. Re-read current protected V1 policy; review PR #173 (E12 content), PR #184 (experimental V2 adversarial failures), PR #188 (real provider harness), and the original true artifact of the first provider attempt. Never treat a GitHub synthetic-test PASS as a provider-issued attestation.
2. Using a separately authorized provider API account/project audit access, independently retrieve the original persisted Responses API object by **actual** provider response ID, compare response text/model/IDs to saved original raw HTTP body and x-request-id logs. Note provider response ID, HTTP/TLS and runner timestamps alone are not nonrepudiable provider signatures.
3. Compare the exact byte-frozen G2 input, option text, first A-D reasoning, no previous_response_id/tools/history, official-answer-after-first-response chronology, approved environment reviewers, caller/trigger actor, key custody, provider project access and deletion/rotation schedule.
4. Explicitly investigate B vs E historical actual execution principals: distinct verified identities, sessions or provider audit logs, no self-review, no shared owner-controlled synthetic personas. If original B/E identity cannot actually be proven, preserve **G7=UNVERIFIED** even when external G6 produced a real answer.
5. Test negative cases: fabricated provider ID, edited raw content, changed source revision/WebP/teaching digest, answer-key disclosure, missing A/B/C/D reasoning, incomplete timestamps, reused nonce, repeated first-run, impersonated operator and unreviewed environment/secret access. Verify durable replay prevention and revocation; document failures, not false positives.
6. V2 is only a security prototype. Adopting V2 in place of protected V1 requires a separate independently reviewed policy-change PR and complete positive/negative release regression. This audit cannot unilaterally promote V2 synthetic artifacts.

RETURN to Issue #36: true independent reviewer identity, provider retrieval proof, original SHA/log/CI, B-vs-E identity finding, attacker cases, precise missing formal contract fields and recommendation. If any critical attribute absent, return **SECURITY_HOLD / G6 or G7 UNVERIFIED**, never TRUST_PASS.

## PROMPT 3 — ROLE E (P1 only AFTER genuine external execution plus security verification)

You are ROLE E, not B teacher author or the blind solver. Refresh Issue #36, PR #173, official G2/G3/G5 and current frozen B lesson.

1. Examine original external provider first answer, A–D complete reasoning, real provider retrieval verification, exact G2 revision + original WebP SHA + G3 final answer, B teaching SHA and your own previously archived semantic QA. Preserve any sound existing evidence; don't rewrite it for an artificial new digest.
2. Confirm separately authenticated B and E execution principals in the approved **DISTINCT_AI_CONTENT_RECEIPT_V1** policy. The earlier E handoff admitted possible answer exposure; do not reclassify that past ChatGPT response as a genuinely blind first attempt.
3. If **every** current approved contract requirement is objectively met, prepare a receipt whose precise SHA-binding is independently reproducible and allow MASTER to review it. Otherwise issue a clear HOLD with exact missing fields. No reviewer-generated fake session IDs, self-registration in trust registry or direct main/approved changes.

RETURN to Issue #36: substantive content finding, external evidence validation, real reviewer identity, exact hashes/CI and next owner. No TRUST_PASS unless protected policy truly authorizes it.

## PROMPT 4 — MASTER then ROLE D (P2 CONDITIONAL; NOT currently triggered)

MASTER must first independently confirm external solver/evidence + B/E distinct execution principals, accepted reviewer receipt and protected-main trust registry. The owner must not unilaterally grant a TRUST_PASS simply because source and semantic content are correct.

ONLY after policy acceptance, generate private original publisher-emitted E12 candidate and assign ROLE D the **true V4 8 viewports × Light/Dark = 16** Chromium runs, with no mocked routing or fabricated approved dataset. Check original WebP, four options, teacher/elementary explanation levels, digest binding, wrong-book/nav, no calculation block for a noncalculation question, asset network integrity, and 16 screenshot SHA256s. MASTER then runs G0–G10 complete gates and same-SHA Pages verify_live before any single-QID LIVE.

If any step cannot be verified, return exact blocker and responsible role and keep **READY=false / LIVE=false**.

---

**Operational limitation:** These instructions are submitted to GitHub as coordination. They do NOT automatically activate separate ChatGPT sessions, create an environment secret, execute a paid provider request, or prove external B/E identity. Until a genuine external model answer and independent role authentication exist, **G6 UNVERIFIED / G7 UNVERIFIED / blindPass false / TRUST_PASS false / READY false / LIVE false**.
