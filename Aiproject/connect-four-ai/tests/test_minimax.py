"""
Unit tests for Minimax algorithm implementation.
Verifies immediate wins, defensive blocking, and search depth node scaling.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from board import create_board, get_bottom_empty_row, drop_piece, HUMAN, AI
from minimax import minimax_search


class TestMinimaxAlgorithm(unittest.TestCase):

    def setUp(self):
        self.board = create_board()

    def test_immediate_winning_move(self):
        """AI must take immediate horizontal 4-in-a-row winning move."""
        # Row 5, columns 0, 1, 2 have AI coins. Column 3 wins.
        for c in (0, 1, 2):
            r = get_bottom_empty_row(self.board, c)
            drop_piece(self.board, r, c, AI)

        stats = {"nodes_visited": 0}
        best_col, score = minimax_search(self.board, depth=2, is_maximizing=True, player=AI, stats=stats)
        self.assertEqual(best_col, 3)
        self.assertGreater(score, 100000)

    def test_block_opponent_winning_threat(self):
        """AI must block Human from completing 4-in-a-row on next turn."""
        # Human has 3 in a row horizontally at row 5 (cols 0, 1, 2).
        for c in (0, 1, 2):
            r = get_bottom_empty_row(self.board, c)
            drop_piece(self.board, r, c, HUMAN)

        stats = {"nodes_visited": 0}
        best_col, score = minimax_search(self.board, depth=2, is_maximizing=True, player=AI, stats=stats)
        self.assertEqual(best_col, 3)

    def test_node_count_scales_with_depth(self):
        """Depth 3 must visit strictly more nodes than Depth 1."""
        stats1 = {"nodes_visited": 0}
        minimax_search(self.board, depth=1, is_maximizing=True, player=AI, stats=stats1)

        stats3 = {"nodes_visited": 0}
        minimax_search(self.board, depth=3, is_maximizing=True, player=AI, stats=stats3)

        self.assertGreater(stats3["nodes_visited"], stats1["nodes_visited"])


if __name__ == "__main__":
    unittest.main()
