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
WORLD_WIDTH, WORLD_HEIGHT = 3000, 3000  # Make the world much larger than the screen

# Generate some stars for the background
stars = [(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(300)]

# Player settings
player_size = 40
player_pos = [WORLD_WIDTH // 2, WORLD_HEIGHT // 2]  # Start in the middle of the world
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

# --- PLANETS SETUP ---
planets = [
    {"name": "Mercury", "pos": (500, 800), "color": (200, 200, 200), "material": "Iron"},
    {"name": "Venus",   "pos": (1200, 400), "color": (255, 200, 0),  "material": "Sulfur"},
    {"name": "Earth",   "pos": (2000, 1500), "color": (0, 100, 255), "material": "Water"},
    {"name": "Mars",    "pos": (2500, 2200), "color": (255, 80, 0),  "material": "Silicon"},
]

# --- STORY & QUEST SYSTEM ---
story = [
    "You are the last explorer of the Solar Federation.",
    "Your mission: gather rare materials to repair the Federation's beacon and call for help.",
    "Travel to each planet, collect their unique resources, and upgrade your ship to reach distant worlds.",
    "Good luck, captain!"
]

quests = [
    {
        "desc": "Collect 3 Iron from Mercury to repair your hull.",
        "planet": "Mercury",
        "material": "Iron",
        "amount": 3,
        "collected": 0,
        "completed": False,
        "reward": {"speed": 1}
    },
    {
        "desc": "Collect 2 Sulfur from Venus to upgrade your thrusters.",
        "planet": "Venus",
        "material": "Sulfur",
        "amount": 2,
        "collected": 0,
        "completed": False,
        "reward": {"speed": 1}
    },
    {
        "desc": "Collect 2 Water from Earth to refill your life support.",
        "planet": "Earth",
        "material": "Water",
        "amount": 2,
        "collected": 0,
        "completed": False,
        "reward": {"size": 10}
    },
    {
        "desc": "Collect 4 Silicon from Mars to repair the Federation beacon.",
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

# --- START MENU LOOP ---
in_menu = True
while in_menu:
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

# Game loop
running = True
while running:
    clock.tick(60) #60FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                show_map = not show_map

    # --- CHARACTER CONTROLLER (same as before) ---
    keys = pygame.key.get_pressed()
    move_x, move_y = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_angle += 5  # Rotate left
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_angle -= 5  # Rotate right
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        rad = math.radians(player_angle)
        move_x += -player_speed * math.sin(rad)
        move_y += -player_speed * math.cos(rad)

    # --- PLANET COLLISION (treat as walls/landing) ---
    next_pos = [player_pos[0] + move_x, player_pos[1] + move_y]
    landed = False
    for planet in planets:
        px, py = planet["pos"]
        dist = math.hypot(next_pos[0] - px, next_pos[1] - py)
        if dist < 50 + player_size // 2:  # 50 is planet radius
            landed = True
            # Snap player to edge of planet
            angle_to_planet = math.atan2(next_pos[1] - py, next_pos[0] - px)
            next_pos[0] = px + (50 + player_size // 2) * math.cos(angle_to_planet)
            next_pos[1] = py + (50 + player_size // 2) * math.sin(angle_to_planet)
    if not landed:
        player_pos[0], player_pos[1] = next_pos[0], next_pos[1]
    else:
        player_pos[0], player_pos[1] = next_pos[0], next_pos[1]

    # --- PLANET INTERACTION & QUEST SYSTEM ---
    if current_quest < len(quests):
        quest = quests[current_quest]
        for planet in planets:
            px, py = planet["pos"]
            dist = math.hypot(player_pos[0] - px, player_pos[1] - py)
            if dist < 80:  # Near a planet
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
                                # End game or show win message
                                pass
                            current_quest += 1  # Move to next quest

    # --- UPGRADE EXAMPLE (optional, can be removed if using quest rewards) ---
    if keys[pygame.K_u]:  # Press U to upgrade speed if you have 2 Iron
        if inventory.get("Iron", 0) >= 2:
            player_speed += 1
            inventory["Iron"] -= 2

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
    # Draw planets
    for planet in planets:
        px, py = planet["pos"]
        pygame.draw.circle(screen, planet["color"], (px - cam_x, py - cam_y), 50)
        font = pygame.font.SysFont(None, 24)
        name_surf = font.render(planet["name"], True, WHITE)
        screen.blit(name_surf, (px - cam_x - 30, py - cam_y - 60))
    # Draw spaceship
    rotated_img = pygame.transform.rotate(spaceship_img, player_angle)
    rect = rotated_img.get_rect(center=(player_pos[0] - cam_x + player_size // 2, player_pos[1] - cam_y + player_size // 2))
    screen.blit(rotated_img, rect.topleft)
    # Draw story (top of screen)
    font = pygame.font.SysFont(None, 24)
    for i, line in enumerate(story):
        story_surf = font.render(line, True, WHITE)
        screen.blit(story_surf, (20, 10 + i * 22))
    # Draw quest info
    font = pygame.font.SysFont(None, 28)
    if current_quest < len(quests):
        quest = quests[current_quest]
        quest_text = quest["desc"] + f" ({quest['collected']}/{quest['amount']})"
    else:
        quest_text = "All missions complete! You have saved the Federation!"
    quest_surf = font.render(quest_text, True, WHITE)
    screen.blit(quest_surf, (20, HEIGHT - 70))
    # Draw inventory
    inv_text = "Inventory: " + ", ".join([f"{k}:{v}" for k, v in inventory.items()])
    inv_surf = font.render(inv_text, True, WHITE)
    screen.blit(inv_surf, (20, HEIGHT - 40))
    pygame.display.flip()

pygame.quit()
sys.exit()