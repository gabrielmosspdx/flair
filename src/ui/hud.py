"""Heads-up display (HUD) for the game."""

from typing import Dict, Optional
import pygame

from ..utils.constants import COLORS, DrinkType


class HUD:
    """Manages the in-game heads-up display."""
    
    def __init__(self, assets_manager):
        """Initialize the HUD.
        
        Args:
            assets_manager: Asset manager for fonts and images
        """
        self.assets = assets_manager
        self.font_normal = self.assets.get_font('normal')
        self.font_small = self.assets.get_font('small')
        self.font_large = self.assets.get_font('large')
        
        # Animation states
        self.score_change_timer = 0
        self.score_change_amount = 0
        self.lives_flash_timer = 0
        self.wave_transition_timer = 0
        self.wave_transition_text = ""
        
    def flash_lives(self):
        """Trigger lives display flash effect."""
        self.lives_flash_timer = 30
    
    def show_score_change(self, amount: int):
        """Show score change animation.
        
        Args:
            amount: Points gained or lost
        """
        self.score_change_amount = amount
        self.score_change_timer = 60
    
    def show_wave_transition(self, wave_number: int):
        """Show wave transition animation.
        
        Args:
            wave_number: New wave number
        """
        self.wave_transition_text = f"Wave {wave_number}"
        self.wave_transition_timer = 120
    
    def update(self):
        """Update HUD animations."""
        if self.score_change_timer > 0:
            self.score_change_timer -= 1
        
        if self.lives_flash_timer > 0:
            self.lives_flash_timer -= 1
        
        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= 1
    
    def draw_stats(
        self,
        screen: pygame.Surface,
        score: int,
        wave: int,
        lives: int,
        x: int = 10,
        y: int = 10
    ):
        """Draw game statistics.
        
        Args:
            screen: Surface to draw on
            score: Current score
            wave: Current wave
            lives: Remaining lives
            x: X position for stats
            y: Y position for stats
        """
        # Score with animation
        score_color = COLORS['text_white']
        if self.score_change_timer > 0:
            # Pulse effect
            pulse = abs(self.score_change_timer % 20 - 10) / 10
            score_color = self._blend_colors(COLORS['text_white'], COLORS['text_gold'], pulse)
        
        score_text = self.font_normal.render(f"Score: {score}", True, score_color)
        screen.blit(score_text, (x, y))
        
        # Score change popup
        if self.score_change_timer > 0:
            change_alpha = min(255, self.score_change_timer * 8)
            change_color = COLORS['text_green'] if self.score_change_amount > 0 else COLORS['text_red']
            change_text = self.font_small.render(
                f"+{self.score_change_amount}" if self.score_change_amount > 0 else str(self.score_change_amount),
                True, change_color
            )
            change_text.set_alpha(change_alpha)
            screen.blit(change_text, (x + 150, y + 5))
        
        # Wave
        wave_text = self.font_normal.render(f"Wave: {wave}", True, COLORS['text_white'])
        screen.blit(wave_text, (x, y + 40))
        
        # Lives with flash effect
        lives_color = COLORS['text_white']
        if self.lives_flash_timer > 0 and self.lives_flash_timer % 10 < 5:
            lives_color = COLORS['text_red']
        
        lives_text = self.font_normal.render(f"Lives: {lives}", True, lives_color)
        screen.blit(lives_text, (x, y + 80))
        
        # Hearts visual
        heart_icon = self.assets.get_image('heart')
        if heart_icon:
            for i in range(lives):
                heart_x = x + 140 + i * 35  # Increased offset from 100 to 140 to avoid text overlap
                heart_y = y + 80  # Aligned with the Lives text baseline (same as lives_text y position)
                if self.lives_flash_timer > 0:
                    # Shake effect
                    import random
                    heart_x += random.randint(-2, 2)
                    heart_y += random.randint(-2, 2)
                screen.blit(heart_icon, (heart_x, heart_y))
    
    def draw_inventory(
        self,
        screen: pygame.Surface,
        inventory: Dict[DrinkType, int],
        selected_drink: DrinkType,
        x: Optional[int] = None,
        y: int = 10
    ):
        """Draw inventory display.
        
        Args:
            screen: Surface to draw on
            inventory: Current inventory counts
            selected_drink: Currently selected drink
            x: X position (None for right-aligned)
            y: Y position
        """
        if x is None:
            x = screen.get_width() - 200
        
        for i, drink_type in enumerate(DrinkType):
            item_x = x + i * 60
            
            # Highlight selected
            if drink_type == selected_drink:
                pygame.draw.circle(screen, COLORS['text_gold'], (item_x, y + 20), 25, 3)
                # Glow effect
                glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*COLORS['text_gold'], 30), (25, 25), 25)
                screen.blit(glow_surf, (item_x - 25, y - 5))
            
            # Draw icon
            icon_name = f'{drink_type.name.lower()}_icon'
            icon = self.assets.get_image(icon_name)
            if icon:
                # Scale pulse for selected
                if drink_type == selected_drink:
                    scale = 1.1
                    scaled_icon = pygame.transform.scale(
                        icon,
                        (int(icon.get_width() * scale), int(icon.get_height() * scale))
                    )
                    screen.blit(scaled_icon, (item_x - 18, y - 2))
                else:
                    screen.blit(icon, (item_x - 16, y))
            
            # Count
            count = inventory[drink_type]
            count_color = COLORS['text_white'] if count > 0 else COLORS['text_red']
            count_text = self.font_small.render(str(count), True, count_color)
            screen.blit(count_text, (item_x - 5, y + 35))
            
            # Hotkey hint
            key_text = self.font_small.render(str(i + 1), True, COLORS['text_gray'])
            screen.blit(key_text, (item_x - 5, y + 55))
    
    def draw_wave_transition(self, screen: pygame.Surface):
        """Draw wave transition animation.
        
        Args:
            screen: Surface to draw on
        """
        if self.wave_transition_timer <= 0:
            return
        
        # Calculate animation phase
        alpha = min(255, self.wave_transition_timer * 4)
        scale = 1.0 + (120 - self.wave_transition_timer) * 0.01
        
        # Create text surface
        text = self.font_large.render(self.wave_transition_text, True, COLORS['text_gold'])
        
        # Scale text
        scaled_width = int(text.get_width() * scale)
        scaled_height = int(text.get_height() * scale)
        scaled_text = pygame.transform.scale(text, (scaled_width, scaled_height))
        scaled_text.set_alpha(alpha)
        
        # Center on screen
        text_rect = scaled_text.get_rect(center=(screen.get_width()//2, screen.get_height()//3))
        screen.blit(scaled_text, text_rect)
        
        # Subtitle
        if self.wave_transition_timer > 60:
            subtitle_alpha = min(255, (self.wave_transition_timer - 60) * 8)
            subtitle = self.font_normal.render("Get Ready!", True, COLORS['text_white'])
            subtitle.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle.get_rect(center=(screen.get_width()//2, screen.get_height()//3 + 60))
            screen.blit(subtitle, subtitle_rect)
    
    def draw_restock_overlay(self, screen: pygame.Surface, timer: int, max_timer: int):
        """Draw restock overlay.
        
        Args:
            screen: Surface to draw on
            timer: Current restock timer
            max_timer: Maximum restock timer
        """
        # Dark overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Progress bar
        bar_width = 300
        bar_height = 30
        bar_x = screen.get_width() // 2 - bar_width // 2
        bar_y = screen.get_height() // 2 - bar_height // 2
        
        # Background
        pygame.draw.rect(screen, COLORS['bar'], (bar_x, bar_y, bar_width, bar_height))
        
        # Progress
        progress = 1.0 - (timer / max_timer)
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, COLORS['text_gold'], (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, COLORS['text_white'], (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Text
        text = self.font_normal.render("RESTOCKING...", True, COLORS['text_gold'])
        text_rect = text.get_rect(center=(screen.get_width()//2, bar_y - 30))
        screen.blit(text, text_rect)
        
        # Percentage
        percent = int(progress * 100)
        percent_text = self.font_small.render(f"{percent}%", True, COLORS['text_white'])
        percent_rect = percent_text.get_rect(center=(screen.get_width()//2, bar_y + bar_height + 20))
        screen.blit(percent_text, percent_rect)
    
    def draw_pause_overlay(self, screen: pygame.Surface):
        """Draw pause overlay.
        
        Args:
            screen: Surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, COLORS['text_gold'])
        pause_rect = pause_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(pause_text, pause_rect)
        
        # Instructions
        instructions = [
            "Press P to Resume",
            "Press ESC for Main Menu"
        ]
        
        y_offset = 60
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, COLORS['text_white'])
            inst_rect = inst_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 30
    
    def _blend_colors(self, color1: tuple, color2: tuple, factor: float) -> tuple:
        """Blend two colors.
        
        Args:
            color1: First color
            color2: Second color
            factor: Blend factor (0 = color1, 1 = color2)
            
        Returns:
            Blended color
        """
        return tuple(
            int(c1 * (1 - factor) + c2 * factor)
            for c1, c2 in zip(color1, color2)
        )