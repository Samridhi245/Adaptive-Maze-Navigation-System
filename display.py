"""Fullscreen display setup; updates config.WIN_W / config.WIN_H for layout."""

import pygame

import config


def set_fullscreen_window():
    """Borderless fullscreen using primary monitor size."""
    sizes = pygame.display.get_desktop_sizes()
    if sizes:
        config.WIN_W, config.WIN_H = sizes[0][0], sizes[0][1]
    else:
        info = pygame.display.Info()
        if info.current_w and info.current_h:
            config.WIN_W, config.WIN_H = info.current_w, info.current_h
    return pygame.display.set_mode((config.WIN_W, config.WIN_H), pygame.FULLSCREEN)
