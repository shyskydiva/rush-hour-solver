"""The gameplay screen: the board, your moves, and the solver."""
import math
import time

import pygame

from solver.bfs import solve
from solver.board import TARGET, load_board
from solver.moves import apply_move, legal_moves
from visual import draw, theme

# Layout
BOARD_X, BOARD_Y = 40, 92
PANEL_X = BOARD_X + theme.BOARD_SIZE + 44     # left edge of the right-hand column
PANEL_W = theme.WIDTH - 40 - PANEL_X          # its width

# Timing, in seconds
AUTO_SOLVE_DELAY = 0.55   # pause between moves while Auto-solve drives
GLIDE = 0.035             # how quickly cars slide to their new square (smaller = snappier)
NUDGE_TIME = 0.12         # how long a blocked car bumps before snapping back
EXIT_TIME = 0.7           # how long the winning car takes to drive off

ARROW_KEYS = {
    # key: (moves horizontally?, step)
    pygame.K_LEFT: (True, -1),
    pygame.K_RIGHT: (True, 1),
    pygame.K_UP: (False, -1),
    pygame.K_DOWN: (False, 1),
}


def cell_rect(row, col):
    """The pixel rect of one square on the board."""
    return pygame.Rect(BOARD_X + theme.BOARD_PAD + col * theme.STEP,
                       BOARD_Y + theme.BOARD_PAD + row * theme.STEP, theme.CELL, theme.CELL)


def car_rect(car):
    """The pixel rect a car covers on the board."""
    rect = cell_rect(car.row, car.col)
    span = car.length * theme.STEP - theme.GAP
    if car.horizontal:
        rect.width = span
    else:
        rect.height = span
    return rect


def car_colors(board):
    """Give X the hot pink and every other car a cool tone, in letter order."""
    colors = {TARGET: theme.HOT_PINK}
    others = sorted(name for name in board.cars if name != TARGET)
    for i, name in enumerate(others):
        colors[name] = theme.CAR_COLORS[i % len(theme.CAR_COLORS)]
    return colors


def rating(moves, best, assisted):
    """How well the level went: (words, number of gems out of 3)."""
    if assisted:
        return "SOLVER ASSIST", 0
    if moves <= best:
        return "PERFECT RUN", 3
    if moves <= best + 3:
        return "CLEAN RUN", 2
    return "YOU MADE IT", 1


def format_time(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02}"


class GameScreen:
    def __init__(self, app, index):
        self.app = app
        self.index = index
        self.name, path = app.levels[index]
        self.start = load_board(path)
        self.colors = car_colors(self.start)
        self.best = app.best_moves(index)
        self.restart()

    def restart(self):
        """Put every car back where the level starts."""
        self.board = self.start
        self.history = []          # list of (move, board before that move), for undo
        self.selected = None       # letter of the car the player clicked
        self.revealed = False      # has the player asked the solver for help?
        self.playing = False       # is Auto-solve driving right now?
        self.paused = False        # is the pause menu open?
        self.auto_timer = 0
        self.elapsed = 0
        self.won = False
        self.result = None         # (words, gems) once the level is cleared
        self.exit_timer = None     # counts up during the exit run
        self.nudge = None          # [car letter, dx, dy, time left] after a blocked move
        self.solution_cache = None
        # Where each car is drawn right now. It slides toward its real square each frame.
        self.shown = {name: list(car_rect(car).topleft) for name, car in self.board.cars.items()}

    # --- Game actions ---

    def solution(self):
        """Solve from the current board and return (moves, boards checked, milliseconds).

        The answer is saved so we only solve each board once.
        """
        key = self.board.key()
        if self.solution_cache is None or self.solution_cache[0] != key:
            started = time.perf_counter()
            moves, checked = solve(self.board)
            ms = round((time.perf_counter() - started) * 1000)
            self.solution_cache = (key, moves, checked, ms)
        return self.solution_cache[1:]

    def make_move(self, move):
        if self.won:
            return
        self.history.append((move, self.board))
        self.board = apply_move(self.board, move)
        self.selected = None
        if self.board.is_solved():
            self.win()

    def win(self):
        self.won = True
        self.playing = False
        self.exit_timer = 0
        moves = len(self.history)
        self.result = rating(moves, self.best, self.revealed)
        self.app.record_clear(self.index, moves, self.result[1])

    def undo(self):
        if self.won or len(self.history) == 0:
            return
        _, before = self.history.pop()
        self.board = before
        self.selected = None
        self.playing = False

    def toggle_auto_solve(self):
        """Start or pause the solver driving the cars."""
        if self.won:
            return
        if self.playing:
            self.playing = False
        else:
            self.playing = True
            self.revealed = True
            self.selected = None
            self.auto_timer = 0

    def pause(self):
        """Open the pause menu. The timer and Auto-solve stop until you resume."""
        if not self.won:
            self.paused = True
            self.selected = None

    def resume(self):
        self.paused = False

    def next_step(self):
        """Make just the solver's next move."""
        self.playing = False
        moves = self.solution()[0]
        if moves:
            self.make_move(moves[0])

    def arrow_move(self, key):
        """Slide the selected car one square with an arrow key, or nudge it if blocked."""
        if self.selected is None:
            return
        car = self.board.cars[self.selected]
        horizontal, step = ARROW_KEYS[key]
        if horizontal != car.horizontal:
            return  # this car doesn't move that way
        for move in legal_moves(self.board):
            if move.car_name == car.name and move.steps == step:
                self.make_move(move)
                if not self.won:
                    self.selected = car.name  # keep it selected so you can keep sliding
                return
        # Blocked: bump 4px toward whatever is in the way, then snap back.
        dx, dy = (step, 0) if horizontal else (0, step)
        self.nudge = [car.name, dx * 4, dy * 4, NUDGE_TIME]

    def targets(self):
        """Every square the selected car can slide to, as (square rect, move)."""
        if self.selected is None or self.won:
            return []
        car = self.board.cars[self.selected]
        result = []
        for move in legal_moves(self.board):
            if move.car_name == self.selected:
                squares = car.moved(move.steps).cells()
                row, col = squares[-1] if move.steps > 0 else squares[0]  # the leading square
                result.append((cell_rect(row, col), move))
        return result

    # --- Buttons ---

    def buttons(self):
        """The buttons on screen right now (they change once the solver is revealed).

        Before Auto-solve: one AUTO-SOLVE button.
        While it drives: one PAUSE SOLVER button.
        While it's paused: RESUME, plus NEXT STEP to go one move at a time.
        """
        half = (PANEL_W - 10) // 2
        row1, row2 = 458, 520
        level_label = f"LVL {self.index + 1:02} · {self.name.upper()}"
        chip_width = draw.render_text(level_label, theme.font("bold", 14), theme.CYAN, 2).get_width() + 32
        menu_x = theme.WIDTH - 40 - 44
        result = [
            draw.Button((menu_x, 26, 44, 44), "", self.pause, cut=8),
            draw.Button((menu_x - 10 - chip_width, 26, chip_width, 44), level_label,
                        self.app.show_levels, style="chip", size=14, cut=8),
            draw.Button((PANEL_X, row2, half, 46), "UNDO", self.undo, size=15),
            draw.Button((PANEL_X + half + 10, row2, half, 46), "RESET", self.restart, size=15),
        ]
        if self.playing:
            result.append(draw.Button((PANEL_X, row1, PANEL_W, 52), "PAUSE SOLVER",
                                      self.toggle_auto_solve, style="pink"))
        elif self.revealed:
            result.append(draw.Button((PANEL_X, row1, half, 52), "RESUME",
                                      self.toggle_auto_solve, style="pink"))
            result.append(draw.Button((PANEL_X + half + 10, row1, half, 52), "NEXT STEP",
                                      self.next_step, style="cyan"))
        else:
            result.append(draw.Button((PANEL_X, row1, PANEL_W, 52), "AUTO-SOLVE",
                                      self.toggle_auto_solve, style="pink"))
        return result

    def win_buttons(self):
        top = 404
        if self.index + 1 < len(self.app.levels):
            first = draw.Button((80, top, 260, 54), "NEXT LEVEL", lambda: self.app.play(self.index + 1),
                                style="pink", size=17, cut=12)
        else:
            first = draw.Button((80, top, 260, 54), "ALL LEVELS", self.app.show_levels,
                                style="pink", size=17, cut=12)
        return [
            first,
            draw.Button((350, top, 170, 54), "REPLAY", self.restart, cut=12),
            draw.Button((530, top, 170, 54), "MENU", self.app.show_title, cut=12),
        ]

    def pause_buttons(self):
        top = 330
        return [
            draw.Button((80, top, 260, 54), "RESUME", self.resume, style="pink", size=17, cut=12),
            draw.Button((350, top, 170, 54), "RESTART", self.restart, cut=12),
            draw.Button((530, top, 170, 54), "LEVELS", self.app.show_levels, cut=12),
            draw.Button((710, top, 170, 54), "MENU", self.app.show_title, cut=12),
        ]

    # --- Events and updates ---

    def handle(self, event):
        if self.paused:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.resume()
                return
            for button in self.pause_buttons():
                if button.handle(event):
                    return
            return

        if self.won:
            if self.exit_timer >= EXIT_TIME:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.win_buttons()[0].on_click()
                    return
                for button in self.win_buttons():
                    if button.handle(event):
                        return
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.selected is not None:
                    self.selected = None
                else:
                    self.pause()
            elif event.key == pygame.K_p:
                self.pause()
            elif event.key in ARROW_KEYS:
                self.arrow_move(event.key)
            elif event.key in (pygame.K_z, pygame.K_BACKSPACE):
                self.undo()
            elif event.key == pygame.K_r:
                self.restart()
            elif event.key == pygame.K_SPACE:
                self.toggle_auto_solve()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons():
                if button.handle(event):
                    return
            for rect, move in self.targets():
                if rect.collidepoint(event.pos):
                    self.make_move(move)
                    return
            for name, car in self.board.cars.items():
                if car_rect(car).collidepoint(event.pos):
                    self.playing = False
                    self.selected = None if self.selected == name else name
                    return
            self.selected = None  # clicked somewhere empty

    def update(self, dt):
        if self.paused:
            return  # everything freezes, including the timer

        if not self.won:
            self.elapsed = self.elapsed + dt

        if self.playing:
            self.auto_timer = self.auto_timer + dt
            if self.auto_timer >= AUTO_SOLVE_DELAY:
                self.auto_timer = 0
                moves = self.solution()[0]
                if moves:
                    self.make_move(moves[0])
                else:
                    self.playing = False

        # Glide: move each car part of the way toward its real square (fast at first, then easing out).
        smooth = 1 - math.exp(-dt / GLIDE)
        for name, car in self.board.cars.items():
            target_x, target_y = car_rect(car).topleft
            shown = self.shown[name]
            shown[0] = shown[0] + (target_x - shown[0]) * smooth
            shown[1] = shown[1] + (target_y - shown[1]) * smooth
            if abs(target_x - shown[0]) < 0.5 and abs(target_y - shown[1]) < 0.5:
                shown[0], shown[1] = target_x, target_y

        if self.nudge is not None:
            self.nudge[3] = self.nudge[3] - dt
            if self.nudge[3] <= 0:
                self.nudge = None

        if self.exit_timer is not None:
            self.exit_timer = self.exit_timer + dt

    # --- Drawing ---

    def draw(self, surface):
        surface.fill(theme.ASPHALT)
        draw.slanted_band(surface, theme.STRIPE, theme.WIDTH - 300, 360, -40, 720)
        draw.slanted_band(surface, theme.HOT_PINK, theme.WIDTH - 14, 8, -40, 720)

        self.draw_header(surface)
        self.draw_board(surface)
        self.draw_status(surface)
        self.draw_stats(surface)
        self.draw_moves_panel(surface)
        for button in self.buttons():
            button.draw(surface)
        # Pause icon on the menu button
        menu_x = theme.WIDTH - 40 - 44
        pygame.draw.rect(surface, theme.TEXT, (menu_x + 15, 41, 5, 14))
        pygame.draw.rect(surface, theme.TEXT, (menu_x + 24, 41, 5, 14))

        if self.won and self.exit_timer >= EXIT_TIME:
            self.draw_win(surface)
        if self.paused:
            self.draw_pause(surface)

    def draw_pause(self, surface):
        shade = pygame.Surface((theme.WIDTH, theme.HEIGHT), pygame.SRCALPHA)
        shade.fill((*theme.ASPHALT, 230))
        surface.blit(shade, (0, 0))

        top = 200
        draw.text(surface, f"LEVEL {self.index + 1:02} · {self.name.upper()}", theme.font("bold", 14),
                  theme.CYAN, (80, top), spacing=4)
        draw.text(surface, "PAUSED", theme.font("display", 78), theme.TEXT, (80, top + 18),
                  shadow=theme.HOT_PINK, shadow_offset=5)
        for button in self.pause_buttons():
            button.draw(surface)
        draw.text(surface, f"{len(self.history)} MOVES · {format_time(self.elapsed)}   ·   ESC TO RESUME",
                  theme.font("semibold", 13), theme.FAINT, (80, top + 210), spacing=3)

    def draw_header(self, surface):
        logo = draw.text(surface, "PINK LANE", theme.font("display", 26), theme.HOT_PINK, (40, 48), anchor="midleft")
        draw.text(surface, "// RUSH HOUR SOLVER", theme.font("semibold", 13), theme.MUTED,
                  (logo.right + 14, 48), spacing=3, anchor="midleft")

    def draw_board(self, surface):
        frame = pygame.Rect(BOARD_X, BOARD_Y, theme.BOARD_SIZE, theme.BOARD_SIZE)
        draw.cut_corner(surface, theme.LINE, frame, 20)
        draw.cut_corner(surface, theme.BOARD, frame.inflate(-4, -4), 19)
        for row in range(6):
            for col in range(6):
                pygame.draw.rect(surface, theme.CELL_COLOR, cell_rect(row, col), border_radius=6)

        # The exit: a pink notch on the right edge of X's row
        exit_row = self.start.cars[TARGET].row
        pygame.draw.rect(surface, theme.HOT_PINK, (BOARD_X + theme.BOARD_SIZE - 18, cell_rect(exit_row, 0).y, 18, theme.CELL))

        # Cars. During the exit run they're clipped so X disappears through the exit.
        surface.set_clip(frame.inflate(-4, -4).union(pygame.Rect(frame.right - 18, frame.y, 18, frame.h)))
        for name, car in self.board.cars.items():
            x, y = self.shown[name]
            if self.nudge is not None and self.nudge[0] == name:
                x, y = x + self.nudge[1], y + self.nudge[2]
            if name == TARGET and self.exit_timer is not None:
                progress = min(self.exit_timer / EXIT_TIME, 1)
                x = x + 560 * progress * progress  # speeds up as it goes
                self.draw_speed_lines(surface, x, y, progress)
            rect = pygame.Rect(round(x), round(y), *car_rect(car).size)
            draw.draw_car(surface, rect, self.colors[name], car.horizontal, hero=name == TARGET)
            if name == self.selected:
                pygame.draw.rect(surface, theme.CYAN, rect.inflate(6, 6), 3, border_radius=16)
        surface.set_clip(None)

        # Hint: once the solver is revealed, outline where its next move goes.
        moves = self.solution()[0]
        if self.revealed and self.selected is None and not self.won and moves:
            hint = moves[0]
            ghost = self.board.cars[hint.car_name].moved(hint.steps)
            draw.dashed_rect(surface, theme.CYAN, car_rect(ghost))

        # Squares the selected car can slide to
        for rect, move in self.targets():
            pygame.draw.rect(surface, draw.mix(theme.CELL_COLOR, theme.CYAN, 0.10), rect, border_radius=6)
            draw.dashed_rect(surface, theme.CYAN, rect)
            draw.diamond(surface, theme.CYAN, rect.center, 18)

    def draw_speed_lines(self, surface, car_x, car_y, progress):
        """Short lines streaming behind the winning car, fading as it leaves."""
        fade = progress
        for offset, length, color in [(16, 90, theme.LINE), (30, 60, theme.HOT_PINK), (46, 80, theme.LINE)]:
            faded = draw.mix(color, theme.BOARD, fade)
            pygame.draw.rect(surface, faded, (car_x - length - 8, car_y + offset, length * progress + 10, 4))

    def draw_status(self, surface):
        y = BOARD_Y + theme.BOARD_SIZE + 14
        draw.play_arrows(surface, theme.HOT_PINK, BOARD_X, y + 2, 12)
        if self.won:
            status = "LANE CLEAR"
        elif self.playing:
            status = "SOLVER DRIVING..."
        elif self.selected is not None:
            status = f"CLICK A SPOT OR USE THE ARROW KEYS TO SLIDE {self.selected}"
        else:
            status = "CLICK A CAR TO MOVE IT"
        draw.text(surface, status, theme.font("semibold", 14), theme.MUTED, (BOARD_X + 34, y), spacing=1)

    def draw_stats(self, surface):
        width = (PANEL_W - 20) // 3
        stats = [
            ("MOVES", f"{len(self.history):02}", theme.TEXT, theme.TEXT),
            ("BEST", f"{self.best:02}", theme.HOT_PINK, theme.HOT_PINK),
            ("TIME", format_time(self.elapsed), theme.CYAN, theme.CYAN),
        ]
        for i, (label, value, edge, value_color) in enumerate(stats):
            x = PANEL_X + i * (width + 10)
            pygame.draw.rect(surface, theme.PANEL, (x, BOARD_Y, width, 76))
            pygame.draw.rect(surface, edge, (x, BOARD_Y, width, 2))
            draw.text(surface, label, theme.font("semibold", 12), theme.MUTED, (x + 14, BOARD_Y + 12), spacing=2)
            draw.text(surface, value, theme.font("bold", 30), value_color, (x + 14, BOARD_Y + 28))

    def draw_moves_panel(self, surface):
        x, y, w, h = PANEL_X, BOARD_Y + 90, PANEL_W, 262
        pygame.draw.polygon(surface, theme.PANEL, [(x, y), (x + w, y), (x + w, y + h - 14), (x + w - 14, y + h), (x, y + h)])

        moves, checked, _ = self.solution()
        title = "SOLVER // BFS" if self.revealed else "YOUR MOVES"
        draw.text(surface, title, theme.font("bold", 14), theme.TEXT, (x + 16, y + 16), spacing=2)
        if self.revealed and moves is not None and not self.won:
            # How many board layouts BFS looked at to find the shortest way out from here
            draw.text(surface, f"{checked} boards checked · {len(moves)} to go", theme.font("regular", 13),
                      theme.MUTED, (x + w - 16, y + 16), anchor="topright")

        rows = self.panel_rows(moves)
        if len(rows) == 0:
            lines = [(line, theme.font("regular", 15), theme.SOFT)
                     for line in draw.wrap("Your moves will show up here.", theme.font("regular", 15), w - 40)]
            lines += [(line, theme.font("regular", 14), theme.MUTED)
                      for line in draw.wrap("Stuck? Press Auto-solve and the BFS solver takes the wheel.",
                                            theme.font("regular", 14), w - 40)]
            line_y = y + 100
            for words, line_font, color in lines:
                draw.text(surface, words, line_font, color, (x + 24, line_y))
                line_y = line_y + 22
            return

        row_y = y + 44
        for number, move, tag, upcoming_next in rows:
            box = pygame.Rect(x + 16, row_y, w - 32, 34)
            pygame.draw.rect(surface, theme.RAISED if upcoming_next else theme.ROW, box)
            if upcoming_next:
                pygame.draw.rect(surface, theme.CYAN, (box.x, box.y, 3, box.h))
            done = tag == "DONE"
            draw.text(surface, f"{number:02}", theme.font("bold", 14), theme.CYAN if upcoming_next else theme.MUTED,
                      (box.x + 12, box.centery), anchor="midleft")
            pygame.draw.rect(surface, self.colors[move.car_name], (box.x + 44, box.centery - 6, 12, 12))
            words = str(move)
            if self.is_exit_move(move, number):
                words = words + " · exit"
            draw.text(surface, words, theme.font("semibold" if upcoming_next else "regular", 15),
                      theme.FAINT if done else theme.SOFT, (box.x + 68, box.centery), anchor="midleft")
            if tag:
                draw.text(surface, tag, theme.font("bold", 12), theme.FAINT if done else theme.CYAN,
                          (box.right - 12, box.centery), spacing=1, anchor="midright")
            row_y = row_y + 40

    def panel_rows(self, solution_moves):
        """Rows for the moves panel: (move number, move, tag, is it the next solver move?).

        Before the solver is revealed: your last 5 moves.
        After: your last 2 moves, then what the solver plans to do next.
        """
        rows = []
        keep = 2 if self.revealed else 5
        start = max(0, len(self.history) - keep)
        for i in range(start, len(self.history)):
            rows.append((i + 1, self.history[i][0], "DONE" if self.revealed else "", False))
        if self.revealed and solution_moves and not self.won:
            for k, move in enumerate(solution_moves[:5 - len(rows)]):
                rows.append((len(self.history) + k + 1, move, "NEXT" if k == 0 else "", k == 0))
        return rows

    def is_exit_move(self, move, number):
        """Is this the move that drives X out?"""
        if move.car_name != TARGET:
            return False
        if number <= len(self.history):
            return self.won and number == len(self.history)
        moves = self.solution()[0]
        return moves is not None and number == len(self.history) + len(moves)

    def draw_win(self, surface):
        shade = pygame.Surface((theme.WIDTH, theme.HEIGHT), pygame.SRCALPHA)
        shade.fill((*theme.ASPHALT, 230))
        surface.blit(shade, (0, 0))

        top = 182
        draw.text(surface, f"LEVEL {self.index + 1:02} COMPLETE", theme.font("bold", 14), theme.CYAN,
                  (80, top), spacing=4)
        draw.text(surface, "LANE CLEAR", theme.font("display", 78), theme.TEXT, (80, top + 18),
                  shadow=theme.HOT_PINK, shadow_offset=5)

        box_y = top + 124
        stats = [
            ("MOVES", f"{len(self.history):02}", theme.TEXT),
            ("BEST", f"{self.best:02}", theme.HOT_PINK),
            ("TIME", format_time(self.elapsed), theme.CYAN),
        ]
        for i, (label, value, color) in enumerate(stats):
            x = 80 + i * 182
            pygame.draw.rect(surface, theme.PANEL, (x, box_y, 170, 76))
            pygame.draw.rect(surface, color if i else theme.TEXT, (x, box_y, 170, 2))
            draw.text(surface, label, theme.font("semibold", 12), theme.MUTED, (x + 16, box_y + 12), spacing=2)
            draw.text(surface, value, theme.font("bold", 32), color, (x + 16, box_y + 28))

        words, gems = self.result
        gem_x = 80 + 3 * 182 + 24
        for gem in range(gems):
            draw.diamond(surface, theme.HOT_PINK, (gem_x + 13 + gem * 34, box_y + 24), 26)
        draw.text(surface, words, theme.font("bold", 14), theme.HOT_PINK,
                  (gem_x, box_y + (58 if gems else 38)), spacing=3, anchor="midleft")

        for button in self.win_buttons():
            button.draw(surface)
