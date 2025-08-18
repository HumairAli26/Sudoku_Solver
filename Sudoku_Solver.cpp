#include<iostream>
#include<vector>
#include<unordered_map>
#include <bits/stdc++.h>
using namespace std;

// Single-class Sudoku solver (9x9) using backtracking + constraint arrays for speed.
class SudokuSolver 
{
    vector<vector<int>> board;       // 9x9 board, 0 = empty
    bool rowUsed[9][10];            // rowUsed[r][num] == true if num used in row r
    bool colUsed[9][10];            // colUsed[c][num] == true if num used in col c
    bool boxUsed[9][10];            // boxUsed[b][num] == true if num used in 3x3 box b

public:
    SudokuSolver(const vector<vector<int>>& initial) 
    {
        board = initial;
        memset(rowUsed, 0, sizeof(rowUsed));
        memset(colUsed, 0, sizeof(colUsed));
        memset(boxUsed, 0, sizeof(boxUsed));
        // Initialize usage arrays from the initial board
        for (int r = 0; r < 9; ++r) 
        {
            for (int c = 0; c < 9; ++c) 
            {
                int v = board[r][c];
                if (v != 0) 
                {
                    int b = boxIndex(r, c);
                    rowUsed[r][v] = true;
                    colUsed[c][v] = true;
                    boxUsed[b][v] = true;
                }
            }
        }
    }

    // Attempt to solve; returns true if a solution was found.
    bool solve() 
    {
        return backtrack();
    }

    void printBoard() const 
    {
        for (int r = 0; r < 9; ++r) 
        {
            if (r % 3 == 0 && r != 0) 
                cout << "------+-------+------\n";
            for (int c = 0; c < 9; ++c) 
            {
                if (c % 3 == 0 && c != 0) cout << "| ";
                cout << board[r][c] << ' ';
            }
            cout << '\n';
        }
    }

private:
    static int boxIndex(int r, int c) 
    {
        return (r / 3) * 3 + (c / 3);
    }

    // Find next empty cell; returns pair(r,c) or (-1,-1) if none
    pair<int,int> findEmpty() const 
    {
        for (int r = 0; r < 9; ++r)
            for (int c = 0; c < 9; ++c)
                if (board[r][c] == 0)
                    return {r, c};
        return {-1, -1};
    }

    bool backtrack() 
    {
        auto [r, c] = findEmpty();
        if (r == -1) return true; // solved

        int b = boxIndex(r, c);
        // Try numbers 1..9
        for (int num = 1; num <= 9; ++num) 
        {
            if (!rowUsed[r][num] && !colUsed[c][num] && !boxUsed[b][num]) 
            {
                // place
                board[r][c] = num;
                rowUsed[r][num] = colUsed[c][num] = boxUsed[b][num] = true;
                if (backtrack()) return true;
                // undo
                board[r][c] = 0;
                rowUsed[r][num] = colUsed[c][num] = boxUsed[b][num] = false;
            }
        }
        return false; // trigger backtracking
    }
};

int main() 
{
    cout << "Enter 9 lines, each with 9 digits (0 for empty). You can put spaces between digits.\n";
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<vector<int>> grid(9, vector<int>(9, 0));
    for (int r = 0; r < 9; ++r) 
    {
        string line;
        if (!getline(cin, line) || line.empty()) 
        {
            // if an empty line was read (e.g., after program start), try reading again
            --r;
            continue;
        }
        // parse digits from the line (allow spaces)
        int idx = 0;
        for (char ch : line) 
        {
            if (idx >= 9) break;
            if (ch >= '0' && ch <= '9') 
            {
                grid[r][idx++] = ch - '0';
            }
        }
        // if fewer than 9 digits on this line, fill remaining with 0
        for (; idx < 9; ++idx) grid[r][idx] = 0;
    }

    SudokuSolver solver(grid);
    if (solver.solve()) 
    {
        cout << "\nSolution:\n";
        solver.printBoard();
    } 
    else 
    {
        cout << "No solution exists for the given puzzle.\n";
    }
    return 0;
}
