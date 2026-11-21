/**
 * Storage Manager for Connect Four AI
 * Handles LocalStorage persistence for themes, audio, scoreboards, and analytics.
 */

const STORAGE_KEYS = {
  THEME: 'c4_theme',
  SOUND: 'c4_sound',
  SCORES: 'c4_scores',
  SETTINGS: 'c4_settings',
  ANALYTICS: 'c4_analytics',
  HISTORY: 'c4_history'
};

export const StorageManager = {
  // Theme
  getTheme() {
    return localStorage.getItem(STORAGE_KEYS.THEME) || 'dark';
  },
  setTheme(theme) {
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  },

  // Sound
  getSound() {
    const val = localStorage.getItem(STORAGE_KEYS.SOUND);
    return val === null ? true : val === 'true';
  },
  setSound(enabled) {
    localStorage.setItem(STORAGE_KEYS.SOUND, String(enabled));
  },

  // Scoreboard
  getScores() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.SCORES);
      return data ? JSON.parse(data) : { human: 0, ai: 0, draws: 0 };
    } catch (e) {
      return { human: 0, ai: 0, draws: 0 };
    }
  },
  saveScores(scores) {
    localStorage.setItem(STORAGE_KEYS.SCORES, JSON.stringify(scores));
  },

  // Settings
  getSettings() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.SETTINGS);
      return data ? JSON.parse(data) : { firstMove: 'human', algorithm: 'alpha_beta', difficulty: 'medium' };
    } catch (e) {
      return { firstMove: 'human', algorithm: 'alpha_beta', difficulty: 'medium' };
    }
  },
  saveSettings(settings) {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
  },

  // Analytics Metrics
  getAnalytics() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ANALYTICS);
      return data ? JSON.parse(data) : {
        totalGames: 0,
        humanWins: 0,
        aiWins: 0,
        draws: 0,
        totalAIDecisions: 0,
        totalSearchTimeMs: 0,
        historyComparisons: []
      };
    } catch (e) {
      return { totalGames: 0, humanWins: 0, aiWins: 0, draws: 0, totalAIDecisions: 0, totalSearchTimeMs: 0, historyComparisons: [] };
    }
  },
  saveAnalytics(data) {
    localStorage.setItem(STORAGE_KEYS.ANALYTICS, JSON.stringify(data));
  },
  resetAnalytics() {
    localStorage.removeItem(STORAGE_KEYS.ANALYTICS);
    localStorage.removeItem(STORAGE_KEYS.SCORES);
  }
};
