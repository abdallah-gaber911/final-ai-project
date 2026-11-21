"""
Top-level AI Engine bridge for Pyodide WebAssembly execution.
Exposes JSON-friendly entry points for frontend calls.
Collects real execution time, visited nodes, pruned nodes, and search traces.
"""

import json
import time
from board import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    create_board, copy_board, is_valid_move, get_valid_moves,
    get_bottom_empty_row, drop_piece, undo_piece, check_win, is_terminal
)
from evaluation import score_position
from minimax import minimax_search
from alpha_beta import alpha_beta_search


def _clean_for_json(data):
    """Recursively ensure no raw Infinity, -Infinity, or NaN tokens exist for RFC 8259 JSON compliance."""
    if isinstance(data, dict):
        return {k: _clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_clean_for_json(item) for item in data]
    elif isinstance(data, float):
        if data == float("inf"):
            return 999999
        elif data == -float("inf"):
            return -999999
        return round(data, 4)
    elif isinstance(data, int):
        if abs(data) > 1e8:
            return 1000000 if data > 0 else -1000000
        return data
    return data


def _parse_board(board_input):
    """Normalize board input from list or JSON string."""
    if isinstance(board_input, str):
        return json.loads(board_input)
    return [row[:] for row in board_input]


def get_ai_move(board_input, algorithm="alpha_beta", depth=3, player=AI):
    """
    Compute optimal AI move using specified algorithm.

    Returns JSON string with:
        selected_column: int (0-6)
        evaluation_score: float
        nodes_visited: int
        pruned_nodes: int
        search_depth: int
        execution_time: float (seconds)
        algorithm_name: str
        search_trace: list or None
    """
    board = _parse_board(board_input)
    depth = int(depth)
    player = int(player)

    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return json.dumps({
            "error": "No valid moves remaining",
            "selected_column": None
        })

    stats = {"nodes_visited": 0, "pruned_nodes": 0}
    trace = []
    start_time = time.perf_counter()

    if algorithm.lower() in ("minimax", "mm"):
        best_col, score = minimax_search(
            board, depth, True, player, stats,
            trace_parent=trace if depth <= 3 else None,
            max_trace_depth=max(1, depth - 1)
        )
        algo_display = "Minimax"
    else:
        best_col, score = alpha_beta_search(
            board, depth, -float("inf"), float("inf"), True, player, stats,
            trace_parent=trace if depth <= 3 else None,
            max_trace_depth=max(1, depth - 1)
        )
        algo_display = "Alpha-Beta Pruning"

    elapsed_time = time.perf_counter() - start_time

    if best_col is None and valid_moves:
        best_col = valid_moves[0]

    result = {
        "selected_column": best_col,
        "evaluation_score": int(score) if score is not None and abs(score) < 1e8 else 0,
        "nodes_visited": stats["nodes_visited"],
        "pruned_nodes": stats["pruned_nodes"],
        "search_depth": depth,
        "execution_time": round(elapsed_time, 4),
        "execution_time_ms": round(elapsed_time * 1000, 2),
        "algorithm_name": algo_display,
        "search_trace": trace
    }

    return json.dumps(_clean_for_json(result))


def get_hint(board_input, algorithm="alpha_beta", depth=3, player=HUMAN):
    """Compute optimal hint move for human player."""
    return get_ai_move(board_input, algorithm=algorithm, depth=depth, player=player)


def run_benchmark(board_input, depth=3, player=AI):
    """
    Run identical board search on Minimax and Alpha-Beta.
    Returns side-by-side metrics:
    - Minimax nodes, time, move, score
    - Alpha-Beta nodes, time, move, score, pruned count
    - Pruning efficiency percentage
    """
    board = _parse_board(board_input)
    depth = int(depth)
    player = int(player)

    # 1. Minimax run
    b1 = copy_board(board)
    stats_mm = {"nodes_visited": 0, "pruned_nodes": 0}
    t0_mm = time.perf_counter()
    col_mm, score_mm = minimax_search(b1, depth, True, player, stats_mm)
    time_mm = time.perf_counter() - t0_mm

    # 2. Alpha-Beta run
    b2 = copy_board(board)
    stats_ab = {"nodes_visited": 0, "pruned_nodes": 0}
    t0_ab = time.perf_counter()
    col_ab, score_ab = alpha_beta_search(b2, depth, -float("inf"), float("inf"), True, player, stats_ab)
    time_ab = time.perf_counter() - t0_ab

    # Savings calculation
    savings_nodes = 0.0
    if stats_mm["nodes_visited"] > 0:
        savings_nodes = (
            (stats_mm["nodes_visited"] - stats_ab["nodes_visited"]) / stats_mm["nodes_visited"]
        ) * 100.0

    savings_time = 0.0
    if time_mm > 0:
        savings_time = ((time_mm - time_ab) / time_mm) * 100.0

    res_bench = {
        "depth": depth,
        "player": player,
        "minimax": {
            "selected_column": col_mm,
            "evaluation_score": int(score_mm) if score_mm is not None and abs(score_mm) < 1e8 else 0,
            "nodes_visited": stats_mm["nodes_visited"],
            "pruned_nodes": 0,
            "execution_time_ms": round(time_mm * 1000, 2)
        },
        "alpha_beta": {
            "selected_column": col_ab,
            "evaluation_score": int(score_ab) if score_ab is not None and abs(score_ab) < 1e8 else 0,
            "nodes_visited": stats_ab["nodes_visited"],
            "pruned_nodes": stats_ab["pruned_nodes"],
            "execution_time_ms": round(time_ab * 1000, 2)
        },
        "move_match": (col_mm == col_ab),
        "node_savings_percent": round(max(0.0, savings_nodes), 1),
        "time_savings_percent": round(max(0.0, savings_time), 1)
    }
    return json.dumps(_clean_for_json(res_bench))


def get_tree_trace(board_input, algorithm="alpha_beta", depth=2, player=AI):
    """
    Generate detailed tree trace specifically formatted for AI Lab tree explorer.
    """
    board = _parse_board(board_input)
    depth = min(int(depth), 3)  # Keep visualization responsive
    player = int(player)

    stats = {"nodes_visited": 0, "pruned_nodes": 0}
    root_trace = []

    if algorithm.lower() in ("minimax", "mm"):
        minimax_search(
            board, depth, True, player, stats,
            trace_parent=root_trace,
            max_trace_depth=1
        )
    else:
        alpha_beta_search(
            board, depth, -float("inf"), float("inf"), True, player, stats,
            trace_parent=root_trace,
            max_trace_depth=1
        )

    tree_res = {
        "algorithm": algorithm,
        "depth": depth,
        "nodes_visited": stats["nodes_visited"],
        "pruned_nodes": stats["pruned_nodes"],
        "tree": {
            "type": "ROOT",
            "player": player,
            "col": None,
            "children": root_trace
        }
    }
    return json.dumps(_clean_for_json(tree_res))
