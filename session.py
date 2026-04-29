"""Starting or restarting a run: new maze, player, timer, and HUD snapshot."""

import pygame

import config
from entities import Maze, Player


def new_game_session(level_key, scores):
    """Fresh maze and player; reset steps, hint path, and timer."""
    cfg = config.LEVELS[level_key]
    maze = Maze(cfg["grid"], cfg["obstacles"], cfg["recharge"], player_energy=cfg["energy"])
    player = Player(cfg["energy"])
    start_time = pygame.time.get_ticks()
    steps = 0
    path = []
    hint_len = 0
    best_rec = scores.get(level_key, {"best_steps": None, "best_time": None})
    return maze, player, start_time, steps, path, hint_len, best_rec, cfg["fps"]
