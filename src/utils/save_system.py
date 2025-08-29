"""Save and load system for game persistence."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from ..utils.logger import game_logger


class SaveSystem:
    """Manages game saves and high scores."""

    def __init__(self, save_dir: str = "saves"):
        """Initialize save system.

        Args:
            save_dir: Directory for save files
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        self.autosave_file = self.save_dir / "autosave.json"
        self.highscores_file = self.save_dir / "highscores.json"
        self.settings_file = self.save_dir / "settings.json"

        self.max_highscores = 10
        self.highscores = self.load_highscores()

    def save_game(self, game_state: Dict[str, Any], slot: str = "autosave") -> bool:
        """Save current game state.

        Args:
            game_state: Dictionary containing game state
            slot: Save slot name

        Returns:
            True if save successful
        """
        try:
            save_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "slot": slot,
                "state": game_state,
            }

            save_file = self.save_dir / f"{slot}.json"
            with open(save_file, "w") as f:
                json.dump(save_data, f, indent=2)

            game_logger.info(f"Game saved to slot: {slot}")
            return True

        except Exception as e:
            game_logger.error(f"Failed to save game: {e}")
            return False

    def load_game(self, slot: str = "autosave") -> Optional[Dict[str, Any]]:
        """Load game state from save file.

        Args:
            slot: Save slot name

        Returns:
            Game state dictionary or None if load fails
        """
        try:
            save_file = self.save_dir / f"{slot}.json"

            if not save_file.exists():
                game_logger.warning(f"Save file not found: {slot}")
                return None

            with open(save_file, "r") as f:
                save_data = json.load(f)

            game_logger.info(f"Game loaded from slot: {slot}")
            return cast(Optional[Dict[str, Any]], save_data.get("state"))

        except Exception as e:
            game_logger.error(f"Failed to load game: {e}")
            return None

    def delete_save(self, slot: str) -> bool:
        """Delete a save file.

        Args:
            slot: Save slot name

        Returns:
            True if deletion successful
        """
        try:
            save_file = self.save_dir / f"{slot}.json"

            if save_file.exists():
                save_file.unlink()
                game_logger.info(f"Save deleted: {slot}")
                return True

            return False

        except Exception as e:
            game_logger.error(f"Failed to delete save: {e}")
            return False

    def list_saves(self) -> list:
        """List all available save files.

        Returns:
            List of save information dictionaries
        """
        saves = []

        for save_file in self.save_dir.glob("*.json"):
            if save_file.name == "highscores.json" or save_file.name == "settings.json":
                continue

            try:
                with open(save_file, "r") as f:
                    data = json.load(f)

                saves.append(
                    {
                        "slot": save_file.stem,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "version": data.get("version", "Unknown"),
                        "score": data.get("state", {}).get("score", 0),
                        "wave": data.get("state", {}).get("wave", 1),
                    }
                )

            except Exception as e:
                game_logger.warning(f"Could not read save file {save_file}: {e}")

        # Sort by timestamp
        saves.sort(key=lambda x: x["timestamp"], reverse=True)
        return saves

    def save_highscore(self, name: str, score: int, wave: int) -> int:
        """Save a high score.

        Args:
            name: Player name
            score: Final score
            wave: Wave reached

        Returns:
            Position in high scores (1-based) or 0 if not a high score
        """
        entry = {
            "name": name[:20],  # Limit name length
            "score": score,
            "wave": wave,
            "timestamp": datetime.now().isoformat(),
        }

        # Insert into sorted position
        position = 0
        for i, hs in enumerate(self.highscores):
            if score > hs["score"]:
                position = i + 1
                self.highscores.insert(i, entry)
                break

        # If not inserted yet, add to end
        if position == 0 and len(self.highscores) < self.max_highscores:
            position = len(self.highscores) + 1
            self.highscores.append(entry)

        # Trim to max size
        self.highscores = self.highscores[: self.max_highscores]

        # Save to file
        if position > 0:
            self._save_highscores()
            game_logger.info(f"New high score #{position}: {name} - {score}")

        return position

    def load_highscores(self) -> List[Any]:
        """Load high scores from file.

        Returns:
            List of high score entries
        """
        try:
            if self.highscores_file.exists():
                with open(self.highscores_file, "r") as f:
                    return cast(List[Any], json.load(f))
        except Exception as e:
            game_logger.error(f"Failed to load high scores: {e}")

        return []

    def _save_highscores(self):
        """Save high scores to file."""
        try:
            with open(self.highscores_file, "w") as f:
                json.dump(self.highscores, f, indent=2)
        except Exception as e:
            game_logger.error(f"Failed to save high scores: {e}")

    def is_highscore(self, score: int) -> bool:
        """Check if a score qualifies as a high score.

        Args:
            score: Score to check

        Returns:
            True if score is a high score
        """
        if len(self.highscores) < self.max_highscores:
            return True

        return any(score > hs["score"] for hs in self.highscores)

    def get_highscores(self, limit: int = 10) -> list:
        """Get top high scores.

        Args:
            limit: Maximum number of scores to return

        Returns:
            List of high score entries
        """
        return self.highscores[: min(limit, len(self.highscores))]

    def create_game_state(
        self,
        score: int,
        wave: int,
        lives: int,
        inventory: Dict,
        customers_served: int,
        selected_drink: Any,
    ) -> Dict[str, Any]:
        """Create a game state dictionary for saving.

        Args:
            score: Current score
            wave: Current wave
            lives: Remaining lives
            inventory: Drink inventory
            customers_served: Number of customers served
            selected_drink: Currently selected drink

        Returns:
            Game state dictionary
        """
        return {
            "score": score,
            "wave": wave,
            "lives": lives,
            "inventory": {k.name: v for k, v in inventory.items()},
            "customers_served": customers_served,
            "selected_drink": (
                selected_drink.name if hasattr(selected_drink, "name") else str(selected_drink)
            ),
        }

    def autosave(self, game_state: Dict[str, Any]) -> bool:
        """Perform an autosave.

        Args:
            game_state: Current game state

        Returns:
            True if autosave successful
        """
        return self.save_game(game_state, "autosave")
