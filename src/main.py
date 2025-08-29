#!/usr/bin/env python3
"""Main entry point for the Flair game."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game import FlairGame
from src.utils.logger import game_logger
from src.utils.config import config


def main():
    """Main entry point for integrated game."""
    try:
        # Setup logging
        log_level = config.get("debug.log_level", "INFO")
        enable_logging = config.get("debug.enable_logging", True)
        
        if enable_logging:
            game_logger.setup_logger(
                name='Flair',
                log_level=log_level,
                log_to_file=True
            )
        
        game_logger.info("=" * 50)
        game_logger.info("Starting Flair")
        game_logger.info("=" * 50)
        game_logger.info("Features:")
        game_logger.info("- Scene Manager for clean state management")
        game_logger.info("- HUD with animations")
        game_logger.info("- Save/Load system with high scores")
        game_logger.info("- InputManager for flexible controls")
        game_logger.info("- Object pooling for performance")
        game_logger.info("- Debug overlay (F3)")
        game_logger.info("- Quick save (F5)")
        game_logger.info("=" * 50)
        
        # Create and run the integrated game
        game = FlairGame()
        game.run()
        
    except KeyboardInterrupt:
        game_logger.info("Game interrupted by user")
        print("\nGame interrupted by user")
    except Exception as e:
        game_logger.exception(f"Fatal error occurred: {e}")
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        game_logger.info("Game shutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()