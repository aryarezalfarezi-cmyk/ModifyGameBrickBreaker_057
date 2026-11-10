
import tkinter as tk
import random
import math
import json
from pathlib import Path

# ==========================================
# NEON BRICK BREAKER
# Python 3.15.2 + Tkinter
# Object Oriented Programming
# ==========================================

WIDTH = 900
HEIGHT = 650
FPS = 16

BG = "#0a0c1e"
PANEL = "#121630"
WHITE = "#f0f5ff"
CYAN = "#28e1ff"
BLUE = "#4173ff"
PURPLE = "#b44bff"
PINK = "#ff419f"
YELLOW = "#ffdc4b"
RED = "#ff4b5a"
GREEN = "#46f5a5"

HIGH_SCORE_FILE = Path("neon_highscore.json")


def load_high_score():
    try:
        data = json.loads(
            HIGH_SCORE_FILE.read_text(encoding="utf-8")
        )
        return int(data.get("high_score", 0))
    except (OSError, ValueError, TypeError):
        return 0


def save_high_score(score):
    try:
        HIGH_SCORE_FILE.write_text(
            json.dumps({"high_score": score}, indent=4),
            encoding="utf-8"
        )
    except OSError:
        pass


