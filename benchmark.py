
import cProfile
import pstats
import io
import math

from guwhy.layout import Box

# ─────────────────────── scene ───────────────────────

def build():
    W, H = 500, 250

    target = 100
    panels = max(2, round((target / 30) ** 0.5))
    rows_per_panel = max(2, round(math.sqrt(target / (panels * 3))))
    cells_per_row = max(2, round(target / (panels * rows_per_panel * 3)))

    root = Box(
        size=f"{W}px {H}px", 
        axis="horizontal", 
        border="double",
        place_children="start"
    )

    for p in range(panels):
        panel = Box(
            parent=root,
            size="grow" if p % 2 == 0 else "25% grow",
            axis="vertical", 
            border="single",
            place_children="start center", 
            padding="1px"
        )

        for r in range(rows_per_panel):
            row = Box(
                parent=panel,
                size="grow fit" if r % 3 != 2 else "grow grow",
                axis="horizontal" if r % 2 == 0 else "vertical",
                border="single" if r % 2 == 0 else "none",
                place_children_along="center" if r % 2 == 0 else "start",
                place_children_across="center",
                margin="0px 1px"
            )

            for c in range(cells_per_row):
                sz = ["grow grow", "50% fit", "fit fit", "grow 3sq"][c % 4]
                Box(
                    parent=row,
                    z_index="2", 
                    size=sz, 
                    border="single",
                    place_children="center",
                    padding="1px",
                    children = [
                        Box(
                            size="75% 75%", 
                            border="single" if c % 2 == 0 else "none",
                            place_children="center"
                        ),
                        Box(
                            z_index='3', 
                            size="2sq", 
                            positioning="relative", 
                            origin="100% 0px",
                            translate="-50% -50%", 
                            border="single", 
                            overflow="show"
                        )
                    ]
                )

    return root

# ─────────────────────── profile ───────────────────────

root = build()
root.compute()
selection = root.select('box box:odd + *')
print(len(selection.selection))

pr = cProfile.Profile()

for _ in range(1000):
    pr.enable()
    root.select('box box:odd + *')
    pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(40)
print(s.getvalue())