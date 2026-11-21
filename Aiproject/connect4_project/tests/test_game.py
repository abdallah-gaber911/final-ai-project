"""
Unit tests for Connect 4 game logic.
Tests board creation, gravity, column validation, wins in all 4 directions, draw state, and undo.
"""

import unittest
import os
import sys

# Ensure parent directory is in Python path for importing game module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    create_board, copy_board, is_valid_move, get_valid_moves,
    get_bottom_empty_row, drop_piece, undo_piece,
    check_win, check_draw, is_terminal
)


class TestGameLogic(unittest.TestCase):

    def setUp(self):
        self.board = create_board()

    def test_board_initialization(self):
        """New board must be 6x7 and completely empty."""
        self.assertEqual(len(self.board), ROWS)
        for row in self.board:
            self.assertEqual(len(row), COLS)
            for cell in row:
                self.assertEqual(cell, EMPTY)
        self.assertEqual(len(get_valid_moves(self.board)), 7)

    def test_piece_gravity(self):
        """Pieces must fall to the lowest empty row."""
        row1 = drop_piece(self.board, 3, HUMAN)
        self.assertEqual(row1, 5)  # bottom row is index 5
        self.assertEqual(self.board[5][3], HUMAN)

        row2 = drop_piece(self.board, 3, AI)
        self.assertEqual(row2, 4)  # next piece stacks above it
        self.assertEqual(self.board[4][3], AI)

    def test_full_column_rejection(self):
        """Cannot drop into a column that already has 6 pieces."""
        for i in range(ROWS):
            self.assertTrue(is_valid_move(self.board, 0))
            drop_piece(self.board, 0, HUMAN if i % 2 == 0 else AI)

        self.assertFalse(is_valid_move(self.board, 0))
        self.assertEqual(get_bottom_empty_row(self.board, 0), -1)
        self.assertEqual(drop_piece(self.board, 0, HUMAN), -1)
        self.assertNotIn(0, get_valid_moves(self.board))

    def test_horizontal_win(self):
        """Check 4 pieces connected horizontally on any row."""
        for c in range(1, 5):
            drop_piece(self.board, c, HUMAN)

        coords = check_win(self.board, HUMAN)
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 4)
        expected = {(5, 1), (5, 2), (5, 3), (5, 4)}
        self.assertEqual(set(coords), expected)
        self.assertIsNone(check_win(self.board, AI))

    def test_vertical_win(self):
        """Check 4 pieces connected vertically in a single column."""
        for _ in range(4):
            drop_piece(self.board, 2, AI)

        coords = check_win(self.board, AI)
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 4)
        expected = {(5, 2), (4, 2), (3, 2), (2, 2)}
        self.assertEqual(set(coords), expected)
        self.assertIsNone(check_win(self.board, HUMAN))

    def test_positive_diagonal_win(self):
        """Check diagonal win from top-left to bottom-right."""
        # Col 0: 3 AI pieces, then 1 HUMAN at row 2
        drop_piece(self.board, 0, AI)
        drop_piece(self.board, 0, AI)
        drop_piece(self.board, 0, AI)
        drop_piece(self.board, 0, HUMAN)  # row 2

        # Col 1: 2 AI pieces, then 1 HUMAN at row 3
        drop_piece(self.board, 1, AI)
        drop_piece(self.board, 1, AI)
        drop_piece(self.board, 1, HUMAN)  # row 3

        # Col 2: 1 AI piece, then 1 HUMAN at row 4
        drop_piece(self.board, 2, AI)
        drop_piece(self.board, 2, HUMAN)  # row 4

        # Col 3: 1 HUMAN at row 5
        drop_piece(self.board, 3, HUMAN)  # row 5

        coords = check_win(self.board, HUMAN)
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 4)
        expected = {(2, 0), (3, 1), (4, 2), (5, 3)}
        self.assertEqual(set(coords), expected)

    def test_negative_diagonal_win(self):
        """Check diagonal win from top-right to bottom-left."""
        # Col 3: 1 AI at row 5
        drop_piece(self.board, 3, AI)

        # Col 4: 1 HUMAN, then 1 AI at row 4
        drop_piece(self.board, 4, HUMAN)
        drop_piece(self.board, 4, AI)

        # Col 5: 2 HUMAN, then 1 AI at row 3
        drop_piece(self.board, 5, HUMAN)
        drop_piece(self.board, 5, HUMAN)
        drop_piece(self.board, 5, AI)

        # Col 6: 3 HUMAN, then 1 AI at row 2
        drop_piece(self.board, 6, HUMAN)
        drop_piece(self.board, 6, HUMAN)
        drop_piece(self.board, 6, HUMAN)
        drop_piece(self.board, 6, AI)

        coords = check_win(self.board, AI)
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 4)
        expected = {(2, 6), (3, 5), (4, 4), (5, 3)}
        self.assertEqual(set(coords), expected)

    def test_undo_restores_board(self):
        """Dropping a piece then undoing it must restore the board to identical state."""
        original_copy = copy_board(self.board)

        row = drop_piece(self.board, 4, HUMAN)
        self.assertNotEqual(self.board, original_copy)

        removed_row = undo_piece(self.board, 4)
        self.assertEqual(removed_row, row)
        self.assertEqual(self.board, original_copy)

    def test_draw_detection(self):
        """A full board with no 4-in-a-row must be recognized as a draw."""
        # Pattern that fills the board without 4 in a row:
        # Col 0: R, R, Y, Y, R, R
        # Col 1: Y, Y, R, R, Y, Y
        # Col 2: R, R, Y, Y, R, R
        # Col 3: Y, Y, R, R, Y, Y
        # Col 4: R, R, Y, Y, R, R
        # Col 5: Y, Y, R, R, Y, Y
        # Col 6: R, R, Y, Y, R, R
        pattern = [
            [HUMAN, AI, HUMAN, AI, HUMAN, AI, HUMAN],
            [HUMAN, AI, HUMAN, AI, HUMAN, AI, HUMAN],
            [AI, HUMAN, AI, HUMAN, AI, HUMAN, AI],
            [AI, HUMAN, AI, HUMAN, AI, HUMAN, AI],
            [HUMAN, AI, HUMAN, AI, HUMAN, AI, HUMAN],
            [HUMAN, AI, HUMAN, AI, HUMAN, AI, HUMAN]
        ]
        self.board = pattern
        self.assertIsNone(check_win(self.board, HUMAN))
        self.assertIsNone(check_win(self.board, AI))
        self.assertTrue(check_draw(self.board))

        is_over, winner, win_coords = is_terminal(self.board)
        self.assertTrue(is_over)
        self.assertIsNone(winner)
        self.assertIsNone(win_coords)


if __name__ == "__main__":
    unittest.main()
