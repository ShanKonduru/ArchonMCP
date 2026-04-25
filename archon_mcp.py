#!/usr/bin/env python3
"""
ArchonMCP: A governance framework server for AI-assisted development.
Provides tools to initialize and manage project governance structures.

Supports two modes of operation:
1. CLI: Local execution for direct governance initialization
2. MCP Server: Runs as MCP-compatible server for IDE integration
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import click
import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult


# All supported stack profiles
VALID_STACKS = [
    "React-FastAPI-Postgres",
    "Next.js-Django-Postgres",
    "Vue-Express-MongoDB",
    "Angular-SpringBoot-MySQL",
    "React-Node-MongoDB",
    "Generic",
]

# Template Engine: Dictionary-based templates for all governance files
GOVERNANCE_TEMPLATES = {
    "copilot_instructions": {
        "React-FastAPI-Postgres": """# ArchonMCP Governance Rules

## Project Context
This is a React-FastAPI-Postgres stack project with AI-assisted development enabled.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing components before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
1. **TypeScript/React**: Strict typing, component composition, hooks best practices
2. **FastAPI**: Type hints on all endpoints, proper exception handling, OpenAPI compliance
3. **PostgreSQL**: Schema versioning, migration scripts, query optimization

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] Code follows established patterns
- [ ] Security implications considered
- [ ] Database schema changes documented
- [ ] Tests pass with >80% coverage
- [ ] ADR created for significant decisions
""",
        "Next.js-Django-Postgres": """# ArchonMCP Governance Rules

## Project Context
This is a Next.js + Django REST Framework + PostgreSQL project with AI-assisted development enabled.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing components before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
1. **TypeScript/Next.js**: App Router conventions, Server vs Client components, strict typing
2. **Django/DRF**: Serializers for all I/O, class-based views preferred, ORM-only data access
3. **PostgreSQL**: Django migrations with reversible operations, query optimization, connection pooling

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] Server vs Client component boundary is correct
- [ ] DRF serializers validate all inputs
- [ ] Django migrations are reversible
- [ ] Tests pass with >80% coverage
- [ ] ADR created for significant decisions
""",
        "Vue-Express-MongoDB": """# ArchonMCP Governance Rules

## Project Context
This is a Vue 3 + Express + MongoDB project with AI-assisted development enabled.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing components before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
1. **Vue 3**: Composition API with `<script setup>`, TypeScript, Pinia for state management
2. **Express**: Middleware-first design, input validation (Zod/Joi), structured async/await
3. **MongoDB**: Mongoose schemas with validation, indexes on all query fields

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] Vue components use Composition API with `<script setup>`
- [ ] Express routes validate inputs before processing
- [ ] Mongoose schemas define indexes and required fields
- [ ] Tests pass with >80% coverage
- [ ] ADR created for significant decisions
""",
        "Angular-SpringBoot-MySQL": """# ArchonMCP Governance Rules

## Project Context
This is an Angular + Spring Boot + MySQL project with AI-assisted development enabled.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing modules before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
1. **Angular**: Standalone components, RxJS operators, strict TypeScript, lazy-loaded routes
2. **Spring Boot**: RESTful controllers with DTOs, Spring Security, JPA repositories
3. **MySQL**: Flyway versioned migrations, JPA entity design, query optimization

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] Angular services encapsulate all HTTP calls
- [ ] Spring Boot controllers use DTOs (not entities directly)
- [ ] Flyway migrations are versioned and reversible
- [ ] Tests pass with >80% coverage
- [ ] ADR created for significant decisions
""",
        "React-Node-MongoDB": """# ArchonMCP Governance Rules

## Project Context
This is a React + Node.js/Express + MongoDB (MERN) project with AI-assisted development enabled.

## AI Assistant Expectations
- Follow all patterns established in `/docs/adr/` (Architecture Decision Records)
- Reference existing components before creating new ones
- Propose changes through pull requests with clear descriptions
- Use the security and migration runbooks from `.github/skills/`

## Code Quality Standards
1. **React**: Functional components, custom hooks, TypeScript strict mode, React Query for server state
2. **Node/Express**: Async/await middleware, input validation, structured error handling
3. **MongoDB**: Mongoose schemas with validation and indexes, aggregation for complex queries

## Governance Artifacts
- **Skills**: Executable runbooks for common tasks (`.github/skills/`)
- **Prompts**: Custom slash commands for workflow acceleration (`.github/prompts/`)
- **ADRs**: Architecture decisions and their rationale (`/docs/adr/`)
- **Stories**: Feature documentation and acceptance criteria (`/docs/stories/`)

## Review Checklist
- [ ] React components are functional with correct hook usage
- [ ] Express routes validate all inputs
- [ ] Mongoose schemas enforce data integrity
- [ ] Tests pass with >80% coverage
- [ ] ADR created for significant decisions
""",
        "Generic": """# ArchonMCP Governance Rules

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
""",
    },
    "security_skill": {
        "React-FastAPI-Postgres": """# Security Runbook

## Purpose
This runbook provides a structured approach to implementing security best practices.

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review API authentication strategy
- [ ] Audit database access patterns

## Implementation Steps

### 1. Frontend Security (React)
- Implement CORS policies
- Use environment variables for API endpoints
- Sanitize user inputs
- Implement CSRF protection
- Use secure session management

### 2. Backend Security (FastAPI)
- Implement JWT or OAuth2 authentication
- Add rate limiting on endpoints
- Validate all inputs server-side
- Use prepared statements for database queries
- Implement proper error handling without leaking information

### 3. Database Security (PostgreSQL)
- Use role-based access control (RBAC)
- Encrypt sensitive columns
- Implement row-level security (RLS) where applicable
- Regular security audits of permissions
- Use secrets management for credentials

## Post-Implementation Verification
- [ ] Security tests written and passing
- [ ] Dependency audit complete
- [ ] Code review with security focus
- [ ] Penetration testing considered
""",
        "Next.js-Django-Postgres": """# Security Runbook

## Purpose
This runbook provides a structured approach to security for Next.js-Django-Postgres.

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review authentication strategy
- [ ] Audit database access patterns

## Implementation Steps

### 1. Frontend Security (Next.js)
- Configure CSP headers in `next.config.js`
- Use `next/headers` for secure cookie management
- Store API URLs in environment variables only
- Use `middleware.ts` for route-level auth guards

### 2. Backend Security (Django)
- Enable `SecurityMiddleware` and `SECURE_SSL_REDIRECT`
- Use `djangorestframework-simplejwt` for authentication
- Apply `IsAuthenticated` permission on all private views
- Rate-limit with `django-ratelimit`

### 3. Database Security (PostgreSQL)
- Use role-based access control (RBAC)
- Implement row-level security (RLS) where applicable
- Encrypt sensitive columns with `pgcrypto`
- Use secrets management for `DATABASE_URL`

## Post-Implementation Verification
- [ ] `python manage.py check --deploy` passes
- [ ] `pip-audit` shows no vulnerabilities
- [ ] Security tests written and passing
- [ ] Code review with security focus
""",
        "Vue-Express-MongoDB": """# Security Runbook

## Purpose
This runbook provides a structured approach to security for Vue-Express-MongoDB.

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review authentication strategy
- [ ] Audit data access patterns

## Implementation Steps

### 1. Frontend Security (Vue 3)
- Use `DOMPurify` for any HTML rendering from user input
- Store tokens in `httpOnly` cookies, not localStorage
- Validate env variables at build time

### 2. Backend Security (Express)
- Add `helmet()` middleware for secure HTTP headers
- Use `cors()` with explicit origin allowlist
- Add `express-rate-limit` on auth and API routes
- Validate inputs with `zod` or `joi` before processing
- Hash passwords with `bcrypt` (minimum 12 rounds)

### 3. Database Security (MongoDB)
- Enable authentication; use a dedicated least-privilege app user
- Use Mongoose schema validation as a data contract
- Enable TLS for all MongoDB connections

## Post-Implementation Verification
- [ ] `npm audit` passes with no high/critical issues
- [ ] Helmet headers verified with security scanner
- [ ] Security tests written and passing
- [ ] Code review with security focus
""",
        "Angular-SpringBoot-MySQL": """# Security Runbook

## Purpose
This runbook provides a structured approach to security for Angular-SpringBoot-MySQL.

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review authentication strategy
- [ ] Audit database access patterns

## Implementation Steps

### 1. Frontend Security (Angular)
- Use `DomSanitizer` for any dynamic HTML binding
- Add `HttpInterceptor` to attach JWT to every API request
- Protect routes with `CanActivate` guards
- Store tokens in memory or `httpOnly` cookies

### 2. Backend Security (Spring Boot)
- Configure Spring Security with JWT or OAuth2
- Enable method-level security with `@PreAuthorize`
- Validate all inputs with `@Valid` (Jakarta Bean Validation)
- Use `BCryptPasswordEncoder` for passwords

### 3. Database Security (MySQL)
- Create a dedicated app user with minimal privileges
- Use Spring Data JPA parameterized queries
- Encrypt sensitive columns at the application layer
- Use Flyway for all schema changes

## Post-Implementation Verification
- [ ] OWASP dependency check passes
- [ ] Security tests written and passing
- [ ] Spring Security configuration reviewed
- [ ] Code review with security focus
""",
        "React-Node-MongoDB": """# Security Runbook

## Purpose
This runbook provides a structured approach to security for React-Node-MongoDB (MERN).

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review authentication strategy
- [ ] Audit data access patterns

## Implementation Steps

### 1. Frontend Security (React)
- Store tokens in `httpOnly` cookies, never in localStorage
- Use environment variables for API base URLs only
- Sanitize user-generated content with `DOMPurify`

### 2. Backend Security (Node/Express)
- Add `helmet()` for secure HTTP headers
- Use `express-rate-limit` on auth and sensitive endpoints
- Validate all inputs with `express-validator` or `zod`
- Hash passwords with `bcrypt` (minimum 12 rounds)
- Use JWT with short expiry and refresh token rotation

### 3. Database Security (MongoDB)
- Enable authentication and use a least-privilege app user
- Use Mongoose schema validation as a data contract
- Enable TLS for MongoDB Atlas connections

## Post-Implementation Verification
- [ ] `npm audit` passes with no high/critical issues
- [ ] Security tests written and passing
- [ ] Helmet headers verified
- [ ] Code review with security focus
""",
        "Generic": """# Security Runbook

## Purpose
This runbook provides a structured approach to implementing security best practices.

## Pre-Implementation Checklist
- [ ] List all external dependencies
- [ ] Identify sensitive data handling points
- [ ] Review authentication strategy
- [ ] Audit access patterns

## Implementation Steps

### 1. Authentication & Authorization
- Implement secure authentication mechanism
- Use role-based or attribute-based access control
- Protect sensitive endpoints
- Implement session management securely

### 2. Data Protection
- Validate all user inputs
- Sanitize data output
- Encrypt sensitive data at rest and in transit
- Use secrets management for credentials

### 3. Infrastructure Security
- Keep dependencies up to date
- Monitor for security vulnerabilities
- Implement logging and audit trails
- Use environment-specific configurations

## Post-Implementation Verification
- [ ] Security tests written and passing
- [ ] Dependency audit complete
- [ ] Code review with security focus
""",
    },
    "migration_skill": {
        "React-FastAPI-Postgres": """# Migration Runbook

## Purpose
This runbook provides a structured approach to implementing data migrations and schema changes.

## Pre-Migration Planning
- [ ] Document current schema state
- [ ] Identify breaking changes
- [ ] Plan rollback strategy
- [ ] Notify stakeholders
- [ ] Backup production database

## Migration Steps

### 1. Schema Preparation
- Create migration script with version number (e.g., `001_initial_schema.sql`)
- Use reversible migration pattern
- Test migration on development database
- Document any manual data transformation needed

### 2. Data Migration
- Implement data validation checks
- Use transactions for atomicity
- Include rollback procedures
- Monitor migration progress

### 3. Deployment
- Apply migration in staging environment first
- Run comprehensive integration tests
- Verify data integrity
- Deploy to production during maintenance window
- Monitor application logs for issues

## Post-Migration Validation
- [ ] All data migrated correctly
- [ ] Application functionality verified
- [ ] Performance baseline established
- [ ] Update documentation
""",
        "Next.js-Django-Postgres": """# Migration Runbook

## Purpose
Structured approach to Django migrations and PostgreSQL schema changes.

## Pre-Migration Planning
- [ ] Run `python manage.py showmigrations` to document current state
- [ ] Identify breaking changes (column renames, NOT NULL additions)
- [ ] Plan rollback with reverse migration functions
- [ ] Backup production database with `pg_dump`

## Migration Steps

### 1. Create the Migration
```bash
python manage.py makemigrations app_name --name descriptive_name
# Always review the generated file before applying
```

### 2. Write Data Migrations (if needed)
```python
from django.db import migrations

def migrate_forward(apps, schema_editor):
    MyModel = apps.get_model('myapp', 'MyModel')
    MyModel.objects.filter(field=None).update(field='default')

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(migrate_forward, migrations.RunPython.noop),
    ]
```

### 3. Test and Apply
```bash
python manage.py migrate  # staging first, then production
```

## Post-Migration Validation
- [ ] `showmigrations` shows all applied
- [ ] Application functionality verified
- [ ] Query performance checked with `EXPLAIN ANALYZE`
""",
        "Vue-Express-MongoDB": """# Migration Runbook

## Purpose
Structured approach to MongoDB schema evolution and data migrations.

## Pre-Migration Planning
- [ ] Document current schema via Mongoose model definitions
- [ ] Prefer additive changes (backward compatible)
- [ ] Plan rollback strategy
- [ ] Backup with `mongodump` or Atlas snapshot

## Migration Steps

### 1. Schema Evolution Strategy
Prefer additive changes. Track versions with a `schemaVersion` field.

### 2. Use migrate-mongo
```bash
npx migrate-mongo create descriptive-name
npx migrate-mongo up    # staging
npx migrate-mongo down  # rollback
```

### 3. Data Transformation Example
```javascript
module.exports = {
  async up(db) {
    await db.collection('users').updateMany(
      { legacyField: { $exists: true } },
      { $rename: { legacyField: 'newField' } }
    );
  },
  async down(db) {
    await db.collection('users').updateMany(
      { newField: { $exists: true } },
      { $rename: { newField: 'legacyField' } }
    );
  },
};
```

## Post-Migration Validation
- [ ] Document counts match pre-migration state
- [ ] Application functionality verified
- [ ] Indexes rebuilt if needed
""",
        "Angular-SpringBoot-MySQL": """# Migration Runbook

## Purpose
Structured approach to Flyway database migrations for Spring Boot + MySQL.

## Pre-Migration Planning
- [ ] Run `flyway info` to document current schema version
- [ ] Identify breaking changes
- [ ] Plan rollback (Flyway undo or manual SQL)
- [ ] Backup production with `mysqldump`

## Migration Steps

### 1. Create Flyway Migration Script
Naming: `V{version}__{description}.sql`
```
src/main/resources/db/migration/V3__add_user_phone.sql
```

```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL;
CREATE INDEX idx_users_phone ON users(phone);
```

### 2. Apply and Verify
```bash
./mvnw flyway:info     # Check pending
./mvnw flyway:migrate  # Apply to staging
./mvnw spring-boot:run # Verify startup
```

## Post-Migration Validation
- [ ] `flyway info` shows all applied
- [ ] Health endpoint responds correctly
- [ ] JPA entity matches new schema
- [ ] Query performance verified
""",
        "React-Node-MongoDB": """# Migration Runbook

## Purpose
Structured approach to MongoDB schema evolution for the MERN stack.

## Pre-Migration Planning
- [ ] Document current Mongoose schema versions
- [ ] Prefer additive changes
- [ ] Plan rollback strategy
- [ ] Backup with `mongodump` or Atlas snapshot

## Migration Steps

### 1. Schema Version Tracking
```javascript
const userSchema = new Schema({
  schemaVersion: { type: Number, default: 1 },
  // ...fields
});
```

### 2. Use migrate-mongo
```bash
npx migrate-mongo create add-user-preferences
npx migrate-mongo up    # staging
npx migrate-mongo down  # rollback
```

### 3. Deployment Order
- Run migration BEFORE deploying new code
- Keep old fields during blue-green transition
- Remove legacy fields in a follow-up migration

## Post-Migration Validation
- [ ] Document counts match pre-migration state
- [ ] Application functionality verified
- [ ] New indexes built and not impacting writes
""",
        "Generic": """# Migration Runbook

## Purpose
This runbook provides a structured approach to implementing data migrations and changes.

## Pre-Migration Planning
- [ ] Document current state
- [ ] Plan rollback strategy
- [ ] Notify stakeholders
- [ ] Backup data

## Migration Steps

### 1. Change Planning
- Document the changes needed
- Create change scripts
- Test on development environment
- Document rollback procedures

### 2. Change Implementation
- Validate changes before applying
- Use transactions where possible
- Include verification steps
- Monitor change progress

### 3. Deployment
- Test in staging environment
- Run validation checks
- Deploy to production
- Monitor for issues

## Post-Migration Validation
- [ ] Changes applied correctly
- [ ] Functionality verified
- [ ] Documentation updated
""",
    },
    "done_skill": {
        "React-FastAPI-Postgres": """# Done Runbook

## Purpose
This runbook defines the criteria for considering a feature or task complete.

## Definition of Done

### Code Quality
- [ ] Code passes linting checks
- [ ] Tests written and passing (>80% coverage)
- [ ] Code reviewed by at least one peer
- [ ] No console errors or warnings
- [ ] Performance benchmarks met

### Documentation
- [ ] Feature documented in `docs/stories/`
- [ ] API documentation updated (if applicable)
- [ ] Architecture decision documented in `docs/adr/` (if significant)
- [ ] User-facing documentation updated

### Testing
- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Edge cases considered

### Security & Accessibility
- [ ] Security review completed
- [ ] Accessibility standards met (WCAG 2.1 AA for UI)
- [ ] Sensitive data properly handled
- [ ] Input validation implemented

### Deployment
- [ ] Code merged to main branch
- [ ] Staging deployment successful
- [ ] No breaking changes to APIs
- [ ] Migration scripts (if any) tested and documented
""",
        "Next.js-Django-Postgres": """# Done Runbook

## Definition of Done

### Code Quality
- [ ] `tsc --noEmit` passes (Next.js)
- [ ] `ruff` / `flake8` pass (Django)
- [ ] Tests written and passing (>80% coverage)
- [ ] Code reviewed by at least one peer

### Documentation
- [ ] Feature documented in `docs/stories/`
- [ ] DRF API schema updated (drf-spectacular)
- [ ] Architecture decision documented in `docs/adr/` (if significant)

### Testing
- [ ] Jest + React Testing Library (frontend)
- [ ] `pytest-django` tests for all new views/serializers
- [ ] Playwright E2E happy path covered

### Security & Accessibility
- [ ] `python manage.py check --deploy` passes
- [ ] `pip-audit` + `npm audit` clean
- [ ] WCAG 2.1 AA standards met

### Deployment
- [ ] Staging deployment successful
- [ ] Django migrations applied and verified
- [ ] No breaking API changes (or version bumped)
""",
        "Vue-Express-MongoDB": """# Done Runbook

## Definition of Done

### Code Quality
- [ ] `vue-tsc --noEmit` passes
- [ ] ESLint + Prettier pass
- [ ] Tests written and passing (>80% coverage)
- [ ] No `console.log` in production code

### Documentation
- [ ] Feature documented in `docs/stories/`
- [ ] OpenAPI spec updated for new endpoints
- [ ] Architecture decision in `docs/adr/` (if significant)

### Testing
- [ ] Vitest + Vue Testing Library (frontend)
- [ ] Jest/Supertest integration tests (Express)
- [ ] Playwright E2E happy path covered

### Security & Accessibility
- [ ] `npm audit` shows no high/critical vulnerabilities
- [ ] WCAG 2.1 AA standards met
- [ ] Zod/Joi validation on all Express routes

### Deployment
- [ ] Staging deployment successful
- [ ] MongoDB migrations applied via migrate-mongo
- [ ] No breaking API changes
""",
        "Angular-SpringBoot-MySQL": """# Done Runbook

## Definition of Done

### Code Quality
- [ ] `ng build --configuration production` passes
- [ ] Java Checkstyle/SpotBugs passes
- [ ] Tests written and passing (>80% coverage)
- [ ] Code reviewed by at least one peer

### Documentation
- [ ] Feature documented in `docs/stories/`
- [ ] Swagger/OpenAPI spec updated (Springdoc)
- [ ] Architecture decision in `docs/adr/` (if significant)

### Testing
- [ ] Jest + Angular Testing Library (frontend)
- [ ] JUnit 5 + MockMvc integration tests (backend)
- [ ] Cypress or Playwright E2E happy path

### Security & Accessibility
- [ ] OWASP dependency check passes
- [ ] WCAG 2.1 AA standards met
- [ ] `@Valid` on all controller inputs

### Deployment
- [ ] Staging deployment successful
- [ ] Flyway migration applied and verified
- [ ] No breaking API changes (or versioned)
""",
        "React-Node-MongoDB": """# Done Runbook

## Definition of Done

### Code Quality
- [ ] `tsc --noEmit` passes on frontend and backend
- [ ] ESLint + Prettier pass
- [ ] Tests written and passing (>80% coverage)
- [ ] No `console.log` in production code

### Documentation
- [ ] Feature documented in `docs/stories/`
- [ ] API documented in Swagger or README
- [ ] Architecture decision in `docs/adr/` (if significant)

### Testing
- [ ] Jest + React Testing Library (frontend)
- [ ] Supertest integration tests for all new routes
- [ ] Playwright E2E happy path covered

### Security & Accessibility
- [ ] `npm audit` shows no high/critical vulnerabilities
- [ ] WCAG 2.1 AA standards met
- [ ] Input validation on all Express routes

### Deployment
- [ ] Staging deployment successful
- [ ] MongoDB migrations applied
- [ ] No breaking API changes
""",
        "Generic": """# Done Runbook

## Purpose
This runbook defines the criteria for considering a feature or task complete.

## Definition of Done

### Code Quality
- [ ] Code passes quality checks
- [ ] Tests written and passing
- [ ] Code reviewed
- [ ] No errors or warnings

### Documentation
- [ ] Feature documented
- [ ] Architecture decisions documented (if significant)
- [ ] User-facing documentation updated

### Testing
- [ ] Tests written and passing
- [ ] Manual testing completed
- [ ] Edge cases considered

### Security
- [ ] Security considerations reviewed
- [ ] Input validation implemented
- [ ] Sensitive data properly handled

### Deployment
- [ ] Code merged
- [ ] Staging deployment successful
- [ ] No breaking changes
""",
    },
    "gap_analysis_prompt": {
        "React-FastAPI-Postgres": """# /gap-analysis Command

## Description
Analyzes the gap between current implementation and best practices for React-FastAPI-Postgres stacks.

## Usage
Type `/gap-analysis` in your AI assistant chat to:
1. Analyze code against established patterns
2. Identify missing security controls
3. Find performance optimization opportunities
4. Suggest refactoring for maintainability

## What It Checks
- React: Component structure, hooks usage, state management
- FastAPI: Endpoint design, validation, error handling
- PostgreSQL: Query optimization, schema design, indexing
- Integration: API contracts, data flow, error propagation

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
        "Next.js-Django-Postgres": """# /gap-analysis Command

## Description
Analyzes gaps for Next.js-Django-Postgres stacks.

## Usage
Type `/gap-analysis` in your AI assistant chat to audit Server vs Client component boundaries, DRF serializer coverage, Django ORM N+1 queries, and missing migration best practices.

## What It Checks
- Next.js: App Router usage, RSC vs Client split, data fetching patterns
- Django: Serializer completeness, view permissions, ORM query efficiency
- PostgreSQL: Index coverage, slow query log, connection pooling
- Integration: CORS config, API versioning, error response consistency

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
        "Vue-Express-MongoDB": """# /gap-analysis Command

## Description
Analyzes gaps for Vue-Express-MongoDB stacks.

## Usage
Type `/gap-analysis` in your AI assistant chat to audit Vue Composition API usage, Express middleware coverage, MongoDB index strategy, and Pinia store patterns.

## What It Checks
- Vue: Composition API adoption, Pinia store structure, component coupling
- Express: Route validation coverage, error middleware, async handling
- MongoDB: Index strategy, schema validation, aggregation performance
- Integration: API response consistency, error propagation

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
        "Angular-SpringBoot-MySQL": """# /gap-analysis Command

## Description
Analyzes gaps for Angular-SpringBoot-MySQL stacks.

## Usage
Type `/gap-analysis` in your AI assistant chat to audit Angular lazy loading, Spring Security config, Flyway migration coverage, and JPA N+1 issues.

## What It Checks
- Angular: Lazy loading, RxJS subscription management, change detection
- Spring Boot: DTO usage, validation annotations, security configuration
- MySQL: Flyway coverage, JPA query optimization, index strategy
- Integration: CORS, API versioning, JWT expiry handling

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
        "React-Node-MongoDB": """# /gap-analysis Command

## Description
Analyzes gaps for React-Node-MongoDB (MERN) stacks.

## Usage
Type `/gap-analysis` in your AI assistant chat to audit React component architecture, Express middleware coverage, Mongoose index strategy, and async error handling.

## What It Checks
- React: Hook usage, state management, React Query patterns
- Express: Validation middleware, error handling, route organization
- MongoDB: Mongoose schema completeness, index strategy, query optimization
- Integration: API contracts, JWT flow, error response consistency

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
        "Generic": """# /gap-analysis Command

## Description
Analyzes the gap between current implementation and best practices.

## Usage
Type `/gap-analysis` in your AI assistant chat to:
1. Analyze code against best practices
2. Identify improvement opportunities
3. Find optimization opportunities
4. Suggest refactoring for maintainability

## What It Checks
- Code quality and style
- Testing coverage
- Documentation
- Performance considerations
- Security concerns

## Output Format
- Current state assessment
- Gaps identified with priority
- Recommended improvements
- Implementation effort estimate
""",
    },
    "harden_prompt": {
        "React-FastAPI-Postgres": """# /harden Command

## Description
Guides hardening of security posture for React-FastAPI-Postgres applications.

## Usage
Type `/harden` in your AI assistant chat to:
1. Review security vulnerabilities
2. Implement security best practices
3. Add security controls
4. Document security decisions

## Security Focus Areas
- React: XSS prevention, CSRF protection, secure headers
- FastAPI: Authentication, authorization, input validation
- PostgreSQL: Row-level security, encryption, access control
- Integration: API security, data protection, audit logging

## Output Includes
- Vulnerability assessment
- Prioritized remediation steps
- Code examples for security controls
- Testing strategies for security
""",
        "Next.js-Django-Postgres": """# /harden Command

## Description
Guides hardening for Next.js-Django-Postgres applications.

## Usage
Type `/harden` in your AI assistant chat to review Django security settings, harden Next.js headers and CSP, audit PostgreSQL permissions, and document security decisions.

## Security Focus Areas
- Next.js: `next.config.js` headers, CSP, environment variable hygiene
- Django: `settings.py` security flags, `check --deploy`, DRF throttling
- PostgreSQL: RLS, encrypted columns, audit logging
- Integration: CORS allowlist, JWT configuration, session security

## Output Includes
- Vulnerability assessment
- Prioritized remediation steps
- Code examples (Django settings, Next.js config)
- Testing strategies
""",
        "Vue-Express-MongoDB": """# /harden Command

## Description
Guides hardening for Vue-Express-MongoDB applications.

## Usage
Type `/harden` in your AI assistant chat to configure Express security middleware, harden Vue frontend, secure MongoDB access, and document security decisions.

## Security Focus Areas
- Vue: Token storage, input sanitization, dependency audit
- Express: `helmet`, `cors`, `express-rate-limit`, input validation
- MongoDB: Auth, network access, field encryption
- Integration: HTTPS enforcement, JWT hardening

## Output Includes
- Vulnerability assessment
- Prioritized remediation steps
- Code examples (helmet config, rate limiters)
- Testing strategies
""",
        "Angular-SpringBoot-MySQL": """# /harden Command

## Description
Guides hardening for Angular-SpringBoot-MySQL applications.

## Usage
Type `/harden` in your AI assistant chat to review Spring Security configuration, harden Angular HTTP handling, audit MySQL permissions, and document security decisions.

## Security Focus Areas
- Angular: `HttpInterceptor`, route guards, `DomSanitizer` usage
- Spring Boot: Spring Security filters, `@PreAuthorize`, Actuator exposure
- MySQL: User privileges, TLS, Flyway permissions
- Integration: CORS, JWT secret management, CSRF tokens

## Output Includes
- Vulnerability assessment
- Prioritized remediation steps
- Code examples (Spring Security config, Angular interceptors)
- Testing strategies
""",
        "React-Node-MongoDB": """# /harden Command

## Description
Guides hardening for React-Node-MongoDB applications.

## Usage
Type `/harden` in your AI assistant chat to configure Express security middleware, harden React frontend, secure MongoDB access, and document security decisions.

## Security Focus Areas
- React: Token storage (httpOnly cookies), env variable hygiene
- Node/Express: `helmet`, rate limiting, input validation, dependency audit
- MongoDB: Authentication, network ACL, TLS connection
- Integration: HTTPS enforcement, JWT rotation, CORS configuration

## Output Includes
- Vulnerability assessment
- Prioritized remediation steps
- Code examples (helmet setup, bcrypt usage, JWT config)
- Testing strategies
""",
        "Generic": """# /harden Command

## Description
Guides hardening of security posture.

## Usage
Type `/harden` in your AI assistant chat to:
1. Review security concerns
2. Implement security improvements
3. Add security controls
4. Document security decisions

## Security Focus Areas
- Authentication and authorization
- Input validation
- Data protection
- Error handling
- Logging and monitoring

## Output Includes
- Security assessment
- Prioritized improvements
- Implementation guidance
- Testing strategies
""",
    },
    "done_prompt": {
        "React-FastAPI-Postgres": """# /done Command

## Description
Validates that work meets the Definition of Done and is ready for merge.

## Usage
Type `/done` in your AI assistant chat to:
1. Verify completion criteria met
2. Generate completion checklist
3. Identify any remaining work
4. Validate against governance standards

## Validation Checks
- Code quality: Tests, linting, coverage
- Security: Review completed, vulnerabilities addressed
- Documentation: Stories, ADRs, API docs updated
- Performance: Benchmarks met, no regressions
- Accessibility: WCAG standards met
- Integration: APIs compatible, migrations tested

## Output Includes
- Completion status
- Checklist of verification items
- Any blockers preventing merge
- Recommendations for improvement
""",
        "Next.js-Django-Postgres": """# /done Command

## Description
Validates completion for Next.js-Django-Postgres projects.

## Validation Checks
- `tsc --noEmit` + `ruff` pass
- `pytest` + `jest` coverage >80%
- `python manage.py check --deploy` passes
- `pip-audit` + `npm audit` clean
- Django migrations applied and verified
- Stories and ADRs updated

## Output Includes
- Completion status per check
- Blockers preventing merge
- Recommendations
""",
        "Vue-Express-MongoDB": """# /done Command

## Description
Validates completion for Vue-Express-MongoDB projects.

## Validation Checks
- `vue-tsc --noEmit` + ESLint pass
- Vitest + Jest coverage >80%
- `npm audit` no high/critical
- migrate-mongo status clean
- Stories and ADRs updated

## Output Includes
- Completion status per check
- Blockers preventing merge
- Recommendations
""",
        "Angular-SpringBoot-MySQL": """# /done Command

## Description
Validates completion for Angular-SpringBoot-MySQL projects.

## Validation Checks
- `ng build --configuration production` passes
- JUnit 5 + Jest coverage >80%
- OWASP dependency check passes
- Flyway info shows all applied
- Stories and ADRs updated

## Output Includes
- Completion status per check
- Blockers preventing merge
- Recommendations
""",
        "React-Node-MongoDB": """# /done Command

## Description
Validates completion for React-Node-MongoDB (MERN) projects.

## Validation Checks
- `tsc --noEmit` passes on frontend and backend
- Jest + Supertest coverage >80%
- `npm audit` no high/critical
- migrate-mongo status clean
- Stories and ADRs updated

## Output Includes
- Completion status per check
- Blockers preventing merge
- Recommendations
""",
        "Generic": """# /done Command

## Description
Validates that work meets the Definition of Done and is ready for merge.

## Usage
Type `/done` in your AI assistant chat to:
1. Verify completion criteria met
2. Generate completion checklist
3. Identify any remaining work
4. Validate against governance standards

## Validation Checks
- Code quality: Tests, linting
- Documentation: Updated
- Testing: Tests passing
- Security: Reviewed
- Integration: Verified

## Output Includes
- Completion status
- Checklist of verification items
- Any blockers preventing merge
- Recommendations
""",
    },
    "naming_bootstrap": {
        "React-FastAPI-Postgres": """# Naming Conventions Bootstrap

## Stack: React + FastAPI + PostgreSQL

## Frontend (React / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Component file | `PascalCase.tsx` | `UserProfile.tsx` |
| Hook | `useCamelCase.ts` | `useAuthState.ts` |
| Context | `PascalCaseContext.tsx` | `AuthContext.tsx` |
| Utility | `camelCase.ts` | `formatDate.ts` |
| Style module | `PascalCase.module.css` | `UserProfile.module.css` |
| Test | `ComponentName.test.tsx` | `UserProfile.test.tsx` |

| Symbol | Convention | Example |
|---|---|---|
| Component | `PascalCase` | `UserProfile` |
| Props interface | `ComponentNameProps` | `UserProfileProps` |
| Hook | `useCamelCase` | `useAuthState` |
| Event handler | `handleEventName` | `handleSubmit` |
| State variable | `camelCase` / `setCamelCase` | `isLoading` / `setIsLoading` |
| Constant | `SCREAMING_SNAKE_CASE` | `API_BASE_URL` |

## Backend (FastAPI / Python)

| Artifact | Convention | Example |
|---|---|---|
| Router | `snake_case_router.py` | `user_router.py` |
| SQLAlchemy model | `snake_case_model.py` | `user_model.py` |
| Pydantic schema | `snake_case_schema.py` | `user_schema.py` |
| Service | `snake_case_service.py` | `user_service.py` |
| Test | `test_snake_case.py` | `test_user_router.py` |

| Symbol | Convention | Example |
|---|---|---|
| Function | `snake_case` | `get_user_by_id` |
| Pydantic model | `PascalCase` | `UserCreate`, `UserResponse` |
| SQLAlchemy model | `PascalCase` | `User` |
| Constant | `SCREAMING_SNAKE_CASE` | `DEFAULT_PAGE_SIZE` |
| Route path | `snake_case` plural | `/api/v1/user_profiles` |
| Env variable | `SCREAMING_SNAKE_CASE` | `DATABASE_URL` |

## Database (PostgreSQL)

| Artifact | Convention | Example |
|---|---|---|
| Table | `snake_case` plural | `user_profiles` |
| Column | `snake_case` | `created_at`, `user_id` |
| Primary key | `id` | `id` |
| Foreign key | `{singular}_id` | `user_id`, `post_id` |
| Index | `idx_{table}_{col}` | `idx_users_email` |
| Constraint | `{table}_{col}_fk` | `posts_user_id_fk` |

## API & Git Conventions
- REST pattern: `/api/v{n}/snake_case_resources`
- Branches: `feature/short-description`, `fix/short-description`
- Commits: `feat: add user auth`, `fix: resolve login loop`, `chore: update deps`
""",
        "Next.js-Django-Postgres": """# Naming Conventions Bootstrap

## Stack: Next.js + Django REST Framework + PostgreSQL

## Frontend (Next.js / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Page (App Router) | `app/kebab-case/page.tsx` | `app/user-profile/page.tsx` |
| Layout | `app/kebab-case/layout.tsx` | `app/dashboard/layout.tsx` |
| Server component | `PascalCase.tsx` (default) | `UserList.tsx` |
| Client component | `PascalCase.tsx` + `'use client'` | `LoginForm.tsx` |
| Hook | `useCamelCase.ts` | `useAuthSession.ts` |
| Server action | `camelCaseAction.ts` | `createUserAction.ts` |
| Test | `ComponentName.test.tsx` | `LoginForm.test.tsx` |

| Symbol | Convention | Example |
|---|---|---|
| Component | `PascalCase` | `UserProfile` |
| Props interface | `ComponentNameProps` | `UserProfileProps` |
| Server action | `camelCaseAction` | `createUserAction` |
| Constant | `SCREAMING_SNAKE_CASE` | `MAX_FILE_SIZE` |

## Backend (Django / DRF / Python)

| Artifact | Convention | Example |
|---|---|---|
| Django app | `snake_case` | `user_profiles` |
| Model class | `PascalCase` singular | `UserProfile` |
| Serializer | `ModelNameSerializer` | `UserProfileSerializer` |
| View class | `ModelNameListView` | `UserProfileListView` |
| URL name | `snake_case` | `user_profile_detail` |
| Migration | `NNNN_description.py` | `0001_initial.py` |
| Model field | `snake_case` | `date_of_birth`, `created_at` |
| Env variable | `SCREAMING_SNAKE_CASE` | `SECRET_KEY`, `DATABASE_URL` |

## Database (PostgreSQL / Django ORM)

| Artifact | Convention | Example |
|---|---|---|
| Table (auto) | `{app}_{model}` | `user_profiles_userprofile` |
| Custom table (`Meta.db_table`) | `snake_case` plural | `user_profiles` |
| Column | `snake_case` | `created_at` |
| Index | `idx_{table}_{col}` | `idx_userprofile_email` |

## API & Git Conventions
- DRF Router pattern: `/api/v{n}/kebab-case-resource/`
- Branches: `feature/short-description`, `fix/short-description`
- Commits: `feat: add user profile endpoint`, `fix: serializer validation`
""",
        "Vue-Express-MongoDB": """# Naming Conventions Bootstrap

## Stack: Vue 3 + Express + MongoDB

## Frontend (Vue 3 / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| SFC Component | `PascalCase.vue` | `UserCard.vue` |
| Composable | `useCamelCase.ts` | `useAuthState.ts` |
| Pinia store | `camelCase.store.ts` | `auth.store.ts` |
| Page/View | `PascalCaseView.vue` | `UserProfileView.vue` |
| Utility | `camelCase.ts` | `formatDate.ts` |
| Test | `ComponentName.spec.ts` | `UserCard.spec.ts` |

| Symbol | Convention | Example |
|---|---|---|
| Component | `PascalCase` | `UserCard` |
| Props | `camelCase` | `userName`, `isLoading` |
| Emits | `camelCase` event | `update:modelValue` |
| Composable | `useCamelCase` | `useAuthState` |
| Pinia store | `useCamelCaseStore` | `useAuthStore` |
| Constant | `SCREAMING_SNAKE_CASE` | `API_TIMEOUT` |

## Backend (Express / Node.js / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Route file | `camelCase.routes.ts` | `user.routes.ts` |
| Controller | `camelCase.controller.ts` | `user.controller.ts` |
| Service | `camelCase.service.ts` | `user.service.ts` |
| Middleware | `camelCase.middleware.ts` | `auth.middleware.ts` |
| Mongoose model | `PascalCase.model.ts` | `User.model.ts` |
| Test | `camelCase.test.ts` | `user.routes.test.ts` |

| Symbol | Convention | Example |
|---|---|---|
| Route handler | `camelCase` | `getUserById` |
| Interface | `IPascalCase` | `IUserDocument` |
| Env variable | `SCREAMING_SNAKE_CASE` | `MONGO_URI` |
| REST endpoint | `/kebab-case` plural | `/api/v1/user-profiles` |

## Database (MongoDB / Mongoose)

| Artifact | Convention | Example |
|---|---|---|
| Collection | `camelCase` plural | `userProfiles` |
| Document field | `camelCase` | `createdAt`, `userId` |
| Mongoose model | `PascalCase` singular | `UserProfile` |
| ObjectId ref | `{entity}Id` | `authorId`, `postId` |

## API & Git Conventions
- REST pattern: `/api/v{n}/kebab-case-resources`
- Branches: `feature/short-description`, `fix/short-description`
- Commits: `feat: add user profile route`, `fix: auth middleware token check`
""",
        "Angular-SpringBoot-MySQL": """# Naming Conventions Bootstrap

## Stack: Angular + Spring Boot + MySQL

## Frontend (Angular / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Component | `kebab-case.component.ts` | `user-profile.component.ts` |
| Service | `kebab-case.service.ts` | `auth.service.ts` |
| Guard | `kebab-case.guard.ts` | `auth.guard.ts` |
| Interceptor | `kebab-case.interceptor.ts` | `jwt.interceptor.ts` |
| Model/Interface | `kebab-case.model.ts` | `user.model.ts` |
| Test | `kebab-case.spec.ts` | `user-profile.component.spec.ts` |

| Symbol | Convention | Example |
|---|---|---|
| Component class | `PascalCaseComponent` | `UserProfileComponent` |
| Service class | `PascalCaseService` | `AuthService` |
| Interface | `PascalCase` | `User`, `AuthResponse` |
| Enum | `PascalCase` | `UserRole` |
| Input property | `camelCase` | `userId` |
| Observable | `camelCase$` | `users$`, `loading$` |
| Selector | `app-kebab-case` | `app-user-profile` |

## Backend (Spring Boot / Java)

| Artifact | Convention | Example |
|---|---|---|
| Controller | `PascalCaseController.java` | `UserController.java` |
| Service | `PascalCaseService.java` | `UserService.java` |
| Repository | `PascalCaseRepository.java` | `UserRepository.java` |
| Entity | `PascalCase.java` | `User.java` |
| DTO | `PascalCaseDto.java` | `UserResponseDto.java` |
| Test | `PascalCaseTest.java` | `UserControllerTest.java` |

| Symbol | Convention | Example |
|---|---|---|
| Class | `PascalCase` | `UserService` |
| Method | `camelCase` | `findUserById` |
| Field | `camelCase` | `firstName` |
| Constant | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Package | `lowercase.dotted` | `com.myapp.user` |
| REST path | `/kebab-case` plural | `/api/v1/user-profiles` |

## Database (MySQL)

| Artifact | Convention | Example |
|---|---|---|
| Table | `snake_case` plural | `user_profiles` |
| Column | `snake_case` | `first_name`, `created_at` |
| Primary key | `id` (BIGINT) | `id` |
| Foreign key | `{singular}_id` | `user_id` |
| Index | `idx_{table}_{col}` | `idx_users_email` |
| Flyway script | `V{n}__{desc}.sql` | `V3__add_phone_column.sql` |

## API & Git Conventions
- REST pattern: `/api/v{n}/kebab-case-resources`
- Branches: `feature/short-description`, `fix/short-description`
- Commits: `feat: add user profile endpoint`, `fix: JWT expiry handling`
""",
        "React-Node-MongoDB": """# Naming Conventions Bootstrap

## Stack: React + Node.js/Express + MongoDB (MERN)

## Frontend (React / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Component | `PascalCase.tsx` | `UserProfile.tsx` |
| Hook | `useCamelCase.ts` | `useAuth.ts` |
| Page | `PascalCasePage.tsx` | `LoginPage.tsx` |
| API service | `camelCase.api.ts` | `user.api.ts` |
| Test | `ComponentName.test.tsx` | `UserProfile.test.tsx` |

| Symbol | Convention | Example |
|---|---|---|
| Component | `PascalCase` | `UserProfile` |
| Props interface | `ComponentNameProps` | `UserProfileProps` |
| Hook | `useCamelCase` | `useAuthState` |
| Event handler | `handleEventName` | `handleFormSubmit` |
| React Query key | `['camelCase', param]` | `['userProfile', userId]` |
| Constant | `SCREAMING_SNAKE_CASE` | `API_BASE_URL` |

## Backend (Node.js / Express / TypeScript)

| Artifact | Convention | Example |
|---|---|---|
| Route | `camelCase.routes.ts` | `user.routes.ts` |
| Controller | `camelCase.controller.ts` | `user.controller.ts` |
| Service | `camelCase.service.ts` | `user.service.ts` |
| Middleware | `camelCase.middleware.ts` | `auth.middleware.ts` |
| Mongoose model | `PascalCase.model.ts` | `User.model.ts` |
| Validation schema | `camelCase.schema.ts` | `user.schema.ts` |
| Test | `camelCase.test.ts` | `user.routes.test.ts` |

| Symbol | Convention | Example |
|---|---|---|
| Route handler | `camelCase` | `createUser`, `getUserById` |
| Interface | `IPascalCase` | `IUser`, `IUserDocument` |
| Env variable | `SCREAMING_SNAKE_CASE` | `MONGO_URI`, `JWT_SECRET` |
| REST endpoint | `/kebab-case` plural | `/api/v1/user-profiles` |

## Database (MongoDB / Mongoose)

| Artifact | Convention | Example |
|---|---|---|
| Collection | `camelCase` plural | `users`, `blogPosts` |
| Document field | `camelCase` | `firstName`, `createdAt` |
| Mongoose model | `PascalCase` singular | `User`, `BlogPost` |
| ObjectId ref field | `{entity}Id` | `authorId`, `postId` |

## API & Git Conventions
- REST pattern: `/api/v{n}/kebab-case-resources`
- Branches: `feature/short-description`, `fix/short-description`
- Commits: `feat: add user registration`, `fix: token refresh race condition`
""",
        "Generic": """# Naming Conventions Bootstrap

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
""",
    },
}


def detect_tech_stack(root_path: Path) -> str:
    """
    Detect the tech stack from files in the root directory.

    Returns one of the VALID_STACKS identifiers, falling back to 'Generic'.
    """
    files_and_dirs: set[str] = set()
    suffixes: set[str] = set()
    try:
        for item in root_path.iterdir():
            files_and_dirs.add(item.name)
            if item.is_file():
                suffixes.add(item.suffix)
    except (PermissionError, OSError):
        pass

    # Presence signals
    has_package_json = "package.json" in files_and_dirs
    has_tsconfig = "tsconfig.json" in files_and_dirs
    has_next_config = any(
        f in files_and_dirs
        for f in ("next.config.js", "next.config.ts", "next.config.mjs")
    )
    has_angular_json = "angular.json" in files_and_dirs
    has_vite_config = any(
        f in files_and_dirs for f in ("vite.config.ts", "vite.config.js")
    )
    has_vue_config = "vue.config.js" in files_and_dirs
    has_py_files = ".py" in suffixes
    has_requirements = "requirements.txt" in files_and_dirs
    has_pyproject = "pyproject.toml" in files_and_dirs
    has_fastapi = "main.py" in files_and_dirs or "app.py" in files_and_dirs
    has_django = "manage.py" in files_and_dirs
    has_pom = "pom.xml" in files_and_dirs
    has_gradle = (
        "build.gradle" in files_and_dirs or "build.gradle.kts" in files_and_dirs
    )
    has_tsx_jsx = ".tsx" in suffixes or ".jsx" in suffixes

    # Angular + Spring Boot + MySQL
    if has_angular_json and (has_pom or has_gradle):
        return "Angular-SpringBoot-MySQL"

    # Next.js + Django + Postgres
    if has_next_config and has_django:
        return "Next.js-Django-Postgres"

    # Vue + Express + MongoDB (Vite present, no Python backend)
    if has_package_json and (has_vite_config or has_vue_config) and not has_py_files:
        return "Vue-Express-MongoDB"

    # React + FastAPI + Postgres (Python backend detected)
    if has_package_json and has_fastapi and not has_django:
        react_signals = sum([has_tsconfig, has_tsx_jsx])
        if react_signals >= 1:
            return "React-FastAPI-Postgres"

    # React + Node + MongoDB (MERN: JS-only, no Python, no Angular, no Next)
    if (
        has_package_json
        and not has_py_files
        and not has_django
        and not has_angular_json
        and not has_next_config
        and (has_tsconfig or has_tsx_jsx)
    ):
        return "React-Node-MongoDB"

    return "Generic"


def create_governance_structure(root_path: Path, stack: str) -> dict:
    """
    Create the governance structure with all necessary files and directories.
    
    Args:
        root_path: The root directory for the project
        stack: The detected or specified stack
        
    Returns:
        Dictionary with creation results
    """
    results = {
        "stack": stack,
        "created_files": [],
        "created_dirs": [],
        "errors": [],
    }
    
    # Ensure stack is valid
    if stack not in VALID_STACKS:
        stack = "Generic"
        results["stack"] = stack
    
    try:
        # Create directory structure
        dirs_to_create = [
            root_path / ".github" / "skills",
            root_path / ".github" / "prompts",
            root_path / "docs" / "stories",
            root_path / "docs" / "adr",
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            results["created_dirs"].append(str(dir_path))
        
        # Create copilot-instructions.md
        instructions_path = root_path / ".github" / "copilot-instructions.md"
        content = GOVERNANCE_TEMPLATES["copilot_instructions"].get(
            stack, GOVERNANCE_TEMPLATES["copilot_instructions"]["Generic"]
        )
        instructions_path.write_text(content, encoding="utf-8")
        results["created_files"].append(str(instructions_path))
        
        # Create skill files
        skills = {
            "security.md": "security_skill",
            "migration.md": "migration_skill",
            "done.md": "done_skill",
        }
        
        for filename, template_key in skills.items():
            skill_path = root_path / ".github" / "skills" / filename
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            skill_path.write_text(content, encoding="utf-8")
            results["created_files"].append(str(skill_path))
        
        # Create prompt files
        prompts = {
            "gap-analysis.md": "gap_analysis_prompt",
            "harden.md": "harden_prompt",
            "done.md": "done_prompt",
        }
        
        for filename, template_key in prompts.items():
            prompt_path = root_path / ".github" / "prompts" / filename
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            prompt_path.write_text(content, encoding="utf-8")
            results["created_files"].append(str(prompt_path))
        
        # Create placeholder ADR and stories files
        adr_template = """# Architecture Decision Record

## Context
Describe the context or problem that led to this decision.

## Decision
Describe the decision made.

## Consequences
Describe the consequences of this decision (positive and negative).

## Alternatives Considered
- Alternative 1: Description
- Alternative 2: Description
"""
        
        adr_index = root_path / "docs" / "adr" / "README.md"
        adr_index.write_text(
            "# Architecture Decision Records\n\n"
            "This directory contains all architecture decisions made for this project.\n"
            "Each decision is documented in a separate Markdown file.\n",
            encoding="utf-8"
        )
        results["created_files"].append(str(adr_index))
        
        stories_index = root_path / "docs" / "stories" / "README.md"
        stories_index.write_text(
            "# Feature Stories\n\n"
            "This directory contains feature stories and acceptance criteria.\n"
            "Use this to document requirements and expected behavior.\n",
            encoding="utf-8"
        )
        results["created_files"].append(str(stories_index))

        # Create naming bootstrap file
        bootstrap_path = root_path / ".github" / "naming-bootstrap.md"
        bootstrap_content = GOVERNANCE_TEMPLATES["naming_bootstrap"].get(
            stack, GOVERNANCE_TEMPLATES["naming_bootstrap"]["Generic"]
        )
        bootstrap_path.write_text(bootstrap_content, encoding="utf-8")
        results["created_files"].append(str(bootstrap_path))

    except Exception as e:
        results["errors"].append(f"Error creating governance structure: {str(e)}")
    
    return results


# Create the MCP server
server = Server("archon-mcp")


@server.call_tool()
async def init_governance(
    root_directory: Optional[str] = None,
    stack: Optional[str] = None,
) -> ToolResult:
    """
    Initialize governance framework for a project.
    
    This tool:
    1. Detects or validates the tech stack
    2. Creates governance directory structure
    3. Deploys governance templates
    
    Args:
        root_directory: Project root directory (defaults to current directory)
        stack: Tech stack to use ('React-FastAPI-Postgres' or 'Generic', auto-detected if not specified)
        
    Returns:
        ToolResult with creation status and details
    """
    try:
        # Determine root directory
        if root_directory:
            root_path = Path(root_directory).resolve()
        else:
            root_path = Path.cwd()
        
        # Validate root directory exists
        if not root_path.is_dir():
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: Root directory does not exist: {root_path}",
                    )
                ],
                is_error=True,
            )
        
        # Detect or validate stack
        if stack is None:
            detected_stack = detect_tech_stack(root_path)
            stack = detected_stack
        elif stack not in VALID_STACKS:
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Invalid stack specified: '{stack}'. "
                        f"Valid options: {', '.join(VALID_STACKS)}",
                    )
                ],
                is_error=True,
            )
        
        # Create governance structure
        results = create_governance_structure(root_path, stack)
        
        # Format output
        if results["errors"]:
            error_text = "\n".join(results["errors"])
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Governance initialization completed with errors:\n\n{error_text}",
                    )
                ],
                is_error=True,
            )
        
        # Success message
        output = f"""✓ Governance framework initialized successfully!

Stack Detected: {results['stack']}
Project Root: {root_path}

Created Directories:
{chr(10).join(f"  • {d}" for d in results['created_dirs'])}

Created Files:
{chr(10).join(f"  • {f}" for f in results['created_files'])}

Next Steps:
1. Review the governance files in .github/
2. Customize templates for your project
3. Add ADRs to docs/adr/ as decisions are made
4. Document features in docs/stories/
5. Reference these governance standards in code reviews
"""
        
        return ToolResult(
            content=[TextContent(type="text", text=output)],
            is_error=False,
        )
        
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True,
        )


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="init_governance",
            description="Initialize governance framework for a project. Detects tech stack and deploys governance templates including rules, skills, and prompts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root_directory": {
                        "type": "string",
                        "description": "Project root directory (defaults to current working directory). Use absolute paths for best compatibility.",
                    },
                    "stack": {
                        "type": "string",
                        "enum": VALID_STACKS,
                        "description": (
                            "Technology stack to use. Auto-detected if not specified. "
                            f"Options: {', '.join(VALID_STACKS)}"
                        ),
                    },
                },
            },
        )
    ]


async def run_mcp_server():
    """Run the MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            mcp.server.stdio.ServerParameters(),
        )


def print_success(message: str):
    """Print success message with formatting."""
    click.secho("✓ " + message, fg="green", bold=True)


def print_error(message: str):
    """Print error message with formatting."""
    click.secho("✗ " + message, fg="red", bold=True)


def print_info(message: str):
    """Print info message with formatting."""
    click.secho("ℹ " + message, fg="blue")


def print_warning(message: str):
    """Print warning message with formatting."""
    click.secho("⚠ " + message, fg="yellow", bold=True)


@click.group()
@click.version_option(version="0.1.0", prog_name="ArchonMCP")
def cli():
    """ArchonMCP: Governance framework for AI-assisted development."""
    pass


@cli.command()
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Project root directory (defaults to current directory)",
)
@click.option(
    "--stack",
    "-s",
    type=click.Choice(VALID_STACKS, case_sensitive=False),
    default=None,
    help=(
        f"Technology stack. Auto-detected if not specified. "
        f"Options: {', '.join(VALID_STACKS)}"
    ),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output with detailed file listings",
)
def init(root: Path, stack: Optional[str], verbose: bool):
    """Initialize governance framework for a project."""
    try:
        click.secho("\n" + "=" * 50, fg="cyan")
        click.secho("ArchonMCP Governance Initialization", fg="cyan", bold=True)
        click.secho("=" * 50 + "\n", fg="cyan")
        
        # Validate root directory
        if not root.is_dir():
            print_error(f"Directory does not exist: {root}")
            sys.exit(1)
        
        # Detect or validate stack
        if stack is None:
            print_info("Scanning project for tech stack indicators...")
            detected_stack = detect_tech_stack(root)
            stack = detected_stack
            print_success(f"Detected stack: {detected_stack}")
        else:
            # Normalize case: click validates presence, but not case
            normalized = next(
                (s for s in VALID_STACKS if s.lower() == stack.lower()), stack
            )
            stack = normalized
            print_info(f"Using specified stack: {stack}")
        
        # Create governance structure
        print_info("Creating governance structure...")
        results = create_governance_structure(root, stack)
        
        # Handle errors
        if results["errors"]:
            print_warning("Governance initialized with errors:")
            for error in results["errors"]:
                print_error(f"  {error}")
        
        # Print results
        print_success("Governance framework initialized successfully!")
        
        click.echo("\n" + "-" * 50)
        click.echo(f"Stack:        {results['stack']}")
        click.echo(f"Project Root: {root}")
        click.echo("-" * 50)
        
        if verbose:
            click.echo("\nCreated Directories:")
            for d in results["created_dirs"]:
                click.echo(f"  📁 {d}")
            
            click.echo("\nCreated Files:")
            for f in results["created_files"]:
                click.echo(f"  📄 {f}")
        else:
            click.echo(f"\nCreated {len(results['created_dirs'])} directories")
            click.echo(f"Created {len(results['created_files'])} files")
        
        click.echo("\nNext Steps:")
        click.echo("  1. Review the governance files in .github/")
        click.echo("  2. Customize templates for your project")
        click.echo("  3. Add ADRs to docs/adr/ as decisions are made")
        click.echo("  4. Document features in docs/stories/")
        click.echo("  5. Reference these governance standards in code reviews")
        click.echo("")
        
    except Exception as e:
        print_error(f"Failed to initialize governance: {str(e)}")
        sys.exit(1)


@cli.command()
def server():
    """Run as MCP server over stdio (for IDE integration)."""
    try:
        click.secho("Starting ArchonMCP MCP Server...", fg="cyan", bold=True)
        click.secho("Ready to accept MCP connections over stdio\n", fg="cyan")
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        click.echo("\nShutting down ArchonMCP MCP Server")
        sys.exit(0)
    except Exception as e:
        print_error(f"Server error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Project root directory (defaults to current directory)",
)
def detect(root: Path):
    """Detect the technology stack of a project."""
    try:
        click.secho("\nDetecting technology stack...\n", fg="cyan")
        
        stack = detect_tech_stack(root)
        
        click.echo(f"Project Root: {root}")
        click.echo(f"Detected Stack: {stack}")
        click.echo("")
        
        indicators = {
            "React-FastAPI-Postgres": [
                "React/TypeScript frontend (package.json + .tsx files)",
                "FastAPI backend (main.py / app.py)",
                "PostgreSQL database",
            ],
            "Next.js-Django-Postgres": [
                "Next.js frontend (next.config.js detected)",
                "Django backend (manage.py detected)",
                "PostgreSQL database",
            ],
            "Vue-Express-MongoDB": [
                "Vue frontend (vite.config.ts detected)",
                "Express/Node.js backend",
                "MongoDB database",
            ],
            "Angular-SpringBoot-MySQL": [
                "Angular frontend (angular.json detected)",
                "Spring Boot backend (pom.xml / build.gradle detected)",
                "MySQL database",
            ],
            "React-Node-MongoDB": [
                "React/TypeScript frontend",
                "Node.js/Express backend",
                "MongoDB database",
            ],
        }
        if stack in indicators:
            click.echo("Indicators found:")
            for ind in indicators[stack]:
                click.echo(f"  ✓ {ind}")
        else:
            click.echo("Generic stack detected (no specific framework signature found).")
            click.echo(f"Override with: archon-mcp init --stack {VALID_STACKS[0]}")
        click.echo(f"\nTo initialize: archon-mcp init --stack \"{stack}\"")

        click.echo("")

    except Exception as e:
        print_error(f"Detection failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
