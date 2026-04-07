"""
MAZE OPTIMIZER — entry point: pygame loop, input, and game state machine.
Logic lives in config, entities, pathfinding, scores, session, ui, display.
"""

import pygame

import config
from display import set_fullscreen_window
from pathfinding import get_hint_path
from scores import is_better_steps, is_better_time, load_scores, save_scores
from session import new_game_session
from ui import (
    Button,
    draw_algorithm_select,
    draw_algorithms_info,
    draw_game,
    draw_home_screen,
    draw_level_select,
    draw_lose_screen,
    draw_win_screen,
)


def main():
    pygame.init()
    win = set_fullscreen_window()
    pygame.display.set_caption("MAZE OPTIMIZER")

    title_font = pygame.font.SysFont("segoeui", 52, bold=True)
    hud_font = pygame.font.SysFont("segoeui", 22)
    body_font = pygame.font.SysFont("segoeui", 20)
    small_font = pygame.font.SysFont("segoeui", 16)
    btn_font = pygame.font.SysFont("segoeui", 22)

    scores = load_scores()

    state = config.HOME
    level_key = "medium"
    algo_key = config.ALGO_DIJKSTRA

    maze = None
    player = None
    start_time = 0
    steps = 0
    path = []
    hint_len = 0
    game_fps = 8
    best_rec = {}

    win_data = {}
    lose_data = {}

    clock = pygame.time.Clock()
    running = True

    def make_playing_buttons():
        bw, bh = 160, 44
        x = config.WIN_W - config.MARGIN - bw
        y = config.WIN_H - config.BOTTOM_H + 24
        return [
            Button((x, y, bw, bh), "Restart", btn_font, config.ACCENT, config.WHITE, hover_color=(120, 190, 255)),
        ]

    playing_buttons = []

    cx = config.WIN_W // 2
    home_btns = [
        Button((cx - 140, 420, 280, 48), "Start Game", btn_font, config.ACCENT, config.WHITE),
        Button((cx - 140, 480, 280, 48), "Choose Level", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx - 140, 540, 280, 48), "Algorithms", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx - 140, 600, 280, 48), "Quit", btn_font, (80, 50, 55), config.TEXT_MAIN),
    ]
    level_btns = [
        Button((cx - 120, 260, 240, 46), "Easy", btn_font, (70, 140, 100), config.WHITE),
        Button((cx - 120, 320, 240, 46), "Medium", btn_font, (90, 120, 160), config.WHITE),
        Button((cx - 120, 380, 240, 46), "Hard", btn_font, (160, 80, 90), config.WHITE),
        Button((cx - 120, 460, 240, 46), "Back", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
    ]
    algo_btns = [
        Button((cx - 180, 230, 360, 46), "Dijkstra (energy-smart path)", btn_font, config.ACCENT, config.WHITE),
        Button((cx - 180, 290, 360, 46), "BFS (fewest steps)", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx - 180, 350, 360, 46), "DFS (any valid path)", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx - 180, 430, 240, 46), "Back", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
    ]
    algo_info_back = Button((cx - 100, config.WIN_H - 120, 200, 44), "Back", btn_font, config.ACCENT, config.WHITE)
    win_btns = [
        Button((cx - 200, config.WIN_H - 200, 120, 42), "Play Again", btn_font, config.ACCENT, config.WHITE),
        Button((cx - 60, config.WIN_H - 200, 120, 42), "Home", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx + 80, config.WIN_H - 200, 120, 42), "Quit", btn_font, (90, 55, 60), config.TEXT_MAIN),
    ]
    lose_btns = [
        Button((cx - 200, config.WIN_H - 200, 120, 42), "Retry", btn_font, config.ACCENT, config.WHITE),
        Button((cx - 60, config.WIN_H - 200, 120, 42), "Home", btn_font, config.BG_PANEL2, config.TEXT_MAIN),
        Button((cx + 80, config.WIN_H - 200, 120, 42), "Quit", btn_font, (90, 55, 60), config.TEXT_MAIN),
    ]

    while running:
        mouse_pos = pygame.mouse.get_pos()
        dt_fps = game_fps if state == config.PLAYING else 60

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                if state == config.HOME:
                    for b in home_btns:
                        if b.clicked(pos):
                            if b.text == "Start Game":
                                state = config.LEVEL_SELECT
                            elif b.text == "Choose Level":
                                state = config.LEVEL_SELECT
                            elif b.text == "Algorithms":
                                state = config.ALGORITHMS_INFO
                            elif b.text == "Quit":
                                running = False

                elif state == config.LEVEL_SELECT:
                    for b in level_btns:
                        if b.clicked(pos):
                            if b.text == "Easy":
                                level_key = "easy"
                                state = config.ALGORITHM_SELECT
                            elif b.text == "Medium":
                                level_key = "medium"
                                state = config.ALGORITHM_SELECT
                            elif b.text == "Hard":
                                level_key = "hard"
                                state = config.ALGORITHM_SELECT
                            elif b.text == "Back":
                                state = config.HOME

                elif state == config.ALGORITHM_SELECT:
                    for b in algo_btns:
                        if b.clicked(pos):
                            if b.text.startswith("Dijkstra"):
                                algo_key = config.ALGO_DIJKSTRA
                                maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                    level_key, scores
                                )
                                playing_buttons = make_playing_buttons()
                                state = config.PLAYING
                            elif b.text.startswith("BFS"):
                                algo_key = config.ALGO_BFS
                                maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                    level_key, scores
                                )
                                playing_buttons = make_playing_buttons()
                                state = config.PLAYING
                            elif b.text.startswith("DFS"):
                                algo_key = config.ALGO_DFS
                                maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                    level_key, scores
                                )
                                playing_buttons = make_playing_buttons()
                                state = config.PLAYING
                            elif b.text == "Back":
                                state = config.LEVEL_SELECT

                elif state == config.ALGORITHMS_INFO:
                    if algo_info_back.clicked(pos):
                        state = config.HOME

                elif state == config.PLAYING:
                    for b in playing_buttons:
                        if b.clicked(pos) and b.text == "Restart":
                            maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                level_key, scores
                            )

                elif state == config.WIN:
                    for b in win_btns:
                        if b.clicked(pos):
                            if b.text == "Play Again":
                                maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                    level_key, scores
                                )
                                playing_buttons = make_playing_buttons()
                                state = config.PLAYING
                            elif b.text == "Home":
                                state = config.HOME
                            elif b.text == "Quit":
                                running = False

                elif state == config.LOSE:
                    for b in lose_btns:
                        if b.clicked(pos):
                            if b.text == "Retry":
                                maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(
                                    level_key, scores
                                )
                                playing_buttons = make_playing_buttons()
                                state = config.PLAYING
                            elif b.text == "Home":
                                state = config.HOME
                            elif b.text == "Quit":
                                running = False

            if event.type == pygame.KEYDOWN and state == config.PLAYING:
                if event.key == pygame.K_r:
                    maze, player, start_time, steps, path, hint_len, best_rec, game_fps = new_game_session(level_key, scores)
                elif event.key == pygame.K_h:
                    path = get_hint_path(algo_key, maze, (player.x, player.y), (maze.size - 1, maze.size - 1))
                    hint_len = len(path)
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    nx, ny = player.x, player.y
                    if event.key == pygame.K_UP:
                        nx -= 1
                    elif event.key == pygame.K_DOWN:
                        nx += 1
                    elif event.key == pygame.K_LEFT:
                        ny -= 1
                    elif event.key == pygame.K_RIGHT:
                        ny += 1

                    if 0 <= nx < maze.size and 0 <= ny < maze.size:
                        if (nx, ny) not in maze.obstacles:
                            player.x, player.y = nx, ny
                            player.energy -= 1
                            steps += 1
                            path = []
                            hint_len = 0
                            if (nx, ny) in maze.recharge:
                                player.energy += 5
                            maze.move_obstacles((player.x, player.y))

        if state == config.HOME:
            draw_home_screen(win, (title_font, body_font, small_font), home_btns, mouse_pos)
        elif state == config.LEVEL_SELECT:
            draw_level_select(win, (title_font, body_font, small_font), level_btns, mouse_pos)
        elif state == config.ALGORITHM_SELECT:
            draw_algorithm_select(win, (title_font, body_font, small_font), algo_btns, mouse_pos, level_key)
        elif state == config.ALGORITHMS_INFO:
            draw_algorithms_info(win, (title_font, body_font, small_font), [algo_info_back], mouse_pos)
        elif state == config.PLAYING:
            current_time = pygame.time.get_ticks()
            time_elapsed = (current_time - start_time) // 1000

            if maze and player:
                if (player.x, player.y) == (maze.size - 1, maze.size - 1):
                    rec = scores.setdefault(level_key, {"best_steps": None, "best_time": None})
                    old_s, old_t = rec.get("best_steps"), rec.get("best_time")
                    broke_s = is_better_steps(old_s, steps)
                    broke_t = is_better_time(old_t, float(time_elapsed))
                    if broke_s:
                        rec["best_steps"] = steps
                    if broke_t:
                        rec["best_time"] = float(time_elapsed)
                    save_scores(scores)

                    hint_full = get_hint_path(algo_key, maze, (0, 0), (maze.size - 1, maze.size - 1))
                    hint_opt = len(hint_full)

                    msg = ""
                    if broke_s or broke_t:
                        msg = "\U0001F389 You Broke Your Record!"

                    win_data = {
                        "time": time_elapsed,
                        "steps": steps,
                        "hint_len": hint_opt,
                        "record_msg": msg,
                        "prev_best_steps": old_s,
                        "new_best_steps": rec["best_steps"],
                        "prev_best_time": f"{old_t:.1f}s" if old_t is not None else None,
                        "new_best_time": f"{rec['best_time']:.1f}s" if rec.get("best_time") is not None else None,
                    }
                    state = config.WIN

                elif player.energy <= 0:
                    lose_data = {"reason": "Energy depleted — recharge or plan a shorter path."}
                    state = config.LOSE

            if maze and player and state == config.PLAYING:
                draw_game(
                    win,
                    maze,
                    player,
                    (title_font, hud_font, small_font),
                    steps,
                    time_elapsed,
                    path,
                    hint_len,
                    level_key,
                    algo_key,
                    best_rec,
                    playing_buttons,
                    mouse_pos,
                )

        elif state == config.WIN:
            draw_win_screen(win, (title_font, body_font, small_font), win_data, win_btns, mouse_pos)
        elif state == config.LOSE:
            draw_lose_screen(win, (title_font, body_font, small_font), lose_data, lose_btns, mouse_pos)

        clock.tick(dt_fps)

    pygame.quit()


if __name__ == "__main__":
    main()
