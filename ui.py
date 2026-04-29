"""Pygame UI: helpers, Button, layout, and all screen drawing routines."""

import pygame

import config


def draw_round_rect(surf, rect, color, radius=12, border=0, border_color=None):
    if border_color is None:
        border_color = color
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border > 0:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_text_centered(surf, text, font, color, center_xy):
    t = font.render(text, True, color)
    r = t.get_rect(center=center_xy)
    surf.blit(t, r)


def draw_text_left(surf, text, font, color, xy):
    surf.blit(font.render(text, True, color), xy)


def wrap_text_lines(text, max_chars=70):
    words = text.split()
    lines, cur = [], []
    n = 0
    for w in words:
        if n + len(w) + 1 > max_chars and cur:
            lines.append(" ".join(cur))
            cur = [w]
            n = len(w)
        else:
            cur.append(w)
            n += len(w) + 1
    if cur:
        lines.append(" ".join(cur))
    return lines


class Button:
    def __init__(self, rect, text, font, base_color, text_color, hover_color=None, radius=14):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.text_color = text_color
        self.hover_color = hover_color or tuple(min(255, c + 25) for c in base_color[:3])
        self.radius = radius
        self.hovered = False

    def draw(self, surf, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        col = self.hover_color if self.hovered else self.base_color
        draw_round_rect(surf, self.rect, col, self.radius)
        draw_text_centered(surf, self.text, self.font, self.text_color, self.rect.center)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def compute_layout(grid_size, side_panel_w=0):
    """Cell size and pixel rectangle for the maze (centered below HUD)."""
    inner_w = config.WIN_W - 2 * config.MARGIN - side_panel_w
    inner_h = config.WIN_H - config.HUD_H - config.BOTTOM_H - 2 * config.MARGIN
    side = min(inner_w, inner_h)
    cell = max(28, side // grid_size)
    gw = cell * grid_size
    gh = cell * grid_size
    gx = (config.WIN_W - side_panel_w - gw) // 2
    gy = config.HUD_H + config.MARGIN + (inner_h - gh) // 2
    return cell, pygame.Rect(gx, gy, gw, gh), gx, gy


def draw_game(
    win,
    maze,
    player,
    fonts,
    steps,
    time_elapsed,
    path,
    hint_len,
    level_key,
    algo_key,
    best_rec,
    move_history,
    buttons,
    mouse_pos,
    hover_path=None
):
    if hover_path is None:
        hover_path = []
    _title_f, hud_f, small_f = fonts
    win.fill(config.BG_DEEP)

    hud_rect = pygame.Rect(0, 0, config.WIN_W, config.HUD_H)
    draw_round_rect(win, hud_rect, config.BG_PANEL, 0)
    pygame.draw.line(win, config.GRID_LINE, (0, config.HUD_H - 1), (config.WIN_W, config.HUD_H - 1))

    lvl_name = config.LEVELS[level_key]["label"]
    algo_name = config.ALGO_LABELS.get(algo_key, algo_key)
    bs = best_rec.get("best_steps")
    bt = best_rec.get("best_time")
    bs_s = str(bs) if bs is not None else "—"
    bt_s = f"{bt:.1f}s" if bt is not None else "—"

    line1 = (
        f"Energy: {player.energy}   |   Steps: {steps}   |   Time: {time_elapsed}s"
        f"   |   Level: {lvl_name}   |   Hint: {algo_name}"
    )
    line2 = f"Best steps: {bs_s}   |   Best time: {bt_s}   |   Hint path cells: {hint_len}"

    draw_text_left(win, line1, hud_f, config.TEXT_MAIN, (config.MARGIN, 18))
    draw_text_left(win, line2, small_f, config.TEXT_DIM, (config.MARGIN, 52))

    side_panel_w = 230
    panel_gap = 14
    cell, grid_rect, gx, gy = compute_layout(maze.size, side_panel_w + panel_gap)

    frame_pad = 6
    fr = grid_rect.inflate(frame_pad * 2, frame_pad * 2)
    draw_round_rect(win, fr, config.BG_PANEL2, 16)
    pygame.draw.rect(win, config.GRID_LINE, fr, 2, border_radius=16)

    gs = maze.size
    for i in range(gs):
        for j in range(gs):
            rect = pygame.Rect(gx + j * cell, gy + i * cell, cell, cell)
            inner = rect.inflate(-2, -2)

            if (i, j) in maze.obstacles:
                draw_round_rect(win, inner, config.OBSTACLE_COLOR, 8)
                pygame.draw.rect(win, (180, 60, 60), inner, 2, border_radius=8)
            elif (i, j) in maze.recharge:
                draw_round_rect(win, inner, config.RECHARGE_COLOR, 8)
                draw_text_centered(win, "+", hud_f, config.WHITE, inner.center)
            elif (i, j) == (gs - 1, gs - 1):
                draw_round_rect(win, inner, config.GOAL_COLOR, 8)
                draw_text_centered(win, "G", hud_f, config.WHITE, inner.center)
            else:
                is_hovered = inner.collidepoint(mouse_pos)
                base_color = config.CELL_HOVER if is_hovered else config.CELL_COLOR
                pygame.draw.rect(win, base_color, inner, border_radius=8)
                pygame.draw.rect(win, config.GRID_LINE, inner, 1, border_radius=8)

            # Draw cell numbering
            if (i, j) not in maze.obstacles:
                num_text = str(i * gs + j + 1)
                # Position number slightly higher or centered, smaller
                # We use small_f (size 16), transparent-like color
                draw_text_centered(win, num_text, small_f, (150, 160, 175), inner.center)

    # Draw hover path preview
    for (i, j) in hover_path:
        r = pygame.Rect(gx + j * cell + 2, gy + i * cell + 2, cell - 4, cell - 4)
        s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        s.fill((120, 200, 255, 90)) # subtle blue for preview
        win.blit(s, r.topleft)

    for (i, j) in path:
        r = pygame.Rect(gx + j * cell + 2, gy + i * cell + 2, cell - 4, cell - 4)
        s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        s.fill((*config.PATH_HINT, 120))
        win.blit(s, r.topleft)

    pr = pygame.Rect(gx + player.y * cell + 2, gy + player.x * cell + 2, cell - 4, cell - 4)
    draw_round_rect(win, pr, config.PLAYER_COLOR, 10)
    pygame.draw.rect(win, config.WHITE, pr, 2, border_radius=10)
    draw_text_centered(win, "P", hud_f, config.WHITE, pr.center)

    panel_x = config.WIN_W - config.MARGIN - side_panel_w
    panel_y = config.HUD_H + config.MARGIN
    panel_h = config.WIN_H - config.HUD_H - config.BOTTOM_H - 2 * config.MARGIN
    side_rect = pygame.Rect(panel_x, panel_y, side_panel_w, panel_h)
    draw_round_rect(win, side_rect, config.BG_PANEL, 12)
    pygame.draw.rect(win, config.GRID_LINE, side_rect, 1, border_radius=12)
    draw_text_left(win, "Movement Path", small_f, config.TEXT_MAIN, (panel_x + 14, panel_y + 12))

    graph_pad = 14
    graph_top = panel_y + 42
    graph_rect = pygame.Rect(
        panel_x + graph_pad,
        graph_top,
        side_panel_w - graph_pad * 2,
        panel_h - (graph_top - panel_y) - graph_pad,
    )
    draw_round_rect(win, graph_rect, config.BG_PANEL2, 10)
    pygame.draw.rect(win, config.GRID_LINE, graph_rect, 1, border_radius=10)

    gs = maze.size
    mini_cell = min(graph_rect.width // gs, graph_rect.height // gs)
    mini_w = mini_cell * gs
    mini_h = mini_cell * gs
    mini_x = graph_rect.x + (graph_rect.width - mini_w) // 2
    mini_y = graph_rect.y + (graph_rect.height - mini_h) // 2

    for i in range(gs + 1):
        y = mini_y + i * mini_cell
        pygame.draw.line(win, config.GRID_LINE, (mini_x, y), (mini_x + mini_w, y))
    for j in range(gs + 1):
        x = mini_x + j * mini_cell
        pygame.draw.line(win, config.GRID_LINE, (x, mini_y), (x, mini_y + mini_h))

    if move_history and mini_cell > 0:
        points = []
        for x, y in move_history:
            px = mini_x + y * mini_cell + mini_cell // 2
            py = mini_y + x * mini_cell + mini_cell // 2
            points.append((px, py))
        if len(points) >= 2:
            pygame.draw.lines(win, config.ACCENT, False, points, 2)
        pygame.draw.circle(win, config.PLAYER_COLOR, points[-1], max(3, mini_cell // 5))

    bot_top = config.WIN_H - config.BOTTOM_H
    bot_rect = pygame.Rect(0, bot_top, config.WIN_W, config.BOTTOM_H)
    draw_round_rect(win, bot_rect, config.BG_PANEL, 0)
    pygame.draw.line(win, config.GRID_LINE, (0, bot_top), (config.WIN_W, bot_top))

    hint_txt = "Arrows: move  |  H: hint  |  R: restart  |  Esc: exit"
    draw_text_centered(win, hint_txt, small_f, config.TEXT_DIM, (config.WIN_W // 2, bot_top + 22))

    for b in buttons:
        b.draw(win, mouse_pos)

    pygame.display.update()


def draw_home_screen(win, fonts, buttons, mouse_pos):
    title_f, body_f, small_f = fonts
    win.fill(config.BG_DEEP)
    draw_round_rect(win, pygame.Rect(80, 60, config.WIN_W - 160, config.WIN_H - 120), config.BG_PANEL2, 20)
    pygame.draw.rect(
        win,
        config.ACCENT,
        pygame.Rect(80, 60, config.WIN_W - 160, config.WIN_H - 120),
        2,
        border_radius=20,
    )

    draw_text_centered(win, "MAZE OPTIMIZER", title_f, config.ACCENT, (config.WIN_W // 2, 130))

    intro = (
        "Reach the purple goal (G) using as few steps and time as you can. "
        "Each move uses 1 energy. Green recharge cells restore +5 energy. "
        "Red blocks are obstacles—some move each frame. "
        "Use path hints (H) to compare shortest routes: Dijkstra minimizes energy cost along the path, "
        "BFS minimizes step count, and DFS explores deeply to find any route. "
        "Optimize your run!"
    )
    y = 200
    for line in wrap_text_lines(intro, 72):
        t = body_f.render(line, True, config.TEXT_MAIN)
        win.blit(t, (120, y))
        y += 28

    for b in buttons:
        b.draw(win, mouse_pos)

    pygame.display.update()


def draw_level_select(win, fonts, buttons, mouse_pos):
    title_f, body_f, _ = fonts
    win.fill(config.BG_DEEP)
    draw_text_centered(win, "Choose Level", title_f, config.TEXT_MAIN, (config.WIN_W // 2, 100))
    draw_text_centered(
        win,
        "Easy: smaller maze, more energy, fewer obstacles",
        body_f,
        config.TEXT_DIM,
        (config.WIN_W // 2, 150),
    )
    draw_text_centered(
        win,
        "Medium: balanced  |  Hard: larger maze, less energy, more obstacles, faster hazards",
        body_f,
        config.TEXT_DIM,
        (config.WIN_W // 2, 185),
    )
    for b in buttons:
        b.draw(win, mouse_pos)
    pygame.display.update()


def draw_algorithm_select(win, fonts, buttons, mouse_pos, level_key):
    title_f, body_f, _ = fonts
    win.fill(config.BG_DEEP)
    draw_text_centered(win, "Hint / Best Path Algorithm", title_f, config.TEXT_MAIN, (config.WIN_W // 2, 90))
    draw_text_centered(
        win,
        f"Level: {config.LEVELS[level_key]['label']} — pick which algorithm draws the hint path (H in game).",
        body_f,
        config.TEXT_DIM,
        (config.WIN_W // 2, 140),
    )
    for b in buttons:
        b.draw(win, mouse_pos)
    pygame.display.update()


def draw_algorithms_info(win, fonts, buttons, mouse_pos):
    title_f, body_f, small_f = fonts
    win.fill(config.BG_DEEP)
    # Main heading (button says "Algorithms"; this screen names each one)
    draw_text_centered(win, "Algorithms", title_f, config.ACCENT2, (config.WIN_W // 2, 55))
    draw_text_centered(
        win,
        "Algorithms used in this game:  Dijkstra  |  BFS  |  DFS",
        body_f,
        config.ACCENT,
        (config.WIN_W // 2, 108),
    )
    draw_text_centered(
        win,
        "BFS = Breadth-First Search   ·   DFS = Depth-First Search",
        small_f,
        config.TEXT_DIM,
        (config.WIN_W // 2, 142),
    )

    lines = [
        "Dijkstra — Finds a minimum energy-cost path (moving costs 1; entering a recharge tile costs 0).",
        "BFS (Breadth-First Search) — Finds a path with the fewest steps on the grid.",
        "DFS (Depth-First Search) — Explores deep branches first; finds one valid path (not always shortest).",
    ]
    y = 185
    for line in lines:
        for part in wrap_text_lines(line, 85):
            win.blit(body_f.render(part, True, config.TEXT_MAIN), (90, y))
            y += 26
        y += 10

    draw_text_centered(
        win,
        "You can choose Dijkstra, BFS, or DFS for the path hint (H) before each run.",
        small_f,
        config.TEXT_DIM,
        (config.WIN_W // 2, y + 20),
    )

    for b in buttons:
        b.draw(win, mouse_pos)
    pygame.display.update()


def draw_win_screen(win, fonts, data, buttons, mouse_pos):
    title_f, body_f, small_f = fonts
    win.fill(config.BG_DEEP)
    draw_round_rect(win, pygame.Rect(100, 80, config.WIN_W - 200, config.WIN_H - 160), config.BG_PANEL2, 18)
    pygame.draw.rect(
        win,
        config.SUCCESS,
        pygame.Rect(100, 80, config.WIN_W - 200, config.WIN_H - 160),
        2,
        border_radius=18,
    )

    draw_text_centered(win, "You Win!", title_f, config.SUCCESS, (config.WIN_W // 2, 120))

    if data.get("record_msg"):
        draw_text_centered(win, data["record_msg"], body_f, config.ACCENT2, (config.WIN_W // 2, 170))

    y = 220
    rows = [
        f"Time: {data['time']} s",
        f"Steps: {data['steps']}",
        f"Hint path length (cells after start): {data['hint_len']}",
    ]
    if data.get("prev_best_steps") is not None or data.get("new_best_steps") is not None:
        rows.append(f"Previous best steps: {data.get('prev_best_steps', '—')}")
        rows.append(f"New best steps: {data.get('new_best_steps', '—')}")
    if data.get("prev_best_time") is not None or data.get("new_best_time") is not None:
        rows.append(f"Previous best time: {data.get('prev_best_time', '—')}")
        rows.append(f"New best time: {data.get('new_best_time', '—')}")

    for r in rows:
        draw_text_centered(win, r, body_f, config.TEXT_MAIN, (config.WIN_W // 2, y))
        y += 32

    for b in buttons:
        b.draw(win, mouse_pos)
    pygame.display.update()


def draw_lose_screen(win, fonts, data, buttons, mouse_pos):
    title_f, body_f, _ = fonts
    win.fill(config.BG_DEEP)
    draw_round_rect(win, pygame.Rect(100, 120, config.WIN_W - 200, config.WIN_H - 240), config.BG_PANEL2, 18)
    pygame.draw.rect(
        win,
        config.DANGER,
        pygame.Rect(100, 120, config.WIN_W - 200, config.WIN_H - 240),
        2,
        border_radius=18,
    )

    draw_text_centered(win, "You Lost", title_f, config.DANGER, (config.WIN_W // 2, 180))
    draw_text_centered(win, data.get("reason", "Try again!"), body_f, config.TEXT_MAIN, (config.WIN_W // 2, 250))

    for b in buttons:
        b.draw(win, mouse_pos)
    pygame.display.update()
