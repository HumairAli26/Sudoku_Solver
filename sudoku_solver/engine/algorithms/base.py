"""
engine/algorithms/base.py
Base class for all Sudoku solving algorithms.
Supports variable grid sizes: 4x4, 6x6, 9x9, 12x12, 16x16.
"""
import copy
import time
import math


class BaseSolver:
    """
    Base solver — subclasses implement _run(grid) -> (solved: bool, grid).

    Grid is an N×N list of ints, 0 = empty.
    Box dimensions are (box_h × box_w) where box_h * box_w == N.
    """

    MAX_STEPS = 8000

    # Supported sizes and their box dimensions
    SIZE_BOXES = {
        4:  (2, 2),
        6:  (2, 3),
        9:  (3, 3),
        12: (3, 4),
        16: (4, 4),
    }

    def __init__(self, puzzle: list[list[int]]):
        self.puzzle = copy.deepcopy(puzzle)
        self.N = len(puzzle)
        self.box_h, self.box_w = self.SIZE_BOXES.get(self.N, (3, 3))
        self.values = list(range(1, self.N + 1))
        self.states_explored = 0
        self.backtracks = 0
        self.steps: list[dict] = []

    def solve(self) -> dict:
        self.states_explored = 0
        self.backtracks = 0
        self.steps = []
        grid = copy.deepcopy(self.puzzle)
        start = time.perf_counter()
        solved, solution = self._run(grid)
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "solved":          solved,
            "solution":        solution,
            "time_ms":         round(elapsed, 3),
            "states_explored": self.states_explored,
            "backtracks":      self.backtracks,
            "algorithm":       self.ALGORITHM_KEY,
            "steps":           self.steps,
        }

    def _run(self, grid):
        raise NotImplementedError

    # ── shared helpers ────────────────────────────────────────────────────────

    def _record(self, r, c, v, action):
        if len(self.steps) < self.MAX_STEPS:
            self.steps.append({"r": r, "c": c, "v": v, "action": action})

    def _is_valid(self, grid, row, col, num):
        N = self.N
        if num in grid[row]:
            return False
        if any(grid[r][col] == num for r in range(N)):
            return False
        br = self.box_h * (row // self.box_h)
        bc = self.box_w * (col // self.box_w)
        for r in range(br, br + self.box_h):
            for c in range(bc, bc + self.box_w):
                if grid[r][c] == num:
                    return False
        return True

    def _find_empty(self, grid):
        for r in range(self.N):
            for c in range(self.N):
                if grid[r][c] == 0:
                    return r, c
        return None

    def _get_peers(self, r, c):
        N = self.N
        peers = set()
        for i in range(N):
            if i != c: peers.add((r, i))
            if i != r: peers.add((i, c))
        br = self.box_h * (r // self.box_h)
        bc = self.box_w * (c // self.box_w)
        for dr in range(br, br + self.box_h):
            for dc in range(bc, bc + self.box_w):
                if (dr, dc) != (r, c):
                    peers.add((dr, dc))
        return peers

    def _get_domains(self, grid):
        N = self.N
        domains = {}
        for r in range(N):
            for c in range(N):
                if grid[r][c] == 0:
                    domains[(r, c)] = set(
                        n for n in self.values if self._is_valid(grid, r, c, n)
                    )
                else:
                    domains[(r, c)] = {grid[r][c]}
        return domains
