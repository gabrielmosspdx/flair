"""Settings manager for game configuration."""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any

from ..utils.constants import (
    DEFAULT_SOUND_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_CONTROLLER_DEADZONE,
    DEFAULT_CONTROLLER_MAPPINGS,
    SETTINGS_FILE
)


@dataclass
class Settings:
    """Game settings."""
    
    sound_volume: float = DEFAULT_SOUND_VOLUME
    music_volume: float = DEFAULT_MUSIC_VOLUME
    controller_enabled: bool = False
    controller_deadzone: float = DEFAULT_CONTROLLER_DEADZONE
    controller_mappings: Dict[str, int] = None
    dev_mode: bool = False
    
    def __post_init__(self):
        """Initialize controller mappings if not provided."""
        if self.controller_mappings is None:
            self.controller_mappings = DEFAULT_CONTROLLER_MAPPINGS.copy()
    
    def save(self) -> None:
        """Save settings to file."""
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from file.
        
        Returns:
            Settings instance
        """
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return cls(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default settings if file doesn't exist or is invalid
            return cls()
    
    def apply_audio_settings(self, pygame_mixer) -> None:
        """Apply audio settings to pygame mixer.
        
        Args:
            pygame_mixer: pygame.mixer module
        """
        if pygame_mixer.get_init():
            pygame_mixer.music.set_volume(self.music_volume)
            # Individual sound volumes are set per sound object