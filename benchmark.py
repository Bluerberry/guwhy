
from typing import Any, Callable
import statistics
import time
import sys

from guwhy.layout import Box
from guwhy.canvas import Canvas

# ─────────────────────────────────────────── timing

def run(fn: Callable[[], Any], n: int) -> list[float]:
	times: list[float] = []
	for _ in range(n):
		t0 = time.perf_counter()
		fn()
		times.append(time.perf_counter() - t0)

	return times

def summarise(times: list[float]) -> tuple[float, float, float]:
	scale = 1_000_000
	return (
		statistics.mean(times) * scale,
		min(times) * scale,
		max(times) * scale,
	)

# ─────────────────────────────────────────── scene builders

def build_sidebar_cards(W: int = 120, H: int = 60) -> tuple[Box, int]:
	root = Box(
		size=f'{W}px {H}px',
		axis='horizontal',
		border='double',
		place_children_along='start',
		place_children_across='start',
	)

	sidebar = Box(size='20px grow', border='single')
	sidebar.setParent(root)
	for _ in range(8):
		Box(size='fit', border='single').setParent(sidebar)

	main = Box(size='grow grow', border='single')
	main.setParent(root)
	for _ in range(3):
		row = Box(size='grow fit', axis='horizontal', border='single')
		row.setParent(main)
		for _ in range(4):
			card = Box(
				size='grow fit',
				border='single',
				place_children_along='center',
				place_children_across='center',
			)

			card.setParent(row)
			Box(size='50%', border='single').setParent(card)

	return root, 1 + len(root.descendants)

def build_centered_dialog(W: int = 80, H: int = 24) -> tuple[Box, int]:
	root = Box(
		size=f'{W}px {H}px',
		place_children_along='center',
		place_children_across='center',
	)

	dialog = Box(
		size='60px 16px',
		border='double',
		axis='vertical',
		place_children_along='start',
		place_children_across='start',
		padding='1px',
	)

	dialog.setParent(root)

	for _ in range(5):
		row = Box(size='grow fit', axis='horizontal', border='single')
		row.setParent(dialog)
		for _ in range(3):
			Box(size='grow fit', border='single').setParent(row)

	return root, 1 + len(root.descendants)

def build_overflow_relative(W: int = 60, H: int = 30) -> tuple[Box, int]:
	root = Box(
		size=f'{W}px {H}px',
		border='double',
		place_children_along='center',
		place_children_across='center',
	)

	a = Box(size='50%', border='single')
	a.setParent(root)

	b = Box(
		size='4sq',
		positioning='relative',
		origin='100% 0px',
		overflow='show',
	)

	b.setParent(a)

	c = Box(
		size='2sq',
		positioning='relative',
		origin_y='50%',
		translate='-50%',
		border='single',
	)

	c.setParent(b)

	return root, 1 + len(root.descendants)

def build_grow_flood(W: int = 100, H: int = 40) -> tuple[Box, int]:
	root = Box(
		size=f'{W}px {H}px',
		axis='horizontal',
		border='single',
	)

	for _ in range(20):
		col = Box(size='grow grow', axis='vertical', border='single')
		col.setParent(root)
		for _ in range(10):
			Box(size='grow grow', border='single').setParent(col)

	return root, 1 + len(root.descendants)

# ─────────────────────────────────────────── table

_COL = [36, 12, 12, 12]

def _row(*cells: str):
	print('  ' + '  '.join(
		f'{c:<{w}}' if i == 0 else f'{c:>{w}}'
		for i, (c, w) in enumerate(zip(cells, _COL))
	))

def _divider():
	print('  ' + '  '.join('─' * w for w in _COL))

def header():
	_row('scenario / phase', 'mean (µs)', 'best (µs)', 'worst (µs)')
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

	print(f'\n  {label}  ({node_count} nodes)')
	for phase, times in (
		('  compute()',  compute_times),
		('  paint()',    paint_times),
		('  compress()', compress_times),
		('  total',      total_times),
	):
		m, b, w = summarise(times)
		_row(phase, f'{m:.1f}', f'{b:.1f}', f'{w:.1f}')

# ─────────────────────────────────────────── main

def main():
	n = 1000
	print(f'\nguwhy benchmark  •  n={n}  •  Python {sys.version.split()[0]}\n')
	header()

	scenes = [
		('sidebar + card grid',       build_sidebar_cards),
		('centered dialog',           build_centered_dialog),
		('overflow + relative',       build_overflow_relative),
		('grow flood (20x10 cells)',  build_grow_flood),
	]

	for label, builder in scenes:
		root, count = builder()
		bench(label, root, count, n)

	print()

if __name__ == '__main__':
	main()
