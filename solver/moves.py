"""Finding the moves every car can make, and making them."""
from solver.board import SIZE

# Direction word for each (horizontal?, moving right/down?) combination.
DIRECTIONS = {
    (True, True): "right",
    (True, False): "left",
    (False, True): "down",
    (False, False): "up",
}


class Move:
    """Slide one car a number of squares."""

    def __init__(self, car_name, steps, horizontal):
        self.car_name = car_name
        self.steps = steps            # positive = right/down, negative = left/up
        self.horizontal = horizontal

    def __str__(self):
        """Describe the move, like "A down 3"."""
        direction = DIRECTIONS[(self.horizontal, self.steps > 0)]
        return f"{self.car_name} {direction} {abs(self.steps)}"


def legal_moves(board):
    """Return every move any car can make right now.

    A sliding car only ever enters one new square per step: the one just past
    its front (or back) end. So we only need to check that one square each time.
    """
    moves = []
    taken = board.occupied()

    for car in board.cars.values():
        cells = car.cells()
        # Try both directions: -1 (left/up) and +1 (right/down).
        for direction in [-1, 1]:
            # Start at the end of the car that faces this direction.
            row, col = cells[0] if direction < 0 else cells[-1]
            steps = 0
            # Keep sliding one more square until the car would leave the board or hit something.
            while True:
                if car.horizontal:
                    col = col + direction
                else:
                    row = row + direction
                off_board = row < 0 or row >= SIZE or col < 0 or col >= SIZE
                if off_board or (row, col) in taken:
                    break
                steps = steps + direction
                moves.append(Move(car.name, steps, car.horizontal))

    return moves


def apply_move(board, move):
    """Return the new board after making a move."""
    car = board.cars[move.car_name]
    return board.copy_with(car.moved(move.steps))