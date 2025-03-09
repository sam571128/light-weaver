import pygame
import sys
from game.game import Game
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE

def main():
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption(TITLE)
    
    # Create game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Create game instance
    game = Game(screen)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        # Update game state
        game.update()
        
        # Render game
        game.render()
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
