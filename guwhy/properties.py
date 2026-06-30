
from __future__ import annotations

# External libraries
from typing import TYPE_CHECKING, cast, overload, Any, Literal
from enum import Enum
import re as regex

# Internal libraries
if TYPE_CHECKING:
	from .layout import Node

# ─────────────────────────────────── Types ───────────────────────────────────

type Unit = int
PIXEL			= 0b000001
SQUARE			= 0b000010
PERCENTAGE		= 0b000100
DIMENSIONLESS	= 0b001000
LITERAL			= 0b010000
STRING			= 0b100000

type Unset = object
UNSET = object()

type All = object
ALL = object()

type Axis = Literal[0, 1]
HORIZONTAL, VERTICAL = 0, 1

type RelativeAxis = Literal[0, 1]
ALONG, ACROSS = 0, 1

type Direction = Literal[0, 1, 2, 3]
TOP, RIGHT, BOTTOM, LEFT = 0, 1, 2, 3

type Quadrant = Literal[0, 1, 2, 3]
TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT = 0, 1, 2, 3

type Key = Axis | RelativeAxis | Direction | Quadrant

# ─────────────────────────────────── Property ───────────────────────────────────

_PARSE_CACHE: dict[tuple[str, Unit], Any] = {}
_PARSE_DATA = (
	(
		PIXEL,
		regex.compile(r'^(-?[0-9]+)px$'),
		int
	),
	(
		SQUARE,
		regex.compile(r'^(-?[0-9]+)sq$'),
		int
	),
	(
		PERCENTAGE,
		regex.compile(r'^(-?[0-9]+(?:\.[0-9]+)?)%$'),
		float
	),
	(
		DIMENSIONLESS,
		regex.compile(r'^(-?[0-9]+)$'),
		int
	)
)

class Property:
	__slots__ = 'unit', 'value', 'computed'

	unit: Unit
	value: Any
	computed: Any

	def prepare(self, axis: Axis | Unset = UNSET, default: Any | Unset = UNSET) -> None:
		if self.unit & PERCENTAGE | LITERAL and default != UNSET:
			self.computed = default
			return

		self.computed = self.value
		if self.unit & SQUARE and axis == HORIZONTAL:
			self.computed *= 2

	def parse(self, value: str, units: Unit, literals: type[Enum] | None):
		for unit, pattern, cast in _PARSE_DATA:
			if not units & unit:
				continue

			key = value, unit
			if key in _PARSE_CACHE:
				self.value = _PARSE_CACHE[key]
				self.unit = unit
				return

			elif match := pattern.match(value):
				self.value = _PARSE_CACHE[key] = cast(match.group(1))
				self.unit = unit
				return

		if literals is not None and value in literals:
			self.value = literals(value)
			self.unit = LITERAL
			return

		if units & STRING: 
			self.value = value
			self.unit = STRING
			return
		
		raise ValueError(f'Unsupported property value: {value}')

# ─────────────────────────────────── Descriptors ───────────────────────────────────

class BaseDescriptor:
	name: str
	default: str
	units: dict[All | Key, Unit]
	literals: dict[All | Key, type[Enum] | None]

	def __init__(self, default: str, *, units: Unit = 0b0, literals: type[Enum] | None = None):
		self.default = default
		self.units = { ALL: units }
		self.literals = { ALL: literals }

	def __set_name__(self, owner: type[Node], name: str):
		if '__descriptors__' not in owner.__dict__:
			owner.__descriptors__ = owner.__descriptors__.copy()
		if '__styles__' not in owner.__dict__:
			owner.__styles__ = owner.__styles__.copy()

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
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		property: Property = instance.__dict__[self.name]
		property.parse(value, self.units[ALL], self.literals[ALL])

class AxialDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, (
			Property(),
			Property()
		))

		self.__set__(instance, self.default)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> AxialDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[Axis, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[Axis, Property] | AxialDescriptor:
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: horizontal, vertical = parts[0], parts[0]
			case 2: horizontal, vertical = parts[0], parts[1]
			case _: raise ValueError(f'Axial property must have 1-2 values: {value}')

		properties: tuple[Property, ...] = instance.__dict__[self.name]
		properties[HORIZONTAL].parse(horizontal, self.units[HORIZONTAL], self.literals[HORIZONTAL])
		properties[VERTICAL].parse(vertical, self.units[VERTICAL], self.literals[VERTICAL])

class RelativeAxialDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, (
			Property(),
			Property()
		))

		self.__set__(instance, self.default)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> RelativeAxialDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[RelativeAxis, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[RelativeAxis, Property] | RelativeAxialDescriptor:
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: along, across = parts[0], parts[0]
			case 2: along, across = parts[0], parts[1]
			case _: raise ValueError(f'Relative axial property must have 1-2 values: {value}')

		properties: tuple[Property, ...] = instance.__dict__[self.name]
		properties[ALONG].parse(along, self.units[ALONG], self.literals[ALONG])
		properties[ACROSS].parse(across, self.units[ACROSS], self.literals[ACROSS])

class DirectionalDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, (
			Property(),
			Property(),
			Property(),
			Property()
		))

		self.__set__(instance, self.default)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> DirectionalDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[Direction, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[Direction, Property] | DirectionalDescriptor:
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: top, right, bottom, left = parts[0], parts[0], parts[0], parts[0]
			case 2: top, right, bottom, left = parts[0], parts[1], parts[0], parts[1]
			case 3: top, right, bottom, left = parts[0], parts[1], parts[2], parts[1]
			case 4: top, right, bottom, left = parts[0], parts[1], parts[2], parts[3]
			case _: raise ValueError(f'Directional property must have 1-4 values: {value}')

		properties: tuple[Property, ...] = instance.__dict__[self.name]
		properties[TOP].parse(top, self.units[TOP], self.literals[TOP])
		properties[RIGHT].parse(right, self.units[RIGHT], self.literals[RIGHT])
		properties[BOTTOM].parse(bottom, self.units[BOTTOM], self.literals[BOTTOM])
		properties[LEFT].parse(left, self.units[LEFT], self.literals[LEFT])

class QuadrantDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, (
			Property(),
			Property(),
			Property(),
			Property()
		))

		self.__set__(instance, self.default)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> QuadrantDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> dict[Quadrant, Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> dict[Quadrant, Property] | QuadrantDescriptor:
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		parts = value.split()
		match len(parts):
			case 1: top_left, top_right, bottom_right, bottom_left = parts[0], parts[0], parts[0], parts[0]
			case 2: top_left, top_right, bottom_left, bottom_right = parts[0], parts[0], parts[1], parts[1]
			case 4: top_left, top_right, bottom_right, bottom_left = parts[0], parts[1], parts[2], parts[3]
			case _: raise ValueError(f'Quadrantial property must have 1, 2, or 4 values: {value}')

		properties: tuple[Property, ...] = instance.__dict__[self.name]
		properties[TOP_LEFT].parse(top_left, self.units[TOP_LEFT], self.literals[TOP_LEFT])
		properties[TOP_RIGHT].parse(top_right, self.units[TOP_RIGHT], self.literals[TOP_RIGHT])
		properties[BOTTOM_RIGHT].parse(bottom_left, self.units[BOTTOM_RIGHT], self.literals[BOTTOM_RIGHT])
		properties[BOTTOM_LEFT].parse(bottom_right, self.units[BOTTOM_LEFT], self.literals[BOTTOM_LEFT])

class ArrayDescriptor(BaseDescriptor):
	def setup(self, instance: Node) -> None:
		setattr(instance, self.name, [])

		self.__set__(
			instance,
			self.default
		)

	@overload
	def __get__(self, instance: None, _: type[Node]) -> ArrayDescriptor:
		...

	@overload
	def __get__(self, instance: Node, _: type[Node]) -> list[Property]:
		...

	def __get__(self, instance: Node | None, _: type[Node]) -> list[Property] | ArrayDescriptor:
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance: Node, value: str) -> None:
		properties: list[Property] = instance.__dict__[self.name]
		properties.clear()

		for part in value.split():
			property = Property()
			property.parse(part, self.units[ALL], self.literals[ALL])
			properties.append(property)

class SubDescriptor:
	def __init__(self, parent: BaseDescriptor, key: Key, *, units: Unit | Unset = UNSET, literals: type[Enum] | None | Unset = UNSET):
		self.parent = parent
		self.key = key

		# Register units and literals
		parent.units[key] = parent.units[ALL] if units == UNSET else cast(Unit, units)
		parent.literals[key] = parent.literals[ALL] if literals == UNSET else cast(type[Enum] | None, literals)

	def __set_name__(self, owner: type[Node], name: str):
		if '__styles__' not in owner.__dict__:
			owner.__styles__ = owner.__styles__.copy()
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
		return instance.__dict__[self.parent.name][self.key]

	def __set__(self, instance: Node, value: str):
		property: Property = instance.__dict__[self.parent.name][self.key]
		property.parse(value, self.parent.units[self.key], self.parent.literals[self.key])
