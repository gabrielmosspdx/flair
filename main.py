"""Pygbag entry point for web (WebAssembly) deployment.

Run locally with:
    python -m pygbag .          # serve with hot-reload
    python -m pygbag --build .  # produce static build in build/web/

The file must be at the project root so Pygbag can bundle assets/,
data/, and src/ together.
"""

import asyncio
import os
import sys

# Ensure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import FlairGame  # noqa: E402
from src.utils.config import config  # noqa: E402
from src.utils.logger import game_logger  # noqa: E402


async def main():
    """Async entry point required by Pygbag."""
    try:
        log_level = config.get("debug.log_level", "INFO")
        # Disable file logging for web — filesystem writes are not available
        game_logger.setup_logger(name="Flair", log_level=log_level, log_to_file=False)

        game = FlairGame()
        await game.run()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(main())
