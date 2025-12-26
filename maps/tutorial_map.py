# maps/tutorial_map.py

# Các khoá tên tile
C = "co"
D = "dat"
B = "betong"
W = "nuoc"
T = "tuong"
TH = "thung"

WIDTH = 40
HEIGHT = 25

MAP_LAYOUT = []

for y in range(HEIGHT):
    row = []
    for x in range(WIDTH):

        # Viền ngoài là tường
        if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
            row.append(T)

        # Vành tường thứ 2 là cỏ để player đứng gần viền
        elif x == 1 or y == 1 or x == WIDTH - 2 or y == HEIGHT - 2:
            row.append(C)

        # Mặc định: khu vực hướng dẫn phủ toàn cỏ
        else:
            row.append(C)

    MAP_LAYOUT.append(row)

# Đặt một vài thùng gỗ (vật chặn) gần vị trí xuất phát để làm quen
# đặt một vài thùng gỗ xa vị trí NPC để không chặn NPC hoặc player
# NPC sẽ được spawn ở (6,5) — tránh đặt thùng quanh vị trí đó
crate_positions = [
    (10, 8), (11, 8), (12, 8),
    (14, 10), (15, 10),
]

for cx, cy in crate_positions:
    if 0 <= cy < HEIGHT and 0 <= cx < WIDTH:
        MAP_LAYOUT[cy][cx] = TH

MAP_ROWS = len(MAP_LAYOUT)
