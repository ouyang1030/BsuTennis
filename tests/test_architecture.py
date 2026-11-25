"""
The layering of the package, enforced.

Each subpackage may import the standard library, its own modules, and only
the third-party libraries and sibling subpackages listed below.
"""

import ast
import sys
from pathlib import Path

import pytest

import bsutennis

ALLOWED = {
    "geometry": {"numpy", "pandas"},
    "rules": set(),
    "data": {"numpy", "pandas", "bsutennis.rules"},
    "models": {"bsutennis.rules"},
    "metrics": {"numpy", "pandas", "bsutennis.rules", "bsutennis.models"},
    "viz": {"numpy", "scipy", "matplotlib", "bsutennis.geometry"},
}

ROOT = Path(bsutennis.__file__).parent


def imports_of(path: Path) -> set[str]:
    """Absolute names of the modules imported by the file at ``path``."""
    package = ".".join(("bsutennis",) + path.relative_to(ROOT).parent.parts)
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                names.add(node.module)
            else:
                base = package.rsplit(".", node.level - 1)[0] if node.level > 1 else package
                names.add(f"{base}.{node.module}" if node.module else base)
    return names


def dependency(name: str) -> str:
    """The unit an import counts against: a top-level library or a bsutennis subpackage."""
    parts = name.split(".")
    return ".".join(parts[:2]) if parts[0] == "bsutennis" else parts[0]


@pytest.mark.parametrize("subpackage", sorted(ALLOWED))
def test_layering(subpackage):
    own = f"bsutennis.{subpackage}"
    used = {
        dependency(name)
        for path in (ROOT / subpackage).rglob("*.py")
        for name in imports_of(path)
    }
    used -= set(sys.stdlib_module_names) | {own}
    assert used <= ALLOWED[subpackage], f"{own} imports {sorted(used - ALLOWED[subpackage])}"
