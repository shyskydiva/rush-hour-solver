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


def test_wrong_board_size_is_an_error():
    with pytest.raises(ValueError, match="6 rows of 6"):
        board_from_lines(["XX....", "......"])


def test_one_square_car_is_an_error():
    with pytest.raises(ValueError, match="at least 2"):
        board_from_lines(["A.....", "......", "XX....", "......", "......", "......"])


def test_car_squares_must_be_in_a_straight_line():
    # A is L-shaped
    with pytest.raises(ValueError, match="straight line"):
        board_from_lines(["AA....", "A.....", "XX....", "......", "......", "......"])


def test_car_squares_must_touch():
    # The two B squares have a gap between them
    with pytest.raises(ValueError, match="straight line"):
        board_from_lines(["B.B...", "......", "XX....", "......", "......", "......"])


def test_target_car_must_be_horizontal():
    with pytest.raises(ValueError, match="horizontally"):
        board_from_lines(["X.....", "X.....", "......", "......", "......", "......"])


def test_same_layout_gives_the_same_key():
    assert board_from_lines(PUZZLE).key() == board_from_lines(PUZZLE).key()


def test_different_layout_gives_a_different_key():
    moved = ["..A...", "..A.BB", "XXA..C", ".....C", ".DD..C", "....FF"]  # D slid right
    assert board_from_lines(PUZZLE).key() != board_from_lines(moved).key()