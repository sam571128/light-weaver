import pygame
import math
from .constants import *

class Button:
    """A UI button that can be clicked"""
    def __init__(self, x, y, width, height, text, action=None, color=GRAY, hover_color=WHITE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE)
    
    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def render(self, screen):
        """Render the button"""
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Border
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events on the button"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False


class UI:
    """Handles all UI elements and rendering"""
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE)
        self.title_font = pygame.font.SysFont(UI_FONT, UI_FONT_SIZE * 2)
        self.buttons = []
        self.setup_menu_buttons()
    
    def setup_menu_buttons(self):
        """Set up buttons for the main menu"""
        button_width, button_height = UI_BUTTON_SIZE
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Start game button
        start_button = Button(
            center_x,
            SCREEN_HEIGHT // 2,
            button_width,
            button_height,
            "Start Game",
            action=self.game.start_game,
            color=(50, 100, 50),
            hover_color=(70, 150, 70)
        )
        
        # Level select button
        level_button = Button(
            center_x,
            SCREEN_HEIGHT // 2 + button_height + UI_PADDING,
            button_width,
            button_height,
            "Level Select",
            action=self.show_level_select,
            color=(50, 50, 100),
            hover_color=(70, 70, 150)
        )
        
        # Quit button
        quit_button = Button(
            center_x,
            SCREEN_HEIGHT // 2 + (button_height + UI_PADDING) * 2,
            button_width,
            button_height,
            "Quit",
            action=pygame.quit,
            color=(100, 50, 50),
            hover_color=(150, 70, 70)
        )
        
        self.menu_buttons = [start_button, level_button, quit_button]
    
    def setup_pause_buttons(self):
        """Set up buttons for the pause menu"""
        button_width, button_height = UI_BUTTON_SIZE
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Resume button
        resume_button = Button(
            center_x,
            SCREEN_HEIGHT // 2,
            button_width,
            button_height,
            "Resume",
            action=self.resume_game,
            color=(50, 100, 50),
            hover_color=(70, 150, 70)
        )
        
        # Restart level button
        restart_button = Button(
            center_x,
            SCREEN_HEIGHT // 2 + button_height + UI_PADDING,
            button_width,
            button_height,
            "Restart Level",
            action=self.restart_level,
            color=(50, 50, 100),
            hover_color=(70, 70, 150)
        )
        
        # Main menu button
        menu_button = Button(
            center_x,
            SCREEN_HEIGHT // 2 + (button_height + UI_PADDING) * 2,
            button_width,
            button_height,
            "Main Menu",
            action=self.return_to_menu,
            color=(100, 50, 50),
            hover_color=(150, 70, 70)
        )
        
        self.pause_buttons = [resume_button, restart_button, menu_button]
    
    def setup_level_select_buttons(self):
        """Set up buttons for the level select screen"""
        button_width, button_height = UI_BUTTON_SIZE[0] // 2, UI_BUTTON_SIZE[1]
        buttons_per_row = 5
        start_x = SCREEN_WIDTH // 2 - (button_width * buttons_per_row + UI_PADDING * (buttons_per_row - 1)) // 2
        start_y = SCREEN_HEIGHT // 3
        
        self.level_buttons = []
        
        # Create a button for each level
        for level_num in range(1, MAX_LEVEL + 1):
            row = (level_num - 1) // buttons_per_row
            col = (level_num - 1) % buttons_per_row
            
            x = start_x + col * (button_width + UI_PADDING)
            y = start_y + row * (button_height + UI_PADDING)
            
            # Only enable buttons for levels that have been reached
            enabled = level_num <= self.game.level_manager.max_level_reached
            color = (50, 100, 50) if enabled else (30, 30, 30)
            hover_color = (70, 150, 70) if enabled else (30, 30, 30)
            
            button = Button(
                x,
                y,
                button_width,
                button_height,
                str(level_num),
                action=lambda ln=level_num: self.select_level(ln) if ln <= self.game.level_manager.max_level_reached else None,
                color=color,
                hover_color=hover_color
            )
            
            self.level_buttons.append(button)
        
        # Back button
        back_button = Button(
            SCREEN_WIDTH // 2 - button_width,
            SCREEN_HEIGHT - button_height - UI_PADDING * 2,
            button_width * 2,
            button_height,
            "Back",
            action=self.return_to_menu,
            color=(100, 50, 50),
            hover_color=(150, 70, 70)
        )
        
        self.level_buttons.append(back_button)
    
    def show_level_select(self):
        """Show the level select screen"""
        self.setup_level_select_buttons()
        self.game.state = "level_select"
    
    def select_level(self, level_number):
        """Select a level and start the game"""
        if self.game.level_manager.set_level(level_number):
            self.game.load_level(level_number)
            self.game.state = "playing"
    
    def resume_game(self):
        """Resume the game from pause"""
        self.game.state = "playing"
    
    def restart_level(self):
        """Restart the current level"""
        current_level = self.game.current_level.level_number
        self.game.load_level(current_level)
        self.game.state = "playing"
    
    def return_to_menu(self):
        """Return to the main menu"""
        self.game.state = "menu"
    
    def handle_event(self, event):
        """Handle UI events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game.state == "menu":
            for button in self.menu_buttons:
                button.update(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.handle_event(event):
                        self.game.audio_manager.play_sound('button_click')
                        return
        
        elif self.game.state == "paused":
            for button in self.pause_buttons:
                button.update(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.handle_event(event):
                        self.game.audio_manager.play_sound('button_click')
                        return
        
        elif self.game.state == "level_select":
            for button in self.level_buttons:
                button.update(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button.handle_event(event):
                        self.game.audio_manager.play_sound('button_click')
                        return
    
    def render_menu(self):
        """Render the main menu"""
        # Draw title
        title_text = self.title_font.render("Light Weaver", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font.render("A Puzzle Game of Light and Reflection", True, (200, 200, 255))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 50))
        self.game.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.menu_buttons:
            button.render(self.game.screen)
        
        # Draw version info
        version_text = self.font.render("v1.0", True, GRAY)
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - UI_PADDING, SCREEN_HEIGHT - UI_PADDING))
        self.game.screen.blit(version_text, version_rect)
    
    def render_pause_menu(self):
        """Render the pause menu"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("Paused", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.game.screen.blit(title_text, title_rect)
        
        # Make sure pause buttons are set up
        if not hasattr(self, 'pause_buttons'):
            self.setup_pause_buttons()
        
        # Draw buttons
        for button in self.pause_buttons:
            button.render(self.game.screen)
    
    def render_level_select(self):
        """Render the level select screen"""
        # Draw title
        title_text = self.title_font.render("Select Level", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6))
        self.game.screen.blit(title_text, title_rect)
        
        # Make sure level select buttons are set up
        if not hasattr(self, 'level_buttons'):
            self.setup_level_select_buttons()
        
        # Draw buttons
        for button in self.level_buttons:
            button.render(self.game.screen)
    
    def render_level_complete(self):
        """Render the level complete screen with visual effects"""
        # Get the current time for animations
        current_time = pygame.time.get_ticks()
        pulse_factor = (math.sin(current_time / 200) + 1) / 2  # Oscillates between 0 and 1
        
        # Draw semi-transparent overlay with pulsing effect
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(overlay, (0, 0))
        
        # Draw radial glow effect
        glow_radius = 300 + int(pulse_factor * 50)  # Pulsing radius
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        
        # Create a radial gradient for the glow
        for radius in range(glow_radius, 0, -2):
            alpha = int(100 * (radius / glow_radius) * (1 - radius / glow_radius))
            color = (100 + int(pulse_factor * 155), 255, 100, alpha)
            pygame.draw.circle(
                glow_surface, 
                color, 
                (glow_radius, glow_radius), 
                radius
            )
        
        # Position the glow in the center of the screen
        self.game.screen.blit(
            glow_surface, 
            (SCREEN_WIDTH // 2 - glow_radius, SCREEN_HEIGHT // 3 - glow_radius)
        )
        
        # Draw title with pulsing effect
        title_scale = 1.0 + pulse_factor * 0.1  # Scale between 1.0 and 1.1
        title_color = (100 + int(pulse_factor * 155), 255, 100)  # Pulse from green to bright green
        title_text = self.title_font.render("Level Complete!", True, title_color)
        title_text = pygame.transform.scale(title_text, 
                                           (int(title_text.get_width() * title_scale), 
                                            int(title_text.get_height() * title_scale)))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw level info
        level_text = self.font.render(f"Level {self.game.current_level.level_number}: {self.game.current_level.name}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 80))
        self.game.screen.blit(level_text, level_rect)
        
        # Draw level description
        desc_text = self.font.render(self.game.current_level.description, True, (200, 200, 255))
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 120))
        self.game.screen.blit(desc_text, desc_rect)
        
        # Draw "Press any key to continue" text with blinking effect
        if (current_time // 500) % 2 == 0:  # Blink every 500ms
            continue_text = self.font.render("Press any key to continue", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 180))
            self.game.screen.blit(continue_text, continue_rect)
    
    def render_game_over(self):
        """Render the game over screen with visual effects"""
        # Get the current time for animations
        current_time = pygame.time.get_ticks()
        pulse_factor = (math.sin(current_time / 300) + 1) / 2  # Oscillates between 0 and 1
        
        # Draw starry background with moving stars
        self.game.screen.fill(BLACK)  # Start with a black background
        
        # Draw twinkling stars
        for i in range(100):  # Draw 100 stars
            # Use time to create twinkling effect and movement
            x = (SCREEN_WIDTH * (i / 100) + current_time / 50) % SCREEN_WIDTH
            y = (SCREEN_HEIGHT * ((i * i) % 100) / 100 + current_time / 100) % SCREEN_HEIGHT
            
            # Vary star brightness based on time
            brightness = 100 + int(155 * ((math.sin(current_time / 200 + i) + 1) / 2))
            size = 1 + int(2 * ((math.sin(current_time / 300 + i) + 1) / 2))
            
            pygame.draw.circle(self.game.screen, (brightness, brightness, brightness), (int(x), int(y)), size)
        
        # Draw golden glow effect
        glow_radius = 350 + int(pulse_factor * 50)  # Pulsing radius
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        
        # Create a radial gradient for the glow
        for radius in range(glow_radius, 0, -2):
            alpha = int(80 * (radius / glow_radius) * (1 - radius / glow_radius))
            color = (255, 255, 100 + int(pulse_factor * 155), alpha)  # Golden glow
            pygame.draw.circle(
                glow_surface, 
                color, 
                (glow_radius, glow_radius), 
                radius
            )
        
        # Position the glow in the center of the screen
        self.game.screen.blit(
            glow_surface, 
            (SCREEN_WIDTH // 2 - glow_radius, SCREEN_HEIGHT // 3 - glow_radius)
        )
        
        # Draw title with pulsing effect
        title_scale = 1.0 + pulse_factor * 0.15  # Scale between 1.0 and 1.15
        title_color = (255, 255, 100 + int(pulse_factor * 155))  # Pulse from gold to bright gold
        title_text = self.title_font.render("Congratulations!", True, title_color)
        title_text = pygame.transform.scale(title_text, 
                                           (int(title_text.get_width() * title_scale), 
                                            int(title_text.get_height() * title_scale)))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw completion message with subtle animation
        y_offset = int(math.sin(current_time / 400) * 5)  # Subtle floating effect
        complete_text = self.font.render("You have mastered the Light Weaver!", True, WHITE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 80 + y_offset))
        self.game.screen.blit(complete_text, complete_rect)
        
        # Draw additional congratulatory text
        congrats_text = self.font.render("You have completed all levels and become a true Light Weaver.", True, (200, 200, 255))
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 120 + y_offset))
        self.game.screen.blit(congrats_text, congrats_rect)
        
        # Draw "Press any key to return to menu" text with blinking effect
        if (current_time // 500) % 2 == 0:  # Blink every 500ms
            menu_text = self.font.render("Press any key to return to menu", True, WHITE)
            menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 180))
            self.game.screen.blit(menu_text, menu_rect)
    
    def render_hud(self):
        """Render the in-game HUD"""
        # Draw level info
        level_text = self.font.render(f"Level {self.game.current_level.level_number}: {self.game.current_level.name}", True, WHITE)
        self.game.screen.blit(level_text, (UI_PADDING, UI_PADDING))
        
        # Draw level description
        desc_text = self.font.render(self.game.current_level.description, True, (200, 200, 200))
        self.game.screen.blit(desc_text, (UI_PADDING, UI_PADDING + UI_FONT_SIZE + 5))
        
        # Draw controls reminder
        controls_text = self.font.render("WASD: Move | Mouse: Aim | Space: Toggle Beam | R: Reset | ESC: Pause", True, GRAY)
        controls_rect = controls_text.get_rect(bottom=SCREEN_HEIGHT - UI_PADDING)
        self.game.screen.blit(controls_text, (UI_PADDING, controls_rect.y))
