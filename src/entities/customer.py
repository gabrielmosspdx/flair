"""Customer entity for the Flair game."""

import random
from typing import Optional

import pygame

from ..utils.constants import NEGATIVE_DIALOGUE, POSITIVE_DIALOGUE, DrinkType
from .animated_sprite import AnimatedSprite


class Customer(AnimatedSprite):
    """A customer that walks toward the bar and needs to be served."""

    def __init__(
        self,
        spawn_x: float,
        spawn_y: float,
        target_x: float,
        target_y: float,
        drink_type: DrinkType,
        base_speed: float = 0.5,
        sprite_frames: Optional[dict] = None,
    ) -> None:
        """Initialize a customer.

        Args:
            spawn_x: Starting X position
            spawn_y: Starting Y position
            target_x: Target X position (bar location)
            target_y: Target Y position (bar location)
            drink_type: Type of drink the customer wants
            base_speed: Movement speed
            sprite_frames: Optional dictionary of animation frames
        """
        super().__init__()

        # Use Vector2 for better position/velocity handling
        self.position = pygame.math.Vector2(spawn_x, spawn_y)
        self.target = pygame.math.Vector2(target_x, target_y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0  # Store rotation angle

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
            # Calculate initial angle to face the bar
            import math

            angle_radians = math.atan2(direction.y, direction.x)
            # Just use the angle directly since we're negating in the rotate function
            self.angle = math.degrees(angle_radians)

        # Setup animations if sprite frames provided
        if sprite_frames:
            self._setup_animations(sprite_frames)
        else:
            # Fallback: create a colored circle as placeholder
            self._create_placeholder_sprite()

        # Create rect for collision detection
        if self.image and self.rect:
            self.rect.center = (int(self.position.x), int(self.position.y))
        else:
            self.rect = pygame.Rect(
                self.position.x - self.size,
                self.position.y - self.size,
                self.size * 2,
                self.size * 2,
            )

        # Ensure rect is never None after initialization
        assert self.rect is not None, "rect should be initialized"

        # Set initial animation
        if "walk" in self.animations:
            self.set_animation("walk")

    @property
    def x(self) -> float:
        """Get X position."""
        return float(self.position.x)

    @x.setter
    def x(self, value: float) -> None:
        """Set X position."""
        self.position.x = value

    @property
    def y(self) -> float:
        """Get Y position."""
        return float(self.position.y)

    @y.setter
    def y(self, value: float) -> None:
        """Set Y position."""
        self.position.y = value

    def update(self) -> None:
        """Update customer position and state."""
        if not self.served:
            self.position += self.velocity
            # Type assertion: rect is guaranteed non-None after __init__
            assert self.rect is not None
            self.rect.center = (int(self.position.x), int(self.position.y))

            # Update angle to always point toward the bar
            import math

            direction = self.target - self.position
            if direction.length() > 0:
                # Calculate the angle to the target
                # atan2(y, x) gives angle from positive x-axis (east)
                angle_radians = math.atan2(direction.y, direction.x)
                angle_degrees = math.degrees(angle_radians)

                # Just set the angle - we'll handle the rotation in the sprite class
                self.angle = angle_degrees

            # Update animation
            self.update_animation()
        else:
            # Switch to idle animation when served
            if "idle" in self.animations and self.current_animation != "idle":
                self.set_animation("idle")
            self.update_animation()

        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1

    def distance_to_target(self) -> float:
        """Calculate distance to the target (bar).

        Returns:
            Distance in pixels
        """
        return float(self.position.distance_to(self.target))

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

        # Change animation based on service success
        if successful and "happy" in self.animations:
            self.set_animation("happy")
        elif not successful and "sad" in self.animations:
            self.set_animation("sad")
        elif "idle" in self.animations:
            self.set_animation("idle")

    def has_reached_bar(self, threshold: float = 30) -> bool:
        """Check if customer has reached the bar.

        Args:
            threshold: Distance threshold to consider "reached"

        Returns:
            True if customer is within threshold of target
        """
        return not self.served and self.distance_to_target() < threshold

    def _setup_animations(self, sprite_frames: dict) -> None:
        """Setup animations from provided sprite frames.

        Args:
            sprite_frames: Dictionary containing animation frames
        """
        # Add walk animation
        if "walk" in sprite_frames:
            self.add_animation("walk", sprite_frames["walk"], loop=True)

        # Add idle animation
        if "idle" in sprite_frames:
            self.add_animation("idle", sprite_frames["idle"], loop=True)

        # Add served animation (happy/sad based on service)
        if "happy" in sprite_frames:
            self.add_animation("happy", sprite_frames["happy"], loop=True)
        if "sad" in sprite_frames:
            self.add_animation("sad", sprite_frames["sad"], loop=True)

        # Set animation speed based on movement speed
        self.set_animation_speed(0.1)

    def _create_placeholder_sprite(self) -> None:
        """Create a placeholder sprite when no sprite sheet is available."""
        # Create a simple colored circle as placeholder
        surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        # Different colors for different drink types
        color_map = {
            DrinkType.BEER: (255, 200, 100),
            DrinkType.WINE: (150, 50, 100),
            DrinkType.COCKTAIL: (100, 150, 255),
        }
        color = color_map.get(self.drink_type, (200, 200, 200))

        # Draw customer circle
        pygame.draw.circle(surface, color, (self.size, self.size), self.size)

        # Add a simple face
        eye_color = (0, 0, 0)
        pygame.draw.circle(surface, eye_color, (self.size - 5, self.size - 5), 2)
        pygame.draw.circle(surface, eye_color, (self.size + 5, self.size - 5), 2)

        # Create animations with the placeholder sprite
        self.add_animation("walk", [surface], loop=True)
        self.add_animation("idle", [surface], loop=True)
        self.add_animation("happy", [surface], loop=True)
        self.add_animation("sad", [surface], loop=True)
