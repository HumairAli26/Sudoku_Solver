"""
engine/algorithms/forward_checking.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Algorithm: Forward Checking with MRV Ordering
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS:
  Forward Checking sits between plain Backtracking and full AC-3.

  1. Maintain a domain for each unassigned cell.
  2. When a value is assigned to cell (r, c):
       - Remove that value from the domain of every PEER of (r, c).
       - If any peer's domain becomes EMPTY, the assignment is infeasible
         → immediately backtrack (no need to recurse deeper).
  3. Choose the next cell using MRV (fewest remaining values).
  4. On backtrack, restore the domains as they were before the assignment.

WHY IT'S BETTER THAN PLAIN BACKTRACKING:
  - Detects dead ends one level earlier (after each assignment rather
    than when an empty cell is actually reached).
  - Avoids exploring subtrees that are provably unsolvable.
  - Cheaper per node than full AC-3 (only checks direct peers).

COMPARISON WITH AC-3:
  - Forward Checking: prunes peers of the *current* assignment only.
  - AC-3: propagates pruning transitively across the whole constraint graph.
  - Result: FC is faster per node; AC-3 prunes more aggressively.

TYPICAL PERFORMANCE:
  - Generally faster than Backtracking.
  - Slower than AC-3+MRV on very hard puzzles, but competitive on medium ones.
"""

import copy
from .base import BaseSolver


class ForwardCheckingSolver(BaseSolver):
    ALGORITHM_KEY = "forward_checking"
    DISPLAY_NAME  = "Forward Checking"

    def _run(self, grid):
        domains = self._get_domains(grid)
        return self._fc_search(grid, domains)

    def _fc_search(self, grid, domains):
        self.states_explored += 1
        empty = [
            (r, c) for r in range(self.N) for c in range(self.N)
            if grid[r][c] == 0
        ]
        if not empty:
            return True, grid
        r, c = min(empty, key=lambda cell: len(domains[cell]))
        for val in sorted(domains[(r, c)]):
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
                # FIX: only count as backtrack when we actually returned from recursion
                self.backtracks += 1
            grid[r][c] = 0
            self._record(r, c, 0, "remove")
        return False, grid
