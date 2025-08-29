"""Game over scene."""

from typing import List
import pygame

from .base_scene import BaseScene
from ..ui import Button
from ..utils.constants import COLORS
from ..utils.logger import game_logger


class GameOverScene(BaseScene):
    """Game over scene implementation."""
    
    def __init__(self, game):
        """Initialize game over scene.
        
        Args:
            game: Reference to main game object
        """
        super().__init__(game)
        self.setup_ui()
        self.check_highscore()
    
    def setup_ui(self):
        """Setup UI elements."""
        font = self.game.assets.get_font('normal')
        
        self.restart_button = Button(
            self.game.screen_width // 2 - 100, 350, 200, 50,
            "Play Again", font, self.start_new_game
        )
        self.menu_button = Button(
            self.game.screen_width // 2 - 100, 420, 200, 50,
            "Main Menu", font, self.go_to_menu
        )
    
    def check_highscore(self):
        """Check if the current score is a high score."""
        if hasattr(self.game, 'final_score') and hasattr(self.game, 'save_system'):
            if self.game.save_system.is_highscore(self.game.final_score):
                # In a real game, you'd show a name entry dialog here
                position = self.game.save_system.save_highscore(
                    "Player", self.game.final_score, self.game.final_wave
                )
                game_logger.info(f"New high score position: {position}")
    
    def start_new_game(self):
        """Start a new game."""
        self.switch_to("game")
        # Reset the game scene
        if "game" in self.game.scene_manager.scenes:
            self.game.scene_manager.scenes["game"].reset_game_state()
    
    def go_to_menu(self):
        """Return to main menu."""
        self.switch_to("main_menu")
    
    def handle_events(self, events: List[pygame.event.Event]):
        """Handle input events.
        
        Args:
            events: List of pygame events
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_new_game()
                elif event.key == pygame.K_ESCAPE:
                    self.go_to_menu()
        
        # Update buttons
        self.restart_button.update(mouse_pos, mouse_clicked)
        self.menu_button.update(mouse_pos, mouse_clicked)
    
    def update(self, dt: float):
        """Update scene logic.
        
        Args:
            dt: Delta time in seconds
        """
        pass  # No continuous updates needed
    
    def draw(self, screen: pygame.Surface):
        """Draw the game over screen.
        
        Args:
            screen: Surface to draw on
        """
        screen.fill(COLORS['menu_bg'])
        
        # Title
        title_font = self.game.assets.get_font('large')
        title = title_font.render("Game Over!", True, COLORS['text_red'])
        title_rect = title.get_rect(center=(screen.get_width()//2, 100))
        screen.blit(title, title_rect)
        
        # Score
        font = self.game.assets.get_font('normal')
        final_score = getattr(self.game, 'final_score', 0)
        score_text = font.render(f"Final Score: {final_score}", True, COLORS['text_white'])
        score_rect = score_text.get_rect(center=(screen.get_width()//2, 200))
        screen.blit(score_text, score_rect)
        
        # Wave
        final_wave = getattr(self.game, 'final_wave', 1)
        wave_text = font.render(f"Wave Reached: {final_wave}", True, COLORS['text_white'])
        wave_rect = wave_text.get_rect(center=(screen.get_width()//2, 250))
        screen.blit(wave_text, wave_rect)
        
        # High scores
        if hasattr(self.game, 'save_system'):
            high_scores = self.game.save_system.get_highscores(5)
            if high_scores:
                small_font = self.game.assets.get_font('small')
                hs_title = small_font.render("High Scores:", True, COLORS['text_gold'])
                screen.blit(hs_title, (50, 300))
                
                for i, hs in enumerate(high_scores):
                    text = f"{i+1}. {hs['name']} - {hs['score']}"
                    hs_text = small_font.render(text, True, COLORS['text_white'])
                    screen.blit(hs_text, (50, 330 + i * 25))
        
        # Buttons
        self.restart_button.draw(screen)
        self.menu_button.draw(screen)