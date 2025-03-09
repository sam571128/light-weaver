import pygame
import os
import math
import time
from .constants import *

class AudioManager:
    """Manages game audio including sound effects and music"""
    def __init__(self):
        # Initialize pygame mixer with higher quality
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Set volume levels
        pygame.mixer.music.set_volume(VOLUME_MUSIC)
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Current music track
        self.current_music = None
        
        # Fade parameters
        self.fade_start_time = 0
        self.fade_duration = 0
        self.fade_start_volume = 0
        self.fade_end_volume = 0
        self.is_fading = False
        
        # Sound channels for advanced audio control
        self.channels = {}
        for i in range(8):  # Reserve 8 channels for different sound types
            self.channels[i] = pygame.mixer.Channel(i)
        
        # Channel assignments
        self.CHANNEL_UI = 0       # UI sounds
        self.CHANNEL_PLAYER = 1   # Player sounds
        self.CHANNEL_BEAM = 2     # Light beam sounds
        self.CHANNEL_OBJECTS = 3  # Interactive objects
        self.CHANNEL_AMBIENT = 4  # Ambient sounds
        self.CHANNEL_CHECKPOINT = 5  # Checkpoint sounds
        self.CHANNEL_VICTORY = 6  # Victory/completion sounds
        self.CHANNEL_MISC = 7     # Miscellaneous sounds
        
        # Load audio assets
        self.load_assets()
    
    def load_assets(self):
        """Load audio assets"""
        # Create assets directory if it doesn't exist
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'audio')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Define sound effects to load
        sound_files = {
            'beam_on': 'beam_on.wav',
            'beam_off': 'beam_off.wav',
            'mirror_rotate': 'mirror_rotate.wav',
            'filter_change': 'filter_change.wav',
            'checkpoint_activate': 'checkpoint_activate.wav',
            'level_complete': 'level_complete.wav',
            'button_click': 'button_click.wav',
            'shadow_creature': 'shadow_creature.wav'
        }
        
        # Load sound effects if they exist
        for sound_name, file_name in sound_files.items():
            file_path = os.path.join(assets_dir, file_name)
            if os.path.exists(file_path):
                self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                self.sounds[sound_name].set_volume(VOLUME_SFX)
            else:
                print(f"Warning: Sound file {file_path} not found")
        
        # Define music tracks
        self.music_tracks = {
            'menu': 'menu_music.mp3',
            'gameplay': 'gameplay_music.mp3',
            'victory': 'victory_music.mp3'
        }
    
    def play_sound(self, sound_name, channel=None):
        """Play a sound effect on the specified channel"""
        if sound_name in self.sounds:
            if channel is not None and channel in self.channels:
                self.channels[channel].play(self.sounds[sound_name])
            else:
                self.sounds[sound_name].play()
    
    def play_sound_with_context(self, sound_name, context_type):
        """Play a sound effect with the appropriate channel based on context"""
        channel = self.CHANNEL_MISC  # Default channel
        
        # Determine appropriate channel based on context
        if context_type == 'ui':
            channel = self.CHANNEL_UI
        elif context_type == 'player':
            channel = self.CHANNEL_PLAYER
        elif context_type == 'beam':
            channel = self.CHANNEL_BEAM
        elif context_type == 'object':
            channel = self.CHANNEL_OBJECTS
        elif context_type == 'ambient':
            channel = self.CHANNEL_AMBIENT
        elif context_type == 'checkpoint':
            channel = self.CHANNEL_CHECKPOINT
        elif context_type == 'victory':
            channel = self.CHANNEL_VICTORY
        
        self.play_sound(sound_name, channel)
    
    def play_spatial_sound(self, sound_name, source_pos, listener_pos, max_distance=500):
        """Play a sound with volume adjusted based on distance from listener"""
        if sound_name not in self.sounds:
            return
            
        # Calculate distance between source and listener
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate volume based on distance (inverse square law)
        if distance <= 0:
            volume = 1.0
        else:
            volume = max(0.0, min(1.0, 1.0 - (distance / max_distance)))
        
        # Calculate stereo panning based on horizontal position
        # -1.0 = full left, 1.0 = full right
        if dx == 0:
            pan = 0.0
        else:
            pan = max(-1.0, min(1.0, dx / (max_distance/2)))
        
        # Find an available channel
        channel = self.channels[self.CHANNEL_MISC]
        
        # Set volume and play
        sound = self.sounds[sound_name]
        sound.set_volume(volume * VOLUME_SFX)
        
        # Apply panning by adjusting left/right volume
        if pan < 0:  # Sound source is to the left
            channel.set_volume(1.0, 1.0 + pan)
        else:  # Sound source is to the right
            channel.set_volume(1.0 - pan, 1.0)
            
        channel.play(sound)
    
    def play_music(self, track_name, loop=-1):
        """Play a music track"""
        if track_name in self.music_tracks:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'audio')
            file_path = os.path.join(assets_dir, self.music_tracks[track_name])
            
            if os.path.exists(file_path):
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(loop)
                self.current_music = track_name
            else:
                print(f"Warning: Music file {file_path} not found")
    
    def fade_music(self, new_track, duration=2000):
        """Fade out current music and fade in new track"""
        if new_track == self.current_music:
            return
            
        # Start fade out
        self.fade_start_time = time.time()
        self.fade_duration = duration / 1000  # Convert to seconds
        self.fade_start_volume = pygame.mixer.music.get_volume()
        self.fade_end_volume = 0.0
        self.is_fading = True
        
        # Store the new track to play after fade out
        self.next_track = new_track
    
    def update_fade(self):
        """Update music fading - should be called in the game loop"""
        if not self.is_fading:
            return
            
        elapsed = time.time() - self.fade_start_time
        progress = min(1.0, elapsed / self.fade_duration)
        
        if self.fade_end_volume > self.fade_start_volume:  # Fading in
            current_volume = self.fade_start_volume + (self.fade_end_volume - self.fade_start_volume) * progress
        else:  # Fading out
            current_volume = self.fade_start_volume - (self.fade_start_volume - self.fade_end_volume) * progress
        
        pygame.mixer.music.set_volume(current_volume)
        
        # If fade out complete, start the new track
        if progress >= 1.0:
            self.is_fading = False
            
            if hasattr(self, 'next_track'):
                if self.fade_end_volume == 0.0:  # We were fading out
                    # Start the new track and fade in
                    self.play_music(self.next_track)
                    
                    # Set up fade in
                    self.fade_start_time = time.time()
                    self.fade_duration = self.fade_duration  # Use same duration
                    self.fade_start_volume = 0.0
                    self.fade_end_volume = VOLUME_MUSIC
                    pygame.mixer.music.set_volume(0.0)  # Start at zero volume
                    self.is_fading = True
                    
                delattr(self, 'next_track')
    
    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
        self.is_fading = False
    
    def pause_music(self):
        """Pause the currently playing music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause the currently playing music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Set the music volume (0.0 to 1.0)"""
        volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
        pygame.mixer.music.set_volume(volume)
        
    def set_sound_volume(self, sound_name, volume):
        """Set the volume for a specific sound (0.0 to 1.0)"""
        if sound_name in self.sounds:
            volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
            self.sounds[sound_name].set_volume(volume)
    
    def set_sfx_volume(self, volume):
        """Set the volume for all sound effects (0.0 to 1.0)"""
        volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def update(self):
        """Update audio manager - call this in the game loop"""
        # Update music fading
        self.update_fade()
        
        # Update any other time-based audio effects
        self.update_ambient_sounds()
    
    def update_ambient_sounds(self):
        """Update ambient sounds based on game state and environment"""
        # This method can be expanded to dynamically adjust ambient sounds
        # based on the game state, player position, etc.
        pass
    
    def play_ambient_loop(self, sound_name, fade_in=1000):
        """Play a looping ambient sound with optional fade-in"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            channel = self.channels[self.CHANNEL_AMBIENT]
            
            # Start at zero volume if fading in
            if fade_in > 0:
                sound.set_volume(0.0)
                
            # Play the sound on loop
            channel.play(sound, loops=-1)
            
            # Store fade-in information
            if fade_in > 0:
                self.ambient_fade_start = time.time()
                self.ambient_fade_duration = fade_in / 1000
                self.ambient_target_volume = VOLUME_SFX
    
    def stop_ambient(self, fade_out=1000):
        """Stop ambient sounds with optional fade-out"""
        channel = self.channels[self.CHANNEL_AMBIENT]
        
        if fade_out > 0 and channel.get_busy():
            # Start fade out
            self.ambient_fade_start = time.time()
            self.ambient_fade_duration = fade_out / 1000
            self.ambient_target_volume = 0.0
            # The channel will be stopped in update_ambient_sounds when volume reaches 0
        else:
            channel.stop()
    
    def play_checkpoint_activation(self, checkpoint_position, player_position):
        """Play checkpoint activation sound with spatial positioning"""
        self.play_spatial_sound('checkpoint_activate', checkpoint_position, player_position)
        
        # Also play a celebratory sound on the victory channel
        self.play_sound('level_complete', self.CHANNEL_VICTORY)
    
    def play_beam_interaction(self, interaction_type, position, player_position):
        """Play appropriate sound for beam interactions"""
        if interaction_type == 'mirror':
            self.play_spatial_sound('beam_reflect', position, player_position)
        elif interaction_type == 'filter':
            self.play_spatial_sound('beam_filter', position, player_position)
        elif interaction_type == 'split':
            self.play_spatial_sound('beam_split', position, player_position)
    
    def play_ui_sound(self, sound_name):
        """Play a UI sound effect"""
        self.play_sound(sound_name, self.CHANNEL_UI)
    
    def fade_music(self, track_name, fade_ms=1000, loop=-1):
        """Fade out current music and fade in new music"""
        if track_name in self.music_tracks:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'audio')
            file_path = os.path.join(assets_dir, self.music_tracks[track_name])
            
            if os.path.exists(file_path):
                pygame.mixer.music.fadeout(fade_ms)
                pygame.time.delay(fade_ms)  # Wait for fadeout to complete
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(loop, fade_ms=fade_ms)
            else:
                print(f"Warning: Music file {file_path} not found")
    

