"""
gui/sidebar.py
Right-side control panel: generate, algorithm picker, playback controls,
speed slider, statistics.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import *


def _sep(parent):
    f = tk.Frame(parent, bg=BORDER, height=1)
    f.pack(fill=tk.X, padx=0, pady=8)


def _section_label(parent, text):
    tk.Label(parent, text=text,
             font=FONT_SECTION, bg=PANEL_BG, fg=MUTED,
             anchor=tk.W).pack(fill=tk.X, padx=16, pady=(10, 3))


class Sidebar(tk.Frame):
    """
    Fires callbacks:
        on_generate(difficulty)
        on_solve(algorithm)
        on_solve_all()
        on_manual()
        on_clear()
        on_play_pause()
        on_step()
        on_speed_change(delay_ms)
    """

    def __init__(self, master,
                 on_generate, on_solve, on_solve_all,
                 on_manual, on_clear,
                 on_play_pause, on_step, on_speed_change,
                 **kwargs):
        super().__init__(master, bg=PANEL_BG, width=230, **kwargs)
        self.pack_propagate(False)

        self._cb_generate    = on_generate
        self._cb_solve       = on_solve
        self._cb_solve_all   = on_solve_all
        self._cb_manual      = on_manual
        self._cb_clear       = on_clear
        self._cb_play_pause  = on_play_pause
        self._cb_step        = on_step
        self._cb_speed       = on_speed_change

        self._diff_var  = tk.StringVar(value="Medium")
        self._algo_var  = tk.StringVar(value="backtracking")
        self._speed_var = tk.IntVar(value=40)

        self._build()

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # scroll-able inner frame
        canvas = tk.Canvas(self, bg=PANEL_BG, highlightthickness=0)
        sb = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = tk.Frame(canvas, bg=PANEL_BG)
        canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # bind mousewheel
        def _scroll(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        self._build_header(inner)
        _sep(inner)
        self._build_generate(inner)
        _sep(inner)
        self._build_algorithms(inner)
        _sep(inner)
        self._build_actions(inner)
        _sep(inner)
        self._build_playback(inner)
        _sep(inner)
        self._build_stats(inner)

    def _build_header(self, p):
        tk.Label(p, text="SUDOKU", font=("Consolas", 20, "bold"),
                 bg=PANEL_BG, fg=ACCENT).pack(pady=(20, 0))
        tk.Label(p, text="SOLVER", font=("Consolas", 14),
                 bg=PANEL_BG, fg=SUBTEXT).pack(pady=(0, 4))

    def _build_generate(self, p):
        _section_label(p, "── GENERATE ─────────")
        f = tk.Frame(p, bg=PANEL_BG)
        f.pack(fill=tk.X, padx=16, pady=(0, 6))
        for d in ("Easy", "Medium", "Hard", "Expert"):
            tk.Radiobutton(f, text=d, variable=self._diff_var, value=d,
                           bg=PANEL_BG, fg=LABEL_FG,
                           selectcolor=CARD_BG, activebackground=PANEL_BG,
                           activeforeground=ACCENT, font=FONT_BODY,
                           indicatoron=False,
                           relief=tk.FLAT, bd=0,
                           padx=4, pady=3,
                           ).pack(side=tk.LEFT)

        self._gen_btn = self._btn(p, "⟳  Generate New Puzzle",
                                  lambda: self._cb_generate(self._diff_var.get()),
                                  primary=True)

    def _build_algorithms(self, p):
        _section_label(p, "── ALGORITHM ────────")
        algos = [
            ("Backtracking DFS",   "backtracking"),
            ("AC-3 + MRV",         "ac3_mrv"),
            ("Forward Checking",   "forward_checking"),
            ("Simulated Annealing","simulated_annealing"),
        ]
        for label, val in algos:
            rb = tk.Radiobutton(p, text=label, variable=self._algo_var, value=val,
                                bg=PANEL_BG, fg=LABEL_FG,
                                selectcolor=CARD_BG,
                                activebackground=PANEL_BG, activeforeground=ACCENT,
                                font=FONT_BODY, anchor=tk.W)
            rb.pack(fill=tk.X, padx=16)

    def _build_actions(self, p):
        _section_label(p, "── ACTIONS ──────────")
        self._solve_btn = self._btn(p, "▶  Solve & Animate",
                                    lambda: self._cb_solve(self._algo_var.get()),
                                    primary=True)
        self._btn(p, "⇉  Compare All",    self._cb_solve_all)
        self._btn(p, "✎  Manual Entry",   self._cb_manual,   danger=False, sec=True)
        self._btn(p, "⌫  Clear Board",    self._cb_clear,    danger=True)

    def _build_playback(self, p):
        _section_label(p, "── PLAYBACK ─────────")

        ctrl = tk.Frame(p, bg=PANEL_BG)
        ctrl.pack(fill=tk.X, padx=16, pady=(0, 6))

        self._play_btn = tk.Button(ctrl, text="▶  Play",
                                   command=self._cb_play_pause,
                                   font=FONT_BTN, bg=BTN_SEC, fg=BTN_SEC_FG,
                                   activebackground=BTN_SEC_ACT,
                                   activeforeground=BTN_SEC_FG,
                                   relief=tk.FLAT, bd=0,
                                   padx=8, pady=5, cursor="hand2")
        self._play_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,4))

        tk.Button(ctrl, text="⏭  Step",
                  command=self._cb_step,
                  font=FONT_BTN, bg=BTN_SEC, fg=BTN_SEC_FG,
                  activebackground=BTN_SEC_ACT,
                  activeforeground=BTN_SEC_FG,
                  relief=tk.FLAT, bd=0,
                  padx=8, pady=5, cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # speed
        spd_row = tk.Frame(p, bg=PANEL_BG)
        spd_row.pack(fill=tk.X, padx=16, pady=(2, 0))
        tk.Label(spd_row, text="Speed:", font=FONT_BODY,
                 bg=PANEL_BG, fg=SUBTEXT).pack(side=tk.LEFT)
        self._spd_lbl = tk.Label(spd_row, text="Med",
                                  font=FONT_BODY, bg=PANEL_BG, fg=ACCENT)
        self._spd_lbl.pack(side=tk.RIGHT)

        self._spd_slider = tk.Scale(p, from_=1, to=100,
                                    orient=tk.HORIZONTAL,
                                    variable=self._speed_var,
                                    command=self._on_speed,
                                    bg=PANEL_BG, fg=LABEL_FG,
                                    troughcolor=CARD_BG,
                                    highlightthickness=0,
                                    sliderrelief=tk.FLAT,
                                    showvalue=False)
        self._spd_slider.pack(fill=tk.X, padx=16)

        # progress bar
        self._prog_var = tk.DoubleVar(value=0)
        style = ttk.Style(p)
        style.theme_use("clam")
        style.configure("S.Horizontal.TProgressbar",
                        troughcolor=CARD_BG, background=ACCENT,
                        bordercolor=CARD_BG, lightcolor=ACCENT, darkcolor=ACCENT)
        self._prog = ttk.Progressbar(p, variable=self._prog_var,
                                     style="S.Horizontal.TProgressbar",
                                     maximum=100)
        self._prog.pack(fill=tk.X, padx=16, pady=(6, 0))
        self._prog_lbl = tk.Label(p, text="0 / 0 steps",
                                   font=FONT_MONO, bg=PANEL_BG, fg=MUTED)
        self._prog_lbl.pack(anchor=tk.W, padx=16)

    def _build_stats(self, p):
        _section_label(p, "── STATISTICS ───────")
        self._stat_vars = {}
        rows = [("Algorithm", "—"), ("Time", "—"),
                ("States",    "—"), ("Backtracks", "—"),
                ("Steps",     "—"), ("Result", "—")]
        for key, default in rows:
            row = tk.Frame(p, bg=PANEL_BG)
            row.pack(fill=tk.X, padx=16, pady=1)
            tk.Label(row, text=f"{key}:", font=FONT_STAT,
                     bg=PANEL_BG, fg=SUBTEXT, width=11, anchor=tk.W).pack(side=tk.LEFT)
            v = tk.StringVar(value=default)
            tk.Label(row, textvariable=v, font=FONT_STAT_V,
                     bg=PANEL_BG, fg=STAT_FG, anchor=tk.W).pack(side=tk.LEFT)
            self._stat_vars[key] = v

        tk.Label(p, text="", bg=PANEL_BG).pack(pady=10)  # bottom padding

    # ── helpers ───────────────────────────────────────────────────────────────

    def _btn(self, parent, text, command, primary=False, sec=False, danger=False):
        if primary:
            bg, fg, abg = BTN_PRIMARY, BTN_PRI_FG, BTN_PRI_ACT
        elif danger:
            bg, fg, abg = BTN_DANGER, BTN_DNG_FG, "#e57a93"
        else:
            bg, fg, abg = BTN_SEC, BTN_SEC_FG, BTN_SEC_ACT
        b = tk.Button(parent, text=text, command=command,
                      font=FONT_BTN, bg=bg, fg=fg,
                      activebackground=abg, activeforeground=fg,
                      relief=tk.FLAT, bd=0, padx=10, pady=6,
                      cursor="hand2", anchor=tk.W)
        b.pack(fill=tk.X, padx=16, pady=2)
        return b

    def _on_speed(self, _=None):
        v = self._speed_var.get()
        # map 1-100 → 500ms-10ms (inverse)
        delay = int(500 - (v - 1) * (490 / 99))
        labels = {True: "Slow", False: "Fast"}
        if v < 33:
            lbl = "Slow"
        elif v < 67:
            lbl = "Med"
        else:
            lbl = "Fast"
        self._spd_lbl.config(text=lbl)
        self._cb_speed(delay)

    # ── public update methods ─────────────────────────────────────────────────

    def set_generating(self, generating: bool):
        txt = "⟳  Generating…" if generating else "⟳  Generate New Puzzle"
        state = tk.DISABLED if generating else tk.NORMAL
        self._gen_btn.config(text=txt, state=state)

    def set_solving(self, solving: bool):
        txt = "⏳  Solving…" if solving else "▶  Solve & Animate"
        state = tk.DISABLED if solving else tk.NORMAL
        self._solve_btn.config(text=txt, state=state)

    def set_play_state(self, playing: bool):
        self._play_btn.config(text="⏸  Pause" if playing else "▶  Play")

    def update_progress(self, idx: int, total: int):
        if total:
            self._prog_var.set(100 * idx / total)
        self._prog_lbl.config(text=f"{idx} / {total} steps")

    def update_stats(self, result: dict):
        names = {
            "backtracking":        "Backtracking",
            "ac3_mrv":             "AC-3 + MRV",
            "forward_checking":    "Fwd Checking",
            "simulated_annealing": "Sim. Annealing",
        }
        self._stat_vars["Algorithm"].set(names.get(result["algorithm"], "—"))
        self._stat_vars["Time"].set(f"{result['time_ms']} ms")
        self._stat_vars["States"].set(f"{result['states_explored']:,}")
        self._stat_vars["Backtracks"].set(f"{result['backtracks']:,}")
        self._stat_vars["Steps"].set(f"{len(result['steps']):,}")
        self._stat_vars["Result"].set("✓ Solved" if result["solved"] else "✗ Failed")

    def get_delay(self) -> int:
        v = self._speed_var.get()
        return int(500 - (v - 1) * (490 / 99))
