"""
Theme color definitions and shared design tokens for Connect 4 GUI.
Provides coordinated modern Dark and Light palettes, layout scale tokens,
corner radii, and cross-platform font detection.

All widgets and canvas renderers retrieve styling tokens from this module.
"""

# =============================================================================
# Design Tokens: Spacing Scale & Corner Radii
# =============================================================================

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "xxl": 24,
}

RADII = {
    "xs": 4,
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 18,
    "full": 999,
}

FONT_SIZES = {
    "micro": 7,
    "caption": 8,
    "body": 9,
    "body_sm": 8,
    "subtitle": 11,
    "title_sm": 12,
    "title": 14,
    "display": 18,
}


# =============================================================================
# Cross-Platform Font Detection
# =============================================================================

_DETECTED_FONTS = {}


def get_font_family(family_type="sans"):
    """
    Return the optimal installed font family name across operating systems.
    Falls back gracefully:
      - sans: Segoe UI (Windows) -> SF Pro Text (macOS) -> Ubuntu -> DejaVu Sans -> Arial
      - mono: Consolas (Windows) -> SF Mono / Menlo (macOS) -> Ubuntu Mono -> Courier New
    """
    if family_type in _DETECTED_FONTS:
        return _DETECTED_FONTS[family_type]

    candidates = {
        "sans": [
            "Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu",
            "DejaVu Sans", "Arial", "sans-serif"
        ],
        "mono": [
            "Consolas", "SF Mono", "Menlo", "Ubuntu Mono",
            "DejaVu Sans Mono", "Courier New", "monospace"
        ]
    }.get(family_type, ["Segoe UI", "Arial"])

    chosen = candidates[-1]
    try:
        import tkinter.font as tkfont
        available = set(tkfont.families())
        for font_name in candidates:
            if font_name in available:
                chosen = font_name
                break
    except Exception:
        chosen = candidates[0]

    _DETECTED_FONTS[family_type] = chosen
    return chosen


def font_spec(size=9, weight="normal", family="sans"):
    """
    Generate a standardized Tkinter font tuple using the detected system font.
    Example: font_spec(10, 'bold') -> ('Segoe UI', 10, 'bold')
    """
    return (get_font_family(family), size, weight)


# =============================================================================
# Color Palettes: Dark & Light (Reviewed for WCAG AA Contrast)
# =============================================================================

THEMES = {
    "dark": {
        "name": "Dark",
        # Window & Panel Surfaces
        "bg": "#0b1120",                  # Deep midnight slate
        "header_bg": "#0f172a",           # Header background
        "header_border": "#1e293b",       # Subtle bottom divider line
        "panel_bg": "#0f172a",            # Side panel surface
        "panel_border": "#1e293b",        # Panel separator
        "card_bg": "#1e293b",             # Card surface
        "card_border": "#334155",         # Clean 1px card outline
        "card_border_subtle": "#1e293b",  # Inset card divider
        "card_hover": "#253349",          # Hover accent

        # Shadows & Focus
        "shadow": "#030712",              # Faux drop shadow
        "header_shadow": "#030712",       # Header bottom shadow
        "focus_ring": "#818cf8",          # Keyboard focus ring

        # Board & Hole Geometry
        "board_bg": "#1e3a8a",            # Deep royal blue board
        "board_bg_gradient": "#172554",   # Lower gradient tone for board body
        "board_rim": "#172554",           # Outer board bezel rim
        "board_shadow": "#030712",         # Soft drop shadow under board
        "cell_empty": "#070d19",          # Deep cutout for empty slots
        "cell_rim": "#0f172a",            # Slot inner border ring
        "cell_inner_shadow": "#030712",   # Inset crescent shadow
        "cell_highlight": "#1e293b",      # Subtle lower specular rim for slots
        "col_hover_beam": "#1e293b",      # Column highlight beam on hover

        # Coins & Highlights (Red / Yellow)
        "human_coin": "#f43f5e",          # Coral red coin body
        "human_highlight": "#fb7185",     # 3D specular highlight arc
        "human_shadow": "#9f1239",        # 3D dark shaded rim
        "human_ghost": "#e11d48",         # Floating preview coin

        "ai_coin": "#fbbf24",             # Warm golden yellow coin body
        "ai_highlight": "#fef08a",        # 3D specular highlight arc
        "ai_shadow": "#b45309",           # 3D dark shaded rim
        "ai_ghost": "#d97706",            # Floating preview coin

        # Winning, Glow & Hints
        "win_glow": "#10b981",            # Emerald glow ring
        "win_ring": "#34d399",            # Inner emerald ring
        "win_line": "#6ee7b7",            # Line through winning 4 coins
        "hint_col": "#06b6d4",            # Cyan hint indicator
        "hint_arrow": "#22d3ee",          # Glowing hint arrow
        "hint_beam": "#0e3a4e",           # Soft cyan column highlight beam

        # Typography (High Contrast WCAG AA)
        "text_primary": "#f8fafc",        # Off-white (12.3:1 on card_bg)
        "text_secondary": "#94a3b8",      # Slate secondary (4.9:1 on card_bg)
        "text_muted": "#8896a6",          # Refined caption slate (4.6:1 on card_bg)
        "text_accent": "#818cf8",         # Indigo accent header
        "danger": "#f43f5e",              # Error / loss accent
        "success": "#10b981",             # Success / win accent
        "warning": "#f59e0b",             # Warning / attention accent

        # Accents & Interactive Controls
        "accent": "#6366f1",              # Electric indigo primary accent
        "accent_hover": "#4f46e5",        # Hover indigo
        "accent_active": "#4338ca",       # Pressed indigo
        "cyan_accent": "#06b6d4",         # Cyan secondary accent

        # Buttons & Segmented Controls
        "pill_bg": "#090d16",             # Segmented track background
        "pill_border": "#1e293b",         # Segmented track border
        "button_subtle": "#1e293b",       # Outlined secondary button
        "button_subtle_border": "#334155",# Outlined secondary button border
        "button_subtle_hover": "#2d3748", # Secondary button hover
        "button_disabled": "#1e293b",     # Disabled button surface
        "button_disabled_text": "#475569",# Disabled button text

        # Toggle Switches
        "switch_track_off": "#334155",    # Track off
        "switch_track_on": "#6366f1",     # Track on
        "switch_knob": "#ffffff",         # Sliding knob

        # Robot Avatar
        "robot_head": "#334155",          # Robot head metal
        "robot_rim": "#475569",           # Robot outline rim
        "robot_eye_glow": "#38bdf8",      # Bright cyan-blue digital eyes
        "robot_eye_pupil": "#0284c7",     # Pupil center
        "robot_antenna": "#64748b",       # Antenna stalk
        "robot_antenna_light": "#f43f5e", # Antenna bulb
        "robot_mouth": "#0284c7",         # Digital mouth line
        "bubble_bg": "#1e293b",           # Speech bubble background
        "bubble_border": "#3b82f6",       # Speech bubble border
        "bubble_text": "#f8fafc",         # Speech bubble text

        # Telemetry, Status & Scoreboard
        "status_bg": "#1e293b",           # Status banner background
        "status_border": "#334155",       # Status banner border
        "badge_bg": "#312e81",            # Indigo pill badge
        "badge_text": "#c7d2fe",          # Indigo badge text
        "bar_bg": "#090d16",              # Telemetry progress bar track
        "bar_fill": "#6366f1",            # Telemetry progress bar fill
        "leader_glow": "#38bdf8",         # Scoreboard leader indicator glow
    },
    "light": {
        "name": "Light",
        # Window & Panel Surfaces
        "bg": "#f8fafc",                  # Crisp off-white slate 50
        "header_bg": "#ffffff",           # Pure white header
        "header_border": "#e2e8f0",       # Header bottom separator
        "panel_bg": "#f1f5f9",            # Soft slate panel background
        "panel_border": "#e2e8f0",        # Panel separator
        "card_bg": "#ffffff",             # White card surface
        "card_border": "#cbd5e1",         # Crisp card border
        "card_border_subtle": "#e2e8f0",  # Inset card divider
        "card_hover": "#f8fafc",          # Card hover accent

        # Shadows & Focus
        "shadow": "#94a3b8",              # Drop shadow
        "header_shadow": "#cbd5e1",       # Header bottom shadow
        "focus_ring": "#4f46e5",          # Keyboard focus ring

        # Board & Hole Geometry
        "board_bg": "#2563eb",            # Royal blue board
        "board_bg_gradient": "#1d4ed8",   # Lower gradient tone
        "board_rim": "#1e40af",           # Outer bezel rim
        "board_shadow": "#94a3b8",        # Drop shadow beneath board
        "cell_empty": "#f1f5f9",          # Clean cutout for empty slots
        "cell_rim": "#cbd5e1",            # Slot inner border ring
        "cell_inner_shadow": "#94a3b8",   # Inset crescent shadow
        "cell_highlight": "#ffffff",      # Subtle lower specular rim for slots
        "col_hover_beam": "#e2e8f0",      # Column highlight beam on hover

        # Coins & Highlights (Red / Rich Yellow)
        "human_coin": "#e11d48",          # Vibrant red coin
        "human_highlight": "#fda4af",     # 3D specular highlight arc
        "human_shadow": "#881337",        # 3D dark shaded rim
        "human_ghost": "#f43f5e",         # Floating preview coin

        "ai_coin": "#d97706",             # Rich amber-yellow coin (accessible on white)
        "ai_highlight": "#fef08a",        # 3D specular highlight arc
        "ai_shadow": "#92400e",           # 3D dark shaded rim
        "ai_ghost": "#b45309",            # Floating preview coin

        # Winning, Glow & Hints
        "win_glow": "#059669",            # Deep emerald glow
        "win_ring": "#10b981",            # Bright emerald ring
        "win_line": "#047857",            # Line through winning 4 coins
        "hint_col": "#0284c7",            # Cyan hint indicator
        "hint_arrow": "#0369a1",          # Arrow color
        "hint_beam": "#e0f2fe",           # Soft cyan column highlight beam

        # Typography (High Contrast WCAG AA)
        "text_primary": "#0f172a",        # Deep slate readable text (15.3:1)
        "text_secondary": "#475569",      # Slate secondary (8.2:1)
        "text_muted": "#64748b",          # Caption slate (4.6:1)
        "text_accent": "#4f46e5",         # Indigo text accent
        "danger": "#e11d48",              # Error / loss accent
        "success": "#059669",             # Success / win accent
        "warning": "#d97706",             # Warning / attention accent

        # Accents & Interactive Controls
        "accent": "#4f46e5",              # Indigo primary accent
        "accent_hover": "#4338ca",        # Darker indigo hover
        "accent_active": "#3730a3",       # Pressed indigo
        "cyan_accent": "#0891b2",         # Cyan secondary accent

        # Buttons & Segmented Controls
        "pill_bg": "#f1f5f9",             # Segmented track background
        "pill_border": "#e2e8f0",         # Segmented track border
        "button_subtle": "#ffffff",       # Outlined secondary button
        "button_subtle_border": "#cbd5e1",# Outlined secondary button border
        "button_subtle_hover": "#f8fafc", # Secondary button hover
        "button_disabled": "#e2e8f0",     # Disabled button surface
        "button_disabled_text": "#94a3b8",# Disabled button text

        # Toggle Switches
        "switch_track_off": "#cbd5e1",    # Track off
        "switch_track_on": "#4f46e5",     # Track on
        "switch_knob": "#ffffff",         # Sliding knob

        # Robot Avatar
        "robot_head": "#e2e8f0",          # Robot head metal
        "robot_rim": "#94a3b8",           # Robot outline rim
        "robot_eye_glow": "#0284c7",      # Blue digital eyes
        "robot_eye_pupil": "#0369a1",     # Pupil center
        "robot_antenna": "#94a3b8",       # Antenna stalk
        "robot_antenna_light": "#e11d48", # Antenna bulb
        "robot_mouth": "#0284c7",         # Digital mouth line
        "bubble_bg": "#ffffff",           # Speech bubble background
        "bubble_border": "#6366f1",       # Speech bubble border
        "bubble_text": "#0f172a",         # Speech bubble text

        # Telemetry, Status & Scoreboard
        "status_bg": "#ffffff",           # Status banner background
        "status_border": "#cbd5e1",       # Status banner border
        "badge_bg": "#e0e7ff",            # Indigo pill badge
        "badge_text": "#3730a3",          # Indigo badge text
        "bar_bg": "#e2e8f0",              # Telemetry progress bar track
        "bar_fill": "#4f46e5",            # Telemetry progress bar fill
        "leader_glow": "#0284c7",         # Scoreboard leader indicator glow
    }
}


def get_theme(theme_name="dark"):
    """Return the theme color dictionary for 'dark' or 'light'."""
    return THEMES.get(theme_name, THEMES["dark"])
