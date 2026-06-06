
from __future__ import annotations

# External
from typing import Callable, Literal, Iterable

# Internal
from .layout import *

# Types
type NodeStream = Generator[Node, None, None]
type Operation = Callable[[NodeStream], NodeStream]
type TokenType = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
type ParseState = Literal[0, 1, 2, 3, 4, 5, 6, 7]

# ─────────────────────────────────── Utility ───────────────────────────────────

def _createStream[T](source: Iterable[T]) -> Generator[T, None, None]:
	yield from source

# ─────────────────────────────────── Operations ───────────────────────────────────

def _selectChildren(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if isinstance(node, Parent):
			yield from node.children

def _selectDescendants(upstream: NodeStream) -> NodeStream:
	visited = set[int]()
	for node in upstream:
		if not isinstance(node, Box):
			continue

		for descendant in node.descendants:
			if (ID := id(descendant)) in visited:
				continue

			visited.add(ID)
			yield descendant

def _selectParents(upstream: NodeStream) -> NodeStream:
	visited = set[int]()
	for node in upstream:
		if node.parent is None:
			continue

		if (ID := id(node.parent)) in visited:
			continue

		visited.add(ID)
		yield node.parent

def _selectSiblings(upstream: NodeStream) -> NodeStream:
	visited = set[int]()
	for node in upstream:
		if node.parent is None:
			continue

		for sibling in node.parent.children:
			if (ID := id(sibling)) in visited:
				continue

			visited.add(ID)
			yield sibling

def _selectPrev(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.prev is not None:
			yield node.prev

def _selectNext(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.next is not None:
			yield node.next

def _selectFirstChild(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.prev is None:
			yield node

def _selectLastChild(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.next is None:
			yield node

def _selectEvenChildren(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.index is not None and node.index % 2 == 0:
			yield node

def _selectOddChildren(upstream: NodeStream) -> NodeStream:
	for node in upstream:
		if node.index is not None and node.index % 2 == 1:
			yield node

def _selectWithId(upstream: NodeStream, _id: str) -> NodeStream:
	for node in upstream:
		if node.id == _id:
			yield node
			break

def _selectWithClass(upstream: NodeStream, _class: str) -> NodeStream:
	for node in upstream:
		if _class in node.classlist:
			yield node

def _selectWithType(_type: type) -> Operation:
	def operation(upstream: NodeStream) -> NodeStream:
		for node in upstream:
			if type(node) == _type:
				yield node

	return operation

# ─────────────────────────────────── Maps & constants ───────────────────────────────────

_KEY_TOKEN		  = 0
_ANY_TOKEN		  = 1
_ID_TOKEN		  = 2
_CLASS_TOKEN	  = 3
_CONTEXT_TOKEN	  = 4
_CHILDREN_TOKEN	  = 5
_PARENTS_TOKEN	  = 6
_SIBLINGS_TOKEN	  = 7
_PREV_TOKEN		  = 8
_NEXT_TOKEN		  = 9
_THIS_TOKEN		  = 10
_WHITESPACE_TOKEN = 11

_INITIAL_STATE           = 0	# The first state of our statemachine
_NARROWING_STATE         = 1	# When applying type, context, class, or ID operations
_EXPANDING_STATE         = 2	# When applying parents, children, siblings, prev, or next operations
_FIRST_WHITESPACE_STATE  = 3	# Optional after narrowing, followed by expanding
_SECOND_WHITESPACE_STATE = 4	# Required after expanding, followed by narrowing
_EXPECT_ID_STATE         = 5	# Awaiting id after `#`
_EXPECT_CLASS_STATE      = 6	# Awaiting class after `.`
_EXPECT_CONTEXT_STATE    = 7	# Awaiting context after `:`

_RESERVED: dict[str, TokenType] = {
	'*': _ANY_TOKEN,
	'&': _THIS_TOKEN,
	'#': _ID_TOKEN,
	'.': _CLASS_TOKEN,
	':': _CONTEXT_TOKEN,
	'>': _CHILDREN_TOKEN,
	'<': _PARENTS_TOKEN,
	'~': _SIBLINGS_TOKEN,
	'-': _PREV_TOKEN,
	'+': _NEXT_TOKEN,
	' ': _WHITESPACE_TOKEN
}

_TYPE_OPS: dict[str, Operation] = {
	'node': _selectWithType(Node),
	'box': _selectWithType(Box)
}

_CONTEXT_OPS: dict[str, Operation] = {
	'first': _selectFirstChild,
	'last': _selectLastChild,
	'even': _selectEvenChildren,
	'odd': _selectOddChildren,
}

_EXPANDING_OPS: dict[TokenType, Operation] = {
	_PARENTS_TOKEN: _selectParents,
	_CHILDREN_TOKEN: _selectChildren,
	_SIBLINGS_TOKEN: _selectSiblings,
	_PREV_TOKEN: _selectPrev,
	_NEXT_TOKEN: _selectNext
}

_STATEMACHINE: dict[tuple[TokenType, ParseState], ParseState] = {
	(_ANY_TOKEN,        _INITIAL_STATE):            _NARROWING_STATE,
	(_KEY_TOKEN,        _INITIAL_STATE):            _NARROWING_STATE,
	(_THIS_TOKEN,       _INITIAL_STATE):            _NARROWING_STATE,
	(_ID_TOKEN,         _INITIAL_STATE):            _EXPECT_ID_STATE,
	(_CLASS_TOKEN,      _INITIAL_STATE):            _EXPECT_CLASS_STATE,
	(_CONTEXT_TOKEN,    _INITIAL_STATE):            _EXPECT_CONTEXT_STATE,
	(_ID_TOKEN,         _NARROWING_STATE):          _EXPECT_ID_STATE,
	(_CLASS_TOKEN,      _NARROWING_STATE):          _EXPECT_CLASS_STATE,
	(_CONTEXT_TOKEN,    _NARROWING_STATE):          _EXPECT_CONTEXT_STATE,
	(_WHITESPACE_TOKEN, _NARROWING_STATE):          _FIRST_WHITESPACE_STATE,
	(_ANY_TOKEN,        _FIRST_WHITESPACE_STATE):   _NARROWING_STATE,
	(_KEY_TOKEN,        _FIRST_WHITESPACE_STATE):   _NARROWING_STATE,
	(_THIS_TOKEN,       _FIRST_WHITESPACE_STATE):   _NARROWING_STATE,
	(_ID_TOKEN,         _FIRST_WHITESPACE_STATE):   _EXPECT_ID_STATE,
	(_CLASS_TOKEN,      _FIRST_WHITESPACE_STATE):   _EXPECT_CLASS_STATE,
	(_CONTEXT_TOKEN,    _FIRST_WHITESPACE_STATE):   _EXPECT_CONTEXT_STATE,
	(_PARENTS_TOKEN,    _FIRST_WHITESPACE_STATE):   _EXPANDING_STATE,
	(_CHILDREN_TOKEN,   _FIRST_WHITESPACE_STATE):   _EXPANDING_STATE,
	(_SIBLINGS_TOKEN,   _FIRST_WHITESPACE_STATE):   _EXPANDING_STATE,
	(_PREV_TOKEN,       _FIRST_WHITESPACE_STATE):   _EXPANDING_STATE,
	(_NEXT_TOKEN,       _FIRST_WHITESPACE_STATE):   _EXPANDING_STATE,
	(_WHITESPACE_TOKEN, _EXPANDING_STATE):          _SECOND_WHITESPACE_STATE,
	(_ANY_TOKEN,        _SECOND_WHITESPACE_STATE):  _NARROWING_STATE,
	(_KEY_TOKEN,        _SECOND_WHITESPACE_STATE):  _NARROWING_STATE,
	(_THIS_TOKEN,       _SECOND_WHITESPACE_STATE):  _NARROWING_STATE,
	(_ID_TOKEN,         _SECOND_WHITESPACE_STATE):  _EXPECT_ID_STATE,
	(_CLASS_TOKEN,      _SECOND_WHITESPACE_STATE):  _EXPECT_CLASS_STATE,
	(_CONTEXT_TOKEN,    _SECOND_WHITESPACE_STATE):  _EXPECT_CONTEXT_STATE,
	(_KEY_TOKEN,        _EXPECT_ID_STATE):          _NARROWING_STATE,
	(_KEY_TOKEN,        _EXPECT_CLASS_STATE):       _NARROWING_STATE,
	(_KEY_TOKEN,        _EXPECT_CONTEXT_STATE):     _NARROWING_STATE,
}

# ─────────────────────────────────── Parser ───────────────────────────────────

class SelectorSyntaxError(Exception):

	@staticmethod
	def tokenError(raw: str, token: Token, message: str):
		pointer = ' ' * (token.end - len(token.raw)) + '^' * len(token.raw)
		return SelectorSyntaxError(f'{message}\n\n  {raw}\n  {pointer}')

class Token:
	__slots__ = 'token_type', 'raw', 'end'

	token_type: TokenType
	raw: str
	end: int

	def __init__(self, token_type: TokenType, raw: str, end: int):
		self.token_type = token_type
		self.raw = raw
		self.end = end

def _tokenize(selector: str) -> list[Token]:
	collapse_whitespace: bool = False
	tokens: list[Token] = []
	token: str = ''

	selector = selector.strip()
	for column, char in enumerate(selector):
		if char in _RESERVED:
			token_type = _RESERVED[char]
			if token_type == _WHITESPACE_TOKEN:
				if collapse_whitespace:
					continue
				collapse_whitespace = True

			else:
				collapse_whitespace = False

			if token:
				tokens.append(Token(_KEY_TOKEN, token, column))
				token = ''

			tokens.append(Token(token_type, char, column + 1))
			continue

		collapse_whitespace = False
		token += char

	if token:
		tokens.append(Token(_KEY_TOKEN, token, len(selector)))
	return tokens

def _parse(selector: str, tokens: list[Token], stream: NodeStream) -> NodeStream:
	state: ParseState = _INITIAL_STATE
	token: Token | None = None

	for token in tokens:
		key = token.token_type, state
		if key not in _STATEMACHINE:
			raise SelectorSyntaxError.tokenError(selector, token, 'Unexpected token')

		if token.token_type in _EXPANDING_OPS:
			stream = _EXPANDING_OPS[token.token_type](stream)
		elif state == _FIRST_WHITESPACE_STATE:
			stream = _selectDescendants(stream)
		elif state == _EXPECT_ID_STATE:
			stream = _selectWithId(stream, token.raw)
		elif state == _EXPECT_CLASS_STATE:
			stream = _selectWithClass(stream, token.raw)
		elif state == _EXPECT_CONTEXT_STATE:
			if token.raw not in _CONTEXT_OPS:
				raise SelectorSyntaxError.tokenError(selector, token, 'Unknown context')
			stream = _CONTEXT_OPS[token.raw](stream)
		elif token.token_type == _KEY_TOKEN:
			if token.raw not in _TYPE_OPS:
				raise SelectorSyntaxError.tokenError(selector, token, 'Unknown type')
			stream = _TYPE_OPS[token.raw](stream)

		state = _STATEMACHINE[key]

	if token is None:
		raise SelectorSyntaxError('Empty selector')
	if state != _NARROWING_STATE:
		raise SelectorSyntaxError.tokenError(selector, token, 'Unexpected EOL')

	return stream

# ─────────────────────────────────── Selection ───────────────────────────────────

class Selection:
	_stream: NodeStream

	def __init__(self, stream: NodeStream):
		self._stream = stream

	# ──── Public

	@staticmethod
	def using(root: Node, selector: str) -> Selection:
		nodes = [root]
		if isinstance(root, Parent):
			nodes.extend(root.descendants)

		tokens = _tokenize(selector)
		stream = _createStream(nodes)
		return Selection(_parse(selector, tokens, stream))

	def select(self, selector: str) -> Selection:
		tokens = _tokenize(selector)
		return Selection(_parse(selector, tokens, self._stream))

	def filter(self, selector: str) -> Selection:
		tokens = _tokenize(selector)
		self._stream = _parse(selector, tokens, self._stream)
		return self

	def apply(self, **kwargs: str) -> Selection:
		for node in self._stream:
			node.apply(**kwargs)
		return self