"""Asset manager for loading and caching game resources."""

import os
from typing import Dict, Optional

import pygame

from ..utils.constants import FONT_FILE, IMAGES_DIR


class AssetManager:
    """Manages game assets like images and fonts."""
    
    def __init__(self):
        """Initialize the asset manager."""
        self.images: Dict[str, Optional[pygame.Surface]] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._loaded = False
    
    def load_all(self) -> None:
        """Load all game assets."""
        if self._loaded:
            return
        
        self.load_fonts()
        self.load_images()
        self._loaded = True
    
    def load_fonts(self) -> None:
        """Load all game fonts."""
        try:
            if os.path.exists(FONT_FILE):
                self.fonts['title'] = pygame.font.Font(FONT_FILE, 72)
                self.fonts['large'] = pygame.font.Font(FONT_FILE, 48)
                self.fonts['normal'] = pygame.font.Font(FONT_FILE, 36)
                self.fonts['small'] = pygame.font.Font(FONT_FILE, 24)
                print(f"Loaded custom font: {FONT_FILE}")
            else:
                raise FileNotFoundError("Custom font not found")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font: {e}. Using default font.")
            self.fonts['title'] = pygame.font.Font(None, 72)
            self.fonts['large'] = pygame.font.Font(None, 48)
            self.fonts['normal'] = pygame.font.Font(None, 36)
            self.fonts['small'] = pygame.font.Font(None, 24)
    
    def load_images(self) -> None:
        """Load all game images."""
        image_files = {
            'floor': 'sanfranhotel.png',
            'happy_customer': 'happycustomer.png',
            'unhappy_customer': 'unhappycustomer.png',
            'beer_icon': 'beer_icon.png',
            'wine_icon': 'wine_icon.png',
            'cocktail_icon': 'cocktail_icon.png',
            'heart': 'heart.png'
        }
        
        for name, filename in image_files.items():
            self.images[name] = self._load_image(filename)
    
    def _load_image(self, filename: str) -> Optional[pygame.Surface]:
        """Load a single image file.
        
        Args:
            filename: Name of the image file
            
        Returns:
            Loaded Surface or None if failed
        """
        # Try multiple locations
        paths = [
            os.path.join(IMAGES_DIR, filename),
            os.path.join('assets', 'images', filename),
            filename  # Root directory
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    image = pygame.image.load(path).convert_alpha()
                    
                    # Scale customer sprites
                    if 'customer' in filename:
                        image = pygame.transform.scale(image, (40, 40))
                    # Scale icons
                    elif 'icon' in filename or 'heart' in filename:
                        image = pygame.transform.scale(image, (32, 32))
                    
                    print(f"Loaded image: {path}")
                    return image
                except pygame.error as e:
                    print(f"Could not load {path}: {e}")
        
        print(f"Image not found: {filename}")
        return None
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded image by name.
        
        Args:
            name: Image name
            
        Returns:
            Image surface or None
        """
        return self.images.get(name)
    
    def get_font(self, size: str = 'normal') -> pygame.font.Font:
        """Get a font by size name.
        
        Args:
            size: Font size name (title, large, normal, small)
            
        Returns:
            Font object
        """
        return self.fonts.get(size, self.fonts['normal'])
    
    def create_floor_pattern(self, screen_width: int, screen_height: int) -> Optional[pygame.Surface]:
        """Create a tiled floor pattern.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            Tiled floor surface or None
        """
        floor_image = self.images.get('floor')
        if not floor_image:
            return None
        
        tile_width, tile_height = floor_image.get_size()
        tiles_x = (screen_width // tile_width) + 2
        tiles_y = (screen_height // tile_height) + 2
        
        floor_surface = pygame.Surface((tiles_x * tile_width, tiles_y * tile_height))
        
        for x in range(tiles_x):
            for y in range(tiles_y):
                floor_surface.blit(floor_image, (x * tile_width, y * tile_height))
        
        return floor_surface