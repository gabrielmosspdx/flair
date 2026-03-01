"""Fully integrated game with all refactored systems properly connected (no nested classes)."""

import asyncio

import pygame

from .managers import AssetManager, AudioManager, Settings
from .managers.input_manager import InputManager
from .scenes.game_over_scene import GameOverScene
from .scenes.game_scene import GameScene
from .scenes.menu_scene import MainMenuScene
from .scenes.scene_manager import SceneManager
from .scenes.settings_scene import SettingsScene
from .ui.hud import HUD
from .utils.config import config
from .utils.debug import debug_overlay
from .utils.logger import game_logger
from .utils.save_system import SaveSystem


class FlairGame:
    """Fully integrated Flair game using all refactored systems."""

    def __init__(self):
        """Initialize the integrated game."""
        game_logger.info("Initializing Integrated Flair Game")

        # Initialize Pygame
        pygame.init()
        pygame.joystick.init()

        # Load configuration
        config.load_config()

        # Display setup
        self.screen_width = config.get("display.screen_width", 1200)
        self.screen_height = config.get("display.screen_height", 800)
        self.fps = config.get("display.fps", 60)

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Flair! - Fully Integrated Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt: float = 0.0

        # Initialize managers
        self.settings = Settings.load()
        self.assets = AssetManager()
        self.audio = AudioManager(self.settings)
        self.input_manager = InputManager()
        self.scene_manager = SceneManager()
        self.save_system = SaveSystem()

        # Load resources
        self.assets.load_all()
        self.audio.initialize()

        # Initialize HUD
        self.hud = HUD(self.assets)

        # Initialize debug overlay
        debug_font = self.assets.get_font("small")
        debug_overlay.font = debug_font
        debug_overlay.enabled = False  # Start disabled, F4 toggles it
        debug_overlay.show_collision_boxes = config.get("debug.show_collision_boxes", False)

        # Create floor pattern
        self.floor_surface = self.assets.create_floor_pattern(self.screen_width, self.screen_height)

        # Initialize scenes
        self.setup_scenes()

        # Game state for persistence
        self.final_score = 0
        self.final_wave = 0

        game_logger.info("Game initialization complete")

    def setup_scenes(self):
        """Setup all game scenes."""
        # Create scene instances
        main_menu = MainMenuScene(self)
        game_scene = GameScene(self)
        game_over = GameOverScene(self)
        settings = SettingsScene(self)

        # Add scenes to manager
        self.scene_manager.add_scene("main_menu", main_menu)
        self.scene_manager.add_scene("game", game_scene)
        self.scene_manager.add_scene("game_over", game_over)
        self.scene_manager.add_scene("settings", settings)

        # Start with main menu
        self.scene_manager.switch_to("main_menu", with_transition=False)

        game_logger.info("All scenes initialized")

    def handle_events(self):
        """Handle input events."""
        events = pygame.event.get()

        # Check for quit
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

        # Update input manager
        self.input_manager.update(events)

        # Global hotkeys
        if self.input_manager.is_key_just_pressed(pygame.K_F3):
            # Toggle Dev Mode
            self.settings.dev_mode = not self.settings.dev_mode
            self.settings.save()
            game_logger.info(f"Dev Mode: {'enabled' if self.settings.dev_mode else 'disabled'}")

            # Hide debug overlay when disabling Dev Mode
            if not self.settings.dev_mode and debug_overlay.enabled:
                debug_overlay.enabled = False
                game_logger.info("Debug overlay disabled (Dev Mode off)")

        if self.input_manager.is_key_just_pressed(pygame.K_F4):
            # Toggle debug overlay (only works in Dev Mode)
            if self.settings.dev_mode:
                debug_overlay.toggle()
                game_logger.info(
                    f"Debug overlay: {'enabled' if debug_overlay.enabled else 'disabled'}"
                )

        if self.input_manager.is_key_just_pressed(pygame.K_F6):
            # Toggle collision boxes (only works in Dev Mode)
            if self.settings.dev_mode:
                debug_overlay.show_collision_boxes = not debug_overlay.show_collision_boxes
                config.set("debug.show_collision_boxes", debug_overlay.show_collision_boxes)
                config.save()
                enabled = "enabled" if debug_overlay.show_collision_boxes else "disabled"
                game_logger.info(f"Collision boxes: {enabled}")

        if self.input_manager.is_key_just_pressed(pygame.K_F5):
            # Quick save (only during gameplay)
            if self.scene_manager.current_scene_name == "game":
                game_scene = self.scene_manager.scenes["game"]
                if isinstance(game_scene, GameScene):
                    state = self.save_system.create_game_state(
                        game_scene.score,
                        game_scene.wave,
                        game_scene.lives,
                        game_scene.inventory,
                        game_scene.customers_served,
                        game_scene.selected_drink,
                    )
                    if self.save_system.autosave(state):
                        game_logger.info("Game autosaved")

        # Pass events to current scene
        self.scene_manager.handle_events(events)

    def update(self):
        """Update game logic."""
        # Update scene
        self.scene_manager.update(self.dt)

        # Update HUD animations if in game
        if self.scene_manager.current_scene_name == "game":
            self.hud.update()

        # Update debug timers
        debug_overlay.update_fps(self.clock)

    def draw(self):
        """Draw everything."""
        # Start frame timing
        debug_overlay.start_timer("frame")

        # Draw current scene
        self.scene_manager.draw(self.screen)

        # Draw debug overlay
        if debug_overlay.enabled:
            game_data = {}
            if self.scene_manager.current_scene_name == "game":
                game_scene = self.scene_manager.scenes["game"]
                if isinstance(game_scene, GameScene):
                    game_data = {
                        "Scene": self.scene_manager.current_scene_name,
                        "Score": game_scene.score,
                        "Wave": game_scene.wave,
                        "Lives": game_scene.lives,
                        "FPS Target": self.fps,
                    }
                else:
                    game_data = {
                        "Scene": self.scene_manager.current_scene_name,
                        "FPS Target": self.fps,
                    }
            else:
                game_data = {"Scene": self.scene_manager.current_scene_name, "FPS Target": self.fps}

            debug_overlay.draw(self.screen, game_data)

        debug_overlay.end_timer("frame")

    async def run(self):
        """Main game loop with fixed timestep for game logic, adapted for WebAssembly."""
        game_logger.info("Starting main game loop")
        self.audio.play_music()

        # Fixed timestep for game logic (60 Hz)
        FIXED_TIMESTEP = 1.0 / 60.0  # 60 updates per second
        accumulator = 0.0
        current_time = pygame.time.get_ticks() / 1000.0

        while self.running:
            new_time = pygame.time.get_ticks() / 1000.0
            frame_time = new_time - current_time
            current_time = new_time

            # Prevent spiral of death
            frame_time = min(frame_time, 0.25)

            accumulator += frame_time

            # Handle events always
            self.handle_events()

            # Fixed timestep updates
            while accumulator >= FIXED_TIMESTEP:
                self.dt = float(FIXED_TIMESTEP)
                self.update()
                accumulator -= FIXED_TIMESTEP

            # Render at display FPS
            self.draw()
            pygame.display.flip()

            # Limit display FPS
            self.clock.tick(self.fps)

            # Yield control to the browser event loop (required for WebAssembly)
            await asyncio.sleep(0)

        # Cleanup
        game_logger.info("Shutting down game")
        self.settings.save()
        config.save()
        pygame.quit()
