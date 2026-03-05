
from guwhy.layout import Box, Node
from guwhy.canvas import Canvas

# -----------------------------------> Layout

W, H = 40, 20
canvas = Canvas(W, H)

root = Box(
    size = f'{W}px {H}px',
    border = 'double',
    place_children_along = 'center',
    place_children_across = 'center'
)

a = Box(
    size = '50%',
    border = 'single'
)

b = Node(
    size = 'grow',
    border = 'single'
)

a.setParent(root)
b.setParent(a)

# -----------------------------------> Run

root.compute()
print(root)

root.paint(canvas)
pixels, nodes = canvas.compress()
for y in range(H):
    print(''.join(pixels[y*W:(y+1)*W]))

""" TODO
box should accept child kwarg
node should accept parent kwarg
place_children_along/across should have an axial property place_children
improve canvas layers
    - support negative layers
    - prevent z=999 from creating 998 new layers
implement text
implement selection
implement grids
"""