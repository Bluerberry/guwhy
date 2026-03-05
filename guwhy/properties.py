
# External libraries
from typing import TYPE_CHECKING, Any, overload
from enum import Enum, auto
import re as regex

# Internal libraries
if TYPE_CHECKING:
	from .layout import Node

# -----------------------------------> Properties

class Unit(Enum):
	PIXEL = auto()
	SQUARE = auto()
	PERCENTAGE = auto()
	DIMENSIONLESS = auto()
	LITERAL = auto()
	STRING = auto()

class Property:
	__slots__ = 'unit', 'value', 'computed'

	unit: Unit
	value: Any
	computed: Any

	def clamp(self, min: int, max: int, new: int | None = None) -> None:
		if new is not None:
			self.computed = new
		if self.computed < min:
			self.computed = min
		elif self.computed > max:
			self.computed = max

	def computeStatic(self, axis: Axis, default: Any = 0) -> None:
		if self.unit in (Unit.LITERAL, Unit.PERCENTAGE):
			self.computed = default

		elif self.unit in (Unit.PIXEL, Unit.DIMENSIONLESS):
			self.computed = self.value

		elif self.unit == Unit.SQUARE:
			self.computed = self.value
			if axis == Axis.HORIZONTAL:
				self.computed *= 2

# -----------------------------------> Parsing

_MATCH_PIXELS = regex.compile(r'^(-?[0-9]+)px$')
_MATCH_SQUARES = regex.compile(r'^(-?[0-9]+)sq$')
_MATCH_PERCENTAGES = regex.compile(r'^(-?[0-9]+(?:\.[0-9]+)?)%$')
_MATCH_DIMENSIONLESS = regex.compile(r'^(-?[0-9]+)$')

_PROPERTY_CACHE: dict[
	tuple[str, bool, bool, bool, bool, bool, type[Enum] | None],
	tuple[Unit, int | float | str | Enum]
] = {}

def _parse(descriptor: BaseDescriptor, property: Property, value: str):
	key = (
		value,
		descriptor.strings,
		descriptor.pixels,
		descriptor.squares,
		descriptor.percentages,
		descriptor.dimensionless,
		descriptor.literals
	)

	if key in _PROPERTY_CACHE:
		hit = _PROPERTY_CACHE[key]
	elif descriptor.pixels and (m := _MATCH_PIXELS.match(value)):
		hit = _PROPERTY_CACHE[key] = Unit.PIXEL, int(m.group(1))
	elif descriptor.squares and (m := _MATCH_SQUARES.match(value)):
		hit = _PROPERTY_CACHE[key] = Unit.SQUARE, int(m.group(1))
	elif descriptor.percentages and (m := _MATCH_PERCENTAGES.match(value)):
		hit = _PROPERTY_CACHE[key] = Unit.PERCENTAGE, float(m.group(1))
	elif descriptor.dimensionless and (m := _MATCH_DIMENSIONLESS.match(value)):
		hit = _PROPERTY_CACHE[key] = Unit.DIMENSIONLESS, int(m.group(1))
	elif descriptor.literals and value in descriptor.literals:
		hit = _PROPERTY_CACHE[key] = Unit.LITERAL, descriptor.literals(value)
	elif descriptor.strings:
		hit = _PROPERTY_CACHE[key] = Unit.STRING, value
	else:
		raise ValueError(f'Unsupported property value: {value}')

	property.unit, property.value = hit

# -----------------------------------> Descriptors

class Axis(Enum):
	HORIZONTAL = 'horizontal'
	VERTICAL = 'vertical'

class Direction(Enum):
	TOP = 'top'
	RIGHT = 'right'
	BOTTOM = 'bottom'
	LEFT = 'left'

class BaseDescriptor:
	name: str

	def __init__(self, default: str, *,
		pixels: bool = False,
		squares: bool = False,
		percentages: bool = False,
		dimensionless: bool = False,
		literals: type[Enum] | None = None,
		strings: bool = False
	):
		self.default = default
		self.pixels = pixels
		self.squares = squares
		self.percentages = percentages
		self.dimensionless = dimensionless
		self.literals = literals
		self.strings = strings

	def __set_name__(self, owner: type[Node], name: str):
		owner.__descriptors__.append(self)
		owner.__styles__.append(name)
		self.name = f'_{name}'

	def setup(self, instance: Node) -> None:
		raise NotImplementedError()

class PropertyDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, Property())
		self.__set__(instance, self.default)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> PropertyDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> Property:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> Property | PropertyDescriptor:
		if instance is None:
			return self
		return getattr(instance, self.name)

	def __set__(self, instance: Node, value: str) -> None:
		property = getattr(instance, self.name)
		_parse(self, property, value)

class AxialDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, {
			Axis.HORIZONTAL: Property(),
			Axis.VERTICAL: Property()
		})

		self.__set__(
			instance,
			self.default
		)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> AxialDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[Axis, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[Axis, Property] | AxialDescriptor:
		if instance is None:
			return self
		return getattr(instance, self.name)

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: horizontal, vertical = parts[0], parts[0]
			case 2: horizontal, vertical = parts[0], parts[1]
			case _: raise ValueError(f'Axial property must have 1-2 values: {value}')

		property = getattr(instance, self.name)
		_parse(self, property[Axis.HORIZONTAL], horizontal)
		_parse(self, property[Axis.VERTICAL], vertical)

class DirectionalDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, {
			Direction.TOP: Property(),
			Direction.RIGHT: Property(),
			Direction.BOTTOM: Property(),
			Direction.LEFT: Property()
		})

		self.__set__(
			instance,
			self.default
		)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> DirectionalDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[Direction, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[Direction, Property] | DirectionalDescriptor:
		if instance is None:
			return self
		return getattr(instance, self.name)

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: top, right, bottom, left = parts[0], parts[0], parts[0], parts[0]
			case 2: top, right, bottom, left = parts[0], parts[1], parts[0], parts[1]
			case 3: top, right, bottom, left = parts[0], parts[1], parts[2], parts[1]
			case 4: top, right, bottom, left = parts[0], parts[1], parts[2], parts[3]
			case _: raise ValueError(f'Cardinal property must have 1-4 values: {value}')

		property = getattr(instance, self.name)
		_parse(self, property[Direction.TOP], top)
		_parse(self, property[Direction.RIGHT], right)
		_parse(self, property[Direction.BOTTOM], bottom)
		_parse(self, property[Direction.LEFT], left)

class SubDescriptor:
	def __init__(self, parent: BaseDescriptor, key: Axis | Direction):
		self.parent = parent
		self.key = key

	def __set_name__(self, owner: type[Node], name: str):
		owner.__styles__.append(name)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> SubDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> Property:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> Property | SubDescriptor:
		if instance is None:
			return self

		property = getattr(instance, self.parent.name)
		return property[self.key]

	def __set__(self, instance: Node, value: str):
		property = getattr(instance, self.parent.name)
		_parse(self.parent, property[self.key], value)
