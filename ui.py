"""
Handles all UI drawing functions: menus, quest bar, health/fuel bars, buttons, tech tree, etc.
"""
import pygame
from assets import WHITE, BLACK, get_font

def draw_start_menu(screen):
    screen.fill(BLACK)
    font_big = get_font(64)
    font_small = get_font(32)
    title = font_big.render("Space Explorer", True, WHITE)
    prompt = font_small.render("Press ENTER to Start", True, WHITE)
    controls = [
        "Controls:",
        "Arrow keys / WASD - Move & Rotate",
        "E - Collect material at planet",
        "U - Upgrade (if available)",
        "ESC - Quit"
    ]
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, screen.get_height() // 2 - 120))
    screen.blit(prompt, (screen.get_width() // 2 - prompt.get_width() // 2, screen.get_height() // 2 - 40))
    for i, line in enumerate(controls):
        ctrl = font_small.render(line, True, WHITE)
        screen.blit(ctrl, (screen.get_width() // 2 - ctrl.get_width() // 2, screen.get_height() // 2 + 30 + i * 30))
    pygame.display.flip()

def draw_game_menu(screen, selected=None, show_controls=False):
    menu_width, menu_height = 400, 320
    menu_x = screen.get_width() // 2 - menu_width // 2 - 100
    menu_y = screen.get_height() // 2 - menu_height // 2
    menu_panel = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
    menu_panel.fill((30, 30, 60, 240))
    pygame.draw.rect(menu_panel, (80, 80, 120, 255), (0, 0, menu_width, menu_height), border_radius=18)
    font = get_font(48)
    title = font.render("Game Menu", True, (255,255,255))
    menu_panel.blit(title, (menu_width//2 - title.get_width()//2, 30))
    font_btn = get_font(36)
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
        ctrl_width, ctrl_height = 340, 320
        ctrl_x = menu_x + menu_width + 20
        ctrl_y = menu_y + 20
        ctrl_panel = pygame.Surface((ctrl_width, ctrl_height), pygame.SRCALPHA)
        ctrl_panel.fill((20, 40, 30, 230))
        pygame.draw.rect(ctrl_panel, (60, 120, 80, 255), (0, 0, ctrl_width, ctrl_height), border_radius=16)
        font_ctrl = get_font(32)
        ctrl_title = font_ctrl.render("Controls", True, (255,255,200))
        ctrl_panel.blit(ctrl_title, (ctrl_width//2 - ctrl_title.get_width()//2, 20))
        # Updated controls list
        controls = [
            "Steer Ship: Move your mouse",
            "Accelerate: W",
            "Reverse: S",
            "Land: Approach a planet and stop",
            "Take Off: SPACE (when landed)",
            "Show Map: M",
            "Open Menu: ESC",
            "Open Inventory: I",
            "Place/Remove Marker: C (near planet)",
            "Follow Compass/Panel to Marker"
        ]
        font_small = get_font(22)
        for i, line in enumerate(controls):
            surf = font_small.render(line, True, (220,255,220))
            ctrl_panel.blit(surf, (24, 64 + i*28))
        screen.blit(ctrl_panel, (ctrl_x, ctrl_y))
    return btn_rects

def draw_quest_bar(screen, current_quest, quests, WIDTH):
    # Modern quest bar at bottom with rounded corners and subtle shadow
    bar_h = 54
    bar_rect = pygame.Rect(18, screen.get_height() - bar_h - 18, WIDTH-36, bar_h)
    shadow = pygame.Surface((bar_rect.width+8, bar_rect.height+8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0,0,0,80), shadow.get_rect(), border_radius=16)
    screen.blit(shadow, (bar_rect.x-4, bar_rect.y-4))
    pygame.draw.rect(screen, (38,44,68), bar_rect, border_radius=16)
    pygame.draw.rect(screen, (120,180,255), bar_rect, 3, border_radius=16)
    font = pygame.font.SysFont("Segoe UI", 28, bold=True)
    if current_quest < len(quests):
        quest = quests[current_quest]
        text = f"Quest: Collect {quest['amount']} {quest['material']} from {quest['planet']} ({quest['collected']}/{quest['amount']})"
        surf = font.render(text, True, (255,255,255))
        screen.blit(surf, (bar_rect.x+24, bar_rect.y+12))
    else:
        surf = font.render("All quests complete!", True, (180,255,180))
        screen.blit(surf, (bar_rect.x+24, bar_rect.y+12))

def draw_health_fuel_bars(screen, health, max_health, fuel, max_fuel):
    # Modern health/fuel bars at top right with icons and gradients
    bar_w, bar_h = 180, 20
    x, y = screen.get_width() - bar_w - 38, 18
    # Health
    bg_rect = pygame.Rect(x, y, bar_w, bar_h)
    pygame.draw.rect(screen, (60,80,120), bg_rect, border_radius=10)
    grad = pygame.Surface((int(bar_w*health/max_health), bar_h))
    for i in range(bar_h):
        c = (120,255-2*i,120)
        pygame.draw.line(grad, c, (0,i), (grad.get_width(),i))
    screen.blit(grad, (x, y))
    pygame.draw.rect(screen, (120,255,120), (x, y, int(bar_w*health/max_health), bar_h), 2, border_radius=10)
    font = pygame.font.SysFont("Segoe UI", 20)
    htxt = font.render(f"HP", True, (0,0,0))
    screen.blit(htxt, (x-32, y+1))
    # Fuel
    y += bar_h + 12
    bg_rect = pygame.Rect(x, y, bar_w, bar_h)
    pygame.draw.rect(screen, (60,80,120), bg_rect, border_radius=10)
    grad = pygame.Surface((int(bar_w*fuel/max_fuel), bar_h))
    for i in range(bar_h):
        c = (120,180,255-2*i)
        pygame.draw.line(grad, c, (0,i), (grad.get_width(),i))
    screen.blit(grad, (x, y))
    pygame.draw.rect(screen, (120,180,255), (x, y, int(bar_w*fuel/max_fuel), bar_h), 2, border_radius=10)
    ftxt = font.render(f"Fuel", True, (0,0,0))
    screen.blit(ftxt, (x-48, y+1))

def draw_menu(screen, menu_open):
    if menu_open:
        pygame.draw.rect(screen, (30,30,30), (200, 100, 400, 400))
        font = get_font(36)
        text = font.render("Game Menu", True, WHITE)
        screen.blit(text, (320, 120))
        # Add more menu items as needed

def draw_tech_tree_button(screen, WIDTH):
    tech_btn_rect = pygame.Rect(WIDTH-170, 18, 140, 40)
    shadow = pygame.Surface((tech_btn_rect.width+6, tech_btn_rect.height+6), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0,0,0,80), shadow.get_rect(), border_radius=12)
    screen.blit(shadow, (tech_btn_rect.x-3, tech_btn_rect.y-3))
    pygame.draw.rect(screen, (60,120,200), tech_btn_rect, border_radius=12)
    pygame.draw.rect(screen, (120,180,255), tech_btn_rect, 2, border_radius=12)
    font = get_font(26)
    tech_surf = font.render("Tech Tree", True, (255,255,255))
    screen.blit(tech_surf, (tech_btn_rect.x + tech_btn_rect.width//2 - tech_surf.get_width()//2, tech_btn_rect.y + tech_btn_rect.height//2 - tech_surf.get_height()//2))
    return tech_btn_rect

def draw_tech_tree(screen, WIDTH, HEIGHT, tech_tree_state, upgrades, unlock_callback=None):
    # Draw a modern tech tree modal at the bottom of the screen with ship upgrades
    panel_width, panel_height = 600, 220
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT - panel_height - 32
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((30, 30, 60, 240))
    pygame.draw.rect(panel, (80, 120, 200, 255), (0, 0, panel_width, panel_height), border_radius=18)
    font = get_font(36)
    title = font.render("Tech Tree", True, (255,255,255))
    panel.blit(title, (panel_width//2 - title.get_width()//2, 18))
    # Draw upgrades as buttons
    font_btn = get_font(26)
    btn_w, btn_h = 150, 54
    btn_gap = 24
    btns = []
    for i, (upg, data) in enumerate(upgrades.items()):
        bx = 32 + i * (btn_w + btn_gap)
        by = 80
        btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
        # Button color based on unlocked
        unlocked = data['level'] > 0
        color = (120, 220, 120) if unlocked else (120, 180, 255)
        pygame.draw.rect(panel, color, btn_rect, border_radius=12)
        # Upgrade name and level
        upg_txt = font_btn.render(f"{upg} (Lv{data['level']})", True, (30,30,30))
        panel.blit(upg_txt, (bx + 12, by + 6))
        # Description
        desc_font = get_font(18)
        desc = desc_font.render(data['desc'], True, (40,40,40))
        panel.blit(desc, (bx + 12, by + 32))
        btns.append((btn_rect.move(panel_x, panel_y), upg))
    # Footer
    font_footer = get_font(20)
    close = font_footer.render("Press ESC to close | Click upgrade to unlock", True, (180,200,220))
    panel.blit(close, (panel_width//2 - close.get_width()//2, panel_height - 38))
    screen.blit(panel, (panel_x, panel_y))
    return btns

def draw_buttons(screen, buttons):
    font = get_font(22)
    for btn in buttons:
        pygame.draw.rect(screen, btn['color'], btn['rect'])
        text = font.render(btn['label'], True, BLACK)
        screen.blit(text, (btn['rect'].x+10, btn['rect'].y+5))

def show_cutscene(screen, WIDTH, HEIGHT):
    import pygame, sys
    cutscene_duration = 5.5  # seconds
    start_time = pygame.time.get_ticks()
    font = get_font(38)
    font_small = get_font(28)
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

def draw_base_buttons(screen, HEIGHT, landed_planet, base_on_planet):
    build_btn_rect = None
    upgrade_base_btn_rect = None
    upgrade_ship_btn_rect = None
    font_btn = get_font(28)
    btn_y = HEIGHT - 110
    if landed_planet:
        pname = landed_planet['name']
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
        upgrade_ship_btn_rect = pygame.Rect(240, btn_y, 180, 44)
        pygame.draw.rect(screen, (80,120,220), upgrade_ship_btn_rect, border_radius=10)
        ship_txt = font_btn.render("Upgrade Ship", True, (255,255,255))
        screen.blit(ship_txt, (upgrade_ship_btn_rect.x + 10, upgrade_ship_btn_rect.y + 8))
    return build_btn_rect, upgrade_base_btn_rect, upgrade_ship_btn_rect

def draw_inventory(screen, inventory, WIDTH, HEIGHT, scroll_offset=0):
    # Draw a modern modal inventory window with scroll support and polish
    modal_w, modal_h = 480, 400
    modal_x = WIDTH // 2 - modal_w // 2
    modal_y = HEIGHT // 2 - modal_h // 2
    # Shadow
    shadow_rect = pygame.Rect(modal_x+8, modal_y+10, modal_w, modal_h)
    pygame.draw.rect(screen, (0,0,0,120), shadow_rect, border_radius=22)
    # Main panel
    pygame.draw.rect(screen, (38, 44, 68), (modal_x, modal_y, modal_w, modal_h), border_radius=22)
    pygame.draw.rect(screen, (120, 180, 255), (modal_x, modal_y, modal_w, modal_h), 5, border_radius=22)
    # Title
    font = pygame.font.SysFont("Segoe UI", 48, bold=True)
    title = font.render("Inventory", True, (255,255,255))
    screen.blit(title, (modal_x + modal_w//2 - title.get_width()//2, modal_y + 22))
    # Items
    font = pygame.font.SysFont("Segoe UI", 30)
    # --- Ensure all possible materials are shown if collected at least once ---
    items = [(item, count) for item, count in inventory.items() if count > 0]
    items_per_page = 7
    start = scroll_offset
    end = min(start + items_per_page, len(items))
    if not items:
        empty = font.render("(Empty)", True, (180,200,220))
        screen.blit(empty, (modal_x + modal_w//2 - empty.get_width()//2, modal_y + 110))
    else:
        for i, (item, count) in enumerate(items[start:end]):
            line = f"{item}: {count}"
            pygame.draw.rect(screen, (60, 80, 120), (modal_x+36, modal_y+90+i*44, modal_w-72, 38), border_radius=12)
            surf = font.render(line, True, (220, 240, 255))
            screen.blit(surf, (modal_x + 52, modal_y + 96 + i*44))
    # Footer
    font = pygame.font.SysFont("Segoe UI", 22)
    close = font.render("Press I or ESC to close | Scroll: Up/Down", True, (180,200,220))
    screen.blit(close, (modal_x + modal_w//2 - close.get_width()//2, modal_y + modal_h - 44))
    # Scroll indicators
    arrow_color = (120, 180, 255)
    if start > 0:
        pygame.draw.polygon(screen, arrow_color, [
            (modal_x + modal_w - 44, modal_y + 100),
            (modal_x + modal_w - 20, modal_y + 100),
            (modal_x + modal_w - 32, modal_y + 76)
        ])
    if end < len(items):
        pygame.draw.polygon(screen, arrow_color, [
            (modal_x + modal_w - 44, modal_y + 100 + items_per_page*44),
            (modal_x + modal_w - 20, modal_y + 100 + items_per_page*44),
            (modal_x + modal_w - 32, modal_y + 124 + items_per_page*44)
        ])

def draw_game_background(screen, stars, cam_x, cam_y, WIDTH, HEIGHT, SUN_COLOR, SUN_POS, SUN_RADIUS, WHITE):
    # Draw a subtle gradient background
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        c = int(20 + 30 * (y / HEIGHT))
        pygame.draw.line(bg, (c, c, 48), (0, y), (WIDTH, y))
    screen.blit(bg, (0, 0))
    # Draw stars with glow
    for sx, sy in stars:
        if cam_x <= sx <= cam_x + WIDTH and cam_y <= sy <= cam_y + HEIGHT:
            pygame.draw.circle(screen, (255,255,255,40), (sx - cam_x, sy - cam_y), 6)
            pygame.draw.circle(screen, WHITE, (sx - cam_x, sy - cam_y), 2)
    # Draw sun with glow
    sun_pos = (SUN_POS[0] - cam_x, SUN_POS[1] - cam_y)
    for r in range(SUN_RADIUS+30, SUN_RADIUS, -6):
        alpha = max(0, 80 - (SUN_RADIUS+30-r)*4)
        glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SUN_COLOR, alpha), (r, r), r)
        screen.blit(glow, (sun_pos[0]-r, sun_pos[1]-r), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(screen, SUN_COLOR, sun_pos, SUN_RADIUS)

# Remove spaceship image loading from ui.py, move to assets.py for proper modularity

# Add more UI helpers as needed
