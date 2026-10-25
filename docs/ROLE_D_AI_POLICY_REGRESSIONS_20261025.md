# Role D independent publisher regression handoff

Task `D-AI-POLICY-REGRESSION-20261025-VSCODE-11`, Issue36 claim
[6393906184](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393906184).
Explicit base `d6f134d20ca3f03c2009971e0ccd801706f4c482`, MASTER branch
`governance/114-115-ai-publisher-gate-20261025`.

The owner removed actual human teacher identity, qualification, Ed25519 and
teacher GitHub APPROVED requirements. MASTER owns the policy/gate/publisher
migration. This Role D branch owns only this handoff, the new regression test
and its workflow. Never overwrite another session's active publisher lease.

The regression exercises **real** `certified`, distinct AI receipt verification
and `apply_independently_certified_review` together. Remote GitHub trust and
official notice boundaries are simulated offline, with synthetic data in a
temporary directory. The reviewer result is not mocked to True. A positive
case proves absence of teacher roster/signing dependencies, without asserting
that any real lesson passed AI E, source, UI, READY or LIVE gates. No API key.

At the original base, 6/8 tests pass. Two fail for an actual retained-quality
defect: the publisher accepts a missing UI teaching digest and accepts an old
UI digest after a new AI-reviewed lesson changes while questionRevision stays
unchanged. Reported to MASTER in
[6393914192](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393914192).
The expected new UI field is `testedTeachingDigest`, equal to SHA256 of the
canonical teaching `content`. Missing or stale values must reject new lessons.
Keep the negative assertions; do not set PASS or replace the tested digest.

Other regressions cover forged author self-review, changed image, changed
calculation without renewed review, official answer conflict even when the
receipt SHA is resealed, and changed necessary table/revision. The existing
publisher suite additionally covers actual historical subject boundaries,
official correction scope, table serialization and source QA. These synthetic
unit tests are never usable as real V4 browser proof or independent content QA.

Coordination command and sole 410-entry ledger remain PR30
`97d351202fe01de8fdb7c34d94cf36d64b646d17`; they already reflect the owner
AI-only directive and correctly describe migration as not integrated. Their
source/lesson/review/READY statuses are not modified on this branch. Normal
repository security/PR controls remain; missing AI evidence is not a missing
teacher. Actual final tests/CI/commit and MASTER follow-up are returned to
[Issue36](https://github.com/homelux-huang/7581707/issues/36).

No student HTML/runtime/localStorage schema, approved questions, original
images/OCR/SQLite or lesson is changed by these regressions. New READY/LIVE=0.
