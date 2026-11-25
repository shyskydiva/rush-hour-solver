"""One car on the board: where it is, how long it is, and which way it slides."""


class Car:
    """One car on the board."""

    def __init__(self, name, row, col, length, horizontal):
        self.name = name              # the letter shown on the board, like "A"
        self.row = row                # row of the car's top-left square
        self.col = col                # column of the car's top-left square
        self.length = length          # how many squares long (2 or 3)
        self.horizontal = horizontal  # True = moves left/right, False = moves up/down

    def cells(self):
        """Return a list of every (row, col) square this car covers."""
        squares = []
        for i in range(self.length):
            if self.horizontal:
                squares.append((self.row, self.col + i))
            else:
                squares.append((self.row + i, self.col))
        return squares

    def moved(self, steps):
        """Return a NEW car slid by `steps` squares.

        Positive steps move right (or down). Negative steps move left (or up).
        We make a new car instead of changing this one, so old boards stay the same.
        """
        if self.horizontal:
            return Car(self.name, self.row, self.col + steps, self.length, self.horizontal)
        else:
            return Car(self.name, self.row + steps, self.col, self.length, self.horizontal)