import sys
import pygame
import math
import random
from assets import WIDTH, HEIGHT, BLACK, WHITE, SUN_COLOR, SUN_POS, SUN_RADIUS, PLAYER_SIZE, PLAYER_SPEED, load_spaceship_image
from planets import PLANETS, update_planet_positions, get_planet_position, get_planet_positions
from game import GameState
import ui

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space explorer ")
clock = pygame.time.Clock()

# Generate some stars for the background
stars = [(random.randint(0, WIDTH*6), random.randint(0, HEIGHT*6)) for _ in range(300)]

game = GameState()

# Load spaceship image at game start
SPACESHIP_IMG = load_spaceship_image(PLAYER_SIZE)
if SPACESHIP_IMG is None:
    print("Error: Could not load spaceship.png. Please ensure the file exists in your project folder.")
    pygame.quit()
    sys.exit()

# --- START MENU LOOP ---
in_menu = True
cutscene_shown = False
while in_menu:
    if not cutscene_shown:
        ui.show_cutscene(screen, WIDTH, HEIGHT)
        cutscene_shown = True
    ui.draw_start_menu(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                in_menu = False
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

# --- MAIN GAME LOOP ---
running = True
selected_btn = None
show_controls = False
while running:
    clock.tick(60)
    # Update planet orbits
    update_planet_positions(PLANETS, 1)
    planets = get_planet_positions(PLANETS, SUN_POS)

    # --- EVENT HANDLING ---
    mouse = pygame.mouse.get_pos()
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.menu_open = True
                selected_btn = None
                show_controls = False

    # --- IN-GAME MENU ---
    if game.menu_open:
        btn_rects = ui.draw_game_menu(screen, selected_btn, show_controls)
        pygame.display.flip()
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    menu_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.menu_open = False
                        show_controls = False
                        menu_running = False
                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    selected_btn = None
                    for i, rect in enumerate(btn_rects):
                        if rect.collidepoint(mx, my):
                            selected_btn = i
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if selected_btn == 0:  # Resume
                        game.menu_open = False
                        show_controls = False
                        menu_running = False
                    elif selected_btn == 1:  # Controls
                        show_controls = not show_controls
                        btn_rects = ui.draw_game_menu(screen, selected_btn, show_controls)
                        pygame.display.flip()
                    elif selected_btn == 2:  # Quit
                        pygame.quit()
                        sys.exit()
        continue

    # --- GAME DRAWING ---
    screen.fill(BLACK)
    for sx, sy in stars:
        pygame.draw.circle(screen, WHITE, (sx % WIDTH, sy % HEIGHT), 2)
    pygame.draw.circle(screen, SUN_COLOR, (SUN_POS[0], SUN_POS[1]), SUN_RADIUS)
    font = pygame.font.SysFont(None, 32)
    sun_surf = font.render("Sun", True, WHITE)
    screen.blit(sun_surf, (SUN_POS[0] - 30, SUN_POS[1] - SUN_RADIUS - 30))
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        pygame.draw.circle(screen, planet["color"], (int(px), int(py)), pr)
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(planet["name"], True, WHITE)
        screen.blit(name_surf, (int(px - pr - 29), int(py - pr - 29)))
        screen.blit(name_surf, (int(px - pr - 30), int(py - pr - 30)))
    # Draw spaceship (example, update as needed)
    rotated_img = pygame.transform.rotate(SPACESHIP_IMG, 0)
    rect = rotated_img.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(rotated_img, rect.topleft)
    ui.draw_quest_bar(screen, game.current_quest, game.quests, WIDTH)
    ui.draw_health_fuel_bars(screen, 100, 100, 100, 100)  # Example values
    # --- BASE BUTTONS ---
    build_btn_rect, upgrade_base_btn_rect, upgrade_ship_btn_rect = ui.draw_base_buttons(screen, HEIGHT, None, False)
    tech_btn_rect = ui.draw_tech_tree_button(screen, WIDTH)
    # ...rest of game logic and UI...
    pygame.display.flip()

pygame.quit()
sys.exit()