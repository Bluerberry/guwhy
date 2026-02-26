
from __future__ import annotations

import re
from typing import Any, Literal, Optional

# Types
type Axis = Literal['horizontal', 'vertical']
type AxialProperty = dict[Axis, Property]
type AxialInteger = dict[Axis, int]

type Direction = Literal['top', 'right', 'bottom', 'left']
type CardinalProperty = dict[Direction, Property]
type CardinalAnything = dict[Direction, Any]

# Regex
MATCH_PIXELS = re.compile(r'^([0-9]+)px$')
MATCH_PERCENTAGES = re.compile(r'^(-?[0-9]+(?:\.[0-9]+)?)%$')
MATCH_SQUARES = re.compile(r'^([0-9]+)sq$')
MATCH_DIMENSIONLESS = re.compile(r'^([0-9]+)$')

# -----------------------------------> Property

class Property:
	__slots__ = 'raw', 'type', 'value', 'computed'

	def __init__(self, raw, type, value):
		self.raw = raw
		self.type = type
		self.value = value
		self.computed = None

	def __repr__(self) -> str:
		return f'Property({self.raw}, computed={self.computed})'
	
	def computeStatic(self, axis: Axis, default: Any = 0):
		if self.type in ('string', 'pixel', 'dimensionless'):
			self.computed = self.value

		elif self.type == 'square':
			self.computed = self.value
			if axis == 'horizontal':
				self.computed *= 2
		
		else:
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
	elif descriptor.pixels and (m := MATCH_PIXELS.match(raw)):
		hit = _PROPERTY_CACHE[key] = { 'type': 'pixel', 'value': int(m.group(1)) }
	elif descriptor.squares and (m := MATCH_SQUARES.match(raw)):
		hit = _PROPERTY_CACHE[key] = { 'type': 'square', 'value': int(m.group(1)) }
	elif descriptor.percentages and (m := MATCH_PERCENTAGES.match(raw)):
		hit = _PROPERTY_CACHE[key] = { 'type': 'percentage', 'value': float(m.group(1)) }
	elif descriptor.dimensionless and (m := MATCH_DIMENSIONLESS.match(raw)):
		hit = _PROPERTY_CACHE[key] = { 'type': 'dimensionless', 'value': int(m.group(1)) }
	elif descriptor.literals and raw in descriptor.literals:
		hit = _PROPERTY_CACHE[key] = { 'type': 'literal', 'value': raw }
	elif descriptor.strings:
		hit = _PROPERTY_CACHE[key] = { 'type': 'string', 'value': raw }
	else:
		raise ValueError(f'Unsupported property: {raw}')

	property.raw = raw
	property.type = hit['type']
	property.value = hit['value']
	property.computed = None

# -----------------------------------> Descriptors

class BaseDescriptor:
	_ANNOTATION_TYPE: type

	def __init__(self, default: str, *,
		strings: bool = False,
		pixels: bool = False,
		squares: bool = False,
		percentages: bool = False,
		dimensionless: bool = False,
		literals: Optional[tuple[str]] = None
	):
		self.default = default
		self.pixels = pixels
		self.squares = squares
		self.percentages = percentages
		self.dimensionless = dimensionless
		self.literals = literals
		self.strings = strings

	def __set_name__(self, owner, name):
		self.attr = f'_{name}'

		# Register descriptor (for setup later)
		if not hasattr(owner, '__descriptors__'):
			owner.__descriptors__ = []
		owner.__descriptors__.append(self)

	def setup(self, instance):
		raise NotImplementedError

class PropertyDescriptor(BaseDescriptor):
	def __get__(self, instance, owner):
		if instance is None:
			return self
		attr: Property = getattr(instance, self.attr)
		return attr.raw

	def __set__(self, instance, raw: str):
		attr: Property = getattr(instance, self.attr)
		_parse(self, attr, raw)
	
	def setup(self, instance):
		attr = Property(None, None, None)
		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class AxialDescriptor(BaseDescriptor):
	def __get__(self, instance, owner):
		if instance is None:
			return self
		attr: AxialProperty = getattr(instance, self.attr)
		return f'{attr['horizontal'].raw} {attr['vertical'].raw}'

	def __set__(self, instance, raw: str):
		parts = raw.split()
		match len(parts):
			case 1: horizontal, vertical = parts[0], parts[0]
			case 2: horizontal, vertical = parts[0], parts[1]
			case _: raise ValueError(f'Axial property must have 1-2 values: {raw}')

		attr: AxialProperty = getattr(instance, self.attr)
		_parse(self, attr['horizontal'], horizontal)
		_parse(self, attr['vertical'], vertical)
	
	def setup(self, instance):
		attr = {
			'horizontal': Property(None, None, None),
			'vertical': Property(None, None, None)
		}

		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class CardinalDescriptor(BaseDescriptor):
	def __get__(self, instance, owner):
		if instance is None:
			return self
		attr: CardinalProperty = getattr(instance, self.attr)
		return f'{attr['top'].raw} {attr['right'].raw} {attr['bottom'].raw} {attr['left'].raw}'

	def __set__(self, instance, raw: str):
		parts = raw.split()
		match len(parts):
			case 1: top, right, bottom, left = parts[0], parts[0], parts[0], parts[0]
			case 2: top, right, bottom, left = parts[0], parts[1], parts[0], parts[1]
			case 3: top, right, bottom, left = parts[0], parts[1], parts[2], parts[1]
			case 4: top, right, bottom, left = parts[0], parts[1], parts[2], parts[3]
			case _: raise ValueError(f'Cardinal property must have 1-4 values: {raw}')

		attr: CardinalProperty = getattr(instance, self.attr)
		_parse(self, attr['top'], top)
		_parse(self, attr['right'], right)
		_parse(self, attr['bottom'], bottom)
		_parse(self, attr['left'], left)

	def setup(self, instance):
		attr = {
			'top': Property(None, None, None),
			'right': Property(None, None, None),
			'bottom': Property(None, None, None),
			'left': Property(None, None, None)
		}

		setattr(instance, self.attr, attr)
		self.__set__(instance, self.default)

class SubDescriptor:
	def __init__(self, parent: BaseDescriptor, key: Axis | Direction):
		self.parent = parent
		self.key = key

	def __get__(self, instance, owner):
		if instance is None:
			return self
		attr: AxialProperty | CardinalProperty = getattr(instance, self.parent.attr)
		return attr[self.key].raw

	def __set__(self, instance, raw: str):
		attr: AxialProperty | CardinalProperty = getattr(instance, self.parent.attr)
		_parse(self.parent, attr[self.key], raw)
