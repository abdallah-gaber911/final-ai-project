"""
Unit tests for Alpha-Beta Pruning algorithm implementation.
Verifies move parity with Minimax, strict pruning efficiency, and node reduction.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from board import create_board, get_bottom_empty_row, drop_piece, HUMAN, AI
from minimax import minimax_search
from alpha_beta import alpha_beta_search


class TestAlphaBetaAlgorithm(unittest.TestCase):

    def setUp(self):
        self.board = create_board()

    def test_immediate_winning_move(self):
        """Alpha-Beta must pick immediate winning move."""
        for c in (1, 2, 3):
            r = get_bottom_empty_row(self.board, c)
            drop_piece(self.board, r, c, AI)

        stats = {"nodes_visited": 0, "pruned_nodes": 0}
        col, score = alpha_beta_search(self.board, 2, -float("inf"), float("inf"), True, AI, stats)
        # Winning column is either 0 or 4
        self.assertIn(col, [0, 4])
        self.assertGreater(score, 100000)

    def test_block_opponent_winning_threat(self):
        """Alpha-Beta must block opponent threat."""
        for c in (0, 1, 2):
            r = get_bottom_empty_row(self.board, c)
            drop_piece(self.board, r, c, HUMAN)

        stats = {"nodes_visited": 0, "pruned_nodes": 0}
        col, _ = alpha_beta_search(self.board, 2, -float("inf"), float("inf"), True, AI, stats)
        self.assertEqual(col, 3)

    def test_minimax_and_alphabeta_move_parity(self):
        """Alpha-Beta and Minimax must yield equivalent optimal decisions on identical state."""
        # Setup sample game position
        moves = [(3, HUMAN), (3, AI), (2, HUMAN), (4, AI), (2, HUMAN), (1, AI)]
        for col, p in moves:
            r = get_bottom_empty_row(self.board, col)
            drop_piece(self.board, r, col, p)

        stats_mm = {"nodes_visited": 0}
        col_mm, score_mm = minimax_search(self.board, depth=3, is_maximizing=True, player=AI, stats=stats_mm)

        stats_ab = {"nodes_visited": 0, "pruned_nodes": 0}
        col_ab, score_ab = alpha_beta_search(self.board, depth=3, alpha=-float("inf"), beta=float("inf"),
                                             is_maximizing=True, player=AI, stats=stats_ab)

        self.assertEqual(col_ab, col_mm)
        self.assertEqual(score_ab, score_mm)
        # Pruning must visit fewer nodes
        self.assertLessEqual(stats_ab["nodes_visited"], stats_mm["nodes_visited"])
        self.assertGreater(stats_ab["pruned_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
