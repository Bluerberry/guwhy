
# External libraries
from typing import TYPE_CHECKING, Generator

# Internal libraries
from .properties import *
from .literals import *

if TYPE_CHECKING:
	from .canvas import Canvas

# -----------------------------------> Maps

_FIRST_DIRECTION = { Axis.HORIZONTAL: Direction.LEFT, Axis.VERTICAL: Direction.TOP }
_LAST_DIRECTION = { Axis.HORIZONTAL: Direction.RIGHT, Axis.VERTICAL: Direction.BOTTOM }

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

# -----------------------------------> Utility

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

# -----------------------------------> Node

class Node:
	__descriptors__: list[BaseDescriptor] = []
	__styles__: list[str] = []

	_parent: Box | None = None
	_index: int | None = None
	_prev: Node | None = None
	_next: Node | None = None

	_inner_offset: dict[Axis, int]
	_outer_offset: dict[Axis, int]
	_rect: dict[Direction, int]
	_clip: dict[Direction, int]

	id: str | None
	classlist: list[str]

	visibility = PropertyDescriptor('show', literals=NodeVisibility)
	positioning = PropertyDescriptor('auto', literals=NodePositioning)
	z_index = PropertyDescriptor('auto', dimensionless=True, literals=NodeZIndex)

	origin = AxialDescriptor('auto', pixels=True, squares=True, percentages=True, literals=NodePosition)
	origin_x = SubDescriptor(origin, Axis.HORIZONTAL)
	origin_y = SubDescriptor(origin, Axis.VERTICAL)

	translate = AxialDescriptor('0px 0px', pixels=True, squares=True, percentages=True)
	translate_x = SubDescriptor(translate, Axis.HORIZONTAL)
	translate_y = SubDescriptor(translate, Axis.VERTICAL)

	size = AxialDescriptor('fit', pixels=True, squares=True, percentages=True, literals=NodeSize)
	width = SubDescriptor(size, Axis.HORIZONTAL)
	height = SubDescriptor(size, Axis.VERTICAL)

	min_size = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMinSize)
	min_width = SubDescriptor(min_size, Axis.HORIZONTAL)
	min_height = SubDescriptor(min_size, Axis.VERTICAL)

	max_size = AxialDescriptor('none', pixels=True, squares=True, percentages=True, literals=NodeMaxSize)
	max_width = SubDescriptor(max_size, Axis.HORIZONTAL)
	max_height = SubDescriptor(max_size, Axis.VERTICAL)

	margin = DirectionalDescriptor('0px', pixels=True, squares=True)
	margin_top = SubDescriptor(margin, Direction.TOP)
	margin_right = SubDescriptor(margin, Direction.RIGHT)
	margin_bottom = SubDescriptor(margin, Direction.BOTTOM)
	margin_left = SubDescriptor(margin, Direction.LEFT)

	padding = DirectionalDescriptor('0px',pixels=True, squares=True)
	padding_top = SubDescriptor(padding, Direction.TOP)
	padding_right = SubDescriptor(padding, Direction.RIGHT)
	padding_bottom = SubDescriptor(padding, Direction.BOTTOM)
	padding_left = SubDescriptor(padding, Direction.LEFT)

	border = DirectionalDescriptor('none', literals=NodeBorder)
	border_top = SubDescriptor(border, Direction.TOP)
	border_right = SubDescriptor(border, Direction.RIGHT)
	border_bottom = SubDescriptor(border, Direction.BOTTOM)
	border_left = SubDescriptor(border, Direction.LEFT)

	overflow =  DirectionalDescriptor('hide', literals=NodeOverflow)
	overflow_top = SubDescriptor(overflow, Direction.TOP)
	overflow_right = SubDescriptor(overflow, Direction.RIGHT)
	overflow_bottom = SubDescriptor(overflow, Direction.BOTTOM)
	overflow_left = SubDescriptor(overflow, Direction.LEFT)

	background = PropertyDescriptor('opaque', literals=NodeBackground)
	mouse_events = PropertyDescriptor('capture', literals=NodeMouseEvents)

	@property
	def parent(self) -> Box | None:
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

	def __init__(self, **kwargs: str) -> None:
		for descriptor in self.__descriptors__:
			descriptor.setup(self)

		self._inner_offset = { Axis.HORIZONTAL: 0, Axis.VERTICAL: 0}
		self._outer_offset = { Axis.HORIZONTAL: 0, Axis.VERTICAL: 0}
		self._rect = { Direction.TOP: 0, Direction.RIGHT: 0, Direction.BOTTOM: 0, Direction.LEFT: 0 }
		self._clip = { Direction.TOP: 0, Direction.RIGHT: 0, Direction.BOTTOM: 0, Direction.LEFT: 0 }

		self.id = None
		self.classlist = []
		self.applyStyles(**kwargs)

	def __repr__(self) -> str:
		return f'Node({self.origin_x.computed}, {self.origin_y.computed})' \
			 + f' {self.width.computed}x{self.height.computed}'

	def _computeStatic(self, axis: Axis) -> None:

		# Compute static properties
		self.origin[axis].computeStatic(axis)
		self.translate[axis].computeStatic(axis)
		self.size[axis].computeStatic(axis)
		self.min_size[axis].computeStatic(axis)
		self.max_size[axis].computeStatic(axis, float('inf'))
		self.margin[_FIRST_DIRECTION[axis]].computeStatic(axis)
		self.margin[_LAST_DIRECTION[axis]].computeStatic(axis)
		self.padding[_FIRST_DIRECTION[axis]].computeStatic(axis)
		self.padding[_LAST_DIRECTION[axis]].computeStatic(axis)
		
		if self.parent is None:
			self.z_index.computeStatic(axis)
		else:
			self.z_index.computeStatic(axis, self.parent.z_index.computed)

		# Compute offset
		self._inner_offset[axis] = self.padding[_FIRST_DIRECTION[axis]].computed + self.padding[_LAST_DIRECTION[axis]].computed
		self._outer_offset[axis] = self.margin[_FIRST_DIRECTION[axis]].computed + self.margin[_LAST_DIRECTION[axis]].computed

		if self.border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			self._inner_offset[axis] += 1
		if self.border[_LAST_DIRECTION[axis]].value != NodeBorder.NONE:
			self._inner_offset[axis] += 1

	def _computePreferred(self, axis: Axis, root: Node) -> None:

		# Compute preferred size
		if self.size[axis].value in (NodeSize.GROW, NodeSize.FIT):
			self.size[axis].computed += self._inner_offset[axis]

		# Clamp size
		self.size[axis].clamp(
			self.min_size[axis].computed,
			self.max_size[axis].computed
		)

		# Propagate to parent if
		#   - this is not the root
		# 	- parent is automatically positioned
		#   - parent is dynamic

		if self == root:
			return
		if self.positioning.value != NodePositioning.AUTO:
			return
		if self.parent is None:
			return
		if self.parent.size[axis].value not in (NodeSize.GROW, NodeSize.FIT):
			return

		external_size = self.size[axis].computed + self._outer_offset[axis]
		if self.parent.axis.value == axis:
			self.parent.size[axis].computed += external_size
		elif self.parent.size[axis].computed < external_size:
			self.parent.size[axis].computed = external_size

	def _computeRelative(self, axis: Axis, root: Node) -> None:
		if self.parent is None:
			return

		# Relative size
		if self.size[axis].unit == Unit.PERCENTAGE:
			self.size[axis].computed = int(self.parent.size[axis].computed * self.size[axis].value / 100)

			# Relative limits
			if self.min_size[axis].unit == Unit.PERCENTAGE:
				self.min_size[axis].computed = int(self.parent.size[axis].computed * self.min_size[axis].value / 100)
			if self.max_size[axis].unit == Unit.PERCENTAGE:
				self.max_size[axis].computed = int(self.parent.size[axis].computed * self.max_size[axis].value / 100)

			# Final clamp
			self.size[axis].clamp(
				self.min_size[axis].computed,
				self.max_size[axis].computed
			)

		# Relative position
		reference = self.parent.size[axis].computed
		if self.positioning.value == NodePositioning.ABSOLUTE:
			reference = root.size[axis].computed

		if self.origin[axis].unit == Unit.PERCENTAGE:
			self.origin[axis].computed = int(reference * self.origin[axis].value / 100)
		if self.origin[axis].unit == Unit.PERCENTAGE:
			self.origin[axis].computed = int(reference * self.origin[axis].value / 100)

		# Relative translation
		if self.translate[axis].unit == Unit.PERCENTAGE:
			self.translate[axis].computed = int(self.size[axis].computed * self.translate[axis].value / 100)

	def _computeDynamic(self, axis: Axis) -> None:
		pass

	def _computeInnerOrigin(self, axis: Axis) -> None:
		pass

	def _computeManualPosition(self, axis: Axis) -> None:
		pass

	def _computeAutoPosition(self, axis: Axis):
		pass

	def _computeRect(self, axis: Axis):
		self._rect[_FIRST_DIRECTION[axis]] = self.origin[axis].computed
		self._rect[_LAST_DIRECTION[axis]] = self.origin[axis].computed + self.size[axis].computed - 1

	def _computeClip(self, axis: Axis):
		self_first = self._rect[_FIRST_DIRECTION[axis]]
		self_last = self._rect[_LAST_DIRECTION[axis]]

		if self.parent is not None:
			parent_first = self.parent._clip[_FIRST_DIRECTION[axis]]
			if parent_first > self_first or self.overflow[_FIRST_DIRECTION[axis]].value == NodeOverflow.SHOW:
				self_first = parent_first

			parent_last = self.parent._clip[_LAST_DIRECTION[axis]]
			if parent_last < self_last or self.overflow[_LAST_DIRECTION[axis]].value == NodeOverflow.SHOW:
				self_last = parent_last

		self._clip[_FIRST_DIRECTION[axis]] = self_first
		self._clip[_LAST_DIRECTION[axis]] = self_last

	def setParent(self, parent: Box | None) -> None:
		if self._parent == parent:
			return
		if self._parent is not None:
			self._parent.removeChild(self)
		self._parent = parent
		if self._parent is not None:
			self._parent.addChild(self)

	def applyStyles(self, **kwargs: str) -> None:
		for key, value in kwargs.items():
			if key not in  self.__class__.__styles__:
				raise ValueError(f'Unknown style: {key}')
			setattr(self, key, value)

	def compute(self) -> None:
		preorder = list(_preOrderTraversal(self))
		postorder = list(_postOrderTraversal(self))

		# Compute static
		for node in preorder:
			node._computeStatic(Axis.HORIZONTAL)
			node._computeStatic(Axis.VERTICAL)

		# Compute horizontal axis
		for node in postorder:
			node._computePreferred(Axis.HORIZONTAL, self)

		for node in preorder:
			node._computeRelative(Axis.HORIZONTAL, self)
			node._computeDynamic(Axis.HORIZONTAL)

		# Compute position
		for node in preorder:
			node._computeInnerOrigin(Axis.HORIZONTAL)
			node._computeManualPosition(Axis.HORIZONTAL)
			node._computeAutoPosition(Axis.HORIZONTAL)

			# Compute boundries
			node._computeRect(Axis.HORIZONTAL)
			node._computeClip(Axis.HORIZONTAL)

		# Compute vertical axis
		for node in postorder:
			node._computePreferred(Axis.VERTICAL, self)

		for node in preorder:
			node._computeRelative(Axis.VERTICAL, self)
			node._computeDynamic(Axis.VERTICAL)

		# Compute position
		for node in preorder:
			node._computeInnerOrigin(Axis.VERTICAL)
			node._computeManualPosition(Axis.VERTICAL)
			node._computeAutoPosition(Axis.VERTICAL)

			# Compute boundries
			node._computeRect(Axis.VERTICAL)
			node._computeClip(Axis.VERTICAL)

	def paint(self, canvas: Canvas) -> bool:
		if self.visibility.value != NodeVisibility.SHOW:
			return False
	
		rect_top = self._rect[Direction.TOP]
		rect_right = self._rect[Direction.RIGHT]
		rect_bottom = self._rect[Direction.BOTTOM]
		rect_left = self._rect[Direction.LEFT]
	
		clip_top = self._clip[Direction.TOP]
		clip_right = self._clip[Direction.RIGHT]
		clip_bottom = self._clip[Direction.BOTTOM]
		clip_left = self._clip[Direction.LEFT]
	
		# Skip if zero-size or entirely outside clip
		if rect_right < rect_left or rect_bottom < rect_top:
			return True
		if rect_right < clip_left or rect_left > clip_right or rect_bottom < clip_top or rect_top > clip_bottom:
			return True
		
		drawn_top = max(rect_top, clip_top)
		drawn_right = min(rect_right, clip_right)
		drawn_bottom = min(rect_bottom, clip_bottom)
		drawn_left = max(rect_left, clip_left)
	
		top_border = self.border[Direction.TOP].value
		right_border = self.border[Direction.RIGHT].value
		bottom_border = self.border[Direction.BOTTOM].value
		left_border = self.border[Direction.LEFT].value
	
		has_top = top_border != NodeBorder.NONE
		has_right = right_border != NodeBorder.NONE
		has_bottom = bottom_border != NodeBorder.NONE
		has_left = left_border != NodeBorder.NONE

		z = self.z_index.computed

		# Fill nodes if necissary
		if self.mouse_events.value == NodeMouseEvents.CAPTURE:
			canvas.fillNodes(
				self,
				drawn_left, drawn_right,
				drawn_top, drawn_bottom,
				z
			)
	
		# Check for degenerate rect shapes
		if rect_left == rect_right:

			# Single cell — collapse to a dot
			if rect_top == rect_bottom:
				if has_left or has_right or has_bottom or has_top:
					canvas.drawChar('·', drawn_left, drawn_top, z)					

				return True

			# Single column — collapse to a vertical line
			style = left_border if has_left else right_border if has_right else NodeBorder.NONE
			if style != NodeBorder.NONE and clip_left <= rect_left <= clip_right:
				canvas.drawVLine(_VLINE[style], drawn_left, drawn_top, drawn_bottom, z)

			return True
	
		# Single row — collapse to a horizontal line
		if rect_top == rect_bottom:
			style = top_border if has_top else bottom_border if has_bottom else NodeBorder.NONE
			if style != NodeBorder.NONE and clip_top <= rect_top <= clip_bottom:
				canvas.drawHLine(_HLINE[style], drawn_left, drawn_right, drawn_top, z)
				
			return True
	
		top_visible = has_top and clip_top <= rect_top <= clip_bottom
		right_visible = has_right and clip_left <= rect_right <= clip_right
		bottom_visible = has_bottom and clip_top <= rect_bottom <= clip_bottom
		left_visible = has_left and clip_left <= rect_left <= clip_right

		# Draw sides
		if top_visible:
			canvas.drawHLine(_HLINE[top_border], drawn_left,  drawn_right,  drawn_top, z)
		if bottom_visible:
			canvas.drawHLine(_HLINE[bottom_border], drawn_left,  drawn_right, drawn_bottom, z)
		if right_visible:
			canvas.drawVLine(_VLINE[right_border], drawn_right, drawn_top, drawn_bottom, z)
		if left_visible:
			canvas.drawVLine(_VLINE[left_border], drawn_left,  drawn_top, drawn_bottom, z)

		# Draw corners
		if top_visible:
			if left_visible:
				canvas.drawChar(
					_CORNERS[(Direction.TOP, Direction.LEFT)][(top_border, left_border)],
					drawn_left, drawn_top, z
				)

			if right_visible:
				canvas.drawChar(
					_CORNERS[(Direction.TOP, Direction.RIGHT)][(top_border, right_border)],
					drawn_right, drawn_top, z
				)

		if bottom_visible:
			if left_visible:
				canvas.drawChar(
					_CORNERS[(Direction.BOTTOM, Direction.LEFT)][(bottom_border, left_border)],
					drawn_left,  drawn_bottom, z
				)

			if right_visible:
				canvas.drawChar(
					_CORNERS[(Direction.BOTTOM, Direction.RIGHT)][(bottom_border, right_border)],
					drawn_right, drawn_bottom, z
				)
		
		# Draw background
		if self.background.value == NodeBackground.OPAQUE:
			bg_left = max(rect_left + (1 if left_visible else 0), clip_left)
			bg_right = min(rect_right - (1 if right_visible else 0), clip_right)
			bg_top = max(rect_top + (1 if top_visible else 0), clip_top)
			bg_bottom = min(rect_bottom - (1 if bottom_visible else 0), clip_bottom)

			if bg_right >= bg_left and bg_bottom >= bg_top:
				canvas.drawRect(' ', bg_left, bg_right, bg_top, bg_bottom, z)

		return True

# -----------------------------------> Box

class Box(Node):
	_children: list[Node]
	_descendants: set[Node]
	_automatic_children: list[Node]
	_inner_origin: dict[Axis, int]

	axis = PropertyDescriptor('vertical', literals=Axis)
	place_children_along = PropertyDescriptor('start', literals=BoxPlaceChildren)
	place_children_across = PropertyDescriptor('start', literals=BoxPlaceChildren)
	child_gap = PropertyDescriptor('0px', pixels=True, squares=True, literals=BoxChildGap)

	@property
	def children(self) -> list[Node]:
		return self._children.copy()

	@property
	def descendants(self) -> set[Node]:
		return self._descendants.copy()

	def __init__(self, **kwargs: str) -> None:
		super().__init__(**kwargs)

		self._children = list()
		self._descendants = set()
		self._inner_origin = { Axis.HORIZONTAL: 0, Axis.VERTICAL: 0}

	def __repr__(self) -> str:
		result = super().__repr__()
		for child in self.children:
			result += '\n\t' + '\n\t'.join(child.__repr__().splitlines())
		return result

	def _computeStatic(self, axis: Axis) -> None:
		super()._computeStatic(axis)

		# Compute static properties
		self.child_gap.computeStatic(axis)

		# Sort children by positioning
		self._automatic_children = []
		for child in self.children:
			if child.positioning.value == NodePositioning.AUTO:
				self._automatic_children.append(child)

	def _computePreferred(self, axis: Axis, root: Node) -> None:

		# Compute preferred size
		if self.axis.value == axis:
			if self.size[axis].value in (NodeSize.GROW, NodeSize.FIT):
				if (gaps := len(self._automatic_children) - 1) > 0:
					self.size[axis].computed += self.child_gap.computed * gaps

		super()._computePreferred(axis, root)

	def _computeDynamic(self, axis: Axis) -> None:

		# Flood children along axis
		if self.axis.value == axis:
			remaining = self._floodChildren(axis)

			# Calculate autmatic child gap
			if self.child_gap.value == BoxChildGap.AUTO:
				if (gaps := len(self._automatic_children) - 1) > 0:
					self.child_gap.computed = int(remaining / gaps)

			return

		# Clamp children across axis
		self._clampChildren(axis)

	def _floodChildren(self, axis: Axis) -> int:

		# Compute delta
		delta = self.size[axis].computed - self._inner_offset[axis]
		if (gaps := len(self._automatic_children) - 1) > 0:
			delta -= self.child_gap.computed * gaps # This works with auto gaps as they init as 0

		for child in self._automatic_children:
			delta -= child.size[axis].computed + child._outer_offset[axis]

		if delta == 0:
			return 0

		# Find eligible children
		eligible = [
			child for child in self._automatic_children
			if child.size[axis].value == NodeSize.FIT and delta < 0
			or child.size[axis].value == NodeSize.GROW
		]

		if not eligible:
			return delta

		sign = 1 if delta > 0 else -1

		eligible.sort(
			key=lambda node: node.size[axis].computed,
			reverse=delta < 0
		)

		# Discrete flood
		while delta != 0:
			reference = None
			for child in eligible:
				if sign + child.size[axis].computed > child.max_size[axis].computed:
					continue

				if sign + child.size[axis].computed < child.min_size[axis].computed:
					continue

				if reference is None:
					reference = sign * child.size[axis].computed
				elif sign * child.size[axis].computed > reference:
					break

				delta -= sign
				child.size[axis].computed += sign

				if delta == 0:
					break

			if reference is None:
				break

		return delta

	def _clampChildren(self, axis: Axis) -> None:
		parent_internal = self.size[axis].computed - self._inner_offset[axis]
		for child in self._automatic_children:
			child_external = child.size[axis].computed + child._outer_offset[axis]

			if child.size[axis].value == NodeSize.GROW \
			or child.size[axis].value == NodeSize.FIT \
			and child_external > parent_internal:
				child.size[axis].computed = parent_internal - child._outer_offset[axis]
				child.size[axis].clamp(
					child.min_size[axis].computed,
					child.max_size[axis].computed
				)

	def _computeInnerOrigin(self, axis: Axis):
		self._inner_origin[axis] = self.origin[axis].computed + self.padding[_FIRST_DIRECTION[axis]].computed
		if self.border[_FIRST_DIRECTION[axis]].value != NodeBorder.NONE:
			self._inner_origin[axis] += 1

	def _computeManualPosition(self, axis: Axis) -> None:
		for child in self.children:
			child.origin[axis].computed += child.translate[axis].computed
			if child.positioning.value == NodePositioning.RELATIVE:
				child.origin[axis].computed += self.origin[axis].computed

	def _computeAutoPosition(self, axis: Axis):
		if self.axis.value == axis:
			self._computeAutoPositionAlong(axis)
		else:
			self._computeAutoPositionAcross(axis)

	def _computeAutoPositionAlong(self, axis: Axis):
		offset = self._inner_origin[axis]
		if self.place_children_along.value != BoxPlaceChildren.START:
			remaining = self.size[axis].computed - self._inner_offset[axis]
			if (gaps := len(self._automatic_children) - 1) > 0:
				remaining -= self.child_gap.computed * gaps
			for child in self._automatic_children:
				remaining -= child.size[axis].computed + child._outer_offset[axis]

			if self.place_children_along.value == BoxPlaceChildren.CENTER:
				offset += int(remaining / 2)
			else:
				offset += remaining

		for child in self._automatic_children:
			child.origin[axis].computed = (
				offset
				+ child.margin[_FIRST_DIRECTION[axis]].computed
				+ child.translate[axis].computed
			)

			offset += child.size[axis].computed + child._outer_offset[axis] + self.child_gap.computed

	def _computeAutoPositionAcross(self, axis: Axis):
		for child in self._automatic_children:
			child.origin[axis].computed = (
				self._inner_origin[axis]
				+ child.margin[_FIRST_DIRECTION[axis]].computed
				+ child.translate[axis].computed
			)

			if self.place_children_across.value != BoxPlaceChildren.START:
				remaining = self.size[axis].computed - self._inner_offset[axis] - child.size[axis].computed - child._outer_offset[axis]
				if self.place_children_across.value == BoxPlaceChildren.CENTER:
					child.origin[axis].computed += int(remaining / 2)
				elif  self.place_children_across.value == BoxPlaceChildren.END:
					child.origin[axis].computed += remaining

	def addChild(self, child: Node) -> None:
		if child in self._children:
			return
		if child is self or isinstance(child, Box) and self in child._descendants:
			raise ValueError('Cannot add an ancestor as a child (cyclic hierarchy)')

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
				node._descendants |= child._descendants
			node = node._parent

	def removeChild(self, child: Node) -> None:
		if child not in self._children:
			return

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
				node._descendants -= child._descendants
			node = node._parent

	def paint(self, canvas: Canvas) -> bool:
		if not super().paint(canvas):
			return False
		
		for child in self.children:
			child.paint(canvas)
		return True