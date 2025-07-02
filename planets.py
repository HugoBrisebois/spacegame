"""
Contains planet data, orbit logic, and planet-related helpers.
"""

import math
from assets import SUN_POS

# Each planet has: name, orbit_radius, color, material, size, angle, speed
PLANETS = [
    # Solar System 1
    {"name": "Mercury", "orbit_radius": 600, "color": (200, 200, 200), "material": "Iron", "size": 40, "speed": 1.6, "angle": 0},
    {"name": "Venus",   "orbit_radius": 1200, "color": (255, 200, 0),  "material": "Sulfur", "size": 60, "speed": 1.2, "angle": math.pi/4.5},
    {"name": "Earth",   "orbit_radius": 1800, "color": (0, 100, 255), "material": "Water", "size": 70, "speed": 1.0, "angle": 2*math.pi/4.5},
    {"name": "Mars",    "orbit_radius": 2400, "color": (255, 80, 0),  "material": "Silicon", "size": 55, "speed": 0.8, "angle": 3*math.pi/4.5},
    {"name": "Jupiter", "orbit_radius": 3000, "color": (210, 180, 140), "material": "Hydrogen", "size": 120, "speed": 0.5, "angle": 4*math.pi/4.5},
    {"name": "Saturn",  "orbit_radius": 3600, "color": (230, 220, 170), "material": "Helium", "size": 110, "speed": 0.4, "angle": 5*math.pi/4.5},
    {"name": "Uranus",  "orbit_radius": 4200, "color": (100, 255, 255), "material": "Methane", "size": 90, "speed": 0.3, "angle": 6*math.pi/4.5},
    {"name": "Neptune", "orbit_radius": 4800, "color": (60, 80, 255),   "material": "Ammonia", "size": 85, "speed": 0.25, "angle": 7*math.pi/4.5},
    {"name": "Pluto",   "orbit_radius": 5200, "color": (200, 200, 255), "material": "Ice", "size": 30, "speed": 0.18, "angle": 8*math.pi/4.5},
    # Alpha Centauri system
    {"name": "Centauri Prime", "orbit_radius": 7000, "color": (180, 255, 255), "material": "Xenon", "size": 60, "speed": 0.13, "angle": 0.5},
    {"name": "Centauri Secundus", "orbit_radius": 7600, "color": (255, 120, 255), "material": "Crystal", "size": 55, "speed": 0.11, "angle": 1.2},
    {"name": "Centauri Tertius", "orbit_radius": 8200, "color": (255, 255, 120), "material": "Helium-3", "size": 100, "speed": 0.09, "angle": 2.1},
    # Trappist-1 system
    {"name": "Trappist-1e", "orbit_radius": 9000, "color": (120, 255, 120), "material": "Organics", "size": 50, "speed": 0.07, "angle": 2.8},
    {"name": "Trappist-1g", "orbit_radius": 9600, "color": (120, 180, 255), "material": "Ice", "size": 45, "speed": 0.06, "angle": 3.5},
    {"name": "Trappist-1h", "orbit_radius": 10200, "color": (255, 200, 120), "material": "Rare Metals", "size": 40, "speed": 0.05, "angle": 4.2},
]


def update_planet_positions(planets, dt):
    for planet in planets:
        planet['angle'] += planet['speed'] * dt * 0.001  # dt scaling for smoothness
        planet['angle'] %= 2 * math.pi


def get_planet_positions(planet_data, sun_pos):
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

# Add more planet-related helpers as needed
