import pygame
import math
import numpy as np
from .constants import *

class ColorFilter:
    """A filter that changes the color of light passing through it"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = FILTER_SIZE
        self.color = color
        self.is_interactive = True
        self.is_collidable = True
        self.available_colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE]
        self.color_index = self.available_colors.index(color) if color in self.available_colors else 0
        
        # Create a rect for collision
        self.rect = pygame.Rect(
            x - self.size/2,
            y - self.size/2,
            self.size,
            self.size
        )
    
    def update(self):
        """Update object state"""
        pass
    
    def interact(self):
        """Cycle through available colors when interacted with"""
        self.color_index = (self.color_index + 1) % len(self.available_colors)
        self.color = self.available_colors[self.color_index]
    
    def contains_point(self, point):
        """Check if this object contains the given point"""
        return self.rect.collidepoint(point)
    
    def collides_with_circle(self, circle_x, circle_y, circle_radius):
        """Check if this object collides with a circle"""
        # Find the closest point on the rect to the circle
        closest_x = max(self.rect.left, min(circle_x, self.rect.right))
        closest_y = max(self.rect.top, min(circle_y, self.rect.bottom))
        
        # Calculate the distance between the circle's center and the closest point
        distance_x = circle_x - closest_x
        distance_y = circle_y - closest_y
        distance_squared = distance_x**2 + distance_y**2
        
        # If the distance is less than the circle's radius, they collide
        return distance_squared < (circle_radius**2)
    
    def intersect_with_ray(self, ray_x, ray_y, ray_dir):
        """Check if a ray intersects with this filter"""
        # For simplicity, we'll treat the filter as a circle for ray intersection
        # Calculate the closest point on the ray to the center of the filter
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
        # Filter the light based on the filter color
        if self.color == WHITE:
            # White filter lets all colors pass through
            filtered_color = color
        elif color == WHITE:
            # White light takes the filter's color
            filtered_color = self.color
        else:
            # Color mixing - simplified version
            # In reality, this would involve more complex color theory
            if self.color == RED:
                if color == BLUE:
                    filtered_color = MAGENTA
                elif color == GREEN:
                    filtered_color = YELLOW
                else:
                    filtered_color = self.color
            elif self.color == GREEN:
                if color == BLUE:
                    filtered_color = CYAN
                elif color == RED:
                    filtered_color = YELLOW
                else:
                    filtered_color = self.color
            elif self.color == BLUE:
                if color == RED:
                    filtered_color = MAGENTA
                elif color == GREEN:
                    filtered_color = CYAN
                else:
                    filtered_color = self.color
            else:
                # For secondary colors, use a simple approach
                r = min(color[0], self.color[0])
                g = min(color[1], self.color[1])
                b = min(color[2], self.color[2])
                filtered_color = (r, g, b)
        
        return [{
            'type': 'filter',
            'direction': direction,  # Direction doesn't change
            'color': filtered_color,
            'intensity': 0.9  # Slight loss of intensity
        }]
    
    def render(self, screen):
        """Render the color filter"""
        # Draw the filter as a semi-transparent colored square
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, 150), (0, 0, self.size, self.size))
        screen.blit(s, (self.x - self.size/2, self.y - self.size/2))
        
        # Draw border
        pygame.draw.rect(
            screen, 
            WHITE, 
            (self.x - self.size/2, self.y - self.size/2, self.size, self.size), 
            2
        )
