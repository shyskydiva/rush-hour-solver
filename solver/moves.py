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


def fits(new_car, old_car, taken):
    """Check that a moved car stays on the board and doesn't hit another car."""
    for row, col in new_car.cells():
        # Off the edge of the board?
        if row < 0 or row >= SIZE or col < 0 or col >= SIZE:
            return False
        # Taken by a different car? (Squares the car already covers are fine.)
        if (row, col) in taken and (row, col) not in old_car.cells():
            return False
    return True


def legal_moves(board):
    """Return every move any car can make right now."""
    moves = []
    taken = board.occupied()

    for car in board.cars.values():
        # Try both directions: -1 (left/up) and +1 (right/down).
        for direction in [-1, 1]:
            steps = direction
            # Keep sliding one more square until the car hits something.
            while fits(car.moved(steps), car, taken):
                moves.append(Move(car.name, steps, car.horizontal))
                steps = steps + direction

    return moves


def apply_move(board, move):
    """Return the new board after making a move."""
    car = board.cars[move.car_name]
    return board.copy_with(car.moved(move.steps))