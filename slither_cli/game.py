"""The Snake game itself, rendered with curses."""

from __future__ import annotations

import curses
import random
from collections import deque

from . import __version__
from .banner import (
    BANNER,
    BANNER_SMALL,
    BANNER_SMALL_WIDTH,
    BANNER_WIDTH,
)
from .storage import load_stats, record_game

# --- Color pair ids ---------------------------------------------------------
CP_SNAKE = 1
CP_HEAD = 2
CP_FOOD = 3
CP_BORDER = 4
CP_SCORE = 5
CP_DIM = 6
CP_ACCENT = 7
CP_GOLD = 8
# Rainbow pairs for the banner (a gradient down the rows).
RAINBOW = [10, 11, 12, 13, 14, 15]

# --- Grid / speed tuning ----------------------------------------------------
MAX_GRID_W = 32
MAX_GRID_H = 20
MIN_GRID_W = 12
MIN_GRID_H = 8
CELL_W = 2  # each logical cell is two terminal columns wide, for square-ish cells

START_DELAY = 120  # ms per tick at the start
MIN_DELAY = 55  # fastest tick
SPEED_STEP = 4  # every N points, get a little faster
SPEED_DECREMENT = 6  # ms shaved off per step

# Cell glyphs (two columns each).
BODY = "██"
HEAD = "██"
FOOD = "◆◆"

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def _init_colors() -> None:
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK
    curses.init_pair(CP_SNAKE, curses.COLOR_GREEN, bg)
    curses.init_pair(CP_HEAD, curses.COLOR_YELLOW, bg)
    curses.init_pair(CP_FOOD, curses.COLOR_RED, bg)
    curses.init_pair(CP_BORDER, curses.COLOR_CYAN, bg)
    curses.init_pair(CP_SCORE, curses.COLOR_YELLOW, bg)
    curses.init_pair(CP_DIM, curses.COLOR_WHITE, bg)
    curses.init_pair(CP_ACCENT, curses.COLOR_MAGENTA, bg)
    curses.init_pair(CP_GOLD, curses.COLOR_YELLOW, bg)
    rainbow_colors = [
        curses.COLOR_MAGENTA,
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
        curses.COLOR_GREEN,
        curses.COLOR_CYAN,
        curses.COLOR_BLUE,
    ]
    for pair_id, color in zip(RAINBOW, rainbow_colors):
        curses.init_pair(pair_id, color, bg)


class QuitGame(Exception):
    """Raised to unwind cleanly out of any screen and exit the program."""


class SlitherGame:
    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        curses.curs_set(0)
        _init_colors()
        stdscr.keypad(True)

    # --- small drawing helpers ---------------------------------------------
    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """addstr that never raises at the screen edges."""
        maxy, maxx = self.stdscr.getmaxyx()
        if y < 0 or y >= maxy or x < 0 or x >= maxx:
            return
        # Trim so we never write past the last column (which curses rejects).
        text = text[: maxx - x]
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def _center_x(self, width: int) -> int:
        _, maxx = self.stdscr.getmaxyx()
        return max(0, (maxx - width) // 2)

    def _draw_banner(self, top: int) -> int:
        """Draw the rainbow banner centered. Returns the y after the banner."""
        _, maxx = self.stdscr.getmaxyx()
        if maxx >= BANNER_WIDTH + 2:
            lines, width = BANNER, BANNER_WIDTH
        else:
            lines, width = BANNER_SMALL, BANNER_SMALL_WIDTH
        x = self._center_x(width)
        for i, line in enumerate(lines):
            attr = curses.color_pair(RAINBOW[i % len(RAINBOW)]) | curses.A_BOLD
            self._safe_addstr(top + i, x, line, attr)
        return top + len(lines)

    # --- menu ---------------------------------------------------------------
    def show_menu(self) -> None:
        stats = load_stats()
        self.stdscr.nodelay(False)
        self.stdscr.timeout(-1)
        while True:
            self.stdscr.erase()
            maxy, maxx = self.stdscr.getmaxyx()
            if maxy < 12 or maxx < 34:
                self._draw_too_small()
                self.stdscr.refresh()
                key = self.stdscr.getch()
                if key in (ord("q"), ord("Q")):
                    raise QuitGame
                continue

            top = max(1, (maxy - 17) // 2)
            y = self._draw_banner(top) + 1

            tagline = "the classic snake, right in your terminal"
            self._safe_addstr(y, self._center_x(len(tagline)), tagline,
                              curses.color_pair(CP_ACCENT))
            y += 2

            hs = f"🏆  High Score: {stats['high_score']}"
            gp = f"🎮  Games Played: {stats['games_played']}"
            self._safe_addstr(y, self._center_x(len(hs) + 1), hs,
                              curses.color_pair(CP_GOLD) | curses.A_BOLD)
            y += 1
            self._safe_addstr(y, self._center_x(len(gp) + 1), gp,
                              curses.color_pair(CP_DIM))
            y += 2

            prompt = "▶  Press SPACE or ENTER to play"
            self._safe_addstr(y, self._center_x(len(prompt)), prompt,
                              curses.color_pair(CP_SNAKE) | curses.A_BOLD)
            y += 2

            controls = "Move: ← ↑ ↓ →  or  W A S D      Pause: P      Quit: Q"
            self._safe_addstr(y, self._center_x(len(controls)), controls,
                              curses.color_pair(CP_DIM))
            y += 2

            credit = "~ crafted with 🐍 & ♥ by Dibyo Dhara ~"
            self._safe_addstr(y, self._center_x(len(credit) + 2), credit,
                              curses.color_pair(CP_ACCENT) | curses.A_BOLD)
            y += 1
            version = f"slither-cli v{__version__}"
            self._safe_addstr(y, self._center_x(len(version)), version,
                              curses.color_pair(CP_BORDER))

            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key in (ord("q"), ord("Q")):
                raise QuitGame
            if key in (ord(" "), curses.KEY_ENTER, 10, 13):
                self.play()
                stats = load_stats()  # refresh high score after a game

    def _draw_too_small(self) -> None:
        self.stdscr.erase()
        msg = "Terminal too small — please enlarge the window."
        maxy, maxx = self.stdscr.getmaxyx()
        self._safe_addstr(maxy // 2, max(0, (maxx - len(msg)) // 2), msg,
                          curses.color_pair(CP_FOOD) | curses.A_BOLD)
        hint = "(press Q to quit)"
        self._safe_addstr(maxy // 2 + 1, max(0, (maxx - len(hint)) // 2), hint,
                          curses.color_pair(CP_DIM))

    # --- play ---------------------------------------------------------------
    def _compute_grid(self) -> tuple[int, int, int, int]:
        """Return (grid_w, grid_h, origin_x, origin_y) for the play box."""
        maxy, maxx = self.stdscr.getmaxyx()
        # Reserve: 1 header line, 2 border lines, 1 footer line, plus margins.
        avail_w = (maxx - 2 - 2) // CELL_W  # minus 2 border cols, minus margin
        avail_h = maxy - 5
        gw = max(MIN_GRID_W, min(MAX_GRID_W, avail_w))
        gh = max(MIN_GRID_H, min(MAX_GRID_H, avail_h))
        box_w = gw * CELL_W + 2
        box_h = gh + 2
        origin_x = max(0, (maxx - box_w) // 2)
        origin_y = max(1, (maxy - box_h) // 2)
        return gw, gh, origin_x, origin_y

    def _draw_box(self, ox: int, oy: int, gw: int, gh: int) -> None:
        inner_w = gw * CELL_W
        border = curses.color_pair(CP_BORDER) | curses.A_BOLD
        self._safe_addstr(oy, ox, "╔" + "═" * inner_w + "╗", border)
        for row in range(gh):
            self._safe_addstr(oy + 1 + row, ox, "║", border)
            self._safe_addstr(oy + 1 + row, ox + 1 + inner_w, "║", border)
        self._safe_addstr(oy + 1 + gh, ox, "╚" + "═" * inner_w + "╝", border)

    def _cell_xy(self, ox: int, oy: int, cx: int, cy: int) -> tuple[int, int]:
        return oy + 1 + cy, ox + 1 + cx * CELL_W

    def _spawn_food(self, gw: int, gh: int, snake: set) -> tuple[int, int]:
        free = [(x, y) for x in range(gw) for y in range(gh) if (x, y) not in snake]
        if not free:
            return (-1, -1)  # board full — a win, effectively
        return random.choice(free)

    def play(self) -> None:
        """Run rounds until the player chooses the menu or quits.

        A single round is played by `_play_round`, which returns the final
        score plus whether the board was cleared. `_game_over` then decides
        what happens next — restart (loop again), menu (return), or quit.
        """
        while True:
            score, won = self._play_round()
            if score is None:  # player pressed Q mid-round — don't count it
                raise QuitGame
            action = self._game_over(score, won=won)
            if action == "quit":
                raise QuitGame
            if action == "menu":
                return
            # action == "restart": loop and play another round

    def _play_round(self) -> tuple:
        """Play one round. Returns (score, won). score is None if the player quit."""
        gw, gh, ox, oy = self._compute_grid()

        cx, cy = gw // 2, gh // 2
        snake = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        snake_set = set(snake)
        direction = RIGHT
        pending = RIGHT
        score = 0
        food = self._spawn_food(gw, gh, snake_set)

        self.stdscr.nodelay(True)
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        self._render_play(score, snake, food, gw, gh, ox, oy)

        while True:
            delay = max(MIN_DELAY, START_DELAY - (score // SPEED_STEP) * SPEED_DECREMENT)
            self.stdscr.timeout(delay)
            key = self.stdscr.getch()

            if key in (ord("q"), ord("Q")):
                return None, False
            if key in (ord("p"), ord("P")):
                if self._pause() == "quit":
                    return None, False
            new_dir = self._key_to_dir(key)
            if new_dir and new_dir != opposite[direction]:
                pending = new_dir

            direction = pending
            hx, hy = snake[0]
            nx, ny = hx + direction[0], hy + direction[1]

            # Wall or self collision ends the round.
            hit_wall = nx < 0 or nx >= gw or ny < 0 or ny >= gh
            # Moving into the current tail cell is fine (it will move away),
            # unless we're about to grow.
            growing = (nx, ny) == food
            body_to_check = snake_set if growing else (snake_set - {snake[-1]})
            if hit_wall or (nx, ny) in body_to_check:
                return score, False

            snake.appendleft((nx, ny))
            snake_set.add((nx, ny))
            if growing:
                score += 1
                food = self._spawn_food(gw, gh, snake_set)
                if food == (-1, -1):  # filled the whole board!
                    return score, True
            else:
                tail = snake.pop()
                snake_set.discard(tail)

            self._render_play(score, snake, food, gw, gh, ox, oy)

    def _render_play(self, score, snake, food, gw, gh, ox, oy) -> None:
        self.stdscr.erase()
        stats = load_stats()

        # Header
        header = f" SCORE {score:<4}   HIGH {max(score, stats['high_score']):<4} "
        self._safe_addstr(oy - 1, ox, header, curses.color_pair(CP_SCORE) | curses.A_BOLD)

        self._draw_box(ox, oy, gw, gh)

        # Food
        if food != (-1, -1):
            fy, fx = self._cell_xy(ox, oy, food[0], food[1])
            self._safe_addstr(fy, fx, FOOD, curses.color_pair(CP_FOOD) | curses.A_BOLD)

        # Snake (head first)
        for i, (sx, sy) in enumerate(snake):
            y, x = self._cell_xy(ox, oy, sx, sy)
            if i == 0:
                self._safe_addstr(y, x, HEAD, curses.color_pair(CP_HEAD) | curses.A_BOLD)
            else:
                self._safe_addstr(y, x, BODY, curses.color_pair(CP_SNAKE))

        footer = "P pause · Q quit"
        self._safe_addstr(oy + gh + 2, ox, footer, curses.color_pair(CP_DIM))
        self.stdscr.refresh()

    @staticmethod
    def _key_to_dir(key: int):
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            return UP
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            return DOWN
        if key in (curses.KEY_LEFT, ord("a"), ord("A")):
            return LEFT
        if key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            return RIGHT
        return None

    def _pause(self) -> str:
        self.stdscr.nodelay(False)
        self.stdscr.timeout(-1)
        maxy, maxx = self.stdscr.getmaxyx()
        msg = "  PAUSED  "
        hint = "press P to resume · Q to quit"
        self._safe_addstr(maxy // 2, (maxx - len(msg)) // 2, msg,
                          curses.color_pair(CP_ACCENT) | curses.A_BOLD | curses.A_REVERSE)
        self._safe_addstr(maxy // 2 + 1, (maxx - len(hint)) // 2, hint,
                          curses.color_pair(CP_DIM))
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key in (ord("p"), ord("P")):
                self.stdscr.nodelay(True)
                return "resume"
            if key in (ord("q"), ord("Q")):
                return "quit"

    def _game_over(self, score, won=False) -> str:
        """Show the game-over screen. Returns 'restart', 'menu', or 'quit'."""
        high_score, is_record = record_game(score)
        self.stdscr.nodelay(False)
        self.stdscr.timeout(-1)
        self.stdscr.erase()

        maxy, maxx = self.stdscr.getmaxyx()
        cy = max(1, maxy // 2 - 4)

        title = "🎉  YOU WIN!  🎉" if won else "GAME OVER"
        title_attr = (curses.color_pair(CP_GOLD if won else CP_FOOD)
                      | curses.A_BOLD)
        self._safe_addstr(cy, self._center_x(len(title) + (2 if won else 0)),
                          title, title_attr)

        lines = [
            (f"Score: {score}", curses.color_pair(CP_SCORE) | curses.A_BOLD),
        ]
        if is_record:
            lines.append(("★  NEW HIGH SCORE!  ★",
                          curses.color_pair(CP_GOLD) | curses.A_BOLD | curses.A_BLINK))
        else:
            lines.append((f"High Score: {high_score}", curses.color_pair(CP_DIM)))
        lines.append(("", 0))
        lines.append(("R  play again", curses.color_pair(CP_SNAKE) | curses.A_BOLD))
        lines.append(("M  main menu", curses.color_pair(CP_ACCENT)))
        lines.append(("Q  quit", curses.color_pair(CP_DIM)))

        yy = cy + 2
        for text, attr in lines:
            if text:
                self._safe_addstr(yy, self._center_x(len(text)), text, attr)
            yy += 1
        self.stdscr.refresh()

        while True:
            key = self.stdscr.getch()
            if key in (ord("q"), ord("Q")):
                return "quit"
            if key in (ord("m"), ord("M")):
                return "menu"
            if key in (ord("r"), ord("R"), ord(" "), curses.KEY_ENTER, 10, 13):
                return "restart"


def run(stdscr: "curses._CursesWindow") -> None:
    game = SlitherGame(stdscr)
    try:
        game.show_menu()
    except QuitGame:
        pass
