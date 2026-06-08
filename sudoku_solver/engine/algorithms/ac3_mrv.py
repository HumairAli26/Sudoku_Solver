"""
engine/algorithms/ac3_mrv.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm: AC-3 Constraint Propagation + MRV Heuristic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS:

  PHASE 1 — AC-3 (Arc Consistency 3):
    Build a queue of all arcs (xi, xj) where xi and xj are peers.
    For each arc, remove values from xi's domain that have no valid
    support in xj's domain. When a domain changes, re-add all arcs
    pointing TO xi, as they may now need pruning.
    If any domain becomes empty → contradiction, return False.

  PHASE 2 — MRV Search (Minimum Remaining Values):
    Pick the unassigned cell with the FEWEST remaining values in its
    domain (most constrained cell first). Break ties by choosing the
    cell with the MOST constrained peers (degree heuristic).
    For each candidate value, run AC-3 on a copy of the domains, then
    recurse. Backtrack if no value leads to a solution.

WHY IT'S BETTER THAN PLAIN BACKTRACKING:
  - AC-3 eliminates many impossible values before searching.
  - MRV ordering focuses the search on the hardest decisions first,
    failing early when a path is infeasible.
  - Dramatically reduces the number of states explored on most puzzles.

COMPLEXITY:
  - AC-3:    O(N³ · d²) where d is max domain size
  - Overall: much faster in practice despite higher constant cost per node
"""

from collections import deque
from .base import BaseSolver


class AC3MRVSolver(BaseSolver):
    ALGORITHM_KEY = "ac3_mrv"
    DISPLAY_NAME  = "AC-3 + MRV"

    def __init__(self, puzzle):
        super().__init__(puzzle)
        # FIX: pre-cache peers for every cell — _get_peers was being recomputed
        # thousands of times per solve; caching makes AC-3 much faster
        self._peers_cache = {
            (r, c): self._get_peers(r, c)
            for r in range(self.N)
            for c in range(self.N)
        }

    def _run(self, grid):
        domains = self._get_domains(grid)
        if not self._ac3(domains):
            return False, grid
        return self._mrv_search(grid, domains)

    # ── AC-3 ──────────────────────────────────────────────────────────────────

    def _ac3(self, domains):
        # FIX: use deque for O(1) popleft instead of O(n) pop(0) on a list
        queue = deque((xi, xj) for xi in domains for xj in self._peers_cache[xi])
        while queue:
            xi, xj = queue.popleft()
            if self._revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                for xk in self._peers_cache[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains, xi, xj):
        # Remove values from xi's domain that have no support in xj's domain.
        # For the ≠ constraint: val has no support iff every value in xj equals val
        # (meaning xj is forced to val, so xi cannot also be val).
        # FIX: short-circuit with len check before the costly set comprehension
        dj = domains[xj]
        if len(dj) > 1:
            return False  # xj has multiple values → every xi value has support
        # xj has exactly one value — remove it from xi if present
        (only,) = dj
        if only in domains[xi]:
            domains[xi].discard(only)
            return True
        return False

    # ── MRV search ────────────────────────────────────────────────────────────

    def _mrv_cell(self, domains, grid):
        best = None
        best_mrv = float("inf")
        best_deg = -1
        for r in range(self.N):
            for c in range(self.N):
                if grid[r][c] != 0:
                    continue
                mrv = len(domains[(r, c)])
                deg = sum(1 for p in self._peers_cache[(r, c)] if grid[p[0]][p[1]] == 0)
                if mrv < best_mrv or (mrv == best_mrv and deg > best_deg):
                    best, best_mrv, best_deg = (r, c), mrv, deg
        return best

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
                # FIX: shallow-copy the domains dict with individual set copies —
                # far cheaper than copy.deepcopy on a dict of sets
                new_domains = {k: set(v) for k, v in domains.items()}
                new_domains[(r, c)] = {val}
                if self._ac3(new_domains):
                    ok, sol = self._mrv_search(grid, new_domains)
                    if ok:
                        return True, sol
                grid[r][c] = 0
                self.backtracks += 1
                self._record(r, c, 0, "remove")
        return False, grid
