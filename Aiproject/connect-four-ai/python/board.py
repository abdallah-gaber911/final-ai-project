"""
Board representation and core rules for Connect Four.
Pure Python, standard library only, headless and deterministic.
"""

ROWS = 6
COLS = 7

EMPTY = 0
HUMAN = 1
AI = 2

PLAYER_NAMES = {
    EMPTY: "Empty",
    HUMAN: "Human",
    AI: "AI"
}


def create_board():
    """Create a new 6x7 empty grid."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def copy_board(board):
    """Create an independent copy of the board."""
    return [row[:] for row in board]


def is_valid_move(board, col):
    """Check if a piece can be placed into the specified column."""
    if col is None or not (0 <= col < COLS):
        return False
    return board[0][col] == EMPTY


def get_valid_moves(board):
    """
    Get all playable columns, prioritizing center columns for optimal search ordering:
    Column order: [3, 2, 4, 1, 5, 0, 6]
    """
    column_order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in column_order if is_valid_move(board, c)]


def get_bottom_empty_row(board, col):
    """Return the lowest unoccupied row index in the column, or None if full."""
    if not (0 <= col < COLS):
        return None
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None


def drop_piece(board, row, col, piece):
    """Place a piece into a specific row and column."""
    board[row][col] = piece


def undo_piece(board, row, col):
    """Remove a piece from a specific row and column."""
    board[row][col] = EMPTY


def check_win(board, piece):
    """
    Check if the specified player has achieved 4-in-a-row.
    Returns:
        (is_win: bool, winning_coords: list of (r, c) tuples or None)
    """
    # 1. Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True, [(r, c + i) for i in range(4)]

    # 2. Vertical check
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True, [(r + i, c) for i in range(4)]

    # 3. Positive diagonal check (bottom-left to top-right /)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True, [(r - i, c + i) for i in range(4)]

    # 4. Negative diagonal check (top-left to bottom-right \)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True, [(r + i, c + i) for i in range(4)]

    return False, None


def is_board_full(board):
    """Check if all top slots are occupied."""
    return all(board[0][c] != EMPTY for c in range(COLS))


def is_terminal(board):
    """
    Check if the board is in a terminal state (win or draw).
    Returns:
        (is_terminal: bool, winner: int or None, winning_coords: list or None)
    """
    win_ai, coords_ai = check_win(board, AI)
    if win_ai:
        return True, AI, coords_ai

    win_human, coords_human = check_win(board, HUMAN)
    if win_human:
        return True, HUMAN, coords_human

    if is_board_full(board):
        return True, None, None

    return False, None, None
