# Connect 4 - AI Minimax & Alpha-Beta Engine

A modern, highly polished Connect 4 desktop game developed with pure Python and `tkinter`. Features an AI engine written from scratch using **Minimax** and **Alpha-Beta Pruning**, dynamic heuristic board evaluation, tactile physics-based coin drop animations, a cheeky animated robot opponent with gaze tracking and witty dialogue, and a custom-designed dark/light UI with zero default system widgets.

- **Course:** Introduction to Artificial Intelligence (CAI3101 / CS366)
- **Institution:** Arab Academy for Science, Technology and Maritime Transport
- **Language:** Python 3.8+ (Standard Library: `tkinter`, `time`, `threading`, `unittest`, `winsound`)
- **Dependencies:** None for core gameplay and AI test suites (Standard Library only). **Optional:** `opencv-python` and `Pillow` enable victory video animations inside the Opponent card (`pip install -r requirements.txt`). If omitted, the game runs normally with the static robot commentary.

---

## 1. How to Run

### Start the Application
From the repository root or the `connect4/` directory:
```bash
python main.py
```

### Install Optional Video Dependencies (Optional)
To enable victory video animations in the Opponent card:
```bash
pip install -r requirements.txt
```

### Run Unit Tests
To run all 24 automated unit tests (game mechanics, winning line detection, Minimax/Alpha-Beta parity, pruning efficiency, and video discovery/selection):
```bash
python -m unittest discover -s tests
```

---

## 2. Architecture & File Overview

```
connect4/
├── main.py            # Application entry point; initializes window and Connect4App
├── game.py            # Pure game logic: 6x7 grid, gravity, win detection, draw, undo
├── ai.py              # Heuristic evaluation, Minimax, Alpha-Beta pruning, best_move()
├── gui.py             # Main interface: responsive arena, game flow, celebration overlays
├── video_player.py    # Victory video player (OpenCV + Pillow), letterboxing & controls
├── widgets.py         # Custom canvas controls: SegmentedControl, RoundedButton, ToggleSwitch, Card
├── avatar.py          # Interactive robot avatar: eyes tracking hovered column, expressions, blinking
├── messages.py        # Contextual humorous dialogue system and dynamic pruning statistics
├── theme.py           # Coordinated Dark (default) and Light color palettes
├── requirements.txt   # Optional dependencies for victory video playback (OpenCV, Pillow)
├── videos/            # Victory video directories with .gitkeep placeholders
│   ├── computer_wins/ # Clips played when Computer wins (or 'computer win')
│   └── human_wins/    # Clips played when Human wins (or 'user win')
├── tests/
│   ├── test_game.py   # Unit tests for horizontal, vertical, diagonal wins, draw, gravity, undo
│   ├── test_ai.py     # Unit tests verifying Minimax == Alpha-Beta moves, node counts, blocking, hint
│   └── test_video.py  # Unit tests for file auto-discovery, case sensitivity, and non-repeating random pick
├── README.md          # User manual, architecture breakdown, and oral discussion guide
└── REPORT.docx        # Academic project report (3-5 pages) formatted for course submission
```

> **Clean Architecture:** `game.py` and `ai.py` contain zero GUI code or `tkinter` imports. All AI and game mechanics remain completely modular, headless, and verifiable by automated unit tests.

---

## 3. Keyboard Shortcuts

Play seamlessly without touching the mouse:

| Key | Action | Description |
| :---: | :--- | :--- |
| **`1` – `7`** | **Drop Coin** | Drop a piece into columns 1 through 7 |
| **`N`** | **New Game** | Reset board and start a new game |
| **`U`** | **Undo Move** | Revert your last move and the computer's reply |
| **`H`** | **Hint** | Highlight the optimal column with glowing arrow |
| **`C`** | **Compare AI** | Open side-by-side Minimax vs Alpha-Beta benchmark |

---

## 4. Key UI & Visual Features

1. **Custom Themed Widgets:** Replaced all standard Tkinter controls with sleek Canvas-drawn widgets (`SegmentedControl`, `RoundedButton`, `ToggleSwitch`, `Card`). No ugly grey/white radio button boxes or square borders anywhere in either theme.
2. **Cheeky Robot Opponent:**
   - **Gaze Tracking:** The robot's eyes dynamically follow the column your cursor is hovering over.
   - **Situational Expressions:** Changes face dynamically (neutral, thinking, smug, surprised, sad on loss, happy on win).
   - **Natural Blinking:** Blinks periodically via non-blocking timers.
   - **Contextual Dialogue:** Features over 80 humorous lines for game openings, tactical blocks, mistakes, wins, hints, undo, and 20-second idle prompts. Includes a "Chatty Robot" toggle switch.
3. **Tactile Board & Coins:**
   - Soft drop shadow behind the board casing.
   - Hole cutouts with dark inner-shadow rim effect.
   - 3D styled coins with top-left highlight arcs and bottom-right shaded rims.
   - Hover column beam highlight and floating translucent ghost preview coin.
4. **Physics Coin-Drop Animation:**
   - Coins drop with gravity acceleration and a subtle, tactile bounce upon landing.
   - Input is locked during animation to prevent race conditions.
5. **Celebration Effects:**
   - Human victory triggers a celebratory confetti particle shower.
   - Winning coins are highlighted with pulsing double glow rings and a line connecting all 4 coins.
6. **Side-by-Side Compare Mode:**
   - Pops up an algorithm benchmark showing proportional horizontal progress bars for nodes visited.
   - Displays exact search times, same-move confirmation badge, and node reduction percentage.
7. **Session Scoreboard:**
   - Big, readable score digits with color-coded player dots (You, Robot, Draws) that persist through "New Game" restarts. Includes a "Reset Scores" button.
8. **Dark / Light Theme Toggle:**
   - Sliding knob switch instantly transitions all frames, canvases, cards, and buttons between deep midnight slate and crisp light mode.
9. **Victory Video Player inside Opponent Card:**
   - On a win (Human or AI), the robot avatar and dialogue bubble swap seamlessly with a letterboxed victory video embedded directly inside the "Opponent" card.
   - Automatically selects a random clip from `videos/human_wins/` or `videos/computer_wins/` (also auto-detecting `user win/` and `computer win/`), preventing immediate repeats.
   - Includes transport controls (Play/Pause, Skip ✕, and real-time elapsed counter) styled to match the active theme.
   - Automatically and gracefully restores the robot avatar and speech bubble upon video conclusion, or immediately when clicking Skip, New Game, Undo, or Reset Scores.
   - Plays synchronized audio when Sound is enabled and cleanly mutes when toggled off.
   - Completely optional: falls back gracefully without video if OpenCV or Pillow are not installed.

---

## 5. Measured Search Performance

Numbers directly measured by profiling on Python 3.12:

| Scenario | Depth | Minimax Nodes | Alpha-Beta Nodes | Node Reduction (%) | Minimax Time | Alpha-Beta Time | Move Match |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Empty Board** | 1 | 8 | 8 | 0.0% | 0.43 ms | 0.34 ms | Yes (Col 4) |
| **Empty Board** | 3 | 400 | 82 | **79.5%** | 17.04 ms | 3.28 ms | Yes (Col 4) |
| **Empty Board** | 5 | 19,608 | 1,295 | **93.4%** | 885.26 ms | 50.55 ms | Yes (Col 4) |
| **Early Game (2 pcs)** | 3 | 400 | 132 | **67.0%** | 17.86 ms | 5.96 ms | Yes (Col 3) |
| **Early Game (2 pcs)** | 5 | 19,607 | 1,244 | **93.7%** | 899.59 ms | 51.37 ms | Yes (Col 3) |
| **Mid Game (6 pcs)** | 3 | 400 | 131 | **67.3%** | 18.26 ms | 5.22 ms | Yes (Col 3) |
| **Mid Game (6 pcs)** | 5 | 18,618 | 1,418 | **92.4%** | 836.68 ms | 58.97 ms | Yes (Col 5) |

*Core Insights:*
- Alpha-Beta selects the **exact same move** as Minimax in 100% of tested board states.
- At Depth 5 (Hard), Alpha-Beta eliminates **over 92% to 93%** of the search tree, executing approximately **16 times faster** (~50 ms vs. ~885 ms).

---

## 6. Oral Discussion & Demo Script

When presenting this project to course instructors or examiners, follow this structured demonstration:

1. **Launch the Game:**
   Run `python main.py`. Point out the dark theme, the vector logo in the header, and the three-panel layout.
2. **Demonstrate Custom Themed Widgets:**
   Click the **Segmented Controls** for First Move, Algorithm, and Difficulty. Note the smooth pill animation and that there are **no default white or grey Tkinter widgets**. Point out the dynamic subtitle under Difficulty ("Warm-up", "Now it is personal", "Prepare to be outsmarted").
3. **Demonstrate Window Resizing:**
   Resize and maximize the window. Show that the board dynamically expands to fill available space while maintaining strict 7:6 circular coin aspect ratios and centered alignment.
4. **Show Robot Avatar & Gaze Tracking:**
   Move the mouse across columns 1 to 7. Show the robot's eyes physically tracking the cursor's column position in real time!
5. **Drop a Coin with Bounce Animation:**
   Click Column 4 (or press `4` on the keyboard). Observe the hover preview ghost coin, the accelerating drop animation, the subtle landing bounce, and the sound effect.
6. **Show AI Thinking State & Dialogue:**
   Observe the robot looking up with animated dots and dialogue explaining the search depth. Point to the **Last AI Move** telemetry card showing chosen column, nodes visited, and search duration in milliseconds.
7. **Demonstrate Compare Mode (Press `C` or click Compare AI):**
   Open the modal benchmark. Show the dual comparative progress bars comparing Minimax nodes vs. Alpha-Beta nodes, the same-move confirmation badge, and the node savings percentage badge.
8. **Demonstrate Hint (Press `H` or click Hint):**
   Show the cyan glowing arrow pointing to the optimal column, accompanied by witty dialogue.
9. **Demonstrate 2-Ply Undo (Press `U` or click Undo Move):**
   Click Undo. Note that both the computer's reply and your last move are cleanly reverted, restoring the turn to Human.
10. **Demonstrate AI Defensive Blocking:**
    Set up a 3-in-a-row threat. Show that the AI prioritizes defensive blocking over greedy expansion (`PENALTY_THREE = -140` vs. `SCORE_THREE = +100`).
11. **Demonstrate Celebrations:**
    Win the game to trigger the victory confetti particle shower, the glowing pulse rings around the 4 winning coins, the victory line, and the scoreboard increment.
12. **Demonstrate Theme Toggle Switch:**
    Click the sliding Theme switch in the top-right corner to show the Light theme. Notice that all cards, buttons, avatar colors, and board gradients adapt smoothly with great contrast.
13. **Run Automated Test Suite:**
    In the terminal, run `python -m unittest discover -s tests`. Point out that all 17 tests pass in under 3 seconds, proving game rule fidelity and algorithmic equivalence.
