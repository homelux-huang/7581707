# 7581707 | E12 G6/G7 | Active provider first-response execution contract (2026-11-11)

**Classification:** SECURITY-CANDIDATE / NOT G6 OR G7 TRUST / NO STUDENT RELEASE  
**QID:** 114-00-E-12  
**Status:** code-only external provider harness, no real model call yet, no authenticated B/E identity  
**Target:** one truthful original first-turn provider response, independently verified, then protected V1 decision.

## 0. Correct the retired-provider root cause

GitHub's **official** retirement notice https://github.blog/changelog/2026-07-30-github-models-is-now-retired/ and GitHub Docs https://docs.github.com/en/github-models confirm GitHub Models fully retired **2026-07-30** (catalog, inference, playground and BYOK). This explains old HTTP 200 / text/plain / four bytes \`OK\r\n\` in prior actual Actions run #42825938647. It is NOT a temporary networking outage or genuine model completion. Original raw failure in Draft PR #186 and artifact #13768437824 MUST remain unmodified negative evidence. Do not spend tokens or model cost retrying dead GitHub Models endpoints.

## 1. What is now implemented (not yet an executed solver)

- New isolated source branch contains the exact answer-free frozen **G2-only** text at \`docs/evidence-inputs/114-00-E-12-G6-answer-free-G2-first-input-20261111.txt\`.
- Original Git Blob \`29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff\`, original UTF8 SHA256 \`8dfc4a2e8c2cb62d1fe3c95318bfaae6fa9bb83e4937b25df1359f41b52063e0\`. This is the only QUESTION passed to solver; never send this operator document to solver.
- New \`scripts/master_e12_openai_first_solver_20261111.py\`: fail-closed \`preflight\`, \`first\`, \`reveal-after\`. One raw **OpenAI Responses API** POST \`https://api.openai.com/v1/responses\`, requested model \`gpt-5.5\`, neutral instructions plus immutable official G2 only, \`store=true\` for later separately authorized provider retrieval, no previous_response_id, tools, assistant history, memory, retrieval, E/B chat or official answer.
- First request body and actual first response raw bytes saved with **exclusive write + fsync**, SHA256 and computable Git blob. Capture provider-returned \`id\`, \`created_at\`, \`model\`, genuine \`x-request-id\` and unique runtime \`X-Client-Request-Id\`, GitHub run SHA/ID, runner UTC observations. None of those IDs/times are invented. A returned ID or runner time alone is **not** provider signature or independent B/E identity.
- A separate \`reveal-after\` step reads frozen official G3 bytes **only after** original first-response bytes are stored, rehashed and minimally checked for A/B/C/D labelled rationale. Its chronology is a **runner observation**, not a provider-attested no-exposure certificate.
- Only after independent security assessment may a real E receipt be considered. All script output fields \`qualifiedG6\`, \`qualifiedG7\`, \`trustedV1Receipt\`, \`blindPass\`, \`ready\`, \`live\` stay false, including on a successful provider HTTP 200.
- \`tests/test_master_e12_openai_first_solver_20261111.py\` uses **explicitly synthetic** local provider fixtures, tests that no API call happens without key, first bytes are preserved, a four-byte \`OK\r\n\` response is rejected, and first official key fetch is forbidden without prior model response.
- \`.github/workflows/master-e12-openai-first-response-20261111.yml\`: automatic **synthetic-contract tests only**, separate paid real-provider job with an exact independent-operator trigger commit. GitHub job is locked to the environment \`e12-g6-independent-operator\`; no auto inference on ordinary commits.

## 2. Mandatory one-time owner security configuration (requires independent actual owner action)

**Do not paste an API key in a ChatGPT message, GitHub commit, issue, PR body, artifact or test file.** The available GitHub connector does NOT support writing repository or environment secrets. Use GitHub repository's **Settings → Environments** and create environment named \`e12-g6-independent-operator\`. Set required reviewers who are a real principal separate from B author, E reviewer and MASTER; restrict environment deployment branches to this exact execution branch when supported. Within the **environment secrets** (NOT a broad repository secret), add \`E12_G6_OPENAI_API_KEY\` holding a dedicated, revocable, scoped OpenAI project key. Restrict project access to Responses create/retrieve, configure an explicit small spend limit, and give the independently accountable operator access to only the necessary project logs. Verify required reviewer approval works before any paid inference.

**Security caveat:** A GitHub environment/Actions actor ID does not by itself authenticate a previous ChatGPT B/E execution session. Historical B/E principal separation remains an external fact to prove.

### One-shot execution trigger after secret and independent reviewer approval

The real-provider job only runs on a new push to \`security/master-e12-openai-first-response-harness-20261111\` with **EXACT** final commit message:

\`execute(e12-g6): approved independent provider first-turn\`

The operator must create a new clearly marked \`docs/evidence-inputs/114-00-E-12-g6-operator-run-marker-YYYYMMDD.md\` on this branch; this path matches the workflow. Only trigger once after confirming key, branch scope, environment approvals, pricing and external independent operator. Do not run as an answer-exposed ChatGPT session and then claim fresh independent role identity.

After run, preserve original Actions **artifact** with raw request and first response, first model text, SHA256s, provider response ID, provider request ID and separately archived G3 chronology. Do not use a synthetic test record or re-run and replace original first response. If HTTP fails or model output misses distinct A/B/C/D rationales, RETURN \`G6=UNVERIFIED\` with original failed bytes and stop.

## 3. Exact prompts for separate roles

### P0 — EXTERNAL independent execution operator (not B/E/MASTER)

> You are a real independent execution operator with a separately accountable provider project and approved GitHub environment access. Read only the answer-free source Git Blob \`29c8e0d3c38ad9f1c997c5284ebb1c639827e0ff\` and this operator instruction, NOT official key, PR173, old E12 chat/memory, user-pasted answer or teacher lesson. Verify the provider project and environment identity, single empty-context Responses API request with no previous_response_id/tools, and inspect the frozen request body before executing. Obtain required owner approval for the restricted paid provider key, trigger exactly once with specified commit, and preserve **original** first HTTP response and model first text, server \`id\`/\`x-request-id\`/\`created_at\`/model, GitHub Actions job identity and first-response SHA. Do not claim provider signature from a GitHub log or imply that this is official G6 PASS. Send originals to independently authorized security reviewer; do not reveal official answer before original model first response has been frozen. On missing key/provider, return EXTERNAL_DEPENDENCY without any fabricated ID, timestamp or answer.

### P0 — Independently authenticated SECURITY REVIEWER (not execution operator or B/E/MASTER)

> Fetch REAL provider response independently using the stored returned provider response ID and a separately authorized OpenAI project retrieval credential; compare stable text/model/response IDs and real provider request metadata against original raw POST response. Verify separate GitHub operator identity/reviewer approvals, exact G2 byte SHA, true absence of official G3 and prior context in all model-visible messages, prompt and response SHA256/Git Blob, chronological post-response key disclosure, distinct first A/B/C/D reasoning and semantics. Audit key custody, expiry, key revocation, immutable provider/audit logs, nonce ledger for repeated runs and independent B vs E execution identity, with positive + adversarial tests. Identify any unprovable history/no-context assumptions and any unmet current \`DISTINCT_AI_CONTENT_RECEIPT_V1\` fields. **Do NOT treat a provider Response ID, provider-model response or synthetic PR184 tests alone as production attestation or a protected-main TRUST_PASS.** Separately approve and test any future V2 policy migration via protected PR; otherwise G6/G7 remain UNVERIFIED. Record exact provider verification logs, real reviewer principal, original hashes and CI SHA.

### P1 — ROLE E only after independent security review

> On a fresh ROLE E CLAIM (not B author), compare original provider first answer and reasons for A-D with frozen G2 and published official G3, plus original B teaching SHA \`c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a\`, question revision \`0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec\`, WebP SHA \`99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60\` and issuer G2/G3/G5. Validate real distinct B/E/authenticated provider execution principals, do not self-sign or reuse an answer-exposed previous E12 response as blind. If all **current approved** protected V1 contract fields genuinely meet policy, propose exact SHA-bound reviewer receipt to MASTER; else preserve G7 UNVERIFIED / HOLD with missing field detail.

### P2 — MASTER then ROLE D only after verified receipt

> MASTER checks protected-main trustedAiReviewReceipts and G4 overlay through normal protected PR, never auto-mints TRUST_PASS from raw API ID or experimental V2. Only once actual current policy and independent receipt are accepted, run original private native publisher \`bc946e4a17c0172e21d9dd5710275c49523af990\`, then ROLE D runs actual V4 8 viewports × Light/Dark = 16 Chromium tests using real publisher-emitted immutable question/image/lesson, 16 screenshots and exact testedTeachingDigest. MASTER runs full unchanged G0-G10 with negative regressions, protected merge and same-SHA Pages verify_live. Otherwise HOLD. No READY/LIVE solely from provider first response.

## 4. Audit boundaries and known dependencies

- Current protected main SHA last verified \`5546a603abfe0af2e62c0e5f63f775be0bfb24cf\`; protected V1 review policy has \`trustedAiReviewReceipts={}\`.
- Original ROLE E [Draft PR #173](https://github.com/homelux-huang/7581707/pull/173), exact author-reviewed E HEAD \`aa77cf6bd2ecfe5e1b4fdf57810be8734ec82161\`: 11 evidence-integrity CI SUCCESS **not original provider/binding proof**.
- V2 synthetic adversarial [Draft PR #184](https://github.com/homelux-huang/7581707/pull/184) shows provider IDs can be fabricated within a self-signed structure; V2 must not be promoted to V1.
- GitHub Models failed-HTTP [Draft PR #186](https://github.com/homelux-huang/7581707/pull/186) remains untouched audit history.
- This new branch does not edit official source, B teaching, E receipt, V2, private publisher, V4, protected review policy, student-approved files, \`main\` or Pages. Merely writing this handoff does not trigger separate ChatGPT sessions or a real external inference.

**No real provider response at document creation; no B/E distinct identity attestation; G6=UNVERIFIED, G7=UNVERIFIED, TRUST_PASS=false, READY=false, LIVE=false.**

## 5. Real provider network reachability receipt (NOT G6; 2026-11-11)

Before requesting anyone to install a paid API key, MASTER ran a distinct **NO API KEY / NO MODEL INFERENCE** workflow from this isolated branch:

- Actual [Actions #42944691936](https://github.com/homelux-huang/7581707/actions/runs/42944691936), exact probe commit `bb82e31bbf7dea025b9f9b0cacc15924da1d5ec6`, job `130274550328`: **COMPLETED SUCCESS**.
- Request: `GET https://api.openai.com/v1/models` with **no credentials**, and no exam input.
- Actual result: HTTP **401**, `application/json`, 151 response bytes, body SHA256 `020cefc21c2f2477bc862fb750a476414029d287454ca6a67d0b1d19d82d219d`; server-returned `x-request-id = 14533012-4b32-49eb-a278-740b28c3fe30` in runner log.
- The body was **not** the retired GitHub Models four-byte `OK\\r\\n`; the official OpenAI endpoint correctly requests authentication. This verifies the route can return a real API JSON error from this runner, **not** that a model was invoked or any B/E execution identity exists.
- Separate exact HEAD synthetic-only contract CI [#42944569697](https://github.com/homelux-huang/7581707/actions/runs/42944569697) completed SUCCESS at `b0e18c5ded72b024ebdbfad7be41ad94746b739f`; real paid external first-run job **SKIPPED**, not PASS.

**Next external dependency remains one securely configured, narrow GitHub environment key plus independent approval and a real first OpenAI Responses API call.** Do not assert `G6=PASS` from an HTTP 401 or synthetic unit test. The ChatGPT key setup flow was opened but no key creation, GitHub environment secret installation or independent operator execution has been confirmed.
