"""Scene management system."""

from typing import Dict, Optional, List
import pygame
from .base_scene import BaseScene


class SceneManager:
    """Manages game scenes and transitions."""
    
    def __init__(self):
        """Initialize the scene manager."""
        self.scenes: Dict[str, BaseScene] = {}
        self.current_scene: Optional[BaseScene] = None
        self.current_scene_name: Optional[str] = None
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_speed = 5.0
        
    def add_scene(self, name: str, scene: BaseScene) -> None:
        """Add a scene to the manager.
        
        Args:
            name: Scene identifier
            scene: Scene instance
        """
        self.scenes[name] = scene
        
    def switch_to(self, name: str, with_transition: bool = True) -> None:
        """Switch to a different scene.
        
        Args:
            name: Name of scene to switch to
            with_transition: Whether to use fade transition
        """
        if name not in self.scenes:
            print(f"Scene '{name}' not found")
            return
            
        if with_transition:
            self.transitioning = True
            self.next_scene_name = name
        else:
            self._perform_switch(name)
    
    def _perform_switch(self, name: str) -> None:
        """Perform the actual scene switch.
        
        Args:
            name: Name of scene to switch to
        """
        if self.current_scene:
            self.current_scene.exit()
            
        self.current_scene = self.scenes[name]
        self.current_scene_name = name
        self.current_scene.enter()
        
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Pass events to current scene.
        
        Args:
            events: List of pygame events
        """
        if self.current_scene and not self.transitioning:
            self.current_scene.handle_events(events)
            
            # Check if scene requested a transition
            if self.current_scene.next_scene:
                self.switch_to(self.current_scene.next_scene)
                self.current_scene.next_scene = None
    
    def update(self, dt: float) -> None:
        """Update current scene.
        
        Args:
            dt: Delta time in seconds
        """
        # Handle transitions
        if self.transitioning:
            if self.transition_alpha < 255:
                self.transition_alpha = min(255, self.transition_alpha + self.transition_speed * dt * 255)
            else:
                self._perform_switch(self.next_scene_name)
                self.transitioning = False
                self.transition_alpha = 0
        
        # Update current scene
        if self.current_scene and not self.transitioning:
            self.current_scene.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw current scene.
        
        Args:
            screen: Surface to draw on
        """
        if self.current_scene:
            self.current_scene.draw(screen)
            
            # Draw transition overlay
            if self.transitioning:
                overlay = pygame.Surface(screen.get_size())
                overlay.set_alpha(int(self.transition_alpha))
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
    
    def get_current_scene_name(self) -> Optional[str]:
        """Get the name of the current scene.
        
        Returns:
            Current scene name or None
        """
        return self.current_scene_name