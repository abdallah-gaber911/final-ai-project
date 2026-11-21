"""
Game state management and high-level interface logic for Connect Four.
"""

from board import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    create_board, copy_board, is_valid_move, get_valid_moves,
    get_bottom_empty_row, drop_piece, undo_piece, check_win, is_terminal, is_board_full
)


class GameState:
    """Manages full game state, moves, turn progression, and history."""

    def __init__(self, first_player=HUMAN):
        self.board = create_board()
        self.current_turn = first_player
        self.game_over = False
        self.winner = None
        self.winning_coords = None
        self.move_history = []  # List of dicts: {'player': int, 'col': int, 'row': int}

    def play_move(self, col):
        """
        Execute move for current player.
        Returns:
            dict with {
                'success': bool,
                'row': int,
                'col': int,
                'player': int,
                'game_over': bool,
                'winner': int or None,
                'winning_coords': list or None
            }
        """
        if self.game_over or not is_valid_move(self.board, col):
            return {"success": False, "reason": "Invalid move or game over"}

        row = get_bottom_empty_row(self.board, col)
        drop_piece(self.board, row, col, self.current_turn)
        self.move_history.append({"player": self.current_turn, "col": col, "row": row})

        # Check terminal
        is_term, winner, coords = is_terminal(self.board)
        if is_term:
            self.game_over = True
            self.winner = winner
            self.winning_coords = coords

        player_who_moved = self.current_turn
        # Switch turn if not over
        if not self.game_over:
            self.current_turn = HUMAN if self.current_turn == AI else AI

        return {
            "success": True,
            "row": row,
            "col": col,
            "player": player_who_moved,
            "next_turn": self.current_turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "winning_coords": self.winning_coords
        }

    def undo_move(self):
        """Undo last 2 plies (AI move and Human move) or 1 ply if needed."""
        if not self.move_history:
            return {"success": False, "reason": "No moves to undo"}

        undone = []
        # If AI just played, undo AI move and human move
        last_move = self.move_history.pop()
        undo_piece(self.board, last_move["row"], last_move["col"])
        undone.append(last_move)

        if self.move_history and last_move["player"] == AI:
            human_move = self.move_history.pop()
            undo_piece(self.board, human_move["row"], human_move["col"])
            undone.append(human_move)

        self.game_over = False
        self.winner = None
        self.winning_coords = None
        self.current_turn = HUMAN

        return {
            "success": True,
            "undone_moves": undone,
            "current_turn": self.current_turn,
            "board": self.board
        }

    def reset(self, first_player=HUMAN):
        """Reset game."""
        self.board = create_board()
        self.current_turn = first_player
        self.game_over = False
        self.winner = None
        self.winning_coords = None
        self.move_history.clear()
        return {"success": True, "current_turn": self.current_turn}
