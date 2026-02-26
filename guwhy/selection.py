
from __future__ import annotations

# External
from enum import Enum, auto
from typing import Callable

# Internal
from .nodes import *

# Types
type SelectionSet = set[Node]
type Operation = Callable[[SelectionSet], SelectionSet]

# -----------------------------------> Tokens

class TokenType(Enum):
	ANY = auto()
	ID = auto()
	CLASS = auto()
	CONTEXT = auto()
	CHILDREN = auto()
	PARENTS = auto()
	SIBLINGS = auto()
	PREV = auto()
	NEXT = auto()
	WHITESPACE = auto()
	KEY = auto()

class Token:
	__slots__ = 'type', 'raw', 'end'

	def __init__(self, type: TokenType, raw: str, end: int):
		self.type = type
		self.raw  = raw
		self.end  = end

# -----------------------------------> Operations

def _op_descendants(s: SelectionSet) -> SelectionSet:
	return {d for n in s if isinstance(n, Box) for d in n._descendants}

def _op_children(s: SelectionSet) -> SelectionSet:
	return {c for n in s if isinstance(n, Box) for c in n._children}

def _op_parents(s: SelectionSet) -> SelectionSet:
	return {n._parent for n in s if n._parent is not None}

def _op_siblings(s: SelectionSet) -> SelectionSet:
	return {sib for n in s if n._parent for sib in n._parent._children}

def _op_prev(s: SelectionSet) -> SelectionSet:
	return {n._prev for n in s if n._prev is not None}

def _op_next(s: SelectionSet) -> SelectionSet:
	return {n._next for n in s if n._next is not None}

def _op_first_child(s: SelectionSet) -> SelectionSet:
	return {n for n in s if n._prev is None}

def _op_last_child(s: SelectionSet) -> SelectionSet:
	return {n for n in s if n._next is None}

def _op_even(s: SelectionSet) -> SelectionSet:
	return {n for n in s if n._index % 2 == 0}

def _op_odd(s: SelectionSet) -> SelectionSet:
	return {n for n in s if n._index % 2 == 1}

def _op_with_id(id: str) -> Operation:
	return lambda s: {n for n in s if n._id == id}

def _op_with_class(cls: str) -> Operation:
	return lambda s: {n for n in s if cls in n._classlist}

def _op_type(t: type) -> Operation:
	return lambda s: {n for n in s if isinstance(n, t)}

# -----------------------------------> Lookup tables

_RESERVED = {
	'*': TokenType.ANY,
	'#': TokenType.ID,
	'.': TokenType.CLASS,
	':': TokenType.CONTEXT,
	'>': TokenType.CHILDREN,
	'<': TokenType.PARENTS,
	'~': TokenType.SIBLINGS,
	'-': TokenType.PREV,
	'+': TokenType.NEXT,
	' ': TokenType.WHITESPACE,
}

_TYPE_OPS = {
	'box': _op_type(Box),
	'text': _op_type(Text)
}

_CONTEXT_OPS = {
	'first': _op_first_child,
	'last': _op_last_child,
	'even': _op_even,
	'odd': _op_odd,
}

_EXPANDING_OPS = {
	TokenType.PARENTS: _op_parents,
	TokenType.CHILDREN: _op_children,
	TokenType.SIBLINGS: _op_siblings,
	TokenType.PREV: _op_prev,
	TokenType.NEXT: _op_next,
}

# -----------------------------------> Parser

class SelectorSyntaxError(Exception):
	def __init__(self, raw: str, token: Token, message: str):
		pointer = ' ' * (token.end - len(token.raw)) + '^' * len(token.raw)
		super().__init__(f'ParseError: {message}\n\n  {raw}\n  {pointer}')

class ParseState(Enum):
	NEUTRAL           = auto()
	NARROWING         = auto()
	EXPANDING         = auto()
	SECOND_WHITESPACE = auto()
	FIRST_WHITESPACE  = auto()
	EXPECT_ID         = auto()
	EXPECT_CLASS      = auto()
	EXPECT_CONTEXT    = auto()

_STATEMACHINE = {
	(TokenType.ANY,        ParseState.NEUTRAL):            ParseState.NARROWING,
	(TokenType.KEY,        ParseState.NEUTRAL):            ParseState.NARROWING,
	(TokenType.ID,         ParseState.NEUTRAL):            ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.NEUTRAL):            ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.NEUTRAL):            ParseState.EXPECT_CONTEXT,
	(TokenType.ID,         ParseState.NARROWING):          ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.NARROWING):          ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.NARROWING):          ParseState.EXPECT_CONTEXT,
	(TokenType.WHITESPACE, ParseState.NARROWING):          ParseState.FIRST_WHITESPACE,
	(TokenType.ANY,        ParseState.FIRST_WHITESPACE):   ParseState.NARROWING,
	(TokenType.ID,         ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_CONTEXT,
	(TokenType.PARENTS,    ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.CHILDREN,   ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.SIBLINGS,   ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.PREV,       ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.NEXT,       ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.KEY,        ParseState.FIRST_WHITESPACE):   ParseState.NARROWING,
	(TokenType.WHITESPACE, ParseState.EXPANDING):          ParseState.SECOND_WHITESPACE,
	(TokenType.ANY,        ParseState.SECOND_WHITESPACE):  ParseState.NARROWING,
	(TokenType.ID,         ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_CONTEXT,
	(TokenType.KEY,        ParseState.SECOND_WHITESPACE):  ParseState.NARROWING,
	(TokenType.KEY,        ParseState.EXPECT_ID):          ParseState.NARROWING,
	(TokenType.KEY,        ParseState.EXPECT_CLASS):       ParseState.NARROWING,
	(TokenType.KEY,        ParseState.EXPECT_CONTEXT):     ParseState.NARROWING,
}

def _tokenize(raw: str) -> list[Token]:
	collapse_whitespace = False
	raw = raw.strip()
	tokens = []
	token = ''

	for current, char in enumerate(raw):
		if char in _RESERVED:
			type = _RESERVED[char]
			if type == TokenType.WHITESPACE:
				if collapse_whitespace:
					continue
				collapse_whitespace = True

			else:
				collapse_whitespace = False

			if token:
				tokens.append(Token(TokenType.KEY, token, current))
				token = ''
			tokens.append(Token(type, char, current + 1))
			continue

		collapse_whitespace = False
		token += char

	if token:
		tokens.append(Token(TokenType.KEY, token, len(raw)))
	return tokens

def _parse(raw: str, tokens: list[Token]) -> list[Operation]:
	operations: list[Operation] = []
	state = ParseState.NEUTRAL
	token = None

	for token in tokens:
		key = token.type, state
		if key not in _STATEMACHINE:
			raise SelectorSyntaxError(raw, token, 'Unexpected token')

		if token.type in _EXPANDING_OPS:
			operations.append(_EXPANDING_OPS[token.type])

		else:
			if state == ParseState.FIRST_WHITESPACE:
				operations.append(_op_descendants)
			if state == ParseState.EXPECT_ID:
				operations.append(_op_with_id(token.raw))
			elif state == ParseState.EXPECT_CLASS:
				operations.append(_op_with_class(token.raw))
			elif state == ParseState.EXPECT_CONTEXT:
				if token.raw not in _CONTEXT_OPS:
					raise SelectorSyntaxError(raw, token, 'Unknown context')
				operations.append(_CONTEXT_OPS[token.raw])
			elif token.type == TokenType.KEY:
				if token.raw not in _TYPE_OPS:
					raise SelectorSyntaxError(raw, token, 'Unknown type')
				operations.append(_TYPE_OPS[token.raw])

		state = _STATEMACHINE[key]

	if state != ParseState.NARROWING:
		raise SelectorSyntaxError(raw, token, 'Unexpected EOL')
	return operations

# -----------------------------------> Selection

class Selection:
	selection: SelectionSet

	def __init__(self, nodes: list[Node]):
		self.selection = set(nodes)

	def applyStyles(self, **kwargs) -> Selection:
		for node in self.selection:
			node.applyStyles(**kwargs)
		return self

	def select(self, selector: str) -> Selection:
		tokens = _tokenize(selector)
		operations = _parse(selector, tokens)
		for op in operations:
			self.selection = op(self.selection)
		return self