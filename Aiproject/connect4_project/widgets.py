"""
Reusable modern UI widgets for Connect 4 built with tkinter Canvas.
Provides custom rounded buttons, segmented controls, toggle switches,
cards, and tooltips using unified design tokens and font fallbacks.
"""

import tkinter as tk
try:
    from theme import SPACING, RADII, FONT_SIZES, font_spec
except ImportError:
    from connect4.theme import SPACING, RADII, FONT_SIZES, font_spec


def rounded_rect(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """
    Draw a smooth rounded rectangle on a Tkinter canvas.
    Uses a 12-point smoothed polygon for clean corners and straight edges.
    """
    r = max(int(radius), 1)
    # Ensure radius does not exceed half the width or height
    max_r = min(abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    if r > max_r:
        r = max(int(max_r), 1)

    points = [
        x1 + r, y1,
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class Tooltip:
    """Floating tooltip label displayed after a short hover delay with screen boundary clipping protection."""
    def __init__(self, widget, text, delay=450):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.after_id = None
        self.widget.bind("<Enter>", self._schedule)
        self.widget.bind("<Leave>", self._hide)
        self.widget.bind("<ButtonPress>", self._hide)

    def _schedule(self, event=None):
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def _show(self):
        if self.tip_window or not self.text:
            return

        try:
            x = self.widget.winfo_rootx() + 8
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.attributes("-topmost", True)

            lbl = tk.Label(
                tw, text=self.text, font=font_spec(FONT_SIZES["caption"]),
                bg="#0f172a", fg="#f8fafc", padx=8, pady=4,
                relief="solid", borderwidth=1, highlightbackground="#334155"
            )
            lbl.pack()

            tw.update_idletasks()
            w = tw.winfo_width()
            h = tw.winfo_height()

            # Prevent clipping outside display edge
            screen_w = tw.winfo_screenwidth()
            screen_h = tw.winfo_screenheight()
            if x + w > screen_w - 8:
                x = max(screen_w - w - 8, 8)
            if y + h > screen_h - 8:
                y = max(self.widget.winfo_rooty() - h - 6, 8)

            tw.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _hide(self, event=None):
        self._cancel()
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None


class RoundedButton(tk.Canvas):
    """Custom canvas-based button with rounded corners, states, and smooth hover."""
    def __init__(self, master, text="", command=None, width=120, height=36,
                 radius=None, primary=False, theme=None, tooltip=""):
        if radius is None:
            radius = RADII["sm"]
        super().__init__(master, width=width, height=height, highlightthickness=0, cursor="hand2")
        self.text = text
        self.command = command
        self.btn_width = width
        self.btn_height = height
        self.radius = radius
        self.primary = primary
        self.theme = theme or {}
        self.is_enabled = True
        self.is_hovered = False
        self.is_pressed = False
        self.is_focused = False

        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        if tooltip:
            Tooltip(self, tooltip)
        self._draw()

    def _on_resize(self, event):
        self.btn_width = event.width
        self.btn_height = event.height
        self._draw()

    def set_theme(self, theme):
        self.theme = theme
        self._draw()

    def set_text(self, text):
        self.text = text
        self._draw()

    def set_enabled(self, enabled):
        self.is_enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _on_focus_in(self, event):
        self.is_focused = True
        self._draw()

    def _on_focus_out(self, event):
        self.is_focused = False
        self._draw()

    def _on_enter(self, event):
        if self.is_enabled:
            self.is_hovered = True
            self._draw()

    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw()

    def _on_press(self, event):
        if self.is_enabled:
            self.is_pressed = True
            self._draw()

    def _on_release(self, event):
        if self.is_enabled and self.is_pressed:
            self.is_pressed = False
            self._draw()
            if self.command:
                self.command()

    def _draw(self):
        self.delete("all")
        t = self.theme
        w = max(self.btn_width, 10)
        h = max(self.btn_height, 10)

        # Background container color
        parent_bg = t.get("card_bg", "#1e293b")
        self.configure(bg=parent_bg)

        if not self.is_enabled:
            bg_color = t.get("button_disabled", "#1e293b")
            border_color = t.get("card_border", "#334155")
            fg_color = t.get("button_disabled_text", "#475569")
        elif self.primary:
            if self.is_pressed:
                bg_color = t.get("accent_active", "#4338ca")
            elif self.is_hovered:
                bg_color = t.get("accent_hover", "#4f46e5")
            else:
                bg_color = t.get("accent", "#6366f1")
            border_color = bg_color
            fg_color = "#ffffff"
        else:
            if self.is_pressed:
                bg_color = t.get("card_border", "#334155")
            elif self.is_hovered:
                bg_color = t.get("button_subtle_hover", "#2d3748")
            else:
                bg_color = t.get("button_subtle", "#1e293b")
            border_color = t.get("button_subtle_border", "#334155")
            fg_color = t.get("text_primary", "#f8fafc")

        # Subtle shadow layer for elevated look on primary buttons
        if self.primary and self.is_enabled and not self.is_pressed and h >= 28:
            rounded_rect(self, 2, 4, w - 2, h, radius=self.radius,
                         fill=t.get("shadow", "#030712"), outline="", width=0)

        # Outer rounded button body
        rounded_rect(self, 2, 2, w - 2, h - 2, radius=self.radius,
                     fill=bg_color, outline=border_color, width=1)

        # Focus ring highlight
        if self.is_focused:
            rounded_rect(self, 4, 4, w - 4, h - 4, radius=max(self.radius - 2, 2),
                         fill="", outline=t.get("focus_ring", "#818cf8"), width=1)

        # Centered button text
        font_size = FONT_SIZES["body_sm"] if h <= 28 else FONT_SIZES["body"]
        font_weight = "bold" if self.primary else "normal"
        self.create_text(
            w / 2, h / 2, text=self.text, fill=fg_color,
            font=font_spec(font_size, font_weight)
        )


class SegmentedControl(tk.Canvas):
    """Pill-shaped segmented selection control replacing standard radio buttons."""
    def __init__(self, master, options, selected_var, callback=None,
                 height=34, theme=None):
        super().__init__(master, height=height, highlightthickness=0, cursor="hand2")
        self.options = options
        self.selected_var = selected_var
        self.callback = callback
        self.ctl_height = height
        self.theme = theme or {}
        self.hover_idx = None

        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)

        self._draw()

    def _on_resize(self, event):
        self._draw()

    def set_theme(self, theme):
        self.theme = theme
        self._draw()

    def _on_motion(self, event):
        w = self.winfo_width()
        n = len(self.options)
        if n == 0 or w == 0:
            return
        seg_w = w / n
        idx = int(event.x // seg_w)
        if 0 <= idx < n and idx != self.hover_idx:
            self.hover_idx = idx
            self._draw()

    def _on_leave(self, event):
        if self.hover_idx is not None:
            self.hover_idx = None
            self._draw()

    def _on_click(self, event):
        w = self.winfo_width()
        n = len(self.options)
        if n == 0 or w == 0:
            return
        seg_w = w / n
        idx = int(event.x // seg_w)
        if 0 <= idx < n:
            val = self.options[idx]
            if self.selected_var.get() != val:
                self.selected_var.set(val)
                self._draw()
                if self.callback:
                    self.callback()

    def _draw(self):
        self.delete("all")
        t = self.theme
        w = self.winfo_width()
        h = max(self.ctl_height, 24)
        if w < 10:
            w = 200

        parent_bg = t.get("card_bg", "#1e293b")
        self.configure(bg=parent_bg)

        # Track background
        pill_bg = t.get("pill_bg", "#090d16")
        pill_border = t.get("pill_border", "#334155")
        rounded_rect(self, 1, 1, w - 1, h - 1, radius=h // 2,
                     fill=pill_bg, outline=pill_border, width=1)

        n = len(self.options)
        if n == 0:
            return

        seg_w = (w - 4) / n
        current_val = self.selected_var.get()

        for i, opt in enumerate(self.options):
            sx1 = 2 + i * seg_w
            sx2 = sx1 + seg_w
            sy1 = 2
            sy2 = h - 2
            is_selected = (opt == current_val)

            if is_selected:
                # Active pill highlight
                accent_color = t.get("accent", "#6366f1")
                rounded_rect(self, sx1, sy1, sx2, sy2, radius=(h - 4) // 2,
                             fill=accent_color, outline="", width=0)
                text_color = "#ffffff"
                font_weight = "bold"
            else:
                if self.hover_idx == i:
                    hover_color = t.get("card_hover", "#253349")
                    rounded_rect(self, sx1, sy1, sx2, sy2, radius=(h - 4) // 2,
                                 fill=hover_color, outline="", width=0)
                text_color = t.get("text_secondary", "#94a3b8")
                font_weight = "normal"

            cx = (sx1 + sx2) / 2
            cy = h / 2
            self.create_text(
                cx, cy, text=opt, fill=text_color,
                font=font_spec(FONT_SIZES["body"], font_weight)
            )


class ToggleSwitch(tk.Canvas):
    """Custom sliding knob toggle switch replacing system checkboxes."""
    def __init__(self, master, is_on=False, callback=None, theme=None,
                 width=44, height=24):
        super().__init__(master, width=width, height=height, highlightthickness=0, cursor="hand2")
        self.is_on = bool(is_on)
        self.callback = callback
        self.theme = theme or {}
        self.sw_width = width
        self.sw_height = height

        self.bind("<Button-1>", self._on_toggle)
        self._draw()

    def set_theme(self, theme):
        self.theme = theme
        self._draw()

    def set_state(self, is_on):
        self.is_on = bool(is_on)
        self._draw()

    def _on_toggle(self, event):
        self.is_on = not self.is_on
        self._draw()
        if self.callback:
            self.callback(self.is_on)

    def _draw(self):
        self.delete("all")
        t = self.theme
        w = self.sw_width
        h = self.sw_height
        r = h // 2

        parent_bg = t.get("header_bg", t.get("panel_bg", "#0f172a"))
        self.configure(bg=parent_bg)

        # Track color
        track_color = t.get("switch_track_on", "#6366f1") if self.is_on else t.get("switch_track_off", "#334155")
        rounded_rect(self, 1, 1, w - 1, h - 1, radius=r,
                     fill=track_color, outline="", width=0)

        # Knob position
        knob_r = r - 3
        if self.is_on:
            kx = w - r
        else:
            kx = r
        ky = h / 2

        # 3D shadow under knob for physical depth
        self.create_oval(
            kx - knob_r + 1, ky - knob_r + 1,
            kx + knob_r + 1, ky + knob_r + 1,
            fill=t.get("shadow", "#030712"), outline=""
        )

        knob_color = t.get("switch_knob", "#ffffff")
        self.create_oval(
            kx - knob_r, ky - knob_r,
            kx + knob_r, ky + knob_r,
            fill=knob_color, outline=""
        )


class Card(tk.Frame):
    """Structured container frame with an accent pip, header bar, and rounded look."""
    def __init__(self, master, title="", subtitle="", theme=None, collapsible=False, **kwargs):
        self.theme = theme or {}
        bg = self.theme.get("card_bg", "#1e293b")
        pad_x = SPACING.get("md", 12)
        pad_y = SPACING.get("sm", 8)
        super().__init__(master, bg=bg, padx=pad_x, pady=pad_y, **kwargs)
        self.title_text = title
        self.sub_text = subtitle
        self.collapsible = collapsible
        self.is_collapsed = False
        self.lbl_title = None
        self.lbl_sub = None
        self.pip_canvas = None

        # Header bar inside card
        if title:
            self.header_frame = tk.Frame(self, bg=bg)
            self.header_frame.pack(fill="x", pady=(0, SPACING.get("xs", 4)))

            # Accent pip indicator (colored 3px bar)
            self.pip_canvas = tk.Canvas(self.header_frame, width=4, height=14, bg=bg, highlightthickness=0)
            self.pip_canvas.pack(side="left", padx=(0, 6))
            self._draw_pip()

            self.lbl_title = tk.Label(
                self.header_frame, text=title.upper(),
                font=font_spec(FONT_SIZES["caption"], "bold"),
                bg=bg, fg=self.theme.get("text_accent", "#818cf8")
            )
            self.lbl_title.pack(side="left")

            if subtitle:
                self.lbl_sub = tk.Label(
                    self.header_frame, text=subtitle,
                    font=font_spec(FONT_SIZES["caption"]),
                    bg=bg, fg=self.theme.get("text_muted", "#64748b")
                )
                self.lbl_sub.pack(side="right")

            if collapsible:
                self.header_frame.configure(cursor="hand2")
                self.lbl_title.configure(cursor="hand2")
                if self.lbl_sub:
                    self.lbl_sub.configure(cursor="hand2")
                self.header_frame.bind("<Button-1>", self._on_toggle_collapse)
                self.lbl_title.bind("<Button-1>", self._on_toggle_collapse)
                if self.lbl_sub:
                    self.lbl_sub.bind("<Button-1>", self._on_toggle_collapse)

        # Content frame for caller widgets
        self.content = tk.Frame(self, bg=bg)
        self.content.pack(fill="both", expand=True)

    def _draw_pip(self):
        if self.pip_canvas:
            self.pip_canvas.delete("all")
            bg = self.theme.get("card_bg", "#1e293b")
            self.pip_canvas.configure(bg=bg)
            accent = self.theme.get("accent", "#6366f1")
            rounded_rect(self.pip_canvas, 0, 1, 4, 13, radius=2, fill=accent, outline="", width=0)

    def _on_toggle_collapse(self, event=None):
        if not self.collapsible:
            return
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.content.pack_forget()
            if self.lbl_sub:
                self.lbl_sub.configure(text="▲ Expand")
        else:
            self.content.pack(fill="both", expand=True)
            if self.lbl_sub:
                self.lbl_sub.configure(text=self.sub_text or "▼ Collapse")

    def set_theme(self, theme):
        self.theme = theme
        bg = self.theme.get("card_bg", "#1e293b")
        self.configure(bg=bg)
        if hasattr(self, "header_frame") and self.header_frame:
            self.header_frame.configure(bg=bg)
        self._draw_pip()
        if self.lbl_title:
            self.lbl_title.configure(bg=bg, fg=self.theme.get("text_accent", "#818cf8"))
        if self.lbl_sub:
            self.lbl_sub.configure(bg=bg, fg=self.theme.get("text_muted", "#64748b"))
        self.content.configure(bg=bg)
