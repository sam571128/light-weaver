# Light Weaver

A 2D puzzle game where players control a glowing orb navigating through dark mazes filled with mirrors, prisms, and reflective objects. The objective is to direct beams of colored light to activate checkpoints and solve puzzles.

(The game is created entirely by Vibe Coding with Claude, it sucks lol)

## Game Concept

In Light Weaver, players manipulate light beams through various interactive objects:
- Mirrors to reflect light
- Prisms to split white light into component colors
- Color filters to change light properties
- Switches and gates activated by specific light colors
- Shadow creatures that block light paths

## Installation

1. Clone this repository
2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Run the game:
```
python main.py
```

## Controls

- Arrow keys or WASD: Move the light orb
- Mouse: Aim light beam direction
- Left click: Interact with objects (rotate mirrors, activate switches)
- Space: Toggle light beam on/off
- R: Reset level
- ESC: Pause menu

## Development

This game is built with:
- Python 3.8+
- Pygame for rendering and game logic
- NumPy for physics calculations

## Features

- Light physics simulation (reflection, refraction, color mixing)
- Interactive puzzle elements
- Progressive level design
- Atmospheric visuals and immersive audio
- Dynamic sound effects for game interactions
- Adaptive background music that changes with game state
