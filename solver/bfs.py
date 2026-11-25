from collections import deque

from solver.moves import apply_move, legal_moves


def solve(start_board):
    """Find the fewest moves to free the target car, using breadth-first search.

    BFS looks at every board 1 move away, then every board 2 moves away, and so
    on. Because it goes in that order, the first solution it finds is the shortest.

    Returns (list of moves, number of boards checked).
    The list is None if the puzzle can't be solved.
    """
    # Each item in the queue is a board plus the moves it took to get there.
    queue = deque()
    queue.append((start_board, []))

    # Remember boards we've already seen so we don't check them twice.
    seen = set()
    seen.add(start_board.key())

    while len(queue) > 0:
        board, path = queue.popleft()  # take the oldest board first

        if board.is_solved():
            return path, len(seen)

        for move in legal_moves(board):
            next_board = apply_move(board, move)
            if next_board.key() not in seen:
                seen.add(next_board.key())
                queue.append((next_board, path + [move]))

    # We ran out of boards to check, so there's no solution.
    return None, len(seen)