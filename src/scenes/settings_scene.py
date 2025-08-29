"""Settings scene."""

from typing import List
import pygame

from .base_scene import BaseScene
from ..ui import Button, Slider
from ..utils.constants import COLORS
from ..utils.logger import game_logger


class SettingsScene(BaseScene):
    """Settings scene implementation."""
    
    def __init__(self, game):
        """Initialize settings scene.
        
        Args:
            game: Reference to main game object
        """
        super().__init__(game)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        font = self.game.assets.get_font('normal')
        
        # Back button
        self.back_button = Button(
            50, self.game.screen_height - 80, 100, 40,
            "Back", font, self.go_back
        )
        
        # Audio sliders
        self.sound_slider = Slider(
            350, 290, 250, 0.0, 1.0,
            self.game.settings.sound_volume, "Sound Volume"
        )
        self.music_slider = Slider(
            350, 360, 250, 0.0, 1.0,
            self.game.settings.music_volume, "Music Volume"
        )
    
    def go_back(self):
        """Return to main menu."""
        # Save settings when leaving
        self.game.settings.save()
        game_logger.info("Settings saved")
        self.switch_to("main_menu")
    
    def handle_events(self, events: List[pygame.event.Event]):
        """Handle input events.
        
        Args:
            events: List of pygame events
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
        
        # Update button
        self.back_button.update(mouse_pos, mouse_clicked)
        
        # Update sliders
        if self.sound_slider.update(mouse_pos, mouse_pressed, mouse_clicked):
            new_volume = self.sound_slider.get_value()
            self.game.audio.set_sound_volume(new_volume)
            self.game.settings.sound_volume = new_volume
            game_logger.debug(f"Sound volume changed to: {new_volume:.2f}")
        
        if self.music_slider.update(mouse_pos, mouse_pressed, mouse_clicked):
            new_volume = self.music_slider.get_value()
            self.game.audio.set_music_volume(new_volume)
            self.game.settings.music_volume = new_volume
            game_logger.debug(f"Music volume changed to: {new_volume:.2f}")
    
    def update(self, dt: float):
        """Update scene logic.
        
        Args:
            dt: Delta time in seconds
        """
        pass  # No continuous updates needed
    
    def draw(self, screen: pygame.Surface):
        """Draw the settings screen.
        
        Args:
            screen: Surface to draw on
        """
        screen.fill(COLORS['menu_bg'])
        
        # Title
        title_font = self.game.assets.get_font('large')
        title = title_font.render("Settings", True, COLORS['text_gold'])
        title_rect = title.get_rect(center=(self.game.screen_width//2, 100))
        screen.blit(title, title_rect)
        
        # Audio section
        font = self.game.assets.get_font('normal')
        audio_label = font.render("Audio", True, COLORS['text_gold'])
        screen.blit(audio_label, (350, 240))
        
        # Draw sliders
        small_font = self.game.assets.get_font('small')
        self.sound_slider.draw(screen, small_font)
        self.music_slider.draw(screen, small_font)
        
        # Controls info
        controls_y = 450
        controls_label = font.render("Controls", True, COLORS['text_gold'])
        screen.blit(controls_label, (50, controls_y - 30))
        
        controls = [
            ("1/2/3", "Select Drink"),
            ("Mouse", "Aim & Throw"),
            ("R", "Restock"),
            ("P", "Pause"),
            ("F3", "Debug Overlay"),
            ("F5", "Quick Save"),
            ("ESC", "Menu")
        ]
        
        for i, (key, action) in enumerate(controls):
            # Draw key
            key_text = small_font.render(key, True, COLORS['text_gold'])
            screen.blit(key_text, (50, controls_y + i * 25))
            
            # Draw action
            action_text = small_font.render(f"- {action}", True, COLORS['text_white'])
            screen.blit(action_text, (150, controls_y + i * 25))
        
        # Back button
        self.back_button.draw(screen)