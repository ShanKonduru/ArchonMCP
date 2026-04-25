# Naming Conventions Bootstrap

## Stack: Generic

## Universal Principles
- Be consistent within your chosen language/framework conventions
- Prefer explicit, descriptive names over short abbreviations
- Align with the official style guide for each language in your stack

## Code Symbols

| Symbol Type | Convention | Notes |
|---|---|---|
| Classes / Types | `PascalCase` | Across most languages |
| Functions / Methods | `camelCase` or `snake_case` | Match language idiom |
| Constants | `SCREAMING_SNAKE_CASE` | Widely accepted |
| Boolean variables | `isX`, `hasX`, `canX` | Prefix for clarity |
| Event handlers | `handleX` or `onX` | Be consistent |

## Files & Folders
- Group by feature/domain, not by type
- Use lowercase with separators appropriate to the language
- Test files co-located: `module.test.ts` or `test_module.py`

## Database / Storage
- Tables/collections: plural noun
- Primary key: `id`
- Foreign keys: `{entity}_id`
- Timestamps: `created_at`, `updated_at`

## API Endpoints
- Use plural nouns: `/resources`
- Use kebab-case: `/user-profiles`
- Version APIs: `/api/v1/resources`

## Environment Variables
- `SCREAMING_SNAKE_CASE` universally
- Prefix by service: `DB_HOST`, `REDIS_URL`, `AUTH_SECRET`

## Git Conventions
- Branches: `feature/short-description`, `fix/issue-description`
- Commits (Conventional Commits): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
