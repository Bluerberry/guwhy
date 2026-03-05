"""
benchmark.py — guwhy layout benchmark

Usage:
    python benchmark.py            # 200 iterations
    python benchmark.py --quick    # 50 iterations
"""

import argparse
import time
import statistics
import sys

from guwhy.layout import Box
from guwhy.canvas import Canvas

# ─────────────────────────────────────────── timing

def run(fn, n: int) -> list[float]:
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return times

def summarise(times: list[float]) -> tuple[float, float, float]:
    """Returns (mean, best, worst) in microseconds."""
    scale = 1_000_000
    return (
        statistics.mean(times) * scale,
        min(times) * scale,
        max(times) * scale,
    )

# ─────────────────────────────────────────── scene builders

def build_sidebar_cards(W: int = 120, H: int = 60) -> tuple[Box, int]:
    """Sidebar + main area with a grid of nested cards."""
    root = Box(
        size=f"{W}px {H}px",
        axis="horizontal",
        border="double",
        place_children_along="start",
        place_children_across="start",
    )

    sidebar = Box(size="20px grow", border="single")
    sidebar.setParent(root)
    for _ in range(8):
        Box(size="fit", border="single").setParent(sidebar)

    main = Box(size="grow grow", border="single")
    main.setParent(root)
    for _ in range(3):
        row = Box(size="grow fit", axis="horizontal", border="single")
        row.setParent(main)
        for _ in range(4):
            card = Box(
                size="grow fit",
                border="single",
                place_children_along="center",
                place_children_across="center",
            )
            card.setParent(row)
            Box(size="50%", border="single").setParent(card)

    return root, 1 + len(root.descendants)

def build_centered_dialog(W: int = 80, H: int = 24) -> tuple[Box, int]:
    """Fullscreen overlay with a centered dialog containing stacked rows."""
    root = Box(
        size=f"{W}px {H}px",
        place_children_along="center",
        place_children_across="center",
    )

    dialog = Box(
        size="60px 16px",
        border="double",
        axis="vertical",
        place_children_along="start",
        place_children_across="start",
        padding="1px",
    )
    dialog.setParent(root)

    for _ in range(5):
        row = Box(size="grow fit", axis="horizontal", border="single")
        row.setParent(dialog)
        for _ in range(3):
            Box(size="grow fit", border="single").setParent(row)

    return root, 1 + len(root.descendants)

def build_overflow_relative(W: int = 60, H: int = 30) -> tuple[Box, int]:
    """Layout exercising relative positioning, overflow, and translate."""
    root = Box(
        size=f"{W}px {H}px",
        border="double",
        place_children_along="center",
        place_children_across="center",
    )

    a = Box(size="50%", border="single")
    a.setParent(root)

    b = Box(
        size="4sq",
        positioning="relative",
        origin="100% 0px",
        overflow="show",
    )
    b.setParent(a)

    c = Box(
        size="2sq",
        positioning="relative",
        origin_y="50%",
        translate="-50%",
        border="single",
    )
    c.setParent(b)

    return root, 1 + len(root.descendants)

def build_grow_flood(W: int = 100, H: int = 40) -> tuple[Box, int]:
    """Many siblings competing for grow space — stresses _floodChildren."""
    root = Box(
        size=f"{W}px {H}px",
        axis="horizontal",
        border="single",
    )

    for _ in range(20):
        col = Box(size="grow grow", axis="vertical", border="single")
        col.setParent(root)
        for _ in range(10):
            Box(size="grow grow", border="single").setParent(col)

    return root, 1 + len(root.descendants)

def build_stress(target_nodes: int, W: int = 200, H: int = 80) -> tuple[Box, int]:
    """
    Dense layout that exercises as many layout features simultaneously as possible:
      - grow + fit + percentage sizes all competing together
      - relative origins and translations (percentage and pixel)
      - centered content at every level (along + across)
      - overflow:show on some branches
      - double + single borders mixed
      - padding and margin throughout
      - both horizontal and vertical axes alternating per level

    The tree is built as a 3-level hierarchy of panels → rows → cells,
    scaled so the total node count lands near `target_nodes`.
    """
    # panels × rows_per_panel × cells_per_row  ≈  target_nodes
    # Each cell spawns 2 extra children (an inner + a floating badge),
    # so each cell contributes 3 nodes.  The panels and rows add overhead.
    # Solve approximately: panels * rows * cells * 3 ≈ target_nodes
    import math
    panels         = max(2, round((target_nodes / 30) ** (1/2)))
    rows_per_panel = max(2, round(math.sqrt(target_nodes / (panels * 3))))
    cells_per_row  = max(2, round(target_nodes / (panels * rows_per_panel * 3)))

    root = Box(
        size=f"{W}px {H}px",
        axis="horizontal",
        border="double",
        place_children_along="start",
        place_children_across="start",
    )

    for p in range(panels):
        # Panels alternate grow / percentage width
        panel_size = "grow grow" if p % 2 == 0 else "25% grow"
        panel = Box(
            size=panel_size,
            axis="vertical",
            border="single",
            place_children_along="start",
            place_children_across="center",
            padding="1px",
        )
        panel.setParent(root)

        for r in range(rows_per_panel):
            # Rows alternate fit / grow height, and flip axis
            row_axis   = "horizontal" if r % 2 == 0 else "vertical"
            row_size   = "grow fit"   if r % 3 != 2  else "grow grow"
            row_place  = ("center"    if r % 2 == 0  else "start")
            row = Box(
                size=row_size,
                axis=row_axis,
                border="single" if r % 2 == 0 else "none",
                place_children_along=row_place,
                place_children_across="center",
                margin="0px 1px",
            )
            row.setParent(panel)

            for c in range(cells_per_row):
                # Cells: mix of grow, fit, percentage, and fixed sizes
                if c % 4 == 0:
                    cell_size = "grow grow"
                elif c % 4 == 1:
                    cell_size = "50% fit"
                elif c % 4 == 2:
                    cell_size = "fit fit"
                else:
                    cell_size = "grow 3sq"

                cell = Box(
                    size=cell_size,
                    border="single",
                    place_children_along="center",
                    place_children_across="center",
                    padding="1px",
                )
                cell.setParent(row)

                # Inner content: percentage-sized, centered
                inner = Box(
                    size="75% 75%",
                    border="single" if c % 2 == 0 else "none",
                    place_children_along="center",
                    place_children_across="center",
                )
                inner.setParent(cell)

                # Floating badge: relative positioning + percentage origin + translate
                badge = Box(
                    size="2sq",
                    positioning="relative",
                    origin="100% 0px",
                    translate="-50% -50%",
                    border="single",
                    overflow="show",
                )
                badge.setParent(cell)

    return root, 1 + len(root.descendants)

# ─────────────────────────────────────────── table

_COL = [36, 12, 12, 12]

def _row(*cells: str):
    print("  " + "  ".join(
        f"{c:<{w}}" if i == 0 else f"{c:>{w}}"
        for i, (c, w) in enumerate(zip(cells, _COL))
    ))

def _divider():
    print("  " + "  ".join("─" * w for w in _COL))

def header():
    _row("scenario / phase", "mean (µs)", "best (µs)", "worst (µs)")
    _divider()

def bench(label: str, root: Box, node_count: int, n: int):
    W, H = 200, 100

    compute_times  = run(lambda: root.compute(), n)

    canvas = Canvas(W, H)
    root.compute()
    paint_times    = run(lambda: root.paint(canvas), n)

    canvas = Canvas(W, H)
    root.paint(canvas)
    compress_times = run(lambda: canvas.compress(), n)

    total_times = [c + p + x
                   for c, p, x in zip(compute_times, paint_times, compress_times)]

    print(f"\n  {label}  ({node_count} nodes)")
    _divider()
    for phase, times in (
        ("  compute()",  compute_times),
        ("  paint()",    paint_times),
        ("  compress()", compress_times),
        ("  total",      total_times),
    ):
        m, b, w = summarise(times)
        _row(phase, f"{m:.1f}", f"{b:.1f}", f"{w:.1f}")

# ─────────────────────────────────────────── main

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    n = 50 if args.quick else 200
    print(f"\nguwhy benchmark  •  n={n}  •  Python {sys.version.split()[0]}\n")
    header()

    scenes = [
        ("sidebar + card grid",       build_sidebar_cards),
        ("centered dialog",           build_centered_dialog),
        ("overflow + relative",       build_overflow_relative),
        ("grow flood (20x10 cells)",  build_grow_flood),
    ]

    for label, builder in scenes:
        root, count = builder()
        bench(label, root, count, n)

    # Stress test — single ~500 node layout
    root, actual = build_stress(500)
    bench("stress (grow+shrink+%+relative+centered)", root, actual, n)

    print()

if __name__ == "__main__":
    main()