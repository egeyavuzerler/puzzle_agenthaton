"""
core/live_view.py

GERÇEK ZAMANLI görünüm: GIF/video KAYDETMEZ, solver çalışırken doğrudan
ekranda bir matplotlib penceresi açıp CANLI günceller.
"""

import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

_NON_GUI_BACKENDS = {"agg", "pdf", "svg", "ps", "cairo", "template"}


def _has_gui_backend() -> bool:
    return matplotlib.get_backend().lower() not in _NON_GUI_BACKENDS


CHECKPOINT_DONE = "#1a1a1a"
CHECKPOINT_PENDING = "#bbbbbb"
PATH_COLOR = "#ff7a3d"
BLOCKED_COLOR = "#2b2b2b"
GRID_COLOR = "#999999"
QUEEN_MARKER = "♛"
REGION_CMAP = plt.get_cmap("tab20")


class LiveQueensView:
    def __init__(self, puzzle, redraw_every=1, pause=0.05):
        self.puzzle = puzzle
        self.rows, self.cols = puzzle["size"]
        self.regions = puzzle["regions"]
        self.redraw_every = max(1, redraw_every)
        self.pause = pause
        self._step_count = 0

        self._gui = _has_gui_backend()
        if not self._gui:
            print(f"[UYARI] GUI backend yok ({matplotlib.get_backend()}), sadece ilerleme yazdirilacak.")
            self.fig = self.ax = None
            self._texts = []
            return

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(self.cols * 0.7 + 1, self.rows * 0.7 + 1))
        self.fig.canvas.manager.set_window_title("Queens -- canli cozum")
        ax = self.ax
        ax.set_xlim(0, self.cols)
        ax.set_ylim(0, self.rows)
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])

        for r in range(self.rows):
            for c in range(self.cols):
                color = REGION_CMAP(self.regions[r][c] % 20)
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor=color, edgecolor=GRID_COLOR, linewidth=1))

        self._texts = []
        self._title = ax.set_title("basliyor...", fontsize=10)
        self.fig.canvas.draw()
        plt.show(block=False)

    def _redraw(self, placement, title):
        for t in self._texts:
            t.remove()
        self._texts = []
        for r, c in placement:
            t = self.ax.text(c + 0.5, r + 0.5, QUEEN_MARKER, ha="center", va="center", fontsize=22, zorder=3)
            self._texts.append(t)
        self._title.set_text(title)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def on_step(self, placement, event):
        self._step_count += 1
        if not self._gui:
            return
        if self._step_count % self.redraw_every != 0:
            return
        self._redraw(placement, title=f"adim {self._step_count} | yerlesen: {len(placement)}/{self.rows} | {event}")
        plt.pause(self.pause)

    def finish(self, result):
        placement = [tuple(p) for p in result.solution] if result.solved else []
        status = "COZULDU" if result.solved else f"COZULEMEDI ({result.error})"
        print(f"\n{status} -- toplam {self._step_count} adim")

        if not self._gui:
            return

        self._redraw(placement, title=f"{status} | {self._step_count} adimda")
        plt.ioff()
        print("Pencereyi kapatmak icin uzerine tiklayip kapatabilir ya da Ctrl+C ile cikabilirsin.")
        plt.show(block=True)
