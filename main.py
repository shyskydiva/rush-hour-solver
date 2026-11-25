from solver.bfs import solve
from solver.board import load_board
from solver.moves import apply_move

# The three levels: menu number -> (name, puzzle file)
LEVELS = {
    "1": ("Easy", "puzzles/easy.txt"),
    "2": ("Medium", "puzzles/medium.txt"),
    "3": ("Hard", "puzzles/hard.txt"),
}


def main():
    print("RUSH HOUR SOLVER")
    for number, (name, path) in LEVELS.items():
        print(f"  {number}. {name}")

    choice = input("Pick a level (1-3): ").strip()
    if choice not in LEVELS:
        print("Please type 1, 2, or 3.")
        return

    name, path = LEVELS[choice]
    board = load_board(path)
    print(f"\n{name} level:\n{board}\n")

    moves, checked = solve(board)

    if moves is None:
        print(f"No solution. Checked {checked} boards.")
        return

    # Show the board after each move so you can follow along.
    for number, move in enumerate(moves, start=1):
        board = apply_move(board, move)
        print(f"Move {number}: {move}\n{board}\n")

    print(f"Solved in {len(moves)} moves! Checked {checked} boards.")


if __name__ == "__main__":
    main()