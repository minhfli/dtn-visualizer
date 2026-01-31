class EventExecutor:
    def __init__(self, nodes, canvas):
        self.nodes = nodes
        self.canvas = canvas

    def apply_events(self, events):
        for ev in events:
            self.apply(ev)

    def apply(self, ev):
        d = ev.data
        t = ev.type

        if t == "pos":
            self.nodes[d["node"]].pos = (float(d["x"]), float(d["y"]))

        elif t == "route":
            self.nodes[d["node"]].route = d["tour"]

        elif t == "buffer":
            n = self.nodes[d["node"]]
            n.buffer = [x for x in d["list"] if x != ""]

        elif t == "send":
            self.draw_send(d)

    def draw_send(self, d):
        src = self.nodes[d["source"]]
        dst = self.nodes[d["dest"]]

        self.canvas.ax.annotate(
            d.get("meta", ""),
            xy=dst.pos,
            xytext=src.pos,
            arrowprops=dict(arrowstyle="->", lw=1, color="blue"),
            zorder=5,
        )
