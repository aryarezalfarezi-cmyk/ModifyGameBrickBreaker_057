
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


# ==========================================
# STRIKER CLASS
# ==========================================

class Striker:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 125
        self.height = 16
        self.speed = 9
        self.x = WIDTH // 2
        self.y = HEIGHT - 90

        self.id = canvas.create_rectangle(
            self.x - self.width // 2,
            self.y,
            self.x + self.width // 2,
            self.y + self.height,
            fill=CYAN,
            outline=WHITE,
            width=2
        )

    def update(self, direction):
        self.x += direction * self.speed
        self.x = max(
            self.width // 2 + 12,
            min(WIDTH - self.width // 2 - 12, self.x)
        )

        self.canvas.coords(
            self.id,
            self.x - self.width // 2,
            self.y,
            self.x + self.width // 2,
            self.y + self.height
        )

    def get_rect(self):
        return (
            self.x - self.width // 2,
            self.y,
            self.x + self.width // 2,
            self.y + self.height
        )


# ==========================================
# BALL CLASS
# ==========================================

class Ball:
    def __init__(self, canvas, level=1):
        self.canvas = canvas
        self.radius = 9
        self.speed = 5.2 + min(level - 1, 8) * 0.35

        self.x = WIDTH / 2
        self.y = HEIGHT - 112

        self.dx = random.choice([-0.65, 0.65])
        self.dy = -0.76

        self.normalize()

        self.id = canvas.create_oval(
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
            fill=YELLOW,
            outline=WHITE,
            width=2
        )

    def normalize(self):
        length = math.sqrt(self.dx ** 2 + self.dy ** 2)

        if length:
            self.dx /= length
            self.dy /= length

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if self.x - self.radius <= 12:
            self.x = 12 + self.radius
            self.dx = abs(self.dx)

        elif self.x + self.radius >= WIDTH - 12:
            self.x = WIDTH - 12 - self.radius
            self.dx = -abs(self.dx)

        if self.y - self.radius <= 70:
            self.y = 70 + self.radius
            self.dy = abs(self.dy)

        self.canvas.coords(
            self.id,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )

        return self.y - self.radius > HEIGHT - 65

    def bounce_paddle(self, paddle):
        offset = (
            self.x - paddle.x
        ) / (paddle.width / 2)

        self.dx = max(-0.9, min(0.9, offset))
        self.dy = -math.sqrt(max(0.1, 1 - self.dx ** 2))
        self.normalize()

    def bounce_block(self, block):
        x1, y1, x2, y2 = block.get_rect()

        overlap_x = min(
            self.x + self.radius - x1,
            x2 - (self.x - self.radius)
        )

        overlap_y = min(
            self.y + self.radius - y1,
            y2 - (self.y - self.radius)
        )

        if overlap_x < overlap_y:
            self.dx *= -1
        else:
            self.dy *= -1


# ==========================================
# BLOCK CLASS
# ==========================================

class Block:
    COLORS = [CYAN, PURPLE, PINK, BLUE, GREEN]

    def __init__(self, canvas, x, y, level):
        self.canvas = canvas
        self.width = 72
        self.height = 23

        self.x = x
        self.y = y

        self.color = random.choice(self.COLORS)

        self.health = (
            1 if level == 1 else random.choice([1, 1, 2])
        )

        self.id = canvas.create_rectangle(
            x, y,
            x + self.width,
            y + self.height,
            fill=self.color,
            outline=WHITE,
            width=1
        )

    def hit(self):
        self.health -= 1

        if self.health <= 0:
            self.canvas.delete(self.id)
            return True

        self.canvas.itemconfigure(
            self.id,
            fill=YELLOW
        )
        return False

    def get_rect(self):
        return (
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )


# ==========================================
# PARTICLE CLASS
# ==========================================

class Particle:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color

        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.2, 4.2)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.life = random.randint(18, 32)
        self.size = random.randint(2, 4)

        self.id = canvas.create_oval(
            x, y,
            x + self.size,
            y + self.size,
            fill=color,
            outline=""
        )

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.06
        self.life -= 1

        self.canvas.coords(
            self.id,
            self.x,
            self.y,
            self.x + self.size,
            self.y + self.size
        )

        if self.life <= 0:
            self.canvas.delete(self.id)
            return False

        return True


# ==========================================
# MAIN GAME
# ==========================================

class NeonBrickBreaker:

    def __init__(self, root):
        self.root = root
        self.root.title("NEON BRICK BREAKER")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack()

        self.keys = set()
        self.high_score = load_high_score()

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.root.bind("<Left>", self.key_down)
        self.root.bind("<Right>", self.key_down)

        self.state = "menu"
        self.reset_game()
        self.state = "menu"

        self.draw_menu()

    def reset_game(self):
        self.canvas.delete("all")

        self.score = 0
        self.lives = 5
        self.level = 1
        self.combo = 0
        self.combo_timer = 0
        self.particles = []

        self.draw_background()
        self.draw_hud()

        self.paddle = Striker(self.canvas)
        self.ball = Ball(self.canvas, self.level)
        self.blocks = self.create_blocks()

        self.update_hud()

    def draw_background(self):
        for x in range(0, WIDTH, 45):
            self.canvas.create_line(
                x, 0, x, HEIGHT,
                fill="#121a36"
            )

        for y in range(0, HEIGHT, 45):
            self.canvas.create_line(
                0, y, WIDTH, y,
                fill="#121a36"
            )

    def draw_hud(self):
        self.canvas.create_rectangle(
            0, 0, WIDTH, 58,
            fill=PANEL,
            outline=CYAN
        )

        self.score_text = self.canvas.create_text(
            100, 28,
            text="SCORE 0",
            fill=WHITE,
            font=("Consolas", 16, "bold")
        )

        self.best_text = self.canvas.create_text(
            300, 28,
            text="BEST 0",
            fill=YELLOW,
            font=("Consolas", 15)
        )

        self.level_text = self.canvas.create_text(
            490, 28,
            text="LEVEL 1",
            fill=CYAN,
            font=("Consolas", 15)
        )

        self.combo_text = self.canvas.create_text(
            650, 28,
            text="COMBO x0",
            fill=PINK,
            font=("Consolas", 15)
        )

        self.lives_text = self.canvas.create_text(
            810, 28,
            text="LIVES 5",
            fill=GREEN,
            font=("Consolas", 15)
        )

    def update_hud(self):
        self.canvas.itemconfigure(
            self.score_text,
            text=f"SCORE {self.score}"
        )

        self.canvas.itemconfigure(
            self.best_text,
            text=f"BEST {max(self.high_score, self.score)}"
        )

        self.canvas.itemconfigure(
            self.level_text,
            text=f"LEVEL {self.level}"
        )

        self.canvas.itemconfigure(
            self.combo_text,
            text=f"COMBO x{self.combo}"
        )

        self.canvas.itemconfigure(
            self.lives_text,
            text=f"LIVES {self.lives}"
        )

    def create_blocks(self):
        blocks = []

        columns = 10
        rows = min(4 + self.level, 7)

        block_width = 72
        block_height = 23
        gap_x = 12
        gap_y = 12

        total_width = (
            columns * block_width
            + (columns - 1) * gap_x
        )

        start_x = (WIDTH - total_width) // 2
        start_y = 95

        for row in range(rows):
            for col in range(columns):
                x = start_x + col * (block_width + gap_x)
                y = start_y + row * (block_height + gap_y)

                blocks.append(
                    Block(self.canvas, x, y, self.level)
                )

        return blocks

    def draw_menu(self):
        self.canvas.create_rectangle(
            100, 170, 800, 480,
            fill=PANEL,
            outline=CYAN,
            width=2,
            tags="menu"
        )

        self.canvas.create_text(
            WIDTH // 2, 230,
            text="NEON",
            fill=CYAN,
            font=("Consolas", 55, "bold"),
            tags="menu"
        )

        self.canvas.create_text(
            WIDTH // 2, 290,
            text="BRICK BREAKER",
            fill=WHITE,
            font=("Consolas", 34, "bold"),
            tags="menu"
        )

        self.canvas.create_text(
            WIDTH // 2, 350,
            text="BREAK THE BLOCKS. BEAT YOUR HIGH SCORE.",
            fill=GREEN,
            font=("Consolas", 12),
            tags="menu"
        )

        self.canvas.create_text(
            WIDTH // 2, 410,
            text="[ ENTER ] START GAME",
            fill=YELLOW,
            font=("Consolas", 19, "bold"),
            tags="menu"
        )

        self.canvas.create_text(
            WIDTH // 2, 450,
            text="ARROW KEYS / A-D : MOVE     P : PAUSE     R : RESTART",
            fill=WHITE,
            font=("Consolas", 10),
            tags="menu"
        )

    def show_overlay(self, title, subtitle):
        self.canvas.delete("overlay")

        self.canvas.create_rectangle(
            130, 240, 770, 390,
            fill=PANEL,
            outline=CYAN,
            width=2,
            tags="overlay"
        )

        self.canvas.create_text(
            WIDTH // 2, 290,
            text=title,
            fill=YELLOW,
            font=("Consolas", 35, "bold"),
            tags="overlay"
        )

        self.canvas.create_text(
            WIDTH // 2, 345,
            text=subtitle,
            fill=WHITE,
            font=("Consolas", 14),
            tags="overlay"
        )

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)

        if key in ("return", "space"):
            if self.state in ("menu", "paused"):
                self.start_game()
            elif self.state in ("gameover", "won"):
                self.reset_game()
                self.start_game()

        elif key == "p":
            self.toggle_pause()

        elif key == "r":
            self.reset_game()
            self.start_game()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def start_game(self):
        if self.state == "menu":
            self.canvas.delete("menu")

        self.canvas.delete("overlay")
        self.state = "playing"
        self.game_loop()

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.show_overlay(
                "PAUSED",
                "Press P or ENTER to continue"
            )

        elif self.state == "paused":
            self.start_game()

    def collision(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        return (
            ax1 < bx2 and ax2 > bx1
            and ay1 < by2 and ay2 > by1
        )

    def lose_life(self):
        self.lives -= 1
        self.combo = 0

        if self.lives <= 0:
            self.state = "gameover"
            self.high_score = max(self.high_score, self.score)
            save_high_score(self.high_score)
            self.show_overlay(
                "GAME OVER",
                f"SCORE: {self.score}  |  Press ENTER to retry"
            )
        else:
            self.canvas.delete(self.ball.id)
            self.ball = Ball(self.canvas, self.level)

        self.update_hud()

    def update_game(self):
        direction = 0

        if "left" in self.keys or "a" in self.keys:
            direction -= 1

        if "right" in self.keys or "d" in self.keys:
            direction += 1

        self.paddle.update(direction)

        if self.ball.update():
            self.lose_life()

            if self.state != "playing":
                return

        ball_rect = (
            self.ball.x - self.ball.radius,
            self.ball.y - self.ball.radius,
            self.ball.x + self.ball.radius,
            self.ball.y + self.ball.radius
        )

        # Collision with paddle
        if self.collision(
            ball_rect,
            self.paddle.get_rect()
        ) and self.ball.dy > 0:

            self.ball.y = (
                self.paddle.y - self.ball.radius - 1
            )
            self.ball.bounce_paddle(self.paddle)

        # Collision with blocks
        for block in self.blocks[:]:
            if self.collision(ball_rect, block.get_rect()):
                self.ball.bounce_block(block)

                if block.hit():
                    self.blocks.remove(block)

                    self.combo += 1
                    self.combo_timer = 100

                    gained = 10 + min(
                        self.combo - 1, 10
                    ) * 2

                    self.score += gained

                    for _ in range(13):
                        self.particles.append(
                            Particle(
                                self.canvas,
                                block.x + block.width // 2,
                                block.y + block.height // 2,
                                block.color
                            )
                        )
                else:
                    self.combo = 0

                break

        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

        # Next level
        if not self.blocks:
            self.level += 1
            self.lives = min(5, self.lives + 1)

            self.canvas.delete(self.paddle.id)
            self.canvas.delete(self.ball.id)

            self.paddle = Striker(self.canvas)
            self.ball = Ball(self.canvas, self.level)
            self.blocks = self.create_blocks()

            self.combo = 0

            self.show_overlay(
                f"LEVEL {self.level}",
                "Press ENTER to continue"
            )

            self.state = "levelup"

        self.update_hud()

    def game_loop(self):
        if self.state != "playing":
            return

        self.update_game()

        if self.state == "playing":
            self.root.after(FPS, self.game_loop)

        elif self.state == "levelup":
            self.state = "paused"

    def run(self):
        self.root.mainloop()


# ==========================================
# RUN GAME
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    game = NeonBrickBreaker(root)
    game.run()
