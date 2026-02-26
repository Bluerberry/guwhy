
from __future__ import annotations

# External
from typing import Optional

# Internal
from .properties import *
from .canvas import *

# maps (h-border, v-border) -> corner
CORNERS = {
	'top-left': {('single','single'): '┌', ('double','double'): '╔', ('single','double'): '╓', ('double','single'): '╒'},
	'top-right': {('single','single'): '┐', ('double','double'): '╗', ('single','double'): '╖', ('double','single'): '╕'},
	'bottom-left': {('single','single'): '└', ('double','double'): '╚', ('single','double'): '╙', ('double','single'): '╘'},
	'bottom-right': {('single','single'): '┘', ('double','double'): '╝', ('single','double'): '╜', ('double','single'): '╛'},
}

# ----------------------------------> Clip rect

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

	def intersect(self, other: Rect, overflow: CardinalProperty) -> Rect:
		top = self.top
		right = self.right
		bottom = self.bottom
		left = self.left

		if overflow['top'].value == 'hide' and other.top > self.top:
			top = other.top
		if overflow['right'].value == 'hide' and other.right < self.right:
			right = other.right
		if overflow['bottom'].value == 'hide' and other.bottom < self.bottom:
			bottom = other.bottom
		if overflow['left'].value == 'hide' and other.left > self.left:
			left = other.left

		return Rect.fromBoundries(top, right, bottom, left)		

# -----------------------------------> Nodes

class Node:
	positioning: str = PropertyDescriptor('auto', literals=('auto', 'relative', 'absolute'))

	z_index: str = PropertyDescriptor('0', dimensionless=True)

	position: str = CardinalDescriptor('auto', pixels=True, squares=True, percentages=True, literals=('auto'))
	top: str = SubDescriptor(position, 'top')
	right: str = SubDescriptor(position, 'right')
	bottom: str = SubDescriptor(position, 'bottom')
	left: str = SubDescriptor(position, 'left')

	translate: str = AxialDescriptor('0px 0px', pixels=True, squares=True, percentages=True)
	translate_x: str = SubDescriptor(translate, 'horizontal')
	translate_y: str = SubDescriptor(translate, 'vertical')

	overflow: str =  CardinalDescriptor('show', literals=('hide', 'show'))
	overflow_top: str = SubDescriptor(overflow, 'top')
	overflow_right: str = SubDescriptor(overflow, 'right')
	overflow_bottom: str = SubDescriptor(overflow, 'bottom')
	overflow_left: str = SubDescriptor(overflow, 'left')

	size: str = AxialDescriptor('fit', pixels=True, squares=True, percentages=True, literals=('grow', 'fit'))
	width: str = SubDescriptor(size, 'horizontal')
	height: str = SubDescriptor(size, 'vertical')

	min_size: str = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=('none'))
	min_width: str = SubDescriptor(min_size, 'horizontal')
	min_height: str = SubDescriptor(min_size, 'vertical')

	max_size: str = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=('none'))
	max_width: str = SubDescriptor(max_size, 'horizontal')
	max_height: str = SubDescriptor(max_size, 'vertical')

	margin: str = CardinalDescriptor('0px', pixels=True, squares=True)
	margin_top: str = SubDescriptor(margin, 'top')
	margin_right: str = SubDescriptor(margin, 'right')
	margin_bottom: str = SubDescriptor(margin, 'bottom')
	margin_left: str = SubDescriptor(margin, 'left')

	padding: str = CardinalDescriptor('0px',pixels=True, squares=True)
	padding_top: str = SubDescriptor(padding, 'top')
	padding_right: str = SubDescriptor(padding, 'right')
	padding_bottom: str = SubDescriptor(padding, 'bottom')
	padding_left: str = SubDescriptor(padding, 'left')

	border: str = CardinalDescriptor('none', literals=('none', 'single', 'double'))
	border_top: str = SubDescriptor(border, 'top')
	border_right: str = SubDescriptor(border, 'right')
	border_bottom: str = SubDescriptor(border, 'bottom')
	border_left: str = SubDescriptor(border, 'left')

	place_self_across: str = PropertyDescriptor('inherit', literals=('inherit', 'start', 'center', 'end'))

	_id: Optional[str]
	_classlist: list[str]

	_parent: Optional[Box] = None
	_index: Optional[int] = None
	_next: Optional[Node] = None
	_prev: Optional[Node] = None

	_origin: AxialInteger
	_rect: Rect
	_clip: Rect

	_axial_margin: AxialInteger
	_axial_padding: AxialInteger
	_axial_border: AxialInteger

	def __init__(self, id=None, classlist=None, **kwargs):

		# Setup privates
		self._origin = { 'horizontal': None, 'vertical': None }
		self._axial_margin = { 'horizontal': None, 'vertical': None }
		self._axial_padding = { 'horizontal': None, 'vertical': None }
		self._axial_border = { 'horizontal': None, 'vertical': None }

		# Setup descriptors
		for descriptor in self.__class__.__descriptors__:
			descriptor.setup(self)

		# ID and classlist
		self._id = id
		self._classlist = classlist or []

		# Apply user styles
		self.applyStyles(**kwargs)

	def __repr__(self):
		return f'Node ({self._origin["horizontal"]}, {self._origin["vertical"]}) {self._size["horizontal"].computed}x{self._size["vertical"].computed}'

	def setParent(self, value: Optional[Box]):
		if value == self._parent:
			return
		if self._parent is not None:
			self._parent.removeChild(self)
		if value is not None:
			value.addChild(self)

	def applyStyles(self, **kwargs):
		for key, value in kwargs.items():
			if key.startswith('_') or not hasattr(self, key):
				raise ValueError(f'Unknown style: {key}')
			setattr(self, key, value)

	def paint(self, canvas: Canvas):
		top_border = self._border['top'].value
		right_border = self._border['right'].value
		bottom_border = self._border['bottom'].value
		left_border = self._border['left'].value

		top_visible = False
		right_visible = False
		bottom_visible = False
		left_visible = False

		if top_border != 'none' and self._clip.top <= self._rect.top <= self._clip.bottom:
			top_visible = True

			if self._rect.w > 2:
				canvas.drawHLine(
					'─' if top_border == 'single' else '═',
					self._clip.left,
					self._clip.right,
					self._clip.top,
					self._z_index.value
				)

		if right_border != 'none' and self._clip.left <= self._rect.right <= self._clip.right:
			right_visible = True

			if self._rect.h > 2:
				canvas.drawVLine(
					'│' if right_border == 'single' else '║',
					self._clip.right,
					self._clip.top,
					self._clip.bottom,
					self._z_index.value
				)

		if bottom_border != 'none' and self._clip.top <= self._rect.bottom <= self._clip.bottom:
			bottom_visible = True

			if self._rect.w > 2:
				canvas.drawHLine(
					'─' if bottom_border == 'single' else '═',
					self._clip.left,
					self._clip.right,
					self._clip.bottom,
					self._z_index.value
				)

		if left_border != 'none' and self._clip.left <= self._rect.left <= self._clip.right:
			left_visible = True

			if self._rect.h > 2:
				canvas.drawVLine(
					'│' if left_border == 'single' else '║',
					self._clip.left,
					self._clip.top,
					self._clip.bottom,
					self._z_index.value
				)

		if top_visible:
			if left_visible:
				canvas.drawChar(
					CORNERS['top-left'][(top_border, left_border)],
					self._clip.left,
					self._clip.top,
					self._z_index.value
				)

			if right_visible:
				canvas.drawChar(
					CORNERS['top-right'][(top_border, right_border)],
					self._clip.right,
					self._clip.top,
					self._z_index.value
				)

		if bottom_visible:
			if left_visible:
				canvas.drawChar(
					CORNERS['bottom-left'][(bottom_border, left_border)],
					self._clip.left,
					self._clip.bottom,
					self._z_index.value
				)

			if right_visible:
				canvas.drawChar(
					CORNERS['bottom-right'][(bottom_border, right_border)],
					self._clip.right,
					self._clip.bottom,
					self._z_index.value
				)
		
class Box(Node):
	layout: str = PropertyDescriptor('vertical', literals=('horizontal', 'vertical'))
	place_content_along: str = PropertyDescriptor('start', literals=('start', 'center', 'end'))
	place_content_across: str = PropertyDescriptor('start', literals=('start', 'center', 'end'))
	child_gap: str = PropertyDescriptor('0px', pixels=True, squares=True, literals=('auto'))

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
		result = f'Box ({self._origin["horizontal"]}, {self._origin["vertical"]}) {self._size["horizontal"].computed}x{self._size["vertical"].computed}'
		for child in self._children:
			result += '\n  ' + '\n  '.join(child.__repr__().splitlines())
		return result

	def addChild(self, child: Node):
		if child in self._children:
			return
		
		# Prevent cycles: child cannot be self or an ancestor of self
		if child is self or (isinstance(child, Box) and self in child._descendants):
			raise ValueError("Cannot add an ancestor as a child (cyclic hierarchy)")

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

	wrap_text: str = PropertyDescriptor('word', literals=('none', 'char', 'word'))
	align_text: str = PropertyDescriptor('left', literals=('left', 'center', 'right'))
	place_text_horz: str = PropertyDescriptor('left', literals=('left', 'center', 'right'))
	place_text_vert: str = PropertyDescriptor('top', literals=('top', 'center', 'bottom'))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def __repr__(self):
		return f'Text ({self._origin["horizontal"]}, {self._origin["vertical"]}) {self._size["horizontal"].computed}x{self._size["vertical"].computed}'

	def paint(self, canvas: Canvas):
		super().paint(canvas)

		x = self._rect.left + self._padding['left'].computed
		if self._place_text_horz.value != 'left':
			remaining = self._rect.w - self._axial_padding['horizontal'] - len(self._text.computed[0])
			if self._place_text_horz.value == 'center':
				x += int(remaining / 2)

			else:
				x += remaining

		y = self._rect.top + self._padding['top'].computed
		if self._place_text_vert.value != 'top':
			remaining = self._rect.h - self._axial_padding['vertical'] - len(self._text.computed)
			if self._place_text_vert.value == 'center':
				y += int(remaining / 2)

			else:
				y += remaining

		for line in self._text.computed:
			canvas.drawText(line, x, y, self._z_index.value)
