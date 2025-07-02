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
# Expand WORLD_WIDTH and WORLD_HEIGHT to fit all Solar System planets, including Neptune
# For a large solar system, set world size to 20000x20000 (adjust as needed for your planet orbits)
WORLD_WIDTH = 20000
WORLD_HEIGHT = 20000

# Sun
SUN_POS = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
SUN_RADIUS = 150

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 5

# Asset loading
import os
import pygame


def load_spaceship_image(size):
    img_path = os.path.join(os.path.dirname(__file__), "spaceship.png")
    if not os.path.exists(img_path):
        print(f"Could not find {img_path}. Make sure the image is in the project folder.")
        return None
    try:
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (size, size))
        return img
    except Exception as e:
        print(f"Error loading {img_path}: {e}")
        return None


# Fonts (example, can be loaded as needed)
def get_font(size):
    return pygame.font.SysFont(None, size)
