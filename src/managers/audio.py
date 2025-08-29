"""Audio manager for sounds and music."""

import os
from typing import Dict, Optional

import pygame

from ..utils.constants import SOUNDS_DIR, MUSIC_DIR


class AudioManager:
    """Manages game audio including sound effects and music."""
    
    def __init__(self, settings):
        """Initialize the audio manager.
        
        Args:
            settings: Game settings object
        """
        self.settings = settings
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.music_loaded = False
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize pygame mixer and load audio assets."""
        if self._initialized:
            return
        
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.load_sounds()
        self.load_music()
        self.apply_volumes()
        self._initialized = True
    
    def load_sounds(self) -> None:
        """Load all sound effects."""
        sound_files = {
            'order_success': 'order_success',
            'order_fail': 'order_fail',
            'throw_drink': 'throw_drink',
            'restock': 'restock',
            'customer_reach_bar': 'customer_reach_bar'
        }
        
        extensions = ['.wav', '.ogg', '.mp3']
        
        for sound_name, base_filename in sound_files.items():
            self.sounds[sound_name] = None
            
            for ext in extensions:
                filename = base_filename + ext
                path = os.path.join(SOUNDS_DIR, filename)
                
                if os.path.exists(path):
                    try:
                        sound = pygame.mixer.Sound(path)
                        sound.set_volume(self.settings.sound_volume)
                        self.sounds[sound_name] = sound
                        print(f"Loaded sound: {path}")
                        break
                    except pygame.error as e:
                        print(f"Could not load {path}: {e}")
    
    def load_music(self) -> None:
        """Load background music."""
        music_files = ['background.ogg', 'background.mp3', 'background.wav']
        
        for filename in music_files:
            path = os.path.join(MUSIC_DIR, filename)
            
            if os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    self.music_loaded = True
                    print(f"Loaded background music: {path}")
                    break
                except pygame.error as e:
                    print(f"Could not load {path}: {e}")
    
    def apply_volumes(self) -> None:
        """Apply volume settings to all audio."""
        # Apply to sound effects
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.settings.sound_volume)
        
        # Apply to music
        if self.music_loaded:
            pygame.mixer.music.set_volume(self.settings.music_volume)
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect.
        
        Args:
            name: Name of the sound to play
        """
        sound = self.sounds.get(name)
        if sound:
            sound.play()
    
    def play_music(self, loops: int = -1) -> None:
        """Start playing background music.
        
        Args:
            loops: Number of loops (-1 for infinite)
        """
        if self.music_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops)
    
    def stop_music(self) -> None:
        """Stop background music."""
        pygame.mixer.music.stop()
    
    def pause_music(self) -> None:
        """Pause background music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Unpause background music."""
        pygame.mixer.music.unpause()
    
    def set_sound_volume(self, volume: float) -> None:
        """Set sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.settings.sound_volume = max(0.0, min(1.0, volume))
        self.apply_volumes()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.settings.music_volume = max(0.0, min(1.0, volume))
        if self.music_loaded:
            pygame.mixer.music.set_volume(self.settings.music_volume)