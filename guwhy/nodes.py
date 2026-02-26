
from __future__ import annotations

# External
from typing import Optional

# Internal
from .properties import *
from .literals import *
from .canvas import *

# Maps
_HLINE = { NodeBorder.SINGLE: '─', NodeBorder.DOUBLE: '═' }
_VLINE = { NodeBorder.SINGLE: '│', NodeBorder.DOUBLE: '║' }
_CORNERS = {
	(Direction.TOP, Direction.LEFT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┌',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╔',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╓',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╒'
	},
	(Direction.TOP, Direction.RIGHT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┐',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╗',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╖',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╕'
	},
	(Direction.BOTTOM, Direction.LEFT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '└',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╚',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╙',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╘'
	},
	(Direction.BOTTOM, Direction.RIGHT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┘',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╝',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╜',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╛'
	}
}

# ----------------------------------> Rect

class Rect:
	__slots__ = 'x', 'y', 'w', 'h', 'top', 'right', 'bottom', 'left'

	@staticmethod
	def fromBoundries(top: int, right: int, bottom: int, left: int) -> Rect:
		rect = Rect()
		rect.x = left
		rect.y = top
		rect.w = right - left + 1
		rect.h = bottom - top + 1
		rect.top = top
		rect.right = right
		rect.bottom = bottom
		rect.left = left

		return rect

	@staticmethod
	def fromOriginAndSize(x: int, y: int, w: int, h: int) -> Rect:
		rect = Rect()
		rect.x = x
		rect.y = y
		rect.w = w
		rect.h = h
		rect.top = y
		rect.right = x + w - 1
		rect.bottom = y + h - 1
		rect.left = x

		return rect

	def intersect(self, other: Rect, overflow: DirectionalProperty) -> Rect:
		top = self.top
		right = self.right
		bottom = self.bottom
		left = self.left

		if overflow[Direction.TOP].value == NodeOverflow.HIDE and other.top > self.top:
			top = other.top
		if overflow[Direction.RIGHT].value == NodeOverflow.HIDE and other.right < self.right:
			right = other.right
		if overflow[Direction.BOTTOM].value == NodeOverflow.HIDE and other.bottom < self.bottom:
			bottom = other.bottom
		if overflow[Direction.LEFT].value == NodeOverflow.HIDE and other.left > self.left:
			left = other.left

		return Rect.fromBoundries(top, right, bottom, left)

# -----------------------------------> Nodes

class Node:
	id: Optional[str]
	classlist: list[str]

	positioning: str = PropertyDescriptor('auto', literals=NodePositioning)
	z_index: str = PropertyDescriptor('0', dimensionless=True)

	position: str = DirectionalDescriptor('auto', pixels=True, squares=True, percentages=True, literals=NodePosition)
	top: str = SubDescriptor(position, Direction.TOP)
	right: str = SubDescriptor(position, Direction.RIGHT)
	bottom: str = SubDescriptor(position, Direction.BOTTOM)
	left: str = SubDescriptor(position, Direction.LEFT)

	translate: str = AxialDescriptor('0px 0px', pixels=True, squares=True, percentages=True)
	translate_x: str = SubDescriptor(translate, Axis.HORIZONTAL)
	translate_y: str = SubDescriptor(translate, Axis.VERTICAL)

	overflow: str =  DirectionalDescriptor('show', literals=NodeOverflow)
	overflow_top: str = SubDescriptor(overflow, Direction.TOP)
	overflow_right: str = SubDescriptor(overflow, Direction.RIGHT)
	overflow_bottom: str = SubDescriptor(overflow, Direction.BOTTOM)
	overflow_left: str = SubDescriptor(overflow, Direction.LEFT)

	size: str = AxialDescriptor('fit', pixels=True, squares=True, percentages=True, literals=NodeSize)
	width: str = SubDescriptor(size, Axis.HORIZONTAL)
	height: str = SubDescriptor(size, Axis.VERTICAL)

	min_size: str = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMinSize)
	min_width: str = SubDescriptor(min_size, Axis.HORIZONTAL)
	min_height: str = SubDescriptor(min_size, Axis.VERTICAL)

	max_size: str = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMaxSize)
	max_width: str = SubDescriptor(max_size, Axis.HORIZONTAL)
	max_height: str = SubDescriptor(max_size, Axis.VERTICAL)

	margin: str = DirectionalDescriptor('0px', pixels=True, squares=True)
	margin_top: str = SubDescriptor(margin, Direction.TOP)
	margin_right: str = SubDescriptor(margin, Direction.RIGHT)
	margin_bottom: str = SubDescriptor(margin, Direction.BOTTOM)
	margin_left: str = SubDescriptor(margin, Direction.LEFT)

	padding: str = DirectionalDescriptor('0px',pixels=True, squares=True)
	padding_top: str = SubDescriptor(padding, Direction.TOP)
	padding_right: str = SubDescriptor(padding, Direction.RIGHT)
	padding_bottom: str = SubDescriptor(padding, Direction.BOTTOM)
	padding_left: str = SubDescriptor(padding, Direction.LEFT)

	border: str = DirectionalDescriptor('none', literals=NodeBorder)
	border_top: str = SubDescriptor(border, Direction.TOP)
	border_right: str = SubDescriptor(border, Direction.RIGHT)
	border_bottom: str = SubDescriptor(border, Direction.BOTTOM)
	border_left: str = SubDescriptor(border, Direction.LEFT)

	place_self_across: str = PropertyDescriptor('inherit', literals=NodePlaceSelf)

	_parent: Optional[Box] = None
	_index: Optional[int] = None
	_next: Optional[Node] = None
	_prev: Optional[Node] = None

	_origin: AxialInteger
	_axial_margin: AxialInteger
	_axial_padding: AxialInteger
	_axial_border: AxialInteger

	_rect: Rect
	_clip: Rect

	__styles__: list[str] = []
	__descriptors__: list[BaseDescriptor] = []

	def __init__(self, id=None, classlist=None, **kwargs):

		# Setup privates
		self._origin = { Axis.HORIZONTAL: None, Axis.VERTICAL: None }
		self._axial_margin = { Axis.HORIZONTAL: None, Axis.VERTICAL: None }
		self._axial_padding = { Axis.HORIZONTAL: None, Axis.VERTICAL: None }
		self._axial_border = { Axis.HORIZONTAL: None, Axis.VERTICAL: None }

		# Setup descriptors
		for descriptor in self.__class__.__descriptors__:
			descriptor.setup(self)

		# ID and classlist
		self.id = id
		self.classlist = classlist or []

		# Apply user styles
		self.applyStyles(**kwargs)

	def __repr__(self):
		return f'Node ({self._origin[Axis.HORIZONTAL]}, {self._origin[Axis.VERTICAL]}) ' \
			 + f'{self._size[Axis.HORIZONTAL].computed}x{self._size[Axis.VERTICAL].computed}'

	def setParent(self, value: Optional[Box]):
		if value == self._parent:
			return
		if self._parent is not None:
			self._parent.removeChild(self)
		if value is not None:
			value.addChild(self)

	def applyStyles(self, **kwargs):
		for key, value in kwargs.items():
			if key not in  self.__class__.__styles__:
				raise ValueError(f'Unknown style: {key}')
			setattr(self, key, value)

	def paint(self, canvas: Canvas):
		border = self._border
		clip = self._clip
		rect = self._rect
		z = self._z_index.value

		top = border[Direction.TOP].value
		right = border[Direction.RIGHT].value
		bottom = border[Direction.BOTTOM].value
		left = border[Direction.LEFT].value

		top_visible = top != NodeBorder.NONE and clip.top <= rect.top <= clip.bottom
		right_visible = right != NodeBorder.NONE and clip.left <= rect.right <= clip.right
		bottom_visible = bottom != NodeBorder.NONE and clip.top <= rect.bottom <= clip.bottom
		left_visible = left != NodeBorder.NONE and clip.left <= rect.left <= clip.right

		# Draw sides
		if top_visible and rect.w > 2:
			canvas.drawHLine(_HLINE[top], clip.left,  clip.right,  clip.top, z)
		if bottom_visible and rect.w > 2:
			canvas.drawHLine(_HLINE[bottom], clip.left,  clip.right, clip.bottom, z)
		if right_visible and rect.h > 2:
			canvas.drawVLine(_VLINE[right], clip.right, clip.top, clip.bottom, z)
		if left_visible and rect.h > 2:
			canvas.drawVLine(_VLINE[left], clip.left,  clip.top, clip.bottom, z)

		# Draw corners
		if top_visible:
			if left_visible:
				canvas.drawChar(
					_CORNERS[(Direction.TOP, Direction.LEFT)][(top, left)],
					clip.left, clip.top, z
				)

			if right_visible:
				canvas.drawChar(
					_CORNERS[(Direction.TOP, Direction.RIGHT)][(top, right)],
					clip.right, clip.top, z
				)

		if bottom_visible:
			if left_visible:
				canvas.drawChar(
					_CORNERS[(Direction.BOTTOM, Direction.LEFT)][(bottom, left)],
					clip.left,  clip.bottom, z
				)

			if right_visible:
				canvas.drawChar(
					_CORNERS[(Direction.BOTTOM, Direction.RIGHT)][(bottom, right)],
					clip.right, clip.bottom, z
				)

class Box(Node):
	axis: str = PropertyDescriptor('vertical', literals=Axis)
	place_content_along: str = PropertyDescriptor('start', literals=BoxPlaceContent)
	place_content_across: str = PropertyDescriptor('start', literals=BoxPlaceContent)
	child_gap: str = PropertyDescriptor('0px', pixels=True, squares=True, literals=BoxChildGap)

	_children: list[Node]
	_descendants: set[Node]
	_automatic_children: list[Node]
	_manual_children: list[Node]

	def __init__(self, children=[], **kwargs):
		super().__init__(**kwargs)

		self._children = []
		self._descendants = set()
		for child in children:
			self.addChild(child)

	def __repr__(self):
		result = f'Box ({self._origin[Axis.HORIZONTAL]}, {self._origin[Axis.VERTICAL]}) ' \
			   + f'{self._size[Axis.HORIZONTAL].computed}x{self._size[Axis.VERTICAL].computed}'
		for child in self._children:
			result += '\n  ' + '\n  '.join(child.__repr__().splitlines())
		return result

	def addChild(self, child: Node):
		if child in self._children:
			return

		# Prevent cycles: child cannot be self or an ancestor of self
		if child is self or (isinstance(child, Box) and self in child._descendants):
			raise ValueError('Cannot add an ancestor as a child (cyclic hierarchy)')

		# Detatch child from old parent
		if child._parent is not None:
			child._parent.removeChild(child)

		# Update value
		child._parent = self
		child._index = len(self._children)

		# Update prev/next
		if child._index > 0:
			prev = self._children[-1]
			prev._next = child
			child._prev = prev

		# Add child to children
		self._children.append(child)

		# Update descendants
		node = self
		while node is not None:
			node._descendants.add(child)
			if isinstance(child, Box):
				node._descendants |= child._descendants
			node = node._parent

	def removeChild(self, child: Node):
		if child not in self._children:
			return

		# Update index
		node = child._next
		while node:
			node._index -= 1
			node = node._next

		# Update prev/next
		if child._prev:
			child._prev._next = child._next
		if child._next:
			child._next._prev = child._prev

		# Update descendants
		node = self
		while node:
			node._descendants.discard(child)
			if isinstance(child, Box):
				node._descendants -= child._descendants
			node = node._parent

		# Update value
		child._parent = None
		child._index = None
		child._prev = None
		child._next = None

	def paint(self, canvas: Canvas):
		super().paint(canvas)
		for child in self._children:
			child.paint(canvas)

class Text(Node):
	text: str = PropertyDescriptor('', strings=True)
	wrap_text: str = PropertyDescriptor('word', literals=TextWrap)
	align_text: str = PropertyDescriptor('left', literals=TextAlign)
	place_text_horz: str = PropertyDescriptor('left', literals=TextPlaceHorz)
	place_text_vert: str = PropertyDescriptor('top', literals=TextPlaceVert)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def __repr__(self):
		return f'Text ({self._origin[Axis.HORIZONTAL]}, {self._origin[Axis.VERTICAL]}) ' \
			 + f'{self._size[Axis.HORIZONTAL].computed}x{self._size[Axis.VERTICAL].computed}'

	def paint(self, canvas: Canvas):
		super().paint(canvas)

		rect = self._rect
		text_lines = self._text.computed
		place_horz = self._place_text_horz.value
		x = rect.left + self._padding[Direction.LEFT].computed
		if place_horz != TextPlaceHorz.LEFT:
			remaining = rect.w - self._axial_padding[Axis.HORIZONTAL] - len(text_lines[0])

			if place_horz == TextPlaceHorz.RIGHT:
				x += int(remaining / 2)
			else:
				x += remaining

		place_vert = self._place_text_vert.value
		y = rect.top + self._padding[Direction.TOP].computed
		if place_vert != TextPlaceVert.TOP:
			remaining = rect.h - self._axial_padding[Axis.VERTICAL] - len(text_lines)

			if place_vert == TextPlaceVert.CENTER:
				y += int(remaining / 2)
			else:
				y += remaining

		for line in text_lines:
			canvas.drawText(line, x, y, self._z_index.value)
