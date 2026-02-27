
from __future__ import annotations

# External
import re
from enum import Enum, auto
from typing import Any, Optional

# Types
class Axis(Enum):
	HORIZONTAL = 'horizontal'
	VERTICAL = 'vertical'

class Direction(Enum):
	TOP = 'top'
	RIGHT = 'right'
	BOTTOM = 'bottom'
	LEFT = 'left'

class Unit(Enum):
	PIXEL = auto()
	SQUARE = auto()
	PERCENTAGE = auto()
	DIMENSIONLESS = auto()
	LITERAL = auto()
	STRING = auto()

type AxialProperty = dict[Axis, Property]
type DirectionalProperty = dict[Direction, Property]

# Regex
_MATCH_PIXELS = re.compile(r'^([0-9]+)px$')
_MATCH_PERCENTAGES = re.compile(r'^(-?[0-9]+(?:\.[0-9]+)?)%$')
_MATCH_SQUARES = re.compile(r'^([0-9]+)sq$')
_MATCH_DIMENSIONLESS = re.compile(r'^([0-9]+)$')

# -----------------------------------> Property

class Property:
	__slots__ = 'raw', 'unit', 'value', 'computed'

	def __init__(self, raw, unit, value):
		self.raw = raw
		self.unit = unit
		self.value = value
		self.computed = None

	def __repr__(self) -> str:
		return f'Property({self.raw}, computed={self.computed})'

	def computeStatic(self, axis: Axis, default: Any = 0):
		if self.unit in (Unit.PIXEL, Unit.DIMENSIONLESS, Unit.STRING):
			self.computed = self.value

		elif self.unit == Unit.SQUARE:
			self.computed = self.value
			if axis == Axis.HORIZONTAL:
				self.computed *= 2

		else: # Literals and percentages
			self.computed = default

# -----------------------------------> Parsing

_PROPERTY_CACHE = {}

def _parse(descriptor: BaseDescriptor, property: Property, raw: str):
	key = (
		raw,
		descriptor.strings,
		descriptor.pixels,
		descriptor.squares,
		descriptor.percentages,
		descriptor.dimensionless,
		descriptor.literals
	)

	if key in _PROPERTY_CACHE:
		hit = _PROPERTY_CACHE[key]
	elif descriptor.pixels and (m := _MATCH_PIXELS.match(raw)):
		hit = _PROPERTY_CACHE[key] = Unit.PIXEL, int(m.group(1))
	elif descriptor.squares and (m := _MATCH_SQUARES.match(raw)):
		hit = _PROPERTY_CACHE[key] = Unit.SQUARE, int(m.group(1))
	elif descriptor.percentages and (m := _MATCH_PERCENTAGES.match(raw)):
		hit = _PROPERTY_CACHE[key] = Unit.PERCENTAGE, float(m.group(1))
	elif descriptor.dimensionless and (m := _MATCH_DIMENSIONLESS.match(raw)):
		hit = _PROPERTY_CACHE[key] = Unit.DIMENSIONLESS, int(m.group(1))
	elif descriptor.literals and raw in descriptor.literals:
		hit = _PROPERTY_CACHE[key] = Unit.LITERAL, descriptor.literals(raw)
	elif descriptor.strings:
		hit = _PROPERTY_CACHE[key] = Unit.STRING, raw
	else:
		raise ValueError(f'Unsupported property: {raw}')

	property.raw = raw
	property.unit, property.value = hit
	property.computed = None

# -----------------------------------> Descriptors

class BaseDescriptor:
	attr: str
	def __init__(self, default: str, *,
		pixels: bool = False,
		squares: bool = False,
		percentages: bool = False,
		dimensionless: bool = False,
		literals: Optional[Enum] = None,
		strings: bool = False
	):
		self.default = default
		self.pixels = pixels
		self.squares = squares
		self.percentages = percentages
		self.dimensionless = dimensionless
		self.literals = literals
		self.strings = strings

	def __set_name__(self, owner, name):
		owner.__descriptors__.append(self)
		owner.__styles__.append(name)
		self.attr = f'_{name}'

	def setup(self, _):
		raise NotImplementedError

class PropertyDescriptor(BaseDescriptor):
	def __get__(self, instance, _):
		if instance is None:
			return self

		attr: Property = getattr(instance, self.attr)
		return attr.raw

	def __set__(self, instance, raw):
		attr: Property = getattr(instance, self.attr)
		_parse(self, attr, raw)

	def setup(self, instance):
		attr = Property(None, None, None)
		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class AxialDescriptor(BaseDescriptor):
	def __get__(self, instance, _):
		if instance is None:
			return self

		attr: AxialProperty = getattr(instance, self.attr)
		return f'{attr[Axis.HORIZONTAL].raw} {attr[Axis.VERTICAL].raw}'

	def __set__(self, instance, raw):
		parts = raw.split()
		match len(parts):
			case 1: horizontal, vertical = parts[0], parts[0]
			case 2: horizontal, vertical = parts[0], parts[1]
			case _: raise ValueError(f'Axial property must have 1-2 values: {raw}')

		attr: AxialProperty = getattr(instance, self.attr)
		_parse(self, attr[Axis.HORIZONTAL], horizontal)
		_parse(self, attr[Axis.VERTICAL], vertical)

	def setup(self, instance):
		attr = {
			Axis.HORIZONTAL: Property(None, None, None),
			Axis.VERTICAL: Property(None, None, None)
		}

		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class DirectionalDescriptor(BaseDescriptor):
	def __get__(self, instance, _):
		if instance is None:
			return self

		attr: DirectionalProperty = getattr(instance, self.attr)
		return f'{attr[Direction.TOP].raw} {attr[Direction.RIGHT].raw} ' \
			 + f'{attr[Direction.BOTTOM].raw} {attr[Direction.LEFT].raw}'

	def __set__(self, instance, raw):
		parts = raw.split()
		match len(parts):
			case 1: top, right, bottom, left = parts[0], parts[0], parts[0], parts[0]
			case 2: top, right, bottom, left = parts[0], parts[1], parts[0], parts[1]
			case 3: top, right, bottom, left = parts[0], parts[1], parts[2], parts[1]
			case 4: top, right, bottom, left = parts[0], parts[1], parts[2], parts[3]
			case _: raise ValueError(f'Cardinal property must have 1-4 values: {raw}')

		attr: DirectionalProperty = getattr(instance, self.attr)
		_parse(self, attr[Direction.TOP], top)
		_parse(self, attr[Direction.RIGHT], right)
		_parse(self, attr[Direction.BOTTOM], bottom)
		_parse(self, attr[Direction.LEFT], left)

	def setup(self, instance):
		attr = {
			Direction.TOP: Property(None, None, None),
			Direction.RIGHT: Property(None, None, None),
			Direction.BOTTOM: Property(None, None, None),
			Direction.LEFT: Property(None, None, None)
		}

		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class SubDescriptor:
	def __init__(self, parent: BaseDescriptor, key: Axis | Direction):
		self.parent = parent
		self.key = key

	def __set_name__(self, owner, name):
		owner.__styles__.append(name)

	def __get__(self, instance, _):
		if instance is None:
			return self

		attr: AxialProperty | DirectionalProperty = getattr(instance, self.parent.attr)
		return attr[self.key].raw

	def __set__(self, instance, raw):
		attr: AxialProperty | DirectionalProperty = getattr(instance, self.parent.attr)
		_parse(self.parent, attr[self.key], raw)
