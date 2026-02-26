
from __future__ import annotations

# External
from typing import Generator

# Internal
from .nodes import *
from .selection import *

# maps axis -> primary direction key ('left'/'top')
FIRST_CARDINAL = { 'horizontal': 'left', 'vertical': 'top' }

# maps axis -> secondary direction key ('right'/'bottom')
LAST_CARDINAL = { 'horizontal': 'right', 'vertical': 'bottom' }

# ----------------------------------> Layout

def _preOrderTraversal(node: Node) -> Generator[Node, Any, None]:
	yield node
	if isinstance(node, Box):
		for child in node._children:
			yield from _preOrderTraversal(child)

def _postOrderTraversal(node: Node) -> Generator[Node, Any, None]:
	if isinstance(node, Box):
		for child in node._children:
			yield from _postOrderTraversal(child)
	yield node

class Layout(Box):

	@staticmethod
	def _wrapChar(lines: list[str], width: int) -> list[str]:
		result = []
		for content in lines:
			for n in range(0, len(content), width):
				result.append(content[n:n + width])

		return result

	@staticmethod
	def _wrapWord(lines: list[str], width: int) -> list[str]:
		result = []
		for content in lines:
			words = content.split()
			if not words:
				result.append('')
				continue

			remaining = width
			line = [words.pop(0)]

			for word in words:
				wlen = len(word)
				if wlen + 1 > remaining:
					remaining = width - wlen
					result.append(' '.join(line))
					line = [word]
					continue

				remaining -= wlen + 1
				line.append(word)

			if line:
				result.append(' '.join(line))

		return result

	@staticmethod
	def _wrapLines(wrap: Literal['none', 'char', 'word'], lines: list[str], width: int) -> list[str]:
		match wrap:
			case 'none':
				return lines
			case 'char':
				return Layout._wrapChar(lines, width)
			case 'word':
				return Layout._wrapWord(lines, width)

	@staticmethod
	def _alignText(align: Literal['left', 'center', 'right'], lines: list[str], width: int) -> list[str]:
		match align:
			case 'left':
				lines = [line.ljust(width) for line in lines]
			case 'center':
				lines = [line.center(width) for line in lines]
			case 'right':
				lines = [line.rjust(width) for line in lines]

		return lines

	@staticmethod
	def _clamp(value, min_value, max_value):
		return max(min_value, min(max_value, value))

	def _floodChildren(self, parent: Box, axis: Axis) -> int:

		# Compute delta
		delta = parent._size[axis].computed - parent._axial_padding[axis] - parent._axial_border[axis]

		if (gaps := len(parent._automatic_children) - 1) > 0:
			delta -= parent._child_gap.computed * gaps # This works with auto gaps as they init as 0
		for child in parent._automatic_children:
			delta -= child._size[axis].computed + child._axial_margin[axis]
		if delta == 0:
			return 0

		# Find eligible children
		eligible = [
			child for child in parent._automatic_children
			if child._size[axis].value == 'fit' and delta < 0
			or child._size[axis].value == 'grow'
		]

		if not eligible:
			return delta

		eligible.sort(
			key=lambda node: node._size[axis].computed,
			reverse=delta < 0
		)

		# Discrete flood
		sign = 1 if delta > 0 else -1
		while delta != 0:
			reference = None
			for child in eligible:
				child_size = child._size[axis]
				if sign + child_size.computed > child._max_size[axis].computed:
					continue
				if sign + child_size.computed < child._min_size[axis].computed:
					continue

				if reference is None:
					reference = sign * child_size.computed
				elif sign * child_size.computed > reference:
					break

				delta -= sign
				child_size.computed += sign
				if delta == 0:
					break

			if reference is None:
				break

		return delta

	def _clampChildren(self, parent: Box, axis: Axis):
		parent_internal = parent._size[axis].computed - parent._axial_padding[axis] - parent._axial_border[axis]
		for child in parent._automatic_children:
			child_size = child._size[axis]
			child_margin = child._axial_margin[axis]
			if child_size.value == 'grow' or child_size.value == 'fit' and child_size.computed + child_margin > parent_internal:
				child_size.computed = Layout._clamp(
					parent_internal - child_margin,
					child._min_size[axis].computed,
					child._max_size[axis].computed
				)

	def _filterChildren(self, parent: Box):
		parent._automatic_children = []
		parent._manual_children = []

		for child in parent._children:
			if child._positioning.value == 'auto':
				parent._automatic_children.append(child)
			else:
				parent._manual_children.append(child)

	def _computeStatic(self, node: Node, axis: Axis):
		node._origin[axis] = 0
		node._position[FIRST_CARDINAL[axis]].computeStatic(axis)
		node._position[LAST_CARDINAL[axis]].computeStatic(axis)
		node._translate[axis].computeStatic(axis)

		node._size[axis].computeStatic(axis)
		node._min_size[axis].computeStatic(axis)
		node._max_size[axis].computeStatic(axis, float('inf'))

		first_margin = node._margin[FIRST_CARDINAL[axis]]
		last_margin = node._margin[LAST_CARDINAL[axis]]
		first_margin.computeStatic(axis)
		last_margin.computeStatic(axis)
		node._axial_margin[axis] = first_margin.computed + last_margin.computed

		first_padding = node._padding[FIRST_CARDINAL[axis]]
		last_padding = node._padding[LAST_CARDINAL[axis]]
		first_padding.computeStatic(axis)
		last_padding.computeStatic(axis)
		node._axial_padding[axis] = first_padding.computed + last_padding.computed

		node._axial_border[axis] = 1 if node._border[FIRST_CARDINAL[axis]].value != 'none' else 0
		if node._border[LAST_CARDINAL[axis]].value != 'none':
			node._axial_border[axis] += 1

		if isinstance(node, Box) and node._layout.value == axis:
			node._child_gap.computeStatic(axis)

	def _computeText(self, node: Text, axis: Axis):
		text = node._text
		if axis == 'horizontal':
			text.computed = text.value.splitlines()
			return

		text.computed = Layout._wrapLines(
			node._wrap_text.value,
			text.computed,
			node._size['horizontal'].computed
		)

		text.computed = Layout._alignText(
			node._align_text.value,
			text.computed,
			max(map(len, text.computed))
		)

	def _computePreferred(self, node: Node, axis: Axis):
		size = node._size[axis]
		if size.value == 'grow' or size.value == 'fit':
			size.computed += node._axial_padding[axis] + node._axial_border[axis]

			if isinstance(node, Box):
				gaps = len(node._automatic_children) - 1
				if node._layout.value == axis and gaps > 0:
					size.computed += node._child_gap.computed * gaps

			elif isinstance(node, Text):
				text = node._text
				if axis == 'horizontal':
					size.computed += max(map(len, text.computed))
				else:
					size.computed += len(text.computed)

		# Clamp size
		size.computed = Layout._clamp(
			size.computed,
			node._min_size[axis].computed,
			node._max_size[axis].computed
		)

		# Propagate size to parent if automatically positioned and parent is dynamic
		if node._positioning.value != 'auto':
			return
		parent = node._parent
		if parent is None:
			return
		parent_size = parent._size[axis]
		if parent_size.value != 'grow' and parent_size.value != 'fit':
			return

		external = size.computed + node._axial_margin[axis]
		if parent._layout.value == axis:
			parent_size.computed += external
		elif parent_size.computed < external:
			parent_size.computed = external

	def _computeRelative(self, parent: Box, axis: Axis):
		parent_size = parent._size[axis]
		for child in parent._children:
			child_size = child._size[axis]

			# Relative size
			if child_size.type == 'percentage':
				child_size.computed = int(parent_size.computed * child_size.value / 100)

			# Relative limits
			min_size = child._min_size[axis]
			max_size = child._max_size[axis]
			if min_size.type == 'percentage':
				min_size.computed = int(parent_size.computed * min_size.value / 100)
			if max_size.type == 'percentage':
				max_size.computed = int(parent_size.computed * max_size.value / 100)

			# Relative position
			first_position = child._position[FIRST_CARDINAL[axis]]
			last_position = child._position[LAST_CARDINAL[axis]]
			reference = self._size[axis].computed if child._positioning.value == 'absolute' else parent_size.computed
			if first_position.type == 'percentage':
				first_position.computed = int(reference * first_position.value / 100)
			if last_position.type == 'percentage':
				last_position.computed = int(reference * last_position.value / 100)

			# Relative translation
			translate = child._translate[axis]
			if translate.type == 'percentage':
				translate.computed = int(child._size[axis].computed * translate.value / 100)

			# Final clamp, yayyy
			child_size.computed = Layout._clamp(
				child_size.computed,
				min_size.computed,
				max_size.computed
			)

	def _computeDynamic(self, parent: Box, axis: Axis):

		# Flood children along axis
		if parent._layout.value == axis:
			remaining = self._floodChildren(parent, axis)

			# Calculate autmatic child gap
			if parent._child_gap.value == 'auto':
				if (gaps := len(parent._automatic_children) - 1) > 0:
					parent._child_gap.computed = int(remaining / gaps)

			return

		# Clamp children across axis
		self._clampChildren(parent, axis)

	def _computePosition(self, parent: Box, axis: Axis):

		# Calculate parent offset
		offset = parent._origin[axis] + parent._padding[FIRST_CARDINAL[axis]].computed
		if parent._border[FIRST_CARDINAL[axis]].value != 'none':
			offset += 1

		# Positioned children
		parent_size = parent._size[axis]
		for child in parent._manual_children:
			translate = child._translate[axis]
			first_position = child._position[FIRST_CARDINAL[axis]]
			second_position = child._position[LAST_CARDINAL[axis]]

			if first_position.value != 'auto':
				child._origin[axis] = first_position.computed + translate.computed
			elif second_position.value != 'auto':
				child._origin[axis] = (
					parent_size.computed
					- child._size[axis].computed
					- second_position.computed
					+ translate.computed
				)

			if child._positioning.value == 'relative':
				child._origin[axis] += offset

		# Automatic children along layout axis
		if parent._layout.value == axis:
			if parent._place_content_along.value != 'start':
				remaining = parent_size.computed - parent._axial_padding[axis] - parent._axial_border[axis]
				gaps = len(parent._automatic_children) - 1

				if gaps > 0:
					remaining -= parent._child_gap.computed * gaps
				for child in parent._automatic_children:
					remaining -= child._size[axis].computed + child._axial_margin[axis]

				if parent._place_content_along.value == 'center':
					offset += int(remaining / 2)
				elif parent._place_content_along.value == 'end':
					offset += remaining

			for child in parent._automatic_children:
				child._origin[axis] = (
					offset
					+ child._margin[FIRST_CARDINAL[axis]].computed
					+ child._translate[axis].computed
				)

				offset += child._size[axis].computed + child._axial_margin[axis] + parent._child_gap.computed

			return

		# Automatic children across layout axis
		for child in parent._automatic_children:
			child._origin[axis] = (
				offset
				+ child._margin[FIRST_CARDINAL[axis]].computed
				+ child._translate[axis].computed
			)

			child._place_self_across.computed = (
				parent._place_content_across.value
				if child._place_self_across.value == 'inherit'
				else child._place_self_across.value
			)

			if child._place_self_across.computed != 'start':
				remaining = (
					parent._size[axis].computed
				  - parent._axial_padding[axis]
				  - parent._axial_border[axis]
				  - child._size[axis].computed
				  - child._axial_margin[axis]
				)

				if child._place_self_across.computed == 'center':
					child._origin[axis] += int(remaining / 2)
				elif child._place_self_across.computed == 'end':
					child._origin[axis] += remaining

	def _computeRect(self, node: Node):
		node._rect = Rect.fromOriginAndSize(
			node._origin['horizontal'],
			node._origin['vertical'],
			node._size['horizontal'].computed,
			node._size['vertical'].computed
		)

		node._clip = node._rect.intersect(
			node._parent._clip, node._overflow
		) if node._parent else node._rect

	def compute(self, width: int, height: int):
		self.width = f'{width}px'
		self.height = f'{height}px'

		pre = list(_preOrderTraversal(self))
		post = list(_postOrderTraversal(self))

		# Compute static
		for node in pre:
			if isinstance(node, Box):
				self._filterChildren(node)
			self._computeStatic(node, 'horizontal')
			self._computeStatic(node, 'vertical')

		# Compute horizontal axis
		for node in post:
			if isinstance(node, Text):
				self._computeText(node, 'horizontal')
			self._computePreferred(node, 'horizontal')
		for node in pre:
			if isinstance(node, Box):
				self._computeRelative(node, 'horizontal')
				self._computeDynamic(node, 'horizontal')
				self._computePosition(node, 'horizontal')

		# Compute vertical axis
		for node in post:
			if isinstance(node, Text):
				self._computeText(node, 'vertical')
			self._computePreferred(node, 'vertical')
		for node in pre:
			if isinstance(node, Box):
				self._computeRelative(node, 'vertical')
				self._computeDynamic(node, 'vertical')
				self._computePosition(node, 'vertical')

		# Compute rects
		for node in pre:
			self._computeRect(node)

	def select(self, selector: str) -> Selection:
		selection = Selection({self} | self._descendants)
		return selection.select(selector)