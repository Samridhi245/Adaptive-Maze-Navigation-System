"""Grid pathfinding: Dijkstra (energy-aware), BFS (shortest steps), DFS (any path)."""

import heapq
from collections import deque

from config import ALGO_BFS, ALGO_DFS


def dijkstra_path(maze, start, goal):
    """Shortest path by energy cost (move = 1; entering recharge tile = 0)."""
    if start == goal:
        return []
    pq = [(0, start)]
    cost = {start: 0}
    came_from = {}

    while pq:
        curr_cost, current = heapq.heappop(pq)
        if current == goal:
            break
        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.size and 0 <= ny < maze.size:
                if (nx, ny) in maze.obstacles:
                    continue
                energy_cost = 0 if (nx, ny) in maze.recharge else 1
                new_cost = curr_cost + energy_cost
                if (nx, ny) not in cost or new_cost < cost[(nx, ny)]:
                    cost[(nx, ny)] = new_cost
                    heapq.heappush(pq, (new_cost, (nx, ny)))
                    came_from[(nx, ny)] = current

    if goal not in came_from and goal != start:
        return []

    path = []
    node = goal
    while node in came_from:
        path.append(node)
        node = came_from[node]
    return path[::-1]


def bfs_path(maze, start, goal):
    """Shortest path in number of steps (unweighted)."""
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
            if 0 <= nx < maze.size and 0 <= ny < maze.size:
                if (nx, ny) in maze.obstacles:
                    continue
                if (nx, ny) not in parent:
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


def dfs_path(maze, start, goal):
    """One valid path (not necessarily shortest)."""
    if start == goal:
        return []
    stack = [(start, [start])]
    visited = {start}

    while stack:
        cur, path_cells = stack.pop()
        if cur == goal:
            full = path_cells
            return full[1:] if len(full) > 1 else []

        x, y = cur
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.size and 0 <= ny < maze.size:
                if (nx, ny) in maze.obstacles:
                    continue
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    stack.append(((nx, ny), path_cells + [(nx, ny)]))

    return []


def get_hint_path(algo_key, maze, start, goal):
    """Return hint polyline for the selected algorithm."""
    if algo_key == ALGO_BFS:
        return bfs_path(maze, start, goal)
    if algo_key == ALGO_DFS:
        return dfs_path(maze, start, goal)
    return dijkstra_path(maze, start, goal)
