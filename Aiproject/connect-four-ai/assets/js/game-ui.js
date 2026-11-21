/**
 * Game UI Renderer and Sound Synthesizer for Connect Four AI
 */

/* global confetti */

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  _initCtx() {
    if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playDrop() {
    if (!this.enabled) return;
    this._initCtx();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    const now = this.ctx.currentTime;
    osc.frequency.setValueAtTime(320, now);
    osc.frequency.exponentialRampToValueAtTime(110, now + 0.14);
    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.14);
  }

  playAIMove() {
    if (!this.enabled) return;
    this._initCtx();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    const now = this.ctx.currentTime;
    osc.frequency.setValueAtTime(440, now);
    osc.frequency.setValueAtTime(660, now + 0.08);
    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.18);
  }

  playWin() {
    if (!this.enabled) return;
    this._initCtx();
    if (!this.ctx) return;
    const notes = [392, 523, 659, 784];
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const now = this.ctx.currentTime + idx * 0.11;
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.28);
    });
  }

  playDraw() {
    if (!this.enabled) return;
    this._initCtx();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const now = this.ctx.currentTime;
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(220, now);
    osc.frequency.linearRampToValueAtTime(140, now + 0.3);
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  }
}

export const Sound = new SoundEngine();

export class GameUI {
  constructor() {
    this.boardEl = document.getElementById("boardColumns");
    this.hoverRowEl = document.getElementById("hoverRow");
    this.statusTextEl = document.getElementById("statusText");
    this.statusDotEl = document.getElementById("statusDot");
    this.humanWinsEl = document.getElementById("humanWins");
    this.aiWinsEl = document.getElementById("aiWins");
    this.historyListEl = document.getElementById("historyList");
    
    // Telemetry Elements
    this.telemetryAlgoEl = document.getElementById("telemAlgo");
    this.telemetryDepthEl = document.getElementById("telemDepth");
    this.telemetryNodesEl = document.getElementById("telemNodes");
    this.telemetryPrunedEl = document.getElementById("telemPruned");
    this.telemetryTimeEl = document.getElementById("telemTime");
    this.telemetryMoveEl = document.getElementById("telemMove");
    this.telemetryScoreEl = document.getElementById("telemScore");

    this.onColumnClick = null;
    this.onColumnHover = null;
    this._buildBoard();
  }

  _buildBoard() {
    this.boardEl.innerHTML = "";
    this.hoverRowEl.innerHTML = "";

    // Build 7 hover cells
    for (let c = 0; c < 7; c++) {
      const hoverCell = document.createElement("div");
      hoverCell.className = "hover-cell";
      hoverCell.dataset.col = c;
      const ghost = document.createElement("div");
      ghost.className = "ghost-coin";
      hoverCell.appendChild(ghost);

      hoverCell.addEventListener("mouseenter", () => {
        if (this.onColumnHover) this.onColumnHover(c);
      });
      hoverCell.addEventListener("click", () => {
        if (this.onColumnClick) this.onColumnClick(c);
      });

      this.hoverRowEl.appendChild(hoverCell);
    }

    // Build 7 columns of 6 slots
    for (let c = 0; c < 7; c++) {
      const colDiv = document.createElement("div");
      colDiv.className = "board-column";
      colDiv.dataset.col = c;

      for (let r = 0; r < 6; r++) {
        const slotDiv = document.createElement("div");
        slotDiv.className = "board-slot";
        slotDiv.dataset.row = r;
        slotDiv.dataset.col = c;
        colDiv.appendChild(slotDiv);
      }

      colDiv.addEventListener("mouseenter", () => {
        if (this.onColumnHover) this.onColumnHover(c);
      });
      colDiv.addEventListener("click", () => {
        if (this.onColumnClick) this.onColumnClick(c);
      });

      this.boardEl.appendChild(colDiv);
    }
  }

  setHoverColumn(col, isHumanTurn = true) {
    const cells = this.hoverRowEl.querySelectorAll(".hover-cell");
    cells.forEach((cell, idx) => {
      const ghost = cell.querySelector(".ghost-coin");
      if (idx === col && isHumanTurn) {
        cell.classList.add("active");
        ghost.style.background = isHumanTurn
          ? "radial-gradient(circle at 35% 35%, var(--human-highlight), var(--human-red))"
          : "radial-gradient(circle at 35% 35%, var(--ai-highlight), var(--ai-yellow))";
      } else {
        cell.classList.remove("active");
      }
    });
  }

  renderBoard(board, winningCoords = null) {
    for (let c = 0; c < 7; c++) {
      for (let r = 0; r < 6; r++) {
        const slot = this.boardEl.querySelector(`.board-slot[data-row="${r}"][data-col="${c}"]`);
        slot.innerHTML = "";

        const piece = board[r][c];
        if (piece !== 0) {
          const coin = document.createElement("div");
          coin.className = `coin ${piece === 1 ? 'human-piece' : 'ai-piece'}`;
          
          const innerRing = document.createElement("div");
          innerRing.className = "coin-inner-ring";
          coin.appendChild(innerRing);

          // Check if winning piece
          if (winningCoords && winningCoords.some(([wr, wc]) => wr === r && wc === c)) {
            coin.classList.add("winning-highlight");
          }

          slot.appendChild(coin);
        }
      }
    }
  }

  animateDrop(row, col, player, onComplete) {
    const slot = this.boardEl.querySelector(`.board-slot[data-row="${row}"][data-col="${col}"]`);
    slot.innerHTML = "";

    const coin = document.createElement("div");
    coin.className = `coin ${player === 1 ? 'human-piece' : 'ai-piece'}`;
    coin.style.animation = `dropToRow${row} 0.42s ease-in forwards`;

    const innerRing = document.createElement("div");
    innerRing.className = "coin-inner-ring";
    coin.appendChild(innerRing);

    slot.appendChild(coin);
    Sound.playDrop();

    setTimeout(() => {
      coin.style.animation = "";
      if (onComplete) onComplete();
    }, 440);
  }

  showHint(col) {
    const colEl = this.boardEl.querySelector(`.board-column[data-col="${col}"]`);
    if (colEl) {
      colEl.classList.add("hinted");
      setTimeout(() => {
        colEl.classList.remove("hinted");
      }, 2600);
    }
  }

  updateStatus(status, type = "info") {
    this.statusTextEl.textContent = status;
    
    this.statusDotEl.classList.remove("thinking-pulse");

    // Dot styling
    if (type === "human") {
      this.statusDotEl.style.background = "var(--human-red)";
      this.statusDotEl.style.boxShadow = "0 0 10px var(--human-red)";
    } else if (type === "ai") {
      this.statusDotEl.style.background = "var(--ai-yellow)";
      this.statusDotEl.style.boxShadow = "0 0 12px var(--ai-yellow)";
      this.statusDotEl.classList.add("thinking-pulse");
    } else if (type === "win") {
      this.statusDotEl.style.background = "var(--success)";
      this.statusDotEl.style.boxShadow = "0 0 16px var(--success)";
      if (typeof confetti === "function") {
        confetti({ particleCount: 110, spread: 80, origin: { y: 0.6 } });
      }
    } else if (type === "error") {
      this.statusDotEl.style.background = "var(--danger)";
      this.statusDotEl.style.boxShadow = "0 0 10px var(--danger)";
    } else {
      this.statusDotEl.style.background = "var(--text-secondary)";
      this.statusDotEl.style.boxShadow = "none";
    }
  }

  updateScores(humanWins, aiWins) {
    if (this.humanWinsEl) this.humanWinsEl.textContent = humanWins;
    if (this.aiWinsEl) this.aiWinsEl.textContent = aiWins;
  }

  updateTelemetry(metrics) {
    if (!metrics) return;
    if (this.telemetryAlgoEl) this.telemetryAlgoEl.textContent = metrics.algorithm_name || "-";
    if (this.telemetryDepthEl) this.telemetryDepthEl.textContent = metrics.search_depth ?? "-";
    if (this.telemetryNodesEl) this.telemetryNodesEl.textContent = (metrics.nodes_visited ?? 0).toLocaleString();
    if (this.telemetryPrunedEl) this.telemetryPrunedEl.textContent = (metrics.pruned_nodes ?? 0).toLocaleString();
    if (this.telemetryTimeEl) this.telemetryTimeEl.textContent = `${metrics.execution_time_ms ?? 0} ms`;
    if (this.telemetryMoveEl) this.telemetryMoveEl.textContent = metrics.selected_column !== null ? `Col ${metrics.selected_column + 1}` : "-";
    if (this.telemetryScoreEl) this.telemetryScoreEl.textContent = metrics.evaluation_score ?? "-";
  }

  addHistory(moveNum, player, col) {
    if (!this.historyListEl) return;
    const item = document.createElement("div");
    item.className = "history-item";
    const pName = player === 1 ? "You" : "AI";
    const pColor = player === 1 ? "var(--human-red)" : "var(--ai-yellow)";
    item.innerHTML = `
      <span>#${moveNum} <strong style="color:${pColor}">${pName}</strong></span>
      <span>Col ${col + 1}</span>
    `;
    this.historyListEl.prepend(item);
  }

  clearHistory() {
    if (this.historyListEl) this.historyListEl.innerHTML = "";
  }
}
