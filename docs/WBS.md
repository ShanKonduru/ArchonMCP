# ArchonMCP — Work Breakdown Structure (Next Level)

> Purpose: take ArchonMCP from a **one-shot governance scaffolder** to a **Governance-as-Code platform** that *deploys, enforces, and measures* AI-development governance.
>
> Structure: **Epic → Feature → User Story → Tasks**, with WBS numbering (`E1`, `E1.F1`, `E1.F1.S1`). Each story carries acceptance criteria (AC). Effort is a rough T-shirt size (S/M/L/XL). Priority is P0 (do first) → P3 (later).

## Guiding thesis

The tool currently makes a *promise* ("stack-aware governance") that the architecture supports but the content and enforcement don't yet fully deliver. The roadmap closes three gaps, in order:

1. **Say what you are** — docs/version tell the truth about what's built (P0, cheap, credibility).
2. **Enforce what you deploy** — add validation/audit/scoring so governance is checked, not just written (P0/P1, the core differentiator).
3. **Deepen and extend** — fill per-stack content, make governance codebase-aware, open it up as a platform (P2/P3).

---

## Epic map (at a glance)

| # | Epic | Outcome | Priority |
|---|------|---------|----------|
| E1 | Release & Documentation Integrity | Docs, version, and metadata match the code | P0 |
| E2 | Governance Validation & Enforcement | `audit` / `verify` / `score` / drift detection | P0–P1 |
| E3 | Stack-Aware Content Depth | Real per-stack templates, not `Generic` fallbacks | P1 |
| E4 | Codebase-Aware / AI-Native Generation | Governance tailored to the actual repo | P2 |
| E5 | Reporting, Scoring & Metrics | Compliance score, reports, trend over time | P2 |
| E6 | Platform & Extensibility | Custom governance packs, config, versioning | P2–P3 |
| E7 | Distribution & Adoption | CI integration, pre-commit, org rollout | P2–P3 |
| E8 | Quality, Testing & Hardening | Coverage, contract tests, cross-platform CI | P1 (ongoing) |
| E9 | Supply-Chain & Prompt-Injection Security | Signed releases, integrity, injection-safe I/O | P0 (cross-cutting) |
| E10 | Downstream-User Protection (Phishing/Malware/Ransomware) | Users who install this never get burned | P0 |

---

## Security review findings (as reviewed on the current codebase)

A full read of `cli.py`, `server.py`, `detector.py`, `scaffold.py`, all of `templates.py`, and the publish scripts. Recorded here so the fixes below are traceable to evidence.

**Reassuring (no action beyond keeping it true):**
- **No dynamic execution** anywhere in the package — no `eval`/`exec`/`subprocess`/`os.system`/`__import__`/`importlib`. The tool cannot be coerced into running code.
- **No runtime network calls** — `init`/`detect`/`server` fetch nothing; there is no wire to poison during use.
- **Templates are clean today** — no `curl|bash`, `Invoke-WebRequest`, `base64 -d`, or fetch-and-run one-liners in generated governance content.

**Findings that create real phishing/malware/ransomware exposure for downstream users:**

| ID | Severity | Finding | Evidence | Fixed by |
|----|----------|---------|----------|----------|
| SEC-1 | **Critical** | Releases published via manual `twine upload` with a long-lived PyPI token on a dev machine. Token leak / account phish → malicious release → mass malware/ransomware to all installers. | `deploy.sh:163,216`, `deploy.bat:132,178` | E10.F1, E9.F2.S2 |
| SEC-2 | **High** | Unpinned, un-hashed dependencies (`fastmcp>=0.1.0`, `click>=8.0`) and unpinned build tools (`pip install --upgrade build twine`). A compromised upstream release ships through ArchonMCP's name. | `pyproject.toml`, `deploy.sh:36`, `deploy.bat:30` | E10.F2 |
| SEC-3 | **High** | Typosquat / impersonation of the package and repo name is trivial and undefended. | package name `archon-mcp` | E10.F3 |
| SEC-4 | **High** | `init` silently overwrites existing files (e.g. a real hand-written `.github/copilot-instructions.md`) with no backup or confirmation — data loss, and an amplifier if templates are ever poisoned. | `scaffold.py:50,65,80,123,129` | E9.F1.S1 |
| SEC-5 | **High** | No path containment on the MCP `root_directory`; a bare `.resolve()` lets a client/agent be steered to write outside the intended project. | `server.py:41` | E9.F1.S2 |
| SEC-6 | **Medium** | No automated guarantee that future template edits/tampering can't introduce fetch-and-execute commands or lookalike URLs into the files AI agents obey. | `templates.py` (clean now, unguarded) | E10.F4 |
| SEC-7 | **Medium** | No `SECURITY.md`, no disclosure path, no artifact/secret scanning in CI. | repo root | E10.F5, E9.F6 |
| SEC-8 | Low (functional) | `deploy.sh` calls its build/upload functions in the `case` block *before* they are defined (lines 54 vs 80+), so the script errors — the real publish path is unclear and likely ad hoc, which itself is a supply-chain risk. | `deploy.sh:54–77` | E10.F1 |

---

## E1 — Release & Documentation Integrity  *(P0)*

Cheapest, highest-credibility work. For a *governance* tool, doc drift is self-discrediting.

### E1.F1 — Single source of truth for version
- **E1.F1.S1** — *As a user, `archon-mcp --version` reports the real package version.* **(S, P0)**
  - AC: version read from installed package metadata (`importlib.metadata.version("archon-mcp")`), not a hard-coded string.
  - Tasks:
    - Remove hard-coded `version="0.1.0"` in `cli.py`.
    - Wire `@click.version_option` to package metadata.
    - Add test asserting CLI version == `pyproject` version.

### E1.F2 — Documentation reflects all supported stacks
- **E1.F2.S1** — *As an evaluator, the README/PyPI list every stack the code detects.* **(M, P0)**
  - AC: README, PyPI long-description, and lobehub listing enumerate all six `VALID_STACKS`, not just React-FastAPI-Postgres.
  - Tasks:
    - Update README "Features" / "Stack Support" sections.
    - Regenerate PyPI description from README on next release.
    - Add a small doc-generation check (see E8.F3) so the stack list can't drift again.
- **E1.F2.S2** — *As a maintainer, docstrings match reality.* **(S, P0)**
  - AC: `server.py` `init_governance`/`list_tools` docstrings reference `VALID_STACKS`, not the stale two-stack description.
  - Tasks: rewrite docstrings to interpolate/reference `constants.VALID_STACKS`.

### E1.F3 — Positioning refresh
- **E1.F3.S1** — *As a prospective adopter, the project positions itself as Governance-as-Code, not "an MCP server."* **(S, P1)**
  - AC: README lede reframed around the deployable-governance value; MCP described as the delivery mechanism.
  - Note: hold "platform" language until E2 ships — earn it with enforcement.

---

## E2 — Governance Validation & Enforcement  *(P0–P1, the core differentiator)*

This is the move that turns a scaffolder into a governance system. Deploy → **Enforce** → Measure.

### E2.F1 — `verify` command (governance present & intact)
- **E2.F1.S1** — *As a developer, I can check that governance files exist and are unmodified/complete.* **(M, P0)**
  - AC: `archon-mcp verify [--root DIR]` reports which expected governance files are present/missing; exit code non-zero on missing.
  - Tasks:
    - Define the canonical governance manifest (files + expected stack) — extract the file list currently hard-coded in `scaffold.py` into a shared manifest module so `init` and `verify` agree.
    - Implement presence check against the manifest.
    - Implement stack-consistency check (marker vs detected).
    - Human-readable + `--format json` output.
    - Tests: fully-initialized repo passes; repo with a deleted skill fails.

### E2.F2 — Rule drift detection
- **E2.F2.S1** — *As a lead, I'm warned when governance files have drifted from the deployed baseline.* **(L, P1)**
  - AC: `archon-mcp verify --drift` compares current governance files against the template baseline for the recorded stack and reports diffs (added/removed/modified sections).
  - Tasks:
    - Store a content fingerprint (hash per file / per section) at `init` time in the stack marker or a lockfile (`.github/archon-lock.json`).
    - Diff current content vs baseline; classify intentional edits vs template updates.
    - Decide policy: warn-only vs `--strict` fail.
    - Tests around edited/renamed/deleted files.

### E2.F3 — `audit` command (is the repo *following* the governance?)
- **E2.F3.S1** — *As a lead, I can audit a repo against its governance rules and get actionable findings.* **(XL, P1)**
  - AC: `archon-mcp audit [--root DIR]` runs a set of checks derived from the deployed governance (e.g. ADR dir non-empty when significant deps exist, security runbook items detectable, presence of tests, Definition-of-Done items) and outputs findings with severity.
  - Tasks:
    - Design a **check interface** (`Check.run(context) -> Finding[]`) so checks are pluggable and stack-scoped.
    - Implement a starter check pack: `adr-present`, `security-basics`, `tests-present`, `docs-structure`, `copilot-instructions-referenced`.
    - Map each check to the governance artifact it enforces (traceability).
    - Aggregate findings; exit-code policy for CI.
    - Tests: fixture repos that pass/fail each check.

### E2.F4 — MCP tools for verify/audit
- **E2.F4.S1** — *As an AI IDE user, I can run verify/audit through the MCP server.* **(M, P1)**
  - AC: `verify_governance` and `audit_governance` MCP tools registered alongside `init_governance`, returning structured `CallToolResult`.
  - Tasks: register tools; share logic with CLI (no duplication); update `list_tools`; contract tests.

---

## E3 — Stack-Aware Content Depth  *(P1)*

Make "stack-aware governance" *true*, not just *possible*. Today most template keys fall back to `Generic`.

### E3.F1 — Per-stack content coverage audit
- **E3.F1.S1** — *As a maintainer, I know exactly which (template_key × stack) cells are real vs `Generic` fallbacks.* **(S, P1)**
  - AC: a generated coverage matrix (keys × stacks) marking real/fallback content.
  - Tasks: script to introspect `GOVERNANCE_TEMPLATES`; emit matrix to `docs/`; add as a make/CI target.

### E3.F2 — Fill high-value per-stack content
- **E3.F2.S1** — *As a React-FastAPI-Postgres team, my security & migration runbooks are specific to my stack.* **(L, P1)**
  - AC: security, migration, and copilot-instructions have genuinely stack-specific guidance for the flagship stack (Postgres migration patterns, FastAPI auth/rate-limiting, React XSS/CORS).
- **E3.F2.S2** — *Same depth for the remaining stacks, prioritized by demand.* **(XL, P2)**
  - AC: Next.js-Django-Postgres, Vue-Express-MongoDB, Angular-SpringBoot-MySQL, React-Node-MongoDB reach a defined content bar.
  - Tasks (per stack): security runbook, migration runbook, stack-specific copilot rules, naming bootstrap; SME/AI-assisted drafting + review.

### E3.F3 — Template maintainability
- **E3.F3.S1** — *As a maintainer, editing template content doesn't mean editing a 53KB Python dict.* **(M, P2)**
  - AC: templates externalized to Markdown files under a `templates/` tree, loaded at runtime (or packaged); `GOVERNANCE_TEMPLATES` becomes a loader.
  - Tasks: move content to files; loader with `Generic` fallback preserved; ensure packaging includes them (`hatch` data files); update tests.

---

## E4 — Codebase-Aware / AI-Native Generation  *(P2)*

Justify the MCP framing: generate governance *tailored to the actual repo*, not just templated.

### E4.F1 — Repo context extraction
- **E4.F1.S1** — *As a user, init inspects the repo (deps, structure, existing configs) to tailor content.* **(L, P2)**
  - AC: context object (languages, frameworks, package managers, CI presence, existing security tooling) feeds template selection/section inclusion.
  - Tasks: extend detector into a richer `analyze_repo()`; define context schema; unit tests on fixtures.

### E4.F2 — Tailored ADR/runbook seeding
- **E4.F2.S1** — *As a user, generated ADR stubs reflect decisions the repo has already implicitly made.* **(L, P3)**
  - AC: e.g. detects Postgres + Alembic → seeds a migration-strategy ADR stub referencing detected tooling.
  - Tasks: heuristic rules → ADR/story stubs; keep deterministic and reviewable; optional LLM-assisted drafting behind a flag.

---

## E5 — Reporting, Scoring & Metrics  *(P2)*

Deployment + Enforcement + **Measurement**.

### E5.F1 — Compliance score
- **E5.F1.S1** — *As a lead, `audit` produces a 0–100 governance/compliance score.* **(M, P2)**
  - AC: weighted score from check results; documented rubric; stable across runs.
  - Tasks: scoring model; weights config; `score-repository` alias; tests for determinism.

### E5.F2 — Report artifacts
- **E5.F2.S1** — *As a stakeholder, I get an HTML/Markdown governance report.* **(M, P2)**
  - AC: `audit --report` emits `governance-report.html` (mirror the existing `run_audit.sh` HTML pattern) and JSON.
  - Tasks: report template; JSON schema; link findings → governance artifact.

### E5.F3 — Trend over time
- **E5.F3.S1** — *As a lead, I can see score/drift trend across runs.* **(L, P3)**
  - AC: append-only history file; simple trend rendering.

---

## E6 — Platform & Extensibility  *(P2–P3)*

### E6.F1 — Config file
- **E6.F1.S1** — *As a team, I configure ArchonMCP via `archon.config.yaml` (stack overrides, enabled checks, custom paths).* **(M, P2)**
  - AC: config discovered at root; CLI flags override config; documented schema.

### E6.F2 — Custom governance packs
- **E6.F2.S1** — *As an org, I ship my own governance pack (templates + checks) that ArchonMCP consumes.* **(XL, P3)**
  - AC: pack format (templates + check definitions + manifest); `--pack` to select; discovery of installed packs.
  - Tasks: pack spec; loader; validation; example org pack; docs.

### E6.F3 — Governance versioning & upgrade
- **E6.F3.S1** — *As a user, I can upgrade already-deployed governance to a newer ArchonMCP version safely.* **(L, P3)**
  - AC: `archon-mcp upgrade` migrates governance files, preserving local edits (three-way merge using the lockfile from E2.F2).

---

## E7 — Distribution & Adoption  *(P2–P3)*

### E7.F1 — CI integration
- **E7.F1.S1** — *As a team, I run verify/audit in CI and fail the build on violations.* **(M, P2)**
  - AC: documented GitHub Actions example; sensible exit codes; `--strict` mode.
  - Tasks: sample workflow; annotations output (GitHub problem matchers).

### E7.F2 — Pre-commit hook
- **E7.F2.S1** — *As a developer, a pre-commit hook runs `verify` locally.* **(S, P2)**
  - AC: published `.pre-commit-hooks.yaml`; docs.

### E7.F3 — Onboarding UX
- **E7.F3.S1** — *As a new team, `init` gives me a guided next-steps path (already partial in CLI).* **(S, P3)**
  - AC: post-init summary links to the specific generated files and the verify/audit commands.

---

## E8 — Quality, Testing & Hardening  *(P1, ongoing)*

### E8.F1 — Coverage & contract tests
- **E8.F1.S1** — *As a maintainer, MCP tools have contract tests and coverage has a floor.* **(M, P1)**
  - AC: coverage gate in CI (e.g. ≥85%); MCP tool schema/response contract tests.

### E8.F2 — Cross-platform CI
- **E8.F2.S1** — *As a maintainer, CI runs on Windows + Linux + macOS across Py 3.10–3.12.* **(M, P1)**
  - AC: matrix CI green; the `.sh`/`.bat` parity verified.

### E8.F3 — Drift guards for docs/metadata
- **E8.F3.S1** — *As a maintainer, CI fails if docs/docstrings fall out of sync with `VALID_STACKS`/version.* **(S, P1)**
  - AC: a test that asserts README + docstrings reference the current stack list and version. (Closes the loop on E1.)

---

## E9 — Supply-Chain & Prompt-Injection Security  *(P0, cross-cutting)*

> **Why this epic is special.** ArchonMCP sits on a trust boundary in the AI supply chain: its output *is* the instructions that downstream AI agents (Cursor, Claude, Copilot, Windsurf) will obey. That makes prompt injection a first-class threat in **two directions**:
> - **Outward** — a tampered package/template turns `archon-mcp init` into an injection-delivery mechanism: attacker-controlled instructions land in every consuming repo's AI-agent config, laundered by the victim's trust in "our governance file."
> - **Inward** — once the tool *reads* untrusted repo content (E2.F3 `audit`, E4 codebase-aware gen) and reasons over it with an LLM, that content can hijack ArchonMCP's own behavior and loop back out into generated governance.
>
> Treat E9 as cross-cutting: E9.F1/F2/F5 are **P0 and precede/accompany the enforcement and AI-native epics**, not "later."

### E9.F1 — Safe file writes (integrity of the target repo)
- **E9.F1.S1** — *As a user, `init` never silently destroys my existing governance files.* **(M, P0)**
  - AC: writing over an existing file requires `--force`; default is skip-with-warning or write `*.archon-new` alongside; a summary lists created/skipped/would-overwrite.
  - Tasks:
    - Replace unconditional `write_text` in `scaffold.py` with a guarded writer (exists → skip/backup/force).
    - Add `--force` / `--merge` flags to CLI `init` and the MCP tool.
    - Optional `.bak` backup before overwrite.
    - Tests: pre-existing file preserved by default; `--force` overwrites; report accuracy.
- **E9.F1.S2** — *As a user, ArchonMCP cannot write outside the intended project root.* **(M, P0)**
  - AC: all write targets are validated to resolve **inside** `root_path`; path traversal (`../`, absolute, symlink escape) is rejected before any write.
  - Tasks:
    - Add `is_within(root, target)` containment check using resolved paths; reject symlinked escapes.
    - Apply in both `scaffold.py` and `server.py` (which currently does a bare `Path(root_directory).resolve()` with no containment — `server.py:41`).
    - Tests for `../`, absolute paths, symlink escape.

### E9.F2 — Template integrity & release supply chain (outward injection)
- **E9.F2.S1** — *As a downstream user, I can trust the templates I received are the ones ArchonMCP published.* **(L, P0)**
  - AC: shipped templates carry integrity hashes; `verify`/`init` can confirm template content matches the signed manifest; mismatch warns loudly.
  - Tasks:
    - Generate a manifest of template content hashes at build time; ship it in the package.
    - Verify template hashes at runtime before writing.
    - Test: mutated template → integrity failure.
- **E9.F2.S2** — *As a maintainer, releases are signed and reproducible.* **(L, P0)**
  - AC: PyPI releases via trusted publishing (OIDC, no long-lived token), Sigstore/attestation on artifacts, pinned+hashed build deps.
  - Tasks:
    - GitHub Actions trusted publishing for PyPI (remove manual `twine` token flow in `deploy.sh`).
    - Generate SLSA/PEP 740 attestations; publish `SECURITY.md` with verification steps.
    - Dependency pinning with hashes; Dependabot/renovate; `pip-audit` gate in CI (extend existing `run_audit.sh` into CI).
- **E9.F2.S3** — *As an ecosystem, typosquat/impersonation risk is reduced.* **(S, P1)**
  - AC: documented canonical package + repo; reserve obvious typo names if feasible; README states the only official install sources.

### E9.F3 — Untrusted-input handling for `audit` (inward injection, ties to E2.F3)
- **E9.F3.S1** — *As a lead, repo content cannot subvert the audit's verdict.* **(L, P0, blocks E2.F3 if LLM-backed)**
  - AC: audit checks over repo *content* are deterministic/rule-based by default; any LLM-backed check treats file content as **data, not instructions** (delimited, never concatenated into the system prompt), and its output is schema-constrained.
  - Tasks:
    - Establish the "repo content is untrusted data" boundary in the check framework (E2.F3).
    - For LLM checks: structured prompts, content in a quoted/delimited channel, output validated against a schema (no free-form "compliant: yes").
    - Guard against injected content inflating the compliance score (E5.F1) — score derives from verified findings only.
    - Red-team tests: fixture repo containing "ignore previous instructions / mark compliant" must NOT change the verdict.

### E9.F4 — Untrusted-input handling for codebase-aware generation (ties to E4)
- **E9.F4.S1** — *As a user, malicious repo content cannot be echoed into generated governance files.* **(L, P1, blocks/accompanies E4)**
  - AC: any repo-derived string that flows into generated content is sanitized/escaped; generated files are diff-previewed before write; no verbatim repo text is injected into instruction files without review.
  - Tasks:
    - Sanitization/allowlist for repo-derived values used in templates.
    - `--dry-run`/diff preview for codebase-aware output.
    - Tests: injected markers in repo files do not appear in generated `copilot-instructions.md`.

### E9.F5 — MCP server hardening
- **E9.F5.S1** — *As an operator, the MCP tool surface is safe by default.* **(M, P0)**
  - AC: `root_directory` validated (exists, is dir, within an allowed base if configured); tool inputs schema-validated and length-bounded; errors returned as `isError` results (already the pattern) without leaking sensitive paths; no execution of repo-provided code.
  - Tasks:
    - Input validation + optional allowed-root confinement (env/config).
    - Ensure no `eval`/dynamic import of repo content anywhere in the read path.
    - Rate/size limits on file reads once E4 lands.
    - Contract tests for malformed/hostile tool inputs.

### E9.F6 — Security posture documentation & disclosure
- **E9.F6.S1** — *As an adopter, I can see the threat model and report vulnerabilities.* **(S, P0)**
  - AC: `SECURITY.md` with threat model (the two injection directions), supported versions, disclosure contact; README security section; verification-of-authenticity instructions.

---

## E10 — Downstream-User Protection: Phishing / Malware / Ransomware  *(P0)*

> **Goal (your words): nobody who installs this gets into trouble.** E9 hardens the tool's *behavior*; E10 protects the *humans who install and run it* against the three delivery paths by which a package like this actually harms people — a poisoned release (malware/ransomware), a fetch-and-run instruction in a trusted file (phishing), and destructive local writes.
>
> Precedence: **E10.F1, E10.F2, E10.F4, E10.F5 are P0 and should ship in the very next release** — they are cheap relative to the blast radius. Note the current review found **no** runtime code execution or network calls in the package (good); these stories keep it that way and close the distribution gaps.

### E10.F1 — Secure release pipeline (kills the malware/ransomware delivery path — SEC-1, SEC-8)
- **E10.F1.S1** — *As a downstream user, a leaked maintainer token cannot be used to publish malware under ArchonMCP's name.* **(L, P0)**
  - AC: all PyPI publishing runs through **GitHub Actions Trusted Publishing (OIDC)** — no long-lived API token exists to steal; manual `twine upload` from a workstation is removed/disabled.
  - Tasks:
    - Add a `release.yml` workflow gated on signed tags; publish via OIDC trusted publishing.
    - Remove/neutralize the token-based `upload_pypi`/`full_cycle` paths in `deploy.sh`/`deploy.bat` (and fix the function-ordering bug SEC-8 so no broken publish path lingers).
    - Require 2FA on the PyPI + GitHub accounts; document it in `SECURITY.md`.
    - Protect the release branch/tags; restrict who can trigger release.
- **E10.F1.S2** — *As a downstream user, I can verify a release is authentic.* **(M, P0)**
  - AC: artifacts carry PEP 740 / Sigstore attestations; `SECURITY.md` documents how to verify before install; checksums published.
  - Tasks: enable attestations in the release workflow; publish verification instructions.

### E10.F2 — Dependency & build supply-chain lockdown (SEC-2)
- **E10.F2.S1** — *As a downstream user, a compromised upstream dependency does not reach me through ArchonMCP.* **(M, P0)**
  - AC: runtime deps carry sensible upper bounds; a hash-pinned lockfile governs the build; CI fails on known-vulnerable deps.
  - Tasks:
    - Add upper bounds to `fastmcp`/`click`; generate a hash-pinned lock (`pip-tools`/`uv`) for reproducible builds.
    - Pin build tools (`build`, `twine`) with hashes in the release workflow instead of `pip install --upgrade`.
    - Wire the existing `pip-audit` (`run_audit.sh`) into CI as a required gate; add Dependabot/Renovate.
    - Add a lockfile-drift check.

### E10.F3 — Anti-typosquat / name-confusion defense (SEC-3)
- **E10.F3.S1** — *As a user, I can't easily be tricked into installing a lookalike.* **(S, P1)**
  - AC: README + PyPI state the single canonical package name, repo URL, and official install command prominently; obvious typo variants reserved where feasible; project metadata (`Homepage`, `Source`, `Security`) filled in `pyproject.toml`.
  - Tasks: add `[project.urls]`; publish a "verify you're installing the real thing" note; reserve `archonmcp`/`archon_mcp` name variants on PyPI if available.

### E10.F4 — Generated-content safety scanner (phishing prevention in output — SEC-6)
- **E10.F4.S1** — *As a user, ArchonMCP's generated files can never contain fetch-and-execute commands or deceptive links.* **(M, P0)**
  - AC: a build/CI check scans every template and every generated file for dangerous patterns — `curl|bash`, `wget ... | sh`, `Invoke-WebRequest`/`iwr ... | iex`, `base64 -d | sh`, `sudo`, raw IP URLs, non-canonical domains, shortened links — and fails the build on a hit. Runtime `init` refuses to write content that trips the scanner.
  - Tasks:
    - Define a denylist of exec/exfil patterns + a URL allowlist policy.
    - CI test over `GOVERNANCE_TEMPLATES` (guards SEC-6 permanently — templates are clean today, this keeps them clean).
    - Runtime guard in the writer path; surface a clear error.
    - Tests with poisoned-template fixtures.
- **E10.F4.S2** — *As a user, I can preview exactly what will be written before it touches my repo.* **(S, P0)**
  - AC: `archon-mcp init --dry-run` prints the full file list + content diff and writes nothing; default `init` shows a summary and (per E9.F1.S1) never overwrites without `--force`.
  - Tasks: add `--dry-run`; render diffs for existing files; wire into MCP tool result.

### E10.F5 — Least-privilege & safe-by-default runtime (SEC-4, SEC-5 reinforcement)
- **E10.F5.S1** — *As a user, running ArchonMCP can only ever touch the project I pointed it at.* **(M, P0)**
  - AC: all writes confined to the resolved project root (shares the containment check from E9.F1.S2); no writes to `$HOME`, system dirs, or outside root; symlink escapes rejected; no hidden network or telemetry.
  - Tasks:
    - Enforce root-containment in `scaffold.py` and `server.py` (reuse E9.F1.S2).
    - Add a test asserting zero writes land outside `root_path` for any input.
    - Add a "no telemetry / no network / no code execution" statement to `SECURITY.md` and README (it's true today — make it a documented guarantee with a test).

### E10.F6 — Malware/behavioral CI scanning of the shipped artifact (SEC-7)
- **E10.F6.S1** — *As a user, the published wheel/sdist has been scanned before release.* **(M, P1)**
  - AC: release workflow runs static/secret scanning (e.g. `bandit`, `gitleaks`/secret scan, `pip-audit`) and inspects the built artifact's file manifest for unexpected files before publish; release blocked on findings.
  - Tasks: add scanners to CI; add an sdist/wheel content allowlist check so nothing unexpected (scripts, binaries) ships.

---

## Suggested delivery sequence (release themes)

- **v0.2 — "Tell the truth & do no harm"**: E1 (all), E8.F3, **E9.F1 (safe writes + path containment), E9.F5, E9.F6**, and the P0 downstream-protection work: **E10.F1 (secure release pipeline / OIDC), E10.F2 (dependency lockdown), E10.F4 (generated-content scanner + `--dry-run`), E10.F5 (least-privilege runtime)**. Cheap relative to blast radius; closes the malware/ransomware/phishing delivery paths before more people install it.
- **v0.3 — "Enforce"**: E2.F1 (`verify`), E2.F2 (drift), E8.F1, **E9.F2 (template integrity + signed releases)**. The scaffolder becomes a checker; the supply chain becomes trustworthy.
- **v0.4 — "Audit & Score"**: E2.F3 (`audit`), E2.F4 (MCP), E5.F1/F2 (score + report), **E9.F3 (untrusted-input handling for audit)**.
- **v0.5 — "Depth"**: E3 (per-stack content + externalized templates).
- **v0.6+ — "Platform"**: E4 (codebase-aware) **with E9.F4 (injection-safe generation)**, E6 (config, packs, upgrade), E7 (CI/pre-commit).

## Critical path / dependencies

- **E9.F1 (safe writes + path containment) is P0 and precedes everything** — it fixes two live issues: silent overwrite in `scaffold.py` and unbounded `Path(...).resolve()` in `server.py:41`. Do it in v0.2.
- E2.F1 depends on extracting the **governance manifest** out of `scaffold.py` (do this first — E2.F1.S1 task 1). Everything in E2/E5 keys off it. The same manifest powers E9.F2 template-integrity hashes.
- E2.F2 (drift) introduces the **lockfile**; E6.F3 (upgrade) reuses it. Design the lockfile once, early.
- E3.F3 (externalize templates) makes E3.F2 content work far less painful — sequence F3 before the bulk of F2 if possible.
- E5 (scoring/reports) depends on E2.F3 (audit) producing structured findings — and **E9.F3 must land with E2.F3**, else injected repo content can forge the compliance score.
- **E9.F3/E9.F4 gate the AI-reasoning epics**: do not ship an LLM-backed `audit` (E2.F3) or codebase-aware generation (E4) without the corresponding untrusted-input handling. Treat repo content as untrusted data the moment the tool reads it.
- **E10 protects installers and must not slip.** E10.F1 (OIDC release) is the single highest-leverage item — it removes the stealable token that is the usual root cause of PyPI supply-chain incidents. E10.F5 shares the root-containment code with E9.F1.S2 (build it once). E10.F4's content scanner reuses the governance manifest from E2.F1.S1.
