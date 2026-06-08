"""
gui/theme.py
Visual constants — dark neon theme with improved readability.
"""

# ── Window ────────────────────────────────────────────────────────────────────
APP_TITLE = "Sudoku Solver"

# ── Palette ───────────────────────────────────────────────────────────────────
BG           = "#0d0d14"        # near-black background
PANEL_BG     = "#13131f"        # sidebar
CARD_BG      = "#1a1a2e"        # card surfaces
BORDER       = "#2a2a45"        # subtle borders

# Grid
CELL_BG_A    = "#16213e"        # box A — navy-dark
CELL_BG_B    = "#0f3460"        # box B — deep blue (more contrast)
CELL_HOVER   = "#1a2a50"
CELL_SEL     = "#1d3461"        # selected cell highlight

# Text
GIVEN_FG     = "#e2e8ff"        # clues — bright white-blue
SOLVED_FG    = "#58d6ff"        # solver placed — cyan
REMOVE_FG    = "#ff6b8a"        # backtrack — pink-red
SWAP_FG      = "#ffb347"        # SA swap — amber
ACTIVE_FG    = "#7fff7f"        # active — bright green
MUTED        = "#4a4a6a"
LABEL_FG     = "#c8d0ff"
SUBTEXT      = "#7a80a8"

# Accent
ACCENT       = "#7c4dff"        # deep violet
ACCENT2      = "#00b4d8"        # cyan-blue
GREEN        = "#56e39f"
RED          = "#ff6b8a"
YELLOW       = "#ffe66d"
PEACH        = "#ffb347"
TEAL         = "#4cc9f0"

# Buttons
BTN_PRIMARY  = "#7c4dff"
BTN_PRI_FG   = "#ffffff"
BTN_PRI_ACT  = "#9c6fff"
BTN_SEC      = "#1e2040"
BTN_SEC_FG   = "#c8d0ff"
BTN_SEC_ACT  = "#2a2d5a"
BTN_DANGER   = "#ff6b8a"
BTN_DNG_FG   = "#1a0010"

# Stat badges
STAT_BG      = "#1a1a35"
STAT_FG      = "#9d79ff"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_TITLE   = ("Consolas", 22, "bold")
FONT_SECTION = ("Consolas", 9,  "bold")
FONT_BODY    = ("Consolas", 10)
FONT_CELL    = ("Consolas", 20, "bold")
FONT_CELL_SM = ("Consolas", 14, "bold")
FONT_CELL_XS = ("Consolas", 9,  "bold")
FONT_BTN     = ("Consolas", 10, "bold")
FONT_STAT    = ("Consolas", 9)
FONT_STAT_V  = ("Consolas", 10, "bold")
FONT_MONO    = ("Consolas", 8)

# ── Grid geometry (9×9 base — scaled per size) ────────────────────────────────
# CELL_SIZE is computed dynamically per grid size in GridWidget
CELL_SIZE_MAP = {
    4:  76,
    6:  64,
    9:  54,
    12: 40,
    16: 32,
}
CELL_FONT_MAP = {
    4:  ("Consolas", 26, "bold"),
    6:  ("Consolas", 22, "bold"),
    9:  ("Consolas", 18, "bold"),
    12: ("Consolas", 14, "bold"),
    16: ("Consolas", 10, "bold"),
}
BOX_GAP      = 4
OUTER_PAD    = 4
BORDER_THICK = 3
BORDER_THIN  = 1

# ── Animation ─────────────────────────────────────────────────────────────────
ANIM_FPS_DEFAULT  = 60
ANIM_DELAY_MIN    = 10
ANIM_DELAY_MAX    = 500

# ── Algorithm display names ───────────────────────────────────────────────────
ALGO_NAMES = {
    "backtracking":        "Backtracking DFS",
    "ac3_mrv":             "AC-3 + MRV",
    "forward_checking":    "Forward Checking",
    "simulated_annealing": "Simulated Annealing",
}

# ── Grid sizes ────────────────────────────────────────────────────────────────
GRID_SIZES = [4, 6, 9, 12, 16]
