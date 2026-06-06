"""
gui/compare_window.py
Modal window comparing all 4 algorithm results side-by-side.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import *


ALGO_NAMES = {
    "backtracking":        "Backtracking DFS",
    "ac3_mrv":             "AC-3 + MRV",
    "forward_checking":    "Forward Checking",
    "simulated_annealing": "Sim. Annealing",
}


class CompareWindow(tk.Toplevel):
    def __init__(self, master, results: dict, on_view=None):
        """
        results: {algo_key: result_dict, ...}
        on_view: callback(result_dict) when user picks one to view
        """
        super().__init__(master)
        self.title("Algorithm Comparison")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        self._results  = results
        self._on_view  = on_view

        self._build(results)

    def _build(self, results):
        # Header
        tk.Label(self, text="Algorithm Comparison",
                 font=("Consolas", 16, "bold"), bg=BG, fg=ACCENT).pack(pady=(20, 4))
        tk.Label(self, text="All four algorithms ran on the same puzzle.",
                 font=FONT_BODY, bg=BG, fg=SUBTEXT).pack(pady=(0, 12))

        # Table
        cols = ("Algorithm", "Solved", "Time (ms)", "States", "Backtracks", "Steps")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Cmp.Treeview",
                        background=PANEL_BG, foreground=LABEL_FG,
                        fieldbackground=PANEL_BG, rowheight=32,
                        font=FONT_BODY, borderwidth=0)
        style.configure("Cmp.Treeview.Heading",
                        background=CARD_BG, foreground=ACCENT,
                        font=FONT_SECTION, borderwidth=0, relief="flat")
        style.map("Cmp.Treeview",
                  background=[("selected", CELL_SEL)],
                  foreground=[("selected", LABEL_FG)])

        tree = ttk.Treeview(self, columns=cols, show="headings",
                            height=4, style="Cmp.Treeview",
                            selectmode="browse")
        widths = [160, 70, 90, 90, 100, 80]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER)

        order = ["backtracking", "ac3_mrv", "forward_checking", "simulated_annealing"]

        # find fastest solved
        solved = [r for r in results.values() if r["solved"]]
        fastest_ms = min((r["time_ms"] for r in solved), default=None)

        iids = {}
        for algo in order:
            res = results.get(algo)
            if not res:
                continue
            ok    = "✓" if res["solved"] else "✗"
            t     = f"{res['time_ms']}"
            iid = tree.insert("", tk.END, values=(
                ALGO_NAMES.get(algo, algo),
                ok, t,
                f"{res['states_explored']:,}",
                f"{res['backtracks']:,}",
                f"{len(res['steps']):,}",
            ))
            iids[iid] = algo
            if res["solved"] and res["time_ms"] == fastest_ms:
                tree.item(iid, tags=("fastest",))

        tree.tag_configure("fastest", foreground=GREEN)
        tree.pack(padx=20, pady=(0, 8), fill=tk.X)

        # fastest label
        if fastest_ms is not None:
            best = min(solved, key=lambda r: r["time_ms"])
            tk.Label(self,
                     text=f"⚡ Fastest: {ALGO_NAMES.get(best['algorithm'])}  ({best['time_ms']} ms)",
                     font=("Consolas", 10, "bold"), bg=BG, fg=GREEN).pack(pady=(0, 6))

        # colour legend
        leg = tk.Frame(self, bg=BG)
        leg.pack(pady=(0, 8))
        for col, label in [(ACTIVE_FG, "Place"), (REMOVE_FG, "Backtrack"),
                            (SWAP_FG, "SA Swap"), (SOLVED_FG, "Solved")]:
            dot = tk.Label(leg, text="●", fg=col, bg=BG, font=("Consolas", 12))
            dot.pack(side=tk.LEFT, padx=(8, 1))
            tk.Label(leg, text=label, fg=SUBTEXT, bg=BG, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 6))

        # bottom buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=(0, 20))

        def view_selected():
            sel = tree.selection()
            if sel:
                algo = iids.get(sel[0])
                if algo and self._on_view:
                    self._on_view(results[algo])
            self.destroy()

        tk.Button(btn_row, text="View Selected on Board",
                  command=view_selected,
                  font=FONT_BTN, bg=BTN_PRIMARY, fg=BTN_PRI_FG,
                  activebackground=BTN_PRI_ACT, activeforeground=BTN_PRI_FG,
                  relief=tk.FLAT, bd=0, padx=12, pady=6,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="Close",
                  command=self.destroy,
                  font=FONT_BTN, bg=BTN_SEC, fg=BTN_SEC_FG,
                  activebackground=BTN_SEC_ACT, activeforeground=BTN_SEC_FG,
                  relief=tk.FLAT, bd=0, padx=12, pady=6,
                  cursor="hand2").pack(side=tk.LEFT, padx=6)
