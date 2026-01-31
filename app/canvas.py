import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from app.model import Node


class CanvasView:
    def __init__(self, ax: Axes, area, nodes):
        self.ax = ax
        self.area = area
        self.nodes = nodes

        self._press = None

        # ===== initial view =====
        self.ax.set_xlim(0, area.width)
        self.ax.set_ylim(0, area.height)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True)

        # save default camera
        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()

        # ===== interaction =====
        canvas = ax.figure.canvas
        canvas.mpl_connect("scroll_event", self.on_scroll)
        canvas.mpl_connect("button_press_event", self.on_press)
        canvas.mpl_connect("button_release_event", self.on_release)
        canvas.mpl_connect("motion_notify_event", self.on_motion)

    # =====================================================
    # Interaction
    # =====================================================

    def on_scroll(self, event):
        if event.xdata is None or event.ydata is None:
            return

        scale = 0.9 if event.button == "up" else 1.1
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        cx, cy = event.xdata, event.ydata

        self.ax.set_xlim(
            cx + (xlim[0] - cx) * scale,
            cx + (xlim[1] - cx) * scale,
        )
        self.ax.set_ylim(
            cy + (ylim[0] - cy) * scale,
            cy + (ylim[1] - cy) * scale,
        )

        self.ax.figure.canvas.draw_idle()

    def on_press(self, event):
        if event.key == "h" and event.xdata is not None:
            self._press = (event.xdata, event.ydata)

    def on_motion(self, event):
        if self._press is None or event.xdata is None:
            return

        dx = self._press[0] - event.xdata
        dy = self._press[1] - event.ydata

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)

        self._press = (event.xdata, event.ydata)
        self.ax.figure.canvas.draw_idle()

    def on_release(self, event):
        self._press = None

    # =====================================================
    # Camera control
    # =====================================================

    def reset_view(self):
        """Reset camera to initial simulation area"""
        self.ax.set_xlim(self.default_xlim)
        self.ax.set_ylim(self.default_ylim)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.figure.canvas.draw_idle()

    # =====================================================
    # Drawing
    # =====================================================

    def redraw(self, highlight_route=None, send_events=[]):
        # 🔒 save camera BEFORE clearing
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.clear()
        self.ax.grid(True)

        # ===== draw nodes =====
        for node in self.nodes.values():
            if node.pos is None:
                continue

            x, y = node.pos
            c = tuple(v / 255 for v in node.color)

            self.ax.scatter(x, y, s=60, c=[c], zorder=3)
            self.ax.text(x + 5, y + 5, node.nid, fontsize=9)

            # ----- buffer bar -----
            if node.buffer_size > 0:
                ratio = len(node.buffer) / node.buffer_size
                self.ax.bar(
                    x + 12,
                    ratio * 100,
                    width=20,
                    bottom=y - 15,
                    color="gray",
                    zorder=2,
                )

            # ----- ranges (only ferry) -----
            if node.type == "ferry":
                for r in node.ranges:
                    self.ax.add_patch(
                        patches.Circle(
                            (x, y),
                            r,
                            fill=False,
                            linestyle="--",
                            alpha=0.5,
                            zorder=1,
                        )
                    )

        # ===== route highlight =====
        if highlight_route:
            pts = [
                self.nodes[n].pos
                for n in highlight_route
                if n in self.nodes and self.nodes[n].pos
            ]
            if len(pts) >= 2:
                xs, ys = zip(*pts)
                self.ax.plot(xs, ys, "r--", lw=2, zorder=4)

        # ===== send events =====
        for evnt in send_events:
            src = self.nodes[evnt["source"]]
            dst = self.nodes[evnt["dest"]]
            x1, y1 = src.pos
            x2, y2 = dst.pos
            meta = evnt.get("meta", "")

            self.ax.annotate(
                "",
                xy=dst.pos,
                xytext=src.pos,
                arrowprops=dict(arrowstyle="->", lw=1, color="blue"),
                zorder=5,
            )
            # metadata text (middle of arrow)
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            self.ax.text(
                mx,
                my,
                meta,
                color="green",
                fontsize=9,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    fc="white",
                    ec="green",
                    alpha=0.7,
                ),
                zorder=6,
            )

        # 🔓 restore camera AFTER redraw
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_aspect("equal", adjustable="box")

        self.ax.figure.canvas.draw_idle()
