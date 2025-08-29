#!/usr/bin/env python3
"""Clean build artifacts and cache files."""

import shutil
from pathlib import Path


def clean_project():
    """Remove all build artifacts and cache files."""
    root_dir = Path(__file__).parent.parent

    patterns_to_remove = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.egg-info",
        ".coverage",
        ".pytest_cache",
        ".mypy_cache",
        "htmlcov",
        "build",
        "dist",
    ]

    removed_items = []

    for pattern in patterns_to_remove:
        # Handle directories
        for path in root_dir.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                removed_items.append(str(path.relative_to(root_dir)))
            elif path.is_file():
                try:
                    path.unlink()
                    removed_items.append(str(path.relative_to(root_dir)))
                except Exception:
                    pass

    if removed_items:
        print(f"Cleaned {len(removed_items)} items:")
        for item in removed_items[:10]:  # Show first 10 items
            print(f"  - {item}")
        if len(removed_items) > 10:
            print(f"  ... and {len(removed_items) - 10} more")
    else:
        print("No artifacts to clean")


if __name__ == "__main__":
    clean_project()
