# Security Policy

ArchonMCP generates governance files that AI coding agents (Cursor, Claude,
Copilot, Windsurf, VS Code AI) and humans read and follow. That places it on a
trust boundary in the AI supply chain, so we take the security of the package
and its output seriously.

## Runtime guarantees

These properties are enforced by the code and covered by tests:

- **No code execution.** ArchonMCP contains no `eval`, `exec`, `subprocess`,
  `os.system`, or dynamic import. It cannot be coerced into running code from a
  repository it inspects.
- **No network access.** `init`, `detect`, and `server` make no outbound network
  calls. Nothing is fetched at runtime.
- **No telemetry.** ArchonMCP collects and transmits nothing.
- **Confined writes.** Every file ArchonMCP writes is confined to the project
  root you point it at. Absolute paths, `..` traversal, and symlink escapes are
  rejected (`archon_mcp.pathsafe`).
- **No silent overwrite.** Existing files are preserved by default and reported
  as skipped. Overwriting requires the explicit `--force` flag (CLI) or
  `force=true` (MCP tool). Use `--dry-run` / `dry_run=true` to preview first.

## Verifying you have the authentic package

- The only official sources are the PyPI project **`archon-mcp`** and the GitHub
  repository **`ShanKonduru/ArchonMCP`**. Beware of typosquats
  (e.g. `archonmcp`, `archon_mcp` as a *distribution* name).
- Releases are published from CI using PyPI **Trusted Publishing (OIDC)** — there
  is no long-lived API token that could be stolen to publish on our behalf.
- Release artifacts carry provenance attestations. Verify before installing in
  sensitive environments.

## Supported versions

Security fixes are applied to the latest released version. Please upgrade to the
latest version before reporting an issue.

## Reporting a vulnerability

Please report suspected vulnerabilities privately via GitHub Security Advisories
("Report a vulnerability" on the repository's **Security** tab) rather than a
public issue. Include reproduction steps and impact. We aim to acknowledge
reports within a few business days.

Do not include working exploit payloads against third parties or any real
secrets in your report.
