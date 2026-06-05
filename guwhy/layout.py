
from __future__ import annotations

# External libraries
from typing import TYPE_CHECKING, Generator

# Internal libraries
from .properties import *
from .selection import *
from .literals import *

if TYPE_CHECKING:
	from .canvas import Canvas

# ─────────────────────────────────── Maps & constants ───────────────────────────────────

# Constants
_INFINITY = float('inf')

# Maps axis → directions
_FIRST_DIRECTION: tuple[Direction, ...] = (LEFT, TOP)
_LAST_DIRECTION: tuple[Direction, ...] = (RIGHT, BOTTOM)

# Maps box axis → axis
_BOX_AXIS: dict[
	BoxAxis, Axis
] = { 
	BoxAxis.HORIZONTAL: HORIZONTAL, 
	BoxAxis.VERTICAL: VERTICAL
}

# Maps border style → line symbols
_HLINE = { NodeBorder.SINGLE: '─', NodeBorder.DOUBLE: '═' }
_VLINE = { NodeBorder.SINGLE: '│', NodeBorder.DOUBLE: '║' }

# Maps (h_side, v_side) → (h_style, v_style) → corner symbols
_CORNERS: dict[
	tuple[Direction, Direction],
	dict[tuple[NodeBorder, NodeBorder], str]
] = {
	(TOP, LEFT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┌',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╔',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╓',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╒'
	},
	(TOP, RIGHT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┐',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╗',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╖',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╕'
	},
	(BOTTOM, LEFT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '└',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╚',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╙',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╘'
	},
	(BOTTOM, RIGHT): {
		(NodeBorder.SINGLE, NodeBorder.SINGLE): '┘',
		(NodeBorder.DOUBLE, NodeBorder.DOUBLE): '╝',
		(NodeBorder.SINGLE, NodeBorder.DOUBLE): '╜',
		(NodeBorder.DOUBLE, NodeBorder.SINGLE): '╛'
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

	# ──── Compute intermediaries

	_inner_offset: dict[Axis, int]	# total padding + border per axis
	_outer_offset: dict[Axis, int]	# total margin per axis
	_rect: dict[Direction, int]		# bounding box
	_clip: dict[Direction, int]		# visible region

	# ──── Properties

	id: str | None
	classlist: list[str]

	visibility = PropertyDescriptor('show', literals=NodeVisibility)
	positioning = PropertyDescriptor('auto', literals=NodePositioning)
	z_index = PropertyDescriptor('auto', dimensionless=True, literals=NodeZIndex)

	origin = AxialDescriptor('auto', pixels=True, squares=True, percentages=True, literals=NodeOrigin)
	origin_x = SubDescriptor(origin, HORIZONTAL)
	origin_y = SubDescriptor(origin, VERTICAL)

	translate = AxialDescriptor('0px 0px', pixels=True, squares=True, percentages=True)
	translate_x = SubDescriptor(translate, HORIZONTAL)
	translate_y = SubDescriptor(translate, VERTICAL)

	size = AxialDescriptor('fit', pixels=True, squares=True, percentages=True, literals=NodeSize)
	width = SubDescriptor(size, HORIZONTAL)
	height = SubDescriptor(size, VERTICAL)

	min_size = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMinSize)
	min_width = SubDescriptor(min_size, HORIZONTAL)
	min_height = SubDescriptor(min_size, VERTICAL)

	max_size = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMaxSize)
	max_width = SubDescriptor(max_size, HORIZONTAL)
	max_height = SubDescriptor(max_size, VERTICAL)

	margin = DirectionalDescriptor('0px', pixels=True, squares=True)
	margin_top = SubDescriptor(margin, TOP)
	margin_right = SubDescriptor(margin, RIGHT)
	margin_bottom = SubDescriptor(margin, BOTTOM)
	margin_left = SubDescriptor(margin, LEFT)

	padding = DirectionalDescriptor('0px',pixels=True, squares=True)
	padding_top = SubDescriptor(padding, TOP)
	padding_right = SubDescriptor(padding, RIGHT)
	padding_bottom = SubDescriptor(padding, BOTTOM)
	padding_left = SubDescriptor(padding, LEFT)

	border = DirectionalDescriptor('none', literals=NodeBorder)
	border_top = SubDescriptor(border, TOP)
	border_right = SubDescriptor(border, RIGHT)
	border_bottom = SubDescriptor(border, BOTTOM)
	border_left = SubDescriptor(border, LEFT)

	overflow =  DirectionalDescriptor('hide', literals=NodeOverflow)
	overflow_top = SubDescriptor(overflow, TOP)
	overflow_right = SubDescriptor(overflow, RIGHT)
	overflow_bottom = SubDescriptor(overflow, BOTTOM)
	overflow_left = SubDescriptor(overflow, LEFT)

	background = PropertyDescriptor('opaque', literals=NodeBackground)
	mouse_events = PropertyDescriptor('capture', literals=NodeMouseEvents)

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
		self._root = self
		self._inner_offset = { HORIZONTAL: 0, VERTICAL: 0 }
		self._outer_offset = { HORIZONTAL: 0, VERTICAL: 0 }
		self._rect = { TOP: 0, RIGHT: 0, BOTTOM: 0, LEFT: 0 }
		self._clip = { TOP: 0, RIGHT: 0, BOTTOM: 0, LEFT: 0 }

		self.id = id
		self.classlist = classlist.copy()

		self.setParent(parent)
		self.applyStyles(**kwargs)

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

	def applyStyles(self, **kwargs: str) -> None:
		for key, value in kwargs.items():
			if key not in  self.__class__.__styles__:
				raise ValueError(f'Unknown style: {key}')
			setattr(self, key, value)

	def compute(self) -> None:
		preorder = list(_preOrderTraversal(self))
		postorder = list(_postOrderTraversal(self))

		# Prepare compute
		for node in preorder:
			node._computeIntrinsic()
			node._computeIntrinsicAxial(HORIZONTAL)
			node._computeIntrinsicAxial(VERTICAL)

		# Compute horizontal axis
		for node in postorder:
			node._computePreferredAxial(HORIZONTAL, self)

		for node in preorder:
			node._computeContextualAxial(HORIZONTAL, self)
			node._computePositionAxial(HORIZONTAL, self)
			node._computeBoundryAxial(HORIZONTAL)

		# Compute vertical axis
		for node in postorder:
			node._computePreferredAxial(VERTICAL, self)

		for node in preorder:
			node._computeContextualAxial(VERTICAL, self)
			node._computePositionAxial(VERTICAL, self)
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

		has_top = top_border != NodeBorder.NONE
		has_right = right_border != NodeBorder.NONE
		has_bottom = bottom_border != NodeBorder.NONE
		has_left = left_border != NodeBorder.NONE

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
			style = left_border if has_left else right_border if has_right else NodeBorder.NONE
			if style != NodeBorder.NONE and clip_left <= rect_left <= clip_right:
				canvas.setVLine(_VLINE[style], drawn_left, drawn_top, drawn_bottom)

			return

		# Single row — collapse to a horizontal line
		if rect_top == rect_bottom:
			style = top_border if has_top else bottom_border if has_bottom else NodeBorder.NONE
			if style != NodeBorder.NONE and clip_top <= rect_top <= clip_bottom:
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
			canvas.setHLine(_HLINE[top_border], drawn_left,  drawn_right,  drawn_top)
		if bottom_visible:
			canvas.setHLine(_HLINE[bottom_border], drawn_left,  drawn_right, drawn_bottom)
		if right_visible:
			canvas.setVLine(_VLINE[right_border], drawn_right, drawn_top, drawn_bottom)
		if left_visible:
			canvas.setVLine(_VLINE[left_border], drawn_left,  drawn_top, drawn_bottom)

		# Draw corners
		if top_visible:
			if left_visible:
				canvas.setChar(_CORNERS[(TOP, LEFT)][(top_border, left_border)], drawn_left, drawn_top)
			if right_visible:
				canvas.setChar(_CORNERS[(TOP, RIGHT)][(top_border, right_border)], drawn_right, drawn_top)

		if bottom_visible:
			if left_visible:
				canvas.setChar(_CORNERS[(BOTTOM, LEFT)][(bottom_border, left_border)], drawn_left, drawn_bottom)
			if right_visible:
				canvas.setChar(_CORNERS[(BOTTOM, RIGHT)][(bottom_border, right_border)], drawn_right, drawn_bottom)

	def select(self, selector: str) -> Selection:
		nodes = {self._root}
		if isinstance(self._root, Parent):
			nodes |= self._root.descendants

		selection = Selection(nodes)
		return selection.select(selector)

	# ──── Compute pipeline

	def _computeIntrinsic(self) -> None:

		# Prepare properties
		if self.z_index.value != NodeZIndex.AUTO:
			self.z_index.computed = self.z_index.value
		elif self._parent is not None:
			self.z_index.computed = self._parent.z_index.computed
		else:
			self.z_index.computed = 0

	def _computeIntrinsicAxial(self, axis: Axis) -> None:

		# Get properties
		first_direction = _FIRST_DIRECTION[axis]
		last_direction = _LAST_DIRECTION[axis]

		first_margin = self.margin[first_direction]
		last_margin = self.margin[last_direction]
		first_padding = self.padding[first_direction]
		last_padding = self.padding[last_direction]

		# Prepare properties
		self.origin[axis].prepare(axis, default=0)
		self.translate[axis].prepare(axis, default=0)
		self.size[axis].prepare(axis, default=0)
		self.min_size[axis].prepare(axis, default=0)
		self.max_size[axis].prepare(axis, default=_INFINITY)

		first_margin.prepare(axis, default=0)
		last_margin.prepare(axis, default=0)
		first_padding.prepare(axis, default=0)
		last_padding.prepare(axis, default=0)

		# Compute intermediaries
		self._inner_offset[axis] = first_padding.computed + last_padding.computed
		self._outer_offset[axis] = first_margin.computed + last_margin.computed

		if self.border[first_direction].value != NodeBorder.NONE:
			self._inner_offset[axis] += 1
		if self.border[last_direction].value != NodeBorder.NONE:
			self._inner_offset[axis] += 1

		# Compute preferred size
		self_size = self.size[axis]
		if self_size.value in (NodeSize.GROW, NodeSize.FIT) or self_size.unit == PERCENTAGE:
			self_size.computed += self._inner_offset[axis]

		# Clamp size
		self_size.clamp(
			self.min_size[axis].computed,
			self.max_size[axis].computed
		)

	def _computePreferredAxial(self, axis: Axis, root: Node) -> None:

		# NOTE this code is only valid if the parent is a box. If grids eventually get implemented, this will not work

		if not isinstance(self._parent, Box):
			return
		if self.positioning.value != NodePositioning.AUTO:
			return

		parent_size = self._parent.size[axis]
		if parent_size.value not in (NodeSize.GROW, NodeSize.FIT) and parent_size.unit != PERCENTAGE:
			return

		external_size = self.size[axis].computed + self._outer_offset[axis]

		# Along-axis: parent accomodates sum of child sizes
		if _compareAxis(axis, self._parent.axis.value):
			parent_size.computed += external_size

		# Across-axis: parent expands to accomodate largest child
		elif parent_size.computed < external_size:
			parent_size.computed = external_size

	def _computeContextualAxial(self, axis: Axis, root: Node) -> None:
		pass

	def _computePositionAxial(self, axis: Axis, root: Node) -> None:
		if self.positioning.value == NodePositioning.AUTO:
			return

		# Translate origin
		self_origin = self.origin[axis]
		self_origin.computed += self.translate[axis].computed

		# Offset origin if relative
		if self.positioning.value == NodePositioning.RELATIVE:
			assert self._parent is not None
			self_origin.computed += self._parent.origin[axis].computed

	def _computeBoundryAxial(self, axis: Axis) -> None:

		# Get properties
		first_direction = _FIRST_DIRECTION[axis]
		last_direction = _LAST_DIRECTION[axis]
		self_origin = self.origin[axis]

		# Compute rect
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

		# Update root
		child._root = self._root
		if isinstance(child, Parent):
			for descendent in child._descendants:
				descendent._root = self._root

		# Update child properties
		child._index = len(self._children)
		if child._index > 0:
			prev = self._children[-1]
			prev._next = child
			child._prev = prev

		# Update parent properties
		if child._parent is not None:
			child._parent.removeChild(child)

		child._parent = self
		self._children.append(child)

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
		
		# Update root
		child._root = child
		if isinstance(child, Parent):
			for descendent in child._descendants:
				descendent._root = child

		# Update sibling index
		node = child._next
		while node:
			assert node._index is not None
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

		# Update descendants
		node = self
		while node:
			node._descendants.discard(child)
			if isinstance(child, Box):
				node._descendants.difference_update(child._descendants)
			node = node._parent

	# ──── Compute pipeline

	def _computeIntrinsic(self) -> None:
		super()._computeIntrinsic()

		# Compute intermediaries
		self._filtered_children = []
		self._automatic_children = []

		for child in self._children:
			if child.visibility.value == NodeVisibility.NONE:
				continue

			self._filtered_children.append(child)
			if child.positioning.value == NodePositioning.AUTO:
				self._automatic_children.append(child)

	def _computeContextualAxial(self, axis: Axis, root: Node) -> None:
		super()._computeContextualAxial(axis, root)

		# Get properties
		self_size = self.size[axis]

		# Relative properties
		for child in self._filtered_children:

			# Get properties
			child_origin = child.origin[axis]
			child_translate = child.translate[axis]
			child_size = child.size[axis]
			child_min_size = child.min_size[axis]
			child_max_size = child.max_size[axis]

			# Relative size
			if child_size.unit == PERCENTAGE:
				child_size.computed = int(self_size.computed * child_size.value / 100)
			if child_min_size.unit == PERCENTAGE:
				child_min_size.computed = int(self_size.computed * child_min_size.value / 100)
			if child_max_size.unit == PERCENTAGE:
				child_max_size.computed = int(self_size.computed * child_max_size.value / 100)

			child_size.clamp(
				child_min_size.computed,
				child_max_size.computed
			)

			# Relative position
			reference = self_size.computed
			if child.positioning.value == NodePositioning.ABSOLUTE:
				reference = root.size[axis].computed
			if child_origin.unit == PERCENTAGE:
				child_origin.computed = int(reference * child_origin.value / 100)

			# Relative translation
			if child_translate.unit == PERCENTAGE:
				child_translate.computed = int(child_size.computed * child_translate.value / 100)

class Box(Parent):

	# ──── Styles

	axis = PropertyDescriptor('vertical', literals=BoxAxis)
	child_gap = PropertyDescriptor('0px', pixels=True, squares=True, literals=BoxChildGap)

	place_children = RelativeAxialDescriptor('start', literals=BoxPlaceChildren)
	place_children_along = SubDescriptor(place_children, ALONG)
	place_children_across = SubDescriptor(place_children, ACROSS)

	# ──── Compute pipeline

	def _computeIntrinsic(self) -> None:
		super()._computeIntrinsic()

		# Prepare properties
		self.child_gap.prepare(self.axis.value, default=0)

		# Compute preferred size
		if self.child_gap.value != BoxChildGap.AUTO:
			self_size = self.size[_BOX_AXIS[self.axis.value]]
			if self_size.value in (NodeSize.GROW, NodeSize.FIT) or self_size.unit == PERCENTAGE:
				if (gaps := len(self._automatic_children) - 1) > 0:
					self_size.computed += self.child_gap.computed * gaps

	def _computeContextualAxial(self, axis: Axis, root: Node) -> None:
		super()._computeContextualAxial(axis, root)

		# Dynamic properties
		if _compareAxis(axis, self.axis.value):
			remaining = self._floodChildren(axis)

			# Calculate autmatic child gap
			if self.child_gap.value == BoxChildGap.AUTO:
				if (gaps := len(self._automatic_children) - 1) > 0:
					self.child_gap.computed = int(remaining / gaps)

		# Clamp children across axis
		else:
			self._clampChildren(axis)

	def _floodChildren(self, axis: Axis) -> int:

		# Compute delta
		delta = self.size[axis].computed - self._inner_offset[axis]
		if (gaps := len(self._automatic_children) - 1) > 0:
			delta -= self.child_gap.computed * gaps
		for child in self._automatic_children:
			delta -= child.size[axis].computed + child._outer_offset[axis]

		if delta == 0:
			return 0

		sign = 1 if delta > 0 else -1
		delta *= sign

		# Find eligible children
		eligible = [
			child for child in self._automatic_children
			if child.size[axis].value == NodeSize.FIT and sign < 0
			or child.size[axis].value == NodeSize.GROW
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
				delta = 0
				break

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

		# Get properties
		self_inner_size = self.size[axis].computed - self._inner_offset[axis]

		for child in self._automatic_children:

			# Get properties
			child_outer_offset = child._outer_offset[axis]
			child_size = child.size[axis]

			# Clamp child
			if child_size.value == NodeSize.GROW or (
				child_size.value == NodeSize.FIT and
				child_size.computed + child_outer_offset > self_inner_size
			):
				child_size.clamp(
					child.min_size[axis].computed,
					child.max_size[axis].computed,
					self_inner_size - child_outer_offset
				)

	def _computePositionAxial(self, axis: Axis, root: Node) -> None:
		super()._computePositionAxial(axis, root)

		if self.positioning.value != NodePositioning.AUTO:
			return

		# Position children along box axis
		if _compareAxis(axis, self.axis.value):
			self._computePositionAlong(axis)

		# Position children across box axis
		else:
			self._computePositionAcross(axis)

	def _computePositionAlong(self, axis: Axis):

		# Get properties
		first_direction = _FIRST_DIRECTION[axis]
		place_children_along = self.place_children[ALONG].value

		# Compute internal origin
		offset = self.origin[axis].computed + self.padding[first_direction].computed
		if self.border[first_direction].value != NodeBorder.NONE:
			offset += 1

		# Resolve child alignment
		if place_children_along != BoxPlaceChildren.START and self.child_gap.value != BoxChildGap.AUTO:

			# Get remaining space
			remaining = self.size[axis].computed - self._inner_offset[axis]
			if (gaps := len(self._automatic_children) - 1) > 0:
				remaining -= self.child_gap.computed * gaps
			for child in self._automatic_children:
				remaining -= child.size[axis].computed + child._outer_offset[axis]

			# Set offset
			if place_children_along == BoxPlaceChildren.CENTER:
				offset += remaining // 2
			else:
				offset += remaining

		# Compute child origin
		for child in self._automatic_children:
			child.origin[axis].computed = (
				offset
				+ child.margin[first_direction].computed
				+ child.translate[axis].computed
			)

			offset += child.size[axis].computed + child._outer_offset[axis] + self.child_gap.computed

	def _computePositionAcross(self, axis: Axis):

		# Get properties
		first_direction = _FIRST_DIRECTION[axis]
		place_children_across = self.place_children[ACROSS].value

		# Compute internal origin
		offset = self.origin[axis].computed + self.padding[first_direction].computed
		if self.border[first_direction].value != NodeBorder.NONE:
			offset += 1

		for child in self._automatic_children:
			child_origin = child.origin[axis]

			# Compute child origin
			child_origin.computed = (
				offset
				+ child.margin[first_direction].computed
				+ child.translate[axis].computed
			)

			# Resolve child alignment
			if place_children_across != BoxPlaceChildren.START:
				remaining = self.size[axis].computed - self._inner_offset[axis] - child.size[axis].computed - child._outer_offset[axis]
				if place_children_across == BoxPlaceChildren.CENTER:
					child_origin.computed += int(remaining / 2)
				elif place_children_across == BoxPlaceChildren.END:
					child_origin.computed += remaining


