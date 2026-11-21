/**
 * Game Controller for Connect Four AI
 * Coordinates game rules, human clicks, Pyodide AI turns, and state synchronization.
 */

import { PyodideManager } from './pyodide-manager.js';
import { StorageManager } from './storage.js';
import { Sound } from './game-ui.js';

export class GameController {
  constructor(ui, robot = null) {
    this.ui = ui;
    this.robot = robot;
    this.board = Array(6).fill(null).map(() => Array(7).fill(0));
    this.currentTurn = 1; // 1 = Human, 2 = AI
    this.isGameOver = false;
    this.isBusy = false;
    this.moveHistory = [];
    
    // Default Settings
    this.settings = StorageManager.getSettings();
    this.scores = StorageManager.getScores();

    // Bind UI callbacks
    this.ui.onColumnClick = (col) => this.handleHumanMove(col);
    this.ui.onColumnHover = (col) => {
      if (this.robot) {
        this.robot.setGazeByColumn(col);
      }
      if (!this.isBusy && !this.isGameOver && this.currentTurn === 1) {
        this.ui.setHoverColumn(col, true);
      }
    };

    this.ui.updateScores(this.scores.human, this.scores.ai);
  }

  startNewGame() {
    if (this.robot) {
      this.robot.stopVictoryVideo();
    }
    this.board = Array(6).fill(null).map(() => Array(7).fill(0));
    this.isGameOver = false;
    this.isBusy = false;
    this.moveHistory = [];
    this.ui.clearHistory();
    this.ui.renderBoard(this.board);

    this.currentTurn = this.settings.firstMove === 'ai' ? 2 : 1;

    if (this.currentTurn === 1) {
      this.ui.updateStatus("Your Turn! Drop a piece.", "human");
      this.ui.setHoverColumn(3, true);
      if (this.robot) {
        this.robot.say("game_start_human", "happy");
      }
    } else {
      this.ui.updateStatus("AI is computing opening move...", "ai");
      this.ui.setHoverColumn(null, false);
      if (this.robot) {
        this.robot.say("game_start_ai", "smug");
      }
      setTimeout(() => this.triggerAITurn(), 550);
    }
  }

  getBottomEmptyRow(col) {
    for (let r = 5; r >= 0; r--) {
      if (this.board[r][col] === 0) return r;
    }
    return null;
  }

  async handleHumanMove(col) {
    if (this.isBusy || this.isGameOver || this.currentTurn !== 1) return;

    const row = this.getBottomEmptyRow(col);
    if (row === null) return; // Column is full

    this.isBusy = true;
    this.board[row][col] = 1;
    this.moveHistory.push({ player: 1, row, col });
    this.ui.addHistory(this.moveHistory.length, 1, col);

    // Contextual Robot commentary
    if (this.robot) {
      if (col === 3) {
        this.robot.say("human_center", "thinking");
      } else if (col === 0 || col === 6) {
        this.robot.say("human_edge", "surprised");
      }
    }

    this.ui.animateDrop(row, col, 1, async () => {
      this.ui.renderBoard(this.board);

      // Check win
      const winCheck = this.checkWin(1);
      if (winCheck.won) {
        this.handleGameOver(1, winCheck.coords);
        return;
      }

      if (this.isBoardFull()) {
        this.handleGameOver(0, null);
        return;
      }

      this.currentTurn = 2;
      this.ui.updateStatus("AI Thinking...", "ai");
      this.ui.setHoverColumn(null, false);
      await this.triggerAITurn();
    });
  }

  async triggerAITurn() {
    if (this.isGameOver) return;
    this.isBusy = true;

    try {
      const depthMap = { easy: 1, medium: 3, hard: 5 };
      const depth = depthMap[this.settings.difficulty] || 3;
      const algo = this.settings.algorithm || 'alpha_beta';

      if (this.robot) {
        this.robot.say(`thinking_${this.settings.difficulty}`, "thinking");
      }

      // Call Python AI via Pyodide
      const result = await PyodideManager.getAIMove(this.board, algo, depth, 2);
      this.ui.updateTelemetry(result);

      const aiCol = result.selected_column;
      const aiRow = this.getBottomEmptyRow(aiCol);

      if (aiRow !== null) {
        this.board[aiRow][aiCol] = 2;
        this.moveHistory.push({ player: 2, row: aiRow, col: aiCol });
        this.ui.addHistory(this.moveHistory.length, 2, aiCol);

        this.ui.animateDrop(aiRow, aiCol, 2, () => {
          this.ui.renderBoard(this.board);

          const winCheck = this.checkWin(2);
          if (winCheck.won) {
            this.handleGameOver(2, winCheck.coords);
            return;
          }

          if (this.isBoardFull()) {
            this.handleGameOver(0, null);
            return;
          }

          this.currentTurn = 1;
          this.isBusy = false;
          this.ui.updateStatus("Your Turn!", "human");
          this.ui.setHoverColumn(aiCol, true);
          if (this.robot) {
            this.robot.setExpression("happy");
          }
        });
      }
    } catch (err) {
      console.error("[AI Turn Error]", err);
      this.isBusy = false;
      // Show specific error and try JS fallback
      const errMsg = err && err.message ? err.message : String(err);
      console.warn("[AI Fallback] Attempting JS fallback minimax...", errMsg);
      try {
        const fallbackCol = this._jsFallbackMove();
        if (fallbackCol !== null) {
          this.ui.updateStatus(`⚠️ Pyodide error (using JS fallback): ${errMsg.slice(0, 60)}`, "error");
          // Execute the fallback move silently
          const fallbackRow = this.getBottomEmptyRow(fallbackCol);
          if (fallbackRow !== null) {
            this.board[fallbackRow][fallbackCol] = 2;
            this.moveHistory.push({ player: 2, row: fallbackRow, col: fallbackCol });
            this.ui.addHistory(this.moveHistory.length, 2, fallbackCol);
            this.ui.animateDrop(fallbackRow, fallbackCol, 2, () => {
              this.ui.renderBoard(this.board);
              const winCheck = this.checkWin(2);
              if (winCheck.won) { this.handleGameOver(2, winCheck.coords); return; }
              if (this.isBoardFull()) { this.handleGameOver(0, null); return; }
              this.currentTurn = 1;
              this.isBusy = false;
              this.ui.updateStatus("Your Turn!", "human");
              this.ui.setHoverColumn(fallbackCol, true);
            });
            return;
          }
        }
      } catch (fbErr) {
        console.error("[AI Fallback Failed]", fbErr);
      }
      this.ui.updateStatus(`AI Error: ${errMsg.slice(0, 80)}`, "error");
    }
  }

  /** JS-side fallback: pick center-biased random valid column. */
  _jsFallbackMove() {
    const order = [3, 2, 4, 1, 5, 0, 6];
    for (const col of order) {
      if (this.getBottomEmptyRow(col) !== null) return col;
    }
    return null;
  }

  async requestHint() {
    if (this.isBusy || this.isGameOver || this.currentTurn !== 1) return;
    this.isBusy = true;
    this.ui.updateStatus("Calculating optimal hint via AI...", "human");
    if (this.robot) {
      this.robot.say("hint", "thinking");
    }

    try {
      const depthMap = { easy: 1, medium: 3, hard: 5 };
      const depth = depthMap[this.settings.difficulty] || 3;
      const result = await PyodideManager.getHint(this.board, 'alpha_beta', depth, 1);
      
      if (result && result.selected_column !== null) {
        this.ui.showHint(result.selected_column);
        this.ui.updateStatus(`Hint: Column ${result.selected_column + 1} recommended!`, "human");
      }
    } catch (err) {
      console.error("[Hint Error]", err);
    } finally {
      this.isBusy = false;
    }
  }

  undoMove() {
    // Allow undo even after game over (so player can review/continue)
    if (this.isBusy || this.moveHistory.length === 0) return;

    if (this.robot) {
      this.robot.stopVictoryVideo();
      this.robot.say("undo", "surprised");
    }

    // Reset game-over state before undoing
    this.isGameOver = false;
    this.isBusy = false;

    // Undo the last move(s): if AI moved last, pop both AI + Human plies
    const last = this.moveHistory.pop();
    this.board[last.row][last.col] = 0;

    if (last.player === 2 && this.moveHistory.length > 0 && this.moveHistory[this.moveHistory.length - 1].player === 1) {
      const humanLast = this.moveHistory.pop();
      this.board[humanLast.row][humanLast.col] = 0;
    }

    this.currentTurn = 1;
    this.ui.renderBoard(this.board);
    this.ui.updateStatus("↺ Move undone — Your Turn!", "human");
    this.ui.setHoverColumn(3, true);
    this.ui.clearHistory();
    this.moveHistory.forEach((m, idx) => {
      this.ui.addHistory(idx + 1, m.player, m.col);
    });
  }

  handleGameOver(winner, coords) {
    this.isGameOver = true;
    this.isBusy = false;

    if (winner === 1) {
      this.scores.human += 1;
      this.ui.updateScores(this.scores.human, this.scores.ai);
      this.ui.updateStatus("VICTORY! You defeated the AI!", "win");
      Sound.playWin();
      this.ui.renderBoard(this.board, coords);
      if (this.robot) {
        this.robot.say("human_wins", "sad");
        setTimeout(() => {
          this.robot.playVictoryVideo(1, Sound.enabled);
        }, 700);
      }
    } else if (winner === 2) {
      this.scores.ai += 1;
      this.ui.updateScores(this.scores.human, this.scores.ai);
      this.ui.updateStatus("DEFEAT! AI wins this match.", "ai");
      this.ui.renderBoard(this.board, coords);
      if (this.robot) {
        this.robot.say("ai_wins", "celebrating");
        setTimeout(() => {
          this.robot.playVictoryVideo(2, Sound.enabled);
        }, 700);
      }
    } else {
      this.scores.draws += 1;
      this.ui.updateStatus("DRAW GAME! Grid is completely full.", "info");
      Sound.playDraw();
      if (this.robot) {
        this.robot.say("draw", "thinking");
      }
    }

    StorageManager.saveScores(this.scores);
  }

  checkWin(player) {
    // Horizontal
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 4; c++) {
        if ([0, 1, 2, 3].every(i => this.board[r][c + i] === player)) {
          return { won: true, coords: [0, 1, 2, 3].map(i => [r, c + i]) };
        }
      }
    }
    // Vertical
    for (let c = 0; c < 7; c++) {
      for (let r = 0; r < 3; r++) {
        if ([0, 1, 2, 3].every(i => this.board[r + i][c] === player)) {
          return { won: true, coords: [0, 1, 2, 3].map(i => [r + i, c]) };
        }
      }
    }
    // Positive Diagonal (/)
    for (let r = 3; r < 6; r++) {
      for (let c = 0; c < 4; c++) {
        if ([0, 1, 2, 3].every(i => this.board[r - i][c + i] === player)) {
          return { won: true, coords: [0, 1, 2, 3].map(i => [r - i, c + i]) };
        }
      }
    }
    // Negative Diagonal (\)
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 4; c++) {
        if ([0, 1, 2, 3].every(i => this.board[r + i][c + i] === player)) {
          return { won: true, coords: [0, 1, 2, 3].map(i => [r + i, c + i]) };
        }
      }
    }
    return { won: false, coords: null };
  }

  isBoardFull() {
    return this.board[0].every(cell => cell !== 0);
  }
}
