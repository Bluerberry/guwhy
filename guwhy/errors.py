
from typing import TYPE_CHECKING

# Internal libraries
if TYPE_CHECKING:
	from .selection import Token

# ─────────────────────────────────── Errors ───────────────────────────────────

class SelectorSyntaxError(Exception):

	@staticmethod
	def tokenError(raw: str, token: Token, message: str):
		pointer = ' ' * (token.end - len(token.raw)) + '^' * len(token.raw)
		return SelectorSyntaxError(f'{message}\n\n  {raw}\n  {pointer}')
