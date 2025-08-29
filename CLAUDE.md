# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Game
```bash
# Using UV (recommended)
uv run python src/main.py

# Using standard Python
python src/main.py
```

### Development Setup
```bash
# Install development dependencies
uv pip install -e ".[dev]"
```

### Code Quality
```bash
# Format code with Black
uv run black src/

# Type check with mypy
uv run mypy src/

# Run tests
uv run pytest
uv run pytest tests/test_config.py  # Run single test file
```

## Architecture Overview

This is a Pygame-based arcade game with a clean, modular architecture following several design patterns:

### Core Patterns

1. **Scene Manager Pattern**: The game uses a scene-based architecture where different game states (menu, game, settings, game over) are separate scenes managed by `SceneManager`. Each scene inherits from `BaseScene` and handles its own update/render logic.

2. **Manager Pattern**: Centralized managers handle specific responsibilities:
   - `AssetManager`: Loads and caches all game assets (images, fonts)
   - `AudioManager`: Manages sound effects and music playback
   - `InputManager`: Abstracts input handling for keyboard/mouse/gamepad
   - `SettingsManager`: Handles user preferences persistence

3. **Entity-Component Pattern**: Game objects like Customer, Projectile, and Particle are separate entities managed by Pygame sprite groups for efficient collision detection and rendering.

4. **Object Pooling**: The game uses object pooling (`ObjectPool` in utils) for frequently created/destroyed objects to reduce garbage collection overhead.

### Key Files and Their Responsibilities

- `src/game.py`: Main game class that initializes Pygame, manages the game loop, and coordinates managers
- `src/scenes/game_scene.py`: Core gameplay logic including wave management, collision detection, and game state
- `src/ui/hud.py`: HUD overlay with animations for score, lives, and wave transitions
- `src/utils/save_system.py`: Handles game saves and high score persistence
- `src/utils/config.py`: Configuration system that merges JSON configs with runtime settings
- `src/utils/debug.py`: Debug overlay system (F3 key) for performance monitoring

### Data Flow

1. **Configuration**: Game loads from `data/game_config.json` (game balance) and `data/settings.json` (user preferences)
2. **Input**: InputManager abstracts input → Scene processes input → Entities respond
3. **Game Loop**: FlairGame.run() → SceneManager.update() → Current Scene update/render
4. **Persistence**: SaveSystem handles saves to `saves/` directory with JSON format

### Important Constants

Game mechanics constants are centralized in `src/utils/constants.py`:
- `BASE_CUSTOMER_SPEED`: Customer movement speed
- `INITIAL_WAVE_SIZE`: Starting wave difficulty
- `RESTOCK_DURATION`: Frames for restock action (180 = 3 seconds at 60 FPS)
- `DrinkType` enum: Defines drink types (BEER, WINE, COCKTAIL)
- `GameState` enum: Defines game states for scene transitions

### Debug Features

- **F3**: Toggle debug overlay showing FPS, entity counts, performance metrics
- **F5**: Quick save current game
- **Dev mode**: Can be toggled in settings to enable debug features like wave control

### Testing Approach

Tests use pytest and are located in `tests/`. Focus areas:
- Configuration system (`test_config.py`)
- Object pooling performance (`test_object_pool.py`)

### Performance Considerations

- Object pooling for projectiles and particles to reduce GC pressure
- Sprite groups for efficient collision detection
- Debug overlay to monitor performance metrics
- Wave size capping at MAX_WAVE_SIZE to prevent performance degradation
