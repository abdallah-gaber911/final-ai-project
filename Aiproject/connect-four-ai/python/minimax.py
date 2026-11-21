"""
Minimax algorithm implementation for Connect Four.
Pure recursive exhaustive search with heuristic depth-cutoff.
Generates full execution telemetry and optional search traces for AI Lab visualization.
"""

from board import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    is_valid_move, get_valid_moves, get_bottom_empty_row,
    drop_piece, undo_piece, check_win, is_board_full
)
from evaluation import score_position


def minimax_search(board, depth, is_maximizing, player, stats, trace_parent=None, max_trace_depth=2):
    """
    Minimax recursive search.

    Args:
        board: 6x7 grid
        depth: remaining search depth (0 = cutoff)
        is_maximizing: True if evaluating current player, False if evaluating opponent
        player: Root player making the move (AI or HUMAN)
        stats: dict tracking {'nodes_visited': int}
        trace_parent: optional list to record trace node hierarchy for AI Lab
        max_trace_depth: max tree depth to include in detailed visualization trace

    Returns:
        (best_col, best_score)
    """
    stats["nodes_visited"] += 1
    opp_player = HUMAN if player == AI else AI

    # Terminal checks
    win_p, _ = check_win(board, player)
    if win_p:
        return None, 1000000 + depth  # Win sooner preferred

    win_opp, _ = check_win(board, opp_player)
    if win_opp:
        return None, -1000000 - depth  # Loss later preferred

    if is_board_full(board):
        return None, 0

    if depth == 0:
        return None, score_position(board, player)

    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return None, 0

    best_col = valid_moves[0]

    if is_maximizing:
        max_eval = -float("inf")
        for col in valid_moves:
            row = get_bottom_empty_row(board, col)
            drop_piece(board, row, col, player)

            node_trace = None
            if trace_parent is not None and depth >= max_trace_depth:
                node_trace = {
                    "col": col,
                    "depth": depth,
                    "player": player,
                    "type": "MAX",
                    "score": None,
                    "children": []
                }
                trace_parent.append(node_trace)

            _, current_score = minimax_search(
                board, depth - 1, False, player, stats,
                trace_parent=node_trace["children"] if node_trace else None,
                max_trace_depth=max_trace_depth
            )

            undo_piece(board, row, col)

            if node_trace:
                node_trace["score"] = current_score

            if current_score > max_eval:
                max_eval = current_score
                best_col = col

        return best_col, max_eval

    else:
        min_eval = float("inf")
        for col in valid_moves:
            row = get_bottom_empty_row(board, col)
            drop_piece(board, row, col, opp_player)

            node_trace = None
            if trace_parent is not None and depth >= max_trace_depth:
                node_trace = {
                    "col": col,
                    "depth": depth,
                    "player": opp_player,
                    "type": "MIN",
                    "score": None,
                    "children": []
                }
                trace_parent.append(node_trace)

            _, current_score = minimax_search(
                board, depth - 1, True, player, stats,
                trace_parent=node_trace["children"] if node_trace else None,
                max_trace_depth=max_trace_depth
            )

            undo_piece(board, row, col)

            if node_trace:
                node_trace["score"] = current_score

            if current_score < min_eval:
                min_eval = current_score
                best_col = col

        return best_col, min_eval
