
from guwhy.layout import Node, Box
from guwhy.canvas import Canvas

W, H = 40, 20

root = Box(
    size = f'{W}px {H}px',
    borders = 'double single bold',
    children=[
        Node(
            size = '60%',
            borders = 'single',
            corners = 'round'
        ),
        Node(
            size = 'grow',
            borders = 'single',
        )
    ]
)

root.compute()
canvas = Canvas(W, H, root)

for y in range(H):
    print(''.join(canvas._pixel_buffer[y*W:(y+1)*W]))
