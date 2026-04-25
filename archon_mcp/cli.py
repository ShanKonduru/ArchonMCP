"""Click-based CLI: init, detect, server sub-commands."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from archon_mcp.constants import VALID_STACKS
from archon_mcp.detector import detect_tech_stack
from archon_mcp.scaffold import create_governance_structure
from archon_mcp.server import run_mcp_server


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
        if not root.is_dir():  # pragma: no cover
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


