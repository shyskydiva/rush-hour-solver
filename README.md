# Rush Hour Solver

A command-line program that solves [Rush Hour](https://en.wikipedia.org/wiki/Rush_Hour_(puzzle)) sliding-car puzzles using **breadth-first search (BFS)**. Pick a level, and it finds the fewest moves needed to get the target car out, then shows the board after every move.

## How it works

The board is a 6×6 grid. Each car can only slide forward or backward along the direction it faces. The goal is to slide the target car `X` to the exit on the right edge of its row.

The solver uses breadth-first search:

1. Start with the puzzle's board.
2. Find every legal move from that board and make a new board for each one.
3. Check all boards 1 move away, then all boards 2 moves away, and so on.
4. Skip any board that's already been seen.
5. Stop at the first board where `X` reaches the exit.

Because BFS checks boards in order of how many moves they take, the first solution it finds is always the shortest one.

## Getting started

You need Python 3.

```bash
git clone https://github.com/shyskydiva/rush-hour-solver.git
cd rush-hour-solver
python -m venv .venv
```

Activate the virtual environment:

- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

Install the requirements:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Then pick a level:

```
RUSH HOUR SOLVER
  1. Easy
  2. Medium
  3. Hard
Pick a level (1-3): 1

Easy level:
......
......
XX.A..
...A..
......
......

Move 1: A ↑ 2
...A..
...A..
XX....
......
......
......

Move 2: X → 4
...A..
...A..
....XX
......
......
......

Solved in 2 moves! Checked 19 boards.
```

## Levels

| Level  | File                 | Fewest moves |
|--------|----------------------|--------------|
| Easy   | `puzzles/easy.txt`   | 2            |
| Medium | `puzzles/medium.txt` | 4            |
| Hard   | `puzzles/hard.txt`   | 8            |

## Puzzle file format

Each puzzle is a text file with 6 lines of 6 characters:

- `.` is an empty square
- `X` is the target car (it must be horizontal)
- Any other letter is a car. A car's letters sit next to each other in one row or one column, and it's 2 or 3 squares long.

Example (`puzzles/medium.txt`):

```
..A...
..A.BB
XXA..C
.....C
DD...C
....FF
```

## Running the tests

From the project's root folder:

```bash
python -m pytest
```

The tests cover cars, loading boards, finding legal moves, and the solver itself, including a puzzle with no solution.

## Project structure

```
rush-hour-solver/
├── main.py          # level menu and output
├── puzzles/         # easy, medium, and hard puzzle files
├── solver/
│   ├── car.py       # Car class: position, length, direction
│   ├── board.py     # Board class and puzzle file loading
│   ├── moves.py     # finding and applying legal moves
│   └── bfs.py       # breadth-first search solver
└── tests/           # pytest tests for each module
```

## What's next

- A Pygame version with a visual board and a "Watch it solve" mode