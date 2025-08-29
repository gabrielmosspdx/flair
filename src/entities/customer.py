"""Customer entity for the Flair game."""

import random
from typing import Optional

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
    ) -> None:
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
        
        # Use Vector2 for better position/velocity handling
        self.position = pygame.math.Vector2(spawn_x, spawn_y)
        self.target = pygame.math.Vector2(target_x, target_y)
        self.velocity = pygame.math.Vector2(0, 0)
        
        self.drink_type: DrinkType = drink_type
        self.speed: float = base_speed
        self.size: int = 20
        self.served: bool = False
        self.service_successful: bool = False
        self.dialogue: str = ""
        self.dialogue_timer: int = 0
        
        # Calculate movement vector using Vector2
        direction = self.target - self.position
        if direction.length() > 0:
            direction.normalize_ip()
            self.velocity = direction * self.speed
        
        # Create rect for collision detection
        self.rect = pygame.Rect(
            self.position.x - self.size,
            self.position.y - self.size,
            self.size * 2,
            self.size * 2
        )
    
    @property
    def x(self) -> float:
        """Get X position."""
        return self.position.x
    
    @x.setter
    def x(self, value: float) -> None:
        """Set X position."""
        self.position.x = value
    
    @property
    def y(self) -> float:
        """Get Y position."""
        return self.position.y
    
    @y.setter
    def y(self, value: float) -> None:
        """Set Y position."""
        self.position.y = value
    
    def update(self) -> None:
        """Update customer position and state."""
        if not self.served:
            self.position += self.velocity
            self.rect.center = (int(self.position.x), int(self.position.y))
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
    
    def distance_to_target(self) -> float:
        """Calculate distance to the target (bar).
        
        Returns:
            Distance in pixels
        """
        return self.position.distance_to(self.target)
    
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