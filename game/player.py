import pygame
import math
from .constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.color = PLAYER_COLOR
        self.glow_color = PLAYER_GLOW_COLOR
        self.glow_radius = PLAYER_GLOW_RADIUS
        self.speed = PLAYER_SPEED
        self.pulse_timer = 0
        self.pulse_rate = 0.05
        self.pulse_amplitude = 5
    
    def update(self, keys, game_objects):
        """Update player position based on keyboard input"""
        dx, dy = 0, 0
        
        # Handle keyboard input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071
        
        # Check for collisions with game objects
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.is_valid_position(new_x, new_y, game_objects):
            self.x = new_x
            self.y = new_y
        elif self.is_valid_position(new_x, self.y, game_objects):
            self.x = new_x
        elif self.is_valid_position(self.x, new_y, game_objects):
            self.y = new_y
        
        # Update pulse effect
        self.pulse_timer += self.pulse_rate
        
    def is_valid_position(self, x, y, game_objects):
        """Check if the position is valid (no collisions with objects)"""
        # Check screen boundaries
        if (x - self.radius < 0 or x + self.radius > SCREEN_WIDTH or
            y - self.radius < 0 or y + self.radius > SCREEN_HEIGHT):
            return False
        
        # Check collisions with game objects
        for obj in game_objects:
            if hasattr(obj, 'is_collidable') and obj.is_collidable:
                if obj.collides_with_circle(x, y, self.radius):
                    return False
        
        return True
    
    def render(self, screen):
        """Render the player"""
        # Draw glow effect
        pulse_offset = math.sin(self.pulse_timer) * self.pulse_amplitude
        current_glow_radius = self.glow_radius + pulse_offset
        
        # Create a surface for the glow with alpha channel
        glow_surface = pygame.Surface((current_glow_radius * 2, current_glow_radius * 2), pygame.SRCALPHA)
        
        # Draw radial gradient for glow
        for radius in range(int(current_glow_radius), 0, -1):
            alpha = int(100 * (radius / current_glow_radius))
            pygame.draw.circle(
                glow_surface, 
                (*self.glow_color, alpha), 
                (current_glow_radius, current_glow_radius), 
                radius
            )
        
        # Blit glow surface onto screen
        screen.blit(
            glow_surface, 
            (self.x - current_glow_radius, self.y - current_glow_radius)
        )
        
        # Draw player circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw highlight
        highlight_pos = (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3))
        highlight_radius = int(self.radius * 0.4)
        pygame.draw.circle(screen, WHITE, highlight_pos, highlight_radius)
