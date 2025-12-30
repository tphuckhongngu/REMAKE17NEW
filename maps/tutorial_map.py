# maps/tutorial_map.py

# Các khoá tên tile
C = "co"
D = "dat"
B = "betong"
W = "nuoc"
T = "tuong"
TH = "betong"

WIDTH = 40
HEIGHT = 25

# Base layout: grass with outer wall
MAP_LAYOUT = [[C for x in range(WIDTH)] for y in range(HEIGHT)]
for y in range(HEIGHT):
    for x in range(WIDTH):
        if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
            MAP_LAYOUT[y][x] = T
        elif x == 1 or y == 1 or x == WIDTH - 2 or y == HEIGHT - 2:
            MAP_LAYOUT[y][x] = C

# Build a smaller enclosed training arena in the center (~1/3 size)
enc_w = max(6, int(WIDTH * 0.33))
enc_h = max(6, int(HEIGHT * 0.33))
enc_x = (WIDTH - enc_w) // 2
enc_y = (HEIGHT - enc_h) // 2

# enclosure walls (tuong) around the central arena
ENCLOSURE_WALLS = []
for y in range(enc_y, enc_y + enc_h):
    for x in range(enc_x, enc_x + enc_w):
        # border -> wall
        if x == enc_x or y == enc_y or x == enc_x + enc_w - 1 or y == enc_y + enc_h - 1:
            MAP_LAYOUT[y][x] = T
            ENCLOSURE_WALLS.append((x, y))

# Define a small gate on the right side of enclosure (initially closed)
GATE_CELLS = []
gate_y = enc_y + enc_h // 2
gate_x = enc_x + enc_w - 1
# make a 2-tile high gate
for dy in (-1, 0):
    gy = gate_y + dy
    gx = gate_x
    if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
        GATE_CELLS.append((gx, gy))
        MAP_LAYOUT[gy][gx] = T

# Enemy spawn points: list all interior cells inside the enclosure (excluding walls)
TRAINING_SPAWNS = []
for y in range(enc_y + 1, enc_y + enc_h - 1):
    for x in range(enc_x + 1, enc_x + enc_w - 1):
        # skip the NPC spawn area if it falls inside
        if (x, y) == (6, 5) or (x, y) == (7, 5):
            continue
        TRAINING_SPAWNS.append((x, y))

# Some crates inside enclosure for cover
crate_positions = [
    (enc_x + 3, enc_y + 2), (enc_x + 4, enc_y + 2),
    (enc_x + 6, enc_y + 4),
]
for cx, cy in crate_positions:
    if 0 <= cy < HEIGHT and 0 <= cx < WIDTH:
        MAP_LAYOUT[cy][cx] = TH

MAP_ROWS = len(MAP_LAYOUT)

# Ensure NPC spawn (and the tile to its right where the player spawns) are clear
# NPC expected at (6,5) by main.py; free (6,5) and (7,5) so NPC/player are not blocked by enclosure.
NPC_SPAWN = (6, 5)
px, py = NPC_SPAWN
if 0 <= py < HEIGHT and 0 <= px < WIDTH:
    MAP_LAYOUT[py][px] = C
# tile to the right of NPC for player spawn
if 0 <= py < HEIGHT and 0 <= px + 1 < WIDTH:
    MAP_LAYOUT[py][px + 1] = C
