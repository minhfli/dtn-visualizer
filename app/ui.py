import tkinter as tk
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from .canvas import CanvasView
from .executor import EventExecutor


class VisualizerApp:

    def __init__(self, root, area, nodes, timeline, step_delay=400):
        self.root = root
        self.area = area
        self.nodes = nodes
        self.timeline = timeline
        self.step_delay = step_delay

        self.index = 0
        self.running = False
        self.after_id = None
        self.selected_node = None

        self.root.title("DTN Visualizer")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # ===== Left panel =====
        left = tk.Frame(root, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y)

        self.play_btn = tk.Button(left, text="Play", command=self.toggle)
        print(self.play_btn.cget("font"))
        self.play_btn.pack(fill=tk.X)

        tk.Button(left, text="Reset View", command=self.reset_view).pack(fill=tk.X)
        tk.Button(left, text="Back to Zero", command=self.back_to_zero).pack(fill=tk.X)

        tk.Label(left, text="Timeline").pack()

        self.listbox = tk.Listbox(left)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        for i, tf in enumerate(self.timeline):
            self.listbox.insert(tk.END, f"[{i}] Time={tf.time}")

        self.listbox.bind("<<ListboxSelect>>", self.jump)

        # ===== Center =====
        center = tk.Frame(root)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots()
        self.canvas_view = CanvasView(ax, area, nodes)
        self.executor = EventExecutor(nodes, self.canvas_view)

        self.canvas = FigureCanvasTkAgg(fig, master=center)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ===== Right =====
        right = tk.Frame(root, width=240)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right, text="Nodes").pack()

        self.node_list = tk.Listbox(right)
        self.node_list.pack(fill=tk.BOTH, expand=True)

        for nid in nodes:
            self.node_list.insert(tk.END, nid)

        self.node_list.bind("<<ListboxSelect>>", self.select_node)

        self.info = tk.Label(right, justify=tk.LEFT, anchor="nw")
        self.info.pack(fill=tk.X)

        # Initial draw
        self._apply_first_event()  # always play the first event, which is setting position

    # ======================================================
    # Playback control
    # ======================================================

    def toggle(self):
        if self.running:
            self.pause()
        else:
            self.play()

    def play(self):
        if self.running:
            return

        self.running = True
        self.play_btn.config(text="⏸ Pause")
        self._tick()

    def pause(self):
        self.running = False
        self.play_btn.config(text="▶ Play")

        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def _tick(self, play_next=True):
        if not self.running:
            return

        if self.index >= len(self.timeline):
            self.pause()
            return

        tf = self.timeline[self.index]
        self.executor.apply_events(tf.events)
        self.render()

        self.index += 1
        if play_next:
            self.after_id = self.root.after(self.step_delay, self._tick)

    def _apply_first_event(self):
        tf = self.timeline[0]
        self.executor.apply_events(tf.events)
        self.render()

    def replay_to(self, target_index):
        # reset executor + canvas bằng cách replay event 0
        self.index = 0

        tf0 = self.timeline[0]
        self.executor.apply_events(tf0.events)

        # replay từ 1 → target
        for i in range(1, target_index + 1):
            tf = self.timeline[i]
            self.executor.apply_events(tf.events)

        self.index = target_index
        self.render()

    # ======================================================
    # UI callbacks
    # ======================================================

    def reset_view(self):
        self.canvas_view.reset_view()

    def back_to_zero(self):
        self.replay_to(0)

    def jump(self, _):
        if not self.listbox.curselection():
            return

        self.pause()

        target = self.listbox.curselection()[0]
        self.replay_to(target)

    def select_node(self, _):
        if not self.node_list.curselection():
            return

        self.selected_node = self.node_list.get(self.node_list.curselection())
        self.selected_node = self.selected_node.split()[0]
        self.render()

    def update_node_list(self):
        # giữ selection hiện tại (nếu có)
        selected = None
        if self.node_list.curselection():
            selected = self.node_list.get(self.node_list.curselection())

        self.node_list.delete(0, tk.END)

        for nid, node in self.nodes.items():
            label = f"{nid}  [{len(node.buffer)}/{node.buffer_size}]"
            self.node_list.insert(tk.END, label)

            if selected and label.startswith(selected.split()[0]):
                self.node_list.selection_set(tk.END)

    # ======================================================
    # Rendering
    # ======================================================

    def render(self):
        self.update_node_list()

        route = None
        send_events = []

        if self.selected_node:
            n = self.nodes[self.selected_node]
            route = n.route

            self.info.config(
                text=(
                    f"Node: {n.nid}\n"
                    f"Type: {n.type}\n"
                    f"Buffer: {len(n.buffer)}/{n.buffer_size}\n"
                    f"Route: {n.route}"
                )
            )
        else:
            self.info.config(text="")

        for ev in self.timeline[self.index].events:
            if ev.type == "send":
                send_events.append(ev.data)
                # print(ev.data)

        self.canvas_view.redraw(route, send_events)
        self.canvas.draw_idle()

    # ======================================================
    # Shutdown
    # ======================================================

    def on_close(self):
        print("[INFO] Closing visualizer")

        self.running = False

        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass

        self.root.quit()
        self.root.destroy()
