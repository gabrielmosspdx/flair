"""Customer entity for the Flair game."""

import math
import random
from typing import Optional, Tuple

import pygame

from ..utils.constants import DrinkType, POSITIVE_DIALOGUE, NEGATIVE_DIALOGUE


class Customer(pygame.sprite.Sprite):
    """A customer that walks toward the bar and needs to be served."""
    
    def __init__(
        self,
        spawn_x: float,
        spawn_y: float,
        target_x: float,
        target_y: float,
        drink_type: DrinkType,
        base_speed: float = 0.5
    ):
        """Initialize a customer.
        
        Args:
            spawn_x: Starting X position
            spawn_y: Starting Y position
            target_x: Target X position (bar location)
            target_y: Target Y position (bar location)
            drink_type: Type of drink the customer wants
            base_speed: Movement speed
        """
        super().__init__()
        
        self.x = spawn_x
        self.y = spawn_y
        self.target_x = target_x
        self.target_y = target_y
        self.drink_type = drink_type
        self.speed = base_speed
        self.size = 20
        self.served = False
        self.service_successful = False
        self.dialogue = ""
        self.dialogue_timer = 0
        
        # Calculate movement vector
        dx = target_x - spawn_x
        dy = target_y - spawn_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = self.vy = 0
        
        # Create rect for collision detection
        self.rect = pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )
    
    def update(self) -> None:
        """Update customer position and state."""
        if not self.served:
            self.x += self.vx
            self.y += self.vy
            self.rect.center = (int(self.x), int(self.y))
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
    
    def distance_to_target(self) -> float:
        """Calculate distance to the target (bar).
        
        Returns:
            Distance in pixels
        """
        dx = self.x - self.target_x
        dy = self.y - self.target_y
        return math.sqrt(dx * dx + dy * dy)
    
    def set_served(self, dialogue: Optional[str] = None, successful: bool = True) -> None:
        """Mark customer as served.
        
        Args:
            dialogue: Optional dialogue to display
            successful: Whether the service was successful
        """
        self.served = True
        self.service_successful = successful
        
        if dialogue is None:
            if successful:
                dialogue = random.choice(POSITIVE_DIALOGUE)
            else:
                dialogue = random.choice(NEGATIVE_DIALOGUE)
        
        self.dialogue = dialogue
        self.dialogue_timer = 120  # 2 seconds at 60 FPS
    
    def has_reached_bar(self, threshold: float = 30) -> bool:
        """Check if customer has reached the bar.
        
        Args:
            threshold: Distance threshold to consider "reached"
            
        Returns:
            True if customer is within threshold of target
        """
        return not self.served and self.distance_to_target() < threshold