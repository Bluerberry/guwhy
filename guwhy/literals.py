
# External libraries
from enum import Enum

# ─────────────────────────────────── Node ───────────────────────────────────

class NodeVisibility(Enum):
	SHOW = 'show'
	HIDE = 'hide'
	NONE = 'none'

class NodePositioning(Enum):
	AUTO = 'auto'
	RELATIVE = 'relative'
	ABSOLUTE = 'absolute'

class NodeZIndex(Enum):
	AUTO = 'auto'

class NodeOrigin(Enum):
	AUTO = 'auto'

class NodeSize(Enum):
	FIT = 'fit'
	GROW = 'grow'
	SHRINK = 'shrink'

class NodeMinSize(Enum):
	NONE = 'none'

class NodeMaxSize(Enum):
	NONE = 'none'

class NodeBorders(Enum):
	NONE = 'none'
	SINGLE = 'single'
	DOUBLE = 'double'
	BOLD = 'bold'

class NodeCorners(Enum):
	SHARP = 'sharp'
	ROUND = 'round'

class NodeOverflow(Enum):
	HIDE = 'hide'
	SHOW = 'show'

class NodePlaceSelfAcross(Enum):
	INHERIT = 'inherit'
	START = 'start'
	CENTER = 'center'
	END = 'end'

class NodeBackground(Enum):
	OPAQUE = 'opaque'
	TRANSPARENT = 'transparent'

class NodeMouseEvents(Enum):
	CAPTURE = 'capture'
	NONE = 'none'

# ─────────────────────────────────── Box ───────────────────────────────────

class BoxAxis(Enum):
	HORIZONTAL = 'horizontal'
	VERTICAL = 'vertical'

class BoxPlaceChildren(Enum):
	START = 'start'
	CENTER = 'center'
	END = 'end'

class BoxChildGap(Enum):
	AUTO = 'auto'

# ─────────────────────────────────── Text ───────────────────────────────────

class TextWrapText(Enum):
	NONE = 'none'
	CHAR = 'none'
	WORD = 'word'

class TextAlignText(Enum):
	LEFT = 'left'
	CENTER = 'center'
	RIGHT = 'right'
	JUSTIFY = 'justify'

class TextPlaceTextX(Enum):
	LEFT = 'left'
	CENTER = 'center'
	RIGHT= 'right'

class TextPlaceTextY(Enum):
	TOP = 'top'
	CENTER = 'center'
	BOTTOM = 'bottom'

# ─────────────────────────────────── Grid ───────────────────────────────────

class GridLayout(Enum):
	AUTO = 'auto'

class GridPlaceChildrenH(Enum):
	LEFT = 'left'
	CENTER = 'center'
	RIGHT = 'right'

class GridPlaceChildrenV(Enum):
	TOP = 'top'
	CENTER = 'center'
	BOTTOM = 'bottom'

class GridChildGap(Enum):
	AUTO = 'auto'
	SINGLE = 'single'
	DOUBLE = 'double'
	BOLD = 'bold'

class GridColumnWidths(Enum):
	FIT = 'fit'
	GROW = 'grow'

class GridRowHeights(Enum):
	FIT = 'fit'
	GROW = 'grow'
