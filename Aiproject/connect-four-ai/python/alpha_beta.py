"""
Alpha-Beta Pruning algorithm implementation for Connect Four.
Applies branch-and-bound pruning to eliminate provably suboptimal subtrees.
Tracks visited and pruned nodes with detailed step traces for AI Lab explorer.
"""

from board import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    is_valid_move, get_valid_moves, get_bottom_empty_row,
    drop_piece, undo_piece, check_win, is_board_full
)
from evaluation import score_position


def _clean_bound(val):
    """Ensure finite JSON-compliant representation of search bounds."""
    if val == -float("inf"):
        return -999999
    elif val == float("inf"):
        return 999999
    elif isinstance(val, (int, float)) and abs(val) > 1e8:
        return 1000000 if val > 0 else -1000000
    return val


def alpha_beta_search(board, depth, alpha, beta, is_maximizing, player, stats, trace_parent=None, max_trace_depth=2):
    """
    Alpha-Beta Pruning recursive search.

    Args:
        board: 6x7 grid
        depth: remaining search depth (0 = cutoff)
        alpha: best score achievable by maximizer so far
        beta: best score achievable by minimizer so far
        is_maximizing: True if evaluating current player, False if evaluating opponent
        player: Root player making the move (AI or HUMAN)
        stats: dict tracking {'nodes_visited': int, 'pruned_nodes': int}
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
        return None, 1000000 + depth

    win_opp, _ = check_win(board, opp_player)
    if win_opp:
        return None, -1000000 - depth

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
        for i, col in enumerate(valid_moves):
            row = get_bottom_empty_row(board, col)
            drop_piece(board, row, col, player)

            node_trace = None
            if trace_parent is not None and depth >= max_trace_depth:
                node_trace = {
                    "col": col,
                    "depth": depth,
                    "player": player,
                    "type": "MAX",
                    "alpha_in": _clean_bound(alpha),
                    "beta_in": _clean_bound(beta),
                    "score": None,
                    "pruned": False,
                    "children": []
                }
                trace_parent.append(node_trace)

            _, current_score = alpha_beta_search(
                board, depth - 1, alpha, beta, False, player, stats,
                trace_parent=node_trace["children"] if node_trace else None,
                max_trace_depth=max_trace_depth
            )

            undo_piece(board, row, col)

            if node_trace:
                node_trace["score"] = _clean_bound(current_score)

            if current_score > max_eval:
                max_eval = current_score
                best_col = col

            alpha = max(alpha, current_score)
            if node_trace:
                node_trace["alpha_out"] = _clean_bound(alpha)
                node_trace["beta_out"] = _clean_bound(beta)

            # Pruning condition
            if beta <= alpha:
                # Count remaining moves that were pruned in this branch
                remaining = len(valid_moves) - (i + 1)
                stats["pruned_nodes"] += remaining

                if trace_parent is not None and depth >= max_trace_depth:
                    for skipped_col in valid_moves[i + 1:]:
                        trace_parent.append({
                            "col": skipped_col,
                            "depth": depth,
                            "player": player,
                            "type": "MAX",
                            "score": None,
                            "pruned": True,
                            "reason": f"β ({_clean_bound(beta)}) <= α ({_clean_bound(alpha)})",
                            "children": []
                        })
                break

        return best_col, max_eval

    else:
        min_eval = float("inf")
        for i, col in enumerate(valid_moves):
            row = get_bottom_empty_row(board, col)
            drop_piece(board, row, col, opp_player)

            node_trace = None
            if trace_parent is not None and depth >= max_trace_depth:
                node_trace = {
                    "col": col,
                    "depth": depth,
                    "player": opp_player,
                    "type": "MIN",
                    "alpha_in": _clean_bound(alpha),
                    "beta_in": _clean_bound(beta),
                    "score": None,
                    "pruned": False,
                    "children": []
                }
                trace_parent.append(node_trace)

            _, current_score = alpha_beta_search(
                board, depth - 1, alpha, beta, True, player, stats,
                trace_parent=node_trace["children"] if node_trace else None,
                max_trace_depth=max_trace_depth
            )

            undo_piece(board, row, col)

            if node_trace:
                node_trace["score"] = _clean_bound(current_score)

            if current_score < min_eval:
                min_eval = current_score
                best_col = col

            beta = min(beta, current_score)
            if node_trace:
                node_trace["alpha_out"] = _clean_bound(alpha)
                node_trace["beta_out"] = _clean_bound(beta)

            # Pruning condition
            if beta <= alpha:
                remaining = len(valid_moves) - (i + 1)
                stats["pruned_nodes"] += remaining

                if trace_parent is not None and depth >= max_trace_depth:
                    for skipped_col in valid_moves[i + 1:]:
                        trace_parent.append({
                            "col": skipped_col,
                            "depth": depth,
                            "player": opp_player,
                            "type": "MIN",
                            "score": None,
                            "pruned": True,
                            "reason": f"β ({_clean_bound(beta)}) <= α ({_clean_bound(alpha)})",
                            "children": []
                        })
                break

        return best_col, min_eval
