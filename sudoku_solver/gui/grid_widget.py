"""
gui/grid_widget.py
Canvas-based Sudoku grid with:
  - Editable cells (keyboard navigation)
  - Step-by-step animation (place / remove / swap)
  - Colour-coded states: given, solved, backtrack, active
"""

import tkinter as tk
from gui.theme import *


class GridWidget(tk.Canvas):
    """A canvas that draws the 9×9 Sudoku grid and animates solve steps."""

    def __init__(self, master, on_cell_edit=None, **kwargs):
        # compute total canvas size
        self._C = CELL_SIZE
        self._G = BOX_GAP
        self._P = OUTER_PAD
        size = self._total_size()

        super().__init__(master,
                         width=size, height=size,
                         bg=BG, highlightthickness=0,
                         **kwargs)

        self._on_cell_edit = on_cell_edit  # callback(r, c, value_str)

        # state
        self._grid   = [[0]*9 for _ in range(9)]
        self._given  = set()          # (r,c) of clue cells
        self._sel    = None           # selected (r,c)
        self._state  = {}             # (r,c) → "given"|"solved"|"remove"|"swap"|"active"|""

        self._draw_bg()
        self._draw_lines()

        # interaction
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>",      self._on_key)
        self.configure(takefocus=True)

    # ── geometry helpers ──────────────────────────────────────────────────────

    def _total_size(self):
        return 2*self._P + 9*self._C + 2*self._G

    def _cell_xy(self, r, c):
        """Top-left pixel of cell (r,c)."""
        x = self._P + c*self._C + (c//3)*self._G
        y = self._P + r*self._C + (r//3)*self._G
        return x, y

    def _pixel_to_cell(self, px, py):
        """Convert canvas pixel → (r,c) or None."""
        for r in range(9):
            for c in range(9):
                x, y = self._cell_xy(r, c)
                if x <= px < x+self._C and y <= py < y+self._C:
                    return r, c
        return None

    # ── initial draw ──────────────────────────────────────────────────────────

    def _draw_bg(self):
        self._bg_rects = {}
        for r in range(9):
            for c in range(9):
                bx, by = c//3, r//3
                fill = CELL_BG_A if (bx+by)%2 == 0 else CELL_BG_B
                x, y = self._cell_xy(r, c)
                rid = self.create_rectangle(x, y, x+self._C, y+self._C,
                                            fill=fill, outline="", tags="bg")
                self._bg_rects[(r,c)] = rid

    def _draw_lines(self):
        sz = self._total_size()
        for i in range(10):
            bi = i // 3
            x = self._P + i*self._C + bi*self._G
            y = self._P + i*self._C + bi*self._G
            is_box = (i % 3 == 0)
            w   = BORDER_THICK if is_box else BORDER_THIN
            col = ACCENT if is_box else BORDER
            self.create_line(x, self._P, x, sz-self._P, width=w, fill=col, tags="line")
            self.create_line(self._P, y, sz-self._P, y, width=w, fill=col, tags="line")

    # ── public API ────────────────────────────────────────────────────────────

    def load_puzzle(self, puzzle, given_set=None):
        """Display a puzzle (9×9 list, 0=empty). given_set = set of (r,c)."""
        self._grid = [row[:] for row in puzzle]
        self._state = {}
        if given_set is not None:
            self._given = set(given_set)
        else:
            self._given = {(r,c) for r in range(9) for c in range(9) if puzzle[r][c] != 0}
        for pos in self._given:
            self._state[pos] = "given"
        self._sel = None
        self._redraw_all()

    def get_grid(self):
        return [row[:] for row in self._grid]

    def set_cell(self, r, c, value, state="solved"):
        """Programmatically set a cell (used by animator)."""
        self._grid[r][c] = value
        self._state[(r,c)] = state
        self._redraw_cell(r, c)

    def flash_cell(self, r, c, state):
        """Temporarily change the visual state of a cell."""
        self._state[(r,c)] = state
        self._redraw_cell(r, c)

    def select_cell(self, r, c):
        old = self._sel
        self._sel = (r, c)
        if old and old != (r,c):
            self._redraw_cell(*old)
        self._redraw_cell(r, c)
        self.focus_set()

    def clear_board(self):
        self._grid = [[0]*9 for _ in range(9)]
        self._given = set()
        self._state = {}
        self._sel = None
        self._redraw_all()

    def unlock_all(self):
        """Allow editing every cell (manual entry mode)."""
        self._given = set()
        self._state = {}
        self._redraw_all()

    # ── drawing ───────────────────────────────────────────────────────────────

    def _cell_fill(self, r, c):
        if self._sel == (r,c):
            return CELL_SEL
        st = self._state.get((r,c), "")
        if st == "remove":  return "#3a1f2a"
        if st == "swap":    return "#2a2215"
        if st == "active":  return "#1f2a3a"
        bx, by = c//3, r//3
        return CELL_BG_A if (bx+by)%2 == 0 else CELL_BG_B

    def _cell_fg(self, r, c):
        st = self._state.get((r,c), "")
        if st == "given":   return GIVEN_FG
        if st == "remove":  return REMOVE_FG
        if st == "swap":    return SWAP_FG
        if st == "active":  return ACTIVE_FG
        return SOLVED_FG

    def _redraw_cell(self, r, c):
        fill = self._cell_fill(r, c)
        self.itemconfig(self._bg_rects[(r,c)], fill=fill)
        # delete old text tag for this cell
        self.delete(f"cell_{r}_{c}")
        v = self._grid[r][c]
        if v:
            x, y = self._cell_xy(r, c)
            cx, cy = x + self._C//2, y + self._C//2
            self.create_text(cx, cy, text=str(v),
                             font=FONT_CELL, fill=self._cell_fg(r,c),
                             tags=(f"cell_{r}_{c}", "num"))
        # selection ring
        self.delete(f"sel_{r}_{c}")
        if self._sel == (r, c):
            x, y = self._cell_xy(r, c)
            self.create_rectangle(x+2, y+2, x+self._C-2, y+self._C-2,
                                  outline=ACCENT, width=2,
                                  tags=(f"sel_{r}_{c}", "sel"))

    def _redraw_all(self):
        self.delete("num", "sel")
        for r in range(9):
            for c in range(9):
                self._redraw_cell(r, c)
        # keep grid lines on top
        self.tag_raise("line")

    # ── interaction ───────────────────────────────────────────────────────────

    def _on_click(self, event):
        cell = self._pixel_to_cell(event.x, event.y)
        if cell:
            self.select_cell(*cell)

    def _on_key(self, event):
        if self._sel is None:
            return
        r, c = self._sel
        moves = {"Up": (-1,0), "Down": (1,0), "Left": (0,-1), "Right": (0,1)}
        if event.keysym in moves:
            dr, dc = moves[event.keysym]
            self.select_cell((r+dr)%9, (c+dc)%9)
            return "break"
        if (r,c) in self._given:
            return "break"
        if event.char in "123456789":
            self._grid[r][c] = int(event.char)
            self._state[(r,c)] = ""
            self._redraw_cell(r, c)
            if self._on_cell_edit:
                self._on_cell_edit(r, c, event.char)
            return "break"
        if event.keysym in ("BackSpace", "Delete"):
            self._grid[r][c] = 0
            self._state.pop((r,c), None)
            self._redraw_cell(r, c)
            if self._on_cell_edit:
                self._on_cell_edit(r, c, "")
            return "break"
        return "break"
