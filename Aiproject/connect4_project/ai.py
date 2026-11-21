"""
Connect 4 AI algorithms: Minimax and Alpha-Beta Pruning.
Implements board evaluation, search tree traversal, and optimal move selection.
Does not import tkinter so all logic remains fully testable.
"""

import time
try:
    from game import (
        ROWS, COLS, EMPTY, HUMAN, AI,
        is_valid_move, get_valid_moves, drop_piece, undo_piece, check_win
    )
except ImportError:
    from connect4.game import (
        ROWS, COLS, EMPTY, HUMAN, AI,
        is_valid_move, get_valid_moves, drop_piece, undo_piece, check_win
    )

# Search order: center column first, then alternating outwards.
# Center-first ordering gives better pruning because center columns control more lines.
COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]

# Evaluation weights with simple rationale
SCORE_WIN = 100000    # Decisive terminal win score
SCORE_THREE = 100     # 3 player pieces with 1 empty space: strong offensive threat
SCORE_TWO = 10        # 2 player pieces with 2 empty spaces: building alignment
PENALTY_THREE = 140   # 3 opponent pieces with 1 empty space: defensive block is prioritized
PENALTY_TWO = 10      # 2 opponent pieces with 2 empty spaces: counter opponent development
CENTER_BONUS = 4      # Bonus per piece in center column (col 3) for board control


def _generate_all_windows():
    """Pre-generate all 69 possible 4-cell windows on a 6x7 board."""
    windows = []
    # 24 horizontal windows
    for r in range(ROWS):
        for c in range(COLS - 3):
            windows.append(((r, c), (r, c + 1), (r, c + 2), (r, c + 3)))
    # 21 vertical windows
    for r in range(ROWS - 3):
        for c in range(COLS):
            windows.append(((r, c), (r + 1, c), (r + 2, c), (r + 3, c)))
    # 12 diagonal down-right windows
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            windows.append(((r, c), (r + 1, c + 1), (r + 2, c + 2), (r + 3, c + 3)))
    # 12 diagonal down-left windows
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            windows.append(((r, c), (r + 1, c - 1), (r + 2, c - 2), (r + 3, c - 3)))
    return windows


ALL_WINDOWS = _generate_all_windows()


def evaluate_window(window, player, opponent):
    """
    Score a single 4-cell window for the player against the opponent.
    Returns an integer score based on pattern matching.
    """
    score = 0
    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(EMPTY)

    if player_count == 4:
        score += SCORE_WIN
    elif player_count == 3 and empty_count == 1:
        score += SCORE_THREE
    elif player_count == 2 and empty_count == 2:
        score += SCORE_TWO

    if opponent_count == 3 and empty_count == 1:
        score -= PENALTY_THREE
    elif opponent_count == 2 and empty_count == 2:
        score -= PENALTY_TWO

    return score


def evaluate_board(board, player):
    """
    Heuristic evaluation function.
    Scores the entire board from the perspective of player.
    Positive values favor player; negative values favor opponent.
    """
    opponent = HUMAN if player == AI else AI
    total_score = 0

    # Center column control bonus
    center_col = COLS // 2
    for r in range(ROWS):
        if board[r][center_col] == player:
            total_score += CENTER_BONUS
        elif board[r][center_col] == opponent:
            total_score -= CENTER_BONUS

    # Evaluate all 4-cell windows
    for coords in ALL_WINDOWS:
        window = [board[r][c] for r, c in coords]
        total_score += evaluate_window(window, player, opponent)

    return total_score


def minimax(board, depth, is_maximizing, root_player, counter):
    """
    Standard Minimax algorithm without pruning.
    Searches all game tree paths down to depth limit.
    Returns (best_score, best_column).
    """
    counter["nodes"] += 1
    opponent = HUMAN if root_player == AI else AI

    # Terminal checks before depth limit
    if check_win(board, root_player):
        return SCORE_WIN + depth, None
    if check_win(board, opponent):
        return -SCORE_WIN - depth, None
    if len(get_valid_moves(board)) == 0:
        return 0, None
    if depth == 0:
        return evaluate_board(board, root_player), None

    ordered_moves = [c for c in COLUMN_ORDER if is_valid_move(board, c)]
    best_col = ordered_moves[0]

    if is_maximizing:
        best_score = float("-inf")
        for col in ordered_moves:
            drop_piece(board, col, root_player)
            score, _ = minimax(board, depth - 1, False, root_player, counter)
            undo_piece(board, col)
            if score > best_score:
                best_score = score
                best_col = col
        return best_score, best_col
    else:
        best_score = float("inf")
        for col in ordered_moves:
            drop_piece(board, col, opponent)
            score, _ = minimax(board, depth - 1, True, root_player, counter)
            undo_piece(board, col)
            if score < best_score:
                best_score = score
                best_col = col
        return best_score, best_col


def alphabeta(board, depth, alpha, beta, is_maximizing, root_player, counter):
    """
    Minimax with Alpha-Beta Pruning.
    Prunes branches that cannot influence the final decision.
    Guaranteed to return the same move as Minimax.
    Returns (best_score, best_column).
    """
    counter["nodes"] += 1
    opponent = HUMAN if root_player == AI else AI

    # Terminal checks before depth limit
    if check_win(board, root_player):
        return SCORE_WIN + depth, None
    if check_win(board, opponent):
        return -SCORE_WIN - depth, None
    if len(get_valid_moves(board)) == 0:
        return 0, None
    if depth == 0:
        return evaluate_board(board, root_player), None

    ordered_moves = [c for c in COLUMN_ORDER if is_valid_move(board, c)]
    best_col = ordered_moves[0]

    if is_maximizing:
        best_score = float("-inf")
        for col in ordered_moves:
            drop_piece(board, col, root_player)
            score, _ = alphabeta(board, depth - 1, alpha, beta, False, root_player, counter)
            undo_piece(board, col)
            if score > best_score:
                best_score = score
                best_col = col
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Beta cut-off: minimizing ancestor already has a better/equal option
        return best_score, best_col
    else:
        best_score = float("inf")
        for col in ordered_moves:
            drop_piece(board, col, opponent)
            score, _ = alphabeta(board, depth - 1, alpha, beta, True, root_player, counter)
            undo_piece(board, col)
            if score < best_score:
                best_score = score
                best_col = col
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha cut-off: maximizing ancestor already has a better/equal option
        return best_score, best_col


def best_move(board, depth, use_alphabeta, player):
    """
    Determine the optimal column move for player using Minimax or Alpha-Beta.
    Parameters:
      board: 2D list representing the current board state
      depth: search depth limit (1 = Easy, 3 = Medium, 5 = Hard)
      use_alphabeta: True to use Alpha-Beta pruning, False for standard Minimax
      player: HUMAN or AI (allows same function to calculate moves for AI or hint for human)
    Returns:
      (chosen_column, nodes_visited, elapsed_seconds)
    """
    start_time = time.perf_counter()
    counter = {"nodes": 0}

    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return None, 0, 0.0

    if use_alphabeta:
        score, col = alphabeta(board, depth, float("-inf"), float("inf"), True, player, counter)
    else:
        score, col = minimax(board, depth, True, player, counter)

    elapsed_seconds = time.perf_counter() - start_time
    return col, counter["nodes"], elapsed_seconds
