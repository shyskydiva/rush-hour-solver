# Rush Hour Solver

A game for [Rush Hour](https://en.wikipedia.org/wiki/Rush_Hour_(puzzle)) sliding-car puzzles, with a solver that uses **breadth-first search (BFS)**. Pick a level and solve it yourself. If you get stuck, ask the solver for help. When you win, it tells you the fewest moves possible.

**▶ [Play Pink Lane in your browser](https://shyskydiva.github.io/rush-hour-solver/)**, no install needed. It takes a few seconds to load the first time.

It comes in two versions that share the same solver:

- **Pink Lane** (`main.py`): a Pygame game where you click cars to slide them. It runs on your computer or in a web browser.
- **Text version** (`text_game.py`): play in the terminal by typing moves.

## How it works

The board is a 6×6 grid. Each car can only slide forward or backward along the direction it faces. The goal is to slide the target car `X` to the exit on the right edge of its row.

The solver uses breadth-first search:

1. Start with the puzzle's board.
2. Find every legal move from that board and make a new board for each one.
3. Check all boards 1 move away, then all boards 2 moves away, and so on.
4. Skip any board that's already been seen. For each new board, remember which board it came from and the move that got there.
5. Stop at the first board where `X` reaches the exit, then follow those notes back to the start to get the list of moves.

Because BFS checks boards in order of how many moves they take, the first solution it finds is always the shortest one.

A few details keep it fast:

- **Small board keys.** To check whether a board has been seen, the solver compares a short list of car positions, not a drawing of the whole grid.
- **One square per step.** When a car slides, only the square just past its front (or back) end can block it, so that's the only square checked.
- **Shared cars.** A new board only replaces the car that moved. All the other cars are shared with the board it came from, so making a new board is cheap.

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

## Playing Pink Lane (Pygame)

```bash
python main.py
```

Press **PLAY** (or Enter) to start the first level you haven't cleared, or pick one from **LEVELS**. Each level unlocks when you clear the one before it.

- **Move a car:** click it, then click one of the highlighted squares. You can also use the arrow keys to slide the selected car one square at a time.
- **Auto-solve:** the solver drives the cars for you. Press **Pause solver** to stop it, then **Resume** to let it keep driving or **Next step** to go one move at a time. The solver's planned moves appear in the side panel, and a dashed outline shows where its next move goes.
- **Undo / Reset:** take back your last move, or start the level over.
- **Pause:** the pause button in the top right (or `Esc`) freezes the timer and opens a menu to resume, restart, pick another level, or go back to the main menu.
- **Keyboard shortcuts:** `Z` undo, `R` reset, `Space` Auto-solve, `Esc` or `P` pause.

When you clear a level, you get up to 3 gems: 3 for the fewest moves possible, 2 for within 3 moves of it, and 1 otherwise. Using Auto-solve still clears the level, but earns no gems.

## The web version

The [browser version](https://shyskydiva.github.io/rush-hour-solver/) is built with [pygbag](https://pypi.org/project/pygbag/), which runs Python and Pygame in the browser using WebAssembly. Every push to `main` rebuilds and publishes it to GitHub Pages automatically (see `.github/workflows/pages.yml`).

To build and test it on your own computer:

```bash
pip install pygbag==0.9.3
pygbag --template web/pink-lane.tmpl --icon web/favicon.png --width 960 --height 640 .
```

Then open http://localhost:8000. Add `--build` to only build the files (into `build/web/`) without starting the test server.

A few things the web version depends on:

- `main.py` must import `pygame` itself. pygbag only reads that file to decide which libraries to load.
- The main loop in `visual/app.py` is `async` and calls `await asyncio.sleep(0)` every frame, so the browser gets a turn to draw.
- `pygbag.ini` keeps `.venv/`, `tests/`, and `web/` out of the game package.
- `web/pink-lane.tmpl` is the loading page (based on pygbag's default template), and `web/favicon.png` is the tab icon.

## Playing the text version

```bash
python text_game.py
```

Pick a level, then type moves until car `X` reaches the right edge. A move is the car's letter, a direction, and how many squares to slide it, like `A down 2`. Capital letters don't matter.

| Command | What it does |
|---------|--------------|
| `A down 2` | Slide car A down 2 squares (directions: `left`, `right`, `up`, `down`) |
| `hint` | Show the best next move from the current board |
| `solve` | Show the rest of the solution, one board per move, and end the game |
| `help` | Show the instructions again |
| `quit` | Exit the game |

If a move isn't allowed (the car is blocked, the car doesn't move in that direction, or there's no car with that letter), the game explains why and lets you try again.

Example game:

```
RUSH HOUR
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

How to play: get car X to the right edge of the board.
  Type a move like:  A down 2   (car, direction, squares)
  Directions: left, right, up, down
  Other commands: hint, solve, help, quit

Your move: hint
Hint: A up 2
Your move: A up 2

...A..
...A..
XX....
......
......
......

Your move: X right 4

...A..
...A..
....XX
......
......
......

You solved it in 2 moves!
The fewest moves possible is 2.
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

If a puzzle file breaks one of these rules, loading it stops with an error that says what's wrong, like `Car A's squares must touch, in one straight line`.

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

```bash
pytest
```

The tests cover cars, loading boards, finding legal moves, the solver (including a puzzle with no solution), the text game (reading typed moves, rejecting illegal ones, and the `hint`, `solve`, and `quit` commands), and Pink Lane (selecting and sliding cars, blocked moves, undo, Auto-solve, ratings, and unlocking levels).

The Pink Lane tests need Pygame, so run them with the virtual environment active. Without Pygame they're skipped.

## Project structure

```
rush-hour-solver/
├── main.py          # starts Pink Lane (also the web version's starting point)
├── text_game.py     # the text version: typed moves, hints, solving
├── pytest.ini       # lets pytest find the project's code
├── pygbag.ini       # folders to leave out of the web version
├── .github/workflows/pages.yml  # builds and publishes the web version
├── web/             # web version's loading page and tab icon
├── puzzles/         # easy, medium, and hard puzzle files
├── solver/
│   ├── car.py       # Car class: position, length, direction
│   ├── board.py     # Board class and puzzle file loading
│   ├── moves.py     # finding and applying legal moves
│   ├── bfs.py       # breadth-first search solver
│   └── levels.py    # the list of levels, shared by both versions
├── visual/          # Pink Lane
│   ├── app.py       # game window, screen switching, level progress
│   ├── theme.py     # colors, sizes, and fonts from the style guide
│   ├── draw.py      # drawing helpers: cars, buttons, cut-corner shapes, text
│   ├── title.py     # title screen
│   ├── levels.py    # level select screen
│   ├── game.py      # the board, moves panel, solver controls, and win screen
│   └── fonts/       # Bungee and Chakra Petch (SIL Open Font License)
└── tests/           # pytest tests for each module
```

## What's next

- Sound effects (the style guide suggests a short low sound on a blocked move)
- Save level progress between games
- More levels