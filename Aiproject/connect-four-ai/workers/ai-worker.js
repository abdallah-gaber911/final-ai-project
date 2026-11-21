/**
 * Web Worker for Off-Thread Connect Four AI Computation via Pyodide.
 * Keeps the main UI completely responsive at 60 FPS even on Depth 5 searches.
 */

/* global importScripts, loadPyodide */
let pyodide = null;
let isReady = false;

function safeJsonParse(rawStr) {
  if (typeof rawStr !== 'string') return rawStr;
  const sanitized = rawStr
    .replace(/:\s*-?Infinity/g, (match) => match.includes('-') ? ': -999999' : ': 999999')
    .replace(/:\s*NaN/g, ': null');
  return JSON.parse(sanitized);
}

self.onmessage = async (e) => {
  const { type, id, payload } = e.data;

  try {
    if (type === "INIT") {
      importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js");
      pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/"
      });

      // Write Python modules passed from main thread or fetch
      if (payload && payload.modules) {
        for (const [name, code] of Object.entries(payload.modules)) {
          pyodide.FS.writeFile(name, code);
        }
      }

      await pyodide.runPythonAsync(`
import sys
import json
import ai_engine
import game_logic
`);
      isReady = true;
      self.postMessage({ type: "INIT_DONE", id, success: true });
    }

    else if (type === "GET_MOVE") {
      const { board, algorithm, depth, player } = payload;
      const boardJson = JSON.stringify(board);
      const res = await pyodide.runPythonAsync(
        `ai_engine.get_ai_move(${JSON.stringify(boardJson)}, "${algorithm}", ${depth}, ${player})`
      );
      self.postMessage({ type: "MOVE_RESULT", id, success: true, data: safeJsonParse(res) });
    }

    else if (type === "BENCHMARK") {
      const { board, depth, player } = payload;
      const boardJson = JSON.stringify(board);
      const res = await pyodide.runPythonAsync(
        `ai_engine.run_benchmark(${JSON.stringify(boardJson)}, ${depth}, ${player})`
      );
      self.postMessage({ type: "BENCHMARK_RESULT", id, success: true, data: safeJsonParse(res) });
    }

    else if (type === "TREE_TRACE") {
      const { board, algorithm, depth, player } = payload;
      const boardJson = JSON.stringify(board);
      const res = await pyodide.runPythonAsync(
        `ai_engine.get_tree_trace(${JSON.stringify(boardJson)}, "${algorithm}", ${depth}, ${player})`
      );
      self.postMessage({ type: "TREE_TRACE_RESULT", id, success: true, data: safeJsonParse(res) });
    }
  } catch (err) {
    self.postMessage({ type: "ERROR", id, error: err.message });
  }
};
