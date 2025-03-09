import pygame
import sys
import time
from .constants import *
from .player import Player
from .light import LightBeam
from .objects import Mirror, Prism
from .objects_colorfilter import ColorFilter
from .objects_checkpoint import Checkpoint
from .objects_shadowcreature import ShadowCreature
from .level import Level, LevelManager
from .ui import UI
from .audio import AudioManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(BLACK)
        
        # Game state
        self.state = "menu"  # menu, playing, paused, level_complete, game_over
        
        # Create audio manager
        self.audio_manager = AudioManager()
        
        # Create UI
        self.ui = UI(self)
        
        # Create level manager
        self.level_manager = LevelManager()
        self.current_level = None
        
        # Game objects
        self.player = None
        self.light_beams = []
        self.game_objects = []
        
        # Load assets
        self.load_assets()
        
        # Initialize menu
        self.setup_menu()
        
        # Start menu music
        self.audio_manager.play_music('menu')
    
    def load_assets(self):
        """Load game assets (images, sounds, etc.)"""
        # TODO: Load images, etc.
        # Example:
        # self.images = {
        #     'player': pygame.image.load('assets/player.png').convert_alpha(),
        #     'mirror': pygame.image.load('assets/mirror.png').convert_alpha(),
        # }
        
        # Sound effects are handled by the AudioManager
        pass
    
    def setup_menu(self):
        """Set up the main menu"""
        # Menu setup will be handled by the UI class
        pass
    
    def start_game(self):
        """Start a new game"""
        self.state = "playing"
        self.load_level(1)
        
        # Switch to gameplay music with a smooth fade
        self.audio_manager.fade_music('gameplay')
    
    def load_level(self, level_number):
        """Load a specific level"""
        self.current_level = self.level_manager.get_level(level_number)
        
        # Clear existing objects
        self.game_objects = []
        self.light_beams = []
        
        # Create player
        player_pos = self.current_level.player_start_position
        self.player = Player(player_pos[0], player_pos[1])
        
        # Create level objects
        for obj_data in self.current_level.objects:
            obj_type = obj_data['type']
            x, y = obj_data['position']
            
            if obj_type == 'mirror':
                angle = obj_data.get('angle', 45)
                self.game_objects.append(Mirror(x, y, angle))
            elif obj_type == 'prism':
                self.game_objects.append(Prism(x, y))
            elif obj_type == 'filter':
                color = obj_data.get('color', RED)
                self.game_objects.append(ColorFilter(x, y, color))
            elif obj_type == 'checkpoint':
                required_color = obj_data.get('required_color', WHITE)
                self.game_objects.append(Checkpoint(x, y, required_color))
            elif obj_type == 'shadow_creature':
                path = obj_data.get('path', [])
                speed = obj_data.get('speed', 2)
                self.game_objects.append(ShadowCreature(x, y, path, speed))
    
    def handle_event(self, event):
        """Handle pygame events"""
        if self.state == "menu" or self.state == "level_select":
            self.ui.handle_event(event)
            return
        
        if self.state == "level_complete":
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Skip to next level on any key/click during level complete screen
                self.check_level_transition()
            return
            
        if self.state == "game_over":
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Return to menu on any key/click during game over screen
                self.state = "menu"
                self.audio_manager.fade_music('menu')
            return
            
        if self.state == "paused":
            self.ui.handle_event(event)
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "playing":
                    self.state = "paused"
                    self.audio_manager.pause_music()
                elif self.state == "paused":
                    self.state = "playing"
                    self.audio_manager.unpause_music()
            
            if event.key == pygame.K_r:
                # Reset level
                self.load_level(self.current_level.level_number)
            
            if event.key == pygame.K_SPACE:
                # Toggle light beam
                if not self.light_beams:
                    self.create_light_beam()
                    self.audio_manager.play_sound('beam_on')
                else:
                    self.light_beams = []
                    self.audio_manager.play_sound('beam_off')
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Interact with objects
                mouse_pos = pygame.mouse.get_pos()
                self.interact_with_objects(mouse_pos)
    
    def create_light_beam(self):
        """Create a light beam from the player"""
        mouse_pos = pygame.mouse.get_pos()
        direction = (mouse_pos[0] - self.player.x, mouse_pos[1] - self.player.y)
        
        # Normalize direction
        length = (direction[0]**2 + direction[1]**2)**0.5
        if length > 0:
            direction = (direction[0]/length, direction[1]/length)
        
        # Create beam
        beam = LightBeam(self.player.x, self.player.y, direction, WHITE)
        self.light_beams.append(beam)
        
        # Play beam creation sound with appropriate context
        self.audio_manager.play_sound_with_context('beam_on', 'beam')
    
    def interact_with_objects(self, mouse_pos):
        """Interact with game objects at the given position"""
        for obj in self.game_objects:
            if hasattr(obj, 'contains_point') and obj.contains_point(mouse_pos):
                if hasattr(obj, 'interact'):
                    obj.interact()
                    
                    # Get object position for spatial audio
                    obj_pos = (obj.x, obj.y)
                    player_pos = (self.player.x, self.player.y)
                    
                    # Play appropriate sound based on object type with spatial positioning
                    if isinstance(obj, Mirror):
                        self.audio_manager.play_spatial_sound('mirror_rotate', obj_pos, player_pos)
                    elif isinstance(obj, ColorFilter):
                        self.audio_manager.play_spatial_sound('filter_change', obj_pos, player_pos)
                    elif isinstance(obj, Prism):
                        self.audio_manager.play_spatial_sound('beam_split', obj_pos, player_pos)
                break
    
    def update(self):
        """Update game state"""
        if self.state != "playing":
            return
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.game_objects)
        
        # Update light beams
        for beam in self.light_beams:
            beam.update(self.game_objects)
        
        # Update game objects
        for obj in self.game_objects:
            obj.update()
        
        # Check for level completion
        if self.check_level_complete():
            self.state = "level_complete"
            # self.sounds['level_complete'].play()
            
            # Load next level after delay
            # In a real game, you'd use a timer here
            next_level = self.current_level.level_number + 1
            if next_level <= MAX_LEVEL:
                self.load_level(next_level)
            else:
                self.state = "game_over"
    
    def check_level_complete(self):
        """Check if all checkpoints are activated"""
        checkpoints = [obj for obj in self.game_objects if isinstance(obj, Checkpoint)]
        return all(checkpoint.activated for checkpoint in checkpoints) and len(checkpoints) > 0
    
    def handle_level_complete(self):
        """Handle level completion"""
        # Update level status
        self.current_level.completed = True
        self.state = "level_complete"
        
        # Play completion sound
        self.audio_manager.play_sound('level_complete')
        
        # Play victory music if this is the final level
        if self.current_level.level_number == self.level_manager.get_max_level():
            self.audio_manager.fade_music('victory')
        
        # Schedule next level load
        self.level_complete_time = time.time()
        
    def check_level_transition(self):
        """Check if it's time to transition to the next level"""
        if self.state == "level_complete" and hasattr(self, 'level_complete_time'):
            if time.time() - self.level_complete_time > LEVEL_TRANSITION_DELAY / 1000:
                next_level = self.current_level.level_number + 1
                if next_level <= MAX_LEVEL:
                    self.level_manager.advance_level()
                    self.load_level(next_level)
                    self.state = "playing"
                else:
                    self.state = "game_over"
                delattr(self, 'level_complete_time')
    
    def render(self):
        """Render the game"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.state == "menu":
            self.ui.render_menu()
            return
        
        if self.state == "level_select":
            self.ui.render_level_select()
            return
        
        # For gameplay states, render the game world first
        if self.state in ["playing", "paused", "level_complete"]:
            # Draw game objects
            for obj in self.game_objects:
                obj.render(self.screen)
            
            # Draw light beams
            for beam in self.light_beams:
                beam.render(self.screen)
            
            # Draw player
            self.player.render(self.screen)
            
            # Draw HUD
            self.ui.render_hud()
        
        # Draw overlays based on game state
        if self.state == "paused":
            self.ui.render_pause_menu()
        
        elif self.state == "level_complete":
            self.ui.render_level_complete()
        
        elif self.state == "game_over":
            self.ui.render_game_over()
    
    def update(self):
        """Update game state"""
        # Always update audio manager for fades and ambient sounds
        self.audio_manager.update()
        
        if self.state == "playing":
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.game_objects)
            
            # Update light beams
            for beam in self.light_beams:
                beam.update(self.game_objects)
            
            # Update game objects
            for obj in self.game_objects:
                if hasattr(obj, 'update'):
                    obj.update()
                    
                    # Check if it's a newly activated checkpoint
                    if isinstance(obj, Checkpoint) and obj.newly_activated:
                        # Play spatial sound for checkpoint activation
                        self.audio_manager.play_checkpoint_activation(
                            (obj.x, obj.y),  # Checkpoint position
                            (self.player.x, self.player.y)  # Player position
                        )
            
            # Check for level completion
            if self.check_level_complete():
                self.state = "level_complete"
                self.handle_level_complete()
        
        # Check for level transition
        self.check_level_transition()
