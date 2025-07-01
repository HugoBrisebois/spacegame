import sys
import pygame

# initialize pygame
pygame.init()

# screen size
WIDTH, HEIGHT = 800,600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space explorer ")

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)

# Player settings
player_size = 40
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5

clock = pygame.time.Clock()


# Game loop
running = True
while running:
    clock.tick(60) #60FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
            
    # character controller
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_pos[1] += player_speed
    
    
    # Keep player on screen
    player_pos[0] = max(0, min(WIDTH - player_size, player_pos[0]))
    player_pos[1] = max(0, min(HEIGHT - player_size, player_pos[1]))
    
    #Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (*player_pos, player_size, player_size))
    pygame.display.flip()

pygame.quit()
sys.exit()