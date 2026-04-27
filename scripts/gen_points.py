from math import dist

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import argparse
import random
import os

# ===============================
# Configuration defaults
# ===============================
DEFAULT_N = 45
DEFAULT_K = 320.0
DEFAULT_SEED = 133142314
DEFAULT_OUTPUT = "points_relaxed.txt"
DEFAULT_IMAGE = "flood2.png"

X_MIN = 0
X_MAX = 4000
Y_MIN = 0
Y_MAX = 4000


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


def plot(points):
    plt.figure(figsize=(8, 8))
    plt.scatter(points[:, 0], points[:, 1], c="blue", marker="o")
    plt.xlim(X_MIN, X_MAX)
    plt.show()


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

    max_max_distance = 0
    max_average_distance = 0

    for i in range(1000):
        seed = random.random()
        points = generate_points(args.n, args.k, seed)

        max_distance = 0
        average_distance = 0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = np.hypot(
                    points[i][0] - points[j][0], points[i][1] - points[j][1]
                )
                max_distance = max(max_distance, distance)
                average_distance += distance

        average_distance /= len(points) * (len(points) - 1) / 2

        max_max_distance = max(max_max_distance, max_distance)
        max_average_distance = max(max_average_distance, average_distance)

    # plot final generated points
    plot(points)
    print("Average distance:", max_average_distance)
    print("Max distance:", max_max_distance)


if __name__ == "__main__":
    main()
