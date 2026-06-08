"""
gui/compare_window.py
Modal window comparing all 4 algorithm results with a performance graph.
"""

import tkinter as tk
from tkinter import ttk
import threading
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from gui.theme import *

ALGO_NAMES = {
    "backtracking":        "Backtracking\nDFS",
    "ac3_mrv":             "AC-3\n+ MRV",
    "forward_checking":    "Forward\nChecking",
    "simulated_annealing": "Simulated\nAnnealing",
}
ALGO_SHORT = {
    "backtracking":        "Backtracking",
    "ac3_mrv":             "AC-3 + MRV",
    "forward_checking":    "Fwd Checking",
    "simulated_annealing": "Sim. Annealing",
}
ALGO_ORDER = ["backtracking", "ac3_mrv", "forward_checking", "simulated_annealing"]


class CompareWindow(tk.Toplevel):
    def __init__(self, master, results: dict, on_view=None, grid_size: int = 9):
        super().__init__(master)
        self.title("Algorithm Comparison")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.grab_set()

        self._results   = results
        self._on_view   = on_view
        self._grid_size = grid_size

        self._build(results)
        self.minsize(800, 620)

    def _build(self, results):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill=tk.X, padx=24, pady=(18, 0))
        tk.Label(hdr, text="◈ Algorithm Comparison",
                 font=("Consolas", 16, "bold"), bg=BG, fg=ACCENT).pack(side=tk.LEFT)
        tk.Label(hdr, text=f"  {self._grid_size}×{self._grid_size} puzzle",
                 font=("Consolas", 12), bg=BG, fg=TEAL).pack(side=tk.LEFT, pady=(4,0))

        tk.Label(self, text="All four algorithms ran on the same puzzle.",
                 font=("Consolas", 9), bg=BG, fg=SUBTEXT).pack(anchor=tk.W, padx=24)

        # ── Tab control ───────────────────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=BG, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=CARD_BG, foreground=SUBTEXT,
                        font=("Consolas", 10, "bold"),
                        padding=[12, 6])
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        nb = ttk.Notebook(self, style="Custom.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Tab 1 — results table
        tab_table = tk.Frame(nb, bg=BG)
        nb.add(tab_table, text="  📊 Results Table  ")
        self._build_table(tab_table, results)

        # Tab 2 — performance graph
        tab_graph = tk.Frame(nb, bg=BG)
        nb.add(tab_graph, text="  📈 Performance Graph  ")
        self._build_graph(tab_graph, results)

        # ── Buttons ───────────────────────────────────────────────────────────
        self._build_buttons(results)

    # ── Table ─────────────────────────────────────────────────────────────────

    def _build_table(self, parent, results):
        # find best values for highlighting
        solved = [r for r in results.values() if r["solved"]]
        fastest_ms = min((r["time_ms"] for r in solved), default=None)
        fewest_states = min((r["states_explored"] for r in solved), default=None)
        fewest_bt = min((r["backtracks"] for r in solved), default=None)

        style = ttk.Style(parent)
        style.configure("Cmp.Treeview",
                        background=PANEL_BG, foreground=LABEL_FG,
                        fieldbackground=PANEL_BG, rowheight=36,
                        font=("Consolas", 10), borderwidth=0)
        style.configure("Cmp.Treeview.Heading",
                        background=CARD_BG, foreground=ACCENT,
                        font=("Consolas", 10, "bold"), borderwidth=0, relief="flat")
        style.map("Cmp.Treeview",
                  background=[("selected", CELL_SEL)],
                  foreground=[("selected", LABEL_FG)])

        cols = ("Algorithm","Solved","Time (ms)","States","Backtracks","Steps")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                            height=4, style="Cmp.Treeview", selectmode="browse")
        widths = [160, 75, 100, 100, 110, 85]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER)

        self._iids = {}
        for algo in ALGO_ORDER:
            res = results.get(algo)
            if not res: continue
            ok = "✓" if res["solved"] else "✗"
            iid = tree.insert("", tk.END, values=(
                ALGO_SHORT.get(algo, algo),
                ok, f"{res['time_ms']}",
                f"{res['states_explored']:,}",
                f"{res['backtracks']:,}",
                f"{len(res['steps']):,}",
            ))
            self._iids[iid] = algo
            # tag best values
            tags = []
            if res["solved"] and res["time_ms"] == fastest_ms:
                tags.append("fastest")
            if res["solved"] and res["states_explored"] == fewest_states:
                tags.append("fewest_states")
            if tags:
                tree.item(iid, tags=tuple(tags))

        tree.tag_configure("fastest",       foreground=GREEN)
        tree.tag_configure("fewest_states", foreground=TEAL)
        tree.pack(padx=16, pady=(12,4), fill=tk.X)

        self._tree = tree

        # Legend
        if fastest_ms is not None:
            best = min(solved, key=lambda r: r["time_ms"])
            tk.Label(parent,
                     text=f"⚡ Fastest: {ALGO_SHORT.get(best['algorithm'])}  ({best['time_ms']} ms)",
                     font=("Consolas", 10, "bold"), bg=BG, fg=GREEN).pack(pady=(4, 2))

        # colour legend
        leg = tk.Frame(parent, bg=BG)
        leg.pack(pady=(4, 8))
        for col, lbl in [(ACTIVE_FG,"Place"), (REMOVE_FG,"Backtrack"),
                          (SWAP_FG,"SA Swap"), (SOLVED_FG,"Solved")]:
            tk.Label(leg, text="●", fg=col, bg=BG, font=("Consolas", 13)).pack(side=tk.LEFT, padx=(8,2))
            tk.Label(leg, text=lbl, fg=SUBTEXT, bg=BG, font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0,6))

    # ── Graph ─────────────────────────────────────────────────────────────────

    def _build_graph(self, parent, results):
        # Colors per algo
        algo_colors = {
            "backtracking":        "#7c4dff",
            "ac3_mrv":             "#00b4d8",
            "forward_checking":    "#56e39f",
            "simulated_annealing": "#ffb347",
        }

        labels   = [ALGO_NAMES.get(a, a)            for a in ALGO_ORDER if a in results]
        times    = [results[a]["time_ms"]            for a in ALGO_ORDER if a in results]
        states   = [results[a]["states_explored"]    for a in ALGO_ORDER if a in results]
        bt       = [results[a]["backtracks"]         for a in ALGO_ORDER if a in results]
        steps    = [len(results[a]["steps"])         for a in ALGO_ORDER if a in results]
        colors   = [algo_colors[a]                   for a in ALGO_ORDER if a in results]
        solved   = [results[a]["solved"]             for a in ALGO_ORDER if a in results]

        n = len(labels)
        x = np.arange(n)
        bar_w = 0.55

        fig = Figure(figsize=(9.5, 6.5), facecolor="#0d0d14")
        fig.subplots_adjust(hspace=0.42, wspace=0.32,
                            left=0.08, right=0.97, top=0.88, bottom=0.14)

        axes_specs = [
            (221, "Time (ms)",           times,  "Execution Time"),
            (222, "States Explored",     states, "States Explored"),
            (223, "Backtracks",          bt,     "Backtracks"),
            (224, "Animation Steps",     steps,  "Recorded Steps"),
        ]

        for spec, ylabel, data, title in axes_specs:
            ax = fig.add_subplot(spec)
            ax.set_facecolor("#13131f")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2a45")

            bars = ax.bar(x, data, bar_w, color=colors, edgecolor="none",
                          alpha=0.88)

            # Dim unsolved bars
            for i, (bar, ok) in enumerate(zip(bars, solved)):
                if not ok:
                    bar.set_alpha(0.3)
                    bar.set_hatch("///")

            # Value labels on top
            for bar, val, ok in zip(bars, data, solved):
                h = bar.get_height()
                label_txt = f"{val:,}" if val < 1e6 else f"{val/1e6:.1f}M"
                ax.text(bar.get_x() + bar.get_width()/2, h * 1.03,
                        label_txt,
                        ha="center", va="bottom",
                        fontsize=7, color="#c8d0ff" if ok else "#555",
                        fontfamily="monospace")

            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=7.5, color="#9399b2",
                               fontfamily="monospace")
            ax.set_ylabel(ylabel, fontsize=8, color="#6c7086", fontfamily="monospace")
            ax.set_title(title, fontsize=9.5, color="#c8d0ff",
                         fontfamily="monospace", pad=6, fontweight="bold")
            ax.tick_params(colors="#4a4a6a", labelsize=7)
            ax.yaxis.set_tick_params(labelcolor="#6c7086")
            ax.grid(axis="y", color="#1e1e2e", linewidth=0.8, alpha=0.7)
            ax.set_axisbelow(True)

            # Highlight fastest bar
            if data:
                best_idx = data.index(min(v for v, ok in zip(data, solved) if ok) if any(solved) else data[0])
                bars[best_idx].set_edgecolor("#ffe66d")
                bars[best_idx].set_linewidth(2)

        fig.suptitle(f"Algorithm Performance — {self._grid_size}×{self._grid_size} Puzzle",
                     fontsize=12, color="#c8d0ff", fontfamily="monospace",
                     fontweight="bold")

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ── Buttons ───────────────────────────────────────────────────────────────

    def _build_buttons(self, results):
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=(0, 16))

        def view_selected():
            sel = self._tree.selection()
            if sel:
                algo = self._iids.get(sel[0])
                if algo and self._on_view:
                    self._on_view(results[algo])
            self.destroy()

        tk.Button(btn_row, text="▶  View Selected on Board",
                  command=view_selected,
                  font=("Consolas", 10, "bold"),
                  bg=BTN_PRIMARY, fg=BTN_PRI_FG,
                  activebackground=BTN_PRI_ACT,
                  activeforeground=BTN_PRI_FG,
                  relief=tk.FLAT, bd=0, padx=14, pady=8,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="✕  Close",
                  command=self.destroy,
                  font=("Consolas", 10, "bold"),
                  bg=BTN_SEC, fg=BTN_SEC_FG,
                  activebackground=BTN_SEC_ACT,
                  activeforeground=BTN_SEC_FG,
                  relief=tk.FLAT, bd=0, padx=14, pady=8,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)
