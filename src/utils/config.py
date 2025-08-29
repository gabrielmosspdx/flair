"""Configuration management system."""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """Manages game configuration from JSON files."""
    
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> 'Config':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration."""
        if not self._config:
            self.load_config()
    
    def load_config(self, config_path: str = "data/game_config.json") -> None:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            full_path = Path(config_path)
            if not full_path.exists():
                # Try relative to script location
                script_dir = Path(__file__).parent.parent.parent
                full_path = script_dir / config_path
                
            with open(full_path, 'r') as f:
                self._config = json.load(f)
                print(f"Loaded configuration from {full_path}")
        except FileNotFoundError:
            print(f"Config file not found: {config_path}, using defaults")
            self._set_defaults()
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}, using defaults")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self._config = {
            "game": {
                "initial_lives": 3,
                "initial_inventory": 5,
                "base_spawn_delay": 120,
                "base_customer_speed": 0.5,
                "initial_wave_size": 8,
                "max_wave_size": 20,
                "restock_duration": 180,
                "restock_amount": 5,
                "base_points": 10,
                "points_per_wave": 2
            },
            "display": {
                "screen_width": 1200,
                "screen_height": 800,
                "fps": 60
            },
            "audio": {
                "default_sound_volume": 0.7,
                "default_music_volume": 0.3
            },
            "debug": {
                "show_fps": False,
                "show_collision_boxes": False,
                "show_entity_count": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "game.initial_lives")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "game.initial_lives")
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def save(self, config_path: str = "data/game_config.json") -> None:
        """Save configuration to JSON file.
        
        Args:
            config_path: Path to save configuration
        """
        try:
            full_path = Path(config_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                json.dump(self._config, f, indent=4)
                print(f"Saved configuration to {full_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.load_config()
    
    @property
    def data(self) -> Dict[str, Any]:
        """Get full configuration dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()


# Global config instance
config = Config()