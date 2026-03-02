"""Main menu scene."""

import math
import random
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

        # Animation state
        self.glow_timer = 0.0

        # Floating ambient motes (golden dust in bar light)
        screen_w = self.game.screen.get_width()
        screen_h = self.game.screen.get_height()
        self.motes = [
            {
                "x": random.uniform(0, screen_w),
                "y": random.uniform(0, screen_h),
                "vy": random.uniform(-0.25, -0.7),
                "drift": random.uniform(-0.12, 0.12),
                "size": random.randint(1, 2),
                "alpha": random.randint(18, 70),
            }
            for _ in range(55)
        ]

    def setup_ui(self):
        """Setup menu UI elements."""
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()

        button_width = 220
        button_height = 54
        center_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 40
        spacing = 76

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

        for button in self.buttons:
            button.update(mouse_pos, mouse_clicked)

    def update(self, dt: float):
        """Update menu animations.

        Args:
            dt: Delta time in seconds
        """
        self.glow_timer += dt * 1.8
        screen_w = self.game.screen.get_width()
        screen_h = self.game.screen.get_height()

        for m in self.motes:
            m["y"] += m["vy"]
            m["x"] += m["drift"]
            if m["y"] < -4:
                m["y"] = screen_h + 4
                m["x"] = random.uniform(0, screen_w)
            if m["x"] < -4:
                m["x"] = screen_w + 4
            if m["x"] > screen_w + 4:
                m["x"] = -4

    def _draw_bg(self, screen: pygame.Surface):
        """Draw layered background with vignette glow."""
        screen.fill(COLORS["menu_bg"])
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2

        # Warm amber spotlight centred slightly above mid
        spotlight_cx = cx
        spotlight_cy = int(screen.get_height() * 0.35)
        for r in range(420, 60, -60):
            t = (420 - r) / 360  # 0 near edge, 1 near centre
            alpha = max(0, int(18 * (1 - t)))
            spot_surf = pygame.Surface((r * 2, r), pygame.SRCALPHA)
            pygame.draw.ellipse(spot_surf, (180, 100, 20, alpha), spot_surf.get_rect())
            screen.blit(spot_surf, (spotlight_cx - r, spotlight_cy - r // 2))

        # Floating golden motes
        for m in self.motes:
            ms = pygame.Surface((m["size"] * 2 + 2, m["size"] * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(
                ms,
                (255, 215, 0, m["alpha"]),
                (m["size"] + 1, m["size"] + 1),
                m["size"],
            )
            screen.blit(ms, (int(m["x"]), int(m["y"])))

    def _draw_title(self, screen: pygame.Surface):
        """Draw the animated glowing title."""
        title_font = self.game.assets.get_font("title")
        title_text = "Flair!"
        title_center = (screen.get_width() // 2, 130)

        glow_pulse = (math.sin(self.glow_timer) + 1) / 2  # 0.0 → 1.0

        base = title_font.render(title_text, True, COLORS["text_gold"])

        # Glow aura layers: scale-up + low alpha
        for scale, max_alpha in [(1.14, 35), (1.08, 55), (1.03, 80)]:
            layer = pygame.transform.scale(
                base, (int(base.get_width() * scale), int(base.get_height() * scale))
            )
            layer_alpha = int(glow_pulse * max_alpha)
            layer.set_alpha(max(0, layer_alpha))
            lr = layer.get_rect(center=title_center)
            screen.blit(layer, lr)

        # Main title
        title_rect = base.get_rect(center=title_center)
        screen.blit(base, title_rect)

    def _draw_ornaments(self, screen: pygame.Surface):
        """Draw tagline, ornamental dividers, and footer hint."""
        cx = screen.get_width() // 2
        small_font = self.game.assets.get_font("small")

        # Tagline
        tagline = small_font.render("throw drinks.  serve chaos.", True, COLORS["text_gray"])
        tl_rect = tagline.get_rect(center=(cx, 190))
        screen.blit(tagline, tl_rect)

        # Ornamental divider
        div_y = 220
        div_col = COLORS["panel_border"]
        half_w = 200
        pygame.draw.line(screen, div_col, (cx - half_w, div_y), (cx - 12, div_y), 1)
        pygame.draw.line(screen, div_col, (cx + 12, div_y), (cx + half_w, div_y), 1)
        pts = [(cx, div_y - 6), (cx + 9, div_y), (cx, div_y + 6), (cx - 9, div_y)]
        pygame.draw.polygon(screen, COLORS["text_gold"], pts)

        # Footer ESC hint
        hint = small_font.render("ESC  ·  quit", True, COLORS["text_dim"])
        hint_rect = hint.get_rect(center=(cx, screen.get_height() - 22))
        screen.blit(hint, hint_rect)

    def draw(self, screen: pygame.Surface):
        """Draw the menu.

        Args:
            screen: Surface to draw on
        """
        self._draw_bg(screen)
        self._draw_title(screen)
        self._draw_ornaments(screen)

        for button in self.buttons:
            button.draw(screen)
