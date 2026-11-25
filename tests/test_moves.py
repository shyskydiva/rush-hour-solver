from solver.board import board_from_lines
from solver.moves import apply_move, legal_moves

PUZZLE = ["..A...", "..A.BB", "XXA..C", ".....C", "DD...C", "....FF"]


def moves_for(board, letter):
    """Helper: only the moves for one car."""
    result = []
    for move in legal_moves(board):
        if move.car_name == letter:
            result.append(move.steps)
    return sorted(result)


def test_blocked_car_has_no_moves():
    board = board_from_lines(PUZZLE)
    assert moves_for(board, "X") == []


def test_car_can_slide_more_than_one_square():
    board = board_from_lines(PUZZLE)
    assert moves_for(board, "A") == [1, 2, 3]


def test_car_stops_at_the_board_edge():
    board = board_from_lines(PUZZLE)
    assert moves_for(board, "D") == [1, 2, 3]  # D is at the left edge, so it can't go left


def test_car_can_slide_both_ways():
    board = board_from_lines(PUZZLE)
    assert moves_for(board, "F") == [-4, -3, -2, -1]


def test_every_move_has_a_readable_description():
    board = board_from_lines(PUZZLE)
    descriptions = [str(move) for move in legal_moves(board)]
    assert "A down 3" in descriptions
    assert "F left 4" in descriptions


def test_apply_move_only_moves_one_car():
    board = board_from_lines(PUZZLE)
    move = [m for m in legal_moves(board) if m.car_name == "F" and m.steps == -1][0]
    after = apply_move(board, move)
    assert after.cars["F"].col == 3
    assert board.cars["F"].col == 4  # the old board didn't change