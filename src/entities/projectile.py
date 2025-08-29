"""Projectile entity for the Flair game."""

import math
from typing import Tuple

import pygame

from ..utils.constants import DrinkType, PROJECTILE_SPEED, PROJECTILE_MAX_LIFE


class Projectile(pygame.sprite.Sprite):
    """A thrown drink projectile."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        drink_type: DrinkType,
        speed: float = PROJECTILE_SPEED,
    ):
        """Initialize a projectile.

        Args:
            start_x: Starting X position
            start_y: Starting Y position
            target_x: Target X position
            target_y: Target Y position
            drink_type: Type of drink being thrown
            speed: Projectile speed
        """
        super().__init__()

        self.x = start_x
        self.y = start_y
        self.drink_type = drink_type
        self.speed = speed
        self.size = 8
        self.life = PROJECTILE_MAX_LIFE

        # Calculate trajectory
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = self.vy = 0

        # Create rect for collision detection
        self.rect = pygame.Rect(
            self.x - self.size, self.y - self.size, self.size * 2, self.size * 2
        )

        # For sprite rotation
        self.angle = 0

    def update(self) -> bool:
        """Update projectile position.

        Returns:
            True if projectile is still alive, False if it should be removed
        """
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

        # Update rotation for visual effect
        self.angle = (self.angle + 10) % 360

        self.life -= 1
        return self.life > 0

    def check_collision(self, target_rect: pygame.Rect) -> bool:
        """Check collision with a target.

        Args:
            target_rect: Rectangle to check collision against

        Returns:
            True if collision detected
        """
        return self.rect.colliderect(target_rect)
