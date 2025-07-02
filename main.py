import sys
import pygame
import math
import random
from assets import WIDTH, HEIGHT, BLACK, WHITE, SUN_COLOR, SUN_POS, SUN_RADIUS, PLAYER_SIZE, PLAYER_SPEED, WORLD_WIDTH, WORLD_HEIGHT, load_spaceship_image
from planets import PLANETS, update_planet_positions, get_planet_positions
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
show_map = False
show_tech_tree = False  # Track if tech tree modal is open
# Player world position (centered on Earth at start)
player_x, player_y = SUN_POS[0], SUN_POS[1] + 1800
player_angle = 0
player_speed = PLAYER_SPEED
player_size = PLAYER_SIZE
player_health = 100
player_max_health = 100
player_fuel = 100
player_max_fuel = 100
player_fuel_efficiency = 1.0
landed_planet = None

while running:
    clock.tick(60)
    # Update planet orbits
    update_planet_positions(PLANETS, 1)
    planets = get_planet_positions(PLANETS, SUN_POS)

    # --- EVENT HANDLING ---
    mouse = pygame.mouse.get_pos()
    click = False
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_tech_tree:
                    show_tech_tree = False
                else:
                    game.menu_open = True
                    selected_btn = None
                    show_controls = False
            if event.key == pygame.K_m:
                show_map = not show_map

    # --- TECH TREE MODAL ---
    if show_tech_tree:
        ui.draw_tech_tree(screen, WIDTH, HEIGHT, game.player.tech_tree)
        pygame.display.flip()
        continue

    # --- PLAYER MOVEMENT & LANDING (ship sticks to planet, improved base button visibility) ---
    move_x, move_y = 0, 0
    dt = clock.get_time() / 16.67  # Normalize to ~60 FPS
    if landed_planet is None:
        # Calculate angle to mouse (relative to screen center)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - WIDTH // 2
        dy = mouse_y - HEIGHT // 2
        player_angle = math.degrees(math.atan2(-dx, -dy))
        # Acceleration (W for forward, S for reverse)
        if keys[pygame.K_w]:
            rad = math.radians(player_angle)
            move_x += -player_speed * math.sin(rad) * dt
            move_y += -player_speed * math.cos(rad) * dt
        if keys[pygame.K_s]:
            rad = math.radians(player_angle)
            move_x -= -player_speed * math.sin(rad) * 0.5 * dt
            move_y -= -player_speed * math.cos(rad) * 0.5 * dt
    else:
        # While landed, lock ship to planet edge and allow rotation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - WIDTH // 2
        dy = mouse_y - HEIGHT // 2
        player_angle = math.degrees(math.atan2(-dx, -dy))
        px, py = landed_planet["pos"]
        pr = landed_planet["radius"]
        angle_to_planet = math.atan2(player_y - py, player_x - px)
        # Lock ship to edge of planet
        player_x = px + (pr + player_size // 2) * math.cos(angle_to_planet)
        player_y = py + (pr + player_size // 2) * math.sin(angle_to_planet)

    # Planet collision/landing
    next_x, next_y = player_x + move_x, player_y + move_y
    landed = False
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        dist = math.hypot(next_x - px, next_y - py)
        if dist < pr + player_size // 2:
            landed = True
            landed_planet = planet
            # Lock to edge handled above
    if not landed:
        player_x, player_y = next_x, next_y
        landed_planet = None
    if keys[pygame.K_SPACE] and landed_planet is not None:
        landed_planet = None  # Take off

    # --- QUEST LOGIC ---
    if game.current_quest < len(game.quests):
        quest = game.quests[game.current_quest]
        for planet in planets:
            px, py = planet["pos"]
            pr = planet["radius"]
            dist = math.hypot(player_x - px, player_y - py)
            if dist < pr + 10:
                if keys[pygame.K_e]:
                    mat = planet["material"]
                    if planet["name"] == quest["planet"] and mat == quest["material"] and not quest["completed"]:
                        game.player.inventory[mat] = game.player.inventory.get(mat, 0) + 1
                        quest["collected"] += 1
                        if quest["collected"] >= quest["amount"]:
                            quest["completed"] = True
                            # Apply reward
                            if "speed" in quest["reward"]:
                                player_speed += quest["reward"]["speed"]
                            if "size" in quest["reward"]:
                                player_size += quest["reward"]["size"]
                            if "win" in quest["reward"]:
                                pass
                            game.current_quest += 1

    # --- IN-GAME MENU ---
    if game.menu_open:
        btn_rects = ui.draw_game_menu(screen, selected_btn, show_controls)
        if btn_rects is None:
            btn_rects = []
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
                        if rect and rect.collidepoint(mx, my):
                            selected_btn = i
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if selected_btn == 0:  # Resume
                        game.menu_open = False
                        show_controls = False
                        menu_running = False
                    elif selected_btn == 1:  # Controls
                        show_controls = not show_controls
                        btn_rects = ui.draw_game_menu(screen, selected_btn, show_controls)
                        if btn_rects is None:
                            btn_rects = []
                        pygame.display.flip()
                    elif selected_btn == 2:  # Quit
                        pygame.quit()
                        sys.exit()
        continue

    # --- CAMERA LOGIC ---
    cam_x = int(player_x + player_size // 2 - WIDTH // 2)
    cam_y = int(player_y + player_size // 2 - HEIGHT // 2)
    cam_x = max(0, min(WORLD_WIDTH - WIDTH, cam_x))
    cam_y = max(0, min(WORLD_HEIGHT - HEIGHT, cam_y))

    # --- MAP VIEW ---
    if show_map:
        map_width, map_height = 400, 400
        map_surf = pygame.Surface((map_width, map_height))
        map_surf.fill((20, 20, 40))
        sun_mx = int(SUN_POS[0] / WORLD_WIDTH * map_width)
        sun_my = int(SUN_POS[1] / WORLD_HEIGHT * map_height)
        pygame.draw.circle(map_surf, SUN_COLOR, (sun_mx, sun_my), 18)
        font = pygame.font.SysFont(None, 20)
        sun_surf = font.render("Sun", True, WHITE)
        map_surf.blit(sun_surf, (sun_mx - 15, sun_my - 30))
        for planet in planets:
            px, py = planet["pos"]
            mx = int(px / WORLD_WIDTH * map_width)
            my = int(py / WORLD_HEIGHT * map_height)
            pygame.draw.circle(map_surf, planet["color"], (mx, my), 8)
            font = pygame.font.SysFont(None, 18)
            name_surf = font.render(planet["name"], True, WHITE)
            map_surf.blit(name_surf, (mx - 10, my - 20))
        mx = int(player_x / WORLD_WIDTH * map_width)
        my = int(player_y / WORLD_HEIGHT * map_height)
        pygame.draw.circle(map_surf, (0,255,0), (mx, my), 6)
        screen.blit(map_surf, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2, map_width, map_height), 2)
        font = pygame.font.SysFont(None, 28)
        exit_surf = font.render("Press M to close map", True, WHITE)
        screen.blit(exit_surf, (WIDTH//2 - exit_surf.get_width()//2, HEIGHT//2 + map_height//2 + 10))
        pygame.display.flip()
        continue

    # --- GAME DRAWING ---
    screen.fill(BLACK)
    for sx, sy in stars:
        if cam_x <= sx <= cam_x + WIDTH and cam_y <= sy <= cam_y + HEIGHT:
            pygame.draw.circle(screen, WHITE, (sx - cam_x, sy - cam_y), 2)
    pygame.draw.circle(screen, SUN_COLOR, (SUN_POS[0] - cam_x, SUN_POS[1] - cam_y), SUN_RADIUS)
    font = pygame.font.SysFont(None, 32)
    sun_surf = font.render("Sun", True, WHITE)
    screen.blit(sun_surf, (SUN_POS[0] - cam_x - 30, SUN_POS[1] - cam_y - SUN_RADIUS - 30))
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        pygame.draw.circle(screen, planet["color"], (int(px - cam_x), int(py - cam_y)), pr)
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(planet["name"], True, WHITE)
        screen.blit(name_surf, (int(px - cam_x - pr - 29), int(py - cam_y - pr - 29)))
        screen.blit(name_surf, (int(px - cam_x - pr - 30), int(py - cam_y - pr - 30)))
    # Draw spaceship at player position and angle
    rotated_img = pygame.transform.rotate(SPACESHIP_IMG, player_angle)
    rect = rotated_img.get_rect(center=(int(player_x - cam_x), int(player_y - cam_y)))
    screen.blit(rotated_img, rect.topleft)
    ui.draw_quest_bar(screen, game.current_quest, game.quests, WIDTH)
    ui.draw_health_fuel_bars(screen, player_health, player_max_health, player_fuel, player_max_fuel)

    # --- BUILD BASE BUTTON ---
    build_btn_rect = None
    if landed_planet is not None:
        # Only allow building a base if not already built
        if not game.player.bases.get(landed_planet["name"], False):
            build_btn_rect = ui.draw_base_buttons(screen, HEIGHT, None, False)[0]
            if build_btn_rect and build_btn_rect.collidepoint(mouse) and click:
                game.player.bases[landed_planet["name"]] = True
                # Optionally: play sound or show feedback

    # --- TECH TREE BUTTON ---
    tech_btn_rect = ui.draw_tech_tree_button(screen, WIDTH)
    if tech_btn_rect and tech_btn_rect.collidepoint(mouse) and click:
        show_tech_tree = True

    # Show landing message if landed
    if landed_planet is not None:
        font = pygame.font.SysFont(None, 40)
        msg = font.render("LANDED! Press SPACE to take off", True, (255,255,0))
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 + 80))

    pygame.display.flip()

pygame.quit()
sys.exit()