
from __future__ import annotations

# Internal libraries
from guwhy.literals import *

# ─────────────────────────────────── Text wrap ───────────────────────────────────

def minTextWidth(lines: list[str], wrap: TextWrapText) -> int:
	match wrap:
		case TextWrapText.NONE:
			return max(map(len, lines))
		case TextWrapText.CHAR:
			return 1 if any(lines) else 0
		case TextWrapText.WORD:
			words: list[str] = []
			for line in lines:
				words += line.split()
			return max(map(len, words))

def minTextHeight(lines: list[str], wrap: TextWrapText) -> int:
	return len(lines)

def formatText(lines: list[str], wrap: TextWrapText, align: TextAlignText, max_width: int) -> list[str]:
	match wrap:
		case TextWrapText.NONE:
			wrapped = _collapseWhitespace(lines)
		case TextWrapText.CHAR:
			wrapped = _wrapChar(lines, max_width)
		case TextWrapText.WORD:
			wrapped = _wrapWord(lines, max_width)

	width = max(map(len, wrapped), default=0)

	match align:
		case TextAlignText.LEFT:
			return [line.ljust(width) for line in wrapped]
		case TextAlignText.CENTER:
			return [line.center(width) for line in wrapped]
		case TextAlignText.RIGHT:
			return [line.rjust(width) for line in wrapped]
		case TextAlignText.JUSTIFY:
			return _justify(wrapped, max_width, justify_last=False)

def _collapseWhitespace(lines: list[str]) -> list[str]:
    return [' '.join(line.split()) for line in lines]

def _wrapChar(lines: list[str], max_width: int) -> list[str]:
	result: list[str] = []

	for line in lines:
		length = len(line)
		if length <= max_width:
			result.append(line)
			continue

		for start in range(0, length, max_width):
			result.append(line[start:start + max_width])

	return result

def _wrapWord(lines: list[str], max_width: int) -> list[str]:
	result: list[str] = []

	for line in lines:
		words = line.split()
		if not words:
			result.append('')
			continue

		current: list[str] = []
		current_length = 0

		for word in words:
			word_length = len(word)
			if current_length == 0:
				current.append(word)
				current_length = word_length

			elif current_length + 1 + word_length <= max_width:
				current.append(word)
				current_length += 1 + word_length

			else:
				result.append(' '.join(current))
				current = [word]
				current_length = word_length

		if current:
			result.append(' '.join(current))

	return result

def _justify(lines: list[str], width: int, *, justify_last: bool = False):
	result: list[str] = []
	lines_length = len(lines)

	for i, line in enumerate(lines):
		is_last = i == lines_length - 1 or not lines[i + 1].strip()
		if is_last and not justify_last:
			result.append(line.ljust(width))
			continue

		words = line.split()
		words_length = len(words)

		if words_length <= 1:
			result.append(line.ljust(width))
			continue

		remaining = width - sum(map(len, words))
		gaps = words_length - 1
		base, extra = divmod(remaining,	gaps)

		line = words[0]
		for i in range(gaps):
			gap = base
			if i < extra:
				gap += 1

			line += ' ' * gap + words[i + 1]
		result.append(line)

	return result