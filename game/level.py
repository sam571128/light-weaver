import pygame
from .constants import *
from .objects import Mirror, Prism
from .objects_colorfilter import ColorFilter
from .objects_checkpoint import Checkpoint
from .objects_shadowcreature import ShadowCreature

class Level:
    """A game level with player start position and objects"""
    def __init__(self, level_number, player_start_position, objects, name="", description=""):
        self.level_number = level_number
        self.player_start_position = player_start_position
        self.objects = objects  # List of object data (type, position, etc.)
        self.name = name or f"Level {level_number}"
        self.description = description
        self.completed = False
        self.best_time = float('inf')
    
    def update_best_time(self, time):
        """Update the best completion time for this level"""
        if time < self.best_time:
            self.best_time = time
            return True
        return False


class LevelManager:
    """Manages game levels and progression"""
    def __init__(self):
        self.levels = {}
        self.current_level = 1
        self.max_level_reached = 1
        self.create_levels()
    
    def create_levels(self):
        """Create all game levels"""
        # Level 1: Introduction to mirrors
        self.levels[1] = Level(
            level_number=1,
            name="First Reflections",
            description="Use the mirror to direct light to the checkpoint.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'mirror',
                    'position': (640, 360),
                    'angle': 45
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 200),
                    'required_color': WHITE
                }
            ]
        )
        
        # Level 2: Multiple mirrors
        self.levels[2] = Level(
            level_number=2,
            name="Double Bounce",
            description="Use multiple mirrors to navigate the light beam.",
            player_start_position=(200, 200),
            objects=[
                {
                    'type': 'mirror',
                    'position': (500, 200),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (500, 500),
                    'angle': 135
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 500),
                    'required_color': WHITE
                }
            ]
        )
        
        # Level 3: Introduction to prisms
        self.levels[3] = Level(
            level_number=3,
            name="Spectrum Split",
            description="Use the prism to split white light into colors.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'prism',
                    'position': (640, 360)
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 260),
                    'required_color': RED
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 360),
                    'required_color': GREEN
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 460),
                    'required_color': BLUE
                }
            ]
        )
        
        # Level 4: Introduction to color filters
        self.levels[4] = Level(
            level_number=4,
            name="Color Change",
            description="Use the color filter to change the light color.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'filter',
                    'position': (500, 360),
                    'color': RED
                },
                {
                    'type': 'mirror',
                    'position': (800, 360),
                    'angle': 45
                },
                {
                    'type': 'checkpoint',
                    'position': (800, 100),
                    'required_color': RED
                }
            ]
        )
        
        # Level 5: Introduction to shadow creatures
        self.levels[5] = Level(
            level_number=5,
            name="Shadow Dance",
            description="Avoid the shadow creatures that block your light.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'mirror',
                    'position': (500, 200),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (500, 500),
                    'angle': 135
                },
                {
                    'type': 'shadow_creature',
                    'position': (700, 360),
                    'path': [(700, 200), (700, 500)],
                    'speed': 3
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 360),
                    'required_color': WHITE
                }
            ]
        )
        
        # Level 6: Combining prisms and filters
        self.levels[6] = Level(
            level_number=6,
            name="Color Combination",
            description="Combine prisms and filters to create the right colors.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'prism',
                    'position': (400, 360)
                },
                {
                    'type': 'filter',
                    'position': (600, 260),
                    'color': RED
                },
                {
                    'type': 'filter',
                    'position': (600, 460),
                    'color': BLUE
                },
                {
                    'type': 'mirror',
                    'position': (800, 260),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (800, 460),
                    'angle': 135
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 200),
                    'required_color': RED
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 520),
                    'required_color': BLUE
                }
            ]
        )
        
        # Level 7: Complex path with multiple reflections
        self.levels[7] = Level(
            level_number=7,
            name="Reflection Maze",
            description="Navigate through a complex path of mirrors.",
            player_start_position=(100, 100),
            objects=[
                {
                    'type': 'mirror',
                    'position': (300, 100),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (300, 300),
                    'angle': 135
                },
                {
                    'type': 'mirror',
                    'position': (500, 300),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (500, 500),
                    'angle': 135
                },
                {
                    'type': 'mirror',
                    'position': (700, 500),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (700, 700),
                    'angle': 135
                },
                {
                    'type': 'checkpoint',
                    'position': (900, 700),
                    'required_color': WHITE
                }
            ]
        )
        
        # Level 8: Shadow creatures with complex movement
        self.levels[8] = Level(
            level_number=8,
            name="Shadow Patrol",
            description="Time your light beams to avoid the patrolling shadows.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'mirror',
                    'position': (500, 200),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (800, 200),
                    'angle': 135
                },
                {
                    'type': 'shadow_creature',
                    'position': (650, 300),
                    'path': [(650, 300), (650, 600), (900, 600), (900, 300)],
                    'speed': 4
                },
                {
                    'type': 'shadow_creature',
                    'position': (350, 500),
                    'path': [(350, 500), (600, 500)],
                    'speed': 5
                },
                {
                    'type': 'checkpoint',
                    'position': (800, 500),
                    'required_color': WHITE
                }
            ]
        )
        
        # Level 9: Color mixing challenge
        self.levels[9] = Level(
            level_number=9,
            name="Color Symphony",
            description="Create the right color combinations to activate all checkpoints.",
            player_start_position=(200, 360),
            objects=[
                {
                    'type': 'prism',
                    'position': (400, 360)
                },
                {
                    'type': 'filter',
                    'position': (600, 260),
                    'color': RED
                },
                {
                    'type': 'filter',
                    'position': (600, 360),
                    'color': GREEN
                },
                {
                    'type': 'filter',
                    'position': (600, 460),
                    'color': BLUE
                },
                {
                    'type': 'mirror',
                    'position': (800, 260),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (800, 360),
                    'angle': 0
                },
                {
                    'type': 'mirror',
                    'position': (800, 460),
                    'angle': 135
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 160),
                    'required_color': RED
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 360),
                    'required_color': GREEN
                },
                {
                    'type': 'checkpoint',
                    'position': (1000, 560),
                    'required_color': BLUE
                }
            ]
        )
        
        # Level 10: Final challenge
        self.levels[10] = Level(
            level_number=10,
            name="Master Weaver",
            description="Use all your skills to complete this final challenge.",
            player_start_position=(100, 360),
            objects=[
                {
                    'type': 'prism',
                    'position': (300, 360)
                },
                {
                    'type': 'mirror',
                    'position': (500, 200),
                    'angle': 45
                },
                {
                    'type': 'mirror',
                    'position': (500, 520),
                    'angle': 135
                },
                {
                    'type': 'filter',
                    'position': (700, 100),
                    'color': RED
                },
                {
                    'type': 'filter',
                    'position': (700, 620),
                    'color': BLUE
                },
                {
                    'type': 'shadow_creature',
                    'position': (600, 360),
                    'path': [(600, 200), (600, 520)],
                    'speed': 4
                },
                {
                    'type': 'shadow_creature',
                    'position': (900, 360),
                    'path': [(900, 100), (900, 620)],
                    'speed': 6
                },
                {
                    'type': 'checkpoint',
                    'position': (1100, 100),
                    'required_color': RED
                },
                {
                    'type': 'checkpoint',
                    'position': (1100, 360),
                    'required_color': GREEN
                },
                {
                    'type': 'checkpoint',
                    'position': (1100, 620),
                    'required_color': BLUE
                }
            ]
        )
    
    def get_level(self, level_number):
        """Get a specific level by number"""
        return self.levels.get(level_number)
    
    def get_current_level(self):
        """Get the current level"""
        return self.get_level(self.current_level)
    
    def advance_level(self):
        """Advance to the next level if available"""
        if self.current_level < MAX_LEVEL:
            self.current_level += 1
            if self.current_level > self.max_level_reached:
                self.max_level_reached = self.current_level
            return True
        return False
    
    def set_level(self, level_number):
        """Set the current level"""
        if 1 <= level_number <= MAX_LEVEL and level_number <= self.max_level_reached:
            self.current_level = level_number
            return True
        return False
        
    def get_max_level(self):
        """Get the highest level number available"""
        return max(self.levels.keys()) if self.levels else 0
