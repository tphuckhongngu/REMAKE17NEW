"""
maps/mainmap.py

Redesigned main map per request:
- Only uses tiles: 'tuong' (walls), 'betong' (concrete), 'nuoc' (water).
- Player spawns near map center; central area kept open.
- Four corners (near (1,1),(cols-2,1),(1,rows-2),(cols-2,rows-2)) are left open for teleport gates
  with a small clear area around them so monsters won't be trapped.
- Interior wall blocks are placed as isolated rectangles (not forming narrow corridors)
  to avoid Monster2 getting stuck.
"""

B = "betong"
W = "nuoc"
T = "tuong"

WIDTH = 40
HEIGHT = 25

MAP_LAYOUT = []

# define corner gate cells that must be clear
corner_cells = [(1, 1), (WIDTH - 2, 1), (1, HEIGHT - 2), (WIDTH - 2, HEIGHT - 2)]

# interior wall blocks (x, y, w, h) -- isolated rectangles
blocks = [
    (6, 3, 4, 3),
    (28, 3, 4, 3),
    (6, 14, 4, 3),
    (28, 14, 4, 3),
]

for y in range(HEIGHT):
    row = []
    for x in range(WIDTH):
        # outer border walls
        if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
            row.append(T)
            continue

        # ensure gate corners and their immediate 3x3 neighborhood are clear (decor tiles)
        clear_for_gate = False
        for (gx, gy) in corner_cells:
            if abs(x - gx) <= 1 and abs(y - gy) <= 1:
                clear_for_gate = True
                break
        if clear_for_gate:
            # decorative concrete near gate
            row.append(B)
            continue

        # keep a generous open central arena to avoid trapping big monsters
        if 12 <= x <= 27 and 7 <= y <= 17:
            # a few water accents but mostly concrete
            if (x + y) % 7 == 0:
                row.append(W)
            else:
                row.append(B)
            continue

        # interior isolated wall blocks
        in_block = False
        for bx, by, bw, bh in blocks:
            if bx <= x < bx + bw and by <= y < by + bh:
                row.append(T)
                in_block = True
                break
        if in_block:
            continue

        # light decoration elsewhere: mostly concrete with occasional water
        if (x * y) % 13 == 0:
            row.append(W)
        else:
            row.append(B)

    MAP_LAYOUT.append(row)

MAP_ROWS = len(MAP_LAYOUT)
