
from __future__ import annotations

# External
from typing import Generator

# Internal
from .literals import *
from .nodes import *
from .selection import *

# Maps
_FIRST_DIRECTION = { Axis.HORIZONTAL: Direction.LEFT, Axis.VERTICAL: Direction.TOP }
_LAST_DIRECTION = { Axis.HORIZONTAL: Direction.RIGHT, Axis.VERTICAL: Direction.BOTTOM }
_PLACE_SELF = {
	BoxPlaceContent.START: NodePlaceSelf.START,
	BoxPlaceContent.CENTER: NodePlaceSelf.CENTER,
	BoxPlaceContent.END: NodePlaceSelf.END
}

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
		for line in lines:
			for n in range(0, len(line), width):
				result.append(line[n:n + width])

		return result

	@staticmethod
	def _wrapWord(lines: list[str], width: int) -> list[str]:
		result = []
		for content in lines:
			words = content.split()
			if not words:
				result.append('')
				continue
			
			line: list[str] = []
			remaining = width
	
			for word in words:
				wlen = len(word)
				needed = wlen if not line else wlen + 1  # +1 for the space separator
				if needed > remaining and line:
					result.append(' '.join(line))
					line = [word]
					remaining = width - wlen
				else:
					line.append(word)
					remaining -= needed
	
			if line:
				result.append(' '.join(line))
	
		return result

	@staticmethod
	def _wrapLines(wrap: TextWrap, lines: list[str], width: int) -> list[str]:
		match wrap:
			case TextWrap.NONE:
				return lines
			case TextWrap.CHAR:
				return Layout._wrapChar(lines, width)
			case TextWrap.WORD:
				return Layout._wrapWord(lines, width)

	@staticmethod
	def _alignText(align: TextAlign, lines: list[str], width: int) -> list[str]:
		match align:
			case TextAlign.LEFT:
				lines = [line.ljust(width) for line in lines]
			case TextAlign.CENTER:
				lines = [line.center(width) for line in lines]
			case TextAlign.RIGHT:
				lines = [line.rjust(width) for line in lines]

		return lines

	@staticmethod
	def _clamp(value, min_value, max_value):
		return max(min_value, min(max_value, value))

	def _filterChildren(self, parent: Box):
		parent._automatic_children = []
		parent._manual_children = []

		for child in parent._children:
			if child._positioning.value == NodePositioning.AUTO:
				parent._automatic_children.append(child)
			else:
				parent._manual_children.append(child)

	def _computeStaticProperties(self, node: Node, axis: Axis):
		node._position[_FIRST_DIRECTION[axis]].computeStatic(axis)
		node._position[_LAST_DIRECTION[axis]].computeStatic(axis)
		node._translate[axis].computeStatic(axis)

		node._size[axis].computeStatic(axis)
		node._min_size[axis].computeStatic(axis)
		node._max_size[axis].computeStatic(axis, float('inf'))

		node._margin[_FIRST_DIRECTION[axis]].computeStatic(axis)
		node._margin[_LAST_DIRECTION[axis]].computeStatic(axis)

		node._padding[_FIRST_DIRECTION[axis]].computeStatic(axis)
		node._padding[_LAST_DIRECTION[axis]].computeStatic(axis)

		if isinstance(node, Box) and node._axis.value == axis:
			node._child_gap.computeStatic(axis)

		node._inner_offset[axis] = node._padding[_FIRST_DIRECTION[axis]].computed + node._padding[_LAST_DIRECTION[axis]].computed
		node._outer_offset[axis] = node._margin[_FIRST_DIRECTION[axis]].computed + node._margin[_LAST_DIRECTION[axis]].computed

		if node._border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			node._inner_offset[axis] += 1
		if node._border[_LAST_DIRECTION[axis]].value != NodeBorder.NONE:
			node._inner_offset[axis] += 1

		node._origin[axis] = 0
		node._inner_origin[axis] = 0
		node._inner_size[axis] = node._size[axis].computed - node._inner_offset[axis]
		node._outer_size[axis] = node._size[axis].computed + node._outer_offset[axis]

	def _computeHorizontalText(self, node: Text):
		node._text.computed = node._text.value.splitlines()

	def _computeVerticalText(self, node: Text):
		node._text.computed = Layout._wrapLines(
			node._wrap_text.value,
			node._text.computed,
			node._inner_size[Axis.HORIZONTAL]
		)

		node._text.computed = Layout._alignText(
			node._align_text.value,
			node._text.computed,
			max(map(len, node._text.computed))
		)

	def _computePreferredSize(self, node: Node, axis: Axis):
		if node._size[axis].value in (NodeSize.GROW, NodeSize.FIT):
			node._size[axis].computed += node._inner_offset[axis]

			if isinstance(node, Box):
				gaps = len(node._automatic_children) - 1
				if node._axis.value == axis and gaps > 0:
					node._size[axis].computed += node._child_gap.computed * gaps

			elif isinstance(node, Text):
				if axis == Axis.HORIZONTAL:
					node._size[axis].computed += max(map(len, node._text.computed))
				else:
					node._size[axis].computed += len(node._text.computed)

		# Clamp size
		node._size[axis].computed = Layout._clamp(
			node._size[axis].computed,
			node._min_size[axis].computed,
			node._max_size[axis].computed
		)

		# Update inner/outer size
		node._inner_size[axis] = node._size[axis].computed - node._inner_offset[axis]
		node._outer_size[axis] = node._size[axis].computed + node._outer_offset[axis]

		# Propagate size to parent if automatically positioned and parent is dynamic
		if node._positioning.value != NodePositioning.AUTO:
			return
		if node._parent is None:
			return
		if node._parent._size[axis].value not in (NodeSize.GROW, NodeSize.FIT):
			return

		if node._parent._axis.value == axis:
			node._parent._size[axis].computed += node._outer_size[axis]
		elif node._parent._size[axis].computed < node._outer_size[axis]:
			node._parent._size[axis].computed = node._outer_size[axis]

	def _computeRelativeSize(self, parent: Box, axis: Axis):
		for child in parent._children:

			# Relative size
			if child._size[axis].unit == Unit.PERCENTAGE:
				child._size[axis].computed = int(parent._size[axis].computed * child._size[axis].value / 100)

			# Relative limits
			if child._min_size[axis].unit == Unit.PERCENTAGE:
				child._min_size[axis].computed = int(parent._size[axis].computed * child._min_size[axis].value / 100)
			if child._max_size[axis].unit == Unit.PERCENTAGE:
				child._max_size[axis].computed = int(parent._size[axis].computed * child._max_size[axis].value / 100)

			# Relative position
			reference = parent._size[axis].computed
			if child._positioning.value == NodePositioning.ABSOLUTE:
				reference = self._size[axis].computed

			if child._position[_FIRST_DIRECTION[axis]].unit == Unit.PERCENTAGE:
				child._position[_FIRST_DIRECTION[axis]].computed = int(reference * child._position[_FIRST_DIRECTION[axis]].value / 100)
			if child._position[_LAST_DIRECTION[axis]].unit == Unit.PERCENTAGE:
				child._position[_LAST_DIRECTION[axis]].computed = int(reference * child._position[_LAST_DIRECTION[axis]].value / 100)

			# Final clamp
			child._size[axis].computed = Layout._clamp(
				child._size[axis].computed,
				child._min_size[axis].computed,
				child._max_size[axis].computed
			)

			# Update inner/outer size
			child._inner_size[axis] = child._size[axis].computed - child._inner_offset[axis]
			child._outer_size[axis] = child._size[axis].computed + child._outer_offset[axis]

			# Relative translation
			if child._translate[axis].unit == Unit.PERCENTAGE:
				child._translate[axis].computed = int(child._size[axis].computed * child._translate[axis].value / 100)

	def _computeDynamicSize(self, parent: Box, axis: Axis):

		# Flood children along axis
		if parent._axis.value == axis:
			remaining = self._floodChildren(parent, axis)

			# Calculate autmatic child gap
			if parent._child_gap.value == BoxChildGap.AUTO:
				if (gaps := len(parent._automatic_children) - 1) > 0:
					parent._child_gap.computed = int(remaining / gaps)

		# Clamp children across axis
		else:
			self._clampChildren(parent, axis)

	def _floodChildren(self, parent: Box, axis: Axis) -> int:

		# Compute delta
		delta = parent._inner_size[axis]
		if (gaps := len(parent._automatic_children) - 1) > 0:
			delta -= parent._child_gap.computed * gaps # This works with auto gaps as they init as 0

		for child in parent._automatic_children:
			delta -= child._outer_size[axis]

		if delta == 0:
			return 0

		# Find eligible children
		eligible = [
			child for child in parent._automatic_children
			if child._size[axis].value == NodeSize.FIT and delta < 0
			or child._size[axis].value == NodeSize.GROW
		]

		if not eligible:
			return delta

		sign = 1 if delta > 0 else -1

		eligible.sort(
			key=lambda node: node._size[axis].computed,
			reverse=delta < 0
		)

		# Discrete flood
		while delta != 0:
			reference = None
			for child in eligible:
				if sign + child._size[axis].computed > child._max_size[axis].computed:
					continue

				if sign + child._size[axis].computed < child._min_size[axis].computed:
					continue

				if reference is None:
					reference = sign * child._size[axis].computed
				elif sign * child._size[axis].computed > reference:
					break

				delta -= sign
				child._size[axis].computed += sign

				if delta == 0:
					break

			if reference is None:
				break

		# Update inner outer
		for child in parent._children:
			child._inner_size[axis] = child._size[axis].computed - child._inner_offset[axis]
			child._outer_size[axis] = child._size[axis].computed + child._outer_offset[axis]

		return delta

	def _clampChildren(self, parent: Box, axis: Axis):
		for child in parent._automatic_children:
			if child._size[axis].value == NodeSize.GROW \
			or child._size[axis].value == NodeSize.FIT and child._outer_size[axis] > parent._inner_size[axis]:
				child._size[axis].computed = Layout._clamp(
					parent._inner_size[axis] - child._outer_offset[axis],
					child._min_size[axis].computed,
					child._max_size[axis].computed
				)

				# Update inner/outer
				child._inner_size[axis] = child._size[axis].computed - child._inner_offset[axis]
				child._outer_size[axis] = child._size[axis].computed + child._outer_offset[axis]

	def _computeInnerOrigin(self, node: Node, axis: Axis):
		node._inner_origin[axis] = node._origin[axis] + node._padding[_FIRST_DIRECTION[axis]].computed
		if node._border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			node._inner_origin[axis] += 1

	def _computeManualPosition(self, parent: Box, axis: Axis):
		for child in parent._manual_children:
			if child._position[_FIRST_DIRECTION[axis]].value != NodePosition.AUTO:
				child._origin[axis] = child._position[_FIRST_DIRECTION[axis]].computed + child._translate[axis].computed
			elif child._position[_LAST_DIRECTION[axis]].value != NodePosition.AUTO:
				child._origin[axis] = (
					parent._size[axis].computed
					- child._size[axis].computed
					- child._position[_LAST_DIRECTION[axis]].computed
					+ child._translate[axis].computed
				)

			if child._positioning.value == NodePositioning.RELATIVE:
				child._origin[axis] += parent._inner_origin[axis]

	def _computeAutoPositionAlong(self, parent: Box, axis: Axis):
		offset = parent._inner_origin[axis]
		if parent._place_children_along.value != BoxPlaceContent.START:
			remaining = parent._inner_size[axis]
			if (gaps := len(parent._automatic_children) - 1) > 0:
				remaining -= parent._child_gap.computed * gaps
			for child in parent._automatic_children:
				remaining -= child._outer_size[axis]

			if parent._place_children_along.value == BoxPlaceContent.CENTER:
				offset += int(remaining / 2)
			else:
				offset += remaining

		for child in parent._automatic_children:
			child._origin[axis] = (
				offset
				+ child._margin[_FIRST_DIRECTION[axis]].computed
				+ child._translate[axis].computed
			)

			offset += child._outer_size[axis] + parent._child_gap.computed

	def _computeAutoPositionAcross(self, parent: Box, axis: Axis):
		for child in parent._automatic_children:
			child._origin[axis] = (
				parent._inner_origin[axis]
				+ child._margin[_FIRST_DIRECTION[axis]].computed
				+ child._translate[axis].computed
			)

			child._place_self_across.computed = (
				_PLACE_SELF[parent._place_children_across.value]
				if child._place_self_across.value == NodePlaceSelf.INHERIT
				else child._place_self_across.value
			)

			if child._place_self_across.computed != NodePlaceSelf.START:
				remaining = parent._inner_size[axis] - child._outer_size[axis]
				if child._place_self_across.computed == NodePlaceSelf.CENTER:
					child._origin[axis] += int(remaining / 2)
				elif child._place_self_across.computed == NodePlaceSelf.END:
					child._origin[axis] += remaining

	def _computeRect(self, node: Node):
		node._rect = Rect.fromOriginAndSize(
			node._origin[Axis.HORIZONTAL],
			node._origin[Axis.VERTICAL],
			node._size[Axis.HORIZONTAL].computed,
			node._size[Axis.VERTICAL].computed
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
			self._computeStaticProperties(node, Axis.HORIZONTAL)
			self._computeStaticProperties(node, Axis.VERTICAL)

		# Compute horizontal axis
		for node in post:
			if isinstance(node, Text):
				self._computeHorizontalText(node)
			self._computePreferredSize(node, Axis.HORIZONTAL)

		for node in pre:
			if isinstance(node, Box):
				self._computeRelativeSize(node, Axis.HORIZONTAL)
				self._computeDynamicSize(node, Axis.HORIZONTAL)

		for node in pre:
			self._computeInnerOrigin(node, Axis.HORIZONTAL)
			if isinstance(node, Box):
				self._computeManualPosition(node, Axis.HORIZONTAL,)
				if node._axis.value == Axis.HORIZONTAL:
					self._computeAutoPositionAlong(node, Axis.HORIZONTAL)
				else:
					self._computeAutoPositionAcross(node, Axis.HORIZONTAL)

		# Compute vertical axis
		for node in post:
			if isinstance(node, Text):
				self._computeVerticalText(node)
			self._computePreferredSize(node, Axis.VERTICAL)

		for node in pre:
			if isinstance(node, Box):
				self._computeRelativeSize(node, Axis.VERTICAL)
				self._computeDynamicSize(node, Axis.VERTICAL)

		for node in pre:
			self._computeInnerOrigin(node, Axis.VERTICAL)
			if isinstance(node, Box):
				self._computeManualPosition(node, Axis.VERTICAL)
				if node._axis.value == Axis.VERTICAL:
					self._computeAutoPositionAlong(node, Axis.VERTICAL)
				else:
					self._computeAutoPositionAcross(node, Axis.VERTICAL)

		# Compute rects
		for node in pre:
			self._computeRect(node)

	def select(self, selector: str) -> Selection:
		selection = Selection({self} | self._descendants)
		return selection.select(selector)
