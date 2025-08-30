"""Base class for animated sprites."""

from typing import Dict, List, Optional

import pygame


class AnimatedSprite(pygame.sprite.Sprite):
    """Base class for sprites with animations."""

    def __init__(self):
        """Initialize the animated sprite."""
        super().__init__()

        # Animation data
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.current_animation: str = "idle"
        self.current_frame: int = 0
        self.animation_speed: float = 0.15  # Frames per game frame
        self.frame_counter: float = 0.0

        # Sprite properties
        self.image: Optional[pygame.Surface] = None
        self.original_image: Optional[pygame.Surface] = None
        self.rect: Optional[pygame.Rect] = None
        self.flip_x: bool = False
        self.flip_y: bool = False
        self.angle: float = 0  # Rotation angle

        # State tracking
        self.animation_finished: bool = False
        self.loop_animation: bool = True

    def add_animation(self, name: str, frames: List[pygame.Surface], loop: bool = True) -> None:
        """Add an animation to this sprite.

        Args:
            name: Name of the animation
            frames: List of frame surfaces
            loop: Whether the animation should loop
        """
        self.animations[name] = frames

        # Set initial image if this is the first animation
        if self.image is None and frames:
            self.image = frames[0]
            self.rect = self.image.get_rect()

    def set_animation(self, name: str, reset: bool = True, loop: bool = True) -> None:
        """Change the current animation.

        Args:
            name: Name of the animation to play
            reset: Whether to reset to the first frame
            loop: Whether the animation should loop
        """
        if name not in self.animations:
            return

        if name != self.current_animation or reset:
            self.current_animation = name
            self.loop_animation = loop
            self.animation_finished = False

            if reset:
                self.current_frame = 0
                self.frame_counter = 0.0
                self._update_image()

    def update_animation(self, dt: float = 1.0) -> None:
        """Update the animation frame.

        Args:
            dt: Delta time multiplier
        """
        if self.current_animation not in self.animations:
            return

        frames = self.animations[self.current_animation]
        if not frames:
            return

        # Update frame counter
        self.frame_counter += self.animation_speed * dt

        # Check if we need to advance to the next frame
        if self.frame_counter >= 1.0:
            self.frame_counter = 0.0

            if not self.animation_finished:
                self.current_frame += 1

                # Handle animation end
                if self.current_frame >= len(frames):
                    if self.loop_animation:
                        self.current_frame = 0
                    else:
                        self.current_frame = len(frames) - 1
                        self.animation_finished = True

        # Always update image to ensure flipping is applied
        self._update_image()

    def _update_image(self) -> None:
        """Update the sprite's image based on current animation frame."""
        if self.current_animation not in self.animations:
            return

        frames = self.animations[self.current_animation]
        if not frames or self.current_frame >= len(frames):
            return

        # Get the current frame
        frame = frames[self.current_frame]
        self.original_image = frame

        # Apply rotation if angle is set
        if hasattr(self, "angle"):
            # The sprite defaults to pointing down (south)
            # In screen coordinates, down is 90° from the positive x-axis
            # We need to rotate from down to the target angle
            # pygame.transform.rotate rotates counterclockwise
            # (but appears clockwise due to inverted Y)
            rotation_needed = self.angle - 90
            frame = pygame.transform.rotate(frame, -rotation_needed)

        # Apply flipping if needed (after rotation)
        if self.flip_x or self.flip_y:
            frame = pygame.transform.flip(frame, self.flip_x, self.flip_y)

        # Update image and preserve rect center
        if self.rect:
            old_center = self.rect.center
            self.image = frame
            self.rect = self.image.get_rect(center=old_center)
        else:
            self.image = frame
            self.rect = self.image.get_rect()

    def set_flip(self, flip_x: bool = False, flip_y: bool = False) -> None:
        """Set sprite flipping.

        Args:
            flip_x: Whether to flip horizontally
            flip_y: Whether to flip vertically
        """
        if flip_x != self.flip_x or flip_y != self.flip_y:
            self.flip_x = flip_x
            self.flip_y = flip_y
            self._update_image()

    def get_current_frame_index(self) -> int:
        """Get the current frame index.

        Returns:
            Current frame index
        """
        return self.current_frame

    def get_animation_progress(self) -> float:
        """Get the progress of the current animation.

        Returns:
            Progress from 0.0 to 1.0
        """
        if self.current_animation not in self.animations:
            return 0.0

        frames = self.animations[self.current_animation]
        if not frames:
            return 0.0

        total_frames = len(frames)
        current_progress = self.current_frame + self.frame_counter

        return min(1.0, current_progress / total_frames)

    def is_animation_finished(self) -> bool:
        """Check if the current animation has finished.

        Returns:
            True if animation is finished
        """
        return self.animation_finished

    def set_animation_speed(self, speed: float) -> None:
        """Set the animation playback speed.

        Args:
            speed: Animation speed (frames per game frame)
        """
        self.animation_speed = max(0.01, speed)
