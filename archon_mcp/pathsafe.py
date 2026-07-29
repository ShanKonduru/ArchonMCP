"""Path-safety helpers: keep every write confined to the project root.

These guards exist so ArchonMCP can only ever touch the project it was
pointed at — never ``$HOME``, system directories, or anywhere reached via
``..`` or a symlink escape. See docs/WBS.md (E9.F1, E10.F5).
"""

from pathlib import Path


class PathContainmentError(Exception):
    """Raised when a target path would resolve outside the project root."""


def resolve_within(root: Path, target: Path) -> Path:
    """Resolve ``target`` and guarantee it stays inside ``root``.

    Args:
        root: The project root. Resolved (following symlinks) before comparison.
        target: A path that must live within ``root``. May be relative to it.

    Returns:
        The fully-resolved ``target`` path.

    Raises:
        PathContainmentError: If ``target`` resolves outside ``root`` (via an
            absolute path, ``..`` traversal, or a symlink escape).
    """
    root_resolved = Path(root).resolve()

    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = root_resolved / candidate
    # ``strict=False`` so not-yet-created files still resolve; symlink
    # components that already exist are still followed and thus caught.
    target_resolved = candidate.resolve()

    if root_resolved != target_resolved and root_resolved not in target_resolved.parents:
        raise PathContainmentError(
            f"Refusing to write outside project root: {target_resolved} "
            f"is not within {root_resolved}"
        )
    return target_resolved
