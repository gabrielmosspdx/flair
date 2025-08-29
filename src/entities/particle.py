"""Particle effects for the Flair game."""

import random
from typing import Tuple, Any

import pygame

from ..utils.constants import PARTICLE_LIFE


class Particle(pygame.sprite.Sprite):
    """A visual particle effect."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        """Initialize a particle.

        Args:
            x: Starting X position
            y: Starting Y position
            color: RGB color tuple
        """
        super().__init__()

        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = PARTICLE_LIFE
        self.max_life = PARTICLE_LIFE
        self.color = color
        self.size = random.randint(2, 5)

        # Create surface for the particle
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update particle position and life."""
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95  # Apply friction
        self.vy *= 0.95
        self.life -= 1

        # Update position
        self.rect.center = (int(self.x), int(self.y))

        # Update alpha based on life
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)

        # Redraw particle with new alpha
        self.image.fill((0, 0, 0, 0))  # Clear
        pygame.draw.circle(self.image, color_with_alpha, (self.size, self.size), self.size)

        if self.life <= 0:
            self.kill()


class ParticleSystem:
    """Manages multiple particle effects."""

    def __init__(self):
        """Initialize the particle system."""
        self.particles = pygame.sprite.Group()

    def create_burst(self, x: float, y: float, color: Tuple[int, int, int], count: int = 8) -> None:
        """Create a burst of particles.

        Args:
            x: Center X position
            y: Center Y position
            color: RGB color tuple
            count: Number of particles to create
        """
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.add(particle)

    def update(self) -> None:
        """Update all particles and remove dead ones."""
        for particle in list(self.particles):
            if not particle.update():
                self.particles.remove(particle)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles.

        Args:
            surface: Surface to draw on
        """
        self.particles.draw(surface)
