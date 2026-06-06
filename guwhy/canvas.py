
# External libraries
from typing import Generator

# Internal libraries
from .layout import *
from .literals import *

# ─────────────────────────────────── Utility ───────────────────────────────────

def _paintTraversal(node: Node) -> Generator[Node, None, None]:
	if node.visibility.value != NodeVisibility.SHOW:
		return
	
	# Collect nodes
	index = 0
	nodes = [node]

	while index < len(nodes):
		parent = nodes[index]
		index += 1

		if isinstance(parent, Parent):
			nodes.extend([
				child for child in parent.children
				if child.visibility.value == NodeVisibility.SHOW
			])

	# Sort by z-index
	nodes.sort(key=lambda node: node.z_index.computed)
	yield from nodes

# ─────────────────────────────────── Canvas ───────────────────────────────────

class Canvas:
	_size: int
	_width: int
	_height: int
	_pixel_buffer: list[str]
	_callback_buffer: list[Node | None]

	def __init__(self, width: int, height: int, root: Node):
		self._size = width * height
		self._height = height
		self._width = width

		self._pixel_buffer = [' '] * self._size
		self._callback_buffer = [None] * self._size

		for node in _paintTraversal(root):
			node.paint(self)
	
	def setChar(self, char: str, x: int, y: int):
		self._pixel_buffer[x + y * self._width] = char

	def setRect(self, char: str, x1: int, x2: int, y1: int, y2: int):

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		# Full width case
		if x2 - x1 == self._width:
			start = x1 + y1 * self._width
			end = x2 + y2 * self._width
			self._pixel_buffer[start:end] = [char] * ((x2 - x1) * (y2 - y1))
			return

		# Regular case
		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._pixel_buffer[start:end] = [char] * (x2 - x1)

	def setHLine(self, char: str, x1: int, x2: int, y: int):

		# Because end is non-inclusive
		x2 += 1

		start = x1 + y * self._width
		end = x2 + y * self._width
		self._pixel_buffer[start:end] = [char] * (x2 - x1)

	def setVLine(self, char: str, x: int, y1: int, y2: int):

		# Because end is non-inclusive
		y2 += 1

		start = x + y1 * self._width
		end = x + y2 * self._width
		self._pixel_buffer[start:end:self._width] = [char] * (y2 - y1)

	def setCallback(self, node: Node, x1: int, x2: int, y1: int, y2: int):

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		# Full width case
		if x2 - x1 == self._width:
			start = x1 + y1 * self._width
			end = x2 + y2 * self._width
			self._callback_buffer[start:end] = [node] * ((x2 - x1) * (y2 - y1))
			return

		# Regular case
		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._callback_buffer[start:end] = [node] * (x2 - x1)

