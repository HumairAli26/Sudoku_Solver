"""
gui/animator.py
Plays solver steps back onto a GridWidget with speed control,
play/pause, step-forward, and completion callback.
"""

import copy


class StepAnimator:
    """
    Drives step-by-step playback of a solver result onto a GridWidget.

    Usage:
        anim = StepAnimator(grid_widget, result, delay_ms=30,
                            on_done=lambda: ...)
        anim.start()
        anim.pause()
        anim.resume()
        anim.step()       # single step forward
        anim.set_delay(d) # change speed live
        anim.stop()       # cancel entirely
    """

    def __init__(self, widget, result: dict, delay_ms: int = 30,
                 on_step=None, on_done=None):
        self._widget    = widget
        self._steps     = result["steps"]
        self._solution  = result["solution"]
        self._delay     = delay_ms
        self._on_step   = on_step    # callback(step_index, total)
        self._on_done   = on_done    # callback()

        self._idx       = 0
        self._paused    = False
        self._after_id  = None
        self._running   = False

        # build the intermediate grid state for playback
        self._grid = copy.deepcopy(widget.get_grid())

    # ── control ───────────────────────────────────────────────────────────────

    def start(self):
        self._running = True
        self._paused  = False
        self._tick()

    def pause(self):
        self._paused = True
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None

    def resume(self):
        if not self._running:
            return
        self._paused = False
        self._tick()

    def stop(self):
        self._running = False
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None

    def step(self):
        """Advance one step (works while paused)."""
        if self._idx < len(self._steps):
            self._apply_step(self._steps[self._idx])
            self._idx += 1
            if self._on_step:
                self._on_step(self._idx, len(self._steps))
        if self._idx >= len(self._steps):
            self._finish()

    def set_delay(self, ms: int):
        self._delay = max(1, ms)

    @property
    def total(self):
        return len(self._steps)

    @property
    def index(self):
        return self._idx

    @property
    def is_paused(self):
        return self._paused

    @property
    def is_running(self):
        return self._running

    # ── internals ─────────────────────────────────────────────────────────────

    def _tick(self):
        if not self._running or self._paused:
            return
        if self._idx >= len(self._steps):
            self._finish()
            return
        self._apply_step(self._steps[self._idx])
        self._idx += 1
        if self._on_step:
            self._on_step(self._idx, len(self._steps))
        self._after_id = self._widget.after(self._delay, self._tick)

    def _apply_step(self, step):
        r, c, v, action = step["r"], step["c"], step["v"], step["action"]
        self._grid[r][c] = v
        if action == "place":
            state = "active"
        elif action == "remove":
            state = "remove"
        elif action == "swap":
            state = "swap"
        else:
            state = "solved"
        self._widget.set_cell(r, c, v, state)

    def _finish(self):
        self._running = False
        # show final solution, all cells marked solved
        for r in range(9):
            for c in range(9):
                v = self._solution[r][c] if self._solution else self._grid[r][c]
                cur_state = self._widget._state.get((r,c), "")
                if cur_state not in ("given",):
                    self._widget.set_cell(r, c, v, "solved")
        if self._on_done:
            self._on_done()
