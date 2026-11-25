"""The breadth-first search solver."""
from collections import deque

from solver.moves import apply_move, legal_moves


def solve(start_board):
    """Find the fewest moves to free the target car, using breadth-first search.

    BFS looks at every board 1 move away, then every board 2 moves away, and so
    on. Because it goes in that order, the first solution it finds is the shortest.

    Returns (list of moves, number of boards checked).
    The list is None if the puzzle can't be solved.
    """
    queue = deque([start_board])

    # For every board we've seen: the board it came from and the move that got
    # there. This doubles as the "already seen" check, and it lets us rebuild the
    # winning path at the end instead of copying a path for every board.
    came_from = {start_board.key(): None}

    while len(queue) > 0:
        board = queue.popleft()  # take the oldest board first

        if board.is_solved():
            return path_to(board, came_from), len(came_from)

        for move in legal_moves(board):
            next_board = apply_move(board, move)
            key = next_board.key()
            if key not in came_from:
                came_from[key] = (board, move)
                queue.append(next_board)

    # We ran out of boards to check, so there's no solution.
    return None, len(came_from)


def path_to(board, came_from):
    """Walk back from a board to the start, collecting the moves in order."""
    moves = []
    step = came_from[board.key()]
    while step is not None:
        board, move = step
        moves.append(move)
        step = came_from[board.key()]
    moves.reverse()
    return moves
