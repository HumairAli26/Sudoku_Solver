"""
gui/theme.py
All visual constants for the Sudoku GUI.
"""

# ── Window ────────────────────────────────────────────────────────────────────
APP_TITLE = "Sudoku Solver"

# ── Palette ───────────────────────────────────────────────────────────────────
BG           = "#0f0f17"        # deep space background
PANEL_BG     = "#181825"        # sidebar / panels
CARD_BG      = "#1e1e2e"        # card surfaces
BORDER       = "#313244"        # subtle borders

# Grid
CELL_BG_A    = "#1e1e2e"        # alternating box A
CELL_BG_B    = "#24243a"        # alternating box B
CELL_HOVER   = "#2a2a45"
CELL_SEL     = "#2d3566"        # selected cell

# Text
GIVEN_FG     = "#cdd6f4"        # pre-filled clue numbers
SOLVED_FG    = "#89b4fa"        # solver-placed numbers
REMOVE_FG    = "#f38ba8"        # backtrack removal
SWAP_FG      = "#fab387"        # simulated annealing swap
ACTIVE_FG    = "#a6e3a1"        # currently active cell during animation
MUTED        = "#6c7086"
LABEL_FG     = "#cdd6f4"
SUBTEXT      = "#9399b2"

# Accent
ACCENT       = "#cba6f7"        # lavender
ACCENT2      = "#89b4fa"        # blue
GREEN        = "#a6e3a1"
RED          = "#f38ba8"
YELLOW       = "#f9e2af"
PEACH        = "#fab387"
TEAL         = "#94e2d5"

# Buttons
BTN_PRIMARY  = "#cba6f7"
BTN_PRI_FG   = "#1e1e2e"
BTN_PRI_ACT  = "#b4befe"
BTN_SEC      = "#313244"
BTN_SEC_FG   = "#cdd6f4"
BTN_SEC_ACT  = "#45475a"
BTN_DANGER   = "#f38ba8"
BTN_DNG_FG   = "#1e1e2e"

# Stat badges
STAT_BG      = "#2a2a3e"
STAT_FG      = "#cba6f7"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_TITLE   = ("Consolas", 22, "bold")
FONT_SECTION = ("Consolas", 9, "bold")
FONT_BODY    = ("Consolas", 9)
FONT_CELL    = ("Consolas", 20, "bold")
FONT_CELL_SM = ("Consolas", 15, "bold")
FONT_BTN     = ("Consolas", 10, "bold")
FONT_STAT    = ("Consolas", 9)
FONT_STAT_V  = ("Consolas", 10, "bold")
FONT_MONO    = ("Consolas", 8)

# ── Grid geometry ─────────────────────────────────────────────────────────────
CELL_SIZE    = 58          # px per cell
BOX_GAP      = 4           # extra gap between 3×3 boxes
OUTER_PAD    = 3           # canvas outer padding
BORDER_THICK = 3           # box border width
BORDER_THIN  = 1           # cell border width

# ── Animation ─────────────────────────────────────────────────────────────────
ANIM_FPS_DEFAULT  = 60     # steps per second (slider max)
ANIM_DELAY_MIN    = 10     # ms  (fastest)
ANIM_DELAY_MAX    = 500    # ms  (slowest)

# Algorithm display names
ALGO_NAMES = {
    "backtracking":        "Backtracking DFS",
    "ac3_mrv":             "AC-3 + MRV",
    "forward_checking":    "Forward Checking",
    "simulated_annealing": "Simulated Annealing",
}
