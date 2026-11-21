/**
 * Pyodide Manager for Connect Four AI
 * Orchestrates WebAssembly Python execution, module mounting, and AI queries.
 */

function safeJsonParse(rawStr) {
  // Coerce Pyodide proxy objects or non-strings to native JS string first
  if (rawStr === null || rawStr === undefined) return null;
  const str = (typeof rawStr === 'string') ? rawStr : String(rawStr);
  // Sanitize invalid JSON tokens that Python may emit
  const sanitized = str
    .replace(/:\s*-Infinity/g, ': -999999')
    .replace(/:\s*Infinity/g, ': 999999')
    .replace(/:\s*NaN/g, ': null')
    .replace(/\b-Infinity\b/g, '-999999')
    .replace(/\bInfinity\b/g, '999999')
    .replace(/\bNaN\b/g, 'null');
  try {
    return JSON.parse(sanitized);
  } catch (e) {
    console.error('[safeJsonParse] Failed to parse:', sanitized.slice(0, 400), e);
    throw new Error(`JSON parse failed: ${e.message} | raw(400): ${sanitized.slice(0, 400)}`);
  }
}

class PyodideBridge {
  constructor() {
    this.pyodide = null;
    this.isReady = false;
    this.onStatusChange = null;
  }

  updateStatus(msg) {
    if (this.onStatusChange) {
      this.onStatusChange(msg);
    }
    console.log(`[Pyodide] ${msg}`);
  }

  async initialize(statusCallback) {
    this.onStatusChange = statusCallback;
    this.updateStatus("Initializing WebAssembly AI Runtime...");

    try {
      if (typeof loadPyodide === "undefined") {
        throw new Error("Pyodide script not loaded in window.");
      }

      this.pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/"
      });

      this.updateStatus("Mounting Python AI Engine modules...");

      // Fetch Python modules and write to Pyodide FS
      const modules = ['board', 'evaluation', 'minimax', 'alpha_beta', 'game_logic', 'ai_engine'];
      const ts = Date.now();
      
      for (const mod of modules) {
        try {
          const res = await fetch(`python/${mod}.py?v=${ts}`);
          if (res.ok) {
            const code = await res.text();
            // Write to both / and /home/pyodide to cover all sys.path variants
            try { this.pyodide.FS.writeFile(`/${mod}.py`, code); } catch(_) {}
            try { this.pyodide.FS.writeFile(`/home/pyodide/${mod}.py`, code); } catch(_) {}
          } else {
            console.warn(`[Pyodide] fetch python/${mod}.py returned ${res.status}`);
          }
        } catch (fetchErr) {
          console.warn(`[Pyodide] Could not fetch python/${mod}.py:`, fetchErr);
        }
      }

      this.updateStatus("Compiling Minimax & Alpha-Beta in WebAssembly...");
      
      // Initialize Python environment with sys.path setup and sanity tests
      const initResult = await this.pyodide.runPythonAsync(`
import sys, json

# Ensure all module search paths include where we wrote the files
for _p in ['/', '/home/pyodide']:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Force fresh import by clearing any stale cached modules
_mods = ['board', 'evaluation', 'minimax', 'alpha_beta', 'game_logic', 'ai_engine']
for _m in _mods:
    sys.modules.pop(_m, None)

import ai_engine, game_logic

# Sanity test: both algorithms on empty board at depth=1
_board = [[0]*7 for _ in range(6)]
try:
    _mm = json.loads(ai_engine.get_ai_move(_board, 'minimax', 1, 2))
    _ab = json.loads(ai_engine.get_ai_move(_board, 'alpha_beta', 1, 2))
    assert isinstance(_mm['selected_column'], int), 'minimax col not int'
    assert isinstance(_ab['selected_column'], int), 'ab col not int'
    _status = f"OK|mm:{_mm['selected_column']}|ab:{_ab['selected_column']}|pruned:{_ab['pruned_nodes']}"
except Exception as _ex:
    import traceback
    _status = f"FAIL:{_ex}|{traceback.format_exc()}"
_status
`);

      const initStr = (typeof initResult === 'string') ? initResult : String(initResult);
      console.log('[Pyodide Engine] Init result:', initStr);
      
      if (initStr.startsWith('FAIL:')) {
        throw new Error(`Python engine self-test failed: ${initStr}`);
      }

      this.isReady = true;
      this.updateStatus("AI Engine Ready!");
      return true;
    } catch (err) {
      console.error("[Pyodide Engine Init Error]", err);
      this.updateStatus(`Engine Error: ${err.message}`);
      throw err;
    }
  }

  /**
   * Run a Python expression that calls ai_engine, wrapped in try/except.
   * Returns parsed JSON object. Throws Error with Python traceback on failure.
   */
  async _callPython(fnCall) {
    const pyCode = `
import json as _j, sys as _s, traceback as _tb
try:
    _r = ${fnCall}
except Exception as _e:
    _r = _j.dumps({"__pyerror__": True, "error": str(_e), "tb": _tb.format_exc()})
_r
`;
    const raw = await this.pyodide.runPythonAsync(pyCode);
    const str = (typeof raw === 'string') ? raw : String(raw);
    const parsed = safeJsonParse(str);
    if (parsed && parsed.__pyerror__) {
      throw new Error(`Python Error: ${parsed.error}\n${parsed.tb || ''}`);
    }
    return parsed;
  }

  async getAIMove(board, algorithm = 'alpha_beta', depth = 3, player = 2) {
    if (!this.isReady) throw new Error("Pyodide AI Engine not initialized.");
    const boardJson = JSON.stringify(JSON.stringify(board));
    return this._callPython(`ai_engine.get_ai_move(${boardJson}, "${algorithm}", ${depth}, ${player})`);
  }

  async getHint(board, algorithm = 'alpha_beta', depth = 3, player = 1) {
    if (!this.isReady) throw new Error("Pyodide AI Engine not initialized.");
    const boardJson = JSON.stringify(JSON.stringify(board));
    return this._callPython(`ai_engine.get_hint(${boardJson}, "${algorithm}", ${depth}, ${player})`);
  }

  async runBenchmark(board, depth = 3, player = 2) {
    if (!this.isReady) throw new Error("Pyodide AI Engine not initialized.");
    const boardJson = JSON.stringify(JSON.stringify(board));
    return this._callPython(`ai_engine.run_benchmark(${boardJson}, ${depth}, ${player})`);
  }

  async getTreeTrace(board, algorithm = 'alpha_beta', depth = 2, player = 2) {
    if (!this.isReady) throw new Error("Pyodide AI Engine not initialized.");
    const boardJson = JSON.stringify(JSON.stringify(board));
    return this._callPython(`ai_engine.get_tree_trace(${boardJson}, "${algorithm}", ${depth}, ${player})`);
  }
}

export const PyodideManager = new PyodideBridge();
