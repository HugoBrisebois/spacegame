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
        ctrl_width, ctrl_height = 340, 260
        ctrl_x = menu_x + menu_width + 20
        ctrl_y = menu_y + 20
        ctrl_panel = pygame.Surface((ctrl_width, ctrl_height), pygame.SRCALPHA)
        ctrl_panel.fill((20, 40, 30, 230))
        pygame.draw.rect(ctrl_panel, (60, 120, 80, 255), (0, 0, ctrl_width, ctrl_height), border_radius=16)
        font_ctrl = get_font(32)
        ctrl_title = font_ctrl.render("Controls", True, (255,255,200))
        ctrl_panel.blit(ctrl_title, (ctrl_width//2 - ctrl_title.get_width()//2, 20))
        # Add more controls as needed
        screen.blit(ctrl_panel, (ctrl_x, ctrl_y))

def draw_quest_bar(screen, current_quest, quests, WIDTH):
    bar_width, bar_height = WIDTH - 80, 48
    bar_x, bar_y = 40, 12
    bar_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    shadow = pygame.Surface((bar_width+8, bar_height+8), pygame.SRCALPHA)
    shadow.fill((0,0,0,80))
    screen.blit(shadow, (bar_x-4, bar_y-4))
    bar_surf.fill((40, 60, 120, 210))
    pygame.draw.rect(bar_surf, (80, 120, 200, 255), (0, 0, bar_width, bar_height), border_radius=16)
    font = get_font(30)
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

def draw_health_fuel_bars(screen, player_health, player_max_health, player_fuel, player_max_fuel):
    bar_x, bar_y = 28, 68
    bar_width, bar_height = 220, 22
    spacing = 14
    font = get_font(22)
    health_ratio = player_health / player_max_health if player_max_health else 0
    health_bg = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    health_bg.fill((0,0,0,120))
    pygame.draw.rect(health_bg, (200,40,40,255), (0,0,int(bar_width*health_ratio),bar_height), border_radius=10)
    pygame.draw.rect(health_bg, (255,80,80,255), (0,0,int(bar_width*health_ratio),bar_height), 2, border_radius=10)
    screen.blit(health_bg, (bar_x, bar_y))
    health_text = font.render(f"Health: {int(player_health)}/{player_max_health}", True, (255,255,255))
    screen.blit(health_text, (bar_x+8, bar_y+2))
    fuel_ratio = player_fuel / player_max_fuel if player_max_fuel else 0
    fuel_bg = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    fuel_bg.fill((0,0,0,120))
    pygame.draw.rect(fuel_bg, (40,120,200,255), (0,0,int(bar_width*fuel_ratio),bar_height), border_radius=10)
    pygame.draw.rect(fuel_bg, (80,180,255,255), (0,0,int(bar_width*fuel_ratio),bar_height), 2, border_radius=10)
    screen.blit(fuel_bg, (bar_x, bar_y+bar_height+spacing))
    fuel_text = font.render(f"Fuel: {int(player_fuel)}/{player_max_fuel}", True, (255,255,255))
    screen.blit(fuel_text, (bar_x+8, bar_y+bar_height+spacing+2))

def draw_menu(screen, menu_open):
    if menu_open:
        pygame.draw.rect(screen, (30,30,30), (200, 100, 400, 400))
        font = get_font(36)
        text = font.render("Game Menu", True, WHITE)
        screen.blit(text, (320, 120))
        # Add more menu items as needed

def draw_tech_tree_button(screen, WIDTH):
    tech_btn_rect = pygame.Rect(WIDTH-160, 18, 130, 38)
    pygame.draw.rect(screen, (60,120,200), tech_btn_rect, border_radius=12)
    font = get_font(26)
    tech_surf = font.render("Tech Tree", True, (255,255,255))
    screen.blit(tech_surf, (WIDTH-150, 26))
    return tech_btn_rect

def draw_tech_tree(screen, WIDTH, HEIGHT):
    panel_width, panel_height = 520, 420
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((30, 30, 60, 240))
    pygame.draw.rect(panel, (80, 120, 200, 255), (0, 0, panel_width, panel_height), border_radius=18)
    font = get_font(40)
    title = font.render("Tech Tree", True, (255,255,255))
    panel.blit(title, (panel_width//2 - title.get_width()//2, 24))
    screen.blit(panel, (panel_x, panel_y))

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

def draw_inventory(screen, inventory, WIDTH, HEIGHT):
    # Draw a modal inventory window
    modal_w, modal_h = 400, 300
    modal_x = WIDTH // 2 - modal_w // 2
    modal_y = HEIGHT // 2 - modal_h // 2
    pygame.draw.rect(screen, (30, 30, 60), (modal_x, modal_y, modal_w, modal_h), border_radius=16)
    pygame.draw.rect(screen, (200, 200, 255), (modal_x, modal_y, modal_w, modal_h), 4, border_radius=16)
    font = pygame.font.SysFont(None, 40)
    title = font.render("Inventory", True, (255,255,0))
    screen.blit(title, (modal_x + modal_w//2 - title.get_width()//2, modal_y + 20))
    font = pygame.font.SysFont(None, 28)
    if not inventory:
        empty = font.render("(Empty)", True, (220,220,220))
        screen.blit(empty, (modal_x + modal_w//2 - empty.get_width()//2, modal_y + 90))
    else:
        for i, (item, count) in enumerate(inventory.items()):
            line = f"{item}: {count}"
            surf = font.render(line, True, (255,255,255))
            screen.blit(surf, (modal_x + 40, modal_y + 80 + i*36))
    font = pygame.font.SysFont(None, 24)
    close = font.render("Press I or ESC to close", True, (200,200,200))
    screen.blit(close, (modal_x + modal_w//2 - close.get_width()//2, modal_y + modal_h - 40))

# Remove spaceship image loading from ui.py, move to assets.py for proper modularity

# Add more UI helpers as needed
