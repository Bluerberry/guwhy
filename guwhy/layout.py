
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

	def _floodChildren(self, parent: Box, axis: Axis) -> int:

		# Compute delta
		automatic_children = parent._automatic_children
		delta = parent._size[axis].computed - parent._axial_padding[axis] - parent._axial_border[axis]

		if (gaps := len(automatic_children) - 1) > 0:
			delta -= parent._child_gap.computed * gaps # This works with auto gaps as they init as 0

		for child in automatic_children:
			delta -= child._size[axis].computed + child._axial_margin[axis]

		if delta == 0:
			return 0

		# Find eligible children
		eligible = [
			child for child in automatic_children
			if child._size[axis].value == NodeSize.FIT and delta < 0
			or child._size[axis].value == NodeSize.GROW
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
		parent_internal = parent._size[axis].computed \
						- parent._axial_padding[axis] \
						- parent._axial_border[axis]

		for child in parent._automatic_children:
			child_size = child._size[axis]
			child_margin = child._axial_margin[axis]

			if child_size.value == NodeSize.GROW \
			or child_size.value == NodeSize.FIT and child_size.computed + child_margin > parent_internal:
				child_size.computed = Layout._clamp(
					parent_internal - child_margin,
					child._min_size[axis].computed,
					child._max_size[axis].computed
				)

	def _filterChildren(self, parent: Box):
		parent._automatic_children = []
		parent._manual_children = []

		for child in parent._children:
			if child._positioning.value == NodePositioning.AUTO:
				parent._automatic_children.append(child)
			else:
				parent._manual_children.append(child)

	def _computeStaticProperties(self, node: Node, axis: Axis):
		node._origin[axis] = 0
		node._position[_FIRST_DIRECTION[axis]].computeStatic(axis)
		node._position[_LAST_DIRECTION[axis]].computeStatic(axis)
		node._translate[axis].computeStatic(axis)

		node._size[axis].computeStatic(axis)
		node._min_size[axis].computeStatic(axis)
		node._max_size[axis].computeStatic(axis, float('inf'))

		first_margin = node._margin[_FIRST_DIRECTION[axis]]
		first_margin.computeStatic(axis)
		last_margin = node._margin[_LAST_DIRECTION[axis]]
		last_margin.computeStatic(axis)

		first_padding = node._padding[_FIRST_DIRECTION[axis]]
		first_padding.computeStatic(axis)
		last_padding = node._padding[_LAST_DIRECTION[axis]]
		last_padding.computeStatic(axis)

		if isinstance(node, Box) and node._axis.value == axis:
			node._child_gap.computeStatic(axis)

		node._axial_margin[axis] = first_margin.computed + last_margin.computed
		node._axial_padding[axis] = first_padding.computed + last_padding.computed
		node._axial_border[axis] = 0

		if node._border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			node._axial_border[axis] += 1
		if node._border[_LAST_DIRECTION[axis]].value != NodeBorder.NONE:
			node._axial_border[axis] += 1

	def _computeHorizontalText(self, node: Text):
		text = node._text
		text.computed = text.value.splitlines()

	def _computeVerticalText(self, node: Text):
		text = node._text
		text.computed = Layout._wrapLines(
			node._wrap_text.value,
			text.computed,
			node._size[Axis.HORIZONTAL].computed - node._axial_border[Axis.VERTICAL] - node._axial_padding[Axis.VERTICAL]
		)

		text.computed = Layout._alignText(
			node._align_text.value,
			text.computed,
			max(map(len, text.computed))
		)

	def _computePreferredSize(self, node: Node, axis: Axis):
		size = node._size[axis]
		if size.value in (NodeSize.GROW, NodeSize.FIT):
			size.computed += node._axial_padding[axis] + node._axial_border[axis]

			if isinstance(node, Box):
				gaps = len(node._automatic_children) - 1
				if node._axis.value == axis and gaps > 0:
					size.computed += node._child_gap.computed * gaps

			elif isinstance(node, Text):
				text = node._text
				if axis == Axis.HORIZONTAL:
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
		if node._positioning.value != NodePositioning.AUTO:
			return

		parent = node._parent
		if parent is None:
			return

		parent_size = parent._size[axis]
		if parent_size.value not in (NodeSize.GROW, NodeSize.FIT):
			return

		external = size.computed + node._axial_margin[axis]

		if parent._axis.value == axis:
			parent_size.computed += external
		elif parent_size.computed < external:
			parent_size.computed = external

	def _computeRelativeSize(self, parent: Box, axis: Axis):
		parent_size = parent._size[axis]
		for child in parent._children:

			# Relative size
			child_size = child._size[axis]
			if child_size.unit == Unit.PERCENTAGE:
				child_size.computed = int(parent_size.computed * child_size.value / 100)

			# Relative limits
			min_size = child._min_size[axis]
			if min_size.unit == Unit.PERCENTAGE:
				min_size.computed = int(parent_size.computed * min_size.value / 100)

			max_size = child._max_size[axis]
			if max_size.unit == Unit.PERCENTAGE:
				max_size.computed = int(parent_size.computed * max_size.value / 100)

			# Relative position
			reference = parent_size.computed
			if child._positioning.value == NodePositioning.ABSOLUTE:
				reference = self._size[axis].computed

			first_position = child._position[_FIRST_DIRECTION[axis]]
			if first_position.unit == Unit.PERCENTAGE:
				first_position.computed = int(reference * first_position.value / 100)

			last_position = child._position[_LAST_DIRECTION[axis]]
			if last_position.unit == Unit.PERCENTAGE:
				last_position.computed = int(reference * last_position.value / 100)

			# Final clamp
			child_size.computed = Layout._clamp(
				child_size.computed,
				min_size.computed,
				max_size.computed
			)

			# Relative translation
			translate = child._translate[axis]
			if translate.unit == Unit.PERCENTAGE:
				translate.computed = int(child_size.computed * translate.value / 100)

	def _computeDynamicSize(self, parent: Box, axis: Axis):

		# Flood children along axis
		if parent._axis.value == axis:
			remaining = self._floodChildren(parent, axis)

			# Calculate autmatic child gap
			child_gap = parent._child_gap
			if child_gap.value == BoxChildGap.AUTO:
				if (gaps := len(parent._automatic_children) - 1) > 0:
					child_gap.computed = int(remaining / gaps)

			return

		# Clamp children across axis
		self._clampChildren(parent, axis)

	def _computePositionOffset(self, parent: Box, axis: Axis):
		offset = parent._origin[axis] + parent._padding[_FIRST_DIRECTION[axis]].computed
		if parent._border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			offset += 1

		return offset

	def _computeManualPosition(self, parent: Box, axis: Axis, offset: int):
		parent_size = parent._size[axis]
		for child in parent._manual_children:
			translate = child._translate[axis]
			first_position = child._position[_FIRST_DIRECTION[axis]]
			second_position = child._position[_LAST_DIRECTION[axis]]

			if first_position.value != NodePosition.AUTO:
				child._origin[axis] = first_position.computed + translate.computed
			elif second_position.value != NodePosition.AUTO:
				child._origin[axis] = (
					parent_size.computed
					- child._size[axis].computed
					- second_position.computed
					+ translate.computed
				)

			if child._positioning.value == NodePositioning.RELATIVE:
				child._origin[axis] += offset

	def _computeAutoPositionAlong(self, parent: Box, axis: Axis, offset: int):
		automatic_children = parent._automatic_children
		place_children_along = parent._place_children_along
		child_gap = parent._child_gap

		if place_children_along.value != BoxPlaceContent.START:
			remaining = parent._size[axis].computed - parent._axial_padding[axis] - parent._axial_border[axis]
			gaps = len(automatic_children) - 1

			if gaps > 0:
				remaining -= child_gap.computed * gaps
			for child in automatic_children:
				remaining -= child._size[axis].computed + child._axial_margin[axis]

			if place_children_along.value == BoxPlaceContent.CENTER:
				offset += int(remaining / 2)
			else:
				offset += remaining

		for child in automatic_children:
			child._origin[axis] = (
				offset
				+ child._margin[_FIRST_DIRECTION[axis]].computed
				+ child._translate[axis].computed
			)

			offset += child._size[axis].computed + child._axial_margin[axis] + child_gap.computed

	def _computeAutoPositionAcross(self, parent: Box, axis: Axis, offset: int):
		inherit_place_self_across = _PLACE_SELF[parent._place_children_across.value]
		parent_padding = parent._axial_padding[axis]
		parent_border = parent._axial_border[axis]
		parent_size = parent._size[axis]

		for child in parent._automatic_children:
			child._origin[axis] = (
				offset
				+ child._margin[_FIRST_DIRECTION[axis]].computed
				+ child._translate[axis].computed
			)

			place_self_across = child._place_self_across
			place_self_across.computed = (
				inherit_place_self_across
				if place_self_across.value == NodePlaceSelf.INHERIT
				else place_self_across.value
			)

			if place_self_across.computed != NodePlaceSelf.START:
				remaining = (
					parent_size.computed
				  - parent_border
				  - parent_padding
				  - child._size[axis].computed
				  - child._axial_margin[axis]
				)

				if place_self_across.computed == NodePlaceSelf.CENTER:
					child._origin[axis] += int(remaining / 2)
				elif place_self_across.computed == NodePlaceSelf.END:
					child._origin[axis] += remaining

	def _computeRect(self, node: Node):
		if isinstance(node, Text) and node.text == 'Card 5: Some longer descriptive content here':
			pass

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

				offset = self._computePositionOffset(node, Axis.HORIZONTAL)
				self._computeManualPosition(node, Axis.HORIZONTAL, offset)

				if node._axis.value == Axis.HORIZONTAL:
					self._computeAutoPositionAlong(node, Axis.HORIZONTAL, offset)
				else:
					self._computeAutoPositionAcross(node, Axis.HORIZONTAL, offset)

		# Compute vertical axis
		for node in post:
			if isinstance(node, Text):
				self._computeVerticalText(node)
			self._computePreferredSize(node, Axis.VERTICAL)

		for node in pre:
			if isinstance(node, Box):
				self._computeRelativeSize(node, Axis.VERTICAL)
				self._computeDynamicSize(node, Axis.VERTICAL)

				offset = self._computePositionOffset(node, Axis.VERTICAL)
				self._computeManualPosition(node, Axis.VERTICAL, offset)
				
				if node._axis.value == Axis.VERTICAL:
					self._computeAutoPositionAlong(node, Axis.VERTICAL, offset)
				else:
					self._computeAutoPositionAcross(node, Axis.VERTICAL, offset)

		# Compute rects
		for node in pre:
			self._computeRect(node)

	def select(self, selector: str) -> Selection:
		selection = Selection({self} | self._descendants)
		return selection.select(selector)
