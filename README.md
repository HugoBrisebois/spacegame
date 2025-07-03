# Space Explorer

A 2D space exploration made with Python and Pygame.

## Features

- Explore a solar system with multiple planets
- Smooth spaceship controls (mouse steering, W/S for thrust)
- Land on planets and gather resources
- Complete quests and gather resources
- Modern UI and menus

## Controls

- **Steer Ship:** Move your mouse (ship always faces the mouse)
- **Accelerate:** W
- **Reverse:** S
- **Land on Planet:** Approach a planet and stop (ship will stick to the edge)
- **Take Off:** SPACE (when landed)
- **Open Inventory:** I
- **Show Map:** M
- **Open Menu:** ESC
- **Interact/Collect:** done automatically
- **Scroll Inventory:** UP/DOWN or Mouse Wheel
- **Resume Game:** ESC (from menu)
- **Quit Game:** Quit button

## Marker/Compass System

- The compass at the top of the screen always points to the planet where your next quest will happen.
- You no longer need to manually set a marker; the marker updates automatically as you progress through quests.
- The marker panel shows the name and distance to your current quest planet.

## How to Play

1. Use your mouse to steer the ship and W to accelerate.
2. Approach a planet to land. The ship will stick to the planet's edge.
3. Complete quests and explore the tech tree for upgrades.

## Requirements

- Python 3.x
- Pygame

Install dependencies:

```sh
pip install pygame
```

Run the game:

```sh
python main.py
```