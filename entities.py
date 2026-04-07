"""Maze generation / moving obstacles and player state."""

import random


class Maze:
    def __init__(self, size, num_obstacles, num_recharge):
        self.size = size
        self.num_obstacles = num_obstacles
        self.num_recharge = num_recharge
        self.obstacles = set()
        self.recharge = set()
        self.generate()

    def generate(self):
        self.obstacles = set()
        self.recharge = set()
        start_end = {(0, 0), (self.size - 1, self.size - 1)}

        while len(self.obstacles) < self.num_obstacles:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (x, y) not in start_end and (x, y) not in self.recharge:
                self.obstacles.add((x, y))

        while len(self.recharge) < self.num_recharge:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (x, y) not in self.obstacles and (x, y) not in start_end:
                self.recharge.add((x, y))

    def move_obstacles(self, player_pos):
        new_obs = set()
        for (x, y) in self.obstacles:
            dx, dy = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if (nx, ny) == player_pos or (nx, ny) in self.recharge:
                    new_obs.add((x, y))
                else:
                    new_obs.add((nx, ny))
            else:
                new_obs.add((x, y))
        self.obstacles = new_obs


class Player:
    def __init__(self, energy):
        self.x = 0
        self.y = 0
        self.energy = energy
