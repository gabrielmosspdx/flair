"""Base scene class for game states."""

from abc import ABC, abstractmethod
from typing import List

import pygame


class BaseScene(ABC):
    """Abstract base class for all game scenes."""

    def __init__(self, game):
        """Initialize the scene.

        Args:
            game: Reference to main game object
        """
        self.game = game
        self.next_scene = None
        self.is_active = True

    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle input events.

        Args:
            events: List of pygame events
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene.

        Args:
            screen: Surface to draw on
        """
        pass

    def enter(self) -> None:
        """Called when scene becomes active."""
        self.is_active = True

    def exit(self) -> None:
        """Called when scene becomes inactive."""
        self.is_active = False

    def switch_to(self, scene_name: str) -> None:
        """Request transition to another scene.

        Args:
            scene_name: Name of scene to switch to
        """
        self.next_scene = scene_name
