"""
engine/algorithms/backtracking.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm: Backtracking DFS (Uninformed Search)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS:
  1. Find the next empty cell (left-to-right, top-to-bottom).
  2. Try placing each value 1..N in that cell.
  3. If the placement is valid (no conflicts in row/col/box), recurse.
  4. If no value works, backtrack to the previous cell and try the next.
  5. Repeat until the board is fully filled (solved) or exhausted (unsolvable).

COMPLEXITY:
  - Time:  O(N^(N²)) worst case (N values, N² cells)
  - Space: O(N²) stack depth

STRENGTHS:
  + Simple to implement and understand
  + Complete — always finds a solution if one exists
  + Uses very little memory

WEAKNESSES:
  - No intelligent cell/value ordering — can explore many dead ends
  - Slow on hard puzzles with few clues

This is the baseline algorithm. All other algorithms in this project
improve on it by adding heuristics or constraint propagation.
"""

from .base import BaseSolver


class BacktrackingSolver(BaseSolver):
    ALGORITHM_KEY = "backtracking"
    DISPLAY_NAME  = "Backtracking DFS"

    def _run(self, grid):
        return self._search(grid)

    def _search(self, grid):
        self.states_explored += 1
        empty = self._find_empty(grid)
        if not empty:
            return True, grid
        r, c = empty
        for num in self.values:
            if self._is_valid(grid, r, c, num):
                grid[r][c] = num
                self._record(r, c, num, "place")
                ok, sol = self._search(grid)
                if ok:
                    return True, sol
                grid[r][c] = 0
                self.backtracks += 1
                self._record(r, c, 0, "remove")
        return False, grid
