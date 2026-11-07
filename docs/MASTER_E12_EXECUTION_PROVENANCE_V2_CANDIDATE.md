# 7581707 E12 — independent execution provenance security prototype

**EXPERIMENTAL ONLY. NOT STUDENT-RELEASE AUTHORIZATION.**

At the protected-main SHA `5546a603abfe0af2e62c0e5f63f775be0bfb24cf` the publisher requires independent `sourceAuthorSessionId` and `reviewerSessionId`, authenticated Issue #36 E return and an unexposed genuine blind solve. GitHub actor identity and timestamps cannot authenticate ChatGPT session identity. ROLE E previously saw official answer C, so existing E notes are **not** a blind solve.

This isolated candidate proposes externally verifiable, signed execution receipts for three genuinely different principals: B original lesson author; answer-blinded independent first-principles solver; separate E content reviewer. The signed manifest binds question ID, source revision, single WebP SHA, original canonical teaching SHA, exact prompt bytes, exact output bytes, provider response ID, chronology, official evidence SHA, and substantive four-option analysis.

## Fails closed

The code checks issuer signatures, nonrevoked issuer keys, nonrepeated principals, nonrepeated provider response IDs, precise QID and SHA matches, first blind answer before E review, absent answer-key fields in the blinded prompt and distinct A–D findings. Negative tests cover forged signatures, changed bytes, wrong SHA, same principal, duplicate provider ID, answer leak, replay, and missing fields.

**Unsolved external prerequisites:** authenticated issuer keys and roles must be independently rooted in protected main; provider API must verify exact original response IDs, original input and output bytes, identity of the actual execution principal, and timestamp. Code-generated role labels and user-managed synthetic test keys are not evidence. Captured prior ChatGPT sessions without provider verification cannot be promoted. The current code deliberately returns `is_student_release_authorized() == False` always and is **not imported by the existing publisher**.

Any production adoption requires an independently reviewed new security policy and protected-main PR with complete adversarial tests and all existing source, G0–G10, UI and Pages gates unchanged. In the meantime the current V1 E12 trust decision stays HOLD. Do not create Session IDs, fabricate blind-solve history, or use this synthetic fixture as a student receipt.
