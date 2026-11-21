"""
Connect 4 GUI implementation using modern custom Canvas-based components.
Features:
- Custom-themed UI with no default grey/white system widgets
- Dynamic responsive board scaling with 3D-styled coins and inner-shadow slots
- Smooth coin-drop animation with tactile bounce effect
- Cheeky animated robot avatar with live gaze tracking and situational expressions
- Context-aware dialogue system with witty commentary and chatty toggle
- Side-by-side Compare Mode with dual comparative node-expansion bars
- Confetti celebration on human victory and pulsing winning line highlights
- Full Dark / Light theme toggle with custom sliding switches
- Complete keyboard shortcut bindings (1-7, N, U, H, C)
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading
import random

try:
    from game import (
        ROWS, COLS, EMPTY, HUMAN, AI, PLAYER_NAMES,
        create_board, copy_board, is_valid_move, get_valid_moves,
        get_bottom_empty_row, drop_piece, undo_piece, is_terminal
    )
    from ai import best_move
    from theme import (
        get_theme, THEMES, SPACING, RADII, FONT_SIZES, font_spec, get_font_family
    )
    from widgets import rounded_rect, RoundedButton, SegmentedControl, ToggleSwitch, Card, Tooltip
    from avatar import RobotAvatar
    from messages import get_message, get_pruning_message
    from video_player import VideoPlayer, HAS_VIDEO_LIBS
except ImportError:
    from connect4.game import (
        ROWS, COLS, EMPTY, HUMAN, AI, PLAYER_NAMES,
        create_board, copy_board, is_valid_move, get_valid_moves,
        get_bottom_empty_row, drop_piece, undo_piece, is_terminal
    )
    from connect4.ai import best_move
    from connect4.theme import (
        get_theme, THEMES, SPACING, RADII, FONT_SIZES, font_spec, get_font_family
    )
    from connect4.widgets import rounded_rect, RoundedButton, SegmentedControl, ToggleSwitch, Card, Tooltip
    from connect4.avatar import RobotAvatar
    from connect4.messages import get_message, get_pruning_message
    try:
        from connect4.video_player import VideoPlayer, HAS_VIDEO_LIBS
    except ImportError:
        VideoPlayer = None
        HAS_VIDEO_LIBS = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class Connect4App:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - AI Minimax & Alpha-Beta Engine")
        self.root.geometry("1120x750")
        self.root.minsize(1020, 700)

        # Core Theme & Audio States
        self.current_theme_name = "dark"
        self.theme = get_theme(self.current_theme_name)
        self.sound_enabled = True
        self.chatty_enabled = True

        # Configuration Variables
        self.first_player_var = tk.StringVar(value="Human")
        self.algorithm_var = tk.StringVar(value="Alpha-Beta")
        self.difficulty_var = tk.StringVar(value="Medium")

        # Game State
        self.board = create_board()
        self.current_turn = HUMAN
        self.game_over = False
        self.winning_cells = None
        self.move_history = []
        self.hover_col = None
        self.hint_col = None
        self.hint_timer = None
        self.hint_dismiss_timer = None
        self.hint_phase = 0
        self.is_animating = False
        self.is_thinking = False
        self.thinking_anim_step = 0
        self.thinking_timer = None

        # Drop Animation State
        self.anim_col = None
        self.anim_target_row = None
        self.anim_current_y = None
        self.anim_player = None
        self.anim_velocity = 0
        self.anim_bouncing = False

        # Winning Animation Pulse State
        self.pulse_phase = 0
        self.pulse_timer = None

        # Confetti Celebration State
        self.confetti_particles = []
        self.confetti_timer = None

        # Idle Timer
        self.idle_timer = None
        self.last_user_action_time = time.time()

        # Scoreboard & Telemetry
        self.scores = {"human": 0, "ai": 0, "draws": 0}
        self.last_ai_stats = {
            "col": "-",
            "nodes": "-",
            "time_ms": "-",
            "mode": "-",
            "nodes_num": 0,
            "mm_ref_nodes": 0
        }

        # Board Drawing Geometry (dynamically recalculated)
        self.cell_size = 72
        self.board_offset_x = 20
        self.board_offset_y = 20
        self.resize_debounce_id = None

        # Build UI Architecture
        self._build_top_header()
        self._build_main_layout()
        self._bind_keyboard_shortcuts()
        self._apply_theme()

        # Handle window closure gracefully
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Start game and idle tracking
        self.new_game()
        self._reset_idle_timer()

    def _on_window_close(self):
        """Release video resources, audio streams, cancel animations, and destroy window."""
        self._stop_winning_pulse()
        self._stop_thinking_pulse()
        self._clear_hint()
        if self.confetti_timer:
            try:
                self.root.after_cancel(self.confetti_timer)
            except Exception:
                pass
            self.confetti_timer = None
        if self.idle_timer:
            try:
                self.root.after_cancel(self.idle_timer)
            except Exception:
                pass
            self.idle_timer = None
        if hasattr(self, "video_player"):
            self.video_player.stop(trigger_callback=False)
        self.root.destroy()

    @property
    def current_theme(self):
        """Compatibility property returning current theme name ('dark' or 'light')."""
        return self.current_theme_name

    # -------------------------------------------------------------------------
    # Top Header Bar
    # -------------------------------------------------------------------------
    def _build_top_header(self):
        """Construct top header with title logo and quick toggle switches."""
        self.header_frame = tk.Frame(self.root, height=56, padx=SPACING["lg"], pady=SPACING["xs"])
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        # Thin 1px divider below header
        self.header_sep = tk.Frame(self.root, height=1, bg=self.theme["header_border"])
        self.header_sep.pack(side="top", fill="x")

        # Left brand container (Canvas logo + Titles)
        left_brand = tk.Frame(self.header_frame)
        left_brand.pack(side="left", fill="y")

        # Canvas Logo: two intersecting 3D coins with an energy spark
        self.logo_canvas = tk.Canvas(left_brand, width=42, height=38, highlightthickness=0)
        self.logo_canvas.pack(side="left", padx=(0, 10))

        title_box = tk.Frame(left_brand)
        title_box.pack(side="left")

        self.lbl_main_title = tk.Label(
            title_box, text="CONNECT 4", font=font_spec(FONT_SIZES["title"], "bold")
        )
        self.lbl_main_title.pack(anchor="w")

        self.lbl_main_sub = tk.Label(
            title_box, text="AI MINIMAX & ALPHA-BETA ENGINE", font=font_spec(FONT_SIZES["micro"], "bold")
        )
        self.lbl_main_sub.pack(anchor="w")

        # Right control toggles (Sound & Theme switches)
        right_controls = tk.Frame(self.header_frame)
        right_controls.pack(side="right", fill="y")

        # Sound Switch
        self.lbl_sound_tag = tk.Label(right_controls, text="SOUND", font=font_spec(FONT_SIZES["caption"], "bold"))
        self.lbl_sound_tag.pack(side="left", padx=(10, 4))
        self.sw_sound = ToggleSwitch(right_controls, is_on=True, callback=self._on_sound_toggled)
        self.sw_sound.pack(side="left", padx=(0, 16))

        # Theme Switch
        self.lbl_theme_tag = tk.Label(right_controls, text="DARK", font=font_spec(FONT_SIZES["caption"], "bold"))
        self.lbl_theme_tag.pack(side="left", padx=(4, 4))
        self.sw_theme = ToggleSwitch(right_controls, is_on=True, callback=self._on_theme_toggled)
        self.sw_theme.pack(side="left", padx=(0, 8))

    # -------------------------------------------------------------------------
    # Main Three-Panel Layout
    # -------------------------------------------------------------------------
    def _build_main_layout(self):
        """Build Left Settings, Center Board Arena, and Right Robot/Telemetry panels."""
        t = self.theme
        self.body_frame = tk.Frame(self.root, bg=t["bg"])
        self.body_frame.pack(side="top", fill="both", expand=True)
        self.body_frame.columnconfigure(1, weight=1)
        self.body_frame.rowconfigure(0, weight=1)

        # 1. Left Panel (Settings Cards)
        self.left_panel = tk.Frame(
            self.body_frame, width=275, padx=SPACING["md"], pady=SPACING["md"],
            bg=t["panel_bg"], highlightbackground=t["panel_border"], highlightthickness=1
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.pack_propagate(False)

        # Card: Match Configuration
        self.card_match = Card(self.left_panel, title="Match Settings")
        self.card_match.pack(fill="x", pady=(0, SPACING["sm"]))

        tk.Label(self.card_match.content, text="FIRST MOVE", font=font_spec(FONT_SIZES["caption"], "bold"),
                 name="lbl_fp").pack(anchor="w", pady=(0, 2))
        self.seg_first_player = SegmentedControl(
            self.card_match.content, options=["Human", "Computer"],
            selected_var=self.first_player_var, callback=self._on_setting_changed,
            height=30
        )
        self.seg_first_player.pack(fill="x", pady=(0, SPACING["sm"]))

        tk.Label(self.card_match.content, text="ALGORITHM", font=font_spec(FONT_SIZES["caption"], "bold"),
                 name="lbl_algo").pack(anchor="w", pady=(0, 2))
        self.seg_algorithm = SegmentedControl(
            self.card_match.content, options=["Alpha-Beta", "Minimax"],
            selected_var=self.algorithm_var, callback=self._on_setting_changed,
            height=30
        )
        self.seg_algorithm.pack(fill="x", pady=(0, SPACING["sm"]))

        tk.Label(self.card_match.content, text="DIFFICULTY LEVEL", font=font_spec(FONT_SIZES["caption"], "bold"),
                 name="lbl_diff").pack(anchor="w", pady=(0, 2))
        self.seg_difficulty = SegmentedControl(
            self.card_match.content, options=["Easy", "Medium", "Hard"],
            selected_var=self.difficulty_var, callback=self._on_difficulty_changed,
            height=30
        )
        self.seg_difficulty.pack(fill="x", pady=(0, 3))

        # Dynamic Difficulty Subtitle
        self.lbl_diff_flavor = tk.Label(
            self.card_match.content, text="Now it is personal (depth 3)",
            font=font_spec(FONT_SIZES["caption"], "normal")
        )
        self.lbl_diff_flavor.pack(anchor="w", pady=(0, 2))

        # Card: Actions
        self.card_actions = Card(self.left_panel, title="Actions")
        self.card_actions.pack(fill="x", pady=(0, SPACING["sm"]))

        self.btn_new_game = RoundedButton(
            self.card_actions.content, text="New Game", command=self.new_game,
            primary=True, height=34, tooltip="Start a new game (Hotkey: N)"
        )
        self.btn_new_game.pack(fill="x", pady=3)

        self.btn_undo = RoundedButton(
            self.card_actions.content, text="Undo Move", command=self.undo_move,
            height=30, tooltip="Take back your last move and AI reply (Hotkey: U)"
        )
        self.btn_undo.pack(fill="x", pady=3)

        self.btn_hint = RoundedButton(
            self.card_actions.content, text="Hint", command=self.request_hint,
            height=30, tooltip="Highlight optimal column for human (Hotkey: H)"
        )
        self.btn_hint.pack(fill="x", pady=3)

        self.btn_compare = RoundedButton(
            self.card_actions.content, text="Compare AI", command=self.show_comparison,
            height=30, tooltip="Benchmark Minimax vs Alpha-Beta side-by-side (Hotkey: C)"
        )
        self.btn_compare.pack(fill="x", pady=3)

        # Card: Commentary Options
        self.card_chat = Card(self.left_panel, title="Robot Commentary")
        self.card_chat.pack(fill="x", side="bottom")

        chat_row = tk.Frame(self.card_chat.content)
        chat_row.pack(fill="x", pady=2)
        self.lbl_chat_tag = tk.Label(
            chat_row, text="Chatty Robot", font=font_spec(FONT_SIZES["body"])
        )
        self.lbl_chat_tag.pack(side="left")
        self.sw_chat = ToggleSwitch(
            chat_row, is_on=True, callback=self._on_chat_toggled
        )
        self.sw_chat.pack(side="right")

        # 2. Center Panel (Arena: Status Banner + Scalable Canvas)
        self.center_panel = tk.Frame(self.body_frame, bg=t["bg"])
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=6, pady=SPACING["sm"])
        self.center_panel.rowconfigure(1, weight=1)
        self.center_panel.columnconfigure(0, weight=1)

        # Status Banner (modern pill style)
        self.status_bar_canvas = tk.Canvas(self.center_panel, height=44, highlightthickness=0, bg=t["bg"])
        self.status_bar_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.status_bar_canvas.bind("<Configure>", lambda e: self._draw_status_banner())

        # Main Scalable Board Canvas
        self.canvas = tk.Canvas(self.center_panel, highlightthickness=0, bg=t["bg"])
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.canvas.bind("<Configure>", self._on_canvas_resize_debounced)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        # 3. Right Panel (Robot Avatar, Scoreboard, Telemetry, Shortcuts)
        self.right_panel = tk.Frame(
            self.body_frame, width=275, padx=SPACING["md"], pady=SPACING["md"],
            bg=t["panel_bg"], highlightbackground=t["panel_border"], highlightthickness=1
        )
        self.right_panel.grid(row=0, column=2, sticky="nsew")
        self.right_panel.pack_propagate(False)

        # Card: Robot Opponent
        self.card_robot = Card(self.right_panel, title="Opponent", subtitle="Silicon Challenger")
        self.card_robot.pack(fill="x", pady=(0, SPACING["sm"]))

        # Avatar
        self.avatar = RobotAvatar(self.card_robot.content, height=95)
        self.avatar.pack(fill="x", pady=(0, 6))

        # Speech Bubble
        self.bubble_canvas = tk.Canvas(self.card_robot.content, height=62, highlightthickness=0)
        self.bubble_canvas.pack(fill="x", pady=(0, 2))
        self.speech_text = "Welcome to Connect 4! Ready when you are."

        # Video Player (embedded inside Opponent card, hidden initially)
        if VideoPlayer is not None:
            self.video_player = VideoPlayer(
                self.card_robot.content,
                width=220,
                height=163,
                theme=self.theme,
                on_finish=self._restore_robot_view,
                get_sound_enabled=lambda: self.sound_enabled
            )
        else:
            self.video_player = None

        # Card: Scoreboard
        self.card_scores = Card(self.right_panel, title="Scoreboard")
        self.card_scores.pack(fill="x", pady=(0, SPACING["sm"]))

        scores_row = tk.Frame(self.card_scores.content)
        scores_row.pack(fill="x", pady=2)
        scores_row.columnconfigure(0, weight=1)
        scores_row.columnconfigure(1, weight=1)
        scores_row.columnconfigure(2, weight=1)

        # You (Red)
        self.f_score_you = tk.Frame(scores_row)
        self.f_score_you.grid(row=0, column=0, sticky="nsew")
        self.lbl_score_num_you = tk.Label(self.f_score_you, text="0", font=font_spec(18, "bold"))
        self.lbl_score_num_you.pack()
        self.lbl_score_tag_you = tk.Label(self.f_score_you, text="● You", font=font_spec(FONT_SIZES["caption"], "bold"))
        self.lbl_score_tag_you.pack()

        # Robot (Yellow)
        self.f_score_ai = tk.Frame(scores_row)
        self.f_score_ai.grid(row=0, column=1, sticky="nsew")
        self.lbl_score_num_ai = tk.Label(self.f_score_ai, text="0", font=font_spec(18, "bold"))
        self.lbl_score_num_ai.pack()
        self.lbl_score_tag_ai = tk.Label(self.f_score_ai, text="● Robot", font=font_spec(FONT_SIZES["caption"], "bold"))
        self.lbl_score_tag_ai.pack()

        # Draws
        self.f_score_draws = tk.Frame(scores_row)
        self.f_score_draws.grid(row=0, column=2, sticky="nsew")
        self.lbl_score_num_draws = tk.Label(self.f_score_draws, text="0", font=font_spec(18, "bold"))
        self.lbl_score_num_draws.pack()
        self.lbl_score_tag_draws = tk.Label(self.f_score_draws, text="Draws", font=font_spec(FONT_SIZES["caption"]))
        self.lbl_score_tag_draws.pack()

        self.btn_reset_scores = RoundedButton(
            self.card_scores.content, text="Reset Scores", command=self.reset_scores,
            height=26, tooltip="Reset win counters to zero"
        )
        self.btn_reset_scores.pack(anchor="e", pady=(4, 0))

        # Card: Last AI Move Telemetry
        self.card_telemetry = Card(self.right_panel, title="Last AI Move")
        self.card_telemetry.pack(fill="x", pady=(0, SPACING["sm"]))

        self.telemetry_rows = {}
        for metric, label in [("col", "Column Chosen"), ("nodes", "Nodes Visited"),
                              ("time_ms", "Search Time"), ("mode", "Engine Mode")]:
            row = tk.Frame(self.card_telemetry.content)
            row.pack(fill="x", pady=1)
            lbl_m = tk.Label(row, text=label, font=font_spec(FONT_SIZES["caption"]), anchor="w")
            lbl_m.pack(side="left")
            lbl_v = tk.Label(row, text="-", font=font_spec(FONT_SIZES["caption"], "bold", family="mono"), anchor="e")
            lbl_v.pack(side="right")
            self.telemetry_rows[metric] = (lbl_m, lbl_v)

        # Progress bar comparing nodes
        self.bar_canvas = tk.Canvas(self.card_telemetry.content, height=10, highlightthickness=0)
        self.bar_canvas.pack(fill="x", pady=(4, 0))

        # Card: Collapsible Keyboard Shortcuts
        self.card_shortcuts = Card(self.right_panel, title="Shortcuts", subtitle="Click to toggle", collapsible=True)
        self.card_shortcuts.pack(fill="x", side="bottom")

        sc_text = "1-7: Drop Coin  |  N: New Game\nU: Undo Move    |  H: Hint  |  C: Compare"
        self.lbl_shortcuts_info = tk.Label(
            self.card_shortcuts.content, text=sc_text,
            font=font_spec(FONT_SIZES["caption"]), justify="left", anchor="w"
        )
        self.lbl_shortcuts_info.pack(fill="x", pady=2)
        self.lbl_shortcuts_info.pack(fill="x", pady=2)

    # -------------------------------------------------------------------------
    # Keyboard Shortcuts Binding
    # -------------------------------------------------------------------------
    def _bind_keyboard_shortcuts(self):
        """Bind keys 1-7, N, U, H, C for seamless keyboard play."""
        for c in range(1, 8):
            self.root.bind(str(c), lambda event, col=c-1: self._on_key_drop(col))
        self.root.bind("<n>", lambda event: self.new_game())
        self.root.bind("<N>", lambda event: self.new_game())
        self.root.bind("<u>", lambda event: self.undo_move())
        self.root.bind("<U>", lambda event: self.undo_move())
        self.root.bind("<h>", lambda event: self.request_hint())
        self.root.bind("<H>", lambda event: self.request_hint())
        self.root.bind("<c>", lambda event: self.show_comparison())
        self.root.bind("<C>", lambda event: self.show_comparison())

    def _on_key_drop(self, col):
        """Triggered when a number key (1 to 7) is pressed."""
        if not self.game_over and not self.is_animating and not self.is_thinking:
            if self.current_turn == HUMAN and is_valid_move(self.board, col):
                self._clear_hint()
                self._record_user_action()
                self._start_coin_animation(col, HUMAN)

    # -------------------------------------------------------------------------
    # Theming & Palette Management
    # -------------------------------------------------------------------------
    def _apply_theme(self):
        """Distribute current palette to all custom widgets, canvas frames, and labels."""
        t = self.theme

        # Backgrounds
        self.root.configure(bg=t["bg"])
        self.header_frame.configure(bg=t["header_bg"])
        if hasattr(self, "header_sep"):
            self.header_sep.configure(bg=t["header_border"])
        for child in self.header_frame.winfo_children():
            try:
                child.configure(bg=t["header_bg"])
            except Exception:
                pass
        self.body_frame.configure(bg=t["bg"])
        self.left_panel.configure(bg=t["panel_bg"], highlightbackground=t["panel_border"], highlightthickness=1)
        self.center_panel.configure(bg=t["bg"])
        self.right_panel.configure(bg=t["panel_bg"], highlightbackground=t["panel_border"], highlightthickness=1)

        # Header Titles
        self.lbl_main_title.configure(bg=t["header_bg"], fg=t["text_primary"])
        self.lbl_main_sub.configure(bg=t["header_bg"], fg=t["text_accent"])
        self.lbl_sound_tag.configure(bg=t["header_bg"], fg=t["text_secondary"])
        self.lbl_theme_tag.configure(
            bg=t["header_bg"], fg=t["text_secondary"],
            text="DARK" if self.current_theme_name == "dark" else "LIGHT"
        )

        # Header Logo Drawing
        self._draw_logo()

        # Update Cards & Widgets
        cards = [self.card_match, self.card_actions, self.card_chat,
                 self.card_robot, self.card_scores, self.card_telemetry,
                 self.card_shortcuts]
        for c in cards:
            c.set_theme(t)

        # Subtitle flavor
        self.lbl_diff_flavor.configure(
            bg=t["card_bg"], fg=t["text_muted"]
        )

        # Segmented controls
        self.seg_first_player.set_theme(t)
        self.seg_algorithm.set_theme(t)
        self.seg_difficulty.set_theme(t)

        # Buttons
        buttons = [self.btn_new_game, self.btn_undo, self.btn_hint,
                   self.btn_compare, self.btn_reset_scores]
        for b in buttons:
            b.set_theme(t)

        # Switches
        self.sw_sound.set_theme(t)
        self.sw_theme.set_theme(t)
        self.sw_chat.set_theme(t)
        self.lbl_chat_tag.configure(bg=t["card_bg"], fg=t["text_primary"])

        # Scoreboard labels
        for f in [self.f_score_you, self.f_score_ai, self.f_score_draws]:
            f.configure(bg=t["card_bg"])

        self.lbl_score_num_you.configure(bg=t["card_bg"], fg=t["human_coin"])
        self.lbl_score_tag_you.configure(bg=t["card_bg"], fg=t["human_coin"])
        self.lbl_score_num_ai.configure(bg=t["card_bg"], fg=t["ai_coin"])
        self.lbl_score_tag_ai.configure(bg=t["card_bg"], fg=t["ai_coin"])
        self.lbl_score_num_draws.configure(bg=t["card_bg"], fg=t["text_primary"])
        self.lbl_score_tag_draws.configure(bg=t["card_bg"], fg=t["text_secondary"])

        # Telemetry labels
        for metric, (lbl_m, lbl_v) in self.telemetry_rows.items():
            lbl_m.master.configure(bg=t["card_bg"])
            lbl_m.configure(bg=t["card_bg"], fg=t["text_secondary"])
            lbl_v.configure(bg=t["card_bg"], fg=t["text_primary"])

        self.lbl_shortcuts_info.configure(bg=t["card_bg"], fg=t["text_secondary"])

        # Avatar and Dialogue
        self.avatar.set_theme(t)
        if hasattr(self, "video_player") and self.video_player is not None:
            self.video_player.set_theme(t)
        self._draw_speech_bubble()
        self._draw_status_banner()
        self._draw_board()
        self._draw_telemetry_bar()

    def _draw_logo(self):
        """Draw intersecting 3D coins with an energy spark as the logo."""
        self.logo_canvas.delete("all")
        t = self.theme
        self.logo_canvas.configure(bg=t["header_bg"])
        # Red coin with shaded rim
        self.logo_canvas.create_oval(4, 7, 22, 25, fill=t["human_coin"], outline=t["human_shadow"], width=1)
        self.logo_canvas.create_arc(4, 7, 22, 25, start=45, extent=125,
                                    fill="", outline=t["human_highlight"], width=2, style="arc")
        # Yellow coin with shaded rim
        self.logo_canvas.create_oval(16, 11, 34, 29, fill=t["ai_coin"], outline=t["ai_shadow"], width=1)
        self.logo_canvas.create_arc(16, 11, 34, 29, start=45, extent=125,
                                    fill="", outline=t["ai_highlight"], width=2, style="arc")
        # Center Sparking Core
        self.logo_canvas.create_oval(16, 15, 22, 21, fill="#ffffff", outline="")

    def _on_theme_toggled(self, is_dark):
        """Toggle between Dark and Light mode without resetting the game."""
        self.current_theme_name = "dark" if is_dark else "light"
        self.theme = get_theme(self.current_theme_name)
        self._apply_theme()

    def _on_sound_toggled(self, is_on):
        """Toggle audio feedback."""
        self.sound_enabled = is_on
        if hasattr(self, "video_player") and self.video_player is not None:
            self.video_player.set_sound_enabled(is_on)

    def _on_chat_toggled(self, is_on):
        """Toggle robot commentary."""
        self.chatty_enabled = is_on
        if not is_on:
            self.speech_text = "..."
        else:
            self.speech_text = "Chatty mode re-enabled! Let's play."
        self._draw_speech_bubble()

    def _play_sound(self, sound_type="drop"):
        """Safely trigger audio in a worker thread."""
        if not self.sound_enabled:
            return

        def _sound_worker():
            try:
                if HAS_WINSOUND:
                    if sound_type == "drop":
                        winsound.Beep(680, 35)
                    elif sound_type == "bounce":
                        winsound.Beep(520, 25)
                    elif sound_type == "win":
                        winsound.Beep(784, 80)
                        winsound.Beep(1046, 130)
                    elif sound_type == "draw":
                        winsound.Beep(440, 100)
                else:
                    self.root.bell()
            except Exception:
                pass

        threading.Thread(target=_sound_worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # Robot Dialogue & Commentary
    # -------------------------------------------------------------------------
    def _say(self, situation, expression=None, custom_msg=None):
        """Trigger robot dialogue and update facial expression."""
        if not self.chatty_enabled and situation not in ["human_wins", "ai_wins", "draw"]:
            return

        if custom_msg:
            self.speech_text = custom_msg
        else:
            self.speech_text = get_message(situation)

        if expression:
            self.avatar.set_expression(expression)

        self._draw_speech_bubble()

    def _draw_speech_bubble(self):
        """Render a rounded speech bubble with tail pointing to the robot."""
        self.bubble_canvas.delete("all")
        t = self.theme
        w = self.bubble_canvas.winfo_width()
        h = max(self.bubble_canvas.winfo_height(), 58)
        if w < 10:
            w = 230

        self.bubble_canvas.configure(bg=t["card_bg"])

        # Rounded bubble rectangle
        bubble_bg = t.get("bubble_bg", "#1e293b")
        bubble_border = t.get("bubble_border", "#6366f1")
        rounded_rect(self.bubble_canvas, 4, 10, w - 4, h - 2, radius=RADII["sm"],
                     fill=bubble_bg, outline=bubble_border, width=1)

        # Bubble upward pointing tail
        self.bubble_canvas.create_polygon(
            w / 2 - 8, 10,
            w / 2, 2,
            w / 2 + 8, 10,
            fill=bubble_bg, outline=""
        )
        self.bubble_canvas.create_line(w / 2 - 8, 10, w / 2, 2, fill=bubble_border, width=1)
        self.bubble_canvas.create_line(w / 2, 2, w / 2 + 8, 10, fill=bubble_border, width=1)

        # Wrapped text
        fg = t.get("bubble_text", "#f8fafc")
        self.bubble_canvas.create_text(
            w / 2, (h + 8) / 2, text=self.speech_text,
            fill=fg, font=font_spec(FONT_SIZES["body_sm"]),
            width=w - 24, justify="center"
        )

    def _show_video(self, winner):
        """
        Play a random victory video inside the Opponent card, replacing
        the robot avatar and speech bubble.
        """
        if not HAS_VIDEO_LIBS or self.video_player is None:
            return

        outcome = "computer" if winner == AI else "human"
        started = self.video_player.play_random(outcome)
        if started:
            self.avatar.pack_forget()
            self.bubble_canvas.pack_forget()
            self.video_player.pack(fill="x", pady=(0, 2))

    def _restore_robot_view(self):
        """
        Stop video playback and re-pack avatar and speech bubble in their
        original order and padding.
        """
        if self.video_player is not None:
            if self.video_player.is_active():
                self.video_player.stop(trigger_callback=False)
            self.video_player.pack_forget()

        self.avatar.pack(fill="x", pady=(0, 6))
        self.bubble_canvas.pack(fill="x", pady=(0, 2))
        self._draw_speech_bubble()

    # -------------------------------------------------------------------------
    # Status Banner
    # -------------------------------------------------------------------------
    def _draw_status_banner(self):
        """Render the status banner pill above the board with dynamic state accents."""
        self.status_bar_canvas.delete("all")
        t = self.theme
        w = self.status_bar_canvas.winfo_width()
        h = max(self.status_bar_canvas.winfo_height(), 44)
        if w < 10:
            w = 500

        self.status_bar_canvas.configure(bg=t["bg"])

        # Centered pill banner
        pill_w = min(w - 24, 480)
        px1 = (w - pill_w) / 2
        px2 = px1 + pill_w
        py1 = 4
        py2 = h - 4

        # Status text, icon color, and pill accent outline
        if self.game_over:
            if self.winning_cells:
                is_human = (self.current_turn == HUMAN)  # Winner took the last move
                txt = "VICTORY! RED CONNECTED 4" if is_human else "ROBOT WINS! 4 IN A ROW"
                dot_color = t["win_glow"] if is_human else t["ai_coin"]
                pill_outline = t["win_glow"] if is_human else t["ai_coin"]
            else:
                txt = "DRAW! 42 CELLS FILLED"
                dot_color = t["cyan_accent"]
                pill_outline = t["cyan_accent"]
        elif self.is_thinking:
            txt = "ROBOT IS THINKING..."
            dot_color = t["ai_coin"]
            pill_outline = t["ai_highlight"]
        elif self.current_turn == HUMAN:
            txt = "YOUR TURN (RED)"
            dot_color = t["human_coin"]
            pill_outline = t["human_highlight"]
        else:
            txt = "ROBOT'S TURN (YELLOW)"
            dot_color = t["ai_coin"]
            pill_outline = t["ai_highlight"]

        # Rounded pill with state border
        rounded_rect(self.status_bar_canvas, px1, py1, px2, py2, radius=(py2 - py1) // 2,
                     fill=t["status_bg"], outline=pill_outline, width=1)

        # Indicator dot
        cx = px1 + 24
        cy = h / 2

        # Soft pulsing glow when thinking
        if self.is_thinking:
            pulse_rad = 5 + (self.thinking_anim_step % 4) * 0.9
            self.status_bar_canvas.create_oval(
                cx - pulse_rad - 2, cy - pulse_rad - 2,
                cx + pulse_rad + 2, cy + pulse_rad + 2,
                fill="", outline=dot_color, width=1
            )

        self.status_bar_canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=dot_color, outline="")

        # Text
        self.status_bar_canvas.create_text(
            w / 2, cy, text=txt, fill=t["text_primary"],
            font=font_spec(FONT_SIZES["body"], "bold")
        )

    def _start_thinking_pulse(self):
        """Start gentle pulsing animation on the status banner thinking dot."""
        if not self.thinking_timer:
            self._step_thinking_pulse()

    def _step_thinking_pulse(self):
        if self.is_thinking:
            self.thinking_anim_step = (self.thinking_anim_step + 1) % 8
            self._draw_status_banner()
            self.thinking_timer = self.root.after(140, self._step_thinking_pulse)
        else:
            self.thinking_timer = None

    def _stop_thinking_pulse(self):
        if self.thinking_timer:
            try:
                self.root.after_cancel(self.thinking_timer)
            except Exception:
                pass
            self.thinking_timer = None
        self.thinking_anim_step = 0

    # -------------------------------------------------------------------------
    # Board Geometry & Dynamic Scaling
    # -------------------------------------------------------------------------
    def _on_canvas_resize_debounced(self, event):
        """Debounce resize calculations to guarantee smooth window scaling."""
        if self.resize_debounce_id:
            self.root.after_cancel(self.resize_debounce_id)
        self.resize_debounce_id = self.root.after(16, lambda: self._recalculate_board_dimensions(event.width, event.height))

    def _recalculate_board_dimensions(self, canvas_w, canvas_h):
        """Calculate maximum undistorted cell size and centered offsets."""
        avail_w = max(canvas_w - 48, 160)
        avail_h = max(canvas_h - 70, 140)

        size_w = avail_w / COLS
        size_h = avail_h / (ROWS + 0.8)

        self.cell_size = max(min(size_w, size_h), 24)

        board_w = self.cell_size * COLS
        board_h = self.cell_size * ROWS

        self.board_offset_x = (canvas_w - board_w) / 2
        self.board_offset_y = max((canvas_h - board_h) / 2 + self.cell_size * 0.35, self.cell_size * 0.8)

        self._draw_board()

    def _get_cell_center(self, r, c):
        """Return (cx, cy) pixel center for cell row r and col c."""
        cx = self.board_offset_x + (c + 0.5) * self.cell_size
        cy = self.board_offset_y + (r + 0.5) * self.cell_size
        return cx, cy

    def _get_col_from_x(self, x):
        """Map canvas X pixel coordinate to column index 0..6."""
        if x < self.board_offset_x:
            return None
        col = int((x - self.board_offset_x) // self.cell_size)
        if 0 <= col < COLS:
            return col
        return None

    # -------------------------------------------------------------------------
    # Board Canvas Drawing
    # -------------------------------------------------------------------------
    def _draw_board(self):
        """Render Connect 4 board, layered bevels, slots, 3D coins, and animations."""
        self.canvas.delete("all")
        t = self.theme
        cs = self.cell_size
        radius = cs * 0.40

        board_left = self.board_offset_x
        board_top = self.board_offset_y
        board_right = board_left + COLS * cs
        board_bottom = board_top + ROWS * cs

        # 1. Multi-layered Soft Board Drop Shadow
        rounded_rect(self.canvas, board_left + 6, board_top + 10,
                     board_right + 6, board_bottom + 10, radius=20,
                     fill=t.get("board_shadow", "#030712"), outline="", width=0)

        # 2. Outer Board Rim & Body Bezel
        rounded_rect(self.canvas, board_left - 10, board_top - 10,
                     board_right + 10, board_bottom + 10, radius=20,
                     fill=t["board_rim"], outline="", width=0)
        rounded_rect(self.canvas, board_left, board_top,
                     board_right, board_bottom, radius=16,
                     fill=t["board_bg"], outline="", width=0)

        # Lower board gradient layer
        rounded_rect(self.canvas, board_left, board_top + (board_bottom - board_top) * 0.55,
                     board_right, board_bottom, radius=16,
                     fill=t["board_bg_gradient"], outline="", width=0)

        # 3. Column Hover Beam Highlight
        if (self.hover_col is not None and not self.game_over and
                not self.is_animating and not self.is_thinking and
                self.current_turn == HUMAN and is_valid_move(self.board, self.hover_col)):
            hx1 = board_left + self.hover_col * cs + 2
            hx2 = hx1 + cs - 4
            rounded_rect(
                self.canvas, hx1, board_top + 2, hx2, board_bottom - 2, radius=8,
                fill=t["col_hover_beam"], outline=""
            )

        # 4. Hint Indicator (Pulsing glowing beam & arrow)
        if self.hint_col is not None:
            hx = board_left + (self.hint_col + 0.5) * cs
            pulse_offset = (self.hint_phase % 4) * 1.5
            hy = board_top - cs * 0.48 + pulse_offset
            # Soft glowing cyan beam down the hinted column
            rounded_rect(
                self.canvas,
                board_left + self.hint_col * cs + 3,
                board_top + 3,
                board_left + (self.hint_col + 1) * cs - 3,
                board_bottom - 3,
                radius=8,
                fill=t.get("hint_beam", "#0e3a4e" if self.current_theme_name == "dark" else "#e0f2fe"),
                outline=""
            )
            # Glowing cyan arrow with stem
            self.canvas.create_polygon(
                hx, hy + cs * 0.42,
                hx - cs * 0.22, hy + cs * 0.10,
                hx - cs * 0.08, hy + cs * 0.10,
                hx - cs * 0.08, hy - cs * 0.10,
                hx + cs * 0.08, hy - cs * 0.10,
                hx + cs * 0.08, hy + cs * 0.10,
                hx + cs * 0.22, hy + cs * 0.10,
                fill=t["hint_arrow"], outline=t["hint_col"], width=2
            )
            self.canvas.create_oval(
                hx - 4, hy + cs * 0.40,
                hx + 4, hy + cs * 0.48,
                fill=t["hint_col"], outline=""
            )

        # 5. Hover Ghost Coin
        if (self.hover_col is not None and not self.game_over and
                not self.is_animating and not self.is_thinking and
                self.current_turn == HUMAN and is_valid_move(self.board, self.hover_col)):
            hcx = board_left + (self.hover_col + 0.5) * cs
            hcy = board_top - cs * 0.45
            self.canvas.create_oval(
                hcx - radius, hcy - radius,
                hcx + radius, hcy + radius,
                fill=t["human_ghost"], outline=""
            )
            self.canvas.create_arc(
                hcx - radius + 2, hcy - radius + 2,
                hcx + radius - 2, hcy + radius - 2,
                start=45, extent=125,
                fill="", outline=t["human_highlight"], width=2, style="arc"
            )

        # 6. Slots and Static Coins
        for r in range(ROWS):
            for c in range(COLS):
                cx, cy = self._get_cell_center(r, c)
                piece = self.board[r][c]
                is_win = self.winning_cells and (r, c) in self.winning_cells

                if piece == EMPTY:
                    # Slot Inner Shadow & Specular Rim Effect
                    self.canvas.create_oval(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        fill=t["cell_empty"], outline=t["cell_rim"], width=2
                    )
                    # Upper crescent inner shadow
                    self.canvas.create_arc(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        start=35, extent=110,
                        fill="", outline=t["cell_inner_shadow"], width=2, style="arc"
                    )
                    # Lower crescent specular bevel rim
                    self.canvas.create_arc(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        start=215, extent=110,
                        fill="", outline=t.get("cell_highlight", "#1e293b"), width=1, style="arc"
                    )
                else:
                    self._draw_3d_coin(cx, cy, radius, piece)

                    # Winning coin pulse rings
                    if is_win:
                        pulse_expand = (self.pulse_phase % 4) * 2.0
                        self.canvas.create_oval(
                            cx - radius - 4 - pulse_expand, cy - radius - 4 - pulse_expand,
                            cx + radius + 4 + pulse_expand, cy + radius + 4 + pulse_expand,
                            fill="", outline=t["win_glow"], width=3
                        )
                        self.canvas.create_oval(
                            cx - radius - 1, cy - radius - 1,
                            cx + radius + 1, cy + radius + 1,
                            fill="", outline=t["win_ring"], width=2
                        )

        # 7. Winning Line Through 4 Coins
        if self.winning_cells and len(self.winning_cells) == 4:
            c1x, c1y = self._get_cell_center(self.winning_cells[0][0], self.winning_cells[0][1])
            c4x, c4y = self._get_cell_center(self.winning_cells[3][0], self.winning_cells[3][1])
            # Soft glow underlay
            self.canvas.create_line(c1x, c1y, c4x, c4y, fill=t["win_glow"], width=8, capstyle="round")
            # Solid core line
            self.canvas.create_line(c1x, c1y, c4x, c4y, fill=t["win_line"], width=4, capstyle="round")

        # 8. Animated Dropping Coin
        if self.is_animating and self.anim_col is not None and self.anim_current_y is not None:
            acx = board_left + (self.anim_col + 0.5) * cs
            acy = self.anim_current_y
            self._draw_3d_coin(acx, acy, radius, self.anim_player)

        # 9. Clean Column Numbers Along Bottom
        for c in range(COLS):
            cx = board_left + (c + 0.5) * cs
            cy = board_bottom + cs * 0.28
            self.canvas.create_text(
                cx, cy, text=str(c + 1), fill=t["text_muted"],
                font=font_spec(max(int(cs * 0.22), 8), "bold")
            )

        # 10. Confetti Overlay
        if self.confetti_particles:
            for p in self.confetti_particles:
                self.canvas.create_rectangle(
                    p["x"], p["y"], p["x"] + p["size"], p["y"] + p["size"],
                    fill=p["color"], outline=""
                )

    def _draw_3d_coin(self, cx, cy, radius, player):
        """Render coin with high-fidelity 3D spherical highlights, emboss, and shaded rim."""
        t = self.theme
        is_human = (player == HUMAN)
        body_col = t["human_coin"] if is_human else t["ai_coin"]
        high_col = t["human_highlight"] if is_human else t["ai_highlight"]
        shad_col = t["human_shadow"] if is_human else t["ai_shadow"]

        # 1. Subtle drop shadow under coin
        self.canvas.create_oval(
            cx - radius + 1, cy - radius + 2,
            cx + radius + 1, cy + radius + 2,
            fill=t.get("shadow", "#030712"), outline=""
        )

        # 2. Coin base body with outer rim outline
        self.canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            fill=body_col, outline=shad_col, width=1
        )
        # 3. Top-left specular gloss arc
        self.canvas.create_arc(
            cx - radius + 2, cy - radius + 2,
            cx + radius - 2, cy + radius - 2,
            start=45, extent=125,
            fill="", outline=high_col, width=3, style="arc"
        )
        # 4. Bottom-right dark rim shadow arc
        self.canvas.create_arc(
            cx - radius + 2, cy - radius + 2,
            cx + radius - 2, cy + radius - 2,
            start=225, extent=125,
            fill="", outline=shad_col, width=2, style="arc"
        )
        # 5. Concentric inner groove ring
        in_r = radius * 0.58
        self.canvas.create_oval(
            cx - in_r, cy - in_r,
            cx + in_r, cy + in_r,
            fill="", outline=high_col, width=1
        )
        # 6. Center embossed core button
        core_r = radius * 0.28
        self.canvas.create_oval(
            cx - core_r, cy - core_r,
            cx + core_r, cy + core_r,
            fill=high_col, outline=""
        )
        self.canvas.create_oval(
            cx - core_r + 1, cy - core_r + 1,
            cx + core_r - 1, cy + core_r - 1,
            fill=body_col, outline=""
        )

    # -------------------------------------------------------------------------
    # Mouse Event Handling
    # -------------------------------------------------------------------------
    def _on_canvas_motion(self, event):
        """Update hover preview beam and robot gaze tracking."""
        self._record_user_action()
        if self.game_over or self.is_animating or self.is_thinking:
            return
        col = self._get_col_from_x(event.x)
        if col != self.hover_col:
            self.hover_col = col
            self.avatar.set_hover_col(col)
            self._draw_board()

    def _on_canvas_leave(self, event):
        """Clear hover coin when cursor leaves board."""
        if self.hover_col is not None:
            self.hover_col = None
            self.avatar.set_hover_col(None)
            self._draw_board()

    def _on_canvas_click(self, event):
        """Handle human clicking a column."""
        self._record_user_action()
        if self.game_over or self.is_animating or self.is_thinking:
            return
        if self.current_turn != HUMAN:
            return

        col = self._get_col_from_x(event.x)
        if col is None or not is_valid_move(self.board, col):
            return

        self._clear_hint()
        self._start_coin_animation(col, HUMAN)

    # -------------------------------------------------------------------------
    # Tactile Coin-Drop Physics & Animation
    # -------------------------------------------------------------------------
    def _start_coin_animation(self, col, player):
        """Initialize gravity fall with bounce physics."""
        self.is_animating = True
        self.anim_col = col
        self.anim_player = player
        self.anim_target_row = get_bottom_empty_row(self.board, col)

        _, target_y = self._get_cell_center(self.anim_target_row, col)
        start_y = self.board_offset_y - self.cell_size * 0.45
        self.anim_current_y = start_y
        self.anim_velocity = max(self.cell_size * 0.22, 10)
        self.anim_bouncing = False

        self._play_sound("drop")
        self._step_drop_animation(target_y)

    def _step_drop_animation(self, target_y):
        """Advance drop frame with subtle physical bounce upon landing."""
        if not self.is_animating:
            return

        self.anim_current_y += self.anim_velocity
        self.anim_velocity += 2.4  # Gravity acceleration

        if not self.anim_bouncing and self.anim_current_y >= target_y:
            # First impact -> trigger small tactile bounce
            self.anim_current_y = target_y
            self.anim_velocity = -max(self.cell_size * 0.12, 6.0)
            self.anim_bouncing = True
            self._play_sound("bounce")
            self._draw_board()
            self.root.after(18, lambda: self._step_drop_animation(target_y))
        elif self.anim_bouncing and self.anim_current_y >= target_y:
            # Settled after bounce
            self.anim_current_y = target_y
            self._finish_coin_animation()
        else:
            self._draw_board()
            self.root.after(18, lambda: self._step_drop_animation(target_y))

    def _finish_coin_animation(self):
        """Complete move placement, update state, and check win conditions."""
        col = self.anim_col
        player = self.anim_player

        drop_piece(self.board, col, player)
        self.move_history.append((col, player))

        self.is_animating = False
        self.anim_col = None
        self.anim_player = None
        self.anim_current_y = None

        is_over, winner, win_coords = is_terminal(self.board)

        if is_over:
            self._handle_game_over(winner, win_coords)
            return

        # Advance turn
        self.current_turn = AI if player == HUMAN else HUMAN
        self._draw_status_banner()
        self._draw_board()

        if self.current_turn == AI:
            # Let UI redraw before AI computation starts
            diff = self.difficulty_var.get()
            self._say(f"thinking_{diff.lower()}", "thinking")
            self.root.after(40, self._run_ai_turn)
        else:
            # Human's turn
            self.avatar.set_expression("neutral")

    # -------------------------------------------------------------------------
    # Game Over Celebrations & Telemetry
    # -------------------------------------------------------------------------
    def _handle_game_over(self, winner, win_coords):
        """Trigger victory/draw animations, sounds, and scoreboard update."""
        self.game_over = True
        self.winning_cells = win_coords

        if winner == HUMAN:
            self.scores["human"] += 1
            self._say("human_wins", "sad")
            self._play_sound("win")
            self._start_confetti()
        elif winner == AI:
            self.scores["ai"] += 1
            self._say("ai_wins", "smug")
            self._play_sound("win")
        else:
            self.scores["draws"] += 1
            self._say("draw", "neutral")
            self._play_sound("draw")

        self._start_winning_pulse()
        self._update_scoreboard_display()
        self._draw_status_banner()
        self._draw_board()

        # Trigger random victory video inside Opponent card (draw plays no video)
        if winner in (HUMAN, AI):
            self._show_video(winner)

    def _start_winning_pulse(self):
        """Animate glowing pulse rings on the 4 winning coins."""
        if not self.pulse_timer and self.winning_cells:
            self._step_winning_pulse()

    def _step_winning_pulse(self):
        if self.game_over and self.winning_cells:
            self.pulse_phase = (self.pulse_phase + 1) % 8
            self._draw_board()
            self.pulse_timer = self.root.after(160, self._step_winning_pulse)

    def _stop_winning_pulse(self):
        if self.pulse_timer:
            self.root.after_cancel(self.pulse_timer)
            self.pulse_timer = None

    def _start_confetti(self):
        """Launch 28 colorful confetti particles on human victory."""
        palette = ["#f43f5e", "#fbbf24", "#38bdf8", "#34d399", "#818cf8", "#f472b6"]
        self.confetti_particles = []
        w = max(self.canvas.winfo_width(), 400)
        for _ in range(32):
            self.confetti_particles.append({
                "x": random.randint(20, w - 20),
                "y": random.randint(-80, 0),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(2.5, 5.0),
                "size": random.randint(5, 9),
                "color": random.choice(palette)
            })
        self._step_confetti(0)

    def _step_confetti(self, frame):
        if frame > 70 or not self.game_over:
            self.confetti_particles = []
            self._draw_board()
            return

        h = self.canvas.winfo_height()
        for p in self.confetti_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] > h:
                p["y"] = -10

        self._draw_board()
        self.confetti_timer = self.root.after(30, lambda: self._step_confetti(frame + 1))

    # -------------------------------------------------------------------------
    # AI Execution
    # -------------------------------------------------------------------------
    def _run_ai_turn(self):
        """Calculate optimal move and launch computer's coin drop."""
        if self.game_over or self.current_turn != AI:
            return

        self.is_thinking = True
        self._start_thinking_pulse()
        self._draw_status_banner()
        self.root.update_idletasks()

        depth_map = {"Easy": 1, "Medium": 3, "Hard": 5}
        depth = depth_map.get(self.difficulty_var.get(), 3)
        use_ab = (self.algorithm_var.get() == "Alpha-Beta")

        col, nodes, elapsed = best_move(self.board, depth, use_ab, AI)
        self.is_thinking = False
        self._stop_thinking_pulse()

        if col is not None:
            time_ms = elapsed * 1000
            mode_tag = f"{'Alpha-Beta' if use_ab else 'Minimax'} (d{depth})"
            self.last_ai_stats = {
                "col": f"Col {col + 1} (idx {col})",
                "nodes": f"{nodes:,}",
                "time_ms": f"{time_ms:.1f} ms",
                "mode": mode_tag,
                "nodes_num": nodes,
                "mm_ref_nodes": 0
            }
            self._update_telemetry_display()

            # Random flavor commentary
            if use_ab and depth >= 3 and random.random() < 0.65:
                # Approximate minimax benchmark reference
                ref_nodes = 400 if depth == 3 else 19600
                saved = max(ref_nodes - nodes, 0)
                pct = (saved / ref_nodes) * 100 if ref_nodes > 0 else 0
                pruning_msg = get_pruning_message(saved, pct)
                self._say("", "smug", custom_msg=pruning_msg)
            else:
                self._say("ai_good_move", "happy")

            self._start_coin_animation(col, AI)

    def _update_scoreboard_display(self):
        """Update scoreboard labels and highlight current leader."""
        t = self.theme
        h = self.scores["human"]
        a = self.scores["ai"]
        d = self.scores["draws"]

        self.lbl_score_num_you.configure(text=str(h))
        self.lbl_score_num_ai.configure(text=str(a))
        self.lbl_score_num_draws.configure(text=str(d))

        # Highlight current leader
        if h > a:
            self.lbl_score_tag_you.configure(text="★ You (Lead)", fg=t["human_coin"])
            self.lbl_score_tag_ai.configure(text="● Robot", fg=t["text_secondary"])
        elif a > h:
            self.lbl_score_tag_you.configure(text="● You", fg=t["text_secondary"])
            self.lbl_score_tag_ai.configure(text="★ Robot (Lead)", fg=t["ai_coin"])
        else:
            self.lbl_score_tag_you.configure(text="● You", fg=t["human_coin"])
            self.lbl_score_tag_ai.configure(text="● Robot", fg=t["ai_coin"])

    def _update_telemetry_display(self):
        """Update last AI move card."""
        s = self.last_ai_stats
        self.telemetry_rows["col"][1].configure(text=s["col"])
        self.telemetry_rows["nodes"][1].configure(text=s["nodes"])
        self.telemetry_rows["time_ms"][1].configure(text=s["time_ms"])
        self.telemetry_rows["mode"][1].configure(text=s["mode"])
        self._draw_telemetry_bar()

    def _draw_telemetry_bar(self):
        """Draw stylized progress bar indicating search effort with rounded track."""
        self.bar_canvas.delete("all")
        t = self.theme
        w = self.bar_canvas.winfo_width()
        h = max(self.bar_canvas.winfo_height(), 10)
        if w < 10:
            w = 200

        self.bar_canvas.configure(bg=t["card_bg"])
        # Subtle rounded track
        rounded_rect(self.bar_canvas, 0, 1, w, h - 1, radius=4,
                     fill=t["bar_bg"], outline=t.get("pill_border", "#1e293b"), width=1)

        # Scale bar logarithmically up to ~20,000 nodes
        nodes = self.last_ai_stats.get("nodes_num", 0)
        if nodes > 0:
            import math
            ratio = min(math.log10(max(nodes, 1)) / math.log10(20000), 1.0)
            bar_w = max(int(w * ratio), 6)
            rounded_rect(self.bar_canvas, 1, 2, bar_w, h - 2, radius=3,
                         fill=t["bar_fill"], outline="", width=0)

    # -------------------------------------------------------------------------
    # Buttons, Settings & Idle Management
    # -------------------------------------------------------------------------
    def _record_user_action(self):
        """Reset idle timer on user interaction."""
        self.last_user_action_time = time.time()

    def _reset_idle_timer(self):
        """Check for user inactivity every 5 seconds."""
        if self.idle_timer:
            self.root.after_cancel(self.idle_timer)
        self.idle_timer = self.root.after(5000, self._check_idle)

    def _check_idle(self):
        """Trigger gentle humorous commentary if human waits > 20s."""
        if not self.game_over and not self.is_thinking and not self.is_animating:
            if self.current_turn == HUMAN:
                elapsed = time.time() - self.last_user_action_time
                if elapsed >= 20.0:
                    self._say("idle", "thinking")
                    self.last_user_action_time = time.time()
        self._reset_idle_timer()

    def _on_difficulty_changed(self):
        """Update difficulty subtitle dynamically."""
        diff = self.difficulty_var.get()
        flavors = {
            "Easy": "Warm-up (depth 1)",
            "Medium": "Now it is personal (depth 3)",
            "Hard": "Prepare to be outsmarted (depth 5)"
        }
        self.lbl_diff_flavor.configure(text=flavors.get(diff, ""))
        self._on_setting_changed()

    def _on_setting_changed(self):
        """Restart cleanly if settings are modified on an empty board."""
        self._record_user_action()
        if hasattr(self, "video_player") and self.video_player is not None and self.video_player.is_active():
            self._restore_robot_view()
        if len(self.move_history) == 0:
            self.new_game()

    def new_game(self):
        """Start fresh game without closing app."""
        if self.is_animating:
            return

        # Return to robot immediately if video is active
        if hasattr(self, "video_player") and self.video_player is not None and self.video_player.is_active():
            self._restore_robot_view()

        self._record_user_action()
        self._stop_winning_pulse()
        self._stop_thinking_pulse()
        self._clear_hint()
        if self.confetti_timer:
            try:
                self.root.after_cancel(self.confetti_timer)
            except Exception:
                pass
            self.confetti_timer = None
        self.confetti_particles = []

        self.board = create_board()
        self.game_over = False
        self.winning_cells = None
        self.move_history.clear()
        self.hint_col = None
        self.hover_col = None

        if self.first_player_var.get() == "Human":
            self.current_turn = HUMAN
            self._say("game_start_human", "happy")
            self._draw_status_banner()
            self._draw_board()
        else:
            self.current_turn = AI
            self._say("game_start_ai", "smug")
            self._draw_status_banner()
            self._draw_board()
            diff = self.difficulty_var.get()
            self.root.after(400, lambda: self._say(f"thinking_{diff.lower()}", "thinking"))
            self.root.after(600, self._run_ai_turn)

    def undo_move(self):
        """Undo human move and computer reply (2 plies)."""
        if self.is_animating or self.is_thinking:
            return

        # Return to robot immediately if video is active
        if hasattr(self, "video_player") and self.video_player is not None and self.video_player.is_active():
            self._restore_robot_view()

        self._record_user_action()
        if not self.move_history:
            self.speech_text = "Nothing to undo yet! Make a move first."
            self._draw_speech_bubble()
            return

        self._stop_winning_pulse()
        self.game_over = False
        self.winning_cells = None

        # Revert moves
        if self.move_history[-1][1] == AI:
            ai_col, _ = self.move_history.pop()
            undo_piece(self.board, ai_col)
            if self.move_history and self.move_history[-1][1] == HUMAN:
                human_col, _ = self.move_history.pop()
                undo_piece(self.board, human_col)
        elif self.move_history[-1][1] == HUMAN:
            human_col, _ = self.move_history.pop()
            undo_piece(self.board, human_col)

        self.current_turn = HUMAN
        self.hint_col = None
        self._say("undo_used", "surprised")
        self._draw_status_banner()
        self._draw_board()

    def request_hint(self):
        """Highlight optimal column for human with gentle pulse."""
        if self.game_over or self.is_animating or self.is_thinking:
            return
        if self.current_turn != HUMAN:
            return
        # Prevent double-click while hint is already computing
        if getattr(self, "_hint_computing", False):
            return

        self._record_user_action()
        self._hint_computing = True

        # Show "calculating" feedback immediately
        self._say("hint_used", "thinking")
        self._draw_status_banner()

        depth_map = {"Easy": 1, "Medium": 3, "Hard": 5}
        depth = depth_map.get(self.difficulty_var.get(), 3)

        def _compute():
            try:
                result = best_move(self.board, depth, use_alphabeta=True, player=HUMAN)
                hint_col = result[0] if result else None
            except Exception:
                hint_col = None
            self.root.after(0, lambda: _apply(hint_col))

        def _apply(hint_col):
            self._hint_computing = False
            if hint_col is not None:
                self.hint_col = hint_col
                self._start_hint_pulse()
                if self.hint_dismiss_timer:
                    try:
                        self.root.after_cancel(self.hint_dismiss_timer)
                    except Exception:
                        pass
                self.hint_dismiss_timer = self.root.after(3500, self._clear_hint)

        threading.Thread(target=_compute, daemon=True).start()

    def _start_hint_pulse(self):
        if self.hint_timer:
            try:
                self.root.after_cancel(self.hint_timer)
            except Exception:
                pass
            self.hint_timer = None
        self.hint_phase = 0
        self._step_hint_pulse()

    def _step_hint_pulse(self):
        if self.hint_col is None:
            return
        self.hint_phase = (self.hint_phase + 1) % 8
        self._draw_board()
        self.hint_timer = self.root.after(140, self._step_hint_pulse)

    def _clear_hint(self):
        if getattr(self, "hint_dismiss_timer", None):
            try:
                self.root.after_cancel(self.hint_dismiss_timer)
            except Exception:
                pass
            self.hint_dismiss_timer = None
        if self.hint_timer:
            try:
                self.root.after_cancel(self.hint_timer)
            except Exception:
                pass
            self.hint_timer = None
        if self.hint_col is not None:
            self.hint_col = None
            self._draw_board()

    def reset_scores(self):
        """Zero out session scores."""
        self._record_user_action()
        if hasattr(self, "video_player") and self.video_player is not None and self.video_player.is_active():
            self._restore_robot_view()
        self.scores = {"human": 0, "ai": 0, "draws": 0}
        self._update_scoreboard_display()

    # -------------------------------------------------------------------------
    # Compare Mode Modal
    # -------------------------------------------------------------------------
    def show_comparison(self):
        """Run Minimax vs Alpha-Beta and show comparative bar chart dialog."""
        if self.is_animating or self.is_thinking:
            return

        self._record_user_action()
        depth_map = {"Easy": 1, "Medium": 3, "Hard": 5}
        depth = depth_map.get(self.difficulty_var.get(), 3)
        self._say("compare_ai", "thinking")

        board_copy = copy_board(self.board)
        col_mm, nodes_mm, time_mm = best_move(board_copy, depth, False, self.current_turn)
        col_ab, nodes_ab, time_ab = best_move(board_copy, depth, True, self.current_turn)

        savings = 0.0
        if nodes_mm > 0:
            savings = ((nodes_mm - nodes_ab) / nodes_mm) * 100.0

        self._open_comparison_modal(depth, col_mm, nodes_mm, time_mm,
                                    col_ab, nodes_ab, time_ab, savings)

    def _open_comparison_modal(self, depth, col_mm, nodes_mm, time_mm,
                               col_ab, nodes_ab, time_ab, savings):
        """Create styled comparative dialog with relative bars centered over parent."""
        t = self.theme
        dlg = tk.Toplevel(self.root)
        dlg.title("Algorithm Benchmark: Minimax vs Alpha-Beta")
        dlg.resizable(False, False)
        dlg.configure(bg=t["panel_bg"])
        dlg.transient(self.root)
        dlg.grab_set()

        width, height = 580, 440
        self.root.update_idletasks()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = max(0, rx + (rw - width) // 2)
        y = max(0, ry + (rh - height) // 2)
        dlg.geometry(f"{width}x{height}+{x}+{y}")
        dlg.bind("<Escape>", lambda e: dlg.destroy())

        # Header
        h_frame = tk.Frame(dlg, bg=t["panel_bg"], padx=SPACING["xl"], pady=SPACING["lg"])
        h_frame.pack(fill="x")
        tk.Label(
            h_frame, text=f"ALGORITHM BENCHMARK (DEPTH {depth})",
            font=font_spec(FONT_SIZES["title"], "bold"), bg=t["panel_bg"], fg=t["text_primary"]
        ).pack(anchor="w")
        tk.Label(
            h_frame, text="Real-time performance comparison on the current board position.",
            font=font_spec(FONT_SIZES["caption"]), bg=t["panel_bg"], fg=t["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # Comparative Chart Card
        chart_card = tk.Frame(
            dlg, bg=t["card_bg"], padx=SPACING["xl"], pady=SPACING["md"],
            highlightthickness=1, highlightbackground=t.get("card_border", "#334155")
        )
        chart_card.pack(fill="x", padx=SPACING["xl"], pady=SPACING["sm"])

        bar_max_w = 480
        # Minimax Row
        tk.Label(chart_card, text=f"Minimax: {nodes_mm:,} nodes visited ({time_mm*1000:.1f} ms) → Picked Col {col_mm+1}",
                 font=font_spec(FONT_SIZES["small"], "bold"), bg=t["card_bg"], fg=t["text_primary"]).pack(anchor="w")
        c_mm = tk.Canvas(chart_card, height=14, bg=t["card_bg"], highlightthickness=0)
        c_mm.pack(fill="x", pady=(4, 14))
        rounded_rect(c_mm, 0, 1, bar_max_w, 13, radius=5, fill=t["bar_bg"], outline="", width=0)
        rounded_rect(c_mm, 0, 1, bar_max_w, 13, radius=5, fill=t["human_coin"], outline="", width=0)

        # Alpha-Beta Row
        tk.Label(chart_card, text=f"Alpha-Beta: {nodes_ab:,} nodes visited ({time_ab*1000:.1f} ms) → Picked Col {col_ab+1}",
                 font=font_spec(FONT_SIZES["small"], "bold"), bg=t["card_bg"], fg=t["text_primary"]).pack(anchor="w")
        c_ab = tk.Canvas(chart_card, height=14, bg=t["card_bg"], highlightthickness=0)
        c_ab.pack(fill="x", pady=(4, 10))
        rounded_rect(c_ab, 0, 1, bar_max_w, 13, radius=5, fill=t["bar_bg"], outline="", width=0)
        ratio = (nodes_ab / max(nodes_mm, 1))
        ab_bar_w = max(bar_max_w * ratio, 8)
        rounded_rect(c_ab, 0, 1, ab_bar_w, 13, radius=5, fill=t["win_glow"], outline="", width=0)

        # Badges Summary Frame
        badges_row = tk.Frame(dlg, bg=t["panel_bg"], padx=SPACING["xl"], pady=SPACING["sm"])
        badges_row.pack(fill="x")

        # Move Match Badge
        same_move = (col_mm == col_ab)
        badge_txt = "Move Match: CONFIRMED (Identical Column)" if same_move else "Move Discrepancy"
        badge_bg = t["card_bg"]
        badge_fg = t["win_glow"] if same_move else t["human_coin"]
        badge_border = t.get("card_border", "#334155")

        lbl_badge = tk.Label(
            badges_row, text=badge_txt, font=font_spec(FONT_SIZES["small"], "bold"),
            bg=badge_bg, fg=badge_fg, padx=12, pady=6, highlightthickness=1,
            highlightbackground=badge_border, relief="flat"
        )
        lbl_badge.pack(anchor="w", pady=(0, 6))

        # Efficiency Badge
        lbl_eff = tk.Label(
            badges_row,
            text=f"Pruning Efficiency: {savings:.1f}% search tree nodes eliminated.",
            font=font_spec(FONT_SIZES["body"]), bg=t["panel_bg"], fg=t["text_primary"]
        )
        lbl_eff.pack(anchor="w")

        # Close Button
        btn_box = tk.Frame(dlg, bg=t["panel_bg"], pady=SPACING["md"])
        btn_box.pack(fill="x")
        btn_close = RoundedButton(btn_box, text="Close", command=dlg.destroy,
                                  width=110, height=34, theme=t)
        btn_close.pack(anchor="center")
