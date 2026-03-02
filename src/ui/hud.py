"""Heads-up display (HUD) for the game."""

from typing import Dict, Optional

import pygame

from ..utils.constants import COLORS, DrinkType


def _draw_panel(screen: pygame.Surface, x: int, y: int, w: int, h: int, alpha: int = 150) -> None:
    """Draw a dark semi-transparent panel with a gold border."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((10, 5, 2, alpha))
    pygame.draw.rect(surf, (*COLORS["panel_border"], 90), pygame.Rect(0, 0, w, h), 1,
                     border_radius=4)
    screen.blit(surf, (x, y))


def _draw_divider(screen: pygame.Surface, cx: int, y: int, half_w: int) -> None:
    """Draw an ornamental line-diamond-line divider centred at cx."""
    col = COLORS["panel_border"]
    pygame.draw.line(screen, col, (cx - half_w, y), (cx - 10, y), 1)
    pygame.draw.line(screen, col, (cx + 10, y), (cx + half_w, y), 1)
    pts = [(cx, y - 5), (cx + 7, y), (cx, y + 5), (cx - 7, y)]
    pygame.draw.polygon(screen, COLORS["text_gold"], pts)


class HUD:
    """Manages the in-game heads-up display."""

    def __init__(self, assets_manager):
        """Initialize the HUD.

        Args:
            assets_manager: Asset manager for fonts and images
        """
        self.assets = assets_manager
        self.font_normal = self.assets.get_font("normal")
        self.font_small = self.assets.get_font("small")
        self.font_large = self.assets.get_font("large")

        # Animation states
        self.score_change_timer = 0
        self.score_change_amount = 0
        self.lives_flash_timer = 0
        self.wave_transition_timer = 0
        self.wave_transition_text = ""

    def flash_lives(self):
        """Trigger lives display flash effect."""
        self.lives_flash_timer = 30

    def show_score_change(self, amount: int):
        """Show score change animation.

        Args:
            amount: Points gained or lost
        """
        self.score_change_amount = amount
        self.score_change_timer = 60

    def show_wave_transition(self, wave_number: int):
        """Show wave transition animation.

        Args:
            wave_number: New wave number
        """
        self.wave_transition_text = f"Wave {wave_number}"
        self.wave_transition_timer = 120

    def update(self):
        """Update HUD animations."""
        if self.score_change_timer > 0:
            self.score_change_timer -= 1

        if self.lives_flash_timer > 0:
            self.lives_flash_timer -= 1

        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= 1

    def draw_stats(
        self, screen: pygame.Surface, score: int, wave: int, lives: int, x: int = 10, y: int = 10
    ):
        """Draw game statistics.

        Args:
            screen: Surface to draw on
            score: Current score
            wave: Current wave
            lives: Remaining lives
            x: X position for stats
            y: Y position for stats
        """
        # Background panel
        panel_h = 115
        _draw_panel(screen, x - 6, y - 5, 195, panel_h)

        # ── Score ──
        label_col = COLORS["text_amber"]
        score_label = self.font_small.render("SCORE", True, label_col)
        screen.blit(score_label, (x + 4, y + 4))

        score_color = COLORS["text_white"]
        if self.score_change_timer > 0:
            pulse = abs(self.score_change_timer % 20 - 10) / 10
            score_color = self._blend_colors(COLORS["text_white"], COLORS["text_gold"], pulse)

        score_text = self.font_normal.render(str(score), True, score_color)
        screen.blit(score_text, (x + 4, y + 20))

        # Score popup
        if self.score_change_timer > 0:
            change_alpha = min(255, self.score_change_timer * 8)
            change_color = (
                COLORS["text_green"] if self.score_change_amount > 0 else COLORS["text_red"]
            )
            prefix = "+" if self.score_change_amount > 0 else ""
            change_text = self.font_small.render(
                f"{prefix}{self.score_change_amount}", True, change_color
            )
            change_text.set_alpha(change_alpha)
            screen.blit(change_text, (x + 4 + score_text.get_width() + 8, y + 28))

        # ── Wave ──
        wave_label = self.font_small.render("WAVE", True, label_col)
        screen.blit(wave_label, (x + 4, y + 55))
        wave_text = self.font_normal.render(str(wave), True, COLORS["text_white"])
        screen.blit(wave_text, (x + 4, y + 70))

        # ── Lives ──
        lives_color = COLORS["text_white"]
        if self.lives_flash_timer > 0 and self.lives_flash_timer % 10 < 5:
            lives_color = COLORS["text_red"]

        lives_label = self.font_small.render("LIVES", True, label_col)
        screen.blit(lives_label, (x + 100, y + 55))

        # Heart icons
        heart_icon = self.assets.get_image("heart")
        if heart_icon:
            for i in range(lives):
                hx = x + 100 + i * 28
                hy = y + 72
                if self.lives_flash_timer > 0:
                    import random
                    hx += random.randint(-2, 2)
                    hy += random.randint(-2, 2)
                screen.blit(heart_icon, (hx, hy))
        else:
            lives_text = self.font_normal.render(str(lives), True, lives_color)
            screen.blit(lives_text, (x + 100, y + 70))

    def draw_inventory(
        self,
        screen: pygame.Surface,
        inventory: Dict[DrinkType, int],
        selected_drink: DrinkType,
        x: Optional[int] = None,
        y: int = 10,
    ):
        """Draw inventory display.

        Args:
            screen: Surface to draw on
            inventory: Current inventory counts
            selected_drink: Currently selected drink
            x: X position (None for right-aligned)
            y: Y position
        """
        if x is None:
            x = screen.get_width() - 215

        # Background panel for inventory
        panel_w = 205
        panel_h = 95
        _draw_panel(screen, x - 8, y - 30, panel_w, panel_h)

        # "DRINKS" label
        drinks_label = self.font_small.render("— DRINKS —", True, COLORS["text_amber"])
        lw = drinks_label.get_width()
        screen.blit(drinks_label, (x - 8 + (panel_w - lw) // 2, y - 26))

        for i, drink_type in enumerate(DrinkType):
            item_x = x + i * 63

            # Selection ring
            if drink_type == selected_drink:
                ring_surf = pygame.Surface((54, 54), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*COLORS["text_gold"], 50), (27, 27), 27)
                screen.blit(ring_surf, (item_x - 11, y - 4))
                pygame.draw.circle(screen, COLORS["text_gold"], (item_x + 16, y + 22), 27, 2)

            # Icon
            icon_name = f"{drink_type.name.lower()}_icon"
            icon = self.assets.get_image(icon_name)
            if icon:
                if drink_type == selected_drink:
                    scale = 1.12
                    scaled = pygame.transform.scale(
                        icon, (int(icon.get_width() * scale), int(icon.get_height() * scale))
                    )
                    screen.blit(scaled, (item_x - 2, y + 5))
                else:
                    screen.blit(icon, (item_x, y + 8))

            # Count
            count = inventory[drink_type]
            count_color = COLORS["text_white"] if count > 0 else COLORS["text_red"]
            count_text = self.font_small.render(str(count), True, count_color)
            screen.blit(count_text, (item_x + 10, y + 40))

            # Hotkey hint
            key_text = self.font_small.render(str(i + 1), True, COLORS["text_dim"])
            screen.blit(key_text, (item_x + 12, y + 55))

    def draw_wave_transition(self, screen: pygame.Surface):
        """Draw wave transition animation.

        Args:
            screen: Surface to draw on
        """
        if self.wave_transition_timer <= 0:
            return

        alpha = min(255, self.wave_transition_timer * 4)
        scale = 1.0 + (120 - self.wave_transition_timer) * 0.01

        # Dark backdrop for readability
        backdrop = pygame.Surface((500, 140), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, int(alpha * 0.55)))
        cx = screen.get_width() // 2
        cy = screen.get_height() // 3
        bx = cx - 250
        by = cy - 50
        screen.blit(backdrop, (bx, by))
        # Backdrop border
        bd_surf = pygame.Surface((500, 140), pygame.SRCALPHA)
        pygame.draw.rect(bd_surf, (*COLORS["text_gold"], int(alpha * 0.4)),
                         pygame.Rect(0, 0, 500, 140), 1)
        screen.blit(bd_surf, (bx, by))

        # Wave number text
        text = self.font_large.render(self.wave_transition_text.upper(), True, COLORS["text_gold"])
        sw = int(text.get_width() * scale)
        sh = int(text.get_height() * scale)
        scaled_text = pygame.transform.scale(text, (sw, sh))
        scaled_text.set_alpha(alpha)
        text_rect = scaled_text.get_rect(center=(cx, cy))
        screen.blit(scaled_text, text_rect)

        # Subtitle
        if self.wave_transition_timer > 60:
            sub_alpha = min(255, (self.wave_transition_timer - 60) * 8)
            subtitle = self.font_normal.render("Get Ready!", True, COLORS["text_amber"])
            subtitle.set_alpha(sub_alpha)
            sub_rect = subtitle.get_rect(center=(cx, cy + 55))
            screen.blit(subtitle, sub_rect)

            # Ornamental dividers
            div_surf = pygame.Surface((300, 12), pygame.SRCALPHA)
            div_col = (*COLORS["panel_border"], sub_alpha)
            pygame.draw.line(div_surf, div_col, (0, 6), (130, 6), 1)
            pygame.draw.line(div_surf, div_col, (170, 6), (300, 6), 1)
            pygame.draw.polygon(div_surf, (*COLORS["text_gold"], sub_alpha),
                                [(150, 0), (158, 6), (150, 12), (142, 6)])
            screen.blit(div_surf, (cx - 150, cy + 30))

    def draw_restock_overlay(self, screen: pygame.Surface, timer: int, max_timer: int):
        """Draw restock overlay.

        Args:
            screen: Surface to draw on
            timer: Current restock timer
            max_timer: Maximum restock timer
        """
        # Dark overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        cx = screen.get_width() // 2
        cy = screen.get_height() // 2

        # Panel
        pw, ph = 340, 100
        _draw_panel(screen, cx - pw // 2, cy - ph // 2, pw, ph, alpha=200)

        # Progress bar
        bar_width = 280
        bar_height = 24
        bar_x = cx - bar_width // 2
        bar_y = cy + 10

        progress = 1.0 - (timer / max_timer)
        # Track
        pygame.draw.rect(screen, COLORS["panel_dark"], (bar_x, bar_y, bar_width, bar_height),
                         border_radius=4)
        # Fill
        fill_width = max(0, int(bar_width * progress))
        if fill_width > 0:
            pygame.draw.rect(screen, COLORS["text_amber"],
                             (bar_x, bar_y, fill_width, bar_height), border_radius=4)
        # Border
        pygame.draw.rect(screen, COLORS["panel_border"], (bar_x, bar_y, bar_width, bar_height),
                         2, border_radius=4)

        # Label
        text = self.font_normal.render("RESTOCKING...", True, COLORS["text_gold"])
        text_rect = text.get_rect(center=(cx, cy - 18))
        screen.blit(text, text_rect)

        # Percentage
        percent = int(progress * 100)
        pct_text = self.font_small.render(f"{percent}%", True, COLORS["text_white"])
        pct_rect = pct_text.get_rect(center=(cx, bar_y + bar_height + 14))
        screen.blit(pct_text, pct_rect)

    def draw_pause_overlay(self, screen: pygame.Surface):
        """Draw pause overlay.

        Args:
            screen: Surface to draw on
        """
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        cx = screen.get_width() // 2
        cy = screen.get_height() // 2

        # Panel
        pw, ph = 360, 150
        _draw_panel(screen, cx - pw // 2, cy - ph // 2, pw, ph, alpha=210)

        # "PAUSED" text
        pause_text = self.font_large.render("PAUSED", True, COLORS["text_gold"])
        pause_rect = pause_text.get_rect(center=(cx, cy - 30))
        screen.blit(pause_text, pause_rect)

        # Ornamental divider
        _draw_divider(screen, cx, cy + 5, 120)

        # Instructions
        instructions = ["P  ·  Resume", "ESC  ·  Main Menu"]
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, COLORS["text_white"])
            inst_rect = inst_text.get_rect(center=(cx, cy + 30 + i * 28))
            screen.blit(inst_text, inst_rect)

    def _blend_colors(self, color1: tuple, color2: tuple, factor: float) -> tuple:
        """Blend two colors.

        Args:
            color1: First color
            color2: Second color
            factor: Blend factor (0 = color1, 1 = color2)

        Returns:
            Blended color
        """
        return tuple(int(c1 * (1 - factor) + c2 * factor) for c1, c2 in zip(color1, color2))
