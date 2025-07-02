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

# Quest system
QUESTS = [
    # Solar System 1
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
    },
    # Alpha Centauri system
    {
        "desc": "Travel to Centauri Prime and collect 5 Xenon for advanced propulsion.",
        "planet": "Centauri Prime",
        "material": "Xenon",
        "amount": 5,
        "collected": 0,
        "completed": False,
        "reward": {"fuel": 30}
    },
    {
        "desc": "Harvest 3 Crystal from Centauri Secundus for quantum computers.",
        "planet": "Centauri Secundus",
        "material": "Crystal",
        "amount": 3,
        "collected": 0,
        "completed": False,
        "reward": {"size": 10}
    },
    {
        "desc": "Collect 4 Helium-3 from the gas giant Centauri Tertius.",
        "planet": "Centauri Tertius",
        "material": "Helium-3",
        "amount": 4,
        "collected": 0,
        "completed": False,
        "reward": {"fuel_efficiency": 0.8}
    },
    # Trappist-1 system
    {
        "desc": "Land on Trappist-1e and gather 6 Organics for terraforming.",
        "planet": "Trappist-1e",
        "material": "Organics",
        "amount": 6,
        "collected": 0,
        "completed": False,
        "reward": {"health": 30}
    },
    {
        "desc": "Mine 5 Ice from Trappist-1g for water reserves.",
        "planet": "Trappist-1g",
        "material": "Ice",
        "amount": 5,
        "collected": 0,
        "completed": False,
        "reward": {"fuel": 40}
    },
    {
        "desc": "Establish a base on Trappist-1h and collect 3 Rare Metals.",
        "planet": "Trappist-1h",
        "material": "Rare Metals",
        "amount": 3,
        "collected": 0,
        "completed": False,
        "reward": {"win": True}
    }
]

class GameState:
    def __init__(self):
        self.player = Player(WORLD_WIDTH//2, WORLD_HEIGHT//2 + 300)
        self.quests = [q.copy() for q in QUESTS]
        self.current_quest = 0
        self.bases = {}  # planet_name: {level, revenue, last_collected}
        self.revenue = 0
        self.menu_open = False
        self.tech_tree_open = False
        self.tech_upgrades = {
            'Speed': {'level': 0, 'max': 5, 'cost': 150, 'desc': 'Increase ship speed'},
            'Size': {'level': 0, 'max': 3, 'cost': 200, 'desc': 'Increase ship size'},
            'Fuel Tank': {'level': 0, 'max': 3, 'cost': 120, 'desc': 'Increase max fuel'},
            'Fuel Efficiency': {'level': 0, 'max': 4, 'cost': 180, 'desc': 'Reduce fuel use'},
            'Max Health': {'level': 0, 'max': 3, 'cost': 180, 'desc': 'Increase max health'},
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

# Add more game logic as needed
