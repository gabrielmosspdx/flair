#!/usr/bin/env python3
"""Development environment setup script using uv."""

import subprocess
import sys


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"⚙️  {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def check_uv_installed():
    """Check if uv is installed."""
    try:
        result = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv is installed: {result.stdout.strip()}")
            return True
    except Exception:
        pass

    print("❌ uv is not installed")
    print("\nPlease install uv first:")
    print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("  or")
    print("  pip install uv")
    return False


def main():
    """Set up the development environment."""
    print("\n🚀 Setting up Flair development environment with uv...")

    # Check if uv is installed
    if not check_uv_installed():
        sys.exit(1)

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    steps = [
        ("uv pip install --upgrade pip", "Upgrading pip"),
        ("uv pip install -e '.[dev]'", "Installing development dependencies"),
        ("uv pip install pre-commit", "Installing pre-commit"),
        ("pre-commit install", "Setting up pre-commit hooks"),
        ("pre-commit run --all-files", "Running initial pre-commit checks"),
    ]

    for cmd, description in steps:
        if not run_command(cmd, description):
            print("\n⚠️  Setup encountered errors. Please fix them and run again.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Development environment setup complete!")
    print("=" * 60)
    print("\nAvailable commands (using uv):")
    print("  make test       - Run tests with coverage")
    print("  make format     - Format code")
    print("  make lint       - Run linting checks")
    print("  make type-check - Run type checking")
    print("  make run        - Run the game")
    print("  make dev        - Run with debug mode")
    print("\nOr use uv directly:")
    print("  uv run python src/main.py")
    print("  uv run pytest")
    print("  uv run black src/")
    print("\nPre-commit hooks are now active and will run on each commit.")
    print("To run pre-commit manually: make pre-commit")


if __name__ == "__main__":
    main()
