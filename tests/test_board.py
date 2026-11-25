import pytest

from solver.board import board_from_lines

PUZZLE = ["..A...", "..A.BB", "XXA..C", ".....C", "DD...C", "....FF"]


def test_finds_every_car():
    board = board_from_lines(PUZZLE)
    assert sorted(board.cars) == ["A", "B", "C", "D", "F", "X"]


def test_reads_car_direction_and_length():
    board = board_from_lines(PUZZLE)
    assert board.cars["A"].horizontal is False
    assert board.cars["A"].length == 3
    assert board.cars["X"].horizontal is True


def test_draws_the_same_board_it_read():
    board = board_from_lines(PUZZLE)
    assert str(board) == "\n".join(PUZZLE)


def test_not_solved_at_start():
    assert board_from_lines(PUZZLE).is_solved() is False


def test_solved_when_target_reaches_edge():
    lines = ["......", "......", "....XX", "......", "......", "......"]
    assert board_from_lines(lines).is_solved() is True


def test_missing_target_car_is_an_error():
    with pytest.raises(ValueError):
        board_from_lines(["AA....", "......", "......", "......", "......", "......"])