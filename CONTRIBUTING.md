# Contributing to Flair

Thank you for your interest in contributing to Flair! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- uv (Python package manager)

### Installing uv

```bash
# On Unix/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flair.git
cd flair
```

2. Set up the development environment:
```bash
# Using the setup script (uses uv)
python scripts/setup_dev.py

# Or manually with Make (uses uv)
make setup
```

3. Verify the setup:
```bash
make test
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Format your code before committing:
```bash
make format
```

Check code quality:
```bash
make lint
make type-check
```

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit. They're installed during setup and will:
- Format code with Black
- Sort imports with isort
- Check for linting issues
- Run type checking
- Validate YAML/JSON/TOML files
- Fix common issues (trailing whitespace, end-of-file)

To run pre-commit manually:
```bash
make pre-commit
```

### Testing

Run the test suite:
```bash
make test
# Or directly with uv
uv run pytest tests/
```

Tests use pytest and should:
- Be placed in the `tests/` directory
- Follow the naming pattern `test_*.py`
- Include both unit and integration tests
- Aim for high code coverage

### Running the Game

Development mode with debug features:
```bash
make dev
# Or directly with uv
uv run python src/main.py --debug
```

Production mode:
```bash
make run
# Or directly with uv
uv run python src/main.py
```

## Project Structure

```
flair/
├── src/              # Source code
│   ├── game.py       # Main game class
│   ├── scenes/       # Scene management
│   ├── entities/     # Game entities
│   ├── ui/           # UI components
│   └── utils/        # Utilities
├── tests/            # Test files
├── data/             # Game configuration
├── assets/           # Game assets
└── scripts/          # Development scripts
```

## Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the code style guidelines

3. Write or update tests for your changes

4. Run the full test suite:
```bash
make lint
make type-check
make test
```

5. Commit your changes (pre-commit hooks will run automatically):
```bash
git add .
git commit -m "feat: add your feature description"
```

### Commit Message Convention

We follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or fixes
- `chore:` Maintenance tasks

## CI/CD Pipeline

All pull requests trigger our CI pipeline which:
- Runs on Python 3.9, 3.10, 3.11, and 3.12
- Executes linting and formatting checks
- Runs the full test suite with coverage
- Performs type checking

Ensure all checks pass before requesting a review.

## Available Make Commands

All commands use `uv` for package management:

```bash
make help         # Show all available commands
make install      # Install production dependencies with uv
make install-dev  # Install development dependencies with uv
make setup        # Complete development setup with uv
make test         # Run tests with coverage using uv
make format       # Format code using uv
make lint         # Run linting checks using uv
make type-check   # Run type checking using uv
make clean        # Clean build artifacts
make run          # Run the game with uv
make dev          # Run with debug mode using uv
make pre-commit   # Run pre-commit on all files using uv
```

## Using uv Directly

You can also use uv commands directly:

```bash
uv pip install -e ".[dev]"  # Install dev dependencies
uv run python src/main.py    # Run the game
uv run pytest                # Run tests
uv run black src/            # Format code
uv run mypy src/             # Type check
```

## Debug Features

When running in debug mode (`F3` key or `--debug` flag):
- Performance metrics overlay
- Entity count display
- FPS counter
- Memory usage tracking
- Wave control (in dev mode)

## Getting Help

- Check the [README](README.md) for general information
- Review [CLAUDE.md](CLAUDE.md) for architecture details
- Open an issue for bugs or feature requests
- Join discussions for questions and ideas

## Code of Conduct

Please be respectful and inclusive in all interactions. We aim to maintain a welcoming environment for all contributors.

Thank you for contributing to Flair!
