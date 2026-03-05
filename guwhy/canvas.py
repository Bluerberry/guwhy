
# External libraries
from typing import cast

# Internal libraries
from .layout import *

# -----------------------------------> Canvas

class Canvas:
	def __init__(self, width: int, height: int):
		self._size = width * height
		self._height = height
		self._width = width

		self._pixel_layers: list[list[str | None]] = [
			[None for _ in range(self._size)]
		]

		self._node_layers: list[list[Node | None]] = [
			[None for _ in range(self._size)]
		]

	def _ensureLayerExists(self, z: int):
		if (new := z + 1 - len(self._pixel_layers)) > 0:

			self._pixel_layers.extend([
				[None for _ in range(self._size)]
				for _ in range(new)
			])

			self._node_layers.extend([
				[None for _ in range(self._size)]
				for _ in range(new)
			])

	def drawChar(self, char: str, x: int, y: int, z: int):
		self._ensureLayerExists(z)
		self._pixel_layers[z][x + y * self._width] = char

	def drawRect(self, char: str, x1: int, x2: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._pixel_layers[z][start:end] = [char for _ in range(x2 - x1)]

	def drawHLine(self, char: str, x1: int, x2: int, y: int, z: int):
		self._ensureLayerExists(z)

		x2 += 1 # Because end is non-inclusive
		start = x1 + y * self._width
		end = x2 + y * self._width
		self._pixel_layers[z][start:end] = [char for _ in range(x2 - x1)]

	def drawVLine(self, char: str, x: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		y2 += 1 # Because end is non-inclusive
		start = x + y1 * self._width
		end = x + y2 * self._width
		self._pixel_layers[z][start:end:self._width] = [char for _ in range(y2 - y1)]

	def fillNodes(self, node: Node, x1: int, x2: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)

		# Because end is non-inclusive
		x2 += 1
		y2 += 1

		for y in range(y1, y2):
			start = x1 + y * self._width
			end = x2 + y * self._width
			self._node_layers[z][start:end] = [node for _ in range(x2 - x1)]

	def compress(self):
		compressed_pixels: list[str] = []
		compressed_nodes: list[Node | None] = []

		for n in range(self._size):
			for layer in reversed(self._pixel_layers):
				if layer[n] is not None:
					compressed_pixels.append(
						cast(str, layer[n])
					)

					break

			for layer in reversed(self._node_layers):
				if layer[n] is not None:
					compressed_nodes.append(
						cast(Node, layer[n])
					)
					
					break
			
		return compressed_pixels, compressed_nodes
