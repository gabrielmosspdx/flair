"""Game over scene."""

from typing import List

import pygame

from ..ui import Button
from ..utils.constants import COLORS
from ..utils.logger import game_logger
from .base_scene import BaseScene


def _draw_panel(screen: pygame.Surface, x: int, y: int, w: int, h: int,
                border_col=None, alpha: int = 185) -> None:
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((10, 5, 2, alpha))
    bc = border_col or COLORS["text_red"]
    pygame.draw.rect(surf, (*bc, 130), pygame.Rect(0, 0, w, h), 2, border_radius=6)
    pygame.draw.rect(surf, (*bc, 40), pygame.Rect(4, 4, w - 8, h - 8), 1, border_radius=4)
    screen.blit(surf, (x, y))


def _draw_divider(screen: pygame.Surface, cx: int, y: int, half_w: int,
                  col=None) -> None:
    c = col or COLORS["panel_border"]
    pygame.draw.line(screen, c, (cx - half_w, y), (cx - 10, y), 1)
    pygame.draw.line(screen, c, (cx + 10, y), (cx + half_w, y), 1)
    pts = [(cx, y - 5), (cx + 8, y), (cx, y + 5), (cx - 8, y)]
    pygame.draw.polygon(screen, COLORS["text_gold"], pts)


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
        font = self.game.assets.get_font("normal")
        cx = self.game.screen_width // 2

        self.restart_button = Button(
            cx - 110, 460, 210, 54, "Play Again", font, self.start_new_game
        )
        self.menu_button = Button(
            cx - 110, 526, 210, 54, "Main Menu", font, self.go_to_menu
        )

    def check_highscore(self):
        """Check if the current score is a high score."""
        if hasattr(self.game, "final_score") and hasattr(self.game, "save_system"):
            if self.game.save_system.is_highscore(self.game.final_score):
                position = self.game.save_system.save_highscore(
                    "Player", self.game.final_score, self.game.final_wave
                )
                game_logger.info(f"New high score position: {position}")

    def start_new_game(self):
        """Start a new game."""
        if "game" in self.game.scene_manager.scenes:
            self.game.scene_manager.scenes["game"].start_new_game()
        self.switch_to("game")

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

        self.restart_button.update(mouse_pos, mouse_clicked)
        self.menu_button.update(mouse_pos, mouse_clicked)

    def update(self, dt: float):
        """Update scene logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def draw(self, screen: pygame.Surface):
        """Draw the game over screen.

        Args:
            screen: Surface to draw on
        """
        screen.fill(COLORS["menu_bg"])

        cx = screen.get_width() // 2
        cy = screen.get_height() // 2

        # ── Central stats panel ──
        pw, ph = 520, 360
        px, py = cx - pw // 2, 80
        _draw_panel(screen, px, py, pw, ph, border_col=COLORS["text_red"])

        # ── "LAST CALL!" header ──
        title_font = self.game.assets.get_font("large")
        title = title_font.render("LAST CALL!", True, COLORS["text_red"])
        title_rect = title.get_rect(center=(cx, 120))
        screen.blit(title, title_rect)

        _draw_divider(screen, cx, 158, 180, col=COLORS["text_red"])

        # ── Score and Wave rows ──
        font = self.game.assets.get_font("normal")
        small_font = self.game.assets.get_font("small")

        final_score = getattr(self.game, "final_score", 0)
        final_wave = getattr(self.game, "final_wave", 1)

        col_label = px + 40
        col_val = px + pw - 40
        row1 = 180
        row2 = 225

        # Labels (left-aligned)
        lbl_score = small_font.render("DRINKS SERVED", True, COLORS["text_amber"])
        screen.blit(lbl_score, (col_label, row1))
        lbl_wave = small_font.render("LAST WAVE", True, COLORS["text_amber"])
        screen.blit(lbl_wave, (col_label, row2))

        # Values (right-aligned)
        val_score = font.render(str(final_score), True, COLORS["text_white"])
        screen.blit(val_score, (col_val - val_score.get_width(), row1 - 2))
        val_wave = font.render(str(final_wave), True, COLORS["text_white"])
        screen.blit(val_wave, (col_val - val_wave.get_width(), row2 - 2))

        # Dotted separator line
        for dot_x in range(col_label, col_val, 6):
            dot_surf = pygame.Surface((3, 1), pygame.SRCALPHA)
            dot_surf.fill((*COLORS["panel_border"], 80))
            screen.blit(dot_surf, (dot_x, row1 + 22))
        for dot_x in range(col_label, col_val, 6):
            dot_surf = pygame.Surface((3, 1), pygame.SRCALPHA)
            dot_surf.fill((*COLORS["panel_border"], 80))
            screen.blit(dot_surf, (dot_x, row2 + 22))

        _draw_divider(screen, cx, 265, 190)

        # ── High Scores ──
        if hasattr(self.game, "save_system"):
            high_scores = self.game.save_system.get_highscores(5)
            if high_scores:
                hs_title = small_font.render("— HIGH SCORES —", True, COLORS["text_amber"])
                hs_rect = hs_title.get_rect(center=(cx, 285))
                screen.blit(hs_title, hs_rect)

                for i, hs in enumerate(high_scores):
                    row_y = 308 + i * 22
                    rank_col = COLORS["text_gold"] if i == 0 else COLORS["text_white"]
                    rank_txt = small_font.render(f"{i + 1}.", True, COLORS["text_amber"])
                    name_txt = small_font.render(hs["name"], True, rank_col)
                    score_txt = small_font.render(str(hs["score"]), True, rank_col)
                    screen.blit(rank_txt, (col_label, row_y))
                    screen.blit(name_txt, (col_label + 30, row_y))
                    screen.blit(score_txt, (col_val - score_txt.get_width(), row_y))

        # ── Buttons ──
        self.restart_button.draw(screen)
        self.menu_button.draw(screen)

        # Footer hint
        hint = small_font.render("SPACE / ENTER  ·  Play Again     ESC  ·  Menu",
                                 True, COLORS["text_dim"])
        hint_rect = hint.get_rect(center=(cx, screen.get_height() - 22))
        screen.blit(hint, hint_rect)
