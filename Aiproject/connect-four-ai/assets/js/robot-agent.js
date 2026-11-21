/**
 * Interactive Robot Opponent Agent & Victory Video Manager
 * Features:
 * - Animated canvas robot avatar with live gaze tracking & situational expressions
 * - Context-aware witty speech bubble dialogue system
 * - Seamless victory video player swap inside the Opponent card
 */

const DIALOGUE = {
  game_start_human: [
    "You get the first drop! Don't be shy.",
    "Your turn first. Let's see your grand opening.",
    "Red goes first! Make it count.",
    "A fresh grid awaits! Show me what you've got.",
    "The board is clean. Your move, human friend!"
  ],
  game_start_ai: [
    "I get to move first! Allow me to demonstrate.",
    "Computer starts! Watch and learn.",
    "Yellow goes first! Securing my favorite column.",
    "Starting up my algorithms. Beep boop, here I go!",
    "First move claimed! The center is calling my name."
  ],
  thinking_easy: [
    "Depth 1 search: glancing at the immediate horizon.",
    "Quick lookahead. Keeping my gears in low gear!",
    "One move ahead is all I need right now."
  ],
  thinking_medium: [
    "Searching 3 moves ahead. Weighing my options!",
    "Calculating your counter-moves... interesting.",
    "Analyzing board windows... defense or attack?",
    "Foreseeing the next 3 plies in silicon clarity."
  ],
  thinking_hard: [
    "Calculating 5 moves ahead. Please hold your breath!",
    "Hard mode active! Exploring thousands of branch realities.",
    "Searching depth 5! My cooling fans are spinning.",
    "Consulting deep heuristics. No mistakes allowed."
  ],
  human_center: [
    "Ah, grabbing column 4! A respectable tactical choice.",
    "Control of the center. Classic opening principle!",
    "Straight down the middle! I see your strategy."
  ],
  human_edge: [
    "Playing the edge columns? Playing it safe, huh?",
    "A flank move! Leaving the center wide open for me.",
    "Column 1? Boldly unconventional, human."
  ],
  human_threat: [
    "Whoa! That's three in a row. You think I didn't see that?",
    "Threat detected! My threat-evaluator is blinking red.",
    "Sneaky line! I must deploy defensive countermeasures."
  ],
  ai_blocked: [
    "Blocked your little plan right there!",
    "Denied! You didn't think I'd let that slip, did you?",
    "Shields up! Four-in-a-row averted."
  ],
  ai_wins: [
    "Checkmate! (Or rather, Connect Four!) Victory is mine!",
    "My algorithms predicted this outcome 3 turns ago!",
    "Good game! My heuristics proved insurmountable today.",
    "Beep boop! Pure mathematical elegance."
  ],
  human_wins: [
    "What?! You found the winning line?! Incredible play!",
    "My circuits are humbled. You outplayed my search tree!",
    "A brilliant tactical victory, human! I salute you.",
    "Gears grinding... You actually beat me fair and square!"
  ],
  draw: [
    "A complete deadlock! A 42-move stalemate.",
    "Grid is full! Perfect defensive parity from both of us.",
    "A draw! Neither silicon nor carbon yields."
  ],
  undo: [
    "Rewinding the timeline? I won't tell anyone!",
    "A tactical mulligan! Second chances granted.",
    "Stepping back in time. Let's see your alternative."
  ],
  hint: [
    "Need a little assistance? Here is what I would do.",
    "A friendly tip from your silicon opponent!",
    "Consulting my Alpha-Beta engine for you... Look there!"
  ],
  idle: [
    "Still contemplating? Take your time, human.",
    "My processor is idling at a cool 40°C.",
    "Whenever you are ready! No rush at all."
  ]
};

const COMPUTER_VIDEOS = [
  "videos/computer_wins/win_1.mp4",
  "videos/computer_wins/win_3.mp4",
  "videos/computer_wins/win_7.mp4",
  "videos/computer_wins/win_8.mp4",
  "videos/computer_wins/win_9.mp4",
  "videos/computer_wins/win_10.mp4",
  "videos/computer_wins/win_11.mp4",
  "videos/computer_wins/win_12.mp4",
  "videos/computer_wins/win_13.mp4",
  "videos/computer_wins/win_14.mp4",
  "videos/computer_wins/win_15.mp4",
  "videos/computer_wins/win_16.mp4",
  "videos/computer_wins/win_17.mp4",
  "videos/computer_wins/win_18.mp4"
];

const HUMAN_VIDEOS = [
  "videos/human_wins/win_1.mp4",
  "videos/human_wins/win_2.mp4",
  "videos/human_wins/win_3.mp4",
  "videos/human_wins/win_4.mp4",
  "videos/human_wins/win_5.mp4",
  "videos/human_wins/win_6.mp4",
  "videos/human_wins/win_7.mp4",
  "videos/human_wins/win_8.mp4"
];

export class RobotAgent {
  constructor() {
    this.canvas = document.getElementById("robotAvatarCanvas");
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
    this.bubbleText = document.getElementById("robotBubbleText");
    this.bubbleContainer = document.getElementById("robotBubble");
    this.robotCardContent = document.getElementById("robotCardContent");
    this.videoContainer = document.getElementById("robotVideoContainer");
    this.videoEl = document.getElementById("victoryVideo");
    this.btnVideoSkip = document.getElementById("btnVideoSkip");
    this.btnVideoPause = document.getElementById("btnVideoPause");
    this.videoTimeEl = document.getElementById("videoTimeDisplay");

    // Avatar state
    this.expression = "happy"; // happy, thinking, smug, surprised, sad, celebrating
    this.targetGazeX = 0; // -1 (left) to 1 (right)
    this.currentGazeX = 0;
    this.isBlinking = false;
    this.blinkTimer = null;
    this.animFrameId = null;
    this.speechEnabled = true;
    this.lastSpeechCategory = null;
    this.lastVideoPlayed = null;

    this._initAvatar();
    this._initVideoControls();
    this.say("game_start_human", "happy");
  }

  _initAvatar() {
    if (!this.canvas) return;

    // Start render loop
    const render = () => {
      this._updatePhysics();
      this._drawAvatar();
      this.animFrameId = requestAnimationFrame(render);
    };
    this.animFrameId = requestAnimationFrame(render);

    // Natural blinking loop
    const scheduleBlink = () => {
      const delay = 2500 + Math.random() * 3500;
      this.blinkTimer = setTimeout(() => {
        this.isBlinking = true;
        setTimeout(() => {
          this.isBlinking = false;
          scheduleBlink();
        }, 160);
      }, delay);
    };
    scheduleBlink();
  }

  _updatePhysics() {
    // Smooth eye interpolation towards target gaze
    this.currentGazeX += (this.targetGazeX - this.currentGazeX) * 0.15;
  }

  setGazeByColumn(col) {
    if (col === null || col === undefined) {
      this.targetGazeX = 0;
    } else {
      // Map col (0 to 6) to gaze (-1.0 to +1.0)
      this.targetGazeX = (col - 3) / 3.0;
    }
  }

  setExpression(expr) {
    this.expression = expr;
  }

  say(category, expression = "happy") {
    if (!this.speechEnabled) return;
    this.setExpression(expression);

    const lines = DIALOGUE[category] || DIALOGUE.idle;
    // Pick random line different from last
    let line = lines[Math.floor(Math.random() * lines.length)];
    if (lines.length > 1 && line === this.lastSpeechCategory) {
      line = lines[(lines.indexOf(line) + 1) % lines.length];
    }
    this.lastSpeechCategory = line;

    if (this.bubbleText) {
      this.bubbleText.style.opacity = "0";
      setTimeout(() => {
        this.bubbleText.textContent = line;
        this.bubbleText.style.opacity = "1";
      }, 120);
    }
  }

  _drawAvatar() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2 + 6;

    // 1. Antenna
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx, cy - 36);
    ctx.lineTo(cx, cy - 50);
    ctx.stroke();

    // Antenna LED
    ctx.beginPath();
    ctx.arc(cx, cy - 52, 6, 0, Math.PI * 2);
    if (this.expression === "thinking") {
      ctx.fillStyle = "#FFD21F";
      ctx.shadowColor = "#FFD21F";
      ctx.shadowBlur = 12;
    } else if (this.expression === "celebrating" || this.expression === "smug") {
      ctx.fillStyle = "#00D6A0";
      ctx.shadowColor = "#00D6A0";
      ctx.shadowBlur = 10;
    } else if (this.expression === "sad") {
      ctx.fillStyle = "#FF304F";
      ctx.shadowColor = "#FF304F";
      ctx.shadowBlur = 8;
    } else {
      ctx.fillStyle = "#287BFF";
      ctx.shadowColor = "#287BFF";
      ctx.shadowBlur = 8;
    }
    ctx.fill();
    ctx.shadowBlur = 0; // reset

    // 2. Ear Bolts
    ctx.fillStyle = "#334155";
    ctx.fillRect(cx - 52, cy - 14, 8, 20);
    ctx.fillRect(cx + 44, cy - 14, 8, 20);

    // 3. Robot Head Chassis
    const headGrad = ctx.createLinearGradient(cx - 44, cy - 36, cx + 44, cy + 34);
    headGrad.addColorStop(0, "#1e293b");
    headGrad.addColorStop(1, "#0f172a");

    ctx.fillStyle = headGrad;
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 2.5;

    ctx.beginPath();
    ctx.roundRect(cx - 44, cy - 36, 88, 68, [18]);
    ctx.fill();
    ctx.stroke();

    // 4. Digital Visor Screen
    ctx.fillStyle = "#030712";
    ctx.beginPath();
    ctx.roundRect(cx - 36, cy - 26, 72, 38, [10]);
    ctx.fill();

    // Visor subtle grid scanline
    ctx.strokeStyle = "rgba(40, 123, 255, 0.12)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx - 36, cy - 7);
    ctx.lineTo(cx + 36, cy - 7);
    ctx.stroke();

    // 5. Eyes with Gaze Tracking
    const eyeOffsetX = this.currentGazeX * 5.5;
    const eyeBaseY = cy - 7;
    const leftEyeX = cx - 16 + eyeOffsetX;
    const rightEyeX = cx + 16 + eyeOffsetX;

    if (this.isBlinking) {
      // Eyelids closed (horizontal slits)
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(leftEyeX - 8, eyeBaseY);
      ctx.lineTo(leftEyeX + 8, eyeBaseY);
      ctx.moveTo(rightEyeX - 8, eyeBaseY);
      ctx.lineTo(rightEyeX + 8, eyeBaseY);
      ctx.stroke();
    } else {
      // Eye Glow Color
      let eyeColor = "#38bdf8";
      if (this.expression === "thinking") eyeColor = "#FFD21F";
      else if (this.expression === "smug") eyeColor = "#00D6A0";
      else if (this.expression === "sad") eyeColor = "#f43f5e";
      else if (this.expression === "celebrating") eyeColor = "#a855f7";

      ctx.fillStyle = eyeColor;
      ctx.shadowColor = eyeColor;
      ctx.shadowBlur = 8;

      if (this.expression === "surprised") {
        // Wide circular eyes
        ctx.beginPath();
        ctx.arc(leftEyeX, eyeBaseY, 7.5, 0, Math.PI * 2);
        ctx.arc(rightEyeX, eyeBaseY, 7.5, 0, Math.PI * 2);
        ctx.fill();
      } else if (this.expression === "smug") {
        // Confident squint
        ctx.beginPath();
        ctx.arc(leftEyeX, eyeBaseY + 1, 6.5, Math.PI * 0.15, Math.PI * 0.85);
        ctx.arc(rightEyeX, eyeBaseY + 1, 6.5, Math.PI * 0.15, Math.PI * 0.85);
        ctx.fill();
      } else {
        // Standard friendly oval eyes
        ctx.beginPath();
        ctx.ellipse(leftEyeX, eyeBaseY, 5.5, 7, 0, 0, Math.PI * 2);
        ctx.ellipse(rightEyeX, eyeBaseY, 5.5, 7, 0, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }

    // 6. Mouth / Expression indicator
    ctx.strokeStyle = "#64748b";
    ctx.lineWidth = 2;
    ctx.beginPath();

    if (this.expression === "happy" || this.expression === "celebrating") {
      ctx.arc(cx, cy + 18, 9, 0.1 * Math.PI, 0.9 * Math.PI);
    } else if (this.expression === "smug") {
      ctx.arc(cx + 3, cy + 17, 8, 0.1 * Math.PI, 0.7 * Math.PI);
    } else if (this.expression === "sad") {
      ctx.arc(cx, cy + 24, 8, 1.1 * Math.PI, 1.9 * Math.PI);
    } else if (this.expression === "surprised") {
      ctx.arc(cx, cy + 19, 4, 0, Math.PI * 2);
    } else {
      // Neutral line
      ctx.moveTo(cx - 7, cy + 19);
      ctx.lineTo(cx + 7, cy + 19);
    }
    ctx.stroke();
  }

  // --------------------------------------------------------------------------
  // Victory Video Player Management
  // --------------------------------------------------------------------------
  _initVideoControls() {
    if (this.btnVideoSkip) {
      this.btnVideoSkip.addEventListener("click", () => this.stopVictoryVideo());
    }
    if (this.btnVideoPause) {
      this.btnVideoPause.addEventListener("click", () => {
        if (!this.videoEl) return;
        if (this.videoEl.paused) {
          this.videoEl.play();
          this.btnVideoPause.textContent = "⏸ Pause";
        } else {
          this.videoEl.pause();
          this.btnVideoPause.textContent = "▶ Play";
        }
      });
    }
    if (this.videoEl) {
      this.videoEl.addEventListener("timeupdate", () => {
        if (!this.videoTimeEl) return;
        const cur = Math.floor(this.videoEl.currentTime || 0);
        const dur = Math.floor(this.videoEl.duration || 0);
        const fmt = (s) => `0:${s < 10 ? '0' : ''}${s}`;
        this.videoTimeEl.textContent = `${fmt(cur)} / ${fmt(dur)}`;
      });
      this.videoEl.addEventListener("ended", () => {
        this.stopVictoryVideo();
      });
    }
  }

  playVictoryVideo(winner, isSoundEnabled = true) {
    if (!this.videoContainer || !this.videoEl) return;

    const playlist = winner === 1 ? HUMAN_VIDEOS : COMPUTER_VIDEOS;
    if (!playlist || playlist.length === 0) return;

    // Pick one video without immediate repeat
    let pick = playlist[Math.floor(Math.random() * playlist.length)];
    if (playlist.length > 1 && pick === this.lastVideoPlayed) {
      pick = playlist[(playlist.indexOf(pick) + 1) % playlist.length];
    }
    this.lastVideoPlayed = pick;

    // Hide avatar & bubble, show video container
    if (this.robotCardContent) this.robotCardContent.style.display = "none";
    this.videoContainer.style.display = "flex";

    this.videoEl.src = pick;
    this.videoEl.muted = !isSoundEnabled;
    this.videoEl.play().catch(e => console.warn("Video autoplay prevented:", e));
    if (this.btnVideoPause) this.btnVideoPause.textContent = "⏸ Pause";
  }

  stopVictoryVideo() {
    if (!this.videoContainer || this.videoContainer.style.display === "none") return;

    if (this.videoEl) {
      this.videoEl.pause();
      this.videoEl.removeAttribute("src");
      this.videoEl.load();
    }

    this.videoContainer.style.display = "none";
    if (this.robotCardContent) this.robotCardContent.style.display = "flex";
  }
}
