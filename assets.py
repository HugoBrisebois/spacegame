"""
Handles asset loading, color definitions, and constants.
"""

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SUN_COLOR = (255, 255, 100)

# Screen size
WIDTH, HEIGHT = 800, 600

# World/map settings
WORLD_WIDTH, WORLD_HEIGHT = 5200, 5200

# Sun
SUN_POS = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
SUN_RADIUS = 150

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5

# Asset loading
import pygame
import sys
try:
    SPACESHIP_IMG = pygame.image.load("spaceship.png").convert_alpha()
    SPACESHIP_IMG = pygame.transform.scale(SPACESHIP_IMG, (PLAYER_SIZE, PLAYER_SIZE))
except pygame.error:
    print("Could not load spaceship.png. Make sure the image is in the project folder.")
    pygame.quit()
    sys.exit()


# Fonts (example, can be loaded as needed)
def get_font(size):
    return pygame.font.SysFont(None, size)
