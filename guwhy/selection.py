
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
	THIS = auto()
	WHITESPACE = auto()
	KEY = auto()

class Token:
	__slots__ = 'token_type', 'raw', 'end'

	def __init__(self, token_type: TokenType, raw: str, end: int):
		self.token_type = token_type
		self.raw = raw
		self.end = end

# -----------------------------------> Operations

def _selectDescendants(selection: SelectionSet) -> SelectionSet:
	return {
		descendant
		for node in selection
		if isinstance(node, Box)
		for descendant in node._descendants
	}

def _selectChildren(selection: SelectionSet) -> SelectionSet:
	return {
		child
		for node in selection
		if isinstance(node, Box)
		for child in node._children
	}

def _selectParents(selection: SelectionSet) -> SelectionSet:
	return {
		node._parent
		for node in selection
		if node._parent is not None
	}

def _selectSiblings(selection: SelectionSet) -> SelectionSet:
	return {
		sibling
		for node in selection
		if node._parent
		for sibling in node._parent._children
	}

def _selectPrev(selection: SelectionSet) -> SelectionSet:
	return {
		node._prev
		for node in selection
		if node._prev is not None
	}

def _selectNext(selection: SelectionSet) -> SelectionSet:
	return {
		node._next
		for node in selection
		if node._next is not None
	}

def _selectThis(selection: SelectionSet) -> SelectionSet:
	return selection

def _selectFirstChild(selection: SelectionSet) -> SelectionSet:
	return {
		node
		for node in selection
		if node._prev is None
	}

def _selectLastChild(selection: SelectionSet) -> SelectionSet:
	return {
		node
		for node in selection
		if node._next is None
	}

def _selectEvenChildren(selection: SelectionSet) -> SelectionSet:
	return {
		node
		for node in selection
		if node._index % 2 == 0
	}

def _selectOddChildren(selection: SelectionSet) -> SelectionSet:
	return {
		node
		for node in selection
		if node._index % 2 == 1
	}

def _selectWithId(id: str) -> Operation:
	return lambda selection: {
		node
		for node in selection
		if node.id == id
	}

def _selectWithClass(cls: str) -> Operation:
	return lambda selection: {
		node
		for node in selection
		if cls in node.classlist
	}

def _selectWithType(type: type) -> Operation:
	return lambda selection: {
		node
		for node in selection
		if isinstance(node, type)
	}

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
	'&': TokenType.THIS,
	' ': TokenType.WHITESPACE,
}

_TYPE_OPS = {
	'box': _selectWithType(Box),
	'text': _selectWithType(Text)
}

_CONTEXT_OPS = {
	'first': _selectFirstChild,
	'last': _selectLastChild,
	'even': _selectEvenChildren,
	'odd': _selectOddChildren,
}

_EXPANDING_OPS = {
	TokenType.PARENTS: _selectParents,
	TokenType.CHILDREN: _selectChildren,
	TokenType.SIBLINGS: _selectSiblings,
	TokenType.PREV: _selectPrev,
	TokenType.NEXT: _selectNext,
	TokenType.THIS: _selectThis,
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
	(TokenType.THIS,       ParseState.NEUTRAL):            ParseState.NARROWING,
	(TokenType.ID,         ParseState.NEUTRAL):            ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.NEUTRAL):            ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.NEUTRAL):            ParseState.EXPECT_CONTEXT,
	(TokenType.ID,         ParseState.NARROWING):          ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.NARROWING):          ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.NARROWING):          ParseState.EXPECT_CONTEXT,
	(TokenType.WHITESPACE, ParseState.NARROWING):          ParseState.FIRST_WHITESPACE,
	(TokenType.ANY,        ParseState.FIRST_WHITESPACE):   ParseState.NARROWING,
	(TokenType.KEY,        ParseState.FIRST_WHITESPACE):   ParseState.NARROWING,
	(TokenType.THIS,       ParseState.FIRST_WHITESPACE):   ParseState.NARROWING,
	(TokenType.ID,         ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.FIRST_WHITESPACE):   ParseState.EXPECT_CONTEXT,
	(TokenType.PARENTS,    ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.CHILDREN,   ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.SIBLINGS,   ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.PREV,       ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.NEXT,       ParseState.FIRST_WHITESPACE):   ParseState.EXPANDING,
	(TokenType.WHITESPACE, ParseState.EXPANDING):          ParseState.SECOND_WHITESPACE,
	(TokenType.ANY,        ParseState.SECOND_WHITESPACE):  ParseState.NARROWING,
	(TokenType.KEY,        ParseState.SECOND_WHITESPACE):  ParseState.NARROWING,
	(TokenType.THIS,       ParseState.SECOND_WHITESPACE):  ParseState.NARROWING,
	(TokenType.ID,         ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_ID,
	(TokenType.CLASS,      ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_CLASS,
	(TokenType.CONTEXT,    ParseState.SECOND_WHITESPACE):  ParseState.EXPECT_CONTEXT,
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
			token_type = _RESERVED[char]
			if token_type == TokenType.WHITESPACE:
				if collapse_whitespace:
					continue
				collapse_whitespace = True

			else:
				collapse_whitespace = False

			if token:
				tokens.append(Token(TokenType.KEY, token, current))
				token = ''
			tokens.append(Token(token_type, char, current + 1))
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
		key = token.token_type, state
		if key not in _STATEMACHINE:
			raise SelectorSyntaxError(raw, token, 'Unexpected token')

		if token.token_type in _EXPANDING_OPS:
			operations.append(_EXPANDING_OPS[token.token_type])

		else:
			if state == ParseState.FIRST_WHITESPACE:
				operations.append(_selectDescendants)
			if state == ParseState.EXPECT_ID:
				operations.append(_selectWithId(token.raw))
			elif state == ParseState.EXPECT_CLASS:
				operations.append(_selectWithClass(token.raw))
			elif state == ParseState.EXPECT_CONTEXT:
				if token.raw not in _CONTEXT_OPS:
					raise SelectorSyntaxError(raw, token, 'Unknown context')
				operations.append(_CONTEXT_OPS[token.raw])
			elif token.token_type == TokenType.KEY:
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
