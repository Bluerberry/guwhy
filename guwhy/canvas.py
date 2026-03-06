
# External libraries
from typing import TYPE_CHECKING, Any

# Internal libraries
if TYPE_CHECKING:
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

	def compress(self):
		layers = [layer for _, layer in sorted(
			self._layers.items(),
			key=lambda item: item[0],
			reverse=True
		)]

		pixels = layers[0]['pixels'].copy()
		nodes = layers[0]['nodes'].copy()

		for layer in layers[1:]:
			lp = layer['pixels']
			ln = layer['nodes']

			for i in range(self._size):
				if pixels[i] is None:
					pixels[i] = lp[i]
				if nodes[i] is None:
					nodes[i]  = ln[i]

		pixels = [' ' if p is None else p for p in pixels]

		return pixels, nodes
