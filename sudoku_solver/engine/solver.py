"""
engine/solver.py
Four Sudoku solving algorithms, each recording every step for animation.

Step format:
    {"r": int, "c": int, "v": int, "action": "place" | "remove" | "swap"}
"""

import copy
import time
import random
import math


class SudokuSolver:
    MAX_STEPS = 5000  # cap recorded steps to avoid massive lists

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.states_explored = 0
        self.backtracks = 0
        self.steps: list[dict] = []

    # ── public ────────────────────────────────────────────────────────────────

    def solve(self, algorithm: str) -> dict:
        self.states_explored = 0
        self.backtracks = 0
        self.steps = []
        grid = copy.deepcopy(self.puzzle)

        start = time.perf_counter()
        dispatch = {
            "backtracking":        self._backtracking,
            "ac3_mrv":             self._ac3_mrv,
            "forward_checking":    self._forward_checking,
            "simulated_annealing": self._simulated_annealing,
        }
        fn = dispatch.get(algorithm)
        solved, solution = fn(grid) if fn else (False, grid)
        elapsed = (time.perf_counter() - start) * 1000

        return {
            "solved":          solved,
            "solution":        solution,
            "time_ms":         round(elapsed, 3),
            "states_explored": self.states_explored,
            "backtracks":      self.backtracks,
            "algorithm":       algorithm,
            "steps":           self.steps,
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    def _record(self, r, c, v, action):
        if len(self.steps) < self.MAX_STEPS:
            self.steps.append({"r": r, "c": c, "v": v, "action": action})

    def _is_valid(self, grid, row, col, num):
        if num in grid[row]:
            return False
        if any(grid[r][col] == num for r in range(9)):
            return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if grid[r][c] == num:
                    return False
        return True

    def _find_empty(self, grid):
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    return r, c
        return None

    def _get_peers(self, r, c):
        peers = set()
        for i in range(9):
            if i != c:
                peers.add((r, i))
            if i != r:
                peers.add((i, c))
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for dr in range(br, br + 3):
            for dc in range(bc, bc + 3):
                if (dr, dc) != (r, c):
                    peers.add((dr, dc))
        return peers

    # ── 1. Backtracking (uninformed DFS) ──────────────────────────────────────

    def _backtracking(self, grid):
        self.states_explored += 1
        empty = self._find_empty(grid)
        if not empty:
            return True, grid
        r, c = empty
        for num in range(1, 10):
            if self._is_valid(grid, r, c, num):
                grid[r][c] = num
                self._record(r, c, num, "place")
                ok, sol = self._backtracking(grid)
                if ok:
                    return True, sol
                grid[r][c] = 0
                self.backtracks += 1
                self._record(r, c, 0, "remove")
        return False, grid

    # ── 2. AC-3 + MRV (informed constraint propagation) ──────────────────────

    def _get_domains(self, grid):
        domains = {}
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    domains[(r, c)] = set(
                        n for n in range(1, 10) if self._is_valid(grid, r, c, n)
                    )
                else:
                    domains[(r, c)] = {grid[r][c]}
        return domains

    def _ac3(self, domains):
        queue = [(xi, xj) for xi in domains for xj in self._get_peers(*xi)]
        while queue:
            xi, xj = queue.pop(0)
            if self._revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                for xk in self._get_peers(*xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains, xi, xj):
        revised = False
        for val in set(domains[xi]):
            if all(val == v for v in domains[xj]):
                domains[xi].remove(val)
                revised = True
        return revised

    def _mrv_cell(self, domains, grid):
        unassigned = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
        if not unassigned:
            return None
        def score(cell):
            mrv = len(domains[cell])
            degree = sum(1 for p in self._get_peers(*cell) if grid[p[0]][p[1]] == 0)
            return (mrv, -degree)
        return min(unassigned, key=score)

    def _ac3_mrv(self, grid):
        domains = self._get_domains(grid)
        if not self._ac3(domains):
            return False, grid
        return self._mrv_search(grid, domains)

    def _mrv_search(self, grid, domains):
        self.states_explored += 1
        cell = self._mrv_cell(domains, grid)
        if cell is None:
            return True, grid
        r, c = cell
        for val in sorted(domains[(r, c)]):
            if self._is_valid(grid, r, c, val):
                grid[r][c] = val
                self._record(r, c, val, "place")
                new_domains = copy.deepcopy(domains)
                new_domains[(r, c)] = {val}
                if self._ac3(new_domains):
                    ok, sol = self._mrv_search(grid, new_domains)
                    if ok:
                        return True, sol
                grid[r][c] = 0
                self.backtracks += 1
                self._record(r, c, 0, "remove")
        return False, grid

    # ── 3. Forward Checking ───────────────────────────────────────────────────

    def _forward_checking(self, grid):
        domains = self._get_domains(grid)
        return self._fc_search(grid, domains)

    def _fc_search(self, grid, domains):
        self.states_explored += 1
        empty = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
        if not empty:
            return True, grid
        r, c = min(empty, key=lambda cell: len(domains[cell]))
        for val in sorted(domains[(r, c)]):
            if self._is_valid(grid, r, c, val):
                grid[r][c] = val
                self._record(r, c, val, "place")
                new_domains = copy.deepcopy(domains)
                new_domains[(r, c)] = {val}
                failed = False
                for peer in self._get_peers(r, c):
                    pr, pc = peer
                    if grid[pr][pc] == 0:
                        new_domains[peer].discard(val)
                        if not new_domains[peer]:
                            failed = True
                            break
                if not failed:
                    ok, sol = self._fc_search(grid, new_domains)
                    if ok:
                        return True, sol
                grid[r][c] = 0
                self.backtracks += 1
                self._record(r, c, 0, "remove")
        return False, grid

    # ── 4. Simulated Annealing (local search) ─────────────────────────────────

    def _count_violations(self, grid):
        v = 0
        for r in range(9):
            row = [grid[r][c] for c in range(9) if grid[r][c] != 0]
            v += len(row) - len(set(row))
        for c in range(9):
            col = [grid[r][c] for r in range(9) if grid[r][c] != 0]
            v += len(col) - len(set(col))
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box = [grid[r][c] for r in range(br, br+3)
                                   for c in range(bc, bc+3) if grid[r][c] != 0]
                v += len(box) - len(set(box))
        return v

    def _simulated_annealing(self, grid):
        fixed = {(r, c) for r in range(9) for c in range(9) if grid[r][c] != 0}
        current = copy.deepcopy(grid)

        # fill each box with missing numbers
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                present = {
                    current[r][c]
                    for r in range(br, br+3)
                    for c in range(bc, bc+3)
                    if current[r][c] != 0
                }
                missing = list(set(range(1, 10)) - present)
                random.shuffle(missing)
                idx = 0
                for r in range(br, br+3):
                    for c in range(bc, bc+3):
                        if current[r][c] == 0:
                            current[r][c] = missing[idx]
                            idx += 1

        # record initial state
        for r in range(9):
            for c in range(9):
                if (r, c) not in fixed:
                    self._record(r, c, current[r][c], "place")

        current_cost = self._count_violations(current)
        best = copy.deepcopy(current)
        best_cost = current_cost
        T, T_min, alpha = 2.0, 0.001, 0.9995

        for _ in range(100_000):
            self.states_explored += 1
            if current_cost == 0:
                break
            br = random.choice([0, 3, 6])
            bc = random.choice([0, 3, 6])
            free = [
                (r, c)
                for r in range(br, br+3)
                for c in range(bc, bc+3)
                if (r, c) not in fixed
            ]
            if len(free) < 2:
                T *= alpha
                continue
            c1, c2 = random.sample(free, 2)
            r1, col1 = c1
            r2, col2 = c2
            current[r1][col1], current[r2][col2] = current[r2][col2], current[r1][col1]
            new_cost = self._count_violations(current)
            delta = new_cost - current_cost
            if delta < 0 or random.random() < math.exp(-delta / max(T, 1e-10)):
                current_cost = new_cost
                if current_cost < best_cost:
                    best = copy.deepcopy(current)
                    best_cost = current_cost
                    self._record(r1, col1, current[r1][col1], "swap")
                    self._record(r2, col2, current[r2][col2], "swap")
            else:
                current[r1][col1], current[r2][col2] = current[r2][col2], current[r1][col1]
            T *= alpha
            if T < T_min:
                T = 0.5

        return best_cost == 0, best
