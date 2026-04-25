# ArchonMCP: Governance Framework for AI-Assisted Development

**ArchonMCP** is a Python-based MCP (Model Context Protocol) server that deploys comprehensive governance frameworks for development projects. It provides tools to initialize and manage governance structures including rules, runbooks, and custom prompts designed to work seamlessly with AI-assisted development tools like Cursor, VS Code, and Claude.

## 🎯 Features

- **Automatic Stack Detection**: Scans your project to identify whether you're using a React-FastAPI-Postgres architecture or a generic tech stack
- **One-Command Governance Setup**: Deploys complete governance structure with a single tool invocation
- **Customizable Templates**: Stack-specific governance templates that scale from generic projects to complex full-stack applications
- **MCP-Compatible**: Runs over stdio for compatibility with all MCP-enabled IDEs
- **Cross-Platform**: Uses `pathlib` for reliable cross-OS file operations

## 📋 What Gets Deployed

When you run the `init_governance` tool, ArchonMCP creates:

```
.github/
├── copilot-instructions.md      # High-level governance rules
├── skills/
│   ├── security.md              # Security hardening runbook
│   ├── migration.md             # Data migration best practices
│   └── done.md                  # Definition of Done checklist
└── prompts/
    ├── gap-analysis.md          # /gap-analysis slash command guide
    ├── harden.md                # /harden security command guide
    └── done.md                  # /done validation command guide

docs/
├── stories/
│   └── README.md                # Feature story documentation
└── adr/
    └── README.md                # Architecture Decision Records
```

## 🚀 Quick Start

### Installation

```bash
# Clone or download the ArchonMCP repository
cd ArchonMCP

# Install as development package
pip install -e .

# Or install in production with specific version
pip install archon-mcp==0.1.0
```

### CLI Usage (Local Execution)

The fastest way to initialize governance is using the CLI locally:

```bash
# Initialize governance (auto-detect stack)
archon-mcp init

# Initialize governance in a specific directory
archon-mcp init --root /path/to/project

# Initialize with a specific stack
archon-mcp init --stack React-FastAPI-Postgres
# or
archon-mcp init --stack Generic

# Verbose output with all files listed
archon-mcp init --verbose

# Detect stack without initializing
archon-mcp detect
archon-mcp detect --root /path/to/project
```

#### CLI Examples

```bash
# Full-stack project in current directory with verbose output
archon-mcp init -v

# Generic project in custom location
archon-mcp init --root ~/projects/my-app --stack Generic --verbose

# Just detect the tech stack
archon-mcp detect
```

### MCP Server Usage (IDE Integration)

Run as an MCP server for integration with AI IDEs:

```bash
# Start the MCP server
archon-mcp server

# In VS Code with Cline:
# - Copy the archon-mcp command path
# - Configure in settings as an MCP server
# - Use with AI assistant chat interface
```

## 🏗️ Architecture

### Dual-Mode Operation

ArchonMCP operates in two modes:

#### 1. **CLI Mode** (Local Execution)
- Direct command-line interface for immediate governance setup
- Fast local execution without server overhead
- Perfect for CI/CD pipelines and scripting
- **Commands**: `init`, `detect`, `server`

```bash
archon-mcp init --stack React-FastAPI-Postgres
```

#### 2. **MCP Server Mode** (IDE Integration)
- Runs as stdio-based MCP server
- Integrates with Cursor, VS Code (Cline), Claude
- Enables AI-assisted governance workflow
- Tools available through AI chat interface

```bash
archon-mcp server
```

### Core Components

#### 1. **CLI Interface** (Click-based)
Command structure:
- `archon-mcp init`: Initialize governance framework
- `archon-mcp detect`: Analyze project tech stack
- `archon-mcp server`: Start MCP server
- `archon-mcp --version`: Show version
- `archon-mcp --help`: Show help

#### 2. **Stack Detection**
The `detect_tech_stack()` function analyzes your project directory for:
- **React**: package.json, tsconfig.json, .tsx/.jsx files
- **FastAPI**: requirements.txt, pyproject.toml, main.py/app.py
- **PostgreSQL**: docker-compose.yml, migrations, Dockerfile

Classification:
- **React-FastAPI-Postgres**: All three stacks detected (recommended profile)
- **Generic**: Fallback for other or mixed stacks

#### 2. **Template Engine**
Dictionary-based template system with stack-aware content:
```python
GOVERNANCE_TEMPLATES = {
    "copilot_instructions": {
        "React-FastAPI-Postgres": "...",
        "Generic": "..."
    },
    # ... more templates
}
```

#### 3. **MCP Tool: init_governance**
Single async tool that:
1. Accepts optional `root_directory` and `stack` parameters
2. Auto-detects stack if not specified
3. Creates directory structure
4. Deploys stack-specific templates
5. Returns structured results with file listings and errors

## 📚 Governance Templates

### `.github/copilot-instructions.md`
High-level governance rules for AI assistants:
- Project context and tech stack specifics
- Code quality standards per language/framework
- Governance artifact locations
- Pull request review checklist

**React-FastAPI-Postgres Profile**: Specific guidance for TypeScript, Python, and SQL
**Generic Profile**: Language-agnostic governance rules

### Skills (`.github/skills/`)

#### `security.md` - Security Runbook
Structured approach to implementing security:
- Frontend security (CORS, input sanitization, session management)
- Backend security (authentication, rate limiting, input validation)
- Database security (RBAC, encryption, row-level security)
- Verification checklist

#### `migration.md` - Migration Runbook
Data migration and schema change procedures:
- Pre-migration planning and backups
- Schema preparation with reversible patterns
- Data migration with transaction management
- Post-migration validation

#### `done.md` - Definition of Done
Completion criteria for features and tasks:
- Code quality requirements (tests, linting, coverage)
- Documentation standards
- Testing requirements
- Security and accessibility
- Deployment readiness

### Prompts (`.github/prompts/`)

Custom slash commands for AI assistants to use in chat:

#### `/gap-analysis`
Analyzes gaps between current implementation and best practices:
- Code quality assessment
- Security opportunities
- Performance optimization suggestions
- Refactoring recommendations

#### `/harden`
Security hardening guidance:
- Vulnerability assessment
- Prioritized remediation steps
- Security control code examples
- Testing strategies

#### `/done`
Work completion validation:
- Checks Definition of Done criteria
- Generates verification checklist
- Identifies blockers
- Provides improvement recommendations

### Documentation Templates (`.docs/`)

#### `/docs/stories/`
Feature documentation directory for:
- User stories with acceptance criteria
- Feature specifications
- Requirements documentation

#### `/docs/adr/`
Architecture Decision Records for:
- Significant technical decisions
- Decision context and rationale
- Consequences (positive and negative)
- Alternative approaches considered

## 🔧 Configuration & Usage

### CLI Commands

#### `archon-mcp init`
Initialize governance framework locally.

**Options:**
```
-r, --root PATH          Project root directory (default: current directory)
-s, --stack STACK        Technology stack (React-FastAPI-Postgres or Generic)
-v, --verbose            Show detailed file listings
--help                   Show help message
```

**Example:**
```bash
archon-mcp init --root /path/to/project --stack React-FastAPI-Postgres --verbose
```

#### `archon-mcp detect`
Analyze and report project tech stack.

**Options:**
```
-r, --root PATH          Project root directory (default: current directory)
--help                   Show help message
```

**Example:**
```bash
archon-mcp detect --root ~/my-project
```

#### `archon-mcp server`
Start MCP server for IDE integration.

**Example:**
```bash
archon-mcp server
```

### MCP Server Configuration

### MCP Server Configuration

When running as `archon-mcp server`, the MCP tool `init_governance` is available.

#### Cursor Integration
Add to `.cursor/rules.md`:
```markdown
# ArchonMCP Governance
Use the init_governance tool to set up project governance frameworks.
```

Or configure via Cursor settings:
```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"]
    }
  }
}
```

#### VS Code with Cline
Configure in VS Code settings:
```json
{
  "cline.mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"]
    }
  }
}
```

Or in workspace settings (`.vscode/settings.json`):
```json
{
  "cline.mcpServers": {
    "archon-mcp": {
      "command": "python",
      "args": ["-m", "archon_mcp", "server"]
    }
  }
}
```

#### Claude.com (MCP Client)
Use any MCP-compatible client that runs stdio servers:
```bash
archon-mcp server
```

### Tool Parameters

**init_governance(root_directory, stack)**

| Parameter | Type | Required | Default | Values |
|-----------|------|----------|---------|--------|
| `root_directory` | string | No | Current directory | Any valid absolute path |
| `stack` | string | No | Auto-detect | `React-FastAPI-Postgres`, `Generic` |

**Response Structure**
```
{
  "stack": "React-FastAPI-Postgres",
  "created_files": [list of file paths],
  "created_dirs": [list of directory paths],
  "errors": [any error messages]
}
```

## 📖 Examples

### Example 1: Quick Local Setup (CLI)
```bash
# Navigate to your project
cd ~/my-react-fastapi-project

# Run governance initialization
archon-mcp init

# Output:
# ==================================================
# ArchonMCP Governance Initialization
# ==================================================
# 
# ℹ Scanning project for tech stack indicators...
# ✓ Detected stack: React-FastAPI-Postgres
# ℹ Creating governance structure...
# ✓ Governance framework initialized successfully!
```

### Example 2: Verbose Setup with Custom Directory
```bash
archon-mcp init --root ~/projects/my-app --verbose

# Shows:
# - All created directories
# - All created files with paths
# - Detailed next steps
```

### Example 3: Detect Stack Before Setup
```bash
# First, analyze what stack the project is
archon-mcp detect --root ~/my-project

# Output:
# Project Root: /Users/dev/my-project
# Detected Stack: React-FastAPI-Postgres
# Indicators found:
#   ✓ React/TypeScript frontend
#   ✓ FastAPI backend
#   ✓ PostgreSQL database
```

### Example 4: Generic Stack Initialization
```bash
# For non-standard stacks
archon-mcp init --root ~/my-python-project --stack Generic

# Creates governance framework with generic templates
```

### Example 5: MCP Server Integration
```bash
# Terminal 1: Start the MCP server
archon-mcp server

# Terminal 2: Use with AI IDE (Cline/VS Code)
# Chat: "Use init_governance to set up governance for /path/to/project"
# Result: Server processes command via MCP interface
```

### Example 6: CI/CD Pipeline
```bash
#!/bin/bash
# .github/workflows/setup-governance.yml

- name: Initialize Governance
  run: |
    pip install archon-mcp
    archon-mcp init --stack React-FastAPI-Postgres
    git add .github/ docs/
    git commit -m "chore: initialize governance framework"
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Install Development Environment
```bash
# Clone repository
git clone <repository-url>
cd ArchonMCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black archon_mcp.py

# Lint
ruff check archon_mcp.py

# Type check
mypy archon_mcp.py
```

### Project Structure
```
ArchonMCP/
├── archon_mcp.py           # Main server implementation
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── tests/                  # Unit tests (future)
└── docs/                   # Additional documentation (future)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=archon_mcp

# Run specific test
pytest tests/test_stack_detection.py -v
```

## 🔐 Security Considerations

- **Template Content**: All governance templates are example-based; customize them for your project
- **File Permissions**: Ensure proper file permissions on governance files post-deployment
- **Credentials**: Never store credentials in governance files; use secrets management
- **Review Process**: Have security team review governance templates before deployment

## 📦 Dependencies

### Core
- **fastmcp** ≥0.1.0: MCP server implementation

### Development
- **pytest** ≥7.0: Testing framework
- **pytest-asyncio** ≥0.21.0: Async test support
- **black** ≥23.0: Code formatter
- **ruff** ≥0.1.0: Linter
- **mypy** ≥1.0: Type checker

## 🤝 Contributing

Contributions welcome! Areas for expansion:
- Additional tech stack profiles (Django-React, Next.js, etc.)
- Enhanced template customization
- Governance validation tools
- CI/CD integration examples
- IDE-specific plugins

Please ensure:
- Code follows `black` and `ruff` standards
- All changes include type hints
- New features have test coverage
- Governance templates are validated for each stack

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### CLI Issues

#### Issue: "archon-mcp: command not found"
**Solution**: 
1. Ensure package is installed: `pip install -e .` or `pip install archon-mcp`
2. Check it's in PATH: `which archon-mcp` (Unix) or `where archon-mcp` (Windows)
3. Try running as module: `python -m archon_mcp init`

#### Issue: "Permission denied" when initializing
**Solution**: 
1. Ensure target directory is writable: `ls -ld /path/to/project`
2. Run with appropriate permissions or use a writable directory
3. Try with `--root` pointing to a temp directory first

#### Issue: "Stack detection returns Generic"
**Solution**: Ensure key indicator files are present:
- React: `package.json` or `.tsx` files
- FastAPI: `requirements.txt` or `pyproject.toml`
- PostgreSQL: `docker-compose.yml` or `migrations/` directory

Force stack detection with:
```bash
archon-mcp init --stack React-FastAPI-Postgres
```

### MCP Server Issues

#### Issue: "MCP server not connecting"
**Solution**: 
1. Verify `archon-mcp` command is in PATH: `which archon-mcp`
2. Test server startup: `archon-mcp server` (should show "Ready to accept MCP connections")
3. Check IDE MCP configuration points to correct command
4. Ensure firewall isn't blocking stdio

#### Issue: "Tool not appearing in AI chat"
**Solution**:
1. Restart the MCP server: `archon-mcp server`
2. Reload IDE window (VS Code: Cmd+Shift+P → Developer: Reload Window)
3. Check MCP server configuration in IDE settings

### General Issues

#### Issue: "Governance templates don't match my project"
**Solution**: Post-deployment, edit files in `.github/`, `docs/stories/`, and `docs/adr/` to match your project's needs

## 🗺️ Roadmap

- [ ] **v0.2.0**: Add governance validation and audit tools
- [ ] **v0.3.0**: Support additional stacks (Django, Next.js, Spring Boot)
- [ ] **v0.4.0**: Custom template loading from configuration files
- [ ] **v0.5.0**: GitHub Actions integration for governance checks
- [ ] **v1.0.0**: Stable release with comprehensive documentation

## 📚 Related Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [Cursor IDE](https://cursor.com)
- [Cline for VS Code](https://github.com/cline/cline)
- [Architecture Decision Records (ADR)](https://adr.github.io/)

## 💬 Support

For issues, questions, or suggestions:
1. Check existing documentation and examples
2. Review troubleshooting section
3. Open an issue with detailed reproduction steps
4. For security issues, please report privately

---

**Made with ❤️ for AI-assisted development teams**
