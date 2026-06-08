# Sudoku_Solver 
# 🧩 Sudoku Solver & Algorithm Visualization Suite---->sudoku_solver

A powerful desktop Sudoku application developed in **Python** using **Tkinter**, designed to generate, solve, visualize, and compare Sudoku puzzles using multiple Artificial Intelligence and Constraint Satisfaction algorithms.

The project combines puzzle generation, intelligent solving techniques, real-time animation, and performance analysis into a single educational and interactive platform. Whether you're a student studying AI search algorithms, a programmer exploring constraint satisfaction problems, or simply a Sudoku enthusiast, this application provides both functionality and insight into how different solving strategies work.

---

# 🎯 Project Objectives

The primary goals of this project are:

* Generate valid Sudoku puzzles of varying difficulty levels.
* Solve puzzles using multiple AI-based algorithms.
* Visualize the internal decision-making process of each solver.
* Compare algorithm performance using real-time statistics.
* Provide an interactive environment for experimentation and learning.

---

# ✨ Key Features

## 🎲 Intelligent Puzzle Generator

Generate valid Sudoku puzzles automatically with support for multiple board sizes:

* 4×4
* 6×6
* 9×9
* 12×12
* 16×16

Supported difficulty levels:

🟢 Easy
🟡 Medium
🟠 Hard
🔴 Expert

Each generated puzzle is guaranteed to have a valid solution.

---

## 🤖 Multiple AI Solving Algorithms

The application implements four distinct solving strategies, each demonstrating different approaches to constraint satisfaction and search optimization.

### 1️⃣ Backtracking DFS

A classic depth-first search algorithm that recursively tries possible values and backtracks whenever a conflict occurs.

**Advantages**

* Simple implementation
* Guaranteed to find a solution if one exists
* Works reliably on all puzzle sizes

**Best For**

* Educational demonstrations
* Understanding recursive search

---

### 2️⃣ AC-3 + MRV

Combines:

* AC-3 (Arc Consistency Algorithm)
* MRV (Minimum Remaining Values Heuristic)

The algorithm aggressively reduces possible values before performing search.

**Advantages**

* Fastest solver in most cases
* Explores significantly fewer states
* Efficient for difficult puzzles

**Best For**

* Performance optimization
* Constraint satisfaction demonstrations

---

### 3️⃣ Forward Checking

Maintains future consistency by updating neighboring domains after every assignment.

**Advantages**

* Faster than pure backtracking
* Reduces unnecessary exploration
* Easier to understand than AC-3

**Best For**

* Intermediate CSP techniques
* Educational comparisons

---

### 4️⃣ Simulated Annealing

A stochastic optimization algorithm inspired by the annealing process used in metallurgy.

**Advantages**

* Non-deterministic approach
* Handles larger grids efficiently
* Demonstrates heuristic optimization concepts

**Best For**

* AI and optimization studies
* Large-scale Sudoku experimentation

---

# 🎬 Real-Time Visualization System

One of the most unique aspects of the project is its advanced animation engine.

Users can watch algorithms solve puzzles step by step in real time.

Visualization highlights:

🟦 Current Cell Being Explored
🟩 Successful Placement
🟥 Backtracking Action
🟨 Simulated Annealing Swap
⚪ Original Given Clues
🏆 Final Solved State

---

# 🎮 Interactive Playback Controls

The animation system includes:

▶ Play
⏸ Pause
⏭ Step Forward
⏮ Step Back
⚡ Adjustable Speed Controls

This allows users to carefully observe how each algorithm explores the search space.

---

# 📊 Algorithm Comparison Dashboard

The comparison window executes all four algorithms on the same puzzle simultaneously.

Performance metrics include:

* Total Solve Time
* States Explored
* Backtracking Count
* Success Rate
* Completion Status

This provides a side-by-side analysis of algorithm efficiency and behavior.

---

# ✍ Manual Puzzle Entry

Users can:

* Clear the board
* Enter their own Sudoku puzzle
* Load custom challenges
* Test algorithm performance on personal puzzles

This feature makes the application useful beyond generated puzzles.

---

# 🏗 Software Architecture

The project follows a modular architecture for maintainability and scalability.

## Project Structure

```text
sudoku_solver/
├── main.py
├── app.py
├── engine/
│   ├── solver.py
│   ├── generator.py
│   └── algorithms/
│       ├── base.py
│       ├── backtracking.py
│       ├── ac3_mrv.py
│       ├── forward_checking.py
│       └── simulated_annealing.py
└── gui/
    ├── grid_widget.py
    ├── sidebar.py
    ├── animator.py
    ├── compare_window.py
    └── theme.py
```

---

# 🛠 Technology Stack

### Programming Language

* Python 3.10+

### GUI Framework

* Tkinter

### Algorithms

* Backtracking DFS
* AC-3 Constraint Propagation
* MRV Heuristic Search
* Forward Checking
* Simulated Annealing

### Architecture

* Object-Oriented Design
* Modular MVC-inspired Structure

---

# 📋 Requirements

The project has minimal dependencies.

Required:

* Python 3.10+
* Tkinter

No third-party packages are required.

---

# 📖 Usage Guide

## Generate a Puzzle

1. Select board size.
2. Choose difficulty.
3. Click **Generate Puzzle**.

---

## Solve a Puzzle

1. Select an algorithm.
2. Click **Solve & Animate**.
3. Watch the solving process in real time.

---

## Compare Algorithms

1. Generate or enter a puzzle.
2. Click **Solve All**.
3. Observe the performance comparison window.

---

## Enter a Custom Puzzle

1. Clear the current board.
2. Type your puzzle manually.
3. Run any algorithm of your choice.

---

# 🎓 Educational Value

This project serves as an excellent learning platform for:

* Artificial Intelligence
* Constraint Satisfaction Problems (CSP)
* Search Algorithms
* Heuristic Optimization
* Recursive Problem Solving
* GUI Development in Python
* Algorithm Visualization Techniques

---

# 🔬 Future Enhancements

Potential future improvements include:

* Dark Mode Theme
* Save/Load Puzzle Functionality
* Puzzle Import/Export
* Hint Generation System
* Machine Learning-Based Solvers
* Web-Based Version
* Multi-threaded Algorithm Execution
* Statistical Performance Graphs

---

# 🏆 Conclusion

The Sudoku Solver & Algorithm Visualization Suite is more than just a Sudoku application. It is a complete educational platform that demonstrates how various Artificial Intelligence and Constraint Satisfaction algorithms solve complex problems. By combining puzzle generation, real-time visualization, algorithm comparison, and interactive controls, the project offers an engaging way to explore both Sudoku and modern problem-solving techniques.

# 🧩 Sudoku Solver Using Backtracking in C++---->Sudoku_Solver.cpp

This C++ program implements a **Sudoku Solver** using the **Backtracking Algorithm**, a classic problem-solving technique based on recursion and trial-and-error. The program accepts a **9×9 Sudoku puzzle** as input, where empty cells are represented by **0**, and efficiently finds a valid solution while following all standard Sudoku rules.

## 🎯 Objective

The goal of the program is to fill all empty cells in the Sudoku grid such that:

✅ Each row contains numbers **1–9** without repetition.
✅ Each column contains numbers **1–9** without repetition.
✅ Each **3×3 sub-grid** contains numbers **1–9** without repetition.

---

## 🏗️ Program Structure

The solution is built around the **`SudokuSolver`** class, which manages the puzzle board and solving process.

### 📌 Data Representation

* The Sudoku board is stored using a **two-dimensional vector**.
* Three boolean tracking arrays are used:

  * **`rowUsed`** → Tracks numbers already present in each row.
  * **`colUsed`** → Tracks numbers already present in each column.
  * **`boxUsed`** → Tracks numbers already present in each 3×3 sub-grid.

During initialization, these arrays are updated according to the given puzzle configuration. This preprocessing step allows the program to verify valid moves quickly and efficiently.

---

## 🔄 Backtracking Algorithm

The core logic is implemented in the **`backtrack()`** function.

### ⚙️ Working Procedure

1. Search for the next empty cell (`0`).
2. Try placing numbers **1–9** in that cell.
3. Check whether the number satisfies Sudoku constraints.
4. If valid:

   * Place the number.
   * Update tracking arrays.
   * Recursively solve the remaining puzzle.
5. If no valid number works:

   * Remove the previously placed number.
   * Restore tracking arrays.
   * Backtrack and try another possibility.

This process continues until:

* 🎉 The entire board is successfully filled, or
* ❌ The puzzle is determined to have no valid solution.

---

## 💻 User Interaction

The program requires the user to enter:

📝 **9 rows**, each containing **9 digits**.

Example Input:

0 0 3 0 2 0 6 0 0
9 0 0 3 0 5 0 0 1
0 0 1 8 0 6 4 0 0
...

After solving, the program displays the completed Sudoku grid in a clean and organized format, with separators between the **3×3 sub-grids** for improved readability.

If no valid solution exists, the program outputs:

❌ **"No solution exists for the given Sudoku puzzle."**

---

## ✨ Key Concepts Demonstrated

🔹 Recursion
🔹 Backtracking Algorithms
🔹 Constraint Satisfaction Problems (CSP)
🔹 Efficient State Tracking using Boolean Arrays
🔹 Object-Oriented Programming (OOP) in C++
🔹 Problem Solving and Algorithm Design

---

## 📊 Conclusion

This Sudoku Solver is an excellent demonstration of how **recursion** and **backtracking** can be applied to solve complex constraint-based problems efficiently. By utilizing optimized tracking structures for rows, columns, and sub-grids, the program significantly reduces unnecessary computations and improves performance. It serves as both a practical Sudoku-solving tool and a valuable educational example for understanding algorithmic problem-solving techniques in C++.

Overall, this code demonstrates practical use of recursion, backtracking, and constraint checking in solving a well-known logic puzzle, making it both an educational and functional example of algorithmic problem-solving in C++.
