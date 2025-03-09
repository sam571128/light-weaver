import pygame
import math
import numpy as np
from .constants import *

class ShadowCreature:
    """A shadow creature that moves along a path and blocks light"""
    def __init__(self, x, y, path, speed):
        self.x = x
        self.y = y
        self.size = SHADOW_CREATURE_SIZE
        self.path = path  # List of points to move between
        self.speed = speed
        self.current_target = 0
        self.is_interactive = False
        self.is_collidable = True
        
        # Create a rect for collision
        self.rect = pygame.Rect(
            x - self.size/2,
            y - self.size/2,
            self.size,
            self.size
        )
        
        # Visual properties
        self.tentacle_count = 5
        self.tentacle_length = self.size * 0.6
        self.tentacle_speed = 0.1
        self.tentacle_phase = 0
        self.pulse_timer = 0
        self.pulse_rate = 0.03
    
    def update(self):
        """Update shadow creature position and animation"""
        # If we have a path to follow
        if self.path and len(self.path) > 1:
            # Get the current target point
            target_x, target_y = self.path[self.current_target]
            
            # Calculate direction to target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If we're close enough to the target, move to the next one
            if distance < self.speed:
                self.current_target = (self.current_target + 1) % len(self.path)
            else:
                # Move towards the target
                direction_x = dx / distance
                direction_y = dy / distance
                
                self.x += direction_x * self.speed
                self.y += direction_y * self.speed
        
        # Update rect position
        self.rect.x = self.x - self.size/2
        self.rect.y = self.y - self.size/2
        
        # Update animation
        self.tentacle_phase += self.tentacle_speed
        self.pulse_timer += self.pulse_rate
    
    def contains_point(self, point):
        """Check if this object contains the given point"""
        # For simplicity, use a circle check instead of the rect
        dx = point[0] - self.x
        dy = point[1] - self.y
        distance_squared = dx*dx + dy*dy
        return distance_squared <= (self.size/2)**2
    
    def collides_with_circle(self, circle_x, circle_y, circle_radius):
        """Check if this object collides with a circle"""
        # Calculate distance between centers
        dx = circle_x - self.x
        dy = circle_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # If the distance is less than the sum of radii, they collide
        return distance < (self.size/2 + circle_radius)
    
    def intersect_with_ray(self, ray_x, ray_y, ray_dir):
        """Check if a ray intersects with this shadow creature"""
        # For simplicity, we'll treat the shadow creature as a circle for ray intersection
        # Calculate the closest point on the ray to the center of the creature
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
        # Shadow creatures absorb all light
        return [{
            'type': 'absorb'
        }]
    
    def render(self, screen):
        """Render the shadow creature"""
        # Draw the main body as a dark circle with pulsing effect
        pulse = math.sin(self.pulse_timer) * 10
        body_radius = int(self.size/2 + pulse)
        
        # Create a surface for the shadow with alpha channel
        shadow_surface = pygame.Surface((body_radius * 2, body_radius * 2), pygame.SRCALPHA)
        
        # Draw radial gradient for shadow body
        for radius in range(body_radius, 0, -1):
            alpha = int(200 * (radius / body_radius))
            pygame.draw.circle(
                shadow_surface, 
                (0, 0, 0, alpha), 
                (body_radius, body_radius), 
                radius
            )
        
        # Blit shadow surface onto screen
        screen.blit(
            shadow_surface, 
            (int(self.x - body_radius), int(self.y - body_radius))
        )
        
        # Draw tentacles
        for i in range(self.tentacle_count):
            angle = (i / self.tentacle_count) * 2 * math.pi + self.tentacle_phase
            
            # Calculate tentacle end point with some wiggling
            wiggle = math.sin(self.tentacle_phase * 2 + i) * 10
            end_x = self.x + math.cos(angle) * (self.tentacle_length + wiggle)
            end_y = self.y + math.sin(angle) * (self.tentacle_length + wiggle)
            
            # Draw tentacle as a line with decreasing thickness
            for thickness in range(5, 0, -1):
                alpha = int(150 * (thickness / 5))
                pygame.draw.line(
                    screen,
                    (0, 0, 0, alpha),
                    (int(self.x), int(self.y)),
                    (int(end_x), int(end_y)),
                    thickness
                )
        
        # Draw glowing red eyes
        eye_distance = self.size / 5
        left_eye_x = self.x - eye_distance
        right_eye_x = self.x + eye_distance
        eye_y = self.y - eye_distance / 2
        
        for eye_x in [left_eye_x, right_eye_x]:
            # Draw eye glow
            glow_radius = 8
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            for radius in range(glow_radius, 0, -1):
                alpha = int(150 * (radius / glow_radius))
                pygame.draw.circle(
                    glow_surface, 
                    (255, 0, 0, alpha), 
                    (glow_radius, glow_radius), 
                    radius
                )
            
            screen.blit(
                glow_surface, 
                (int(eye_x - glow_radius), int(eye_y - glow_radius))
            )
            
            # Draw eye center
            pygame.draw.circle(screen, (255, 0, 0), (int(eye_x), int(eye_y)), 3)
