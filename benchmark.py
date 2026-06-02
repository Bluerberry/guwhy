
import cProfile
import pstats
import io
import math

from guwhy.layout import Box
from guwhy.canvas import Canvas

# ─────────────────────── scene ───────────────────────

def build():
    W, H = 500, 250
    target = 100
    panels = max(2, round((target / 30) ** 0.5))
    rows_per_panel = max(2, round(math.sqrt(target / (panels * 3))))
    cells_per_row  = max(2, round(target / (panels * rows_per_panel * 3)))

    root = Box(
        size=f"{W}px {H}px", axis="horizontal", border="double",
        place_children_along="start", place_children_across="start",
    )
    for p in range(panels):
        panel = Box(
            size="grow grow" if p % 2 == 0 else "25% grow",
            axis="vertical", border="single",
            place_children_along="start", place_children_across="center", padding="1px",
        )
        panel.setParent(root)
        for r in range(rows_per_panel):
            row = Box(
                size="grow fit" if r % 3 != 2 else "grow grow",
                axis="horizontal" if r % 2 == 0 else "vertical",
                border="single" if r % 2 == 0 else "none",
                place_children_along="center" if r % 2 == 0 else "start",
                place_children_across="center", margin="0px 1px",
            )
            row.setParent(panel)
            for c in range(cells_per_row):
                sz = ["grow grow", "50% fit", "fit fit", "grow 3sq"][c % 4]
                cell = Box(z_index="2", size=sz, border="single",
                           place_children_along="center", place_children_across="center",
                           padding="1px")
                cell.setParent(row)
                Box(size="75% 75%", border="single" if c % 2 == 0 else "none",
                    place_children_along="center", place_children_across="center").setParent(cell)
                Box(z_index='3', size="2sq", positioning="relative", origin="100% 0px",
                    translate="-50% -50%", border="single", overflow="show").setParent(cell)
    return root

# ─────────────────────── profile ───────────────────────

root = build()
root.compute()

pr = cProfile.Profile()

for _ in range(1000):
    canvas = Canvas(500, 250)
    root.paint(canvas)
    pr.enable()
    canvas.compress()
    pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(40)
print(s.getvalue())