import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse
import random
import os

# ===============================
# Configuration defaults
# ===============================
DEFAULT_N = 30
DEFAULT_K = 320.0
DEFAULT_SEED = 2004
DEFAULT_OUTPUT = "points_relaxed.txt"
DEFAULT_IMAGE = "flood2.png"

X_MIN = 100
X_MAX = 3900
Y_MIN = 100
Y_MAX = 3900


# ===============================
# Generate initial points
# ===============================
def generate_points(n, k, seed):
    random.seed(seed)
    points = []

    while len(points) < n:
        x = random.uniform(X_MIN, X_MAX)
        y = random.uniform(Y_MIN, Y_MAX)

        valid = True
        for px, py in points:
            if np.hypot(x - px, y - py) < k:
                valid = False
                break

        if valid:
            points.append([x, y])

    return np.array(points)


# ===============================
# Force Relaxation
# ===============================
def relax(points, k, iterations=50, step=0.1):
    n = len(points)

    for _ in range(iterations):
        forces = np.zeros_like(points)

        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i] - points[j]
                dist = np.linalg.norm(dx)

                if dist < 1e-5:
                    continue

                if dist < k:
                    # repulsive force
                    direction = dx / dist
                    magnitude = (k - dist) / k
                    force = direction * magnitude

                    forces[i] += force
                    forces[j] -= force

        points += step * forces

        # Clamp boundary
        points[:, 0] = np.clip(points[:, 0], X_MIN, X_MAX)
        points[:, 1] = np.clip(points[:, 1], Y_MIN, Y_MAX)

    return points


# ===============================
# Interactive Editor
# ===============================
class DTNEditor:
    def __init__(self, points, k, image_path, output):
        self.points = points
        self.k = k
        self.output = output
        self.selected = None

        self.fig, self.ax = plt.subplots(figsize=(8, 8))

        if image_path and os.path.exists(image_path):
            img = mpimg.imread(image_path)
            self.ax.imshow(img, extent=(0, 4000, 0, 4000))

        self.scatter = self.ax.scatter(points[:, 0], points[:, 1])
        self.ax.set_xlim(0, 4000)
        self.ax.set_ylim(0, 4000)
        self.ax.set_aspect("equal")

        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

    def redraw(self):
        self.scatter.set_offsets(self.points)
        self.fig.canvas.draw_idle()

    def find_nearest(self, x, y):
        dists = np.hypot(self.points[:, 0] - x, self.points[:, 1] - y)
        idx = np.argmin(dists)
        if dists[idx] < 100:
            return idx
        return None

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        self.selected = self.find_nearest(event.xdata, event.ydata)

    def on_motion(self, event):
        if self.selected is None or event.inaxes != self.ax:
            return

        self.points[self.selected] = [event.xdata, event.ydata]
        self.points = relax(self.points, self.k, iterations=10)
        self.redraw()

    def on_release(self, event):
        self.selected = None

    def on_key(self, event):
        if event.key == "s":
            self.save()
        elif event.key == "r":
            self.points = relax(self.points, self.k, iterations=100)
            self.redraw()
        elif event.key == "q":
            plt.close(self.fig)

    def save(self):
        with open(self.output, "w") as f:
            f.write("id,x,y\n")
            for i, (x, y) in enumerate(self.points):
                f.write(f"{i},{x:.2f},{y:.2f}\n")
        print(f"Saved to {self.output}")


# ===============================
# Main
# ===============================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    parser.add_argument("--k", type=float, default=DEFAULT_K)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--image", type=str, default=DEFAULT_IMAGE)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT)

    args = parser.parse_args()

    points = generate_points(args.n, args.k, args.seed)

    editor = DTNEditor(points, args.k, args.image, args.output)
    plt.title("Drag points | S=save | R=relax | Q=quit")
    plt.show()


if __name__ == "__main__":
    main()
