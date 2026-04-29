"""Maze generation / moving obstacles and player state."""

import random
from collections import deque


class Maze:
    def __init__(self, size, num_obstacles, num_recharge, player_energy=None):
        self.size = size
        self.num_obstacles = num_obstacles
        self.num_recharge = num_recharge
        self.player_energy = player_energy
        self.obstacles = set()
        self.recharge = set()
        self.generate()

    # ------------------------------------------------------------------
    # BFS helper: returns shortest path (list of cells) or [] if blocked
    # ------------------------------------------------------------------
    def _bfs_path(self, start, goal, obstacles):
        """BFS on the grid avoiding *obstacles*; returns cell list (excl. start)."""
        if start == goal:
            return []
        q = deque([start])
        parent = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            x, y = cur
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if (nx, ny) not in obstacles and (nx, ny) not in parent:
                        parent[(nx, ny)] = cur
                        q.append((nx, ny))
        if goal not in parent:
            return []
        out = []
        node = goal
        while node != start:
            out.append(node)
            node = parent[node]
        return out[::-1]

    # ------------------------------------------------------------------
    # Check if the maze is solvable with given energy
    # ------------------------------------------------------------------
    def _is_solvable(self, energy):
        """True when a path exists AND its net energy cost is affordable.

        Energy cost = steps_on_path − 5 × recharge_tiles_on_path.
        We check whether the cheapest path (BFS ≈ shortest) is affordable.
        """
        start = (0, 0)
        goal = (self.size - 1, self.size - 1)
        path = self._bfs_path(start, goal, self.obstacles)
        if not path:
            return False
        if energy is None:
            return True  # no energy constraint to check
        # simulate energy along the path
        e = energy
        for cell in path:
            e -= 1
            if cell in self.recharge:
                e += 5
            if e <= 0 and cell != goal:
                return False
        return True

    # ------------------------------------------------------------------
    # Generate a guaranteed-solvable maze
    # ------------------------------------------------------------------
    def generate(self):
        start_end = {(0, 0), (self.size - 1, self.size - 1)}

        for _ in range(500):  # retry cap to avoid infinite loop
            self.obstacles = set()
            self.recharge = set()

            while len(self.obstacles) < self.num_obstacles:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if (x, y) not in start_end and (x, y) not in self.recharge:
                    self.obstacles.add((x, y))

            while len(self.recharge) < self.num_recharge:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if (x, y) not in self.obstacles and (x, y) not in start_end:
                    self.recharge.add((x, y))

            if self._is_solvable(self.player_energy):
                return  # ✓ valid layout found

        # Fallback: clear all obstacles so the maze is trivially solvable
        self.obstacles = set()

    def move_obstacles(self, player_pos):
        goal = (self.size - 1, self.size - 1)
        new_obs = set()
        for (x, y) in self.obstacles:
            dx, dy = random.choice([(0, 1), (1, 0), (-1, 0), (0, -1)])
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if (nx, ny) == player_pos or (nx, ny) in self.recharge or (nx, ny) == goal:
                    new_obs.add((x, y))  # stay put
                else:
                    new_obs.add((nx, ny))
            else:
                new_obs.add((x, y))

        # Safety: verify the player can still reach the goal after obstacles move.
        # If not, revert to previous obstacle positions.
        test_path = self._bfs_path(player_pos, goal, new_obs)
        if test_path or player_pos == goal:
            self.obstacles = new_obs
        # else: keep old self.obstacles — path stays open


class Player:
    def __init__(self, energy):
        self.x = 0
        self.y = 0
        self.energy = energy
