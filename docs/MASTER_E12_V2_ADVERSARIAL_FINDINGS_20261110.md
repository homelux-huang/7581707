# MASTER E12 | Experimental V2 adverse-case diagnostic | 2026-11-10

**NOT an independent security review. NOT V1 acceptance. NO student release.**

This file documents bounded MASTER diagnostics against the existing E12 V2 prototype at frozen parent `57f752956046a6543e6f25fa0365662b550c2d79`. The original V2 module and tests are unchanged; all added tests use generated synthetic keys, no provider API, no real blinded solve or genuine role identities. Passing diagnostic tests means unsafe-looking records satisfy **structure-only** checks, NOT that real records are trusted.

## Findings demonstrated by added executable tests

1. **Provider response ID isn't authenticated:** A made-up but format-conforming `resp_...` with a valid self-generated signature can satisfy `verify_offline_structure`; provider retrieval/signature/ownership is not checked.
2. **First blind response completeness not established:** A verbose one-option response without A/B/D independent reasons satisfies current length + firstAnswer checks.
3. **Prompt disclosure/inherited knowledge not ruled out:** A paraphrased prompt that reveals the selected option can bypass the small exact-substring detector; even complete prompt scanning cannot prove the model has no prior hidden context.
4. **Claimed run timestamps are issuer-authored:** Signed `startedAt`/`completedAt` strings are not provider-authenticated clock evidence.
5. **Replay prevention is local to the checked bundle:** The same complete chain can be verified repeatedly. There is no independently persisted nonce ledger.
6. **No age/expiry bound:** A valid old structurally signed chain can still pass future validation.

Existing role/principal/issuer-key field checks do not authenticate independent underlying persons, companies, models or sessions. Caller-provided issuer registry is not a protected-main independent trust root. JSON decoding also requires duplicate-key rejection and canonical raw-byte design in a future production contract.

## Safe facts

- The helper's return value for otherwise acceptable structure is `SIGNED_STRUCTURE_ONLY_EXTERNAL_PROVIDER_UNVERIFIED`.
- `is_student_release_authorized()` **always returns False**. Diagnostics explicitly assert this, including when synthetic records pass structure checks.
- The private publisher continues to fail closed on external G6 provenance and V1 E trusted registry.
- This report is not an actual provider execution log. Test identifiers, timestamps, keys and model responses are intentionally synthetic fixtures.

## Required separate reviewer action

An independently accountable security reviewer (not MASTER, not B/E, not the issuer operator) must review the actual issuer identity architecture and verify external provider-produced original request/response, immutable history/no-key chronology, prior-context isolation, independent B/solver/E principals, real provider keys, trusted-public-key bootstrap and revocation, durable replay database/nonces/expiry, exact source/lesson/QID/official SHA, D original publisher candidate, and full adversarial G0-G10 regression. Production V2 requires a **separate policy-change PR** reviewed/approved under protected main. Synthetic CI SUCCESS must never become V1 TRUST_PASS or E12 READY/LIVE.

## External blocker retained

At the time of this diagnostic, source/official/lesson G2/G3/G5 are frozen and valid, and the user-provided detailed answer C is exposed to possible prior C summary. The genuine first raw provider response and authenticated B/E session identities have not been supplied. Thus **G6=UNVERIFIED; G7=UNVERIFIED; G8 formal positive=0/16; new READY/LIVE=0**.

Related handoff: `docs/MASTER_E12_G6_G7_EXTERNAL_DISPATCH_20261108.md` in DRAFT PR #183 (separate coordination branch). Original ROLE E: DRAFT PR #173. Do not conflate SHA of a handoff with SHA of a real provider first response.
