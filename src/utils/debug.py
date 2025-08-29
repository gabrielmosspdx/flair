"""Debug overlay and utilities for development."""

import time
from typing import Dict, List, Optional, Tuple

import pygame


class DebugOverlay:
    """Debug information overlay for development."""

    def __init__(self, font: Optional[pygame.font.Font] = None):
        """Initialize debug overlay.

        Args:
            font: Font to use for debug text
        """
        self.enabled = False
        self.show_collision_boxes = False

        self.font = font  # Will be set later after pygame init
        self.text_color = (0, 255, 0)
        self.box_color = (255, 0, 0)
        self.background_color = (0, 0, 0, 180)

        # Performance tracking
        self.fps_history: List[float] = []
        self.fps_history_size = 60
        self.frame_times: Dict[str, float] = {}
        self.timers: Dict[str, float] = {}

        # Debug info
        self.info_lines: List[str] = []
        self.entity_counts: Dict[str, int] = {}

    def toggle(self) -> None:
        """Toggle debug overlay on/off."""
        self.enabled = not self.enabled

    def start_timer(self, name: str) -> None:
        """Start a performance timer.

        Args:
            name: Timer name
        """
        self.timers[name] = time.perf_counter()

    def end_timer(self, name: str) -> float:
        """End a performance timer and record the time.

        Args:
            name: Timer name

        Returns:
            Elapsed time in milliseconds
        """
        if name in self.timers:
            elapsed = (time.perf_counter() - self.timers[name]) * 1000
            self.frame_times[name] = elapsed
            del self.timers[name]
            return elapsed
        return 0.0

    def update_fps(self, clock: pygame.time.Clock) -> None:
        """Update FPS tracking.

        Args:
            clock: Pygame clock object
        """
        fps = clock.get_fps()
        self.fps_history.append(fps)

        if len(self.fps_history) > self.fps_history_size:
            self.fps_history.pop(0)

    def set_entity_count(self, entity_type: str, count: int) -> None:
        """Set entity count for display.

        Args:
            entity_type: Type of entity
            count: Number of entities
        """
        self.entity_counts[entity_type] = count

    def add_info(self, text: str) -> None:
        """Add a line of debug info.

        Args:
            text: Debug text to display
        """
        self.info_lines.append(text)

    def clear_info(self) -> None:
        """Clear debug info lines."""
        self.info_lines.clear()

    def draw(self, screen: pygame.Surface, game_data: Optional[Dict] = None) -> None:
        """Draw debug overlay.

        Args:
            screen: Surface to draw on
            game_data: Optional game data dictionary
        """
        if not self.enabled:
            return

        # Ensure we have a font
        if not self.font:
            self.font = pygame.font.Font(None, 20)

        lines = []
        y_offset = 10

        # FPS (always show when overlay is enabled)
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            min_fps = min(self.fps_history) if self.fps_history else 0
            max_fps = max(self.fps_history) if self.fps_history else 0
            lines.append(f"FPS: {avg_fps:.1f} (min: {min_fps:.1f}, max: {max_fps:.1f})")

        # Entity counts (always show when overlay is enabled)
        for entity_type, count in self.entity_counts.items():
            lines.append(f"{entity_type}: {count}")

        # Performance timers (always show when overlay is enabled)
        if self.frame_times:
            lines.append("Performance:")
            for name, time_ms in self.frame_times.items():
                lines.append(f"  {name}: {time_ms:.2f}ms")

        # Collision boxes status
        lines.append(
            f"Collision Boxes: {'ON' if self.show_collision_boxes else 'OFF'} (F6 to toggle)"
        )

        # Game data
        if game_data:
            lines.append("Game State:")
            for key, value in game_data.items():
                lines.append(f"  {key}: {value}")

        # Custom info lines
        lines.extend(self.info_lines)

        # Draw background
        if lines:
            max_width = max(self.font.size(line)[0] for line in lines) + 20
            height = len(lines) * 22 + 20

            bg_surface = pygame.Surface((max_width, height), pygame.SRCALPHA)
            bg_surface.fill(self.background_color)
            screen.blit(bg_surface, (5, 5))

        # Draw text
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            screen.blit(text_surface, (10, y_offset + i * 22))

    def draw_collision_box(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """Draw a collision box.

        Args:
            screen: Surface to draw on
            rect: Rectangle to draw
            color: Optional color override
        """
        if self.show_collision_boxes:  # Only check show_collision_boxes, not enabled
            pygame.draw.rect(screen, color or self.box_color, rect, 2)

    def draw_vector(
        self,
        screen: pygame.Surface,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: Tuple[int, int, int] = (255, 255, 0),
    ) -> None:
        """Draw a vector for debugging.

        Args:
            screen: Surface to draw on
            start: Start position
            end: End position
            color: Line color
        """
        if self.enabled:
            pygame.draw.line(screen, color, start, end, 2)
            # Draw arrowhead
            pygame.draw.circle(screen, color, (int(end[0]), int(end[1])), 3)


# Global debug instance
debug_overlay = DebugOverlay()
