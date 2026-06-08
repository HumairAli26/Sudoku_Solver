"""
engine/generator.py
Generates valid Sudoku puzzles for sizes: 4x4, 6x6, 9x9, 12x12, 16x16.
"""
import random
import copy


class SudokuGenerator:
    # (box_h, box_w) for each N
    SIZE_BOXES = {4: (2,2), 6: (2,3), 9: (3,3), 12: (3,4), 16: (4,4)}

    DIFFICULTY_CLUE_RATIO = {
        "Easy":   (0.55, 0.65),
        "Medium": (0.40, 0.54),
        "Hard":   (0.30, 0.39),
        "Expert": (0.20, 0.29),
    }

    def generate(self, difficulty: str = "Medium", size: int = 9):
        """Return (puzzle, solution) as N×N lists of ints (0 = empty)."""
        self.N = size
        self.box_h, self.box_w = self.SIZE_BOXES.get(size, (3, 3))
        self.values = list(range(1, size + 1))

        grid = self._generate_full_grid()
        solution = copy.deepcopy(grid)
        lo, hi = self.DIFFICULTY_CLUE_RATIO.get(difficulty, (0.40, 0.54))
        total = size * size
        target_clues = random.randint(int(lo * total), int(hi * total))
        puzzle = self._remove_cells(grid, target_clues)
        return puzzle, solution

    def _generate_full_grid(self):
        grid = [[0] * self.N for _ in range(self.N)]
        self._fill_grid(grid)
        return grid

    def _fill_grid(self, grid):
        nums = self.values[:]
        for i in range(self.N * self.N):
            r, c = divmod(i, self.N)
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
        if num in [grid[r][col] for r in range(self.N)]:
            return False
        br = self.box_h * (row // self.box_h)
        bc = self.box_w * (col // self.box_w)
        for r in range(br, br + self.box_h):
            for c in range(bc, bc + self.box_w):
                if grid[r][c] == num:
                    return False
        return True

    def _remove_cells(self, grid, target_clues):
        puzzle = copy.deepcopy(grid)
        cells = list(range(self.N * self.N))
        random.shuffle(cells)
        removed = 0
        target_remove = self.N * self.N - target_clues
        for idx in cells:
            if removed >= target_remove:
                break
            r, c = divmod(idx, self.N)
            backup = puzzle[r][c]
            puzzle[r][c] = 0
            test = copy.deepcopy(puzzle)
            if self._count_solutions(test) == 1:
                removed += 1
            else:
                puzzle[r][c] = backup
        return puzzle

    def _count_solutions(self, grid, count=0):
        for i in range(self.N * self.N):
            r, c = divmod(i, self.N)
            if grid[r][c] == 0:
                for n in self.values:
                    if self._is_valid(grid, r, c, n):
                        grid[r][c] = n
                        count = self._count_solutions(grid, count)
                        grid[r][c] = 0
                        if count > 1:
                            return count
                return count
        return count + 1
