# CodeAlpha_Sudoku_Solver
This C++ program implements a Sudoku Solver using a backtracking algorithm. The program accepts a 9x9 Sudoku grid as input, where empty cells are represented by zero, and then attempts to find a valid solution following Sudoku rules. The solution ensures that each row, column, and 3x3 sub-grid contains all numbers from 1 to 9 without repetition.

The program is structured around the SudokuSolver class. The board is stored as a two-dimensional vector, and three boolean arrays (rowUsed, colUsed, and boxUsed) are used to track whether a particular number is already present in a row, column, or sub-grid. During initialization, these arrays are updated based on the starting puzzle configuration. This setup improves efficiency by quickly checking if a number can be placed in a given position.

The core solving process is handled by the backtrack function, which applies recursion and backtracking. It searches for the next empty cell, tries numbers 1 through 9, and checks whether placing a number is valid according to the Sudoku rules. If a valid number is placed, the algorithm recursively proceeds. If no valid number is found, it backtracks by resetting the cell and trying alternative values. The process continues until the board is completely filled or determined unsolvable.

For user interaction, the program requests nine lines of input, each containing nine digits. After solving, it prints the Sudoku grid in a structured format, separating sub-grids for clarity. If no solution exists, an appropriate message is displayed.

Overall, this code demonstrates practical use of recursion, backtracking, and constraint checking in solving a well-known logic puzzle, making it both an educational and functional example of algorithmic problem-solving in C++.
