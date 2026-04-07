"""Load / save best steps and best time per level (JSON)."""

import json
import os

from config import SCORES_FILE


def default_scores():
    return {
        "easy": {"best_steps": None, "best_time": None},
        "medium": {"best_steps": None, "best_time": None},
        "hard": {"best_steps": None, "best_time": None},
    }


def load_scores():
    data = default_scores()
    if os.path.isfile(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            for k in data:
                if k in loaded and isinstance(loaded[k], dict):
                    data[k]["best_steps"] = loaded[k].get("best_steps")
                    data[k]["best_time"] = loaded[k].get("best_time")
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_scores(data):
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def is_better_steps(old, new):
    if old is None:
        return True
    return new < old


def is_better_time(old, new):
    if old is None:
        return True
    return new < old
