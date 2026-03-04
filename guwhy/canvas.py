
# External libraries
from typing import TYPE_CHECKING, cast

# Internal libraries
if TYPE_CHECKING:
	from .layout import Node

# -----------------------------------> Canvas

class Canvas:
	def __init__(self, width: int, height: int):
		self._size = width * height
		self._height = height
		self._width = width

		self._layers: list[list[tuple[Node | None, str | None]]] = [
			[(None, None) for _ in range(self._size)]
		]

	def _ensureLayerExists(self, z: int):
		if (new := z + 1 - len(self._layers)) > 0:
			self._layers.extend([
				[(None, None) for _ in range(self._size)]
				for _ in range(new)
			])

	def drawChar(self, node: Node | None, char: str, x: int, y: int, z: int):
		self._ensureLayerExists(z)
		self._layers[z][x + y * self._width] = node, char

	def drawRect(self, node: Node | None, char: str, x1: int, x2: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._layers[z][start:end] = [(node, char) for _ in range(x2 - x1)]

	def drawHLine(self, node: Node | None, char: str, x1: int, x2: int, y: int, z: int):
		self._ensureLayerExists(z)

		x2 += 1 # Because end is non-inclusive
		start = x1 + y * self._width
		end = x2 + y * self._width
		self._layers[z][start:end] = [(node, char) for _ in range(x2 - x1)]

	def drawVLine(self, node: Node | None, char: str, x: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		y2 += 1 # Because end is non-inclusive
		start = x + y1 * self._width
		end = x + y2 * self._width
		self._layers[z][start:end:self._width] = [(node, char) for _ in range(y2 - y1)]

	def compress(self):
		compressed: list[tuple[Node | None, str]] = []
		reverse = reversed(self._layers)

		for n in range(self._size):
			node, char = None, ''
			for layer in reverse:
				if layer[n][0] is not None:
					node = cast(Node, layer[n][0])
					break

			for layer in reverse:
				if layer[n][1] is not None:
					char = cast(str, layer[n][1])
					break
			
			compressed.append((node, char))
