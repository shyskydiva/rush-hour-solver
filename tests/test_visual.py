import asyncio
import os

import pytest

pygame = pytest.importorskip("pygame")  # skip these tests if Pygame isn't installed
os.environ["SDL_VIDEODRIVER"] = "dummy"  # run without opening a real window

from solver.board import board_from_lines  # noqa: E402
from visual import theme  # noqa: E402
from visual.app import App  # noqa: E402
from visual.game import car_colors, car_rect, format_time, rating  # noqa: E402

EASY = ["......", "......", "XX.A..", "...A..", "......", "......"]


@pytest.fixture
def app():
    return App()


def press(screen, key):
    screen.handle(pygame.event.Event(pygame.KEYDOWN, key=key))


def click(screen, pos):
    screen.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))


# --- Small helpers ---

def test_only_x_is_pink():
    colors = car_colors(board_from_lines(["..A...", "..A.BB", "XXA..C", ".....C", "DD...C", "....FF"]))
    assert colors["X"] == theme.HOT_PINK
    for name in "ABCDF":
        assert colors[name] != theme.HOT_PINK


def test_rating():
    assert rating(4, 4, assisted=False) == ("PERFECT RUN", 3)
    assert rating(7, 4, assisted=False) == ("CLEAN RUN", 2)
    assert rating(20, 4, assisted=False) == ("YOU MADE IT", 1)
    assert rating(4, 4, assisted=True) == ("SOLVER ASSIST", 0)


def test_format_time():
    assert format_time(42.7) == "0:42"
    assert format_time(65) == "1:05"


def test_car_rect_matches_the_style_guide():
    # Style guide: x = 14 + col * 70, cars are 64px wide.
    board = board_from_lines(EASY)
    rect = car_rect(board.cars["A"])
    assert rect.width == 64
    assert rect.height == 2 * 70 - 6


# --- Progress and unlocking ---

def test_only_the_first_level_starts_unlocked(app):
    assert app.is_unlocked(0)
    assert not app.is_unlocked(1)


def test_clearing_a_level_unlocks_the_next(app):
    app.record_clear(0, moves=2, gems=3)
    assert app.is_unlocked(1)


def test_record_clear_keeps_the_best_result(app):
    app.record_clear(0, moves=5, gems=2)
    app.record_clear(0, moves=9, gems=1)  # worse, so it's ignored
    assert app.cleared[0] == {"moves": 5, "gems": 2}


# --- Playing a level ---

def test_clicking_a_car_selects_it(app):
    app.play(0)
    game = app.scene
    click(game, car_rect(game.board.cars["A"]).center)
    assert game.selected == "A"
    assert len(game.targets()) > 0


def test_arrow_keys_slide_the_selected_car(app):
    app.play(0)
    game = app.scene
    game.selected = "A"
    press(game, pygame.K_UP)
    assert game.board.cars["A"].row == 1
    assert len(game.history) == 1


def test_blocked_move_nudges_instead_of_moving(app):
    app.play(0)
    game = app.scene
    game.selected = "X"
    press(game, pygame.K_RIGHT)  # X can slide 1 square, to the left of A
    press(game, pygame.K_RIGHT)  # now A is in the way
    assert game.board.cars["X"].col == 1
    assert game.nudge is not None


def test_undo_puts_the_car_back(app):
    app.play(0)
    game = app.scene
    game.selected = "A"
    press(game, pygame.K_UP)
    game.undo()
    assert game.board.cars["A"].row == 2
    assert game.history == []


def test_auto_solve_finishes_the_level(app):
    app.play(0)
    game = app.scene
    game.toggle_auto_solve()
    for _ in range(300):  # 5 seconds of frames at 60 fps
        game.update(1 / 60)
    assert game.won
    assert game.result == ("SOLVER ASSIST", 0)
    assert 0 in app.cleared


def test_solving_it_yourself_in_the_fewest_moves_is_perfect(app):
    app.play(0)
    game = app.scene
    for move in game.solution()[0]:
        game.make_move(move)
    assert game.won
    assert game.result == ("PERFECT RUN", 3)


def labels(game):
    return [button.label for button in game.buttons()]


def test_next_step_only_shows_while_auto_solve_is_paused(app):
    app.play(1)
    game = app.scene
    assert "AUTO-SOLVE" in labels(game)
    game.toggle_auto_solve()  # solver driving
    assert "PAUSE SOLVER" in labels(game)
    assert "NEXT STEP" not in labels(game)
    game.toggle_auto_solve()  # solver paused
    assert "RESUME" in labels(game)
    assert "NEXT STEP" in labels(game)


def test_pause_button_opens_the_pause_menu(app):
    app.play(0)
    game = app.scene
    click(game, (theme.WIDTH - 40 - 22, 48))  # the pause button in the top right
    assert game.paused
    assert app.scene is game  # still on the same level, not the main menu


def test_pausing_freezes_the_timer_and_auto_solve(app):
    app.play(0)
    game = app.scene
    game.toggle_auto_solve()
    press(game, pygame.K_ESCAPE)
    for _ in range(300):
        game.update(1 / 60)
    assert game.elapsed == 0
    assert game.history == []
    press(game, pygame.K_ESCAPE)  # resume
    assert not game.paused


def test_plain_moves_never_wait_on_the_solver(app):
    # Until you use Auto-solve, the solver shouldn't run at all (it made every move stutter).
    app.play(2)
    game = app.scene
    game.selected = "A"
    press(game, pygame.K_RIGHT)
    game.update(1 / 60)
    game.draw(app.screen)
    assert len(game.history) == 1
    assert game.solution_cache is None


def test_main_loop_runs_until_the_window_closes(app):
    pygame.event.post(pygame.event.Event(pygame.QUIT))  # pretend the player closed the window
    asyncio.run(app.run())
    assert not app.running


def test_every_screen_draws_without_errors(app):
    for show in (app.show_title, app.show_levels, lambda: app.play(2)):
        show()
        app.scene.update(1 / 60)
        app.scene.draw(app.screen)
