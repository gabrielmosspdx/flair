"""Centralized input management system."""

from typing import Dict, List, Optional, Tuple, Callable
import pygame
from ..utils.constants import DEFAULT_CONTROLLER_MAPPINGS, DEFAULT_CONTROLLER_DEADZONE


class InputManager:
    """Manages all input from keyboard, mouse, and controllers."""
    
    def __init__(self):
        """Initialize the input manager."""
        self.keys_pressed: Dict[int, bool] = {}
        self.keys_just_pressed: Dict[int, bool] = {}
        self.keys_just_released: Dict[int, bool] = {}
        
        self.mouse_buttons: Dict[int, bool] = {}
        self.mouse_just_clicked: Dict[int, bool] = {}
        self.mouse_position: Tuple[int, int] = (0, 0)
        self.mouse_delta: Tuple[int, int] = (0, 0)
        
        self.controller: Optional[pygame.joystick.Joystick] = None
        self.controller_buttons: Dict[int, bool] = {}
        self.controller_axes: Dict[int, float] = {}
        self.controller_deadzone = DEFAULT_CONTROLLER_DEADZONE
        self.controller_mappings = DEFAULT_CONTROLLER_MAPPINGS.copy()
        
        self.key_bindings: Dict[str, List[int]] = {
            'select_beer': [pygame.K_1],
            'select_wine': [pygame.K_2],
            'select_cocktail': [pygame.K_3],
            'restock': [pygame.K_r],
            'pause': [pygame.K_p, pygame.K_ESCAPE],
        }
        
        self.init_controller()
        
    def init_controller(self) -> None:
        """Initialize game controller if available."""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print(f"Controller connected: {self.controller.get_name()}")
            
    def update(self, events: List[pygame.event.Event]) -> None:
        """Update input state based on pygame events.
        
        Args:
            events: List of pygame events from current frame
        """
        # Reset just pressed/released states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_clicked.clear()
        
        # Store previous mouse position
        prev_mouse = self.mouse_position
        self.mouse_position = pygame.mouse.get_pos()
        self.mouse_delta = (
            self.mouse_position[0] - prev_mouse[0],
            self.mouse_position[1] - prev_mouse[1]
        )
        
        # Update mouse button states
        mouse_buttons = pygame.mouse.get_pressed()
        for i in range(len(mouse_buttons)):
            self.mouse_buttons[i] = mouse_buttons[i]
        
        # Process events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                self.keys_just_pressed[event.key] = True
                
            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
                self.keys_just_released[event.key] = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_just_clicked[event.button] = True
                
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.controller:
                    self.controller_buttons[event.button] = True
                    
            elif event.type == pygame.JOYBUTTONUP:
                if self.controller:
                    self.controller_buttons[event.button] = False
                    
            elif event.type == pygame.JOYAXISMOTION:
                if self.controller:
                    # Apply deadzone
                    value = event.value
                    if abs(value) < self.controller_deadzone:
                        value = 0.0
                    self.controller_axes[event.axis] = value
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if key is pressed
        """
        return self.keys_pressed.get(key, False)
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if a key was just pressed this frame.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if key was just pressed
        """
        return self.keys_just_pressed.get(key, False)
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if an action's bound keys are pressed.
        
        Args:
            action: Action name from key_bindings
            
        Returns:
            True if any bound key is pressed
        """
        if action not in self.key_bindings:
            return False
            
        for key in self.key_bindings[action]:
            if self.is_key_pressed(key):
                return True
                
        # Check controller buttons if mapped
        if self.controller and action in self.controller_mappings:
            button = self.controller_mappings[action]
            if isinstance(button, int) and self.controller_buttons.get(button, False):
                return True
                
        return False
    
    def is_action_just_pressed(self, action: str) -> bool:
        """Check if an action was just triggered.
        
        Args:
            action: Action name from key_bindings
            
        Returns:
            True if action was just triggered
        """
        if action not in self.key_bindings:
            return False
            
        for key in self.key_bindings[action]:
            if self.is_key_just_pressed(key):
                return True
                
        return False
    
    def is_mouse_clicked(self, button: int = 1) -> bool:
        """Check if mouse button was just clicked.
        
        Args:
            button: Mouse button (1=left, 2=middle, 3=right)
            
        Returns:
            True if button was just clicked
        """
        return self.mouse_just_clicked.get(button, False)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return self.mouse_position
    
    def get_controller_axis(self, axis: int) -> float:
        """Get controller axis value.
        
        Args:
            axis: Axis index
            
        Returns:
            Axis value (-1.0 to 1.0)
        """
        return self.controller_axes.get(axis, 0.0)
    
    def bind_key(self, action: str, key: int) -> None:
        """Bind a key to an action.
        
        Args:
            action: Action name
            key: Pygame key constant
        """
        if action not in self.key_bindings:
            self.key_bindings[action] = []
        
        if key not in self.key_bindings[action]:
            self.key_bindings[action].append(key)
    
    def unbind_key(self, action: str, key: int) -> None:
        """Unbind a key from an action.
        
        Args:
            action: Action name
            key: Pygame key constant
        """
        if action in self.key_bindings and key in self.key_bindings[action]:
            self.key_bindings[action].remove(key)