
# External libraries
from typing import Any

# Internal libraries
from .layout import Node

# ─────────────────────────────────── Canvas ───────────────────────────────────

class Canvas:
	def __init__(self, width: int, height: int):
		self._size = width * height
		self._height = height
		self._width = width

		self._layers: dict[int, dict[str, list[Any | None]]] = {
			0: {
				'pixels': [None] * self._size,
				'nodes': [None] * self._size
			}
		}

	def _ensureLayerExists(self, z: int):
		if z not in self._layers:
			self._layers[z] = {
				'pixels': [None] * self._size,
				'nodes': [None] * self._size
			}

	def drawChar(self, char: str, x: int, y: int, z: int):
		self._ensureLayerExists(z)
		self._layers[z]['pixels'][x + y * self._width] = char

	def drawRect(self, char: str, x1: int, x2: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._layers[z]['pixels'][start:end] = [char] * (x2 - x1)

	def drawHLine(self, char: str, x1: int, x2: int, y: int, z: int):
		self._ensureLayerExists(z)

		x2 += 1 # Because end is non-inclusive
		start = x1 + y * self._width
		end = x2 + y * self._width
		self._layers[z]['pixels'][start:end] = [char] * (x2 - x1)

	def drawVLine(self, char: str, x: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		y2 += 1 # Because end is non-inclusive
		start = x + y1 * self._width
		end = x + y2 * self._width
		self._layers[z]['pixels'][start:end:self._width] = [char] * (y2 - y1)

	def fillNodes(self, node: Node, x1: int, x2: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._layers[z]['nodes'][start:end] = [node] * (x2 - x1)

		return pixels, nodes