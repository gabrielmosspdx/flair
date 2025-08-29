"""Main game play scene."""

import random
from typing import List

import pygame

from ..entities import Customer, ParticleSystem, Projectile
from ..utils.config import config
from ..utils.constants import COLORS, PROJECTILE_MAX_LIFE, PROJECTILE_SPEED, DrinkType
from ..utils.debug import debug_overlay
from ..utils.logger import game_logger
from ..utils.object_pool import ObjectPool
from .base_scene import BaseScene


class GameScene(BaseScene):
    """Main gameplay scene."""

    def __init__(self, game):
        """Initialize game scene.

        Args:
            game: Reference to main game object
        """
        super().__init__(game)

        # Object pools
        self.projectile_pool = ObjectPool(
            factory=lambda: Projectile(0, 0, 0, 0, DrinkType.BEER),
            reset_func=self._reset_projectile,
            initial_size=20,
            max_size=50,
        )

        # Sprite groups
        self.customers: pygame.sprite.RenderUpdates = pygame.sprite.RenderUpdates()
        self.projectiles: pygame.sprite.RenderUpdates = pygame.sprite.RenderUpdates()
        self.particle_system = ParticleSystem()

        # Initialize state variables
        self.paused = False
        self.game_initialized = False
        self.score = 0
        self.wave = 1
        self.lives = 3
        self.inventory = {}
        self.customers_served = 0
        self.selected_drink = DrinkType.BEER

    def _reset_projectile(self, projectile: Projectile):
        """Reset projectile for reuse."""
        projectile.life = PROJECTILE_MAX_LIFE
        if hasattr(projectile, "groups") and projectile.groups():
            projectile.remove(self.projectiles)

    def enter(self):
        """Called when scene becomes active."""
        super().enter()
        # Only reset if we haven't initialized yet (first time entering)
        if not self.game_initialized:
            self.reset_game_state()
            self.game_initialized = True

    def start_new_game(self):
        """Explicitly start a new game."""
        self.reset_game_state()
        self.game_initialized = True

    def reset_game_state(self):
        """Reset game state for new game."""
        game_logger.info("Resetting game state")

        # Player position
        self.player_x = self.game.screen.get_width() // 2
        self.player_y = self.game.screen.get_height() // 2

        # Game stats
        self.score = 0
        self.wave = 1
        self.lives = config.get("game.initial_lives", 3)
        self.customers_served = 0
        self.selected_drink = DrinkType.BEER

        # Inventory
        initial_inventory = config.get("game.initial_inventory", 5)
        self.inventory = {
            DrinkType.BEER: initial_inventory,
            DrinkType.WINE: initial_inventory,
            DrinkType.COCKTAIL: initial_inventory,
        }

        # Clear entities
        self.customers.empty()
        self.projectiles.empty()
        self.particle_system.particles.empty()
        self.projectile_pool.release_all()

        # Wave management
        self.wave_timer = 0
        self.spawn_timer = 0
        self.customers_in_wave = 0
        self.wave_size = config.get("game.initial_wave_size", 8)

        # Restock
        self.is_restocking = False
        self.restock_timer = 0

    def spawn_customer(self):
        """Spawn a new customer with minimum distance checking."""
        if self.customers_in_wave >= self.wave_size:
            return

        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()

        # Get configuration values
        min_distance = config.get("game.min_customer_spawn_distance", 90)
        retry_attempts = config.get("game.spawn_retry_attempts", 10)

        # Generate potential spawn locations
        def get_random_spawn_location():
            edge = random.randint(0, 3)
            if edge == 0:  # Left edge
                return (-30, random.randint(100, screen_height - 100))
            elif edge == 1:  # Right edge
                return (screen_width + 30, random.randint(100, screen_height - 100))
            elif edge == 2:  # Top edge
                return (random.randint(100, screen_width - 100), -30)
            else:  # Bottom edge
                return (random.randint(100, screen_width - 100), screen_height + 30)

        # Try to find a spawn location with adequate spacing
        best_location = None
        best_min_distance = 0

        for _ in range(retry_attempts):
            spawn_x, spawn_y = get_random_spawn_location()

            # Check distance to all existing customers
            if len(self.customers) == 0:
                # No customers yet, any location is fine
                best_location = (spawn_x, spawn_y)
                break

            min_dist_to_customers = float("inf")
            for customer in self.customers:
                dist = ((spawn_x - customer.x) ** 2 + (spawn_y - customer.y) ** 2) ** 0.5
                min_dist_to_customers = min(min_dist_to_customers, dist)

            # If this location meets minimum distance requirement, use it
            if min_dist_to_customers >= min_distance:
                best_location = (spawn_x, spawn_y)
                break

            # Otherwise, track the best location found so far
            if min_dist_to_customers > best_min_distance:
                best_min_distance = int(min_dist_to_customers)
                best_location = (spawn_x, spawn_y)

        # Use the best location found
        if best_location is None:
            best_location = get_random_spawn_location()

        spawn_x, spawn_y = best_location
        drink_type = random.choice(list(DrinkType))

        # Calculate speed
        base_speed = config.get("game.base_customer_speed", 0.5)
        speed_multiplier = config.get("game.wave_speed_multiplier", 1.05) ** (self.wave - 1)
        customer_speed = base_speed * speed_multiplier

        customer = Customer(
            spawn_x, spawn_y, self.player_x, self.player_y, drink_type, customer_speed
        )
        self.customers.add(customer)
        self.customers_in_wave += 1

    def throw_drink(self, target_x: float, target_y: float):
        """Throw a drink projectile."""
        if self.is_restocking or self.inventory[self.selected_drink] <= 0:
            return

        projectile = self.projectile_pool.acquire()
        # Reset the projectile with new parameters
        projectile.reset(
            self.player_x, self.player_y, target_x, target_y, self.selected_drink, PROJECTILE_SPEED
        )

        self.projectiles.add(projectile)
        self.inventory[self.selected_drink] -= 1

        self.game.audio.play_sound("throw_drink")

        # Auto-switch drink if empty
        if self.inventory[self.selected_drink] <= 0:
            for drink_type in DrinkType:
                if self.inventory[drink_type] > 0:
                    self.selected_drink = drink_type
                    break

    def start_restock(self):
        """Start restocking drinks."""
        if not self.is_restocking:
            self.is_restocking = True
            self.restock_timer = config.get("game.restock_duration", 180)
            game_logger.info("Started restocking")

    def jump_to_wave(self, wave_number: int):
        """Jump directly to a specific wave number (debug feature).

        Args:
            wave_number: The wave number to jump to
        """
        game_logger.info(f"Debug: Jumping to wave {wave_number}")

        # Clear existing customers
        self.customers.empty()

        # Set the wave number
        self.wave = wave_number

        # Reset wave-related variables
        self.customers_in_wave = 0
        initial_wave_size = config.get("game.initial_wave_size", 8)
        max_wave_size = config.get("game.max_wave_size", 20)
        self.wave_size = min(initial_wave_size + (self.wave - 1) * 2, max_wave_size)

        # Give bonus score for jumped waves (optional, for testing progression)
        base_points = config.get("game.base_points", 10)
        points_per_wave = config.get("game.points_per_wave", 2)
        estimated_customers_per_wave = initial_wave_size
        for w in range(1, wave_number):
            wave_points = (base_points + (w - 1) * points_per_wave) * estimated_customers_per_wave
            self.score += wave_points // 2  # Give half points for skipped waves

        # Refresh inventory
        restock_amount = config.get("game.restock_amount", 5)
        for drink_type in DrinkType:
            self.inventory[drink_type] = restock_amount

        game_logger.info(f"Wave {self.wave} started! Size: {self.wave_size}")

    def check_collisions(self):
        """Check projectile-customer collisions."""
        for projectile in list(self.projectiles):
            for customer in list(self.customers):
                if customer.served:
                    continue

                if projectile.rect.colliderect(customer.rect):
                    if projectile.drink_type == customer.drink_type:
                        # Correct drink
                        base_points = config.get("game.base_points", 10)
                        points_per_wave = config.get("game.points_per_wave", 2)
                        points = base_points + (self.wave - 1) * points_per_wave
                        self.score += points
                        self.customers_served += 1
                        customer.set_served(successful=True)

                        # Trigger HUD animation
                        if hasattr(self.game, "hud"):
                            self.game.hud.show_score_change(points)

                        # Effects
                        drink_color = COLORS[f"{projectile.drink_type.name.lower()}"]
                        color = (drink_color[0], drink_color[1], drink_color[2])
                        self.particle_system.create_burst(customer.x, customer.y, color)
                        self.game.audio.play_sound("order_success")
                    else:
                        # Wrong drink
                        self.lives -= 1
                        customer.set_served(successful=False)

                        # Trigger HUD flash
                        if hasattr(self.game, "hud"):
                            self.game.hud.flash_lives()
                        splat_color = COLORS["particle_splat"]
                        self.particle_system.create_burst(
                            customer.x, customer.y, (splat_color[0], splat_color[1], splat_color[2])
                        )
                        self.game.audio.play_sound("order_fail")

                        if self.lives <= 0:
                            self.game_over()
                            return

                    # Return projectile to pool
                    projectile.kill()
                    self.projectile_pool.release(projectile)
                    break

    def game_over(self):
        """Handle game over."""
        game_logger.info(f"Game Over! Score: {self.score}, Wave: {self.wave}")
        self.switch_to("game_over")
        # Store final stats for game over screen
        self.game.final_score = self.score
        self.game.final_wave = self.wave

    def handle_events(self, events: List[pygame.event.Event]):
        """Handle game input events."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and self.inventory[DrinkType.BEER] > 0:
                    self.selected_drink = DrinkType.BEER
                elif event.key == pygame.K_2 and self.inventory[DrinkType.WINE] > 0:
                    self.selected_drink = DrinkType.WINE
                elif event.key == pygame.K_3 and self.inventory[DrinkType.COCKTAIL] > 0:
                    self.selected_drink = DrinkType.COCKTAIL
                elif event.key == pygame.K_r:
                    self.start_restock()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.switch_to("main_menu")
                # Debug wave jump controls - only in Dev Mode
                elif self.game.settings.dev_mode:
                    if event.key == pygame.K_PAGEUP:
                        # Next wave
                        self.jump_to_wave(self.wave + 1)
                    elif event.key == pygame.K_PAGEDOWN:
                        # Previous wave
                        if self.wave > 1:
                            self.jump_to_wave(self.wave - 1)
                    # Number keys with SHIFT for specific waves
                    elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if event.key == pygame.K_4:
                            self.jump_to_wave(5)
                        elif event.key == pygame.K_5:
                            self.jump_to_wave(10)
                        elif event.key == pygame.K_6:
                            self.jump_to_wave(15)
                        elif event.key == pygame.K_7:
                            self.jump_to_wave(20)
                        elif event.key == pygame.K_8:
                            self.jump_to_wave(25)
                        elif event.key == pygame.K_9:
                            self.jump_to_wave(30)
                        elif event.key == pygame.K_0:
                            self.jump_to_wave(40)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.paused:
                    mouse_pos = pygame.mouse.get_pos()
                    self.throw_drink(mouse_pos[0], mouse_pos[1])

    def update(self, dt: float):
        """Update game logic."""
        if self.paused:
            return

        debug_overlay.start_timer("game_update")

        # Spawn logic
        base_spawn_delay = config.get("game.base_spawn_delay", 120)
        spawn_delay_reduction = config.get("game.spawn_delay_reduction", 8)
        current_spawn_delay = max(30, base_spawn_delay - (self.wave - 1) * spawn_delay_reduction)

        if self.customers_in_wave < self.wave_size:
            self.spawn_timer += 1
            if self.spawn_timer >= current_spawn_delay:
                self.spawn_customer()
                self.spawn_timer = 0

        # Update entities
        self.customers.update()

        for projectile in list(self.projectiles):
            projectile.update()
            if projectile.life <= 0:
                projectile.kill()
                self.projectile_pool.release(projectile)

        self.particle_system.update()

        # Update restock
        if self.is_restocking:
            self.restock_timer -= 1
            if self.restock_timer <= 0:
                restock_amount = config.get("game.restock_amount", 5)
                for drink_type in DrinkType:
                    self.inventory[drink_type] = restock_amount
                self.is_restocking = False
                self.game.audio.play_sound("restock")

        # Check collisions
        self.check_collisions()

        # Check if customers reached bar
        customer_reach_threshold = config.get("physics.customer_reach_threshold", 30)
        for customer in list(self.customers):
            if customer.has_reached_bar(customer_reach_threshold):
                self.lives -= 1
                customer.kill()
                splat_color = COLORS["particle_splat"]
                self.particle_system.create_burst(
                    customer.x, customer.y, (splat_color[0], splat_color[1], splat_color[2])
                )
                self.game.audio.play_sound("customer_reach_bar")

                if self.lives <= 0:
                    self.game_over()

        # Check wave completion
        max_wave_size = config.get("game.max_wave_size", 20)
        if (
            self.customers_in_wave >= self.wave_size
            and len([c for c in self.customers if not c.served]) == 0
        ):
            self.wave += 1
            self.customers_in_wave = 0
            initial_wave_size = config.get("game.initial_wave_size", 8)
            self.wave_size = min(initial_wave_size + (self.wave - 1) * 2, max_wave_size)
            game_logger.info(f"Wave {self.wave} started! Size: {self.wave_size}")

        # Update debug info
        debug_overlay.set_entity_count("Customers", len(self.customers))
        debug_overlay.set_entity_count("Projectiles", len(self.projectiles))
        debug_overlay.set_entity_count("Particles", len(self.particle_system.particles))
        debug_overlay.end_timer("game_update")

    def draw(self, screen: pygame.Surface):
        """Draw the game scene."""
        # Background
        if hasattr(self.game, "floor_surface") and self.game.floor_surface:
            screen.blit(self.game.floor_surface, (0, 0))
        else:
            screen.fill(COLORS["bg"])

        # Draw bar
        bar_size = config.get("ui.bar_size", 60)
        bar_rect = pygame.Rect(
            self.player_x - bar_size // 2, self.player_y - bar_size // 2, bar_size, bar_size
        )
        pygame.draw.rect(screen, COLORS["bar"], bar_rect)
        inner_rect = bar_rect.inflate(-10, -10)
        pygame.draw.rect(screen, COLORS["bar_top"], inner_rect)
        pygame.draw.circle(screen, COLORS["crosshair"], (self.player_x, self.player_y), 8, 2)

        # Draw entities
        for customer in self.customers:
            color = COLORS["customer"] if not customer.served else COLORS["customer_served"]
            pygame.draw.circle(screen, color, (int(customer.x), int(customer.y)), customer.size)

            # Draw collision box for customer
            debug_overlay.draw_collision_box(
                screen, customer.rect, (255, 0, 0) if not customer.served else (128, 128, 128)
            )

            if not customer.served:
                icon_name = f"{customer.drink_type.name.lower()}_icon"
                icon = self.game.assets.get_image(icon_name)
                if icon:
                    icon_rect = icon.get_rect(center=(int(customer.x), int(customer.y - 35)))
                    screen.blit(icon, icon_rect)

            if customer.dialogue and customer.dialogue_timer > 0:
                font = self.game.assets.get_font("small")
                color = COLORS["text_green"] if customer.service_successful else COLORS["text_red"]
                text = font.render(customer.dialogue, True, color)
                text_rect = text.get_rect(center=(customer.x, customer.y - 55))
                screen.blit(text, text_rect)

        for projectile in self.projectiles:
            icon_name = f"{projectile.drink_type.name.lower()}_icon"
            icon = self.game.assets.get_image(icon_name)
            if icon:
                rotated = pygame.transform.rotate(icon, projectile.angle)
                rect = rotated.get_rect(center=(int(projectile.x), int(projectile.y)))
                screen.blit(rotated, rect)

            # Draw collision box for projectile
            debug_overlay.draw_collision_box(screen, projectile.rect, (0, 255, 0))

        self.particle_system.draw(screen)

        # Draw UI
        self.draw_ui(screen)

        # Overlays
        if self.is_restocking:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            font = self.game.assets.get_font("normal")
            text = font.render("RESTOCKING...", True, COLORS["text_gold"])
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

        if self.paused:
            font = self.game.assets.get_font("normal")
            text = font.render("PAUSED", True, COLORS["text_gold"])
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

    def draw_ui(self, screen: pygame.Surface):
        """Draw the game UI using HUD."""
        if hasattr(self.game, "hud"):
            # Use the HUD system
            self.game.hud.draw_stats(screen, self.score, self.wave, self.lives)
            self.game.hud.draw_inventory(screen, self.inventory, self.selected_drink)

            # Draw wave transition if needed
            self.game.hud.draw_wave_transition(screen)

            # Draw Dev Mode indicator and controls help text
            if self.game.settings.dev_mode:
                small_font = self.game.assets.get_font("small")

                # Dev Mode indicator
                dev_text = "DEV MODE"
                dev_surface = small_font.render(dev_text, True, (255, 100, 100))
                screen.blit(dev_surface, (10, screen.get_height() - 50))

                # Wave controls help text
                debug_text = (
                    "PageUp/Down: change wave | Shift+4-9,0: jump to waves 5-40 | "
                    "F4: overlay | F6: collision boxes"
                )
                text_surface = small_font.render(debug_text, True, (150, 150, 150))
                screen.blit(text_surface, (10, screen.get_height() - 25))
        else:
            # Fallback to basic UI
            font = self.game.assets.get_font("normal")
            small_font = self.game.assets.get_font("small")

            # Score, wave, lives
            score_text = font.render(f"Score: {self.score}", True, COLORS["text_white"])
            screen.blit(score_text, (10, 10))

            wave_text = font.render(f"Wave: {self.wave}", True, COLORS["text_white"])
            screen.blit(wave_text, (10, 50))

            lives_text = font.render(f"Lives: {self.lives}", True, COLORS["text_white"])
            screen.blit(lives_text, (10, 90))

            # Inventory
            inv_y = 10
            for i, drink_type in enumerate(DrinkType):
                x = screen.get_width() - 200 + i * 60

                if drink_type == self.selected_drink:
                    pygame.draw.circle(screen, COLORS["text_gold"], (x, inv_y + 20), 25, 3)

                icon_name = f"{drink_type.name.lower()}_icon"
                icon = self.game.assets.get_image(icon_name)
                if icon:
                    screen.blit(icon, (x - 16, inv_y))

                count_text = small_font.render(
                    str(self.inventory[drink_type]), True, COLORS["text_white"]
                )
                screen.blit(count_text, (x - 5, inv_y + 35))
