"""
Cheeky Robot Avatar widget for Connect 4.
Renders an interactive animated robot face that blinks, tracks cursor column,
and adapts facial expressions dynamically based on game events.
"""

import tkinter as tk
import random
from widgets import rounded_rect
try:
    from theme import font_spec, FONT_SIZES
except ImportError:
    from connect4.theme import font_spec, FONT_SIZES


class RobotAvatar(tk.Canvas):
    """Interactive canvas-drawn robot avatar with dynamic expressions and gaze tracking."""
    def __init__(self, master, width=220, height=105, theme=None):
        super().__init__(master, width=width, height=height, highlightthickness=0)
        self.canvas_w = width
        self.canvas_h = height
        self.theme = theme or {}

        # Expression states: 'neutral', 'thinking', 'smug', 'surprised', 'sad', 'happy'
        self.expression = "neutral"
        self.hover_col = None
        self.is_blinking = False
        self.thinking_dot_frame = 0

        # Timers
        self.blink_timer = None
        self.thinking_timer = None

        self.bind("<Configure>", self._on_resize)
        self._schedule_blink()
        self._draw()

    def _on_resize(self, event):
        self.canvas_w = event.width
        self.canvas_h = event.height
        self._draw()

    def set_theme(self, theme):
        self.theme = theme
        self._draw()

    def set_expression(self, expr):
        """Update face expression and redraw."""
        if expr in ["neutral", "thinking", "smug", "surprised", "sad", "happy"]:
            self.expression = expr
            if expr == "thinking":
                self._start_thinking_animation()
            else:
                self._stop_thinking_animation()
            self._draw()

    def set_hover_col(self, col):
        """Update gaze to follow the column the human is hovering over."""
        if col != self.hover_col:
            self.hover_col = col
            self._draw()

    def _schedule_blink(self):
        """Schedule the next spontaneous blink."""
        delay = random.randint(3200, 5500)
        self.blink_timer = self.after(delay, self._do_blink)

    def _do_blink(self):
        """Momentarily close eyes for realistic blinking."""
        if self.expression != "thinking":
            self.is_blinking = True
            self._draw()
            self.after(140, self._finish_blink)
        else:
            self._schedule_blink()

    def _finish_blink(self):
        self.is_blinking = False
        self._draw()
        self._schedule_blink()

    def _start_thinking_animation(self):
        if not self.thinking_timer:
            self._step_thinking()

    def _stop_thinking_animation(self):
        if self.thinking_timer:
            self.after_cancel(self.thinking_timer)
            self.thinking_timer = None

    def _step_thinking(self):
        if self.expression == "thinking":
            self.thinking_dot_frame = (self.thinking_dot_frame + 1) % 4
            self._draw()
            self.thinking_timer = self.after(350, self._step_thinking)

    def _draw(self):
        self.delete("all")
        t = self.theme
        w = max(self.canvas_w, 100)
        h = max(self.canvas_h, 80)

        card_bg = t.get("card_bg", "#1e293b")
        self.configure(bg=card_bg)

        cx = w / 2
        cy = h / 2 + 6

        # 1. Antenna
        ant_color = t.get("robot_antenna", "#64748b")
        self.create_line(cx, cy - 28, cx, cy - 42, fill=ant_color, width=3)
        bulb_color = t.get("robot_antenna_light", "#f43f5e")
        if self.expression == "thinking":
            bulb_color = t.get("cyan_accent", "#06b6d4")
        self.create_oval(cx - 5, cy - 47, cx + 5, cy - 37, fill=bulb_color, outline="")

        # 2. Side metallic ear bolts
        ear_color = t.get("robot_rim", "#475569")
        self.create_rectangle(cx - 48, cy - 10, cx - 42, cy + 10, fill=ear_color, outline="")
        self.create_rectangle(cx + 42, cy - 10, cx + 48, cy + 10, fill=ear_color, outline="")

        # 3. Outer Robot Head (rounded metal case)
        head_bg = t.get("robot_head", "#334155")
        head_rim = t.get("robot_rim", "#475569")
        rounded_rect(self, cx - 42, cy - 28, cx + 42, cy + 28, radius=12,
                     fill=head_bg, outline=head_rim, width=2)

        # 4. Inner Dark Display Screen
        screen_bg = t.get("cell_empty", "#070d19")
        rounded_rect(self, cx - 35, cy - 22, cx + 35, cy + 22, radius=8,
                     fill=screen_bg, outline="", width=0)

        # 5. Eyes
        eye_color = t.get("robot_eye_glow", "#38bdf8")
        pupil_color = t.get("robot_eye_pupil", "#0284c7")

        eye_y = cy - 6
        eye_dx = 15

        # Eye tracking offset (-3px to +3px based on col 0..6)
        gaze_x = 0
        gaze_y = 0
        if self.hover_col is not None:
            gaze_x = (self.hover_col - 3) * 1.2

        if self.expression == "thinking":
            gaze_y = -3

        if self.is_blinking:
            # Draw horizontal blink slits
            self.create_line(cx - eye_dx - 6, eye_y, cx - eye_dx + 6, eye_y, fill=eye_color, width=2)
            self.create_line(cx + eye_dx - 6, eye_y, cx + eye_dx + 6, eye_y, fill=eye_color, width=2)
        elif self.expression == "smug":
            # Curved ^ ^ confident eyes
            self.create_arc(cx - eye_dx - 7, eye_y - 6, cx - eye_dx + 7, eye_y + 4,
                            start=0, extent=180, style="arc", outline=eye_color, width=2)
            self.create_arc(cx + eye_dx - 7, eye_y - 6, cx + eye_dx + 7, eye_y + 4,
                            start=0, extent=180, style="arc", outline=eye_color, width=2)
        elif self.expression == "surprised":
            # Big wide round eyes
            for ex in [cx - eye_dx, cx + eye_dx]:
                self.create_oval(ex - 8, eye_y - 8, ex + 8, eye_y + 8, fill=eye_color, outline="")
                self.create_oval(ex - 3 + gaze_x, eye_y - 3 + gaze_y, ex + 3 + gaze_x, eye_y + 3 + gaze_y,
                                 fill=pupil_color, outline="")
        elif self.expression == "sad":
            # Drooping sad eyes
            for ex in [cx - eye_dx, cx + eye_dx]:
                self.create_oval(ex - 6, eye_y - 5, ex + 6, eye_y + 5, fill=eye_color, outline="")
            # Downward slanted brows
            self.create_line(cx - eye_dx - 6, eye_y - 8, cx - eye_dx + 6, eye_y - 5, fill=eye_color, width=2)
            self.create_line(cx + eye_dx - 6, eye_y - 5, cx + eye_dx + 6, eye_y - 8, fill=eye_color, width=2)
        elif self.expression == "happy":
            # Happy smiling arcs
            self.create_arc(cx - eye_dx - 7, eye_y - 6, cx - eye_dx + 7, eye_y + 6,
                            start=20, extent=140, style="arc", outline=eye_color, width=2)
            self.create_arc(cx + eye_dx - 7, eye_y - 6, cx + eye_dx + 7, eye_y + 6,
                            start=20, extent=140, style="arc", outline=eye_color, width=2)
        else:
            # Neutral / normal tracking eyes
            for ex in [cx - eye_dx, cx + eye_dx]:
                self.create_oval(ex - 6, eye_y - 6, ex + 6, eye_y + 6, fill=eye_color, outline="")
                self.create_oval(ex - 3 + gaze_x, eye_y - 3 + gaze_y, ex + 3 + gaze_x, eye_y + 3 + gaze_y,
                                 fill=pupil_color, outline="")

        # 6. Mouth
        mouth_y = cy + 11
        mouth_color = t.get("robot_mouth", "#0284c7")

        if self.expression == "thinking":
            # Dots animation
            dots = "." * (self.thinking_dot_frame + 1)
            self.create_text(cx, mouth_y - 1, text=dots, fill=mouth_color,
                             font=font_spec(FONT_SIZES["subtitle"], "bold"))
        elif self.expression == "smug":
            # Asymmetrical smirk
            self.create_line(cx - 10, mouth_y + 1, cx + 2, mouth_y + 1, fill=mouth_color, width=2)
            self.create_line(cx + 2, mouth_y + 1, cx + 12, mouth_y - 4, fill=mouth_color, width=2)
        elif self.expression == "surprised":
            # Open oval mouth
            self.create_oval(cx - 5, mouth_y - 4, cx + 5, mouth_y + 4, outline=mouth_color, width=2)
        elif self.expression == "sad":
            # Downward frown curve
            self.create_arc(cx - 12, mouth_y - 2, cx + 12, mouth_y + 10,
                            start=30, extent=120, style="arc", outline=mouth_color, width=2)
        elif self.expression == "happy":
            # Wide cheerful smile
            self.create_arc(cx - 12, mouth_y - 8, cx + 12, mouth_y + 4,
                            start=200, extent=140, style="arc", outline=mouth_color, width=2)
        else:
            # Straight neutral line
            self.create_line(cx - 10, mouth_y, cx + 10, mouth_y, fill=mouth_color, width=2)
