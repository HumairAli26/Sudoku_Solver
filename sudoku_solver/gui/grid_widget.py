"""
gui/grid_widget.py
Canvas-based Sudoku grid — supports 4×4, 6×6, 9×9, 12×12, 16×16.
"""

import tkinter as tk
from gui.theme import *

# box dimensions per N
SIZE_BOXES = {4: (2,2), 6: (2,3), 9: (3,3), 12: (3,4), 16: (4,4)}


class GridWidget(tk.Canvas):
    """Canvas that draws an N×N Sudoku grid and animates solve steps."""

    def __init__(self, master, on_cell_edit=None, size=9, **kwargs):
        self._N   = size
        self._C   = CELL_SIZE_MAP.get(size, 54)
        self._G   = BOX_GAP
        self._P   = OUTER_PAD
        self._bh, self._bw = SIZE_BOXES.get(size, (3, 3))
        sz = self._total_size()

        super().__init__(master, width=sz, height=sz,
                         bg=BG, highlightthickness=0, **kwargs)

        self._on_cell_edit = on_cell_edit
        self._grid   = [[0]*size for _ in range(size)]
        self._given  = set()
        self._sel    = None
        self._state  = {}

        self._draw_bg()
        self._draw_lines()

        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>",      self._on_key)
        self.configure(takefocus=True)

    # ── geometry ──────────────────────────────────────────────────────────────

    def _total_size(self):
        n_boxes_h = self._N // self._bh
        n_boxes_w = self._N // self._bw
        return 2*self._P + self._N*self._C + (n_boxes_w-1)*self._G

    def _cell_xy(self, r, c):
        x = self._P + c*self._C + (c//self._bw)*self._G
        y = self._P + r*self._C + (r//self._bh)*self._G
        return x, y

    def _pixel_to_cell(self, px, py):
        for r in range(self._N):
            for c in range(self._N):
                x, y = self._cell_xy(r, c)
                if x <= px < x+self._C and y <= py < y+self._C:
                    return r, c
        return None

    # ── initial draw ──────────────────────────────────────────────────────────

    def _draw_bg(self):
        self._bg_rects = {}
        for r in range(self._N):
            for c in range(self._N):
                bx, by = c//self._bw, r//self._bh
                fill = CELL_BG_A if (bx+by)%2 == 0 else CELL_BG_B
                x, y = self._cell_xy(r, c)
                rid = self.create_rectangle(x, y, x+self._C, y+self._C,
                                            fill=fill, outline="", tags="bg")
                self._bg_rects[(r,c)] = rid

    def _draw_lines(self):
        sz = self._total_size()
        n_boxes_h = self._N // self._bh
        n_boxes_w = self._N // self._bw

        # draw cell lines
        for i in range(self._N + 1):
            is_box_h = (i % self._bh == 0)
            is_box_w = (i % self._bw == 0)
            x = self._P + i*self._C + (i//self._bw)*self._G
            y = self._P + i*self._C + (i//self._bh)*self._G

            w_v = BORDER_THICK if is_box_w else BORDER_THIN
            col_v = ACCENT if is_box_w else BORDER
            self.create_line(x, self._P, x, sz-self._P,
                             width=w_v, fill=col_v, tags="line")

            w_h = BORDER_THICK if is_box_h else BORDER_THIN
            col_h = ACCENT if is_box_h else BORDER
            self.create_line(self._P, y, sz-self._P, y,
                             width=w_h, fill=col_h, tags="line")

    # ── public API ────────────────────────────────────────────────────────────

    @property
    def grid_size(self):
        return self._N

    def resize(self, new_size):
        """Rebuild the grid for a new size."""
        self._N = new_size
        self._C = CELL_SIZE_MAP.get(new_size, 54)
        self._bh, self._bw = SIZE_BOXES.get(new_size, (3, 3))
        sz = self._total_size()
        self.config(width=sz, height=sz)
        self._grid  = [[0]*new_size for _ in range(new_size)]
        self._given = set()
        self._state = {}
        self._sel   = None
        self.delete("all")
        self._draw_bg()
        self._draw_lines()

    def load_puzzle(self, puzzle, given_set=None):
        self._grid = [row[:] for row in puzzle]
        self._state = {}
        if given_set is not None:
            self._given = set(given_set)
        else:
            self._given = {(r,c) for r in range(self._N) for c in range(self._N)
                           if puzzle[r][c] != 0}
        for pos in self._given:
            self._state[pos] = "given"
        self._sel = None
        self._redraw_all()

    def get_grid(self):
        return [row[:] for row in self._grid]

    def set_cell(self, r, c, value, state="solved"):
        self._grid[r][c] = value
        self._state[(r,c)] = state
        self._redraw_cell(r, c)

    def flash_cell(self, r, c, state):
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
        self._grid  = [[0]*self._N for _ in range(self._N)]
        self._given = set()
        self._state = {}
        self._sel   = None
        self._redraw_all()

    def unlock_all(self):
        self._given = set()
        self._state = {}
        self._redraw_all()

    # ── drawing ───────────────────────────────────────────────────────────────

    def _cell_fill(self, r, c):
        if self._sel == (r,c):
            return CELL_SEL
        st = self._state.get((r,c), "")
        if st == "remove": return "#3a0f1f"
        if st == "swap":   return "#2a1f00"
        if st == "active": return "#0f2a1f"
        bx, by = c//self._bw, r//self._bh
        return CELL_BG_A if (bx+by)%2 == 0 else CELL_BG_B

    def _cell_fg(self, r, c):
        st = self._state.get((r,c), "")
        if st == "given":  return GIVEN_FG
        if st == "remove": return REMOVE_FG
        if st == "swap":   return SWAP_FG
        if st == "active": return ACTIVE_FG
        return SOLVED_FG

    def _cell_font(self):
        return CELL_FONT_MAP.get(self._N, FONT_CELL)

    def _redraw_cell(self, r, c):
        fill = self._cell_fill(r, c)
        self.itemconfig(self._bg_rects[(r,c)], fill=fill)
        self.delete(f"cell_{r}_{c}")
        v = self._grid[r][c]
        if v:
            x, y = self._cell_xy(r, c)
            cx, cy = x + self._C//2, y + self._C//2
            # for 16x16 show hex-like display (A-G for 10-16)
            txt = str(v) if v <= 9 else chr(ord('A') + v - 10)
            self.create_text(cx, cy, text=txt,
                             font=self._cell_font(),
                             fill=self._cell_fg(r,c),
                             tags=(f"cell_{r}_{c}", "num"))
        self.delete(f"sel_{r}_{c}")
        if self._sel == (r, c):
            x, y = self._cell_xy(r, c)
            self.create_rectangle(x+2, y+2, x+self._C-2, y+self._C-2,
                                  outline=ACCENT2, width=2,
                                  tags=(f"sel_{r}_{c}", "sel"))

    def _redraw_all(self):
        self.delete("num", "sel")
        for r in range(self._N):
            for c in range(self._N):
                self._redraw_cell(r, c)
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
            self.select_cell((r+dr)%self._N, (c+dc)%self._N)
            return "break"
        if (r,c) in self._given:
            return "break"
        # accept 1-9 and A-G for 10-16
        val = None
        if event.char in "123456789":
            val = int(event.char)
        elif event.char.upper() in "ABCDEFG" and self._N > 9:
            val = ord(event.char.upper()) - ord('A') + 10
        if val is not None and 1 <= val <= self._N:
            self._grid[r][c] = val
            self._state[(r,c)] = ""
            self._redraw_cell(r, c)
            if self._on_cell_edit:
                self._on_cell_edit(r, c, str(val))
            return "break"
        if event.keysym in ("BackSpace", "Delete"):
            self._grid[r][c] = 0
            self._state.pop((r,c), None)
            self._redraw_cell(r, c)
            if self._on_cell_edit:
                self._on_cell_edit(r, c, "")
            return "break"
        return "break"
