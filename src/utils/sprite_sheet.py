"""Sprite sheet utility for loading and managing sprite animations."""

import json
import os
from typing import Dict, List, Optional

import pygame


class SpriteSheet:
    """Handles loading and extracting frames from sprite sheets."""

    def __init__(self, image_path: str, json_path: Optional[str] = None):
        """Initialize sprite sheet.

        Args:
            image_path: Path to the sprite sheet image
            json_path: Optional path to JSON file with frame definitions
        """
        self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        self.frames: Dict[str, List[pygame.Surface]] = {}
        self.frame_data: Dict = {}

        if json_path and os.path.exists(json_path):
            with open(json_path, "r") as f:
                self.frame_data = json.load(f)
            self._load_from_json()

    def _load_from_json(self) -> None:
        """Load frame definitions from JSON data."""
        if "animations" in self.frame_data:
            for anim_name, anim_data in self.frame_data["animations"].items():
                frames = []
                for frame_info in anim_data["frames"]:
                    x = frame_info["x"]
                    y = frame_info["y"]
                    width = frame_info["width"]
                    height = frame_info["height"]
                    frames.append(self.get_frame(x, y, width, height))
                self.frames[anim_name] = frames

    def get_frame(self, x: int, y: int, width: int, height: int) -> pygame.Surface:
        """Extract a single frame from the sprite sheet.

        Args:
            x: X position of frame
            y: Y position of frame
            width: Frame width
            height: Frame height

        Returns:
            Extracted frame surface
        """
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return frame

    def get_frames_uniform(
        self,
        rows: int,
        cols: int,
        frame_width: int,
        frame_height: int,
        start_x: int = 0,
        start_y: int = 0,
    ) -> List[pygame.Surface]:
        """Extract frames from a uniformly spaced sprite sheet.

        Args:
            rows: Number of rows in the sprite sheet
            cols: Number of columns in the sprite sheet
            frame_width: Width of each frame
            frame_height: Height of each frame
            start_x: Starting X offset
            start_y: Starting Y offset

        Returns:
            List of frame surfaces
        """
        frames = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * frame_width
                y = start_y + row * frame_height
                frames.append(self.get_frame(x, y, frame_width, frame_height))
        return frames

    def get_animation_frames(self, animation_name: str) -> List[pygame.Surface]:
        """Get frames for a specific animation.

        Args:
            animation_name: Name of the animation

        Returns:
            List of frames for the animation
        """
        return self.frames.get(animation_name, [])

    def scale_frames(self, frames: List[pygame.Surface], scale: float) -> List[pygame.Surface]:
        """Scale a list of frames.

        Args:
            frames: List of frame surfaces
            scale: Scale factor

        Returns:
            List of scaled frame surfaces
        """
        scaled_frames = []
        for frame in frames:
            width = int(frame.get_width() * scale)
            height = int(frame.get_height() * scale)
            scaled = pygame.transform.scale(frame, (width, height))
            scaled_frames.append(scaled)
        return scaled_frames


class SpriteSheetManager:
    """Manages multiple sprite sheets."""

    def __init__(self):
        """Initialize the sprite sheet manager."""
        self.sprite_sheets: Dict[str, SpriteSheet] = {}

    def load_sprite_sheet(
        self, name: str, image_path: str, json_path: Optional[str] = None
    ) -> None:
        """Load a sprite sheet.

        Args:
            name: Name to reference this sprite sheet
            image_path: Path to the sprite sheet image
            json_path: Optional path to JSON file with frame definitions
        """
        self.sprite_sheets[name] = SpriteSheet(image_path, json_path)

    def get_sprite_sheet(self, name: str) -> Optional[SpriteSheet]:
        """Get a loaded sprite sheet.

        Args:
            name: Name of the sprite sheet

        Returns:
            SpriteSheet instance or None
        """
        return self.sprite_sheets.get(name)

    def get_animation_frames(self, sheet_name: str, animation_name: str) -> List[pygame.Surface]:
        """Get animation frames from a specific sprite sheet.

        Args:
            sheet_name: Name of the sprite sheet
            animation_name: Name of the animation

        Returns:
            List of animation frames
        """
        sheet = self.sprite_sheets.get(sheet_name)
        if sheet:
            return sheet.get_animation_frames(animation_name)
        return []
