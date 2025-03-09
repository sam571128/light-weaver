import pygame
import math
import numpy as np
from .constants import *

class GameObject:
    """Base class for all game objects"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_collidable = True
        self.is_interactive = False
        self.rect = pygame.Rect(x, y, 0, 0)  # Will be updated by subclasses
    
    def update(self):
        """Update object state"""
        pass
    
    def render(self, screen):
        """Render the object"""
        pass
    
    def interact(self):
        """Handle interaction with the object"""
        pass
    
    def collides_with_circle(self, circle_x, circle_y, circle_radius):
        """Check if this object collides with a circle"""
        # Default implementation using rect
        # Find the closest point on the rect to the circle
        closest_x = max(self.rect.left, min(circle_x, self.rect.right))
        closest_y = max(self.rect.top, min(circle_y, self.rect.bottom))
        
        # Calculate the distance between the circle's center and the closest point
        distance_x = circle_x - closest_x
        distance_y = circle_y - closest_y
        distance_squared = distance_x**2 + distance_y**2
        
        # If the distance is less than the circle's radius, they collide
        return distance_squared < (circle_radius**2)
    
    def contains_point(self, point):
        """Check if this object contains the given point"""
        return self.rect.collidepoint(point)


class Mirror(GameObject):
    """A mirror that reflects light beams"""
    def __init__(self, x, y, angle=45):
        super().__init__(x, y)
        self.width = MIRROR_WIDTH
        self.height = MIRROR_HEIGHT
        self.angle = angle  # in degrees
        self.is_interactive = True
        self.rotation_speed = 5  # degrees per interaction
        self.update_rect()
    
    def update_rect(self):
        """Update the rectangle based on position and angle"""
        # Create a rect centered at (x, y)
        self.rect = pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
        
        # We'll use this for rendering and collision detection
        # Calculate the endpoints of the mirror line
        radians = math.radians(self.angle)
        half_width = self.width / 2
        
        self.start_point = (
            self.x - half_width * math.cos(radians),
            self.y - half_width * math.sin(radians)
        )
        
        self.end_point = (
            self.x + half_width * math.cos(radians),
            self.y + half_width * math.sin(radians)
        )
        
        # Calculate normal vector (perpendicular to mirror surface)
        self.normal = (
            math.cos(radians + math.pi/2),
            math.sin(radians + math.pi/2)
        )
    
    def interact(self):
        """Rotate the mirror when interacted with"""
        self.angle = (self.angle + self.rotation_speed) % 360
        self.update_rect()
    
    def intersect_with_ray(self, ray_x, ray_y, ray_dir):
        """Check if a ray intersects with this mirror"""
        # Line segment intersection algorithm
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        # Ray is from (ray_x, ray_y) in direction ray_dir
        x3, y3 = ray_x, ray_y
        x4, y4 = ray_x + ray_dir[0] * BEAM_MAX_LENGTH, ray_y + ray_dir[1] * BEAM_MAX_LENGTH
        
        # Calculate denominator
        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        
        # Lines are parallel if denominator is zero
        if den == 0:
            return None
        
        # Calculate parameters for intersection point
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        
        # Check if intersection is within both line segments
        if 0 <= ua <= 1 and ub > 0:
            # Calculate intersection point
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            
            # Return intersection point and normal
            return (x, y, self.normal)
        
        return None
    
    def interact_with_light(self, color, hit_point, direction, normal):
        """Handle interaction with a light beam"""
        # Calculate reflection
        dir_vec = np.array(direction)
        normal_vec = np.array(normal)
        
        # Reflection formula: r = d - 2(d·n)n
        reflected_dir = dir_vec - 2 * np.dot(dir_vec, normal_vec) * normal_vec
        reflected_dir = reflected_dir / np.linalg.norm(reflected_dir)
        
        return [{
            'type': 'reflect',
            'direction': (reflected_dir[0], reflected_dir[1]),
            'color': color,
            'intensity': 0.95  # Slight loss of intensity on reflection
        }]
    
    def render(self, screen):
        """Render the mirror"""
        # Draw the mirror line
        pygame.draw.line(
            screen,
            WHITE,
            (int(self.start_point[0]), int(self.start_point[1])),
            (int(self.end_point[0]), int(self.end_point[1])),
            self.height
        )
        
        # Draw a small circle at the center to indicate it's interactive
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), 5)
        
        # Draw a line indicating the normal direction (for debugging)
        # normal_length = 20
        # pygame.draw.line(
        #     screen,
        #     RED,
        #     (int(self.x), int(self.y)),
        #     (int(self.x + self.normal[0] * normal_length), int(self.y + self.normal[1] * normal_length)),
        #     2
        # )


class Prism(GameObject):
    """A prism that splits white light into component colors"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = PRISM_SIZE
        self.is_interactive = False
        
        # Create a triangular prism
        self.points = [
            (x, y - self.size/2),  # Top
            (x - self.size/2, y + self.size/2),  # Bottom left
            (x + self.size/2, y + self.size/2)   # Bottom right
        ]
        
        # Create a rect for basic collision
        self.rect = pygame.Rect(
            x - self.size/2,
            y - self.size/2,
            self.size,
            self.size
        )
        
        # Define the three sides of the triangle for ray intersection
        self.sides = [
            (self.points[0], self.points[1]),  # Top to bottom left
            (self.points[1], self.points[2]),  # Bottom left to bottom right
            (self.points[2], self.points[0])   # Bottom right to top
        ]
        
        # Calculate normals for each side (pointing outward)
        self.normals = []
        for i in range(3):
            p1, p2 = self.sides[i]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx*dx + dy*dy)
            # Normal is perpendicular to the side (rotate 90 degrees)
            nx = -dy / length
            ny = dx / length
            
            # Make sure normal points outward
            center_to_normal = (nx * (self.x - p1[0]) + ny * (self.y - p1[1]))
            if center_to_normal > 0:
                nx, ny = -nx, -ny
                
            self.normals.append((nx, ny))
    
    def intersect_with_ray(self, ray_x, ray_y, ray_dir):
        """Check if a ray intersects with this prism"""
        closest_intersection = None
        closest_distance = float('inf')
        closest_normal = None
        
        # Check intersection with each side
        for i, ((x1, y1), (x2, y2)) in enumerate(self.sides):
            # Line segment intersection algorithm
            x3, y3 = ray_x, ray_y
            x4, y4 = ray_x + ray_dir[0] * BEAM_MAX_LENGTH, ray_y + ray_dir[1] * BEAM_MAX_LENGTH
            
            # Calculate denominator
            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            
            # Lines are parallel if denominator is zero
            if den == 0:
                continue
            
            # Calculate parameters for intersection point
            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
            
            # Check if intersection is within both line segments
            if 0 <= ua <= 1 and ub > 0:
                # Calculate intersection point
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                
                # Calculate distance
                distance = math.sqrt((x - ray_x)**2 + (y - ray_y)**2)
                
                # Keep track of closest intersection
                if distance < closest_distance:
                    closest_distance = distance
                    closest_intersection = (x, y)
                    closest_normal = self.normals[i]
        
        if closest_intersection:
            return (closest_intersection[0], closest_intersection[1], closest_normal)
        
        return None
        
    def interact_with_light(self, color, hit_point, direction, normal):
        """Handle interaction with a light beam - split white light into component colors"""
        # Only split white light
        if color == WHITE:
            # Calculate refraction angle - simplified for game purposes
            dir_vec = np.array(direction)
            normal_vec = np.array(normal)
            
            # Dot product to determine if light is entering or exiting the prism
            dot_product = np.dot(dir_vec, normal_vec)
            is_entering = dot_product < 0
            
            # For simplicity, we'll create three beams with slightly different angles
            # representing the RGB components of white light
            result = []
            
            if is_entering:
                # Create refracted beams with different angles for each color
                # Red beam - least refraction
                red_angle = math.atan2(direction[1], direction[0]) + 0.1
                red_dir = (math.cos(red_angle), math.sin(red_angle))
                result.append({
                    'type': 'refract',
                    'direction': red_dir,
                    'color': RED,
                    'intensity': 0.9
                })
                
                # Green beam - medium refraction
                green_angle = math.atan2(direction[1], direction[0])
                green_dir = (math.cos(green_angle), math.sin(green_angle))
                result.append({
                    'type': 'refract',
                    'direction': green_dir,
                    'color': GREEN,
                    'intensity': 0.9
                })
                
                # Blue beam - most refraction
                blue_angle = math.atan2(direction[1], direction[0]) - 0.1
                blue_dir = (math.cos(blue_angle), math.sin(blue_angle))
                result.append({
                    'type': 'refract',
                    'direction': blue_dir,
                    'color': BLUE,
                    'intensity': 0.9
                })
                
                return result
            else:
                # If exiting, just continue with slight refraction
                refracted_angle = math.atan2(direction[1], direction[0])
                refracted_dir = (math.cos(refracted_angle), math.sin(refracted_angle))
                return [{
                    'type': 'refract',
                    'direction': refracted_dir,
                    'color': color,
                    'intensity': 0.95
                }]
        else:
            # For colored light, just refract slightly
            refracted_angle = math.atan2(direction[1], direction[0])
            refracted_dir = (math.cos(refracted_angle), math.sin(refracted_angle))
            return [{
                'type': 'refract',
                'direction': refracted_dir,
                'color': color,
                'intensity': 0.95
            }]
    
    def render(self, screen):
        """Render the prism with a translucent rainbow effect"""
        # Draw the triangular prism outline
        pygame.draw.polygon(screen, WHITE, self.points, 2)
        
        # Create a translucent surface for the rainbow effect
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Calculate the center of the triangle
        center_x = sum(p[0] for p in self.points) / 3
        center_y = sum(p[1] for p in self.points) / 3
        
        # Draw rainbow gradient inside the prism
        colors = [
            (255, 0, 0, 100),    # Red (translucent)
            (255, 127, 0, 100),  # Orange (translucent)
            (255, 255, 0, 100),  # Yellow (translucent)
            (0, 255, 0, 100),    # Green (translucent)
            (0, 0, 255, 100),    # Blue (translucent)
            (75, 0, 130, 100),   # Indigo (translucent)
            (148, 0, 211, 100)   # Violet (translucent)
        ]
        
        # Draw rainbow layers from inside out
        for i, color in enumerate(colors):
            # Scale factor decreases with each layer to create gradient effect
            scale = 1.0 - (i / len(colors)) * 0.7
            
            # Scale the triangle points around the center
            scaled_points = []
            for p in self.points:
                # Vector from center to point
                dx = p[0] - center_x
                dy = p[1] - center_y
                
                # Scale the vector
                scaled_x = center_x + dx * scale
                scaled_y = center_y + dy * scale
                
                scaled_points.append((scaled_x, scaled_y))
            
            # Draw the scaled, colored triangle
            pygame.draw.polygon(surface, color, scaled_points, 0)
        
        # Draw the surface on the screen at the prism position
        screen.blit(surface, (self.x - self.size/2, self.y - self.size/2))
        
        # Draw a small highlight to indicate it's a prism
        pygame.draw.circle(screen, (255, 255, 255, 180), (int(self.points[0][0]), int(self.points[0][1])), 3)
