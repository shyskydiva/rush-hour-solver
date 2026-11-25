from main import find_move, pick_level, play
from solver.board import board_from_lines

# The easy puzzle: X needs to get past A, which blocks its row.
EASY = ["......", "......", "XX.A..", "...A..", "......", "......"]


def type_these(monkeypatch, answers):
    """Helper: pretend the player types each answer in order."""
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


# --- find_move: turning typed text into a move ---

def test_find_move_accepts_a_legal_move():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "A up 2")
    assert str(move) == "A up 2"
    assert reason is None


def test_find_move_ignores_capitals():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "a UP 2")
    assert str(move) == "A up 2"


def test_find_move_needs_three_words():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "A up")
    assert move is None
    assert "like" in reason


def test_find_move_rejects_a_missing_car():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "Q up 1")
    assert move is None
    assert "no car Q" in reason


def test_find_move_rejects_a_blocked_move():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "X right 2")  # A is in the way
    assert move is None
    assert "can't" in reason


def test_find_move_rejects_the_wrong_direction():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "A left 1")  # A only moves up and down
    assert move is None


def test_find_move_rejects_a_word_instead_of_a_number():
    board = board_from_lines(EASY)
    move, reason = find_move(board, "A up two")
    assert move is None


# --- play: the game loop ---

def test_play_ends_when_the_puzzle_is_solved(monkeypatch, capsys):
    type_these(monkeypatch, ["A up 2", "X right 4"])
    play(board_from_lines(EASY))
    output = capsys.readouterr().out
    assert "You solved it in 2 moves!" in output
    assert "fewest moves possible is 2" in output


def test_play_keeps_going_after_a_bad_move(monkeypatch, capsys):
    type_these(monkeypatch, ["X right 2", "A up 2", "X right 4"])
    play(board_from_lines(EASY))
    output = capsys.readouterr().out
    assert "can't" in output
    assert "You solved it in 2 moves!" in output  # the bad move didn't count


def test_play_hint_gives_a_move(monkeypatch, capsys):
    type_these(monkeypatch, ["hint", "quit"])
    play(board_from_lines(EASY))
    output = capsys.readouterr().out
    assert "Hint: A" in output


def test_play_solve_shows_the_answer(monkeypatch, capsys):
    type_these(monkeypatch, ["solve"])
    play(board_from_lines(EASY))
    output = capsys.readouterr().out
    assert "Solved in 2 more moves." in output


def test_play_quit_stops_the_game(monkeypatch, capsys):
    type_these(monkeypatch, ["quit"])
    play(board_from_lines(EASY))
    output = capsys.readouterr().out
    assert "Bye!" in output
    assert "You solved it" not in output


# --- pick_level: the menu ---

def test_pick_level_asks_again_after_a_bad_choice(monkeypatch, capsys):
    type_these(monkeypatch, ["9", "", "2"])
    name, path = pick_level()
    assert name == "Medium"
    assert capsys.readouterr().out.count("Please type 1, 2, or 3.") == 2
