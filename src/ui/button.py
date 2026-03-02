"""Button UI component."""

from typing import Callable, Optional, Tuple

import pygame

from ..utils.constants import COLORS


class Button:
    """A clickable button UI element with bar-sign styling."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        callback: Optional[Callable] = None,
        color_bg: Optional[Tuple[int, int, int]] = None,
        color_hover: Optional[Tuple[int, int, int]] = None,
        color_pressed: Optional[Tuple[int, int, int]] = None,
        color_text: Optional[Tuple[int, int, int]] = None,
    ):
        """Initialize a button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            font: Font to use for text
            callback: Function to call when clicked
            color_bg: Background color (default from COLORS)
            color_hover: Hover color (default from COLORS)
            color_pressed: Pressed color (default from COLORS)
            color_text: Text color (default white)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.enabled = True

        # Colors
        self.color_bg = color_bg or COLORS["button_bg"]
        self.color_hover = color_hover or COLORS["button_hover"]
        self.color_pressed = color_pressed or COLORS["button_pressed"]
        self.color_text = color_text or COLORS["text_white"]
        self.color_border = COLORS["button_border"]

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Update button state.

        Args:
            mouse_pos: Current mouse position
            mouse_clicked: Whether mouse was clicked this frame

        Returns:
            True if button was clicked
        """
        if not self.enabled:
            return False

        self.hovered = self.rect.collidepoint(mouse_pos)

        clicked = False
        if self.hovered and mouse_clicked:
            self.pressed = True
            if self.callback:
                self.callback()
            clicked = True
        else:
            self.pressed = False

        return clicked

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button with rounded corners, glow, shadow, and sheen.

        Args:
            screen: Surface to draw on
        """
        # Determine fill color based on state
        if not self.enabled:
            color = COLORS["tab_inactive"]
        elif self.pressed:
            color = self.color_pressed
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color_bg

        border_color = COLORS["text_gray"] if not self.enabled else self.color_border

        # Outer glow aura on hover
        if self.hovered and self.enabled:
            for radius_extra, alpha in [(14, 25), (8, 45), (3, 70)]:
                gw = self.rect.width + radius_extra * 2
                gh = self.rect.height + radius_extra * 2
                glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf,
                    (*border_color, alpha),
                    pygame.Rect(0, 0, gw, gh),
                    border_radius=8 + radius_extra,
                )
                screen.blit(glow_surf, (self.rect.x - radius_extra, self.rect.y - radius_extra))

        # Drop shadow (offset bottom-right)
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, 90),
            shadow_surf.get_rect(),
            border_radius=6,
        )
        screen.blit(shadow_surf, (self.rect.x + 3, self.rect.y + 4))

        # Button body
        pygame.draw.rect(screen, color, self.rect, border_radius=6)

        # Top-edge highlight sheen (depth illusion)
        if self.enabled and not self.pressed:
            sheen_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 4, self.rect.width - 10, 2)
            sheen_surf = pygame.Surface((sheen_rect.width, sheen_rect.height), pygame.SRCALPHA)
            sheen_surf.fill((255, 255, 255, 30))
            screen.blit(sheen_surf, sheen_rect.topleft)

        # Border
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=6)

        # Text (shifts down 1px when pressed for click-feel)
        text_color = COLORS["text_dim"] if not self.enabled else self.color_text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        if self.pressed:
            text_rect.y += 1
        screen.blit(text_surface, text_rect)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button.

        Args:
            enabled: Whether button should be enabled
        """
        self.enabled = enabled
        if not enabled:
            self.hovered = False
            self.pressed = False
