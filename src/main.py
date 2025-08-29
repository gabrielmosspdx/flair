#!/usr/bin/env python3
"""Main entry point for the Flair game."""

import sys
import os

# Add parent directory to path to allow running from any location
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game import FlairGame


def main():
    """Main entry point."""
    try:
        # Create and run the game
        game = FlairGame()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()