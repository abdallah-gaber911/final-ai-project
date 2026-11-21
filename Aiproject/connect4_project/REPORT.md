# Connect 4: AI Game Engine with Minimax and Alpha-Beta Pruning
**Course Project Report | CAI3101 / CS366: Introduction to Artificial Intelligence**  
*College of Computing and Information Technology | Arab Academy for Science, Technology and Maritime Transport*

---

## 1. The Game and Its Rules

Connect 4 is a classic two-player zero-sum deterministic board game of perfect information. The game is played on a vertical grid consisting of **6 rows and 7 columns**, comprising 42 individual slots. In this implementation:
- The **Human** plays with **Red** pieces.
- The **Computer AI** plays with **Yellow** pieces.

### Gameplay Rules
1. **Turns & Gravity:** Players take turns selecting one of the seven columns (indexed 0 through 6). The piece drops to the lowest available empty cell in the selected column.
2. **Column Restrictions:** If a column has all 6 slots filled, it is invalid and no further pieces may be placed in it.
3. **Winning Condition:** The first player to align **four pieces contiguously** in any straight line wins immediately. Valid lines include:
   - Horizontal lines (4 in a row)
   - Vertical lines (4 in a column)
   - Diagonal lines with positive slope (down-right / up-left)
   - Diagonal lines with negative slope (down-left / up-right)
4. **Draw Condition:** If all 42 positions on the board are occupied and neither player has achieved a four-in-a-row connection, the match terminates in a draw.

---

## 2. Architecture and Program Structure

The application is structured into modular components, isolating the core game rules and AI decision algorithms from graphical presentation.

```
connect4/
├── main.py            # Entry point: configures geometry and boots Connect4App
├── game.py            # Board representation, move validation, gravity, win/draw checking, undo
├── ai.py              # Heuristic evaluation, Minimax, Alpha-Beta pruning, best_move()
├── gui.py             # Tkinter desktop interface: layout, board scaling, animations, modals
├── theme.py           # Coordinated Dark (default) and Light color palettes
├── tests/
│   ├── test_game.py   # Unit tests for game logic, wins, draw, gravity, and undo
│   └── test_ai.py     # Unit tests verifying Minimax vs Alpha-Beta parity and pruning
├── README.md          # Comprehensive user manual and oral discussion guide
├── REPORT.docx        # Submission-ready Word document report
└── REPORT.md          # Markdown mirror of the report
```

### Module Interactions
- **Pure Logic Isolation:** Neither `game.py` nor `ai.py` imports `tkinter`. All game logic can be executed headless, tested via `unittest`, and analyzed independently.
- **Event Flow:** The GUI listens to user input (mouse clicks, button presses, option selections), invokes `drop_piece()` or `undo_piece()` in `game.py`, delegates computer move calculations or hints to `best_move()` in `ai.py`, and renders the visual feedback onto an adaptive canvas.

---

## 3. How Minimax Works

Minimax is a recursive decision algorithm for two-player adversarial games. One player is designated as the **Maximizer** (aiming for the highest possible evaluation score), and the other is the **Minimizer** (aiming to minimize the score).

Because the Connect 4 state space contains approximately $4.53 \times 10^{12}$ reachable positions, exhaustive search to the game end is computationally infeasible for interactive play. The algorithm therefore enforces a depth limit (1, 3, or 5 plies):

1. **Terminal & Depth Check:** At each step, if a winning state is detected, the algorithm returns a decisive score scaled by remaining depth ($100,000 + \text{depth}$), encouraging the AI to win as quickly as possible and delay inevitable losses. If the depth limit is reached without a terminal state, `evaluate_board()` computes a heuristic score.
2. **Recursive Exploration:**
   - At Maximizing plies, it tries each legal column in center-first order (`[3, 2, 4, 1, 5, 0, 6]`), drops the piece, recursively calls Minimax at `depth - 1` with `is_maximizing = False`, undos the move, and retains the maximum value.
   - At Minimizing plies, it simulates the opponent's counter-moves, recursing with `is_maximizing = True`, and retains the minimum value.
3. **Backpropagation:** The computed value propagates back to the root, selecting the column that guarantees the optimal outcome under the assumption of perfect opponent play.

---

## 4. How Alpha-Beta Pruning Works

Alpha-Beta Pruning optimizes the standard Minimax search by eliminating subtrees that cannot influence the final root decision.

### The Bounding Variables
- **Alpha ($\alpha$):** The best (highest) value that the Maximizer has found so far along the path (initialized to $-\infty$).
- **Beta ($\beta$):** The best (lowest) value that the Minimizer has found so far along the path (initialized to $+\infty$).

### Cut-off Conditions
- **Beta Cut-off (at Maximizer node):** If a child move produces a value $V \ge \beta$, the minimizing ancestor above will never allow the game to enter this state (it already has an alternative branch guaranteeing a value $\le \beta$). The remaining children of this node can be immediately pruned.
- **Alpha Cut-off (at Minimizer node):** If a child move produces a value $V \le \alpha$, the maximizing ancestor above will never select this branch (it already has an alternative guaranteeing $\ge \alpha$). The remaining children can be safely skipped.

### Move Equivalence and Efficiency
Because pruned branches can never exceed $\alpha$ or fall below $\beta$, pruning preserves the **exact mathematical minimax value**. Furthermore, because our implementation orders columns **center-first** in both algorithms and enforces identical tie-breaking, Alpha-Beta is proven by our unit tests to choose the **identical move** as Minimax in 100% of tested board states, while pruning over 92% to 93% of nodes at depth 5.

---

## 5. The Evaluation Function

When the search reaches the depth limit without encountering a terminal victory or draw, the heuristic evaluation function scores the board from the viewpoint of the maximizing player.

Connect 4 has exactly **69 distinct 4-cell windows** across the board:
- 24 horizontal windows
- 21 vertical windows
- 12 diagonal down-right windows
- 12 diagonal down-left windows

### Heuristic Weights and Rationale
- **`SCORE_WIN = 100,000`:** Decisive terminal score.
- **`SCORE_THREE = +100`:** Awarded for a window with 3 player coins and 1 empty cell. Represents an immediate offensive alignment.
- **`SCORE_TWO = +10`:** Awarded for a window with 2 player coins and 2 empty cells. Encourages developing multi-directional threats.
- **`PENALTY_THREE = -140`:** Subtracted when the opponent has 3 coins and 1 empty cell. Setting this penalty higher than `SCORE_THREE` ensures the AI prioritizes defensive blocking over greedy attacks.
- **`PENALTY_TWO = -10`:** Subtracted when the opponent has 2 coins and 2 empty cells, countering opponent development.
- **`CENTER_BONUS = +4`:** Awarded for each coin occupying the center column (column 3). The center column participates in up to 13 distinct 4-in-a-row lines, granting significant tactical versatility compared to edge columns.

---

## 6. Difficulty Levels and Search Depth

The three difficulty levels scale the search lookahead depth:

1. **Easy (Depth 1):** One-ply search (visits only 8 nodes in under 1 ms). Instantly takes immediate terminal wins and avoids basic one-turn mistakes, but cannot plan multi-turn combinations.
2. **Medium (Depth 3):** Three-ply search (evaluates player move, opponent response, and player follow-up). Actively creates tactical forks, blocks opponent alignments, and avoids giving away wins. Response time: 3 to 6 ms.
3. **Hard (Depth 5):** Five-ply search exploring deep tactical sequences. Capable of setting multi-step traps and playing near-optimal Connect 4 strategy. With Alpha-Beta pruning, search completes in ~50 ms.

---

## 7. Experimental Results & Performance Comparison

The following numbers were directly measured by executing our benchmarking suite on Python 3.12:

| Scenario | Depth | Minimax Nodes | Alpha-Beta Nodes | Nodes Saved (%) | Minimax Time | Alpha-Beta Time | Move Match |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Empty Board** | 1 | 8 | 8 | 0.0% | 0.43 ms | 0.34 ms | Yes (Col 4) |
| **Empty Board** | 3 | 400 | 82 | **79.5%** | 17.04 ms | 3.28 ms | Yes (Col 4) |
| **Empty Board** | 5 | 19,608 | 1,295 | **93.4%** | 885.26 ms | 50.55 ms | Yes (Col 4) |
| **Early Game (2 pcs)** | 1 | 8 | 8 | 0.0% | 0.34 ms | 0.33 ms | Yes (Col 4) |
| **Early Game (2 pcs)** | 3 | 400 | 132 | **67.0%** | 17.86 ms | 5.96 ms | Yes (Col 3) |
| **Early Game (2 pcs)** | 5 | 19,607 | 1,244 | **93.7%** | 899.59 ms | 51.37 ms | Yes (Col 3) |
| **Mid Game (6 pcs)** | 1 | 8 | 8 | 0.0% | 0.35 ms | 0.34 ms | Yes (Col 3) |
| **Mid Game (6 pcs)** | 3 | 400 | 131 | **67.3%** | 18.26 ms | 5.22 ms | Yes (Col 3) |
| **Mid Game (6 pcs)** | 5 | 18,618 | 1,418 | **92.4%** | 836.68 ms | 58.97 ms | Yes (Col 5) |

### Key Observations
- At Depth 1, no pruning is possible because every valid move must be evaluated; node counts are identical (8 nodes).
- At Depth 3, Alpha-Beta reduces node expansion by 67% to 80%.
- At Depth 5, Alpha-Beta achieves a massive **92.4% to 93.7% reduction** in nodes visited, accelerating search time by ~16x.
- Across all test configurations, Minimax and Alpha-Beta selected the exact same column.

---

## 8. Extra Features Implemented

1. **Custom Themed UI Components (`widgets.py`):** Developed Canvas-based `SegmentedControl`, `RoundedButton`, and sliding `ToggleSwitch` widgets, eliminating all default system Tkinter widgets and preventing white/grey box artifacts in both dark and light modes.
2. **Cheeky Robot Opponent (`avatar.py` & `messages.py`):** Interactive canvas robot featuring live gaze tracking (eyes follow hovered column), spontaneous blinking, situational facial expressions (neutral, thinking, smug, surprised, sad, happy), and over 80 witty lines of dialogue with an optional "Chatty Robot" toggle switch.
3. **Tactile Physics Coin-Drop Animation:** Coins drop with gravity acceleration and a subtle landing bounce before locking into the grid, with input locked to prevent accidental clicks.
4. **Victory Celebrations & Visual Polish:** Confetti particle shower on human victory, pulsing double glow rings on the 4 winning coins, a victory connecting line, and 3D styled coins with spherical highlight arcs and inner-shadow slots.
5. **Side-by-Side Compare Mode:** An on-demand benchmark modal displaying scaled comparative horizontal progress bars (Minimax vs Alpha-Beta), move parity confirmation, and search tree node reduction percentage.
6. **Move Suggestion / Hint:** Highlights the optimal column for the human player with a glowing cyan arrow and friendly pointer dialogue.
7. **2-Ply Move Undo:** Reverts both the human's move and the computer's reply, with graceful handling of boundary conditions.
8. **Session Scoreboard & Hotkeys:** Bold digits for You, Robot, and Draws with colored player indicators; complete keyboard bindings (keys 1-7 for columns, N for New Game, U for Undo, H for Hint, C for Compare).
9. **Complete Theme & Audio Toggles:** Sliding knob switches toggle instantly between deep midnight slate and crisp light mode, and enable/mute sound effects.

---

## 9. Team Member Contributions

| Member | Student Name | Assigned Role & Responsibilities |
| :---: | :---: | :--- |
| **Member 1** | [Student Name 1] | **Game Logic & State Management:** Implemented 6x7 board, gravity mechanics, move validation, and tests in `game.py` & `test_game.py`. |
| **Member 2** | [Student Name 2] | **Minimax Search Engine:** Developed the recursive Minimax game tree algorithm, terminal checks, and node counting in `ai.py`. |
| **Member 3** | [Student Name 3] | **Alpha-Beta Optimization:** Engineered alpha/beta bounds tracking, cut-off mechanisms, and verified algorithmic parity in `ai.py`. |
| **Member 4** | [Student Name 4] | **Evaluation Function & Heuristics:** Designed 69-window pattern evaluation, center-column bonus, and difficulty tuning in `ai.py`. |
| **Member 5** | [Student Name 5] | **GUI & Animation:** Built the 3-panel Tkinter layout, dynamic canvas scaling, coin drop animation, and themes in `gui.py` & `theme.py`. |
| **Member 6** | [Student Name 6] | **Testing, Benchmarking & Report:** Created unit test suites in `test_ai.py`, collected empirical performance data, and prepared `REPORT.docx`. |

---

## 10. How to Run the App

1. Ensure Python 3.8+ is installed on your computer.
2. Open a terminal / command prompt and navigate to the project directory:
   ```bash
   cd connect4
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Run the automated test suite:
   ```bash
   python -m unittest discover -s tests
   ```
No third-party packages or internet access are required.
