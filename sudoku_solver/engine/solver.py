import copy
from engine.algorithms import (
    BacktrackingSolver,
    AC3MRVSolver,
    ForwardCheckingSolver,
    SimulatedAnnealingSolver,
)

ALGORITHM_CLASSES = {
    "backtracking":        BacktrackingSolver,
    "ac3_mrv":             AC3MRVSolver,
    "forward_checking":    ForwardCheckingSolver,
    "simulated_annealing": SimulatedAnnealingSolver,
}

ALGORITHM_NAMES = {
    "backtracking":        "Backtracking DFS",
    "ac3_mrv":             "AC-3 + MRV",
    "forward_checking":    "Forward Checking",
    "simulated_annealing": "Simulated Annealing",
}


class SudokuSolver:
    """Thin wrapper — picks the right algorithm class and runs it."""

    def __init__(self, puzzle: list[list[int]]):
        self.puzzle = copy.deepcopy(puzzle)

    def solve(self, algorithm: str) -> dict:
        cls = ALGORITHM_CLASSES.get(algorithm)
        if cls is None:
            raise ValueError(f"Unknown algorithm: {algorithm!r}")
        solver = cls(self.puzzle)
        result = solver.solve()
        return result
