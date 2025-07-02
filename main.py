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
controls_shown = False
controls_text = [
    "CONTROLS:",
    "Steer Ship: Move your mouse",
    "Accelerate: W",
    "Reverse: S",
    "Land: Approach a planet and stop",
    "Take Off: SPACE (when landed)",
    "Open Tech Tree: Click tech tree button (top right)",
    "Show Map: M",
    "Open Menu: ESC",
    "Interact/Collect: E (when near quest planet)",
    "",
    "Press ENTER to start"
]
while in_menu:
    if not cutscene_shown:
        ui.show_cutscene(screen, WIDTH, HEIGHT)
        cutscene_shown = True
    screen.fill(BLACK)
    # Draw controls at the start (replace ui.draw_start_menu controls)
    font = pygame.font.SysFont(None, 44)
    title = font.render("SPACE EXPLORER", True, (0, 200, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 220))
    font = pygame.font.SysFont(None, 36)
    for i, line in enumerate(controls_text):
        surf = font.render(line, True, WHITE)
        screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - 120 + i*32))
    pygame.display.flip()
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
show_inventory = False  # Track if inventory modal is open
inventory_scroll = 0    # Track scroll offset for inventory
# Player world position (centered on Earth at start)
player_x, player_y = SUN_POS[0], SUN_POS[1] + 1800
player_angle = 0
player_speed = PLAYER_SPEED
player_size = PLAYER_SIZE
landed_planet = None
landed_angle = None  # Angle at which the ship landed

# --- SYSTEM PROGRESSION STATE ---
# Update quest system to include Jupiter - Neptune in the beginning (Solar System)
# Update system_quest_ranges accordingly
system_names = [
    "Inner Worlds",      # Mercury to Mars
    "Outer Worlds",      # Jupiter to Pluto
    "Alpha Centauri",   # Centauri Prime to Centauri Tertius
    "Trappist-1"        # Trappist-1e to Trappist-1h
]
system_quest_ranges = [
    (0, 4),    # Mercury to Mars (0-3)
    (4, 9),    # Jupiter to Pluto (4-8)
    (9, 12),   # Centauri Prime to Centauri Tertius (9-11)
    (12, 15)   # Trappist-1e to Trappist-1h (12-14)
]
current_system = 0
in_hyperjump = False
hyperjump_timer = 0
HYPERJUMP_DURATION = 120  # frames (2 seconds at 60fps)

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
                elif show_inventory:
                    show_inventory = False
                else:
                    game.menu_open = True
                    selected_btn = None
                    show_controls = False
            if event.key == pygame.K_m:
                show_map = not show_map
            if event.key == pygame.K_i:
                show_inventory = not show_inventory
            if show_inventory:
                if event.key == pygame.K_DOWN:
                    inventory_scroll += 1
                if event.key == pygame.K_UP:
                    inventory_scroll -= 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_inventory:
                if event.button == 5:  # Mouse wheel down
                    inventory_scroll += 1
                if event.button == 4:  # Mouse wheel up
                    inventory_scroll -= 1
    # Clamp scroll
    inventory_items = list(game.player.inventory.items())
    max_scroll = max(0, len(inventory_items) - 6)
    inventory_scroll = max(0, min(inventory_scroll, max_scroll))
    # --- TECH TREE MODAL ---
    if show_tech_tree:
        # Draw tech tree at bottom, get upgrade button rects
        tech_btns = ui.draw_tech_tree(screen, WIDTH, HEIGHT, game.player.tech_tree, game.tech_upgrades)
        pygame.display.flip()
        # Handle tech tree interaction
        tech_tree_running = True
        while tech_tree_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    tech_tree_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        show_tech_tree = False
                        tech_tree_running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    for rect, upg in tech_btns:
                        if rect.collidepoint(mx, my):
                            upg_data = game.tech_upgrades[upg]
                            if upg_data['level'] < upg_data['max']:
                                upg_data['level'] += 1
                                # Apply upgrade effect
                                if upg == 'Speed':
                                    player_speed += 1
                                elif upg == 'Size':
                                    player_size += 5
                                # Redraw tree with updated state
                                tech_btns = ui.draw_tech_tree(screen, WIDTH, HEIGHT, game.player.tech_tree, game.tech_upgrades)
                                pygame.display.flip()
        continue

    # --- INVENTORY MODAL ---
    if show_inventory:
        ui.draw_inventory(screen, game.player.inventory, WIDTH, HEIGHT, inventory_scroll)
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
        # While landed, lock ship to planet edge at landing angle and allow rotation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - WIDTH // 2
        dy = mouse_y - HEIGHT // 2
        player_angle = math.degrees(math.atan2(-dx, -dy))
        px, py = landed_planet["pos"]
        pr = landed_planet["radius"]
        # Stick to the angle where the ship landed
        if landed_angle is not None:
            player_x = px + (pr + player_size // 2) * math.cos(landed_angle)
            player_y = py + (pr + player_size // 2) * math.sin(landed_angle)

    # Planet collision/landing
    next_x, next_y = player_x + move_x, player_y + move_y
    landed = False
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        dist = math.hypot(next_x - px, next_y - py)
        if dist < pr + player_size // 2:
            if landed_planet is None:
                # Just landed: record the angle
                landed_angle = math.atan2(next_y - py, next_x - px)
            landed = True
            landed_planet = planet
    if not landed:
        player_x, player_y = next_x, next_y
        landed_planet = None
        landed_angle = None
    if keys[pygame.K_SPACE] and landed_planet is not None:
        landed_planet = None  # Take off
        landed_angle = None

    # --- QUEST LOGIC: Progress by system, hyperspeed to next when all done ---
    # Allow collection from all planets in PLANETS
    allowed_planets = set(p["name"] for p in PLANETS)
    start_idx, end_idx = system_quest_ranges[current_system]
    # Find the first incomplete quest in the current system
    active_quest_idx = None
    for i in range(start_idx, end_idx):
        if not game.quests[i]['completed']:
            active_quest_idx = i
            break
    if active_quest_idx is not None:
        quest = game.quests[active_quest_idx]
        found_planet = False
        for planet in planets:
            if planet["name"] not in allowed_planets:
                continue
            px, py = planet["pos"]
            pr = planet["radius"]
            dist = math.hypot(player_x - px, player_y - py)
            # Increase collection radius to fit all planets (planet radius + 30)
            if dist < pr + 30:
                found_planet = True
                mat = planet["material"]
                # Auto-collect: increment quest progress if this is the quest planet/material
                if planet["name"] == quest["planet"] and mat == quest["material"] and not quest['completed']:
                    quest["collected"] += 1
                    if quest["collected"] >= quest["amount"]:
                        quest["completed"] = True
                        # Find next incomplete quest in this system
                        for j in range(start_idx, end_idx):
                            if not game.quests[j]['completed']:
                                game.current_quest = j
                                break
                        else:
                            # All quests in this system complete, trigger hyperspeed
                            if current_system + 1 < len(system_quest_ranges):
                                in_hyperjump = True
                                hyperjump_timer = 0
                                current_system += 1
                                # Move to first quest of next system
                                next_start, _ = system_quest_ranges[current_system]
                                game.current_quest = next_start
                            else:
                                # End of game, keep last quest
                                game.current_quest = len(game.quests) - 1
                # Show gather prompt (optional, for feedback)
                font = pygame.font.SysFont(None, 36)
                gather_msg = f"Auto-collecting {mat}..."
                prompt = font.render(gather_msg, True, (255,255,0))
                screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 120))
                break
        if not found_planet:
            print(f"[DEBUG] No accessible planet found for collection in this frame. Player at ({player_x:.1f}, {player_y:.1f})")
    else:
        # All quests in this system complete, waiting for hyperspeed
        pass
    # Draw only the current active quest in the quest bar
    ui.draw_quest_bar(screen, game.current_quest, game.quests, WIDTH)
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
        map_width, map_height = 350, 350  # Reduced map view size
        map_surf = pygame.Surface((map_width, map_height))
        # Modern map background
        for y in range(map_height):
            c = int(20 + 30 * (y / map_height))
            pygame.draw.line(map_surf, (c, c, 48), (0, y), (map_width, y))
        # Center the sun in the map
        sun_mx, sun_my = map_width // 2, map_height // 2
        pygame.draw.circle(map_surf, SUN_COLOR, (sun_mx, sun_my), 14)
        font = pygame.font.SysFont(None, 18)
        sun_surf = font.render("Sun", True, WHITE)
        map_surf.blit(sun_surf, (sun_mx - 10, sun_my - 24))
        # Calculate scale for planet orbits
        max_orbit = max(p["orbit_radius"] for p in PLANETS)
        scale = (map_width // 2 - 24) / max_orbit
        for planet in PLANETS:
            angle = planet["angle"]
            orbit = planet["orbit_radius"] * scale
            mx = int(sun_mx + orbit * math.cos(angle))
            my = int(sun_my + orbit * math.sin(angle))
            pygame.draw.circle(map_surf, planet["color"], (mx, my), 7)
            font = pygame.font.SysFont(None, 16)
            name_surf = font.render(planet["name"], True, WHITE)
            map_surf.blit(name_surf, (mx - 10, my - 18))
        # Player position on map (projected from world to map orbit)
        # Find player's polar coordinates relative to sun
        dx = player_x - SUN_POS[0]
        dy = player_y - SUN_POS[1]
        player_dist = math.hypot(dx, dy)
        player_angle = math.atan2(dy, dx)
        player_map_dist = player_dist * scale
        pmx = int(sun_mx + player_map_dist * math.cos(player_angle))
        pmy = int(sun_my + player_map_dist * math.sin(player_angle))
        pygame.draw.circle(map_surf, (0,255,0), (pmx, pmy), 5)
        screen.blit(map_surf, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2, map_width, map_height), 2)
        font = pygame.font.SysFont(None, 22)
        exit_surf = font.render("Press M to close map", True, WHITE)
        screen.blit(exit_surf, (WIDTH//2 - exit_surf.get_width()//2, HEIGHT//2 + map_height//2 + 8))
        pygame.display.flip()
        continue

    # --- GAME DRAWING ---
    ui.draw_game_background(screen, stars, cam_x, cam_y, WIDTH, HEIGHT, SUN_COLOR, SUN_POS, SUN_RADIUS, WHITE)
    font = pygame.font.SysFont(None, 32)
    sun_surf = font.render("Sun", True, WHITE)
    screen.blit(sun_surf, (SUN_POS[0] - cam_x - 30, SUN_POS[1] - cam_y - SUN_RADIUS - 30))
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        # Draw planet with glow
        for r in range(pr+18, pr, -4):
            alpha = max(0, 60 - (pr+18-r)*4)
            glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*planet["color"], alpha), (r, r), r)
            screen.blit(glow, (int(px - cam_x - r), int(py - cam_y - r)), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(screen, planet["color"], (int(px - cam_x), int(py - cam_y)), pr)
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(planet["name"], True, WHITE)
        screen.blit(name_surf, (int(px - cam_x - pr - 29), int(py - cam_y - pr - 29)))
        screen.blit(name_surf, (int(px - cam_x - pr - 30), int(py - cam_y - pr - 30)))
    # Draw spaceship at player position and angle
    rotated_img = pygame.transform.rotate(SPACESHIP_IMG, player_angle)
    rect = rotated_img.get_rect(center=(int(player_x - cam_x), int(player_y - cam_y)))
    # Add a subtle ship shadow
    shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0,0,0,80), shadow.get_rect().move(0,8))
    screen.blit(shadow, rect.topleft)
    screen.blit(rotated_img, rect.topleft)
    # Draw only the current active quest in the quest bar
    ui.draw_quest_bar(screen, game.current_quest, game.quests, WIDTH)
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