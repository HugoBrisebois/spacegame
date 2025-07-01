import sys
import pygame
import math
import random

# initialize pygame
pygame.init()

# screen size
WIDTH, HEIGHT = 800,600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space explorer ")

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)

# World/map settings
WORLD_WIDTH, WORLD_HEIGHT = 5200, 5200  # Expand world to fit all planets

# Generate some stars for the background
stars = [(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(300)]

# --- SUN & PLANETS ORBIT SETUP ---
sun_pos = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
sun_radius = 150
sun_color = (255, 255, 100)

# Each planet has: name, orbit_radius, color, material, size, angle, speed
planet_data = [
    {"name": "Mercury", "orbit_radius": 600, "color": (200, 200, 200), "material": "Iron", "size": 40, "speed": 1.6},
    {"name": "Venus",   "orbit_radius": 1200, "color": (255, 200, 0),  "material": "Sulfur", "size": 60, "speed": 1.2},
    {"name": "Earth",   "orbit_radius": 1800, "color": (0, 100, 255), "material": "Water", "size": 70, "speed": 1.0},
    {"name": "Mars",    "orbit_radius": 2400, "color": (255, 80, 0),  "material": "Silicon", "size": 55, "speed": 0.8},
    {"name": "Jupiter", "orbit_radius": 3000, "color": (210, 180, 140), "material": "Hydrogen", "size": 120, "speed": 0.5},
    {"name": "Saturn",  "orbit_radius": 3600, "color": (230, 220, 170), "material": "Helium", "size": 110, "speed": 0.4},
    {"name": "Uranus",  "orbit_radius": 4200, "color": (100, 255, 255), "material": "Methane", "size": 90, "speed": 0.3},
    {"name": "Neptune", "orbit_radius": 4800, "color": (60, 80, 255),   "material": "Ammonia", "size": 85, "speed": 0.25},
    {"name": "Pluto",   "orbit_radius": 5200, "color": (200, 200, 255), "material": "Ice", "size": 30, "speed": 0.18},
]
# Add initial angle to each planet
for i, p in enumerate(planet_data):
    p["angle"] = i * (math.pi / 4.5)

# Player settings
# Find Earth's initial position
for p in planet_data:
    if p["name"] == "Earth":
        earth_angle = p["angle"]
        earth_radius = p["orbit_radius"]
        break
else:
    earth_angle = 0
    earth_radius = 0
player_size = 20  # Make ship smaller
player_pos = [
    int(sun_pos[0] + earth_radius * math.cos(earth_angle)),
    int(sun_pos[1] + earth_radius * math.sin(earth_angle))
]
player_speed = 5
player_angle = 0  # Angle in degrees

# Load spaceship image (place 'spaceship.png' in your project folder)
try:
    spaceship_img = pygame.image.load("spaceship.png").convert_alpha()
    spaceship_img = pygame.transform.scale(spaceship_img, (player_size, player_size))
except pygame.error:
    print("Could not load spaceship.png. Make sure the image is in the project folder.")
    pygame.quit()
    sys.exit()

# --- STORY & QUEST SYSTEM ---
story = [
    "You are Errin, a pioneer of the Galactic Expansion Fleet.",
    "Your mission: travel to distant planets, colonize them, and extract their resources for humanity's future.",
    "Each world holds unique materials vital for Earth's survival and the growth of the new colonies.",
    "Explore, land, and exploit the riches of the solar system. The fate of civilization rests on your success!"
]

quests = [
    {
        "desc": "Colonize Mercury and extract 3 Iron for Earth's new outpost.",
        "planet": "Mercury",
        "material": "Iron",
        "amount": 3,
        "collected": 0,
        "completed": False,
        "reward": {"speed": 1}
    },
    {
        "desc": "Establish a mining base on Venus and collect 2 Sulfur for advanced fuel.",
        "planet": "Venus",
        "material": "Sulfur",
        "amount": 2,
        "collected": 0,
        "completed": False,
        "reward": {"speed": 1}
    },
    {
        "desc": "Terraform Earth by gathering 2 Water for the new colony's life support.",
        "planet": "Earth",
        "material": "Water",
        "amount": 2,
        "collected": 0,
        "completed": False,
        "reward": {"size": 10}
    },
    {
        "desc": "Exploit Mars for 4 Silicon to build the first Martian city.",
        "planet": "Mars",
        "material": "Silicon",
        "amount": 4,
        "collected": 0,
        "completed": False,
        "reward": {"win": True}
    }
]
current_quest = 0

inventory = {}

clock = pygame.time.Clock()

# --- BASES SYSTEM ---
bases = {}  # planet_name: {level, revenue, last_collected}
revenue = 0
REVENUE_INTERVAL = 180  # frames (3 seconds at 60 FPS)
BASE_BUILD_COST = 0  # Free to build for now
BASE_UPGRADE_COST = 100
BASE_REVENUE_BASE = 10
BASE_REVENUE_MULT = 1.5
SHIP_UPGRADE_COST = 200

def draw_start_menu():
    screen.fill(BLACK)
    font_big = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 32)
    title = font_big.render("Space Explorer", True, WHITE)
    prompt = font_small.render("Press ENTER to Start", True, WHITE)
    controls = [
        "Controls:",
        "Arrow keys / WASD - Move & Rotate",
        "E - Collect material at planet",
        "U - Upgrade (if available)",
        "ESC - Quit"
    ]
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 40))
    for i, line in enumerate(controls):
        ctrl = font_small.render(line, True, WHITE)
        screen.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT // 2 + 30 + i * 30))
    pygame.display.flip()

def draw_game_menu(selected=None, show_controls=False):
    menu_width, menu_height = 400, 320
    menu_x = WIDTH // 2 - menu_width // 2 - 100  # Shift left for controls panel
    menu_y = HEIGHT // 2 - menu_height // 2
    menu_panel = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
    menu_panel.fill((30, 30, 60, 240))
    pygame.draw.rect(menu_panel, (80, 80, 120, 255), (0, 0, menu_width, menu_height), border_radius=18)
    font = pygame.font.SysFont(None, 48)
    title = font.render("Game Menu", True, (255,255,255))
    menu_panel.blit(title, (menu_width//2 - title.get_width()//2, 30))
    font_btn = pygame.font.SysFont(None, 36)
    btns = ["Resume", "Controls", "Quit"]
    btn_rects = []
    for i, btn in enumerate(btns):
        color = (255,255,120) if selected == i else (220,220,255)
        btn_surf = font_btn.render(btn, True, color)
        bx = menu_width//2 - btn_surf.get_width()//2
        by = 100 + i*60
        menu_panel.blit(btn_surf, (bx, by))
        btn_rects.append(pygame.Rect(menu_x+bx, menu_y+by, btn_surf.get_width(), btn_surf.get_height()))
    screen.blit(menu_panel, (menu_x, menu_y))
    # Draw controls panel to the right if needed
    if show_controls:
        ctrl_width, ctrl_height = 340, 260
        ctrl_x = menu_x + menu_width + 20
        ctrl_y = menu_y + 20
        ctrl_panel = pygame.Surface((ctrl_width, ctrl_height), pygame.SRCALPHA)
        ctrl_panel.fill((20, 40, 30, 230))
        pygame.draw.rect(ctrl_panel, (60, 120, 80, 255), (0, 0, ctrl_width, ctrl_height), border_radius=16)
        font_ctrl = pygame.font.SysFont(None, 32)
        ctrl_title = font_ctrl.render("Controls", True, (255,255,200))
        ctrl_panel.blit(ctrl_title, (ctrl_width//2 - ctrl_title.get_width()//2, 18))
        font_ctrl2 = pygame.font.SysFont(None, 24)
        controls = [
            "Arrow keys / WASD - Move & Rotate",
            "E - Collect material at planet",
            "U - Upgrade (if available)",
            "M - Minimap",
            "ESC - Menu/Quit",
            "Mouse Wheel/Arrows - Scroll Inventory"
        ]
        for i, line in enumerate(controls):
            ctrl_surf = font_ctrl2.render(line, True, (200,255,200))
            ctrl_panel.blit(ctrl_surf, (24, 60 + i*32))
        screen.blit(ctrl_panel, (ctrl_x, ctrl_y))
    pygame.display.flip()
    return btn_rects

def show_cutscene():
    cutscene_duration = 5.5  # seconds
    start_time = pygame.time.get_ticks()
    font = pygame.font.SysFont(None, 38)
    font_small = pygame.font.SysFont(None, 28)
    lines = [
        "You are Errin, a pioneer of the Galactic Expansion Fleet.",
        "Your mission: travel to distant planets, colonize them,",
        "and extract their resources for humanity's future.",
        "Each world holds unique materials vital for Earth's survival",
        "and the growth of the new colonies.",
        "Explore, land, and exploit the riches of the solar system.",
        "The fate of civilization rests on your success!"
    ]
    prompt = "Press SPACE or ENTER to continue..."
    while True:
        screen.fill((10, 10, 30))
        panel = pygame.Surface((WIDTH-80, HEIGHT-120), pygame.SRCALPHA)
        panel.fill((30, 30, 60, 230))
        screen.blit(panel, (40, 60))
        for i, line in enumerate(lines):
            surf = font.render(line, True, (220, 220, 255))
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 120 + i*48))
        prompt_surf = font_small.render(prompt, True, (255,255,180))
        screen.blit(prompt_surf, (WIDTH//2 - prompt_surf.get_width()//2, HEIGHT-100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return
        if (pygame.time.get_ticks() - start_time) > cutscene_duration * 1000:
            return

# --- START MENU LOOP ---
in_menu = True
cutscene_shown = False
while in_menu:
    if not cutscene_shown:
        show_cutscene()
        cutscene_shown = True
    draw_start_menu()
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

show_map = False  # Track if map is being shown

# --- LANDING STATE ---
landed_planet = None  # None if not landed, else the planet dict
landed_message_timer = 0  # Frames left to show landing message

# --- PLANETS SETUP ---
def get_planet_positions():
    planets = []
    for p in planet_data:
        angle = p["angle"]
        px = sun_pos[0] + p["orbit_radius"] * math.cos(angle)
        py = sun_pos[1] + p["orbit_radius"] * math.sin(angle)
        planets.append({
            "name": p["name"],
            "pos": (px, py),
            "color": p["color"],
            "material": p["material"],
            "radius": p["size"]
        })
    return planets

# --- INVENTORY PANEL SCROLLING ---
INVENTORY_PANEL_HEIGHT = 120
INVENTORY_PANEL_WIDTH = 320
INVENTORY_LINE_HEIGHT = 28
INVENTORY_VISIBLE_LINES = INVENTORY_PANEL_HEIGHT // INVENTORY_LINE_HEIGHT
inventory_scroll = 0

def clamp(val, minval, maxval):
    return max(minval, min(val, maxval))

# Game loop
running = True
in_game_menu = False
show_controls = False
selected_btn = None
while running:
    clock.tick(60) #60FPS

    # Update planet angles for orbit (slower)
    for p in planet_data:
        p["angle"] += 0.002 * p["speed"]  # Slower orbit
        if p["angle"] > 2 * math.pi:
            p["angle"] -= 2 * math.pi

    planets = get_planet_positions()

    # --- EVENT HANDLING ---
    mouse = pygame.mouse.get_pos()
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
            if event.button == 4:  # Scroll up
                inventory_scroll = clamp(inventory_scroll - 1, 0, max(0, len(inventory) - INVENTORY_VISIBLE_LINES))
            if event.button == 5:  # Scroll down
                inventory_scroll = clamp(inventory_scroll + 1, 0, max(0, len(inventory) - INVENTORY_VISIBLE_LINES))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                inventory_scroll = clamp(inventory_scroll - 1, 0, max(0, len(inventory) - INVENTORY_VISIBLE_LINES))
            if event.key == pygame.K_DOWN:
                inventory_scroll = clamp(inventory_scroll + 1, 0, max(0, len(inventory) - INVENTORY_VISIBLE_LINES))
            if event.key == pygame.K_m:
                show_map = not show_map
            if event.key == pygame.K_SPACE and landed_planet is not None:
                landed_planet = None  # Take off from planet
            if event.key == pygame.K_ESCAPE:
                in_game_menu = True
                selected_btn = None
                show_controls = False
    # --- IN-GAME MENU HANDLING ---
    if in_game_menu:
        btn_rects = draw_game_menu(selected_btn, show_controls)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_game_menu = False
                    show_controls = False
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                selected_btn = None
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(mx, my):
                        selected_btn = i
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_btn == 0:  # Resume
                    in_game_menu = False
                    show_controls = False
                elif selected_btn == 1:  # Controls
                    show_controls = not show_controls
                elif selected_btn == 2:  # Quit
                    pygame.quit()
                    sys.exit()
        continue  # Skip rest of game loop when menu is open
    # --- CHARACTER CONTROLLER ---
    keys = pygame.key.get_pressed()
    move_x, move_y = 0, 0
    if landed_planet is None:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_angle += 5  # Rotate left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_angle -= 5  # Rotate right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            rad = math.radians(player_angle)
            move_x += -player_speed * math.sin(rad)
            move_y += -player_speed * math.cos(rad)
    # If landed, player moves with planet
    if landed_planet is not None:
        # Find the current planet's new position
        for p in planets:
            if p["name"] == landed_planet["name"]:
                px, py = p["pos"]
                pr = p["radius"]
                # Keep player at the same angle and distance from planet center
                angle = math.atan2(player_pos[1] - py, player_pos[0] - px)
                player_pos[0] = px + (pr + player_size // 2) * math.cos(angle)
                player_pos[1] = py + (pr + player_size // 2) * math.sin(angle)
                landed_message_timer = 120  # Show message for 2 seconds (60 FPS)
                break
    else:
        # --- PLANET COLLISION (treat as walls/landing) ---
        next_pos = [player_pos[0] + move_x, player_pos[1] + move_y]
        landed = False
        for planet in planets:
            px, py = planet["pos"]
            pr = planet["radius"]
            dist = math.hypot(next_pos[0] - px, next_pos[1] - py)
            if dist < pr + player_size // 2:
                landed = True
                landed_planet = planet  # Land on this planet
                # Snap player to edge of planet
                angle_to_planet = math.atan2(next_pos[1] - py, next_pos[0] - px)
                next_pos[0] = px + (pr + player_size // 2) * math.cos(angle_to_planet)
                next_pos[1] = py + (pr + player_size // 2) * math.sin(angle_to_planet)
                landed_message_timer = 120  # Reset timer when landing
        if not landed:
            player_pos[0], player_pos[1] = next_pos[0], next_pos[1]
        else:
            player_pos[0], player_pos[1] = next_pos[0], next_pos[1]

    # --- PLANET INTERACTION & QUEST SYSTEM ---
    if current_quest < len(quests):
        quest = quests[current_quest]
        for planet in planets:
            px, py = planet["pos"]
            pr = planet["radius"]
            dist = math.hypot(player_pos[0] - px, player_pos[1] - py)
            if dist < pr + 10:  # Near a planet (10 px buffer)
                if keys[pygame.K_e]:  # Press E to collect
                    mat = planet["material"]
                    if planet["name"] == quest["planet"] and mat == quest["material"] and not quest["completed"]:
                        inventory[mat] = inventory.get(mat, 0) + 1
                        quest["collected"] += 1
                        if quest["collected"] >= quest["amount"]:
                            quest["completed"] = True
                            # Apply reward
                            if "speed" in quest["reward"]:
                                player_speed += quest["reward"]["speed"]
                            if "size" in quest["reward"]:
                                player_size += quest["reward"]["size"]
                                spaceship_img = pygame.transform.scale(spaceship_img, (player_size, player_size))
                            if "win" in quest["reward"]:
                                pass
                            current_quest += 1

    # --- UPGRADE EXAMPLE (optional, can be removed if using quest rewards) ---
    if keys[pygame.K_u]:  # Press U to upgrade speed if you have 2 Iron
        if inventory.get("Iron", 0) >= 2:
            player_speed += 1
            inventory["Iron"] -= 2

    # --- BASE REVENUE GENERATION ---
    for pname, base in bases.items():
        base['last_collected'] += 1
        if base['last_collected'] >= REVENUE_INTERVAL:
            revenue += int(BASE_REVENUE_BASE * (BASE_REVENUE_MULT ** (base['level']-1)))
            base['last_collected'] = 0

    # Keep player in world bounds
    player_pos[0] = max(0, min(WORLD_WIDTH - player_size, player_pos[0]))
    player_pos[1] = max(0, min(WORLD_HEIGHT - player_size, player_pos[1]))

    # --- CAMERA LOGIC ---
    cam_x = int(player_pos[0] + player_size // 2 - WIDTH // 2)
    cam_y = int(player_pos[1] + player_size // 2 - HEIGHT // 2)
    cam_x = max(0, min(WORLD_WIDTH - WIDTH, cam_x))
    cam_y = max(0, min(WORLD_HEIGHT - HEIGHT, cam_y))

    # --- DRAWING ---
    if show_map:
        # Draw solar system map overlay
        map_width, map_height = 400, 400
        map_surf = pygame.Surface((map_width, map_height))
        map_surf.fill((20, 20, 40))
        # Draw sun on map
        sun_mx = int(sun_pos[0] / WORLD_WIDTH * map_width)
        sun_my = int(sun_pos[1] / WORLD_HEIGHT * map_height)
        pygame.draw.circle(map_surf, sun_color, (sun_mx, sun_my), 18)
        font = pygame.font.SysFont(None, 20)
        sun_surf = font.render("Sun", True, WHITE)
        map_surf.blit(sun_surf, (sun_mx - 15, sun_my - 30))
        # Draw planets on map
        for planet in planets:
            px, py = planet["pos"]
            mx = int(px / WORLD_WIDTH * map_width)
            my = int(py / WORLD_HEIGHT * map_height)
            pygame.draw.circle(map_surf, planet["color"], (mx, my), 8)
            font = pygame.font.SysFont(None, 18)
            name_surf = font.render(planet["name"], True, WHITE)
            map_surf.blit(name_surf, (mx - 10, my - 20))
        # Draw player on map
        mx = int(player_pos[0] / WORLD_WIDTH * map_width)
        my = int(player_pos[1] / WORLD_HEIGHT * map_height)
        pygame.draw.circle(map_surf, (0,255,0), (mx, my), 6)
        # Blit map to screen center
        screen.blit(map_surf, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2))
        # Draw map border
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - map_width//2, HEIGHT//2 - map_height//2, map_width, map_height), 2)
        # Draw exit map prompt
        font = pygame.font.SysFont(None, 28)
        exit_surf = font.render("Press M to close map", True, WHITE)
        screen.blit(exit_surf, (WIDTH//2 - exit_surf.get_width()//2, HEIGHT//2 + map_height//2 + 10))
        pygame.display.flip()
        continue  # Skip rest of drawing/game logic when map is open

    # --- DRAWING --- (continued)
    screen.fill(BLACK)
    # Draw stars relative to camera
    for sx, sy in stars:
        if cam_x <= sx <= cam_x + WIDTH and cam_y <= sy <= cam_y + HEIGHT:
            pygame.draw.circle(screen, WHITE, (sx - cam_x, sy - cam_y), 2)
    # Draw sun
    pygame.draw.circle(screen, sun_color, (sun_pos[0] - cam_x, sun_pos[1] - cam_y), sun_radius)
    font = pygame.font.SysFont(None, 32)
    sun_surf = font.render("Sun", True, (255, 255, 255))
    screen.blit(sun_surf, (sun_pos[0] - cam_x - 30, sun_pos[1] - cam_y - sun_radius - 30))
    # Draw planets
    for planet in planets:
        px, py = planet["pos"]
        pr = planet["radius"]
        pygame.draw.circle(screen, planet["color"], (int(px - cam_x), int(py - cam_y)), pr)
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(planet["name"], True, WHITE)
        # Add a subtle shadow for planet names
        screen.blit(name_surf, (int(px - cam_x - 29), int(py - cam_y - pr - 29)))
        screen.blit(name_surf, (int(px - cam_x - 30), int(py - cam_y - pr - 30)))
    # Draw spaceship
    rotated_img = pygame.transform.rotate(spaceship_img, player_angle)
    rect = rotated_img.get_rect(center=(player_pos[0] - cam_x + player_size // 2, player_pos[1] - cam_y + player_size // 2))
    screen.blit(rotated_img, rect.topleft)
    # Draw a modern quest/objective panel at the bottom left
    quest_panel_width = 420
    quest_panel_height = 70
    quest_panel_x = 20
    quest_panel_y = HEIGHT - quest_panel_height - 20
    quest_panel = pygame.Surface((quest_panel_width, quest_panel_height), pygame.SRCALPHA)
    pygame.draw.rect(quest_panel, (30, 30, 60, 220), (0, 0, quest_panel_width, quest_panel_height), border_radius=18)
    pygame.draw.rect(quest_panel, (80, 80, 120, 120), (0, 0, quest_panel_width, quest_panel_height), 3, border_radius=18)
    font = pygame.font.SysFont(None, 28)
    if current_quest < len(quests):
        quest = quests[current_quest]
        quest_text = quest["desc"] + f" ({quest['collected']}/{quest['amount']})"
    else:
        quest_text = "All missions complete! You have saved the Federation!"
    quest_surf = font.render(quest_text, True, (255, 255, 120))
    quest_panel.blit(quest_surf, (22, 22))
    screen.blit(quest_panel, (quest_panel_x, quest_panel_y))
    # Draw inventory in a scrollable rounded box at the top right
    inv_panel = pygame.Surface((INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(inv_panel, (40, 40, 60, 200), (0, 0, INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT), border_radius=16)
    font = pygame.font.SysFont(None, 24)
    inv_items = list(inventory.items())
    visible_items = inv_items[inventory_scroll:inventory_scroll+INVENTORY_VISIBLE_LINES]
    for i, (k, v) in enumerate(visible_items):
        inv_surf = font.render(f"{k}: {v}", True, (180, 255, 180))
        inv_panel.blit(inv_surf, (12, 8 + i * INVENTORY_LINE_HEIGHT))
    # Draw scroll indicators if needed
    if inventory_scroll > 0:
        up_surf = font.render("▲", True, (255,255,255))
        inv_panel.blit(up_surf, (INVENTORY_PANEL_WIDTH - 28, 4))
    if inventory_scroll + INVENTORY_VISIBLE_LINES < len(inv_items):
        down_surf = font.render("▼", True, (255,255,255))
        inv_panel.blit(down_surf, (INVENTORY_PANEL_WIDTH - 28, INVENTORY_PANEL_HEIGHT - 28))
    screen.blit(inv_panel, (WIDTH - INVENTORY_PANEL_WIDTH - 20, 10))
    # Draw landing message with a drop shadow
    if landed_planet is not None and landed_message_timer > 0:
        font = pygame.font.SysFont(None, 32)
        land_surf = font.render(f"Landed on {landed_planet['name']} (Press SPACE to take off)", True, (255,255,0))
        shadow = font.render(f"Landed on {landed_planet['name']} (Press SPACE to take off)", True, (60,60,0))
        screen.blit(shadow, (WIDTH//2 - land_surf.get_width()//2 + 2, HEIGHT - 118))
        screen.blit(land_surf, (WIDTH//2 - land_surf.get_width()//2, HEIGHT - 120))
        landed_message_timer -= 1

    # --- UI BUTTONS: BUILD BASE, UPGRADE BASE, UPGRADE SHIP ---
    build_btn_rect = None
    upgrade_base_btn_rect = None
    upgrade_ship_btn_rect = None
    base_on_planet = landed_planet and landed_planet['name'] in bases
    if landed_planet:
        btn_x, btn_y = 40, HEIGHT - 180
        btn_w, btn_h = 180, 38
        build_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (60,180,60) if not base_on_planet else (120,120,120), build_btn_rect, border_radius=12)
        font = pygame.font.SysFont(None, 28)
        label = "Build Base" if not base_on_planet else "Base Built"
        btn_surf = font.render(label, True, (255,255,255))
        screen.blit(btn_surf, (btn_x + 18, btn_y + 6))
        if base_on_planet:
            upgrade_base_btn_rect = pygame.Rect(btn_x, btn_y+48, btn_w, btn_h)
            pygame.draw.rect(screen, (60,60,180), upgrade_base_btn_rect, border_radius=12)
            upg_surf = font.render(f"Upgrade Base ({BASE_UPGRADE_COST})", True, (255,255,255))
            screen.blit(upg_surf, (btn_x + 8, btn_y+54))
    upgrade_ship_btn_rect = pygame.Rect(WIDTH-240, HEIGHT-70, 200, 38)
    pygame.draw.rect(screen, (180,120,60), upgrade_ship_btn_rect, border_radius=12)
    font = pygame.font.SysFont(None, 28)
    ship_surf = font.render(f"Upgrade Ship ({SHIP_UPGRADE_COST})", True, (255,255,255))
    screen.blit(ship_surf, (WIDTH-230, HEIGHT-64))
    font = pygame.font.SysFont(None, 28)
    rev_surf = font.render(f"Revenue: {revenue}", True, (255,255,120))
    screen.blit(rev_surf, (WIDTH-230, HEIGHT-110))
    # --- BUTTON LOGIC ---
    if click:
        if landed_planet and build_btn_rect and build_btn_rect.collidepoint(mouse):
            if not base_on_planet:
                bases[landed_planet['name']] = {'level': 1, 'last_collected': 0}
        if landed_planet and base_on_planet and upgrade_base_btn_rect and upgrade_base_btn_rect.collidepoint(mouse):
            if revenue >= BASE_UPGRADE_COST:
                bases[landed_planet['name']]['level'] += 1
                revenue -= BASE_UPGRADE_COST
        if upgrade_ship_btn_rect and upgrade_ship_btn_rect.collidepoint(mouse):
            if revenue >= SHIP_UPGRADE_COST:
                player_speed += 1
                player_size += 2
                spaceship_img = pygame.transform.scale(spaceship_img, (player_size, player_size))
                revenue -= SHIP_UPGRADE_COST

    pygame.display.flip()

pygame.quit()
sys.exit()