"""
Game constants: window defaults, colors, levels, algorithms, and state names.
WIN_W / WIN_H are updated at runtime when fullscreen is enabled (see display.py).
"""

import os

# Persistent high scores next to this package
SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")

# Window (fallback; real size set by set_fullscreen_window)
WIN_W, WIN_H = 1180, 920
HUD_H = 96
BOTTOM_H = 92
MARGIN = 20

# Theme colors
BG_DEEP = (18, 22, 32)
BG_PANEL = (28, 34, 48)
BG_PANEL2 = (36, 44, 62)
ACCENT = (88, 166, 255)
ACCENT2 = (120, 220, 180)
TEXT_MAIN = (235, 240, 250)
TEXT_DIM = (160, 170, 190)
DANGER = (255, 100, 120)
SUCCESS = (100, 230, 160)
GOAL_COLOR = (186, 120, 255)
RECHARGE_COLOR = (60, 200, 140)
OBSTACLE_COLOR = (220, 90, 90)
PLAYER_COLOR = (70, 140, 255)
PATH_HINT = (255, 210, 100)
GRID_LINE = (55, 65, 85)
WHITE = (255, 255, 255)

# Game states (finite state machine)
HOME = "HOME"
LEVEL_SELECT = "LEVEL_SELECT"
ALGORITHM_SELECT = "ALGORITHM_SELECT"
ALGORITHMS_INFO = "ALGORITHMS_INFO"
PLAYING = "PLAYING"
WIN = "WIN"
LOSE = "LOSE"

# Level: grid size, obstacles, recharge, starting energy, game tick rate
LEVELS = {
    "easy": {
        "label": "Easy",
        "grid": 8,
        "obstacles": 3,
        "recharge": 3,
        "energy": 25,
        "fps": 6,
    },
    "medium": {
        "label": "Medium",
        "grid": 10,
        "obstacles": 5,
        "recharge": 2,
        "energy": 15,
        "fps": 8,
    },
    "hard": {
        "label": "Hard",
        "grid": 12,
        "obstacles": 8,
        "recharge": 2,
        "energy": 8,
        "fps": 11,
    },
}

ALGO_DIJKSTRA = "dijkstra"
ALGO_BFS = "bfs"
ALGO_DFS = "dfs"

ALGO_LABELS = {
    ALGO_DIJKSTRA: "Dijkstra",
    ALGO_BFS: "BFS",
    ALGO_DFS: "DFS",
}
