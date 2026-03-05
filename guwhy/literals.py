
# External libraries
from enum import Enum

# -----------------------------------> Node literals

class NodeVisibility(Enum):
	SHOW = 'show'
	HIDE = 'hide'
	NONE = 'none'

class NodePositioning(Enum):
	AUTO = 'auto'
	RELATIVE = 'relative'
	ABSOLUTE = 'absolute'

class NodeZIndex(Enum):
	Auto = 'auto'

class NodePosition(Enum):
	AUTO = 'auto'

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

class NodeOverflow(Enum):
	HIDE = 'hide'
	SHOW = 'show'

class NodeBackground(Enum):
	OPAQUE = 'opaque'
	TRANSPARENT = 'transparent'

class NodeMouseEvents(Enum):
	CAPTURE = 'capture'
	NONE = 'none'

# -----------------------------------> Box literals

class BoxPlaceChildren(Enum):
	START = 'start'
	CENTER = 'center'
	END = 'end'

class BoxChildGap(Enum):
	AUTO = 'auto'