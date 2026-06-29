import random
import matplotlib.pyplot as plt
from point import Point

N_POINTS = 100
X_RANGE = {"minX": -400, "maxX": 600}
Y_RANGE = {"minY": -200, "maxY": 300}

points = [Point("ORIGIN", 0, 0)]

def load_points():
    """Create and return a list of random points including ORIGIN.
    Returns:
        list[Point]: Points named ORIGIN, P1, P2, ... within configured ranges.
    """
    # Start with the origin so charts always include (0, 0).
    points = [Point("ORIGIN", 0, 0)]
    for i in range(1, N_POINTS):
        # Generate random coordinates inside configured X/Y bounds.
        x = random.randint(X_RANGE["minX"], X_RANGE["maxX"])
        y = random.randint(Y_RANGE["minY"], Y_RANGE["maxY"])
        p = Point(f"P{i}", x, y)
        points.append(p)
    return points

def write_points(points, filename):
    """Write points to a TSV file with Name, X, Y columns.
    Args:
        points: Iterable of Point objects to serialize.
        filename: Output file path.
    """
    # Open the output file in text mode and overwrite existing content.
    f = open(filename, "w", encoding="utf-8", newline="")
    # Write TSV header expected by spreadsheet tools.
    f.write("Name\tX\tY\n")
    for p in points:
        # Write one point per line as: Name TAB X TAB Y.
        f.write(f"{p._name}\t{p._x}\t{p._y}\n")
    # Always close the file handle after writing.
    f.close()

def plot_points(points):
    """Display the given points on a 2D scatter plot.
    Args:
        points: Iterable of Point objects to draw.
    """
    # Build x/y arrays used by matplotlib scatter.
    # use a traditional for loop for building x array
    x_values = []
    for p in points:
        x_values.append(p._x)
    # use a comprehension statement for building y array
    y_values = [p._y for p in points]
    # Configure figure and draw points plus axis helper lines.
    plt.figure(figsize=(10, 6))
    plt.scatter(x_values, y_values, s=10, c="#1f29b4", alpha=0.8)
    plt.axhline(0, color="gray", linewidth=1)
    plt.axvline(0, color="gray", linewidth=1)
    # Render the interactive chart window.
    plt.show()

if __name__ == "__main__":
    points = load_points()
    plot_points(points)
    write_points(points, "points.dat")
