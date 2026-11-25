from main import PUZZLES
from solver.bfs import solve
from solver.board import board_from_lines, load_board
from solver.moves import apply_move


def test_already_solved_needs_no_moves():
    board = board_from_lines(["......", "......", "....XX", "......", "......", "......"])
    moves, checked = solve(board)
    assert moves == []


def test_easy_takes_2_moves():
    moves, checked = solve(load_board(PUZZLES / "easy.txt"))
    assert len(moves) == 2


def test_medium_takes_4_moves():
    moves, checked = solve(load_board(PUZZLES / "medium.txt"))
    assert len(moves) == 4


def test_hard_solution_really_works():
    board = load_board(PUZZLES / "hard.txt")
    moves, checked = solve(board)
    for move in moves:
        board = apply_move(board, move)
    assert board.is_solved()


def test_impossible_puzzle_returns_none():
    # B sits in X's own row, so X can never get out
    board = board_from_lines(["......", "......", "XXBBB.", "......", "......", "......"])
    moves, checked = solve(board)
    assert moves is None