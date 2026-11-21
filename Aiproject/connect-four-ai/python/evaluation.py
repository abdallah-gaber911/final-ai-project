"""
Heuristic evaluation functions for Connect Four.
Shared identically by Minimax and Alpha-Beta Pruning.
"""

from board import ROWS, COLS, EMPTY, HUMAN, AI, check_win


def evaluate_window(window, piece):
    """
    Score a 4-cell window from the perspective of 'piece'.
    Opponent threats are penalized heavily to ensure defensive blocking.
    """
    score = 0
    opp_piece = HUMAN if piece == AI else AI

    count_piece = window.count(piece)
    count_empty = window.count(EMPTY)
    count_opp = window.count(opp_piece)

    if count_piece == 4:
        score += 100000
    elif count_piece == 3 and count_empty == 1:
        score += 100
    elif count_piece == 2 and count_empty == 2:
        score += 10

    # Defensive penalties (blocking opponent threats)
    if count_opp == 4:
        score -= 100000
    elif count_opp == 3 and count_empty == 1:
        score -= 120
    elif count_opp == 2 and count_empty == 2:
        score -= 10

    return score


def score_position(board, piece):
    """
    Evaluate entire board state from the perspective of 'piece'.
    Combines:
    1. Center column control bonus
    2. Horizontal window evaluations
    3. Vertical window evaluations
    4. Positive diagonal window evaluations
    5. Negative diagonal window evaluations
    """
    score = 0

    # 1. Center column dominance bonus
    center_col = [board[r][COLS // 2] for r in range(ROWS)]
    center_count = center_col.count(piece)
    opp_piece = HUMAN if piece == AI else AI
    opp_center_count = center_col.count(opp_piece)
    score += (center_count * 6) - (opp_center_count * 6)

    # Flanking center columns (cols 2 and 4)
    for c in (2, 4):
        col_cells = [board[r][c] for r in range(ROWS)]
        score += (col_cells.count(piece) * 2) - (col_cells.count(opp_piece) * 2)

    # 2. Horizontal windows
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # 3. Vertical windows
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # 4. Positive diagonals (bottom-left to top-right /)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # 5. Negative diagonals (top-left to bottom-right \)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score
