# maps/complex_map.py

# A more complex deterministic map layout generator.
# Tiles: C=co (grass), D=dat (dirt), B=betong (concrete), W=nuoc (water), T=tuong (wall)

C = "co"
D = "dat"
B = "betong"
W = "nuoc"
T = "tuong"

WIDTH = 40
HEIGHT = 25

MAP_LAYOUT = []

for y in range(HEIGHT):
    row = []
    for x in range(WIDTH):
        # Outer border
        if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
            row.append(T)
            continue

        # Inner soft border of grass
        if x == 1 or y == 1 or x == WIDTH - 2 or y == HEIGHT - 2:
            row.append(C)
            continue

        # Central open arena (big grass area)
        if 12 <= x <= 27 and 7 <= y <= 17:
            # place some patterned concrete patches
            if (x - 12) % 5 == 0 and (y - 7) % 4 == 0:
                row.append(B)
            else:
                row.append(C)
            continue

        # Create rooms: top-left and bottom-right rectangles of walls (obstacles)
        if (3 <= x <= 9 and 3 <= y <= 9) or (30 <= x <= 36 and 15 <= y <= 21):
            # hollow boxes: wall border, dirt inside
            if x in (3,9) or y in (3,9) or x in (30,36) or y in (15,21):
                row.append(T)
            else:
                row.append(D)
            continue

        # Maze-like pillars and corridors: vertical wall strips with gaps
        if x % 6 == 0 and 4 <= x <= WIDTH - 6:
            # leave gaps for passages every 7 tiles in y
            if y % 7 in (3,4):
                row.append(D)
            else:
                row.append(T)
            continue

        # Some horizontal breaks of wall to form chokepoints
        if y % 6 == 0 and 5 <= y <= HEIGHT - 6:
            if x % 9 in (2,3):
                row.append(T)
            else:
                row.append(D)
            continue

        # A few water pools near the left-center
        if (5 <= x <= 11 and 12 <= y <= 15) or (22 <= x <= 25 and 18 <= y <= 20):
            row.append(W)
            continue

        # Scattered concrete patches
        if (x * y) % 11 == 0:
            row.append(B)
            continue

        # default ground
        row.append(D)

    MAP_LAYOUT.append(row)

MAP_ROWS = len(MAP_LAYOUT)
