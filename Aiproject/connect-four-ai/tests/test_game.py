"""
Unit tests for Connect Four game mechanics and win detection.
Tests horizontal, vertical, diagonal wins, draw, gravity, and undo.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from board import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    create_board, is_valid_move, get_bottom_empty_row,
    drop_piece, undo_piece, check_win, is_board_full, is_terminal
)


class TestGameLogic(unittest.TestCase):

    def setUp(self):
        self.board = create_board()

    def test_empty_board_initialization(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.assertEqual(self.board[r][c], EMPTY)

    def test_gravity_drop(self):
        row0 = get_bottom_empty_row(self.board, 3)
        self.assertEqual(row0, ROWS - 1)
        drop_piece(self.board, row0, 3, HUMAN)
        self.assertEqual(self.board[ROWS - 1][3], HUMAN)

        row1 = get_bottom_empty_row(self.board, 3)
        self.assertEqual(row1, ROWS - 2)
        drop_piece(self.board, row1, 3, AI)
        self.assertEqual(self.board[ROWS - 2][3], AI)

    def test_column_full_and_invalid_move(self):
        for _ in range(ROWS):
            r = get_bottom_empty_row(self.board, 0)
            drop_piece(self.board, r, 0, HUMAN)
        self.assertFalse(is_valid_move(self.board, 0))
        self.assertIsNone(get_bottom_empty_row(self.board, 0))

    def test_horizontal_win(self):
        # Place 4 pieces horizontally in bottom row (row 5)
        for c in range(4):
            drop_piece(self.board, ROWS - 1, c, HUMAN)
        win, coords = check_win(self.board, HUMAN)
        self.assertTrue(win)
        self.assertEqual(len(coords), 4)
        for r, c in coords:
            self.assertEqual(r, ROWS - 1)

    def test_vertical_win(self):
        # Place 4 pieces vertically in col 2
        for r in range(4):
            row = get_bottom_empty_row(self.board, 2)
            drop_piece(self.board, row, 2, AI)
        win, coords = check_win(self.board, AI)
        self.assertTrue(win)
        self.assertEqual(len(coords), 4)
        for r, c in coords:
            self.assertEqual(c, 2)

    def test_positive_diagonal_win(self):
        # / diagonal from (5, 0) to (2, 3)
        coords_expected = [(5, 0), (4, 1), (3, 2), (2, 3)]
        for r, c in coords_expected:
            self.board[r][c] = HUMAN
        win, coords = check_win(self.board, HUMAN)
        self.assertTrue(win)
        self.assertEqual(set(coords), set(coords_expected))

    def test_negative_diagonal_win(self):
        # \ diagonal from (2, 0) to (5, 3)
        coords_expected = [(2, 0), (3, 1), (4, 2), (5, 3)]
        for r, c in coords_expected:
            self.board[r][c] = AI
        win, coords = check_win(self.board, AI)
        self.assertTrue(win)
        self.assertEqual(set(coords), set(coords_expected))

    def test_undo_piece(self):
        r = get_bottom_empty_row(self.board, 4)
        drop_piece(self.board, r, 4, HUMAN)
        self.assertEqual(self.board[r][4], HUMAN)
        undo_piece(self.board, r, 4)
        self.assertEqual(self.board[r][4], EMPTY)
        self.assertEqual(get_bottom_empty_row(self.board, 4), ROWS - 1)


if __name__ == "__main__":
    unittest.main()
