# Flair! 🍺

A fast-paced bar management game where you serve drinks to thirsty customers before they reach the bar!

## 🎮 Game Overview

In Flair!, you play as a bartender who must quickly serve the correct drinks to approaching customers. Throw beers, wines, and cocktails with precision to keep your customers happy and your bar running smoothly. But be careful - serve the wrong drink or let customers reach the bar, and you'll lose lives!

### Features

- **Fast-paced arcade action** - Customers approach from all directions with increasing speed
- **Three drink types** - Beer, Wine, and Cocktails to match customer preferences  
- **Wave-based gameplay** - Survive increasingly difficult waves of thirsty customers
- **High score system** - Compete for the top spot on the leaderboard with persistent saves
- **Controller support** - Play with keyboard/mouse or gamepad
- **Customizable settings** - Adjust audio levels and controls to your preference
- **Debug mode** - Press F3 to see FPS and performance metrics
- **Quick save** - Press F5 to save your progress instantly
- **Scene-based architecture** - Clean separation of menu, game, and settings screens
- **HUD animations** - Visual feedback for scores, lives, and wave transitions

## 🚀 Installation

### Using UV (Recommended)

UV is a fast Python package manager that handles dependencies efficiently.

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/flair.git
cd flair

# Install dependencies with UV
uv pip install -r requirements.txt

# Or install as a package
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/flair.git
cd flair

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 How to Play

### Running the Game

```bash
# Using UV
uv run python src/main.py

# Or if installed as package
flair

# Using standard Python
python src/main.py
```

### Controls

#### Keyboard & Mouse
- **1, 2, 3** - Select Beer, Wine, or Cocktail
- **Mouse Click** - Throw selected drink at cursor position
- **R** - Restock all drinks
- **P** - Pause game
- **F3** - Toggle debug overlay
- **F5** - Quick save
- **ESC** - Return to main menu

#### Controller (Xbox layout)
- **A Button** - Select Beer
- **B Button** - Select Wine
- **X Button** - Select Cocktail
- **Y Button** - Restock
- **Left Stick** - Aim
- **Right Bumper** - Throw drink
- **Start** - Pause

### Gameplay Tips

1. **Watch the icons** - Each customer shows what drink they want above their head
2. **Manage your inventory** - You only have 5 of each drink before needing to restock
3. **Time your restocks** - Restocking takes 3 seconds, leaving you vulnerable
4. **Accuracy matters** - Wrong drinks cost you a life!
5. **Speed increases** - Each wave gets 5% faster than the last

## 🏗️ Project Structure

The project follows Pygame best practices with a modular architecture:

```
flair/
├── src/                     # Source code
│   ├── entities/           # Game objects (Customer, Projectile, Particle)
│   ├── managers/           # Resource managers (Audio, Assets, Input, Settings)
│   ├── scenes/             # Game scenes (Menu, Game, Settings, GameOver)
│   ├── ui/                 # UI components (Button, Slider, HUD)
│   ├── utils/              # Utilities (Config, Logger, Debug, SaveSystem)
│   ├── game.py             # Main game class
│   └── main.py             # Entry point
├── assets/                 # Game resources
│   ├── fonts/              # Font files
│   ├── images/             # Sprites and textures
│   ├── sounds/             # Sound effects
│   └── music/              # Background music
├── data/                   # Configuration and saves
│   ├── game_config.json    # Game configuration
│   └── settings.json       # User settings
├── saves/                  # Save files and high scores (auto-created)
├── logs/                   # Game logs (auto-created)
└── tests/                  # Unit tests
```

### Architecture Highlights

- **Entity-Component Pattern** - Game objects are separate entities with focused responsibilities
- **Manager Pattern** - Centralized management of assets, audio, and settings
- **Sprite Groups** - Efficient collision detection and rendering using Pygame's sprite system
- **Type Hints** - Full type annotations for better code maintainability
- **Constants Module** - All game constants in one place for easy tweaking

## 🔧 Development

### Setting Up Development Environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Format code with Black
black src/

# Type check with mypy
mypy src/

# Run tests
pytest
```

### Adding New Features

1. **New Drink Types** - Add to `DrinkType` enum in `constants.py`
2. **New Customer Behaviors** - Extend `Customer` class in `entities/customer.py`
3. **New UI Elements** - Create components in `ui/` following Button/Slider patterns
4. **New Game States** - Add to `GameState` enum and implement state handler

## 🎨 Customization

### Modifying Game Balance

Edit values in `src/utils/constants.py`:

```python
BASE_CUSTOMER_SPEED = 0.5  # Customer movement speed
INITIAL_WAVE_SIZE = 8      # Customers in first wave
RESTOCK_DURATION = 180     # Frames to restock (3 seconds at 60 FPS)
BASE_POINTS = 10           # Points per correct serve
```

### Adding Custom Assets

1. Place images in `assets/images/`
2. Add sounds in `assets/sounds/` (.wav, .ogg, or .mp3)
3. Update `AssetManager` in `src/managers/assets.py` to load them

## 📝 Requirements

- Python 3.9+
- Pygame 2.5.0+
- Operating System: Windows, macOS, or Linux
- Optional: Game controller for gamepad support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Guidelines

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for classes and public methods
4. Test your changes thoroughly
5. Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Font: Grandstander by Tyler Finck
- Inspired by classic arcade games

## 🐛 Troubleshooting

### Common Issues

**Game won't start**
- Ensure Python 3.9+ is installed
- Check that Pygame is installed: `pip show pygame`
- Verify all asset files are present in `assets/` directory

**No sound**
- Check system volume and mixer settings
- Verify sound files exist in `assets/sounds/`
- Try different audio formats (.wav usually works best)

**Controller not detected**
- Ensure controller is connected before starting game
- Go to Settings > Controller Setup to verify detection
- Check controller compatibility with Pygame

**Performance issues**
- Lower display resolution in system settings
- Close other applications
- Ensure graphics drivers are up to date

---

Made with ❤️ and Pygame