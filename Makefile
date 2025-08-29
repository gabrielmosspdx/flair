.PHONY: help install install-dev test format lint type-check clean run dev setup pre-commit

help:
	@echo "Available commands (using uv):"
	@echo "  make install      - Install production dependencies with uv"
	@echo "  make install-dev  - Install development dependencies with uv"
	@echo "  make setup        - Complete development setup with pre-commit"
	@echo "  make test         - Run tests with coverage"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run linting checks"
	@echo "  make type-check   - Run type checking with mypy"
	@echo "  make clean        - Clean build artifacts and cache"
	@echo "  make run          - Run the game"
	@echo "  make dev          - Run with debug mode enabled"
	@echo "  make pre-commit   - Run pre-commit on all files"

install:
	uv pip install --upgrade pip
	uv pip install -e .

install-dev:
	uv pip install --upgrade pip
	uv pip install -e ".[dev]"
	uv pip install pre-commit

setup: install-dev
	uv run pre-commit install
	@echo "Development environment ready with uv!"

test:
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

format:
	uv run black src/ tests/
	uv run isort src/ tests/ --profile black --line-length 100

lint:
	uv run flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/ --profile black --line-length 100

type-check:
	uv run mypy src/

clean:
	@python scripts/clean.py

run:
	uv run python src/main.py

dev:
	uv run python src/main.py --debug

pre-commit:
	uv run pre-commit run --all-files
