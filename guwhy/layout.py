
from __future__ import annotations

# External libraries
from typing import TYPE_CHECKING, Generator

from guwhy.properties import Node

# Internal libraries
from .properties import *
from .literals import *
from .errors import *
from .wrap import *

if TYPE_CHECKING:
	from .canvas import Canvas

# ─────────────────────────────────── Maps & constants ───────────────────────────────────

_INFINITY = float('inf')

_FIRST_DIRECTION: tuple[Direction, ...] = (LEFT, TOP)
_LAST_DIRECTION: tuple[Direction, ...] = (RIGHT, BOTTOM)

_HLINE = {
	NodeBorders.SINGLE: '─',
	NodeBorders.DOUBLE: '═',
	NodeBorders.BOLD: '━'
}

_VLINE = {
	NodeBorders.SINGLE: '│',
	NodeBorders.DOUBLE: '║',
	NodeBorders.BOLD: '┃'
}

_CORNERS = {
	TOP_LEFT: {
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.SINGLE): '┌',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '╔',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.BOLD):   '┏',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.SINGLE): '╒',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.DOUBLE): '╓',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.SINGLE): '┍',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.BOLD):   '┎',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.SINGLE): '╭',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�'

	},
	TOP_RIGHT: {
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.SINGLE): '┐',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '╗',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.BOLD):   '┓',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.SINGLE): '╕',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.DOUBLE): '╖',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.SINGLE): '┑',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.BOLD):   '┒',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.SINGLE): '╮',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�'
	},
	BOTTOM_LEFT: {
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.SINGLE): '└',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '╚',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.BOLD):   '┗',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.SINGLE): '╘',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.DOUBLE): '╙',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.SINGLE): '┕',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.BOLD):   '┖',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.SINGLE): '╰',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�'
	},
	BOTTOM_RIGHT: {
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.SINGLE): '┘',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '╝',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.BOLD):   '┛',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.SINGLE): '╛',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.DOUBLE): '╜',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.SINGLE): '┙',
		(NodeCorners.SHARP, NodeBorders.SINGLE, NodeBorders.BOLD):   '┚',
		(NodeCorners.SHARP, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.SHARP, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.SINGLE): '╯',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.DOUBLE): '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.SINGLE): '�',
		(NodeCorners.ROUND, NodeBorders.SINGLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.DOUBLE, NodeBorders.BOLD):   '�',
		(NodeCorners.ROUND, NodeBorders.BOLD,   NodeBorders.DOUBLE): '�'
	}
}

# ─────────────────────────────────── Utility ───────────────────────────────────

def _preOrderTraversal(node: Node) -> Generator[Node, None, None]:
	if node.visibility.value == NodeVisibility.NONE:
		return

	yield node
	if isinstance(node, Box):
		for child in node.children:
			yield from _preOrderTraversal(child)

def _postOrderTraversal(node: Node) -> Generator[Node, None, None]:
	if node.visibility.value == NodeVisibility.NONE:
		return

	if isinstance(node, Box):
		for child in node.children:
			yield from _postOrderTraversal(child)
	yield node

def _compareAxis(axis: Axis, box_axis: BoxAxis) -> bool:
	return axis == HORIZONTAL and box_axis == BoxAxis.HORIZONTAL \
		or axis == VERTICAL and box_axis == BoxAxis.VERTICAL

def _clamp(value: int, min: int, max: int) -> int:
	if value <= min:
		return min
	if value >= max:
		return max
	return value

# ─────────────────────────────────── Nodes ───────────────────────────────────

class AbstractNode(type):
	_abstract: set[AbstractNode] = set()

	def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):

		# Register class as abstract if base not already abstract
		cls = super().__new__(mcs, name, bases, namespace)
		if not any(base in mcs._abstract for base in bases):
			mcs._abstract.add(cls)

		return cls

	def __call__(cls,
		*args: Any,
		**kwargs: Any
	):

		# Prevent instantiation if abstract
		if cls in AbstractNode._abstract:
			raise TypeError(f"{cls.__name__} cannot be instantiated directly")
		return super().__call__(*args, **kwargs)

class Node:
	__descriptors__: list[BaseDescriptor] = []
	__styles__: list[str] = []

	_root: Node
	_parent: Parent | None = None
	_index: int | None = None
	_prev: Node | None = None
	_next: Node | None = None

	@property
	def root(self) -> Node:
		return self._root

	@property
	def parent(self) -> Parent | None:
		return self._parent

	@property
	def index(self) -> int | None:
		return self._index

	@property
	def prev(self) -> Node | None:
		return self._prev

	@property
	def next(self) -> Node | None:
		return self._next

	# ──── Intermediaries

	_inner_offset: dict[Axis, int]	# Total padding + border per axis
	_outer_offset: dict[Axis, int]	# Total margin per axis
	_rect: dict[Direction, int]		# Bounding box
	_clip: dict[Direction, int]		# Visible region

	# ──── Properties

	id: str | None
	classlist: list[str]

	visibility = PropertyDescriptor('show', literals=NodeVisibility)
	positioning = PropertyDescriptor('auto', literals=NodePositioning)
	mouse_events = PropertyDescriptor('capture', literals=NodeMouseEvents)
	background = PropertyDescriptor('opaque', literals=NodeBackground)

	origin = AxialDescriptor('auto', units=PIXEL | SQUARE | PERCENTAGE, literals=NodeOrigin)
	origin_x = SubDescriptor(origin, HORIZONTAL)
	origin_y = SubDescriptor(origin, VERTICAL)

	z_index = PropertyDescriptor('auto', units=DIMENSIONLESS, literals=NodeZIndex)

	translate = AxialDescriptor('0px 0px', units=PIXEL | SQUARE | PERCENTAGE)
	translate_x = SubDescriptor(translate, HORIZONTAL)
	translate_y = SubDescriptor(translate, VERTICAL)

	size = AxialDescriptor('fit', units=PIXEL | SQUARE | PERCENTAGE, literals=NodeSize)
	width = SubDescriptor(size, HORIZONTAL)
	height = SubDescriptor(size, VERTICAL)

	min_size = AxialDescriptor('none', units=PIXEL | SQUARE | PERCENTAGE, literals=NodeMinSize)
	min_width = SubDescriptor(min_size, HORIZONTAL)
	min_height = SubDescriptor(min_size, VERTICAL)

	max_size = AxialDescriptor('none', units=PIXEL | SQUARE | PERCENTAGE, literals=NodeMaxSize)
	max_width = SubDescriptor(max_size, HORIZONTAL)
	max_height = SubDescriptor(max_size, VERTICAL)

	margin = DirectionalDescriptor('0px', units=PIXEL | SQUARE)
	margin_top = SubDescriptor(margin, TOP)
	margin_right = SubDescriptor(margin, RIGHT)
	margin_bottom = SubDescriptor(margin, BOTTOM)
	margin_left = SubDescriptor(margin, LEFT)

	padding = DirectionalDescriptor('0px', units=PIXEL | SQUARE)
	padding_top = SubDescriptor(padding, TOP)
	padding_right = SubDescriptor(padding, RIGHT)
	padding_bottom = SubDescriptor(padding, BOTTOM)
	padding_left = SubDescriptor(padding, LEFT)

	border = DirectionalDescriptor('none', literals=NodeBorders)
	border_top = SubDescriptor(border, TOP)
	border_right = SubDescriptor(border, RIGHT)
	border_bottom = SubDescriptor(border, BOTTOM)
	border_left = SubDescriptor(border, LEFT)

	corner = QuadrantDescriptor('sharp', literals=NodeCorners)
	corner_top_left = SubDescriptor(border, TOP_LEFT)
	corner_top_right = SubDescriptor(border, TOP_RIGHT)
	corner_bottom_left = SubDescriptor(border, BOTTOM_LEFT)
	corner_bottom_right = SubDescriptor(border, BOTTOM_RIGHT)

	overflow =  DirectionalDescriptor('hide', literals=NodeOverflow)
	overflow_top = SubDescriptor(overflow, TOP)
	overflow_right = SubDescriptor(overflow, RIGHT)
	overflow_bottom = SubDescriptor(overflow, BOTTOM)
	overflow_left = SubDescriptor(overflow, LEFT)

	def __init__(self, *,
		id: str | None = None,
		classlist: list[str] = [],
		parent: Parent | None = None,
		**kwargs: str
	) -> None:

		# Setup descriptors
		for descriptor in self.__descriptors__:
			descriptor.setup(self)

		# Setup properties
		self._inner_offset = { HORIZONTAL: 0, VERTICAL: 0 }
		self._outer_offset = { HORIZONTAL: 0, VERTICAL: 0 }
		self._rect = { TOP: 0, RIGHT: 0, BOTTOM: 0, LEFT: 0 }
		self._clip = { TOP: 0, RIGHT: 0, BOTTOM: 0, LEFT: 0 }

		self.id = id
		self.classlist = classlist.copy()

		self._root = self 
		self.setParent(parent)
		self.apply(**kwargs)

	def __repr__(self) -> str:
		return f'Node({self.origin_x.computed}, {self.origin_y.computed})' \
			 + f' {self.width.computed}x{self.height.computed}'

	# ──── Public methods

	def setParent(self, parent: Parent | None) -> None:
		if self._parent == parent:
			return
		if self._parent is not None:
			self._parent.removeChild(self)
		if parent is not None:
			parent.addChild(self)

	def apply(self, **kwargs: str) -> None:
		for key, value in kwargs.items():
			if key not in  self.__class__.__styles__:
				raise ValueError(f'Unknown style: {key}')
			setattr(self, key, value)

	def compute(self) -> None:
		preorder = list(_preOrderTraversal(self))
		postorder = list(_postOrderTraversal(self))

		# Prepare compute
		for node in preorder:
			node._prepareCompute()
			node._prepareComputeAxial(HORIZONTAL)
			node._prepareComputeAxial(VERTICAL)

			node._computeInherent()
			node._computeInherentAxial(HORIZONTAL)
			node._computeInherentAxial(VERTICAL)

		# Compute horizontal axis
		for node in postorder:
			node._computeContentSizeHorizontal()
			node._computeContentSizeAxial(HORIZONTAL)

		for node in preorder:
			node._computeRelativeChildSizeAxial(HORIZONTAL)
			node._computeDynamicChildSizeAxial(HORIZONTAL)

			node._computePositionAxial(HORIZONTAL)
			node._computeRelativeChildPositionAxial(HORIZONTAL)
			node._computeAutomaticChildPositionAxial(HORIZONTAL)

			node._computeBoundryAxial(HORIZONTAL)

		# Compute vertical axis
		for node in postorder:
			node._computeContentSizeVertical()
			node._computeContentSizeAxial(VERTICAL)

		for node in preorder:
			node._computeRelativeChildSizeAxial(VERTICAL)
			node._computeDynamicChildSizeAxial(VERTICAL)

			node._computePositionAxial(VERTICAL)
			node._computeRelativeChildPositionAxial(VERTICAL)
			node._computeAutomaticChildPositionAxial(VERTICAL)

			node._computeBoundryAxial(VERTICAL)

	def paint(self, canvas: Canvas) -> None:
		rect_top = self._rect[TOP]
		rect_right = self._rect[RIGHT]
		rect_bottom = self._rect[BOTTOM]
		rect_left = self._rect[LEFT]

		clip_top = self._clip[TOP]
		clip_right = self._clip[RIGHT]
		clip_bottom = self._clip[BOTTOM]
		clip_left = self._clip[LEFT]

		# Skip if zero-size
		if rect_right < rect_left or rect_bottom < rect_top:
			return

		# Skip if outside of clip
		if rect_right < clip_left or rect_left > clip_right or rect_bottom < clip_top or rect_top > clip_bottom:
			return

		drawn_top = max(rect_top, clip_top)
		drawn_right = min(rect_right, clip_right)
		drawn_bottom = min(rect_bottom, clip_bottom)
		drawn_left = max(rect_left, clip_left)

		top_border = self.border[TOP].value
		right_border = self.border[RIGHT].value
		bottom_border = self.border[BOTTOM].value
		left_border = self.border[LEFT].value

		top_left_corner = self.corner[TOP_LEFT].value
		top_right_corner = self.corner[TOP_RIGHT].value
		bottom_left_corner = self.corner[BOTTOM_LEFT].value
		bottom_right_corner = self.corner[BOTTOM_RIGHT].value

		has_top = top_border != NodeBorders.NONE
		has_right = right_border != NodeBorders.NONE
		has_bottom = bottom_border != NodeBorders.NONE
		has_left = left_border != NodeBorders.NONE

		# Fill nodes if necissary
		if self.mouse_events.value == NodeMouseEvents.CAPTURE:
			canvas.setCallback(
				self,
				drawn_left, drawn_right,
				drawn_top, drawn_bottom
			)

		# Check for degenerate rect shapes
		if rect_left == rect_right:

			# Single cell — collapse to a dot
			if rect_top == rect_bottom:
				if has_left or has_right or has_bottom or has_top:
					canvas.setChar('·', drawn_left, drawn_top)

				return

			# Single column — collapse to a vertical line
			style = left_border if has_left else right_border if has_right else NodeBorders.NONE
			if style != NodeBorders.NONE and clip_left <= rect_left <= clip_right:
				canvas.setVLine(_VLINE[style], drawn_left, drawn_top, drawn_bottom)

			return

		# Single row — collapse to a horizontal line
		if rect_top == rect_bottom:
			style = top_border if has_top else bottom_border if has_bottom else NodeBorders.NONE
			if style != NodeBorders.NONE and clip_top <= rect_top <= clip_bottom:
				canvas.setHLine(_HLINE[style], drawn_left, drawn_right, drawn_top)

			return

		top_visible = has_top and clip_top <= rect_top <= clip_bottom
		right_visible = has_right and clip_left <= rect_right <= clip_right
		bottom_visible = has_bottom and clip_top <= rect_bottom <= clip_bottom
		left_visible = has_left and clip_left <= rect_left <= clip_right

		# Draw background
		if self.background.value == NodeBackground.OPAQUE:
			canvas.setRect(' ', drawn_left, drawn_right,drawn_top, drawn_bottom)

		# Draw sides
		if top_visible:
			canvas.setHLine(_HLINE[top_border], drawn_left, drawn_right,  drawn_top)
		if bottom_visible:
			canvas.setHLine(_HLINE[bottom_border], drawn_left, drawn_right, drawn_bottom)
		if right_visible:
			canvas.setVLine(_VLINE[right_border], drawn_right, drawn_top, drawn_bottom)
		if left_visible:
			canvas.setVLine(_VLINE[left_border], drawn_left, drawn_top, drawn_bottom)

		# Draw corners
		if top_visible:
			if left_visible:
				canvas.setChar(
					_CORNERS[TOP_LEFT][(top_left_corner, top_border, left_border)],
					drawn_left, drawn_top
				)

			if right_visible:
				canvas.setChar(
					_CORNERS[TOP_RIGHT][(top_right_corner, top_border, right_border)],
					drawn_right, drawn_top
				)

		if bottom_visible:
			if left_visible:
				canvas.setChar(
					_CORNERS[BOTTOM_LEFT][(bottom_left_corner, bottom_border, left_border)],
					drawn_left, drawn_bottom
				)

			if right_visible:
				canvas.setChar(
					_CORNERS[BOTTOM_RIGHT][(bottom_right_corner, bottom_border, right_border)],
					drawn_right, drawn_bottom
				)

	# ──── Compute pipeline

	def _prepareCompute(self) -> None:
		
		# Prepare properties
		self.z_index.prepare(default=0)

	def _prepareComputeAxial(self, axis: Axis) -> None:
		first_direction = _FIRST_DIRECTION[axis]
		last_direction = _LAST_DIRECTION[axis]

		# Prepare properties
		self.origin[axis].prepare(axis, 0)
		self.translate[axis].prepare(axis, 0)

		self.size[axis].prepare(axis, 0)
		self.min_size[axis].prepare(axis, 0)
		self.max_size[axis].prepare(axis, _INFINITY)

		self.margin[first_direction].prepare(axis, 0)
		self.margin[last_direction].prepare(axis, 0)

		self.padding[first_direction].prepare(axis, 0)
		self.padding[last_direction].prepare(axis, 0)

	def _computeInherent(self) -> None:
		if self._parent is None:
			return
		
		# Compute z-index
		if self.z_index.value == NodeZIndex.AUTO:
			self.z_index.computed = self._parent.z_index.computed

	def _computeInherentAxial(self, axis: Axis) -> None:
		first_direction = _FIRST_DIRECTION[axis]
		last_direction = _LAST_DIRECTION[axis]

		self._inner_offset[axis] = self.padding[first_direction].computed + self.padding[last_direction].computed
		self._outer_offset[axis] = self.margin[first_direction].computed + self.margin[last_direction].computed

		if self.border[first_direction].value != NodeBorders.NONE:
			self._inner_offset[axis] += 1
		if self.border[last_direction].value != NodeBorders.NONE:
			self._inner_offset[axis] += 1

	def _computeContentSizeHorizontal(self) -> None:
		pass

	def _computeContentSizeVertical(self) -> None:
		pass

	def _computeContentSizeAxial(self, axis: Axis) -> None:

		# Compute preferred size
		self_size = self.size[axis]
		if self_size.unit & (PERCENTAGE | LITERAL):
			self_size.computed += self._inner_offset[axis]

		# Clamp size
		self_size.computed = _clamp(
			self_size.computed,
			self.min_size[axis].computed,
			self.max_size[axis].computed
		)

	def _computeRelativeChildSizeAxial(self, axis: Axis) -> None:
		pass

	def _computeDynamicChildSizeAxial(self, axis: Axis) -> None:
		pass
	
	def _computePositionAxial(self, axis: Axis) -> None:

		# Translate origin
		self.origin[axis].computed += self.translate[axis].computed
	
	def _computeRelativeChildPositionAxial(self, axis: Axis) -> None:
		pass

	def _computeAutomaticChildPositionAxial(self, axis: Axis) -> None:
		pass

	def _computeBoundryAxial(self, axis: Axis) -> None:
		first_direction = _FIRST_DIRECTION[axis]
		last_direction = _LAST_DIRECTION[axis]
		self_origin = self.origin[axis]

		# Resolve rect
		self_rect_first = self._rect[first_direction] = self_origin.computed
		self_rect_last = self._rect[last_direction] = self_origin.computed + self.size[axis].computed - 1

		# Compute clip
		if self._parent is not None:
			parent_clip_first = self._parent._clip[first_direction]
			parent_clip_last = self._parent._clip[last_direction]

			if parent_clip_first > self_rect_first or self.overflow[first_direction].value == NodeOverflow.SHOW:
				self_rect_first = parent_clip_first
			if parent_clip_last < self_rect_last or self.overflow[last_direction].value == NodeOverflow.SHOW:
				self_rect_last = parent_clip_last

		self._clip[first_direction] = self_rect_first
		self._clip[last_direction] = self_rect_last

class Parent(Node, metaclass=AbstractNode):

	# ──── Intermediaries

	_children: list[Node]
	_descendants: set[Node]
	_filtered_children: list[Node]
	_automatic_children: list[Node]

	@property
	def children(self) -> list[Node]:
		return self._children.copy()

	@property
	def descendants(self) -> set[Node]:
		return self._descendants.copy()

	def __init__(self, *,
		id: str | None = None,
		classlist: list[str] = [],
		parent: Parent | None = None,
		children: list[Node] = [],
		**kwargs: str
	) -> None:

		# Setup privates
		self._children = list()
		self._descendants = set()

		super().__init__(
			id=id,
			classlist=classlist,
			parent=parent,
			**kwargs
		)

		# Setup children
		for child in children:
			child.setParent(self)

	def __repr__(self) -> str:
		result = super().__repr__()
		for child in self._filtered_children:
			result += '\n\t' + '\n\t'.join(child.__repr__().splitlines())
		return result

	# ──── Public methods

	def addChild(self, child: Node) -> None:
		if child in self._children:
			return
		if child is self or isinstance(child, Parent) and self in child._descendants:
			raise ValueError('Cannot add an ancestor as a child (cyclic hierarchy)')

		# Link child
		if child._parent is not None:
			child._parent.removeChild(child)

		child._parent = self
		self._children.append(child)

		# Update index
		child._index = len(self._children) - 1
		if child._index > 0:
			prev = self._children[-2]
			prev._next = child
			child._prev = prev

		# Update root
		for node in _preOrderTraversal(child):
			node._root = self._root

		# Update descendants
		node = self
		while node is not None:
			node._descendants.add(child)
			if isinstance(child, Box):
				node._descendants.update(child._descendants)
			node = node._parent

	def removeChild(self, child: Node) -> None:
		if child not in self._children:
			return

		# Update sibling index
		node = child._next
		while node is not None:
			if node._index is None:
				raise InternalError('Malformed layout hierarchy')
			
			node._index -= 1
			node = node._next

		# Update sibling prev/next
		if child._prev:
			child._prev._next = child._next
		if child._next:
			child._next._prev = child._prev

		# Update child properties
		child._parent = None
		child._index = None
		child._prev = None
		child._next = None

		# Update root
		for node in _preOrderTraversal(child):
			node._root = child

		# Update descendants
		node = self
		while node is not None:
			node._descendants.discard(child)
			if isinstance(child, Box):
				node._descendants -= child._descendants
			node = node._parent

	# ──── Compute pipeline

	def _computeInherent(self) -> None:
		super()._prepareCompute()

		# Filter children
		self._filtered_children = []
		self._automatic_children = []

		for child in self._children:
			if child.visibility.value == NodeVisibility.NONE:
				continue

			self._filtered_children.append(child)
			if child.positioning.value == NodePositioning.AUTO:
				self._automatic_children.append(child)

	def _computeRelativeChildSizeAxial(self, axis: Axis) -> None:
		root_size = self._root.size[axis]
		self_size = self.size[axis]

		# Resolve relative size
		for child in self._filtered_children:
			child_size = child.size[axis]
			child_min_size = child.min_size[axis]
			child_max_size = child.max_size[axis]

			reference = self_size.computed
			if child.positioning.value == NodePositioning.ABSOLUTE:
				reference = root_size.computed

			if child_size.unit == PERCENTAGE:
				child_size.computed = int(reference * child_size.value / 100)
			if child_min_size.unit == PERCENTAGE:
				child_min_size.computed = int(reference * child_min_size.value / 100)
			if child_max_size.unit == PERCENTAGE:
				child_max_size.computed = int(reference * child_max_size.value / 100)

			child_size.computed = _clamp(
				child_size.computed,
				child_min_size.computed,
				child_max_size.computed
			)
	
	def _computeRelativeChildPositionAxial(self, axis: Axis) -> None:
		self_size = self.size[axis]
		self_origin = self.origin[axis]
		root_size = self._root.size[axis]

		# Resolve relative position
		for child in self._filtered_children:
			child_origin = child.origin[axis]
			child_translate = child.translate[axis]

			reference = self_size.computed
			if child.positioning.value == NodePositioning.ABSOLUTE:
				reference = root_size.computed

			if child_origin.unit == PERCENTAGE:
				child_origin.computed = int(reference * child_origin.value / 100)
			if child_translate.unit == PERCENTAGE:
				child_translate.computed = int(reference * child_translate.value / 100)
			
			if self.positioning.value == NodePositioning.RELATIVE:
				child_origin.computed += self_origin.computed

class Box(Parent):

	# ──── Styles

	axis = PropertyDescriptor('vertical', units=LITERAL, literals=BoxAxis)
	gap = PropertyDescriptor('0px', units=PIXEL | SQUARE | LITERAL, literals=BoxChildGap)

	place_children = RelativeAxialDescriptor('start', units=LITERAL, literals=BoxPlaceChildren)
	place_children_along = SubDescriptor(place_children, ALONG)
	place_children_across = SubDescriptor(place_children, ACROSS)

	# ──── Compute pipeline

	def _prepareCompute(self) -> None:
		super()._prepareCompute()

		# Prepare properties
		self.gap.prepare(self.axis.value, 0)

	def _computeContentSizeAxial(self, axis: Axis) -> None:
		self_size = self.size[axis]
		if not self_size.unit & (PERCENTAGE | LITERAL):
			return super()._computeContentSizeAxial(axis)

		# Along-axis: parent accomodates sum of child sizes
		if _compareAxis(axis, self.axis.value):
			for child in self._automatic_children:
				self_size.computed += child.size[axis].computed + child._outer_offset[axis]
			if (gaps := len(self._automatic_children) - 1) > 0:
				self_size.computed += self.gap.computed * gaps

			return super()._computeContentSizeAxial(axis)

		# Across-axis: parent expands to accomodate largest child
		for child in self._automatic_children:
			external_size = child.size[axis].computed + child._outer_offset[axis]
			if self_size.computed < external_size:
				self_size.computed = external_size

		return super()._computeContentSizeAxial(axis)

	def _computeDynamicSizeAxial(self, axis: Axis) -> None:
		
		# Flood children along axis
		if _compareAxis(axis, self.axis.value):
			remaining = self._floodChildren(axis)

			# Calculate autmatic child gap
			if remaining > 0 and self.gap.value == BoxChildGap.AUTO:
				if (gaps := len(self._automatic_children) - 1) > 0:
					self.gap.computed = int(remaining / gaps)

		# Clamp children across axis
		else:
			self._clampChildren(axis)

	def _floodChildren(self, axis: Axis) -> int:

		# Compute delta
		delta = self.size[axis].computed - self._inner_offset[axis]
		if (gaps := len(self._automatic_children) - 1) > 0:
			delta -= self.gap.computed * gaps
		for child in self._automatic_children:
			delta -= child.size[axis].computed + child._outer_offset[axis]

		if delta == 0:
			return 0

		sign = 1 if delta > 0 else -1
		delta = abs(delta)

		# Find eligible children
		eligible = [
			child for child in self._automatic_children
			if child.size[axis].value == NodeSize.GROW
			or sign < 0 and child.size[axis].unit & LITERAL
		]

		if not eligible:
			return delta

		# Sort smallest-first when growing, largest-first when shrinking
		eligible.sort(key=lambda node: sign * node.size[axis].computed)

		# Bulk flood algorithm
		while delta > 0:
			reference = None	# Size of nodes in group
			step = _INFINITY	# Size of next step
			group = 0			# Size of group

			# Collect group
			while group < len(eligible):

				# Get properties
				child = eligible[group]
				child_size = child.size[axis]
				child_min = child.min_size[axis]
				child_max = child.max_size[axis]

				# When node is different from group, stop collecting group
				if reference is None:
					reference = sign * child_size.computed

				else:
					difference = sign * child_size.computed - reference
					if difference > 0:
						if difference < step:
							step = difference # Step limit 1 - Step cant exceed node after group
						break

				# If child has no room to resize, its no longer eligible
				headroom = (child_max.computed - child_size.computed)	\
						   if sign > 0 else								\
						   (child_size.computed - child_min.computed)

				if headroom <= 0:
					eligible.pop(group)
					continue

				if headroom < step:
					step = headroom # Step limit 2 - Step cant exceed smallest headroom amongst group

				# Increase group size
				group += 1

			# If group size is 0, all nodes are at their limit
			if group == 0:
				break

			# If delta < group size, distribute remaining delta
			if delta < group:
				for child in eligible[:delta]:
					child.size[axis].computed += sign
				return 0

			# Step limit 3 - Cumulative step cannot exceed delta
			remaining = delta // group
			if remaining < step:
				step = remaining

			# Apply step
			for child in eligible[:group]:
				child.size[axis].computed += sign * step
			delta -= group * step

		return sign * delta

	def _clampChildren(self, axis: Axis) -> None:
		self_inner_size = self.size[axis].computed - self._inner_offset[axis]

		for child in self._automatic_children:

			# Get properties
			child_outer_offset = child._outer_offset[axis]
			child_size = child.size[axis]

			# Clamp child
			if child_size.value == NodeSize.GROW or (
				child_size.unit & LITERAL and
				child_size.computed + child_outer_offset > self_inner_size
			):
				child_size.computed = _clamp(
					self_inner_size - child_outer_offset,
					child.min_size[axis].computed,
					child.max_size[axis].computed
				)

	def _computeAutomaticChildPositionAxial(self, axis: Axis) -> None:
		if _compareAxis(axis, self.axis.value):
			self._computeAutomaticChildPositionAlong(axis)
		else:
			self._computeAutomaticChildPositionAcross(axis)

	def _computeAutomaticChildPositionAlong(self, axis: Axis):
		first_direction = _FIRST_DIRECTION[axis]
		place_children_along = self.place_children[ALONG].value

		# Compute internal origin
		offset = self.origin[axis].computed + self.padding[first_direction].computed
		if self.border[first_direction].value != NodeBorders.NONE:
			offset += 1

		# Resolve child alignment
		if place_children_along != BoxPlaceChildren.START and self.gap.value != BoxChildGap.AUTO:

			# Get remaining space
			remaining = self.size[axis].computed - self._inner_offset[axis]
			if (gaps := len(self._automatic_children) - 1) > 0:
				remaining -= self.gap.computed * gaps
			for child in self._automatic_children:
				remaining -= child.size[axis].computed + child._outer_offset[axis]

			# Set offset
			if place_children_along == BoxPlaceChildren.CENTER:
				offset += remaining // 2
			else:
				offset += remaining

		# Compute child origin
		for child in self._automatic_children:
			child.origin[axis].computed = offset + child.margin[first_direction].computed
			offset += child.size[axis].computed + child._outer_offset[axis] + self.gap.computed

	def _computeAutomaticChildPositionAcross(self, axis: Axis):
		first_direction = _FIRST_DIRECTION[axis]
		place_children_across = self.place_children[ACROSS].value

		# Compute internal origin
		offset = self.origin[axis].computed + self.padding[first_direction].computed
		if self.border[first_direction].value != NodeBorders.NONE:
			offset += 1

		for child in self._automatic_children:
			child_origin = child.origin[axis]

			# Compute child origin
			child_origin.computed = offset + child.margin[first_direction].computed

			# Resolve child alignment
			if place_children_across != BoxPlaceChildren.START:
				remaining = self.size[axis].computed - self._inner_offset[axis] - child.size[axis].computed - child._outer_offset[axis]
				if place_children_across == BoxPlaceChildren.CENTER:
					child_origin.computed += int(remaining / 2)
				elif place_children_across == BoxPlaceChildren.END:
					child_origin.computed += remaining

class Text(Node):

	# ──── Properties

	text = PropertyDescriptor('', units=STRING)
	wrap_text = PropertyDescriptor('word', literals=TextWrapText)
	align_text = PropertyDescriptor('left', literals=TextAlignText)
	
	place_text = AxialDescriptor('left top')
	place_text_x = SubDescriptor(place_text, HORIZONTAL, literals=TextPlaceTextX)
	place_text_y = SubDescriptor(place_text, VERTICAL, literals=TextPlaceTextY)

	# ──── Public

	def paint(self, canvas: Canvas) -> None:
		rect_top = self._rect[TOP]
		rect_right = self._rect[RIGHT]
		rect_bottom = self._rect[BOTTOM]
		rect_left = self._rect[LEFT]
		
		clip_top = self._clip[TOP]
		clip_right = self._clip[RIGHT]
		clip_bottom = self._clip[BOTTOM]
		clip_left = self._clip[LEFT]
		
		# Skip if zero-size
		if rect_right < rect_left or rect_bottom < rect_top:
			return

		# Skip if outside of clip
		if rect_right < clip_left or rect_left > clip_right or rect_bottom < clip_top or rect_top > clip_bottom:
			return
		
		# Inherit Node.paint for background, borders, corners
		super().paint(canvas)
		
		lines: list[str] = self.text.computed
		if not lines:
			return
		
		content_left = rect_left + self._inner_offset[HORIZONTAL] // 2
		content_top = rect_top + self._inner_offset[VERTICAL] // 2
		content_right = rect_right - self._inner_offset[HORIZONTAL] // 2
		content_bottom = rect_bottom - self._inner_offset[VERTICAL]   // 2
		
		content_width = content_right - content_left + 1
		content_height = content_bottom - content_top  + 1
		
		if content_width <= 0 or content_height <= 0:
			return
		
		# Vertical placement
		lines_length = len(lines)
		place_vert = self.place_text[VERTICAL].value
		
		if place_vert == TextPlaceTextY.TOP:
			text_top = content_top
		elif place_vert == TextPlaceTextY.BOTTOM:
			text_top = content_bottom - lines_length + 1
		else:
			text_top = content_top + (content_height - lines_length) // 2
		
		# Horizontal placement
		lines_width  = len(lines[0])
		place_horz  = self.place_text[HORIZONTAL].value
		
		if place_horz == TextPlaceTextX.LEFT:
			text_left = content_left
		elif place_horz == TextPlaceTextX.RIGHT:
			text_left = content_right - lines_width + 1
		else:
			text_left = content_left + (content_width - lines_width) // 2
		
		# Clip bounds for text (intersection of content area and node clip)
		draw_top = max(text_top, clip_top, content_top)
		draw_bottom = min(text_top + lines_length - 1, clip_bottom, content_bottom)
		draw_left = max(text_left, clip_left, content_left)
		draw_right = min(text_left + lines_width - 1, clip_right, content_right)
		
		if draw_right < draw_left or draw_bottom < draw_top:
			return
		
		# Character offsets into the line string
		char_start = draw_left - text_left
		char_end = draw_right - text_left + 1
		
		# Paint each visible line
		for row in range(draw_top, draw_bottom + 1):
			line_index = row - text_top
			canvas.setString(lines[line_index][char_start:char_end], draw_left, row)

	# ──── Compute pipeline

	def _computePreferredHorizontal(self) -> None:
		self.text.computed = prepareText(self.text.value)

		self_size = self.size[HORIZONTAL]
		if self_size.value == NodeSize.SHRINK:
			self_size.computed += measureTextWidth(self.text.computed, self.wrap_text.value)
		elif self_size.unit & (PERCENTAGE | LITERAL):
			self_size.computed += measureTextWidth(self.text.computed, TextWrapText.NONE)

	def _computePreferredVertical(self) -> None:
			
		self_size = self.size[VERTICAL]
		if self_size.value == NodeSize.SHRINK:
			


			self.text.computed = wrapLines(
				self.text.computed, 
				self.wrap_text.value, 
				self.align_text.value, 
				self.size[HORIZONTAL].computed - self._inner_offset[HORIZONTAL]
			)
			
			self.size[VERTICAL].computed += len(self.text.computed)
		
		super()._computePreferredAxial(axis, root)

class Grid(Parent):

	# ──── Styles

	layout = AxialDescriptor('auto', units=DIMENSIONLESS | LITERAL, literals=GridLayout)
	column_layout = SubDescriptor(layout, HORIZONTAL)
	row_layout = SubDescriptor(layout, VERTICAL)

	column_widths = ArrayDescriptor('fit', units=PIXEL | SQUARE | PERCENTAGE | LITERAL, literals=GridColumnWidths)
	row_heights = ArrayDescriptor('fit', units=PIXEL | SQUARE | PERCENTAGE | LITERAL, literals=GridRowHeights)

	place_children = AxialDescriptor('left top', units=LITERAL)
	place_children_h = SubDescriptor(place_children, HORIZONTAL, literals=GridPlaceChildrenH)
	place_children_v = SubDescriptor(place_children, VERTICAL, literals=GridPlaceChildrenV)

	gap = AxialDescriptor('0px', units=PIXEL | SQUARE | LITERAL, literals=GridChildGap)
	column_gap = SubDescriptor(gap, HORIZONTAL)
	row_gap = SubDescriptor(gap, VERTICAL)

	# ──── Compute pipeline

	def _prepareCompute(self) -> None:

		# Prepare properties
		for property in self.column_widths:
			property.prepare(HORIZONTAL, default=0)
		for property in self.row_heights:
			property.prepare(VERTICAL, default=0)

		return super()._prepareCompute()

	def _prepareComputeAxial(self, axis: Axis) -> None:

		# Prepare properties
		self.layout[axis].prepare(axis, default=0)
		self.gap[axis].prepare(axis, default=0)

		return super()._prepareComputeAxial(axis)
