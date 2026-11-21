/**
 * Connect Four AI - Master Application Entry Point
 */

import { PyodideManager } from './pyodide-manager.js';
import { GameUI } from './game-ui.js';
import { GameController } from './game-controller.js';
import { RobotAgent } from './robot-agent.js';
import { setupNavigation } from './navigation.js';
import { AILabManager } from './ai-lab.js';
import { AnalyticsManager } from './analytics.js';
import { StorageManager } from './storage.js';

document.addEventListener("DOMContentLoaded", async () => {
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingStatusText = document.getElementById("loadingStatusText");

  // 1. Initialize UI & Subsystems
  const ui = new GameUI();
  const robot = new RobotAgent();
  const controller = new GameController(ui, robot);
  const lab = new AILabManager();
  const analytics = new AnalyticsManager();

  setupNavigation((sectionId) => {
    if (sectionId === 'ai-lab') {
      lab.generateAndRenderTree(controller.board);
    } else if (sectionId === 'analytics') {
      analytics.updateKPIs();
    }
  });

  // 2. Settings Segmented Controls
  const setupSegmentedGroup = (containerId, settingKey, onChange) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    const currentVal = controller.settings[settingKey];
    const buttons = container.querySelectorAll(".seg-btn");
    buttons.forEach(btn => {
      if (btn.dataset.value === currentVal) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
      btn.addEventListener("click", () => {
        buttons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const val = btn.dataset.value;
        controller.settings[settingKey] = val;
        StorageManager.saveSettings(controller.settings);
        if (settingKey === "algorithm") {
          const algoLabel = val === "alpha_beta" ? "Alpha-Beta Pruning" : "Minimax";
          const elAlgo = document.getElementById("telemAlgo");
          if (elAlgo) elAlgo.textContent = algoLabel;
        }
        if (onChange) onChange(val);
      });
    });
  };

  setupSegmentedGroup("segFirstMove", "firstMove", () => controller.startNewGame());
  setupSegmentedGroup("segAlgorithm", "algorithm");
  setupSegmentedGroup("segDifficulty", "difficulty");

  // 3. Action Buttons
  const btnNewGame = document.getElementById("btnNewGame");
  const btnUndo = document.getElementById("btnUndo");
  const btnHint = document.getElementById("btnHint");
  const btnRestart = document.getElementById("btnRestart");

  if (btnNewGame) btnNewGame.addEventListener("click", () => controller.startNewGame());
  if (btnUndo) btnUndo.addEventListener("click", () => controller.undoMove());
  if (btnHint) btnHint.addEventListener("click", () => controller.requestHint());
  if (btnRestart) btnRestart.addEventListener("click", () => controller.startNewGame());

  // 4. Keyboard Shortcuts
  window.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
    const key = e.key.toUpperCase();
    if (key >= '1' && key <= '7') {
      controller.handleHumanMove(parseInt(key, 10) - 1);
    } else if (key === 'N') {
      controller.startNewGame();
    } else if (key === 'U') {
      controller.undoMove();
    } else if (key === 'H') {
      controller.requestHint();
    }
  });

  // 5. Initialize Pyodide WebAssembly AI Engine
  try {
    await PyodideManager.initialize((msg) => {
      if (loadingStatusText) loadingStatusText.textContent = msg;
    });

    // Dismiss Loading Screen
    setTimeout(() => {
      if (loadingOverlay) {
        loadingOverlay.classList.remove("active");
      }
      controller.startNewGame();
    }, 600);
  } catch (err) {
    if (loadingStatusText) {
      loadingStatusText.textContent = `Initialization failed. Check network or reload: ${err.message}`;
    }
    console.error("Pyodide startup failure:", err);
  }
});
