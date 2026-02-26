
from enum import Enum

class NodePositioning(Enum):
	AUTO = 'auto'
	RELATIVE = 'relative'
	ABSOLUTE = 'absolute'

class NodePosition(Enum):
	AUTO = 'auto'

class NodeOverflow(Enum):
	HIDE = 'hide'
	SHOW = 'show'

class NodeSize(Enum):
	GROW = 'grow'
	FIT = 'fit'

class NodeMinSize(Enum):
	NONE = 'none'

class NodeMaxSize(Enum):
	NONE = 'none'

class NodeBorder(Enum):
	NONE = 'none'
	SINGLE = 'single'
	DOUBLE = 'double'

class NodePlaceSelf(Enum):
	INHERIT = 'inherit'
	START = 'start'
	CENTER = 'center'
	END = 'end'

class BoxPlaceContent(Enum):
	START = 'start'
	CENTER = 'center'
	END = 'end'

class BoxChildGap(Enum):
	AUTO = 'auto'

class TextWrap(Enum):
	NONE = 'none'
	CHAR = 'char'
	WORD = 'word'

class TextAlign(Enum):
	LEFT = 'left'
	CENTER = 'center'
	RIGHT = 'right'

class TextPlaceHorz(Enum):
	LEFT = 'left'
	CENTER = 'center'
	RIGHT = 'right'

class TextPlaceVert(Enum):
	TOP = 'top'
	CENTER = 'center'
	BOTTOM = 'bottom'