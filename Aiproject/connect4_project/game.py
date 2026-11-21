"""
Connect 4 game logic.
Provides board operations, move execution, win checking, and terminal state evaluation.
Does not import tkinter so all logic remains fully testable.
"""

ROWS = 6
COLS = 7

EMPTY = 0
HUMAN = 1
AI = 2

PLAYER_NAMES = {
    HUMAN: "Human",
    AI: "Computer"
}


def create_board():
    """Create a new empty 6x7 Connect 4 board."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def copy_board(board):
    """Return a deep copy of the board."""
    return [row[:] for row in board]


def is_valid_move(board, col):
    """Check if a column is inside the board and has at least one empty cell."""
    if not (0 <= col < COLS):
        return False
    return board[0][col] == EMPTY


def get_valid_moves(board):
    """Return a list of column indices that are not yet full."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def get_bottom_empty_row(board, col):
    """
    Find the lowest empty row in the given column.
    Row 0 is the top of the board, row 5 is the bottom.
    Returns row index (0 to 5) or -1 if the column is full.
    """
    if not (0 <= col < COLS):
        return -1
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def drop_piece(board, col, player):
    """
    Drop a player's piece into the specified column.
    Modifies the board in place and returns the row index where the piece landed.
    Returns -1 if the move is invalid or the column is full.
    """
    row = get_bottom_empty_row(board, col)
    if row == -1:
        return -1
    board[row][col] = player
    return row


def undo_piece(board, col):
    """
    Remove the topmost piece from the specified column.
    Modifies the board in place and returns the row index of the removed piece.
    Returns -1 if the column was already empty.
    """
    if not (0 <= col < COLS):
        return -1
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return r
    return -1


def check_win(board, player):
    """
    Check if the given player has won by connecting 4 pieces in a row.
    Checks horizontal, vertical, and both diagonal directions.
    Returns a list of the 4 winning coordinates [(r, c), ...] if found, else None.
    """
    # Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == player and
                board[r][c + 1] == player and
                board[r][c + 2] == player and
                board[r][c + 3] == player):
                return [(r, c), (r, c + 1), (r, c + 2), (r, c + 3)]

    # Vertical check
    for r in range(ROWS - 3):
        for c in range(COLS):
            if (board[r][c] == player and
                board[r + 1][c] == player and
                board[r + 2][c] == player and
                board[r + 3][c] == player):
                return [(r, c), (r + 1, c), (r + 2, c), (r + 3, c)]

    # Positive diagonal check (going down and right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if (board[r][c] == player and
                board[r + 1][c + 1] == player and
                board[r + 2][c + 2] == player and
                board[r + 3][c + 3] == player):
                return [(r, c), (r + 1, c + 1), (r + 2, c + 2), (r + 3, c + 3)]

    # Negative diagonal check (going down and left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if (board[r][c] == player and
                board[r + 1][c - 1] == player and
                board[r + 2][c - 2] == player and
                board[r + 3][c - 3] == player):
                return [(r, c), (r + 1, c - 1), (r + 2, c - 2), (r + 3, c - 3)]

    return None


def check_draw(board):
    """
    Check if the board is full with no winner.
    Returns True if all cells are filled and neither player has 4 in a row.
    """
    if len(get_valid_moves(board)) > 0:
        return False
    return check_win(board, HUMAN) is None and check_win(board, AI) is None


def is_terminal(board):
    """
    Check if the game has ended.
    Returns a tuple (is_over, winner, winning_cells):
      - winner is HUMAN, AI, or None (in case of draw or ongoing)
      - winning_cells is the list of coordinates of the 4 winning pieces, or None
    """
    human_win = check_win(board, HUMAN)
    if human_win:
        return True, HUMAN, human_win

    ai_win = check_win(board, AI)
    if ai_win:
        return True, AI, ai_win

    if len(get_valid_moves(board)) == 0:
        return True, None, None

    return False, None, None


def board_to_string(board):
    """Return a plain text representation of the board for logging or debugging."""
    symbols = {EMPTY: ".", HUMAN: "R", AI: "Y"}
    lines = []
    for row in board:
        lines.append(" ".join(symbols[cell] for cell in row))
    lines.append("-" * (COLS * 2 - 1))
    lines.append(" ".join(str(c) for c in range(COLS)))
    return "\n".join(lines)
