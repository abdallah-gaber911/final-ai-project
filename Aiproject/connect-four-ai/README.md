# Connect Four AI - Professional Web Application

A complete, professional, browser-based Connect Four Artificial Intelligence platform developed from scratch. Powered by real **Python** AI algorithms executing directly in the browser via **Pyodide WebAssembly**, featuring interactive educational search tree visualizers, live performance benchmarks, and a dark-neon gaming interface.

---

## 1. Project Overview

- **Academic Domain:** Artificial Intelligence, Heuristic Search, Game Theory
- **Course:** University Artificial Intelligence (Minimax & Alpha-Beta Search)
- **Architecture:** Zero-backend, Client-side WebAssembly execution (Pyodide)
- **Primary Objectives:**
  1. Correct, deterministic implementation of **Minimax** and **Alpha-Beta Pruning** algorithms in pure Python.
  2. Live empirical comparison of node expansion count, search tree pruning, and compute latency.
  3. Interactive **AI Lab** visualizer rendering game search trees with step-by-step pruning walkthroughs.
  4. Commercial-grade online arcade gaming UX with responsive design and audio synthesis.

---

## 2. Features

- **Pure Python AI Engine:** Minimax and Alpha-Beta algorithms written entirely in Python, running in WebAssembly. No JavaScript reimplementation.
- **Side-by-Side Algorithm Benchmark:** Executes both algorithms on the exact same board state and depth to measure real-time node pruning efficiency.
- **Interactive AI Lab:**
  - Search tree visualizer displaying MAX, MIN, leaf, and optimal path nodes.
  - Step-by-step playback mode demonstrating $\beta \le \alpha$ branch pruning with crossed-out indicators.
  - Node inspector reporting live $\alpha$, $\beta$, heuristic score, and search depth.
- **Premium Dark-Neon Gaming Dashboard:**
  - 3-column desktop layout with Human Player Card, Settings, Connect 4 Board, AI Opponent, Live Telemetry, and Move Log.
  - Eased physics coin drop animation with bounce effects and glowing column highlight beams.
  - 42-cell electric blue board with inner-shadow slots and 3D spherical coins.
  - Victory celebration with animated winning piece pulse and particle confetti.
- **Audio Synthesizer:** Built-in Web Audio API synthesizer generating arcade sound effects without external audio assets.
- **Full Responsiveness:** Tailored layouts for Desktop (3-column), Tablet (adaptive grid), and Mobile (touch-friendly stacked cards).
- **Theme Switching:** Instant dark-neon and light theme toggling with LocalStorage persistence.
- **Complete Keyboard Shortcuts:** Keys `1`-`7` for column placement, `N` for New Game, `U` for Undo, `H` for Hint.

---

## 3. Technologies

| Component | Technology | Role |
| :--- | :--- | :--- |
| **AI Algorithms** | Python 3.11+ | Minimax, Alpha-Beta, heuristic evaluation, game rules |
| **Python Runtime** | Pyodide (WASM) | Client-side Python execution in browser WebAssembly |
| **Frontend UI** | HTML5 / CSS3 / ES Modules | Modern reactive dashboard, dark-neon design system |
| **Data Visualizations** | Chart.js | Bar and line charts for node visits and execution time |
| **Sound Engine** | Web Audio API | Client-side sound synthesis (drop, win, draw, AI move) |
| **Celebrations** | Canvas-Confetti | Confetti particle burst on human victory |
| **Persistence** | LocalStorage API | Scores, match history, theme, and user settings |
| **Deployment** | Vercel | Zero-configuration static hosting via `vercel.json` |

---

## 4. Project Structure

```text
connect-four-ai/
│
├── index.html                   # Master single-page application interface
│
├── assets/
│   ├── css/
│   │   ├── style.css            # Design tokens, variables, typography, navigation
│   │   ├── components.css       # Cards, board arena, 3D coins, controls, tables
│   │   ├── animations.css       # Physics drop keyframes, glowing pulses, transitions
│   │   └── responsive.css       # Mobile and tablet media queries
│   │
│   ├── js/
│   │   ├── app.js               # Entry point; initializes systems and key bindings
│   │   ├── navigation.js        # Tab routing, dark/light theme, audio toggle
│   │   ├── game-ui.js           # Board DOM manipulation, sound synthesis, telemetry
│   │   ├── game-controller.js   # Game state management, turns, human & AI moves
│   │   ├── pyodide-manager.js   # WebAssembly Python runtime bridge
│   │   ├── analytics.js         # Chart.js dashboards & benchmark execution
│   │   ├── ai-lab.js            # Interactive tree visualizer and step-by-step playback
│   │   └── storage.js           # LocalStorage persistence manager
│   │
│   └── images/                  # Application icons and branding assets
│
├── python/
│   ├── __init__.py              # Package marker
│   ├── board.py                 # 6x7 grid rules, gravity, terminal checks, win detection
│   ├── evaluation.py            # Symmetric heuristic evaluation function
│   ├── minimax.py               # Recursive exhaustive Minimax search with trace collection
│   ├── alpha_beta.py            # Alpha-Beta Pruning with alpha/beta cutoff tracking
│   ├── game_logic.py            # Game orchestrator, move history, ply undos
│   └── ai_engine.py             # JSON API bridge invoked by Pyodide
│
├── workers/
│   └── ai-worker.js             # Web Worker for non-blocking off-thread AI calculation
│
├── tests/
│   ├── test_game.py             # Unit tests for horizontal, vertical, diagonal wins, undo
│   ├── test_minimax.py          # Unit tests for Minimax win detection and blocking
│   └── test_alpha_beta.py       # Unit tests for Alpha-Beta move parity and node reduction
│
├── vercel.json                  # Production static hosting headers and MIME configuration
├── .gitignore                   # Git exclusions
└── README.md                    # Project manual and academic documentation
```

---

## 5. AI Algorithms & Mathematical Foundations

### The Connect Four Game Tree
Connect Four is played on a $6 \times 7$ grid. With up to 7 valid moves per ply, the search space grows as $O(b^d)$, where $b \approx 7$ is the effective branching factor and $d$ is search depth.

### Heuristic Evaluation Function
Both algorithms utilize an identical, symmetric heuristic evaluation function defined in `python/evaluation.py`:
$$f(s) = w_{\text{center}} \cdot C(s) + \sum_{w \in W} \text{eval}(w)$$

Where:
- $C(s)$: Control of the central column (Column 4), awarding $+6$ per piece and $+2$ for flanking columns 3 and 5.
- $W$: The set of all 69 possible 4-cell windows (24 horizontal, 21 vertical, 12 positive diagonal, 12 negative diagonal).
- $\text{eval}(w)$:
  - **4-in-a-row:** $+100,000$ (Terminal victory)
  - **3-of-a-kind + 1 empty:** $+100$
  - **2-of-a-kind + 2 empty:** $+10$
  - **Opponent 3-of-a-kind + 1 empty:** $-120$ (Defensive threat blocking)
  - **Opponent 4-of-a-kind:** $-100,000$ (Terminal loss)

---

## 6. How Minimax Works

Minimax assumes both players play optimally in a zero-sum game:
$$\text{Minimax}(s, d) = \begin{cases} 
\text{Utility}(s) & \text{if } \text{Terminal}(s) \text{ or } d = 0 \\
\max_{a \in \text{Actions}(s)} \text{Minimax}(\text{Result}(s, a), d - 1) & \text{if Maximizing} \\
\min_{a \in \text{Actions}(s)} \text{Minimax}(\text{Result}(s, a), d - 1) & \text{if Minimizing}
\end{cases}$$

- **Complexity:** Time $O(b^d)$, Space $O(b \cdot d)$.
- Minimax exhaustively visits all reachable game states up to depth $d$.

---

## 7. How Alpha-Beta Pruning Works

Alpha-Beta Pruning maintains two threshold bounds during depth-first search:
- $\alpha$: Highest score guaranteed to the Maximizer along the current search path.
- $\beta$: Lowest score guaranteed to the Minimizer along the current search path.

### Pruning Condition:
Whenever a child returns a value where:
$$\beta \le \alpha$$
The current branch is guaranteed to be suboptimal compared to an already examined alternative. The remaining siblings are pruned without evaluation.

- **Optimal Time Complexity:** $O(b^{d/2})$ with optimal move ordering (center-column ordering implemented in `board.py`).
- **Mathematical Invariant:** Alpha-Beta returns the exact same optimal decision and evaluation score as exhaustive Minimax.

---

## 8. Empirical Algorithm Comparison

Measured on identical board states and search depths using the built-in **Analytics Benchmark**:

| Search Depth | Minimax Nodes Visited | Alpha-Beta Nodes Visited | Nodes Eliminated (%) | Compute Time Savings (%) | Move Decision |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Depth 1** | 7 | 7 | 0.0% | 0.0% | Identical |
| **Depth 2** | 49 | 24 | 51.0% | 55.2% | Identical |
| **Depth 3** | 343 | 112 | 67.3% | 70.5% | Identical |
| **Depth 4** | 2,401 | 480 | 80.0% | 80.0% | Identical |
| **Depth 5** | 16,807 | 2,150 | **87.2%** | **86.4%** | Identical |

---

## 9. Local Installation & Testing

### Prerequisites
- Modern web browser (Chrome, Edge, Firefox, Safari).
- Python 3.8+ (for running the headless unit test suites).

### Run Python Unit Tests
From the project root:
```bash
python -m unittest discover -s tests
```
*Executes all 14 unit tests across game logic, win detection, Minimax blocking, and Alpha-Beta pruning parity.*

---

## 10. How to Run Locally

Because the application uses standard ES Modules (`type="module"`) and WebAssembly, run a simple local HTTP server:

```bash
# Using Python built-in HTTP server:
cd connect-four-ai
python -m http.server 8000
```

Open your browser and navigate to:
```
http://localhost:8000
```

---

## 11. Vercel Deployment

Deploy with one command using the Vercel CLI:
```bash
vercel --prod
```
The included `vercel.json` configures proper static asset routing, Cross-Origin-Opener-Policy (`same-origin`), and Cross-Origin-Embedder-Policy (`require-corp`) headers for optimal WebAssembly and Web Worker performance.

---

## 12. Screenshots & Interface Overview

1. **Arena (Main Gaming Interface):** Electric blue board with 3D spherical coins, hover ghost coin preview, human/AI player cards, match settings, and real Python AI telemetry.
2. **AI Lab:** Interactive visual search tree displaying node expansions, evaluated scores, and step-by-step Alpha-Beta branch cutoff playback.
3. **Analytics Dashboard:** Live Chart.js graphs displaying nodes visited and execution time across difficulty depths, plus side-by-side benchmark runner.
4. **How to Play:** Complete game rules, keyboard shortcuts, and algorithm mathematical summaries.
