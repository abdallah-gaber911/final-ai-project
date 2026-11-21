"""
Main entry point for Connect 4 application.
Launches the tkinter graphical user interface with High-DPI awareness
and an in-memory generated branded window icon.
"""

import sys
import os
import tkinter as tk

# Safe High-DPI Awareness on Windows
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Ensure current directory is accessible for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from gui import Connect4App


def set_dynamic_app_icon(root):
    """Dynamically generate a 32x32 Connect 4 coin icon in-memory without external files."""
    try:
        from PIL import Image, ImageDraw, ImageTk
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Red coin with highlight rim
        draw.ellipse([2, 4, 20, 22], fill="#f43f5e", outline="#fb7185", width=1)
        # Yellow coin with highlight rim
        draw.ellipse([12, 10, 30, 28], fill="#fbbf24", outline="#fef08a", width=1)
        # Center sparkling energy core
        draw.ellipse([13, 13, 19, 19], fill="#ffffff")
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(True, photo)
        root._icon_photo = photo
    except Exception:
        pass


def main():
    root = tk.Tk()
    root.title("Connect 4 - AI Minimax & Alpha-Beta Engine")
    root.geometry("1140x760")
    root.minsize(1000, 680)

    # Apply dynamic icon
    set_dynamic_app_icon(root)

    # Instantiate the application
    app = Connect4App(root)

    root.mainloop()


if __name__ == "__main__":
    main()
