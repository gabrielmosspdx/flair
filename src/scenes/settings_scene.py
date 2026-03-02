"""Comprehensive settings scene with tabs for all configuration options."""

from typing import Dict, List

import pygame

from ..ui import Button, Slider
from ..utils.config import config
from ..utils.constants import COLORS
from ..utils.logger import game_logger
from .base_scene import BaseScene


class SettingsScene(BaseScene):
    """Settings scene with comprehensive configuration controls."""

    def __init__(self, game):
        """Initialize settings scene.

        Args:
            game: Reference to main game object
        """
        super().__init__(game)

        # Tab system
        self.tabs = ["Gameplay", "Display", "Audio", "Debug", "Controls"]
        self.current_tab = 0
        self.tab_buttons = []

        # UI elements for each tab
        self.sliders: Dict[str, Dict[str, Slider]] = {tab: {} for tab in self.tabs}
        self.buttons: Dict[str, Dict[str, Button]] = {tab: {} for tab in self.tabs}
        self.checkboxes: Dict[str, Dict[str, bool]] = {tab: {} for tab in self.tabs}

        # Store original values for reset
        self.original_config = config.data.copy()

        self.setup_ui()

    def setup_ui(self):
        """Setup UI elements for all tabs."""
        font = self.game.assets.get_font("normal")

        # Create tab buttons
        tab_width = 150
        tab_height = 40
        tab_y = 150
        start_x = (self.game.screen_width - len(self.tabs) * tab_width) // 2

        for i, tab in enumerate(self.tabs):
            button = Button(
                start_x + i * tab_width,
                tab_y,
                tab_width - 5,
                tab_height,
                tab,
                font,
                lambda idx=i: self.switch_tab(idx),
            )
            self.tab_buttons.append(button)

        # Common buttons
        self.back_button = Button(
            50, self.game.screen_height - 80, 100, 40, "Back", font, self.go_back
        )

        self.apply_button = Button(
            self.game.screen_width - 250,
            self.game.screen_height - 80,
            100,
            40,
            "Apply",
            font,
            self.apply_settings,
        )

        self.reset_button = Button(
            self.game.screen_width - 130,
            self.game.screen_height - 80,
            100,
            40,
            "Reset",
            font,
            self.reset_settings,
        )

        # Setup UI for each tab
        self.setup_gameplay_tab()
        self.setup_display_tab()
        self.setup_audio_tab()
        self.setup_debug_tab()

    def setup_gameplay_tab(self):
        """Setup Gameplay tab UI elements."""
        y_start = 220
        y_spacing = 45

        # Game difficulty and balance settings
        self.sliders["Gameplay"]["initial_lives"] = Slider(
            350,
            y_start,
            250,
            1,
            10,
            config.get("game.initial_lives", 3),
            "Initial Lives",
            integer_only=True,
        )

        self.sliders["Gameplay"]["initial_inventory"] = Slider(
            350,
            y_start + y_spacing,
            250,
            1,
            20,
            config.get("game.initial_inventory", 5),
            "Initial Inventory",
            integer_only=True,
        )

        self.sliders["Gameplay"]["base_spawn_delay"] = Slider(
            350,
            y_start + y_spacing * 2,
            250,
            30,
            240,
            config.get("game.base_spawn_delay", 120),
            "Base Spawn Delay",
            integer_only=True,
        )

        self.sliders["Gameplay"]["base_customer_speed"] = Slider(
            350,
            y_start + y_spacing * 3,
            250,
            0.1,
            2.0,
            config.get("game.base_customer_speed", 0.5),
            "Customer Speed",
        )

        self.sliders["Gameplay"]["initial_wave_size"] = Slider(
            350,
            y_start + y_spacing * 4,
            250,
            4,
            20,
            config.get("game.initial_wave_size", 8),
            "Initial Wave Size",
            integer_only=True,
        )

        self.sliders["Gameplay"]["max_wave_size"] = Slider(
            350,
            y_start + y_spacing * 5,
            250,
            10,
            50,
            config.get("game.max_wave_size", 20),
            "Max Wave Size",
            integer_only=True,
        )

        self.sliders["Gameplay"]["wave_speed_multiplier"] = Slider(
            350,
            y_start + y_spacing * 6,
            250,
            1.0,
            1.2,
            config.get("game.wave_speed_multiplier", 1.05),
            "Wave Speed Multiplier",
        )

        self.sliders["Gameplay"]["min_customer_spawn_distance"] = Slider(
            350,
            y_start + y_spacing * 7,
            250,
            50,
            150,
            config.get("game.min_customer_spawn_distance", 90),
            "Min Spawn Distance",
            integer_only=True,
        )

        self.sliders["Gameplay"]["base_points"] = Slider(
            350,
            y_start + y_spacing * 8,
            250,
            5,
            50,
            config.get("game.base_points", 10),
            "Base Points",
            integer_only=True,
        )

    def setup_display_tab(self):
        """Setup Display tab UI elements."""
        y_start = 220
        y_spacing = 50

        self.sliders["Display"]["fps"] = Slider(
            350,
            y_start,
            250,
            30,
            144,
            config.get("display.fps", 60),
            "Display FPS",
            integer_only=True,
        )

        self.sliders["Display"]["bar_size"] = Slider(
            350,
            y_start + y_spacing,
            250,
            40,
            100,
            config.get("ui.bar_size", 60),
            "Bar Size",
            integer_only=True,
        )

    def setup_audio_tab(self):
        """Setup Audio tab UI elements."""
        y_start = 220
        y_spacing = 50

        # Audio sliders (using settings manager values)
        self.sliders["Audio"]["sound_volume"] = Slider(
            350, y_start, 250, 0.0, 1.0, self.game.settings.sound_volume, "Sound Volume"
        )

        self.sliders["Audio"]["music_volume"] = Slider(
            350, y_start + y_spacing, 250, 0.0, 1.0, self.game.settings.music_volume, "Music Volume"
        )

    def setup_debug_tab(self):
        """Setup Debug tab UI elements."""
        # Debug checkboxes - only show_collision_boxes and dev_mode remain
        self.checkboxes["Debug"]["show_collision_boxes"] = config.get(
            "debug.show_collision_boxes", False
        )
        self.checkboxes["Debug"]["dev_mode"] = self.game.settings.dev_mode

    def switch_tab(self, tab_index: int):
        """Switch to a different settings tab."""
        self.current_tab = tab_index
        game_logger.debug(f"Switched to {self.tabs[tab_index]} tab")

    def go_back(self):
        """Return to main menu."""
        self.apply_settings()
        self.switch_to("main_menu")

    def apply_settings(self):
        """Apply all settings changes."""
        needs_new_game = False

        # Apply Gameplay settings
        for key, slider in self.sliders["Gameplay"].items():
            old_value = config.get(f"game.{key}")
            new_value = slider.get_value()
            config.set(f"game.{key}", new_value)

            # Check if this setting needs a new game
            if (
                key in ["initial_lives", "initial_inventory", "initial_wave_size"]
                and old_value != new_value
            ):
                needs_new_game = True

        # Apply Display settings
        old_fps = config.get("display.fps")
        new_fps = self.sliders["Display"]["fps"].get_value()
        config.set("display.fps", new_fps)
        config.set("ui.bar_size", self.sliders["Display"]["bar_size"].get_value())

        # Update FPS immediately if changed
        if old_fps != new_fps:
            self.game.fps = new_fps

        # Apply Audio settings
        self.game.settings.sound_volume = self.sliders["Audio"]["sound_volume"].get_value()
        self.game.settings.music_volume = self.sliders["Audio"]["music_volume"].get_value()
        self.game.audio.set_sound_volume(self.game.settings.sound_volume)
        self.game.audio.set_music_volume(self.game.settings.music_volume)

        # Apply Debug settings
        config.set("debug.show_collision_boxes", self.checkboxes["Debug"]["show_collision_boxes"])
        self.game.settings.dev_mode = self.checkboxes["Debug"]["dev_mode"]

        # Update debug overlay collision boxes setting
        from ..utils.debug import debug_overlay

        debug_overlay.show_collision_boxes = self.checkboxes["Debug"]["show_collision_boxes"]

        # Hide debug overlay if Dev Mode is disabled
        if not self.game.settings.dev_mode:
            from ..utils.debug import debug_overlay

            if debug_overlay.enabled:
                debug_overlay.enabled = False
                game_logger.info("Debug overlay disabled (Dev Mode off)")

        # Save configurations
        config.save()
        self.game.settings.save()

        # If we're in a game and settings changed that need a new game, notify
        if needs_new_game and self.game.scene_manager.current_scene_name == "game":
            game_logger.info("Some settings will apply on the next game")

        game_logger.info("Settings saved and applied")

    def reset_settings(self):
        """Reset settings to defaults."""
        # Reset config to defaults
        config._set_defaults()

        # Reset settings manager
        self.game.settings.sound_volume = 0.7
        self.game.settings.music_volume = 0.3
        self.game.settings.dev_mode = False

        # Reinitialize UI with default values
        self.setup_ui()
        game_logger.info("Settings reset to defaults")

    def handle_events(self, events: List[pygame.event.Event]):
        """Handle input events."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
                elif event.key == pygame.K_TAB:
                    # Quick tab switching with TAB key
                    self.current_tab = (self.current_tab + 1) % len(self.tabs)

        # Update tab buttons
        for button in self.tab_buttons:
            button.update(mouse_pos, mouse_clicked)

        # Update common buttons
        self.back_button.update(mouse_pos, mouse_clicked)
        self.apply_button.update(mouse_pos, mouse_clicked)
        self.reset_button.update(mouse_pos, mouse_clicked)

        # Update current tab's controls
        current_tab_name = self.tabs[self.current_tab]

        # Update sliders for current tab
        for slider in self.sliders[current_tab_name].values():
            slider.update(mouse_pos, mouse_pressed, mouse_clicked)

        # Handle checkbox clicks for current tab (only Debug tab has checkboxes now)
        if (
            mouse_clicked
            and current_tab_name in self.checkboxes
            and self.checkboxes[current_tab_name]
        ):
            checkbox_y = 220
            checkbox_spacing = 40
            for i, (key, value) in enumerate(self.checkboxes[current_tab_name].items()):
                checkbox_rect = pygame.Rect(350, checkbox_y + i * checkbox_spacing, 20, 20)
                if checkbox_rect.collidepoint(mouse_pos):
                    self.checkboxes[current_tab_name][key] = not value

    def update(self, dt: float):
        """Update scene logic."""
        pass  # No continuous updates needed

    def _draw_settings_panel(self, screen: pygame.Surface) -> None:
        """Draw the main content area panel."""
        cx = self.game.screen_width // 2
        pw, ph = 760, 480
        px, py = cx - pw // 2, 195
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((10, 5, 2, 160))
        pygame.draw.rect(
            panel_surf, (*COLORS["panel_border"], 70), pygame.Rect(0, 0, pw, ph), 1,
            border_radius=4
        )
        screen.blit(panel_surf, (px, py))

    def draw(self, screen: pygame.Surface):
        """Draw the settings screen."""
        screen.fill(COLORS["menu_bg"])
        cx = self.game.screen_width // 2

        # Subtle warm ambient glow at top
        for r in (350, 250, 150):
            gs = pygame.Surface((r * 2, r), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (180, 100, 20, max(0, 12 - (350 - r) // 30)),
                                gs.get_rect())
            screen.blit(gs, (cx - r, -r // 2))

        # Title
        title_font = self.game.assets.get_font("large")
        title = title_font.render("Settings", True, COLORS["text_gold"])
        title_rect = title.get_rect(center=(cx, 75))
        screen.blit(title, title_rect)

        # Ornamental divider under title
        col = COLORS["panel_border"]
        pygame.draw.line(screen, col, (cx - 200, 112), (cx - 12, 112), 1)
        pygame.draw.line(screen, col, (cx + 12, 112), (cx + 200, 112), 1)
        pts = [(cx, 106), (cx + 8, 112), (cx, 118), (cx - 8, 112)]
        pygame.draw.polygon(screen, COLORS["text_gold"], pts)

        # Content panel
        self._draw_settings_panel(screen)

        # Tab buttons with active-tab underline highlight
        for i, button in enumerate(self.tab_buttons):
            # Override button colors for active/inactive tab feel
            if i == self.current_tab:
                button.color_bg = COLORS["tab_active"]
                button.color_hover = COLORS["tab_active"]
            else:
                button.color_bg = COLORS["tab_inactive"]
                button.color_hover = COLORS["button_hover"]
            button.draw(screen)
            if i == self.current_tab:
                # Underline bar for active tab
                underline_surf = pygame.Surface((button.rect.width, 3), pygame.SRCALPHA)
                underline_surf.fill((*COLORS["text_gold"], 200))
                screen.blit(underline_surf, (button.rect.x, button.rect.bottom + 1))

        # Tab content
        self.draw_tab_content(screen)

        # Common action buttons
        self.back_button.draw(screen)
        self.apply_button.draw(screen)
        self.reset_button.draw(screen)

        # Dev mode indicator
        if self.game.settings.dev_mode:
            font = self.game.assets.get_font("small")
            dev_text = font.render("DEV MODE ACTIVE", True, COLORS["text_red"])
            screen.blit(dev_text, (10, 10))

    def draw_tab_content(self, screen: pygame.Surface):
        """Draw content for the current tab."""
        current_tab_name = self.tabs[self.current_tab]
        small_font = self.game.assets.get_font("small")

        if current_tab_name == "Gameplay":
            self.draw_gameplay_tab(screen, small_font)
        elif current_tab_name == "Display":
            self.draw_display_tab(screen, small_font)
        elif current_tab_name == "Audio":
            self.draw_audio_tab(screen, small_font)
        elif current_tab_name == "Debug":
            self.draw_debug_tab(screen, small_font)
        elif current_tab_name == "Controls":
            self.draw_controls_tab(screen, small_font)

    def _draw_note(self, screen: pygame.Surface, text: str, y: int = 638) -> None:
        """Draw a styled note/hint below the tab content area."""
        cx = self.game.screen_width // 2
        note_font = self.game.assets.get_font("small")
        note_surf = note_font.render(text, True, COLORS["text_amber"])
        note_rect = note_surf.get_rect(center=(cx, y))
        note_surf.set_alpha(180)
        screen.blit(note_surf, note_rect)

    def draw_gameplay_tab(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw Gameplay tab content."""
        for slider in self.sliders["Gameplay"].values():
            slider.draw(screen, font)
        self._draw_note(
            screen, "* Initial Lives, Inventory, and Wave Size apply to new games"
        )

    def draw_display_tab(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw Display tab content."""
        for slider in self.sliders["Display"].values():
            slider.draw(screen, font)
        self._draw_note(
            screen, "* Game logic runs at fixed 60 Hz. FPS only affects visual smoothness."
        )

    def draw_audio_tab(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw Audio tab content."""
        for slider in self.sliders["Audio"].values():
            slider.draw(screen, font)

    def draw_debug_tab(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw Debug tab content."""
        checkbox_y = 230
        checkbox_spacing = 50
        checkbox_labels = {
            "show_collision_boxes": "Show Collision Boxes",
            "dev_mode": "Developer Mode",
        }

        for i, (key, label) in enumerate(checkbox_labels.items()):
            row_y = checkbox_y + i * checkbox_spacing
            checked = self.checkboxes["Debug"][key]

            # Checkbox background
            checkbox_rect = pygame.Rect(350, row_y, 22, 22)
            bg_surf = pygame.Surface((22, 22), pygame.SRCALPHA)
            bg_surf.fill((10, 5, 2, 200) if checked else (30, 15, 5, 120))
            screen.blit(bg_surf, checkbox_rect.topleft)

            border_col = COLORS["text_gold"] if checked else COLORS["panel_border"]
            pygame.draw.rect(screen, border_col, checkbox_rect, 2, border_radius=3)

            if checked:
                # Gold checkmark
                pygame.draw.line(
                    screen,
                    COLORS["text_gold"],
                    (checkbox_rect.left + 4, checkbox_rect.centery),
                    (checkbox_rect.centerx - 1, checkbox_rect.bottom - 4),
                    2,
                )
                pygame.draw.line(
                    screen,
                    COLORS["text_gold"],
                    (checkbox_rect.centerx - 1, checkbox_rect.bottom - 4),
                    (checkbox_rect.right - 3, checkbox_rect.top + 4),
                    2,
                )

            label_col = COLORS["text_white"] if checked else COLORS["text_gray"]
            label_text = font.render(label, True, label_col)
            screen.blit(label_text, (checkbox_rect.right + 18, row_y - 1))

    def draw_controls_tab(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw Controls tab content."""
        controls_y = 215
        controls = [
            ("Game Controls", None),
            ("1 / 2 / 3", "Select Drink"),
            ("Mouse", "Aim & Throw"),
            ("R", "Restock"),
            ("P", "Pause"),
            ("ESC", "Menu"),
            ("", ""),
            ("Developer Controls", None),
            ("F3", "Toggle Dev Mode"),
            ("F4", "Debug Overlay"),
            ("F5", "Quick Save"),
            ("F6", "Collision Boxes"),
            ("PageUp / Down", "Change Wave"),
            ("Shift + 4–9, 0", "Jump to Wave"),
        ]

        header_font = self.game.assets.get_font("normal")
        key_x = 360
        action_x = 520

        for i, (key, action) in enumerate(controls):
            row_y = controls_y + i * 26
            if action is None:
                # Section header with mini-divider
                text = header_font.render(key, True, COLORS["text_amber"])
                screen.blit(text, (key_x - 10, row_y))
                pygame.draw.line(screen, COLORS["panel_border"],
                                 (key_x - 10, row_y + 32), (key_x + 300, row_y + 32), 1)
            elif key or action:
                if key:
                    key_text = font.render(key, True, COLORS["text_gold"])
                    screen.blit(key_text, (key_x, row_y))
                if action:
                    action_text = font.render(f"· {action}", True, COLORS["text_white"])
                    screen.blit(action_text, (action_x, row_y))
