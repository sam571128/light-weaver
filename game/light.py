import pygame
import math
import numpy as np
from .constants import *

class LightBeam:
    def __init__(self, x, y, direction, color, parent=None, intensity=1.0, reflection_count=0):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.direction = direction
        self.color = color
        self.width = BEAM_WIDTH
        self.max_length = BEAM_MAX_LENGTH
        self.speed = BEAM_SPEED
        self.intensity = intensity
        self.parent = parent
        self.reflection_count = reflection_count
        self.child_beams = []
        self.segments = []  # List of line segments [(x1,y1,x2,y2,color,intensity)]
        self.active = True
        
        # Calculate endpoint
        self.end_x = self.x + self.direction[0] * self.max_length
        self.end_y = self.y + self.direction[1] * self.max_length
    
    def update(self, game_objects):
        """Update the light beam and handle collisions"""
        if not self.active:
            return
            
        # Clear previous segments and child beams
        self.segments = []
        for child in self.child_beams:
            child.active = False
        self.child_beams = []
        
        # Start from beam origin
        current_x, current_y = self.start_x, self.start_y
        current_dir = self.direction
        current_color = self.color
        current_intensity = self.intensity
        
        # Maximum number of reflections to prevent infinite loops
        if self.reflection_count >= MAX_REFLECTIONS:
            self.segments.append((current_x, current_y, self.end_x, self.end_y, current_color, current_intensity))
            return
            
        # Cast the beam and check for collisions
        hit_object = None
        hit_point = None
        hit_normal = None
        min_distance = float('inf')
        
        # Check collisions with all game objects
        for obj in game_objects:
            if hasattr(obj, 'intersect_with_ray'):
                intersection = obj.intersect_with_ray(current_x, current_y, current_dir)
                if intersection:
                    hit_x, hit_y, normal = intersection
                    distance = math.sqrt((hit_x - current_x)**2 + (hit_y - current_y)**2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        hit_object = obj
                        hit_point = (hit_x, hit_y)
                        hit_normal = normal
        
        # If we hit something
        if hit_object and hit_point:
            # Add segment to the hit point
            self.segments.append((current_x, current_y, hit_point[0], hit_point[1], current_color, current_intensity))
            
            # Handle different object interactions
            if hasattr(hit_object, 'interact_with_light'):
                interaction = hit_object.interact_with_light(current_color, hit_point, current_dir, hit_normal)
                
                # Process the interaction results
                for result in interaction:
                    result_type = result.get('type', 'none')
                    
                    if result_type == 'reflect':
                        # Create reflected beam
                        new_dir = result.get('direction')
                        new_color = result.get('color', current_color)
                        new_intensity = result.get('intensity', current_intensity * BEAM_FADE_RATE)
                        
                        child = LightBeam(
                            hit_point[0], hit_point[1],
                            new_dir, new_color,
                            parent=self,
                            intensity=new_intensity,
                            reflection_count=self.reflection_count + 1
                        )
                        self.child_beams.append(child)
                        child.update(game_objects)
                        
                    elif result_type == 'refract':
                        # Create refracted beam directly from the result
                        # The Prism class returns the beam parameters directly, not in a 'beams' list
                        new_dir = result.get('direction')
                        new_color = result.get('color', current_color)
                        new_intensity = result.get('intensity', current_intensity * 0.8)
                        
                        child = LightBeam(
                            hit_point[0], hit_point[1],
                            new_dir, new_color,
                            parent=self,
                            intensity=new_intensity,
                            reflection_count=self.reflection_count + 1
                        )
                        self.child_beams.append(child)
                        child.update(game_objects)
                    
                    elif result_type == 'filter':
                        # Create filtered beam (changes color)
                        new_dir = result.get('direction', current_dir)
                        new_color = result.get('color')
                        new_intensity = result.get('intensity', current_intensity * 0.9)
                        
                        child = LightBeam(
                            hit_point[0], hit_point[1],
                            new_dir, new_color,
                            parent=self,
                            intensity=new_intensity,
                            reflection_count=self.reflection_count + 1
                        )
                        self.child_beams.append(child)
                        child.update(game_objects)
                    
                    elif result_type == 'absorb':
                        # Light is absorbed, no child beams
                        pass
            else:
                # Default behavior for objects without specific light interaction
                # Simple reflection
                normal_vec = np.array(hit_normal)
                dir_vec = np.array(current_dir)
                reflected_dir = dir_vec - 2 * np.dot(dir_vec, normal_vec) * normal_vec
                reflected_dir = reflected_dir / np.linalg.norm(reflected_dir)
                
                child = LightBeam(
                    hit_point[0], hit_point[1],
                    (reflected_dir[0], reflected_dir[1]),
                    current_color,
                    parent=self,
                    intensity=current_intensity * BEAM_FADE_RATE,
                    reflection_count=self.reflection_count + 1
                )
                self.child_beams.append(child)
                child.update(game_objects)
        else:
            # No collision, beam goes to maximum length
            self.segments.append((current_x, current_y, self.end_x, self.end_y, current_color, current_intensity))
    
    def render(self, screen):
        """Render the light beam and its children"""
        if not self.active:
            return
            
        # Draw all segments
        for segment in self.segments:
            x1, y1, x2, y2, color, intensity = segment
            
            # Adjust color based on intensity
            adjusted_color = tuple(min(255, int(c * intensity)) for c in color)
            
            # Draw the beam with a glow effect
            for width in range(self.width, 0, -1):
                alpha = int(255 * (width / self.width) * intensity)
                glow_color = (*adjusted_color, alpha)
                pygame.draw.line(screen, glow_color, (int(x1), int(y1)), (int(x2), int(y2)), width)
        
        # Render child beams
        for child in self.child_beams:
            child.render(screen)
    
    @staticmethod
    def mix_colors(color1, color2, ratio=0.5):
        """Mix two RGB colors"""
        r = int(color1[0] * ratio + color2[0] * (1 - ratio))
        g = int(color1[1] * ratio + color2[1] * (1 - ratio))
        b = int(color1[2] * ratio + color2[2] * (1 - ratio))
        return (r, g, b)
