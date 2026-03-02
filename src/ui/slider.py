"""Slider UI component."""

from typing import Tuple

import pygame

from ..utils.constants import COLORS


class Slider:
    """A draggable slider UI element styled as a bar tap handle."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str,
        integer_only: bool = False,
    ):
        """Initialize a slider.

        Args:
            x: X position
            y: Y position
            width: Slider width
            min_val: Minimum value
            max_val: Maximum value
            initial_val: Initial value
            label: Label text
            integer_only: If True, slider will only return integer values
        """
        self.rect = pygame.Rect(x, y, width, 14)
        self.min_val = min_val
        self.max_val = max_val
        self.integer_only = integer_only
        self.val = int(initial_val) if integer_only else initial_val
        self.label = label
        self.dragging = False

        # Calculate handle position
        self.handle_pos = x + int((initial_val - min_val) / (max_val - min_val) * width)
        self.handle_rect = pygame.Rect(self.handle_pos - 8, y - 8, 16, 30)

    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool, mouse_clicked: bool) -> bool:
        """Update slider state.

        Args:
            mouse_pos: Current mouse position
            mouse_pressed: Whether mouse is currently pressed
            mouse_clicked: Whether mouse was clicked this frame

        Returns:
            True if value changed
        """
        old_val = self.val

        if mouse_clicked and self.handle_rect.collidepoint(mouse_pos):
            self.dragging = True

        if not mouse_pressed:
            self.dragging = False

        if self.dragging:
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            new_val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = round(new_val) if self.integer_only else new_val
        elif mouse_clicked and self.rect.collidepoint(mouse_pos):
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            new_val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = round(new_val) if self.integer_only else new_val

        self.handle_rect.x = self.handle_pos - 8
        return self.val != old_val

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the slider.

        Args:
            screen: Surface to draw on
            font: Font for label
        """
        # Label and value above
        if self.integer_only:
            label_str = f"{self.label}: {int(self.val)}"
        else:
            label_str = f"{self.label}: {self.val:.2f}"
        label_surf = font.render(label_str, True, COLORS["text_white"])
        screen.blit(label_surf, (self.rect.x, self.rect.y - 22))

        # Track groove (dark inset)
        groove_rect = pygame.Rect(self.rect.x, self.rect.y + 3, self.rect.width, 8)
        pygame.draw.rect(screen, COLORS["panel_dark"], groove_rect, border_radius=4)
        pygame.draw.rect(screen, COLORS["text_dim"], groove_rect, 1, border_radius=4)

        # Filled portion (amber fill)
        filled_w = int(
            (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        )
        if filled_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y + 3, filled_w, 8)
            pygame.draw.rect(screen, COLORS["text_amber"], fill_rect, border_radius=4)

        # Handle (tap-handle style: rounded rectangle)
        handle_col = COLORS["button_hover"] if self.dragging else COLORS["button_bg"]
        pygame.draw.rect(screen, handle_col, self.handle_rect, border_radius=4)
        # Handle highlight
        h_sheen = pygame.Surface((self.handle_rect.width - 4, 2), pygame.SRCALPHA)
        h_sheen.fill((255, 255, 255, 40))
        screen.blit(h_sheen, (self.handle_rect.x + 2, self.handle_rect.y + 3))
        # Handle border
        pygame.draw.rect(screen, COLORS["button_border"], self.handle_rect, 1, border_radius=4)

    def get_value(self) -> float:
        """Get the current value.

        Returns:
            Current slider value
        """
        return self.val

    def set_value(self, value: float) -> None:
        """Set the slider value.

        Args:
            value: New value (will be clamped to min/max)
        """
        clamped_val = max(self.min_val, min(self.max_val, value))
        self.val = round(clamped_val) if self.integer_only else clamped_val
        rel_pos = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos = self.rect.x + int(rel_pos * self.rect.width)
        self.handle_rect.x = self.handle_pos - 8
