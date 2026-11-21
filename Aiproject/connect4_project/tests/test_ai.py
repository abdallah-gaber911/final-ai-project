"""
Unit tests for Connect 4 AI algorithms.
Validates:
1. Minimax and Alpha-Beta pick identical columns across 30+ distinct positions.
2. Alpha-Beta visits fewer or equal nodes than Minimax in every position.
3. Alpha-Beta visits significantly fewer nodes at depth 5.
4. AI takes immediate wins when available.
5. AI blocks immediate human threats at depth 3 and above.
6. Hint mode works correctly for the human player.
"""

import unittest
import os
import sys

# Ensure parent directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    create_board, drop_piece, copy_board
)
from ai import best_move, evaluate_board


def generate_test_positions():
    """
    Generate 32 distinct, realistic board positions from various move sequences.
    Returns a list of board states.
    """
    positions = []

    # Sequence lists of column moves (alternating HUMAN, AI)
    move_sequences = [
        # Empty board
        [],
        # Single moves
        [3],
        [2],
        [4],
        # 2 moves
        [3, 3],
        [3, 2],
        [2, 4],
        [1, 5],
        # 3 moves
        [3, 2, 3],
        [3, 3, 2],
        [2, 3, 4],
        [0, 6, 3],
        # 4 moves
        [3, 3, 2, 4],
        [3, 2, 3, 2],
        [1, 2, 3, 4],
        [2, 3, 3, 2],
        # 5 moves
        [3, 2, 4, 1, 3],
        [3, 3, 2, 2, 4],
        [0, 1, 2, 3, 4],
        [3, 2, 1, 4, 5],
        # 6 moves
        [3, 3, 2, 2, 4, 4],
        [3, 2, 3, 2, 4, 1],
        [1, 2, 1, 2, 3, 4],
        [2, 3, 4, 3, 2, 4],
        # 7 moves
        [3, 2, 4, 1, 5, 0, 6],
        [3, 3, 3, 2, 2, 4, 4],
        [2, 2, 3, 3, 4, 4, 1],
        # 8 moves
        [3, 3, 2, 2, 4, 4, 1, 5],
        [1, 2, 3, 4, 1, 2, 3, 4],
        [3, 2, 4, 3, 2, 4, 1, 5],
        # 9 moves
        [3, 3, 3, 2, 2, 2, 4, 4, 1],
        [2, 3, 2, 3, 4, 5, 4, 5, 3]
    ]

    for seq in move_sequences:
        b = create_board()
        player = HUMAN
        for col in seq:
            drop_piece(b, col, player)
            player = AI if player == HUMAN else HUMAN
        positions.append(b)

    return positions


class TestAIAlgorithms(unittest.TestCase):

    def test_minimax_and_alphabeta_equality_and_nodes(self):
        """
        Verify that on at least 30 different positions at depth 1 and 3,
        Minimax and Alpha-Beta return the exact same column, and
        Alpha-Beta visits <= Minimax nodes in every case.
        """
        positions = generate_test_positions()
        self.assertGreaterEqual(len(positions), 30)

        for depth in [1, 3]:
            for idx, board in enumerate(positions):
                col_mm, nodes_mm, _ = best_move(board, depth, use_alphabeta=False, player=AI)
                col_ab, nodes_ab, _ = best_move(board, depth, use_alphabeta=True, player=AI)

                self.assertEqual(
                    col_mm, col_ab,
                    f"Mismatch at depth {depth}, position {idx}: Minimax picked {col_mm}, Alpha-Beta picked {col_ab}"
                )
                self.assertLessEqual(
                    nodes_ab, nodes_mm,
                    f"Alpha-Beta visited more nodes at depth {depth}, position {idx}: AB={nodes_ab}, MM={nodes_mm}"
                )

    def test_alphabeta_at_depth_4_equality(self):
        """Check equality at depth 4 on 5 representative positions."""
        positions = generate_test_positions()[:5]
        for idx, board in enumerate(positions):
            col_mm, nodes_mm, _ = best_move(board, 4, use_alphabeta=False, player=AI)
            col_ab, nodes_ab, _ = best_move(board, 4, use_alphabeta=True, player=AI)

            self.assertEqual(col_mm, col_ab)
            self.assertLessEqual(nodes_ab, nodes_mm)

    def test_alphabeta_efficiency_at_depth_5(self):
        """At depth 5, Alpha-Beta must visit substantially fewer nodes than Minimax."""
        board = create_board()
        # Drop a couple pieces to create a non-trivial position
        drop_piece(board, 3, HUMAN)
        drop_piece(board, 3, AI)

        col_mm, nodes_mm, time_mm = best_move(board, 5, use_alphabeta=False, player=AI)
        col_ab, nodes_ab, time_ab = best_move(board, 5, use_alphabeta=True, player=AI)

        self.assertEqual(col_mm, col_ab)
        # Pruning should cut down nodes visited by at least 60%
        reduction_pct = ((nodes_mm - nodes_ab) / nodes_mm) * 100
        self.assertGreater(
            reduction_pct, 60.0,
            f"Expected >60% node reduction at depth 5, got {reduction_pct:.1f}% (MM={nodes_mm}, AB={nodes_ab})"
        )

    def test_ai_takes_immediate_horizontal_win(self):
        """AI must take an immediate winning move horizontally."""
        board = create_board()
        # AI has pieces at (5, 1), (5, 2), (5, 3). Column 4 wins.
        drop_piece(board, 1, AI)
        drop_piece(board, 2, AI)
        drop_piece(board, 3, AI)

        col, _, _ = best_move(board, depth=3, use_alphabeta=True, player=AI)
        # 0 or 4 could win; 4 or 0 are valid winning moves
        self.assertIn(col, [0, 4])

    def test_ai_takes_immediate_vertical_win(self):
        """AI must take an immediate winning move vertically."""
        board = create_board()
        # Col 2 has 3 AI pieces stacked
        drop_piece(board, 2, AI)
        drop_piece(board, 2, AI)
        drop_piece(board, 2, AI)

        col, _, _ = best_move(board, depth=3, use_alphabeta=True, player=AI)
        self.assertEqual(col, 2)

    def test_ai_blocks_immediate_horizontal_loss(self):
        """AI must block human's 3-in-a-row when AI has no immediate win."""
        # Case 1: Human has pieces at 0, 1, 2 bounded by the wall at -1. Only column 3 wins.
        board1 = create_board()
        drop_piece(board1, 0, HUMAN)
        drop_piece(board1, 1, HUMAN)
        drop_piece(board1, 2, HUMAN)
        col1, _, _ = best_move(board1, depth=3, use_alphabeta=True, player=AI)
        self.assertEqual(col1, 3, f"AI failed to block horizontal win at col 3, chose {col1}")

        # Case 2: Human has pieces at 1, 2, 3 but col 0 is already blocked by AI. Only col 4 wins.
        board2 = create_board()
        drop_piece(board2, 0, AI)
        drop_piece(board2, 1, HUMAN)
        drop_piece(board2, 2, HUMAN)
        drop_piece(board2, 3, HUMAN)
        col2, _, _ = best_move(board2, depth=3, use_alphabeta=True, player=AI)
        self.assertEqual(col2, 4, f"AI failed to block horizontal win at col 4, chose {col2}")

        # Case 3: Inside threat at col 2 with human pieces at 0, 1, 3
        board3 = create_board()
        drop_piece(board3, 0, HUMAN)
        drop_piece(board3, 1, HUMAN)
        drop_piece(board3, 3, HUMAN)
        col3, _, _ = best_move(board3, depth=3, use_alphabeta=True, player=AI)
        self.assertEqual(col3, 2, f"AI failed to block inside threat at col 2, chose {col3}")

    def test_ai_blocks_immediate_vertical_loss(self):
        """AI must block human's vertical 3-in-a-row."""
        board = create_board()
        # Human stacked 3 pieces in column 4
        drop_piece(board, 4, HUMAN)
        drop_piece(board, 4, HUMAN)
        drop_piece(board, 4, HUMAN)

        col, _, _ = best_move(board, depth=3, use_alphabeta=True, player=AI)
        self.assertEqual(col, 4, f"AI failed to block vertical win, chose {col}")

    def test_hint_functionality_for_human(self):
        """Hint must suggest a winning move for the human player."""
        board = create_board()
        # Human has 3 pieces in column 3
        drop_piece(board, 3, HUMAN)
        drop_piece(board, 3, HUMAN)
        drop_piece(board, 3, HUMAN)

        col, _, _ = best_move(board, depth=3, use_alphabeta=True, player=HUMAN)
        self.assertEqual(col, 3, f"Hint did not suggest winning move for Human: {col}")


if __name__ == "__main__":
    unittest.main()
