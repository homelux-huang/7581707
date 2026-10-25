# 7581707 管理員啟用檢查清單（PR #66 + Codex gh-aw）

## Current readback and honest deployment state
GitHub login `homelux-huang` has repository **admin** permission. The *connected ChatGPT GitHub tool*, however, exposes no branch protection/ruleset/Actions Secrets **write** endpoint. Branch GET main is `protected=false`, enforcement OFF. Therefore no assistant tool has enabled main protection; do not claim this is done.

The current five-minute deterministic watcher is PR #66, pending main merge. Its cron runs every five minutes at minutes 02/07/12/.../57 **only after it is on default main**, and triggers may be delayed. It has read-only permissions and does NOT start AI workers or release student questions.

New `.github/workflows/7581707-role-agent.md` is **gh-aw Markdown source, not executable Actions YAML**. Official setup requires compiling it with `gh aw compile` into `7581707-role-agent.lock.yml` and committing both source and lock file. It is deliberately read-only on initial rollout; it cannot author or release content.

## Actual required user/admin-side operations
1. Visit **https://github.com/homelux-huang/7581707/settings/branches** (or Settings → Rules → Rulesets). Create rule for exact `main` with **Require pull request before merging**, **Require status checks** (choose existing stable tests from completed main/PR validation; do not guess a check name), **Do not allow force pushes**, **Do not allow deletions**, and **Include administrators** / no implicit admin bypass. Set 1 independent human repository-configuration/code review where practical; this is NOT a real-teacher signoff for lesson content. Beware that adding required checks unavailable to a new PR can deadlock all merges.
2. Once rule is active, read GET branch main and verify `protected=true`; don't rely on settings clicks alone. Do not invent technical approval for teaching: independent E AI review remains distinct.
3. Open **https://github.com/homelux-huang/7581707/settings/secrets/actions**. Add `CODEX_API_KEY` (or `OPENAI_API_KEY`), obtained in the OpenAI Platform secure key setup or platform.openai.com/api-keys. Do not share the raw value in chat, source code, GitHub Issues, shell history or Actions logs. Put a restricted project budget on the Platform account and monitor actual charges. A ChatGPT subscription does not authenticate Codex inside gh-aw.
4. Install GitHub CLI `gh` on a trusted development runner, and install extension `gh extension install github/gh-aw`. Compile reviewed source with `gh aw compile`. The compiler produces `.github/workflows/7581707-role-agent.lock.yml`. Commit **both** source and lock file to an isolated PR. Never claim an uncompiled Markdown source runs. Recheck current GitHub gh-aw CLI syntax/agent model support at compile time.
5. Release the deterministic watcher PR #66 only after a safe independent infrastructure review and branch protection readback. Confirm its exact-head tests pass, then merge by controlled SHA-pinned PR into protected main. Verify an actual scheduled Actions run and inspect nonempty JSON artifact from Issue #36. Do not confuse it with an AI worker.
6. Review the compiled AI runner PR, ensure read-only source/trust context; then merge with checks and audit an actual `workflow_dispatch` inference run. The bootstrap workflow is deliberately **15-minute** cadence to control initial API cost; only after real costs and permissions are measured should the owner change it to a 5-minute cadence. Scheduling the same model five times in parallel without bounded expense or truly independent reviewers is unsafe.
7. For actual source/lesson/UI code-writing jobs, create **separate reviewed** A/B/C/D read/isolated-PR author workflows and E a completely separate read-only reviewer with distinct trusted provenance. All roles must make bounded CLAIM/RETURN via Issue #36 and produce Draft PRs, CI and original version SHAs; no code-generation workflow may directly merge main or write approval receipts. MASTER release job must remain fail-closed and verify protected main, original official pixels and answers, source/OCR/SQLite, E trust, D exact 8x2, prior GitHub Actions, Pages and LIVE SHA.

## Roles and progress
A original source/OCR/SQLite; B 114 lessons; C 115 lessons; D 35-Demo V4 UI 8x2; E independently audited AI source/lesson/gate evidence. 104–113 historical raw records (2,043) have no independently approved source/teaching lessons yet, so zero historical student READY from that inventory. All non-ready remain quarantined. No real human teacher credential/Ed25519/teacher APPROVED prerequisite is permitted.

## Evidence of tool limitation
The ChatGPT-connected GitHub integration has repository admin metadata (account-level) but **its tool endpoints exclude administration-write and secrets-write**. Trying to use `GITHUB_TOKEN` to modify branch protection or install paid model API keys is not a valid replacement. Authentication creation/opened setup does not prove that CODEX_API_KEY has been saved as GitHub repository secret.

Useful references:
- https://github.github.com/gh-aw/setup/creating-workflows/
- https://github.github.com/gh-aw/engines/codex/
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
