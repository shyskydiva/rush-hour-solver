"""The game window: runs the main loop and switches between screens."""
import asyncio

import pygame

from solver.bfs import solve
from solver.board import load_board
from solver.levels import LEVELS
from visual import theme
from visual.game import GameScreen
from visual.levels import LevelsScreen
from visual.title import TitleScreen


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((theme.WIDTH, theme.HEIGHT))
        pygame.display.set_caption("Pink Lane")
        self.clock = pygame.time.Clock()
        self.running = True

        self.levels = LEVELS                  # [(name, puzzle file), ...]
        self.cleared = {}                     # level index -> {"moves": ..., "gems": ...}
        self.best = {}                        # level index -> fewest moves possible
        self.scene = TitleScreen(self)

    # --- Progress ---

    def best_moves(self, index):
        """The fewest moves that solve a level (solved once, then remembered)."""
        if index not in self.best:
            moves, _ = solve(load_board(self.levels[index][1]))
            self.best[index] = len(moves)
        return self.best[index]

    def is_unlocked(self, index):
        """Level 1 is always open. Each other level opens when the one before is cleared."""
        return index == 0 or (index - 1) in self.cleared

    def record_clear(self, index, moves, gems):
        """Remember a cleared level, keeping your best result."""
        old = self.cleared.get(index)
        if old is None or gems > old["gems"] or (gems == old["gems"] and moves < old["moves"]):
            self.cleared[index] = {"moves": moves, "gems": gems}

    # --- Switching screens ---

    def show_title(self):
        self.scene = TitleScreen(self)

    def show_levels(self):
        self.scene = LevelsScreen(self)

    def play(self, index):
        self.scene = GameScreen(self, index)

    def play_next(self):
        """Jump into the first level you haven't cleared yet."""
        for index in range(len(self.levels)):
            if index not in self.cleared and self.is_unlocked(index):
                self.play(index)
                return
        self.play(0)

    # --- Main loop ---

    async def run(self):
        """Run the game until the window closes.

        It's async so it also works in a web browser (through pygbag): after each
        frame, `await asyncio.sleep(0)` hands control back to the browser so it
        can draw the frame and handle input. On your computer it makes no difference.
        """
        while self.running:
            dt = self.clock.tick(60) / 1000  # seconds since the last frame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle(event)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)
        theme.forget_fonts()
        pygame.quit()
