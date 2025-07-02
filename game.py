"""
Handles game state, player logic, quest system, base management, and world state.
"""

import pygame
from assets import PLAYER_SIZE, PLAYER_SPEED, WORLD_WIDTH, WORLD_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.fuel = 100
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.base_built = False
        self.angle = 0
        self.inventory = {}
        self.bases = {}  # Track bases built on planets
        self.tech_tree = {}  # Track tech tree state (empty dict by default)

    def move(self, dx, dy):
        self.x += dx * PLAYER_SPEED
        self.y += dy * PLAYER_SPEED
        self.x = max(0, min(self.x, WORLD_WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, WORLD_HEIGHT - PLAYER_SIZE))
        self.rect.topleft = (self.x, self.y)

# Update QUESTS in game.py to include Jupiter - Neptune in the Solar System section
QUESTS = [
    # Solar System (now includes Jupiter - Neptune)
    {"desc": "Colonize Mercury and extract 3 Iron for Earth's new outpost.", "planet": "Mercury", "material": "Iron", "amount": 3, "collected": 0, "completed": False, "reward": {"speed": 1}},
    {"desc": "Establish a mining base on Venus and collect 2 Sulfur for advanced fuel.", "planet": "Venus", "material": "Sulfur", "amount": 2, "collected": 0, "completed": False, "reward": {"speed": 1}},
    {"desc": "Terraform Earth by gathering 2 Water for the new colony's life support.", "planet": "Earth", "material": "Water", "amount": 2, "collected": 0, "completed": False, "reward": {"size": 10}},
    {"desc": "Exploit Mars for 4 Silicon to build the first Martian city.", "planet": "Mars", "material": "Silicon", "amount": 4, "collected": 0, "completed": False, "reward": {"win": True}},
    {"desc": "Harvest Ammonia from Jupiter for advanced life support.", "planet": "Jupiter", "material": "Ammonia", "amount": 2, "collected": 0, "completed": False, "reward": {"size": 10}},
    {"desc": "Mine Methane from Saturn for fuel research.", "planet": "Saturn", "material": "Methane", "amount": 2, "collected": 0, "completed": False, "reward": {"speed": 1}},
    {"desc": "Collect Uranium from Uranus for power generation.", "planet": "Uranus", "material": "Uranium", "amount": 2, "collected": 0, "completed": False, "reward": {"size": 10}},
    {"desc": "Extract Deuterium from Neptune for fusion research.", "planet": "Neptune", "material": "Deuterium", "amount": 2, "collected": 0, "completed": False, "reward": {"speed": 1}},
    # Alpha Centauri
    {"desc": "Mine Centauri Prime for 3 Crystal to power advanced tech.", "planet": "Centauri Prime", "material": "Crystal", "amount": 3, "collected": 0, "completed": False, "reward": {"size": 10}},
    {"desc": "Harvest 2 Xenon from Centauri Secundus for propulsion research.", "planet": "Centauri Secundus", "material": "Xenon", "amount": 2, "collected": 0, "completed": False, "reward": {"speed": 1}},
    {"desc": "Build a colony on Centauri Tertius and collect 2 Ice for life support.", "planet": "Centauri Tertius", "material": "Ice", "amount": 2, "collected": 0, "completed": False, "reward": {"fuel": 20}},
    # Trappist-1
    {"desc": "Extract 3 Organics from Trappist-1e for food production.", "planet": "Trappist-1e", "material": "Organics", "amount": 3, "collected": 0, "completed": False, "reward": {"health": 20}},
    {"desc": "Mine 2 Platinum from Trappist-1f for advanced electronics.", "planet": "Trappist-1f", "material": "Platinum", "amount": 2, "collected": 0, "completed": False, "reward": {"size": 10}},
    {"desc": "Harvest 2 Helium-3 from Trappist-1g for fusion power.", "planet": "Trappist-1g", "material": "Helium-3", "amount": 2, "collected": 0, "completed": False, "reward": {"win": True}}
]

class GameState:
    def __init__(self):
        self.player = Player(WORLD_WIDTH//2, WORLD_HEIGHT//2 + 300)
        self.quests = [q.copy() for q in QUESTS]
        # Ensure all quests start as incomplete
        for q in self.quests:
            q['completed'] = False
            q['collected'] = 0
        self.current_quest = 0
        self.bases = {}  # planet_name: {level, revenue, last_collected}
        self.revenue = 0
        self.menu_open = False
        self.tech_tree_open = False
        self.tech_upgrades = {
            'Speed': {'level': 0, 'max': 5, 'materials': {'Iron': 2, 'Xenon': 1}, 'desc': 'Increase ship speed'},
            'Size': {'level': 0, 'max': 3, 'materials': {'Crystal': 2, 'Water': 1}, 'desc': 'Increase ship size'},
        }
        self.base_on_planet = None
        self.story = [
            # Solar System 1
            "You are Errin, a pioneer of the Galactic Expansion Fleet.",
            "Your mission: travel to distant planets, colonize them, and extract their resources for humanity's future.",
            "Each world in your home solar system holds unique materials vital for Earth's survival and the growth of the new colonies.",
            "From the burning iron of Mercury to the icy reaches of Pluto, every planet offers new challenges and opportunities.",
            # Solar System 2
            "With Earth's future secured, your journey continues to Alpha Centauri, a system of three suns and a host of new worlds.",
            "Here, you must adapt to alien atmospheres, harvest exotic elements, and build outposts on planets never before seen by human eyes.",
            "The twin planets of Centauri Prime and Secundus are rich in rare crystals and volatile gases, while the outer ice giants hide secrets beneath their frozen crusts.",
            # Solar System 3
            "Your final destination is the mysterious Trappist-1 system, a compact family of seven rocky worlds orbiting a cool red star.",
            "Survive the harsh conditions, unlock advanced technology, and establish the first interstellar civilization among the stars.",
            "The fate of humanity now stretches across three solar systems. Your courage and ingenuity will determine the future of all!"
        ]
        self.inventory = {}  # Unlimited storage: no artificial limit
        self.inventory_scroll = 0
        self.landed_planet = None
        self.landed_message_timer = 0
        self.show_map = False

    def complete_quest(self, quest_idx):
        if 0 <= quest_idx < len(self.quests):
            self.quests[quest_idx]['completed'] = True

    def can_collect_resource(self, planet, material):
        """
        Returns True if the player can collect the resource for the current quest on the given planet.
        Debugs mismatches if collection fails.
        """
        if not (0 <= self.current_quest < len(self.quests)):
            print(f"[DEBUG] Invalid current_quest index: {self.current_quest}")
            return False
        quest = self.quests[self.current_quest]
        if quest['completed']:
            print(f"[DEBUG] Quest already completed: {quest}")
            return False
        if quest['planet'] != planet:
            print(f"[DEBUG] Planet mismatch: quest expects '{quest['planet']}', got '{planet}'")
            return False
        if quest['material'] != material:
            print(f"[DEBUG] Material mismatch: quest expects '{quest['material']}', got '{material}'")
            return False
        return True

# Add more game logic as needed
