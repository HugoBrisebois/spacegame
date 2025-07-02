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

# --- PLAYER STATS ---
player_health = 100
player_max_health = 100
player_fuel = 100
player_max_fuel = 100
player_fuel_efficiency = 1.0  # Lower is better
# --- TECH TREE ---
tech_tree_open = False
tech_upgrades = {
    'Speed': {'level': 0, 'max': 5, 'cost': 150, 'desc': 'Increase ship speed'},
    'Size': {'level': 0, 'max': 3, 'cost': 200, 'desc': 'Increase ship size'},
    'Fuel Tank': {'level': 0, 'max': 3, 'cost': 120, 'desc': 'Increase max fuel'},
    'Fuel Efficiency': {'level': 0, 'max': 4, 'cost': 180, 'desc': 'Reduce fuel use'},
    'Max Health': {'level': 0, 'max': 3, 'cost': 180, 'desc': 'Increase max health'},
}

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

# --- QUEST BAR DRAWING ---
def draw_quest_bar():
    # Draw a modern quest bar at the top of the screen
    bar_width, bar_height = WIDTH - 80, 48
    bar_x, bar_y = 40, 12
    bar_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    # Semi-transparent background with drop shadow
    shadow = pygame.Surface((bar_width+8, bar_height+8), pygame.SRCALPHA)
    shadow.fill((0,0,0,80))
    screen.blit(shadow, (bar_x-4, bar_y-4))
    bar_surf.fill((40, 60, 120, 210))
    pygame.draw.rect(bar_surf, (80, 120, 200, 255), (0, 0, bar_width, bar_height), border_radius=16)
    # Quest text
    font = pygame.font.SysFont(None, 30)
    if current_quest < len(quests):
        quest = quests[current_quest]
        quest_text = quest['desc']
        progress = f"({quest['collected']}/{quest['amount']})" if not quest['completed'] else "(Completed)"
        text = f"Objective: {quest_text}  {progress}"
    else:
        text = "All quests complete! You have secured the future of humanity."
    text_surf = font.render(text, True, (255,255,255))
    bar_surf.blit(text_surf, (24, bar_height//2 - text_surf.get_height()//2))
    screen.blit(bar_surf, (bar_x, bar_y))

def draw_health_fuel_bars():
    # Draw health and fuel bars in the top left
    bar_x, bar_y = 28, 68
    bar_width, bar_height = 220, 22
    spacing = 14
    font = pygame.font.SysFont(None, 22)
    # Health bar
    health_ratio = player_health / player_max_health if player_max_health else 0
    health_bg = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    health_bg.fill((0,0,0,120))
    pygame.draw.rect(health_bg, (200,40,40,255), (0,0,int(bar_width*health_ratio),bar_height), border_radius=10)
    pygame.draw.rect(health_bg, (255,80,80,255), (0,0,int(bar_width*health_ratio),bar_height), 2, border_radius=10)
    screen.blit(health_bg, (bar_x, bar_y))
    health_text = font.render(f"Health: {int(player_health)}/{player_max_health}", True, (255,255,255))
    screen.blit(health_text, (bar_x+8, bar_y+2))
    # Fuel bar
    fuel_ratio = player_fuel / player_max_fuel if player_max_fuel else 0
    fuel_bg = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    fuel_bg.fill((0,0,0,120))
    pygame.draw.rect(fuel_bg, (40,120,200,255), (0,0,int(bar_width*fuel_ratio),bar_height), border_radius=10)
    pygame.draw.rect(fuel_bg, (80,180,255,255), (0,0,int(bar_width*fuel_ratio),bar_height), 2, border_radius=10)
    screen.blit(fuel_bg, (bar_x, bar_y+bar_height+spacing))
    fuel_text = font.render(f"Fuel: {int(player_fuel)}/{player_max_fuel}", True, (255,255,255))
    screen.blit(fuel_text, (bar_x+8, bar_y+bar_height+spacing+2))

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
    # --- IN-GAME MENU HANDLING (move to top of loop for proper blocking) ---
    if in_game_menu:
        btn_rects = draw_game_menu(selected_btn, show_controls)
        pygame.display.flip()
        menu_running = True
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    menu_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_game_menu = False
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
                        in_game_menu = False
                        show_controls = False
                        menu_running = False
                    elif selected_btn == 1:  # Controls
                        show_controls = not show_controls
                        btn_rects = draw_game_menu(selected_btn, show_controls)
                        pygame.display.flip()
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
    rect = rotated_img.get_rect(center=(player_pos[0] - cam_x + player_size // 2, player_pos[1] - cam_x + player_size // 2))
    screen.blit(rotated_img, rect.topleft)
    draw_quest_bar()
    draw_health_fuel_bars()

    # --- BASE BUTTONS ---
    build_btn_rect = None
    upgrade_base_btn_rect = None
    upgrade_ship_btn_rect = None
    base_on_planet = False
    if landed_planet:
        pname = landed_planet['name']
        base_on_planet = pname in bases
        font_btn = pygame.font.SysFont(None, 28)
        btn_y = HEIGHT - 110
        if not base_on_planet:
            build_btn_rect = pygame.Rect(40, btn_y, 180, 44)
            pygame.draw.rect(screen, (60,200,100), build_btn_rect, border_radius=10)
            build_txt = font_btn.render("Build Base", True, (255,255,255))
            screen.blit(build_txt, (build_btn_rect.x + 20, build_btn_rect.y + 8))
        else:
            upgrade_base_btn_rect = pygame.Rect(40, btn_y, 180, 44)
            pygame.draw.rect(screen, (200,180,60), upgrade_base_btn_rect, border_radius=10)
            upg_txt = font_btn.render("Upgrade Base", True, (255,255,255))
            screen.blit(upg_txt, (upgrade_base_btn_rect.x + 10, upgrade_base_btn_rect.y + 8))
        # Ship upgrade button
        upgrade_ship_btn_rect = pygame.Rect(240, btn_y, 180, 44)
        pygame.draw.rect(screen, (80,120,220), upgrade_ship_btn_rect, border_radius=10)
        ship_txt = font_btn.render("Upgrade Ship", True, (255,255,255))
        screen.blit(ship_txt, (upgrade_ship_btn_rect.x + 10, upgrade_ship_btn_rect.y + 8))

    # Tech tree button (top right)
    tech_btn_rect = pygame.Rect(WIDTH-160, 18, 130, 38)
    pygame.draw.rect(screen, (60,120,200), tech_btn_rect, border_radius=12)
    font = pygame.font.SysFont(None, 26)
    tech_surf = font.render("Tech Tree", True, (255,255,255))
    screen.blit(tech_surf, (WIDTH-150, 26))
    # Tech tree modal
    if tech_tree_open:
        close_rect = draw_tech_tree()
    # --- TECH TREE DRAW FUNCTION ---
    def draw_tech_tree():
        panel_width, panel_height = 520, 420
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((30, 30, 60, 240))
        pygame.draw.rect(panel, (80, 120, 200, 255), (0, 0, panel_width, panel_height), border_radius=18)
        font = pygame.font.SysFont(None, 40)
        title = font.render("Tech Tree", True, (255,255,255))
        panel.blit(title, (panel_width//2 - title.get_width()//2, 24))
        font2 = pygame.font.SysFont(None, 28)
        font3 = pygame.font.SysFont(None, 22)
        y = 80
        upg_btns = []
        for i, (name, upg) in enumerate(tech_upgrades.items()):
            desc = upg['desc']
            level = upg['level']
            max_level = upg['max']
            cost = upg['cost']
            color = (180,255,180) if level < max_level else (180,180,180)
            txt = f"{name} ({level}/{max_level})"
            txt_surf = font2.render(txt, True, color)
            panel.blit(txt_surf, (40, y))
            desc_surf = font3.render(desc, True, (220,220,255))
            panel.blit(desc_surf, (40, y+28))
            btn_rect = pygame.Rect(panel_x+340, panel_y+y, 120, 36)
            upg['_rect'] = btn_rect
            btn_color = (60,200,100) if level < max_level and revenue >= cost else (120,120,120)
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
            btn_txt = "Upgrade" if level < max_level else "Maxed"
            btn_txt_surf = font3.render(btn_txt, True, (255,255,255))
            screen.blit(btn_txt_surf, (btn_rect.x + 16, btn_rect.y + 7))
            cost_txt = f"{cost} revenue"
            cost_surf = font3.render(cost_txt, True, (255,255,180))
            screen.blit(cost_surf, (btn_rect.x + 16, btn_rect.y + 22))
            upg_btns.append(btn_rect)
            y += 70
        # Draw panel to screen
        screen.blit(panel, (panel_x, panel_y))
        # Draw close button
        close_rect = pygame.Rect(panel_x + panel_width - 44, panel_y + 12, 32, 32)
        pygame.draw.rect(screen, (200,60,60), close_rect, border_radius=8)
        font_close = pygame.font.SysFont(None, 32)
        close_surf = font_close.render("X", True, (255,255,255))
        screen.blit(close_surf, (close_rect.x + 7, close_rect.y + 2))
        pygame.display.flip()
        return close_rect

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
        if tech_btn_rect.collidepoint(mouse):
            tech_tree_open = True
        if tech_tree_open:
            if close_rect.collidepoint(mouse):
                tech_tree_open = False
            for name, upg in tech_upgrades.items():
                if upg['_rect'].collidepoint(mouse):
                    if upg['level'] < upg['max'] and revenue >= upg['cost']:
                        upg['level'] += 1
                        revenue -= upg['cost']
                        if name == 'Speed':
                            player_speed += 1
                        elif name == 'Size':
                            player_size += 4
                            spaceship_img = pygame.transform.scale(spaceship_img, (player_size, player_size))
                        elif name == 'Fuel Tank':
                            player_max_fuel += 40
                        elif name == 'Fuel Efficiency':
                            player_fuel_efficiency *= 0.85
                        elif name == 'Max Health':
                            player_max_health += 30
                            player_health = player_max_health

    # --- FUEL CONSUMPTION ---
    if landed_planet is None:
        if move_x != 0 or move_y != 0:
            player_fuel -= 0.12 * player_fuel_efficiency
            if player_fuel < 0:
                player_fuel = 0
    # Clamp health/fuel
    player_health = max(0, min(player_max_health, player_health))
    player_fuel = max(0, min(player_max_fuel, player_fuel))

pygame.quit()
sys.exit()