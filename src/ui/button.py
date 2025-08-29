"""Button UI component."""

from typing import Callable, Optional, Tuple

import pygame

from ..utils.constants import COLORS


class Button:
    """A clickable button UI element."""
    
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
        color_text: Optional[Tuple[int, int, int]] = None
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
        self.color_bg = color_bg or COLORS['button_bg']
        self.color_hover = color_hover or COLORS['button_hover']
        self.color_pressed = color_pressed or COLORS['button_pressed']
        self.color_text = color_text or COLORS['text_white']
        self.color_border = COLORS['text_gold']
    
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
        """Draw the button.
        
        Args:
            screen: Surface to draw on
        """
        # Determine color based on state
        if not self.enabled:
            color = COLORS['text_gray']
        elif self.pressed:
            color = self.color_pressed
        elif self.hovered:
            color = self.color_hover
        else:
            color = self.color_bg
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.color_border, self.rect, 2)
        
        # Draw text
        text_color = COLORS['text_gray'] if not self.enabled else self.color_text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
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