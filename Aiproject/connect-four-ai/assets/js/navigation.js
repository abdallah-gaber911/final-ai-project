/**
 * Navigation and Global Theme/Sound Controls for Connect Four AI
 */

import { StorageManager } from './storage.js';
import { Sound } from './game-ui.js';

export function setupNavigation(onSectionChange) {
  const navItems = document.querySelectorAll(".nav-item");
  const sections = document.querySelectorAll(".app-section");
  const themeToggle = document.getElementById("themeToggle");
  const soundToggle = document.getElementById("soundToggle");

  // Nav Tab Switching
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const targetSectionId = item.dataset.target;

      navItems.forEach(n => n.classList.remove("active"));
      item.classList.add("active");

      sections.forEach(s => {
        if (s.id === targetSectionId) {
          s.classList.add("active");
        } else {
          s.classList.remove("active");
        }
      });

      if (onSectionChange) onSectionChange(targetSectionId);
    });
  });

  // Brand Home Link
  const brandLink = document.getElementById("brandHomeLink");
  if (brandLink) {
    brandLink.addEventListener("click", () => {
      const homeBtn = document.querySelector('.nav-item[data-target="home-section"]');
      if (homeBtn) homeBtn.click();
    });
  }

  // Theme Toggle
  const currentTheme = StorageManager.getTheme();
  document.documentElement.setAttribute("data-theme", currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const active = document.documentElement.getAttribute("data-theme") || "dark";
      const next = active === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      StorageManager.setTheme(next);
    });
  }

  // Sound Toggle
  const soundEnabled = StorageManager.getSound();
  Sound.enabled = soundEnabled;

  if (soundToggle) {
    soundToggle.addEventListener("click", () => {
      Sound.enabled = !Sound.enabled;
      StorageManager.setSound(Sound.enabled);
      soundToggle.style.opacity = Sound.enabled ? "1" : "0.5";
    });
  }
}
