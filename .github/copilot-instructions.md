# ArchonMCP Governance Rules

## Project Context
This project uses ArchonMCP for governance and AI-assisted development.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing components before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
- Follow language and framework conventions
- Maintain consistent code style across the project
- Document significant decisions
- Ensure adequate test coverage

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] Code follows established patterns
- [ ] Security implications considered
- [ ] Tests pass with adequate coverage
- [ ] ADR created for significant decisions
