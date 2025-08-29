import pygame
import math
import random
import os
import json
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.joystick.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
COLORS = {
    'bg': (44, 24, 16),
    'bar': (139, 69, 19),
    'bar_top': (160, 82, 45),
    'customer': (65, 105, 225),
    'customer_served': (136, 136, 136),
    'crosshair': (255, 215, 0),
    'text_white': (255, 255, 255),
    'text_gold': (255, 215, 0),
    'text_green': (0, 255, 0),
    'text_red': (255, 0, 0),
    'text_gray': (128, 128, 128),
    'ui_bg': (139, 69, 19, 80),
    'ui_border': (139, 69, 19),
    'menu_bg': (32, 20, 12),
    'button_bg': (139, 69, 19),
    'button_hover': (160, 82, 45),
    'button_pressed': (110, 55, 15),
    'beer': (218, 165, 32),
    'wine': (114, 47, 55),
    'cocktail': (255, 99, 71),
    'particle_splat': (255, 0, 0)
}

class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SETTINGS = 3
    LEADERBOARD = 4
    CONTROLLER_SETUP = 5

class DrinkType(Enum):
    BEER = 0
    WINE = 1
    COCKTAIL = 2

@dataclass
class HighScore:
    name: str
    score: int
    wave: int
    date: str

class Settings:
    def __init__(self):
        self.sound_volume = 0.7
        self.music_volume = 0.3
        self.controller_enabled = False
        self.controller_deadzone = 0.3
        
        # Controller mappings (Xbox controller defaults)
        self.controller_mappings = {
            'select_beer': 0,      # A button
            'select_wine': 1,      # B button  
            'select_cocktail': 2,  # X button
            'restock': 3,          # Y button
            'pause': 7,            # Start button
            'throw_axis_x': 0,     # Left stick X
            'throw_axis_y': 1,     # Left stick Y
            'throw_button': 5      # Right bumper
        }
        
        self.load_settings()
    
    def save_settings(self):
        settings_data = {
            'sound_volume': self.sound_volume,
            'music_volume': self.music_volume,
            'controller_enabled': self.controller_enabled,
            'controller_deadzone': self.controller_deadzone,
            'controller_mappings': self.controller_mappings
        }
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings_data, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings_data = json.load(f)
                self.sound_volume = settings_data.get('sound_volume', 0.7)
                self.music_volume = settings_data.get('music_volume', 0.3)
                self.controller_enabled = settings_data.get('controller_enabled', False)
                self.controller_deadzone = settings_data.get('controller_deadzone', 0.3)
                self.controller_mappings.update(settings_data.get('controller_mappings', {}))
        except:
            pass  # Use defaults if file doesn't exist

class HighScoreManager:
    def __init__(self):
        self.high_scores = []
        self.load_scores()
    
    def add_score(self, name, score, wave):
        new_score = HighScore(
            name=name,
            score=score,
            wave=wave,
            date=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x.score, reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        self.save_scores()
    
    def save_scores(self):
        scores_data = []
        for score in self.high_scores:
            scores_data.append({
                'name': score.name,
                'score': score.score,
                'wave': score.wave,
                'date': score.date
            })
        
        try:
            with open('highscores.json', 'w') as f:
                json.dump(scores_data, f, indent=2)
        except Exception as e:
            print(f"Could not save high scores: {e}")
    
    def load_scores(self):
        try:
            with open('highscores.json', 'r') as f:
                scores_data = json.load(f)
                self.high_scores = []
                for data in scores_data:
                    self.high_scores.append(HighScore(
                        name=data['name'],
                        score=data['score'],
                        wave=data['wave'],
                        date=data['date']
                    ))
        except:
            pass  # Use empty list if file doesn't exist

class Button:
    def __init__(self, x, y, width, height, text, font, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.hovered = False
        self.pressed = False
    
    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if self.hovered and mouse_pressed and self.callback:
            self.callback()
            self.pressed = True
        else:
            self.pressed = False
    
    def draw(self, screen):
        color = COLORS['button_pressed'] if self.pressed else \
                COLORS['button_hover'] if self.hovered else \
                COLORS['button_bg']
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['text_gold'], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, COLORS['text_white'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        
        # Calculate handle position
        self.handle_pos = x + int((initial_val - min_val) / (max_val - min_val) * width)
    
    def update(self, mouse_pos, mouse_pressed, mouse_clicked):
        handle_rect = pygame.Rect(self.handle_pos - 10, self.rect.y - 5, 20, 30)
        
        if mouse_clicked and handle_rect.collidepoint(mouse_pos):
            self.dragging = True
        
        if not mouse_pressed:
            self.dragging = False
        
        if self.dragging:
            # Update handle position
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            
            # Update value
            self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
        
        # Also allow clicking on the track to jump to position
        elif mouse_clicked and self.rect.collidepoint(mouse_pos):
            rel_x = max(0, min(self.rect.width, mouse_pos[0] - self.rect.x))
            self.handle_pos = self.rect.x + rel_x
            self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
    
    def draw(self, screen, font):
        # Draw track
        pygame.draw.rect(screen, COLORS['text_gray'], self.rect)
        pygame.draw.rect(screen, COLORS['text_white'], self.rect, 2)
        
        # Draw handle
        handle_rect = pygame.Rect(self.handle_pos - 10, self.rect.y - 5, 20, 30)
        pygame.draw.rect(screen, COLORS['button_bg'], handle_rect)
        pygame.draw.rect(screen, COLORS['text_gold'], handle_rect, 2)
        
        # Draw label and value
        label_text = f"{self.label}: {self.val:.2f}"
        text_surface = font.render(label_text, True, COLORS['text_white'])
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))

class Customer:
    def __init__(self, spawn_x, spawn_y, target_x, target_y, drink_type, base_speed=0.5):
        self.x = spawn_x
        self.y = spawn_y
        self.target_x = target_x
        self.target_y = target_y
        self.drink_type = drink_type
        self.speed = base_speed
        self.size = 20
        self.served = False
        self.service_successful = False
        self.dialogue = ""
        self.dialogue_timer = 0
        
        # Calculate movement vector
        dx = target_x - spawn_x
        dy = target_y - spawn_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = self.vy = 0
    
    def update(self):
        if not self.served:
            self.x += self.vx
            self.y += self.vy
        
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
    
    def distance_to_target(self):
        dx = self.x - self.target_x
        dy = self.y - self.target_y
        return math.sqrt(dx * dx + dy * dy)
    
    def set_served(self, dialogue, successful=True):
        self.served = True
        self.service_successful = successful
        self.dialogue = dialogue
        self.dialogue_timer = 120  # 2 seconds at 60 FPS

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, drink_type, speed=6):
        self.x = start_x
        self.y = start_y
        self.drink_type = drink_type
        self.speed = speed
        self.size = 8
        self.life = 150  # Max travel time
        
        # Calculate trajectory
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = self.vy = 0
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = 30
        self.max_life = 30
        self.color = color
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1
        return self.life > 0

class FlairGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flair!")
        self.clock = pygame.time.Clock()
        
        # Load custom font with fallback
        self.load_fonts()
        
        # Load visual assets
        self.images = {}
        self.load_images()
        
        # Game systems
        self.settings = Settings()
        self.high_score_manager = HighScoreManager()
        self.state = GameState.MAIN_MENU
        self.running = True
        
        # Audio system
        self.sounds = {}
        self.background_music = None
        self.load_audio_assets()
        
        # Controller
        self.controller = None
        self.controller_throw_target = None
        self.init_controller()
        
        # Game state
        self.reset_game_state()
        
        # Menu system
        self.setup_menus()
        
        # Input text for high score
        self.input_text = ""
        self.input_active = False
        
        self.positive_dialogue = [
            "That's sick!",
            "So voodoo!",
            "Righteous!",
            "Perfect!",
            "Organic vibes!",
            "Locally sourced!",
            "Artisanal!",
            "Small batch!",
            "Craft AF!",
            "This would be good out of a shoe!",
            "Show me the way!"
        ]
        
        self.negative_dialogue = [
            "Not what I ordered!",
            "This isn't right!",
            "O...kay.",
            "Kay.",
            "Mkay.",
            "Don't quit your day job!",
            "Uh yeah. Hmm. Great.",
            "Rubbish!",
            "Bye Felicia!"
        ]
    
    def load_fonts(self):
        """
        Load custom font with fallback to system font.
        Place 'Grandstander-Medium.ttf' in the same directory as the game.
        """
        font_path = "Grandstander-Medium.ttf"
        
        try:
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 36)
                self.small_font = pygame.font.Font(font_path, 24)
                self.large_font = pygame.font.Font(font_path, 48)
                self.title_font = pygame.font.Font(font_path, 72)
                print(f"Loaded custom font: {font_path}")
            else:
                raise FileNotFoundError("Custom font not found, using default")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font: {e}")
            # Fallback to system font
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 48)
            self.title_font = pygame.font.Font(None, 72)
    
    def load_images(self):
        """
        Load all game images with error handling.
        
        Expected files:
        - sanfranhotel.png (floor texture)
        - happycustomer.png (satisfied customer sprite)
        - unhappycustomer.png (dissatisfied customer sprite)
        """
        os.makedirs("assets/images", exist_ok=True)
        
        image_files = {
            'floor': 'assets/images/sanfranhotel.png',
            'happy_customer': 'assets/images/happycustomer.png',
            'unhappy_customer': 'assets/images/unhappycustomer.png'
        }
        
        # Also check root directory for convenience
        root_image_files = {
            'floor': 'sanfranhotel.png',
            'happy_customer': 'happycustomer.png',
            'unhappy_customer': 'unhappycustomer.png'
        }
        
        for image_name, filepath in image_files.items():
            self.images[image_name] = None
            
            # Try assets folder first, then root directory
            paths_to_try = [filepath, root_image_files[image_name]]
            
            for path in paths_to_try:
                if os.path.exists(path):
                    try:
                        image = pygame.image.load(path).convert_alpha()
                        
                        # Scale customer images to appropriate size (40x40 pixels)
                        if 'customer' in image_name:
                            image = pygame.transform.scale(image, (40, 40))
                        
                        self.images[image_name] = image
                        print(f"Loaded image: {path}")
                        break
                    except pygame.error as e:
                        print(f"Could not load {path}: {e}")
        
        # Create floor tile pattern if floor image exists
        if self.images['floor']:
            self.create_floor_pattern()
    
    def create_floor_pattern(self):
        """Create a repeating 2x2 pattern of the floor texture"""
        floor_image = self.images['floor']
        tile_width, tile_height = floor_image.get_size()
        
        # Calculate how many tiles we need to fill the screen
        tiles_x = (SCREEN_WIDTH // tile_width) + 2
        tiles_y = (SCREEN_HEIGHT // tile_height) + 2
        
        # Create a surface large enough to tile the entire screen
        self.floor_surface = pygame.Surface((tiles_x * tile_width, tiles_y * tile_height))
        
        # Tile the floor image across the surface
        for x in range(tiles_x):
            for y in range(tiles_y):
                self.floor_surface.blit(floor_image, (x * tile_width, y * tile_height))
    
    def reset_game_state(self):
        """Reset all game variables for a new game"""
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.score = 0
        self.wave = 1
        self.lives = 3
        self.customers_served = 0
        self.selected_drink = DrinkType.BEER
        
        self.inventory = {
            DrinkType.BEER: 20,
            DrinkType.WINE: 20,
            DrinkType.COCKTAIL: 20
        }
        
        self.customers = []
        self.projectiles = []
        self.particles = []
        
        self.wave_timer = 0
        self.spawn_timer = 0
        self.base_spawn_delay = 120
        self.base_customer_speed = 0.5
        self.customers_in_wave = 0
        self.wave_size = 8
        
        self.is_restocking = False
        self.restock_timer = 0
        self.restock_duration = 180
        
        self.paused = False
    
    def init_controller(self):
        """Initialize controller if available"""
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print(f"Controller connected: {self.controller.get_name()}")
        else:
            self.controller = None
    
    def setup_menus(self):
        """Setup all menu buttons and UI elements with improved spacing"""
        # Main Menu Buttons
        button_width = 220
        button_height = 55
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 350
        spacing = 90
        
        self.main_menu_buttons = [
            Button(center_x, start_y, button_width, button_height, "New Game", self.font, self.start_new_game),
            Button(center_x, start_y + spacing, button_width, button_height, "High Scores", self.font, self.show_leaderboard),
            Button(center_x, start_y + spacing * 2, button_width, button_height, "Settings", self.font, self.show_settings),
            Button(center_x, start_y + spacing * 3, button_width, button_height, "Quit", self.font, self.quit_game)
        ]
        
        # Settings Menu Elements
        self.settings_buttons = [
            Button(80, SCREEN_HEIGHT - 120, 120, 50, "Back", self.font, self.show_main_menu),
            Button(250, SCREEN_HEIGHT - 120, 180, 50, "Controller Setup", self.small_font, self.show_controller_setup)
        ]
        
        # Better positioned sliders
        slider_x = 400
        self.sound_slider = Slider(slider_x, 250, 300, 0.0, 1.0, self.settings.sound_volume, "Sound Volume")
        self.music_slider = Slider(slider_x, 350, 300, 0.0, 1.0, self.settings.music_volume, "Music Volume")
        
        # Leaderboard Buttons
        self.leaderboard_buttons = [
            Button(80, SCREEN_HEIGHT - 120, 120, 50, "Back", self.font, self.show_main_menu)
        ]
        
        # Controller Setup Buttons
        self.controller_buttons = [
            Button(80, SCREEN_HEIGHT - 120, 120, 50, "Back", self.font, self.show_settings),
            Button(250, SCREEN_HEIGHT - 120, 180, 50, "Detect Controller", self.small_font, self.init_controller)
        ]
        
        # Game Over Buttons
        self.game_over_buttons = [
            Button(center_x, start_y + spacing, button_width, button_height, "Main Menu", self.font, self.show_main_menu),
            Button(center_x, start_y + spacing * 2, button_width, button_height, "Play Again", self.font, self.start_new_game)
        ]
    
    def load_audio_assets(self):
        """Load all audio assets with proper volume application"""
        os.makedirs("assets/sounds", exist_ok=True)
        os.makedirs("assets/music", exist_ok=True)
        
        sound_files = {
            'order_success': 'assets/sounds/order_success',
            'order_fail': 'assets/sounds/order_fail', 
            'throw_drink': 'assets/sounds/throw_drink',
            'restock': 'assets/sounds/restock',
            'customer_reach_bar': 'assets/sounds/customer_reach_bar'
        }
        
        extensions = ['.wav', '.ogg', '.mp3']
        
        for sound_name, filepath in sound_files.items():
            self.sounds[sound_name] = None
            for ext in extensions:
                full_path = filepath + ext
                if os.path.exists(full_path):
                    try:
                        sound = pygame.mixer.Sound(full_path)
                        sound.set_volume(self.settings.sound_volume)
                        self.sounds[sound_name] = sound
                        print(f"Loaded sound: {full_path}")
                        break
                    except pygame.error as e:
                        print(f"Could not load {full_path}: {e}")
        
        # Load background music
        music_files = ['assets/music/background.ogg', 'assets/music/background.mp3', 'assets/music/background.wav']
        for music_file in music_files:
            if os.path.exists(music_file):
                try:
                    pygame.mixer.music.load(music_file)
                    self.background_music = music_file
                    print(f"Loaded background music: {music_file}")
                    break
                except pygame.error as e:
                    print(f"Could not load {music_file}: {e}")
    
    def update_audio_volumes(self):
        """Update all audio volumes based on settings"""
        # Update sound effects volume
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.settings.sound_volume)
        
        # Update music volume
        pygame.mixer.music.set_volume(self.settings.music_volume)
    
    def play_background_music(self):
        """Start background music if available"""
        if self.background_music and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)  # Loop indefinitely
    
    def stop_background_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
    
    # Audio hooks
    def hook_order_success(self, customer, drink_type, points_earned):
        if self.sounds['order_success']:
            self.sounds['order_success'].play()
    
    def hook_order_fail(self, customer, wrong_drink_type, correct_drink_type):
        if self.sounds['order_fail']:
            self.sounds['order_fail'].play()
    
    def hook_throw_drink(self, drink_type, target_x, target_y):
        if self.sounds['throw_drink']:
            self.sounds['throw_drink'].play()
    
    def hook_restock_complete(self):
        if self.sounds['restock']:
            self.sounds['restock'].play()
    
    def hook_customer_reach_bar(self, customer):
        if self.sounds['customer_reach_bar']:
            self.sounds['customer_reach_bar'].play()
    
    # Menu Navigation
    def start_new_game(self):
        self.reset_game_state()
        self.state = GameState.PLAYING
        self.play_background_music()
    
    def show_main_menu(self):
        self.state = GameState.MAIN_MENU
        self.input_active = False
        self.play_background_music()
    
    def show_settings(self):
        self.state = GameState.SETTINGS
    
    def show_leaderboard(self):
        self.state = GameState.LEADERBOARD
    
    def show_controller_setup(self):
        self.state = GameState.CONTROLLER_SETUP
    
    def quit_game(self):
        self.settings.save_settings()
        self.running = False
    
    def game_over(self):
        # Check if this is a high score
        is_high_score = (len(self.high_score_manager.high_scores) < 10 or 
                        self.score > self.high_score_manager.high_scores[-1].score)
        
        if is_high_score:
            self.input_active = True
            self.input_text = ""
        
        self.state = GameState.GAME_OVER
    
    def add_high_score(self):
        if self.input_text.strip():
            self.high_score_manager.add_score(self.input_text.strip(), self.score, self.wave)
            self.input_active = False
    
    # Game utility methods
    def get_drink_color(self, drink_type):
        color_map = {
            DrinkType.BEER: COLORS['beer'],
            DrinkType.WINE: COLORS['wine'],
            DrinkType.COCKTAIL: COLORS['cocktail']
        }
        return color_map.get(drink_type, COLORS['beer'])
    
    def get_drink_name(self, drink_type):
        name_map = {
            DrinkType.BEER: "Beer",
            DrinkType.WINE: "Wine", 
            DrinkType.COCKTAIL: "Cocktail"
        }
        return name_map.get(drink_type, "Unknown")
    
    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_clicked = False
        controller_input = self.get_controller_input()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    self.handle_game_input(event)
                elif self.state == GameState.GAME_OVER and self.input_active:
                    self.handle_text_input(event)
                elif self.state == GameState.SETTINGS:
                    if event.key == pygame.K_c:
                        self.settings.controller_enabled = not self.settings.controller_enabled
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.state == GameState.PLAYING and self.settings.controller_enabled:
                    self.handle_controller_input(event.button)
        
        # Update UI elements based on current state
        if self.state == GameState.MAIN_MENU:
            for button in self.main_menu_buttons:
                button.update(mouse_pos, mouse_clicked)
        
        elif self.state == GameState.SETTINGS:
            for button in self.settings_buttons:
                button.update(mouse_pos, mouse_clicked)
            
            self.sound_slider.update(mouse_pos, mouse_pressed, mouse_clicked)
            self.music_slider.update(mouse_pos, mouse_pressed, mouse_clicked)
            
            # Apply volume changes in real-time
            if abs(self.sound_slider.val - self.settings.sound_volume) > 0.01:
                self.settings.sound_volume = self.sound_slider.val
                self.update_audio_volumes()
            
            if abs(self.music_slider.val - self.settings.music_volume) > 0.01:
                self.settings.music_volume = self.music_slider.val
                self.update_audio_volumes()
        
        elif self.state == GameState.LEADERBOARD:
            for button in self.leaderboard_buttons:
                button.update(mouse_pos, mouse_clicked)
        
        elif self.state == GameState.CONTROLLER_SETUP:
            for button in self.controller_buttons:
                button.update(mouse_pos, mouse_clicked)
        
        elif self.state == GameState.GAME_OVER:
            for button in self.game_over_buttons:
                button.update(mouse_pos, mouse_clicked)
        
        elif self.state == GameState.PLAYING:
            # Handle mouse throwing
            if mouse_clicked and not self.paused:
                self.throw_drink(mouse_pos[0], mouse_pos[1])
            
            # Handle controller throwing
            if (controller_input and self.settings.controller_enabled and 
                controller_input.get('throw_button') and not self.paused):
                if self.controller_throw_target:
                    self.throw_drink(self.controller_throw_target[0], self.controller_throw_target[1])
    
    def handle_game_input(self, event):
        """Handle keyboard input during gameplay"""
        if event.key == pygame.K_1:
            if self.inventory[DrinkType.BEER] > 0:
                self.selected_drink = DrinkType.BEER
        elif event.key == pygame.K_2:
            if self.inventory[DrinkType.WINE] > 0:
                self.selected_drink = DrinkType.WINE
        elif event.key == pygame.K_3:
            if self.inventory[DrinkType.COCKTAIL] > 0:
                self.selected_drink = DrinkType.COCKTAIL
        elif event.key == pygame.K_r:
            self.start_restock()
        elif event.key == pygame.K_p:
            self.paused = not self.paused
        elif event.key == pygame.K_ESCAPE:
            self.show_main_menu()
    
    def handle_text_input(self, event):
        """Handle text input for high score name"""
        if event.key == pygame.K_RETURN:
            self.add_high_score()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif len(self.input_text) < 15 and event.unicode.isprintable():
            self.input_text += event.unicode
    
    def get_controller_input(self):
        """Get controller input state"""
        if not self.controller or not self.settings.controller_enabled:
            return None
        
        # Update controller throw target based on left stick
        if self.controller.get_numaxes() >= 2:
            stick_x = self.controller.get_axis(self.settings.controller_mappings['throw_axis_x'])
            stick_y = self.controller.get_axis(self.settings.controller_mappings['throw_axis_y'])
            
            if abs(stick_x) > self.settings.controller_deadzone or abs(stick_y) > self.settings.controller_deadzone:
                # Convert stick input to screen coordinates
                center_x, center_y = self.player_x, self.player_y
                max_range = 200  # Maximum throw range
                
                target_x = center_x + stick_x * max_range
                target_y = center_y + stick_y * max_range
                
                # Clamp to screen bounds
                target_x = max(50, min(SCREEN_WIDTH - 50, target_x))
                target_y = max(100, min(SCREEN_HEIGHT - 100, target_y))
                
                self.controller_throw_target = (target_x, target_y)
        
        # Return controller state
        return {
            'throw_button': self.controller.get_button(self.settings.controller_mappings.get('throw_button', 5))
        }
    
    def handle_controller_input(self, button):
        """Handle controller button presses"""
        mappings = self.settings.controller_mappings
        
        if button == mappings.get('select_beer', 0) and self.inventory[DrinkType.BEER] > 0:
            self.selected_drink = DrinkType.BEER
        elif button == mappings.get('select_wine', 1) and self.inventory[DrinkType.WINE] > 0:
            self.selected_drink = DrinkType.WINE
        elif button == mappings.get('select_cocktail', 2) and self.inventory[DrinkType.COCKTAIL] > 0:
            self.selected_drink = DrinkType.COCKTAIL
        elif button == mappings.get('restock', 3):
            self.start_restock()
        elif button == mappings.get('pause', 7):
            self.paused = not self.paused
    
    # Game logic methods (same as before but organized)
    def spawn_customer(self):
        if self.customers_in_wave >= self.wave_size:
            return
        
        spawn_locations = [
            (-30, random.randint(100, SCREEN_HEIGHT - 100)),
            (SCREEN_WIDTH + 30, random.randint(100, SCREEN_HEIGHT - 100)),
            (random.randint(100, SCREEN_WIDTH - 100), -30),
            (random.randint(100, SCREEN_WIDTH - 100), SCREEN_HEIGHT + 30)
        ]
        
        spawn_x, spawn_y = random.choice(spawn_locations)
        drink_type = random.choice(list(DrinkType))
        
        # 5% compounding speed increase per wave
        speed_multiplier = 1.05 ** (self.wave - 1)
        customer_speed = self.base_customer_speed * speed_multiplier
        
        customer = Customer(
            spawn_x, spawn_y, 
            self.player_x, self.player_y,
            drink_type, customer_speed
        )
        
        self.customers.append(customer)
        self.customers_in_wave += 1
    
    def throw_drink(self, target_x, target_y):
        if (self.is_restocking or 
            self.inventory[self.selected_drink] <= 0):
            return
        
        projectile = Projectile(
            self.player_x, self.player_y,
            target_x, target_y,
            self.selected_drink
        )
        
        self.projectiles.append(projectile)
        self.inventory[self.selected_drink] -= 1
        
        self.hook_throw_drink(self.selected_drink, target_x, target_y)
        
        # Auto-switch to available drink if current is empty
        if self.inventory[self.selected_drink] <= 0:
            for drink_type in DrinkType:
                if self.inventory[drink_type] > 0:
                    self.selected_drink = drink_type
                    break
    
    def create_particles(self, x, y, color, count=8):
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def check_collisions(self):
        for proj_idx, projectile in enumerate(self.projectiles[:]):
            for customer in self.customers[:]:
                if customer.served:
                    continue
                    
                dx = projectile.x - customer.x
                dy = projectile.y - customer.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < customer.size + projectile.size:
                    if projectile.drink_type == customer.drink_type:
                        # Correct drink
                        points = 10 + (self.wave - 1) * 2
                        self.score += points
                        self.customers_served += 1
                        
                        dialogue = random.choice(self.positive_dialogue)
                        customer.set_served(dialogue, successful=True)
                        
                        self.create_particles(
                            customer.x, customer.y,
                            self.get_drink_color(projectile.drink_type)
                        )
                        
                        self.hook_order_success(customer, projectile.drink_type, points)
                    else:
                        # Wrong drink - lose a life!
                        self.lives -= 1
                        dialogue = random.choice(self.negative_dialogue)
                        customer.set_served(dialogue, successful=False)
                        
                        self.create_particles(
                            customer.x, customer.y,
                            COLORS['particle_splat']
                        )
                        
                        self.hook_order_fail(customer, projectile.drink_type, customer.drink_type)
                        
                        if self.lives <= 0:
                            self.game_over()
                            return
                    
                    # Remove projectile
                    if proj_idx < len(self.projectiles):
                        self.projectiles.pop(proj_idx)
                    break
    
    def update_wave_system(self):
        current_spawn_delay = max(30, self.base_spawn_delay - (self.wave - 1) * 8)
        
        if self.customers_in_wave < self.wave_size:
            self.spawn_timer += 1
            if self.spawn_timer >= current_spawn_delay:
                self.spawn_customer()
                self.spawn_timer = 0
        
        if (self.customers_in_wave >= self.wave_size and 
            len([c for c in self.customers if not c.served]) == 0):
            self.wave += 1
            self.customers_in_wave = 0
            self.wave_size = min(8 + (self.wave - 1) * 2, 20)
            self.customers = [c for c in self.customers if c.dialogue_timer > 0]
    
    def start_restock(self):
        if not self.is_restocking:
            self.is_restocking = True
            self.restock_timer = self.restock_duration
    
    def update_restock(self):
        if self.is_restocking:
            self.restock_timer -= 1
            if self.restock_timer <= 0:
                self.inventory = {
                    DrinkType.BEER: 20,
                    DrinkType.WINE: 20,
                    DrinkType.COCKTAIL: 20
                }
                self.is_restocking = False
                self.hook_restock_complete()
    
    def update_customers(self):
        for customer in self.customers[:]:
            customer.update()
            
            if not customer.served and customer.distance_to_target() < 30:
                self.lives -= 1
                self.customers.remove(customer)
                self.create_particles(customer.x, customer.y, COLORS['particle_splat'])
                self.hook_customer_reach_bar(customer)
                
                if self.lives <= 0:
                    self.game_over()
    
    def update_projectiles(self):
        for projectile in self.projectiles[:]:
            if not projectile.update():
                self.projectiles.remove(projectile)
    
    def update_particles(self):
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
    
    def update_game(self):
        """Update game logic when in playing state"""
        if self.paused:
            return
            
        self.update_wave_system()
        self.update_customers()
        self.update_projectiles()
        self.update_particles()
        self.update_restock()
        self.check_collisions()
    
    # Drawing methods
    def draw_background(self):
        """Draw the game background with optional floor texture"""
        if hasattr(self, 'floor_surface') and self.floor_surface:
            # Draw tiled floor
            self.screen.blit(self.floor_surface, (0, 0))
        else:
            # Fallback to solid color
            self.screen.fill(COLORS['bg'])
    
    def draw_menu_background(self):
        self.screen.fill(COLORS['menu_bg'])
        
        # Draw title with improved positioning
        title_surface = self.title_font.render("🍺 Flair! 🍺", True, COLORS['text_gold'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle = "Master the Art of Cocktail Combat"
        subtitle_surface = self.font.render(subtitle, True, COLORS['text_white'])
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 240))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_main_menu(self):
        self.draw_menu_background()
        
        for button in self.main_menu_buttons:
            button.draw(self.screen)
        
        # Draw controller status - better positioned
        controller_status = "Controller: Connected" if self.controller else "Controller: Not Connected"
        controller_color = COLORS['text_green'] if self.controller else COLORS['text_gray']
        status_surface = self.small_font.render(controller_status, True, controller_color)
        self.screen.blit(status_surface, (80, SCREEN_HEIGHT - 40))
        
        # Draw version or credits
        credits_surface = self.small_font.render("Made with Pygame", True, COLORS['text_gray'])
        credits_rect = credits_surface.get_rect(right=SCREEN_WIDTH - 80, bottom=SCREEN_HEIGHT - 40)
        self.screen.blit(credits_surface, credits_rect)
    
    def draw_settings_menu(self):
        self.draw_menu_background()
        
        # Draw settings title
        title_surface = self.large_font.render("Settings", True, COLORS['text_gold'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_surface, title_rect)
        
        # Draw sliders with labels
        self.sound_slider.draw(self.screen, self.font)
        self.music_slider.draw(self.screen, self.font)
        
        # Draw controller settings
        controller_y = 450
        controller_status = "ENABLED" if self.settings.controller_enabled else "DISABLED"
        controller_color = COLORS['text_green'] if self.settings.controller_enabled else COLORS['text_red']
        
        controller_label = self.font.render("Controller Support:", True, COLORS['text_white'])
        self.screen.blit(controller_label, (400, controller_y))
        
        controller_status_surface = self.font.render(controller_status, True, controller_color)
        self.screen.blit(controller_status_surface, (600, controller_y))
        
        controller_hint = self.small_font.render("Press 'C' to toggle", True, COLORS['text_gray'])
        self.screen.blit(controller_hint, (400, controller_y + 30))
        
        # Instructions
        instructions_y = 550
        instructions = [
            "• Use sliders to adjust audio levels",
            "• Changes apply immediately",
            "• Settings are saved automatically"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.small_font.render(instruction, True, COLORS['text_white'])
            self.screen.blit(instruction_surface, (200, instructions_y + i * 25))
        
        for button in self.settings_buttons:
            button.draw(self.screen)
    
    def draw_leaderboard_menu(self):
        self.draw_menu_background()
        
        title_surface = self.large_font.render("High Scores", True, COLORS['text_gold'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_surface, title_rect)
        
        # Draw high scores with better spacing
        y_start = 200
        if not self.high_score_manager.high_scores:
            no_scores_text = "No high scores yet! Play a game to set one."
            no_scores_surface = self.font.render(no_scores_text, True, COLORS['text_white'])
            no_scores_rect = no_scores_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))
            self.screen.blit(no_scores_surface, no_scores_rect)
        else:
            headers = ["Rank", "Name", "Score", "Wave", "Date"]
            header_x_positions = [250, 350, 500, 600, 750]
            
            # Draw headers
            for i, header in enumerate(headers):
                header_surface = self.font.render(header, True, COLORS['text_gold'])
                self.screen.blit(header_surface, (header_x_positions[i], y_start))
            
            # Draw separator line
            pygame.draw.line(self.screen, COLORS['text_gold'], 
                           (250, y_start + 30), (850, y_start + 30), 2)
            
            # Draw scores
            for i, score in enumerate(self.high_score_manager.high_scores):
                y_pos = y_start + 50 + i * 35
                values = [str(i + 1), score.name, str(score.score), str(score.wave), score.date.split()[0]]
                
                for j, value in enumerate(values):
                    value_surface = self.small_font.render(value, True, COLORS['text_white'])
                    self.screen.blit(value_surface, (header_x_positions[j], y_pos))
        
        for button in self.leaderboard_buttons:
            button.draw(self.screen)
    
    def draw_controller_setup_menu(self):
        self.draw_menu_background()
        
        title_surface = self.large_font.render("Controller Setup", True, COLORS['text_gold'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_surface, title_rect)
        
        if self.controller:
            controller_info = [
                f"Controller: {self.controller.get_name()}",
                f"Buttons: {self.controller.get_numbuttons()}",
                f"Axes: {self.controller.get_numaxes()}",
                "",
                "Default Xbox Controller Mapping:",
                "",
                "A Button (0) - Select Beer",
                "B Button (1) - Select Wine", 
                "X Button (2) - Select Cocktail",
                "Y Button (3) - Restock",
                "Start Button (7) - Pause",
                "Right Bumper (5) - Throw Drink",
                "Left Stick - Aim & Target"
            ]
            
            start_y = 200
            for i, info in enumerate(controller_info):
                if "Default Xbox" in info:
                    color = COLORS['text_gold']
                elif info.startswith(("A Button", "B Button", "X Button", "Y Button", "Start Button", "Right Bumper", "Left Stick")):
                    color = COLORS['text_white']
                elif info == "":
                    continue
                else:
                    color = COLORS['text_white']
                
                info_surface = self.small_font.render(info, True, color)
                self.screen.blit(info_surface, (300, start_y + i * 30))
        else:
            no_controller_text = "No controller detected."
            no_controller_surface = self.font.render(no_controller_text, True, COLORS['text_red'])
            no_controller_rect = no_controller_surface.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(no_controller_surface, no_controller_rect)
            
            instruction_text = "Connect a controller and click 'Detect Controller' to set it up."
            instruction_surface = self.small_font.render(instruction_text, True, COLORS['text_white'])
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))
            self.screen.blit(instruction_surface, instruction_rect)
        
        for button in self.controller_buttons:
            button.draw(self.screen)
    
    def draw_game_over_menu(self):
        self.draw_menu_background()
        
        # Game over title
        title_surface = self.large_font.render("Game Over!", True, COLORS['text_red'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_surface, title_rect)
        
        # Final stats
        stats = [
            f"Final Score: {self.score}",
            f"Wave Reached: {self.wave}",
            f"Customers Served: {self.customers_served}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font.render(stat, True, COLORS['text_white'])
            stat_rect = stat_surface.get_rect(center=(SCREEN_WIDTH // 2, 260 + i * 30))
            self.screen.blit(stat_surface, stat_rect)
        
        # High score input
        if self.input_active:
            input_prompt = "New High Score! Enter your name:"
            prompt_surface = self.font.render(input_prompt, True, COLORS['text_gold'])
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, 380))
            self.screen.blit(prompt_surface, prompt_rect)
            
            # Input box
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, 420, 200, 30)
            pygame.draw.rect(self.screen, COLORS['text_white'], input_box)
            pygame.draw.rect(self.screen, COLORS['text_gold'], input_box, 2)
            
            # Input text
            input_surface = self.font.render(self.input_text, True, COLORS['text_red'])
            self.screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))
            
            # Instructions
            instruction = "Press Enter to save"
            instruction_surface = self.small_font.render(instruction, True, COLORS['text_white'])
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, 470))
            self.screen.blit(instruction_surface, instruction_rect)
        
        for button in self.game_over_buttons:
            button.draw(self.screen)
    
    def draw_bar(self):
        bar_size = 60
        pygame.draw.rect(
            self.screen, COLORS['bar'],
            (self.player_x - bar_size//2, self.player_y - bar_size//2, bar_size, bar_size)
        )
        pygame.draw.rect(
            self.screen, COLORS['bar_top'],
            (self.player_x - bar_size//2 + 5, self.player_y - bar_size//2 + 5, bar_size - 10, bar_size - 10)
        )
        
        pygame.draw.circle(
            self.screen, COLORS['crosshair'],
            (self.player_x, self.player_y), 8, 2
        )
        
        # Draw controller aim indicator
        if (self.controller_throw_target and self.settings.controller_enabled and 
            self.controller):
            pygame.draw.circle(
                self.screen, COLORS['crosshair'],
                (int(self.controller_throw_target[0]), int(self.controller_throw_target[1])), 10, 2
            )
    
    def draw_customers(self):
        for customer in self.customers:
            if customer.served:
                # Use custom sprites for served customers
                if customer.service_successful and self.images['happy_customer']:
                    # Draw happy customer sprite
                    sprite = self.images['happy_customer']
                    sprite_rect = sprite.get_rect(center=(int(customer.x), int(customer.y)))
                    self.screen.blit(sprite, sprite_rect)
                elif not customer.service_successful and self.images['unhappy_customer']:
                    # Draw unhappy customer sprite
                    sprite = self.images['unhappy_customer']
                    sprite_rect = sprite.get_rect(center=(int(customer.x), int(customer.y)))
                    self.screen.blit(sprite, sprite_rect)
                else:
                    # Fallback to colored circles if sprites not available
                    color = COLORS['text_green'] if customer.service_successful else COLORS['text_red']
                    pygame.draw.circle(
                        self.screen, color,
                        (int(customer.x), int(customer.y)), customer.size
                    )
            else:
                # Draw active customer as blue circle
                pygame.draw.circle(
                    self.screen, COLORS['customer'],
                    (int(customer.x), int(customer.y)), customer.size
                )
                
                # Draw drink request bubble
                drink_color = self.get_drink_color(customer.drink_type)
                pygame.draw.circle(
                    self.screen, drink_color,
                    (int(customer.x), int(customer.y - 35)), 15
                )
                pygame.draw.circle(
                    self.screen, COLORS['text_white'],
                    (int(customer.x), int(customer.y - 35)), 15, 2
                )
            
            # Draw dialogue
            if customer.dialogue and customer.dialogue_timer > 0:
                dialogue_color = COLORS['text_green'] if customer.service_successful else COLORS['text_red']
                dialogue_surface = self.small_font.render(customer.dialogue, True, dialogue_color)
                dialogue_rect = dialogue_surface.get_rect(center=(customer.x, customer.y - 55))
                self.screen.blit(dialogue_surface, dialogue_rect)
    
    def draw_projectiles(self):
        for projectile in self.projectiles:
            color = self.get_drink_color(projectile.drink_type)
            pygame.draw.circle(
                self.screen, color,
                (int(projectile.x), int(projectile.y)), projectile.size
            )
    
    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle.life / particle.max_life))
            color = (*particle.color[:3], alpha)
            
            particle_surf = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surf, color,
                (particle.size, particle.size), particle.size
            )
            self.screen.blit(
                particle_surf, 
                (particle.x - particle.size, particle.y - particle.size)
            )
    
    def draw_game_ui(self):
        # Game title
        title_surface = self.large_font.render("🍺 Flair! 🍺", True, COLORS['text_gold'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_surface, title_rect)
        
        # Stats
        stats_x = 50
        stats_y = 60
        stats = [
            f"Score: {self.score}",
            f"Wave: {self.wave}",
            f"Lives: {'❤️' * self.lives}",
            f"Served: {self.customers_served}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.small_font.render(stat, True, COLORS['text_white'])
            self.screen.blit(stat_surface, (stats_x + i * 160, stats_y))
        
        # Inventory
        inv_x = SCREEN_WIDTH - 300
        inv_y = 50
        
        drink_types = [DrinkType.BEER, DrinkType.WINE, DrinkType.COCKTAIL]
        drink_keys = ['1', '2', '3']
        
        for i, (drink_type, key) in enumerate(zip(drink_types, drink_keys)):
            x = inv_x + i * 120
            
            color = self.get_drink_color(drink_type)
            if drink_type == self.selected_drink:
                pygame.draw.circle(self.screen, COLORS['text_gold'], (x, inv_y), 22, 3)
            pygame.draw.circle(self.screen, color, (x, inv_y), 18)
            
            count = self.inventory[drink_type]
            count_surface = self.small_font.render(str(count), True, COLORS['text_white'])
            count_rect = count_surface.get_rect(center=(x, inv_y + 30))
            self.screen.blit(count_surface, count_rect)
            
            key_surface = self.small_font.render(f"({key})", True, COLORS['text_gold'])
            key_rect = key_surface.get_rect(center=(x, inv_y + 50))
            self.screen.blit(key_surface, key_rect)
        
        # Controls
        controls_y = SCREEN_HEIGHT - 60
        controls = [
            "1/2/3: Select drinks",
            "Mouse/Controller: Aim & throw",
            "R: Restock",
            "P: Pause | ESC: Menu"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.small_font.render(control, True, COLORS['text_white'])
            self.screen.blit(control_surface, (50 + i * 250, controls_y))
        
        # Wave info
        wave_info = f"Wave {self.wave} - {self.customers_in_wave}/{self.wave_size} spawned"
        wave_surface = self.font.render(wave_info, True, COLORS['text_gold'])
        wave_rect = wave_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(wave_surface, wave_rect)
        
        # Restock overlay
        if self.is_restocking:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            restock_text = "RESTOCKING..."
            restock_surface = self.large_font.render(restock_text, True, COLORS['text_gold'])
            restock_rect = restock_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restock_surface, restock_rect)
            
            time_text = f"{self.restock_timer // 60 + 1} seconds remaining"
            time_surface = self.font.render(time_text, True, COLORS['text_white'])
            time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(time_surface, time_rect)
        
        # Pause overlay
        if self.paused:
            pause_surface = self.large_font.render("PAUSED - Press P to continue", True, COLORS['text_gold'])
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_surface, pause_rect)
    
    def draw_game(self):
        self.draw_background()
        self.draw_bar()
        self.draw_customers()
        self.draw_projectiles()
        self.draw_particles()
        self.draw_game_ui()
    
    def run(self):
        """Main game loop"""
        self.play_background_music()
        
        while self.running:
            self.handle_input()
            
            # Update based on current state
            if self.state == GameState.PLAYING:
                self.update_game()
            
            # Draw based on current state
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.SETTINGS:
                self.draw_settings_menu()
            elif self.state == GameState.LEADERBOARD:
                self.draw_leaderboard_menu()
            elif self.state == GameState.CONTROLLER_SETUP:
                self.draw_controller_setup_menu()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Save settings before quitting
        self.settings.save_settings()
        pygame.quit()

if __name__ == "__main__":
    game = FlairGame()

    game.run()
