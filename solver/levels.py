"""The game's levels, shared by the text version and Pink Lane."""
from pathlib import Path

# The puzzles folder sits at the top of the project. Building the path from this
# file's location means it works no matter which folder you run the program from.
PUZZLES = Path(__file__).parent.parent / "puzzles"

# Each level is (name, puzzle file), easiest first.
LEVELS = [
    ("Easy", PUZZLES / "easy.txt"),
    ("Medium", PUZZLES / "medium.txt"),
    ("Hard", PUZZLES / "hard.txt"),
]
