/**
 * AI Lab Interactive Educational Explorer for Connect Four AI
 * Renders visual search trees, node cards, and step-by-step Alpha-Beta pruning walk-throughs.
 */

import { PyodideManager } from './pyodide-manager.js';

export class AILabManager {
  constructor() {
    this.container = document.getElementById("treeCanvasContainer");
    this.algoSelect = document.getElementById("labAlgoSelect");
    this.depthSelect = document.getElementById("labDepthSelect");
    this.btnRun = document.getElementById("btnRunLabTrace");
    this.btnStepNext = document.getElementById("btnStepNext");
    this.btnStepPrev = document.getElementById("btnStepPrev");
    this.btnAutoPlay = document.getElementById("btnAutoPlay");
    this.btnReset = document.getElementById("btnResetLab");
    this.stepCounterEl = document.getElementById("labStepCounter");
    this.nodeDetailsEl = document.getElementById("labNodeDetails");

    this.currentTraceData = null;
    this.steps = [];
    this.currentStepIdx = 0;
    this.autoPlayInterval = null;

    this._bindEvents();
  }

  _bindEvents() {
    if (this.btnRun) {
      this.btnRun.addEventListener("click", () => this.generateAndRenderTree());
    }
    if (this.btnStepNext) {
      this.btnStepNext.addEventListener("click", () => this.stepNext());
    }
    if (this.btnStepPrev) {
      this.btnStepPrev.addEventListener("click", () => this.stepPrev());
    }
    if (this.btnAutoPlay) {
      this.btnAutoPlay.addEventListener("click", () => this.toggleAutoPlay());
    }
    if (this.btnReset) {
      this.btnReset.addEventListener("click", () => this.resetPlayback());
    }
  }

  async generateAndRenderTree(board = null) {
    if (!PyodideManager.isReady) {
      alert("AI Engine is still initializing WebAssembly. Please wait a moment.");
      return;
    }

    const algo = this.algoSelect ? this.algoSelect.value : "alpha_beta";
    const depth = parseInt(this.depthSelect ? this.depthSelect.value : "2", 10);
    
    // Default sample board if none provided (early opening position)
    const testBoard = board || [
      [0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 1, 0, 0, 0],
      [0, 0, 2, 1, 2, 0, 0]
    ];

    if (this.container) {
      this.container.innerHTML = '<div style="color:var(--text-secondary); text-align:center; padding: 60px;">Computing game tree trace from Python AI Engine...</div>';
    }

    try {
      const traceResult = await PyodideManager.getTreeTrace(testBoard, algo, depth, 2);
      this.currentTraceData = traceResult;
      this._flattenSteps(traceResult.tree);
      this.resetPlayback();
      this.renderCurrentState();
    } catch (e) {
      console.error("[Lab Trace Error]", e);
      if (this.container) {
        this.container.innerHTML = `<div style="color:var(--danger); text-align:center; padding: 40px;">Trace Error: ${e.message}</div>`;
      }
    }
  }

  _flattenSteps(root) {
    this.steps = [];
    const traverse = (node, path) => {
      this.steps.push({ node, path: [...path, node] });
      if (node.children) {
        node.children.forEach(child => traverse(child, [...path, node]));
      }
    };
    traverse(root, []);
  }

  stepNext() {
    if (this.currentStepIdx < this.steps.length - 1) {
      this.currentStepIdx++;
      this.renderCurrentState();
    } else if (this.autoPlayInterval) {
      this.toggleAutoPlay();
    }
  }

  stepPrev() {
    if (this.currentStepIdx > 0) {
      this.currentStepIdx--;
      this.renderCurrentState();
    }
  }

  toggleAutoPlay() {
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
      if (this.btnAutoPlay) this.btnAutoPlay.textContent = "▶ Auto Play";
    } else {
      if (this.btnAutoPlay) this.btnAutoPlay.textContent = "⏸ Pause";
      this.autoPlayInterval = setInterval(() => {
        if (this.currentStepIdx < this.steps.length - 1) {
          this.stepNext();
        } else {
          this.toggleAutoPlay();
        }
      }, 700);
    }
  }

  resetPlayback() {
    if (this.autoPlayInterval) this.toggleAutoPlay();
    this.currentStepIdx = 0;
    this.renderCurrentState();
  }

  renderCurrentState() {
    if (!this.container || !this.currentTraceData) return;

    if (this.stepCounterEl) {
      this.stepCounterEl.textContent = `Step ${this.currentStepIdx + 1} / ${this.steps.length}`;
    }

    const currentStep = this.steps[this.currentStepIdx];
    if (this.nodeDetailsEl && currentStep) {
      const n = currentStep.node;
      this.nodeDetailsEl.innerHTML = `
        <div><strong>Node Type:</strong> <span style="color:var(--primary-blue)">${n.type || 'ROOT'}</span></div>
        <div><strong>Column Played:</strong> ${n.col !== null ? `Col ${n.col + 1}` : 'Root'}</div>
        <div><strong>Score:</strong> ${n.score !== null ? n.score : 'Evaluating...'}</div>
        ${n.alpha_in !== undefined ? `<div><strong>Alpha:</strong> ${n.alpha_in} | <strong>Beta:</strong> ${n.beta_in}</div>` : ''}
        ${n.pruned ? `<div style="color:var(--danger)"><strong>PRUNED:</strong> ${n.reason || 'β <= α'}</div>` : ''}
      `;
    }

    // Render Tree SVG / Visual Representation
    this.container.innerHTML = "";
    const wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    wrapper.style.flexDirection = "column";
    wrapper.style.alignItems = "center";
    wrapper.style.gap = "28px";
    wrapper.style.padding = "20px";

    // Level 0: Root
    const rootRow = document.createElement("div");
    rootRow.style.display = "flex";
    rootRow.style.justifyContent = "center";
    rootRow.innerHTML = `<div class="game-card" style="padding: 10px 18px; border-color: var(--primary-blue); box-shadow: 0 0 14px var(--primary-blue-glow);">
      <strong>ROOT (AI Turn)</strong>
    </div>`;
    wrapper.appendChild(rootRow);

    // Level 1: First Ply (Cols 0-6)
    const ply1Row = document.createElement("div");
    ply1Row.style.display = "flex";
    ply1Row.style.justifyContent = "center";
    ply1Row.style.flexWrap = "wrap";
    ply1Row.style.gap = "12px";

    const children = this.currentTraceData.tree.children || [];
    children.forEach((child, idx) => {
      const isPruned = child.pruned;
      const isVisited = this.steps.slice(0, this.currentStepIdx + 1).some(s => s.node === child);
      const isCurrent = currentStep && currentStep.node === child;

      const card = document.createElement("div");
      card.className = "game-card";
      card.style.padding = "8px 12px";
      card.style.fontSize = "0.78rem";
      card.style.minWidth = "90px";
      card.style.textAlign = "center";
      card.style.cursor = "pointer";

      if (isCurrent) {
        card.style.borderColor = "var(--success)";
        card.style.boxShadow = "0 0 14px var(--success-glow)";
      } else if (isPruned) {
        card.style.borderColor = "var(--danger)";
        card.style.opacity = "0.6";
        card.style.textDecoration = "line-through";
      } else if (isVisited) {
        card.style.borderColor = "var(--purple)";
      }

      card.innerHTML = `
        <div style="font-weight:700;">Col ${child.col + 1}</div>
        <div style="color:var(--text-secondary);">${child.type || 'PLY'}</div>
        <div style="font-family:var(--font-mono); font-weight:700; color:${child.score > 0 ? 'var(--success)' : 'var(--text-primary)'}">
          ${child.score !== null ? child.score : (isPruned ? 'CUTOFF' : '...')}
        </div>
      `;

      card.addEventListener("click", () => {
        const foundIdx = this.steps.findIndex(s => s.node === child);
        if (foundIdx !== -1) {
          this.currentStepIdx = foundIdx;
          this.renderCurrentState();
        }
      });

      ply1Row.appendChild(card);
    });

    wrapper.appendChild(ply1Row);
    this.container.appendChild(wrapper);
  }
}
