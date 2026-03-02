"""Game constants and configuration."""

from enum import Enum

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (RGB tuples)
COLORS = {
    # Core game colors
    "bg": (44, 24, 16),
    "bar": (100, 50, 12),
    "bar_top": (130, 68, 25),
    "bar_highlight": (170, 100, 40),
    "customer": (65, 105, 225),
    "customer_served": (136, 136, 136),
    "crosshair": (255, 215, 0),
    # Text
    "text_white": (255, 248, 235),
    "text_gold": (255, 210, 60),
    "text_amber": (255, 175, 30),
    "text_green": (80, 230, 120),
    "text_red": (230, 60, 60),
    "text_gray": (110, 95, 80),
    "text_dim": (80, 65, 50),
    # UI panels and borders
    "ui_bg": (139, 69, 19, 80),
    "ui_border": (139, 69, 19),
    "panel_dark": (12, 6, 2),
    "panel_border": (180, 130, 40),
    # Menu
    "menu_bg": (22, 12, 6),
    "menu_deep": (12, 6, 2),
    # Buttons
    "button_bg": (100, 50, 12),
    "button_hover": (140, 78, 25),
    "button_pressed": (75, 38, 8),
    "button_border": (200, 155, 50),
    # Drink colors
    "beer": (218, 165, 32),
    "wine": (140, 55, 65),
    "cocktail": (240, 95, 65),
    # Effects
    "particle_splat": (220, 50, 50),
    "glow_gold": (255, 200, 80),
    "mote": (255, 215, 0),
    # Tabs
    "tab_active": (120, 65, 18),
    "tab_inactive": (55, 30, 10),
}


# Game states
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SETTINGS = 3
    LEADERBOARD = 4
    CONTROLLER_SETUP = 5


# Drink types
class DrinkType(Enum):
    BEER = 0
    WINE = 1
    COCKTAIL = 2


# Game mechanics
INITIAL_LIVES = 3
INITIAL_INVENTORY = 5
BASE_SPAWN_DELAY = 120
BASE_CUSTOMER_SPEED = 0.5
INITIAL_WAVE_SIZE = 8
MAX_WAVE_SIZE = 20
RESTOCK_DURATION = 180
RESTOCK_AMOUNT = 5

# Points
BASE_POINTS = 10
POINTS_PER_WAVE = 2

# Physics
PROJECTILE_SPEED = 6
PROJECTILE_MAX_LIFE = 150
PARTICLE_LIFE = 30

# UI
BAR_SIZE = 60
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
SLIDER_WIDTH = 250
SLIDER_HEIGHT = 20

# Controller defaults
DEFAULT_CONTROLLER_DEADZONE = 0.3
DEFAULT_CONTROLLER_MAPPINGS = {
    "select_beer": 0,  # A button
    "select_wine": 1,  # B button
    "select_cocktail": 2,  # X button
    "restock": 3,  # Y button
    "pause": 7,  # Start button
    "throw_axis_x": 0,  # Left stick X
    "throw_axis_y": 1,  # Left stick Y
    "throw_button": 5,  # Right bumper
}

# Audio
DEFAULT_SOUND_VOLUME = 0.7
DEFAULT_MUSIC_VOLUME = 0.3

# Dialogue
POSITIVE_DIALOGUE = [
    "That's sick!",
    "Yum yum in my tum tum!",
    "Righteous!",
    "Perfect!",
    "Organic vibes!",
    "Locally sourced!",
    "Artisanal!",
    "Small batch!",
    "Craft AF!",
    "This would be good out of a shoe!",
    "Show me the way!",
]

NEGATIVE_DIALOGUE = [
    "Not what I ordered!",
    "This isn't right!",
    "O...kay.",
    "Kay.",
    "Mkay.",
    "Don't quit your day job!",
    "Uh yeah. Hmm. Great.",
    "Rubbish!",
    "Bye Felicia!",
]

# File paths
SETTINGS_FILE = "data/settings.json"
HIGHSCORES_FILE = "data/highscores.json"
FONT_FILE = "assets/fonts/Grandstander-Medium.ttf"

# Asset paths
ASSETS_DIR = "assets"
IMAGES_DIR = f"{ASSETS_DIR}/images"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
MUSIC_DIR = f"{ASSETS_DIR}/music"
