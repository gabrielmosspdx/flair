"""Tests for configuration system."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import Config  # noqa: E402


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.config._config = {
            "game": {"initial_lives": 3, "initial_inventory": 5},
            "display": {"screen_width": 1200, "screen_height": 800},
        }

    def test_get_simple_value(self):
        """Test getting a simple configuration value."""
        self.assertEqual(self.config.get("game.initial_lives"), 3)
        self.assertEqual(self.config.get("display.screen_width"), 1200)

    def test_get_with_default(self):
        """Test getting value with default."""
        self.assertEqual(self.config.get("nonexistent.key", "default"), "default")

    def test_set_value(self):
        """Test setting configuration values."""
        self.config.set("game.new_setting", 42)
        self.assertEqual(self.config.get("game.new_setting"), 42)

        self.config.set("new_category.setting", "value")
        self.assertEqual(self.config.get("new_category.setting"), "value")

    def test_nested_get(self):
        """Test getting nested values."""
        game_config = self.config.get("game")
        self.assertIsInstance(game_config, dict)
        self.assertEqual(game_config["initial_lives"], 3)

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"

            # Save config
            self.config.save(str(config_path))
            self.assertTrue(config_path.exists())

            # Load and verify
            with open(config_path, "r") as f:
                loaded_data = json.load(f)

            self.assertEqual(loaded_data["game"]["initial_lives"], 3)
            self.assertEqual(loaded_data["display"]["screen_width"], 1200)


if __name__ == "__main__":
    unittest.main()
