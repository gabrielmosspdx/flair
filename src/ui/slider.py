"""Slider UI component."""

from typing import Tuple

import pygame

from ..utils.constants import COLORS


class Slider:
    """A draggable slider UI element."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str,
        integer_only: bool = False
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
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.integer_only = integer_only
        self.val = int(initial_val) if integer_only else initial_val
        self.label = label
        self.dragging = False
        
        # Calculate handle position
        self.handle_pos = x + int((initial_val - min_val) / (max_val - min_val) * width)
        self.handle_rect = pygame.Rect(self.handle_pos - 10, y - 5, 20, 30)
    
    def update(
        self,
        mouse_pos: Tuple[int, int],
        mouse_pressed: bool,
        mouse_clicked: bool
    ) -> bool:
        """Update slider state.
        
        Args:
            mouse_pos: Current mouse position
            mouse_pressed: Whether mouse is currently pressed
            mouse_clicked: Whether mouse was clicked this frame
            
        Returns:
            True if value changed
        """
        old_val = self.val
        
        # Check if starting to drag
        if mouse_clicked and self.handle_rect.collidepoint(mouse_pos):
            self.dragging = True
        
        # Stop dragging when mouse released
        if not mouse_pressed:
            self.dragging = False
        
        # Update value while dragging
        if self.dragging:
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            new_val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = round(new_val) if self.integer_only else new_val
        
        # Allow clicking on track to jump to position
        elif mouse_clicked and self.rect.collidepoint(mouse_pos):
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            new_val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.val = round(new_val) if self.integer_only else new_val
        
        # Update handle rect position
        self.handle_rect.x = self.handle_pos - 10
        
        return self.val != old_val
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the slider.
        
        Args:
            screen: Surface to draw on
            font: Font for label
        """
        # Draw track
        pygame.draw.rect(screen, COLORS['text_gray'], self.rect)
        pygame.draw.rect(screen, COLORS['text_white'], self.rect, 2)
        
        # Draw filled portion
        filled_width = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        pygame.draw.rect(screen, COLORS['text_gold'], filled_rect)
        
        # Draw handle
        handle_color = COLORS['button_hover'] if self.dragging else COLORS['button_bg']
        pygame.draw.rect(screen, handle_color, self.handle_rect)
        pygame.draw.rect(screen, COLORS['text_gold'], self.handle_rect, 2)
        
        # Draw label and value
        if self.integer_only:
            label_text = f"{self.label}: {int(self.val)}"
        else:
            label_text = f"{self.label}: {self.val:.2f}"
        text_surface = font.render(label_text, True, COLORS['text_white'])
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))
    
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
        # Update handle position
        rel_pos = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos = self.rect.x + int(rel_pos * self.rect.width)
        self.handle_rect.x = self.handle_pos - 10