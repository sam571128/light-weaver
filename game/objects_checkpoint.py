import pygame
import math
import numpy as np
from .constants import *

class Checkpoint:
    """A checkpoint that gets activated when hit by a specific color of light"""
    def __init__(self, x, y, required_color):
        self.x = x
        self.y = y
        self.size = CHECKPOINT_SIZE
        self.required_color = required_color
        self.activated = False
        self.newly_activated = False  # Flag to indicate the checkpoint was just activated
        self.is_interactive = False
        self.is_collidable = False  # Player can pass through checkpoints
        self.pulse_timer = 0
        self.pulse_rate = 0.05
        self.pulse_amplitude = 10
        
        # Create a rect for collision detection with light beams
        self.rect = pygame.Rect(
            x - self.size/2,
            y - self.size/2,
            self.size,
            self.size
        )
    
    def update(self):
        """Update checkpoint state"""
        # Update pulse effect
        self.pulse_timer += self.pulse_rate
        
        # Reset newly_activated flag after it's been processed
        if self.newly_activated:
            self.newly_activated = False
    
    def contains_point(self, point):
        """Check if this object contains the given point"""
        return self.rect.collidepoint(point)
    
    def collides_with_circle(self, circle_x, circle_y, circle_radius):
        """Check if this object collides with a circle"""
        # Since checkpoints are not collidable, we'll always return False
        return False
    
    def intersect_with_ray(self, ray_x, ray_y, ray_dir):
        """Check if a ray intersects with this checkpoint"""
        # For simplicity, we'll treat the checkpoint as a circle for ray intersection
        # Calculate the closest point on the ray to the center of the checkpoint
        center_to_ray = (self.x - ray_x, self.y - ray_y)
        ray_length = math.sqrt(ray_dir[0]**2 + ray_dir[1]**2)
        ray_normalized = (ray_dir[0] / ray_length, ray_dir[1] / ray_length)
        
        # Project center_to_ray onto the ray direction
        projection = center_to_ray[0] * ray_normalized[0] + center_to_ray[1] * ray_normalized[1]
        
        # If projection is negative, the ray is pointing away from the circle
        if projection < 0:
            return None
        
        # Calculate the closest point on the ray to the circle center
        closest_point = (ray_x + ray_normalized[0] * projection, 
                         ray_y + ray_normalized[1] * projection)
        
        # Calculate distance from closest point to circle center
        distance = math.sqrt((closest_point[0] - self.x)**2 + (closest_point[1] - self.y)**2)
        
        # If the closest point is outside the circle, no intersection
        if distance > self.size/2:
            return None
        
        # Calculate the distance from the closest point to the intersection points
        # Using Pythagorean theorem: r² = d² + x²
        half_chord = math.sqrt((self.size/2)**2 - distance**2)
        
        # Calculate the intersection point (the first one the ray hits)
        intersection = (
            closest_point[0] - ray_normalized[0] * half_chord,
            closest_point[1] - ray_normalized[1] * half_chord
        )
        
        # Check if the intersection point is in the forward direction of the ray
        if ((intersection[0] - ray_x) * ray_dir[0] + (intersection[1] - ray_y) * ray_dir[1]) < 0:
            # Try the other intersection point
            intersection = (
                closest_point[0] + ray_normalized[0] * half_chord,
                closest_point[1] + ray_normalized[1] * half_chord
            )
            
            # If still not in the forward direction, no valid intersection
            if ((intersection[0] - ray_x) * ray_dir[0] + (intersection[1] - ray_y) * ray_dir[1]) < 0:
                return None
        
        # Calculate normal at intersection point (pointing outward from center)
        normal = (
            (intersection[0] - self.x) / (self.size/2),
            (intersection[1] - self.y) / (self.size/2)
        )
        
        return (intersection[0], intersection[1], normal)
    
    def interact_with_light(self, color, hit_point, direction, normal):
        """Handle interaction with a light beam"""
        # Check if the light color matches the required color
        # We'll use a simple color matching algorithm
        # In a real game, you might want to use a more sophisticated approach
        
        # Function to check if colors are similar enough
        def colors_match(color1, color2, threshold=30):
            r_diff = abs(color1[0] - color2[0])
            g_diff = abs(color1[1] - color2[1])
            b_diff = abs(color1[2] - color2[2])
            return r_diff <= threshold and g_diff <= threshold and b_diff <= threshold
        
        if colors_match(color, self.required_color):
            if not self.activated:
                self.activated = True
                self.newly_activated = True  # Set flag for sound to be played
        
        # Light passes through the checkpoint
        return [{
            'type': 'filter',
            'direction': direction,
            'color': color,
            'intensity': 0.95  # Slight loss of intensity
        }]
    
    def render(self, screen):
        """Render the checkpoint"""
        # Calculate pulse effect
        pulse_offset = math.sin(self.pulse_timer) * self.pulse_amplitude
        current_size = self.size + pulse_offset if not self.activated else self.size
        
        # Draw the base circle
        base_color = GRAY if not self.activated else self.required_color
        pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), int(current_size/2))
        
        # Draw the required color indicator in the center
        indicator_size = current_size * 0.6
        pygame.draw.circle(screen, self.required_color, (int(self.x), int(self.y)), int(indicator_size/2))
        
        # If activated, draw a glow effect
        if self.activated:
            # Create a surface for the glow with alpha channel
            glow_radius = int(current_size * 0.8)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Draw radial gradient for glow
            for radius in range(glow_radius, 0, -1):
                alpha = int(100 * (radius / glow_radius))
                pygame.draw.circle(
                    glow_surface, 
                    (*self.required_color, alpha), 
                    (glow_radius, glow_radius), 
                    radius
                )
            
            # Blit glow surface onto screen
            screen.blit(
                glow_surface, 
                (self.x - glow_radius, self.y - glow_radius)
            )
