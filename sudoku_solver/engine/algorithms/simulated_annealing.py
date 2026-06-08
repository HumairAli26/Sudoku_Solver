"""
engine/algorithms/simulated_annealing.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm: Simulated Annealing (Local / Stochastic Search)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS:
  Simulated Annealing (SA) is inspired by the annealing process in
  metallurgy, where controlled cooling allows atoms to find low-energy
  configurations.

  1. INITIALIZATION:
       Fill each N×N box with the digits that are missing from it,
       placed randomly. The given (clue) cells stay fixed.
       This creates a "complete" (but invalid) grid.

  2. COST FUNCTION:
       Count the number of DUPLICATE values in each row and column.
       (Boxes are already conflict-free by construction.)
       Goal: drive cost to 0.

  3. NEIGHBOUR GENERATION:
       Pick a random box. Swap two non-fixed cells within that box.
       Boxes are conflict-free before and after the swap.

  4. ACCEPTANCE CRITERION:
       If the new cost is lower  → always accept.
       If the new cost is higher → accept with probability exp(-Δ/T).
       (High temperature T = willing to accept bad moves to escape local minima.)

  5. COOLING SCHEDULE:
       T ← T × α  each iteration (geometric cooling).
       Restart with T = 0.5 when T drops below T_min to avoid freezing.

WHY IT'S DIFFERENT:
  - Does NOT systematically enumerate cells — works on complete grids.
  - Can escape local optima via probabilistic acceptance.
  - Non-deterministic — may fail or produce a different path each run.
  - Useful for very large grids where exact search is expensive.

LIMITATIONS:
  - Not guaranteed to find a solution (stochastic).
  - Can be slower than constraint-based methods on standard 9×9 puzzles.
  - Tuning temperature schedule is problem-specific.
"""

import copy
import random
import math
from .base import BaseSolver


class SimulatedAnnealingSolver(BaseSolver):
    ALGORITHM_KEY = "simulated_annealing"
    DISPLAY_NAME  = "Simulated Annealing"

    def _run(self, grid):
        N = self.N
        fixed = {(r, c) for r in range(N) for c in range(N) if grid[r][c] != 0}
        current = copy.deepcopy(grid)

        # fill each box with missing numbers
        for br in range(0, N, self.box_h):
            for bc in range(0, N, self.box_w):
                present = {
                    current[r][c]
                    for r in range(br, br + self.box_h)
                    for c in range(bc, bc + self.box_w)
                    if current[r][c] != 0
                }
                missing = list(set(self.values) - present)
                random.shuffle(missing)
                idx = 0
                for r in range(br, br + self.box_h):
                    for c in range(bc, bc + self.box_w):
                        if current[r][c] == 0:
                            current[r][c] = missing[idx]
                            idx += 1

        # record initial state
        for r in range(N):
            for c in range(N):
                if (r, c) not in fixed:
                    self._record(r, c, current[r][c], "place")

        current_cost = self._count_violations(current)
        best = copy.deepcopy(current)
        best_cost = current_cost
        T, T_min, alpha = 2.0, 0.001, 0.9995

        max_iters = max(100_000, N * N * 1000)
        for _ in range(max_iters):
            self.states_explored += 1
            if current_cost == 0:
                break
            # pick random box
            br = random.choice(list(range(0, N, self.box_h)))
            bc = random.choice(list(range(0, N, self.box_w)))
            free = [
                (r, c)
                for r in range(br, br + self.box_h)
                for c in range(bc, bc + self.box_w)
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
                # FIX: record ALL accepted swaps, not just when best improves
                current_cost = new_cost
                self._record(r1, col1, current[r1][col1], "swap")
                self._record(r2, col2, current[r2][col2], "swap")
                if current_cost < best_cost:
                    best = copy.deepcopy(current)
                    best_cost = current_cost
            else:
                current[r1][col1], current[r2][col2] = current[r2][col2], current[r1][col1]
            T *= alpha
            if T < T_min:
                T = 0.5

        return best_cost == 0, best

    def _count_violations(self, grid):
        N = self.N
        v = 0
        for r in range(N):
            row = [grid[r][c] for c in range(N) if grid[r][c] != 0]
            v += len(row) - len(set(row))
        for c in range(N):
            col = [grid[r][c] for r in range(N) if grid[r][c] != 0]
            v += len(col) - len(set(col))
        return v
