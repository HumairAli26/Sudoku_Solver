"""
app.py
Main application window — wires the grid, sidebar, animator, and engines.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import copy

from engine import SudokuSolver, SudokuGenerator
from gui import GridWidget, Sidebar, StepAnimator, CompareWindow
from gui.theme import *


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BG)
        self.resizable(False, False)

        # state
        self._puzzle   = [[0]*9 for _ in range(9)]
        self._solution = None
        self._given    = set()
        self._animator: StepAnimator | None = None
        self._last_result = None

        self._build_ui()
        self._status("Ready — generate a puzzle or enter one manually.")
        self._new_game("Medium")

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── left: grid area ──────────────────────────────────────────────────
        left = tk.Frame(self, bg=BG, padx=20, pady=20)
        left.pack(side=tk.LEFT, fill=tk.BOTH)

        self._grid = GridWidget(left, on_cell_edit=self._on_cell_edit)
        self._grid.pack()

        # legend row
        leg = tk.Frame(left, bg=BG)
        leg.pack(fill=tk.X, pady=(8, 0))
        for col, label in [(ACTIVE_FG, "Place"), (REMOVE_FG, "Backtrack"),
                            (SWAP_FG, "SA Swap"), (SOLVED_FG, "Solved"),
                            (GIVEN_FG, "Clue")]:
            tk.Label(leg, text="●", fg=col, bg=BG, font=("Consolas", 11)).pack(side=tk.LEFT, padx=(4,1))
            tk.Label(leg, text=label, fg=SUBTEXT, bg=BG, font=FONT_MONO).pack(side=tk.LEFT, padx=(0,6))

        # status bar
        self._status_var = tk.StringVar()
        tk.Label(left, textvariable=self._status_var,
                 font=FONT_MONO, bg=BG, fg=MUTED,
                 wraplength=540, justify=tk.LEFT, anchor=tk.W).pack(fill=tk.X, pady=(4,0))

        # ── right: sidebar ────────────────────────────────────────────────────
        self._sidebar = Sidebar(self,
            on_generate    = self._on_generate,
            on_solve       = self._on_solve,
            on_solve_all   = self._on_solve_all,
            on_manual      = self._on_manual,
            on_clear       = self._on_clear,
            on_play_pause  = self._on_play_pause,
            on_step        = self._on_step,
            on_speed_change= self._on_speed_change,
        )
        self._sidebar.pack(side=tk.RIGHT, fill=tk.Y)

    # ── callbacks ─────────────────────────────────────────────────────────────

    def _on_cell_edit(self, r, c, val):
        # user typed into a cell manually — mark as given for solving
        pass

    def _on_generate(self, difficulty):
        self._stop_animator()
        self._sidebar.set_generating(True)
        self._status(f"Generating {difficulty} puzzle…")

        def _gen():
            gen = SudokuGenerator()
            puzzle, solution = gen.generate(difficulty)
            self.after(0, lambda: self._finish_generate(puzzle, solution))

        threading.Thread(target=_gen, daemon=True).start()

    def _finish_generate(self, puzzle, solution):
        self._puzzle   = puzzle
        self._solution = solution
        self._given    = {(r,c) for r in range(9) for c in range(9) if puzzle[r][c] != 0}
        self._grid.load_puzzle(puzzle, self._given)
        self._sidebar.set_generating(False)
        self._status(f"Puzzle ready. Choose an algorithm and press Solve & Animate.")

    def _on_solve(self, algorithm):
        self._stop_animator()
        grid = self._grid.get_grid()

        # gather given from current board
        self._given = {(r,c) for r in range(9) for c in range(9) if grid[r][c] != 0}
        self._grid.load_puzzle(grid, self._given)  # reset colours

        self._sidebar.set_solving(True)
        self._status(f"Running {algorithm}…")

        def _run():
            solver = SudokuSolver(grid)
            result = solver.solve(algorithm)
            self.after(0, lambda: self._finish_solve(result))

        threading.Thread(target=_run, daemon=True).start()

    def _finish_solve(self, result):
        self._sidebar.set_solving(False)
        self._last_result = result
        self._sidebar.update_stats(result)

        if not result["solved"]:
            messagebox.showwarning("Unsolvable",
                "The puzzle could not be solved.\n"
                "Check for conflicts or try another algorithm.")
            self._status("✗ Could not solve the puzzle.")
            return

        step_count = len(result["steps"])
        self._status(
            f"Solved in {result['time_ms']} ms · "
            f"{result['states_explored']:,} states · "
            f"{result['backtracks']:,} backtracks · "
            f"{step_count:,} recorded steps → animating…"
        )
        self._sidebar.update_progress(0, step_count)
        self._start_animator(result)

    def _on_solve_all(self):
        self._stop_animator()
        grid = self._grid.get_grid()
        self._given = {(r,c) for r in range(9) for c in range(9) if grid[r][c] != 0}
        self._status("Running all 4 algorithms…")

        def _run():
            results = {}
            algos = ["backtracking", "ac3_mrv", "forward_checking", "simulated_annealing"]
            for algo in algos:
                solver = SudokuSolver(grid)
                results[algo] = solver.solve(algo)
            self.after(0, lambda: self._finish_solve_all(results))

        threading.Thread(target=_run, daemon=True).start()

    def _finish_solve_all(self, results):
        def _view(result):
            self._last_result = result
            self._sidebar.update_stats(result)
            self._grid.load_puzzle(self._puzzle, self._given)
            self._start_animator(result)

        CompareWindow(self, results, on_view=_view)

    def _on_manual(self):
        self._stop_animator()
        self._given = set()
        self._puzzle = [[0]*9 for _ in range(9)]
        self._grid.clear_board()
        self._grid.unlock_all()
        self._status("Manual entry — type digits into cells, then press Solve & Animate.")

    def _on_clear(self):
        self._stop_animator()
        self._given = set()
        self._puzzle = [[0]*9 for _ in range(9)]
        self._grid.clear_board()
        self._sidebar.update_progress(0, 0)
        self._status("Board cleared.")

    def _on_play_pause(self):
        if self._animator is None:
            return
        if self._animator.is_paused:
            self._animator.resume()
            self._sidebar.set_play_state(True)
        else:
            self._animator.pause()
            self._sidebar.set_play_state(False)

    def _on_step(self):
        if self._animator:
            self._animator.step()

    def _on_speed_change(self, delay_ms):
        if self._animator:
            self._animator.set_delay(delay_ms)

    # ── animator management ───────────────────────────────────────────────────

    def _start_animator(self, result):
        delay = self._sidebar.get_delay()
        self._animator = StepAnimator(
            self._grid, result,
            delay_ms = delay,
            on_step  = self._on_anim_step,
            on_done  = self._on_anim_done,
        )
        self._sidebar.set_play_state(True)
        self._animator.start()

    def _stop_animator(self):
        if self._animator:
            self._animator.stop()
            self._animator = None
        self._sidebar.set_play_state(False)

    def _on_anim_step(self, idx, total):
        self._sidebar.update_progress(idx, total)

    def _on_anim_done(self):
        self._sidebar.set_play_state(False)
        self._sidebar.update_progress(
            self._last_result["steps"].__len__() if self._last_result else 0,
            self._last_result["steps"].__len__() if self._last_result else 0,
        )
        self._status("✓ Animation complete.")

    # ── misc ──────────────────────────────────────────────────────────────────

    def _status(self, msg):
        self._status_var.set(msg)

    def _new_game(self, difficulty):
        self._on_generate(difficulty)
