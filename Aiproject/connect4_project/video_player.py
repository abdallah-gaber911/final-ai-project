"""
Video Player widget and helper utilities for Connect 4.
Displays victory videos inside the Opponent robot card upon game completion.

Features:
- Non-blocking frame-by-frame decoding using OpenCV and Tkinter after() callbacks
- Aspect-ratio preserving letterboxing inside the opponent card
- Play/Pause and Skip/Close controls styled with the application theme
- Audio playback support via cached wav + winsound or ffplay subprocess
- Pure selection and discovery utilities (folder resolution, random pick without repeat)
- Graceful degradation when opencv-python or Pillow are not installed
"""

import os
import sys
import time
import random
import hashlib
import tempfile
import subprocess
import tkinter as tk

# Safe imports for OpenCV and Pillow
try:
    import cv2
    from PIL import Image, ImageTk
    HAS_VIDEO_LIBS = True
except ImportError:
    HAS_VIDEO_LIBS = False
    print(
        "[Connect 4] Video libraries not found (opencv-python / Pillow). "
        "Victory videos disabled; install with: pip install -r requirements.txt"
    )

# Audio playback availability
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Try importing imageio_ffmpeg for background audio extraction if available
try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None

try:
    from widgets import RoundedButton
    from theme import font_spec, FONT_SIZES
except ImportError:
    from connect4.widgets import RoundedButton
    from connect4.theme import font_spec, FONT_SIZES

SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")


# =============================================================================
# Pure Discovery & Selection Utilities (Tested headlessly)
# =============================================================================

def get_video_files(folder_path):
    """
    Discover all supported video files within the specified folder.

    Args:
        folder_path (str): Directory path to search.

    Returns:
        list[str]: Sorted list of absolute file paths matching supported extensions.
    """
    if not folder_path or not os.path.isdir(folder_path):
        return []

    video_files = []
    try:
        for entry in os.listdir(folder_path):
            full_path = os.path.join(folder_path, entry)
            if os.path.isfile(full_path):
                ext = os.path.splitext(entry)[1].lower()
                if ext in SUPPORTED_VIDEO_EXTENSIONS:
                    video_files.append(os.path.abspath(full_path))
    except Exception:
        return []
    return sorted(video_files)


def pick_random_video(video_list, last_video=None):
    """
    Select a random video from video_list, avoiding immediate repetition
    when more than one video is available.

    Args:
        video_list (list[str]): List of video paths.
        last_video (str or None): The path of the video played previously.

    Returns:
        str or None: Selected video path, or None if video_list is empty.
    """
    if not video_list:
        return None
    if len(video_list) == 1:
        return video_list[0]

    # Filter out last_video to prevent back-to-back duplicate playback
    candidates = [v for v in video_list if v != last_video]
    if not candidates:
        candidates = video_list

    return random.choice(candidates)


def find_outcome_folder(outcome, search_roots=None):
    """
    Detect the directory containing victory videos for a specific outcome.
    Auto-detects custom folder names (e.g., 'computer win', 'user win')
    as well as standard 'videos/computer_wins' and 'videos/human_wins'.

    Args:
        outcome (str): 'computer' or 'human' (or 'ai').
        search_roots (list[str] or None): Roots to search from. Defaults to
            [current working directory, script directory, parent directories].

    Returns:
        tuple[str, list[str]]: (folder_path, list_of_video_paths)
    """
    if search_roots is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cwd = os.getcwd()
        parent_dir = os.path.dirname(script_dir)
        # Search order: cwd, script directory, parent of script directory
        roots = []
        for d in [cwd, script_dir, parent_dir]:
            if d and d not in roots and os.path.isdir(d):
                roots.append(d)
        search_roots = roots

    is_computer = str(outcome).lower() in ("computer", "ai", "2")
    if is_computer:
        candidate_names = [
            os.path.join("videos", "computer_wins"),
            "computer win",
            "computer_win",
            "computer_wins",
            "ai_wins",
            "ai win",
            "ai_win"
        ]
        fallback_default = "videos/computer_wins"
    else:
        candidate_names = [
            os.path.join("videos", "human_wins"),
            "user win",
            "user_win",
            "human_wins",
            "human_win",
            "player win",
            "player_win"
        ]
        fallback_default = "videos/human_wins"

    # 1. Search for an existing directory containing supported video files
    for root in search_roots:
        for name in candidate_names:
            target = os.path.abspath(os.path.join(root, name))
            if os.path.isdir(target):
                videos = get_video_files(target)
                if videos:
                    return target, videos

    # 2. Search for any existing directory matching candidates even if empty
    for root in search_roots:
        for name in candidate_names:
            target = os.path.abspath(os.path.join(root, name))
            if os.path.isdir(target):
                return target, []

    # 3. Fallback default directory under the first root
    default_path = os.path.abspath(os.path.join(search_roots[0], fallback_default))
    return default_path, []


# =============================================================================
# VideoPlayer Tkinter Component
# =============================================================================

class VideoPlayer(tk.Frame):
    """
    Canvas-based video player embedded inside the Opponent card.
    Plays victory videos with real-time frame scaling, letterboxing,
    and responsive transport controls (Pause/Play, Skip/Close).
    """

    def __init__(self, master, width=220, height=163, theme=None,
                 on_finish=None, get_sound_enabled=None):
        """
        Initialize VideoPlayer.

        Args:
            master (tk.Widget): Container widget (card_robot.content).
            width (int): Target width matching card width (~220 px).
            height (int): Target height matching avatar + bubble (~163 px).
            theme (dict or None): Current theme palette.
            on_finish (callable or None): Callback invoked when playback ends or is skipped.
            get_sound_enabled (callable or None): Returns True if game sound is enabled.
        """
        self.theme = theme or {}
        bg_col = self.theme.get("card_bg", "#1e293b")
        super().__init__(master, width=width, height=height, bg=bg_col)
        self.pack_propagate(False)

        self.player_width = width
        self.player_height = height
        self.on_finish = on_finish
        self.get_sound_enabled = get_sound_enabled or (lambda: True)

        # Video State
        self.cap = None
        self.is_playing = False
        self.is_paused = False
        self.current_video_path = None
        self.fps = 30.0
        self.total_frames = 0
        self.current_frame_idx = 0
        self.start_playback_time = 0.0
        self.after_id = None
        self.photo_image = None
        self.audio_proc = None
        self.current_audio_wav = None

        # History tracking to avoid back-to-back repeats
        self.last_played_by_outcome = {"computer": None, "human": None}

        # Build UI layout (Video Canvas + Control Row)
        self._build_ui()
        self.set_theme(self.theme)

    def _build_ui(self):
        """Construct the letterboxed video display and transport controls."""
        bg_col = self.theme.get("card_bg", "#1e293b")

        # Video Frame Canvas (height ~134 to leave ~29 for controls = 163 total)
        self.canvas_h = max(self.player_height - 29, 60)
        self.canvas_w = self.player_width
        self.canvas = tk.Canvas(
            self, width=self.canvas_w, height=self.canvas_h,
            bg=bg_col, highlightthickness=0
        )
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Bottom Control Bar
        self.ctrl_frame = tk.Frame(self, height=27, bg=bg_col)
        self.ctrl_frame.pack(side="bottom", fill="x", pady=(2, 0))
        self.ctrl_frame.pack_propagate(False)

        # Pause / Play Button
        self.btn_pause = RoundedButton(
            self.ctrl_frame, text="Pause", command=self.toggle_pause,
            width=62, height=24, radius=5, theme=self.theme,
            tooltip="Pause or resume playback"
        )
        self.btn_pause.pack(side="left", padx=(2, 4))

        # Time Duration Display
        self.lbl_time = tk.Label(
            self.ctrl_frame, text="0:00 / 0:00",
            font=font_spec(FONT_SIZES["caption"]), bg=bg_col,
            fg=self.theme.get("text_muted", "#64748b")
        )
        self.lbl_time.pack(side="left", expand=True)

        # Skip / Close Button
        self.btn_skip = RoundedButton(
            self.ctrl_frame, text="Skip ✕", command=self._on_skip_clicked,
            width=62, height=24, radius=5, theme=self.theme,
            tooltip="Skip video and return to robot"
        )
        self.btn_skip.pack(side="right", padx=(4, 2))

    def _on_canvas_resize(self, event):
        """Update canvas internal dimensions when card resizes."""
        if event.width > 10 and event.height > 10:
            self.canvas_w = event.width
            self.canvas_h = event.height

    def set_theme(self, theme):
        """Update colors of container, video canvas, and transport buttons."""
        self.theme = theme or {}
        bg_col = self.theme.get("card_bg", "#1e293b")
        text_muted = self.theme.get("text_muted", "#64748b")

        self.configure(bg=bg_col)
        if hasattr(self, "canvas"):
            self.canvas.configure(bg=bg_col)
        if hasattr(self, "ctrl_frame"):
            self.ctrl_frame.configure(bg=bg_col)
        if hasattr(self, "lbl_time"):
            self.lbl_time.configure(bg=bg_col, fg=text_muted)
        if hasattr(self, "btn_pause"):
            self.btn_pause.set_theme(self.theme)
        if hasattr(self, "btn_skip"):
            self.btn_skip.set_theme(self.theme)

    def is_active(self):
        """Check whether video playback is currently active or open."""
        return self.is_playing or (self.cap is not None)

    # -------------------------------------------------------------------------
    # Playback Control
    # -------------------------------------------------------------------------

    def play_random(self, outcome):
        """
        Discover victory videos for the specified outcome and play one at random,
        avoiding back-to-back repetition.

        Args:
            outcome (str): 'computer' or 'human'.

        Returns:
            bool: True if video started, False otherwise.
        """
        if not HAS_VIDEO_LIBS:
            return False

        key = "computer" if str(outcome).lower() in ("computer", "ai", "2") else "human"
        _, videos = find_outcome_folder(key)

        if not videos:
            return False

        last_vid = self.last_played_by_outcome.get(key)
        picked = pick_random_video(videos, last_vid)
        if not picked:
            return False

        self.last_played_by_outcome[key] = picked
        return self.play(picked)

    def play(self, video_path):
        """
        Open video file and begin non-blocking frame playback.

        Args:
            video_path (str): Full filesystem path to video file.

        Returns:
            bool: True if video opened successfully, False otherwise.
        """
        if not HAS_VIDEO_LIBS or not video_path or not os.path.isfile(video_path):
            return False

        # Clean up any existing playback first
        self.stop(trigger_callback=False)

        try:
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                self.cap.release()
                self.cap = None
                return False

            self.current_video_path = video_path
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0 or self.fps != self.fps:
                self.fps = 30.0

            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.current_frame_idx = 0
            self.is_playing = True
            self.is_paused = False

            # Update button text to 'Pause'
            self._set_button_text(self.btn_pause, "Pause")
            self._update_time_label(0)

            # Start synchronized audio if enabled
            self._start_audio(video_path)

            # Begin frame rendering loop
            self.start_playback_time = time.time()
            self._step_frame()
            return True
        except Exception as err:
            print(f"[Connect 4] Error opening video {video_path}: {err}")
            self.stop(trigger_callback=False)
            return False

    def toggle_pause(self):
        """Toggle between paused and playing states."""
        if not self.is_active():
            return

        if self.is_paused:
            # Resume
            self.is_paused = False
            self._set_button_text(self.btn_pause, "Pause")
            # Recalibrate start time to continue seamless FPS tracking
            self.start_playback_time = time.time() - (self.current_frame_idx / self.fps)
            self._step_frame()
        else:
            # Pause
            self.is_paused = True
            self._set_button_text(self.btn_pause, "▶ Play")
            self._stop_audio()
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None

    def _on_skip_clicked(self):
        """Handler for Skip button: stop immediately and notify callback."""
        self.stop(trigger_callback=True)

    def stop(self, trigger_callback=True):
        """
        Halt playback, cancel timers, release video handle, and reset canvas.

        Args:
            trigger_callback (bool): If True, invokes self.on_finish callback.
        """
        # 1. Cancel pending after() timer
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

        # 2. Halt audio playback
        self._stop_audio()

        # 3. Release OpenCV video handle
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        # 4. Clear frame canvas
        self.photo_image = None
        if hasattr(self, "canvas"):
            self.canvas.delete("all")

        # 5. Reset state flags
        self.is_playing = False
        self.is_paused = False
        self.current_video_path = None
        self.current_frame_idx = 0

        # 6. Trigger finish callback to restore avatar + bubble
        if trigger_callback and self.on_finish:
            try:
                self.on_finish()
            except Exception as err:
                print(f"[Connect 4] Error in on_finish callback: {err}")

    # -------------------------------------------------------------------------
    # Frame Loop & Letterboxing
    # -------------------------------------------------------------------------

    def _step_frame(self):
        """Decode next frame, render letterboxed on canvas, and schedule next step."""
        if not self.is_playing or self.is_paused or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            # Video reached the end -> return cleanly to robot
            self.stop(trigger_callback=True)
            return

        self.current_frame_idx += 1
        self._render_frame(frame)
        self._update_time_label(self.current_frame_idx)

        # Drift-compensated non-blocking scheduling
        target_elapsed = (self.current_frame_idx + 1) / self.fps
        real_elapsed = time.time() - self.start_playback_time
        delay_ms = max(1, int((target_elapsed - real_elapsed) * 1000))

        self.after_id = self.after(delay_ms, self._step_frame)

    def _render_frame(self, frame):
        """
        Scale frame maintaining aspect ratio and center on canvas (letterboxing).
        """
        cw = max(self.canvas.winfo_width(), self.canvas_w, 40)
        ch = max(self.canvas.winfo_height(), self.canvas_h, 40)

        fh, fw = frame.shape[:2]
        scale = min(cw / fw, ch / fh)
        nw = max(int(fw * scale), 1)
        nh = max(int(fh * scale), 1)

        resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)

        # Prevent Python garbage collection of Tk PhotoImage
        self.photo_image = ImageTk.PhotoImage(image=img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.photo_image, anchor="center")

    def _update_time_label(self, frame_idx):
        """Format and update current/total time display."""
        if self.fps <= 0:
            return
        cur_sec = int(frame_idx / self.fps)
        tot_sec = int(self.total_frames / self.fps) if self.total_frames > 0 else 0
        txt = f"{cur_sec // 60}:{cur_sec % 60:02d} / {tot_sec // 60}:{tot_sec % 60:02d}"
        self.lbl_time.configure(text=txt)

    def _set_button_text(self, btn, text):
        """Safely update RoundedButton text."""
        if hasattr(btn, "set_text"):
            btn.set_text(text)
        else:
            btn.text = text
            if hasattr(btn, "_draw"):
                btn._draw()

    # -------------------------------------------------------------------------
    # Audio Handling
    # -------------------------------------------------------------------------

    def set_sound_enabled(self, is_enabled):
        """Update sound state; immediately mute video audio if turned off."""
        if not is_enabled:
            self._stop_audio()

    def _start_audio(self, video_path):
        """Attempt synchronized audio playback for the video."""
        if not self.get_sound_enabled():
            return

        # 1. Try ffplay subprocess if ffplay binary is accessible on PATH
        try:
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", video_path]
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            self.audio_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
            return
        except Exception:
            self.audio_proc = None

        # 2. Try extracting audio track to cached wav and play via winsound (Windows)
        if HAS_WINSOUND and FFMPEG_EXE:
            try:
                h = hashlib.md5(video_path.encode()).hexdigest()
                wav_path = os.path.join(tempfile.gettempdir(), f"c4_audio_{h}.wav")
                if not os.path.isfile(wav_path):
                    cmd = [
                        FFMPEG_EXE, "-y", "-i", video_path, "-vn",
                        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                        wav_path
                    ]
                    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                    subprocess.run(
                        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=flags, timeout=5
                    )
                if os.path.isfile(wav_path):
                    self.current_audio_wav = wav_path
                    winsound.PlaySound(wav_path, winsound.SND_ASYNC | winsound.SND_FILENAME)
            except Exception:
                pass

    def _stop_audio(self):
        """Safely terminate any active audio stream."""
        if self.audio_proc is not None:
            try:
                self.audio_proc.terminate()
                self.audio_proc.kill()
            except Exception:
                pass
            self.audio_proc = None

        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
