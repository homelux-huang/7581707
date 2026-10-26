# Repository owner: independent reviewer activation is BLOCKED until authorization

The repository owner must decide the two questions stated by the Master Session:
(A) continue requiring a **qualified human teacher** for every NEW official student lesson (currently `requireHumanTeacher=true`), or formally approve another independently qualified role through a reviewed governance PR; and
(B) authorize a named **different** reviewer, verified GitHub account ID, professional qualification, and their Ed25519 public key.

The current `authorizedReviewers={}` is intentionally empty. **NO release permission is granted by this document, by CODEOWNERS, or by a signed test fixture.**

## Security properties implemented in this candidate branch

- The production source QA cannot register keys, roles or trusted review events: only the release-side reviewed registry is read. Unauthorized authored JSON, reviewer-string changes and self-generated keys are rejected.
- Review signer authenticates actual Ed25519 signature over canonical UTF-8 JSON containing per-question source revision, single-question WebP SHA, official final answer, official evidence JSON SHA, complete teaching canonical digest and raw teaching evidence SHA, reviewed date, professional & elementary explanations, A-D findings, signed independent notes path & SHA, author login and GitHub account ID, PR number, approval review ID and reviewed GitHub PR HEAD.
- Online GitHub API checks **PR creator**, matching human GitHub account ID, every actual commit author and committer, actual `APPROVED` review event on identical HEAD, GitHub reviewer ID, and submitted timestamp. If missing, unlinked, dismissed, changed HEAD, private/unreachable API, oversized unpaginated PR or reviewer also contributed a commit: **fail closed**.
- Owner-signed policy registry checks key ID, GitHub reviewer user ID, verified qualification, validFrom/expiresAt window, key enabled/revokedAt, and required human teacher role.
- The existing five historical questions are grandfathered **ONLY** when original question revision, WebP binary SHA and original teaching evidence Git Blob are unchanged. The whitelist does not assert these students already had independent teacher review.
- For each new question, after a legitimate real approval event and signature, existing original QA G0-G10, publisher stage/check, same-SHA 8x2 V4 and LIVE verifier remain independently mandatory. The crypto signature does not prove content correctness on its own.

## Owner actions required — not performed by AI Session

1. Enable branch rulesets/branch protection on `main`: require PR, at least one approval from a **different person**, require CODEOWNERS review, dismiss stale approvals, require fresh approval for every source/policy modification, forbid force-push and deletion, include administrators, no unconditional CI/App bypass. Verify that the configured reviewers are real, have access and are not the source author.
2. Approve or reject adopting qualified human teacher as permanent role before registering any reviewer. A different AI Session's substantive review is supporting evidence only; it cannot impersonate a credentialed human.
3. Personally verify each reviewer legal account affiliation/qualification and public key fingerprint using an independent trusted channel. Require individual control and safe custody of the **private** key, never store it in the repository, issue, evidence JSON, Actions env/log, or frontend.
4. Add approved `authorizedReviewers[keyId]` to the owner-reviewed policy ONLY after the role and identity are verified, with `login`, `githubUserId`, `enabled`, `role`, `organizationVerified`, `ed25519PublicKey`, `validFrom`, `expiresAt`, and optional `revokedAt`; use unique IDs and signed review event, and run the full negative CI.
5. PR author must submit a real PR (<=100 commits; each author/committer linked to GitHub). The **different** authorized reviewer must inspect original official examination pixel evidence, per-question text, correction notice, A–D professional/child explanations, calculation conditions and source, leave substantive notes with SHA, then submit a real GitHub **APPROVED** review for the exact PR HEAD, and sign the exact canonical attestation.
6. If role or key is revoked, disable its policy entry and rerun all related source approvals. Revised official evidence, WebP, source revision, lesson digest, signed notes or reviewed PR HEAD **invalidate the old statement**. Treat existing live data with a documented remediation and independent release decision, not silent deletion.

## Required status until owner completion

`TRUSTED_EXTERNAL_REVIEWER_REGISTERED=0`

`NEW_READY=0`

`MAIN_MERGE_ALLOWED=NO_UNTIL_MASTER_GO`

`NEW_LIVE=0`

Cross-session instructions and artificial test signing keys never constitute owner authorization. 
