from solver.car import Car

SIZE = 6      # the board is 6 x 6 squares
TARGET = "X"  # the car we need to get out
EMPTY = "."   # an empty square in a puzzle file


class Board:
    """All the cars on the board at one moment."""

    def __init__(self, cars):
        self.cars = cars  # a dictionary: car letter -> Car

    def occupied(self):
        """Return a set of every square that has a car on it."""
        taken = set()
        for car in self.cars.values():
            for square in car.cells():
                taken.add(square)
        return taken

    def copy_with(self, new_car):
        """Return a NEW board where one car has been swapped for its moved version."""
        new_cars = dict(self.cars)    # copy the dictionary
        new_cars[new_car.name] = new_car
        return Board(new_cars)

    def is_solved(self):
        """The puzzle is solved when the target car touches the right edge."""
        target = self.cars[TARGET]
        last_col = target.col + target.length - 1
        return last_col == SIZE - 1

    def key(self):
        """
        Two boards with the same layout get the same key, so the solver can
        tell when it has already seen a board.
        """
        return str(self)

    def __str__(self):
        """Draw the board as 6 lines of text, the same way puzzle files look."""
        grid = []
        for row in range(SIZE):
            grid.append([EMPTY] * SIZE)

        for car in self.cars.values():
            for row, col in car.cells():
                grid[row][col] = car.name

        lines = []
        for row in grid:
            lines.append("".join(row))
        return "\n".join(lines)


def board_from_lines(lines):
    """Build a Board from 6 strings like "..A...".

    Each letter is a car. A car's letters all sit in one row (horizontal)
    or one column (vertical).
    """
    # Step 1: collect the squares for each letter.
    squares_by_letter = {}
    for row in range(len(lines)):
        for col in range(len(lines[row])):
            letter = lines[row][col]
            if letter != EMPTY:
                if letter not in squares_by_letter:
                    squares_by_letter[letter] = []
                squares_by_letter[letter].append((row, col))

    if TARGET not in squares_by_letter:
        raise ValueError("The puzzle needs a target car marked X")

    # Step 2: turn each group of squares into a Car.
    cars = {}
    for letter, squares in squares_by_letter.items():
        first_row, first_col = squares[0]  # we read top-to-bottom, left-to-right, so this is the top-left
        second_row, second_col = squares[1]
        horizontal = first_row == second_row  # same row means it lies sideways
        cars[letter] = Car(letter, first_row, first_col, len(squares), horizontal)

    return Board(cars)


def load_board(path):
    """Read a puzzle file and return a Board."""
    lines = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line != "":  # skip blank lines
                lines.append(line)
    return board_from_lines(lines)