"""Main menu scene."""

from typing import List

import pygame

from ..ui import Button
from ..utils.constants import COLORS
from ..utils.logger import game_logger
from .base_scene import BaseScene


class MainMenuScene(BaseScene):
    """Main menu scene implementation."""

    def __init__(self, game):
        """Initialize main menu scene.

        Args:
            game: Reference to main game object
        """
        super().__init__(game)
        self.setup_ui()

    def setup_ui(self):
        """Setup menu UI elements."""
        screen_width = self.game.screen.get_width()

        button_width = 200
        button_height = 50
        center_x = screen_width // 2 - button_width // 2
        start_y = 220
        spacing = 80

        font = self.game.assets.get_font("normal")

        self.buttons = [
            Button(
                center_x, start_y, button_width, button_height, "New Game", font, self.start_game
            ),
            Button(
                center_x,
                start_y + spacing,
                button_width,
                button_height,
                "Settings",
                font,
                self.open_settings,
            ),
            Button(
                center_x,
                start_y + spacing * 2,
                button_width,
                button_height,
                "Quit",
                font,
                self.quit_game,
            ),
        ]

    def start_game(self):
        """Start a new game."""
        game_logger.info("Starting new game from menu")
        # Explicitly start a new game with current settings
        if "game" in self.game.scene_manager.scenes:
            game_scene = self.game.scene_manager.scenes["game"]
            game_scene.start_new_game()
        self.switch_to("game")

    def open_settings(self):
        """Open settings menu."""
        self.switch_to("settings")

    def quit_game(self):
        """Quit the game."""
        self.game.running = False

    def handle_events(self, events: List[pygame.event.Event]):
        """Handle menu events.

        Args:
            events: List of pygame events
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()

        # Update buttons
        for button in self.buttons:
            button.update(mouse_pos, mouse_clicked)

    def update(self, dt: float):
        """Update menu logic.

        Args:
            dt: Delta time in seconds
        """
        pass  # Menu doesn't need continuous updates

    def draw(self, screen: pygame.Surface):
        """Draw the menu.

        Args:
            screen: Surface to draw on
        """
        screen.fill(COLORS["menu_bg"])

        # Draw title
        title_font = self.game.assets.get_font("title")
        title = title_font.render("Flair!", True, COLORS["text_gold"])
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        # Draw version
        # small_font = self.game.assets.get_font('small')
        # version = small_font.render("Enhanced Edition", True, COLORS['text_gray'])
        # version_rect = version.get_rect(center=(screen.get_width()//2, 150))
        # screen.blit(version, version_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
