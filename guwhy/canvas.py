
class Canvas:
	def __init__(self, width: int, height: int):
		self.width = width
		self.height = height
		self.layers = 1
		self.pixels = [
			[None] * (self.width * self.height)
		]

	def __repr__(self):
		compressed = self.compress()
		result = ''

		for y in range(self.height):
			result += ''.join(compressed[y*self.width:(y+1)*self.width]) + '\n'
		return result

	def _ensureLayerExists(self, z: int):
		if z + 1 > self.layers:
			new = z + 1 - self.layers
			self.pixels.extend([[None] * (self.width * self.height) for _ in range(new)])
			self.layers = z + 1

	def drawHLine(self, char: str, x1: int, x2: int, y: int, z: int):
		self._ensureLayerExists(z)
		x2 += 1 # bc end is non-inclusive
		width = self.width
		start = x1 + y * width
		end = x2 + y * width
		self.pixels[z][start:end] = [char] * (x2 - x1)

	def drawVLine(self, char: str, x: int, y1: int, y2: int, z: int):
		self._ensureLayerExists(z)
		y2 += 1 # bc end is non-inclusive
		width = self.width
		start = x + y1 * width
		end = x + y2 * width
		self.pixels[z][start:end:width] = [char] * (y2 - y1)

	def drawChar(self, char: str, x: int, y: int, z: int):
		self._ensureLayerExists(z)
		self.pixels[z][x + y * self.width] = char

	def drawText(self, text: str, x: int, y: int, z: int):
		self._ensureLayerExists(z)
		start = x + y * self.width
		end = start + len(text)
		self.pixels[z][start:end] = list(text)

	def compress(self):
		pixels = self.pixels
		size = self.width * self.height
		compressed = [' '] * size
		
		for n in range(size):
			for layer in reversed(pixels):
				if layer[n] is not None:
					compressed[n] = layer[n]
					break

		return compressed
