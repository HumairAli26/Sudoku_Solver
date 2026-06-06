"""
engine/generator.py
Generates valid Sudoku puzzles with guaranteed unique solutions.
"""

import random
import copy


class SudokuGenerator:
    DIFFICULTY_CLUES = {
        "Easy":   {"min": 36, "max": 45},
        "Medium": {"min": 27, "max": 35},
        "Hard":   {"min": 22, "max": 26},
        "Expert": {"min": 17, "max": 21},
    }

    def generate(self, difficulty: str = "Medium"):
        """Return (puzzle, solution) as 9×9 lists of ints (0 = empty)."""
        grid = self._generate_full_grid()
        solution = copy.deepcopy(grid)
        clue_range = self.DIFFICULTY_CLUES.get(difficulty, self.DIFFICULTY_CLUES["Medium"])
        target_clues = random.randint(clue_range["min"], clue_range["max"])
        puzzle = self._remove_cells(grid, target_clues)
        return puzzle, solution

    # ── internals ──────────────────────────────────────────────────────────────

    def _generate_full_grid(self):
        grid = [[0] * 9 for _ in range(9)]
        self._fill_grid(grid)
        return grid

    def _fill_grid(self, grid):
        nums = list(range(1, 10))
        for i in range(81):
            r, c = divmod(i, 9)
            if grid[r][c] == 0:
                random.shuffle(nums)
                for n in nums:
                    if self._is_valid(grid, r, c, n):
                        grid[r][c] = n
                        if self._fill_grid(grid):
                            return True
                        grid[r][c] = 0
                return False
        return True

    def _is_valid(self, grid, row, col, num):
        if num in grid[row]:
            return False
        if num in [grid[r][col] for r in range(9)]:
            return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if grid[r][c] == num:
                    return False
        return True

    def _remove_cells(self, grid, target_clues):
        puzzle = copy.deepcopy(grid)
        cells = list(range(81))
        random.shuffle(cells)
        removed = 0
        target_remove = 81 - target_clues
        for idx in cells:
            if removed >= target_remove:
                break
            r, c = divmod(idx, 9)
            backup = puzzle[r][c]
            puzzle[r][c] = 0
            test = copy.deepcopy(puzzle)
            if self._count_solutions(test) == 1:
                removed += 1
            else:
                puzzle[r][c] = backup
        return puzzle

    def _count_solutions(self, grid, count=0):
        for i in range(81):
            r, c = divmod(i, 9)
            if grid[r][c] == 0:
                for n in range(1, 10):
                    if self._is_valid(grid, r, c, n):
                        grid[r][c] = n
                        count = self._count_solutions(grid, count)
                        grid[r][c] = 0
                        if count > 1:
                            return count
                return count
        return count + 1
