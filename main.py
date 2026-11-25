from pathlib import Path

from solver.bfs import solve
from solver.board import load_board
from solver.moves import apply_move, legal_moves

# The puzzles folder sits next to this file, so this works no matter
# which folder you run the program from.
PUZZLES = Path(__file__).parent / "puzzles"

# The three levels: menu number -> (name, puzzle file)
LEVELS = {
    "1": ("Easy", PUZZLES / "easy.txt"),
    "2": ("Medium", PUZZLES / "medium.txt"),
    "3": ("Hard", PUZZLES / "hard.txt"),
}

HELP = """How to play: get car X to the right edge of the board.
  Type a move like:  A down 2   (car, direction, squares)
  Directions: left, right, up, down
  Other commands: hint, solve, help, quit"""


def pick_level():
    """Ask for a level until the player types a valid number."""
    print("RUSH HOUR")
    for number, (name, _) in LEVELS.items():
        print(f"  {number}. {name}")

    while True:
        choice = input("Pick a level (1-3): ").strip()
        if choice in LEVELS:
            return LEVELS[choice]
        print("Please type 1, 2, or 3.")


def find_move(board, text):
    """Turn typed text like "a down 2" into a legal Move.

    Returns (move, None) if the move is allowed, or (None, reason) if not.
    """
    parts = text.split()
    if len(parts) != 3:
        return None, "Type a move like: A down 2"

    car_name = parts[0].upper()
    if car_name not in board.cars:
        return None, f"There's no car {car_name} on the board."

    typed = f"{car_name} {parts[1].lower()} {parts[2]}"

    # Every legal move prints like "A down 2", so compare the text.
    for move in legal_moves(board):
        if str(move) == typed:
            return move, None

    return None, f"Car {car_name} can't do that. It's blocked, or that's the wrong direction."


def show_solution(board):
    """Print every move from the current board to the end."""
    moves, _ = solve(board)
    if moves is None:
        print("This board can't be solved from here.")
        return

    for number, move in enumerate(moves, start=1):
        board = apply_move(board, move)
        print(f"Move {number}: {move}\n{board}\n")
    print(f"Solved in {len(moves)} more moves.")


def play(board):
    """Let the player make moves until the puzzle is solved or they quit."""
    moves_made = 0
    best, _ = solve(board)  # the shortest solution, to compare at the end

    while not board.is_solved():
        text = input("Your move: ").strip().lower()

        if text == "quit":
            print("Bye!")
            return
        elif text == "help":
            print(HELP)
        elif text == "hint":
            moves, _ = solve(board)
            if moves is None:
                print("No solution from here.")
            else:
                print(f"Hint: {moves[0]}")
        elif text == "solve":
            show_solution(board)
            return
        else:
            move, reason = find_move(board, text)
            if move is None:
                print(reason)
            else:
                board = apply_move(board, move)
                moves_made = moves_made + 1
                print(f"\n{board}\n")

    print(f"You solved it in {moves_made} moves!")
    if best is not None:
        print(f"The fewest moves possible is {len(best)}.")


def main():
    name, path = pick_level()
    board = load_board(path)
    print(f"\n{name} level:\n{board}\n")
    print(HELP + "\n")
    play(board)


if __name__ == "__main__":
    main()
