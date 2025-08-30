# Flair! 🍺

A fast-paced bar management game where you serve drinks to thirsty customers before they reach the bar!

## Installation

```bash
# Install dependencies with UV
uv pip install -e .

# Or with pip
pip install pygame
```

## Running the Game

```bash
# Using UV
uv run python src/main.py

# Or standard Python
python src/main.py
```

## Controls

### Keyboard & Mouse
- **1, 2, 3** - Select Beer, Wine, or Cocktail
- **Mouse Click** - Throw selected drink at cursor position
- **R** - Restock all drinks
- **P** - Pause game
- **F3** - Toggle debug overlay
- **F5** - Quick save
- **ESC** - Return to main menu

### Controller (Xbox layout)
- **A/B/X** - Select drink type
- **Y** - Restock
- **Left Stick** - Aim
- **Right Bumper** - Throw drink
- **Start** - Pause

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
make test

# Format code
make format

# Type check
make type-check
```

## Requirements

- Python 3.9+
- Pygame 2.5.0+
